---
artifact: Schemas
status: complete
order: 6
fills: "conceptual ontology — Entity→State→Event→Evaluation→Decision→Action"
depends_on: [Types]
filled_by: both
last_decision: null
---

# Schemas — Talos_Kain (as built)

## Core Transformation Chain
The canonical chain made concrete for the organism — this is what makes a
`Schemas.md` from Talos comparable to one from any other system in the family:

```
Entity      = the organism (Talos)
   ↓
State       = memory: WAL + Episodic + SelfModel + Skills, plus the reward value table
   ↓
Event       = Observation (from the world) | outcome (StepResult)
   ↓
Evaluation  = RewardEngine.observe → prediction error   (and Gate.admit → GateDecision, for consolidation)
   ↓
Decision    = the chosen Action (Policy) — and, for learning, the nominated SkillCandidate
   ↓
Action      = Motor.act executed against the Environment
   ↺ (outcome → Reflection → the next Event)
```

## Cognitive Schemas
- **Belief** ← `SelfModelEntry.winning_action` and any live `Skill` for a
  context (what the organism holds true about how to act there).
- **Skill** ← a distilled, **gated** capability — belief that has earned the
  right to shape behavior by passing the gate.
- **Value** ← the reward engine's recency-weighted estimate (what an action is
  *currently* worth, independent of how it was once crowned).

## Information Schemas — the trust transitions
- Experience enters as an `outcome`, is logged append-only (WAL) and archived
  (Episodic) — **untrusted, raw fact**.
- It is consolidated two different ways, across the one line that matters:
  - **Reflection → SelfModel** is *consolidation of fact* — ungated, because a
    faithful summary of the log is not a new behavior (D-003).
  - **Extraction → Gate → Skill** is *promotion to capability* — gated, because
    a published skill *shapes behavior*. **Gate `ADMIT` is the only trust
    transition into behavior-shaping memory.**

## Transformation Schemas (the verbs)
| From → To | By |
|---|---|
| `Observation → Action` | `Policy.choose` (reasoning/selection) |
| `outcome → prediction error` | `RewardEngine.observe` (valuation) |
| `episodes → SelfModelEntry` | `Reflector.reflect` (metacognition) |
| `recent+trusted episodes → SkillCandidate` | `Extractor.nominate` (distillation) |
| `SkillCandidate → GateDecision` | `Gate.admit` (gating) |
| `surprise → demotion + belief reset` | `Talos._recover` (repair) |
