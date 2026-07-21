"""Mode-select dialog for the interactive play mode.

A modal `Toplevel` with one radio button per `GameMode` plus a Start
button. `show()` blocks (via `wait_window`) until the dialog closes; the
caller gets back the chosen `GameMode`, or `None` if the window was closed
without starting.
"""

from __future__ import annotations

import tkinter as tk

from police_thief.domain.interactive_match import MODE_LABELS, GameMode


class ModeSelectDialog:
    def __init__(self, master: tk.Misc) -> None:
        self.result: GameMode | None = None
        self.window = tk.Toplevel(master)
        self.window.title("Choose Game Mode")

        self._mode_var = tk.StringVar(value=GameMode.AGENT_VS_AGENT.value)
        tk.Label(self.window, text="Select a game mode:", font=("Segoe UI", 11, "bold")).pack(
            anchor="w", padx=12, pady=(12, 6)
        )
        for mode, label in MODE_LABELS.items():
            tk.Radiobutton(self.window, text=label, value=mode.value, variable=self._mode_var).pack(
                anchor="w", padx=24
            )

        self.start_button = tk.Button(self.window, text="Start", command=self._on_start)
        self.start_button.pack(pady=12)

    def _on_start(self) -> None:
        self.result = GameMode(self._mode_var.get())
        self.window.destroy()

    def show(self) -> GameMode | None:
        """Block until the dialog closes; returns the chosen mode, or `None`
        if it was closed without clicking Start."""
        self.window.wait_window()
        return self.result
