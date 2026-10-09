#!/bin/bash
# Stop hook: verify the import-linter architecture contracts once per turn.
# The import graph only changes when imports do, so running this per edit is
# wasted work, but CI enforces it, so it runs before the turn ends. Fires only
# when backend Python files are dirty.

input=$(cat)

# Claude Code sets this when the stop was already blocked once; bail so we can't loop.
[[ "$(jq -r '.stop_hook_active // false' <<<"$input" 2>/dev/null)" == "true" ]] && exit 0

root="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[[ -z "$root" ]] && exit 0

git -C "$root" status --porcelain -- backend 2>/dev/null | grep -q '\.py$' || exit 0

output=$(cd "$root/backend" && uv run lint-imports 2>&1)
if [[ $? -ne 0 ]]; then
  {
    echo "Import-linter contracts are broken. Fix these before finishing:"
    sed -n '/Broken contracts/,$p' <<<"$output" | head -40
  } >&2
  exit 2
fi

exit 0
