# /// script
# requires-python = ">=3.10"
# dependencies = ["loguru"]
# ///
"""为 content/posts 下缺少 description 的文章批量回填 SEO 描述。

从正文第一段有效文字中提取（跳过引用块、标题、图片、代码块等），
清洗 Markdown/LaTeX 标记后截断到约 110 字，优先在句读处收尾。
幂等：已有 description 的文章会跳过，可重复运行。
"""

import re
import sys
from pathlib import Path

from loguru import logger

POSTS_DIR = Path(__file__).parent / "content" / "posts"
DESC_LIMIT = 110
MIN_PARA_LEN = 15

# 正文段落跳过的开头标记（引用、标题、图片、HTML、短代码、表格、代码块、数学块）
SKIP_PREFIXES = ("#", ">", "!", "<", "{%", "{{", "```", "|", "$$", r"\[", "- ", "* ", "1. ")

IMG_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)")
LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")
HTML_RE = re.compile(r"<[^>]+>")
INLINE_MATH_RE = re.compile(r"\\\((.*?)\\\)")
BLOCK_MATH_RE = re.compile(r"\\\[(.*?)\\\]", re.S)
EMPHASIS_RE = re.compile(r"(\*\*|__|\*|_|~~|`+)(.+?)\1")
SHORTCODE_RE = re.compile(r"\{\{[<%].*?[>%]\}\}", re.S)
SENTENCE_END_RE = re.compile(r"[。！？!?]")
WHITESPACE_RE = re.compile(r"\s+")


def split_frontmatter(text: str) -> tuple[str, str, str] | None:
    """返回 (delimiter, frontmatter_body, content)。无 frontmatter 返回 None。"""
    m = re.match(r"^(\+\+\+|---)\n(.*?)\n\1\n?(.*)$", text, re.S)
    if not m:
        return None
    return m.group(1), m.group(2), m.group(3)


def clean_paragraph(para: str) -> str:
    text = IMG_RE.sub("", para)
    text = SHORTCODE_RE.sub("", text)
    text = BLOCK_MATH_RE.sub(r"\1", text)
    text = INLINE_MATH_RE.sub(r"\1", text)
    text = LINK_RE.sub(r"\1", text)
    text = HTML_RE.sub("", text)
    for _ in range(3):
        new = EMPHASIS_RE.sub(r"\2", text)
        if new == text:
            break
        text = new
    text = text.replace("<!--more-->", "").replace("**", "").replace("`", "")
    return WHITESPACE_RE.sub(" ", text).strip()


def make_description(body: str) -> str:
    for para in re.split(r"\n\s*\n", body):
        para = para.strip()
        if not para or para.startswith(SKIP_PREFIXES):
            continue
        cleaned = clean_paragraph(para)
        if len(cleaned) < MIN_PARA_LEN:
            continue
        if len(cleaned) <= DESC_LIMIT:
            return cleaned
        for m in SENTENCE_END_RE.finditer(cleaned[: DESC_LIMIT + 30]):
            if m.end() >= 40:
                return cleaned[: m.end()]
        return cleaned[:DESC_LIMIT]
    return ""


def toml_quote(s: str) -> str:
    if "'" not in s:
        return f"'{s}'"
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def process_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    parts = split_frontmatter(text)
    if not parts:
        logger.warning("无 frontmatter，跳过: {}", path.name)
        return False
    delim, fm, body = parts
    if re.search(r"(?im)^\s*description\s*=", fm):
        return False

    desc = make_description(body)
    if not desc:
        logger.warning("未能提取有效段落，跳过: {}", path.name)
        return False

    new_fm = fm + f"\ndescription = {toml_quote(desc)}"
    path.write_text(f"{delim}\n{new_fm}\n{delim}\n{body}", encoding="utf-8")
    logger.info("{} -> {}", path.name, desc[:60])
    return True


def main() -> int:
    files = sorted(POSTS_DIR.rglob("*.md"))
    if not files:
        logger.error("未找到文章目录: {}", POSTS_DIR)
        return 1
    updated = sum(process_file(f) for f in files)
    logger.success("共 {} 篇，回填 {} 篇，跳过 {}", len(files), updated, len(files) - updated)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        logger.exception("回填失败")
        sys.exit(1)
