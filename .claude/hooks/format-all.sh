#!/bin/bash
# PostToolUse hook: format and check a file after Edit/Write.
# Backend uses ruff + pyright through uv; frontend uses prettier + oxlint
# through npm. Tools must run with the right working directory: bare
# `ruff`/`pyright` are not on PATH.

file_path=$(jq -r '.tool_input.file_path' 2>/dev/null)
[[ -z "$file_path" || "$file_path" == "null" ]] && exit 0

root="${CLAUDE_PROJECT_DIR:-$(git -C "$(dirname "$file_path")" rev-parse --show-toplevel 2>/dev/null)}"
[[ -z "$root" ]] && exit 0

if [[ "$file_path" == "$root/backend/"*.py ]]; then
  (cd "$root/backend" && uv run ruff format "$file_path" && uv run ruff check --fix "$file_path" && uv run pyright "$file_path")
fi

if [[ "$file_path" == "$root/frontend/"* && "$file_path" =~ \.(ts|tsx)$ ]]; then
  (cd "$root/frontend" && npx prettier --write "$file_path" && npx oxlint --type-aware "$file_path")
fi

exit 0
