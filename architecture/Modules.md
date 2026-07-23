---
artifact: Modules
status: complete
order: 9
fills: "module list, ownership, responsibilities, boundaries"
depends_on: [Interfaces]
filled_by: both
last_decision: null
---

# Modules — Talos_Kain (as built)

## Live modules
| Module | Responsibility | Owns (boundary) | Implements |
|--------|----------------|-----------------|------------|
| `domain/types` | the vocabulary | the domain dataclasses/enums | — |
| `domain/ports` | the seams | port `Protocol` definitions | — |
| `domain/gate` | the admission decision | gate policy (thresholds) | `Gate` |
| `domain/reward` | valence calculus | — (pure functions) | — |
| `services/sensorium` | perceive + salience | intake normalization | — |
| `services/policy` | action selection | the skill→self-model→explore policy | — |
| `services/motor` | actuate a chosen action | the world-I/O call | — |
| `services/reflection` | update the self-model | metacognition | — |
| `services/reward_engine` | value + prediction error | reward modulation state (in-memory) | — |
| `services/skill_extraction` | nominate (extractor) + gated publish (publisher) | consolidation; **single skill writer** | — |
| `services/organism` | drive the loop; own recovery | control flow, run budget | — |
| `infrastructure/storage/sqlite/wal` | append-only experience | the `wal` table | `WALStore` |
| `infrastructure/storage/sqlite/episodic` | trajectory archive | the `episodes` table | `EpisodeStore` |
| `infrastructure/storage/sqlite/skills` | skill library | the `skills` table | `SkillStore` |
| `infrastructure/storage/sqlite/self_model` | metacognition store | the `self_model` table | `SelfModelStore` |
| `infrastructure/storage/sqlite/audit` | hash-chained ledger | the `audit_log` table | `AuditStore` |
| `infrastructure/environments/mock` | the primary world | hidden winners + drift schedule | `Environment` |
| `infrastructure/environments/sc2` | dormant SC2 adapter | — | `Environment` (unimplemented) |
| `infrastructure/telemetry/logging` | log setup | — | — |

## Dormant modules (typed stubs, woken on a forcing function — D-005)
- **Services:** `immune` (§0), `scheduler` (§1), `cortex`/`planner` (§2),
  `consolidation` (§3/§8), `reflex` (§4), `skill_lifecycle` (§7 shadow/canary/
  monitor — demotion edge already live), `sleep` (§1/§8/§9),
  `identity_crucible` (§10/§11), `metacognition` (§12), `purpose` (§15).
- **Infrastructure:** `sqlite/{semantic, hypergraph, hot_cache, identity,
  telos}` stores; `telemetry/{metrics, tracing}`; `environments/sc2/curriculum`.

## Boundaries worth restating
- The **composition root** is `organism.main` (+ test fixtures): the only place
  that names concrete adapters and wires them.
- The **skill store** has exactly one writer path (`SkillPublisher.submit`) and
  one retire path (`Talos._recover`). Reads are open; writes are not.
