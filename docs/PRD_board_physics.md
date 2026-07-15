# PRD: Board Physics, Movement, Barriers, Capture & Scoring

**Mechanism owner:** `src/police_thief/domain/board.py`, `capture.py`, `scoring.py`, `simulation.py`; shared config `src/police_thief/shared/game_config.py` + `config/game.json`
**Parent document:** `docs/PRD.md` (see §7, "Per-Mechanism PRD Documents")
**Corresponds to:** `docs/tasks.md` Chapter 3 ("Physics Mechanics, Board & Scoring System")

---

## 1. Description & Theoretical Background

This mechanism makes concrete the six Dec-POMDP tuple components (Ch.1) that Chapter 1's `dec_pomdp.py` deliberately left as documented placeholders: the state space `S` (board + agent positions + barrier layout), the action spaces `{Ai}` (movement + barrier placement), the transition function `P` (`Board.apply_move`/`place_barrier`), and the reward function `R` (`ScoringTable`/`score_for`).

There is no central server enforcing these physics; both sides self-enforce identical rules by loading the same `config/game.json` (docs/tasks.md Sec. 3.1.2). The design goal is a state space large enough (7×7 default, chosen deliberately over the smaller 5×5 lecture example) to make brute-force search infeasible, forcing later chapters toward heuristics or learning rather than exhaustive search — while the physics themselves stay simple, deterministic, and fully self-contained.

## 2. Specific Requirements, Input/Output, Performance Metrics

| Requirement | Implementation | Expected input → output |
|---|---|---|
| 4-directional movement only, no diagonals | `Move` enum (N/S/E/W/STAY), `Board.apply_move` | `(Position(3,3), Move.NORTH) → Position(2,3)` |
| Reject illegal moves, never silently execute | `MoveRejectedError` raised on out-of-bounds/blocked/non-`Move` input | `(Position(0,0), Move.NORTH) → raises MoveRejectedError` |
| `STAY` always legal, including on a self-placed barrier | Special-cased in `apply_move` before bounds/blocked checks | `(Position(3,3), Move.STAY) → Position(3,3)` unconditionally |
| Barrier placement: adjacent-or-own cell only, budget-limited, irreversible | `Board.place_barrier` | `place_barrier(cop=(3,3), target=(2,3))` → blocked forever, budget −1 |
| Capture on cop/thief position match (by move or by barrier) | `check_capture(a, b) -> bool` (position equality, source-agnostic) | `check_capture((2,2), (2,2)) → True` |
| Capture on "boxed in" (no legal neighbor at all) | `is_boxed_in(board, pos) -> bool` | all 4 neighbors blocked/off-board → `True` |
| Scoring table with asymmetric rewards per outcome | `ScoringTable`, `score_for(outcome, scoring)` | `score_for(CAPTURE, ScoringTable()) → (20, 5)` |
| Shared, identical physics config for both sides | `config/game.json` + `load_match_parameters` | malformed/missing/below-floor → `GameConfigError` |
| Performance | Single match (≤35 turns) completes in well under 10ms; no profiling concerns at this board scale | measured empirically during test runs (~6s for the full 85-test suite, dominated by the unrelated real-HTTP integration tests from Chapter 2) |

## 3. Constraints, Limitations, Alternatives Considered & Rationale

- **Constraint — floors, never lowered:** `grid_size ≥ 7`, `max_barriers ≥ 14` are enforced by `load_match_parameters`, raising `GameConfigError` below either floor (docs/tasks.md App. F).
- **Limitation — no barrier-placing policy yet:** the Chapter 3 placeholder policies (`move_toward_policy`, `move_away_policy`) only move; they never call `place_barrier`. This means `is_boxed_in`'s mid-match branch and the barrier-onto-thief capture path are exercised by dedicated unit tests (`test_capture.py`) but not by a full simulated match yet. This is a deliberate scope boundary, not an oversight — real barrier-placement *strategy* is Chapter 6's territory (docs/tasks.md Sec. 3.3.8).
- **Limitation — no adversarial illegal-move handling in the local harness:** `run_local_match` trusts its own policies (which self-filter via `apply_move`'s exceptions before ever returning an illegal move), so no illegal move currently reaches the harness's turn loop. Handling a genuinely adversarial illegal move from an untrusted opponent is already covered at the transport layer (Chapter 2's FastMCP input validation) and will be fully covered once the commit-reveal protocol (Chapter 5/6) treats any illegal claim as an auditable, disqualifying event.
- **Alternative considered — separate `BarrierBudget` class:** rejected in favor of a `remaining_barrier_budget` property directly on `Board`, since the budget is intrinsically board state (how many of *this* board's cells can still be blocked), not an independent concern needing its own object.
- **Alternative considered — printing/logging match results directly from `run_local_match`:** rejected; the function returns a structured `MatchResult` dataclass instead, and printing is left to the CLI's `simulate` subcommand (`main.py`). This keeps the domain layer free of I/O side effects, consistent with the SDK-layer architectural principle (docs/PLAN.md §1, principle 3).
- **Alternative considered — JSON schema-level default values for missing `config/game.json` fields:** rejected. Unlike the private per-peer TOML (Chapter 2, which reasonably defaults `turn_timeout_seconds`), the shared config is the one place both sides' physics must be *fully explicit and identical* — silently defaulting a missing shared field could let two sides disagree about "what the rules were" without either side noticing. A missing required field is therefore always a hard `GameConfigError`, never a silent default.

## 4. Success Criteria & Test Scenarios

All satisfied, per `tests/unit/test_board.py`, `test_capture.py`, `test_scoring.py`, `test_game_config.py`, and `tests/integration/test_simulation.py` (85 tests total, 99.26% coverage, zero lint violations):

1. Movement is orthogonal-only, one cell per turn, `STAY` always legal (including atop a self-placed barrier).
2. Illegal moves (out-of-bounds, into a blocked cell, non-`Move` input) are rejected via `MoveRejectedError`, never silently executed.
3. Barriers: adjacent-or-own-cell only, decrement a finite budget, are permanent, and (by direct test) landing exactly on the thief's cell is captured via the same generic `check_capture` used for ordinary moves.
4. A thief with zero legal orthogonal neighbors is detected as boxed-in/captured.
5. Scoring matches the Mandatory Parameters Table exactly for capture/survival/technical-loss/tie, and is overridable upward via config without touching game logic.
6. The shared `config/game.json` loader rejects a missing file, a missing required key, and any value below the mandatory floor.
7. A full local match (shipped config, placeholder policies) runs to completion with no crash, terminating deterministically via either capture, survival-threshold, or the `max_moves` hard cap — including the case where `survival_threshold > max_moves` (a misconfiguration the loader doesn't itself forbid, but the simulation loop still resolves safely).
