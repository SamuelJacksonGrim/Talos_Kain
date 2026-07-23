# North Star — learn by losing, and be able to show it

The end goal, stated plainly (Samuel, 2026-07-23):

> The organism gets **better at something by failing at it** — repeatedly,
> unattended, over a long time — and can **point at what it learned**. A noisy
> losing streak becomes a durable win, and there is a named skill to show for it.
> It survives that failure without drifting into something else: everything it
> became, it became through a door that was watched.
>
> Governance is what makes running it unattended safe. It is not what the running
> is for.

This is the compass. Every mechanism in `aamsfc.md` is measured against it, and
so is every tier in the roadmap.

## What "learn by losing" actually commits to

- **Losing is the signal, not the error state.** Failure is the training data.
  That makes the reward path and skill neurogenesis the spine, and everything
  else support.
- **It has to survive losing.** Repeated failure without collapse, without
  drift, without becoming something else in order to cope. This is where the
  governing law re-enters — as what makes unattended failure safe to run.
- **It has to be able to show you.** A named, versioned skill you can point at
  and diff out of the library. Learning that can't be exhibited is
  indistinguishable from noise.

## The governing law (the constraint, not the goal)

One sentence, and it runs through every repo in the family:

**Nothing modifies the system except through one audited gate. Consolidation may
nominate; it may not appoint.**

Everything else in the architecture is that sentence applied to a specific
domain — identity through `ANNEAL`, capability through `PUBLISH`, control-plane
change through `META`, campaign purpose through `HORIZON`, standing purpose
through the architect's signature.

It is what lets the organism fail ten thousand times unattended and still be
itself on the other side. That is a precondition for the north star, and a
precondition is not a destination.

## The tightrope the name states

**Talos** — the bronze automaton, autonomous and guardian, animated through a
single sealed nail its maker controls. **Kain** — the agent who acts on its own,
against the design.

*Autonomous enough to matter, governed enough to trust.* Every design decision
in this repo is a position on that line, and the invariants exist so a position
can't be moved by accident.

## Why this is reachable

The forcing-function loop already runs end to end — `observe → score → choose →
act → reward → record → learn` — and it learns. What is live, what is dormant,
and which module holds each: **[`architecture.md`](architecture.md)**. That file
is the source of truth for build state; this one does not duplicate it.

## The three real gaps

1. **The spine runs, two organs are awake, nineteen aren't.** The learning loop
   is real on a mock environment — 400 episodes, 80% → 100%, four named skills,
   verified ledger, 21 tests — and the self-model (§11 tail) and reward engine
   (§5) are live, so it can recover from a drifting world rather than locking
   into confident failure. That is a genuinely different thing from a
   specification. It is also not yet sleep, not yet the crucible, not yet telos,
   and not yet StarCraft. Organs wake on forcing function, not on speculation —
   see [`BACKLOG.md`](BACKLOG.md).

2. **The invariants are checked against the map, not the territory.**
   `invariant_lint.py` asserts I1, I2, I4, I8, I10, I11 and I12 against
   `aamsfc.md`'s diagram. Nothing yet asserts them against `talos/`. A diagram
   that passes and an implementation that quietly doesn't is exactly the failure
   the linter exists to prevent, one level down. I3, I5, I6, I7 and I9 constrain
   payloads, timing and staging — they were never diagram-checkable and become
   testable only against running code.

3. **Growth has one worked story.** `SEM → EVICT` is the only store in the
   *diagram* with a bounded-growth path. `EPI`, `HG`, `PROC` and `AUDIT`
   accumulate without drain. The identity crucible replays through `EPI`, so the
   cost of the strictest gate rises for the life of the system — and a gate that
   gets too expensive is a gate that gets skipped. Whether the SQLite stores
   inherit that gap is unchecked.

## What "done" would look like for the first era

Not the full organism. The smallest thing that proves the spec touches reality:

> An agent that **measurably learns across games**, and can point at the **named
> skill it grew** to get there.

**That test already passes on the mock environment.** What remains is making it
pass somewhere the world pushes back — StarCraft II on Easy, then a re-baseline
at Medium to see whether a second curve appears. See `ROADMAP.md`.

---

*Related: [`../README.md`](../README.md) · [`../aamsfc.md`](../aamsfc.md) ·
[`BACKLOG.md`](BACKLOG.md) · [`../ROADMAP.md`](../ROADMAP.md)*
