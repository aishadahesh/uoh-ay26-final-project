"""Unit tests for the thin Tkinter GUI layer (Chapter 7).

Tkinter works headlessly on this platform (verified: Tk() constructs and
widgets can be inspected/invoked without ever calling mainloop() or
showing a window -- root.withdraw() keeps it off-screen). These tests
exercise real widget construction, state, and button wiring rather than
mocking Tkinter away, since the actual risk in a "thin wiring" layer is a
typo in a widget option name or a wrong callback, which only a real
widget catches.
"""

import dataclasses
import tkinter as tk

import pytest

from police_thief.domain.belief import BeliefMap
from police_thief.domain.board import Board, BoardConfig, Position
from police_thief.domain.live_view_model import TurnState, build_live_view_model
from police_thief.domain.replay import ReplaySession
from police_thief.domain.scent import ScentConfig, ScentField
from police_thief.gui.live_gui import LiveGUI
from police_thief.gui.replay_gui import ReplayGUI
from police_thief.services.commit_reveal import LogEntry, commit


@pytest.fixture(scope="session")
def tk_root():
    """One Tk() interpreter for the whole test session.

    Tkinter does not reliably support creating and destroying many Tk()
    root instances within a single process (verified: it fails with
    'invalid command name "tcl_findLibrary"' after a handful of create/
    destroy cycles) -- so tests share one root and each gets its own
    Toplevel for isolation instead.
    """
    window = tk.Tk()
    window.withdraw()
    yield window
    window.destroy()


@pytest.fixture
def root(tk_root):
    window = tk.Toplevel(tk_root)
    window.withdraw()
    yield window
    window.destroy()


def _belief_peaked_at(grid_size: int, peak: Position) -> tuple[Board, BeliefMap]:
    board = Board(BoardConfig(grid_size=grid_size, max_barriers=14))
    scent = ScentField(grid_size=grid_size, config=ScentConfig())
    scent.emit(peak)
    belief = BeliefMap(board)
    belief.update_from_scent(scent)
    return board, belief


def test_live_gui_constructs_one_cell_rect_per_board_position(root):
    gui = LiveGUI(root, grid_size=7)
    assert len(gui._rects) == 49


def test_live_gui_render_updates_the_banner_text_and_color(root):
    board, belief = _belief_peaked_at(7, Position(5, 5))
    vm = build_live_view_model(Position(0, 0), belief, board, TurnState.YOUR_TURN)
    gui = LiveGUI(root, grid_size=7)
    gui.render(vm)
    assert gui.banner.cget("text") == "YOUR TURN"
    assert gui.banner.cget("fg") == "#2e7d32"


def test_live_gui_render_colors_the_belief_peak_cell(root):
    board, belief = _belief_peaked_at(7, Position(5, 5))
    vm = build_live_view_model(Position(0, 0), belief, board, TurnState.YOUR_TURN)
    gui = LiveGUI(root, grid_size=7)
    gui.render(vm)
    rect_id = gui._rects[(5, 5)]
    assert gui.canvas.itemcget(rect_id, "fill") == "#c80000"


def test_live_gui_render_outlines_only_the_own_position_cell(root):
    board, belief = _belief_peaked_at(7, Position(5, 5))
    vm = build_live_view_model(Position(2, 2), belief, board, TurnState.YOUR_TURN)
    gui = LiveGUI(root, grid_size=7)
    gui.render(vm)
    own_rect = gui._rects[(2, 2)]
    other_rect = gui._rects[(0, 0)]
    assert gui.canvas.itemcget(own_rect, "outline") == "#000000"
    assert gui.canvas.itemcget(other_rect, "outline") == "#cccccc"


def test_live_gui_locked_banner_renders_gray(root):
    board, belief = _belief_peaked_at(7, Position(5, 5))
    vm = build_live_view_model(Position(0, 0), belief, board, TurnState.LOCKED)
    gui = LiveGUI(root, grid_size=7)
    gui.render(vm)
    assert gui.banner.cget("text") == "LOCKED"
    assert gui.banner.cget("fg") == "#616161"


def test_live_gui_render_shows_a_barrier_cell_in_its_distinct_color(root):
    board, belief = _belief_peaked_at(7, Position(5, 5))
    board.place_barrier(Position(5, 4), Position(5, 5))
    vm = build_live_view_model(Position(0, 0), belief, board, TurnState.YOUR_TURN)
    gui = LiveGUI(root, grid_size=7)
    gui.render(vm)
    rect_id = gui._rects[(5, 5)]
    assert gui.canvas.itemcget(rect_id, "fill") == "#2b2b2b"


def _make_entries(n: int) -> list[LogEntry]:
    entries = []
    for i in range(n):
        c = commit(state={"turn": i}, move="N", intent=True)
        entries.append(LogEntry(state={"turn": i}, move="N", intent=True, nonce=c.nonce, h_commit=c.h_commit))
    return entries


def test_replay_gui_shows_step_one_of_n_on_construction(root):
    session = ReplaySession(_make_entries(5))
    gui = ReplayGUI(root, session)
    assert gui.step_label.cget("text") == "Step 1 / 5"


def test_replay_gui_shows_verified_ok_in_green_on_a_clean_log(root):
    session = ReplaySession(_make_entries(3))
    gui = ReplayGUI(root, session)
    assert gui.status_label.cget("text") == "Verified OK"
    assert gui.status_label.cget("fg") == "#2e7d32"


def test_replay_gui_shows_tampered_in_red_at_the_tampered_step(root):
    entries = _make_entries(4)
    tampered = list(entries)
    tampered[1] = dataclasses.replace(tampered[1], move="TAMPERED")
    session = ReplaySession(tampered)
    gui = ReplayGUI(root, session)
    gui.next_button.invoke()  # advance to step index 1 (the tampered one)
    assert gui.status_label.cget("text") == "TAMPERED"
    assert gui.status_label.cget("fg") == "#c62828"


def test_replay_gui_next_button_advances_the_step_label(root):
    session = ReplaySession(_make_entries(4))
    gui = ReplayGUI(root, session)
    gui.next_button.invoke()
    assert gui.step_label.cget("text") == "Step 2 / 4"


def test_replay_gui_previous_button_retreats_the_step_label(root):
    session = ReplaySession(_make_entries(4))
    gui = ReplayGUI(root, session)
    gui.next_button.invoke()
    gui.next_button.invoke()
    gui.prev_button.invoke()
    assert gui.step_label.cget("text") == "Step 2 / 4"


def test_replay_gui_detail_label_reflects_the_current_steps_move(root):
    session = ReplaySession(_make_entries(2))
    gui = ReplayGUI(root, session)
    assert "move='N'" in gui.detail_label.cget("text")


def test_replay_gui_summary_label_shows_verified_and_tampered_counts(root):
    entries = _make_entries(5)
    tampered = list(entries)
    tampered[2] = dataclasses.replace(tampered[2], move="X")
    session = ReplaySession(tampered)
    gui = ReplayGUI(root, session)
    assert gui.summary_label.cget("text") == "2 verified / 3 tampered (of 5 total steps)"
