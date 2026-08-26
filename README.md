# Talos_Kain

**The organism.** An autonomous-agent harness that gets better at something by
failing at it — repeatedly, unattended, over a long time — and can point at the
named skill it grew. The body and nervous system that wraps a cognitive *mind*
and lets it live, act, learn, rest, and remain itself across time.

The thesis is small enough to falsify: a noisy losing streak becomes reliable
winning, and the improvement is attributable to a *named, provenance-bearing
skill* the organism grew from the games it lost — not to variance, and not to a
hand-tuned policy. Everything else in the architecture exists to make that claim
survive contact with a world that pushes back, and to keep the whole thing
**governed**: nothing modifies the system except through one audited gate.

> **Status.** The spine runs and three organs are awake, on a deterministic mock
> world, with **26 tests green** and a verified audit chain.
> - **Learning** — 400 episodes, ~80% → 100% win rate, one named skill grown per
>   context, each carrying the episode lineage that produced it.
> - **Self-model** (§11 tail) — the organism models its own track record and
>   uses it to make exploration bounded instead of a blind walk.
> - **Reward engine** (§5) — prediction-error signal that lets a confident agent
>   notice it is *wrong* and recover when the world drifts under it.
> - **Wake / run-continuity** (§1/§9) — a run now survives interruption (crash,
>   power-off, hibernate) and **resumes** instead of restarting.
>
> Most of the v7 spec's organs are still typed stubs that raise
> `NotImplementedError` — the autonomic *sleep* pressure, the identity crucible,
> telos, the federated cortex, the immune system — and **StarCraft II is not yet
> wired**. The cornerstone (`aamsfc.md`) describes far more than is built; treat
> every mechanism it names as a hypothesis until `talos/` implements it.

## Run it

```bash
# The learning slice — stdlib only, no install, ephemeral temp stores.
PYTHONPATH=. python3 scripts/run_mock.py

# Dev install + the full test suite (26 tests) + the invariant linter.
python3 -m venv .venv && .venv/bin/pip install -e .[dev]
.venv/bin/python -m pytest -q
python3 tools/invariant_lint.py aamsfc.md --audit --growth
```

A run prints a rising win rate and the skills it grew, with the game count
behind each:

```
episodes         : 400  (contexts=4, actions=6)
win rate  first  40: 85.00%
win rate  last   40: 100.00%
skills grown     : 4
  - prefer-action-2-in-ctx-0  (confidence=1.00, from 3 games)
  ...
audit ledger ok  : True
```

### Persist and resume

By default a run lives in a temp dir and vanishes. Give it a durable home and a
stable id, and it becomes **resumable** — kill it and re-run the same command;
it wakes from where it left off instead of starting over:

```bash
# Start a persistent run.
python3 scripts/run_mock.py --state-dir ./run --run-id demo --episodes 400
#   ^C, power loss, hibernate, whatever — then simply run it again:
python3 scripts/run_mock.py --state-dir ./run --run-id demo --episodes 400
#   -> [wake] run demo: resume from episode N  (audit_ok=True, ...)
```

On wake, the organism verifies its audit chain, rebuilds the in-memory
modulation state (the reward value table and the admission memo) from the
durable log, fast-forwards the world, and continues. See
[ADR 0002](docs/decisions/0002-resume-and-wake.md) for the design and its honest
boundary (bit-identical resume at episode boundaries; a bounded, self-healing
skew for a hard crash mid-episode).

## Architecture

Hexagonal: `domain` (pure organism logic) never imports SQLite or a game engine.
Swapping the store or the world is an infrastructure change behind a
`talos.domain.ports` Protocol.

```
talos/
  domain/          types, ports (Protocols), the admission gate, reward law
  services/        the loop (organism), sensorium, motor, policy, reflection,
                   reward engine, skill neurogenesis, resume/wake
  infrastructure/  SQLite stores (one file per store — bulkhead containment),
                   the mock + SC2 environment adapters, telemetry
```

Three invariants are load-bearing from commit one:

1. **Hash-chained audit ledger** — each row carries the previous row's digest;
   `verify()` recomputes the chain. The ledger is the trust root, and a run
   refuses to resume onto a tampered one.
2. **Provenance-aware schema** — every episode records `run_id` + `seed` + env
   version; every skill stores the episode lineage that grew it. "This skill
   emerged from these games" is a query, not a story.
3. **One universal admission gate** — nothing writes to a behavior-shaping store
   directly; `gate.admit()` returns `ADMIT/REJECT/DEFER/ESCALATE` and the
   decision is logged. Consolidation may nominate; it may not appoint.

## Where this sits (the family)

| Repo | Role |
|------|------|
| **RFE-Core2** | The **mind** — the governed cognitive substrate (arbitrate, λ-isolation, the empirical spine). |
| **Liminal-Anchor-Engine** | Instrument — observe-only, watches *transitions* (the in-between). |
| **Paradox-Lattice-Engine** | Instrument — observe-only, watches *contradictions* (the collision). |
| **Talos_Kain** *(this repo)* | The **organism** — the agent lifecycle a mind runs inside: sensorium, motor loop, memory ecosystem, sleep/wake, skill neurogenesis, identity kernel, telos. |

The governing law runs through every repo in the family: **nothing modifies the
system except through one audited gate.**

## Cornerstone & working documents

- **`aamsfc.md`** — *Autonomous Agent Memory & Skill Flow Chart (v7)*: the full
  architecture, diagram + walkthrough. Review and final authority: Samuel Grim.
- **`docs/north_star.md`** — the compass: *learn by losing, and be able to show it.*
- **`docs/decisions/`** — architecture decision records (language & skeleton;
  run continuity).
- **`ROADMAP.md`** — sequencing. Current position: **T2**, making the cornerstone
  falsifiable.
- **`docs/BACKLOG.md`** — the open-work ledger, including what the linter found.
- **`tools/invariant_lint.py`** — asserts the cornerstone's invariants against its
  own diagram (the v5/v6 hand audit, automated). It currently reports one
  violation, which is real work rather than a broken test.

## The milestone

The **test** is small and already passes on the mock:

> measurably learns across games, and can point at the **named skill it grew** to
> get there.

The **milestone** is making that same test pass somewhere the world pushes back —
**StarCraft II**, built-in AI on Easy, then a re-baseline at Medium to see whether
a second curve appears. The game is the forcing function that drags the spec into
code. The test needs episodic capture, a reward signal, and one skill that is
born, promoted and cited — not all of sensorium, sleep, crucible and telos. Those
are the organism; this is the milestone.

## On the name

**Talos** — the bronze automaton of Crete: a made, autonomous, guardian being,
animated through a single sealed nail that its maker controls. **Kain** — the
archetype of the agent who acts *on its own*, against the design. Together they
name the tightrope this architecture exists to walk: *autonomous enough to
matter, governed enough to trust.*

## License

AGPL-3.0. Commercial terms available on request; see `CONTRIBUTING.md` for the
dual-license grant-back.
