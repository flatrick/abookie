"""The composition root reports missing system dependencies without a traceback."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from abookie.app.main import main
from abookie.platform.sysdeps import DependencyCheck

pytestmark = pytest.mark.integration

MISSING = DependencyCheck(
    missing="libmpv", message="libmpv missing: sudo pacman -S mpv"
)


def _missing_libmpv_env(tmp_path: Path) -> dict[str, str]:
    """Environment in which `import mpv` fails as it does without libmpv."""
    shadow = tmp_path / "shadow"
    shadow.mkdir()
    (shadow / "mpv.py").write_text('raise OSError("Cannot find libmpv")\n')
    env = {
        k: v for k, v in os.environ.items() if k not in ("DISPLAY", "WAYLAND_DISPLAY")
    }
    env["PYTHONPATH"] = str(shadow)
    return env


def test_main_exits_cleanly_when_libmpv_missing(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "abookie"],
        env=_missing_libmpv_env(tmp_path),
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )

    assert result.returncode == 1
    assert "libmpv" in result.stderr
    assert "sudo pacman -S mpv" in result.stderr
    assert "Traceback" not in result.stderr


def test_missing_dependency_is_shown_in_dialog_when_display_available(
    capsys: pytest.CaptureFixture[str],
) -> None:
    shown: list[str] = []

    code = main(
        check_dependencies=lambda: MISSING,
        display_available=lambda: True,
        show_error_dialog=shown.append,
    )

    assert code == 1
    assert shown == [MISSING.message]
    assert MISSING.message in capsys.readouterr().err


def test_no_dialog_without_display(capsys: pytest.CaptureFixture[str]) -> None:
    shown: list[str] = []

    code = main(
        check_dependencies=lambda: MISSING,
        display_available=lambda: False,
        show_error_dialog=shown.append,
    )

    assert code == 1
    assert shown == []
    assert MISSING.message in capsys.readouterr().err
