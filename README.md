# Talos_Kain

**The organism.** An autonomous-agent harness that gets better at something by failing at it — repeatedly, unattended, over a long time — and can point at the named skill it grew. The body and nervous system that wraps a cognitive *mind* and lets it live, act, learn, rest, and remain itself across time.

> **Status:** the spine runs and two organs are awake. A milestone-zero vertical slice learns on a mock environment — 400 episodes, 80% → 100%, four named skills, verified audit chain — with 21 tests green. Woken: the **self-model** (§11 tail) and the **reward engine** (§5), which lets the organism recover from a drifting world instead of locking into confident failure. Nineteen modules still raise `NotImplementedError`, and StarCraft II is not wired. The cornerstone (`aamsfc.md`) describes far more than is built; treat every mechanism it names as a hypothesis unless `talos/` implements it.

## Run it

```bash
PYTHONPATH=. python3 scripts/run_mock.py          # the learning slice, stdlib only
python3 -m venv .venv && .venv/bin/pip install -e .[dev]
.venv/bin/python -m pytest -q                     # 16 tests
python3 tools/invariant_lint.py aamsfc.md --audit --growth
```

## Where this sits (the family)

| Repo | Role |
|------|------|
| **RFE-Core2** | The **mind** — the governed cognitive substrate (arbitrate, λ-isolation, the empirical spine). |
| **Liminal-Anchor-Engine** | Instrument — observe-only, watches *transitions* (the in-between). |
| **Paradox-Lattice-Engine** | Instrument — observe-only, watches *contradictions* (the collision). |
| **Talos_Kain** *(this repo)* | The **organism** — the agent lifecycle that a mind runs inside: sensorium, motor loop, memory ecosystem, sleep/wake, skill neurogenesis, identity kernel, telos. |

The governing law is the same one that runs through every repo in the family: **nothing modifies the system except through one audited gate.** Consolidation may nominate; it may not appoint.

## Cornerstone

- **`aamsfc.md`** — *Autonomous Agent Memory & Skill Flow Chart (v7)*: the full architecture, diagram + walkthrough. Provenance and authority as stated in that document (review and final authority: Samuel Grim).

## Working documents

- **`docs/north_star.md`** — the compass: *learn by losing, and be able to show it.*
- **`ROADMAP.md`** — sequencing. Current position: **T2**, making the cornerstone falsifiable.
- **`docs/BACKLOG.md`** — the open-work ledger, including what the linter found.
- **`tools/invariant_lint.py`** — asserts the cornerstone's invariants against its own
  diagram. The v5/v6 hand audit, automated. It currently reports one violation, which
  is real work rather than a broken test.

## The milestone

The **test** is small and already passes on the mock:

> measurably learns across games, and can point at the **named skill it grew** to get there.

The **milestone** is making that same test pass somewhere the world pushes back — **StarCraft II**, built-in AI on Easy, then a re-baseline at Medium to see whether a second curve appears. The game is the forcing function that drags the spec into code.

Worth keeping the two apart: the test needs episodic capture, a reward signal, and one skill that is born, promoted and cited. It does not need all of sensorium, motor loop, sleep, crucible and telos — those are the organism, not the milestone.

## On the name

**Talos** — the bronze automaton of Crete: a made, autonomous, guardian being, animated through a single sealed nail that its maker controls. **Kain** — the archetype of the agent who acts *on its own*, against the design. Together they name the tightrope this whole architecture exists to walk: *autonomous enough to matter, governed enough to trust.*

---

*This README is a provisional Claude-drafted stub. The architect (Samuel Grim) revises it into his own voice.*
