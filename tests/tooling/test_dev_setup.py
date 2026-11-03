"""dev-setup.sh applies the repository's expected local git settings."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

from tests.tooling.hookrepo import GIT_IDENTITY, PROJECT_ROOT

pytestmark = pytest.mark.tooling

SCRIPT = PROJECT_ROOT / "dev-setup.sh"

EXPECTED = {
    "core.hookspath": ".githooks",
    "merge.ff": "only",
    "pull.ff": "only",
    "rebase.autosquash": "true",
    "rebase.autostash": "true",
    "rebase.updaterefs": "true",
    "push.autosetupremote": "true",
}


def _env(tmp_path: Path) -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_IDENTITY)
    # Isolate from the developer's global and system git config.
    env["HOME"] = str(tmp_path / "home")
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["XDG_CONFIG_HOME"] = str(tmp_path / "home" / ".config")
    return env


def _repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=root, check=True)
    shutil.copy2(SCRIPT, root / "dev-setup.sh")
    return root


def _run(cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    script = next(p for p in (cwd, *cwd.parents) if (p / "dev-setup.sh").exists())
    return subprocess.run(
        [str(script / "dev-setup.sh")],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def _local_config(root: Path, env: dict[str, str]) -> dict[str, str]:
    out = subprocess.run(
        ["git", "config", "--local", "--list"],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return dict(line.split("=", 1) for line in out.splitlines())


def test_sets_expected_local_settings(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    env = _env(tmp_path)

    result = _run(root, env)

    assert result.returncode == 0, result.stderr
    config = _local_config(root, env)
    for key, value in EXPECTED.items():
        assert config.get(key) == value, key


def test_is_idempotent(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    env = _env(tmp_path)

    first = _run(root, env)
    after_first = _local_config(root, env)
    second = _run(root, env)

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    assert _local_config(root, env) == after_first


def test_works_from_a_subdirectory(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    env = _env(tmp_path)
    sub = root / "src" / "deep"
    sub.mkdir(parents=True)

    result = _run(sub, env)

    assert result.returncode == 0, result.stderr
    assert _local_config(root, env)["merge.ff"] == "only"


def test_non_fast_forward_merge_is_refused_after_setup(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    env = _env(tmp_path)
    assert _run(root, env).returncode == 0

    def git(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args], cwd=root, env=env, capture_output=True, text=True
        )

    git("commit", "-q", "--allow-empty", "--no-verify", "-m", "chore: base")
    git("switch", "-q", "-c", "side")
    git("commit", "-q", "--allow-empty", "--no-verify", "-m", "chore: side")
    git("switch", "-q", "main")
    git("commit", "-q", "--allow-empty", "--no-verify", "-m", "chore: main")

    result = git("merge", "side")

    assert result.returncode != 0
    assert "fast-forward" in result.stderr


def test_fails_outside_a_git_repository(tmp_path: Path) -> None:
    outside = tmp_path / "plain"
    outside.mkdir()
    shutil.copy2(SCRIPT, outside / "dev-setup.sh")
    env = _env(tmp_path)
    env["GIT_CEILING_DIRECTORIES"] = str(tmp_path)

    result = _run(outside, env)

    assert result.returncode != 0
    assert "not a git repository" in result.stderr
