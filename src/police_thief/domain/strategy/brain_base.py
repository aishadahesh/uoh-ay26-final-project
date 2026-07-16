"""BrainBase: the strategy module's required interface (Chapter 6, Sec. 6.1.2).

Sec. 6.4.1 -- MUST NOT rely on an LLM for spatial computation: neither
method below accepts an LLM handle, a prompt, or any text input of any
kind. That is a structural guarantee, not just a convention -- there is
nothing for a subclass to plug an LLM call into even if it wanted to for
the move decision itself. The verbal layer (domain/hints.py) is a
completely separate pipeline that never feeds into these methods.

Both methods receive only this side's own local truth (its own position
and its own belief map) -- never the opponent's real position. A
subclass that somehow obtained the opponent's true position from
elsewhere would be violating partial observability, not this interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from police_thief.domain.belief import BeliefMap
from police_thief.domain.board import Board, Move, Position


class BrainBase(ABC):
    """Override `_decide_move` (both roles); the cop may also override
    `_pick_move` for barrier placement (Sec. 6.1.2).
    """

    @abstractmethod
    def _decide_move(self, board: Board, own: Position, belief: BeliefMap) -> Move:
        """Choose this turn's movement. Must return a legal Move."""

    def _pick_move(self, board: Board, own: Position, belief: BeliefMap) -> Position | None:
        """Optional: choose a barrier target (cop only).

        Returning None means "place no barrier this turn" -- the default,
        since barrier placement is optional even for the cop on any given
        turn (docs/tasks.md Sec. 3.3.7's budget-management framing).
        """
        return None
