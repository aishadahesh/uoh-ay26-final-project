"""Unit tests for the Live GUI's local-truth-only view-model (Chapter 7)."""

import dataclasses
import inspect

import pytest

from police_thief.domain.belief import BeliefMap
from police_thief.domain.board import Board, BoardConfig, Position
from police_thief.domain.live_view_model import (
    LiveViewModel,
    TurnState,
    belief_to_color,
    build_live_view_model,
)
from police_thief.domain.scent import ScentConfig, ScentField


def test_belief_to_color_at_zero_intensity_is_white():
    assert belief_to_color(0.0, max_intensity=1.0) == "#ffffff"


def test_belief_to_color_at_peak_intensity_is_deep_red():
    assert belief_to_color(1.0, max_intensity=1.0) == "#c80000"


def test_belief_to_color_handles_a_zero_max_intensity_without_crashing():
    assert belief_to_color(0.0, max_intensity=0.0) == "#ffffff"


def test_belief_to_color_is_monotonic_between_white_and_red():
    low = belief_to_color(0.2, max_intensity=1.0)
    high = belief_to_color(0.8, max_intensity=1.0)
    # Red channel stays saturated; green/blue should decrease as intensity rises.
    assert int(low[3:5], 16) > int(high[3:5], 16)


@pytest.fixture
def board() -> Board:
    return Board(BoardConfig(grid_size=7, max_barriers=14))


def _belief_peaked_at(board: Board, peak: Position) -> BeliefMap:
    scent = ScentField(grid_size=board.config.grid_size, config=ScentConfig())
    scent.emit(peak)
    belief = BeliefMap(board)
    belief.update_from_scent(scent)
    return belief


def test_build_live_view_model_has_one_cell_per_board_position(board):
    belief = _belief_peaked_at(board, Position(5, 5))
    vm = build_live_view_model(Position(0, 0), belief, board, TurnState.YOUR_TURN)
    assert len(vm.cells) == 49


def test_build_live_view_model_marks_exactly_the_own_position(board):
    belief = _belief_peaked_at(board, Position(5, 5))
    vm = build_live_view_model(Position(2, 3), belief, board, TurnState.YOUR_TURN)
    own_cells = [c for c in vm.cells if c.is_own_position]
    assert len(own_cells) == 1
    assert own_cells[0].position == Position(2, 3)


def test_build_live_view_model_colors_the_belief_peak_reddest(board):
    belief = _belief_peaked_at(board, Position(5, 5))
    vm = build_live_view_model(Position(0, 0), belief, board, TurnState.YOUR_TURN)
    peak_cell = next(c for c in vm.cells if c.position == Position(5, 5))
    far_cell = next(c for c in vm.cells if c.position == Position(0, 6))
    assert peak_cell.color == "#c80000"
    assert far_cell.color != peak_cell.color


def test_build_live_view_model_renders_a_barrier_cell_distinctly_never_a_belief_color(board):
    """T0405: a blocked cell must never show a belief-gradient color, even
    if the (physically real, but game-illegal) scent field has intensity
    there -- it structurally can never hold the opponent.
    """
    board.place_barrier(Position(5, 4), Position(5, 5))
    belief = _belief_peaked_at(board, Position(5, 5))  # scent still emits there physically
    vm = build_live_view_model(Position(0, 0), belief, board, TurnState.YOUR_TURN)
    barrier_cell = next(c for c in vm.cells if c.position == Position(5, 5))
    assert barrier_cell.is_blocked is True
    assert barrier_cell.color == "#2b2b2b"


def test_your_turn_banner_is_green_and_correctly_labeled(board):
    belief = _belief_peaked_at(board, Position(5, 5))
    vm = build_live_view_model(Position(0, 0), belief, board, TurnState.YOUR_TURN)
    assert vm.turn_banner_text == "YOUR TURN"
    assert vm.turn_banner_color == "#2e7d32"


def test_locked_banner_is_gray_and_correctly_labeled(board):
    belief = _belief_peaked_at(board, Position(5, 5))
    vm = build_live_view_model(Position(0, 0), belief, board, TurnState.LOCKED)
    assert vm.turn_banner_text == "LOCKED"
    assert vm.turn_banner_color == "#616161"


def test_live_view_model_has_no_field_capable_of_holding_an_opponent_position():
    """Structural guarantee (Sec. 7.3.3 FORBIDDEN): there is no field in
    LiveViewModel, and no parameter in build_live_view_model, through which
    the opponent's true position could even be represented.
    """
    field_names = {f.name for f in dataclasses.fields(LiveViewModel)}
    assert field_names == {"own_position", "cells", "turn_state", "turn_banner_text", "turn_banner_color"}
    params = set(inspect.signature(build_live_view_model).parameters)
    assert "opponent_position" not in params
    assert params == {"own_position", "belief", "board", "turn_state"}
