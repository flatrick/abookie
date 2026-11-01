"""The Clock port's fake lets time-dependent core behavior run without sleeping."""

from datetime import UTC, datetime, timedelta

import pytest

from abookie.core.ports.clock import Clock
from tests.fakes.fake_clock import FakeClock

pytestmark = pytest.mark.unit

START = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


def test_fake_clock_now_advances() -> None:
    clock = FakeClock(start=START)

    clock.advance(timedelta(seconds=90))

    assert clock.now() == START + timedelta(seconds=90)


def test_fake_clock_fires_scheduled_callback_on_advance() -> None:
    fake = FakeClock(start=START)
    clock: Clock = fake  # used only through the port, as core code would
    fired: list[datetime] = []
    clock.call_later(timedelta(seconds=5), lambda: fired.append(clock.now()))

    fake.advance(timedelta(seconds=4))
    assert fired == []

    fake.advance(timedelta(seconds=1))
    assert fired == [START + timedelta(seconds=5)]


def test_fake_clock_fires_callbacks_in_due_order_at_their_due_time() -> None:
    clock = FakeClock(start=START)
    fired: list[tuple[str, datetime]] = []
    clock.call_later(timedelta(seconds=3), lambda: fired.append(("b", clock.now())))
    clock.call_later(timedelta(seconds=1), lambda: fired.append(("a", clock.now())))

    clock.advance(timedelta(seconds=10))

    assert fired == [
        ("a", START + timedelta(seconds=1)),
        ("b", START + timedelta(seconds=3)),
    ]
    assert clock.now() == START + timedelta(seconds=10)


def test_callback_scheduled_during_advance_fires_if_due() -> None:
    clock = FakeClock(start=START)
    fired: list[datetime] = []

    def reschedule() -> None:
        fired.append(clock.now())
        if len(fired) < 3:
            clock.call_later(timedelta(seconds=2), reschedule)

    clock.call_later(timedelta(seconds=2), reschedule)
    clock.advance(timedelta(seconds=5))

    assert fired == [START + timedelta(seconds=2), START + timedelta(seconds=4)]


def test_cancelled_callback_does_not_fire() -> None:
    clock = FakeClock(start=START)
    fired: list[int] = []
    handle = clock.call_later(timedelta(seconds=1), lambda: fired.append(1))

    handle.cancel()
    clock.advance(timedelta(seconds=2))

    assert fired == []


def test_negative_advance_is_rejected() -> None:
    clock = FakeClock(start=START)
    with pytest.raises(ValueError):
        clock.advance(timedelta(seconds=-1))
