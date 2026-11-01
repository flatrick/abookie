#!/usr/bin/env bash
# Used by pre-push (can also be run by hand): run every project check and fail if any of them fails.
#
# Checks: ruff lint, ruff format, pyright, and pytest (which enforces the
# coverage floor through the pytest config). All checks run, even after a
# failure, so one push attempt reports every problem.
#
# Skipped with a warning when uv is not installed.
set -uo pipefail

if ! command -v uv >/dev/null 2>&1; then
    echo "pre-push: uv not installed, lint/format/type/test checks skipped" >&2
    exit 0
fi

cd "$(git rev-parse --show-toplevel)" || exit 1

failed=()

run_check() {
    local name=$1
    shift
    echo "pre-push: running $name check" >&2
    if ! "$@" >&2; then
        failed+=("$name")
    fi
}

run_check lint uv run --frozen ruff check .
run_check format uv run --frozen ruff format --check .
run_check type uv run --frozen pyright
run_check test uv run --frozen pytest

if [ "${#failed[@]}" -gt 0 ]; then
    echo "pre-push: push blocked, failed checks: ${failed[*]}" >&2
    exit 1
fi
