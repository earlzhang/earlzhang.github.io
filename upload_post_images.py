#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "oss2",
#   "arrow",
#   "pillow",
#   "python-dotenv",
#   "loguru",
# ]
# ///
"""发布前图片检查：将 content/posts 下 Markdown 引用的本地图片上传到阿里云 OSS。

识别 `![alt](path)` 与 `<img src="path">` 中的本地路径（跳过 http(s)/data:），
超宽图片先按格式上限缩放，上传到 earlmind bucket 的 blog/ 前缀下，
并把引用改写为带 OSS 压缩参数（webp + q80 + 限宽 1200）的 URL，
与 publish_to_blog.py 产出的最终形态一致。

由 push_blog.command 在 git add 之前调用：
- 无本地图片：直接退出，无需 OSS 凭证；
- 有本地图片但凭证缺失或上传失败：退出码非零，中断发布，避免上线失效引用。

凭证加载顺序：环境变量 → 本仓库 .env → CSO写作 script/.env。
"""
from __future__ import annotations

import hashlib
import os
import re
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import unquote

import arrow
import oss2
from dotenv import load_dotenv
from loguru import logger
from PIL import Image, ImageOps

BLOG_ROOT = Path(__file__).resolve().parent
POSTS_DIR = BLOG_ROOT / "content" / "posts"

# CSO 写作仓库的凭证文件，与 md_upload_images.py 共用同一份密钥
CSO_ENV = Path(
    "/Users/earlzhang/Library/CloudStorage/坚果云-earlzhang@163.com"
    "/我的坚果云/1SeekingBeta/CSO写作/script/.env"
)

OSS_ENDPOINT = "oss-cn-shanghai.aliyuncs.com"
OSS_BUCKET = "earlmind"
OSS_PREFIX = "blog/"
OSS_DOMAIN = f"https://{OSS_BUCKET}.{OSS_ENDPOINT}"
# 与 publish_to_blog.py 一致：限宽 1200 + webp + q80
OSS_IMAGE_PROCESS = "x-oss-process=image/resize,w_1200/format,webp/quality,q_80"
# gif/svg 不追加处理参数，避免动图丢帧、矢量图报错
_BITMAP_EXT = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}

# 与 md_upload_images.py 一致的宽度上限：JPG/WebP 1920（有损照片类）、PNG 2160（截图保留 Retina）
MAX_WIDTH_JPG = 1920
MAX_WIDTH_PNG = 2160
MAX_WIDTH_WEBP = 1920

_INVALID_KEY_CHARS = re.compile(r"[^A-Za-z0-9._\-/]")
_MD_IMAGE_RE = re.compile(r'!\[([^\]]*)\]\((?:<([^>]+)>|([^)]+?))(?:\s+"[^"]*")?\)')
_HTML_IMG_RE = re.compile(r'<img\b[^>]*?\bsrc=(["\'])([^"\']+)\1[^>]*?/?>', re.IGNORECASE)


def _sanitize_object_name(name: str) -> str:
    parts = [part for part in name.split("/") if part]
    sanitized: list[str] = []
    for part in parts or ["file"]:
        ascii_part = part.encode("ascii", "ignore").decode().replace(" ", "_")
        cleaned = _INVALID_KEY_CHARS.sub("", ascii_part)
        sanitized.append(cleaned or "file")
    return "/".join(sanitized) or "file"


def _is_local(path: str) -> bool:
    return not path.startswith(("http://", "https://", "data:"))


def collect_local_images(text: str, base_dir: Path) -> list[tuple[str, Path]]:
    """收集 (原始路径字符串, 绝对 Path)，仅本地图片，按 cleaned 路径去重。"""
    results: list[tuple[str, Path]] = []
    seen: set[str] = set()

    def add(raw_path: str) -> None:
        if not _is_local(raw_path):
            return
        cleaned = unquote(raw_path.strip().strip("<>").strip())
        if cleaned in seen:
            return
        seen.add(cleaned)
        results.append((raw_path, (base_dir / cleaned).resolve()))

    for m in _MD_IMAGE_RE.finditer(text):
        add((m.group(2) or m.group(3)).strip())
    for m in _HTML_IMG_RE.finditer(text):
        add(m.group(2).strip())
    return results


def build_uploader() -> oss2.Bucket:
    load_dotenv(BLOG_ROOT / ".env")
    load_dotenv(CSO_ENV)
    load_dotenv()
    key_id = os.getenv("ALIBABA_OSS_ACCESS_KEY_ID") or os.getenv("OSS_ACCESS_KEY_ID")
    key_secret = os.getenv("ALIBABA_OSS_ACCESS_KEY_SECRET") or os.getenv("OSS_ACCESS_KEY_SECRET")
    if not key_id or not key_secret:
        raise ValueError("缺少 OSS 凭证，请设置 ALIBABA_OSS_ACCESS_KEY_ID / ALIBABA_OSS_ACCESS_KEY_SECRET")
    return oss2.Bucket(oss2.Auth(key_id, key_secret), OSS_ENDPOINT, OSS_BUCKET)


