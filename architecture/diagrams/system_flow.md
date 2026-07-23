# System Flow — Talos_Kain (as built)

Behavioral view: one episode, and how learning and recovery hang off it.

```
Environment.reset(seed)
 │
 ▼
Perceive (Observation + salience)
 │
 ▼
Choose ── skill? ──▶ exploit skill
 │        self-model winner? ──▶ exploit belief
 │        else ──▶ explore an untried action
 ▼
Act ──▶ StepResult   (crosses the world boundary)
 │
 ▼
Record (Episodic + WAL)
 │
 ▼
Reflect ──▶ self-model updated
 │
 ▼
Reward: prediction error = reward − value
 │
 ├── surprise (pe ≤ −0.5)? ──▶ RECOVER: retire skill (audited) + reset belief
 │
 ▼
Learn: nominate (recent + trusted) ──▶ Gate
                                        ├── ADMIT ──▶ publish Skill + audit
                                        └── DEFER ──▶ nothing written
 │
 ▼
next episode
```
