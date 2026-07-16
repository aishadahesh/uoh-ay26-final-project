# PRD: Strategy Module — Belief Map, Heuristic Brain, Verbal Hints

**Mechanism owner:** `src/police_thief/domain/belief.py`, `domain/strategy/` (`brain_base.py`, `manhattan_brain.py`), `domain/heuristics.py`, `domain/hints.py`; config wiring in `shared/config.py`
**Parent document:** `docs/PRD.md` (see §7, "Per-Mechanism PRD Documents")
**Corresponds to:** `docs/tasks.md` Chapter 6 ("Strategy Module & Decision-Making") — §6.1-6.4. Belief-map construction, hint generation, and bluff detection were explicitly deferred here from Chapter 4 (see `docs/PRD_pheromone_scent.md` §3). Real LLM provider integration (ollama/claude_api/claude_cli), prompt-based deception strategy, and network wiring of the strategy module into a live turn loop are **not** built here — see "Constraints & Limitations."

---

## 1. Description & Theoretical Background

Chapter 6 is the boundary between "a generic communication component" and "a thinking agent" (Sec. 6.1.1): a separate strategy module, connected at a precise point (after hint decoding, before Commit packaging), makes the movement decision using only local information. The rulebook presents three algorithmically-equal tracks (Manhattan heuristic, custom algorithm, optional RL) — per `docs/PLAN.md` ADR-010, this project's chosen baseline is the Manhattan-distance heuristic blended with a Bayesian belief map, with RL explicitly out of scope (Sec. 6.2.1: "the course does not require RL at all").

The belief map (`b(s)`) is where Chapter 1's `{Ωi}, O` observation components and Chapter 4's scent mechanism finally connect to a decision: a probability distribution over the board, updated from the one always-truthful channel (scent), with a peak (`arg max_s b(s)`) that is only ever a best guess, never certainty (Sec. 6.3.5). Sec. 6.4.1's single unbreakable architectural constraint — never hand the move decision to an LLM — is enforced structurally in `BrainBase`, not just by convention.

## 2. Specific Requirements, Input/Output, Performance Metrics

| Requirement | Implementation | Expected input → output |
|---|---|---|
| `BeliefMap` probability distribution over open cells | `belief.py::BeliefMap` | uniform prior `1/N` per open cell; sums to `1.0` |
| Bayesian-style update from scent | `update_from_scent(scent_field)` | posterior ∝ prior × (scent intensity + ε), renormalized |
| Blocked cells always zero belief | open cells computed by excluding `board.is_blocked` | a blocked cell never appears in the tracked distribution at all |
| `arg max_s b(s)` peak extraction | `arg_max()` | returns the highest-probability `Position` |
| `BrainBase` interface | `_decide_move` (abstract, both roles), `_pick_move` (optional, cop-only) | structurally cannot accept an LLM handle or hint text |
| Mandatory Manhattan-distance formula | `heuristics.py::manhattan_distance`/`greedy_manhattan_move` | reproduces Sec. 6.3.3's own worked example exactly: `D((2,2),(5,5)) = 6`, best move reduces `D` to `5` |
| Config-driven brain selection | `shared/config.py::load_strategy_class` | `[strategy] cop_class`/`thief_class` dotted path, default `ManhattanHeuristicBrain` |
| Word-limited, Intent-tagged verbal hints | `hints.py::Hint`, `TemplateHintProvider`, `enforce_word_limit` (15 words) | deterministic, zero-token phrase generation |
| Bluff detection reproducing Sec. 4.3.4's worked example | `detect_bluff` | a lie about direction, contradicted by the real scent trail → `True`; a truthful hint in the same scenario → `False` |
| Performance | All operations are simple dict/loop operations over a ≤49-cell board; negligible cost | full 193-test suite runs in ~7.7s |

## 3. Constraints, Limitations, Alternatives Considered & Rationale

