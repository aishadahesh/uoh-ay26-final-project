"""Unit tests for the shared Manhattan-distance search helper (Chapter 6, Sec. 6.3.2)."""

import pytest

from police_thief.domain.board import Board, BoardConfig, Move, Position
from police_thief.domain.heuristics import greedy_manhattan_move, manhattan_distance


@pytest.mark.parametrize(
    ("a", "b", "expected"),
    [
        (Position(2, 2), Position(5, 5), 6),  # docs/tasks.md Sec. 6.3.3's own worked example
        (Position(0, 0), Position(0, 0), 0),
        (Position(0, 0), Position(6, 6), 12),
    ],
)
def test_manhattan_distance_matches_hand_computed_examples(a, b, expected):
    assert manhattan_distance(a, b) == expected


def test_worked_example_east_or_north_both_minimize_distance_by_one():
    """Sec. 6.3.3: cop at (2,2), belief peak (5,5) -> D=6. East (3,2) and
    north (2,3) [using this project's (row,col) convention] both give D=5;
    west (1,2) gives D=7. The greedy search must never pick the worsening
    move.
    """
    board = Board(BoardConfig(grid_size=7, max_barriers=14))
    cop = Position(2, 2)
    target = Position(5, 5)
    chosen = greedy_manhattan_move(board, cop, target, chase=True)
    resulting = board.apply_move(cop, chosen)
    assert manhattan_distance(resulting, target) == 5


def test_greedy_chase_strictly_decreases_distance_when_possible():
    board = Board(BoardConfig(grid_size=7, max_barriers=14))
    own, target = Position(0, 0), Position(6, 6)
    move = greedy_manhattan_move(board, own, target, chase=True)
    new_pos = board.apply_move(own, move)
    assert manhattan_distance(new_pos, target) < manhattan_distance(own, target)


def test_greedy_flee_strictly_increases_distance_when_possible():
    board = Board(BoardConfig(grid_size=7, max_barriers=14))
    own, threat = Position(3, 3), Position(3, 4)
    move = greedy_manhattan_move(board, own, threat, chase=False)
    new_pos = board.apply_move(own, move)
    assert manhattan_distance(new_pos, threat) > manhattan_distance(own, threat)


def test_greedy_move_stays_when_already_at_the_target():
    board = Board(BoardConfig(grid_size=7, max_barriers=14))
    target = Position(3, 3)
    assert greedy_manhattan_move(board, target, target, chase=True) == Move.STAY


def test_tie_breaking_is_deterministic_by_fixed_iteration_order():
    """No explicit tie-break rule beyond "first orthogonal move (N,S,E,W)
    that improves distance wins" -- deterministic and reproducible, which
    is what matters for a reproducible match, not any particular tie
    preference.
    """
    board = Board(BoardConfig(grid_size=7, max_barriers=14))
    own, target = Position(3, 3), Position(5, 5)  # NORTH/SOUTH tie is impossible here;
    # EAST and SOUTH both reduce distance equally from (3,3) toward (5,5).
    move_a = greedy_manhattan_move(board, own, target, chase=True)
    move_b = greedy_manhattan_move(board, own, target, chase=True)
    assert move_a == move_b  # deterministic: same inputs, same output every time
