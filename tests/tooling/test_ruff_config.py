"""The project ruff config catches formatting and lint problems."""

import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

pytestmark = pytest.mark.tooling

PROJECT_CONFIG = Path(__file__).resolve().parents[2] / "pyproject.toml"

BAD_SOURCE = """import sys
import os
def f( x ):
  if x == None:
    return sys.prefix
  return os.path.join(sys.prefix,x)
"""


def _ruff(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "ruff", *args, "--config", str(PROJECT_CONFIG), "."],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture
def bad_file(tmp_path: Path) -> Path:
    path = tmp_path / "bad.py"
    path.write_text(BAD_SOURCE)
    return path


def test_format_check_reports_badly_formatted_code(bad_file: Path) -> None:
    result = _ruff("format", "--check", cwd=bad_file.parent)
    assert result.returncode == 1
    assert "bad.py" in result.stdout


def test_lint_reports_unsorted_imports(bad_file: Path) -> None:
    result = _ruff("check", "--no-cache", cwd=bad_file.parent)
    assert result.returncode == 1
    assert "I001" in result.stdout


def test_lint_reports_rules_outside_ruff_defaults(bad_file: Path) -> None:
    # E711 (comparison to None) is in the selected E set but not in ruff's defaults.
    result = _ruff("check", "--no-cache", cwd=bad_file.parent)
    assert "E711" in result.stdout


def test_config_pins_target_indent_and_rule_sets() -> None:
    ruff = tomllib.loads(PROJECT_CONFIG.read_text())["tool"]["ruff"]
    assert ruff["target-version"] == "py312"
    assert ruff["indent-width"] == 4
    assert {"E", "F", "I", "UP", "B", "SIM"} <= set(ruff["lint"]["select"])
