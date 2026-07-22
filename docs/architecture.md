# Architecture

The authoritative design is [`aamsfc.md`](../aamsfc.md) (v7) — the full v7
flow chart and walkthrough. This document is the *code-side* map: how that
spec is organized into packages, and which organs are live versus dormant.

## Layering (hexagonal)

Dependencies point inward only. Nothing in an inner layer imports an outer one.

```
talos/
  domain/          pure organism logic — types, ports, gate, reward, identity, telos
                   (no SQLite, no environment, no third-party I/O)
  services/        orchestration — the organs that drive the cycle
  infrastructure/  adapters — SQLite stores, environments (mock, sc2), telemetry
```

The `domain/ports.py` Protocols are the seams. Swapping SQLite for Postgres,
or the mock world for StarCraft II, is an infrastructure change behind a port
— never a domain rewrite.

## What is live (milestone zero)

The forcing-function loop, end to end, against a deterministic mock world:

```
observe → score → choose → act → reward → record → learn
```

- `services/organism.py` — the loop (`Talos`)
- `services/sensorium.py` — perceive + trivial salience
- `services/policy.py` — action selection (skill → self-model → systematic exploration)
- `services/motor.py` — actuate
- `services/skill_extraction.py` — nominate candidates + gated publish
- `services/reflection.py` — reflect after each episode, update the self-model (§11 tail)
- `services/reward_engine.py` — prediction error / surprise; drives recovery (§5)
- `domain/gate.py` — the one admission gate
- `domain/reward.py` — valence
- `infrastructure/storage/sqlite/{wal,episodic,skills,self_model,audit}.py` — the five stores
- `infrastructure/environments/mock/mock_env.py` — the primary world (stationary, or drifting with `drift_every`)

**Woken organs (were dormant, now live):**

- **Self-model + reflection (§11 tail).** The organism models *itself* — per
  context, what it has tried, what wins, how sure it is (`SELFSTORE`). The
  reflection pass updates it after every episode; the policy reads it to
  explore by systematic elimination instead of blind guessing, so it never
  repeats a known loser and masters each context in at most (number of
  actions) tries. Identity-touching reflection still escalates to the dormant
  crucible rather than writing directly — that seam is where this organ ends.
- **Reward engine (§5).** Turns each outcome into a prediction error. When a
  *committed* belief (a published skill, or a self-model winner) fails, that is
  the signal the world drifted: the organism demotes the stale skill (audited)
  and resets its self-model belief so it re-explores. The engine's
  recency-weighted value also gates consolidation, so a drifted-away winner is
  never re-crowned on stale wins. This is what lets Talos hold a high win rate
  in a **drifting world** instead of locking into confident failure —
  demotion is the §7-monitor edge that arrives with it.

## What is dormant

Everything else in this tree is a typed stub tied to its spec section, present
so the organ has a home and a named seam before it wakes — but implemented
only when gameplay justifies it. Notable dormant organs:

| Organ | Module | Spec |
|-------|--------|------|
| Immune / adaptive intake | `services/immune.py` | §0 |
| Brainstem scheduler, leases | `services/scheduler.py` | §1 |
| Federated cortex, context broker | `services/cortex.py`, `services/planner.py` | §2 |
| Memory consolidation, eviction, dream | `services/consolidation.py` | §3, §8 |
| Cerebellar reflex, ghost-pointer | `services/reflex.py` | §4 |
| Skill CI / shadow / canary / monitor (demotion edge now live) | `services/skill_lifecycle.py` | §7 |
| Sleep / wake machinery | `services/sleep.py` | §1, §8, §9 |
| Identity crucible | `services/identity_crucible.py` | §10, §11 |
| Metacognition, offline evolution | `services/metacognition.py` | §12 |
| Telos, horizon gate | `services/purpose.py` | §15 |
| Semantic / hypergraph / hot cache / IDK / telos stores | `infrastructure/storage/sqlite/*` | §3, §15 |
| SC2 environment + curriculum | `infrastructure/environments/sc2/*` | README milestone |

## Invariants (live from commit one)

1. **One audited gate.** Nothing writes a behavior-shaping store except through
   a gate whose decision is recorded. Skill publishing enforces this today;
   the identity crucible and horizon gate are the same pattern, dormant.
2. **Hash-chained audit ledger.** The trust root. `verify()` detects any
   tamper.
3. **Provenance everywhere.** Episodes carry `run_id` + `seed`; skills carry
   the episodes that grew them.

See [`decisions/0001-language-and-skeleton.md`](decisions/0001-language-and-skeleton.md)
for the reasoning behind all of the above.
