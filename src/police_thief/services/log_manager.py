"""Log Manager: accumulates match steps for audit and replay (Chapter 8).

One of Diagram 12's five named sub-systems (Sec. 8.3.8): MCP Connector,
Decision Module, Log Manager, Deadline Tracker, Watchdog. Thin by design --
recording and persisting are its only responsibilities; verification
itself is Chapter 5's audit_log()/verify(), and persistence reuses
Chapter 7's save_log(), neither reimplemented here.
"""

from __future__ import annotations

from pathlib import Path

from police_thief.domain.replay import save_log
from police_thief.services.commit_reveal import LogEntry


class LogManager:
    """Append-only record of this side's own committed-and-revealed steps."""

    def __init__(self) -> None:
        self._entries: list[LogEntry] = []

    def record(self, entry: LogEntry) -> None:
        self._entries.append(entry)

    @property
    def entries(self) -> list[LogEntry]:
        return list(self._entries)

    def save(self, path: Path) -> None:
        save_log(self._entries, path)
