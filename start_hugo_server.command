#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if ! command -v hugo >/dev/null 2>&1; then
  echo "错误: 未找到 hugo 命令，请先安装 Hugo。"
  exit 1
fi


open "http://localhost:1313/"
cd "${SCRIPT_DIR}"
exec hugo server -D
