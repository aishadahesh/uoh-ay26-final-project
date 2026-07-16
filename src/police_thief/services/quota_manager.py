"""Quota Manager: the last line of defense against account lockout (Chapter 9, Sec. 9.3.8).

docs/tasks.md Sec. 9.3.8: tracks operations performed on a given day and
blocks any further request once the daily safety threshold is crossed --
even a single additional request must never leave the box. The counter is
persisted to disk (a lightweight local JSON store, Sec. I.5/T0463) so it
survives a process restart within the same day.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass
class _QuotaState:
    day: str
    count: int


class QuotaManager:
    def __init__(
        self,
        daily_threshold: int,
        persist_path: Path,
        today: Callable[[], date] = date.today,
    ) -> None:
        self.daily_threshold = daily_threshold
        self.persist_path = persist_path
        self._today = today
        self._state = self._load()

    def _load(self) -> _QuotaState:
        if self.persist_path.is_file():
            raw = json.loads(self.persist_path.read_text(encoding="utf-8"))
            state = _QuotaState(day=raw["day"], count=int(raw["count"]))
        else:
            state = _QuotaState(day=self._today().isoformat(), count=0)
        return self._rolled_over(state)

    def _rolled_over(self, state: _QuotaState) -> _QuotaState:
        current_day = self._today().isoformat()
        if state.day != current_day:
            return _QuotaState(day=current_day, count=0)
        return state

    def _save(self) -> None:
        self.persist_path.parent.mkdir(parents=True, exist_ok=True)
        self.persist_path.write_text(
            json.dumps({"day": self._state.day, "count": self._state.count}), encoding="utf-8"
        )

    @property
    def count_today(self) -> int:
        self._state = self._rolled_over(self._state)
        return self._state.count

    def allow(self) -> bool:
        self._state = self._rolled_over(self._state)
        return self._state.count < self.daily_threshold

    def record_send(self) -> None:
        self._state = self._rolled_over(self._state)
        self._state.count += 1
        self._save()
