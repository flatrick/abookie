"""Clock adapter backed by the system clock and the Qt event loop."""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from PySide6.QtCore import QTimer


class _TimerHandle:
    """Cancel handle owning one single-shot timer until it fires or is cancelled."""

    def __init__(
        self,
        delay: timedelta,
        callback: Callable[[], None],
        on_done: Callable[["_TimerHandle"], None],
    ) -> None:
        self._callback = callback
        self._on_done = on_done
        self._timer: QTimer | None = QTimer()
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._fire)
        self._timer.start(max(0, round(delay.total_seconds() * 1000)))

    def cancel(self) -> None:
        if self._timer is not None:
            self._timer.stop()
            self._release()

    def _fire(self) -> None:
        self._release()
        self._callback()

    def _release(self) -> None:
        if self._timer is not None:
            self._timer.deleteLater()
            self._timer = None
            self._on_done(self)


class SystemClock:
    """Real time; callbacks run on the Qt event loop of the calling thread."""

    def __init__(self) -> None:
        # Keeps handles (and their timers) alive while pending, even if the
        # caller drops the returned handle.
        self._pending: set[_TimerHandle] = set()

    def now(self) -> datetime:
        return datetime.now(UTC)

    def call_later(
        self, delay: timedelta, callback: Callable[[], None]
    ) -> _TimerHandle:
        handle = _TimerHandle(delay, callback, self._pending.discard)
        self._pending.add(handle)
        return handle
