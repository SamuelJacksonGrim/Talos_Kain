---
artifact: Dependencies
status: complete
order: 8
fills: "allowed/forbidden dependency directions, hierarchy, import rules"
depends_on: [Modules, Interfaces]
filled_by: both
last_decision: D-001
---

# Dependencies — Talos_Kain (as built)

## Module Hierarchy (top = depended-upon, bottom = depends-on-others)
```
domain/    types · ports · gate · reward     (pure — depend on nothing outward)
        ▲
services/  sensorium · policy · motor · reflection · reward_engine
           skill_extraction · organism        (depend on domain; compose each other)
        ▲
infrastructure/  sqlite stores · environments · telemetry
                 (implement domain ports; depend on domain types)
```

## Allowed Directions
- **Any layer → `domain/types`.** The vocabulary is shared.
- **services → `domain/ports`, `domain/gate`, `domain/reward`**, and **other
  services** (composition — e.g. `organism` uses `policy`, `skill_extraction`
  uses `reward_engine`).
- **infrastructure → `domain`** (the types + the port it implements).
- **The composition root** (`organism.main`, and the test fixtures) is the *one*
  place allowed to name concrete adapters (`SqliteSkillStore`, `MockEnv`, …) and
  wire them into `Talos`. Everything else receives ports.

## Forbidden Directions
- **`domain ⇏ services` and `domain ⇏ infrastructure`.** A single
  `domain → infrastructure` import welds the pure logic to SQLite / PySC2 and
  destroys swappability. *Enforces G4.* (Grep-verifiable: no `import` in
  `talos/domain/` names `services`, `infrastructure`, `sqlite`, or `pysc2`.)
- **service logic ⇏ concrete adapters.** `policy`, `reflection`,
  `skill_extraction`, etc. depend on the port Protocols, never on `SqliteX` /
  `MockEnv` — *except* the composition root above. The urge to `import
  SqliteSkillStore` inside a service goes to a constructor parameter typed as
  `SkillStore` instead.
- **No cycles.** Strictly layered.

## Import Rules
- Depend on **interfaces, not implementations** (dependency inversion) — the
  port lives in `domain`, the adapter in `infrastructure`, and the service holds
  the port.
- **The skill store's write authority is the publisher.** Other modules may hold
  a `SkillStore` reference and *read* (`for_context`), but only `SkillPublisher`
  calls `publish`, and only `Talos._recover` calls `retire`. (Enforces G1 / the
  single-writer authority table in Contracts.)
- **The world boundary** (`Motor → Environment`) is the only place untrusted
  outcomes enter; nothing treats an outcome as authority.
