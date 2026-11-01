"""The main window. It only binds to its view-model; it holds no logic."""

from PySide6.QtWidgets import QMainWindow, QWidget

from abookie.ui.main_view_model import MainViewModel


class MainWindow(QMainWindow):
    def __init__(
        self, view_model: MainViewModel, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)
        self._view_model = view_model
        self.setWindowTitle(view_model.title)
        view_model.title_changed.connect(self.setWindowTitle)
