#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "litellm>=1.80.0",
#   "httpx[socks]",
#   "python-dotenv",
#   "oss2",
#   "loguru",
# ]
# ///
"""
批量为博客文章生成 tags（Hugo frontmatter）

复用 CSO写作/script/publish_to_blog.py 的 generate_tags（deepseek/deepseek-flash），
按本仓库根目录 blog_tags.txt 词表为每篇文章选 3-5 个 tag，写回 frontmatter。
兼容 +++ TOML 与 --- YAML 两种 frontmatter；已有 tags 默认重新生成归一。
词表外的新 tag 跑批结束后追加进 blog_tags.txt 末尾。

用法:
    uv run add_blog_tags.py <posts目录或md文件>... [--dry-run] [--limit N] [--skip-tagged]

示例:
    uv run add_blog_tags.py content/posts/2026 --dry-run --limit 3
    uv run add_blog_tags.py content/posts/2026
"""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from pathlib import Path

from loguru import logger

BLOG_ROOT = Path(__file__).resolve().parent
BLOG_TAGS_FILE = BLOG_ROOT / "blog_tags.txt"
CSO_SCRIPT_DIR = Path(
    "/Users/earlzhang/Library/CloudStorage/坚果云-earlzhang@163.com/"
    "我的坚果云/1SeekingBeta/CSO写作/script"
)

sys.path.insert(0, str(CSO_SCRIPT_DIR))
try:
    from publish_to_blog import (
        generate_tags,
        load_tag_vocab,
        append_new_tags,
        _toml_escape,
        BLOG_TAGS_FILE as _PUBLISH_TAGS_FILE,
    )
except ImportError as e:
    print(f"错误：无法从 {CSO_SCRIPT_DIR} 导入 publish_to_blog: {e}", file=sys.stderr)
    sys.exit(1)

# 文件开头的 TOML / YAML frontmatter 块
_FM_TOML_RE = re.compile(r"\A\+\+\+\n(.*?)\n\+\+\+\n?", re.DOTALL)
_FM_YAML_RE = re.compile(r"\A---\n(.*?)\n---\n?", re.DOTALL)
# 单行 tags（TOML: tags = [...]；YAML: tags: [...] 或 tags: a, b）
_TAGS_TOML_LINE_RE = re.compile(r'(?m)^tags\s*=\s*\[.*\]\s*$')
_TAGS_YAML_LINE_RE = re.compile(r"(?m)^tags\s*:.*$")
# 单行 description / title（决定 tags 插入位置）
_DESC_TOML_LINE_RE = re.compile(
    r"(?m)^(description\s*=\s*(?:'[^'\n]*'|\"(?:[^\"\\\n]|\\.)*\"))\s*$"
)
_TITLE_TOML_LINE_RE = re.compile(
    r"(?m)^(title\s*=\s*(?:'[^'\n]*'|\"(?:[^\"\\\n]|\\.)*\"))\s*$"
)
_DESC_YAML_LINE_RE = re.compile(r"(?m)^(description\s*:.*)$")
_TITLE_YAML_LINE_RE = re.compile(r"(?m)^title\s*:\s*\"?([^\"\n]+?)\"?\s*$")
_TITLE_YAML_FULL_RE = re.compile(r"(?m)^(title\s*:.*)$")


def split_frontmatter(text: str) -> tuple[str, str, str] | None:
    """拆分 frontmatter 与正文，返回 (格式 'toml'|'yaml', fm文本, 正文)。无则 None。"""
    if m := _FM_TOML_RE.match(text):
        return "toml", m.group(1), text[m.end():]
    if m := _FM_YAML_RE.match(text):
        return "yaml", m.group(1), text[m.end():]
    return None


def get_title(fmt: str, fm: str, fallback: str) -> str:
    """从 frontmatter 取标题；失败退回文件名。"""
    if fmt == "toml":
        try:
            return tomllib.loads(fm).get("title") or fallback
        except tomllib.TOMLDecodeError:
            return fallback
    m = _TITLE_YAML_LINE_RE.search(fm)
    return m.group(1).strip() if m else fallback


def set_tags_toml(fm: str, tags: list[str]) -> str | None:
    """在 TOML frontmatter 中替换/插入 tags 行，tomllib 校验失败返回 None。"""
    new_line = "tags = [" + ", ".join(f'"{_toml_escape(t)}"' for t in tags) + "]"
    if _TAGS_TOML_LINE_RE.search(fm):
        new_fm = _TAGS_TOML_LINE_RE.sub(new_line, fm, count=1)
    else:
        # 优先插到 description 行之后，其次 title 行之后
        new_fm, n = _DESC_TOML_LINE_RE.subn(
            lambda m: m.group(1) + "\n" + new_line, fm, count=1
        )
        if n == 0:
            new_fm, n = _TITLE_TOML_LINE_RE.subn(
                lambda m: m.group(1) + "\n" + new_line, fm, count=1
            )
        if n == 0:
            return None
    try:
        tomllib.loads(new_fm)
    except tomllib.TOMLDecodeError:
        return None
    return new_fm


