# Backlog

A living list of what's next for the organism, so ideas and place aren't lost
between sessions. This is the working companion to two other docs:

- [`architecture.md`](architecture.md) — what is **live** vs **dormant** right now.
- [`../aamsfc.md`](../aamsfc.md) — the v7 spec (the §-numbers below point into it).

**The governing rule stays:** organs wake only when gameplay exposes the need,
not on speculation. So this backlog is ordered by *forcing function* — the thing
that makes an organ suddenly necessary — not by how interesting it is.

**How to use:** when you wake an organ, move it from here to the "woken" section
of `architecture.md`, and add anything new you discovered to the relevant list
below. One line is fine. Keep it honest about what's a hypothesis.

---

## Near-term (the mock world can still teach us this)

1. **Stochastic / noisy world.** Outcomes stop being deterministic — the best
   action wins with probability `p < 1`. This is the single highest-value next
   step, because it forces two things at once:
   - **Recovery trigger: surprise-threshold → value-collapse** (see Queued
     Decisions). The current surprise-threshold trigger (`prediction_error ≤
     −0.5`) over-triggers under noise and must become value-collapse based.
   - **Streaming TD-style value learning (§5 deeper).** A running win-rate
     estimate per (context, action) with real confidence, not a binary winner.

2. **Multi-step episodes.** Today an episode is one decision. Multi-step
   trajectories unlock credit assignment, TD error over a trajectory (§5), and
   make the cerebellar reflex / ghost-pointer motor-yield (§4) meaningful
   (there's nothing to yield *to* in a one-step world).

3. **Insurance comment at the recovery site.** Tiny: note in
   `organism._recover` / `reward_engine` that the surprise-threshold trigger
   assumes deterministic outcomes and must move to value-collapse under noise,
   so nobody adds a noisy env later and gets silent thrashing. (Do this whenever
   the reward-engine change merges.)

## Organs still dormant (forcing function → what waking needs)

| Organ | §| Forcing function | Notes |
|---|---|---|---|
| Memory consolidation, eviction, dream | 3, 8 | episodic archive grows large over long runs | async encoder, terminal distillation, tombstones, resonance shield. **`--growth` found one store in eighteen with a drain (`SEM → EVICT`); the code inherits the gap exactly — `DELETE FROM` appears nowhere in `talos/`, `EvictionProtocol` is a dormant stub. Sharpest case: `EPI` has two writers and no drain, and the crucible replays through it, so the cost of the strictest gate rises for the life of the system. `PROC`, `HG` need drains; `AUDIT` wants tiering, not pruning.** |
| Sleep / wake machinery | 1, 8, 9 | continuous operation builds backlog pressure | needs async queues (MQ/REFLECTQ) + consolidation to have something to batch; don't wake before there's offline work to do |
| Skill CI full gauntlet | 7 | a skill could be wrong or harmful, not just stale | generated tests, sandbox gate, shadow (recommend-only), canary; **demotion edge already live** |
| Semantic memory + retrieval | 3 | needing similarity retrieval / richer observations | SQLite + vector ext → Postgres + pgvector behind `SemanticStore` |
| Hypergraph / constraints | 3 | distillation needs a target to graft lessons into | causal relations, fallacies; where evicted episodes leave their "instinct" |
| Cerebellar reflex + ghost-pointer | 4 | cold memory + multi-step loop | micro-retries; unthaw-verify against tombstone digest |
| Identity kernel + crucible | 10, 11 | the organism has a self worth protecting | the hardest gate; ANNEAL only through the crucible; `IDENTITY_PROPOSAL` escalation seam already exists in reflection |
| Telos + horizon gate | 15 | multi-mission, months-long objectives | standing purposes (architect-signed) vs campaigns (HORIZON-gated). *Note: in the diagram `HORIZON` is one node with its four tests written inside the label, while the crucible is five separate nodes — so the linter can verify the crucible's ordering and not the horizon gate's. Expand it when this wakes, or accept the asymmetry in writing.* |
| Metacognition / offline evolution | 12 | enough logged data + a model to fine-tune | DPO/RLHF/RLAIF; the `learn` optional-dep group lands here |
| Federated cortex / agent mesh | 2 | a task too big for one policy | planner, researcher, executor, critic pods; context broker |
| Immune / adaptive intake | 0 | hostile or adversarial inputs | fast hygiene gate, novelty lane, deep review, adaptive tuner |

## The milestone

- **SC2 environment + curriculum (README first milestone).** The real forcing
  function that drags most of the above into being. Heavyweight: needs PySC2 +
  the StarCraft II binary + maps (won't run in bare CI). Strategy: mature the
  learning architecture cheaply on the mock world (stochastic, multi-step)
  until it's proven, *then* attach SC2 as an adapter behind the existing
  `Environment` port. `SC2Env` and `curriculum.py` stubs are already in place
  (Easy → re-baseline at Medium).

## Queued decisions

- **Recovery trigger: surprise-threshold (current) → value-collapse.** See
  `architecture/DecisionLog.md` D-004. The shipped trigger is the reward
  surprise `prediction_error ≤ −0.5` (an action valued ≥ 0.5 lost) — *not* a
  source-based commit-failure check, which an earlier session summary mislabeled
  it as. Decided: keep it while the world is deterministic; switch to
  value-collapse the moment outcomes become stochastic. Value-collapse recovers
  only when an action's recency-weighted value drops below the trust line after
  *sustained* failure, which distinguishes an *unlucky* loss from a *stale*
  belief — the distinction noise forces. The short version: the surprise
  threshold is simple and correct under determinism but over-triggers under
  noise; value-collapse is noise-tolerant.

## Spec & governance (found by `tools/invariant_lint.py`, 2026-07-23)

The cornerstone's invariants are now executable against its own diagram —
`mermaid_graph.py` parses the flowchart, `invariant_lint.py` asserts I1, I2, I4,
I8, I10, I11, I12 against it. `--audit` reproduces the v5/v6 write-path ratios
mechanically; `--growth` asks the dual question, which store has a drain.

**It exits 1 today.** That is real work, not a broken test. The same
forcing-function rule applies here: these are ordered by *when the fix stops
being cheap*, not by how interesting the defect is.

1. **`META` has no edge to `CTRL`.** v6 fixed META's inputs (`SELFMOD`, `CFACT`
   → `META`) and never its outputs. Seven lateral edges mutate `CRYSTAL`,
   `RETRY`, `DEP`, `LOCAL1`, `LOCAL2`, `BROKER`, `PAIRGEN` directly, while
   `CTRL` records none of it — so `CTRL --> DEP` is the declared path and
   `META -.-> DEP` is the real one. **`CTRL` is not the control plane; it is a
   partial record of it.** Fourth instance of the v5/v6 bug class and the first
   invisible to the hand method, because it lives in the edges *out of* a gate
   rather than *into* a store.
   Consequence worth keeping: the counterfactual crucible replays `EPI` against
   the standing prior, and that replay is only sound if the config at the time
   of those episodes is reconstructable. Lateral pokes don't just lose
   auditability — they weaken the identity gate.
   **Forcing function: before §12 metacognition wakes.** `metacognition.py` is
   dormant, so fixing the spec now costs an edit; fixing it after the module
   exists costs a refactor of the machinery the governance argument rests on.

2. **Split `CTRL` → `CTRL_OPS` / `CTRL_CONFIG`.** One store doing two jobs:
   operational control (budgets, priorities, stop conditions, routing) and gate
   configuration (policy-engine rules, deployment manifests). A single door
   can't be strict about either while they share a node — which is why `PFC -->
   CTRL` can't be adjudicated mechanically. Third instance of the v5 self-model
   store-split fix. Needs config epochs on the read side (§9's precompiled delta
   + pointer swap), which also closes an unnamed hazard: today META can retune
   routing while a plan is mid-flight. **Same forcing function as (1).**

3. **Rewrite I10 without the word "tuning."** It is the ambiguity that made
   `PFC → CTRL` unfindable by anything but a human. Replace with two mechanical
   assertions once (2) lands: `CTRL_CONFIG <- {META, ARCH}`,
   `CTRL_OPS <- {GOV}`. **Ships with (2).**

4. **Lint the territory, not just the map.** Nothing asserts the invariants
   against `talos/`. A diagram that passes while the implementation quietly
   doesn't is the exact failure the linter exists to prevent, one level down.
   Start from `architecture.md` §"Invariants (live from commit one)" — the code
   already claims which ones it holds — plus `tests/test_gate.py` and
   `tests/test_audit_chain.py`. I3, I5, I6, I7 and I9 were never
   diagram-checkable and only become testable here.
   **Forcing function: the moment a second organ wakes.** Every waking is a
   chance for the code and the spec to diverge silently.

### Deferred — no forcing function yet

- **Governor on `CTRL_OPS`.** Trajectory-priced admission (the `SLEEPDEBT`
  accumulator pattern pointed at write pressure) to catch sequences of
  individually-legal writes whose trend is capture. Real idea; nothing contests
  the control plane yet. Revisit when §12 or the federated cortex wakes. Note it
  is itself a proxy, so it inherits the proxy-gaming problem it partly answers.
- **Threat-model entries** for governor-as-proxy and config shadow writes, and
  the amendment to *wake-state executive compromise* (no longer wholly open once
  the split lands).
- **The grounding paragraph.** Three places now bottom out in the trust root —
  identity in the crucible, standing purpose in the architect's signature,
  governor config in `CTRL_CONFIG`. Worth saying once as a property of the
  architecture rather than letting it be rediscovered a fourth time. Write it
  after the governor exists, or it only has two instances.
- **Arbiter over the control plane.** *Shelved, decided.* An arbiter needs a
  ruleset; rulesets live in the control plane; the recursion grounds in the
  trust root anyway (§15). It collapses into "architect-signed config" while
  adding a live-path hop. The split plus a governor gets there without the hop.

### Closed 2026-07-23

- **Crucible stage count.** §11 said "four tests," I2 said four and then listed
  five, and the diagram has five stages plus a write. The diagram was right; the
  prose was merging `POISON` into lineage and `CONTINUITY` into the
  counterfactual. Fixed in §11, I2 and the identity-drift threat entry.
- **Stale status claims.** `README.md` led with *"design specification. Nothing
  here is implemented or test-validated yet"* and `aamsfc.md` said *"nothing in
  this document is implemented"* — both false since PRs #1–#3, and the most
  visible lines in the repo. Both now state what runs; README gained a **Run it**
  block.
- **Milestone framing.** Split *the test* (small, already passing on the mock)
  from *the milestone* (that test where the world pushes back), so the
  five-subsystem list stops reading as a prerequisite.
- **Dev environment.** `pytest` is an optional `[dev]` extra and had never been
  installed in the WSL checkout, so `tests/` had never run from that side.
  **16 passed.** Nothing was broken; the checkout could not see the code.

---

## Infrastructure / tech-debt

- **Rust hot-cache (`rust/hot_cache/`)** — only when profiling the SC2 agent
  shows the hot path is the wall. Not before. Seam already reserved.
- **Migrations framework** (`infrastructure/storage/sqlite/migrations/`) — the
  first time a store's schema must change while preserving rows (likely
  episodic going multi-step, or semantic when embeddings arrive).
- **Postgres + pgvector** — when the semantic store wakes or SQLite hits a
  scale wall. Behind the existing ports, so it's an adapter swap.
- **Reward-engine value persistence** — the value table is in-memory
  modulation state today; persist or rebuild-from-log if a run must survive a
  restart mid-learning.
- **Optional-dependency groups** — fill in `sc2` (pysc2 + binary) and `learn`
  (torch + the §12 training stack) in `pyproject.toml` when those organs wake.

---

*Living document. Provisional and Claude-drafted; the architect (Samuel Grim)
reprioritizes. Review and final authority as stated in `aamsfc.md`.*
