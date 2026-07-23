---
artifact: DecisionLog
status: complete
order: 99
fills: "architectural memory — decisions, alternatives, reasons, dates"
depends_on: []
filled_by: both
last_decision: null
---

# DecisionLog — Talos_Kain

> Append-only architectural memory. Referenced by `last_decision` fields across
> this artifact set. Supersede, never rewrite. Titles state the *question*.
> Absorbs `../docs/decisions/0001-language-and-skeleton.md` as D-001.

## Status values
`active` · `superseded by D-NNN` · `reversed by D-NNN`

---

### D-001 — Implementation language & layering?
- **Date:** 2026-07-22
- **Decided by:** both
- **Status:** active
- **Decision:** A Python spine with a hexagonal `domain`/`services`/
  `infrastructure` layering; a dormant Rust/PyO3 escape hatch reserved for
  profiled hot paths only.
- **Alternatives:** Rust / C++ / Nim as the primary language (rejected — the SC2
  forcing function and the RL/LLM stack are Python); a flat by-organ folder
  layout (rejected — it can't express or enforce the inward-only dependency
  rule).
- **Reason:** Iteration speed against the milestone dominates for an unvalidated
  spec; hexagonal layering is what makes store/environment swaps adapter
  changes, not rewrites.
- **Affects:** everything; Dependencies, Architecture. (Full text:
  `docs/decisions/0001`.)

### D-002 — One audited gate into behavior-shaping stores?
- **Date:** 2026-07-22
- **Decided by:** both
- **Status:** active
- **Decision:** The skill store is written only via `SkillPublisher.submit →
  Gate.admit`, and every admission attempt is recorded to the audit ledger.
- **Alternatives:** let the encoder/extractor write skills directly (rejected).
- **Reason:** An ungated write injects behavior nobody reviewed — the family's
  core failure mode ("consolidation may nominate; it may not appoint"). The gate
  is the cheapest enforceable checkpoint and is what makes G1 real.
- **Affects:** Architecture (gate line), Flows (learning), Contracts (G1),
  Interfaces (Gate), skill_extraction.

### D-003 — Is the self-model gated?
- **Date:** 2026-07-23
- **Decided by:** both
- **Status:** active
- **Decision:** No. Reflection writes the self-model store directly.
- **Alternatives:** route self-model writes through the gate too (rejected).
- **Reason:** The self-model is a consolidated *summary of logged fact*, not an
  autonomous behavior injection; gating it would be ceremony without payoff.
  The line holds because identity-*touching* reflection escalates to the dormant
  crucible rather than writing — that is where the gate boundary actually sits.
- **Affects:** Contracts (boundaries), Schemas (trust transitions), reflection.

### D-004 — What triggers drift recovery?
- **Date:** 2026-07-23
- **Decided by:** both
- **Status:** active (C queued — see BACKLOG)
- **Decision:** Recovery fires on a **reward surprise**:
  `RewardEngine.is_surprise(pe)`, i.e. `prediction_error ≤ −0.5` — an action the
  engine values ≥ 0.5 produced a loss.
- **Alternatives:** (A) a source-based "committed belief lost" check; (C)
  value-collapse — recover only when recency-weighted value falls below the
  trust line after *sustained* failure.
- **Reason:** In the deterministic world (A1), only the established winner is
  high-value, so a surprise *is* the winner failing — the simplest correct
  trigger. **Correction of record:** an earlier session summary mislabeled the
  shipped trigger as source-based (A); the code is the surprise-threshold.
  Under stochastic outcomes this over-triggers (an unlucky loss of a good action
  trips it), so the trigger must move to **C** before noise is introduced.
- **Affects:** Flows (recovery), Contracts (A1, G5, constants), reward_engine,
  organism.

### D-005 — When do dormant organs wake?
- **Date:** 2026-07-22
- **Decided by:** both
- **Status:** active
- **Decision:** Only on a forcing function — organs stay typed stubs until
  gameplay exposes the need.
- **Alternatives:** build the full v7 architecture up front (rejected).
- **Reason:** The spec is an unvalidated hypothesis; speculative complexity is
  the thing the whole project's empirical spine exists to avoid.
- **Affects:** the roadmap; `docs/BACKLOG.md` ordering; every "dormant" note.

### D-006 — Build order: Flows before Contracts?
- **Date:** 2026-07-23
- **Decided by:** both
- **Status:** active
- **Decision:** Architecture → Flows → Contracts, per `PIPELINE.md`.
- **Alternatives:** Contracts before Flows (rejected).
- **Reason:** A contract constrains a behavior; you can't write a meaningful
  guarantee for a flow you haven't described. Inherited from the framework.
- **Affects:** this artifact set's fill order.

### D-007 — Which world do we build against first?
- **Date:** 2026-07-22
- **Decided by:** both
- **Status:** active
- **Decision:** `MockEnv` is the primary world (deterministic, optionally
  drifting); `SC2Env` is a dormant adapter behind the same `Environment` port.
- **Alternatives:** build against StarCraft II from the start (rejected).
- **Reason:** SC2 needs the game binary and can't run in CI; the learning
  architecture is matured cheaply on the mock world, then SC2 attaches as an
  adapter with no domain/service changes.
- **Affects:** environments, the milestone strategy.
