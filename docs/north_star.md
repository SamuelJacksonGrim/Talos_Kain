# North Star — an organism that stays itself while it changes

The end goal, stated plainly:

> A mind can run inside this harness **continuously** — acting, learning,
> resting, and waking — for a long time, and still be **recognizably the same
> mind** at the end of it. Everything it becomes, it became through a door that
> was watched. Nothing it became happened by accident, by drift, or by anyone
> who wasn't supposed to have a say.

This is the compass. Every mechanism in `aamsfc.md` is a step toward it, and
every finding, gate, and invariant is measured against it.

> **Draft notice.** The statement above is a Claude draft assembled from the
> README and the cornerstone. It is written here so collaborators aim at the
> same target, not because it is final. The architect (Samuel Grim) revises it
> into his own words, exactly as with `README.md`.

## The governing law

One sentence, and it runs through every repo in the family:

**Nothing modifies the system except through one audited gate. Consolidation may
nominate; it may not appoint.**

Everything else in the architecture is that sentence applied to a specific
domain — identity through `ANNEAL`, capability through `PUBLISH`, control-plane
change through `META`, campaign purpose through `HORIZON`, standing purpose
through the architect's signature.

## The tightrope the name states

**Talos** — the bronze automaton, autonomous and guardian, animated through a
single sealed nail its maker controls. **Kain** — the agent who acts on its own,
against the design.

*Autonomous enough to matter, governed enough to trust.* Every design decision
in this repo is a position on that line, and the invariants exist so a position
can't be moved by accident.

## Why this is reachable: what already exists

| Capability | What it needs | Where it lives today |
|---|---|---|
| **Live** | sensorium, motor loop, reflex-speed action over disk-speed memory | §0, §3, §4 — designed |
| **Learn** | episodic capture, consolidation, skill neurogenesis | §3, §7, §8 — designed |
| **Rest** | autonomic sleep pressure, blind leases, zero-latency wake | §1, §8, §9 — designed |
| **Stay itself** | identity kernel behind a forensic crucible | §10, §11 — designed |
| **Know what it's for** | tiered telos, wake-path fit check, horizon gate | §15 — designed |
| **Be checkable** | invariants phrased as violations | `tools/invariant_lint.py` — **running** |

The last row is the only one that is not a hypothesis, and it is the newest. It
matters out of proportion to its size: it is the first thing in this repo that
can be *wrong in public*.

## The three real gaps

1. **None of it is code.** 723 lines of specification, zero lines of
   implementation. Every mechanism above is a hypothesis until it survives
   contact with a running system. The document says this on every page and the
   discipline is worth keeping.

2. **Half the invariants aren't structurally checkable.** I1, I2, I4, I8, I10,
   I11, I12 can be asserted against the diagram today. I3, I5, I6, I7, I9
   constrain payloads, timing, and staging — they need a runtime, and until
   there is one they are prose.

3. **Growth has one worked story.** `SEM → EVICT` is the only store in the
   architecture with a bounded-growth path. `EPI`, `HG`, `PROC`, and `AUDIT`
   accumulate without drain. The identity crucible replays through `EPI`, so the
   cost of the strictest gate rises for the life of the system — and a gate that
   gets too expensive is a gate that gets skipped.

## What "done" would look like for the first era

Not the full organism. The smallest thing that proves the spec touches reality:
a StarCraft II agent that **measurably learns across games**, and can point at
the **named skill it grew** to get there. See `ROADMAP.md` for why that test is
smaller than the subsystem list it is usually quoted with.

---

*Related: [`../README.md`](../README.md) · [`../aamsfc.md`](../aamsfc.md) ·
[`BACKLOG.md`](BACKLOG.md) · [`../ROADMAP.md`](../ROADMAP.md)*
