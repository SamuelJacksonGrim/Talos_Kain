---
artifact: Interfaces
status: complete
order: 7
fills: "plug points — the port Protocols that make adapters swappable"
depends_on: [Schemas]
filled_by: both
last_decision: D-002
---

# Interfaces — Talos_Kain (as built)

> The formal seams are the `Protocol`s in `talos/domain/ports.py` (+
> `domain/gate.py`). Swapping an implementation is legal iff it preserves the
> interface and the contract it upholds. This is what makes SQLite→Postgres and
> Mock→SC2 adapter swaps, not rewrites (G4).

### Environment
- **Purpose:** a world the organism acts in.
- **Surface:** `reset(seed) → Observation`; `step(Action) → StepResult`;
  `close()`; attrs `name`, `version`.
- **Upholds:** A2.
- **Implemented by:** `MockEnv` (live, primary) · `SC2Env` (dormant) ·
  **Consumed by:** Motor, Talos.

### Gate (`domain/gate.py`)
- **Purpose:** the one admission decision into behavior-shaping stores.
- **Surface:** `admit(SkillCandidate) → GateDecision`.
- **Upholds:** G1, A3.
- **Implemented by:** `ConfidenceGate` (live), `AlwaysAdmitGate` ·
  **Consumed by:** SkillPublisher (the single writer).

### WALStore
- **Purpose:** append-only experience log.
- **Surface:** `append(kind, payload) → seq`; `count() → int`. No update/delete.
- **Upholds:** the append-only state-update rule (Flows).
- **Implemented by:** `SqliteWAL` · **Consumed by:** Talos.

### EpisodeStore
- **Purpose:** trajectory archive with provenance.
- **Surface:** `save(Episode)`; `get(id)`; `by_context(ctx) → [Episode]`;
  `recent(n)`.
- **Upholds:** G3.
- **Implemented by:** `SqliteEpisodeStore` · **Consumed by:** Talos, Extractor.

### SkillStore
- **Purpose:** the procedural skill library (behavior-shaping).
- **Surface:** `publish(Skill)`; `for_context(ctx) → Skill?`; `all()`;
  `retire(id)`; `max_version(ctx) → int`.
- **Upholds:** I1, I3 (single writer discipline enforced upstream by the
  publisher — G1).
- **Implemented by:** `SqliteSkillStore` · **Consumed by:** Publisher (write),
  Policy (read), `Talos._recover` (retire).

### SelfModelStore
- **Purpose:** the organism's model of itself (metacognition, **not gated**).
- **Surface:** `get(ctx) → SelfModelEntry?`; `put(entry)`; `all()`.
- **Upholds:** D-003 (derived fact, not injection).
- **Implemented by:** `SqliteSelfModelStore` · **Consumed by:** Reflector
  (write), Policy (read), `_recover` (belief reset).

### AuditStore
- **Purpose:** the tamper-evident trust root.
- **Surface:** `record(kind, payload) → AuditRecord`; `history()`;
  `verify() → bool`.
- **Upholds:** G2.
- **Implemented by:** `SqliteAuditStore` · **Consumed by:** Publisher, Talos.

## Service surfaces (concrete, not yet ports)
`RewardEngine` (`observe`, `value`, `is_surprise`, `is_trusted`), `Reflector`
(`reflect`), `Policy` (`choose`), `Sensorium` (`perceive`), `Motor` (`act`),
`SkillExtractor` (`nominate`), `SkillPublisher` (`submit`, `forget`) are
services with stable surfaces but are not Protocols yet — promote to ports if a
second implementation is ever needed.

## Dormant ports (declared, unimplemented)
`HotCache`, `SemanticStore`, `HypergraphStore`, `IdentityKernel`, `TelosStore`
— in `ports.py`, so the organs that need them plug into a named seam when woken.
