"""Token-Bucket rate limiter (Chapter 9, Sec. 9.3.9-9.3.11).

docs/tasks.md Sec. 9.3.10's mandatory formula:

    tokens <- min(C, tokens + r*dt),   allow iff tokens >= 1

Guards the pace of outbound Gmail API report sends -- not to be confused
with LLM tokens (Sec. 6.4) or OAuth tokens (App. A), a terminology
collision the rulebook itself calls out explicitly (Sec. 9.3.7).
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass, field


@dataclass
class TokenBucket:
    capacity: float
    refill_rate: float
    clock: Callable[[], float] = time.monotonic
    tokens: float = field(init=False)
    _last_update: float = field(init=False)

    def __post_init__(self) -> None:
        self.tokens = self.capacity
        self._last_update = self.clock()

    def _refill(self) -> None:
        now = self.clock()
        elapsed = now - self._last_update
        self._last_update = now
        self.tokens = min(self.capacity, self.tokens + self.refill_rate * elapsed)

    def allow(self, cost: float = 1.0) -> bool:
        self._refill()
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False
