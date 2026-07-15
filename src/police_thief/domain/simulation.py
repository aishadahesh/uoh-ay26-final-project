"""Single-process local simulation harness (Chapters 3-4).

Placeholder-policy only: real strategic decision-making is Chapter 6's
domain (heuristics, a custom algorithm, or optionally reinforcement
learning). The policies here exist purely to prove the board/movement/
barrier/capture/scoring/scent logic plays a full, legal match end-to-end
with no crash -- no networking, no crypto, no belief modeling yet.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from police_thief.domain.board import Board, Move, MoveRejectedError, Position
from police_thief.domain.capture import check_capture, is_boxed_in
from police_thief.domain.scent import ScentField
from police_thief.domain.scoring import MatchOutcome, ScoringTable, score_for
from police_thief.shared.game_config import MatchParameters

Policy = Callable[[Board, Position, Position], Move]

_ORTHOGONAL = (Move.NORTH, Move.SOUTH, Move.EAST, Move.WEST)


def _manhattan(a: Position, b: Position) -> int:
    return abs(a.row - b.row) + abs(a.col - b.col)


@dataclass(frozen=True)
class MatchResult:
    """The final outcome of one simulated match.

    cop_scent/thief_scent are each side's *own* emitted trail at match end
    (named after who emits it, not who reads it -- docs/tasks.md Sec. 4.1.3).
    Exposed for inspection/testing only; no policy in this chapter reads
    them to make a decision -- that is Chapter 6's belief-map territory.
    """

    outcome: MatchOutcome
    cop_score: int
    thief_score: int
    turns_played: int
    cop_scent: ScentField
    thief_scent: ScentField


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

    Scent (Chapter 4): every turn, after each side's move resolves, that
    side's own ScentField decays (the whole board's forgetting step) and
    then emits fresh around its new position -- reproducing the mandatory
    tau(t+1) = max(0, (1-rho)*tau(t) + delta_tau) equation in two calls.
    """
    board = Board(params.board)
    cop_pos, thief_pos = params.cop_start, params.thief_start
    scoring: ScoringTable = params.scoring
    cop_scent = ScentField(params.board.grid_size, params.scent)
    thief_scent = ScentField(params.board.grid_size, params.scent)

    def finish(outcome: MatchOutcome, turn: int) -> MatchResult:
        cop_score, thief_score = score_for(outcome, scoring)
        return MatchResult(outcome, cop_score, thief_score, turn, cop_scent, thief_scent)

    for turn in range(1, params.max_moves + 1):
        cop_pos = board.apply_move(cop_pos, cop_policy(board, cop_pos, thief_pos))
        cop_scent.decay()
        cop_scent.emit(cop_pos)
        if check_capture(cop_pos, thief_pos):
            return finish(MatchOutcome.CAPTURE, turn)

        # Not exercised by any current test: the placeholder policies (this
        # chapter's scope) never place barriers, so a mid-match boxed-in
        # thief cannot occur yet. The check stays here because it is
        # correct and forward-looking -- Chapter 6's barrier-placing
        # strategies will reach it -- not because it is currently dead code
        # by mistake. board.py/test_capture.py already prove is_boxed_in()
        # itself is correct in isolation.
        if is_boxed_in(board, thief_pos):
            return finish(MatchOutcome.CAPTURE, turn)
        thief_pos = board.apply_move(thief_pos, thief_policy(board, thief_pos, cop_pos))
        thief_scent.decay()
        thief_scent.emit(thief_pos)
        if check_capture(cop_pos, thief_pos):
            # Also not exercised: the greedy flee policy never steps onto
            # the cop's cell by construction. Kept for defensive symmetry
            # with the pre-thief-move capture check above.
            return finish(MatchOutcome.CAPTURE, turn)

        if turn >= params.survival_threshold:
            return finish(MatchOutcome.SURVIVAL, turn)

    return finish(MatchOutcome.SURVIVAL, params.max_moves)
