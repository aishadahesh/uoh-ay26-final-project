"""Interactive play mode: a mode-selectable, human-playable match window.

A deliberate addition beyond docs/tasks.md's own scope -- see
domain/interactive_match.py's module docstring for why, and for the one
explicit, user-confirmed exception to Local Truth (Human vs Human hotseat
mode shows both true positions on a shared board).

Thin wiring only: every rule (turn order, legal moves, capture detection,
agent move computation) lives in `InteractiveMatch`. This class only
translates human input (move-pad buttons, board clicks) into calls on that
engine and renders whatever `VisibleView` it returns -- reusing Chapter 7's
`build_live_view_model` for the belief-driven rendering rather than
re-implementing belief-to-color logic a second time.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from police_thief.domain.board import Move, MoveRejectedError, Position
from police_thief.domain.interactive_match import InteractiveMatch
from police_thief.domain.live_view_model import TurnState, build_live_view_model
from police_thief.domain.scoring import MatchOutcome
from police_thief.gui.board_canvas import BoardCanvas
from police_thief.shared.constants import AgentRole

AGENT_MOVE_DELAY_MS = 500
_ROLE_LABEL = {AgentRole.COP: "C", AgentRole.THIEF: "T"}
_ROLE_FILL = {AgentRole.COP: "#1565c0", AgentRole.THIEF: "#c62828"}
_BARRIER_COLOR = "#2b2b2b"
_DIRECTIONS = [
    ("North", "NORTH"),
    ("South", "SOUTH"),
    ("East", "EAST"),
    ("West", "WEST"),
    ("Stay", "STAY"),
]
_OUTCOME_TEXT = {MatchOutcome.CAPTURE: "Capture!", MatchOutcome.SURVIVAL: "The thief survives!"}


class PlayApp:
    """Drives one `InteractiveMatch` inside a single Tkinter window."""

    def __init__(self, master: tk.Misc, match: InteractiveMatch) -> None:
        self.master = master
        self.match = match
        self._barrier_mode = False

        self.status_label = tk.Label(master, font=("Segoe UI", 13, "bold"))
        self.status_label.pack(fill="x")

        self.canvas = BoardCanvas(master, grid_size=match.board.config.grid_size)
        self.canvas.pack()

        controls = tk.Frame(master)
        controls.pack(pady=6)
        self.move_buttons: dict[Move, tk.Button] = {}
        for label, move_name in _DIRECTIONS:
            move = Move[move_name]
            button = tk.Button(controls, text=label, width=8, command=lambda m=move: self._on_human_move(m))
            button.pack(side="left", padx=2)
            self.move_buttons[move] = button

        self.barrier_button = tk.Button(master, text="Place Barrier (click a cell)", command=self._toggle_barrier_mode)
        self.barrier_button.pack(pady=(0, 6))

    def start(self) -> None:
        self._advance()

    # --- turn advancement ---------------------------------------------------

    def _advance(self) -> None:
        if self.match.is_finished:
            self._show_result()
            return
        if self.match.is_human_turn():
            self._enable_human_controls()
        else:
            self._disable_human_controls()
            self.master.after(AGENT_MOVE_DELAY_MS, self._agent_turn)
        self._render()

    def _agent_turn(self) -> None:
        if self.match.is_finished:
            return
        self.match.apply_move(self.match.agent_move())
        self._advance()

    def _on_human_move(self, move: Move) -> None:
        if self.match.is_finished or not self.match.is_human_turn() or move not in self.match.legal_moves():
            return
        self._barrier_mode = False
        self.match.apply_move(move)
        self._advance()

    def _toggle_barrier_mode(self) -> None:
        if self.match.is_finished or not self.match.is_human_turn() or self.match.current_role is not AgentRole.COP:
            return
        self._barrier_mode = not self._barrier_mode
        self._render()

    def _on_cell_click(self, row: int, col: int) -> None:
        if self.match.is_finished or not self.match.is_human_turn():
            return
        position = Position(row, col)
        if self._barrier_mode:
            try:
                self.match.place_barrier(position)
            except (MoveRejectedError, ValueError):
                return
            self._barrier_mode = False
            self._advance()
            return
        move = next((m for m, p in self.match.legal_moves().items() if p == position), None)
        if move is not None:
            self.match.apply_move(move)
            self._advance()

    # --- control enable/disable ---------------------------------------------

    def _enable_human_controls(self) -> None:
        legal = self.match.legal_moves()
        for move, button in self.move_buttons.items():
            button.config(state="normal" if move in legal else "disabled")
        is_cop = self.match.current_role is AgentRole.COP
        self.barrier_button.config(state="normal" if is_cop else "disabled")
        self.canvas.set_click_handler(self._on_cell_click)

    def _disable_human_controls(self) -> None:
        for button in self.move_buttons.values():
            button.config(state="disabled")
        self.barrier_button.config(state="disabled")
        self.canvas.set_click_handler(None)
        self._barrier_mode = False

    # --- rendering -----------------------------------------------------------

    def _render(self) -> None:
        view = self.match.visible_view_for_current()
        human_turn = self.match.is_human_turn()
        turn_word = "YOUR" if human_turn else "AGENT"
        self.status_label.config(text=f"{view.own_role.value.upper()}'s turn ({turn_word})")

        self.canvas.clear_markers()
        legal_cells = (
            {(p.row, p.col) for p in self.match.legal_moves().values()}
            if human_turn and not self._barrier_mode
            else set()
        )
        self.canvas.highlight_legal_cells(legal_cells)

        if view.belief is not None:
            turn_state = TurnState.YOUR_TURN if human_turn else TurnState.LOCKED
            vm = build_live_view_model(view.own_position, view.belief, self.match.board, turn_state, role_label=_ROLE_LABEL[view.own_role])
            for cell in vm.cells:
                self.canvas.set_cell_color(cell.position.row, cell.position.col, cell.color)
            self.canvas.draw_agent(view.own_position.row, view.own_position.col, _ROLE_LABEL[view.own_role], _ROLE_FILL[view.own_role])
        else:
            grid_size = self.match.board.config.grid_size
            for row in range(grid_size):
                for col in range(grid_size):
                    pos = Position(row, col)
                    color = _BARRIER_COLOR if self.match.board.is_blocked(pos) else "#ffffff"
                    self.canvas.set_cell_color(row, col, color)
            self.canvas.draw_agent(view.own_position.row, view.own_position.col, _ROLE_LABEL[view.own_role], _ROLE_FILL[view.own_role])
            if view.opponent_position is not None:
                other = AgentRole.THIEF if view.own_role is AgentRole.COP else AgentRole.COP
                self.canvas.draw_agent(view.opponent_position.row, view.opponent_position.col, _ROLE_LABEL[other], _ROLE_FILL[other])

    def _show_result(self) -> None:
        self._disable_human_controls()
        text = _OUTCOME_TEXT.get(self.match.outcome, str(self.match.outcome))
        self.status_label.config(text=f"Match over: {text}")
        messagebox.showinfo("Match Over", text)
