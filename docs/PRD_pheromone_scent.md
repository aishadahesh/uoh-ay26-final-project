# PRD: Pheromone Emission & Decay (Scent Model)

**Mechanism owner:** `src/police_thief/domain/scent.py`; wired into `simulation.py`; config in `config/game.json` (`pheromones` section) + `shared/game_config.py`
**Parent document:** `docs/PRD.md` (see §7, "Per-Mechanism PRD Documents")
**Corresponds to:** `docs/tasks.md` Chapter 4 ("Dynamic Pheromone Trails & Collective Memory of the Trail") — specifically §4.1-4.2 (emission/decay mechanics). Belief-map construction, natural-language hints, LLM integration, and deception (`docs/tasks.md` §4.3 narrative + the formal belief-map machinery) are **Chapter 6's** territory and out of scope here — see the "Constraints & Limitations" section below.

---

## 1. Description & Theoretical Background

Stigmergy: indirect coordination through changing a shared environment, the same mechanism ant colonies use with no central dispatcher, no language, and no shared memory (docs/tasks.md Sec. 4.1.1). This is the project's primary partial-observability channel from Chapter 1's Dec-POMDP model — `{Ωi}, O` are realized concretely here: neither agent ever observes the opponent directly, but each can read the *environment*, which the opponent's own movement has physically altered.

Scent is explicitly **natural and non-fakeable**: it emanates from mere presence, cannot be suppressed, and (unlike a verbal hint, Chapter 6) cannot lie. This asymmetry — one always-truthful channel (scent), one potentially-deceptive channel (hints) — is the entire premise behind the lie-detection worked example in Sec. 4.3.4, which this mechanism deliberately does not yet implement (see below).

## 2. Specific Requirements, Input/Output, Performance Metrics

