"""Single-process local simulation harness (Chapter 3 / Stage-1 milestone).

Placeholder-policy only: real strategic decision-making is Chapter 6's
domain (heuristics, a custom algorithm, or optionally reinforcement
learning). The policies here exist purely to prove the board/movement/
barrier/capture/scoring logic plays a full, legal match end-to-end with no
crash -- no networking, no crypto, no belief modeling.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from police_thief.domain.board import Board, Move, MoveRejectedError, Position
from police_thief.domain.capture import check_capture, is_boxed_in
from police_thief.domain.scoring import MatchOutcome, ScoringTable, score_for
from police_thief.shared.game_config import MatchParameters

Policy = Callable[[Board, Position, Position], Move]

_ORTHOGONAL = (Move.NORTH, Move.SOUTH, Move.EAST, Move.WEST)


def _manhattan(a: Position, b: Position) -> int:
    return abs(a.row - b.row) + abs(a.col - b.col)


@dataclass(frozen=True)
class MatchResult:
    """The final outcome of one simulated match."""

    outcome: MatchOutcome
    cop_score: int
    thief_score: int
    turns_played: int


def move_toward_policy(board: Board, own: Position, target: Position) -> Move:
    """Placeholder: greedily reduce Manhattan distance to `target`. Not real strategy."""
    best_move, best_distance = Move.STAY, _manhattan(own, target)
    for move in _ORTHOGONAL:
        try:
            candidate = board.apply_move(own, move)
        except MoveRejectedError:
            continue
        if (distance := _manhattan(candidate, target)) < best_distance:
            best_move, best_distance = move, distance
    return best_move


def move_away_policy(board: Board, own: Position, threat: Position) -> Move:
    """Placeholder: greedily increase Manhattan distance from `threat`. Not real strategy."""
    best_move, best_distance = Move.STAY, _manhattan(own, threat)
    for move in _ORTHOGONAL:
        try:
            candidate = board.apply_move(own, move)
        except MoveRejectedError:
            continue
        if (distance := _manhattan(candidate, threat)) > best_distance:
            best_move, best_distance = move, distance
    return best_move


def run_local_match(
    params: MatchParameters,
    cop_policy: Policy = move_toward_policy,
    thief_policy: Policy = move_away_policy,
) -> MatchResult:
    """Alternate cop/thief turns until capture, survival, or max_moves.

    max_moves vs. survival_threshold precedence (docs/TODO.md T0137):
    survival_threshold is checked every turn and is expected to be <=
    max_moves; max_moves is a hard safety cap that also resolves to a
    SURVIVAL outcome if somehow reached first, so the match always
    terminates deterministically either way.
    """
    board = Board(params.board)
    cop_pos, thief_pos = params.cop_start, params.thief_start
    scoring: ScoringTable = params.scoring

    for turn in range(1, params.max_moves + 1):
        cop_pos = board.apply_move(cop_pos, cop_policy(board, cop_pos, thief_pos))
        if check_capture(cop_pos, thief_pos):
            return MatchResult(MatchOutcome.CAPTURE, *score_for(MatchOutcome.CAPTURE, scoring), turn)

        # Not exercised by any current test: the placeholder policies (this
        # chapter's scope) never place barriers, so a mid-match boxed-in
        # thief cannot occur yet. The check stays here because it is
        # correct and forward-looking -- Chapter 6's barrier-placing
        # strategies will reach it -- not because it is currently dead code
        # by mistake. board.py/test_capture.py already prove is_boxed_in()
        # itself is correct in isolation.
        if is_boxed_in(board, thief_pos):
            return MatchResult(MatchOutcome.CAPTURE, *score_for(MatchOutcome.CAPTURE, scoring), turn)
        thief_pos = board.apply_move(thief_pos, thief_policy(board, thief_pos, cop_pos))
        if check_capture(cop_pos, thief_pos):
            # Also not exercised: the greedy flee policy never steps onto
            # the cop's cell by construction. Kept for defensive symmetry
            # with the pre-thief-move capture check above.
            return MatchResult(MatchOutcome.CAPTURE, *score_for(MatchOutcome.CAPTURE, scoring), turn)

        if turn >= params.survival_threshold:
            return MatchResult(MatchOutcome.SURVIVAL, *score_for(MatchOutcome.SURVIVAL, scoring), turn)

    return MatchResult(
        MatchOutcome.SURVIVAL, *score_for(MatchOutcome.SURVIVAL, scoring), params.max_moves
    )
