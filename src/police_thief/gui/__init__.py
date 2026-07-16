"""Presentation-only Tkinter widgets (Chapter 7).

Per docs/PLAN.md's architectural principle 3 (SDK-layer architecture): no
business logic lives here. Both live_gui.py and replay_gui.py are thin
wiring between a framework-agnostic view-model/session (domain/
live_view_model.py, domain/replay.py) and actual widgets -- every decision
about colors, verification status, or banner state is already made before
it reaches this package.
"""
