# PRD: Live GUI & Replay Viewer

**Mechanism owner:** `src/police_thief/domain/live_view_model.py`, `domain/replay.py`, `gui/live_gui.py`, `gui/replay_gui.py`; CLI wiring in `main.py`
**Parent document:** `docs/PRD.md` (see §7, "Per-Mechanism PRD Documents")
**Corresponds to:** `docs/tasks.md` Chapter 7 ("User Interface (GUI) & Replay Simulator") — §7.1-7.5. Turn-banner wiring to a live state machine, a scrolling event log, a scoreboard, and networked/threaded live-match GUI operation are **not** built here — see "Constraints & Limitations."

---

## 1. Description & Theoretical Background

Chapter 7 answers two distinct questions: "what is happening right now?" (the Live GUI) and "did it really happen as claimed?" (the Replay Viewer). The Live GUI's **Local Truth** principle is a direct corollary of Chapter 1's Dec-POMDP formalism: each agent's partial observation `Ωi` is a strict subset of the true state `S`, so an interface revealing the full `S` would violate the game's own rules — there is no "bird's-eye view" at any point (Sec. 7.2). The Replay Viewer's job is not its graphical polish but its **cryptographic verification**: re-hashing every logged step and comparing against the originally-committed value (Sec. 7.4.2), directly reusing the collision-resistance guarantee established in Chapter 5.

## 2. Specific Requirements, Input/Output, Performance Metrics

| Requirement | Implementation | Expected input → output |
|---|---|---|
| Local-truth-only Live GUI | `live_view_model.py::build_live_view_model`, `gui/live_gui.py::LiveGUI` | takes only `own_position` + `BeliefMap` + `Board`; no parameter through which the opponent's true position could pass |
| Heatmap gradient | `belief_to_color(intensity, max_intensity)` | white (`#ffffff`) at zero belief → deep red (`#c80000`) at peak, normalized to the map's own current maximum |
| Barrier cells rendered distinctly | `CellView.is_blocked` → fixed `#2b2b2b`, never a belief color | true even if the scent field has residual intensity there (scent physically emits regardless of board rules) |
| Turn-state banner | `TurnState.YOUR_TURN`/`LOCKED` → text + color | green `#2e7d32` "YOUR TURN" / gray `#616161` "LOCKED" |
| Replay Viewer cryptographic core | `domain/replay.py::ReplaySession`, reusing Chapter 5's `verify()`/`audit_log()` | a tampered log entry at index *i* → every step from *i* onward renders `TAMPERED` |
| Step-by-step scrubbing | `ReplaySession.next`/`previous`/`jump_to` | out-of-range `jump_to` raises `IndexError` and leaves the current step unchanged |
| Verified/tampered summary | `ReplaySession.verified_count`/`tampered_count` | `2 verified / 3 tampered (of 5 total steps)` on a log tampered at index 2 |
| Standalone launch | `python -m police_thief replay --log-file PATH` | constructs and renders correctly independent of any live match code |
| Performance | All GUI/replay logic is O(board size) or O(log length); negligible cost | full 235-test suite runs in ~8s |

## 3. Constraints, Limitations, Alternatives Considered & Rationale

