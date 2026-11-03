#!/usr/bin/env bash
# dev-setup.sh: apply the expected local git settings for this repository.
#
# Run it once in each clone. You can run it again at any time; it is safe.
# It changes only the repository config (.git/config), never your global config.
#
# The settings:
#   core.hooksPath        .githooks  Turns on the project git hooks.
#   merge.ff              only       A merge can only fast-forward.
#   pull.ff               only       A pull can only fast-forward.
#   rebase.autosquash     true       Rebase applies fixup! and squash! commits.
#   rebase.autostash      true       Rebase stashes local edits and restores them.
#   rebase.updaterefs     true       Rebase moves stacked branches too.
#   push.autoSetupRemote  true       The first push sets the upstream branch.
set -euo pipefail

if ! root=$(git rev-parse --show-toplevel 2>/dev/null); then
    echo "dev-setup: not a git repository; run this script inside a clone" >&2
    exit 1
fi
cd "$root"

settings=(
    "core.hooksPath .githooks"
    "merge.ff only"
    "pull.ff only"
    "rebase.autosquash true"
    "rebase.autostash true"
    "rebase.updaterefs true"
    "push.autoSetupRemote true"
)

for entry in "${settings[@]}"; do
    read -r key value <<<"$entry"
    git config --local "$key" "$value"
    printf '  %-22s %s\n' "$key" "$value"
done
echo "dev-setup: local git settings applied."

for tool in uv gir; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "dev-setup: warning: $tool is not installed; see README.md" >&2
    fi
done
echo "Next step: run 'uv sync' to create the virtual environment."
