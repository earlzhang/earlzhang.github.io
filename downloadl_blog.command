#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if ! command -v git >/dev/null 2>&1; then
  echo "错误: 未找到 git 命令，请先安装 Git。"
  exit 1
fi

cd "${SCRIPT_DIR}"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "错误: 当前目录不是 Git 仓库: ${SCRIPT_DIR}"
  exit 1
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "警告: 检测到本地有未提交的改动 (包含未跟踪文件/已修改未提交)。"
  git status --short
  echo ""
  read -q "REPLY?继续执行拉取操作吗？(可能触发 rebase/冲突处理) [y/N]: "
  echo ""
  if [[ "${REPLY}" != "y" && "${REPLY}" != "Y" ]]; then
    echo "已取消拉取。"
    exit 0
  fi
fi

echo "正在从远端拉取最新内容..."

git pull --rebase --autostash

echo "拉取完成！"
