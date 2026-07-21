# Product Requirements Document (PRD)

**Project:** Distributed Cops-and-Robbers over a Peer-to-Peer Network
**Course:** Orchestration of AI Agents — Dept. of Computer Science, University of Haifa
**Sources:** `ref/police_thief_p2p.pdf` (game rulebook, v3.0.0) · `ref/software_submission_guidelines-V3.pdf` (professional software standard, v3.00) · full requirement extraction in `docs/tasks.md` · task breakdown in `docs/TODO.md`
**Status:** Draft v1.0 — pending team approval before development proceeds (per the mandatory workflow in the submission guidelines, §2.5: PRD → PLAN → TODO → per-mechanism PRDs → approval → development)

> This document intentionally does not restate every rule already captured in `docs/tasks.md` (the full rulebook extraction). It defines the **product** built on top of those rules: why it exists, what "done" means, what is and isn't in scope, and what we're assuming/depending on. Where a number or rule is cited, `docs/tasks.md` is the source of truth.

---

## 1. Project Overview & Context

### 1.1 What we are building
A pair of autonomous AI agents — a **Cop** and a **Thief** — that play a pursuit-and-evasion game on a discrete grid, communicating **only** over a peer-to-peer network (no central game server), under partial observability, and under a fully self-enforced cryptographic protocol (no external referee). The two agents are developed and run as **two entirely separate codebases/processes**, each exposing and consuming a FastMCP (Model Context Protocol) interface, and each independently reporting match outcomes by email.

This is not a toy client/server game: it is a **distributed-systems teaching vehicle**. The board-game rules (Ch.1–4 of the rulebook) are the *substrate*; the actual graded subject matter is whether the resulting system demonstrates correct multi-agent coordination, adaptation under uncertainty, cryptographic integrity, and resilient architecture (rulebook Ch.11, the "Four Metrics of Success" — see `docs/tasks.md` §11).

### 1.2 Problem being solved
**Pedagogical problem:** how do you get two mutually distrusting, independently developed AI agents to coordinate a real-time interaction, over the public internet, with no central authority, such that neither can cheat undetected and the system degrades gracefully instead of hanging when the network or an LLM misbehaves?

**Concretely, for the player/agent itself:** the Cop must find a Thief it cannot see, using only its own position, a decaying scent trail, and the Thief's (possibly deceptive) verbal hints; the Thief must survive long enough while evading a cop that is progressively fencing it in with barriers. Both sides must prove, after the fact, that neither cheated — without ever trusting the other's word alone.

### 1.3 Prior art / problem domain (in place of a commercial "market analysis")
This is an academic project, so there is no commercial market to analyze; the guideline's required "market analysis" section is instead a survey of the technical domains this project sits at the intersection of:
- **Decentralized POMDPs** (Dec-POMDP) — multi-agent planning under partial observability (Bernstein et al. 2002; Oliehoek & Amato 2016).
- **Multi-agent orchestration protocols** — MCP (Model Context Protocol), with A2A and ACP as adjacent, non-required protocols (`docs/tasks.md` §3).
- **Stigmergic coordination** — ant-colony pheromone models as a substitute for direct communication (Bonabeau, Dorigo, Theraulaz).
- **Commit-Reveal cryptographic protocols** — trustless commitment schemes (Blum 1983) and Zero-Knowledge proof framing (Goldwasser–Micali–Rackoff 1989).
- **Reliability patterns for distributed systems** — Gatekeeper, Watchdog, Deadline Tracker, Orchestrator/Gateway (Nygard, *Release It!*; Gamma et al., *Design Patterns*).
- **Live, competitive multi-team evaluation** — analogous to game-AI competitions/leagues rather than a fixed offline benchmark.

