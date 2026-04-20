#!/usr/bin/env -S uv run --script
# -*- coding: utf-8 -*-
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
双半转全 —— 将文本中的半角双引号/单引号转换为全角中文引号。

用法：
  cat input.txt | python convert_quotes.py        # 从标准输入读取，结果输出到stdout
  python convert_quotes.py input.txt              # 从文件读取，结果输出到stdout
  python convert_quotes.py input.txt -o out.txt   # 从文件读取，结果写入文件
  python convert_quotes.py input.txt --inplace    # 原地修改（覆盖原文件）
  python convert_quotes.py --single input.txt     # 只转换单引号
  python convert_quotes.py --double input.txt     # 只转换双引号（默认两者都转）

规则（与 txt.html 保持一致）：
  双引号：
    - " " 交替替换为 " "
    - 数字后面紧跟 " 且下一个字符不是中文时，视为英制单位（如 12"），保留原样

  单引号：
    - ' ' 交替替换为 ' '
    - 英文字母之间的 ' 视为撇号（如 Don't、O'Reilly），保留原样

  Markdown 保护区（转换前暂存、转换后还原）：
    1. Fenced 代码块 ```...```
    2. 行内代码 `...`
    3. Markdown 链接/图片 [text](url) 或 ![alt](url)
    4. 裸 URL（http:// / https://）
