"""Composition root: checks system dependencies, builds the UI and runs Qt."""

import sys
from collections.abc import Callable, Sequence

from PySide6.QtWidgets import QApplication, QMessageBox

from abookie.platform.display import display_available as _display_available
from abookie.platform.sysdeps import DependencyCheck, check_libmpv
from abookie.ui.main_view_model import APP_NAME, MainViewModel
from abookie.ui.main_window import MainWindow


def _application(argv: Sequence[str]) -> QApplication:
    existing = QApplication.instance()
    if isinstance(existing, QApplication):
        return existing
    return QApplication(list(argv))


def _show_error_dialog(message: str) -> None:
    _application(sys.argv)
    QMessageBox.critical(None, f"{APP_NAME}: missing dependency", message)


def main(
    argv: Sequence[str] | None = None,
    *,
    check_dependencies: Callable[[], DependencyCheck] = check_libmpv,
    display_available: Callable[[], bool] = _display_available,
    show_error_dialog: Callable[[str], None] = _show_error_dialog,
) -> int:
    """Start abookie and return the process exit code."""
    dependencies = check_dependencies()
    if not dependencies.ok:
        print(dependencies.message, file=sys.stderr)
        if display_available():
            show_error_dialog(dependencies.message)
        return 1

    app = _application(sys.argv if argv is None else argv)
    window = MainWindow(MainViewModel())
    window.show()
    return app.exec()


def run() -> None:
    """Console-script entry point (`abookie`)."""
    sys.exit(main())
