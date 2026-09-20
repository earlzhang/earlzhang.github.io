#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

for cmd in git hugo wrangler; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "错误: 未找到 $cmd 命令，请先安装。"
    exit 1
  fi
done

cd "${SCRIPT_DIR}"

echo "正在添加文件..."
git add .

echo "正在提交更改..."
git commit -m "Update blog content"

echo "正在拉取远程更改..."
git pull --rebase

echo "正在推送到 GitHub..."
git push

echo "正在构建 Hugo 站点..."
hugo --config hugo.toml --minify

echo "正在部署到 Cloudflare Pages..."
# 先触发一次 whoami 让 wrangler 静默刷新 OAuth token，再取出作为 API token 使用
if ! wrangler whoami >/dev/null 2>&1; then
  echo "错误: wrangler 未登录或登录已过期，请先运行 wrangler login 后重试。"
  exit 1
fi
WRANGLER_CONF="$HOME/Library/Preferences/.wrangler/config/default.toml"
export CLOUDFLARE_API_TOKEN="$(sed -n 's/^oauth_token = "\(.*\)"/\1/p' "$WRANGLER_CONF")"
export CLOUDFLARE_ACCOUNT_ID="f44fa8564dc0270da8eb3b69daa20c57"
wrangler pages deploy public --project-name earlmind --branch main --commit-hash "$(git rev-parse --short HEAD)"

echo "推送完成！已部署到 https://earlmind.com"
