"""Whether a graphical dialog can be shown in the current environment."""

import pytest

from abookie.platform.display import display_available

pytestmark = pytest.mark.unit


@pytest.mark.parametrize(
    ("environ", "expected"),
    [
        ({"DISPLAY": ":0"}, True),
        ({"WAYLAND_DISPLAY": "wayland-0"}, True),
        ({}, False),
        ({"DISPLAY": ""}, False),
        ({"DISPLAY": ":0", "QT_QPA_PLATFORM": "offscreen"}, False),
        ({"DISPLAY": ":0", "QT_QPA_PLATFORM": "minimal"}, False),
    ],
)
def test_display_available_on_linux(environ: dict[str, str], expected: bool) -> None:
    assert display_available(environ, platform="linux") is expected


def test_display_assumed_on_desktop_oses_without_x11() -> None:
    assert display_available({}, platform="darwin") is True
    assert display_available({}, platform="win32") is True
