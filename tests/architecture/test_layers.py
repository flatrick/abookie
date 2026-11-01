"""The layer boundaries (core / ui / platform) hold, checked by import-linter."""

import subprocess

import pytest

from tests.tooling.hookrepo import PROJECT_ROOT, VENV_BIN

pytestmark = pytest.mark.unit


def test_import_contracts_hold() -> None:
    result = subprocess.run(
        [str(VENV_BIN / "lint-imports"), "--no-cache"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "Contracts: 2 kept, 0 broken" in output
