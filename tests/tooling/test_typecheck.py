"""The whole project type-checks cleanly with pyright."""

import subprocess
import sys

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
