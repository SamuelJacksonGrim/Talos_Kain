# Talos_Kain Roadmap

The organism, from specification to something that runs. Work items live in
[`docs/BACKLOG.md`](docs/BACKLOG.md); the compass lives in
[`docs/north_star.md`](docs/north_star.md). This file is sequencing only.

**Current position: T1.** The specification is complete through v7 and is now
mechanically checkable for the first time. One invariant fails.

---

## T0 — The cornerstone (shipped)

`aamsfc.md` v1–v7. Six problems answered: reflex speed over disk-speed memory,
learning without being programmed by the world, rest without dying, finite
memory that keeps what matters, change without ceasing to be itself, and knowing
what it is for.

Two hardening passes (v5, v6) established the method the rest of this roadmap
leans on: **enumerate every write path into a protected object, and check the
ratio of gated to total.** It found the same bug class twice.

---

## T1 — The spec becomes falsifiable (in progress)

The point of this tier is that the document can be *wrong in public*.

**Shipped**
- `tools/mermaid_graph.py` — parses the cornerstone's flowchart into an edge
  list. 157 nodes, 308 edges.
- `tools/invariant_lint.py` — asserts I1, I2, I4, I8, I10, I11, I12 against that
  graph. `--audit` reproduces the v5/v6 write-path ratios mechanically.
  `--growth` runs the dual: which stores have a drain.
- **B4 closed** — crucible test count corrected against the diagram.

**Open — this is v8**
1. **B1** split `CTRL` → `CTRL_OPS` / `CTRL_CONFIG`
2. **B1a** reroute META's seven lateral edges to `CTRL_CONFIG`
3. **B1b** config epochs (precompiled delta + pointer swap, per §9)
4. **B2** governor on `CTRL_OPS`
5. **B3** rewrite I10 without the word "tuning"
6. **B5** threat model: governor-as-proxy, config shadow writes, amend
   wake-state executive compromise
7. **B6** the grounding paragraph — written last, placed first

**Exit criterion:** `invariant_lint.py` exits 0, and every invariant it *can't*
check is listed as such in the document rather than implied to hold.

---

## T2 — Growth stories (B7)

Deliberately its own tier, because it is the first thing that would bite a
long-running system and the last thing a short demo would reveal.

- `EPI` drain — highest priority. The crucible replays through it, so its size
  is the cost of the strictest gate.
- `PROC` skill retirement.
- `HG` constraint decay beyond `LOCALPATCHMEM`.
- `AUDIT` tiering — hot replay window, cold archive, digests bridging.

**Exit criterion:** every store in `--growth` is either bounded, or documented
as deliberately unbounded with the reason written down.

---

## T3 — First code: the narrow test

The milestone as usually quoted is "sensorium + motor loop + reward + episodic
memory + skill neurogenesis." That is five subsystems and most of the
architecture. **The test is much smaller than the subsystem list** (B9):

> A StarCraft II agent that measurably learns across games, and can point at the
> **named skill it grew** to get there.

That test needs: episodic capture, a reward signal, and one skill that is born,
promoted through the CI gauntlet, and cited in a win. Sensorium and motor loop
can be dumb glue at this tier. Everything else in the cornerstone stays on
paper.

**Exit criterion:** a losing streak becomes a win, and the system names the
skill that did it. Curriculum: built-in AI on Easy first.

---

## T4 — Re-baseline

Medium difficulty, and watch the second learning curve. A system that learns
once may have found a trick; a system that learns again after the ground moves
is learning.

**Exit criterion:** a second distinguishable curve, with a second named skill.

---

## T5+ — The organism proper (unspecified)

Where the harness stops being scaffolding around a narrow agent and starts being
the thing the cornerstone describes: sleep and wake on real consolidation
pressure, the identity crucible running on real episodic memory, telos above a
real mission stream — and a mind from `RFE-Core2` running inside it rather than
a task-specific policy.

Not scheduled. Not designed past the cornerstone. Named so the earlier tiers can
be checked against where they are supposed to lead.

---

## Tracked cross-tier items

- **The invariants that need a runtime.** I3, I5, I6, I7, I9 constrain payloads,
  timing, and staging. They cannot be linted from a diagram and become testable
  only at T3. Until then they are prose, and the north star says so.
- **`HORIZON` granularity (B8).** Blocks nothing; decide before T2 so the
  diagram's resolution is consistent when growth work touches it.
- **The open problems** in `docs/BACKLOG.md` §3 are not roadmap items. They are
  standing admissions. Any tier that appears to close one has probably
  misunderstood it.

---

## History

- **2026-07-23** — T1 opened. Linter written; invariants executable for the
  first time; B4 closed; B1a and B7 found by machine. Roadmap, backlog, and
  north star created.
- **Before that** — the cornerstone, v1 through v7. See `aamsfc.md` version
  history.
