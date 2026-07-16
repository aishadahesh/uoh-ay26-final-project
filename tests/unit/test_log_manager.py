"""Unit tests for the Log Manager (Chapter 8)."""

from police_thief.domain.replay import load_log
from police_thief.services.commit_reveal import LogEntry, commit
from police_thief.services.log_manager import LogManager


def _make_entry(turn: int) -> LogEntry:
    c = commit(state={"turn": turn}, move="N", intent=True)
    return LogEntry(state={"turn": turn}, move="N", intent=True, nonce=c.nonce, h_commit=c.h_commit)


def test_log_manager_starts_empty():
    manager = LogManager()
    assert manager.entries == []


def test_record_appends_entries_in_order():
    manager = LogManager()
    manager.record(_make_entry(0))
    manager.record(_make_entry(1))
    assert [e.state["turn"] for e in manager.entries] == [0, 1]


def test_entries_property_returns_a_copy_not_the_internal_list():
    manager = LogManager()
    manager.record(_make_entry(0))
    snapshot = manager.entries
    snapshot.append(_make_entry(99))
    assert len(manager.entries) == 1  # the manager's own state is unaffected


def test_save_writes_a_file_load_log_can_read_back(tmp_path):
    manager = LogManager()
    manager.record(_make_entry(0))
    manager.record(_make_entry(1))
    path = tmp_path / "log.json"
    manager.save(path)
    loaded = load_log(path)
    assert loaded == manager.entries
