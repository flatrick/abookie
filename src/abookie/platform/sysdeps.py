"""Startup checks for required system (native) dependencies."""

import importlib
from collections.abc import Callable
from dataclasses import dataclass

# Keep in sync with the "System dependency: libmpv" table in README.md.
LIBMPV_INSTALL_COMMANDS: tuple[tuple[str, str], ...] = (
    ("Arch Linux", "sudo pacman -S mpv"),
    ("Debian/Ubuntu", "sudo apt install libmpv2"),
    ("Fedora", "sudo dnf install mpv-libs"),
)


@dataclass(frozen=True)
class DependencyCheck:
    """Outcome of a system dependency check."""

    missing: str | None = None
    message: str = ""

    @property
    def ok(self) -> bool:
        return self.missing is None


def _load_libmpv() -> None:
    # python-mpv loads libmpv when imported and raises OSError if it cannot.
    importlib.import_module("mpv")


def _libmpv_missing_message(error: OSError) -> str:
    width = max(len(distro) for distro, _ in LIBMPV_INSTALL_COMMANDS)
    lines = [
        "abookie needs the system library libmpv, which could not be loaded.",
        f"  ({error})",
        "",
        "Install it with your distribution's package manager:",
        *(f"  {distro:<{width}}  {cmd}" for distro, cmd in LIBMPV_INSTALL_COMMANDS),
    ]
    return "\n".join(lines)


def check_libmpv(loader: Callable[[], None] = _load_libmpv) -> DependencyCheck:
    """Check that libmpv can be loaded; describe how to install it if not."""
    try:
        loader()
    except OSError as error:
        return DependencyCheck(missing="libmpv", message=_libmpv_missing_message(error))
    return DependencyCheck()
