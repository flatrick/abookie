"""Detect whether a graphical display is available for dialogs."""

import os
import sys
from collections.abc import Mapping

_HEADLESS_QT_PLATFORMS = frozenset({"offscreen", "minimal"})


def display_available(
    environ: Mapping[str, str] = os.environ, platform: str = sys.platform
) -> bool:
    """Return True when a window or dialog can be shown to the user."""
    if environ.get("QT_QPA_PLATFORM") in _HEADLESS_QT_PLATFORMS:
        return False
    if platform.startswith("linux"):
        return bool(environ.get("DISPLAY") or environ.get("WAYLAND_DISPLAY"))
    return True
