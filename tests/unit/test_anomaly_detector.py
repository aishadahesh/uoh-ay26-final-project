"""Unit tests for the DOS/Anomaly Detector (Chapter 9, Sec. 9.3.12)."""

from police_thief.services.anomaly_detector import AnomalyDetector


class FakeClock:
    def __init__(self, start: float = 0.0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def test_detector_allows_sends_within_the_normal_pattern():
    clock = FakeClock()
    detector = AnomalyDetector(max_sends_in_window=3, window_seconds=10.0, clock=clock)
    for _ in range(3):
        detector.record_attempt()
    assert detector.tripped is False
    assert detector.allow() is True


def test_detector_trips_on_a_simulated_infinite_loop_send_pattern():
    clock = FakeClock()
    detector = AnomalyDetector(max_sends_in_window=3, window_seconds=10.0, clock=clock)
    for _ in range(10):
        detector.record_attempt()
    assert detector.tripped is True
    assert detector.allow() is False


def test_spaced_out_sends_never_trip_the_detector():
    clock = FakeClock()
    detector = AnomalyDetector(max_sends_in_window=3, window_seconds=10.0, clock=clock)
    for _ in range(20):
        detector.record_attempt()
        clock.advance(20.0)  # always well outside the window
    assert detector.tripped is False


def test_once_tripped_the_breaker_stays_locked_even_after_a_quiet_period():
    clock = FakeClock()
    detector = AnomalyDetector(max_sends_in_window=2, window_seconds=5.0, clock=clock)
    detector.record_attempt()
    detector.record_attempt()
    detector.record_attempt()  # trips here
    assert detector.tripped is True

    clock.advance(1000.0)  # long quiet period
    detector.record_attempt()
    assert detector.tripped is True
    assert detector.allow() is False


def test_old_attempts_fall_out_of_the_sliding_window():
    clock = FakeClock()
    detector = AnomalyDetector(max_sends_in_window=2, window_seconds=5.0, clock=clock)
    detector.record_attempt()
    detector.record_attempt()
    clock.advance(6.0)  # both prior attempts now outside the window
    detector.record_attempt()
    assert detector.tripped is False
