"""Legal state machine governing match progression (Chapter 8, Sec. 8.2).

docs/tasks.md Sec. 8.2.2-8.2.4: only legal transitions between game phases
are allowed; any transition not in the table is rejected immediately with
an error -- turning a hidden bug into a loud, visible one during
development rather than a silent deadlock during a live match (Sec. 8.2.3,
the state machine is "the first line of defense against deadlock").
"""

from __future__ import annotations

from enum import StrEnum


class MatchState(StrEnum):
    """Sec. 8.2.2's exact state list, plus the TECHNICAL_LOSS error state."""

    WAITING_FOR_OPPONENT = "WAITING_FOR_OPPONENT"
    COMPUTING_MOVE = "COMPUTING_MOVE"
    COMMITTING = "COMMITTING"
    AWAITING_REVEAL = "AWAITING_REVEAL"
    VERIFYING = "VERIFYING"
    TECHNICAL_LOSS = "TECHNICAL_LOSS"


class IllegalStateTransitionError(RuntimeError):
    """Raised when a transition is attempted that isn't in the legal table."""


_TRANSITIONS: dict[MatchState, frozenset[MatchState]] = {
    MatchState.WAITING_FOR_OPPONENT: frozenset({MatchState.COMPUTING_MOVE}),
    MatchState.COMPUTING_MOVE: frozenset({MatchState.COMMITTING, MatchState.TECHNICAL_LOSS}),
    MatchState.COMMITTING: frozenset({MatchState.AWAITING_REVEAL, MatchState.TECHNICAL_LOSS}),
    MatchState.AWAITING_REVEAL: frozenset({MatchState.VERIFYING, MatchState.TECHNICAL_LOSS}),
    MatchState.VERIFYING: frozenset({MatchState.WAITING_FOR_OPPONENT, MatchState.TECHNICAL_LOSS}),
    MatchState.TECHNICAL_LOSS: frozenset(),  # terminal: no legal transitions out, ever
}


class MatchStateMachine:
    """Wraps a single MatchState, enforcing only the transitions in the table."""

    def __init__(self, initial: MatchState = MatchState.WAITING_FOR_OPPONENT) -> None:
        self._state = initial

    @property
    def state(self) -> MatchState:
        return self._state

    @property
    def is_terminal(self) -> bool:
        return not _TRANSITIONS[self._state]

    def legal_next_states(self) -> frozenset[MatchState]:
        return _TRANSITIONS[self._state]

    def transition(self, target: MatchState) -> MatchState:
        """Move to `target`, or raise IllegalStateTransitionError immediately.

        Sec. 8.2.4: this must reject, never silently drift into an
        undefined state -- a loud development-time error is the point.
        """
        legal = _TRANSITIONS[self._state]
        if target not in legal:
            raise IllegalStateTransitionError(
                f"cannot transition from {self._state} to {target}; legal targets: {sorted(legal)}"
            )
        self._state = target
        return self._state
