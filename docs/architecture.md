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
- `services/policy.py` — action selection (skill → memory → explore)
- `services/motor.py` — actuate
- `services/skill_extraction.py` — nominate candidates + gated publish
- `domain/gate.py` — the one admission gate
- `domain/reward.py` — valence
- `infrastructure/storage/sqlite/{wal,episodic,skills,audit}.py` — the four stores
- `infrastructure/environments/mock/mock_env.py` — the primary world

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
| Limbic reward (streaming TD) | `services/reward_engine.py` | §5 |
| Skill CI/shadow/canary/monitor | `services/skill_lifecycle.py` | §7 |
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
