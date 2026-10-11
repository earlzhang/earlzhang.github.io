# design/ 目录指引

本目录存放 EarlMind 博客的品牌与视觉设计产物，**与站点构建完全隔离**：Hugo 不读取这里，`push_blog.command` 也不会部署这里的文件。

## 目录结构

```
design/
├── vi-family.html        # 方案预览页（双击即可在浏览器中打开，Canvas 实时绘制）
└── export/
    ├── build_assets.py   # 唯一的素材生成脚本（uv 单文件运行）
    ├── earlmind/         # EarlMind 素材（当前品牌方案：扫描线）
    │   ├── favicon.svg / favicon.ico / favicon-16x16.png / favicon-32x32.png
    │   ├── apple-touch-icon.png (180)
    │   ├── android-chrome-192x192.png / android-chrome-512x512.png
    │   ├── og-image.png (1200×1200，方形分享图)
    │   ├── wechat-avatar-1080.jpg (公众号头像，JPG)
    │   └── source/       # 母版 SVG：favicon-pixel / round-scanline / square-scanline / og-image
    └── earletf/          # EarlETF 素材（字形取自 AI 原稿，暂不做 OG 与网站）
```

## 生成素材

```bash
cd /Users/earlzhang/pycharm/earlzhang_blog
uv run design/export/build_assets.py
```

- 依赖 `rsvg-convert`（`brew install librsvg`）做 SVG 光栅化，脚本通过 `uv` 声明依赖（loguru、pillow、pymupdf==1.28.2）。
- EarlETF 图形从 AI 源文件直接读取矢量路径，路径位于 `~/Library/CloudStorage/坚果云-.../VI/2Logo/VI/EarlETF专业投基之道-定稿.ai`。**不要手工重绘或修改 EarlETF 的字形**，它是用了十年的既有标识。
- EarlMind 的几何与 `vi-family.html` 方案一保持一致，修改时两边要同步。

## 设计约定

- **品牌色**：Earl 蓝 `#043888`（取自 EarlETF 原稿）、纸白 `#F6F7FA`、偏见红 `#F2483C`（仅 EarlMind 使用）。
- **EarlMind 方案**：扫描线。16px 与 32px 使用像素台阶版（`favicon-pixel`），48px 及以上使用扫描线版。
- **微信头像**：会被压缩到约 240px 并裁切为圆形，图形需落在圆内安全区，只用纯色，不用细线和渐变。上传格式仅支持 JPG/BMP/GIF。
- **OG 图**：方形 1200×1200，当前用于站点 `og:image`，不做 Twitter 卡片。
- **字体**：`source/og-image.svg` 依赖本机字体（Helvetica Neue、HarmonyOS Sans SC、Menlo）。在其他机器上重新生成时请先确认字体。不要用 PingFang SC 作为中文字体名，在 macOS 的 rsvg 下会回落到 Verdana。

## 与站点的关系

- 站点实际使用的文件在 `static/brand/` 与 `static/` 根目录，**不是**从本目录自动同步的。需要更新站点时，手动复制对应文件，例如：
  - `design/export/earlmind/favicon.ico` → `static/favicon.ico`
  - `design/export/earlmind/og-image.png` → `static/brand/og-image.png`
- 复制后用 `hugo --config hugo.toml --minify -d /tmp/hugo_check` 验证构建，不要覆盖 `public/`（那是部署产物）。
- `hugo.toml` 中 `[params.assets]` 与 `params.images` 指向 `/brand/` 下的文件名，改文件名需要同步改配置。

## 工作约定

- 新增或修改设计产物时，优先改脚本或母版 SVG，再重新生成，不要直接手改 PNG。
- 不要为了追求家族感而改动已确定的 EarlMind 方案一，方案二、三已被否决。
- 本目录的改动默认不提交。提交时按功能拆分（例如 `feat(brand): ...`、`chore(design): ...`），不要使用 `git add .`。
- 不要把临时文件留在本目录，脚本内的中间文件使用系统临时目录。