def prepare_image(path: Path) -> tuple[Path, Path | None]:
    """超宽则缩放（含 EXIF 转正），返回 (待上传路径, 临时文件或 None)。"""
    try:
        with Image.open(path) as img:
            format_name = (img.format or "").upper()
            if (img.getexif().get(274, 1) or 1) != 1:
                img = ImageOps.exif_transpose(img)
            max_width = {"JPEG": MAX_WIDTH_JPG, "WEBP": MAX_WIDTH_WEBP}.get(format_name, MAX_WIDTH_PNG)
            if img.width <= max_width:
                return path, None
            ratio = max_width / img.width
            img = img.resize((max_width, int(img.height * ratio)), Image.Resampling.LANCZOS)
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=path.suffix or ".img")
            save_kwargs = {"format": format_name}
            if format_name in ("JPEG", "WEBP"):
                save_kwargs.update({"quality": 85, "optimize": True})
            else:
                save_kwargs.update({"compress_level": 9, "optimize": True})
            img.save(tmp.name, **save_kwargs)
            tmp.close()
            logger.info(f"缩放 {path.name}: {img.width / ratio:.0f}px -> {max_width}px")
            return Path(tmp.name), Path(tmp.name)
    except Exception as e:
        logger.warning(f"缩放失败，按原图上传 {path.name}: {e}")
        return path, None


def upload_one(bucket: oss2.Bucket, local_path: Path) -> str:
    """上传单张图片，返回带压缩参数的 OSS URL。"""
    upload_path, tmp = prepare_image(local_path)
    try:
        md5 = hashlib.md5(upload_path.read_bytes()).hexdigest()[:8]
        ts = arrow.now().format("YYYYMMDD_HHmmss_SSS")
        key = f"{OSS_PREFIX}{ts}_{md5}_{_sanitize_object_name(local_path.name)}"
        bucket.put_object_from_file(key, str(upload_path))
        url = f"{OSS_DOMAIN}/{key}"
        if local_path.suffix.lower() in _BITMAP_EXT:
            url += f"?{OSS_IMAGE_PROCESS}"
        return url
    finally:
        if tmp:
            tmp.unlink(missing_ok=True)


def replace_refs(text: str, url_map: dict[str, str]) -> str:
    def md_replacer(m: re.Match) -> str:
        raw = (m.group(2) or m.group(3)).strip()
        return f"![{m.group(1)}]({url_map.get(raw, raw)})"

    def html_replacer(m: re.Match) -> str:
        quote, raw = m.group(1), m.group(2)
        return m.group(0).replace(
            f"src={quote}{raw}{quote}", f"src={quote}{url_map.get(raw, raw)}{quote}", 1
        )

    return _HTML_IMG_RE.sub(html_replacer, _MD_IMAGE_RE.sub(md_replacer, text))


def process_post(bucket: oss2.Bucket, md_file: Path) -> bool:
    """处理单篇文章：全部本地图上传成功才改写落盘；任一失败返回 False。"""
    text = md_file.read_text(encoding="utf-8")
    refs = collect_local_images(text, md_file.parent)
    if not refs:
        return True

    logger.info(f"{md_file.name}: 发现 {len(refs)} 张本地图片")
    url_map: dict[str, str] = {}
    ok = True

    def _task(item: tuple[str, Path]) -> tuple[str, str | None, bool]:
        """返回 (raw, url, 是否为文件缺失)。文件缺失只警告不阻塞，上传失败才阻塞。"""
        raw, abs_path = item
        if not abs_path.is_file():
            logger.warning(f"本地文件缺失（引用保持原样）: {raw}")
            return raw, None, True
        try:
            return raw, upload_one(bucket, abs_path), False
        except Exception as e:
            logger.error(f"上传失败 {abs_path}: {e}")
            return raw, None, False

    with ThreadPoolExecutor(max_workers=5) as pool:
        for raw, url, missing in pool.map(_task, refs):
            if url:
                url_map[raw] = url
                logger.success(f"{raw} -> {url}")
            elif not missing:
                ok = False

    # 部分成功时也落盘已成功的替换，只有上传失败才整体阻断
    if url_map:
        md_file.write_text(replace_refs(text, url_map), encoding="utf-8")
        logger.success(f"{md_file.name}: 已替换 {len(url_map)} 处本地图片引用")
    if not ok:
        logger.error(f"{md_file.name}: 有图片上传失败")
        return False
    return True


def main() -> None:
    logger.remove()
    logger.add(sys.stderr, level="INFO")

    posts = sorted(POSTS_DIR.rglob("*.md"))
    pending = [p for p in posts if collect_local_images(p.read_text(encoding="utf-8"), p.parent)]
    if not pending:
        print("未发现本地图片引用，跳过上传。")
        return

    print(f"共 {len(pending)} 篇文章含本地图片，开始上传至 {OSS_DOMAIN}/{OSS_PREFIX}")
    try:
        bucket = build_uploader()
    except Exception as e:
        logger.critical(f"OSS 初始化失败: {e}")
        sys.exit(1)

    failures = [p for p in pending if not process_post(bucket, p)]
    if failures:
        logger.error(f"{len(failures)} 篇文章处理失败: {[p.name for p in failures]}")
        sys.exit(1)
    print("全部本地图片已上传并改写为 OSS URL。")


if __name__ == "__main__":
    main()
