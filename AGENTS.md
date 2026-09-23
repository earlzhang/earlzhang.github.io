# EarlMind 博客（Hugo + PaperMod）

## 项目基本情况

- 基于 **Hugo** 的个人博客，主题为 **PaperMod**（位于 `themes/PaperMod`，主题文件不要直接修改；自定义内容放在根目录 `layouts/` 覆盖）。
- 站点配置：`hugo.toml`（baseURL 为 https://earlmind.com/ ，语言 zh-cn，时区 Asia/Shanghai）。
- 文章目录：`content/posts/<年份>/YYYY-MM-DD.md`，永久链接格式为 `/:year/:contentbasename/`。
- 部署目标：**Cloudflare Pages**（项目名 `earlmind`，生产分支 `main`），由本地 `public/` 构建产物直接部署，GitHub 仓库仅作源码备份。
- Google Analytics ID：`G-BBE8BTPTWL`（配置在 `hugo.toml`）。

## 常用脚本（双击运行或命令行执行）

| 脚本 | 作用 |
| --- | --- |
| `new_hugo_post.command` | 在 `content/posts/<当年>/` 下按当天日期新建文章草稿 |
| `start_hugo_server.command` | 本地预览（http://localhost:1313/ ，`hugo server -D`） |
| `push_blog.command` | 一键发布：git 提交推送 → Hugo 构建 → 部署到 Cloudflare Pages |
| `downloadl_blog.command` | 拉取远程仓库最新内容 |

## 如何发布

优先运行 `./push_blog.command`，它会依次完成：

1. `git add .` + 提交（"Update blog content"）+ `git pull --rebase` + `git push`
2. `hugo --config hugo.toml --minify` 构建到 `public/`
3. 刷新 Cloudflare OAuth token（refresh_token 会轮换，脚本自动回写到 wrangler 配置）
4. `wrangler pages deploy public --project-name earlmind --branch main`

注意事项：

- 脚本开了 `set -euo pipefail`，若工作区无改动，`git commit` 会失败并中断，此时可手动执行构建和部署部分。
- 访问 Cloudflare 不稳定时，脚本会自动检测本地代理（Clash/Mihomo，127.0.0.1:7897）并启用。
- wrangler access_token 有效期约 1 小时，过期需先运行 `wrangler login`。

手动发布（等价命令）：

```bash
hugo --config hugo.toml --minify
wrangler pages deploy public --project-name earlmind --branch main --commit-hash "$(git rev-parse --short HEAD)"
```

## 如何增加页面底部链接

底部链接区由 `layouts/partials/extend_footer.html` 定义（覆盖 PaperMod 同名 partial），当前包含 Email 图标、SVGArena、大模型谄媚榜单等链接。

新增一个链接时，在 `<div>` 内追加（各链接之间用 `<span>·</span>` 分隔，样式保持一致）：

```html
<span>·</span>
<a href="https://example.com/" target="_blank" rel="noopener noreferrer" title="名称" style="color: inherit; border-bottom: 1px solid var(--secondary);">名称</a>
```

改完后按「如何发布」流程构建部署即可生效。

## Git 提交规范

- 遵循 Conventional Commits（`feat`、`fix`、`docs` 等），按功能模块原子提交，禁止 `git add .` 混提多个领域（`push_blog.command` 内部的 `git add .` 除外，那是既有脚本行为）。
- 本地完成全部分步提交后，最后统一执行一次 push。
