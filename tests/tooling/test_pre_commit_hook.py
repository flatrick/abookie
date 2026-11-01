"""The pre-commit hook auto-formats staged Python files and aborts on changes."""

from pathlib import Path

import pytest

from tests.tooling.hookrepo import HookRepo, make_hook_repo

pytestmark = pytest.mark.tooling

MISFORMATTED = (
    "import sys\nimport os\ndef f( x ):\n  return os.path.join(sys.prefix,x)\n"
)
CLEAN = 'def greet(name: str) -> str:\n    return f"hello {name}"\n'


def _repo(tmp_path: Path, *, with_uv: bool = True) -> HookRepo:
    repo = make_hook_repo(tmp_path, ("pre-commit",), with_uv=with_uv)
    repo.git("add", "pyproject.toml", ".githooks")
    repo.git("commit", "-q", "--no-verify", "-m", "chore: base")
    return repo


def test_misformatted_staged_file_is_fixed_and_commit_aborted(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    path = repo.write("pkg/bad.py", MISFORMATTED)
    repo.git("add", "pkg/bad.py")

    result = repo.git("commit", "-m", "feat: add bad", check=False)

    assert result.returncode != 0
    assert "pkg/bad.py" in result.stderr
    assert "re-stage" in result.stderr
    fixed = path.read_text()
    assert fixed.startswith("import os\nimport sys\n")
    assert "def f(x):\n    return" in fixed
    assert repo.git("rev-list", "--count", "HEAD").stdout.strip() == "1"


def test_clean_commit_passes(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    repo.write("pkg/good.py", CLEAN)
    repo.git("add", "pkg/good.py")

    result = repo.git("commit", "-m", "feat: add good", check=False)

    assert result.returncode == 0, result.stderr
    assert repo.git("rev-list", "--count", "HEAD").stdout.strip() == "2"


def test_unstaged_files_are_left_alone(tmp_path: Path) -> None:
    repo = _repo(tmp_path)
    untouched = repo.write("pkg/untracked_bad.py", MISFORMATTED)
    repo.write("pkg/good.py", CLEAN)
    repo.git("add", "pkg/good.py")

    result = repo.git("commit", "-m", "feat: add good", check=False)

    assert result.returncode == 0, result.stderr
    assert untouched.read_text() == MISFORMATTED


def test_without_uv_hook_warns_and_allows_commit(tmp_path: Path) -> None:
    repo = _repo(tmp_path, with_uv=False)
    repo.write("pkg/bad.py", MISFORMATTED)
    repo.git("add", "pkg/bad.py")

    result = repo.git("commit", "-m", "feat: add bad", check=False)

    assert result.returncode == 0, result.stderr
    assert "uv" in result.stderr
    assert "skipped" in result.stderr
