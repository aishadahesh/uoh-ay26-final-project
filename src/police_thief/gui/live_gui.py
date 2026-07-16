"""The Live GUI: local-truth-only heatmap and turn banner (Chapter 7, Sec. 7.3).

Thin wiring only -- every color and text decision already happened in
domain/live_view_model.py::LiveViewModel. This class just draws it and
never computes anything itself, so it structurally cannot leak the
opponent's true position even by accident: it has no such data to draw.
"""

from __future__ import annotations

import tkinter as tk

from police_thief.domain.live_view_model import LiveViewModel

_CELL_SIZE = 24


class LiveGUI:
    """A grid of colored cells plus a turn-state banner, for one side only."""

    def __init__(self, master: tk.Misc, grid_size: int) -> None:
        self.master = master
        self.grid_size = grid_size
        self.banner = tk.Label(master, text="", font=("Segoe UI", 14, "bold"))
        self.banner.pack(fill="x")
        self.canvas = tk.Canvas(
            master, width=grid_size * _CELL_SIZE, height=grid_size * _CELL_SIZE
        )
        self.canvas.pack()
        self._rects: dict[tuple[int, int], int] = {}
        self._draw_empty_grid()

    def _draw_empty_grid(self) -> None:
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x0, y0 = col * _CELL_SIZE, row * _CELL_SIZE
                rect_id = self.canvas.create_rectangle(
                    x0, y0, x0 + _CELL_SIZE, y0 + _CELL_SIZE, fill="#ffffff", outline="#cccccc"
                )
                self._rects[(row, col)] = rect_id

    def render(self, view_model: LiveViewModel) -> None:
        """Redraw the grid and banner from a fully-computed view model."""
        self.banner.config(text=view_model.turn_banner_text, fg=view_model.turn_banner_color)
        for cell in view_model.cells:
            rect_id = self._rects[(cell.position.row, cell.position.col)]
            outline = "#000000" if cell.is_own_position else "#cccccc"
            self.canvas.itemconfig(rect_id, fill=cell.color, outline=outline)
