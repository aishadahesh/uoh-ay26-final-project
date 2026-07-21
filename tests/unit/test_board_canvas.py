"""Unit tests for the shared BoardCanvas widget (Chapter 7 GUI enhancement).

Real Tkinter widget construction/inspection, same discipline as test_gui.py
-- no mocking, since a typo in a widget option is exactly what a real
widget catches and a mock would hide.
"""

from police_thief.gui.board_canvas import BoardCanvas

# tk_root/root fixtures live in tests/unit/conftest.py, shared across every
# GUI test file -- Tkinter does not reliably support creating more than one
# session-scoped Tk() root within a single process.


def test_board_canvas_constructs_one_rect_per_cell(root):
    canvas = BoardCanvas(root, grid_size=7)
    assert len(canvas._rects) == 49


def test_set_cell_color_updates_the_correct_rect(root):
    canvas = BoardCanvas(root, grid_size=7)
    canvas.set_cell_color(3, 4, "#ff0000")
    assert canvas.itemcget(canvas._rects[(3, 4)], "fill") == "#ff0000"
    assert canvas.itemcget(canvas._rects[(0, 0)], "fill") == "#ffffff"


def test_set_cell_outline_updates_the_correct_rect(root):
    canvas = BoardCanvas(root, grid_size=7)
    canvas.set_cell_outline(3, 4, "#000000")
    assert canvas.itemcget(canvas._rects[(3, 4)], "outline") == "#000000"


def test_draw_agent_creates_an_oval_and_a_labeled_text(root):
    canvas = BoardCanvas(root, grid_size=7)
    canvas.draw_agent(2, 2, "C", "#1565c0")
    texts = [canvas.itemcget(i, "text") for i in canvas.find_all() if canvas.type(i) == "text"]
    assert "C" in texts
    assert len(canvas._marker_ids) == 2  # one oval + one text


def test_draw_dot_creates_exactly_one_marker(root):
    canvas = BoardCanvas(root, grid_size=7)
    canvas.draw_dot(1, 1, "#9e9e9e")
    assert len(canvas._marker_ids) == 1


def test_clear_markers_removes_every_marker_but_not_the_grid(root):
    canvas = BoardCanvas(root, grid_size=7)
    canvas.draw_agent(2, 2, "C", "#1565c0")
    canvas.draw_dot(1, 1, "#9e9e9e")
    canvas.clear_markers()
    assert canvas._marker_ids == []
    assert len(canvas._rects) == 49  # the grid itself is untouched


def test_clear_markers_is_safe_to_call_when_nothing_was_drawn(root):
    canvas = BoardCanvas(root, grid_size=7)
    canvas.clear_markers()  # must not raise
    assert canvas._marker_ids == []


class _FakeClickEvent:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y


def test_cell_from_pixel_translates_correctly(root):
    canvas = BoardCanvas(root, grid_size=7)
    assert canvas.cell_from_pixel(0, 0) == (0, 0)
    assert canvas.cell_from_pixel(35, 35) == (1, 1)  # CELL_SIZE=32, so 35//32 == 1


def test_cell_from_pixel_returns_none_outside_the_grid(root):
    canvas = BoardCanvas(root, grid_size=7)
    assert canvas.cell_from_pixel(9999, 9999) is None


def test_click_handler_fires_with_the_correct_cell(root):
    canvas = BoardCanvas(root, grid_size=7)
    clicks = []
    canvas.set_click_handler(lambda r, c: clicks.append((r, c)))
    canvas._on_click(_FakeClickEvent(35, 35))
    assert clicks == [(1, 1)]


def test_click_handler_does_not_fire_when_disabled(root):
    canvas = BoardCanvas(root, grid_size=7)
    clicks = []
    canvas.set_click_handler(lambda r, c: clicks.append((r, c)))
    canvas.set_click_handler(None)
    canvas._on_click(_FakeClickEvent(0, 0))
    assert clicks == []


def test_click_handler_ignores_a_click_outside_the_grid(root):
    canvas = BoardCanvas(root, grid_size=7)
    clicks = []
    canvas.set_click_handler(lambda r, c: clicks.append((r, c)))
    canvas._on_click(_FakeClickEvent(9999, 9999))
    assert clicks == []


def test_highlight_legal_cells_outlines_exactly_the_given_cells(root):
    canvas = BoardCanvas(root, grid_size=7)
    canvas.highlight_legal_cells({(1, 1), (2, 2)})
    assert canvas.itemcget(canvas._rects[(1, 1)], "outline") == "#2e7d32"
    assert canvas.itemcget(canvas._rects[(2, 2)], "outline") == "#2e7d32"
    assert canvas.itemcget(canvas._rects[(0, 0)], "outline") == "#cccccc"


def test_highlight_legal_cells_clears_previous_highlights_not_in_the_new_set(root):
    canvas = BoardCanvas(root, grid_size=7)
    canvas.highlight_legal_cells({(1, 1)})
    canvas.highlight_legal_cells({(2, 2)})
    assert canvas.itemcget(canvas._rects[(1, 1)], "outline") == "#cccccc"
    assert canvas.itemcget(canvas._rects[(2, 2)], "outline") == "#2e7d32"


def test_highlight_legal_cells_with_an_empty_set_clears_everything(root):
    canvas = BoardCanvas(root, grid_size=7)
    canvas.highlight_legal_cells({(1, 1), (2, 2)})
    canvas.highlight_legal_cells(set())
    assert canvas.itemcget(canvas._rects[(1, 1)], "outline") == "#cccccc"
    assert canvas.itemcget(canvas._rects[(2, 2)], "outline") == "#cccccc"