- **Scope boundary — presentation vs. live wiring:** both GUI layers are fully built and thoroughly tested (100% coverage), including two integration tests that drive *real* Chapter 5/6 data (a live multi-turn strategy pipeline for the Live GUI; a real `commit()`-sealed multi-turn log, tampered on disk, for the Replay Viewer). What is **not** built is wiring either GUI into an actual live, networked match loop: the turn banner does not yet reflect a real Commit/Acknowledge/Reveal state machine (Chapter 8 doesn't exist yet), there is no scrolling event log or scoreboard (both need a Log Manager, Chapter 8), and there is no threading model separating GUI updates from network I/O (no network I/O loop is wired to the GUI yet).
- **A real Tkinter limitation found and worked around, not papered over:** an early version of the GUI test suite created a fresh `tk.Tk()` per test function. After a handful of create/destroy cycles, this failed with `_tkinter.TclError: invalid command name "tcl_findLibrary"` — a known limitation where Tkinter does not reliably support creating and destroying many root interpreters within one process. Fixed with a session-scoped root fixture and per-test `Toplevel` windows for isolation, verified by re-running the full suite afterward.
- **Design choice — reuse Chapter 5's crypto exactly, add nothing new:** `ReplaySession` calls `audit_log()`/`verify()` directly rather than re-implementing "recompute SHA-256, compare to stored commit" a second time. The only genuinely new logic this chapter adds is the per-step "voided from the first tamper onward" display rule (Sec. 7.5.1) and scrubbing state.
- **Design choice — thin GUI classes, view-model logic elsewhere:** every color/text decision is made in framework-agnostic modules (`live_view_model.py`, `replay.py`) before it ever reaches a Tkinter widget. This is what made real (not mocked) 100% GUI coverage achievable: widget state can be asserted directly via `.cget()`/`.itemcget()`, and buttons can be exercised via `.invoke()`, without ever needing a human to click anything.
- **Limitation — no screenshots produced this session:** `docs/tasks.md` explicitly lists a belief-heatmap GUI screenshot and a Replay Viewer "Verified OK" screenshot as mandatory submission deliverables (Sec. 7.5.3). No tool available in this working session captures native desktop window screenshots (only web-preview screenshots are supported). Correctness was instead verified exhaustively via automated widget-state assertions (e.g., `status_label.cget("text") == "Verified OK"`), which is a stronger correctness guarantee than a screenshot alone would be — but it does not substitute for the literal deliverable. **This remains a manual step**: run `python -m police_thief replay --log-file <path>` (or launch `LiveGUI` directly) and capture the window before final submission.
- **Limitation — no manual input controls in the Live GUI:** by design, since agents act autonomously via `BrainBase` (Chapter 6); there is nothing for a human to "act out of turn" with, so T0413's disabling requirement doesn't apply to this project's actual architecture.
- **Limitation — no visual board replay in the Replay Viewer:** `LogEntry.state` is intentionally generic (`Any`) at the crypto layer (Chapter 5), so rendering it as a board would require assuming a specific state shape that the crypto primitives deliberately don't mandate. The *textual* detail view (move/intent/hash) is sufficient for the tool's actual purpose — cryptographic verification, not visualization (Sec. 7.4.2 says so explicitly).
- **Alternative considered — PyQt/PySide instead of Tkinter:** rejected; Tkinter is stdlib (zero new dependencies) and, once verified to work headlessly in this environment, fully sufficient for the required heatmap/banner/scrubber widgets.

## 4. Success Criteria & Test Scenarios

All satisfied, per `tests/unit/test_live_view_model.py`, `test_replay.py`, `test_gui.py`, and `tests/integration/test_gui_pipeline.py` (58 new tests directly on this mechanism; 235 tests total project-wide, 99.73% coverage, zero lint violations):

1. `belief_to_color` produces the correct white-to-red gradient, including a zero-max-intensity edge case; `build_live_view_model` marks exactly the own position, colors the belief peak reddest, and renders barrier cells in a fixed distinct color regardless of any residual scent there.
2. `LiveViewModel` and `build_live_view_model` are structurally proven (via `dataclasses.fields`/`inspect.signature`) to have no field or parameter capable of holding the opponent's true position.
3. `ReplaySession` correctly verifies a clean log, detects tampering at the exact index, propagates `TAMPERED` status to every subsequent step, supports full scrubbing (including boundary and out-of-range behavior), and reports accurate verified/tampered summary counts.
4. Both `LiveGUI` and `ReplayGUI` construct real Tkinter widgets, render the correct colors/text/banners, and respond correctly to real button `.invoke()` calls — no part of the GUI layer is mocked away.
5. **The two headline integration proofs**: `test_live_gui_stays_in_sync_across_a_real_multi_turn_match` drives the actual Chapter 6 strategy pipeline for 5 real turns and confirms the GUI's banner and own-position marker match the real turn state and real position at every single turn; `test_replay_viewer_against_a_real_commit_reveal_sealed_multi_turn_log` builds a real multi-turn commit-sealed log, saves it to an actual file, reloads it, tampers the file on disk exactly as a dishonest player might, and confirms both the crypto layer and the GUI layer agree on the correct verified/tampered verdict throughout.
