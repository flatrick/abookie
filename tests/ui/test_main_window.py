"""The main window only renders what its view-model says."""

import pytest
from pytestqt.qtbot import QtBot

from abookie.ui.main_view_model import MainViewModel
from abookie.ui.main_window import MainWindow

pytestmark = pytest.mark.ui


def test_view_model_title_defaults_to_app_name() -> None:
    assert MainViewModel().title == "abookie"


def test_view_model_announces_title_changes(qtbot: QtBot) -> None:
    view_model = MainViewModel()

    with qtbot.waitSignal(view_model.title_changed) as blocker:
        view_model.set_title("Dune")

    assert blocker.args == ["Dune"]
    assert view_model.title == "Dune"


def test_window_title_comes_from_view_model(qtbot: QtBot) -> None:
    view_model = MainViewModel(title="abookie")
    window = MainWindow(view_model)
    qtbot.addWidget(window)

    assert window.windowTitle() == "abookie"

    view_model.set_title("Dune - abookie")
    assert window.windowTitle() == "Dune - abookie"
