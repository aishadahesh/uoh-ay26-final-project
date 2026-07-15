# TODO — Distributed Cops-and-Robbers P2P Project

Derived from `requirements.md` (itself derived from `ref/police_thief_p2p.pdf` + `ref/software_submission_guidelines-V3.pdf`). Organized by the book's recommended 7-layer incremental build order (Ch.10), plus setup, reliability, league, testing, docs, and submission phases. Each task is atomic and checkable. "Both roles" means duplicate the task once for the cop repo and once for the thief repo, since they must run as fully separate codebases/processes.

Legend: `[ ]` = not started, `[x]` = done. Do not skip layers — each stage should be end-to-end working before the next begins (Ch.10).

> **Architecture decision recorded during implementation (see `docs/PLAN.md` ADR-011):** development proceeds as a **single shared package/repo** (`police_thief`, role-differentiated via `--role cop`/`--role thief` and separate `config/police/`/`config/thief/` directories) rather than two duplicated repos from day one. This satisfies the "no shared runtime state" rule (two OS processes importing the same stateless module still share no memory) while avoiding premature code duplication. The literal two-GitHub-repos submission requirement (rule 49) is deferred to Section O (Submission Prep), where this codebase will be exported into two tagged repos before final submission. Tasks below written as "for cop repo" / "for thief repo" are satisfied by this single shared structure during development unless noted otherwise.

---

## A. Environment & Tooling Setup

- [x] T0001 Install Python 3.11+ and confirm version on dev machine — `requires-python = ">=3.11"` in `pyproject.toml`; `uv sync` resolved a 3.14.2 venv
- [x] T0002 Install `uv` (or chosen package manager) for dependency management — `uv 0.10.3` confirmed
- [x] T0003 Create a Python virtual environment for the cop agent — single shared `.venv` per architecture note above
- [x] T0004 Create a Python virtual environment for the thief agent — same shared `.venv`
- [ ] T0005 Install `fastmcp` package in both environments
- [x] T0006 Install `pytest` for both environments — `pytest`, `pytest-cov` added as dev dependencies
- [ ] T0007 Install `pydantic` (or equivalent) for config/schema validation
- [ ] T0008 Install `tomli`/`tomllib`/`tomli-w` for TOML read/write
- [ ] T0009 Install `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib` for Gmail API
- [ ] T0010 Install GUI toolkit (Tkinter confirm bundled, or install PyQt/PySide)
- [ ] T0011 Install `ngrok` CLI locally and verify `ngrok version`
- [ ] T0012 Create free ngrok account and retrieve authtoken
- [ ] T0013 Configure `ngrok config add-authtoken`
- [ ] T0014 Evaluate Localtonet as an ngrok alternative/backup tunnel
- [ ] T0015 Install `matplotlib` (or similar) for heatmap rendering
- [ ] T0016 Install `numpy` for scent-grid math
- [ ] T0017 Choose and install an LLM local runtime: Ollama
- [ ] T0018 Pull a small local model into Ollama (e.g., llama3/phi)
- [ ] T0019 Verify Ollama server responds on `localhost:11434`
- [ ] T0020 Obtain an Anthropic API key (or chosen LLM API) for `claude_api` mode
- [ ] T0021 Store API key in a local `.env` file, never committed
- [ ] T0022 Verify Claude Code CLI installed and authenticated for `claude_cli` mode
- [ ] T0023 Set up `pre-commit` hooks (lint/format) for both repos
- [x] T0024 Configure `ruff`/`flake8` linting rules — `[tool.ruff]`/`[tool.ruff.lint]` in `pyproject.toml`, zero violations confirmed
- [ ] T0025 Configure `black` (or chosen formatter) settings
- [ ] T0026 Set up `mypy` or `pyright` for type checking (optional but recommended)
- [x] T0027 Decide on Python package name/namespace for cop project (e.g., `police_thief`) — single shared package `police_thief` (see architecture note)
- [x] T0028 Decide on Python package name/namespace for thief project — same shared package `police_thief`
- [ ] T0029 Set up a shared local scratch directory for test logs/screenshots
- [ ] T0030 Verify two terminals can run two independent Python processes simultaneously without port clash
- [ ] T0031 Choose port numbers for cop's local FastMCP server (e.g., 8801)
- [ ] T0032 Choose port numbers for thief's local FastMCP server (e.g., 8802)
- [ ] T0033 Verify firewall/OS allows local binding to chosen ports
- [ ] T0034 Set up VS Code / IDE workspace for cop repo
- [ ] T0035 Set up VS Code / IDE workspace for thief repo
- [ ] T0036 Install `python-dotenv` or equivalent for environment variable loading
- [ ] T0037 Decide logging library/strategy (stdlib `logging` vs `structlog`)
- [ ] T0038 Configure logging to write to both console and a rotating file per role
- [ ] T0039 Create scratch/dev Gmail test account (or reuse personal) for OAuth testing
- [ ] T0040 Document all environment setup steps in a `SETUP.md` per repo

---

## B. Repository & Project Scaffolding (both roles)

