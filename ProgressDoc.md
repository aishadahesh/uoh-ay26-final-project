# Distributed Cops-and-Robbers over a Peer-to-Peer Network

Final project for **Orchestration of AI Agents** (University of Haifa, Dept. of Computer Science). Two autonomous AI agents — a Cop and a Thief — play a pursuit-and-evasion game on a discrete grid, communicating only peer-to-peer (no central server), under partial observability, with a fully self-enforced cryptographic protocol (no external referee).

## Project documents

| Document | Purpose |
|---|---|
| [`docs/tasks.md`](docs/tasks.md) | Full requirement extraction from the two source PDFs in `ref/` — the single source of truth for every rule, formula, and parameter |
| [`docs/PRD.md`](docs/PRD.md) | Product Requirements Document — goals, scope, assumptions, limitations, timeline |
| [`docs/PLAN.md`](docs/PLAN.md) | Technical architecture plan — C4 diagrams, sequence/state diagrams, package structure, Architecture Decision Records |
| [`docs/TODO.md`](docs/TODO.md) | Granular, checkable task list (~900 items) tracking implementation progress chapter by chapter |

Development proceeds **chapter by chapter following `docs/tasks.md`**, each chapter's work checked off in `docs/TODO.md` and summarized below before moving to the next.

---

## Quickstart

```bash
uv sync                 # install dependencies into .venv
uv run pytest --cov     # run the test suite with coverage
uv run ruff check .     # lint (must report zero violations)
```

**Architecture note (see `docs/PLAN.md` ADR-011):** the cop and thief agents are developed as **one shared package** (`police_thief`), differentiated at runtime via a `--role cop`/`--role thief` flag and separate `config/cop/`/`config/thief/` directories, rather than as two duplicated repos from the first commit. This satisfies the rulebook's "no shared runtime state between the two sides" requirement (two OS processes running this package never share memory), while avoiding premature duplication of shared/generic code. The rulebook's mandatory **two separate GitHub repos** deliverable is produced later, at submission time, by exporting this codebase into two tagged repos (tracked in `docs/TODO.md` Section O).

```bash
# Try it: start one peer, call it from the other side's client
uv run python -m police_thief --role cop &      # binds 0.0.0.0:8801
uv run python -c "from police_thief.services.mcp_client import send_move; \
print(send_move('http://127.0.0.1:8801/mcp', signed_move='N', signature='abc123'))"
```

---

## Development Log

### Chapter 1 — Theoretical Framework & Problem Modeling (Dec-POMDP)

**What this chapter covers (`docs/tasks.md` §2):** the game is modeled as a Decentralized Partially Observable Markov Decision Process — the tuple `⟨n, S, {Ai}, P, R, {Ωi}, O, γ⟩` — with exactly `n = 2` agents, a combinatorial state space too large for brute-force search, and partial observability that must be treated as both an obstacle *and* a usable resource (Ch.1.3).

**What was implemented:**
- **Project scaffolding**: `pyproject.toml` (uv-managed, `requires-python = ">=3.11"`), Ruff configured per the professional-software guideline's exact rule set (`E, F, W, I, N, UP, B, C4, SIM`), pytest + coverage gated at `fail_under = 85`.
- `src/police_thief/shared/constants.py` — `AgentRole` enum (`COP`, `THIEF`) and `NUM_AGENTS = 2`, the typed vocabulary for "which side am I," replacing ad hoc string literals everywhere downstream.
- `src/police_thief/shared/version.py` — `VERSION = "1.00"`, per the submission guideline's versioning convention (starts at 1.00, rises on significant changes).
- `src/police_thief/domain/dec_pomdp.py` — `DecPOMDPSpec` (an immutable dataclass capturing `num_agents` and `discount_factor`, the two tuple components that are meaningful as standalone data at this stage) and `validate_discount_factor()` (enforces `0 ≤ γ < 1`). The module's docstring explicitly maps the other six tuple components (`S`, `{Ai}`, `P`, `R`, `{Ωi}`, `O`) to the later chapters that will concretize them (board/scoring → Chapter 3; scent/belief → Chapter 4), rather than stubbing them out prematurely.
- `config/setup.json`, `config/rate_limits.json` — versioned skeleton config files (per the generic project-structure requirement); not yet wired to real code — that happens when the Gatekeeper is built in Chapter 9.
- `.env-example` and an extended `.gitignore` (Python artifacts, `.venv/`, `credentials.json`, `token.json`, `*.pem`/`*.key`).
- `tests/unit/test_dec_pomdp.py`, `tests/unit/test_version.py` — 15 tests covering: `NUM_AGENTS` fixed at 2, `AgentRole` has exactly `{cop, thief}`, discount-factor validation accepts `[0, 1)` and rejects everything else, `DecPOMDPSpec` rejects `num_agents != 2`, rejects an invalid discount factor, and is immutable.

