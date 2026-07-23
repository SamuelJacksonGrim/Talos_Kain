---
artifact: Flows
status: complete
order: 3
fills: "behavioral blueprint — episode, learning, recovery, error, state-update flows"
depends_on: [Architecture]
filled_by: both
last_decision: D-004
---

# Flows — Talos_Kain (as built)

> The behavioral view of the implemented loop. Line references are to
> `services/organism.py::Talos._run_episode` unless noted.

## Run Flow (a run of N episodes)
1. `Talos.run(n)` records `run.start` to the audit ledger.
2. For each episode index `i`, execute the **Episode Flow** below.
3. Records `run.end`. Returns a list of `EpisodeReport`.

## Episode Flow (the organism loop)
```
seed        = run_seed * 1_000_003 + index            # deterministic per-episode
obs         = Sensorium.perceive(Environment.reset(seed))   # Observation + salience
action, src = Policy.choose(obs, rng)                  # src ∈ {skill, self_model, explore}
result      = Motor.act(action)                        # StepResult — crosses world boundary
Episode(...) saved to Episodic; each step logged to WAL
Reflection.reflect(episode)                            # update self-model for this context
pe          = RewardEngine.observe(ctx, action, reward)   # prediction error
if RewardEngine.is_surprise(pe):                       # pe ≤ −0.5  → D-004
    _recover(ctx, action)                              # demote + reset belief
candidate   = Extractor.nominate(ctx)                  # recent + still-trusted evidence
if candidate: Publisher.submit(candidate)              # → Gate → [ADMIT ⇒ write + audit]
return EpisodeReport(..., decision_source=src, recovered=…)
```

## Decision Flow (Policy.choose — `services/policy.py`)
1. Is there a live published skill for this context whose action is available?
   → exploit it (`source = "skill"`).
2. Else, does the self-model hold a `winning_action` for this context?
   → exploit it (`source = "self_model"`).
3. Else, choose (seeded) among actions the self-model has **not yet tried**
   (systematic elimination); if all tried, a blind guess (`source = "explore"`).

## Learning Flow (skill neurogenesis — §7 slice)
1. `Extractor.nominate(ctx)` reads the last `window` (25) episodes for the
   context, keeps only actions the reward engine still **trusts**
   (`value ≥ 0.5`), and picks the most-recently-winning of those, with its
   supporting episode ids as provenance.
2. `Publisher.submit(candidate)` asks the **Gate**. `ConfidenceGate` returns
   `ADMIT` iff `len(provenance) ≥ 3` **and** `confidence ≥ 0.75`; otherwise
   `DEFER`.
3. On `ADMIT`: version = `max_version(ctx) + 1` (retired rows included), any
   superseded live skill is retired, the new `Skill` is written, and the
   decision is recorded to the audit ledger.
4. Submission is **idempotent**: a re-decision of an already-settled
   `(action, verdict)` for a context is a no-op — no re-write, no re-audit.

## Recovery Flow (drift response — `_recover`)
Triggered when `RewardEngine.is_surprise(pe)` — an action valued ≥ 0.5 lost
(the established winner failing). Steps:
1. Retire the live skill for the context, and record `skill.demotion` to the
   audit ledger (removing a behavior-shaping capability is a governance event).
2. `Publisher.forget(ctx)` — clear the idempotency memo so the replacement can
   publish.
3. Reset the self-model belief: `winning_action = None`, `tried_actions = ()`,
   so the policy re-explores from scratch. Lifetime `attempts`/`wins` are kept.

## Error / Edge Flow
- **Loss (non-drift):** an ordinary losing episode with a low-value action —
  no surprise, no recovery; just recorded and reflected on.
- **Drift with no revisit yet:** a context can drift and not be visited for a
  few episodes; its stale skill persists until the next visit triggers
  recovery. (Convergence is only guaranteed once the context is revisited —
  see `test_drift` freeze-and-settle.)
- **`step()` before `reset()`:** `MockEnv` raises `RuntimeError` (a guard, not a
  silent wrong answer).

## State-Update Flow
- **WAL** is written **every** sub-step (observe, choose, act, reward) —
  append-only.
- **Episodic** is written once per episode, with full provenance
  (`run_id`, `seed`, env name/version).
- **SelfModel** is updated every episode (lifetime counts always; belief fields
  reset on recovery).
- **Skills** change **only** through the gate (publish) or through recovery
  (retire) — never elsewhere.
- **Audit** grows only on governance events: `run.start/end`,
  `skill.admission`, `skill.demotion`.
