# /// script
# requires-python = ">=3.11"
# dependencies = ["loguru", "pillow", "pymupdf==1.28.2"]
# ///
"""生成 EarlMind 与 EarlETF 两套方形素材：favicon / iOS / Android / 微信头像。

- EarlMind：方案一「扫描线」，几何与 design/vi-family.html 中的绘制逻辑一致。
- EarlETF：直接从 AI 源文件读取原始矢量路径，不做任何重绘。
输出：design/export/earlmind/ 与 design/export/earletf/，母版 SVG 放在各自的 source/ 下。
"""

import math
import struct
import subprocess
import tempfile
from pathlib import Path
from typing import Final

import pymupdf
from loguru import logger
from PIL import Image

DESIGN: Final = Path(__file__).resolve().parent
ETF_AI: Final = Path(
    "/Users/earlzhang/Library/CloudStorage/坚果云-earlzhang@163.com/我的坚果云/1SeekingBeta/VI/2Logo/VI/EarlETF专业投基之道-定稿.ai"
)
BLUE: Final = "#043888"  # 取自 AI 源文件中方形标识的蓝色
WHITE: Final = "#F6F7FA"
RED: Final = "#F2483C"
ROUND_RX: Final = 16 * 0.22
ETF_WECHAT_SCALE: Final = 0.8

PIXEL_LEFT: Final = "M8 2H6V3H4V4H3V6H2V10H3V12H4V13H6V14H8V12H6V11H5V10H4V6H5V5H6V4H8Z"
RIGHT_RING: Final = "M8 2A6 6 0 0 1 8 14V12A4 4 0 0 0 8 4Z"


def doc(w: float, h: float, body: str) -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:g} {h:g}">{body}</svg>\n'


def bg(w: float, h: float, rx: float = 0.0) -> str:
    return f'<rect width="{w:g}" height="{h:g}" rx="{rx:g}" fill="{BLUE}"/>'


def rrect(x: float, y: float, w: float, h: float, tl: float, tr: float, br: float, bl: float) -> str:
    return (
        f"M{x + tl:.4f} {y:.4f}H{x + w - tr:.4f}A{tr:.4f} {tr:.4f} 0 0 1 {x + w:.4f} {y + tr:.4f}"
        f"V{y + h - br:.4f}A{br:.4f} {br:.4f} 0 0 1 {x + w - br:.4f} {y + h:.4f}"
        f"H{x + bl:.4f}A{bl:.4f} {bl:.4f} 0 0 1 {x:.4f} {y + h - bl:.4f}"
        f"V{y + tl:.4f}A{tl:.4f} {tl:.4f} 0 0 1 {x + tl:.4f} {y:.4f}Z"
    )


def scanline_left() -> str:
    th, r = 0.62, 0.31
    parts: list[str] = []
    for i in range(12):
        y = 2.5 + i
        dy = y - 8
        ox = 8 - math.sqrt(36 - dy * dy)
        to_center = abs(dy) >= 4
        ix = 8.0 if to_center else 8 - math.sqrt(16 - dy * dy)
        radii = (r, 0, 0, r) if to_center else (r, r, r, r)
        parts.append(rrect(ox, y - th / 2, ix - ox, th, *radii))
    return "".join(parts)


def mind_mark(scanline: bool) -> str:
    left = scanline_left() if scanline else PIXEL_LEFT
    return (
        f'<path fill="{WHITE}" d="{left}"/>'
        f'<path fill="{WHITE}" d="{RIGHT_RING}"/>'
        f'<circle cx="9.5" cy="6.5" r="1.5" fill="{RED}"/>'
    )


def earlmind_set() -> dict[str, object]:
    pixel_round = doc(16, 16, bg(16, 16, ROUND_RX) + mind_mark(scanline=False))
    scan_round = doc(16, 16, bg(16, 16, ROUND_RX) + mind_mark(scanline=True))
    scan_square = doc(16, 16, bg(16, 16) + mind_mark(scanline=True))
    return {
        "favicon": pixel_round,
        "ico": {16: pixel_round, 32: pixel_round, 48: scan_round},
        "square": scan_square,
        "wechat": scan_square,
        "masters": {
            "favicon-pixel.svg": pixel_round,
            "round-scanline.svg": scan_round,
            "square-scanline.svg": scan_square,
        },
    }


