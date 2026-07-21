"""Shared NxN grid-drawing widget, composed by both LiveGUI and ReplayGUI.

Extracted once both windows needed the same "draw a grid of colored cells,
plus a distinct circular marker for a tracked position, plus a faint dot
trail for previously-visited cells" logic -- the same DRY precedent as
Chapter 6's heuristics.py extraction. This is a pure drawing primitive: it
holds no game/match state and makes no rendering decisions of its own
(no color choice, no belief math) -- callers decide what to draw, this
class only knows how to put it on screen.

Loosely inspired by the course's reference example repo's own board_view.py
(a plain grid + colored-circle-with-letter agent marker), but re-implemented
against this project's own data shapes rather than reused verbatim -- see
docs/tasks.md Appendix D's own usage terms (a learning starting point, not
a submission template).
"""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable

CELL_SIZE = 32
_LEGAL_MOVE_OUTLINE = "#2e7d32"  # green -- a cell the human player may click


class BoardCanvas(tk.Canvas):
    """An NxN grid of colored cells, with optional agent-marker/trail overlays."""

    def __init__(self, master: tk.Misc, grid_size: int) -> None:
        self.grid_size = grid_size
        side = grid_size * CELL_SIZE
        super().__init__(master, width=side, height=side, highlightthickness=1, highlightbackground="#888888")
        self._rects: dict[tuple[int, int], int] = {}
        self._marker_ids: list[int] = []
        self._legal_cells: set[tuple[int, int]] = set()
        self._click_callback: Callable[[int, int], None] | None = None
        for row in range(grid_size):
            for col in range(grid_size):
                x0, y0 = col * CELL_SIZE, row * CELL_SIZE
                self._rects[(row, col)] = self.create_rectangle(
                    x0, y0, x0 + CELL_SIZE, y0 + CELL_SIZE, fill="#ffffff", outline="#cccccc"
                )
        self.bind("<Button-1>", self._on_click)

    def set_cell_color(self, row: int, col: int, color: str) -> None:
        self.itemconfig(self._rects[(row, col)], fill=color)

    def set_cell_outline(self, row: int, col: int, color: str) -> None:
        self.itemconfig(self._rects[(row, col)], outline=color)

    def cell_from_pixel(self, x: int, y: int) -> tuple[int, int] | None:
        """Translate a canvas-relative pixel coordinate to a `(row, col)`
        cell, or `None` if the click landed outside the grid entirely."""
        row, col = y // CELL_SIZE, x // CELL_SIZE
        if (row, col) in self._rects:
            return (row, col)
        return None

    def set_click_handler(self, callback: Callable[[int, int], None] | None) -> None:
        """`callback(row, col)` fires on every left-click inside the grid.
        Pass `None` to disable clicking (e.g. when it isn't a human's turn).
        """
        self._click_callback = callback

    def _on_click(self, event: tk.Event) -> None:
        if self._click_callback is None:
            return
        cell = self.cell_from_pixel(event.x, event.y)
        if cell is not None:
            self._click_callback(*cell)

    def highlight_legal_cells(self, cells: set[tuple[int, int]]) -> None:
        """Outline every cell in `cells` distinctly, so a human player can
        see exactly where they're allowed to click. Replaces any previous
        highlight -- call with an empty set to clear it."""
        for row, col in self._legal_cells - cells:
            self.set_cell_outline(row, col, "#cccccc")
        for row, col in cells:
            self.set_cell_outline(row, col, _LEGAL_MOVE_OUTLINE)
        self._legal_cells = set(cells)

    def clear_markers(self) -> None:
        """Remove every agent marker/trail dot drawn since the last clear."""
        for marker_id in self._marker_ids:
            self.delete(marker_id)
        self._marker_ids.clear()

    def draw_dot(self, row: int, col: int, color: str) -> None:
        """A small, subdued dot -- for a visited-cell trail."""
        x0, y0 = col * CELL_SIZE, row * CELL_SIZE
        inset = CELL_SIZE * 0.36
        marker = self.create_oval(
            x0 + inset, y0 + inset, x0 + CELL_SIZE - inset, y0 + CELL_SIZE - inset,
            fill=color, outline="",
        )
        self._marker_ids.append(marker)

    def draw_agent(self, row: int, col: int, label: str, fill: str, outline: str = "#000000") -> None:
        """A prominent circular marker with a short text label (a role initial)."""
        x0, y0 = col * CELL_SIZE, row * CELL_SIZE
        inset = 4
        oval = self.create_oval(
            x0 + inset, y0 + inset, x0 + CELL_SIZE - inset, y0 + CELL_SIZE - inset,
            fill=fill, outline=outline, width=2,
        )
        text = self.create_text(
            x0 + CELL_SIZE / 2, y0 + CELL_SIZE / 2, text=label,
            fill="white", font=("Segoe UI", 11, "bold"),
        )
        self._marker_ids.extend([oval, text])
