#!/usr/bin/env bash
set -euo pipefail

printf '%s\n' '安全提示：无需粘贴 TikHub Key。'

if command -v uv >/dev/null 2>&1; then
  uv --version
  exit 0
fi

if command -v brew >/dev/null 2>&1; then
  brew install uv
  uv --version
  exit 0
fi

printf '%s\n' 'Homebrew 未安装。请审阅并自行执行：curl -LsSf https://astral.sh/uv/install.sh | sh'
exit 1
