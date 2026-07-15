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

**Status:** awaiting review before committing. Next up — Chapter 4 (dynamic pheromone trails & collective memory).
