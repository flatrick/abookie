"""View-model for the main window: the state the window renders."""

from PySide6.QtCore import QObject, Signal

APP_NAME = "abookie"


class MainViewModel(QObject):
    """Holds the main window's title and announces changes to it."""

    title_changed = Signal(str)

    def __init__(self, title: str = APP_NAME, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._title = title

    @property
    def title(self) -> str:
        return self._title

    def set_title(self, title: str) -> None:
        if title != self._title:
            self._title = title
            self.title_changed.emit(title)
