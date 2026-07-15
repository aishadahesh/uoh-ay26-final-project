"""Unit tests for project version tracking."""

from police_thief.shared.version import VERSION


def test_version_starts_at_baseline():
    assert VERSION == "1.00"
