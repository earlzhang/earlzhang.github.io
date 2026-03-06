#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if ! command -v git >/dev/null 2>&1; then
  echo "错误: 未找到 git 命令，请先安装 Git。"
  exit 1
fi

cd "${SCRIPT_DIR}"

echo "正在添加文件..."
git add .

echo "正在提交更改..."
git commit -m "Update blog content"

echo "正在拉取远程更改..."
git pull --rebase

echo "正在推送到 GitHub..."
git push

echo "推送完成！"
