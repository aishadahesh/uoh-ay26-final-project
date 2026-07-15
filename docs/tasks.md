# Project Requirements — Distributed Cops-and-Robbers over a Peer-to-Peer Network

**Source documents** (both in `ref/`):
- `police_thief_p2p.pdf` — the full rulebook/guide, v3.0.0 (code sample v3.0.0), Dr. Yoram Raviv Segal, Dept. of Computer Science, University of Haifa, "Orchestration of AI Agents" course, 2026. 143 pages, 11 chapters + 6 appendices (A–F).
- `software_submission_guidelines-V3.pdf` — 39 pages. Its submission-format content (Word/PDF template, per-member individual submission, 8-character team code, "don't move template fields") is reproduced almost verbatim inside `police_thief_p2p.pdf`'s own appendices (C "GitHub submission requirements" and the final checklist in Ch.11). All matching content from it has been folded into the sections below and is flagged **[from submission guidelines]** where relevant.

This document translates and reorganizes **every explicit requirement, formula, table, and rule** found in the source book, chapter by chapter and appendix by appendix — nothing is summarized away. Page/section references to the book are given as `(Ch.X)` / `(App.X)` throughout.

---

## 0. How to Read This Book (mandatory framing rules from the front matter)

Before any technical requirement, the book itself sets ground rules for interpreting itself. These are binding on how you interpret everything else below:

0.1. **Golden rule — nothing is mandatory by default.** All diagrams, illustrations, code excerpts, and narrated scenarios in the book are *illustrations of one way to satisfy a rule*, not the rule itself, **unless a passage is explicitly marked as binding**. Where the book says "there is no other way to do X," that IS binding; where it just shows a diagram/example, it is not, by itself.
0.2. **The only unconditional source of binding numeric values is the Mandatory Parameters Table** (App. F / §14 below). Values there may only be *raised*, never lowered, unless marked "by agreement," in which case both teams must agree and the value becomes binding for that match once written into the shared signed config.
0.3. **"Do this" vs "you may do this" is distinguished explicitly** throughout the book using bracketed emphasis: **Do** = mandatory obligation; **Recommend** = optional, encouraged; a plain statement is only binding if the book states so explicitly. If a rule says "no central rule forbids X," teams are free to agree bilaterally to allow X (as long as it doesn't contradict the Mandatory Parameters Table).
0.4. **Academic freedom in case of contradiction.** If you find an apparent contradiction between two places in the book, you may pick either reading and proceed — but you must **explicitly document in your report** where the contradiction was and which reading you chose and why. This choice will not count against you, but silence about a known contradiction might.
0.5. **No external judge, no central authority, ever.** There is no central server that holds "the truth" and adjudicates disputes; ground truth is built bottom-up from cryptographic proof between two mutually-distrusting rivals who must nonetheless prove the mathematics to each other. This is the central design constraint driving the entire rulebook: *coordination without control, trust without a central authority, and grounded decision-making under fog of information.*
0.6. **Why such strict rules exist:** the rules in this book are described as "iron laws," precisely *because* the crypto protocol is rigid, the JSON schema is exact, and there are no time-window tolerances for handshakes — this scaffolding exists specifically to maximize your **freedom to innovate inside the frame** (strategy, spatial engineering, architecture). Details matter enormously; that rigor is what unlocks creative freedom elsewhere.
0.7. Bracketed terms like `[board size]` appearing throughout the prose are **placeholder names**, not literal numbers — the actual value always lives in the Mandatory Parameters Table (App. F / §14). One placeholder token can combine data from more than one place in the book; each side must know precisely which numeric value maps to which placeholder token (only example values are shown inline).
0.8. **Key terms glossary** (non-exhaustive, from the book's front matter): Dec-POMDP · multi-agent distributed system · symmetry between agents · FastMCP · Model Context Protocol · P2P (peer network) · ngrok tunneling · dynamic pheromones and scent decay · ant colony collective memory · Commit-Reveal · Bayesian belief map · Zero-Knowledge · SHA-256 · Reveal · Manhattan distance heuristic · LLM prompt engineering & strategy · reinforcement learning (optional tool) · Token bucket · Gatekeeper · Watchdog · Orchestrator · state machines · replay simulator · computational fairness · OAuth 2.0 · Gmail API.

---

## 1. Chapter 1 — Theoretical Framework & Problem Modeling (Dec-POMDP)

**Chapter goal (explicit):** by the end of this chapter you must understand: (a) why a cop-vs-robber chase is *not* a single-agent problem but a multi-agent one; (b) how to model a competitive environment under partial observability using the Dec-POMDP formalism; (c) what each of the 8 tuple components means concretely, from the current state to the discount horizon.

### 1.1 From Single Agent to Orchestration
1.1.1. You must move your mental model **from "training one static agent"** (agent trained against a static, non-adaptive environment) **to "distributed multi-agent orchestration"** — here, the world itself is another thinking rival: the thief plans, deceives, and reads the board while the cop tries to reason about where it is.
1.1.2. Your architecture must be judged as a **multi-agent orchestration**, not a single "brain."

### 1.1.3 Sharp Distinction — Prompt Chaining vs. Multi-Agent Orchestration
- **Prompt Chaining** = writing the output of one LLM call as the literal input to the next, in a fixed, pre-written linear sequence. There is **no** dynamic work division, no bidirectional context-sharing, no shared-state management — just a one-directional pipeline.
- **Multi-Agent Orchestration** = managed distributed work division: context-sharing, shared state management among agents operating in parallel. **This is what your project must be** — it is **strongly recommended** to review the survey of frameworks/protocols this refers to.
- **Three critical failure patterns of multi-agent orchestration you must know to avoid**:
  1. **Task Duplication** — two or more agents perform the same work, wasting tokens/compute and duplicating output.
  2. **Contradictory Outputs** — agents reach conflicting conclusions with no reconciliation mechanism, leaving the system without a coherent decision.
  3. **Convergence Failure / Infinite Loops** — the system never converges on a solution; it loops absorbing responses without termination.

### 1.2 The Dec-POMDP Formalism
1.2.1. **You must model the environment as a Dec-POMDP** — Decentralized Partially Observable Markov Decision Process, extending the classical single-agent POMDP to multiple decentralized decision-makers under critical uncertainty.
1.2.2. **The full ordered tuple, all 8 components mandatory to understand and reflect in your design:**

`⟨ n, S, {Ai}, P, R, {Ωi}, O, γ ⟩`

| Symbol | Name | Meaning | Practical implication |
|---|---|---|---|
| `n` | number of agents | `n = 2` (cop, thief) | Every decision is a rational binary interaction, not against a random nature |
| `S` | state space | Full world snapshot: exact coordinates of both agents + static barrier layout + the dynamic scent-trail network at every step | Combinatorially huge — brute-force search over `S` is *not viable*; you must use heuristics/learning (Ch.6) |
| `{Ai}` | action space | Combines: physical movement, construction actions (placing barriers), and communicative actions (natural-language hints, which may be lies) | Action space mixes physics *and* psychology |
| `P` | transition function `P(s' \| s, a1, a2)` | Determines how the world changes given both agents' joint actions | No central server exists — **both sides must agree on and encode the exact same transition function** in the shared config |
| `R` | reward function | Feeds the algorithm's learning signal | Maps directly to the Scoring Table (§3.5 / Table 2 below) |
| `{Ωi}, O` | observation space & function | What each agent's sensors actually capture: neither agent ever sees the opponent; each sees only its own scent + the opponent's (possibly false) verbal hint | This is why each side needs its own belief map (Ch.4/Ch.6) |
| `γ ∈ [0,1)` | discount factor | How much future matters vs. present | High `γ` encourages strategic patience (e.g., building a barrier trap over many turns) |

1.2.3. **Practical note on `S`:** the state space is exponential in board size and number of moves; this is a deliberate, load-bearing design decision that *forces* your team toward heuristics or learning-based algorithms rather than exhaustive search (Ch.6).

### 1.3 Uncertainty as a Resource, Not Just an Obstacle
1.3.1. Partial observability is not merely a limitation to model — the same fog that hampers the cop is also the thief's shield, and vice versa (fully symmetric).
1.3.2. Since there is no central server, either side can exploit the observation channel actively: send a deceptive verbal hint, feint the opponent, or hide behind a barrier — these are all legitimate active uses of the observation function `O`.
1.3.3. **The one honest, non-fakeable observation channel is scent** (natural, physical, cannot be suppressed or willfully redirected) — as opposed to verbal hints, which can always be lies. Design your belief-update logic to reflect this asymmetry in trustworthiness between scent (Ch.4) and hints (Ch.6).
1.3.4. Chapter thesis to internalize: whoever reasons correctly about information under uncertainty wins the match — not whoever has the most raw data.

---

## 2. Chapter 2 — P2P Distributed Network Architecture & FastMCP

**Chapter goal (explicit):** by the end you must understand why full decentralization of state management eliminates the need for a central judge; how the MCP protocol + FastMCP let every agent be simultaneously a server and client; why exposing a server via a tunnel (e.g. ngrok) to the public internet is required, and why total separation of the two roles' working environments is a hard requirement of legality, not just a suggestion.

### 2.1 The Paradigm Shift to Full Decentralization
2.1.1. Traditional architectures center a **Game Server** holding "ground truth," resolving disputes, and updating clients. **This project explicitly removes that role entirely.**
2.1.2. Under **P2P (Peer-to-Peer)**, each peer keeps only its **local truth**. Neither side trusts the other's claims; every claim about the opponent's moves must be independently verified via cryptographic signatures (Ch.5).
2.1.3. **[MUST]** No central server may exist. Removing the single point of both failure and trust is the entire point: the security literature is unambiguous that eliminating the single control point transfers coordination weight from central computation to cryptography between the parties (this is *exactly* the challenge posed to you).

### 2.2 The MCP Protocol and LLM Integration
2.2.1. **[MUST]** Communication between the two agents runs over **MCP (Model Context Protocol)**, an open standard connecting LLMs to external tools/data sources.
2.2.2. **[MUST]** Implementation is via the Python **FastMCP** library, which abstracts both server and client construction.
2.2.3. **Every agent is simultaneously:**
   - an MCP **server** — exposing tools (e.g., `receive_move`) that answer natural-language requests, decorated with `@mcp.tool`.
   - an MCP **client** — calling the opponent's server-exposed tools to send data or trigger actions.
2.2.4. **No "strong side" / "weak side"** — both peers are fully symmetric in their network role.
2.2.5. **[STRONGLY RECOMMENDED, not required]** be aware of complementary maturing protocols:
   - **A2A (Agent-to-Agent, Google)** — full lifecycle management of inter-agent tasks via states like "submitted"/"in progress"/"completed." Recommended for task handoff and communication between agents.
   - **ACP (Agent Communication Protocol)** — federated Zero-Trust communication for systems with many participants and federations of agents.
   - **MCP remains the project's required protocol** for tool/data connections; do not replace it with A2A/ACP.

### 2.2.6 Table 1 — Division of Responsibility Between Agent Components
| Component | Responsibility | Integration point |
|---|---|---|
| Local FastMCP server | Manage resources, expose actions to the opponent, process asynchronous responses | Use decorators like `@mcp.tool` to receive cryptographic signatures |
| Client engine | Game logic, calls to the strategy module, turn scheduling | Connects to the opponent's URL and invokes its tools over the network |
| LLM model | Producing natural-language phrasing, text comprehension, game/psychological prompt engineering | Local access via API (Claude, Ollama, Gemini) |
2.2.7. **Critical distinction: the LLM does not decide legal moves** — it produces the narrative/rhetorical layer only. Final legality-decision authority remains with the client engine and cryptographic verification layer; the LLM is never a trusted party by itself. LLM engagement can be produced in 4 different modes (see §6.5 / Table 21 below).

### 2.3 Tunneling and Environment Separation
2.3.1. **[MUST]** Expose your locally-running FastMCP server via a tunneling tool (**ngrok** or **Localtonet**) to the **public internet** so independent groups on different machines can connect. Running purely on `localhost` is only acceptable *within your own dev/testing environment during the earliest bring-up stages* (Ch.10) — the live league (Ch.9) requires public reachability over the internet.
2.3.2. **Why tunneling is required — NAT traversal**: most computers sit behind firewalls/NAT and are not directly internet-addressable. A tunneling tool creates a public URL that performs NAT traversal (conceptually similar to STUN), letting your opponent connect to your server from anywhere.
2.3.3. **Deadlock risk if tunnels fail**: if either side's tunnel goes down, the counterpart may lose the ability to complete moves and hit a "dead-end" mid-turn-scheduling — hence tunnel resilience is part of the match's own resilience (see Watchdog/Deadline Tracker, Ch.8).

### 2.3.4 Total Separation of Working Environments — MANDATORY RULE
2.3.5. **[MUST]** Cop code and thief code must run under **two fully separate processes**, with fully separate config directories (e.g., `config/police/` vs `config/thief/`), per the config-file structure in App. B.
2.3.6. **[FORBIDDEN]** It is absolutely forbidden to share a live in-process object or memory holding state between the two sides, and forbidden for either side to call/read a shared variable — even within the same team's own codebase during development.
2.3.7. Any such sharing breaks the **Zero-Trust model** of the architecture, invalidates the solution, **even if the game "works" technically** at a superficial level — this is explicitly called out as a rule violation independent of whether the game functions.

---

## 3. Chapter 3 — Physics Mechanics, Board & Scoring System

**Chapter goal (explicit):** understand how a discrete geometric space + a small set of simple rules define a complete match arena; why enlarging `[board size]` (relative to earlier 5×5 lecture examples) expands the state space exponentially and defeats brute-force search; how barrier placement turns the cop from a random walker into a spatial-resource manager; and how a scoring table translates every end-of-match scenario into a reward that a heuristic, your own custom algorithm, or (as one optional possibility) reinforcement learning can optimize.

### 3.1 A Discrete Space & Shared Physical Contract
3.1.1. The game takes place on a **discrete grid**: a finite lattice where every position, every move, and every barrier placement is a countable, precise assignment. Precisely *how* the physics is enforced is defined by: **there is no central server enforcing physics laws — physics laws are self-enforced by the agents themselves ("no external judge").**
3.1.2. **[MUST]** All physical laws are dictated by a pre-agreed shared config file (`config/game.json`, App. B) — board dimensions, starting positions, the barrier set, and the scoring table — as **hard-coded values**. Since both agents literally load the same file, they always compute the same transition function and can never dispute "what the rules were" mid-match.
3.1.3. **Contract is negotiated between the two teams — but only where explicitly allowed.** The physical contract is not written top-down; it is set via negotiation between the two teams (via the shared config), and may therefore vary group-to-group. **[MUST]** the contract must be identical and agreed for both sides — it is forbidden to weaken or dilute the mandatory instructions defined in this book (App. F values are a floor, not negotiable downward); groups **may** agree to strengthen requirements, and **may** legally exploit any freedom not explicitly defined here — for either side's benefit or as a competitive advantage — as long as everything remains lawful and mutually agreed.

### 3.2 Board Dimensions & Start Points
3.2.1. Default board size `[board size]` = **7×7** (vs. 5×5 used in earlier smaller lecture examples). This enlargement is **not cosmetic** — it expands the number of possible joint state configurations by roughly the 4th power of the linear scale (positions of both agents × all possible barrier layouts) — the practical consequence is that brute-force search of the full state space is a `Dec-POMDP`-hard combinatorial problem, and both sides must resort to heuristics or learning (Ch.6) rather than exhaustive search.
3.2.2. **Coordinate system**: two negotiable parameters — `[coordinate axis origin corner]` (default: top-left corner = `(0,0)`) and `[coordinate axis start index]` (default: 0-indexed). Both parameters are negotiable between the two teams **but must be identical** — one side using 0-indexed and the other 1-indexed, or disagreeing on which corner is `(0,0)`, splits the match into two disjoint, disagreeing realities.
3.2.3. **Starting positions are strategic, not fixed or arbitrary** — negotiated between the two teams during the shared-config negotiation stage; any legal layout agreed by both sides is allowed. Example shown (illustrative, not mandatory): thief starts at board center (`[thief start position]` example `(3,3)` on a 7×7 board) to maximize escape-route options in every direction; cop starts in a defined pursuit-distance position (example `[cop start position]` = `(0,0)`, a corner) — you may rebalance the initial force balance between sides by agreement, without touching the agents' own code.

### 3.3 Movement, Barriers & Spatial Engineering
3.3.1. **[MUST]** Each turn, an agent may move exactly one cell in one of the four orthogonal directions (up/down/left/right) — **or** choose to stay in place. **[FORBIDDEN]** Diagonal movement of any kind.
3.3.2. **[MUST]** Any attempted illegal move must be rejected/handled and must never be silently executed.
3.3.3. **The cop's core spatial-engineering advantage:** the cop, on its turn, may place a static barrier in any cell **exactly one step away from itself** (its own current cell, or one of the 4 orthogonally-adjacent cells). The barrier turns that cell into a permanently impassable obstacle for the rest of the match for **both** players — barriers are irreversible ("no un-blocking"); once blocked, always blocked until game end.

#### Barrier Rule Details
3.3.4. **[MUST]** The cop may place a barrier only in a cell exactly one step from where it stands.
3.3.5. **Immediate capture rule**: if the cop places a barrier on the cell the thief currently occupies, that instant counts as capture — the thief is captured at that moment. Similarly, if the thief is left with **no legal move at all** (all orthogonally-adjacent cells are blocked by barriers and/or board edges), it is also treated as captured.
3.3.6. **[MUST] Declaration obligation**: the cop must truthfully declare, in real time, every barrier placement and its exact location; it is forbidden to place a hidden barrier or lie about its location.
3.3.7. `[max barriers]` = the cop's maximum barrier budget for the match (minimum required value: 14) — **placement decisions therefore constitute resource-management decisions**: the cop must "squeeze" the thief toward a corner without accidentally wasting its own escape-route-blocking resource.
3.3.8. **Spatial-engineering challenge for cop's design:** managing when, where, and how many barriers to place to progressively narrow the thief's viable path space toward a long-term pursuit-and-trap strategy (discussed further in Ch.6).
3.3.9. **Iron rules on movement & barrier honesty (explicitly restated as binding):**
   - **[FORBIDDEN]** No illegal moves at all; an attempted illegal move must simply be rejected — the underlying physics is enforced only by the agents themselves (no external judge).
   - **[MUST]** Truth obligation when the cop lands on the thief's cell — a `Capture Claim` must be cryptographically declared; the same applies to any attempt to falsely claim capture when it did not truly occur (audit-log will expose it via the commit/reveal cryptographic protocol, resulting in absolute disqualification of that match).
   - **[MUST]** Barrier declaration must be public — no hidden barrier placement, no lying about barrier location.
   - Full binding mapping of Do/Don't/Recommend rules is centralized in App. E (§15 below).

### 3.4 Win Conditions & the Scoring Table
3.4.1. The scoring system balances two opposing tensions: the cop's difficulty in finding a hidden opponent vs. the thief's difficulty in surviving in a shrinking, constricting arena. Every ending scenario awards each side a *different* score (a binary win/loss is intentionally avoided) — this directly encodes the reward function `R` from the Dec-POMDP model (Ch.1).

### 3.4.2 Table 2 — Win Conditions & Score Allocation (exact values, see also §14 Mandatory Parameters Table)

| End event | Win condition | Cop score | Thief score |
|---|---|---|---|
| Successful capture | Cop lands on thief's cell and announces `Capture Claim` | `[cop-capture score]` | `[thief-capture score]` |
| Extended survival | Thief survives ≥ `[survival threshold]` steps with no valid capture | `[cop-survival score]` | `[thief-survival score]` |
| Technical loss | Falling out of protocol course, timeout, or cryptographic forgery | `0` | `0` |

3.4.3. **[MUST]** Asymmetry in the table is deliberate: capture rewards the cop with the highest possible score (`[cop-capture score]`), fulfilling its primary goal; extended survival tolerance rewards the thief with **its** highest possible score (`[thief-survival score]`). Technical failure zeros out both sides equally, incentivizing both to preserve protocol correctness rather than "win at any cost."
3.4.4. **[MUST] Tie Rule**: if the cumulative score across **all games played** between two teams ends equal, each team gets `[tie score]` — mandatory value defined in App. F (§14).
3.4.5. **[MUST] Capture Claim requires cryptographic truth-telling**: capture claims are not a matter of trust between rivals — they must be reveal-audit-verifiable proof, submitted for post-hoc audit; any attempt to lie will surface during the log-audit phase and lead to disqualification (the numeric score itself becomes a mathematically-enforceable fact derived from the opponent's own declaration).

---

## 4. Chapter 4 — Dynamic Pheromone Trails & Collective Memory of the Trail

**Chapter goal (explicit):** understand how a simple biological mechanism — scent diffusion and evaporation — solves (partially) the partial-observability problem introduced in Ch.1; what Stigmergy (indirect coordination through the environment) is and why it governs the emission/decay mathematical model; how each agent projects the opponent's historical scent map to expose deceptive verbal hints and strengthen a probabilistic belief map.

### 4.1 Indirect Coordination Through Changing the Environment
4.1.1. Millions of ants coordinate with no central dispatcher, no language, and no shared memory — the answer is **Stigmergy**: indirect coordination through changing the shared environment. Each ant leaves pheromone trails behind, and other ants respond to them; the environment itself becomes the shared bulletin board.
4.1.2. **[MUST]** Implement a scent-trail mechanism directly inspired by ant-colony behavior as a central answer to partial observability: when either agent (cop or thief) moves on the board, it emits **virtual pheromones** behind it over time. Neither agent directly observes the opponent — but reading the environment turns this physical channel into a primary information source.
4.1.3. **Scent is a natural, non-controllable, non-fakeable phenomenon**: it emanates from mere movement or presence; no one can suppress their own scent, and every side reads only the opponent's scent field.

### 4.2 Emission & Decay Model — MANDATORY FORMULA
4.2.1. Whenever an agent is present or has just been present at a location, a **scent field** of size `[scent field size]` (default 5×5) is generated centered on its position.
4.2.2. At the emission center, intensity `[scent center intensity]` (default 0.9); intensity falls off radially the further from the center a cell is.
4.2.3. Both agents leave a scent field, symmetrically, on every turn — cop and thief alike, and this applies both while occupying a cell **and** after leaving it via a decay process across the whole board each full turn (cop + thief).

4.2.4. **Mandatory scent-update equation** — decay rate is `[scent decay rate] = ρ` (default `ρ = 0.10`):

```
τij(t+1) = max(0, (1 − ρ) · τij(t) + Δτij)
```

| Term | Meaning | Practical implication |
|---|---|---|
| `τij(t)` | current scent intensity at cell (i,j) | continuous value in `[0, 0.9]`; higher = "fresher" clue that an agent was recently there |
| `(1 − ρ)` decay factor, `ρ = 0.10` | Decay Rate | 90% of existing scent is retained per turn; a deliberate design choice — slow decay leaves enough historical trail to be tactically useful, but not eternal |
| `Δτij` | new emission this turn | added at the emission center based on radial proximity to the agent's current position (`Δτ = 0.9` at agent's own cell; `Δτij = 0` if far away) — this is the channel linking agent presence to the "written" board state |
| `max(0, ·)` | floor to zero | ensures scent intensity is never negative — silence is literally "no information," never "negative information" |

4.2.5. The formula combines two forces: **forgetting** (`(1−ρ)·τij(t)`, gradual erosion of the past) and **memory** (`Δτij`, encoding of the present) — the balance between them determines how far back each side can "look" into its rival's trail.
4.2.6. **[MUST — mandatory sequencing rule]**: the emission/decay mechanism's formula, and its parameters, must be cryptographically **locked/agreed via the signed shared config before the game starts** — a group must not be able to change the decay function unilaterally mid-game (see App. B "signed shared file," and §15 rule 23).

### 4.3 Scent-Map Tactics
4.3.1. Because scent decays slowly, it leaves a **historical scent trail** — not a snapshot of the current instant, but a short "video clip" of the opponent's recent movement over past turns.
4.3.2. Each agent can render the board and obtain the opponent's scent map. This is where **belief modeling** truly starts: cross-referencing this map against the opponent's verbal claims lets a side strengthen probabilistic convergence on the rival's real location.
4.3.3. **Symmetry**: the cop reads the thief's scent trail; the thief reads the cop's scent trail — full symmetry, using the opposing rival's verbal hints as the counterpoint each side supplies.
4.3.4. **Worked example: catching a lie about direction** — if the true scent trail is concentrated in the south-east corner but the thief verbally claims "I moved north," the cop can compute the probability gap (e.g., ~0.81 expected intensity near the claimed direction vs. ~0.00 observed) and conclude with high confidence that the thief is lying, updating the trust weight it assigns to that opponent's future verbal hints downward, and re-focusing pursuit toward the true scent source rather than the claimed direction.
4.3.5. **[MUST]** Scent maps cannot be forged — they are emitted directly by the movement act, not by a verbal claim, so what is exposed here is a caught **verbal lie**, not a "false trail" (scent itself cannot lie, since the environment doesn't fake itself).
4.3.6. **Sensitivity of parameter choices — illustrative "what if" analysis in the book**: doubling `ρ` to 0.20 makes the trail decay much faster and shortens the memory window drastically; halving `ρ` toward 0 makes the board almost eternally saturated with scent and removes the ability to distinguish "old" from "new" trail information. Parameter tuning materially changes gameplay difficulty and must be set thoughtfully if teams negotiate it (bounded below by the Mandatory Parameters Table).

---

## 5. Chapter 5 — Cryptographic Security & Zero-Knowledge Protocol

**Chapter goal (explicit):** understand why an unrefereed P2P competitive game invites cheating temptation; how the Commit-Reveal mechanism based on hash functions (SHA-256) makes deception practically impossible; how mutual end-of-match audit exposes any tampering after the fact; how a "Step-0" hardware declaration guarantees computational fairness between competitors on wildly different machines.

### 5.1 The Temptation to Cheat in a Referee-Less Network
5.1.1. In a chess game with no board and no referee, each player privately manages their own board state and reports moves to the rival on trust. In a distributed P2P system talking directly over FastMCP with no central referee, this same temptation of "hindsight rewriting/cheating" appears in three forms:
   - **Changing a move after it was already made.**
   - **Changing a move after the opponent's move was already revealed.**
   - **Denying or retroactively re-editing a location or previous declaration.**
5.1.2. As long as both the player and its own protocol-writing entity are the same side, nothing stops it from rewriting its own move history retroactively to its own benefit.
5.1.3. **[MUST]** The solution is not legal/contractual but mathematical: trust is anchored to a **Commit-Reveal mechanism** based on cryptographic hash (SHA-256) functions — the "coin-flipping over the telephone" concept (Blum, 1983): a commitment binds each side to a decision **before** revealing it, closing off the ability to change one's mind after the fact, since any change would break the previously-transmitted cryptographic signature.

### 5.2 Commit-Reveal Mechanism over SHA-256
5.2.1. **[MUST] Every single move in the game must pass through four mandatory cryptographic steps, in this exact order** — these steps are irreversible and cannot be skipped or reordered.

#### Step 1 — Commit
5.2.2. Agent picks its physical move and the accompanying verbal hint (flagged with an `Intent` tag — is the hint true or a lie), and generates a unique `Nonce`. Four data components are concatenated and hashed together for a single cryptographic digest. Only the resulting **commitment hash** is sent over the FastMCP server — **never the raw content**.

**Mandatory commitment formula:**
```
H_commit = SHA256(State ‖ Move ‖ Intent ‖ Nonce)
```

| Field | Meaning | Practical implication |
|---|---|---|
| `H_commit` | commitment hash | 256-bit digest; the move's "fingerprint" — sent to the rival, but reveals nothing about content |
| `State` | board state the move is based on | prevents reuse of an old commitment in a new context |
| `Move` | the physical action chosen (movement/barrier/etc.) | this is the value being "locked" against tampering |
| `Intent` | flag marking whether the accompanying hint is truthful or a lie | forces declaring honesty about one's own honesty in advance — can't claim after the fact "I was lying intentionally" |
| `Nonce` | one-time random cryptographic number | ensures uniqueness of the hash and defeats dictionary attacks (see §5.2.3) |

5.2.3. **What is a Nonce and why it matters (mandatory concept)**: a Nonce is a unique random number generated fresh for every single commitment. Dual role: (1) guarantees that if the same agent repeats the exact same move, the resulting hash is still different every time; (2) defeats "dictionary attacks" where a rival could try to guess the sealed content by pre-hashing all reasonably-probable move combinations. Without the Nonce, the small movement space would make it trivial to crack a hash by brute force.
5.2.4. **Serialization detail**: concatenation is done via canonical JSON serialization (sorted keys, fixed separators) so both peers hash byte-identical input — this is not simple numeric concatenation, it is field-name-based serialization. The reference implementation seals a richer record (hint, verdict, step, role, sub_game) — the illustrated example shows the core fields only.

#### Steps 2–4 — Acknowledge, Reveal, Audit
5.2.5. **Step 2 — Acknowledge**: opponent confirms it received the commitment and that it is now locked; this acknowledgment prevents the sender from backing out of its commitment, and simultaneously guarantees that reveal will only happen once both sides have already locked in their moves.
5.2.6. **Step 3 — Reveal**: the agent sends the actual move and the verbal hint text. The Nonce **remains hidden at this stage** to prevent reverse-engineering ahead of time.
5.2.7. **Step 4 — Audit / Final Reveal (only at game end)**: all Nonce values are revealed for **all** steps at once, so each side can recompute and independently verify all commitments in full mutual audit.
5.2.8. **[MUST]** Provided reference code implements `commit()` (produces the hash + a fresh cryptographic random Nonce via a `secrets`-style module, never plain `random`) and `verify()` (recomputes and compares the hash using constant-time comparison, e.g. `secrets.compare_digest`).

### 5.3 Zero-Knowledge Framing
5.3.1. The Commit-Reveal mechanism embodies the spirit of a **Zero-Knowledge proof** (Goldwasser–Micali–Rackoff, 1989): each agent proves it chose a legal move and fixed it *before* observing the opponent's move — without revealing the content ahead of time. At commit time, the opponent gets absolute certainty a locked decision exists — but zero knowledge of its content. Only at the reveal stage is the content exposed, and it can then be truth-tested against the original commitment. Thus the **commitment** is separated from **knowledge disclosure**.

### 5.4 Mutual Audit & Log Integrity
5.4.1. **[MUST]** System reliability rests on a **post-mortem integrity check**: at game end, each side submits its complete match log, including SHA-256 for every step's `State`, `Move`, `Intent`, and the now-revealed `Nonce`. Each side must independently recompute the hash for every one of its own and the opponent's steps and compare the resulting hash against the value originally committed at that step.
5.4.2. **[MUST — tampering detection is decisive]**: any single mismatch between the recomputed hash and the originally-committed hash **unambiguously proves tampering**. This is not a matter of statistical interpretation: the SHA-256 function is highly sensitive to any single-bit change — a real difference in even one byte changes the entire digest. A caught mismatch means **immediate, total technical loss for that match** — the outcome on the board becomes irrelevant, and cryptography (not human judgment) is the decisive factor.

### 5.5 Step-0 & Computational Fairness
5.5.1. Fairness question raised: is it reasonable for one team running on a modest laptop to compete under the same terms as a team running a deep search on a powerful cloud machine using a heavy LLM?
5.5.2. **[MUST] Computational Fairness** requires that the material hardware advantage not by itself decide the match's outcome — this principle is reflected in scoring in the live league (Ch.9).
5.5.3. **[MUST]** Before the first move, both sides must perform a "**Step-0**" declaration: each side gathers its own machine spec — OS, number of CPU cores, RAM size, presence of a GPU/VRAM, and the name of the LLM model in use — alongside the code version and team name and the game/sub-game count. This full spec is serialized to JSON and **cryptographically signed** with a pre-shared key so it cannot be forged after the fact.
5.5.4. **[MUST]** In parallel, every LLM token consumption must be tracked (the LLM model's own tokens are also cryptographically sealed) so as to expose the real computational resource cost actually consumed.

### 5.5.5 Mandatory Identity Verification: Commit Hash in Step-0 Declaration
5.5.6. **[MUST]** Alongside the hardware spec, each side must also declare in its Step-0 declaration the **Git commit hash (commit hash)** of the code that will run in that match. It is permitted to update/improve code between games, but **for every single game the exact commit hash used must be recorded in the declaration**. This same identity must also be included in the results JSON field (`github_commit`, see end-of-match report, §9).
5.5.7. Normalization principle governing computational thinking in league scoring — bonuses for efficient algorithmic solutions run on modest resources under low resource consumption; the reward/incentive inverts: raw hardware power should **not** earn the reward — algorithmic wisdom should. A fast, lightweight solution running on a modest machine should beat a heavy opponent by outsmarting it, not by out-computing it.

---

## 6. Chapter 6 — Strategy Module & Decision-Making

**Chapter goal (explicit):** understand why the reasoning of a decision-maker must be independent, and never blindly rely on an LLM for spatial computation; a catalog of alternative/equivalent movement-policy approaches — Manhattan-distance heuristics, your own custom algorithm, or (as one single optional tool) reinforcement learning; how a Bayesian belief map is built and continuously updated; how the LLM integrates into the strategy pipeline only for the verbal layer.

### 6.1 Why a Separate Strategy Module Is Required
6.1.1. **[MUST]** Build a separate **strategy module**, connecting to the `PeerRuntime` layer at a precise point: immediately after hint decoding (the incoming hint) and before `Commit` packaging (the outgoing move). Two decision points sit inside this module: belief update and legal-move choice, plus deception-text composition. This separation is not cosmetic — it is the boundary between a "generic communication component" and "a thinking agent."
6.1.2. **[MUST]** Students are required to point one of the two config keys `police_class` / `thief_class` (in `[strategy]` section of the private per-peer config) at your own "brain" subclass deriving from `BrainBase` and overriding `_decide_move` (and, for the cop, also `_pick_move` for barrier placement).
6.1.3. **A minimal illustrative implementation with no strategic depth (`BrainBase`) exists in the example repo (App. D) purely for educational purposes** — it is not intended to be your final solution.

### 6.2 Reinforcement Learning as One Optional Tool — NOT Mandatory
6.2.1. **[MUST clarify]** Reinforcement learning is **just one of the possible ways to realize the movement policy — an optional tool only, not "what the course taught."** The course does not require RL at all. Teams may build a strong agent using purely heuristics, with **no RL whatsoever**.
6.2.2. **Three algorithmically equal, tied-for-legitimacy tracks are described** — in every one of the three, the **movement decision-authority stays with the algorithm**, and the LLM only serves the verbal layer:
   1. **Pure Manhattan-distance heuristics**, optionally blended with a Bayesian belief map.
   2. **Your own, custom-designed algorithm.**
   3. **Reinforcement learning, presented as a single optional tool among several — not mandatory.**
6.2.3. **[MUST NOT]** the board must never be `[board size]` so large that exhaustive brute-force is even remotely feasible; the game's state-space design is *deliberately* built to force heuristics/learning rather than the reverse.

#### 6.2.4 Mandatory Q-Learning Update Formula (if RL is chosen)
```
Q(s, a) ← Q(s, a) + α [ r + γ · max_a' Q(s', a') − Q(s, a) ]
```
| Term | Meaning | Practical implication |
|---|---|---|
| `Q(s,a)` | current estimate of cumulative expected reward for action `a` in state `s` | the table (or approximation) the agent updates as it plays |
| `r` | immediate reward received right after the action | maps directly from the scoring table (§3.4 / Table 2) |
| `α ∈ (0,1]` | learning rate | how much new information overrides old — high = faster but jittery, low = slow but stable convergence |
| `γ ∈ [0,1)` | discount factor | preference for delayed vs. immediate reward — high `γ` encourages e.g. building a long barrier trap over many turns |
| `max_a' Q(s', a')` | best possible future value | the estimate is "borrowed back" from the future state, letting the agent plan beyond the immediate step |
6.2.5. **Epsilon-Greedy** exploration policy is used to prevent getting stuck in local optima: with small probability `ε`, choose a fully random action; otherwise choose the action with the highest current `Q` value. This balances *Exploration* (of new fleeing/scent trajectories) against *Exploitation* (of an already-learned policy loop).
6.2.6. If you choose the RL track, note that the project is actually against a **thinking opponent** — this is technically Multi-Agent Reinforcement Learning (since the opponent's own policy is simultaneously improving as it learns), though the book still counts this among "one of several equally-valid tracks," not a requirement.
6.2.7. **[RECOMMENDED]** for groups wanting to go deeper into advanced win tactics: look into decentralized evolutionary coordination for LLM-based multi-agent systems as an approach complementing an RL learning track with population-development ideas.

### 6.3 Distance Heuristics & the Belief Heatmap
6.3.1. **[MUST]** Both agents maintain a **belief map** (probabilistic heatmap) over the opponent's likely hidden location, built from the scent field, decay over turns, and the opponent's (possibly false) verbal hint. This is fully symmetric — cop builds a belief map over the thief's position and vice versa.
6.3.2. **Mandatory Manhattan-distance formula** (over an orthogonal grid):
```
D = |x_cop − x_target| + |y_cop − y_target|
```
| Term | Meaning | Practical implication |
|---|---|---|
| `(x_cop, y_cop)` | own known coordinates | the one unambiguous term in the equation |
| `(x_target, y_target)` | highest-belief cell (`arg max_s b(s)`) | not the "real" opponent, only the current best guess from the belief map |
| `D` | sum of absolute axis differences | fits orthogonal grid movement (no diagonal), so it is an admissible lower-bound estimate of the number of steps needed |
6.3.3. **Worked example**: cop at `(2,2)`, belief map peak at `(5,5)` → `D = |2−5| + |2−5| = 6`. Among the legal moves — east `(3,2)` gives `D=5`, north `(2,3)` gives `D=5`, west `(1,2)` gives `D=7` — the agent picks the east or north move, both minimizing `D` by one step. This combines probabilistic reasoning (choice of target) with a learned reasoning layer (choice of move via `Q` values, if RL is used).
6.3.4. Table 8 (referenced) shows a worked example of a 10×10 Bayesian belief map (`b(s) = P(thief = s | hints)`), each cell colored by posterior probability after a Bayes update from a scent hint; the cop keeps a symmetric belief map over the thief, and vice versa; the peak (`arg max_s b(s)`) is marked; blocked barrier cells always carry zero belief.
6.3.5. **[MUST]** Even after an update, uncertainty always remains: distribution is a cloud, not a single point — a new hint may reinforce or contradict the prior distribution, and the peak may split into two competing hotspots, forcing the cop to decide which one to commit to first.

### 6.4 LLM Integration for Prompt Engineering
6.4.1. **[MUST NOT rely on the LLM for spatial computation]**: never hand the actual move decision over to the LLM to compute directly on the raw grid — LLMs are prone to hallucinating coordinates, directions, and distances during numeric reasoning, and could produce an illegal move without warning; the destination the LLM believes it reached may not match reality.
6.4.2. **The LLM's role is text-only**: connecting text, style classification, and psychological game/prompt engineering. Spatial decision-making remains reserved for the algorithm — the only one that can guarantee mathematical legality.
6.4.3. **The single unbreakable prohibition presented above is the one and only exception explicitly flagged as bindable-by-mutual-agreement**: teams **may** together choose to deviate from this recommendation via **explicit, documented, mutual agreement of both sides** — separate accountability applies (see rule §15 item 25 and Ch.6.5's callout box).

### 6.4.4 How the Bluff Text is Produced — Four Operating Modes (mandatory config selection)
6.4.5. Since the movement decision is 100% algorithmic, the LLM is only needed for the verbal layer — so the choice of "how" to activate it is essentially a budget question: how many tokens are you willing to spend on speech. The reference implementation offers **four modes**, selected in the private config `[provider]` field under `[trash_talk]`:

### 6.4.6 Table 21 — LLM Modes for the Verbal Game (private, per-peer choice)
| Mode | Cost & where it runs | Token limit |
|---|---|---|
| `template` (default) | Ready-made phrases; chosen in code deterministically — **zero tokens**, no network dependency | none |
| `ollama` | Local model via `localhost:11434` | free API tokens, no cost |
| `claude_api` | Small cloud model (e.g., Haiku) via real API | subject to `[token budget per series]` |
| `claude_cli` | Via `claude -p` command through the Claude Code CLI | highest cost, subject to subscription |
6.4.7. The `every_n_steps` parameter can throttle the model to run only once every few turns, further reducing token cost. Teams can play an entire series using only the `template` or `ollama` modes (zero/free tokens), and all competitiveness rests on movement-algorithm quality only.

---

## 7. Chapter 7 — User Interface (GUI) & Replay Simulator

**Chapter goal (explicit):** understand why real-time observability is a core component of building complex P2P systems, not a decorative add-on; how to translate the abstract mathematics of the belief-probability table into an accessible heatmap visualization; how to build a synchronous turn-taking indicator in the local GUI; how the Replay Viewer serves as a trustworthy, cryptographically-verified retrospective witness that authenticates every step taken and detects any attempt to falsify the match after the fact.

### 7.1 Two Axes: Live Monitoring vs. Retrospective Witness
7.1.1. Real-time monitoring vs. retrospective proof are two related but distinct needs. **The Live GUI** answers "what is happening right now?" **The Replay Viewer** answers a harder question: "did it really happen as claimed?"
7.1.2. The distinction is not merely technical but fundamental: match history under a refereeless, decentralized architecture is **not** stored with a trusted authority — it is kept in a local log file per player. The temptation to lie exists — a player could try to rewrite the past retroactively to their benefit.

### 7.2 Local Truth (mandatory design principle)
7.2.1. **[MUST]** Local Truth is a planning principle stating that each agent's own interface displays **only** what is available to it — its own position, the scent map it has smelled, and hints it has received — **never** the full objective board state. No "bird's-eye view" exists in this principle at any point.
7.2.2. This principle derives directly from the Dec-POMDP formalism (Ch.1): each agent's partial observation `Ωi` is a strict subset of the true state `S` — so an interface that reveals the full `S` would violate the rules of the game itself.

### 7.3 The Live GUI: Heatmap and Turn Banner
7.3.1. **[MUST]** Each side — cop and thief — runs its own dedicated GUI application (e.g., Tkinter/PyQt) built purely on its own local-truth definition; the interface never exposes the objective board state, only local truth.
7.3.2. **Heatmap visualization**: the heatmap mechanism is fully symmetric between the two sides — each renders a dynamically-changing grid live-displaying its own agent's belief map about the opponent only. Cells are colored/shaded on a gradient (e.g., toward red, deeper = higher believed probability of opponent presence) based on received hints and the scent map.
7.3.3. **[FORBIDDEN]** Neither side may ever display the opponent's true location — only its continuously-updated probabilistic estimate.
7.3.4. **Turn indicator**: needed to reflect the asynchronous acknowledge/reveal handshake — the GUI must include a turn-state banner showing whose turn it is (e.g., **"YOUR TURN"** in green when the local player may act, vs. **"LOCKED"** in gray once the local player has sent a `Commit` and is waiting for the opponent's turn to complete). This banner is a purely visual construct representing the underlying asynchronous state machine (Ch.8) — it prevents a player attempting to act out of turn, which could create a race condition.

### 7.4 The Replay Viewer & Integrity Enforcement
7.4.1. **[MUST — mandatory submission requirement]** Build a **Replay Viewer** application that provides trustworthy end-of-match proof: the player supplies the final log file (e.g., `logs/police_match.json`) and the viewer allows scrubbing forward/backward through the match at will via control buttons.
7.4.2. **[MUST]** The uniqueness of this tool is **not** its graphical display, but its **cryptographic verification**: at every step, a verification engine takes the move appearing in the raw log and re-hashes it using the revealed `Nonce` per SHA-256, comparing it against the originally-committed `Commitment`.
7.4.3. **[MUST]** If the values match, a green **"Verified OK"** stamp is displayed. If any tampering is found — even the smallest attempt to alter past data — the tool must display a red **"TAMPERED"** banner, and **the match is disqualified immediately**. This rests directly on the collision-resistance property of the hash function discussed in Ch.5: it is computationally infeasible to find a different (Nonce, move) pair that produces the same hash — any change to a move necessarily reveals itself.

### 7.5 The Verification Engine: Code Sketch
7.5.1. **[MUST]** Implement the verification loop: read log entry (`nonce`, `move`, `commit`), recompute `SHA256(nonce, move)`, compare to the stored `commit`, and return `"Verified OK"` if matched or `"TAMPERED"` (disqualify) if not. `replay(log)` walks every recorded step; the entire match is voided on the **first** tamper detected.
7.5.2. **[MUST]** Submission requirement: providing a working Replay Viewer, and it discovering **zero tampering** on your own final submitted match, is a hard pre-condition of a valid submission — appeal is not possible; the cryptographic evidence system is designed precisely so that whether the log was falsified is never left to human judgment or subjective interpretation.
7.5.3. A screenshot of the belief-heatmap Live GUI, and a screenshot of the Replay Viewer showing `"Verified OK"`, are part of the mandatory submission deliverables (App. C, App. D usage).

---

## 8. Chapter 8 — Agent Architecture Design & Deep Reliability Mechanisms

**Chapter goal (explicit):** understand why an autonomous game agent is never a linear coding exercise but requires disciplined systems architecture; how the `Orchestrator` acts as the single gateway behind all sub-systems; how a legal state machine binds match progression to legal state transitions only; what `Deadline Tracker` and `Watchdog` reliability patterns are, and why they protect the agent from paralysis and disconnects in a peer-to-peer network.

### 8.1 Separation of Concerns as a Guiding Principle
8.1.1. Why does a system that beats an opponent in simulation sometimes fail against a real, remote opponent? The answer usually lies not in flawed decision-making algorithms but in the development of the surrounding system: an agent participating in a multi-agent competitive game — per the protocols recommended in this domain — must not mix connection management, decision-making, and log-writing into a single monolithic code path. Such mixing creates a fragile system that collapses entirely on failure of just one sub-system.
8.1.2. **[MUST]** The development solution is division into modules with clear, isolated single responsibilities, coordinated through one central component. This chapter is about the architectural skeleton: how to build a single `Orchestrator` that serves as the single gateway to all sub-systems, and how to wrap it with a trust layer that assumes from the start that the world — the network, the model, the opponent — will fail at exactly the critical moment.

### 8.2 The Orchestrator & State Machine
8.2.1. **[MUST]** Build a single central **Orchestrator (Gateway)** — a single entry point for all agent sub-systems: connects up the MCP connectors (Ch.2), invokes the Decision Module (Ch.6), and links to the log managers and cryptographic-obligation mechanisms (Ch.5). Every sub-module knows the Orchestrator alone — no module directly knows and calls another module. **The Orchestrator must not itself contain decision-making or communication logic — its role is purely coordination, not execution.**
8.2.2. **[MUST]** The entire match is governed by a legal **state machine**, meticulously constraining match progress: only legal transitions between game phases are allowed. States shown include: `WAITING_FOR_OPPONENT`, `COMPUTING_MOVE`, `COMMITTING`, `AWAITING_REVEAL`, `VERIFYING`, cycling back to `WAITING_FOR_OPPONENT`; plus an error state `TECHNICAL_LOSS` reachable from illegal transitions.
8.2.3. **Deadlock** is defined explicitly: a situation where two or more entities are each waiting for a resource or message held by the other, such that neither can progress — under a P2P system with no central referee, a deadlock can silently freeze an entire match with no error message at all. The state machine blocking illegal transitions is the **first line of defense against deadlock**.
8.2.4. **[MUST]** The state-machine implementation must reject any transition request not listed in its own transition table, immediately raising an error rather than silently letting the system drift into an undefined state — this converts a hidden bug caught during runtime into a loud, visible error caught during development, rather than a silent deadlock during a live game.
8.2.5. **[MUST]** Every completed detail should be visibly confirmed ("did the described end-to-end behavior actually happen?") **before** moving to the next stage.

### 8.3 Reliability Patterns: Watchdog & Deadline Tracker
8.3.1. Peer-to-peer systems (P2P) are exposed to network glitches and critical bottlenecks precisely at the model layer — the system cannot assume every request will get an answer in time; therefore, two mechanisms are mandatory: **Deadline Tracker** (per-request timeout) and **Watchdog** (per-process heartbeat monitor).

#### 8.3.2 Deadline Tracker — Timeout per Request
8.3.3. **[MUST]** Every request sent over the FastMCP server carries a **timestamp** and an **expiry deadline**. If a response has not arrived within the allotted time, the system must retry (`Retry`) or issue a technical-loss/timeout notification.
8.3.4. **[MUST — iron rule]**: a missed deadline **is a failure, not patience** — a request whose deadline has passed must be considered failed, and must **not** simply be left waiting indefinitely. Leaving a request "dependent" with no deadline is a direct path to deadlock: the main process gets stuck waiting, with no heartbeat, and the whole match hangs. On every FastMCP request, a deadline must be set, and once the deadline expires, the system must either issue a `Retry` or declare a technical loss and close the turn cleanly.

#### 8.3.5 Watchdog — Heartbeat Monitor
8.3.6. **[MUST]** While the Deadline Tracker watches an individual request, the **Watchdog** watches the entire system: an independent background process monitoring the main game loop from the outside. If it detects the system has been frozen for many minutes with no heartbeat (e.g., due to a network failure or model crash), it must be able to perform a **State Persistence** (save game state for later recovery) and then a **Controlled Shutdown** (release MCP connections, close logs), rather than crashing silently.
8.3.7. **[MUST]** The Watchdog check compares elapsed time since the last heartbeat against a fixed threshold (default: `[watchdog timeout sec]` from Table F/§14). If the threshold is exceeded, it persists state and returns `"SHUTDOWN"`; otherwise `"ALIVE"`. Once every regular period the main loop should emit a heartbeat signal, `Watchdog` returns `ALIVE`, and does not interfere; but if too much time passes without one — a sign the model crashed, communication froze, or connection was interrupted — the Watchdog guards the state and executes a controlled shutdown, so a later restart can happen without losing the entire match.
8.3.8. Diagram 12 in the book depicts a single `Orchestrator (Gateway)` splitting into five separate modules: `MCP Connector`, `Decision Module`, `Log Manager`, `Deadline Tracker`, and `Watchdog`. All inter-module communication passes through one single point; no module knows another module directly — this is the embodiment of the single-gateway principle. If you want to replace the decision-making engine with a different module, you simply swap that module while the interface with the Orchestrator stays fixed; the rest of the system is unaffected — this is the strength of separation of concerns.

---

## 9. Chapter 9 — League, Computational Fairness & Automated Reporting

**Chapter goal (explicit):** understand why the project is not tested under isolated lab conditions but in a dynamic academic league where agents produced by different teams face each other in real time; how "diversity incentive" and "computational fairness" mechanisms shape the league's scoring function; what architecture is needed for automated reporting over Gmail API without collapsing under its own volume; what the mandatory `Gatekeeper` structure is — three defense gates against network flooding or account lockout.

### 9.1 The League: From Lab to Arena
9.1.1. A coding exercise proves itself against known, expected input in a sterile environment where neither the input nor the rival is unpredictable; a system-building exercise is measured in a noisy world: dropped connection lines, a slow clock, a public URL that disconnects mid-route. **[MUST]** you must handle all of it, at once, in the same season.
9.1.2. This project belongs to the second category: it is not tested under isolated lab conditions but must prove itself in a **live, dynamic academic league**, where agents made by different teams face each other in real time, without a central referee, without a fixed opponent, and without a set of pre-known timings.
9.1.3. **Success is not re-measured against a fixed test scenario, but against a changing population of rivals**, each with a different strategy, architecture, and different failure modes. An agent that excels against one opponent may lose sharply to another — and that's precisely the pedagogical goal: to build **robust** systems, not overfitted solutions tuned to one judge.

### 9.2 League Structure & Score Weighting
9.2.1. **[MUST]** Every team must play against **multiple different opponents**, and the league score is derived from the collection of games played. To reward exploring new rivals and prevent farming an easy rival repeatedly, the system implements a **Diversity Incentive**: victory against an opponent your team has not already beaten scores the full `[diversity reward]`.
9.2.2. **[MUST]** Do not play the exact same match over and over for score accumulation purposes: **only one game per opponent counts** toward scoring. Warm-up games are permitted, and even recommended, but do not count. Once the counted game with a given rival concludes, both teams send the end-of-match notification, and mutual sign-off constitutes the recorded outcome — you must not continue playing the same rival for additional counted score.

### 9.2.3 Mandatory Game-Count Declaration
9.2.4. **[MUST]** At the start of every match, each team must declare to its opponent how many countable games it has already played so far, and the diversity-reward weighting is set according to these mutual declarations. This declaration is not a matter of trust: at the end of every legal match, both teams send a match-summary notification (§9.3) to the lecturer; therefore at any given moment, the actual number of games each team has played is knowable.
9.2.5. **[MUST]** **A false declaration**, discovered at any point during the project's audit stage, **disqualifies the team that made the false declaration**.
9.2.6. **[MUST]** Minimum threshold to pass the project is modest but unconditional: each team must play a proper minimum of `[min games to pass]` games against **different** opponent teams. On the flip side, there's also an upper cap: every team may play up to `[max games per team]` (max) counted games to keep the league bounded and fair.
9.2.7. Alongside the diversity incentive, the league operates on the principle of **Computational Fairness**: the system minimizes the scoring-advantage of anyone leaning on massive cloud resources, and rewards teams whose algorithm is efficiently developed to run on modest machines. In other words, the league rewards **algorithmic cleverness**, not raw global compute power — a smart algorithm on a modest machine deserves a higher score than a "brute-force" algorithm burning cloud-server hours.

### 9.2.8 Mandatory Tie Rule (restated here for league scoring context)
9.2.9. **[MUST]** If the accumulated score of all games played between two teams ends in an exact tie, each team receives `[tie score]` — no un-decided rematch is needed. The mandatory value of `[tie score]` is defined in App. F (§14).

### 9.3 Gmail API Reporting Automation
9.3.1. At the end of every legal match against a rival team, there is no more room for human intervention in reporting: **each of the two teams programmatically, automatically, and separately** sends a summary notification — via the **Gmail API** — to the lecturer's address. This automation is both a blessing and a curse in one: it guarantees immediate, uniform reporting, but entrusts a mistake in code — which could bug out — with access to a real email account. What happens if an infinite loop starts firing thousands of messages a minute?

### 9.3.2 Mandatory Reporting Address Obligation
9.3.3. **[MUST]** At the end of every legal match, both agents must automatically send the end-of-match summary report to the lecturer's email address `[agent's report address]`. This is the unique, mandatory recipient address for all report submissions; it must be set as a fixed constant destination in each of the two agents' code.
9.3.4. This is not merely technical — it directly relates to the engineering skills the course intends to teach, as emphasized explicitly.

### 9.3.5 The Gatekeeper Pattern & Three Layers of Defense
9.3.6. A `Gatekeeper` architecture is required — the same defensive layer needed to prevent severe failures: raodmail spamming or hitting Google's `Rate Limit 429`. It is recommended to implement the network communications module together with a `Rate Limit`, `Watchdog`-family reliability patterns, and the `Deadline Tracker` discussed in Ch.8 — the whole is composed of **three cumulative protection mechanisms**:

9.3.7. **Terminology clarification: three kinds of "token"** appear in this project, and must not be confused:
   - **Token Bucket (rate limiting)** — capacity units accumulated in a component that limits sending pace. Unrelated to the language model at all.
   - **LLM tokens** — units of consumed text in every LLM read call, counted and budgeted per Step-0 cryptographic seal (Ch.5).
   - **OAuth tokens (Refresh Token / Access Token)** — Gmail authorization/approval tokens (App. A).

9.3.8. **Quota Manager**: tracks the number of operations performed on a given day and prevents crossing the daily safety threshold — the last line of defense against account lockout: if the quota is exhausted, even an additional request never leaves the box.
9.3.9. **Token-Bucket Rate Limiter**: the algorithm limiting the pace of API request firing. **[MUST]** every report requires a "rate token" valid for a defined time window; the token allowance blocks sending. This way, burst-flurries that could ignite a `429` immediate-block are avoided. **Not** to be confused with LLM tokens.

#### 9.3.10 Mandatory Token-Bucket Rule (mathematical formula)
```
tokens ← min(C, tokens + r·Δt),     allow ⟺ tokens ≥ 1
```
| Term | Meaning | Practical implication |
|---|---|---|
| `C` (capacity) | maximum number of tokens the bucket can hold | bounds the size of the burst allowed — can send "all at once" after a quiet period |
| `r` (fill rate) | number of additional tokens per unit time | the sustainable average pace, must remain safely under Google's API quota |
| `Δt` (elapsed time) | time since the last update | the more time between reports, the more the bucket refills, enabling future bursty capacity |
9.3.11. **[MUST]** A report is allowed only if `tokens ≥ 1` after refill; otherwise, the sender must back off (`back off`) and wait for the next window. Choosing `C` and `r` is a balance between the number of legitimate reports vs. safety margin against the provider's quota — reducing `C` cuts reports too aggressively; setting `r` too high risks tripping the API limit.
9.3.12. **DOS/Anomaly Detector**: identifies abnormal send-repetition patterns hinting at a bug or an infinite loop in the agent's code (analogous to `backpressure` and `circuit breaker` patterns from systems development), and locks the entire API pathway on anomaly detection, preventing exhausting the account's computational resources by an unresponsive code path.

### 9.3.13 Iron Rule: `Rate Limit 429` & Deterministic Reporting
9.3.14. **[MUST]** Rate limiting & quota — Google's Gmail API returns HTTP `429 Too Many Requests` on rate-limit violation. This is a temporary error, not a permanent failure — blind retries could exacerbate quota exhaustion. Report format must be uniform JSON, machine-parseable. On receiving a `429`, back off and wait for the next time window.
9.3.15. **[FORBIDDEN]** Sending an open, free-text report — must be sent as a JSON attachment only, not free text (unparseable text will cause the report to be rejected and score zero).

### 9.3.16 The Mandatory Signed Report — JSON Format
9.3.17. **[MUST]** The end-of-match report is **not free text**; it is sent as a **single, mandatory, uniform JSON** attached to the email. It includes all identity details of the team: cryptographic identity of both teams, their GitHub repo URLs, their FastMCP server URL, a hardware-declaration cryptographic timestamp of the match, mutual sign-off (score-agreed) approval, and a SHA-256 of the match log.
9.3.18. **[MUST — mandatory obligation of two separate reports]**: at end of match, both teams must agree on the outcome, and **each team must independently send its own separate summary report** in the exact mutually agreed format. **A report is not a matter of trust between rivals — it is post-hoc-verifiable proof.** If only one report is received, that side alone is not credited toward league scoring — even if the other side won on the board! Enforcement mechanism prevents unfairness in reporting.
9.3.19. **[MUST]** The whole report is sent as a JSON file, and a full example is attached to the book (see App. B's `[results file]`). Actually **four JSON files** cover the full lifecycle of a match, each with its own filename variable defined in the mandatory parameters table (App. F / §14, Table 20):

| Config-file variable | Content & Role |
|---|---|
| `[declaration file]` | Pre-game declaration: all fixed match data — teams, members, repos, hardware, LLM model, token/time budgets |
| `[config file]` | Agreed configuration: the cryptographically-locked match parameters |
| `[log file]` | Match log: for cryptographic audit in a replay simulator |
| `[results file]` | Final result report: for league-score weighting by the lecturer |
9.3.20. Actual filename pattern (from App. F, Table 20, using `<game_id>` and per-sub-game `g<NN>` suffixes so files never mix across different matches):
   - `declaration_<game_id>.json`
   - `config_<game_id>_g<NN>.json`
   - `log_<game_id>_g<NN>.json`
   - `result_<game_id>.json`
9.3.21. **[MUST]** Mutual comprehensive log audits must be performed at the end of every game as a precondition before the JSON outcome is finalized.
9.3.22. **[MUST]** Teams must precisely declare, in real time at the start of every game, the exact number of games actually played so far — a precondition for computing the real diversity factor, and must match the outcome JSON actually agreed by the two teams at the start of each game — a precondition to computing the real competitive factor.

### 9.4 GitHub Submission: Structure, Contents, Two Repositories
9.4.1. **[MUST]** Submission takes place on GitHub. **Every repo must be reachable by the lecturer**: either fully public, or shared explicitly with `[lecturer's address]`. **Each team must submit two separate repositories** — one for the cop agent, one for the thief agent — and supply **two cross-links**: a link from the cop repo to the thief repo, and vice versa.
9.4.2. **[MUST]** Each repo's `README.md` must include a link to the sibling repo of the same team.
9.4.3. **[MUST]** The submitted results JSON (at match end) must include **all four** cross-reference links: the two repo links of Team A and the two repo links of Team B.

### 9.4.4 Mandatory Repository Contents
9.4.5. **[MUST]** Every GitHub repo must contain, at minimum: `README.md` (academic report, see §9.4.6 below); config files (`/config`); Product Requirements Definition files (`PRD`) used to build the code; a `PLAN` work-plan document; and `TODO` task files. These allow a grader to retrace the development story and reconstruct the working process — not just review the final output. Full submission guide — branches, tag, version, and checklist — is centralized in App. C (§16 below).

### 9.4.6 README.md Contents (Mandatory Academic Report Structure)
9.4.7. **[MUST]** The heart of the intended submission is the academic report inside `README.md`, in every repo. This is not a bare instructions file, but an academic-quality document explaining decisions, deeply justifying them, and presenting empirical evidence for their success. The following list details the required components — **omission of any one of them is grounds for docking points off the submission**:
   1. **The chosen Dec-POMDP model.** Scientific description of the formalism used to model the chase — the state space, observability, and uncertainty — as explained in Ch.1.
   2. **FastMCP orchestration dilemmas.** Discussion of development tensions around agent-to-agent communication orchestration: turn management, network-failure handling, and how strategies were implemented (Ch.2, Ch.8).
   3. **Details of the decision-making mechanism and the roles/parameters chosen** for `Gatekeeper` and `Orchestrator` (Ch.2, Ch.8): heuristics (Manhattan distance, Bayesian belief map), an LLM-based strategy, or (as one optional possibility) `Q-Learning` (Ch.6).
   4. **Learning curves (if RL was used).** If a team trained an agent using reinforcement learning, presenting the learning curves is a meaningful piece of evidence for productive convergence of the policy.
   5. **Mandatory screenshots — absolute obligation:** the belief-map heatmap from the Live GUI, and the Replay App usage demonstrating a `Verified OK` stamp (Ch.7).
   6. **Link to the sibling repository.** Link to the second (cop/thief) GitHub repo of the same team, as required above.

---

## 10. Chapter 10 — Recommended Development Priority Order & Process

**Chapter goal (explicit):** understand why a complex system must be built in staged, layered fashion and not all at once; what the recommended priority order for development is, seven stages by seven PRD files; the recommended milestone path and development discipline before advancing to the next stage; why skipping ahead to encryption or cloud exposure before the foundation is proven is a recipe for failure.

### 10.1 Why Build in Layers
10.1.1. The biggest risk of a beginning developer is starting to build the full system's final, most impressive part — the cloud exposure, the neural network, the machine intelligence that weaves lies — before verifying that the basics work. A distributed system is not a tower built floor-by-floor from the roof down.
10.1.2. What is the risk of placing the cloud-exposure layer before base logic was thoroughly proven? If a leaked secret is discovered later, you may not know whether the fault is in cryptography, in the server, or in basic logic itself — a proliferation of unproven variables turns any obstacle into an untraceable investigative nightmare.
10.1.3. **[MUST] The `Incremental Delivery` principle** — cumulative supply — each shipped layer must be built, tested, and validated end-to-end **before** the next layer sitting on top of it is added. Thus at every given moment, the space of possible failures narrows to only the most-recently-added layer.
10.1.4. On the other side of the same principle stands **Production Readiness**: a system is not considered fully ready to ship when it is complete on the developer's own laptop, but only when it stands up under failures, under load, and under real-world network glitches. Both principles are the load-bearing pillars for the priority order presented below — built cumulatively, and prepared to fail gracefully at every step of the way.

### 10.2 Recommended Layer-Building via PRD Files
10.2.1. **[RECOMMENDED]** The recommended way to implement the layered build is to split the software specification into several separate **Product Requirements Document (PRD)** files, one per layer. Start from the first `PRD`, produce it, test and validate the layer it defines separately, checking that the code runs correctly, before ever adding the next `PRD`'s layer atop it.

### 10.3 Table 3 — The Seven Development Priorities (mapped to the book's chapters)

| Stage (PRD) | What's built | Relevant chapter |
|---|---|---|
| 1 | Grid `[board size]`, movement rules, barrier set `[max barriers]`, capture detection | Ch.3 |
| 2 | FastMCP server, geometric tools over `Localhost` | Ch.2 |
| 3 | First strategy module: heuristics, LLM policies, or (optional) Q-Learning/heuristic | Ch.6 |
| 4 | Natural-language scent equations, decay, LLM integration for deception | Ch.4, Ch.6 |
| 5 | Transition to public URLs and tunneling (`ngrok`/`Localtonet`) | Ch.2 |
| 6 | Commit-Reveal, Nonce, hardware declaration (Step-0) | Ch.5 |
| 7 | Gmail API, GUI, Replay App | Ch.9, Ch.7, App.A |

10.3.2. **[MUST NOT skip ahead]**: do not attempt cryptography or cloud exposure before the foundational logic and basic MCP infrastructure over `Localhost` are proven end-to-end. A skipped layer risks costly time loss: fixing a fault deep in unstable foundations costs far more, and wastes hours investigating a source that may not even exist yet. It's recommended to build the layers bottom-up.

### 10.4 Milestones & Development Discipline
10.4.1. **[MUST]** For every recommended stage, define a binary, verifiable checkpoint ("milestone"): a criterion that must be true **before** advancing to the next stage. A milestone is **not** "the code was written," but "the end-to-end-observed behavior actually happened" — precisely the spirit needed to produce production-readiness — a list of every mandatory rule (do/don't/recommend) is centralized in App. E (§15).

### 10.4.2 Milestone Sign-off Checklist (from the book, per stage)
Every item on this list must be observed and confirmed **before** advancing to the next stage:
- **Stage 1**: two agents legally move on the grid `[board size]`; barrier placement per `[max barriers]` blocks movement; capture detection works.
- **Stage 2**: a geometric message sent from agent A over `Localhost` is received correctly and decoded properly at agent B.
- **Stage 3**: given a known target position, the computing agent executes the shortest path without any manual intervention.
- **Stage 4**: reporting in free-form language subject to word-count limits; a scent map suitable for viewing; the LLM produces a hint each step (true or lie).
- **Stage 5**: an agent on a remote machine connects via `ngrok` and gameplay is updated correctly per step (LLM active in the loop).
- **Stage 6**: the move must be committed via `Commit` and only then revealed via `Reveal`, with `Nonce`; correct `Step-0` hardware declaration.
- **Stage 7**: a match summary sent via Gmail; GUI shows the state; the Replay App replays a captured match correctly.

---

## 11. Chapter 11 — Summary & Looking Forward

**Chapter goal (explicit):** understand why the running logic of a single agent must be independent, and never lean blindly on the LLM for spatial computation; why the project is a systems-development exercise, not a coding exercise; understand the four success metrics and their meaning; complete a final pre-submission checklist covering the entire book — do not stop mid-stage before checking off each item as it progresses.

### 11.1 The Arc of the Book: From Uncertainty Modeling to a Live League
11.1.1. When we opened the book, we modeled the P2P race as a Dec-POMDP: two distributed agents, a combinatorial state space, and partial observability lying at the heart of uncertainty (Ch.1). We saw the leap the course requires from lectures on single/multi-agents, through inter-agent communication via MCP, to full autonomous multi-agent independence.
11.1.2. On this infrastructure we built the decision-making brain. We saw three algorithmically equal decision tracks — heuristics, learning, and your own custom algorithm — all of which leave movement-decision authority with the algorithm (Ch.6). We built the pheromone-trail mechanism, itself directly inspired by ants, showing how each side builds a belief-map estimate of a hidden rival from within scent trails (Ch.4), and how the language model serves only the verbal layer, and never global spatial computation (Ch.6).
11.1.3. We saw a symmetric cryptographic-proof architecture (`Verified OK` / `TAMPERED`), showing how the mutual audit of match integrity is preserved (Ch.5, Ch.7). From static rules, we moved to the dynamic strategies agents deploy in order to win in this arena. We saw how each side — cop and thief — builds belief maps in a symmetric manner over the opponent hidden within the historical scent map, and how the language model serves only the verbal layer, and never global spatial computation.
11.1.4. Finally, we left the lab and went out to the world: the live league, teams competing against other teams, and a JSON reporting of results (Ch.9). Every layer built on top of the previous, until the tower stood whole.

### 11.2 The Project as Systems Development, Not a Coding Exercise
11.2.1. What separates a coding exercise from a systems-development exercise? A coding exercise proves itself against known, expected input in a sterile lab environment, where neither the input nor the rival is unpredictable. A system, by contrast, is measured in a noisy world: dropped connection lines, a slow clock, a stubbed local URL that disconnects mid-route. **[MUST]** you must handle all of it, at once, in the same season.
11.2.2. This understanding needs to be internalized from here on: your code quality is judged not by whether everything is perfect, but by whether it degrades gracefully. An agent that beats a rival in simulation without genuinely solving the problem, but merely finds an exploit to cheaply solve its version — is not the intended outcome. This distinction separates being a coder from being a systems developer.

### 11.3 The Four Metrics of Success (restated, mandatory grading axes)
11.3.1. **[MUST]** — success is judged against four independent metrics, each an independent facet, not a single winning/losing outcome — measured as: does your system truly know how to coordinate with a side beyond its control? Does it adapt when information is only partial? Does it stay honest even when payoffs are on the line? Does its architecture hold up under load? An agent is judged positively across all four — not merely the race.

### 11.3.2 Table 4 — Success Metrics of the Project and Submission Criteria
| Metric | Realization in the project | Chapter |
|---|---|---|
| **Coordination** | P2P turn management, FastMCP protocol, agent synchronization with no central referee | Ch.2 |
| **Adaptation** | Both agents build a symmetric belief about the opponent under uncertainty: each side builds a belief from scent + (possibly deceptive) verbal hints, and updates a probabilistic belief map | Ch.4, Ch.6 |
| **Integrity** | Fraud prevention via SHA-256 + Commit-Reveal, and full mutual audit | Ch.5 |
| **Architecture** | Adherence to Gatekeeper + Orchestrator design patterns, code resilient to failure | Ch.8, Ch.10 |

### 11.4 Final Pre-Submission Checklist (comprehensive, mandatory)
Before sending the project, make sure every layer built throughout the book actually functions end-to-end. The following checklist maps every requirement to the chapter it derives from — go over every single item, marked as done, not merely "probably":

- **[MUST] Base logic works**: the game engine runs a complete match with no crash, and scoring rules obeyed correctly (Ch.3).
- **[MUST] FastMCP with public URL**: two agents connect over a P2P protocol through a reachable address, not merely over `localhost` (Ch.2).
- **[MUST] Commit-Reveal & audit pass**: the commit-reveal-and-audit mechanism is active, and the audit completes successfully with no fraud/tampering detected (Ch.5).
- **[MUST] Scent map & belief map**: pheromone-trail mechanics implemented, and the belief map computed and influencing decisions in practice (Ch.4, Ch.6).
- **[MUST] Live GUI & Replay App with `Verified OK`**: display tools present the match in real time and in replay, with proper integrity stamps (Ch.7).
- **[MUST] JSON report via Gmail between both sides**: at match end, both teams agree on the outcome, and each separately sends its own end-of-match summary as a well-formed JSON via Gmail API (Ch.9). If one side does not send a report, that side is not credited for that game. See App. A for OAuth requirements.
- **[MUST] GitHub repo with Git Tag and academic README**: code tagged, ordered README per the required structure (Ch.9, App. C).
- **[MUST] At least `[min games to pass]` games vs. different opponent teams**: minimum number of distinct-opponent games completed in the live league (Ch.9); check the shared config file and mandatory parameters table (App. F).

### 11.5 Looking Forward: Toward Decentralized Autonomous AI
11.5.1. The race you have built is a small model of a much larger question troubling the artificial-intelligence field in the coming decade: how can multiple autonomous, un-trusting-each-other entities, that don't see the full picture and are not subject to central control, act together and coherently, in real time? This is not a purely theoretical question — it lies at the heart of the domain of distributed multi-agent AI systems, where multi-agent reinforcement learning is only one of the optional tools, one among several equally-legitimate algorithmic tracks, seeking to squeeze potential out of these types of systems.
11.5.2. If one thing should stay with you from this project, it is: a good system is not a collection of smart agents — it is an architecture that enables mediocre agents to act together in trust, in adaptation, and in resilience. If your project succeeded in matching this ability — to adapt, preserve integrity, and develop correctly — take this outside the book with you: the world of decentralized autonomous multi-agent AI has only just opened before you; you now have the tools to build in it, and not merely to use it. Go build it.

---

## 12. Appendix A — Gmail API & OAuth 2.0 Setup Guide

### 12.1 The Five Setup Steps

12.1.1. **Step A — Open the project and enable the service.** Go to Google Cloud Console; create (or select) a project. Within the project, go to the API library and explicitly enable the **Gmail API** service. This activation is what marks your Google project as officially authorized to call the mail service's endpoints.

12.1.2. **Step B — OAuth Consent Screen setup.** Define the consent screen through which the user is informed which app is requesting authorization. Choose `External` (for users outside the org) or `Internal` (for a Google Workspace org), and add the students' testing-user email addresses to the **Test Users** list — only listed users can complete the authorization flow while the app is in `Testing` status.

12.1.3. **Step C — Scope restriction to minimum necessary.** Define the authorization scope to the exact minimum needed: `https://www.googleapis.com/auth/gmail.send` — this scope permits only email *sending*, and grants **no** read authorization whatsoever. This is a data-security-minimization principle — the fewer permissions a token has, the smaller the damage if it leaks.

12.1.4. **Step D — Create Credentials.** Under Credentials, create an `OAuth Client ID` of type `Desktop Application` and download the `credentials.json` file to your project's local working directory. **[MUST]** add this file to `.gitignore` **before** pushing code to GitHub, to prevent leaking a secret shared with the entire world (in a public repo), or even just with the lecturer (in a private repo). Forgetting this step is one of the most common and most dangerous mistakes in cloud-based projects.

12.1.5. **Step E — First authorization flow.** On the code's first run, Google's official libraries open a browser window and ask you to authorize the requested access. On completing authorization, a `token.json` file is automatically created containing a short-lived `Access Token` alongside a long-lived `Refresh Token`; thanks to the `Refresh Token`, the agent can send reports fully automatically for many months without further human intervention.

### 12.1.6 Critical: Never Push Secrets to a Repository
12.1.7. **[MUST]** `credentials.json` (the app's secret identity) and `token.json` (the signed access tokens) are secrets. Pushing them to GitHub is equivalent to publishing your mailbox login key to the public. **[MUST]** add both `credentials.json` and `token.json` to `.gitignore` before the first `commit`. If a secret was accidentally pushed even once, remember: deleting it from the current code is not enough — you must rotate the credentials in the console (revoke and reissue).

### 12.2 Refresh Token vs. Access Token — Anatomy
12.2.1. **Access Token** — short-lived (typically expires within about an hour), attached to every API request, and authorizes the operation in practice. Its short lifetime shrinks the risk window if it leaks.
12.2.2. **Refresh Token** — long-lived, never sent to the mail API itself, but used solely to obtain a new `Access Token` once the old one has expired. This is the token that grants the agent long-term autonomy as long as the `Refresh Token` is valid — no repeated human intervention is needed.
12.2.3. **Least Privilege principle**: request only the `gmail.send` scope, never a broader scope like `mail.google.com` or `gmail.modify`. This is a direct application of the least-privilege principle: grant a component exactly the authorization it needs for its task, no more. The reporting agent only ever needs to *send* mail — there is no reason it should ever be able to *read* or *delete* mail. Scope reduction turns a stolen token into a nearly harmless, limited-capability key.

### 12.3 Minimal Send-Only Python Flow Implementation
12.3.1. **[MUST]** Use the minimum required scope only (`gmail.send`), per the Least-Privilege principle. Full mandatory flow: load the `token.json` Nonce (or create it on first run via the authorization flow), build a Gmail service, construct a MIME message, and send it — with the scope pinned to `gmail.send` only, per the least-privilege principle.
12.3.2. Provided reference code implements `get_service()` (reuses `token.json` if present, otherwise runs the consent flow once) and `send_report(service, to_addr, subject, body)` (builds a plain-text MIME message, base64url-encodes it, and calls `service.users().messages().send(...)`).
12.3.3. On first run, `InstalledAppFlow.from_client_secrets_file(...)` handles the token-request flow that creates `token.json`; on all subsequent runs, the flow reuses and automatically refreshes the existing token.

### 12.4 Required Files Summary

| File | Source | Content | Add to `.gitignore`? |
|---|---|---|---|
| `credentials.json` | Downloaded from console | App's secret identity | **Yes — mandatory** |
| `token.json` | Created on first run | Access + refresh tokens | **Yes — mandatory** |

---

## 13. Appendix B — Unified Configuration File Format

### 13.1 Why a Constitution Document in a Judge-Less World?
13.1.1. In a P2P game where two agents communicate directly and there is no central authority, a fundamental question arises: who determines the physics rules of the game? When a central server exists, it alone enforces board size, max moves, and scent decay rate, and both players obey its decisions. But absent one, if each side runs its own local copy of game logic, and the two copies don't agree on exactly the same values, the match splits into two contradictory realities that cannot be reconciled.
13.1.2. **[MUST] The practical solution**: turn all agreed game conditions into a single, readable, open, signed source of truth — the config file `config/game.json` — **the signed constitution** of the match. This file is not just a collection of constants: it is a **contract** both sides agree to before the screen even loads, and each side holds it in a hash-locked cryptographic signature, byte-for-byte matching the other side's copy.
13.1.3. Each side, in addition, keeps a private per-peer file `config/game.toml` — local settings only (network port, strategy module choice, LLM mode for the verbal game, team identity, or an email destination) that are **not** negotiated and need **not** be identical between sides. When the board, boundaries, and decay rate are all shared, then even though no third party truly enforces the physics, the two agents impose exactly the same physics on each other: their private `TOML` file's values are overridden (`overlay`) by the shared, matching `JSON` values wherever a conflict would occur, so both sides compute the same result from within the same shared rules.
13.1.4. Additional benefit: **Configurability** — separating parameters from code allows changing match conditions (larger grid, tighter time limit, wider scent field, tighter movement rules) without touching a single line of logic code.
13.1.5. Values shown throughout the book are the book's own default agreed baseline; each can be renegotiated at every fresh match (`per-match`), as long as both sides agree on the same value from within the same rules. A full example of the JSON config structure is attached as `[config file]` (see the table in App. F / §14, Table 5 there).

### 13.2 When JSON, When TOML — and Why
13.2.1. The project uses two config formats, each with a distinct role: the simple distinction — **anything both sides must agree on is written in JSON; anything that is purely local and personal is written in TOML.**
13.2.2. **JSON — for shared, sealed, unchanging data.** Written in this format: (a) the game's static conditions — `config/game.json` (b) the pre-game declaration, config, log, and results files — the four standard files (Ch.9); (c) the rate-limit config — `rate_limits.json`. JSON is chosen because it is an unambiguous cross-language standard, can be canonically serialized (sorted keys, fixed separators), and lends itself to consistent (`config_sha256`) hashing, matching byte-for-byte between competing teams or teams writing in different languages. Anything that could affect the other side's proof of truth must be here.
13.2.3. **TOML — for private, local config only.** Written in this format: the per-peer private file `config/game.toml` — port, opponent URL, strategy-module selection, LLM model mode, hardware, and the team's email destination. TOML is chosen because it is read by humans, supports comments distinctly, and readers claim it as a decisive advantage — sections like `[strategy]` and `[trash_talk]` contain the code-explaining comments guiding the student. This file is private, does not cross the network, and therefore need not be canonical-serializable/hashable. **No relevant value the rival needs is found in it**; if any value becomes shared, it moves to JSON.

12.2.4. **Test of decision**: ask "must the rival agree to this value, or trust me on it?" — if yes, it belongs in the shared JSON, otherwise it stays in your private TOML.

### 13.3 The Signed Shared File — `config/game.json`
13.3.1. Below is the shared, locked config file that both sides own copies of on their sections: board and agents (`board_and_agents`), movement and barriers (`movement_and_barriers`), scoring (`scoring`), pheromones (`pheromones`), network and league (`network_and_league`), and rate-limiter Gatekeeper (`rate_limiter_gatekeeper`). Both peers claim an identical byte-for-byte copy and cryptographically lock it before any exchange of signatures with the game refusing to play on any mismatch.

```json
{
  "schema_version": "1.2",
  "agreed_between": ["group-a", "group-b"],
  "board_and_agents": {
    "grid_size": 7,
    "num_agents": 2,
    "thief_start": [3, 3],
    "cop_start": [0, 0],
    "axis_origin_corner": "top-left",
    "axis_start_index": 0
  },
  "world": {
    "map_area": "New York",
    "hint_max_words": 15
  },
  "movement_and_barriers": {
    "move_set": ["N", "S", "E", "W", "STAY"],
    "max_barriers": 14,
    "max_moves": 35,
    "survival_threshold": 35
  },
  "scoring": {
    "capture_cop": 20, "capture_thief": 5,
    "survival_cop": 5, "survival_thief": 10,
    "tie_score": 2, "technical_loss": 0
  },
  "pheromones": {
    "pheromone_center_intensity": 0.9,
    "pheromone_decay": 0.10,
    "pheromone_grid_size": 5
  },
  "network_and_league": {
    "response_timeout_sec": 30, "watchdog_timeout_sec": 60,
    "num_games": 1, "diversity_reward": 10,
    "min_games_to_pass": 2, "max_games_per_team": 10,
    "token_budget_per_series": 200000
  },
  "rate_limiter_gatekeeper": {
    "requests_per_minute": 30, "concurrent_requests": 2,
    "retry_backoff_sec": 5, "max_retries": 3, "queue_depth": 100
  }
}
```

13.3.2. Field-name-to-placeholder correspondence, one to one: `[max barriers] = max_barriers`, `[board size] = grid_size`, `[cop-capture score] = scoring.capture_cop`, etc. Each value may vary between negotiations (in the rimissive direction for a parameter marked "minimum"), but field names are fixed and mandatory. Field `num_games` is sent with default `1` (single sample-game); the full league series requires `[number of games]` games.

### 13.4 The Private Per-Peer File — `config/game.toml`
13.4.1. Beside the shared JSON, each peer keeps its own `config/game.toml`, private, local, not negotiated, and not exchanged with the rival. Contains: team identity, network port, opponent's URL, strategy-module selection (`[strategy]`), verbal-game LLM model configuration (`[trash_talk]`), LLM configuration (`[llm]`), and email destination (`[email]`). Excerpt (illustrative):

```toml
version = "1.10"

[game]
group_name = "My-Team"
group_id   = "my-team"
sub_game_number = 1
members = ["id-1001", "id-1002"]
repos = { cop = "https://github.com/you/repo", thief = "https://github.com/you/repo" }

[network]
my_port        = 8802                          # MY MCP server port
opponent_url = "http://127.0.0.1:8801/mcp"      # the only thing I know about the opponent
turn_timeout_seconds = 180

# [strategy] -- optional: point at YOUR brain subclass (else the shipped heuristic runs)
# thief_class  = "my_team.strategy:MyThiefBrain"
# police_class = "my_team.strategy:MyPoliceBrain"

# [trash_talk] -- optional: HOW the banter is produced. The MOVE is always pure Python.
# provider = "template"   # template(0 tokens, default) | ollama | claude_api | claude_cli

[llm]
model = "claude-opus-4-8[1m]"       # MY choice; the opponent may differ
step_deadline_seconds = 30           # hard cap on LLM thinking per step

[email]
recipient = "rmisegal+uoh26finalgame@gmail.com"
mode = "draft"
```

13.4.2. When shared `config/game.json` values exist, they override every matching key in the private `TOML` — so the private file can never "weaken" a signed obligation. The **full mandatory dictionary of every parameter's name, meaning, and value** is centralized in App. F (§14).

---

## 14. Appendix C — GitHub Submission Requirements & Academic Report

### 14.1 GitHub Repo Structure, Branches & Tagging
14.1.1. **[MUST]** Submission infrastructure is a GitHub repo, either **publicly accessible**, or **shared explicitly with the lecturer's address** `[lecturer's address]`. Accessibility is not a technicality — it's a professional stance: the code must be written to be read, reviewed, and reproduced by others.
14.1.2. **[RECOMMENDED]** Development managed via branches — every distinct feature developed in its own dedicated branch, merged into the main branch only after being proven stable — matching development practices for distributed systems and microservices.
14.1.3. **[MUST]** The final submission version is **not** marked as "the last commit on the main branch" but by an **annotated Git tag**, documented with a message, providing an irrefutable, un-disputable timestamp in the repo's history, and allowing precise recovery of the exact code submitted — not a later version possibly written after the deadline.

```
git tag -a v1.0-submission -m "Final submission: Police-Thief P2P, group N"
git push origin v1.0-submission
git show v1.0-submission     # (optional) verify
```

### 14.2 The Academic README Report
14.2.1. **[MUST]** The heart of the intended submission is the academic report written in `README.md` at the repo root. This is **not** merely an installation-instructions file, but an academic-quality document that explains the design decisions, justifies them in depth, and presents empirical evidence of their success.
14.2.2. **[MUST — five required components]** (per Ch.9.4.6/14.2.3 above, restated here as the exact required README content list): (1) the chosen Dec-POMDP model; (2) FastMCP orchestration dilemmas; (3) decision-mechanism details and Gatekeeper/Orchestrator role/parameter choices; (4) learning curves (if RL used); (5) mandatory screenshots — belief-heatmap GUI + Replay App `Verified OK`; (6) link to the sibling repository.
14.2.3. **[MUST]** Never push secrets to a repo — whether public or private-shared-only. This is repeated explicitly as a submission-blocking security failure (see §15 rule 39/40 below).

### 14.3 Submission Checklist Table
14.3.1. Every item below must be verifiably `done`, not merely "probably," before the submission tag is created.

| Item | Required status |
|---|---|
| Two GitHub repos (cop, thief) accessible to the lecturer | Public or private-shared with lecturer |
| Cross-link between the two repos + two links in submission JSON | Present |
| `v1.0-submission` Git tag | Pushed |
| README.md components (Ch.9) | Complete in both repos |
| Belief-map heatmap (GUI) screenshot | Attached |
| Replay screenshot with `Verified OK` | Attached |
| At least 2 games vs. different opponent teams | ≥2 |
| End-of-match Gmail JSON — each team sends separately | Both sides sent |
| No secrets leaked to the repo (`.gitignore` present) | Confirmed |

---

## 15. Appendix D — Example Code Repository (Basic Simulation)

15.1. Attached alongside the book is an **open, public, basic-implementation example code repository**, shared with all students in the course, on GitHub. **[MUST NOT be treated as a submission template or a shortcut to bypass building your own solution]** — using it as-is to submit is explicitly against the intent of the assignment.

### 15.2 What the Example Shows
15.2.1. The repo runs two independent peers (cop/thief), each with its own separate FastMCP server and its own config file, precisely as two students would run two machines competing against each other. It demonstrates: board movement, barrier placement, scent-trail mechanism, belief-map computation, Commit-Reveal protocol over SHA-256 with full end-of-match audit, token consumption tracking, and a JSON draft report sent to Gmail. The strategic decision logic remains deliberately minimal — the goal is to show the "chassis," not the "brain," which you're expected to build.

### 15.3 Code Layout
15.3.1. Per the repo's `README.md`, the architecture is layered:
   - `SimulationSdk` — a single business entry point.
   - `PeerRuntime` — one independent peer: receiving and sending → turn loop → audit.
   - `domain` — board, scent, belief, state, rules, cryptography, protocol, and the decision "brain."
   - `infra` — supplies the LLM model for the verbal game (default is an offline template; or `Ollama` local, cloud/`CLI`), MCP transport to the opponent's server, and Gmail sending.
   - `shared` — config manager, rate-limiter, run/system metadata & version.
15.3.2. Every file is short (up to ~150 lines of code), development accompanied by tests (`pytest`), full separation of `config/thief/` vs `config/police/`, all external config clearly separated in the private config file. **Two extension points for students** are clearly separated in the private config file's `[strategy]` section: `police_class`/`thief_class` pointing to the student's own "brain" derived from `BrainBase` overriding `_pick_move` (and, for the cop, also `_decide_move`) and the `[trash_talk]` section choosing how the deceptive text is produced (default: `template` — zero tokens). **The move itself is always computed in pure Python code; the LLM concerns only the verbal layer.**

### 15.4 How to Run
15.4.1. Example commands:
```
uv sync
# Terminal 1
uv run python -m police_thief peer --role police
# Terminal 2
uv run python -m police_thief peer --role thief
# Replay a saved match:
uv run python -m police_thief replay --log logs/police_match.json
```
15.4.2. **[RECOMMENDED TIP]** turn the repo into a "chat-with-the-code" tool via NotebookLM: convert all repo files to text format (`.txt`), upload them to NotebookLM, and ask the AI questions about the code directly ("where is the belief map computed?", "how is Commit-Reveal enforced?") to understand components quickly without reading the entire repo linearly.
15.4.3. **[STRONGLY RECOMMENDED]** produce a **Performance Analysis Research Report** (`docs/RESEARCH-REPORT-Performance-Analysis.md`) analyzing your own agent's resource consumption: how many LLM calls per full turn sequence, how they scale against rate-limits (RPM and time windows) of different providers (Ollama, ChatGPT, Gemini, Claude, Grok — even free/paid tiers), and how the fallback mechanism ensures a game always finishes even when a provider is blocked. Use it to plan and visualize your own architecture: choose the strategy and LLM model that fits your resource budget, and understand where the "bottleneck" is likely to sit — then go back and rebuild on your findings, not guesses.

### 15.5 Usage Terms
15.5.1. You are allowed to reuse and modify parts of this code for your project's needs. Two ground rules apply: (1) the repo is a **learning starting point**, not a submission template — your own solution must stand fully against the complete specification; (2) the repo's license is an **educational use license** (see `LICENSE`). Anywhere the repo diverges from the book, **the book and the Mandatory Parameters Table always override**.

---

## 16. Appendix E — Complete Mapping of Mandatory Rules (Do / Don't / Recommend), All 55 Rules

Each rule below is tagged **[MUST]**, **[FORBIDDEN]**, or **[RECOMMEND]**, with the consequence of violation as stated in the source, organized into the book's own six categories.

### 16.1 Network architecture, decentralization & local epistemology
1. **[MUST]** Run cop code and thief code as two fully separate processes. *Consequence: total disqualification; breaks the Zero-Trust model.*
2. **[FORBIDDEN]** Share memory or state variables between the two sides at all, at all costs. *Consequence: instant, non-negotiable disqualification for information leakage.*
3. **[MUST]** Define the Orchestrator component as the single entry point for all sub-systems. *Consequence: architectural instability, technical-loss risk.*
4. **[MUST]** Manage game phases via a legal state machine. *Consequence: technical loss from undefined-state deadlock.*
5. **[MUST]** Reject any attempt to transition to an illegal state in the state machine. *Consequence: logic error propagating to a disqualifying failure.*
6. **[MUST]** Implement a Deadline Tracker to prevent deadlock while awaiting the opponent. *Consequence: system hang / timeout-based loss.*
7. **[MUST]** Run a Watchdog monitoring the main process for crashes, with controlled data flush. *Consequence: process crash & loss of official record.*
8. **[MUST]** GUI displays only local truth for the running side. *Consequence: disqualification for tracking illegal information flow.*
9. **[FORBIDDEN]** Display the full objective board state in the live GUI. *Consequence: disqualification for illegitimate advantage.*
10. **[MUST]** Use tunneling tools to expose the local server to the public internet. *Consequence: inability to compete in the live league against opponents.*

### 16.2 Spatial mechanics, physics & board layout
11. **[MUST]** Ensure the config file is identical, byte-for-byte, on both sides. *Consequence: disqualification for breaking symmetry.*
12. **[MUST]** Load minimum parameter values from the parameters table only; never reduce them below the floor. *Consequence: disqualification for deviating below the minimum-threshold requirement.*
13. **[MUST]** Move only in orthogonal directions. *Consequence: illegal move → technical loss.*
14. **[FORBIDDEN]** Execute illegal moves. *Consequence: move rejection by the opponent → technical loss.*
15. **[MUST]** Declare every barrier placement publicly. *Consequence: automatic board falsification loss upon audit.*
16. **[FORBIDDEN]** Lie about barrier placement location. *Consequence: severe disqualification cause.*

### 16.3 Cryptography, integrity & zero-knowledge proof
17. **[MUST]** Use the SHA-256-based commit-reveal handshake protocol. *Consequence: missing mechanism → solution illegitimacy.*
18. **[MUST]** Keep the Nonce secret until game end. *Consequence: disqualification for exposing the protection against dictionary attacks.*
19. **[MUST]** Fail the match on any audit-stage hash mismatch. *Consequence: violates the "iron law" written from Step-0 for the offending team.*
20. **[MUST]** Build a replay/audit application to reproduce and verify the match. *Consequence: pre-condition for review approval and project submission.*
21. **[MUST]** Announce capture claims only when true. *Consequence: immediate disqualification for reality falsification.*
22. **[FORBIDDEN]** Falsely announce capture. *Consequence: immediate disqualification, zero-score, no appeal.*
23. **[MUST]** Lock the scent-emission-model formula cryptographically before game start. *Consequence: mid-game deviation invalidates the match.*
24. **[MUST]** Perform a cryptographic Step-0 hardware declaration before game start. *Consequence: loss of eligibility for the computational-fairness bonus.*

### 16.4 Strategy, language & public network
25. **[RECOMMEND, not strictly enforced]** Do not hand the actual move decision to the LLM; use it for text/deception only. *Note: not a strict rule per se, but blind trust risks hallucinations, illegal moves, and technical loss; deviation IS allowed by explicit mutual documented agreement of both teams.*
26. **[MUST]** Conduct free-text communication in natural language only. *Consequence: keeping the psychological-challenge character of the project.*
27. **[FORBIDDEN]** Use direct numeric-coordinate protocols. *Consequence: disqualification for breaking the game's defined nature.*
28. **[MUST]** Implement a token-bucket-based rate limiter to send reports to Gmail. *Consequence: prevention of `429` blocking of the team's reports.*
29. **[MUST]** Define a DOS/anomaly detector to protect network resources. *Consequence: prevention of the reporting account being blocked.*
30. **[MUST]** Use send-only permission scope for the Gmail interface in code. *Consequence: severe security-scope violation → disqualification.*

### 16.5 League fairness, admin procedures & competition integrity
31. **[MUST]** Each team plays a minimum number of games vs. distinct opposing teams. *Consequence: ineligibility for a passing score below the minimum.*
32. **[MUST]** Automatically report every match's results via Gmail. *Consequence: missing report invalidates that game's credit.*
33. **[MUST]** Structure the match report as a valid JSON data object. *Consequence: free-text/non-parsable report is rejected.*
34. **[FORBIDDEN]** Send end-of-match report as free text; only as a JSON attachment. *Consequence: non-JSON report treated as a zero-score credit failure.*
35. **[MUST]** Both teams agree on the outcome and each sends a separate final report. *Consequence: one missing/conflicting report from either side disqualifies that match with a 0 score for both sides. Enforcement mechanism prevents unilateral advantage in reporting.*
36. **[MUST]** Conduct comprehensive mutual log audits at the end of every match. *Consequence: mandatory pre-condition before the JSON outcome is finalized.*
37. **[MUST]** Precisely declare the number of games already played, in effect, at the start of every match. *Consequence: precondition for computing the real diversity factor.*
38. **[FORBIDDEN]** Falsely declare game counts to opponents. *Consequence: false declaration disqualifies the project entirely upon discovery.*
39. **[FORBIDDEN]** Push secrets and credentials to any repo — even if private and shared only with the lecturer. *Consequence: severe security failure in the project.*
40. **[MUST]** Add authorization/secret files to `.gitignore`. *Consequence: mandatory protection against leaking Gmail API credentials.*
41. **[MUST]** Tag the final submission version with a documented, annotated Git tag. *Consequence: allows the lecturer to review the exact final version.*
42. **[MUST]** Attach a comprehensive academic README report to the repo (model description, dilemmas, strategy, RL amounts and locations). *Consequence: without the report the project is not academically complete.*
43. **[MUST]** Submit deliverables as a Word/PDF file, keep field layout, don't move fields. *Consequence: precondition for score assignment.*
44. **[MUST]** Submit the assignment as a separate file per team member. *Consequence: a team member without a personal submission won't be scored.*
45. **[MUST]** Encode team identity as an 8-character unique code without spaces. *Consequence: prevents automated report-attribution mismatch.*

### 16.6 Completions found by cross-checking the book body against the appendix summary
46. **[MUST]** A barrier is placed on the cell the cop occupies at the moment of placement (that instant counts toward capture). *Source: Ch.3.*
47. **[MUST]** A thief that leaves the arena via any illegal move counts as captured. *Source: Ch.3.*
48. **[MUST]** Every match outcome is scored per the scoring table (capture 20/5, survival 10/5, technical loss 0/0). *Source: Ch.3 + parameters table.*
49. **[MUST]** Submit two separate GitHub repos (cop, thief) with cross-linked README + four cross-links in the JSON submission for both teams. *Source: Ch.9.*
50. **[MUST]** Every repo includes at minimum: README, config files, PRD files, PLAN file, TODO files. *Source: Ch.9.*
51. **[MUST]** Automated end-of-match reports are sent to the lecturer's address `[agent's report address]`. *Source: Ch.9.*
52. **[MUST]** Each opponent match-up counts only one game (no re-farming score against the same opponent); warm-ups are allowed but don't count. *Source: Ch.9.*
53. **[MUST]** Record the commit-hash identifier in the Step-0 declaration; code may change between games but each game's own commit hash must be updated. *Source: Ch.5.*
54. **[MUST]** The final-results JSON reports the total token count consumed per game (and series). *Source: Ch.5, Ch.9.*
55. **[MUST]** Self-score **code quality only** — not the league game outcome. *Source: Ch.11.*

---

## 17. Appendix F — Complete Mandatory Parameters Table (All 10 Sub-Tables)

> Single source of truth for every numeric value in the project. **`minimum`** = teams may raise, never lower. **`fixed`** = teams may never change under any circumstance. **`by agreement`** = teams must agree via the shared signed config; the value shown is only an example unless a team overrides it by mutual consent (subject to being no lower than any applicable minimum).

### 17.1 Board, axis system & starting positions (Table 13)
| # | Parameter | Meaning | Example value | Status |
|---|---|---|---|---|
| 1 | `[board size]` | Board grid side length | 7×7 | minimum |
| 2 | `[number of agents]` | Agents in the match | 2 | fixed |
| 3 | `[coordinate axis origin]` | Which corner is (0,0) | top-left | by agreement |
| 4 | `[coordinate axis start index]` | Indexing start | 0 | by agreement |
| 5 | `[thief-start position]` | Thief's starting cell | (3,3) | by agreement |
| 6 | `[cop-start position]` | Cop's starting cell | (0,0) | by agreement |

### 17.2 Game arena & verbal hints (Table 14)
| # | Parameter | Meaning | Example value | Status |
|---|---|---|---|---|
| 1 | `[game arena]` | Real-world area theme for hints (or empty string) | "New York" | by agreement |
| 2 | `[hint word limit]` | Max words per verbal hint sent | 15 | by agreement |

### 17.3 Movement & barriers (Table 15)
| # | Parameter | Meaning | Example value | Status |
|---|---|---|---|---|
| 1 | `[movement set]` | Legal move set | 4 orthogonal directions + stay-in-place | fixed |
| 2 | `[max barriers]` | Max barriers the cop may place | 14 | minimum |
| 3 | `[max moves]` | Max moves allowed per match | 35 | minimum |
| 4 | `[survival threshold]` | Steps thief must survive to "win" | 35 | minimum |

### 17.4 Dynamic pheromones — scent (Table 16)
| # | Parameter | Meaning | Example value | Status |
|---|---|---|---|---|
| 1 | `[scent center intensity]` | Peak scent value at emission point | 0.9 | fixed |
| 2 | `[scent decay rate]` (ρ) | Fraction lost per turn | 0.10 | fixed |
| 3 | `[scent field size]` | Emission radius grid | 5×5 | fixed |

### 17.5 Scoring — win conditions & tie (Table 17, expands Table 2 in §3.4)
| # | Parameter | Meaning | Example value | Status |
|---|---|---|---|---|
| 1 | `[cop-capture score]` | Cop score on successful capture | 20 | fixed |
| 2 | `[thief-capture score]` | Thief score on being captured | 5 | fixed |
| 3 | `[cop-survival score]` | Cop score if thief survives full match | 5 | fixed |
| 4 | `[thief-survival score]` | Thief score for surviving full match | 10 | fixed |
| 5 | `[tie score]` | Score awarded to each side on a tied series | 2 | fixed |

*(`[technical loss score]` for both sides is fixed at 0/0, per §3.4/Table 2 above.)*

### 17.6 Network & league (Table 18)
| # | Parameter | Meaning | Example value | Status |
|---|---|---|---|---|
| 1 | `[number of games]` | Games per single match-up (default) | 1 | fixed |
| 2 | `[diversity reward]` | Bonus for beating a new opponent | 10 | fixed |
| 3 | `[min games to pass]` | Minimum distinct-opponent games required to pass | 2 | fixed |
| 4 | `[token budget per series]` | Max LLM tokens a team may spend per series | ~200,000 | by agreement |
| 5 | `[max games per team]` | Cap on countable games per team | 10 | fixed |

### 17.7 Rate-limiter / Gatekeeper (Table 19)
| # | Parameter | Meaning | Example value | Status |
|---|---|---|---|---|
| 1 | `[requests per minute]` | Outbound API request cap | 30 | minimum |
| 2 | `[concurrent requests]` | Max parallel requests | 2 | minimum |
| 3 | `[retry backoff seconds]` | Wait before retrying after failure | 5 sec | minimum |
| 4 | `[max retries]` | Retry attempts before hard failure | 3 | minimum |
| 5 | `[queue depth]` | Max queued requests under load | 100 | minimum |
| 6 | `[response timeout sec]` | Deadline per network response | 30 sec | by agreement |
| 7 | `[watchdog timeout sec]` | Time before Watchdog declares hang | 60 sec | by agreement |

### 17.8 Attached files, repository & addresses (Table 20)
| Config-file variable | Content & Role | Example value |
|---|---|---|
| `[declaration file]` | Pre-game declaration: all fixed match data (teams, members, repos, hardware, model, tokens, times) | `declaration_<game_id>.json` |
| `[config file]` | Agreed configuration: cryptographically-locked match parameters | `config_<game_id>_g<NN>.json` |
| `[log file]` | Match log for cryptographic audit in the replay simulator | `log_<game_id>_g<NN>.json` |
| `[results file]` | Final results report used to weight league scoring by the lecturer | `result_<game_id>.json` |
| `[example code repo]` | Reference implementation for use of `README`/`GitHub` linkage of the example simulation | `https://github.com/rmisegal/Game-P2P-Cop-Chase` |
| `[lecturer's address]` | General correspondence & GitHub repo-sharing address | `rmisegal@gmail.com` |
| `[agent's report address]` | Destination the agent automatically sends its JSON reports to | `rmisegal+uoh26finalgame@gmail.com` |

### 17.9 LLM modes for the verbal game — private, per-peer choice (Table 21)
| Mode (`[trash_talk] provider`) | Where it runs / cost | Token limit |
|---|---|---|
| `template` (default) | Pre-baked phrases in code — **zero tokens** | none |
| `ollama` | Local model, e.g. `localhost:11434` | free API tokens |
| `claude_api` | Small cloud model (e.g. Haiku) via real API | subject to `[token budget per series]` |
| `claude_cli` | Via `claude -p` (Claude Code CLI) | highest cost, subject to subscription |

*(`every_n_steps` may throttle LLM invocation to once every N turns to further reduce cost; `template`/`ollama` modes allow playing an entire league series at zero/free token cost.)*

### 17.10 Strategy module selection — private, per-peer choice (Table 22)
| Config key (`[strategy]`) | Role | How to point at it |
|---|---|---|
| `thief_class` | Your thief "brain" | write `package.module:Class`, derive from `BrainBase`, override `_pick_move` and/or `_decide_move` |
| `police_class` | Your cop "brain" (also chooses barrier placement) | same as above; cop also selects barrier placement via `_decide_move` |

---

## 18. Consolidated Mandatory JSON/Config File Inventory (cross-reference)

For convenience, every file referenced as mandatory anywhere in the book, gathered in one place:

| File | Format | Mandatory? | Shared or private | Purpose |
|---|---|---|---|---|
| `config/game.json` | JSON | **MUST** | Shared, signed, byte-identical | The game's "constitution" — physics/scoring/network parameters (App. B) |
| `config/game.toml` | TOML | **MUST** (contents private) | Private, per-peer | Team identity, network port, opponent URL, strategy class, LLM mode, email destination (App. B) |
| `declaration_<game_id>.json` | JSON | **MUST** | Sent/compared between peers | Pre-game declaration — teams, hardware, model, commit hash, token/time budgets (Ch.5, Ch.9) |
| `config_<game_id>_g<NN>.json` | JSON | **MUST** | Sent/compared between peers | The specific sub-game's locked configuration snapshot (Ch.9) |
| `log_<game_id>_g<NN>.json` | JSON | **MUST** | Sent/compared between peers, replayable | Full move-by-move Commit/Reveal/Nonce log for cryptographic audit + Replay Viewer (Ch.5, Ch.7) |
| `result_<game_id>.json` | JSON | **MUST** | Sent to lecturer separately by each side | Final result — score, mutual sign-off, all 4 repo cross-links, token totals (Ch.9) |
| `rate_limits.json` | JSON | shared config detail | Shared | Gatekeeper token-bucket/quota configuration (App. B) |
| `credentials.json` | JSON | **MUST exist, MUST be gitignored** | Secret, never shared | OAuth app identity for Gmail API (App. A) |
| `token.json` | JSON | **MUST exist, MUST be gitignored** | Secret, never shared | OAuth access + refresh tokens (App. A) |
| `README.md` (× 2 repos) | Markdown | **MUST** | Public/shared with lecturer | Academic report — 6 mandatory components (Ch.9, App. C) |
| `PRD` files (×7 recommended) | Markdown/text | **MUST** (at least one PRD file per repo; layered build is recommended) | Public/shared with lecturer | Design specification per development layer (Ch.10) |
| `PLAN` file | text | **MUST** | Public/shared with lecturer | Work plan documentation (Ch.9) |
| `TODO` file(s) | text | **MUST** | Public/shared with lecturer | Outstanding task tracking (Ch.9) |
| Word/PDF submission document **[from submission guidelines]** | Word template → PDF | **MUST** | Submitted via course system | Do not alter template field layout; fill fields only, export to PDF (Ch.9, App. C) |

---

## 19. Notes on the Second PDF & the User-Provided Summary Cross-Check

19.1. **On `software_submission_guidelines-V3.pdf`**: its content — Word/PDF submission template usage, per-team-member individual submission requirement, the 8-character team identity code, and "do not move template fields" — is reproduced almost verbatim inside `police_thief_p2p.pdf`'s own Appendix C and Chapter 11 checklist (same author, same course). All of it has been folded into §14 and §16.5 (rules 43–45) above rather than duplicated as a separate section.

19.2. **Cross-check against the user-supplied summary**: the summary provided matches the book closely; the following corrections/clarifications were made when merging it into this document:
   - JSON filenames: the user's summary used illustrative names (`1-pre-game-declaration.txt`, etc.); the book's actual mandatory filenames are `declaration_<game_id>.json`, `config_<game_id>_g<NN>.json`, `log_<game_id>_g<NN>.json`, `result_<game_id>.json` (App. F, Table 20) — corrected in §9.3.20 and §18 above.
   - "LLM used exclusively for verbal layer, unless both teams agree otherwise" — confirmed accurate; this is explicitly the **one rule in the whole book flagged as a [RECOMMEND], not a [MUST]** (§16.4 rule 25), and deviation is explicitly allowed by mutual documented agreement (Ch.6.4.3).
   - "Moodle" submission portal — not found by name in the extracted text of either source PDF; the requirement actually stated is submission of a Word document converted to PDF via the course's official submission system/template (kept generic in §14/§18 above rather than naming a specific portal not confirmed in the source).
   - All other items in the user's summary (P2P/Zero-Trust, FastMCP dual role, tunneling, 7×7 grid, orthogonal-only movement, barrier max 14, capture claim, scoring values, pheromone constants, commit-reveal + SHA-256, Step-0 hardware+commit-hash declaration, mutual audit, state machine, Gatekeeper/token-bucket for Gmail 429, Watchdog/Deadline Tracker, central Orchestrator, Live GUI local-truth-only, Replay Viewer Verified-OK/TAMPERED, two GitHub repos with `v1.0-submission` tag, never pushing secrets, 6-part academic README, min. 2 league games) were verified accurate against the primary source and are fully incorporated at their respective sections above.
