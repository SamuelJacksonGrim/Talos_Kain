---
artifact: README
status: complete
order: 10
fills: "front door — what/why/problem/components for the instantiated system"
depends_on: [Architecture, Flows, Contracts, Modules]
filled_by: both
last_decision: null
---

# Talos_Kain — Architecture (10-artifact instantiation)

> This folder is Talos_Kain described in the family's standard 10-artifact
> language, so its `Contracts.md` reads against any other system's. It documents
> the **as-built** organism (milestone-zero slice + two woken organs), not the
> full vision. Two companions hold the rest:
> - [`../aamsfc.md`](../aamsfc.md) — the v7 conceptual spec (all 15 subsystems).
> - [`../docs/architecture.md`](../docs/architecture.md) — the live/dormant
>   ledger and layering map. [`../docs/BACKLOG.md`](../docs/BACKLOG.md) — what's
>   next.

## What is this?
A governed, continuously-learning autonomous-agent harness — a bounded loop that
turns situations into evaluated, executed actions over memory, grows skills from
what works, models itself, and recovers when the world drifts. It is the closest
live instance of the family's **guarded agent** pattern — with one honest
difference: the guarded skeleton gates every *action* before execution, whereas
Talos's live gate is on *consolidation* (writes to behavior-shaping stores).
Per-action risk-gating is the dormant §2 layer.

## Why does it exist?
To be the *organism* a cognitive mind runs inside — sensorium, motor loop,
memory ecosystem, skill neurogenesis, and (dormant) sleep/identity/telos — built
empirically, one organ at a time, against a forcing function (StarCraft II, via
a mock world first).

## What problem does it solve?
It gives, from milestone zero: a measurable learning loop with **provenance**
(this skill grew from these games), a **tamper-evident** governance ledger, a
**single audited gate** so nothing shapes behavior unreviewed, and — with the
reward engine — the ability to **recover from a drifting world** instead of
locking into confident failure.

## Major components
Sensorium · Policy · Motor · Reflection (self-model) · Reward engine · Skill
extraction + gate · the five stores (WAL · Episodic · Skills · SelfModel ·
Audit) · Environment (mock / dormant SC2). See [`Modules.md`](Modules.md) and
[`Architecture.md`](Architecture.md).

## The load-bearing decisions
- **D-002** One audited gate into behavior-shaping stores.
- **D-003** The self-model is derived fact, not gated.
- **D-004** Recovery fires on a reward surprise (value-collapse queued for noise).
- **D-005** Dormant organs wake only on a forcing function.

(Full reasoning in [`DecisionLog.md`](DecisionLog.md).)

## Proven to run
`talos-mock` runs the loop end to end; **21 tests pass**
(`python3 -m pytest -q`). Stationary: converges to 100% and names its skills.
Drifting (`--drift-every 30`): holds ~83% through 20 drift events while the
audit ledger still verifies. (This satisfies the Architecture-Blueprints
framework's QUALITY-BAR §9 — "prove it runs".)

## Artifact status
| Artifact | Status |
|----------|--------|
| Architecture | complete |
| Flows | complete |
| Contracts | complete |
| Types | complete |
| Schemas | complete |
| Interfaces | complete |
| Dependencies | complete |
| Modules | complete |
| DecisionLog | complete |
| README | complete |
