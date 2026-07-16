"""Heartbeat-based liveness monitor (Chapter 8, Sec. 8.3.5-8.3.7).

Distinct from the Deadline Tracker's per-request scope: the Watchdog
watches the *entire system* from outside. If too much time passes without
a heartbeat -- a sign the model crashed, communication froze, or a
connection was interrupted -- it must persist state and perform a
controlled shutdown rather than crash silently (Sec. 8.3.6).

An injectable clock keeps this testable without real wall-clock sleeps:
tests advance a fake clock instead of waiting for real timeouts to elapse.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from enum import StrEnum


class WatchdogStatus(StrEnum):
    ALIVE = "ALIVE"
    SHUTDOWN = "SHUTDOWN"


class Watchdog:
    """`on_timeout` bundles Sec. 8.3.6's State Persistence + Controlled
    Shutdown into one caller-supplied callback, invoked exactly once the
    first time a timeout is detected.
    """

    def __init__(
        self,
        timeout_seconds: float,
        on_timeout: Callable[[], None] | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.timeout_seconds = timeout_seconds
        self._on_timeout = on_timeout
        self._clock = clock
        self._last_heartbeat = clock()
        self._triggered = False

    def heartbeat(self) -> None:
        """Call this regularly from the main loop; resets the timer."""
        self._last_heartbeat = self._clock()

    @property
    def shutdown_triggered(self) -> bool:
        return self._triggered

    def check(self) -> WatchdogStatus:
        """Compare elapsed time since the last heartbeat against the
        threshold (Sec. 8.3.7). Once triggered, stays SHUTDOWN forever --
        `on_timeout` fires exactly once, not on every subsequent check.
        """
        if self._triggered:
            return WatchdogStatus.SHUTDOWN
        elapsed = self._clock() - self._last_heartbeat
        if elapsed > self.timeout_seconds:
            self._triggered = True
            if self._on_timeout is not None:
                self._on_timeout()
            return WatchdogStatus.SHUTDOWN
        return WatchdogStatus.ALIVE