- [ ] T0041 Create GitHub repo for the cop agent — deferred to Section O submission-prep repo split
- [ ] T0042 Create GitHub repo for the thief agent — deferred to Section O submission-prep repo split
- [ ] T0043 Set repo visibility: public, or private + share with lecturer's address
- [x] T0044 Initialize `git` in both local project folders — single shared repo initialized (initial commit already present)
- [x] T0045 Create initial `.gitignore` for cop repo (Python defaults + secrets) — single shared `.gitignore`, Python/venv/secrets patterns added
- [x] T0046 Create initial `.gitignore` for thief repo (Python defaults + secrets) — same shared `.gitignore`
- [x] T0047 Add `credentials.json` to `.gitignore` in both repos
- [x] T0048 Add `token.json` to `.gitignore` in both repos
- [x] T0049 Add `.env` to `.gitignore` in both repos
- [ ] T0050 Add `logs/` directory to `.gitignore` (or decide to keep sample logs tracked)
- [ ] T0051 Create top-level package folder structure for cop repo (`domain/`, `infra/`, `shared/`)
- [ ] T0052 Create top-level package folder structure for thief repo (mirrored)
- [ ] T0053 Create `config/police/` directory
- [ ] T0054 Create `config/thief/` directory
- [ ] T0055 Create empty `README.md` scaffold for cop repo with section headers matching Ch.9.4.6
- [ ] T0056 Create empty `README.md` scaffold for thief repo with section headers matching Ch.9.4.6
- [ ] T0057 Add cross-link placeholder from cop README to thief repo URL
- [ ] T0058 Add cross-link placeholder from thief README to cop repo URL
- [ ] T0059 Create `PRD/` folder for the 7 layered PRD documents (cop repo)
- [ ] T0060 Create `PRD/` folder for the 7 layered PRD documents (thief repo)
- [ ] T0061 Create `PLAN.md` work-plan file (cop repo)
- [ ] T0062 Create `PLAN.md` work-plan file (thief repo)
- [ ] T0063 Create `TODO.md` task file inside cop repo (project-management copy, distinct from this master file)
- [ ] T0064 Create `TODO.md` task file inside thief repo
- [ ] T0065 Create `LICENSE` file (confirm educational-use terms if reusing example code)
- [x] T0066 Add `pyproject.toml` / `requirements.txt` for cop repo dependencies — single shared `pyproject.toml` (uv-managed, `uv.lock` committed)
- [x] T0067 Add `pyproject.toml` / `requirements.txt` for thief repo dependencies — same shared `pyproject.toml`
- [x] T0068 Set up `tests/` directory skeleton (cop repo) — `tests/{unit,integration}` created
- [x] T0069 Set up `tests/` directory skeleton (thief repo) — same shared `tests/` tree
- [x] T0070 Set up `docs/` directory for research/analysis reports (both repos) — `docs/` already holds `tasks.md`, `TODO.md`, `PRD.md`, `PLAN.md`
- [ ] T0071 Create initial commit for cop repo
- [ ] T0072 Create initial commit for thief repo
- [ ] T0073 Push cop repo to GitHub remote
- [ ] T0074 Push thief repo to GitHub remote
- [ ] T0075 Verify both repos are reachable by a second account (simulating the lecturer's access)
- [ ] T0076 Set up branch protection / branching convention (e.g., `main` + feature branches)
- [ ] T0077 Create first feature branch for Stage-1 work in cop repo
- [ ] T0078 Create first feature branch for Stage-1 work in thief repo
- [ ] T0079 Decide and record team identity: unique 8-character code, no spaces
- [ ] T0080 Record team members' IDs for both repos' declarations
- [ ] T0081 Decide `group_id` / `group_name` values used across configs
- [ ] T0082 Draft initial `CONTRIBUTING.md` describing branch workflow (optional but recommended)
- [ ] T0083 Verify GitHub Actions / CI not required but consider adding a lint/test workflow (optional)
- [ ] T0084 Confirm repo default branch name convention (`main`)
- [ ] T0085 Set up issue templates or task board (optional project-management aid)
- [ ] T0086 Draft initial architecture diagram (freeform, for your own reference) mapping Orchestrator/modules
- [ ] T0087 Record the book's Mandatory Parameters Table values into a local reference doc for quick lookup
- [ ] T0088 Record the book's 55 mandatory rules into a local checklist doc for quick lookup during coding
- [ ] T0089 Schedule internal team review checkpoints aligned to the 7 build stages
- [ ] T0090 Confirm both team members can independently clone and run both repos locally

---

## C. Stage 1 — Base Logic: Board, Movement, Barriers, Capture (single process, no networking)

### C.0 Dec-POMDP Formal Model (Chapter 1 of `docs/tasks.md`) — *added during implementation*
- [x] T0890 Scaffold project structure: `pyproject.toml` (uv + ruff + pytest/coverage config), `src/police_thief` package, `tests/{unit,integration}`
- [x] T0891 Implement `AgentRole` enum and `NUM_AGENTS = 2` constant (`shared/constants.py`) representing the fixed `n` in the Dec-POMDP tuple
- [x] T0892 Implement version tracking (`shared/version.py`, `VERSION = "1.00"`) per the submission-guidelines versioning convention
- [x] T0893 Implement `DecPOMDPSpec` dataclass + discount-factor validation (`domain/dec_pomdp.py`), documenting the `<n, S, {Ai}, P, R, {Omega_i}, O, gamma>` tuple and where each remaining component (S, {Ai}, P, R, {Omega_i}, O) will be concretized in later chapters
- [x] T0894 Write unit tests for `AgentRole`, `NUM_AGENTS`, discount-factor validation, and `DecPOMDPSpec` immutability
- [x] T0895 Create `config/setup.json` and `config/rate_limits.json` version-tracked skeletons (content to be wired to real code in Stage 7 / Chapter 9's Gatekeeper)
- [x] T0896 Create `.env-example` and extend `.gitignore` for Python artifacts, `.venv`, and secrets
- [x] T0897 Run `uv sync`, `pytest --cov` (100% coverage on new code), and `ruff check` (zero violations) as the Chapter-1 quality gate

### C.1 Board & Coordinate System
- [ ] T0091 Define `BoardConfig` data structure (grid_size, axis_origin_corner, axis_start_index)
- [ ] T0092 Implement default `grid_size = 7` per Mandatory Parameters Table
- [ ] T0093 Implement coordinate system with configurable origin corner (default top-left = (0,0))
- [ ] T0094 Implement configurable axis start index (default 0)
- [ ] T0095 Write unit test: coordinate (0,0) resolves to the configured corner
- [ ] T0096 Write unit test: grid boundaries reject out-of-range coordinates
- [ ] T0097 Implement `Cell` / `Position` value type (immutable, hashable)
- [ ] T0098 Implement equality/hash for `Position` for use in sets/dicts (barrier lookups, visited cells)
- [ ] T0099 Implement `Board` class holding grid_size + set of blocked cells
- [ ] T0100 Implement method `Board.is_within_bounds(pos)`
- [ ] T0101 Implement method `Board.is_blocked(pos)`
- [ ] T0102 Implement method `Board.neighbors(pos)` returning the 4 orthogonal neighbors only
- [ ] T0103 Write unit test: `neighbors()` never returns diagonal cells
- [ ] T0104 Write unit test: `neighbors()` excludes out-of-bounds cells
- [ ] T0105 Write unit test: `neighbors()` excludes blocked cells (or flags them, depending on API design)

### C.2 Movement Rules
- [ ] T0106 Define `MoveSet` enum: N, S, E, W, STAY
- [ ] T0107 Implement `apply_move(position, move) -> new_position`
- [ ] T0108 Write unit test: each of N/S/E/W moves exactly one cell in the correct direction
- [ ] T0109 Write unit test: STAY returns the same position unchanged
- [ ] T0110 Implement move legality check: reject moves that leave board bounds
- [ ] T0111 Implement move legality check: reject moves into a blocked (barrier) cell
- [ ] T0112 Implement move legality check: reject any move not in `MoveSet` (defensive check against diagonal/other input)
- [ ] T0113 Write unit test: illegal out-of-bounds move raises/rejects rather than silently executing
- [ ] T0114 Write unit test: illegal into-barrier move raises/rejects rather than silently executing
- [ ] T0115 Decide and implement exact failure semantics for illegal moves (exception vs. rejection object vs. technical-loss flag)
- [ ] T0116 Write unit test: a thief with zero legal moves (fully boxed in) is flagged as captured

### C.3 Barrier Placement (Cop-only mechanic)
- [ ] T0117 Define `BarrierBudget` tracking remaining barriers vs. `max_barriers` (default 14)
- [ ] T0118 Implement `place_barrier(cop_position, target_cell)` — only adjacent-or-own cell allowed
- [ ] T0119 Write unit test: barrier placement on a cell not adjacent to cop is rejected
- [ ] T0120 Write unit test: barrier placement decrements the remaining budget
- [ ] T0121 Write unit test: barrier placement fails once budget is exhausted
- [ ] T0122 Implement permanent/irreversible barrier semantics (no un-blocking once placed)
- [ ] T0123 Write unit test: a previously-placed barrier remains blocked for the rest of the match
- [ ] T0124 Implement rule: barrier placement is public/declared, never hidden (data-model level: barrier events always recorded in the log)
- [ ] T0125 Write unit test: barrier event always includes exact location in whatever event/message structure is used
- [ ] T0126 Design barrier data structure shared between both agents' board models (must match schema in `config/game.json`)

### C.4 Capture & Win/Loss Detection
- [ ] T0127 Implement `check_capture(cop_position, thief_position) -> bool`
- [ ] T0128 Write unit test: cop landing on thief's cell triggers capture
- [ ] T0129 Write unit test: cop placing a barrier exactly on the thief's current cell also triggers capture
- [ ] T0130 Implement `CaptureClaim` event/message type (to be cryptographically signed later in Stage 6)
- [ ] T0131 Implement thief "boxed in" detection (no legal moves at all → treated as captured)
- [ ] T0132 Write unit test for thief-boxed-in edge cases (corner + surrounding barriers)
- [ ] T0133 Implement survival counter tracking steps survived by the thief
- [ ] T0134 Implement `survival_threshold` check (default 35) — thief "wins" once reached without capture
- [ ] T0135 Implement `max_moves` cap (default 35) as a match-length safety limit
- [ ] T0136 Write unit test: match ends at `max_moves` even with no capture (falls through to survival scoring)
- [ ] T0137 Decide relationship/precedence between `max_moves` and `survival_threshold` if they differ, and document it

### C.5 Scoring
- [ ] T0138 Implement `ScoringTable` data structure matching Mandatory Parameters Table values
- [ ] T0139 Implement scoring rule: capture → cop=20, thief=5 (defaults)
- [ ] T0140 Implement scoring rule: survival → cop=5, thief=10 (defaults)
- [ ] T0141 Implement scoring rule: technical loss → both sides 0
- [ ] T0142 Implement scoring rule: tie across a series → both sides `[tie score]` (default 2)
- [ ] T0143 Write unit test: capture scenario yields the correct cop/thief score pair
- [ ] T0144 Write unit test: survival scenario yields the correct cop/thief score pair
- [ ] T0145 Write unit test: technical-loss scenario yields 0/0
- [ ] T0146 Ensure scoring values are loaded from config, never hardcoded as magic numbers in game logic
- [ ] T0147 Write unit test: scoring values can be overridden upward via config without code changes

### C.6 Single-Process Local Simulation Harness
- [ ] T0148 Build a minimal local game loop that alternates cop/thief turns within one process (pre-networking)
- [ ] T0149 Implement a placeholder "always move toward target" cop policy for local testing
- [ ] T0150 Implement a placeholder "always move away from cop" thief policy for local testing
- [ ] T0151 Run a full local match end-to-end with no crash (Stage-1 milestone criterion)
- [ ] T0152 Verify scoring output is printed/logged correctly at match end
- [ ] T0153 Add CLI entry point to run the local simulation (`--role police`/`--role thief` stub, single-process mode)
- [ ] T0154 Write integration test: full local match completes and returns a valid score tuple
- [ ] T0155 Write integration test: illegal-move attempt during local match is handled without crashing the loop
- [ ] T0156 Write integration test: barrier-exhaustion scenario plays out correctly to match end
- [ ] T0157 Write integration test: max_moves cap correctly ends a stalemate-style match
- [ ] T0158 Profile the single-process loop for obvious performance issues (should be trivial at this scale)
- [ ] T0159 Document Stage-1 architecture decisions in `PRD/01-base-logic.md`
- [ ] T0160 Confirm Stage-1 milestone: two simulated agents legally move on the grid; barriers block movement; capture detection works (sign off before Stage 2)

### C.7 Config Wiring for Board/Physics (early pass, refined later)
- [ ] T0161 Draft the `board_and_agents` section of `config/game.json` schema (grid_size, num_agents, thief_start, cop_start, axis_origin_corner, axis_start_index)
- [ ] T0162 Draft the `movement_and_barriers` section of `config/game.json` schema (move_set, max_barriers, max_moves, survival_threshold)
- [ ] T0163 Draft the `scoring` section of `config/game.json` schema (capture_cop, capture_thief, survival_cop, survival_thief, tie_score, technical_loss)
- [ ] T0164 Write a config loader that reads `config/game.json` and constructs `BoardConfig`/`ScoringTable`
- [ ] T0165 Write unit test: config loader rejects a config missing required fields
- [ ] T0166 Write unit test: config loader applies defaults correctly when values are absent (where allowed)
- [ ] T0167 Write unit test: loader enforces minimum values are not violated (e.g., `max_barriers >= 14`)
- [ ] T0168 Add schema versioning field (`schema_version`) to the config and validate it on load

---

## D. Stage 2 — Basic FastMCP P2P Infrastructure (separate processes over localhost)

### D.1 Process Separation
- [ ] T0169 Split single-process simulation into two independent runnable processes (cop / thief)
- [ ] T0170 Create `config/police/` local settings distinct from `config/thief/`
- [ ] T0171 Verify no shared Python module holds mutable state imported by both processes
- [ ] T0172 Add a manual review checklist item forbidding cross-imports between cop and thief packages
- [ ] T0173 Write a design note documenting the Zero-Trust separation boundary explicitly

### D.2 FastMCP Server (per role)
- [ ] T0174 Install and import FastMCP in the cop package
- [ ] T0175 Install and import FastMCP in the thief package
- [ ] T0176 Instantiate a FastMCP("police_peer") server instance
- [ ] T0177 Instantiate a FastMCP("thief_peer") server instance
- [ ] T0178 Implement @mcp.tool receive_move(...) on the cop server
- [ ] T0179 Implement @mcp.tool receive_move(...) on the thief server
- [ ] T0180 Decide the exact tool signature/schema for move exchange (state, move, intent placeholder for now)
- [ ] T0181 Implement server-side input validation on receive_move (reject malformed payloads)
- [ ] T0182 Bind cop server to 0.0.0.0 on its chosen port (e.g., 8801) with transport=http
- [ ] T0183 Bind thief server to 0.0.0.0 on its chosen port (e.g., 8802) with transport=http
- [ ] T0184 Write a smoke test: server starts and responds to a health-check call
- [ ] T0185 Add graceful shutdown handling for the server process (SIGINT/SIGTERM)

### D.3 FastMCP Client (per role)
- [ ] T0186 Implement a client wrapper that calls the opponents receive_move tool
- [ ] T0187 Implement client-side retry-on-connection-refused logic (bounded retries)
- [ ] T0188 Implement client-side timeout for the outbound call
- [ ] T0189 Write unit test: client correctly serializes a move payload before sending
- [ ] T0190 Write unit test: client correctly deserializes the opponents acknowledgment/response
- [ ] T0191 Write integration test: cop client successfully calls thief server on localhost and vice versa

### D.4 Turn Management (pre-crypto version)
- [ ] T0192 Implement a basic turn-alternation protocol: cop moves, then thief moves, repeat
- [ ] T0193 Implement local turn-tracking state on each side
- [ ] T0194 Write integration test: two localhost processes complete a full match via network calls only (no shared memory)
- [ ] T0195 Verify each side's local board state stays in sync after every exchanged move
- [ ] T0196 Write test: simulate a dropped/garbled message and confirm it does not crash either process
- [ ] T0197 Log every sent/received MCP message with timestamps for later debugging

### D.5 Config for Networking
- [ ] T0198 Draft the network section of config/game.toml (my_port, opponent_url, turn_timeout_seconds)
- [ ] T0199 Implement TOML config loader for the private per-peer settings
- [ ] T0200 Write unit test: TOML loader correctly parses the network, strategy, trash_talk, llm, and email sections
- [ ] T0201 Write unit test: TOML loader tolerates commented-out optional sections
- [ ] T0202 Confirm private TOML never contains any value that must be agreed with the opponent
- [ ] T0203 Implement config precedence: shared JSON values override matching TOML keys where both exist

### D.6 MCP Protocol Hygiene
- [ ] T0204 Document exactly which tools are exposed by each server (API contract doc)
- [ ] T0205 Version the MCP tool schema so future changes do not silently break compatibility
- [ ] T0206 Add defensive parsing: reject any tool call with unexpected/extra fields
- [ ] T0207 Add defensive parsing: reject any tool call missing required fields
- [ ] T0208 Write test: malformed JSON payload to a tool returns a clean error, not a crash
- [ ] T0209 Confirm server responses never leak more information than the local-truth principle allows (strengthen later in Stage 6)
- [ ] T0210 Benchmark round-trip latency of a localhost MCP call as a sanity baseline before adding tunneling overhead

### D.7 Stage-2 Milestone
- [ ] T0211 Confirm milestone: a geometric message sent from agent A over localhost is received and decoded correctly at agent B
- [ ] T0212 Document Stage-2 architecture decisions in PRD/02-mcp-infra.md
- [ ] T0213 Run a full two-process match end-to-end with no crash, using the Stage-1 placeholder policies over the network
- [ ] T0214 Confirm identical scoring/log output vs. the single-process Stage-1 version (parity check)
- [ ] T0215 Tag this milestone commit locally (not yet the final submission tag) for traceability

---

## E. Stage 3 — First Strategy Module (Blind: no language, no scent yet)

### E.1 Strategy Module Boundary
- [ ] T0216 Create a dedicated strategy module/package, separate from PeerRuntime networking code
- [ ] T0217 Define BrainBase abstract class with a _decide_move() method
- [ ] T0218 Add a _pick_move() (or barrier-placement) hook for the cops BrainBase subclass
- [ ] T0219 Wire PeerRuntime to call into the strategy module exactly once per turn, at the correct pipeline point
- [ ] T0220 Write unit test: strategy module receives the current known state and returns a legal move
- [ ] T0221 Write unit test: strategy module never receives full objective state (only local-truth-consistent inputs)
- [ ] T0222 Add config keys police_class / thief_class in the private TOML strategy section
- [ ] T0223 Implement dynamic class loading from a package.module:Class string (e.g., via importlib)
- [ ] T0224 Write unit test: dynamic strategy-class loading correctly instantiates a custom subclass
- [ ] T0225 Write unit test: fallback to default heuristic brain when no custom class is configured

### E.2 Manhattan-Distance Heuristic (baseline/example track)
- [ ] T0226 Implement Manhattan distance function D = |x_cop - x_target| + |y_cop - y_target|
- [ ] T0227 Write unit test: Manhattan distance matches hand-computed examples
- [ ] T0228 Implement greedy-toward-target move selection using Manhattan distance
- [ ] T0229 Write unit test: greedy heuristic picks a move that strictly decreases distance when possible
- [ ] T0230 Implement tie-breaking logic when multiple moves yield equal distance reduction
- [ ] T0231 Implement thief flee heuristic: maximize distance from believed cop position
- [ ] T0232 Write unit test: flee heuristic increases distance from the cops last known position

### E.3 Custom/Alternative Algorithm Track (optional, if chosen)
- [ ] T0233 Decide whether the team will implement a custom pathfinding/planning algorithm instead of or alongside heuristics
- [ ] T0234 If custom: design the algorithms state representation
- [ ] T0235 If custom: implement the algorithms core decision function
- [ ] T0236 If custom: write unit tests validating legality and sane behavior of its output moves
- [ ] T0237 If custom: benchmark its decision latency per turn against step_deadline_seconds

### E.4 Reinforcement-Learning Track (optional tool, if chosen)
- [ ] T0238 Decide whether the team will use RL as one optional strategy tool
- [ ] T0239 If RL chosen: design the state representation for Q(s,a)
- [ ] T0240 If RL chosen: implement a Q-table (or function-approximator) storage structure
- [ ] T0241 If RL chosen: implement the Bellman update Q(s,a) += alpha times reward plus gamma times max next Q minus current Q
- [ ] T0242 If RL chosen: implement epsilon-greedy action selection
- [ ] T0243 If RL chosen: implement a training loop against a scripted/self-play opponent
- [ ] T0244 If RL chosen: implement a decay schedule for epsilon over training episodes
- [ ] T0245 If RL chosen: implement checkpointing/saving of learned Q-values
- [ ] T0246 If RL chosen: implement loading of a pretrained policy at match start
- [ ] T0247 If RL chosen: write unit test verifying the Q-update math against a hand-computed example
- [ ] T0248 If RL chosen: log learning-curve data (episode vs. cumulative reward) for later reporting
- [ ] T0249 If RL chosen: produce a learning-curve plot for the academic README
- [ ] T0250 If RL chosen: verify the final trained policy still only ever outputs legal moves
- [ ] T0251 If RL chosen: document that RL is one optional tool among several, not a course requirement, in the README

### E.5 Barrier-Placement Strategy (Cop)
- [ ] T0252 Implement a barrier-placement policy function distinct from movement policy
- [ ] T0253 Implement a simple corner-the-thief barrier heuristic (progressively block flanking cells)
- [ ] T0254 Write unit test: barrier placement never targets a cell more than one step from the cop
- [ ] T0255 Write unit test: barrier budget is respected by the placement policy (stops placing at zero budget)
- [ ] T0256 Tune barrier-placement timing (early game vs. late game) and document reasoning

### E.6 Decision Pipeline Wiring & Determinism
- [ ] T0257 Ensure the actual move-selection computation is always pure algorithmic/deterministic code (no LLM call in this stage)
- [ ] T0258 Add a hard boundary/interface so a later LLM verbal layer cannot influence the move return value
- [ ] T0259 Add a code-review checklist item: no LLM output is ever assigned to the move variable
- [ ] T0260 Add logging of every decision made by the strategy module (state in, move out) for later debugging

### E.7 Stage-3 Milestone
- [ ] T0261 Confirm milestone: given a known target position, the computing agent executes the shortest legal path with no manual intervention
- [ ] T0262 Run a full two-process match using real (non-placeholder) strategies end-to-end
- [ ] T0263 Write integration test: match completes with sensible (non-random-looking) tactical behavior from both sides
- [ ] T0264 Document Stage-3 decisions in PRD/03-strategy-module.md
- [ ] T0265 Record chosen strategy track (heuristic / custom / RL) rationale for the academic README draft

---

## F. Stage 4 — Language + Scent (pheromone mechanics, deception hints, LLM integration)

### F.1 Pheromone Emission & Decay
- [ ] T0266 Define `ScentField` data structure sized `[scent field size]` (default 5x5) centered on an agent
- [ ] T0267 Implement emission with `scent_center_intensity` (default 0.9) at the emitting agent's own cell
- [ ] T0268 Implement radial falloff of intensity from the emission center across the 5x5 field
- [ ] T0269 Implement the mandatory decay formula: tau(t+1) = max(0, (1 - rho) * tau(t) + delta_tau)
- [ ] T0270 Wire `rho` (scent decay rate, default 0.10) from config, not hardcoded
- [ ] T0271 Implement per-cell scent state storage for the full board grid
- [ ] T0272 Implement per-turn decay application across the entire board (both agents' emissions)
- [ ] T0273 Write unit test: emission at t=0 yields exactly `scent_center_intensity` at the agent's own cell
- [ ] T0274 Write unit test: decay-only cell (agent left) follows the exact decay curve over N turns
- [ ] T0275 Write unit test: re-emission while agent remains present keeps intensity elevated at/above the decay floor
- [ ] T0276 Write unit test: scent value never goes negative (floor at zero enforced)
- [ ] T0277 Write unit test: scent value never exceeds the configured intensity ceiling
- [ ] T0278 Implement symmetric scent tracking: cop's field is visible to the thief's belief logic and vice versa
- [ ] T0279 Verify scent maps are computed independently per side from each side's own local observations (no shared object)
- [ ] T0280 Add a debug visualization/printout of the scent grid for development purposes

### F.2 Belief Map Construction
- [ ] T0281 Define `BeliefMap` structure: probability distribution `b(s)` over board cells
- [ ] T0282 Implement Bayesian-style update of `b(s)` incorporating the observed scent field
- [ ] T0283 Implement Bayesian-style update of `b(s)` incorporating the opponent's verbal hint (weighted by trust)
- [ ] T0284 Implement `arg max_s b(s)` extraction (current best-guess opponent location)
- [ ] T0285 Write unit test: belief map updates correctly given a synthetic scent snapshot
- [ ] T0286 Write unit test: belief map normalizes to a valid probability distribution (sums to 1) after each update
- [ ] T0287 Write unit test: blocked/barrier cells always carry zero belief
- [ ] T0288 Implement belief-map decay/diffusion over time when no new evidence arrives
- [ ] T0289 Implement a trust-weighting mechanism for verbal hints vs. the always-trustworthy scent channel
- [ ] T0290 Write unit test: a caught lie (hint contradicts scent trail) reduces future trust weight assigned to that opponent's hints
- [ ] T0291 Implement the worked lie-detection example as a regression test (south-east scent trail vs. false north claim)

### F.3 Natural-Language Hint Generation & Parsing
- [ ] T0292 Define the free-text hint schema/field in the move-exchange message
- [ ] T0293 Implement `[hint word limit]` enforcement (default 15 words) on outgoing hints
- [ ] T0294 Implement `[game arena]` theme substitution into hint text (e.g., "New York" landmarks) or empty-string fallback
- [ ] T0295 Write unit test: generated hint never exceeds the configured word limit
- [ ] T0296 Implement an `Intent` flag alongside every hint marking it as truthful or a deliberate lie
- [ ] T0297 Write unit test: `Intent` flag is always set before the hint is sent (never left undefined)
- [ ] T0298 Implement hint-parsing logic on the receiving side to extract usable directional/positional signal
- [ ] T0299 Write unit test: hint parser handles a variety of phrasing styles without crashing
- [ ] T0300 Write unit test: hint parser gracefully handles nonsensical or malformed text (no signal extracted, no crash)
- [ ] T0301 Prohibit direct numeric coordinate leakage in generated hint text (no raw grid coordinates)
- [ ] T0302 Write unit test/lint check: hint text never contains a raw coordinate pair pattern

### F.4 LLM Integration for the Verbal Layer Only
- [ ] T0303 Confirm and document: the LLM is used exclusively for hint text generation and opponent-hint interpretation, never for move selection
- [ ] T0304 Implement `[trash_talk] provider` config switch: template / ollama / claude_api / claude_cli
- [ ] T0305 Implement `template` provider: deterministic pre-written phrases, zero tokens
- [ ] T0306 Implement `ollama` provider: call local model at `localhost:11434`
- [ ] T0307 Implement `claude_api` provider: call Anthropic API with a small/cheap model
- [ ] T0308 Implement `claude_cli` provider: shell out to `claude -p` via Claude Code CLI
- [ ] T0309 Implement `every_n_steps` throttling to reduce LLM invocation frequency
- [ ] T0310 Implement `step_deadline_seconds` timeout around every LLM call
- [ ] T0311 Write unit test: LLM call exceeding its deadline is aborted/falls back gracefully
- [ ] T0312 Implement a fallback path: if the configured LLM provider is unreachable, fall back to `template` mode rather than crash
- [ ] T0313 Write integration test: fallback path triggers correctly when Ollama/API is deliberately made unreachable
- [ ] T0314 Implement token-usage counting for every LLM call (for later Step-0/budget reporting)
- [ ] T0315 Write unit test: token counter accumulates correctly across a full match
- [ ] T0316 Enforce `[token budget per series]` (default ~200000) as a soft cap with warning/log when approached
- [ ] T0317 Implement prompt templates for hint generation (bluff/deception composition)
- [ ] T0318 Implement prompt templates for opponent-hint psychological analysis (bluff classifier / behavioral profiler)
- [ ] T0319 Write unit test: prompt construction never embeds the agent's own true hidden state in a way that could leak via a bug
- [ ] T0320 Document the LLM integration architecture (which layer calls the model, how output flows back) in `PRD/04-language-scent.md`

### F.5 Deception & Psychological Layer
- [ ] T0321 Design a strategy for deciding when to lie vs. tell the truth in verbal hints
- [ ] T0322 Implement randomized or strategic lie-frequency logic (avoid being either always-truthful or always-lying, both exploitable)
- [ ] T0323 Implement a simple opponent-hint "bluff classifier" heuristic (cross-reference hint against scent)
- [ ] T0324 Write unit test: bluff classifier flags a hint contradicted by the scent trail
- [ ] T0325 Write unit test: bluff classifier does not falsely flag a truthful, scent-consistent hint

### F.6 Stage-4 Milestone
- [ ] T0326 Confirm milestone: free-form hint reporting subject to the word-count limit works end-to-end
- [ ] T0327 Confirm milestone: a scent map is computed and viewable/loggable
- [ ] T0328 Confirm milestone: the LLM produces a hint (true or lie) every step without crashing the match
- [ ] T0329 Run a full match with real scent + real LLM-generated hints end-to-end with no crash
- [ ] T0330 Verify belief maps visibly track approximate opponent location better than random guessing over a test match
- [ ] T0331 Document Stage-4 decisions and worked examples in `PRD/04-language-scent.md`

---

## G. Stage 5 — Cloud Exposure & Tunneling (real cross-machine P2P)

### G.1 Tunnel Setup
- [ ] T0332 Configure `ngrok http <cop_port>` and confirm a public HTTPS URL is issued
- [ ] T0333 Configure `ngrok http <thief_port>` and confirm a public HTTPS URL is issued
- [ ] T0334 Verify the public ngrok URL is reachable from an external network (e.g., mobile hotspot test)
- [ ] T0335 Update `config/game.toml` `opponent_url` to point at the tunneled public URL rather than localhost
- [ ] T0336 Test Localtonet as a fallback tunnel provider in case ngrok is unavailable
- [ ] T0337 Document the tunnel-startup procedure step by step for reproducibility
- [ ] T0338 Automate tunnel startup via a script/Makefile target (optional convenience)
- [ ] T0339 Handle tunnel URL rotation (free ngrok URLs change on restart) by re-sharing the URL with the opponent team each session
- [ ] T0340 Write a runbook entry: what to do if the tunnel drops mid-match

### G.2 Cross-Machine Match Testing
- [ ] T0341 Recruit a second machine (or teammate's machine) to run the opponent side for a real cross-machine test
- [ ] T0342 Run a full match between two genuinely separate machines over the public internet
- [ ] T0343 Verify latency over the tunnel is within acceptable bounds for `turn_timeout_seconds`
- [ ] T0344 Write integration test/checklist: confirm no `localhost`-only assumptions remain anywhere in networking code
- [ ] T0345 Test behavior when the opponent's tunnel is temporarily down (simulated network partition)
- [ ] T0346 Verify Deadline Tracker/Watchdog behavior under real (non-simulated) network latency

### G.3 NAT/Firewall Considerations
- [ ] T0347 Confirm outbound firewall rules do not block the ngrok/Localtonet client process
- [ ] T0348 Confirm no manual port-forwarding is required beyond the tunnel tool itself
- [ ] T0349 Document any campus/ISP network restrictions encountered and their workarounds

### G.4 Stage-5 Milestone
- [ ] T0350 Confirm milestone: an agent on a remote machine connects via ngrok and gameplay updates correctly per step (LLM active in the loop)
- [ ] T0351 Document Stage-5 setup in `PRD/05-cloud-tunnel.md`
- [ ] T0352 Record the exact tunnel command/config used for reproducibility by the lecturer

---

## H. Stage 6 — Cryptographic Security & Zero-Knowledge Protocol

### H.1 Commit-Reveal Core Implementation
- [ ] T0353 Implement `commit(state, move, intent)` producing `H_commit = SHA256(state || move || intent || nonce)`
- [ ] T0354 Implement canonical JSON serialization (sorted keys, fixed separators) for the hashed payload
- [ ] T0355 Implement cryptographically-secure Nonce generation (e.g., `secrets.token_hex`), never `random`
- [ ] T0356 Write unit test: identical inputs with different Nonces produce different commitment hashes
- [ ] T0357 Write unit test: `commit()` never transmits the raw move/intent, only the hash
- [ ] T0358 Implement `verify(state, move, intent, nonce, h_commit)` recomputing and comparing hashes
- [ ] T0359 Use constant-time comparison (e.g., `secrets.compare_digest`) in `verify()`
- [ ] T0360 Write unit test: `verify()` returns True for a correct, untampered reveal
- [ ] T0361 Write unit test: `verify()` returns False for any single-field tampering (state/move/intent/nonce)

### H.2 Four-Step Protocol Wiring
- [ ] T0362 Implement Step 1 (Commit): send only `H_commit` over the network
- [ ] T0363 Implement Step 2 (Acknowledge): opponent confirms receipt and lock-in before either side proceeds
- [ ] T0364 Write unit test: Acknowledge cannot be sent before a valid Commit was received
- [ ] T0365 Implement Step 3 (Reveal): send the actual move + hint text, Nonce still withheld
- [ ] T0366 Write unit test: Reveal step is rejected if it arrives before the corresponding Acknowledge
- [ ] T0367 Implement Step 4 (Audit / Final Reveal): reveal all Nonces only at game end
- [ ] T0368 Write unit test: the four steps cannot be executed out of order (protocol sequencing enforced)
- [ ] T0369 Write unit test: skipping a step causes a technical-loss/rejection, not a silent pass-through
- [ ] T0370 Add sequence diagrams/comments in code documenting the four-step handshake per turn

### H.3 Mutual Audit & Log Integrity
- [ ] T0371 Implement full match-log recording of every step's state, move, intent, nonce, and commitment hash
- [ ] T0372 Implement end-of-match mutual audit: recompute every step's hash and compare against the log's recorded commitment
- [ ] T0373 Write unit test: audit passes on an untampered log
- [ ] T0374 Write unit test: audit fails and flags tampering when any single byte of a logged step is altered
- [ ] T0375 Implement automatic technical-loss declaration triggered by a failed audit
- [ ] T0376 Write integration test: full match runs, log is deliberately tampered post-hoc, and audit correctly catches it
- [ ] T0377 Ensure the audit result is deterministic and reproducible independent of who runs it

### H.4 Capture Claim & Barrier Declaration Integrity
- [ ] T0378 Implement cryptographic signing of `Capture Claim` events
- [ ] T0379 Write unit test: a false capture claim is exposed during audit (position mismatch)
- [ ] T0380 Implement cryptographic signing/logging of every barrier-placement declaration
- [ ] T0381 Write unit test: barrier location cannot be silently altered after being declared without breaking the audit

### H.5 Scent-Model Locking
- [ ] T0382 Cryptographically lock the scent emission/decay formula parameters into the signed shared config before match start
- [ ] T0383 Write unit test: any attempt to change scent parameters mid-match is detected/rejected

### H.6 Step-0 Computational Fairness Declaration
- [ ] T0384 Implement hardware-spec gathering: OS, CPU core count, RAM size, GPU/VRAM presence
- [ ] T0385 Implement LLM-model-name capture for the Step-0 declaration
- [ ] T0386 Implement Git commit-hash capture for the Step-0 declaration
- [ ] T0387 Implement team-name and game/sub-game-number capture for the Step-0 declaration
- [ ] T0388 Serialize the Step-0 declaration as canonical JSON
- [ ] T0389 Cryptographically sign the Step-0 declaration with a pre-shared/agreed key
- [ ] T0390 Write unit test: Step-0 declaration cannot be modified after signing without invalidating the signature
- [ ] T0391 Implement exchange of Step-0 declarations between both agents before the first real move
- [ ] T0392 Write integration test: match refuses to start without both sides' valid Step-0 declarations

### H.7 Replay-Ready Log Format
- [ ] T0393 Ensure the log format produced here is directly consumable by the Stage-7 Replay Viewer
- [ ] T0394 Write a schema/contract test verifying log fields match what the Replay Viewer expects

### H.8 Stage-6 Milestone
- [ ] T0395 Confirm milestone: moves must be committed via Commit and only then revealed via Reveal, with Nonce
- [ ] T0396 Confirm milestone: correct Step-0 hardware declaration exchanged and verified
- [ ] T0397 Run a full match with the complete crypto protocol active end-to-end with no crash
- [ ] T0398 Deliberately inject a tampering bug and confirm the match is correctly disqualified
- [ ] T0399 Document Stage-6 decisions in `PRD/06-security-crypto.md`
- [ ] T0400 Peer-review the cryptographic code with your teammate for subtle bugs (constant-time comparisons, nonce reuse, serialization consistency)

---

## I. Stage 7 — GUI, Replay Viewer & Gmail Reporting Automation

### I.1 Live GUI — Local Truth Only
- [ ] T0401 Choose GUI toolkit (Tkinter or PyQt/PySide) and scaffold a main window per role
- [ ] T0402 Design the GUI layout: own position, own scent-emitted trail, belief heatmap over opponent, turn banner
- [ ] T0403 Implement rendering of the board grid at the configured `[board size]`
- [ ] T0404 Implement rendering of the agent's own current position on the grid
- [ ] T0405 Implement rendering of static barrier cells (blocked, no belief)
- [ ] T0406 Implement heatmap color-gradient rendering of the belief map (e.g., deeper red = higher probability)
- [ ] T0407 Write unit test: heatmap rendering never displays the opponent's true position directly
- [ ] T0408 Implement live refresh of the heatmap as new turns are played
- [ ] T0409 Implement the turn-state banner ("YOUR TURN" vs "LOCKED")
- [ ] T0410 Wire the turn-state banner to the actual Commit/Acknowledge/Reveal state machine state
- [ ] T0411 Write unit test: banner shows LOCKED immediately after a Commit is sent, before Reveal completes
- [ ] T0412 Write unit test: banner shows YOUR TURN only when the local agent may legally act
- [ ] T0413 Implement disabling of manual input controls while LOCKED (prevent user from acting out of turn)
- [ ] T0414 Add a scrolling event/log panel showing recent hints, moves, and barrier placements
- [ ] T0415 Add a scoreboard panel showing current score/turn count
- [ ] T0416 Add graceful handling of GUI close/exit without crashing the underlying match process
- [ ] T0417 Test GUI responsiveness under normal match pacing (no UI freeze during LLM calls)
- [ ] T0418 Run the GUI update loop on a separate thread/async task from network I/O to avoid blocking
- [ ] T0419 Write integration test: GUI correctly reflects a full match from start to finish without desync
- [ ] T0420 Take and save a screenshot of the belief-heatmap GUI for the README

### I.2 Replay Viewer Application
- [ ] T0421 Scaffold a standalone Replay Viewer application (CLI or GUI)
- [ ] T0422 Implement loading of a saved match log JSON file
- [ ] T0423 Implement step-by-step navigation controls (next/previous/scrub)
- [ ] T0424 Implement per-step recomputation of SHA-256 over (nonce, move) from the log
- [ ] T0425 Implement comparison of recomputed hash against the log's stored commitment
- [ ] T0426 Implement the green "Verified OK" stamp display per step on match
- [ ] T0427 Implement the red "TAMPERED" banner display on any mismatch
- [ ] T0428 Implement match-level disqualification flagging once any tamper is detected
- [ ] T0429 Write unit test: verification engine correctly verifies an untampered log end-to-end
- [ ] T0430 Write unit test: verification engine correctly flags a deliberately corrupted log
- [ ] T0431 Implement visual replay of board state alongside the verification stamps (position/barriers per step)
- [ ] T0432 Implement replay of scent/belief map state per step (optional enhancement)
- [ ] T0433 Add a summary view: total steps, verification pass/fail count, final score
- [ ] T0434 Write integration test: replay viewer runs against a real completed match log without crashing
- [ ] T0435 Take and save a screenshot of the Replay Viewer showing "Verified OK" for the README
- [ ] T0436 Take and save a screenshot of the Replay Viewer showing "TAMPERED" against a deliberately corrupted test log (for your own validation, not submission)
- [ ] T0437 Package the Replay Viewer so it can be run independently from the live match code

### I.3 Gmail API OAuth 2.0 Setup
- [ ] T0438 Create/select a Google Cloud project for the cop agent's Gmail integration
- [ ] T0439 Enable the Gmail API in the Google Cloud Console
- [ ] T0440 Configure the OAuth consent screen (External or Internal, Test Users list)
- [ ] T0441 Add both team members' emails to the Test Users list
- [ ] T0442 Restrict OAuth scope to `gmail.send` only
- [ ] T0443 Create OAuth Client ID credentials of type Desktop Application
- [ ] T0444 Download `credentials.json` into the local project folder
- [ ] T0445 Confirm `credentials.json` is listed in `.gitignore` before any commit
- [ ] T0446 Run the first authorization flow locally and confirm `token.json` is generated
- [ ] T0447 Confirm `token.json` is listed in `.gitignore` before any commit
- [ ] T0448 Repeat the same OAuth setup steps for the thief agent's own Google Cloud project (or shared project, per team decision)
- [ ] T0449 Write a setup runbook documenting all OAuth steps for reproducibility
- [ ] T0450 Test token refresh behavior (force an expired access token and confirm silent refresh works)

### I.4 Gmail Sending Implementation
- [ ] T0451 Implement `get_service()` loading credentials/token and building the Gmail API service object
- [ ] T0452 Implement `send_report(service, to_addr, subject, body)` constructing a MIME message
- [ ] T0453 Implement base64url encoding of the MIME message before sending
- [ ] T0454 Wire the recipient address to the configured `[agent's report address]`
- [ ] T0455 Write unit test: message construction produces valid MIME structure
- [ ] T0456 Write integration test: a test email is successfully sent and received at the target address
- [ ] T0457 Implement error handling for Gmail API send failures (network error, auth error, quota error)
- [ ] T0458 Implement retry-with-backoff on transient send failures
- [ ] T0459 Log every send attempt (success/failure) locally for audit purposes

### I.5 Gatekeeper: Quota Manager
- [ ] T0460 Implement a daily operation counter for Gmail sends
- [ ] T0461 Implement a configurable daily safety threshold
- [ ] T0462 Write unit test: quota manager blocks sends once the daily threshold is reached
- [ ] T0463 Persist the daily counter across process restarts (file or lightweight local store)
- [ ] T0464 Write unit test: counter resets correctly at day boundary

### I.6 Gatekeeper: Token-Bucket Rate Limiter
- [ ] T0465 Implement `TokenBucket` class with `capacity` and `refill_rate` parameters
- [ ] T0466 Implement continuous refill logic based on elapsed time
- [ ] T0467 Implement `allow(cost=1.0)` method spending a token if available
- [ ] T0468 Write unit test: bucket starts full at capacity
- [ ] T0469 Write unit test: bucket refills over time up to capacity, never beyond
- [ ] T0470 Write unit test: `allow()` returns False when no tokens are available
- [ ] T0471 Wire the token-bucket parameters to config (`requests_per_minute`, `concurrent_requests`)
- [ ] T0472 Integrate the token bucket in front of every outbound Gmail API call
- [ ] T0473 Write integration test: rapid-fire send attempts are correctly throttled by the bucket

### I.7 Gatekeeper: DOS/Anomaly Detector & 429 Handling
- [ ] T0474 Implement detection of abnormal repeated-send patterns (e.g., N sends within a short window)
- [ ] T0475 Implement a circuit-breaker/lock state that halts all sends once an anomaly is detected
- [ ] T0476 Write unit test: anomaly detector trips on a simulated infinite-loop send pattern
- [ ] T0477 Implement HTTP 429 response detection from the Gmail API
- [ ] T0478 Implement backoff-and-wait logic specifically for 429 responses (respecting `retry_backoff_sec` and `max_retries`)
- [ ] T0479 Write unit test: a simulated 429 response triggers backoff rather than an immediate retry storm
- [ ] T0480 Implement a bounded request queue (`queue_depth`) for outbound reports under load
- [ ] T0481 Write unit test: queue depth cap is respected; excess requests are rejected/logged rather than silently dropped
- [ ] T0482 Wire the Quota Manager, Token-Bucket, and DOS Detector into a single composed `Gatekeeper` pipeline
- [ ] T0483 Write integration test: a report passes cleanly through all three Gatekeeper stages under normal load
- [ ] T0484 Write integration test: a report is correctly rejected/blocked at each stage under simulated abuse conditions

### I.8 Mandatory JSON Report Files
- [ ] T0485 Implement `declaration_<game_id>.json` builder (teams, members, repos, hardware, model, commit hash, budgets)
- [ ] T0486 Implement `config_<game_id>_g<NN>.json` builder (locked match configuration snapshot)
- [ ] T0487 Implement `log_<game_id>_g<NN>.json` builder (full move-by-move commit/reveal log)
- [ ] T0488 Implement `result_<game_id>.json` builder (final score, sign-off, all four repo cross-links, token totals)
- [ ] T0489 Write unit test: each of the four JSON builders produces schema-valid output
- [ ] T0490 Write unit test: `game_id` and sub-game number consistently namespace all four files so they never mix across matches
- [ ] T0491 Implement canonical JSON serialization consistently across all four file types
- [ ] T0492 Implement inclusion of the SHA-256 of the match log inside the results report
- [ ] T0493 Implement inclusion of total LLM token consumption inside the results report
- [ ] T0494 Implement mutual sign-off logic: both sides must agree on the score before either sends its report
- [ ] T0495 Write integration test: a disagreement in final score between the two sides is detected and handled (e.g., flagged, not silently sent)
- [ ] T0496 Implement attaching the results JSON as an email attachment (not inline free text)
- [ ] T0497 Write unit test: attempting to send a non-JSON/free-text report is rejected by the sending code path itself

### I.9 Stage-7 Milestone
- [ ] T0498 Confirm milestone: a match summary is sent via Gmail successfully from both sides independently
- [ ] T0499 Confirm milestone: the GUI shows live match state correctly throughout a full match
- [ ] T0500 Confirm milestone: the Replay App replays a captured match correctly with Verified OK stamps
- [ ] T0501 Run a full end-to-end match: crypto + scent + LLM + GUI + Gmail reporting all active simultaneously
- [ ] T0502 Document Stage-7 decisions in `PRD/07-reporting-gui.md`

---

## J. Reliability Layer — Orchestrator, State Machine, Watchdog, Deadline Tracker

### J.1 Orchestrator (Gateway)
- [ ] T0503 Design the single `Orchestrator` class as the sole entry point for all sub-systems
- [ ] T0504 Wire the MCP connector module behind the Orchestrator (no direct external access from other modules)
- [ ] T0505 Wire the Decision Module (strategy) behind the Orchestrator
- [ ] T0506 Wire the Log Manager behind the Orchestrator
- [ ] T0507 Wire the Deadline Tracker behind the Orchestrator
- [ ] T0508 Wire the Watchdog behind the Orchestrator
- [ ] T0509 Verify the Orchestrator itself contains no decision-making or communication business logic
- [ ] T0510 Write unit test: replacing the Decision Module implementation requires no changes to the Orchestrator interface
- [ ] T0511 Write architecture-review checklist: confirm no module calls another module directly, bypassing the Orchestrator
- [ ] T0512 Document the Orchestrator's public interface (methods, expected inputs/outputs)

### J.2 Legal State Machine
- [ ] T0513 Define the full state set: WAITING_FOR_OPPONENT, COMPUTING_MOVE, COMMITTING, AWAITING_REVEAL, VERIFYING, TECHNICAL_LOSS
- [ ] T0514 Implement the transition table mapping each state to its legal successor states
- [ ] T0515 Implement `transition(target)` raising/rejecting on any transition not in the table
- [ ] T0516 Write unit test: every legal transition succeeds
- [ ] T0517 Write unit test: every illegal transition attempt is rejected immediately
- [ ] T0518 Write unit test: `TECHNICAL_LOSS` is correctly reachable from both `COMPUTING_MOVE` and `AWAITING_REVEAL` failure paths
- [ ] T0519 Write unit test: `TECHNICAL_LOSS` is a terminal state (no further legal transitions out)
- [ ] T0520 Wire the state machine's current state to the GUI turn-banner (Stage 7)
- [ ] T0521 Write integration test: a full match cycles through the state machine correctly turn after turn
- [ ] T0522 Write integration test: an opponent disconnect mid-`AWAITING_REVEAL` correctly drives the state machine to `TECHNICAL_LOSS` rather than hanging

### J.3 Deadline Tracker
- [ ] T0523 Implement per-outbound-request timestamp + deadline attachment
- [ ] T0524 Implement deadline-expiry checking on every awaited response
- [ ] T0525 Implement retry-on-expiry logic (bounded by `max_retries`)
- [ ] T0526 Implement technical-loss/timeout declaration once retries are exhausted
- [ ] T0527 Write unit test: a response arriving within the deadline is accepted normally
- [ ] T0528 Write unit test: a response arriving after the deadline triggers retry or timeout handling, never an indefinite wait
- [ ] T0529 Wire `response_timeout_sec` from config into the Deadline Tracker
- [ ] T0530 Write integration test: simulated slow/no-response opponent triggers correct timeout behavior without hanging the process

### J.4 Watchdog
- [ ] T0531 Implement a background heartbeat-monitoring process/thread independent of the main game loop
- [ ] T0532 Implement `watchdog_check(last_heartbeat, timeout_sec)` comparing elapsed time to threshold
- [ ] T0533 Implement `persist_state()` saving current game state to disk for later recovery
- [ ] T0534 Implement `controlled_shutdown()` releasing MCP connections and closing logs cleanly
- [ ] T0535 Wire `watchdog_timeout_sec` from config into the Watchdog
- [ ] T0536 Write unit test: Watchdog returns ALIVE when heartbeats are timely
- [ ] T0537 Write unit test: Watchdog returns SHUTDOWN and persists state when heartbeats stop arriving
- [ ] T0538 Implement the main loop emitting a heartbeat signal on a regular cadence
- [ ] T0539 Write integration test: deliberately freezing the main loop triggers Watchdog-initiated state persistence and shutdown
- [ ] T0540 Implement a state-recovery/resume path that can reload persisted state after a controlled shutdown

### J.5 Deadlock Prevention Review
- [ ] T0541 Conduct a manual deadlock-risk review across all await points in the codebase
- [ ] T0542 Confirm every await point has either a Deadline Tracker timeout or is bounded by the state machine
- [ ] T0543 Write a stress test: simulate simultaneous mutual-wait conditions and confirm no permanent hang occurs
- [ ] T0544 Document the deadlock-prevention design in the architecture section of the README

---

## K. Configuration Files — Full JSON/TOML Implementation

### K.1 Shared Signed Config (`config/game.json`)
- [ ] T0545 Finalize the full `config/game.json` schema covering all sections (board_and_agents, world, movement_and_barriers, scoring, pheromones, network_and_league, rate_limiter_gatekeeper)
- [ ] T0546 Implement `schema_version` field and version-compatibility check
- [ ] T0547 Implement `agreed_between` field listing both team identities
- [ ] T0548 Write a validation function checking all mandatory fields are present
- [ ] T0549 Write a validation function checking all minimum-value constraints (e.g., `max_barriers >= 14`)
- [ ] T0550 Implement byte-for-byte equality check between the two sides' loaded config (hash comparison)
- [ ] T0551 Write unit test: mismatched configs between sides are detected and block match start
- [ ] T0552 Implement a config-negotiation handshake exchanged before Step-0 (both sides propose/confirm identical values)
- [ ] T0553 Write integration test: two independently-authored config files that differ trigger a pre-match rejection, not silent divergence
- [ ] T0554 Add `config_sha256` computation over the canonical serialized config
- [ ] T0555 Write unit test: `config_sha256` is identical when computed independently by both sides on the same content

### K.2 Private Per-Peer Config (`config/game.toml`)
- [ ] T0556 Finalize the `[game]` section: group_name, group_id, sub_game_number, members, repos
- [ ] T0557 Finalize the `[network]` section: my_port, opponent_url, turn_timeout_seconds
- [ ] T0558 Finalize the `[strategy]` section: thief_class, police_class (optional overrides)
- [ ] T0559 Finalize the `[trash_talk]` section: provider selection
- [ ] T0560 Finalize the `[llm]` section: model, step_deadline_seconds
- [ ] T0561 Finalize the `[email]` section: recipient, mode
- [ ] T0562 Write unit test: all optional sections have sane defaults when omitted
- [ ] T0563 Write unit test: TOML parse errors produce a clear, actionable error message
- [ ] T0564 Confirm no value in the private TOML ever needs to match the opponent's TOML (spot-check review)

### K.3 Rate-Limiter Config (`rate_limits.json`)
- [ ] T0565 Finalize `rate_limits.json` schema (requests_per_minute, concurrent_requests, retry_backoff_sec, max_retries, queue_depth)
- [ ] T0566 Wire this config into the Gatekeeper's Token-Bucket and Quota Manager
- [ ] T0567 Write unit test: rate-limit config values are correctly loaded and applied

### K.4 Config Loader Robustness
- [ ] T0568 Implement a single unified config-loading entry point used consistently across the whole codebase
- [ ] T0569 Write unit test: loader raises a clear error on missing files rather than a generic exception
- [ ] T0570 Write unit test: loader raises a clear error on malformed JSON/TOML syntax
- [ ] T0571 Add environment-variable overrides for local development convenience (never overriding shared/signed values)
- [ ] T0572 Document every config field's meaning, default, and status (minimum/fixed/by-agreement) in a local reference table matching App. F
- [ ] T0573 Cross-check every config field against the Mandatory Parameters Table for completeness (no missing parameter)
- [ ] T0574 Cross-check every config field against the 55 mandatory rules for any crypto-locking or declaration requirements

---

## L. League Operations & Live Matches

### L.1 Pre-Match Coordination With Opponent Teams
- [ ] T0575 Identify at least two other teams to arrange live matches against
- [ ] T0576 Exchange public tunnel URLs with each opposing team ahead of a scheduled match
- [ ] T0577 Exchange/agree on `config/game.json` values with each opponent before match start
- [ ] T0578 Confirm both sides' `config_sha256` match before proceeding to Step-0
- [ ] T0579 Exchange Step-0 declarations with each opponent and verify signatures
- [ ] T0580 Exchange each side's already-played-games count before every match (diversity/fairness declaration)
- [ ] T0581 Write down/record the agreed game-count declaration for later audit cross-checking
- [ ] T0582 Schedule a specific time window with each opposing team for the live match

### L.2 Running Matches
- [ ] T0583 Start both agents' processes and confirm both tunnels are live before match start
- [ ] T0584 Run a warm-up (non-counted) game against a new opponent first, per team preference
- [ ] T0585 Run the first counted game against Opponent Team 1
- [ ] T0586 Confirm both sides' end-of-match JSON reports were sent and received
- [ ] T0587 Run a counted game against Opponent Team 2 (a different team, per the diversity rule)
- [ ] T0588 Confirm both sides' end-of-match JSON reports were sent and received for match 2
- [ ] T0589 If time allows, run additional counted games against further distinct opponents (up to `[max games per team]`)
- [ ] T0590 Track a running tally of games played vs. `[min games to pass]` and `[max games per team]`
- [ ] T0591 Confirm at least `[min games to pass]` distinct-opponent games are completed before the submission deadline
- [ ] T0592 Avoid re-playing already-completed counted opponents purely for extra scoring (respect the one-counted-game-per-opponent rule)
- [ ] T0593 Record final scores from every counted match for the academic README's results summary

### L.3 Handling League-Level Failures
- [ ] T0594 Define a procedure for what happens if an opponent's tunnel is down at match time (reschedule)
- [ ] T0595 Define a procedure for what happens if a match ends in a technical loss due to your own bug (fix and re-arrange if time permits)
- [ ] T0596 Define a procedure for handling a suspected false game-count declaration from an opponent (document and flag, do not unilaterally retaliate)
- [ ] T0597 Keep a log of all attempted/aborted matches (not just successful ones) for your own troubleshooting history

### L.4 Tie & Edge-Case Handling
- [ ] T0598 Write integration test: a tied cumulative score across a full series correctly awards `[tie score]` to both sides
- [ ] T0599 Write integration test: exactly reaching `[max games per team]` correctly stops further counted games
- [ ] T0600 Write integration test: exactly reaching `[min games to pass]` correctly marks the team as eligible
- [ ] T0601 Verify scoring computation correctly separates counted games from warm-up games in all reporting

---

## M. Testing & Quality Assurance

### M.1 Unit Test Coverage
- [ ] T0602 Set up `pytest` configuration (`pytest.ini`/`pyproject.toml` test section) for both repos
- [ ] T0603 Achieve unit test coverage for the board/movement/barrier module
- [ ] T0604 Achieve unit test coverage for the scoring module
- [ ] T0605 Achieve unit test coverage for the scent/pheromone module
- [ ] T0606 Achieve unit test coverage for the belief-map module
- [ ] T0607 Achieve unit test coverage for the strategy/decision module
- [ ] T0608 Achieve unit test coverage for the commit-reveal cryptography module
- [ ] T0609 Achieve unit test coverage for the state-machine module
- [ ] T0610 Achieve unit test coverage for the Deadline Tracker
- [ ] T0611 Achieve unit test coverage for the Watchdog
- [ ] T0612 Achieve unit test coverage for the Gatekeeper (Quota Manager, Token Bucket, DOS Detector)
- [ ] T0613 Achieve unit test coverage for the config loaders (JSON + TOML)
- [ ] T0614 Achieve unit test coverage for the Gmail-sending wrapper (mocked API)
- [ ] T0615 Achieve unit test coverage for the Replay Viewer's verification engine
- [ ] T0616 Set up a coverage report tool (`pytest-cov` or similar) and record baseline coverage percentage
- [ ] T0617 Add tests to CI or a pre-push local hook so regressions are caught early

### M.2 Integration Tests
- [ ] T0618 Write an integration test running a full localhost match end-to-end (both processes) with assertions on final score
- [ ] T0619 Write an integration test running a full match with tunneling active (or a mocked equivalent) end-to-end
- [ ] T0620 Write an integration test exercising a full commit-reveal cycle across real network calls
- [ ] T0621 Write an integration test exercising a full Gmail report round-trip against a real test inbox
- [ ] T0622 Write an integration test for a simulated opponent disconnect mid-match
- [ ] T0623 Write an integration test for a simulated slow/laggy opponent exceeding deadlines
- [ ] T0624 Write an integration test for a simulated malformed/hostile payload from the opponent
- [ ] T0625 Write an integration test for a full match with the LLM verbal layer active (real or mocked provider)
- [ ] T0626 Write an integration test verifying the GUI, Replay Viewer, and Gmail reporting all function together in one full run

### M.3 Adversarial / Red-Team Testing (self-testing your own integrity mechanisms)
- [ ] T0627 Attempt to submit a false Capture Claim and confirm it is caught by audit
- [ ] T0628 Attempt to hide a barrier placement and confirm it is caught by audit/log completeness checks
- [ ] T0629 Attempt to alter a move after Commit but before Reveal and confirm it is rejected
- [ ] T0630 Attempt to replay an old Nonce and confirm uniqueness/freshness is enforced
- [ ] T0631 Attempt to tamper with a saved log file and confirm the Replay Viewer flags it as TAMPERED
- [ ] T0632 Attempt to send a non-JSON free-text report and confirm it is rejected before sending
- [ ] T0633 Attempt to exceed the Gmail rate limit deliberately and confirm the Gatekeeper throttles correctly
- [ ] T0634 Attempt an illegal diagonal move and confirm it is rejected at every layer (client, protocol, audit)
- [ ] T0635 Attempt to falsely declare a lower games-played count and confirm your own system would detect the inconsistency if checked against your own logs
- [ ] T0636 Attempt to exceed `max_barriers` and confirm placement is blocked
- [ ] T0637 Attempt to share state between cop and thief processes deliberately (as a negative test) and confirm your architecture makes this structurally impossible, not just discouraged

### M.4 Performance & Load Testing
- [ ] T0638 Measure end-to-end turn latency (compute + network + crypto) under normal conditions
- [ ] T0639 Measure LLM call latency for each configured provider mode
- [ ] T0640 Measure the impact of `every_n_steps` throttling on overall match duration
- [ ] T0641 Measure memory usage over a long match (many turns) to catch leaks
- [ ] T0642 Stress-test the Gatekeeper under a burst of simulated report requests
- [ ] T0643 Stress-test the belief-map update function for computational cost at larger board sizes (if team increases grid size)
- [ ] T0644 Profile and optimize any function exceeding `step_deadline_seconds` under normal load

### M.5 Cross-Platform / Environment Testing
- [ ] T0645 Test the full pipeline on the primary development OS
- [ ] T0646 Test the full pipeline on a second OS if available (e.g., Windows vs. Linux/Mac) to catch path/encoding bugs
- [ ] T0647 Test with a fresh virtual environment (no leftover cached dependencies) to confirm reproducibility from `requirements.txt`/`pyproject.toml`
- [ ] T0648 Test the OAuth flow from a completely fresh machine/browser profile
- [ ] T0649 Verify no hardcoded absolute file paths remain anywhere in the codebase

### M.6 Regression Testing After Each Stage
- [ ] T0650 Re-run Stage 1-3 tests after Stage 4 changes to confirm no regression
- [ ] T0651 Re-run Stage 1-4 tests after Stage 5 changes to confirm no regression
- [ ] T0652 Re-run Stage 1-5 tests after Stage 6 changes to confirm no regression
- [ ] T0653 Re-run Stage 1-6 tests after Stage 7 changes to confirm no regression
- [ ] T0654 Run the full test suite one final time immediately before tagging the submission

### M.7 Manual QA Pass
- [ ] T0655 Manually play through a full match end-to-end, observing the GUI in real time
- [ ] T0656 Manually inspect a full generated match log for readability and completeness
- [ ] T0657 Manually inspect a generated results JSON for correctness of every field
- [ ] T0658 Manually inspect the received Gmail report in an actual inbox
- [ ] T0659 Manually verify the Replay Viewer against the exact match just played
- [ ] T0660 Have your teammate independently attempt to run your side's agent from a clean checkout, following only the README

---

## N. Documentation & Academic Report

### N.1 README.md — Academic Report (both repos)
- [ ] T0661 Write the Dec-POMDP model section: state, action, observation spaces as implemented
- [ ] T0662 Write the FastMCP orchestration dilemmas section: turn management, network-failure handling
- [ ] T0663 Write the decision-mechanism section: heuristics/custom algorithm/RL details and parameters chosen
- [ ] T0664 Write the Gatekeeper/Orchestrator role and parameter-choice discussion
- [ ] T0665 Include learning-curve plots if RL was used, with a caption explaining convergence behavior
- [ ] T0666 Insert the mandatory belief-heatmap GUI screenshot
- [ ] T0667 Insert the mandatory Replay Viewer "Verified OK" screenshot
- [ ] T0668 Insert the cross-link to the sibling repository (cop <-> thief)
- [ ] T0669 Write a section explaining the scent/pheromone model and how uncertainty/deception were combined
- [ ] T0670 Write a section summarizing league results (games played, opponents faced, final scores)
- [ ] T0671 Write a section documenting any book-contradiction interpretation choices made per the academic-freedom clause
- [ ] T0672 Proofread the README for clarity, spelling, and academic tone
- [ ] T0673 Verify the README renders correctly on GitHub's web UI (formatting, images, links)

### N.2 PRD Files (7 layers)
- [ ] T0674 Finalize `PRD/01-base-logic.md`
- [ ] T0675 Finalize `PRD/02-mcp-infra.md`
- [ ] T0676 Finalize `PRD/03-strategy-module.md`
- [ ] T0677 Finalize `PRD/04-language-scent.md`
- [ ] T0678 Finalize `PRD/05-cloud-tunnel.md`
- [ ] T0679 Finalize `PRD/06-security-crypto.md`
- [ ] T0680 Finalize `PRD/07-reporting-gui.md`
- [ ] T0681 Cross-reference each PRD file from the README's table of contents

### N.3 Supporting Documents
- [ ] T0682 Finalize `PLAN.md` describing the work plan and division of labor between teammates
- [ ] T0683 Finalize `TODO.md` (repo copy) reflecting actual completed/outstanding tasks at submission time
- [ ] T0684 Write `docs/RESEARCH-REPORT-Performance-Analysis.md` covering resource consumption analysis
- [ ] T0685 Include LLM call counts/costs per provider in the research report
- [ ] T0686 Include rate-limit comparisons across providers (Ollama, ChatGPT, Gemini, Claude, Grok) in the research report
- [ ] T0687 Include a discussion of the fallback mechanism's effectiveness in the research report
- [ ] T0688 Write `SETUP.md` describing full environment setup from a clean machine
- [ ] T0689 Write a `RUNBOOK.md` describing how to run a live match against another team step by step

### N.4 Code-Level Documentation
- [ ] T0690 Add docstrings to every public class and function in the domain layer
- [ ] T0691 Add docstrings to every public class and function in the infra layer
- [ ] T0692 Add docstrings to every public class and function in the shared layer
- [ ] T0693 Add inline comments explaining non-obvious cryptographic steps
- [ ] T0694 Add inline comments explaining the scent decay formula implementation
- [ ] T0695 Generate/update an architecture diagram reflecting the final Orchestrator + module structure
- [ ] T0696 Review all comments/docstrings for accuracy against the final implementation (no stale documentation)

---

## O. Submission Preparation & Compliance

### O.1 Repository Finalization
- [ ] T0697 Confirm both repos are reachable by the lecturer (public or explicitly shared)
- [ ] T0698 Confirm the cross-link between cop and thief README files is correct and working
- [ ] T0699 Run a final `.gitignore` audit: confirm `credentials.json` and `token.json` were never committed in history
- [ ] T0700 If a secret was ever accidentally committed, rotate/revoke it in the Google Cloud console
- [ ] T0701 Confirm no other secrets (API keys, personal tokens) exist anywhere in tracked files
- [ ] T0702 Squash/clean up any messy work-in-progress commits if desired (optional, not required)
- [ ] T0703 Confirm both repos contain README, config files, PRD files, PLAN file, and TODO file(s) at minimum

### O.2 Git Tagging
- [ ] T0704 Create annotated Git tag `v1.0-submission` on the cop repo's final commit
- [ ] T0705 Create annotated Git tag `v1.0-submission` on the thief repo's final commit
- [ ] T0706 Push both tags to their respective remotes
- [ ] T0707 Verify `git show v1.0-submission` resolves to the intended final commit on both repos
- [ ] T0708 Record both tags' commit hashes for inclusion in the final Step-0/declaration data

### O.3 Team Identity & Individual Submission
- [ ] T0709 Finalize the 8-character team identity code (no spaces)
- [ ] T0710 Confirm the team code is embedded consistently across declaration/config/result JSON files
- [ ] T0711 Each team member prepares their own individual submission package
- [ ] T0712 Each team member independently submits via the course's official submission system
- [ ] T0713 Confirm the shared code repo links are identical across every team member's individual submission

### O.4 Word/PDF Submission Document
- [ ] T0714 Obtain the official Word submission template
- [ ] T0715 Fill in all required template fields without moving/renaming any field
- [ ] T0716 Paste/insert the finalized README content (or summary) into the template as instructed
- [ ] T0717 Insert the belief-heatmap GUI screenshot into the template
- [ ] T0718 Insert the Replay Viewer "Verified OK" screenshot into the template
- [ ] T0719 Insert both GitHub repo links into the template
- [ ] T0720 Export the completed template to PDF
- [ ] T0721 Proofread the exported PDF for layout corruption (images cut off, fields misaligned)
- [ ] T0722 Confirm the PDF file naming convention matches what the course submission system expects
- [ ] T0723 Submit the PDF via the official course submission channel

### O.5 Final Compliance Cross-Check Against the 55 Mandatory Rules
- [ ] T0724 Re-verify rule set 1-10 (network architecture & local epistemology) against the final code
- [ ] T0725 Re-verify rule set 11-16 (spatial mechanics & board) against the final code
- [ ] T0726 Re-verify rule set 17-24 (cryptography & zero-knowledge) against the final code
- [ ] T0727 Re-verify rule set 25-30 (strategy, language & public network) against the final code
- [ ] T0728 Re-verify rule set 31-45 (league fairness & admin procedures) against the final code
- [ ] T0729 Re-verify completions 46-55 (cross-checked additions) against the final code
- [ ] T0730 Re-verify every entry in the Mandatory Parameters Table matches the final `config/game.json`
- [ ] T0731 Confirm the self-grading submitted reflects code quality only, not league game outcomes

### O.6 Final Pre-Submission Checklist (Ch.11 restated)
- [ ] T0732 Confirm base logic works: full match runs with no crash and correct scoring
- [ ] T0733 Confirm FastMCP public-URL connectivity between two agents (not localhost-only)
- [ ] T0734 Confirm commit-reveal and mutual audit pass cleanly with no tampering flagged
- [ ] T0735 Confirm scent map and belief map are implemented and actually influence decisions
- [ ] T0736 Confirm Live GUI and Replay Viewer both show correct, matching, "Verified OK" state
- [ ] T0737 Confirm both sides sent their own separate Gmail JSON report for every counted match
- [ ] T0738 Confirm GitHub repos are tagged and README is properly structured
- [ ] T0739 Confirm at least `[min games to pass]` distinct-opponent games were completed
- [ ] T0740 Do a final full read-through of `requirements.md` against the finished project, line by line

---

## P. Polish, Performance & Final Research Pass

### P.1 Code Quality Polish
- [ ] T0741 Run the full linter across both repos and fix all warnings
- [ ] T0742 Run the formatter across both repos for consistent style
- [ ] T0743 Run the type checker (if used) and resolve all type errors
- [ ] T0744 Remove dead code and unused imports across both repos
- [ ] T0745 Remove any leftover debug print statements not needed for the final submission
- [ ] T0746 Review variable/function naming for clarity and consistency
- [ ] T0747 Refactor any duplicated logic between cop and thief repos into clearly-documented shared reference points (without violating process separation)
- [ ] T0748 Ensure consistent error handling/logging style across all modules

### P.2 Performance Tuning
- [ ] T0749 Profile the full match loop and identify the single slowest step
- [ ] T0750 Optimize the belief-map update function if it is a bottleneck
- [ ] T0751 Optimize LLM call frequency/throttling for a good balance of realism vs. token cost
- [ ] T0752 Confirm the agent operates comfortably within `step_deadline_seconds` under realistic load
- [ ] T0753 Re-run the performance-analysis research report after final optimizations and update its numbers

### P.3 Resilience Hardening
- [ ] T0754 Add a top-level exception handler around the main loop that logs and attempts graceful recovery rather than crashing silently
- [ ] T0755 Add health-check logging every N turns for easier post-match debugging
- [ ] T0756 Verify the agent can recover cleanly from an unexpected process restart mid-match (or fails gracefully with a clear technical-loss record)
- [ ] T0757 Add a "dry run" mode that validates config and connectivity without playing a real scored match

### P.4 Final Review & Sign-Off
- [ ] T0758 Conduct a final joint team review session covering the entire codebase
- [ ] T0759 Conduct a final joint team review session covering the entire README/report
- [ ] T0760 Confirm both teammates independently agree the project is ready for submission
- [ ] T0761 Archive a final local backup copy of both repos and all logs before the submission deadline
- [ ] T0762 Celebrate — submit the project

---

## Q. Risk Register & Edge-Case Hardening

### Q.1 Networking Edge Cases
- [ ] T0763 Handle the case where the opponent's tunnel URL changes mid-session (free ngrok restart)
- [ ] T0764 Handle the case where both agents attempt to bind the same local port accidentally
- [ ] T0765 Handle the case where an MCP call succeeds but the response body is empty/null
- [ ] T0766 Handle the case where the opponent sends a well-formed but semantically invalid move (e.g., referencing a nonexistent cell)
- [ ] T0767 Handle the case where DNS resolution for the opponent's tunnel URL temporarily fails
- [ ] T0768 Handle the case where the opponent's server responds with an unexpected HTTP status code
- [ ] T0769 Handle simultaneous commit attempts from both sides in the same turn window (race condition)
- [ ] T0770 Handle a duplicate message delivery (idempotency check on move/commit handling)

### Q.2 Game-Logic Edge Cases
- [ ] T0771 Handle the thief's starting position being adjacent to a pre-placed barrier zone
- [ ] T0772 Handle the cop attempting to place a barrier on its own starting cell before moving
- [ ] T0773 Handle the case where the thief and cop attempt to occupy the same cell simultaneously via near-simultaneous moves
- [ ] T0774 Handle the case where all remaining cells around the thief become blocked in the same turn the cop moves
- [ ] T0775 Handle a board configuration where `thief_start` and `cop_start` are identical (should be rejected at config-validation time)
- [ ] T0776 Handle barrier placement attempts once `max_barriers` is already exhausted (already covered in C.3, add regression test here)
- [ ] T0777 Handle the very last allowed move at exactly `max_moves` cleanly ending the match
- [ ] T0778 Handle a configuration where `survival_threshold` is greater than `max_moves` (decide and document precedence)

### Q.3 Cryptography Edge Cases
- [ ] T0779 Handle a Nonce collision (extremely unlikely, but confirm the code path detects and regenerates rather than silently accepting)
- [ ] T0780 Handle a Commit message arriving twice (duplicate network delivery) without double-processing it
- [ ] T0781 Handle a Reveal arriving with a Nonce that does not match any prior Commit
- [ ] T0782 Handle a final Audit request arriving before all Reveals have completed
- [ ] T0783 Handle a partial/corrupted log file at Replay-Viewer load time (clear error rather than a crash)
- [ ] T0784 Handle mismatched `schema_version` between the two sides' Step-0 declarations

### Q.4 LLM/Provider Edge Cases
- [ ] T0785 Handle Ollama server not running at all when `ollama` mode is configured
- [ ] T0786 Handle Claude API returning a rate-limit error mid-match
- [ ] T0787 Handle Claude CLI not being authenticated/installed when `claude_cli` mode is configured
- [ ] T0788 Handle an LLM response containing content unsuitable for the hint word-limit (auto-truncate safely)
- [ ] T0789 Handle an LLM response containing accidental raw coordinates (post-filter/sanitize before sending)
- [ ] T0790 Handle a completely empty LLM response (fallback to template text)

### Q.5 Gmail/Reporting Edge Cases
- [ ] T0791 Handle OAuth token expiry with no internet connectivity available to refresh
- [ ] T0792 Handle the lecturer's report inbox rejecting the message (bounced email) - log and alert
- [ ] T0793 Handle a match ending in a technical loss before any real gameplay occurred (still must report correctly)
- [ ] T0794 Handle two matches with the same `game_id` being started in error (collision check on file naming)
- [ ] T0795 Handle a partial send failure (declaration sent, but log/result attachment fails) with a clear retry/resume path

### Q.6 GUI/Replay Edge Cases
- [ ] T0796 Handle the GUI being closed and reopened mid-match without losing live state
- [ ] T0797 Handle the Replay Viewer being pointed at a log from an unrelated/older match version (schema mismatch handling)
- [ ] T0798 Handle extremely long matches (near `max_moves`) rendering smoothly in both GUI and Replay Viewer without slowdown

---

## R. Two-Repo Parity & Cross-Team Consistency Checklist

### R.1 Structural Parity Between Cop and Thief Repos
- [ ] T0799 Confirm both repos follow the same folder layout convention (domain/infra/shared/tests/docs/config/PRD)
- [ ] T0800 Confirm both repos' README files follow the identical required section order
- [ ] T0801 Confirm both repos' `.gitignore` files cover the same secret-file patterns
- [ ] T0802 Confirm both repos' `pyproject.toml`/dependency files are kept in sync where shared libraries are used
- [ ] T0803 Confirm both repos independently pass their own full test suite
- [ ] T0804 Confirm both repos independently start their FastMCP server without depending on the other repo's code
- [ ] T0805 Confirm both repos each ship their own copy of the shared `config/game.json` schema definition (not a symlink to a shared mutable resource)
- [ ] T0806 Confirm both repos' `BrainBase` strategy interfaces expose equivalent extension points

### R.2 Cross-Team Config Agreement Process
- [ ] T0807 Draft a short pre-match checklist to run through with any new opposing team before kickoff
- [ ] T0808 Confirm both teams agree on `grid_size` before match start
- [ ] T0809 Confirm both teams agree on `axis_origin_corner` and `axis_start_index` before match start
- [ ] T0810 Confirm both teams agree on `max_barriers`, `max_moves`, and `survival_threshold` before match start
- [ ] T0811 Confirm both teams agree on the scoring table values before match start
- [ ] T0812 Confirm both teams agree on pheromone parameters (`scent_center_intensity`, `pheromone_decay`, `pheromone_grid_size`) before match start
- [ ] T0813 Confirm both teams agree on `hint_max_words` and `map_area` before match start
- [ ] T0814 Confirm both teams exchange and verify `config_sha256` before proceeding past Step-0
- [ ] T0815 Log the agreed configuration for every distinct opponent match separately (avoid config drift between matches)

### R.3 Communication Etiquette With Opposing Teams
- [ ] T0816 Establish a shared communication channel (email/chat) with each opposing team for scheduling
- [ ] T0817 Share your public tunnel URL only shortly before the scheduled match window (URLs may rotate)
- [ ] T0818 Confirm receipt of the opposing team's Step-0 declaration before sending your own first real move
- [ ] T0819 Politely flag any detected rule violation to the opposing team and to the lecturer per course policy, rather than silently exploiting it

---

## S. Team Process & Project Management

### S.1 Task Tracking
- [ ] T0820 Set up a shared task board (GitHub Projects, Trello, or similar) mirroring this TODO list
- [ ] T0821 Assign clear ownership (cop side vs. thief side vs. shared infra) between the two teammates
- [ ] T0822 Hold a short recurring sync to review progress against the 7-stage build order
- [ ] T0823 Track blockers explicitly (e.g., "waiting on opponent team's tunnel URL") separate from code tasks
- [ ] T0824 Re-triage this TODO list after each stage milestone, marking completed items and re-prioritizing what's left

### S.2 Time & Scope Management
- [ ] T0825 Estimate a rough calendar date target for completing each of the 7 build stages
- [ ] T0826 Reserve explicit buffer time before the deadline for the league-match scheduling phase (depends on other teams' availability)
- [ ] T0827 Reserve explicit buffer time for OAuth/Gmail setup, which often has unexpected console-configuration friction
- [ ] T0828 Reserve explicit buffer time for writing the academic README, which should not be rushed at the very end
- [ ] T0829 Identify which optional/recommended items (RL, custom algorithm, advanced GUI polish) are stretch goals vs. must-haves for your team

### S.3 Knowledge Sharing Between Teammates
- [ ] T0830 Ensure both teammates understand the full commit-reveal protocol, not just whoever implemented it
- [ ] T0831 Ensure both teammates understand the Orchestrator/state-machine architecture
- [ ] T0832 Ensure both teammates can independently run and debug the full match pipeline
- [ ] T0833 Pair-review each other's code for the cop vs. thief repo before final submission
- [ ] T0834 Walk through the final academic README together and confirm both teammates agree with every claim in it

---

## T. Final Sanity Sweep — One Task Per Mandatory Rule (App. E cross-check)

- [ ] T0835 Verify rule 1: cop and thief run as two fully separate processes
- [ ] T0836 Verify rule 2: no shared memory/state variables exist between the two sides
- [ ] T0837 Verify rule 3: a single Orchestrator is the entry point for all sub-systems
- [ ] T0838 Verify rule 4: game phases are managed via a legal state machine
- [ ] T0839 Verify rule 5: illegal state transitions are rejected
- [ ] T0840 Verify rule 6: a Deadline Tracker prevents deadlock while awaiting the opponent
- [ ] T0841 Verify rule 7: a Watchdog monitors the main process with controlled data flush
- [ ] T0842 Verify rule 8: the GUI displays only local truth
- [ ] T0843 Verify rule 9: the GUI never displays the full objective board state
- [ ] T0844 Verify rule 10: a tunneling tool exposes the local server publicly
- [ ] T0845 Verify rule 11: the config file is byte-identical on both sides
- [ ] T0846 Verify rule 12: minimum parameter values are never reduced below the floor
- [ ] T0847 Verify rule 13: movement is orthogonal-only
- [ ] T0848 Verify rule 14: illegal moves are never executed
- [ ] T0849 Verify rule 15: every barrier placement is publicly declared
- [ ] T0850 Verify rule 16: barrier placement location is never misrepresented
- [ ] T0851 Verify rule 17: the SHA-256 commit-reveal handshake protocol is used for every move
- [ ] T0852 Verify rule 18: the Nonce stays secret until game end
- [ ] T0853 Verify rule 19: any audit-stage hash mismatch fails the match
- [ ] T0854 Verify rule 20: a replay/audit application exists and works
- [ ] T0855 Verify rule 21: capture claims are announced only when true
- [ ] T0856 Verify rule 22: false capture announcements are structurally impossible to hide from audit
- [ ] T0857 Verify rule 23: the scent-emission-model formula is cryptographically locked before game start
- [ ] T0858 Verify rule 24: a cryptographic Step-0 hardware declaration occurs before game start
- [ ] T0859 Verify rule 25: the LLM is not handed the actual move decision (or deviation is explicitly documented by mutual agreement)
- [ ] T0860 Verify rule 26: free-text communication uses natural language only
- [ ] T0861 Verify rule 27: no direct numeric-coordinate protocol is used in hints
- [ ] T0862 Verify rule 28: a token-bucket rate limiter protects Gmail report sending
- [ ] T0863 Verify rule 29: a DOS/anomaly detector protects network resources
- [ ] T0864 Verify rule 30: the Gmail interface code uses send-only permission scope
- [ ] T0865 Verify rule 31: each team plays the minimum number of games vs. distinct opposing teams
- [ ] T0866 Verify rule 32: every match's results are automatically reported via Gmail
- [ ] T0867 Verify rule 33: the match report is structured as valid JSON
- [ ] T0868 Verify rule 34: no end-of-match report is ever sent as free text
- [ ] T0869 Verify rule 35: both teams agree on the outcome and each sends its own separate report
- [ ] T0870 Verify rule 36: comprehensive mutual log audits occur at the end of every match
- [ ] T0871 Verify rule 37: the number of games already played is precisely declared at the start of every match
- [ ] T0872 Verify rule 38: game counts are never falsely declared to opponents
- [ ] T0873 Verify rule 39: no secrets or credentials are ever pushed to any repo
- [ ] T0874 Verify rule 40: authorization/secret files are listed in `.gitignore`
- [ ] T0875 Verify rule 41: the final submission version is tagged with a documented annotated Git tag
- [ ] T0876 Verify rule 42: a comprehensive academic README report is attached to the repo
- [ ] T0877 Verify rule 43: deliverables are submitted as Word/PDF with the template's field layout unchanged
- [ ] T0878 Verify rule 44: the assignment is submitted as a separate file per team member
- [ ] T0879 Verify rule 45: team identity is encoded as an 8-character unique code without spaces
- [ ] T0880 Verify rule 46: a barrier placed on the cop's own occupied cell counts toward capture at that instant
- [ ] T0881 Verify rule 47: a thief leaving the arena via an illegal move counts as captured
- [ ] T0882 Verify rule 48: every match outcome is scored exactly per the scoring table
- [ ] T0883 Verify rule 49: two separate GitHub repos are submitted with cross-linked READMEs and four cross-links in the submission JSON
- [ ] T0884 Verify rule 50: every repo includes README, config files, PRD files, PLAN file, and TODO files
- [ ] T0885 Verify rule 51: automated end-of-match reports go to the correct lecturer report address
- [ ] T0886 Verify rule 52: each opponent match-up counts only once toward scoring
- [ ] T0887 Verify rule 53: the commit-hash identifier is recorded and updated in every Step-0 declaration
- [ ] T0888 Verify rule 54: the final-results JSON reports total token consumption
- [ ] T0889 Verify rule 55: self-scoring reflects code quality only, not league game outcome

---

**Total task count target: 800-1000.** Run `grep -c '^- \[ \]' docs/TODO.md` (unchecked) and `grep -c '^- \[x\]' docs/TODO.md` (checked) to confirm the live count as tasks are checked off and/or added during development.

**Progress log:**
- Chapter 1 (Dec-POMDP formal model) — 27 tasks checked, 8 newly added (T0890–T0897). See `README.md` for what was executed and why.