| Requirement | Implementation | Expected input → output |
|---|---|---|
| 5×5 emission footprint centered on the agent | `ScentField.emit(position)`, radius = `field_size // 2` | `emit(Position(3,3))` touches cells within Manhattan distance 2 |
| Center intensity 0.9 | `ScentConfig.center_intensity` | `intensity_at(Position(3,3))` immediately after emission → `0.9` |
| Radial falloff to 0 at the field edge | `_emission_delta`: linear interpolation by Manhattan distance | distance 0/1/2 → `0.9/0.6/0.3`; distance 3+ → `0.0` |
| Mandatory decay equation `tau(t+1) = max(0, (1-rho)*tau(t) + delta_tau)` | `decay()` then `emit()` called once per turn, in that order | `emit` → `0.9`; `decay` with no re-emission → `0.81` (matches the rulebook's own Sec. 4.3.4 worked-example number exactly) |
| Decay rate ρ = 0.10 | `ScentConfig.decay_rate`, loaded from `config/game.json` | verified via the exact geometric curve `0.9 * (1-ρ)^n` over 5 turns |
| Symmetric, independent per-agent fields | Two separate `ScentField` instances in `run_local_match` (`cop_scent`, `thief_scent`) | one field's emission never appears in the other's `intensity_at` |
| Fixed (not negotiable) parameters | `game_config.py::_validate_fixed_scent_config` | any deviation (e.g., `scent_decay_rate=0.20`) → `GameConfigError` |
| Performance | Sparse dict storage (board ≤ 7×7 = 49 cells); negligible cost — no profiling concerns at this scale | measured empirically: full 105-test suite runs in ~6.8s |

## 3. Constraints, Limitations, Alternatives Considered & Rationale

- **Constraint — parameters are FIXED, not minimums:** unlike `grid_size`/`max_barriers` (Chapter 3, which are floors that may be raised), the Mandatory Parameters Table marks `scent_center_intensity`, `scent_decay_rate`, and `scent_field_size` as **fixed**. `load_match_parameters` rejects *any* deviation from `0.9`/`0.10`/`5`, not just values below a floor.
- **Documented tension, resolved via the academic-freedom clause (docs/tasks.md Sec. 0.4):** the rulebook's own descriptive text calls `tau_ij(t)` "a continuous value in `[0, 0.9]`", but its own **mandatory** formula adds a fresh `Δτ = 0.9` every turn an agent is present, which provably exceeds `0.9` after just two consecutive turns in the same cell (`0.9 → 0.81 + 0.9 = 1.71`). This implementation follows the mandatory formula **literally** rather than silently capping the result to match the descriptive prose, since the formula is explicitly labeled MANDATORY while the `[0, 0.9]` range is only descriptive. This choice is tested directly (`test_sustained_presence_can_exceed_the_bare_center_intensity`) rather than hidden.
- **Limitation — no belief map yet:** this mechanism produces raw scent intensities only. Turning that into a probability distribution over the opponent's likely location (`b(s)`, Bayesian updates, `arg max_s b(s)`) is Chapter 6's `docs/tasks.md` Sec. 6.3 content — deliberately not built here, to avoid coupling this mechanism to a belief-update design that hasn't been decided yet (the same incremental-layering discipline applied in Chapters 1 and 3).
- **Limitation — no lie-detection yet:** the Sec. 4.3.4 "south-east trail vs. false north claim" worked example requires natural-language hints (Chapter 6) to exist before any contradiction can be detected. This chapter instead proves the *precondition*: `test_thief_scent_trail_concentrates_near_its_actual_path_not_elsewhere` shows the raw trail data already carries the asymmetry (hot near the real path, exactly zero elsewhere) that a future lie-detector would need.
- **Limitation — no debug visualization:** a printed/rendered scent-grid view (`docs/TODO.md` T0280) is deferred to the GUI work in Chapter 7, where a real rendering surface (heatmap) already needs to exist.
- **Alternative considered — dense 2D array (e.g., via `numpy`) instead of a sparse dict:** rejected. The board is at most a handful of tens of cells; a sparse `dict[Position, float]` is simpler, has zero new dependencies, and untouched cells are implicitly and correctly `0.0`.
- **Alternative considered — capping emission at `center_intensity`:** rejected in favor of literal formula compliance (see the documented tension above); capping would have been an undocumented silent deviation from a rule explicitly marked MANDATORY.
- **Alternative considered — Euclidean or Chebyshev distance for the radial falloff:** rejected in favor of Manhattan distance, for consistency with the rest of the project's orthogonal-only movement model (Chapter 3) and the upcoming Manhattan-distance heuristic (Chapter 6).

## 4. Success Criteria & Test Scenarios

All satisfied, per `tests/unit/test_scent.py`, `tests/unit/test_game_config.py` (fixed-value rejection), and `tests/integration/test_scent_trail.py` (14 new tests directly on this mechanism; 105 tests total project-wide, 99.41% coverage, zero lint violations):

1. Emission produces exactly `center_intensity` at distance 0, with a monotonically decreasing falloff to exactly `0.0` outside the field radius.
2. The decay-only curve over N turns matches the exact closed-form `center_intensity * (1-ρ)^n` — including reproducing the rulebook's own `0.81` worked-example number precisely.
3. Sustained presence (repeated emission) keeps a cell's intensity at or above a cell that was only ever visited once — and can mathematically exceed the bare center intensity, a consequence of the formula this implementation deliberately does not suppress.
4. Decay never produces a negative value; a decay rate of `1.0` (tested independently of the loader's fixed-value restriction) fully clears a cell in one step.
5. Two independent `ScentField` instances never share state — proven both in isolation and after a full simulated match.
6. `config/game.json`'s `pheromones` section is parsed and any deviation from the three fixed values is rejected with a clear error.
7. In a full simulated match, the thief's own scent trail is measurably hotter near its actual flight path than in an unvisited region — the precondition Chapter 6's lie-detection logic will eventually depend on.
