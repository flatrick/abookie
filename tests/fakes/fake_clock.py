"""Fake implementation of the Clock port: time moves only when a test says so."""

import heapq
import itertools
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class _Scheduled:
    cancelled: bool = False

    def cancel(self) -> None:
        self.cancelled = True


@dataclass(order=True)
class _Entry:
    due: datetime
    seq: int
    callback: Callable[[], None] = field(compare=False)
    handle: _Scheduled = field(compare=False)


class FakeClock:
    """Manually advanced clock. Callbacks fire during ``advance`` at their due time."""

    def __init__(self, start: datetime) -> None:
        if start.tzinfo is None:
            raise ValueError("FakeClock needs a timezone-aware start time")
        self._now = start
        self._queue: list[_Entry] = []
        self._seq = itertools.count()

    def now(self) -> datetime:
        return self._now

    def call_later(self, delay: timedelta, callback: Callable[[], None]) -> _Scheduled:
        handle = _Scheduled()
        entry = _Entry(self._now + delay, next(self._seq), callback, handle)
        heapq.heappush(self._queue, entry)
        return handle

    def advance(self, delta: timedelta) -> None:
        if delta < timedelta(0):
            raise ValueError("time cannot go backwards")
        target = self._now + delta
        while self._queue and self._queue[0].due <= target:
            entry = heapq.heappop(self._queue)
            if entry.handle.cancelled:
                continue
            self._now = entry.due
            entry.callback()
        self._now = target
