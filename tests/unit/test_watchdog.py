"""Unit tests for the Watchdog heartbeat monitor (Chapter 8, Sec. 8.3.5-8.3.7)."""

from police_thief.services.watchdog import Watchdog, WatchdogStatus


class FakeClock:
    """A controllable clock so tests never need a real wall-clock sleep."""

    def __init__(self, start: float = 0.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def test_watchdog_is_alive_immediately_after_construction():
    clock = FakeClock()
    wd = Watchdog(timeout_seconds=10.0, clock=clock)
    assert wd.check() == WatchdogStatus.ALIVE


def test_watchdog_stays_alive_within_the_threshold():
    clock = FakeClock()
    wd = Watchdog(timeout_seconds=10.0, clock=clock)
    clock.advance(9.0)
    assert wd.check() == WatchdogStatus.ALIVE


def test_watchdog_reports_shutdown_once_the_threshold_is_exceeded():
    clock = FakeClock()
    wd = Watchdog(timeout_seconds=10.0, clock=clock)
    clock.advance(11.0)
    assert wd.check() == WatchdogStatus.SHUTDOWN


def test_heartbeat_resets_the_elapsed_timer():
    clock = FakeClock()
    wd = Watchdog(timeout_seconds=10.0, clock=clock)
    clock.advance(9.0)
    wd.heartbeat()
    clock.advance(9.0)  # 18s total, but only 9s since the last heartbeat
    assert wd.check() == WatchdogStatus.ALIVE


def test_on_timeout_callback_fires_exactly_once():
    clock = FakeClock()
    events = []
    wd = Watchdog(timeout_seconds=10.0, on_timeout=lambda: events.append("fired"), clock=clock)
    clock.advance(11.0)
    assert wd.check() == WatchdogStatus.SHUTDOWN
    assert events == ["fired"]

    clock.advance(100.0)  # long past the threshold again
    assert wd.check() == WatchdogStatus.SHUTDOWN
    assert events == ["fired"]  # not fired a second time


def test_shutdown_triggered_property_reflects_state():
    clock = FakeClock()
    wd = Watchdog(timeout_seconds=10.0, clock=clock)
    assert wd.shutdown_triggered is False
    clock.advance(11.0)
    wd.check()
    assert wd.shutdown_triggered is True


def test_watchdog_with_no_on_timeout_callback_does_not_crash():
    clock = FakeClock()
    wd = Watchdog(timeout_seconds=5.0, clock=clock)
    clock.advance(6.0)
    assert wd.check() == WatchdogStatus.SHUTDOWN