### 1.4 Target audience / stakeholders
| Stakeholder | Interest |
|---|---|
| Course lecturer / grader | Verifying the four success metrics, reviewing the academic README, running the Replay Viewer against the submitted log |
| Our own two-person team | Building, testing, and jointly understanding the whole system (Ch.9.5/`docs/tasks.md` — both teammates must understand the full commit-reveal and Orchestrator design, not just whoever wrote it) |
| Opposing student teams | Real-time adversaries in the live league; also implicitly co-reviewers, since a rule violation surfaces via mutual audit |
| Future readers of the repo | Anyone using the repo as a reference for distributed multi-agent system design (per the educational-use license on the example repo, `docs/tasks.md` App. D) |

---

## 2. Goals & Success Criteria

### 2.1 Measurable goals (mapped to the rulebook's Four Metrics of Success — `docs/tasks.md` §11.3)
| Goal | Metric | Acceptance criterion |
|---|---|---|
| **Coordination** | Two independent processes complete a full match via FastMCP with no shared memory | A full match runs end-to-end over a public tunnel URL with zero crashes (TODO §D, §G) |
| **Adaptation** | Belief-map convergence under partial observability | In a recorded match, the belief map's `arg max` visibly tracks the true opponent position better than a random baseline over repeated trials (TODO §F.2) |
| **Integrity** | Zero undetected tampering | 100% of committed moves pass mutual SHA-256 audit on an untampered log; a deliberately corrupted log is caught 100% of the time by the Replay Viewer (TODO §H, §I.2) |
| **Architecture** | Resilience under induced failure | Simulated opponent disconnects, dropped tunnels, and LLM-provider outages are handled by Deadline Tracker/Watchdog/fallback without an unhandled crash or silent hang (TODO §J) |

