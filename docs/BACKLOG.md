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
| Memory consolidation, eviction, dream | 3, 8 | episodic archive grows large over long runs | async encoder, terminal distillation, tombstones, resonance shield |
| Sleep / wake machinery | 1, 8, 9 | continuous operation builds backlog pressure | needs async queues (MQ/REFLECTQ) + consolidation to have something to batch; don't wake before there's offline work to do |
| Skill CI full gauntlet | 7 | a skill could be wrong or harmful, not just stale | generated tests, sandbox gate, shadow (recommend-only), canary; **demotion edge already live** |
| Semantic memory + retrieval | 3 | needing similarity retrieval / richer observations | SQLite + vector ext → Postgres + pgvector behind `SemanticStore` |
| Hypergraph / constraints | 3 | distillation needs a target to graft lessons into | causal relations, fallacies; where evicted episodes leave their "instinct" |
| Cerebellar reflex + ghost-pointer | 4 | cold memory + multi-step loop | micro-retries; unthaw-verify against tombstone digest |
| Identity kernel + crucible | 10, 11 | the organism has a self worth protecting | the hardest gate; ANNEAL only through the crucible; `IDENTITY_PROPOSAL` escalation seam already exists in reflection |
| Telos + horizon gate | 15 | multi-mission, months-long objectives | standing purposes (architect-signed) vs campaigns (HORIZON-gated) |
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