def extract_etf_mark() -> tuple[float, float, str, str]:
    """读取 AI 第一页中间的方形标识，返回 (宽, 高, 圆角方块路径, E 路径)。"""
    page = pymupdf.open(ETF_AI)[0]
    drawing = next(
        (g for g in page.get_drawings() if g["fill"] and g["rect"].x0 > 600 and g["rect"].y0 > 800 and g["rect"].width > 200),
        None,
    )
    if drawing is None:
        raise ValueError("AI 文件中未找到 EarlETF 方形标识")
    rect = drawing["rect"]
    ox, oy = rect.x0, rect.y0
    subs: list[dict[str, list[str] | list[float]]] = []
    cur: tuple[float, float] | None = None
    for it in drawing["items"]:
        if it[0] == "l":
            a, b, c = it[1], it[2], None
        elif it[0] == "c":
            a, b, c = it[1], it[4], (it[2], it[3])
        else:
            raise ValueError(f"未预期的路径类型: {it[0]}")
        if cur is None or math.dist((a.x, a.y), cur) > 0.01:
            subs.append({"d": [], "x": [], "y": []})
            subs[-1]["d"].append(f"M{a.x - ox:.3f} {a.y - oy:.3f}")
        sub = subs[-1]
        if c is None:
            sub["d"].append(f"L{b.x - ox:.3f} {b.y - oy:.3f}")
        else:
            sub["d"].append(f"C{c[0].x - ox:.3f} {c[0].y - oy:.3f} {c[1].x - ox:.3f} {c[1].y - oy:.3f} {b.x - ox:.3f} {b.y - oy:.3f}")
        sub["x"].extend([b.x - ox]); sub["y"].extend([b.y - oy])
        cur = (b.x, b.y)
    for s in subs:
        s["d"].append("Z")
    tile = max(subs, key=lambda s: max(s["x"]) - min(s["x"]))
    e_parts = [s for s in subs if s is not tile]
    tile_d = "".join(tile["d"])
    e_d = "".join("".join(s["d"]) for s in e_parts)
    logger.info("AI 标识: {:.2f} × {:.2f}pt，E 子路径 {} 段", rect.width, rect.height, len(e_parts))
    return rect.width, rect.height, tile_d, e_d


def earletf_set() -> dict[str, object]:
    w, h, tile_d, e_d = extract_etf_mark()
    official = doc(w, h, f'<path fill="{BLUE}" d="{tile_d}"/><path fill="{WHITE}" d="{e_d}"/>')
    square = doc(w, h, bg(w, h) + f'<path fill="{WHITE}" d="{e_d}"/>')
    cx, cy = w / 2, h / 2
    wechat = doc(
        w, h,
        bg(w, h)
        + f'<g transform="translate({cx:g} {cy:g}) scale({ETF_WECHAT_SCALE:g}) translate({-cx:g} {-cy:g})">'
        f'<path fill="{WHITE}" d="{e_d}"/></g>',
    )
    return {
        "favicon": official,
        "ico": {16: official, 32: official, 48: official},
        "square": square,
        "wechat": wechat,
        "masters": {"official-tile.svg": official, "square.svg": square, "wechat.svg": wechat},
    }


def raster(svg_text: str, size: int, out: Path, tmp: Path) -> Path:
    src = tmp / f"{out.stem}-{size}.svg"
    src.write_text(svg_text, encoding="utf-8")
    subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size), str(src), "-o", str(out)], check=True)
    return out


def to_jpg(png: Path, jpg: Path) -> None:
    Image.open(png).convert("RGB").save(jpg, quality=95, subsampling=0)


