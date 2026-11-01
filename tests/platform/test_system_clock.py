"""SystemClock implements the Clock port with real time and the Qt event loop."""

from datetime import UTC, datetime, timedelta

import pytest
from pytestqt.qtbot import QtBot

from abookie.core.ports.clock import Clock
from abookie.platform.clock import SystemClock

pytestmark = pytest.mark.integration


def test_now_tracks_real_time() -> None:
    clock: Clock = SystemClock()

    before = datetime.now(UTC)
    now = clock.now()
    after = datetime.now(UTC)

    assert now.tzinfo is not None
    assert before <= now <= after


def test_call_later_fires_on_qt_event_loop(qtbot: QtBot) -> None:
    clock: Clock = SystemClock()
    fired: list[bool] = []

    clock.call_later(timedelta(milliseconds=10), lambda: fired.append(True))

    assert fired == []
    qtbot.waitUntil(lambda: fired == [True], timeout=2000)


def test_cancelled_call_does_not_fire(qtbot: QtBot) -> None:
    clock: Clock = SystemClock()
    fired: list[bool] = []
    handle = clock.call_later(timedelta(milliseconds=10), lambda: fired.append(True))

    handle.cancel()
    handle.cancel()
    qtbot.wait(100)

    assert fired == []


def test_call_later_fires_when_handle_is_dropped(qtbot: QtBot) -> None:
    clock = SystemClock()
    fired: list[bool] = []

    clock.call_later(timedelta(milliseconds=10), lambda: fired.append(True))

    qtbot.waitUntil(lambda: fired == [True], timeout=2000)
