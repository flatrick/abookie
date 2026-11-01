"""Clock port: the only way core reads the time or schedules delayed work."""

from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Protocol


class Cancellable(Protocol):
    """Handle for scheduled work that has not run yet."""

    def cancel(self) -> None:
        """Prevent the scheduled callback from running. Safe to call twice."""
        ...


class Clock(Protocol):
    """Source of the current time and of delayed callbacks."""

    def now(self) -> datetime:
        """Return the current time as a timezone-aware datetime."""
        ...

    def call_later(self, delay: timedelta, callback: Callable[[], None]) -> Cancellable:
        """Run ``callback`` once, ``delay`` from now, on the application thread."""
        ...
