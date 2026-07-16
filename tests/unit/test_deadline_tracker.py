"""Unit tests for the Deadline Tracker (Chapter 8, Sec. 8.3.2-8.3.4)."""

import asyncio

import pytest

from police_thief.services.deadline_tracker import DeadlineExceededError, DeadlineTracker


async def test_call_returns_the_result_when_within_the_deadline():
    tracker = DeadlineTracker(timeout_seconds=0.2)

    async def fast():
        await asyncio.sleep(0.01)
        return "ok"

    assert await tracker.call(fast) == "ok"


async def test_call_raises_deadline_exceeded_when_consistently_too_slow():
    """Sec. 8.3.4's iron rule: a missed deadline is a failure, not patience --
    it must not wait indefinitely, and must surface as a clear error.
    """
    tracker = DeadlineTracker(timeout_seconds=0.05, max_retries=1)

    async def slow():
        await asyncio.sleep(0.5)
        return "too late"

    with pytest.raises(DeadlineExceededError):
        await tracker.call(slow)


async def test_call_retries_the_configured_number_of_times():
    tracker = DeadlineTracker(timeout_seconds=0.2, max_retries=2)
    attempts = {"n": 0}

    async def counts_attempts():
        attempts["n"] += 1
        raise ConnectionError("boom")

    with pytest.raises(DeadlineExceededError):
        await tracker.call(counts_attempts)
    assert attempts["n"] == 3  # 1 initial attempt + 2 retries


async def test_call_recovers_if_a_later_retry_succeeds():
    tracker = DeadlineTracker(timeout_seconds=0.2, max_retries=3)
    attempts = {"n": 0}

    async def flaky():
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise ConnectionError("boom")
        return "recovered"

    assert await tracker.call(flaky) == "recovered"
    assert attempts["n"] == 3


async def test_zero_max_retries_means_exactly_one_attempt():
    tracker = DeadlineTracker(timeout_seconds=0.2, max_retries=0)
    attempts = {"n": 0}

    async def always_fails():
        attempts["n"] += 1
        raise ConnectionError("boom")

    with pytest.raises(DeadlineExceededError):
        await tracker.call(always_fails)
    assert attempts["n"] == 1


async def test_each_retry_gets_a_fresh_awaitable_not_a_reused_coroutine():
    """make_awaitable must be a factory, not a bare coroutine -- a coroutine
    object can only be awaited once.
    """
    tracker = DeadlineTracker(timeout_seconds=0.2, max_retries=2)
    calls = []

    async def _one_attempt():
        calls.append(1)
        if len(calls) < 2:
            raise ConnectionError("boom")
        return "ok"

    result = await tracker.call(_one_attempt)
    assert result == "ok"
    assert len(calls) == 2
