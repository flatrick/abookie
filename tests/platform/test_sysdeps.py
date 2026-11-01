"""The startup check names a missing libmpv and how to install it."""

import pytest

from abookie.platform.sysdeps import check_libmpv

pytestmark = pytest.mark.unit


def _failing_loader() -> None:
    raise OSError("libmpv.so.2: cannot open shared object file")


def test_reports_missing_libmpv_with_install_hint() -> None:
    result = check_libmpv(loader=_failing_loader)

    assert not result.ok
    assert result.missing == "libmpv"
    message = result.message
    assert "libmpv" in message
    assert "sudo pacman -S mpv" in message
    assert "sudo apt install libmpv2" in message
    assert "sudo dnf install mpv-libs" in message


def test_passes_when_libmpv_loads() -> None:
    result = check_libmpv(loader=lambda: None)

    assert result.ok
    assert result.missing is None
    assert result.message == ""


@pytest.mark.integration
@pytest.mark.usefixtures("libmpv")
def test_default_loader_finds_installed_libmpv() -> None:
    assert check_libmpv().ok