### 2.2 Project-level KPIs
- **Test coverage** ≥ 85% (submission-guidelines requirement, `docs/tasks.md` App. — see `software_submission_guidelines-V3.pdf` §6.2), enforced via `pytest --cov` with `fail_under = 85`.
- **Lint cleanliness**: zero Ruff violations (`ruff check`) on every commit prior to tagging.
- **File-size discipline**: no source file exceeds 150 lines of code (blank/comment lines excluded); split via helper-function extraction, mixin extraction, 50/50 read/write split, or constants extraction when a file grows past the limit.
- **League participation**: ≥ `[min games to pass]` = 2 completed, distinct-opponent, mutually-reported matches (`docs/tasks.md` §9, Table 18).
- **Reporting reliability**: 100% of counted matches produce a JSON Gmail report from *both* sides (a missing report voids that side's credit for the match).

### 2.3 Acceptance criteria for "done" (ties to the Final Pre-Submission Checklist, `docs/tasks.md` §12 / TODO §O.6)
The project is considered feature-complete when all of the following are simultaneously true:
1. A full match runs with no crash and correct scoring, using the exact values in the Mandatory Parameters Table.
2. Both agents connect over public FastMCP URLs (not `localhost`-only).
3. Commit-Reveal + mutual audit passes cleanly on a real recorded match.
4. The scent/belief-map mechanism visibly influences decisions.
5. The Live GUI and Replay Viewer both function and show correct `Verified OK` state.
6. Both sides' Gmail JSON reports were sent and received for every counted match.
7. Both GitHub repos are tagged `v1.0-submission` with the required README structure.
8. At least 2 distinct-opponent league games are completed.
9. The generic software-quality bar is met: 85% coverage, zero lint violations, `docs/PRD.md` + `docs/PLAN.md` + `docs/TODO.md` present and current, secrets never committed.

---

## 3. Functional Requirements

### 3.1 Feature list (mapped to the 7-stage build order — see `docs/PLAN.md` §2 and TODO §C–I)
| # | Feature | Description | Primary spec |
|---|---|---|---|
| F1 | Board & physics engine | Discrete grid, orthogonal movement, barrier placement/budget, capture detection, scoring | `docs/tasks.md` §4 |
| F2 | FastMCP P2P transport | Each agent is simultaneously an MCP server and client; no shared process/memory between roles | `docs/tasks.md` §3 |
| F3 | Strategy module | Pluggable decision "brain" (heuristic / custom / optional RL) producing legal moves only | `docs/tasks.md` §6 |
| F4 | Pheromone scent model | Emission/decay formula producing a symmetric, non-fakeable information channel | `docs/tasks.md` §5 |
| F5 | Natural-language hint layer | Free-text (possibly deceptive) hints, word-limited, LLM-generated (verbal layer only) | `docs/tasks.md` §6.4 |
| F6 | Belief-map reasoning | Bayesian-style probabilistic map over the opponent's location, combining scent + hints | `docs/tasks.md` §6.3 |
| F7 | Public tunneling | Expose local MCP servers via ngrok/Localtonet for real cross-machine play | `docs/tasks.md` §3, §7 |
| F8 | Commit-Reveal crypto protocol | 4-step SHA-256 commitment handshake + Nonce + mutual end-of-match audit | `docs/tasks.md` §6 |
| F9 | Step-0 fairness declaration | Signed hardware + commit-hash + token-budget declaration before first move | `docs/tasks.md` §6.5 (Ch.5.5) |
| F10 | Reliability layer | Orchestrator (single gateway), legal state machine, Deadline Tracker, Watchdog | `docs/tasks.md` §8 |
| F11 | Live GUI | Local-truth-only display: own position, belief heatmap, turn-state banner | `docs/tasks.md` §7 |
| F12 | Replay Viewer | Offline cryptographic re-verification of a completed match log; `Verified OK`/`TAMPERED` stamps | `docs/tasks.md` §7 |
| F13 | Gmail reporting automation | Automated, Gatekeeper-protected JSON report to the lecturer at match end | `docs/tasks.md` §9 |
| F14 | League operations | Multi-opponent match scheduling, diversity/tie scoring, game-count declarations | `docs/tasks.md` §9 |
| F15 | Submission packaging | Two tagged GitHub repos, academic README, PRD/PLAN/TODO docs, Word/PDF submission | `docs/tasks.md` §14, §17 |

### 3.2 User stories
- **As the Cop agent**, I need to place barriers and interpret the Thief's scent trail and verbal hints, so that I can narrow down its location and capture it before running out of moves.
- **As the Thief agent**, I need to evade capture using movement and (optionally) deceptive hints, so that I survive to the survival threshold.
- **As either agent**, I need to cryptographically commit to a move before revealing it, so that neither side can retroactively rewrite history.
- **As either agent**, I need to detect and reject any protocol violation from my opponent (illegal move, false capture claim, tampered log), so that the match is fairly adjudicated with no central referee.
- **As a teammate**, I need a live GUI showing only my own agent's local truth, so that I can observe gameplay without accidentally violating the "no bird's-eye view" rule.
- **As a teammate**, I need a Replay Viewer, so that I can independently verify a completed match's integrity before submitting it as evidence.
- **As the lecturer/grader**, I need an automated Gmail JSON report from each side at match end, so that I have machine-parseable, tamper-evident proof of every league result.
- **As an opposing team**, I need a publicly reachable MCP URL and an agreed, signed config, so that I can play a fair match against this agent without needing to trust its internals.

### 3.3 Key use-case scenarios
1. **Happy path**: two agents complete Step-0, play a full match with several barrier placements, a capture occurs, both sides run mutual audit successfully, both send matching Gmail reports.
2. **Deception scenario**: the Thief sends a false verbal hint; the Cop's belief map (built from scent) contradicts it; the Cop's trust weighting downgrades future hints from that opponent.
3. **Tamper-detection scenario**: a log is deliberately altered post-hoc; the Replay Viewer flags `TAMPERED` and the match is disqualified.
4. **Network-failure scenario**: the opponent's tunnel drops mid-match; the Deadline Tracker times out the pending request and the Watchdog persists state and performs a controlled shutdown rather than hanging indefinitely.
5. **Provider-outage scenario**: the configured LLM provider (Ollama/Claude API/CLI) is unreachable; the system falls back to the zero-token `template` provider rather than crashing the match.
6. **Rate-limit scenario**: many matches complete in quick succession; the Gmail Gatekeeper's token bucket throttles report sending and avoids a Google API `429`.
7. **False-declaration scenario**: an opponent misreports its already-played-game count; this is later caught during cross-team audit and is a disqualifying rule violation for the false-declaring side (not us — but our own declarations must be provably accurate).

---

## 4. Non-Functional Requirements

| Category | Requirement | Source |
|---|---|---|
| **Performance** | Per-turn decision latency stays within `step_deadline_seconds` (default 30s); LLM calls are timeout-bounded | `docs/tasks.md` §6.4, §14 (Table 15/19) |
| **Security** | Commit-Reveal + SHA-256 for every move; least-privilege Gmail OAuth scope (`gmail.send` only); no secrets ever committed to git | `docs/tasks.md` §6, §9, §12 |
| **Reliability** | Deadline Tracker on every network await; Watchdog heartbeat monitoring with controlled shutdown; legal state machine rejecting undefined transitions | `docs/tasks.md` §8 |
| **Availability (of the interaction)** | Public reachability via tunnel for the duration of every scheduled league match | `docs/tasks.md` §3 |
| **Maintainability** | ≤150 LOC/file, SDK-layer architecture, no code duplication (DRY), docstrings on all public functions | `software_submission_guidelines-V3.pdf` §3–4 |
| **Testability** | TDD workflow, ≥85% coverage, unit + integration + adversarial (red-team) test suites | `software_submission_guidelines-V3.pdf` §6; TODO §M |
| **Configurability** | All tunable values loaded from `config/game.json` / `config/game.toml` / `config/rate_limits.json`; zero hardcoded magic numbers in logic | `docs/tasks.md` §13; `software_submission_guidelines-V3.pdf` §7.2–7.3 |
| **Usability** | Live GUI meets basic Nielsen heuristics (status visibility, error prevention, minimalist design); Replay Viewer is independently runnable | `software_submission_guidelines-V3.pdf` §10 |
| **Auditability** | Every match produces a fully reconstructable, independently-verifiable log (`declaration`/`config`/`log`/`result` JSON quartet) | `docs/tasks.md` §9.3.19-21 |
| **Portability** | Runs identically for both team members from a clean checkout following only the README | `software_submission_guidelines-V3.pdf` §13 (ISO/IEC 25010 — Portability) |

---

## 5. Assumptions, Dependencies & Limitations

### 5.1 Assumptions
- Both team members have working Python 3.11+ environments and can each independently run both agent roles locally.
- Opposing teams will, in good faith, attempt Step-0/config negotiation honestly enough to reach a playable match — our system's job is to detect and survive violations, not to prevent teams from attempting them.
- Free-tier `ngrok`/`Localtonet` tunnels, and free/low-tier LLM APIs (Ollama local, or a small Claude model), are sufficient for development, testing, and the live league — we are not budgeting for paid infrastructure beyond incidental API token costs.
- The lecturer's Gmail report address (`docs/tasks.md` §14, Table 20) remains reachable and unchanged for the duration of the course.
- A single shared conceptual design (this PRD/PLAN) can be **duplicated into two independent repos** (cop, thief) without violating the "fully separate processes/no shared memory" rule, since the two repos never import from one another at runtime — only the design documentation is shared during planning.

### 5.2 Dependencies
| Dependency | Purpose | Risk if unavailable |
|---|---|---|
| `fastmcp` (Python) | P2P server/client transport | Blocks all networking (F2) — no known substitute within project scope |
| `ngrok` / `Localtonet` | Public tunnel exposure | Falls back to the alternate provider; if both are down, match cannot be played publicly (local-only fallback for dev/testing) |
| Google Cloud Console + Gmail API + OAuth 2.0 | Automated match reporting | Blocks F13; no manual-reporting fallback is permitted (rule: reports must be automated JSON) |
| An LLM provider: Ollama (local) / Claude API / Claude CLI | Verbal-layer hint generation | Falls back to the zero-token `template` provider automatically (F5 design requirement) |
| GitHub | Code hosting, tagging, submission | Blocks submission entirely; no alternative permitted by course rules |
| `uv` package manager | Dependency management, running code (per `software_submission_guidelines-V3.pdf` §8.4, `pip`/`venv` direct use is forbidden) | Blocks reproducible builds; must be installed |
| Opposing teams' agents | Live league play | Blocks F14; without opponents, minimum-games requirement cannot be met |

### 5.3 Limitations (explicit, by design)
- The LLM is used **exclusively** for the verbal/deception layer; it never decides the physical move (rulebook rule 25 — the one explicitly optional/"recommend" rule; any deviation requires documented mutual agreement between both competing teams, not just our own team's decision).
- The board is a small discrete grid (default 7×7); this is a deliberate design constraint to make brute-force infeasible while keeping heuristic/learning-based play computationally cheap on modest hardware (computational-fairness principle).
- Belief modeling is inherently probabilistic — the system is not expected to achieve perfect opponent localization, only demonstrably-better-than-random convergence.
- Reinforcement learning is **one optional strategy track among several**, not a project requirement; whichever track is chosen, the movement decision must remain deterministic/algorithmic at inference time.
- We do not implement A2A or ACP protocols; MCP/FastMCP is the only required and used P2P transport.
- We are not building our own cryptographic primitives; we rely on the Python standard library's `hashlib`/`secrets` (SHA-256, cryptographically-secure Nonce generation) rather than inventing new cryptography.

### 5.4 Out of scope
- Any GUI/UX polish beyond what is needed to satisfy the local-truth, heatmap, turn-banner, and Replay Viewer requirements (this is not a commercial game UI).
- Support for board sizes, move sets, or scoring schemes below the Mandatory Parameters Table's minimum values (§13/Table 5 in `docs/tasks.md`) — these floors are non-negotiable downward.
- Building a fully generic/pluggable transport layer supporting protocols other than MCP.
- Persisting match history in a database — flat JSON log files are sufficient and match the rulebook's file-based reporting model.
- Supporting more than 2 agents/players in a single match (`num_agents` is fixed at 2 per the rulebook).
- Localization/internationalization of the GUI or hints beyond English (and whatever incidental Hebrew appears in source documentation).

---

## 6. Timeline & Milestones

Mirrors the rulebook's recommended 7-layer incremental build order (`docs/tasks.md` §10) and the project management structure in `docs/TODO.md`. Each milestone gate must be sign-off-confirmed (binary, verifiable) before the next stage begins — see `docs/PLAN.md` §9 for the full engineering plan and `docs/TODO.md` for the granular task checklist behind each milestone.

| Milestone | Deliverable | Gate criterion | TODO section |
|---|---|---|---|
| M0 — Setup | Dev environments, two repos scaffolded, `docs/` structure in place | Both teammates can clone and run a "hello world" MCP exchange | TODO §A–B |
| M1 — Base Logic | Board, movement, barriers, capture, scoring (single process) | Full local match runs with no crash | TODO §C |
| M2 — MCP Infra | Two independent processes over `localhost` FastMCP | Cross-process match completes correctly | TODO §D |
| M3 — Strategy Module | Blind heuristic/algorithmic decision-making | Shortest-path pursuit works with no manual intervention | TODO §E |
| M4 — Language + Scent | Pheromone model, belief map, LLM verbal layer | Full match with real scent + real hints, no crash | TODO §F |
| M5 — Cloud Exposure | Public tunneling, real cross-machine match | Remote-machine match completes correctly | TODO §G |
| M6 — Security & Crypto | Commit-Reveal, Nonce, Step-0 declaration, mutual audit | Full crypto-protected match; tamper-injection test catches disqualification correctly | TODO §H |
| M7 — Reporting & GUI | Live GUI, Replay Viewer, Gmail automation, Gatekeeper | End-to-end match with all subsystems active simultaneously | TODO §I |
| M8 — League Readiness | Reliability layer (Orchestrator/Watchdog/Deadline Tracker) hardened, ≥85% coverage, zero lint violations | Full regression suite passes; adversarial/red-team tests pass | TODO §J, §M |
| M9 — Live League | ≥2 distinct-opponent matches completed and mutually reported | Both sides' Gmail JSON reports received for each counted match | TODO §L |
| M10 — Submission | Tagged repos, academic README, PRD/PLAN/TODO finalized, Word/PDF submitted | Full pre-submission checklist (`docs/tasks.md` §12) passes | TODO §N–O |

Buffer time is explicitly reserved (per `docs/TODO.md` §S.2) for: league-match scheduling (depends on other teams' availability), OAuth/Gmail console setup (frequent source of unexpected friction), and academic-README writing (should not be rushed at the deadline).

---

## 7. Per-Mechanism PRD Documents (required by `software_submission_guidelines-V3.pdf` §2.3)

Per the submission guideline's explicit requirement that *"for every specific algorithm, central mechanism, or complex technical component in the project, a dedicated, separate PRD document must be created,"* the following focused documents are planned (naming convention `docs/PRD_<mechanism>.md`, one per non-trivial subsystem). These are scoped as follow-up documents once this master PRD and `docs/PLAN.md` are approved, and each will contain: a detailed description of the algorithm/mechanism including theoretical background, specific requirements/expected input-output/performance metrics, constraints/limitations/alternatives-considered/rationale, and success criteria/specific test scenarios.

| Planned file | Mechanism covered |
|---|---|
| `docs/PRD_board_physics.md` | Grid, movement, barrier budget, capture/scoring rules (Stage 1) |
| `docs/PRD_fastmcp_networking.md` | P2P transport, server/client duality, tunneling (Stages 2, 5) |
| `docs/PRD_strategy_module.md` | Decision-making brain: heuristic / custom / optional RL track |
| `docs/PRD_pheromone_scent.md` | Scent emission/decay model and belief-map construction (Stage 4) |
| `docs/PRD_commit_reveal_crypto.md` | Commit-Reveal protocol, Nonce handling, Step-0 fairness, mutual audit (Stage 6) |
| `docs/PRD_reliability_layer.md` | Orchestrator, legal state machine, Deadline Tracker, Watchdog |
| `docs/PRD_gui_replay.md` | Live GUI (local truth, heatmap, turn banner) and Replay Viewer (Stage 7) |
| `docs/PRD_gmail_gatekeeper.md` | Automated reporting (Gatekeeper: Quota Manager, Token-Bucket, DOS detector), the four mandatory match JSON reports, and league scoring (Diversity Incentive, tie rule, game caps) (Stage 7, 9) |
| `docs/PRD_interactive_play.md` | Interactive, mode-selectable play mode (Agent vs Agent / Human vs Agent / Human vs Human) — a deliberate addition beyond this rulebook's own scope, added at direct user request |

> **Naming reconciliation note**: `docs/TODO.md` currently references per-stage design notes as `PRD/0X-<name>.md` (following the rulebook's own Ch.10 recommendation for 7 layered PRDs). This master PRD adopts the submission guideline's `docs/PRD_<mechanism>.md` naming convention instead, since it is the more rigorous, generically-applicable standard. When each per-mechanism document above is authored, it supersedes the corresponding `PRD/0X-*.md` reference in `docs/TODO.md`; those TODO line items should be updated to point at the correct `docs/PRD_<mechanism>.md` filename at that time.

---

## 8. Open Questions / Decisions Pending Team Sign-off

- [ ] Final choice of strategy track: pure heuristic vs. custom algorithm vs. optional RL (affects `docs/PRD_strategy_module.md` and `docs/PLAN.md` ADR-010).
- [ ] Whether to run cop/thief Google Cloud projects as one shared OAuth project or two separate ones (affects Gmail setup steps).
- [ ] Confirm final `[game arena]` theme (or empty string) and other "by agreement" parameters before first live match.
- [ ] Confirm ngrok vs. Localtonet as primary tunnel provider for league play (fallback order).
- [ ] Confirm GUI toolkit choice: Tkinter (simpler, stdlib) vs. PyQt/PySide (richer, external dependency).

**Approval:** this PRD must be reviewed and approved by both team members before `docs/PLAN.md` implementation details are finalized and coding begins in earnest (per the mandatory workflow, `software_submission_guidelines-V3.pdf` §2.5).
