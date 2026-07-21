"""Unit tests for the mode-select dialog (real Tkinter widgets, no mocking)."""

from police_thief.domain.interactive_match import GameMode
from police_thief.gui.mode_select import ModeSelectDialog


def test_dialog_defaults_to_agent_vs_agent(root):
    dialog = ModeSelectDialog(root)
    assert dialog._mode_var.get() == GameMode.AGENT_VS_AGENT.value
    assert dialog.result is None


def test_clicking_start_sets_the_result_to_the_selected_mode(root):
    dialog = ModeSelectDialog(root)
    dialog._mode_var.set(GameMode.HUMAN_VS_HUMAN.value)
    dialog.start_button.invoke()
    assert dialog.result is GameMode.HUMAN_VS_HUMAN


def test_clicking_start_destroys_the_dialog_window(root):
    dialog = ModeSelectDialog(root)
    dialog.start_button.invoke()
    assert not dialog.window.winfo_exists()


def test_show_blocks_until_start_is_clicked_then_returns_the_chosen_mode(root):
    """`show()` calls `wait_window()`, which runs the real Tcl event loop
    until the dialog is destroyed -- scheduling the click via `after()`
    lets that real event loop process it, a genuine exercise of the
    blocking call rather than a mock."""
    dialog = ModeSelectDialog(root)
    dialog._mode_var.set(GameMode.HUMAN_VS_HUMAN.value)
    root.after(10, dialog.start_button.invoke)
    result = dialog.show()
    assert result is GameMode.HUMAN_VS_HUMAN
