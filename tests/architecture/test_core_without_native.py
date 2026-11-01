"""Core runs without the playback engine library or a display server.

The core tests are run in a separate interpreter where PySide6 (and its
shiboken6 runtime) cannot be imported, importing mpv fails as it does
without libmpv, and no display is set. Every core module must still import
and every core test must still pass.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from tests.tooling.hookrepo import PROJECT_ROOT

pytestmark = pytest.mark.unit

_UNAVAILABLE = {
    "PySide6/__init__.py": 'raise ImportError("PySide6 unavailable (test)")\n',
    "shiboken6/__init__.py": 'raise ImportError("shiboken6 unavailable (test)")\n',
    "mpv.py": 'raise OSError("libmpv unavailable (test)")\n',
}

_IMPORT_ALL_CORE = """
import importlib, pkgutil
import abookie.core as core
for info in pkgutil.walk_packages(core.__path__, "abookie.core."):
    importlib.import_module(info.name)
print("imported core")
"""


def _environment_without_natives(tmp_path: Path) -> dict[str, str]:
    shadow = tmp_path / "unavailable"
    for relative, content in _UNAVAILABLE.items():
        path = shadow / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    env = {
        k: v
        for k, v in os.environ.items()
        if k not in ("DISPLAY", "WAYLAND_DISPLAY", "QT_QPA_PLATFORM")
    }
    env["PYTHONPATH"] = str(shadow)
    return env


def _run(args: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def test_natives_are_really_unavailable(tmp_path: Path) -> None:
    env = _environment_without_natives(tmp_path)
    for module in ("PySide6", "mpv"):
        result = _run(["-c", f"import {module}"], env)
        assert result.returncode != 0, f"{module} was importable"


def test_core_modules_import_without_natives(tmp_path: Path) -> None:
    result = _run(["-c", _IMPORT_ALL_CORE], _environment_without_natives(tmp_path))
    assert result.returncode == 0, result.stderr
    assert "imported core" in result.stdout


def test_core_tests_pass_without_natives(tmp_path: Path) -> None:
    result = _run(
        ["-m", "pytest", "tests/core", "-q", "-p", "no:pytest-qt", "--no-cov"],
        _environment_without_natives(tmp_path),
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "passed" in result.stdout
