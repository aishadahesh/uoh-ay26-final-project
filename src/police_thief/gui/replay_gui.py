"""The Replay Viewer: scrubbing controls + cryptographic verification stamp
(Chapter 7, Sec. 7.4-7.5).

Thin wiring only -- every verification decision already happened in
domain/replay.py::ReplaySession (which itself reuses Chapter 5's audit_log).
This class just displays "VERIFIED OK" (green) or "TAMPERED" (red) per
step and lets a human scrub forward/backward; it recomputes nothing.
"""

from __future__ import annotations

import tkinter as tk

from police_thief.domain.replay import VERIFIED_OK, ReplaySession

_STATUS_COLOR = {VERIFIED_OK: "#2e7d32", "TAMPERED": "#c62828"}  # green / red
_STATUS_TEXT = {VERIFIED_OK: "Verified OK", "TAMPERED": "TAMPERED"}


class ReplayGUI:
    """Prev/Next-driven scrubber over a ReplaySession, with a status stamp."""

    def __init__(self, master: tk.Misc, session: ReplaySession) -> None:
        self.master = master
        self.session = session

        self.step_label = tk.Label(master, font=("Segoe UI", 11))
        self.step_label.pack()
        self.status_label = tk.Label(master, font=("Segoe UI", 16, "bold"))
        self.status_label.pack()
        self.detail_label = tk.Label(master, font=("Consolas", 10), justify="left")
        self.detail_label.pack()

        buttons = tk.Frame(master)
        buttons.pack()
        self.prev_button = tk.Button(buttons, text="< Previous", command=self._on_previous)
        self.prev_button.pack(side="left")
        self.next_button = tk.Button(buttons, text="Next >", command=self._on_next)
        self.next_button.pack(side="left")

        self.summary_label = tk.Label(master, font=("Segoe UI", 9))
        self.summary_label.pack()
        self.summary_label.config(
            text=f"{session.verified_count} verified / {session.tampered_count} tampered "
            f"(of {session.total_steps} total steps)"
        )

        self._render_current()

    def _on_previous(self) -> None:
        self.session.previous()
        self._render_current()

    def _on_next(self) -> None:
        self.session.next()
        self._render_current()

    def _render_current(self) -> None:
        step = self.session.current_step
        self.step_label.config(text=f"Step {step.index + 1} / {self.session.total_steps}")
        self.status_label.config(
            text=_STATUS_TEXT[step.status], fg=_STATUS_COLOR[step.status]
        )
        self.detail_label.config(
            text=f"move={step.entry.move!r}\nintent={step.entry.intent!r}\nh_commit={step.entry.h_commit[:16]}..."
        )
