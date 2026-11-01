"""Helpers for running the project's git hooks inside throwaway repositories."""

import os
import shutil
import stat
import subprocess
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
VENV_BIN = Path(sys.executable).parent

# Stands in for `uv run [options] <tool> [args]` by running <tool> from this
# project's virtual environment, so tests need no network and no fresh venv.
UV_SHIM = f"""#!/bin/sh
[ "$1" = run ] || {{ echo "uv shim: only 'run' is supported" >&2; exit 99; }}
shift
while [ "${{1#-}}" != "$1" ]; do shift; done
tool=$1
shift
PATH="{VENV_BIN}:$PATH" exec "{VENV_BIN}/$tool" "$@"
"""

GIT_IDENTITY = {
    "GIT_AUTHOR_NAME": "Test",
    "GIT_AUTHOR_EMAIL": "test@example.invalid",
    "GIT_COMMITTER_NAME": "Test",
    "GIT_COMMITTER_EMAIL": "test@example.invalid",
}


def _make_executable(path: Path) -> None:
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def path_without_uv(bin_dir: Path) -> str:
    """Build a PATH with every executable of the current PATH except `uv`."""
    bin_dir.mkdir(parents=True, exist_ok=True)
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        if not directory or not Path(directory).is_dir():
            continue
        for entry in Path(directory).iterdir():
            target = bin_dir / entry.name
            if entry.name == "uv" or target.exists() or target.is_symlink():
                continue
            target.symlink_to(entry)
    return str(bin_dir)


@dataclass(frozen=True)
class HookRepo:
    """A temporary git repository with selected project hooks installed."""

    root: Path
    env: Mapping[str, str]

    def git(self, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=self.root,
            env=dict(self.env),
            capture_output=True,
            text=True,
            check=check,
        )

    def write(self, relative: str, content: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path


def make_hook_repo(
    tmp_path: Path,
    hooks: tuple[str, ...],
    *,
    with_uv: bool = True,
    pyproject: str | None = None,
) -> HookRepo:
    root = tmp_path / "repo"
    root.mkdir()
    hooks_dir = root / ".githooks"
    hooks_dir.mkdir()
    helpers = [path.name for path in (PROJECT_ROOT / ".githooks").glob("*.sh")]
    for name in (*hooks, *helpers):
        shutil.copy2(PROJECT_ROOT / ".githooks" / name, hooks_dir / name)
    (root / "pyproject.toml").write_text(
        pyproject
        if pyproject is not None
        else (PROJECT_ROOT / "pyproject.toml").read_text()
    )

    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_IDENTITY)
    if with_uv:
        shim_dir = tmp_path / "shim"
        shim_dir.mkdir()
        shim = shim_dir / "uv"
        shim.write_text(UV_SHIM)
        _make_executable(shim)
        env["PATH"] = f"{shim_dir}{os.pathsep}{env.get('PATH', '')}"
    else:
        env["PATH"] = path_without_uv(tmp_path / "bin-without-uv")

    repo = HookRepo(root=root, env=env)
    repo.git("init", "-q", "-b", "main")
    repo.git("config", "core.hooksPath", ".githooks")
    return repo
