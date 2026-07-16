"""Replay Viewer core logic (Chapter 7): cryptographic re-verification with
step-by-step scrubbing.

docs/tasks.md Sec. 7.4-7.5: the Replay Viewer's uniqueness is not its
graphical display but its cryptographic verification -- this module reuses
Chapter 5's verify()/audit_log() exactly, since this project already
implements the "read log entry, recompute SHA-256, compare to stored
commit" verification loop as a generic, tested primitive. What Chapter 7
adds is step-by-step scrubbing and the "voided on first tamper" per-step
display status (Sec. 7.5.1): once a tamper is found at some index, every
step at or after that index is disqualified, not just the exact byte that
changed.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from police_thief.services.commit_reveal import LogEntry, audit_log

VERIFIED_OK = "VERIFIED_OK"
TAMPERED = "TAMPERED"


class ReplayLogError(ValueError):
    """Raised when a match log file is missing or malformed."""


def save_log(entries: list[LogEntry], path: Path) -> None:
    """Persist a match log as a JSON array of LogEntry records."""
    payload = [asdict(entry) for entry in entries]
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_log(path: Path) -> list[LogEntry]:
    """Load a match log JSON file into LogEntry objects."""
    if not path.is_file():
        raise ReplayLogError(f"missing match log file: {path}")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return [LogEntry(**record) for record in raw]
    except (KeyError, TypeError, ValueError) as exc:
        raise ReplayLogError(f"malformed match log at {path}: {exc}") from exc


@dataclass(frozen=True)
class ReplayStepView:
    """One step's data plus its verification status for display."""

    index: int
    entry: LogEntry
    status: str  # VERIFIED_OK or TAMPERED


class ReplaySession:
    """Scrub forward/backward through a loaded match log."""

    def __init__(self, entries: list[LogEntry]) -> None:
        self.entries = entries
        self._audit = audit_log(entries)
        self._current_index = 0 if entries else -1

    @property
    def total_steps(self) -> int:
        return len(self.entries)

    @property
    def is_fully_verified(self) -> bool:
        return self._audit.verified

    @property
    def first_tampered_index(self) -> int | None:
        return self._audit.tampered_index

    @property
    def verified_count(self) -> int:
        """Steps before any tampering -- all of them, on a clean log."""
        tampered_at = self._audit.tampered_index
        return len(self.entries) if tampered_at is None else tampered_at

    @property
    def tampered_count(self) -> int:
        """Steps voided from the first tamper onward (Sec. 7.5.1)."""
        return self.total_steps - self.verified_count

    def step_view(self, index: int) -> ReplayStepView:
        if not (0 <= index < len(self.entries)):
            raise IndexError(f"step index {index} out of range for {len(self.entries)} steps")
        tampered_at = self._audit.tampered_index
        status = TAMPERED if tampered_at is not None and index >= tampered_at else VERIFIED_OK
        return ReplayStepView(index=index, entry=self.entries[index], status=status)

    @property
    def current_step(self) -> ReplayStepView:
        return self.step_view(self._current_index)

    def next(self) -> ReplayStepView:
        if self._current_index < len(self.entries) - 1:
            self._current_index += 1
        return self.current_step

    def previous(self) -> ReplayStepView:
        if self._current_index > 0:
            self._current_index -= 1
        return self.current_step

    def jump_to(self, index: int) -> ReplayStepView:
        self.step_view(index)  # validates range before committing to it
        self._current_index = index
        return self.current_step
