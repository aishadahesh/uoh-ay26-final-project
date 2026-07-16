"""Unit tests for the Quota Manager (Chapter 9, Sec. 9.3.8)."""

from datetime import date

from police_thief.services.quota_manager import QuotaManager

DAY_1 = date(2026, 7, 16)
DAY_2 = date(2026, 7, 17)


def test_quota_manager_allows_sends_below_the_threshold(tmp_path):
    qm = QuotaManager(daily_threshold=3, persist_path=tmp_path / "q.json", today=lambda: DAY_1)
    assert qm.allow() is True
    assert qm.count_today == 0


def test_quota_manager_blocks_once_the_daily_threshold_is_reached(tmp_path):
    qm = QuotaManager(daily_threshold=2, persist_path=tmp_path / "q.json", today=lambda: DAY_1)
    qm.record_send()
    qm.record_send()
    assert qm.count_today == 2
    assert qm.allow() is False


def test_even_a_single_additional_request_never_leaves_the_box(tmp_path):
    qm = QuotaManager(daily_threshold=1, persist_path=tmp_path / "q.json", today=lambda: DAY_1)
    qm.record_send()
    assert qm.allow() is False
    # calling record_send again would exceed the threshold; callers must
    # check allow() first -- but the counter itself keeps incrementing
    # honestly regardless, since it is a record of what happened, not a cap.


def test_counter_persists_across_a_simulated_process_restart(tmp_path):
    path = tmp_path / "q.json"
    qm1 = QuotaManager(daily_threshold=5, persist_path=path, today=lambda: DAY_1)
    qm1.record_send()
    qm1.record_send()

    qm2 = QuotaManager(daily_threshold=5, persist_path=path, today=lambda: DAY_1)
    assert qm2.count_today == 2


def test_counter_resets_correctly_at_the_day_boundary(tmp_path):
    path = tmp_path / "q.json"
    qm1 = QuotaManager(daily_threshold=2, persist_path=path, today=lambda: DAY_1)
    qm1.record_send()
    qm1.record_send()
    assert qm1.allow() is False

    qm2 = QuotaManager(daily_threshold=2, persist_path=path, today=lambda: DAY_2)
    assert qm2.count_today == 0
    assert qm2.allow() is True
