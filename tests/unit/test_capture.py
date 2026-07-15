"""Unit tests for capture detection (Chapter 3)."""

from police_thief.domain.board import Board, BoardConfig, Position
from police_thief.domain.capture import CaptureClaim, check_capture, is_boxed_in
from police_thief.shared.constants import AgentRole


def test_check_capture_true_when_positions_match():
    assert check_capture(Position(2, 2), Position(2, 2))


def test_check_capture_false_when_positions_differ():
    assert not check_capture(Position(2, 2), Position(2, 3))


def test_is_boxed_in_false_in_open_space():
    board = Board(BoardConfig(grid_size=7, max_barriers=14))
    assert not is_boxed_in(board, Position(3, 3))


def test_is_boxed_in_true_when_all_neighbors_blocked():
    board = Board(BoardConfig(grid_size=7, max_barriers=14))
    thief = Position(3, 3)
    for neighbor in board.neighbors(thief):
        board.place_barrier(thief, neighbor)
    assert is_boxed_in(board, thief)


def test_is_boxed_in_true_when_cornered_by_board_edges_and_barriers():
    board = Board(BoardConfig(grid_size=7, max_barriers=14))
    thief = Position(0, 0)  # corner: only 2 orthogonal neighbors exist at all
    for neighbor in board.neighbors(thief):
        board.place_barrier(thief, neighbor)
    assert is_boxed_in(board, thief)


def test_barrier_placed_exactly_on_thiefs_cell_counts_as_capture():
    """Sec. 3.3.5: a barrier landing on the thief's cell captures it, same as a move.

    check_capture() is deliberately generic position-equality -- it does not
    care whether the cop's claimed position arose from a move or a barrier
    placement, so the same function correctly covers both rules at once.
    """
    board = Board(BoardConfig(grid_size=7, max_barriers=14))
    cop_pos = Position(3, 2)
    thief_pos = Position(3, 3)
    barrier_target = thief_pos  # the cop chooses to barrier exactly the thief's cell
    board.place_barrier(cop_pos, barrier_target)
    assert board.is_blocked(barrier_target)
    assert check_capture(barrier_target, thief_pos)


def test_capture_claim_records_claimant_and_position():
    claim = CaptureClaim(claimant=AgentRole.COP, position=Position(2, 2))
    assert claim.claimant is AgentRole.COP
    assert claim.position == Position(2, 2)