def write_ico(frames: list[tuple[int, bytes]], out: Path) -> None:
    header = struct.pack("<HHH", 0, 1, len(frames))
    offset = 6 + 16 * len(frames)
    entries = b""
    blobs = b""
    for size, data in frames:
        entries += struct.pack("<BBBBHHII", size, size, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
        blobs += data
    out.write_bytes(header + entries + blobs)


def emit(out: Path, *, favicon: str, ico: dict[int, str], square: str, wechat: str, masters: dict[str, object]) -> None:
    src = out / "source"
    src.mkdir(parents=True, exist_ok=True)
    for name, text in masters.items():
        (src / name).write_text(str(text), encoding="utf-8")
    (out / "favicon.svg").write_text(favicon, encoding="utf-8")

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        try:
            f16 = raster(favicon, 16, out / "favicon-16x16.png", tmp)
            f32 = raster(favicon, 32, out / "favicon-32x32.png", tmp)
            frames = [(16, f16.read_bytes()), (32, f32.read_bytes())]
            for size, text in ico.items():
                if size in (16, 32):
                    continue
                frames.append((size, raster(text, size, tmp / f"ico-{size}.png", tmp).read_bytes()))
            frames.sort(key=lambda f: f[0])
            write_ico(frames, out / "favicon.ico")
            raster(square, 180, out / "apple-touch-icon.png", tmp)
            raster(square, 192, out / "android-chrome-192x192.png", tmp)
            raster(square, 512, out / "android-chrome-512x512.png", tmp)
            to_jpg(raster(wechat, 1080, tmp / "wechat-1080.png", tmp), out / "wechat-avatar-1080.jpg")
        except (subprocess.CalledProcessError, OSError) as e:
            logger.error("{} 素材生成失败: {}", out.name, e)
            raise SystemExit(1) from e
    logger.success("{} 素材已输出到 {}", out.name, out.relative_to(DESIGN.parent.parent))


def og_square() -> str:
    k = 30
    tx, ty = 600 - 8 * k, 470 - 8 * k
    text = (
        f'<text x="600" y="800" text-anchor="middle" fill="{WHITE}" font-family="Helvetica Neue, sans-serif" '
        f'font-weight="700" font-size="150" letter-spacing="-2">EarlMind</text>'
        f'<text x="600" y="890" text-anchor="middle" fill="{WHITE}" fill-opacity=".8" '
        f'font-family="HarmonyOS Sans SC, Helvetica Neue, sans-serif" font-weight="500" font-size="42">'
        f"一半是对算力的好奇，一半是对生活的偏见</text>"
        f'<text x="600" y="1040" text-anchor="middle" fill="{WHITE}" fill-opacity=".5" '
        f'font-family="Menlo, Andale Mono, monospace" font-size="30" letter-spacing="8">earlmind.com</text>'
    )
    grid = (
        f'<defs><pattern id="px" width="60" height="60" patternUnits="userSpaceOnUse">'
        f'<path d="M60 0H0V60" fill="none" stroke="{WHITE}" stroke-opacity=".07" stroke-width="2"/></pattern></defs>'
        f'<rect width="600" height="1200" fill="url(#px)"/>'
    )
    mark = f'<g transform="translate({tx} {ty}) scale({k})">{mind_mark(scanline=True)}</g>'
    return doc(1200, 1200, bg(1200, 1200) + grid + mark + text)


def write_og(out: Path) -> None:
    og = og_square()
    src = out / "source"
    src.mkdir(parents=True, exist_ok=True)
    (src / "og-image.svg").write_text(og, encoding="utf-8")
    with tempfile.TemporaryDirectory() as td:
        raster(og, 1200, out / "og-image.png", Path(td))
    logger.success("OG 已输出到 {}", (out / "og-image.png").relative_to(DESIGN.parent.parent))


def main() -> None:
    try:
        mind = earlmind_set()
        emit(DESIGN / "earlmind", **mind)
        write_og(DESIGN / "earlmind")
        etf = earletf_set()
        emit(DESIGN / "earletf", **etf)
    except ValueError as e:
        logger.error("{}", e)
        raise SystemExit(1) from e


if __name__ == "__main__":
    main()
