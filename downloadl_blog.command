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
  read -q "REPLY?继续执行强制同步吗？(将丢弃本地改动，强制以远端覆盖本地) [y/N]: "
  echo ""
  if [[ "${REPLY}" != "y" && "${REPLY}" != "Y" ]]; then
    echo "已取消拉取。"
    exit 0
  fi
fi

echo "正在从远端拉取最新内容..."

git fetch --prune

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [[ -z "${CURRENT_BRANCH}" || "${CURRENT_BRANCH}" == "HEAD" ]]; then
  echo "错误: 无法确定当前分支(可能处于 detached HEAD 状态)，无法执行强制同步。"
  exit 1
fi

git reset --hard "origin/${CURRENT_BRANCH}"
git clean -fdx

echo "拉取完成！"
