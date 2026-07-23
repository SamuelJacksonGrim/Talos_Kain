---
artifact: Contracts
status: complete
order: 4
fills: "guarantees, assumptions, invariants, pre/post-conditions"
depends_on: [Architecture, Flows]
filled_by: both
last_decision: D-002
---

# Contracts — Talos_Kain (as built)

> Every guarantee below is backed by a test in `tests/` (named inline). These
> are the load-bearing rules; violating one is subtle breakage, not a loud
> error — which is exactly why they are written down.

## Guarantees
- **G1 — One audited gate.** No `Skill` enters the behavior-shaping skill store
  except through `SkillPublisher.submit → Gate.admit`, and **every** admission
  attempt records a `skill.admission` entry. *Failure mode:* an ungated write
  injects behavior nobody reviewed — the precise drift the family law
  ("consolidation may nominate; it may not appoint") exists to prevent.
  *(tests/test_gate.py)*
- **G2 — Tamper-evident ledger.** `AuditStore.verify()` recomputes the hash
  chain; any edited, deleted, or reordered row breaks it. *Failure mode:*
  without chaining, "immutable" is a comment and a silently altered governance
  record becomes an unauditable blind spot. *(tests/test_audit_chain.py)*
- **G3 — Provenance & reproducibility.** Every `Episode` carries
  `run_id + seed + env name/version`; every published `Skill` carries the
  episode ids that grew it; identical seeds produce an identical trajectory.
  *Failure mode:* without this, "this skill emerged from these games" is a
  story, not a query, and the milestone's learning claim is unfalsifiable.
  *(tests/test_learning.py::test_run_is_reproducible, tests/test_self_model.py)*
- **G4 — Inward-only dependencies.** `domain/` imports nothing from `services/`
  or `infrastructure/`; services depend only on the port Protocols. *Failure
  mode:* a single `domain → infrastructure` import welds the logic to SQLite /
  PySC2 and the swappability the entire design rests on evaporates.
  *(grep-verifiable; see Dependencies.md)*
- **G5 — No permanent lock-in under drift.** A committed belief that fails
  triggers demotion (retire + audit) and belief reset, so once a drifted
  context is revisited the organism reconverges to the current winner.
  *Failure mode without it:* the organism exploits a stale skill forever,
  losing every visit, with no path back. *(tests/test_drift.py)*

## Assumptions
- **A1 — Outcomes are deterministic (today).** A context's winning action is
  stable unless *drift* changes it. This is *why* the surprise-threshold
  recovery trigger (D-004) is safe now. Under stochastic outcomes it
  over-triggers, and the trigger must become value-collapse (C) first.
- **A2 — The environment honors the `Environment` port:** `reset(seed) →
  Observation`, `step(Action) → StepResult`, deterministic given
  `(env_seed, episode order)`.
- **A3 — Skill candidates are untrusted until admitted.** The extractor
  proposes; only the gate appoints (this is *why* G1 exists).
- **A4 — The reward value table is ephemeral modulation state**, rebuildable
  from the experience log — not a store of record. The WAL and episodic archive
  are.

## Invariants
- **I1 — At most one live skill per context.** `for_context` returns the
  highest-version non-retired skill.
- **I2 — One governance write per change.** Publisher idempotency prevents
  re-auditing an unchanged `(action, verdict)`; the ledger logs events, not
  heartbeats.
- **I3 — Monotonic skill versions.** `max_version` counts retired rows too, so a
  replacement skill never reuses a demoted skill's id.
- **I4 — Self-model faithfulness (stationary).** Lifetime `attempts`/`wins`
  equal the episodic log's per-context counts. (Belief fields `winning_action`/
  `tried_actions` are current-epoch and may be reset by recovery.)
- **I5 — Bounded exploration.** With the self-model, a context loses at most
  `n_actions − 1` times before its first win — it never repeats a known loser.
  *(tests/test_self_model.py)*

## Boundaries — terminal sinks & one-way streets
- **The audit ledger is observe-only for control.** Nothing in `Policy.choose`
  reads it. *Don't let a governance record become a control input.*
- **Reward is async modulation.** The policy has already chosen and acted
  before `RewardEngine.observe` runs. *Don't move reward into the
  action-selection path.*
- **The self-model is consolidation of fact, not injection** — which is *why*
  it is not gated (D-003). *Don't promote it to a gated store, and don't let
  reflection write the identity kernel:* identity-touching reflection escalates
  to the dormant crucible instead.

## Single source of truth (authority)
| Store | Single writer | Everything else |
|---|---|---|
| Skills | `SkillPublisher` (publish) + `Talos._recover` (retire only) | may nominate, never writes |
| SelfModel | `Reflector` (+ `_recover` belief reset) | reads only |
| Audit | holder of `AuditStore.record`; append-only + chained | reads only |

## Constants (audit obligation — do not change without auditing consumers)
- **`ConfidenceGate(threshold=0.75, min_support=3)`** — chosen. Governs what
  gets consolidated. Re-run the extractor + drift tests before changing.
- **`RewardEngine(learning_rate=0.5, surprise_threshold=0.5, exploit_value=0.5)`**
  — chosen. `surprise_threshold` is the one coupled to A1: under noise it must
  be re-derived or replaced by value-collapse, or good actions get demoted on
  unlucky losses (D-004).
- **`SkillExtractor(window=25)`** — chosen. Too small risks stationary
  flakiness; too large slows drift tracking.

## Pre/Post-Conditions
| Operation | Pre | Post |
|---|---|---|
| `Policy.choose` | observation well-formed | returns `(Action ∈ available_actions, source)`; no writes |
| `Gate.admit` | candidate well-formed | returns a `GateDecision`; no side effects |
| `Publisher.submit` | candidate from extractor | on `ADMIT`: exactly one skill written + one audit record; else no skill write |
| `RewardEngine.observe` | — | value updated; returns prediction error; never throws |
| `Reflector.reflect` | episode saved | self-model entry for the context updated |
| `AuditStore.record` | — | appended as a new chained link; `verify()` remains true |
| `Talos._recover` | a surprise fired | live skill (if any) retired + audited; belief reset |
