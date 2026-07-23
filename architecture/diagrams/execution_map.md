# Execution Map — Talos_Kain (as built)

Control view: one episode. `Talos` owns control; the policy never writes a
store, and the reward path runs only *after* the action (async modulation — see
the "Boundaries" section in Contracts). Recovery is conditional on a surprise.

```mermaid
sequenceDiagram
  participant LC as Talos
  participant ENV as Environment
  participant POL as Policy
  participant SM as SelfModel
  participant REF as Reflection
  participant RW as RewardEngine
  participant EXT as Extractor
  participant GATE as Gate
  participant SKL as Skills
  participant AUD as Audit

  LC->>ENV: reset(seed)
  ENV-->>LC: Observation
  LC->>POL: choose(obs)
  POL->>SM: get(context)
  SM-->>POL: belief
  POL-->>LC: Action, source
  LC->>ENV: step(Action)
  ENV-->>LC: StepResult
  LC->>REF: reflect(episode)
  REF->>SM: put(entry)
  LC->>RW: observe(ctx, action, reward)
  RW-->>LC: prediction_error
  alt is_surprise(pe)
    LC->>SKL: retire(stale skill)
    LC->>AUD: record(skill.demotion)
    LC->>SM: reset belief
  end
  LC->>EXT: nominate(ctx)
  EXT->>RW: is_trusted(ctx, action)
  RW-->>EXT: trusted?
  EXT-->>LC: candidate
  LC->>GATE: admit(candidate)
  GATE-->>LC: decision
  alt ADMIT
    LC->>SKL: publish(skill)
    LC->>AUD: record(skill.admission)
  end
```
