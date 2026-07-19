"""Shared Tkinter root fixture for every GUI test file (Chapter 7).

Tkinter does not reliably support creating and destroying many Tk() root
instances within a single process (verified: it fails with 'invalid command
name "tcl_findLibrary"' / "Can't find a usable init.tcl" after a handful of
create/destroy cycles, or once a second file tries to create its own
session-scoped root). This one fixture is shared by every test module that
needs Tkinter (test_gui.py, test_board_canvas.py, ...) so exactly one Tk()
interpreter ever exists for the whole test session; each test gets its own
Toplevel for isolation instead.
"""

import tkinter as tk

import pytest


@pytest.fixture(scope="session")
def tk_root():
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
