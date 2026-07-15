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

**Architecture note (see `docs/PLAN.md` ADR-011):** the cop and thief agents are developed as **one shared package** (`police_thief`), differentiated at runtime via a `--role cop`/`--role thief` flag and separate `config/police/`/`config/thief/` directories, rather than as two duplicated repos from the first commit. This satisfies the rulebook's "no shared runtime state between the two sides" requirement (two OS processes running this package never share memory), while avoiding premature duplication of shared/generic code. The rulebook's mandatory **two separate GitHub repos** deliverable is produced later, at submission time, by exporting this codebase into two tagged repos (tracked in `docs/TODO.md` Section O).

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

**Status:** awaiting review before committing. Next up — Chapter 2 (P2P network architecture & FastMCP).
