"""The whole project type-checks cleanly with pyright."""

import subprocess
import sys
import tomllib

import pytest

from tests.tooling.hookrepo import PROJECT_ROOT, VENV_BIN

pytestmark = pytest.mark.tooling


def test_pyright_clean() -> None:
    result = subprocess.run(
        [str(VENV_BIN / "pyright"), "--pythonpath", sys.executable],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_production_code_is_strict_and_tests_are_basic() -> None:
    pyright = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text())["tool"][
        "pyright"
    ]
    assert pyright["strict"] == ["src"]
    assert pyright["typeCheckingMode"] == "basic"
    assert "tests" in pyright["include"]
