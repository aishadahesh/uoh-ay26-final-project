"""The Live GUI: local-truth-only heatmap and turn banner (Chapter 7, Sec. 7.3).

Thin wiring only -- every color and text decision already happened in
domain/live_view_model.py::LiveViewModel. This class just draws it and
never computes anything itself, so it structurally cannot leak the
opponent's true position even by accident: it has no such data to draw.

Composes gui/board_canvas.py::BoardCanvas for the grid itself, plus a
prominent circular marker (with a role-initial label) on the own-position
cell and a faint trail of dots over this side's own previously-visited
cells -- a purely cosmetic upgrade over a plain cell outline, since
`LiveViewModel.role_label`/`.visited` are both this side's own data only.
"""

from __future__ import annotations

import tkinter as tk

from police_thief.domain.live_view_model import LiveViewModel
from police_thief.gui.board_canvas import BoardCanvas

_OWN_OUTLINE = "#000000"
_OTHER_OUTLINE = "#cccccc"
_AGENT_FILL = "#1565c0"
_TRAIL_DOT_COLOR = "#9e9e9e"


class LiveGUI:
    """A grid of colored cells plus a turn-state banner, for one side only."""

    def __init__(self, master: tk.Misc, grid_size: int) -> None:
        self.master = master
        self.grid_size = grid_size
        self.banner = tk.Label(master, text="", font=("Segoe UI", 14, "bold"))
        self.banner.pack(fill="x")
        self.step_label = tk.Label(master, text="Step 0", font=("Segoe UI", 9))
        self.step_label.pack()
        self.canvas = BoardCanvas(master, grid_size)
        self.canvas.pack()
        self._rects = self.canvas._rects  # kept for backward-compatible test/introspection access
        self._step = 0

    def render(self, view_model: LiveViewModel) -> None:
        """Redraw the grid and banner from a fully-computed view model."""
        self._step += 1
        self.step_label.config(text=f"Step {self._step}")
        self.banner.config(text=view_model.turn_banner_text, fg=view_model.turn_banner_color)
        self.canvas.clear_markers()
        for cell in view_model.cells:
            self.canvas.set_cell_color(cell.position.row, cell.position.col, cell.color)
            outline = _OWN_OUTLINE if cell.is_own_position else _OTHER_OUTLINE
            self.canvas.set_cell_outline(cell.position.row, cell.position.col, outline)
        for pos in view_model.visited:
            if pos != view_model.own_position:
                self.canvas.draw_dot(pos.row, pos.col, _TRAIL_DOT_COLOR)
        own = view_model.own_position
        self.canvas.draw_agent(own.row, own.col, view_model.role_label, _AGENT_FILL)
