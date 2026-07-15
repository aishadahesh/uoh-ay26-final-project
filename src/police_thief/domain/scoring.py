"""The Dec-POMDP reward function R, made concrete (Chapter 3, Table 2).

docs/tasks.md Sec. 3.4: every match ending awards each side a *different*
score -- a binary win/loss is deliberately avoided. Defaults below are the
Mandatory Parameters Table's values (App. F); they may only be raised, never
lowered, by mutual team agreement via config/game.json.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class MatchOutcome(StrEnum):
    """Every way a match can end (docs/tasks.md Sec. 3.4.2, Table 2)."""

    CAPTURE = "capture"
    SURVIVAL = "survival"
    TECHNICAL_LOSS = "technical_loss"
    TIE = "tie"


@dataclass(frozen=True)
class ScoringTable:
    """Score values for every MatchOutcome. Defaults are the mandatory floor."""

    capture_cop: int = 20
    capture_thief: int = 5
    survival_cop: int = 5
    survival_thief: int = 10
    tie_score: int = 2
    technical_loss: int = 0


def score_for(outcome: MatchOutcome, scoring: ScoringTable) -> tuple[int, int]:
    """Return (cop_score, thief_score) for the given match outcome."""
    if outcome is MatchOutcome.CAPTURE:
        return scoring.capture_cop, scoring.capture_thief
    if outcome is MatchOutcome.SURVIVAL:
        return scoring.survival_cop, scoring.survival_thief
    if outcome is MatchOutcome.TECHNICAL_LOSS:
        return scoring.technical_loss, scoring.technical_loss
    if outcome is MatchOutcome.TIE:
        return scoring.tie_score, scoring.tie_score
    raise ValueError(f"unhandled match outcome: {outcome!r}")
