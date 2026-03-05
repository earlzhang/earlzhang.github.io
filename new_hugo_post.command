#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if ! command -v hugo >/dev/null 2>&1; then
  echo "错误: 未找到 hugo 命令，请先安装 Hugo。"
  exit 1
fi

year="$(date +%Y)"
base_date="$(date +%F)"

posts_dir="${SCRIPT_DIR}/content/posts/${year}"
mkdir -p "${posts_dir}"

filename="${base_date}.md"
relative_path="posts/${year}/${filename}"

if [ -e "${SCRIPT_DIR}/content/${relative_path}" ]; then
  index=2
  while [ -e "${SCRIPT_DIR}/content/posts/${year}/${base_date}-${index}.md" ]; do
    index=$((index + 1))
  done
  filename="${base_date}-${index}.md"
  relative_path="posts/${year}/${filename}"
fi

echo "将创建新文章: ${relative_path}"
(
  cd "${SCRIPT_DIR}"
  hugo new "${relative_path}"
)

echo "创建完成: content/${relative_path}"
open -a "Typora" "${SCRIPT_DIR}/content/${relative_path}"