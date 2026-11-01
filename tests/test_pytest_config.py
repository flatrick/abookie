"""The pytest and coverage configuration matches the project's testing rules."""

import os
import tomllib
from pathlib import Path

import pytest

PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"


def _registered_marker_names(config: pytest.Config) -> set[str]:
    lines: list[str] = config.getini("markers")
    return {line.split(":", 1)[0].strip() for line in lines}


def test_markers_registered(pytestconfig: pytest.Config) -> None:
    assert {"unit", "integration", "ui", "tooling"} <= _registered_marker_names(
        pytestconfig
    )


def test_strict_markers_enabled(pytestconfig: pytest.Config) -> None:
    assert pytestconfig.getoption("strict_markers")


def test_qt_runs_offscreen() -> None:
    assert os.environ.get("QT_QPA_PLATFORM") == "offscreen"


def test_coverage_floor_is_80() -> None:
    coverage = tomllib.loads(PYPROJECT.read_text())["tool"]["coverage"]
    assert coverage["report"]["fail_under"] == 80
    assert "src/abookie/app/*" in coverage["run"]["omit"]


def test_pytest_measures_coverage_of_the_package(pytestconfig: pytest.Config) -> None:
    assert "abookie" in (pytestconfig.getoption("cov_source") or [])