**Quality gate results:**
```
15 passed in 0.14s
TOTAL coverage: 100.00% (required: 85.0%)
ruff check: All checks passed!
```

**Why this chapter has no board/movement/scoring code yet:** Chapter 1 in the rulebook is explicitly a *modeling* chapter, not a *board-mechanics* chapter — those are Chapter 3's territory (see `docs/TODO.md` Section C.1 onward). Building board logic here would have meant either faking the remaining six Dec-POMDP components or coupling this module prematurely to a board design that hasn't been decided yet. What Chapter 1 needed to deliver — and does — is the small, tested, typed contract (`n = 2`, `γ ∈ [0, 1)`) that every later chapter's board, scent, and strategy code will build on top of.

**Tasks checked off:** `docs/TODO.md` T0001, T0002, T0006, T0024, T0027, T0028, T0044–T0049, T0066–T0070, plus 8 new tasks added for this chapter's actual scope of work (T0890–T0897). See the "Progress log" note at the end of `docs/TODO.md`.

**Status:** committed (5 commits: scaffolding, domain model, tests, docs/ADR-011, ProgressDoc.md).

---

### Chapter 2 — P2P Network Architecture & FastMCP

**What this chapter covers (`docs/tasks.md` §3):** full decentralization — no central game server; each peer keeps only its own local truth. Every agent is simultaneously an MCP **server** (exposes tools the opponent calls) and an MCP **client** (calls the opponent's tools), fully symmetric with no "strong"/"weak" side. Tunneling (ngrok/Localtonet) later exposes each local server to the public internet. A mandatory rule requires cop and thief to run as fully separate processes with no shared runtime state, each loading its own config directory.

**What was implemented:**
- Added `fastmcp>=3.4.4` as a real dependency (previously only referenced in docs) and inspected its actual 3.x API directly rather than trusting the rulebook's illustrative (older-style) example code verbatim — confirmed the real transport URL pattern (`http://host:port/mcp`), the in-memory `Client(mcp_instance)` transport (fast tests, no sockets), and that FastMCP already derives a pydantic schema from the tool's function signature, rejecting missing/extra fields with a clean `ToolError` before our own code ever runs.
- `src/police_thief/services/mcp_server.py` — `MoveEnvelope` (placeholder wire format: `signed_move`, `signature` — real board moves arrive in Ch.3, real cryptographic signatures in Ch.5/6) with `is_structurally_valid()` (defensive blank-field check, explicitly *not* cryptographic verification); `build_peer_server(peer_name)` constructing a `FastMCP` instance exposing the `receive_move` tool (schema-versioned via `@mcp.tool(version=...)`); `run_peer_server(mcp, host, port)` binding to `0.0.0.0` (required for later tunnel exposure).
- `src/police_thief/services/mcp_client.py` — `send_move`/`send_move_async` calling the opponent's `receive_move` tool, wrapping any failure in `PeerClientError`. Deliberately does **not** implement retry logic — that's Chapter 8's Deadline Tracker concern, kept out of this transport-only wrapper.
- `src/police_thief/shared/config.py` — `load_network_config(role, config_root)` reading only `config/<role>/game.toml`'s `[network]` section (`my_port`, `opponent_url`, `turn_timeout_seconds`); raises `ConfigError` on a missing file or missing required key. Never reads the other role's directory.
- `config/cop/game.toml`, `config/thief/game.toml` — the concrete realization of the mandatory environment-separation rule. **Naming note:** renamed from the rulebook's illustrative `config/police/` to `config/cop/` to stay internally consistent with the `AgentRole` enum (`COP = "cop"`) introduced in Chapter 1 — directory *naming* isn't itself a mandatory rule (only the *separation* is; see `docs/tasks.md` §15 rule 1), so this is a safe, deliberate deviation, not a rule violation.
- `src/police_thief/main.py` + `src/police_thief/__main__.py` — CLI entry point: `uv run python -m police_thief --role cop|thief` loads only that role's config and starts its FastMCP server. This is where "separate processes, no shared memory" stops being a design intention and becomes an observable fact: two independent OS processes, each with its own interpreter and heap.
- Tests: `tests/unit/test_mcp_server.py` (in-memory transport — `MoveEnvelope` validation, valid/invalid payloads, FastMCP's own missing/extra-field rejection), `tests/unit/test_config.py` (TOML loading, missing file/key errors, cross-role isolation), `tests/unit/test_mcp_client.py` (unreachable-opponent error path), `tests/integration/test_mcp_http_roundtrip.py` (a **real** HTTP server bound to an actual OS port in a background thread, called over genuine HTTP — not mocked).
- Added `pytest-asyncio` (`asyncio_mode = "auto"` in `pyproject.toml`) since FastMCP's client API is async-native.
- **Manual end-to-end smoke test** beyond the automated suite: ran `python -m police_thief --role cop` as a real subprocess, then called it from a separate Python process via `send_move` over real HTTP — confirmed `{"accepted": True, "move": "N"}`, proving the full CLI → config → server → client path works, not just the unit-tested building blocks.

**Quality gate results:**
```
35 passed in 6.80s
TOTAL coverage: 100.00% (required: 85.0%)
ruff check: All checks passed!
```

**Why this chapter has no turn-alternation game loop or board-aware payloads yet:** Chapter 2 in the rulebook is about the *transport* (P2P architecture, FastMCP, environment separation) — not about *what* is transported. A real turn loop needs board state (Chapter 3) and a real trust mechanism needs the commit-reveal protocol (Chapter 5/6); building either here would mean inventing throwaway stand-ins for designs not yet made. What Chapter 2 needed to prove — and did, with a real (not mocked) HTTP round trip — is that two independent, config-isolated processes can reach each other symmetrically over MCP.

**Deviation from `docs/TODO.md`'s own stage order, and why:** `docs/TODO.md` follows the rulebook's *recommended build priority* (Ch.10: board logic before networking), whereas this session follows `docs/tasks.md`'s *chapter order* (1, 2, 3, ...) per instruction. Section D (Stage 2 / Chapter 2 content) is therefore checked off before Section C (Stage 1 / Chapter 3 content) — the opposite of `docs/TODO.md`'s own recommended sequence. This is a deliberate, explicit choice for accuracy/traceability against `docs/tasks.md`, not an oversight; it is flagged in `docs/TODO.md`'s progress log so the discrepancy is never silently ambiguous.

**Tasks checked off:** `docs/TODO.md` T0005, T0169–T0186, T0188–T0191 (23 tasks). T0187 (client retry logic) explicitly deferred to Chapter 8.

**Status:** committed (5 commits: dependencies, config, source, tests, docs).

---

### Chapter 3 — Physics Mechanics, Board & Scoring System

**What this chapter covers (`docs/tasks.md` §4):** the six Dec-POMDP tuple components Chapter 1 deliberately left as documented placeholders (`S`, `{Ai}`, `P`, `R`) become concrete here: a discrete 7×7 grid, four-directional movement with `STAY`, cop-only barrier placement (adjacent-or-own cell, budget-limited, irreversible), two capture conditions (position match, or the thief fully boxed in), and an asymmetric scoring table encoding the reward function `R`. All physics are self-enforced from one identical, shared `config/game.json` — there is no external judge.

**What was implemented:**
- `domain/board.py` — `Position` (immutable, hashable), `Move` (StrEnum: N/S/E/W/STAY), `MoveRejectedError`, `BoardConfig`, `Board` (`is_within_bounds`, `is_blocked`, `neighbors` — bounds-only, barrier-agnostic by design — `apply_move`, `place_barrier`). **Caught and fixed a real edge case while writing this**: a cop is allowed to barrier its own occupied cell (Sec. 3.3.4), which would have made a later `STAY` on that same cell wrongly raise `MoveRejectedError` under a naive "check bounds+blocked for every move" implementation — `apply_move` now special-cases `STAY` to bypass those checks entirely, since staying doesn't "enter" a new cell.
- `domain/capture.py` — `check_capture` (deliberately generic position-equality, so it covers *both* "cop moved onto thief" and "cop's barrier landed on thief" with one function), `is_boxed_in` (all orthogonal neighbors blocked/off-board), `CaptureClaim` (placeholder event shape — Chapter 5/6 adds the real cryptographic signature).
- `domain/scoring.py` — `MatchOutcome` (CAPTURE/SURVIVAL/TECHNICAL_LOSS/TIE), `ScoringTable` (defaults = Mandatory Parameters Table exactly: 20/5 capture, 5/10 survival, 2/2 tie, 0/0 technical loss), `score_for`.
- `config/game.json` + `shared/game_config.py` — the shared, identical-for-both-sides physics contract (`board_and_agents`, `movement_and_barriers`, `scoring` sections), with `load_match_parameters` enforcing the mandatory floors (`grid_size ≥ 7`, `max_barriers ≥ 14`) and a `schema_version` compatibility check. Unlike Chapter 2's private per-peer TOML (which reasonably defaults missing optional values), this loader treats every missing required field as a hard error — the whole point of a shared config is that nothing about physics is ever silently assumed.
- `domain/simulation.py` — a single-process local match harness (`run_local_match`) with explicitly-labeled placeholder policies (`move_toward_policy`, `move_away_policy` — greedy Manhattan-distance, **not** real strategy, which is Chapter 6's territory). Alternates turns, applies moves, checks both capture conditions, and terminates via capture, `survival_threshold`, or the `max_moves` hard cap — with the precedence between the latter two explicitly decided and tested (`max_moves` always wins as the safety net).
- `main.py` restructured from a single `--role` flag into `serve`/`simulate` subcommands: `serve --role cop|thief` (Chapter 2's server, unchanged behavior) and the new `simulate` (runs a local match against the shipped config and prints the result) — closing what would otherwise have been two under-delivered TODO items (verifying scoring output, having a CLI to exercise the simulation) with working code instead of a written excuse.
- `docs/PRD_board_physics.md` — the first of the per-mechanism PRD documents promised in `docs/PRD.md` §7, using the corrected `docs/PRD_<mechanism>.md` naming convention instead of the rulebook's own `PRD/01-base-logic.md` suggestion.
- Tests: `test_board.py`, `test_capture.py`, `test_scoring.py`, `test_game_config.py` (unit), `test_simulation.py` (integration) — 51 new tests (86 total).

**Quality gate results:**
```
86 passed in 6.78s
TOTAL coverage: 99.27% (required: 85.0%)
ruff check: All checks passed!
```
(The 2 uncovered lines in `simulation.py` are the mid-match `is_boxed_in`/post-move-capture checks — genuinely unreachable *this chapter*, since no current policy ever places a barrier. They stay in the code, commented as such, because they're correct and forward-looking for Chapter 6, not dead code by mistake.)

**What was deliberately left undone, and why (see `docs/PRD_board_physics.md` §3 for the full rationale):**
- **Barrier-placement strategy** (when/where to actually place barriers) is Chapter 6's territory. This chapter proves the barrier *mechanic* is correct in isolation (adjacency, budget, permanence, capture-on-placement) but no policy here ever calls `place_barrier` during a match.
- **Declared/logged barrier events** (T0124/T0125) wait for a real match log to exist — meaningless to build ahead of Chapter 5/9.
- **Adversarial illegal-move handling inside the simulation loop** (T0155) isn't reachable because the placeholder policies self-filter; genuinely adversarial input is already handled at the transport layer (Chapter 2) and will be fully covered by the commit-reveal protocol (Chapter 5/6).
- **Default-filling for missing shared-config fields** (T0166) was a deliberate *won't-do*, not an oversight: the shared config's entire purpose is that both sides' physics are fully explicit, so a missing field is always a hard error.

**Tasks checked off:** `docs/TODO.md` Sections C.0 (carried over from Ch.1) through C.7 — 73 new tasks this chapter (T0091–T0168 minus the 5 explicitly-deferred items above).

**Status:** committed (6 commits: shared config, board, capture/scoring, simulation+CLI, tests, docs).

---

### Chapter 4 — Dynamic Pheromone Trails & Collective Memory of the Trail

**What this chapter covers (`docs/tasks.md` §5):** Stigmergy — indirect coordination through changing the shared environment, the same mechanism ant colonies use with no central dispatcher. Every agent emits a 5×5 scent footprint around its own position every turn, decaying by a fixed rate each turn; this is the concrete realization of the Dec-POMDP's `{Ωi}, O` (observation) components that Chapter 1 left as documented placeholders. Scent is explicitly natural and non-fakeable — unlike a verbal hint (Chapter 6), it cannot lie. **Scope note:** `docs/tasks.md` Chapter 4 covers *only* the emission/decay mechanics (§4.1-4.2) plus qualitative narrative about lie-detection (§4.3); the actual belief-map formula, natural-language hints, and LLM integration are Chapter 6 content, even though `docs/TODO.md`'s own stage grouping ("Stage 4 — Language + Scent") bundles them together. This session followed `docs/tasks.md`'s chapter boundary, not the TODO's stage grouping.

**What was implemented:**
- `domain/scent.py` — `ScentConfig` (center_intensity=0.9, decay_rate=0.10, field_size=5 — all **fixed** per the Mandatory Parameters Table, not minimums) and `ScentField` (`emit`, `decay`, `intensity_at`), implementing the mandatory equation `τ(t+1) = max(0, (1-ρ)·τ(t) + Δτ)` as two method calls per turn (`decay()` then `emit()`), with a linear Manhattan-distance radial falloff (0.9/0.6/0.3/0.0 at distances 0/1/2/3).
- `config/game.json` gained a `pheromones` section; `game_config.py` now parses it into a `ScentConfig` and — unlike Chapter 3's floor checks — validates all three values as **exactly** fixed (any deviation is a hard `GameConfigError`), since the Mandatory Parameters Table marks these as fixed, not negotiable minimums.
- `domain/simulation.py` now constructs two independent `ScentField` instances (`cop_scent`, `thief_scent`) and decays+emits each one every turn; both are exposed on `MatchResult` for inspection. No policy reads them for decisions yet — that's still Chapter 6's belief-map territory.
- `docs/PRD_pheromone_scent.md` — the second per-mechanism PRD.
- Tests: `test_scent.py` (14 tests) + `test_scent_trail.py` integration tests (2 tests) + 4 new `test_game_config.py` tests for the fixed-value rejection — 19 new tests (105 total).

**Quality gate results:**
```
105 passed in 6.82s
TOTAL coverage: 99.41% (required: 85.0%)
ruff check: All checks passed!
```

**A genuine rulebook tension found and resolved, not papered over:** while verifying the formula against the rulebook's own worked example (Sec. 4.3.4's "~0.81" number — which I reproduced exactly: emit 0.9, decay once with no re-emission, get 0.81), I noticed the same section's descriptive text calls scent intensity "a continuous value in `[0, 0.9]`" — but the *mandatory* formula adds a fresh 0.9 every single turn an agent remains present, which mathematically exceeds 0.9 after just two consecutive turns in the same cell (0.9 → 0.81 + 0.9 = 1.71, confirmed empirically before writing the test). Rather than silently capping the value to match the prose (which would have been an undocumented deviation from a rule explicitly marked MANDATORY), I implemented the formula literally and used the project's own "academic freedom in case of contradiction" clause (`docs/tasks.md` Sec. 0.4) to document the choice explicitly — in the code's docstring, in a dedicated test (`test_sustained_presence_can_exceed_the_bare_center_intensity`), in `docs/PRD_pheromone_scent.md` §3, and in `docs/TODO.md`'s T0277 (left unchecked, since "never exceeds the ceiling" literally doesn't hold — checking it off would have misrepresented the code).

**What was deliberately left undone, and why:** belief-map construction, hint generation/parsing, LLM integration, and the lie-detection classifier are all Chapter 6 content (`docs/TODO.md` Sections F.2-F.6 remain unchecked). This chapter instead proves the *precondition* those future mechanisms will depend on: `test_thief_scent_trail_concentrates_near_its_actual_path_not_elsewhere` shows that after a real simulated match, the raw scent trail already carries the hot-path/cold-path asymmetry a lie-detector would need — without building the lie-detector itself ahead of its own chapter.

**Tasks checked off:** `docs/TODO.md` Section F.1 — 12 of 15 tasks (T0278 and T0280 deferred to Chapter 6/7 respectively; T0277 left explicitly unchecked as documented above, not simply skipped).

**Status:** committed (5 commits: scent model, config wiring, simulation integration, tests, docs).

---

### Chapter 5 — Cryptographic Security & Zero-Knowledge Protocol

**What this chapter covers (`docs/tasks.md` §6):** in a referee-less P2P match, "hindsight rewriting" (changing a move after the fact) is the central cheating risk. The fix is mathematical: a Commit-Reveal protocol over SHA-256 binds each side to `State+Move+Intent` before either side reveals anything, using a fresh cryptographic Nonce; a Step-0 declaration (hardware spec, code version, git commit hash) signed with HMAC-SHA256 makes any computational advantage visible and auditable. **Scope note:** the rulebook's four-step protocol (`Commit → Acknowledge → Reveal → Audit`) has both a *cryptographic* half (the primitives — this chapter) and a *network-enforcement* half (rejecting an out-of-order step, converting a failed audit into a live match loss — Chapter 8's Orchestrator/state machine). This session built only the primitives, deliberately not touching `mcp_server.py`/`mcp_client.py`.

**What was implemented:**
- `services/commit_reveal.py` — `canonical_json` (deterministic serialization), `generate_nonce` (via `secrets`, never `random`), `commit`/`verify` implementing `H_commit = SHA256(State‖Move‖Intent‖Nonce)` with constant-time comparison, and `LogEntry`/`AuditResult`/`audit_log` for mutual end-of-match tampering detection.
- `services/step0.py` — `HardwareSpec` + `gather_hardware_spec` (stdlib-only OS/CPU/RAM detection across Windows/Linux/macOS, graceful `0.0` fallback, GPU presence caller-supplied), `get_git_commit_hash` (verified against this real repo), `Step0Declaration` + HMAC-SHA256 `sign_step0`/`verify_step0_signature`, and a minimal `TokenUsage` counter.
- `shared/game_config.py::config_fingerprint` — SHA-256 over the canonically-serialized shared config, wired into `Step0Declaration.config_fingerprint`, closing Chapter 4's "scent parameters must be cryptographically locked" requirement (Sec. 4.2.6) as a side effect of a more general config-integrity mechanism rather than a bespoke per-parameter lock.
- **No bespoke `sign_capture_claim()`/`sign_barrier_declaration()` functions**: demonstrated that the generic `commit`/`verify` primitives already seal and tamper-detect both, the same DRY pattern `check_capture()` already established in Chapter 3.
- `docs/PRD_commit_reveal_crypto.md` — the third per-mechanism PRD.
- Tests: `test_commit_reveal.py` (20 tests), `test_step0.py` (18 tests), `test_config_fingerprint.py` (5 tests) — 40 new tests (145 total).

**Quality gate results:**
```
145 passed in 9.48s
TOTAL coverage: 99.57% (required: 85.0%)
ruff check: All checks passed!
```

**A real bug found and fixed, the same discipline as Chapter 3's `STAY`-on-barrier fix:** while wiring the Windows RAM-detection helper, I verified it standalone first (`ctypes` + `GlobalMemoryStatusEx`, confirmed `15.71 GB` correctly) — but the version I then wrote *inside* `step0.py` used a trimmed-down `ctypes.Structure` with only 4 of the 9 fields Windows' real `MEMORYSTATUSEX` struct actually has. Windows' `GlobalMemoryStatusEx` validates `dwLength` against its own fixed struct size and silently no-ops on a mismatch — no exception, just a wrong answer: `gather_hardware_spec()` reported `ram_gb=0.0` instead of the real value. Caught immediately by re-running the same "verify empirically before trusting a test assertion" check used every chapter so far, then fixed by using the complete, correctly-ordered 9-field struct — re-verified at `15.71 GB` afterward.

**What was deliberately left undone, and why (see `docs/PRD_commit_reveal_crypto.md` §3):** the entire four-step network protocol's live sequencing/enforcement, automatic technical-loss on a failed audit, Step-0 exchange between two live processes, and the Replay-Viewer-facing log format contract are all Chapter 8 (Orchestrator/state machine) or Chapter 7 (Replay Viewer) territory. This chapter proves the underlying cryptographic primitives are correct in isolation and via a realistic synthetic multi-turn sequence (`test_multi_turn_log_audit_catches_a_post_hoc_tampering_attempt`) — without inventing throwaway state-machine or logging infrastructure ahead of the chapters that actually own that design.

**Tasks checked off:** `docs/TODO.md` Sections H.1, H.4, H.5, H.6 (mostly complete), plus scattered items in H.3 — 28 of the ~48 tasks in Section H. The rest (H.2 entirely, most of H.3, H.7, H.8's live-match milestones) are explicitly deferred to Chapter 8, with inline rationale rather than silent gaps.

**Status:** committed (5 commits: crypto primitives, Step-0, config fingerprinting, tests, docs).

---

### Chapter 6 — Strategy Module & Decision-Making

**What this chapter covers (`docs/tasks.md` §7):** the strategy module is the boundary between "a generic communication component" and "a thinking agent" — a separate `BrainBase` interface, selected via config (`[strategy] cop_class`/`thief_class`), whose movement decision-authority is architecturally guaranteed to stay with the algorithm, never an LLM. A Bayesian belief map turns Chapter 4's raw scent into a probabilistic guess about the opponent's location, using the mandatory Manhattan-distance formula to pick a move toward or away from that guess. The LLM's role, if used at all, is text-only — this project implements only the zero-token `template` provider.

**What was implemented:**
- `domain/belief.py::BeliefMap` — uniform prior over open (non-blocked) cells, `update_from_scent` (posterior ∝ prior × scent-derived likelihood, renormalized), `arg_max()`. Blocked cells are excluded from the distribution entirely, not just zeroed.
- `domain/heuristics.py` — extracted `manhattan_distance`/`greedy_manhattan_move` as a shared helper, refactoring Chapter 3/4's `move_toward_policy`/`move_away_policy` to use it rather than duplicating the search loop (DRY). Reproduces the rulebook's own worked example exactly (`D((2,2),(5,5))=6`).
- `domain/strategy/brain_base.py` + `manhattan_brain.py` — `BrainBase` (abstract `_decide_move`, optional `_pick_move`) and `ManhattanHeuristicBrain`, the team's chosen baseline per `docs/PLAN.md` ADR-010. Neither method's signature can accept an LLM handle or hint text — a structural guarantee, not a convention.
- `shared/config.py::load_strategy_class` — dynamic `importlib`-based loading of `[strategy] cop_class`/`thief_class` (renamed from the rulebook's `police_class` for the same `AgentRole`-consistency reason as Chapter 2's `config/cop/`), defaulting to `ManhattanHeuristicBrain`.
- `domain/hints.py` — `Hint` (word-limited, `Intent`-tagged), `TemplateHintProvider` (zero-token, deterministic), `parse_claimed_direction`, and `detect_bluff` reproducing Chapter 4's own worked example (a lie about direction, exposed by the truthful scent trail).
- `docs/PRD_strategy_module.md` — the fifth per-mechanism PRD.
- Tests: `test_belief.py`, `test_heuristics.py`, `test_strategy.py`, `test_hints.py` (unit), `tests/integration/test_strategy_pipeline.py` — 48 new tests (193 total).

**Quality gate results:**
```
193 passed in 7.71s
TOTAL coverage: 99.65% (required: 85.0%)
ruff check: All checks passed!
```

**The headline result — a genuine partial-observability proof, not just plumbing:** `test_strategy_pipeline.py` drives two `ManhattanHeuristicBrain` instances (one per role) through a full match where each side's `_decide_move` call receives *only* its own belief map — itself fed only by that side's own reading of the opponent's scent trail. The opponent's true `Position` is never passed to either brain anywhere in the test; only the test harness (playing the role of "no external judge, just a human observer") uses both real positions to check for capture. The cop's belief converges tightly on the thief's real location, and a genuine capture occurs within the mandatory move budget — proving Chapter 1's Dec-POMDP partial-observability constraint holds architecturally, not merely by convention.

**Two things caught and fixed while building this, same discipline as every prior chapter:**
1. An early version of the custom-strategy-class-loading test pointed the config at `ManhattanHeuristicBrain` itself as the "custom" class — which would have passed even if `load_strategy_class` were silently broken and always fell back to its own default. Caught before trusting it; fixed by introducing a distinct `DummyCustomBrain` in the test module.
2. A first attempt at a multi-turn `detect_bluff` test scenario produced a confusing result (a false claim showing *higher* scent than the true direction) because several turns of accumulated path history overlapped near the starting region. Verified empirically (as always, before writing an assertion) that the function is correct for its intended use — assessing a single, isolated turn's move — and documented the multi-turn dilution as an explicit scope limitation rather than silently working around it.

**What was deliberately left undone, and why (see `docs/PRD_strategy_module.md` §3):** real LLM provider integration (`ollama`/`claude_api`/`claude_cli`) requires live external services this project's automated tests should not depend on, and Sec. 6.4.7 explicitly confirms the zero-token `template`-only mode is fully legitimate for an entire league series. Trust-weighted fusion of hints into the belief map, lie-frequency strategy, belief-map diffusion, and barrier-placement timing are all deeper, stateful features better suited once a live multi-turn match loop (Chapter 8) exists to give them something real to accumulate over.

**Tasks checked off:** `docs/TODO.md` Section E (E.1-E.2, E.5-E.7 mostly complete; E.3/E.4 marked as deliberate "decided not to pursue") and Section F.2-F.6 (belief map and bluff detection largely complete; hint/LLM depth explicitly scoped down) — 55 tasks this chapter.

**Status:** committed (7 commits: belief map, heuristics refactor, strategy module, config wiring, hints, tests, docs).

---

### Chapter 7 — User Interface (GUI) & Replay Simulator

**What this chapter covers (`docs/tasks.md` §8):** two distinct needs — the Live GUI answers "what is happening right now?" (local-truth-only: own position, belief heatmap, turn banner, never the opponent's true location), and the Replay Viewer answers "did it really happen as claimed?" (cryptographic re-verification of every logged step, with a green "Verified OK" or red "TAMPERED" stamp).

**What was implemented:**
- `domain/live_view_model.py` — `TurnState`, `belief_to_color` (white-to-red gradient, normalized to the map's own peak), `build_live_view_model` producing a `LiveViewModel` from *only* `own_position` + `BeliefMap` + `Board` — structurally incapable of holding the opponent's true position (no field, no parameter). Barrier cells render in a fixed distinct color, never a belief gradient.
- `domain/replay.py` — `ReplaySession` reusing Chapter 5's `verify()`/`audit_log()` exactly rather than re-implementing the verification loop; adds scrubbing (`next`/`previous`/`jump_to`) and the "voided from the first tamper onward" per-step display rule (Sec. 7.5.1), plus `verified_count`/`tampered_count` summary properties. `save_log`/`load_log` handle the JSON file round trip.
- `gui/live_gui.py` + `gui/replay_gui.py` — thin Tkinter wiring, all decisions already made in the view-model/session layer.
- `main.py` gained a `replay --log-file PATH` subcommand, so the Replay Viewer runs standalone, independent of any live match code.
- `docs/PRD_gui_replay.md` — the sixth per-mechanism PRD.
- Tests: `test_live_view_model.py`, `test_replay.py`, `test_gui.py` (unit, including real Tkinter widget construction/rendering/button-invocation — nothing mocked), `tests/integration/test_gui_pipeline.py` (two headline integration proofs) — 58 new tests (235 total).

**Quality gate results:**
```
235 passed in 7.97s
TOTAL coverage: 99.73% (required: 85.0%)
ruff check: All checks passed!
```
100% coverage on every GUI/replay module, including both Tkinter files — the `gui/*` coverage omission from `pyproject.toml` (added preemptively back in Chapter 1, anticipating GUI code would be hard to test) was removed once real widget-state testing proved it wasn't.

**A real Tkinter limitation found and worked around, same discipline as every prior chapter's empirical-verification habit:** the first version of the GUI test suite created a fresh `tk.Tk()` per test function. After a handful of create/destroy cycles it failed with `_tkinter.TclError: invalid command name "tcl_findLibrary"` — a genuine, documented Tkinter limitation (it does not reliably support creating and destroying many root interpreters in one process). Fixed with a session-scoped root fixture and a per-test `Toplevel` window for isolation instead, then re-verified the full suite passed cleanly.

**The two headline integration proofs, not just plumbing:**
1. `test_live_gui_stays_in_sync_across_a_real_multi_turn_match` drives the actual Chapter 6 strategy pipeline for 5 real turns and asserts, at every turn, that the rendered banner and own-position marker match the real turn state and real position — using only the cop's own local truth.
2. `test_replay_viewer_against_a_real_commit_reveal_sealed_multi_turn_log` builds a real multi-turn log via actual `commit()` calls over real board positions (not synthetic placeholders), saves it to a real file, reloads it, tampers the file on disk exactly as a dishonest player might, and confirms both the crypto layer and the GUI layer agree on the correct verdict throughout.

**What was deliberately left undone, and why (see `docs/PRD_gui_replay.md` §3):** wiring the turn banner to a real state machine, a scrolling event log, a scoreboard, and a threading model separating GUI updates from network I/O all require the Orchestrator and Log Manager that Chapter 8 builds — none of that exists yet. Visual board/belief replay inside the Replay Viewer wasn't built either, since `LogEntry.state` is intentionally generic at the crypto layer.

**An honest, flagged limitation — no screenshots:** `docs/tasks.md` Sec. 7.5.3 lists a belief-heatmap screenshot and a Replay Viewer "Verified OK" screenshot as mandatory submission deliverables. No tool available in this session captures native desktop window screenshots (only web-preview screenshots are supported here). Correctness was instead verified exhaustively via automated widget-state assertions — arguably a stronger correctness guarantee, but it does not substitute for the literal deliverable. **This is flagged as a manual step for you**: run `python -m police_thief replay --log-file <path>` (or launch `LiveGUI` directly) and capture the window before final submission.

**Tasks checked off:** `docs/TODO.md` Section I.1-I.2 — 25 of 37 tasks. The rest are either deferred to Chapter 8 (state machine wiring, event log, scoreboard, threading), deliberately out of scope by design (manual input controls), or the three screenshot tasks noted above.

**Status:** awaiting review before committing. Next up — Chapter 8 (Agent Architecture Design & Deep Reliability Mechanisms).
