#!/bin/bash
# Stop hook: knip (unused files, exports, dependencies) and dependency-cruiser
# (module boundaries) over the frontend. Dead code only shows up once a change
# is complete, so this runs per turn rather than per edit. Fires only when
# frontend sources or package.json are dirty. CI runs the same checks.

input=$(cat)

# Claude Code sets this when the stop was already blocked once; bail so we can't loop.
[[ "$(jq -r '.stop_hook_active // false' <<<"$input" 2>/dev/null)" == "true" ]] && exit 0

root="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null)}"
[[ -z "$root" ]] && exit 0

git -C "$root" status --porcelain -- frontend 2>/dev/null |
  grep -qE '\.(ts|tsx)$|package\.json$' || exit 0

# Binaries hoist to the workspace root. Skip quietly when deps are not
# installed, so a fresh clone does not fail every turn.
bin="$root/node_modules/.bin"
[[ -x "$bin/knip" && -x "$bin/tsr" && -x "$bin/depcruise" ]] || exit 0

# The route tree has to be current, or every route file looks unreachable.
(cd "$root/frontend" && "$bin/tsr" generate) >/dev/null 2>&1

report=""

if ! output=$(cd "$root/frontend" && "$bin/knip" --no-progress 2>&1); then
  report+="Knip found unused code. Delete it, or justify an ignore in frontend/knip.config.ts:"$'\n'
  report+="$(head -40 <<<"$output")"$'\n'
fi

if ! output=$(cd "$root/frontend" && "$bin/depcruise" src tests --config .dependency-cruiser.cjs 2>&1); then
  report+="dependency-cruiser found boundary violations (rules in frontend/.dependency-cruiser.cjs):"$'\n'
  report+="$(head -40 <<<"$output")"$'\n'
fi

if [[ -n "$report" ]]; then
  printf '%s' "$report" >&2
  exit 2
fi

exit 0
