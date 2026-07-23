---
artifact: Architecture
status: complete
order: 2
fills: "structural blueprint — subsystems, boundaries, data & control flow"
depends_on: []
filled_by: both
last_decision: D-002
---

# Architecture — Talos_Kain (as built)

> The conceptual cornerstone is [`../aamsfc.md`](../aamsfc.md) (the v7 flow
> chart + walkthrough, 15 subsystems). **This artifact is the *as-built*
> structural view** of what is actually implemented today: the milestone-zero
> vertical slice plus two woken organs (self-model, reward engine). It does not
> restate the v7 vision — where it references a dormant organ, the authority is
> `aamsfc.md` and the live/dormant ledger in
> [`../docs/architecture.md`](../docs/architecture.md).

## Purpose
Talos_Kain is *the organism*: a governed control loop that turns a stream of
situations into evaluated, executed actions over memory, learns skills from
what worked, models itself, and recovers when the world moves — with **every
write to a behavior-shaping store passing one audited gate.**

## Layering (the spine)
Hexagonal. Dependencies point inward only.

```
domain/          pure logic — types, ports (interfaces), gate, reward calculus
services/        orchestration — the organs that drive the loop
infrastructure/  adapters — SQLite stores, environments, telemetry
```

The domain imports nothing from `services` or `infrastructure`; services depend
on the port Protocols in `domain/ports.py`, never on concrete adapters. This is
what makes "swap SQLite for Postgres" and "swap the mock world for StarCraft"
adapter changes, not rewrites (see `Dependencies.md`, enforced by G4).

## Major Subsystems (live)
- **Sensorium** (`services/sensorium.py`) — normalizes a world signal into an
  `Observation` and attaches a salience score.
- **Policy** (`services/policy.py`) — action selection: published **skill** →
  **self-model** winner → **systematic exploration** of untried actions.
- **Motor** (`services/motor.py`) — actuates the chosen `Action` against the
  `Environment`.
- **Reflection** (`services/reflection.py`) — after each episode, updates the
  **self-model** (`SELFSTORE`): what's been tried, what wins, how sure.
- **Reward engine** (`services/reward_engine.py`) — folds each outcome into a
  recency-weighted value and emits a **prediction error**; its surprise signal
  drives recovery, its value gates consolidation.
- **Skill neurogenesis** (`services/skill_extraction.py`) — the **extractor**
  nominates a candidate from recent, still-valued episodes; the **publisher**
  submits it to the **gate** (`domain/gate.py`) and, only on `ADMIT`, writes a
  `Skill` and records the decision.
- **Organism** (`services/organism.py`) — `Talos`, the loop coordinator; owns
  the cycle and the recovery path.
- **Stores** (`infrastructure/storage/sqlite/`) — five bulkheaded SQLite files:
  WAL (append-only experience), Episodic (trajectories + provenance), Skills
  (versioned, gated), SelfModel (metacognition), Audit (hash-chained ledger).
- **Environment** (`infrastructure/environments/`) — `MockEnv` is the *primary*
  world (stationary, or drifting via `drift_every`); `SC2Env` is a dormant
  adapter behind the same `Environment` port.

## Boundaries
- **Inside (trusted):** the loop coordinator, policy, reflection, reward,
  skill extraction, the stores.
- **Outside (untrusted):** the `Environment` — its outcomes are the world, and
  the loop treats them as input, never as authority.
- **The gate line:** the admission gate sits between *nominating* a skill and
  *writing* it to the behavior-shaping skill store. Nothing reaches that store
  except through it (D-002, G1). The self-model store is deliberately on the
  other side of that line — it is derived fact, not an autonomous injection
  (D-003).

## Data & Control Flow (one episode)
```
Environment.reset ─▶ Sensorium ─▶ Observation(+salience)
                                       │
                                Policy.choose ──▶ Action        (skill / self-model / explore)
                                       │
                                 Motor.act ──▶ StepResult       (crosses the world boundary)
                                       │
                            Episode saved to Episodic + WAL
                                       │
                         Reflection.reflect ──▶ SelfModel updated
                                       │
                      RewardEngine.observe ──▶ prediction error
                                       │
                    is_surprise? ──yes──▶ _recover (retire skill [audited] + reset belief)
                                       │
              Extractor.nominate ──▶ candidate ──▶ Publisher.submit ──▶ Gate ──▶ [ADMIT ⇒ write Skill + audit]
```

Control originates in `Talos.run`, lives in `_run_episode`, and returns an
`EpisodeReport`. The loop coordinator owns the cycle; no organ ends or
side-effects the run except through it.

## High-Level Diagrams
See [`diagrams/architecture_graph.md`](diagrams/architecture_graph.md) (structure),
[`diagrams/system_flow.md`](diagrams/system_flow.md) (behavior), and
[`diagrams/execution_map.md`](diagrams/execution_map.md) (control, one step).

## Relationship to the v7 spec
This is roughly §0 (sensorium, trivial), §2/§4 (policy/motor, trivial), §3
(memory — episodic/WAL/self-model live; semantic/hypergraph/hot-cache dormant),
§5 (reward — live), §7 (skill CI — nominate/gate/publish + demotion live;
shadow/canary/monitor dormant), §11 tail (reflection/self-model — live). The
executive mesh (§2 cortex), sleep/wake (§1/§8/§9), identity crucible (§10/§11
core), telos (§15), and immune system (§0 full) are **dormant** — present as
typed stubs, woken only on a forcing function (D-005).