- **Scope boundary — decision architecture vs. live network wiring:** `BrainBase`/`ManhattanHeuristicBrain` are fully built and proven via a genuine partial-observability integration test, but nothing wires a brain into the actual FastMCP turn loop yet (`PeerRuntime` calling the strategy module "exactly once per turn" — Chapter 8's Orchestrator). This chapter proves the *decision logic* is correct in isolation and via a real (if single-process) two-brain match.
- **A real design correction caught while writing tests, not the implementation:** an early version of the "custom class loading" test pointed the config at `ManhattanHeuristicBrain` itself to represent "a custom class" — which would have passed even if config loading were silently ignored and the code just fell back to its own default. Caught before trusting it; fixed by introducing a genuinely distinct `DummyCustomBrain` in the test module so the assertion actually exercises the `importlib`-based loading path.
- **Design choice — DRY refactor of the Manhattan search:** rather than let the Chapter 3/4 placeholder policies (`move_toward_policy`/`move_away_policy`) and the new `ManhattanHeuristicBrain` duplicate the same "try every orthogonal move, keep whichever improves distance" loop, both now call one shared `domain/heuristics.py::greedy_manhattan_move`. The placeholder policies still "cheat" (take the opponent's raw position) — that distinction is preserved and documented, only the search *mechanics* are shared.
- **Documented empirical finding — bluff detection is recency-sensitive:** an initial multi-turn test scenario for `detect_bluff` produced a counter-intuitive result (a claimed-but-false direction showing *higher* scent than the true direction) because several turns of accumulated history overlapped near the path's starting region. Verified empirically before trusting any assertion; the function is correct and matches the rulebook's own worked-example number exactly when assessed for a single, isolated turn (its intended use), but a longer curving path can dilute the signal — documented directly in the function's docstring as a scope limitation, not hidden.
- **Limitation — no belief/hint trust-weighting system:** Sec. 6.3.1/T0289 call for weighting a verbal hint's influence on the belief map by an accumulated trust score per opponent. Not built: `detect_bluff` exists as a standalone classifier, but nothing yet feeds a caught lie back into a persistent, decaying trust weight, nor blends hints into `BeliefMap.update_from_scent` itself. This is a deeper, stateful feature better suited once a live multi-turn match loop (Chapter 8) exists to actually accumulate trust over real games.
- **Limitation — only the `template` hint provider is implemented:** `ollama`/`claude_api`/`claude_cli` (Sec. 6.4.6, Table 21) are not built. They require live external services (a local Ollama server, real API keys, network calls) that this project's automated test suite should not depend on — and per Sec. 6.4.7, a team may legitimately play an entire league series using only the zero-token `template` mode. The `[trash_talk] provider` config key exists (commented, defaulting to `template`) but has no loader/dispatch code yet.
- **Limitation — hint parsing is template-exact, not general NLP:** `parse_claimed_direction` recognizes only this project's own fixed phrase set, not arbitrary free text an opponent might send. Building a robust parser for genuinely varied phrasing is a much larger natural-language task; since only the `template` provider is implemented on our own side, there is no real free-text input from an opponent to parse yet either.
- **Limitation — no lying-frequency strategy:** `TemplateHintProvider.generate` takes `tell_truth` as a caller-supplied parameter rather than deciding autonomously when to lie (Sec. 6.4/T0321-322). The *mechanism* for producing either a true or false hint exists; the *policy* for choosing between them is not built.
- **Alternative considered — building the belief map to also ingest hints directly:** rejected for now in favor of keeping `BeliefMap` scent-only and `detect_bluff` a separate, composable function — simpler to reason about and test independently; a future trust-weighted fusion (if built) can compose these rather than requiring `BeliefMap` itself to understand verbal claims.

## 4. Success Criteria & Test Scenarios

All satisfied, per `tests/unit/test_belief.py`, `test_heuristics.py`, `test_strategy.py`, `test_hints.py`, and `tests/integration/test_strategy_pipeline.py` (48 new tests directly on this mechanism; 193 tests total project-wide, 99.65% coverage, zero lint violations):

1. `BeliefMap` starts uniform, stays normalized after every update, always excludes blocked cells, and correctly peaks at a scent-emission center; a fully-blocked degenerate board is handled without crashing.
2. `manhattan_distance`/`greedy_manhattan_move` reproduce the rulebook's own worked example exactly (`D=6` at `(2,2)`→`(5,5)`, best move reduces it to `5`); chase/flee both behave correctly; ties are resolved deterministically.
3. `BrainBase` cannot be instantiated directly; its default `_pick_move` is `None`; `ManhattanHeuristicBrain` correctly chases (cop) or flees (thief) the belief peak and respects the barrier budget.
4. `load_strategy_class` defaults to the built-in heuristic, loads a genuinely distinct custom class by dotted path, never reads the other role's config key, and rejects both a malformed path and a class that isn't a `BrainBase` subclass.
5. Hints respect the word limit, carry a mandatory Intent flag, never contain a raw coordinate pattern (verified directly), and `detect_bluff` correctly catches a lie and clears a truthful claim in the rulebook's own worked-example scenario.
6. **The headline integration proof**: two `ManhattanHeuristicBrain` instances, one per role, play a full match using *only* their own belief maps (themselves fed only by their own reading of the opponent's scent trail) — the opponent's true `Position` is never passed to either brain's `_decide_move` anywhere in the test. The cop's belief converges tightly on the thief's real final location, and a real capture occurs within the mandatory move budget — proving partial observability is preserved architecturally, not just by convention.