def set_tags_yaml(fm: str, tags: list[str]) -> str | None:
    """在 YAML frontmatter 中替换/插入 tags 行（flow sequence 写法）。"""
    def yaml_quote(s: str) -> str:
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'

    new_line = "tags: [" + ", ".join(yaml_quote(t) for t in tags) + "]"
    if _TAGS_YAML_LINE_RE.search(fm):
        return _TAGS_YAML_LINE_RE.sub(new_line, fm, count=1)
    new_fm, n = _DESC_YAML_LINE_RE.subn(
        lambda m: m.group(1) + "\n" + new_line, fm, count=1
    )
    if n == 0:
        new_fm, n = _TITLE_YAML_FULL_RE.subn(
            lambda m: m.group(1) + "\n" + new_line, fm, count=1
        )
    return new_fm if n else None


def process_file(path: Path, vocab: list[str], *, dry_run: bool, skip_tagged: bool) -> tuple[bool, list[str]]:
    """为单篇文章生成并写回 tags。返回 (是否有变更, 词表外新tag列表)。"""
    text = path.read_text(encoding="utf-8")
    parts = split_frontmatter(text)
    if not parts:
        logger.warning(f"无 frontmatter，跳过: {path.name}")
        return False, []
    fmt, fm, body = parts

    if skip_tagged and (_TAGS_TOML_LINE_RE.search(fm) or _TAGS_YAML_LINE_RE.search(fm)):
        logger.info(f"已有 tags，跳过: {path.name}")
        return False, []

    title = get_title(fmt, fm, path.stem)
    try:
        tags = generate_tags(title, body, vocab)
    except Exception as e:
        logger.error(f"生成失败 {path.name}: {e}")
        return False, []
    if not tags:
        logger.warning(f"未生成有效 tags，跳过: {path.name}")
        return False, []

    new_tags = [t for t in tags if t not in vocab]
    if fmt == "toml":
        new_fm = set_tags_toml(fm, tags)
        if new_fm is None:
            logger.error(f"tags 写入 frontmatter 失败，跳过: {path.name}")
            return False, new_tags
        new_text = f"+++\n{new_fm}\n+++\n{body}"
    else:
        new_fm = set_tags_yaml(fm, tags)
        if new_fm is None:
            logger.error(f"tags 写入 frontmatter 失败，跳过: {path.name}")
            return False, new_tags
        new_text = f"---\n{new_fm}\n---\n{body}"

    logger.info(f"{path.name}  →  [{', '.join(tags)}]")
    if not dry_run:
        path.write_text(new_text, encoding="utf-8")
    return True, new_tags


def main() -> None:
    parser = argparse.ArgumentParser(description="批量为博客文章生成 tags")
    parser.add_argument(
        "paths", nargs="+",
        help="博文目录（如 content/posts/2026）或单个 .md 文件，可混合多个",
    )
    parser.add_argument("--dry-run", action="store_true", help="只打印不写文件")
    parser.add_argument("--limit", type=int, default=None, help="只处理前 N 篇")
    parser.add_argument(
        "--skip-tagged", action="store_true",
        help="跳过已有 tags 的文章（默认重新生成并归一）",
    )
    args = parser.parse_args()

    files: list[Path] = []
    for raw in args.paths:
        p = Path(raw).expanduser()
        if p.is_dir():
            files.extend(sorted(p.rglob("*.md")))
        elif p.is_file() and p.suffix == ".md":
            files.append(p)
        else:
            print(f"错误：路径不存在或不是 .md 文件 {p}", file=sys.stderr)
            sys.exit(1)
    files = sorted(set(files))
    if not files:
        print("错误：未找到任何 .md 文件", file=sys.stderr)
        sys.exit(1)

    vocab = load_tag_vocab()
    if not vocab:
        print(f"错误：词表为空或不存在 {BLOG_TAGS_FILE}", file=sys.stderr)
        sys.exit(1)
    if _PUBLISH_TAGS_FILE != BLOG_TAGS_FILE:
        logger.warning(
            f"注意：publish_to_blog 使用的词表为 {_PUBLISH_TAGS_FILE}，"
            f"与本脚本 {BLOG_TAGS_FILE} 不一致"
        )

    logger.remove()
    logger.add(sys.stderr, level="INFO", format="{message}")
    if args.limit:
        files = files[: args.limit]
    logger.info(
        f"共 {len(files)} 篇文章待处理，词表 {len(vocab)} 个 tag"
        f"{'（dry-run）' if args.dry_run else ''}"
    )

    changed = skipped = 0
    all_new_tags: list[str] = []
    for i, path in enumerate(files, 1):
        logger.info(f"[{i}/{len(files)}] {path.name}")
        try:
            did_change, new_tags = process_file(
                path, vocab, dry_run=args.dry_run, skip_tagged=args.skip_tagged
            )
            for t in new_tags:
                if t not in all_new_tags:
                    all_new_tags.append(t)
            if did_change:
                changed += 1
            else:
                skipped += 1
        except Exception as e:
            logger.exception(f"处理异常 {path.name}: {e}")
            skipped += 1

    logger.info(f"完成：{changed} 篇更新，{skipped} 篇跳过")
    if all_new_tags:
        logger.info(f"词表外新 tag: {', '.join(all_new_tags)}")
        if not args.dry_run:
            append_new_tags(all_new_tags, BLOG_TAGS_FILE)


if __name__ == "__main__":
    main()
