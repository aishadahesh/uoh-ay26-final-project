"""Gatekeeper: three cumulative defense layers in front of Gmail sends (Chapter 9, Sec. 9.3.5-9.3.14).

docs/tasks.md Sec. 9.3.6: guards against spamming the lecturer's inbox or
tripping Google's `Rate Limit 429` -- composed of the Quota Manager
(Sec. 9.3.8), the Token-Bucket rate limiter (Sec. 9.3.9-9.3.11), and the
DOS/Anomaly Detector (Sec. 9.3.12), checked in that order: quota first
(the cheapest, most absolute check), then pace, then pattern.

A `429` from Gmail itself (Sec. 9.3.13-9.3.14) is a distinct, later concern:
it can only be discovered by attempting to send, so it is handled by the
caller backing off via `retry_backoff_seconds`/`max_retries`, not by this
pre-send gate. `Http429BackoffPolicy` below encodes that backoff schedule.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from police_thief.services.anomaly_detector import AnomalyDetector
from police_thief.services.quota_manager import QuotaManager
from police_thief.services.token_bucket import TokenBucket


class GatekeeperBlockReason(StrEnum):
    QUOTA_EXCEEDED = "quota_exceeded"
    RATE_LIMITED = "rate_limited"
    ANOMALY_DETECTED = "anomaly_detected"


@dataclass(frozen=True)
class GatekeeperDecision:
    allowed: bool
    reason: GatekeeperBlockReason | None = None


class Gatekeeper:
    def __init__(
        self,
        quota_manager: QuotaManager,
        token_bucket: TokenBucket,
        anomaly_detector: AnomalyDetector,
    ) -> None:
        self.quota_manager = quota_manager
        self.token_bucket = token_bucket
        self.anomaly_detector = anomaly_detector

    def check(self) -> GatekeeperDecision:
        """Evaluate all three gates without consuming any of them (a dry run)."""
        if not self.quota_manager.allow():
            return GatekeeperDecision(allowed=False, reason=GatekeeperBlockReason.QUOTA_EXCEEDED)
        if not self.anomaly_detector.allow():
            return GatekeeperDecision(allowed=False, reason=GatekeeperBlockReason.ANOMALY_DETECTED)
        return GatekeeperDecision(allowed=True)

    def submit(self) -> GatekeeperDecision:
        """Attempt to actually send one report, consuming gate resources on success.

        Order matters: quota and anomaly checks are free (no resource
        consumed by checking), so they run first; the token bucket is
        checked and spent last since `allow()` itself consumes a token on
        success -- we don't want to spend a token only to then reject on
        quota or anomaly grounds.
        """
        decision = self.check()
        if not decision.allowed:
            return decision
        self.anomaly_detector.record_attempt()
        if self.anomaly_detector.tripped:
            return GatekeeperDecision(allowed=False, reason=GatekeeperBlockReason.ANOMALY_DETECTED)
        if not self.token_bucket.allow():
            return GatekeeperDecision(allowed=False, reason=GatekeeperBlockReason.RATE_LIMITED)
        self.quota_manager.record_send()
        return GatekeeperDecision(allowed=True)


@dataclass(frozen=True)
class Http429BackoffPolicy:
    """Sec. 9.3.13's iron rule: a 429 is temporary, never retried blindly."""

    retry_backoff_seconds: float
    max_retries: int

    def backoff_schedule(self) -> list[float]:
        """One wait duration per retry attempt (flat backoff, per the mandatory minimum)."""
        return [self.retry_backoff_seconds] * self.max_retries
