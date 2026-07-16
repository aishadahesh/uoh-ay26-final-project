"""DOS/Anomaly Detector: a circuit breaker against an infinite-loop bug (Chapter 9, Sec. 9.3.12).

docs/tasks.md Sec. 9.3.12: identifies abnormal send-repetition patterns
hinting at a bug or an infinite loop in the agent's own code (analogous to
the `backpressure`/`circuit-breaker` patterns from systems development), and
locks the entire API pathway once tripped -- a runaway loop must never be
able to exhaust the account's real-world resources.

Unlike the Watchdog (Chapter 8), which detects the *absence* of a heartbeat,
this detects the *excess* of send attempts -- the opposite failure mode.
"""

from __future__ import annotations

import time
from collections import deque
from collections.abc import Callable


class AnomalyDetector:
    def __init__(
        self,
        max_sends_in_window: int,
        window_seconds: float,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self.max_sends_in_window = max_sends_in_window
        self.window_seconds = window_seconds
        self._clock = clock
        self._recent_sends: deque[float] = deque()
        self._tripped = False

    @property
    def tripped(self) -> bool:
        return self._tripped

    def record_attempt(self) -> None:
        """Register one send attempt; trips the breaker if the pattern is abnormal.

        Once tripped, the breaker stays locked -- it never self-resets on the
        next quiet window, since a bug that caused a runaway burst is not
        proven fixed just because the burst paused.
        """
        if self._tripped:
            return
        now = self._clock()
        self._recent_sends.append(now)
        cutoff = now - self.window_seconds
        while self._recent_sends and self._recent_sends[0] < cutoff:
            self._recent_sends.popleft()
        if len(self._recent_sends) > self.max_sends_in_window:
            self._tripped = True

    def allow(self) -> bool:
        return not self._tripped
