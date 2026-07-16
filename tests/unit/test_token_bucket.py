"""Unit tests for the Token-Bucket rate limiter (Chapter 9, Sec. 9.3.9-9.3.11)."""

from police_thief.services.token_bucket import TokenBucket


class FakeClock:
    def __init__(self, start: float = 0.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def test_bucket_starts_full_at_capacity():
    bucket = TokenBucket(capacity=5, refill_rate=1.0, clock=FakeClock())
    assert bucket.tokens == 5


def test_allow_spends_a_token_and_returns_true_while_available():
    clock = FakeClock()
    bucket = TokenBucket(capacity=2, refill_rate=1.0, clock=clock)
    assert bucket.allow() is True
    assert bucket.allow() is True


def test_allow_returns_false_once_empty():
    clock = FakeClock()
    bucket = TokenBucket(capacity=1, refill_rate=1.0, clock=clock)
    assert bucket.allow() is True
    assert bucket.allow() is False


def test_bucket_refills_over_time_up_to_capacity_never_beyond():
    clock = FakeClock()
    bucket = TokenBucket(capacity=3, refill_rate=1.0, clock=clock)
    bucket.allow()
    bucket.allow()
    bucket.allow()
    assert bucket.allow() is False

    clock.advance(100.0)  # far more than enough to refill to capacity
    assert bucket.allow() is True
    assert bucket.tokens == 2.0  # capped at capacity (3), then one spent


def test_partial_refill_allows_exactly_the_expected_number_of_sends():
    clock = FakeClock()
    bucket = TokenBucket(capacity=5, refill_rate=1.0, clock=clock)
    for _ in range(5):
        bucket.allow()
    assert bucket.allow() is False

    clock.advance(2.0)  # +2 tokens
    assert bucket.allow() is True
    assert bucket.allow() is True
    assert bucket.allow() is False


def test_allow_respects_a_custom_cost():
    clock = FakeClock()
    bucket = TokenBucket(capacity=5, refill_rate=0.0, clock=clock)
    assert bucket.allow(cost=3.0) is True
    assert bucket.tokens == 2.0
    assert bucket.allow(cost=3.0) is False
