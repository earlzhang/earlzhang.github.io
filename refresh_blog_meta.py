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
一次性刷新存量博文的 description 与 tags（Hugo frontmatter）

每篇文章只调用一次 generate_metadata（deepseek/deepseek-flash，复用
CSO写作/script/publish_to_blog.py 的新 prompt：先 thesis/topics 再写字段），
同时更新 frontmatter 中的 description 与 tags 两行，避免
regen_blog_descriptions.py + add_blog_tags.py 跑两遍的重复调用。
兼容 +++ TOML 与 --- YAML 两种 frontmatter；slug 不改动（文件名已定）。
词表外的新 tag 跑批结束后统一追加进 blog_tags.txt 末尾。

用法:
    uv run refresh_blog_meta.py <posts目录或md文件>... [--dry-run] [--limit N]

示例:
    uv run refresh_blog_meta.py content/posts/2026 --dry-run --limit 3
    uv run refresh_blog_meta.py content/posts/2026
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
        generate_metadata,
        load_tag_vocab,
        append_new_tags,
        _toml_escape,
        BLOG_TAGS_FILE as _PUBLISH_TAGS_FILE,
    )
    from add_blog_tags import (
        split_frontmatter,
        get_title,
        set_tags_toml,
        set_tags_yaml,
    )
except ImportError as e:
    print(f"错误：无法导入 publish_to_blog / add_blog_tags: {e}", file=sys.stderr)
    sys.exit(1)

# 单行 description（TOML / YAML），用于替换或确定插入位置
_DESC_TOML_LINE_RE = re.compile(
    r"(?m)^description\s*=\s*(?:'[^'\n]*'|\"(?:[^\"\\\n]|\\.)*\")\s*$"
)
_TITLE_TOML_LINE_RE = re.compile(
    r"(?m)^(title\s*=\s*(?:'[^'\n]*'|\"(?:[^\"\\\n]|\\.)*\"))\s*$"
)
_DESC_YAML_LINE_RE = re.compile(r"(?m)^description\s*:.*$")
_TITLE_YAML_FULL_RE = re.compile(r"(?m)^(title\s*:.*)$")


def set_description_toml(fm: str, desc: str) -> str | None:
    """在 TOML frontmatter 中替换/插入 description 行，tomllib 校验失败返回 None。"""
    new_line = f'description = "{_toml_escape(desc)}"'
    if _DESC_TOML_LINE_RE.search(fm):
        new_fm = _DESC_TOML_LINE_RE.sub(new_line, fm, count=1)
    else:
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


def set_description_yaml(fm: str, desc: str) -> str | None:
    """在 YAML frontmatter 中替换/插入 description 行。"""
    def yaml_quote(s: str) -> str:
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'

    new_line = f"description: {yaml_quote(desc)}"
    if _DESC_YAML_LINE_RE.search(fm):
        return _DESC_YAML_LINE_RE.sub(new_line, fm, count=1)
    new_fm, n = _TITLE_YAML_FULL_RE.subn(
        lambda m: m.group(1) + "\n" + new_line, fm, count=1
    )
    return new_fm if n else None


def process_file(
    path: Path, vocab: list[str], *, dry_run: bool
) -> tuple[bool, list[str]]:
    """刷新单篇文章的 description 与 tags。返回 (是否有变更, 词表外新tag列表)。"""
    text = path.read_text(encoding="utf-8")
    parts = split_frontmatter(text)
    if not parts:
        logger.warning(f"无 frontmatter，跳过: {path.name}")
        return False, []
    fmt, fm, body = parts

    title = get_title(fmt, fm, path.stem)
    old_desc_m = re.search(r"description\s*[=:]\s*(.+)", fm)
    old_desc = old_desc_m.group(1).strip().strip('"\'') if old_desc_m else ""

    try:
        desc, tags, _slug = generate_metadata(title, body, vocab)
    except Exception as e:
        logger.error(f"生成失败 {path.name}: {e}")
        return False, []
    if not desc and not tags:
        logger.warning(f"未生成有效元数据，跳过: {path.name}")
        return False, []

    new_tags = [t for t in tags if t not in vocab]
    if fmt == "toml":
        new_fm = set_tags_toml(fm, tags) if tags else fm
        if new_fm is not None and desc:
            new_fm = set_description_toml(new_fm, desc)
    else:
        new_fm = set_tags_yaml(fm, tags) if tags else fm
        if new_fm is not None and desc:
            new_fm = set_description_yaml(new_fm, desc)
    if new_fm is None:
        logger.error(f"frontmatter 写入失败，跳过: {path.name}")
        return False, new_tags

    logger.info(f"{path.name}")
    if desc:
        logger.info(f"  desc 旧: {old_desc or '(无)'}\n  desc 新: {desc}")
    if tags:
        logger.info(f"  tags 新: [{', '.join(tags)}]")
    if not dry_run:
        if fmt == "toml":
            path.write_text(f"+++\n{new_fm}\n+++\n{body}", encoding="utf-8")
        else:
            path.write_text(f"---\n{new_fm}\n---\n{body}", encoding="utf-8")
    return True, new_tags


def main() -> None:
    parser = argparse.ArgumentParser(description="一次性刷新博文 description 与 tags")
    parser.add_argument(
        "paths", nargs="+",
        help="博文目录（如 content/posts/2026）或单个 .md 文件，可混合多个",
    )
    parser.add_argument("--dry-run", action="store_true", help="只打印不写文件")
    parser.add_argument("--limit", type=int, default=None, help="只处理前 N 篇")
    args = parser.parse_args()

    files: list[Path] = []
    for raw in args.paths:
        p = Path(raw).expanduser()
        if p.is_dir():
            files.extend(p.rglob("*.md"))
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
            did_change, new_tags = process_file(path, vocab, dry_run=args.dry_run)
            for t in new_tags:
                if t not in all_new_tags:
                    all_new_tags.append(t)
            changed += 1 if did_change else 0
            skipped += 0 if did_change else 1
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
