"""Unit tests for the composed Gatekeeper pipeline (Chapter 9, Sec. 9.3.5-9.3.14)."""

from datetime import date

from police_thief.services.anomaly_detector import AnomalyDetector
from police_thief.services.gatekeeper import (
    Gatekeeper,
    GatekeeperBlockReason,
    Http429BackoffPolicy,
)
from police_thief.services.quota_manager import QuotaManager
from police_thief.services.token_bucket import TokenBucket

DAY_1 = date(2026, 7, 16)


class FakeClock:
    def __init__(self, start: float = 0.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now


def _make_gatekeeper(tmp_path, *, quota=10, capacity=5, refill_rate=1.0, max_sends=10, window=60.0):
    clock = FakeClock()
    return Gatekeeper(
        QuotaManager(daily_threshold=quota, persist_path=tmp_path / "q.json", today=lambda: DAY_1),
        TokenBucket(capacity=capacity, refill_rate=refill_rate, clock=clock),
        AnomalyDetector(max_sends_in_window=max_sends, window_seconds=window, clock=clock),
    )


def test_a_report_passes_cleanly_under_normal_load(tmp_path):
    gk = _make_gatekeeper(tmp_path)
    decision = gk.submit()
    assert decision.allowed is True
    assert decision.reason is None


def test_report_is_rejected_once_the_daily_quota_is_exceeded(tmp_path):
    gk = _make_gatekeeper(tmp_path, quota=1, capacity=10)
    assert gk.submit().allowed is True
    decision = gk.submit()
    assert decision.allowed is False
    assert decision.reason == GatekeeperBlockReason.QUOTA_EXCEEDED


def test_report_is_rate_limited_once_the_token_bucket_is_empty(tmp_path):
    gk = _make_gatekeeper(tmp_path, capacity=1, refill_rate=0.0)
    assert gk.submit().allowed is True
    decision = gk.submit()
    assert decision.allowed is False
    assert decision.reason == GatekeeperBlockReason.RATE_LIMITED


def test_report_is_blocked_once_the_anomaly_detector_trips(tmp_path):
    gk = _make_gatekeeper(tmp_path, capacity=100, max_sends=2, window=60.0)
    gk.submit()
    gk.submit()
    decision = gk.submit()
    assert decision.allowed is False
    assert decision.reason == GatekeeperBlockReason.ANOMALY_DETECTED

    # once tripped, check()'s own pre-flight anomaly gate also blocks --
    # not just the record_attempt() check inside submit()
    assert gk.check().reason == GatekeeperBlockReason.ANOMALY_DETECTED
    decision2 = gk.submit()
    assert decision2.allowed is False
    assert decision2.reason == GatekeeperBlockReason.ANOMALY_DETECTED


def test_a_blocked_send_never_consumes_quota_or_rate_limit_resources(tmp_path):
    gk = _make_gatekeeper(tmp_path, quota=1, capacity=10)
    gk.submit()  # consumes the only quota slot
    tokens_before = gk.token_bucket.tokens
    gk.submit()  # blocked on quota
    assert gk.token_bucket.tokens == tokens_before  # no token spent on a blocked attempt


def test_http_429_backoff_schedule_has_one_wait_per_retry():
    policy = Http429BackoffPolicy(retry_backoff_seconds=5.0, max_retries=3)
    assert policy.backoff_schedule() == [5.0, 5.0, 5.0]


def test_http_429_backoff_schedule_is_empty_for_zero_retries():
    policy = Http429BackoffPolicy(retry_backoff_seconds=5.0, max_retries=0)
    assert policy.backoff_schedule() == []