"""

from __future__ import annotations

import re
import sys
import argparse
from pathlib import Path


# ─────────────────────────────────────────────────────────────
# Markdown 保护机制
# ─────────────────────────────────────────────────────────────

def with_markdown_protection(text: str, transform_fn) -> str:
    """
    在标点转换前，将不应被转换的区域替换为占位符，转换后再还原。

    保护范围：
      1. Fenced 代码块（```lang\\n...\\n```）
      2. 行内代码（`code`）
      3. Markdown 链接/图片的 URL 部分：[text](url) 或 ![alt](url)
      4. 裸 URL（http:// / https://）
    """
    placeholders: list[str] = []

    def protect(s: str) -> str:
        token = f"\x00MDPROTECT{len(placeholders)}\x00"
        placeholders.append(s)
        return token

    # 1. 保护 fenced 代码块
    result = re.sub(r"```[\s\S]*?```", lambda m: protect(m.group()), text)

    # 2. 保护行内代码（支持多个反引号作开闭）
    result = re.sub(r"`+[^`]+`+", lambda m: protect(m.group()), result)

    # 3. 保护完整的 Markdown 链接/图片语法
    result = re.sub(r"!?\[[^\]]*\]\([^)]*\)", lambda m: protect(m.group()), result)

    # 4. 保护裸 URL
    result = re.sub(
        r"https?://[^\s\u4e00-\u9fff]*",
        lambda m: protect(m.group()),
        result,
    )

    # 执行转换
    result = transform_fn(result)

    # 还原占位符
    result = re.sub(
        r"\x00MDPROTECT(\d+)\x00",
        lambda m: placeholders[int(m.group(1))],
        result,
    )

    return result


# ─────────────────────────────────────────────────────────────
# 双引号转换（半角 " → 全角 " "）
# ─────────────────────────────────────────────────────────────

_CHINESE_CHAR = re.compile(r"[\u4e00-\u9fff]")


def convert_double_quotes(text: str) -> str:
    """
    将半角双引号 " 交替替换为 " 和 "。

    例外：数字后面紧跟 " 且下一个字符不是中文，视为英制单位保留。
    例：12" 或 12"x → 保留原有双引号。
    """
    is_open = True
    chars = list(text)
    result: list[str] = []

    for i, ch in enumerate(chars):
        if ch != '"':
            result.append(ch)
            continue

        prev_char = chars[i - 1] if i > 0 else ""
        next_char = chars[i + 1] if i < len(chars) - 1 else ""

        # 英制单位写法保留，如 12"、12"x
        if prev_char.isdigit() and not _CHINESE_CHAR.match(next_char):
            result.append(ch)
            continue

        result.append("\u201c" if is_open else "\u201d")  # " or "
        is_open = not is_open

    return "".join(result)


# ─────────────────────────────────────────────────────────────
# 单引号转换（半角 ' → 全角 ' '）
# ─────────────────────────────────────────────────────────────

def convert_single_quotes(text: str) -> str:
    """
    将半角单引号 ' 交替替换为 ' 和 '。

    例外：英文字母之间的 ' 视为撇号（如 Don't、O'Reilly），保留原样。
    """
    is_open = True
    chars = list(text)
    result: list[str] = []

    for i, ch in enumerate(chars):
        if ch != "'":
            result.append(ch)
            continue

        prev_char = chars[i - 1] if i > 0 else ""
        next_char = chars[i + 1] if i < len(chars) - 1 else ""

        # 英文撇号用法保留，如 Don't、O'Reilly、it's
        if re.match(r"[A-Za-z]", prev_char) and re.match(r"[A-Za-z]", next_char):
            result.append(ch)
            continue

        result.append("\u2018" if is_open else "\u2019")  # ' or '
        is_open = not is_open

    return "".join(result)


# ─────────────────────────────────────────────────────────────
# 组合：双半转全（双引号 + 单引号）
# ─────────────────────────────────────────────────────────────

def convert_quotes(text: str, *, double: bool = True, single: bool = True) -> str:
    """对文本执行双半转全，并启用 Markdown 保护。"""
    def _transform(t: str) -> str:
        if double:
            t = convert_double_quotes(t)
        if single:
            t = convert_single_quotes(t)
        return t

    return with_markdown_protection(text, _transform)


# ─────────────────────────────────────────────────────────────
# CLI 入口
# ─────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="convert_quotes",
        description="双半转全：将半角引号转换为全角中文引号（与 txt.html 逻辑一致）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "file",
        nargs="?",
        type=Path,
        metavar="FILE",
        help="输入文件路径（省略则从 stdin 读取）",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        metavar="OUTPUT",
        help="输出文件路径（省略则输出到 stdout）",
    )
    parser.add_argument(
        "--inplace", "-i",
        action="store_true",
        help="原地修改输入文件（与 --output 互斥）",
    )
    quote_group = parser.add_mutually_exclusive_group()
    quote_group.add_argument(
        "--double", "-d",
        action="store_true",
        help="只转换双引号（默认双引号和单引号都转）",
    )
    quote_group.add_argument(
        "--single", "-s",
        action="store_true",
        help="只转换单引号（默认双引号和单引号都转）",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # 校验
    if args.inplace and args.output:
        parser.error("--inplace 和 --output 不能同时使用")
    if args.inplace and not args.file:
        parser.error("--inplace 需要指定输入文件")

    # 读取输入
    if args.file:
        try:
            text = args.file.read_text(encoding="utf-8")
        except FileNotFoundError:
            sys.exit(f"错误：文件不存在：{args.file}")
        except OSError as e:
            sys.exit(f"错误：无法读取文件：{e}")
    else:
        text = sys.stdin.read()

    # 确定转换模式
    if args.double:
        do_double, do_single = True, False
    elif args.single:
        do_double, do_single = False, True
    else:
        do_double, do_single = True, True  # 默认：两者都转

    # 执行转换
    result = convert_quotes(text, double=do_double, single=do_single)

    # 输出结果
    if args.inplace:
        args.file.write_text(result, encoding="utf-8")
        print(f"✓ 已原地修改：{args.file}", file=sys.stderr)
    elif args.output:
        try:
            args.output.write_text(result, encoding="utf-8")
            print(f"✓ 已写入：{args.output}", file=sys.stderr)
        except OSError as e:
            sys.exit(f"错误：无法写入文件：{e}")
    else:
        sys.stdout.write(result)


if __name__ == "__main__":
    main()
