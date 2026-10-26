#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

for cmd in git hugo wrangler uv npx; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "错误: 未找到 $cmd 命令，请先安装。"
    exit 1
  fi
done

cd "${SCRIPT_DIR}"

# 先把文章里引用的本地图片上传到 OSS 并改写为远程 URL，
# 无本地图片时脚本立即退出；上传失败则中断，避免发布失效引用。
echo "正在检查本地图片并上传至 OSS..."
uv run "${SCRIPT_DIR}/upload_post_images.py"

echo "正在添加文件..."
git add .

echo "正在提交更改..."
git commit -m "Update blog content"

echo "正在拉取远程更改..."
git pull --rebase

echo "正在推送到 GitHub..."
git push

echo "正在构建 Hugo 站点..."
hugo --config hugo.toml --minify --cleanDestinationDir

echo "正在生成 Pagefind 搜索索引..."
npx -y pagefind@1.5.2 --site "${SCRIPT_DIR}/public"
# 删除未使用的 UI 变体（站点用 Default UI），减少约 240K 部署体积
rm -f "${SCRIPT_DIR}"/public/pagefind/pagefind-component-ui.* "${SCRIPT_DIR}"/public/pagefind/pagefind-modular-ui.*

echo "正在部署到 Cloudflare Pages..."

# Cloudflare API 直连在本机不稳定，本地代理可用则自动启用；
# 依次实测 Clash/Mihomo(7897) 与 MonoProxy(8118 http / 8119 socks5)——用真实代理请求验证，
# 而非 nc 探测端口：TUN/增强模式可能接走连接却不提供有效代理，造成假阳性。均不可用则回落直连。
PROXY_OK=""
for spec in "http://127.0.0.1:7897 socks5://127.0.0.1:7897" "http://127.0.0.1:8118 socks5://127.0.0.1:8119"; do
  http_p="${spec%% *}"; socks_p="${spec##* }"
  if curl -s -o /dev/null --connect-timeout 2 --max-time 4 -x "$http_p" https://dash.cloudflare.com 2>/dev/null; then
    export http_proxy="$http_p"
    export https_proxy="$http_p"
    export all_proxy="$socks_p"
    echo "检测到可用代理 ${http_p}，经代理访问 Cloudflare"
    PROXY_OK=1
    break
  fi
done
if [ -z "$PROXY_OK" ]; then
  # 无可用代理：清掉环境中可能残留的死代理变量，回落直连
  unset http_proxy https_proxy all_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY
fi

# wrangler access_token 有效期约 1 小时。用 refresh_token 换新 token 并回写配置
# （refresh_token 每次刷新会轮换，必须回写否则登录链断裂）。
WRANGLER_CONFS=("$HOME/.wrangler/config/default.toml" "$HOME/Library/Preferences/.wrangler/config/default.toml")
WRANGLER_CONF=""
for f in "${WRANGLER_CONFS[@]}"; do
  [ -f "$f" ] && WRANGLER_CONF="$f" && break
done
if [ -z "$WRANGLER_CONF" ]; then
  echo "错误: 未找到 wrangler 登录配置，请先运行 wrangler login。"
  exit 1
fi

REFRESH_TOKEN="$(sed -n 's/^refresh_token = "\(.*\)"/\1/p' "$WRANGLER_CONF")"
RESPONSE="$(curl -s -X POST "https://dash.cloudflare.com/oauth2/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "grant_type=refresh_token" \
  --data-urlencode "refresh_token=${REFRESH_TOKEN}" \
  --data-urlencode "client_id=54d11594-84e4-41aa-b438-e81b8fa78ee7" \
  --max-time 30)"
NEW_TOKEN="$(echo "$RESPONSE" | sed -n 's/.*"access_token":"\([^"]*\)".*/\1/p')"
NEW_REFRESH="$(echo "$RESPONSE" | sed -n 's/.*"refresh_token":"\([^"]*\)".*/\1/p')"

if [ -z "$NEW_TOKEN" ]; then
  echo "错误: Cloudflare 登录态已失效，请先运行 wrangler login 后重试。"
  exit 1
fi

# 回写新 token 到所有已存在的 wrangler 配置文件
NEW_EXPIRY="$(date -u -v+3600S '+%Y-%m-%dT%H:%M:%S.000Z')"
for f in "${WRANGLER_CONFS[@]}"; do
  [ -f "$f" ] || continue
  sed -i '' "s|^oauth_token = \".*\"|oauth_token = \"$NEW_TOKEN\"|" "$f"
  sed -i '' "s|^refresh_token = \".*\"|refresh_token = \"$NEW_REFRESH\"|" "$f"
  sed -i '' "s|^expiration_time = \".*\"|expiration_time = \"$NEW_EXPIRY\"|" "$f"
done

export CLOUDFLARE_API_TOKEN="$NEW_TOKEN"
export CLOUDFLARE_ACCOUNT_ID="f44fa8564dc0270da8eb3b69daa20c57"
wrangler pages deploy public --project-name earlmind --branch main --commit-hash "$(git rev-parse --short HEAD)"

echo "推送完成！已部署到 https://earlmind.com"

# 部署完成，打开网站确认线上状态
open "https://earlmind.com"
