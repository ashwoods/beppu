# Worktree setup for beppu: a uv-managed .venv on Python 3.12+.
# Runs in each new worktree (coordinators, workers, the lander) before its first tool call.
[ -f pyproject.toml ] || exit 0
if [ -f uv.lock ]; then
  uv sync --frozen --all-groups
else
  uv sync --all-groups
fi
