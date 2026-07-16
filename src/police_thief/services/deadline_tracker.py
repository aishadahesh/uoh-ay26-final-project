"""Per-request timeout enforcement (Chapter 8, Sec. 8.3.2-8.3.4).

Iron rule (Sec. 8.3.4): "a missed deadline is a failure, not patience."
Every outbound request gets a deadline; once it expires, the caller must
retry (bounded) or declare a technical loss -- never wait indefinitely.
Leaving a request "dependent" with no deadline is a direct path to
deadlock (Sec. 8.2.3).

Uses real asyncio cancellation (asyncio.wait_for), not an after-the-fact
elapsed-time check -- a synchronous "measure how long it took" approach
cannot actually cut off a call that never returns.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")


class DeadlineExceededError(TimeoutError):
    """Raised when every attempt times out or fails before a deadline."""


@dataclass(frozen=True)
class DeadlineTracker:
    """Wraps an async call with a per-attempt timeout and bounded retries."""

    timeout_seconds: float
    max_retries: int = 0

    async def call(self, make_awaitable: Callable[[], Awaitable[T]]) -> T:
        """`make_awaitable` is a zero-arg factory (not a bare coroutine) --
        a coroutine object can only be awaited once, so a fresh one is
        needed for every retry attempt.
        """
        attempts = self.max_retries + 1
        last_exc: BaseException | None = None
        for _ in range(attempts):
            try:
                return await asyncio.wait_for(make_awaitable(), timeout=self.timeout_seconds)
            except TimeoutError as exc:
                last_exc = exc
            except Exception as exc:  # noqa: BLE001 -- any failure is retry-eligible here
                last_exc = exc
        raise DeadlineExceededError(
            f"all {attempts} attempt(s) failed or exceeded {self.timeout_seconds}s"
        ) from last_exc
