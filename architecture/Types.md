---
artifact: Types
status: complete
order: 5
fills: "core domain types, primitives, enums, identifiers, structural schemas"
depends_on: [Contracts]
filled_by: both
last_decision: null
---

# Types — Talos_Kain (as built)

> Source of truth is the code: `talos/domain/types.py` (+ `identity.py`,
> `telos.py` for the dormant types). This artifact mirrors it; if the two ever
> disagree, the code wins and this file is the bug (QUALITY-BAR §8).

## Core Domain Types (`domain/types.py`)
- **Observation** — `{ context_id: str, available_actions: tuple[int, …], features: dict }`
- **Action** — `{ action_id: int }`
- **StepResult** — `{ reward: float, done: bool, outcome: "win" | "loss" | None, info: dict }`
- **Step** — `{ observation: Observation, action: Action, reward: float, salience: float }`
- **Episode** — `{ episode_id, run_id, seed: int, env_name, env_version, context_id, steps: [Step], outcome, started_at, finished_at }`
- **SelfModelEntry** — `{ context_id, attempts: int, wins: int, tried_actions: tuple[int, …], winning_action: int | None }` · derived props: `confidence = wins/attempts`, `mastered = winning_action is not None`
- **SkillCandidate** — `{ context_id, action_id: int, confidence: float, provenance: tuple[episode_id, …] }` (a *nomination*, not yet a skill)
- **Skill** — `{ skill_id, name, context_id, action_id, version: int, confidence, provenance, created_at }`
- **AuditRecord** — `{ seq: int, kind, payload: dict, prev_digest, digest, ts }`

## Enums
- **GateDecision** = `ADMIT | REJECT | DEFER | ESCALATE` — milestone zero
  exercises `ADMIT`/`DEFER`; `REJECT`/`ESCALATE` exist so the §7 skill CI, §11
  crucible, and §15 horizon gate plug into the same enum later.

## Primitives & Identifiers
- `context_id` — stable string, e.g. `"ctx-0"`.
- `action_id` — int in `range(n_actions)`.
- `episode_id` — `"{run_id}::ep{index:06d}"`.
- `skill_id` — `"skill::{context_id}::v{version}"`.
- `seed` — int; the per-episode seed is `run_seed * 1_000_003 + index`.
- `digest` — SHA-256 hex; `prev_digest` of the genesis audit row is 64 zeros.

## Structural Schemas
- A **loop step** is `(Observation, Action, StepResult)` recorded as an
  `Episode` of one `Step` (milestone zero is single-step; the `Episode.steps`
  list is a JSON array already ready for multi-step — see BACKLOG).

## Dormant Domain Types (present, not yet used)
- **FixedPoint** (`domain/identity.py`) — `{ key, statement, signed_by }`; the
  identity kernel's axioms. Single autonomous writer would be `ANNEAL`.
- **Purpose** (`domain/telos.py`) — `{ purpose_id, tier: PurposeTier, statement, signed_by? }`
- **PurposeTier** = `standing | campaign` · **TelosFit** = `serves | neutral | conflicts`
