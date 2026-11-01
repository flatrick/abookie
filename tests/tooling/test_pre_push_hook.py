"""The pre-push hook blocks pushes that fail lint, format, type or test checks."""

from pathlib import Path

import pytest

from tests.tooling.hookrepo import HookRepo, make_hook_repo

pytestmark = pytest.mark.tooling

MINI_PYPROJECT = """\
[tool.ruff]
target-version = "py312"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "UP", "B", "SIM"]

[tool.pyright]
include = ["."]
typeCheckingMode = "basic"

[tool.pytest.ini_options]
testpaths = ["tests"]
"""

GOOD_MODULE = 'def greet(name: str) -> str:\n    return f"hello {name}"\n'
GOOD_TEST = "def test_ok() -> None:\n    assert sum([1, 1]) == 2\n"

FAILING_FILES = {
    "lint": ("pkg/lint.py", "import os\n"),
    "format": ("pkg/fmt.py", "x = 'a'\n"),
    "type": ("pkg/typ.py", 'x: int = "a"\n'),
    "test": (
        "tests/test_fail.py",
        "def test_fail() -> None:\n    assert sum([1]) == 2\n",
    ),
}


def _repo(tmp_path: Path, *, with_uv: bool = True) -> HookRepo:
    repo = make_hook_repo(
        tmp_path, ("pre-push",), with_uv=with_uv, pyproject=MINI_PYPROJECT
    )
    repo.write("pkg/__init__.py", "")
    repo.write("pkg/good.py", GOOD_MODULE)
    repo.write("tests/test_ok.py", GOOD_TEST)
    repo.git("add", ".")
    repo.git("commit", "-q", "--no-verify", "-m", "chore: base")
    remote = tmp_path / "remote.git"
    repo.git("init", "-q", "--bare", str(remote))
    repo.git("remote", "add", "origin", str(remote))
    return repo


def _remote_has_main(repo: HookRepo) -> bool:
    return repo.git("ls-remote", "origin", "main").stdout.strip() != ""


def test_push_allowed_when_all_checks_pass(tmp_path: Path) -> None:
    repo = _repo(tmp_path)

    result = repo.git("push", "-q", "origin", "main", check=False)

    assert result.returncode == 0, result.stderr
    assert _remote_has_main(repo)


@pytest.mark.parametrize("check", sorted(FAILING_FILES))
def test_push_blocked_when_a_check_fails(tmp_path: Path, check: str) -> None:
    repo = _repo(tmp_path)
    relative, content = FAILING_FILES[check]
    repo.write(relative, content)
    repo.git("add", ".")
    repo.git("commit", "-q", "--no-verify", "-m", f"test: break {check}")

    result = repo.git("push", "-q", "origin", "main", check=False)

    assert result.returncode != 0
    assert not _remote_has_main(repo)
    assert check in result.stderr


def test_without_uv_checks_are_skipped_with_warning(tmp_path: Path) -> None:
    repo = _repo(tmp_path, with_uv=False)
    repo.write(*FAILING_FILES["lint"])
    repo.git("add", ".")
    repo.git("commit", "-q", "--no-verify", "-m", "test: break lint")

    result = repo.git("push", "-q", "origin", "main", check=False)

    assert result.returncode == 0, result.stderr
    assert "uv not installed" in result.stderr
    assert _remote_has_main(repo)
