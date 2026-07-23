# Talos_Kain Roadmap

The organism, from specification to something that runs. Work items live in
[`docs/BACKLOG.md`](docs/BACKLOG.md); the compass lives in
[`docs/north_star.md`](docs/north_star.md). This file is sequencing only.

**Current position: T2.** The spine runs on a mock environment and the
cornerstone is mechanically checkable for the first time. One invariant fails.

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

## T1 — Milestone zero: the vertical slice (shipped, PRs #1–#3)

A Python spine under hexagonal layering — `domain/` holds types and ports,
`infrastructure/` holds SQLite stores and environments, `services/` holds the
organs. Zero third-party runtime dependencies on purpose; heavy deps arrive with
the organs that justify them.

**What actually runs** (`PYTHONPATH=. python3 scripts/run_mock.py`):

```
episodes         : 400  (contexts=4, actions=6)
win rate  first   40: 80.00%   ->   last 40: 100.00%
skills grown     : 4      (named, with confidence and provenance)
contexts mastered: 4 / 4  (self-model)
audit ledger ok  : True   (chain verified)
```

That is the north-star test — measurably learns, names the skill it grew —
passing against a deterministic mock. Also shipped: typed stubs for every v7
section (§0–§15), SQLite implementations for each memory tier, an SC2
environment and curriculum shell, and four test modules.

---

## T2 — The spec becomes falsifiable (current)

The point of this tier is that the document can be *wrong in public*.

**Shipped**
- `tools/mermaid_graph.py` — parses the cornerstone's flowchart. 157 nodes, 308 edges.
- `tools/invariant_lint.py` — asserts I1, I2, I4, I8, I10, I11, I12 against that
  graph. `--audit` reproduces the v5/v6 write-path ratios mechanically;
  `--growth` runs the dual: which stores have a drain.
- **B4 closed** — crucible stage count corrected against the diagram.

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

## T3 — Lint the territory, not just the map (B10)

The linter checks the diagram. Nothing checks `talos/`. A diagram that passes
while the implementation quietly doesn't is the same failure the linter exists
to prevent, one level down.

- Assert the structural invariants against the code: who imports and writes each
  store, and whether `identity.py` has exactly one writer in practice.
- I3, I5, I6, I7 and I9 were never diagram-checkable. They become testable here,
  as runtime assertions and tests rather than lint.
- `tests/test_gate.py` and `tests/test_audit_chain.py` are the seed of this.

**Exit criterion:** every invariant is enforced by something that runs — lint
for topology, tests for behaviour — with the unenforceable ones named.

---

## T4 — Growth stories (B7)

Its own tier, because it is the first thing that would bite a long-running
system and the last thing a short demo would reveal.

- `EPI` drain — highest priority. The crucible replays through it, so its size
  is the running cost of the strictest gate.
- `PROC` skill retirement.
- `HG` constraint decay beyond `LOCALPATCHMEM`.
- `AUDIT` tiering — hot replay window, cold archive, digests bridging.
- Check whether the SQLite stores already inherit the gap or dodged it.

**Exit criterion:** every store is either bounded, or documented as deliberately
unbounded with the reason written down.

---

## T5 — Wake the organs

Roughly twenty modules still raise `NotImplementedError`. Priority order follows
what the north-star test needs next rather than section order: sleep and
consolidation (§1, §8), then the identity crucible (§11), then telos (§15).

**Exit criterion:** the mock slice runs through a sleep cycle, wakes, and passes
the crucible on a real identity candidate.

---

## T6 — StarCraft II

The forcing function. Same test as milestone zero, somewhere the world pushes
back: built-in AI on Easy, `pysc2`/`burnysc2` moved out of the reserved extras.

**Exit criterion:** a losing streak becomes a win, and the system names the skill
that did it — on SC2, not the mock.

---

## T7 — Re-baseline

Medium difficulty; watch the second learning curve. A system that learns once may
have found a trick. A system that learns again after the ground moves is
learning.

**Exit criterion:** a second distinguishable curve, with a second named skill.

---

## T8+ — The organism proper (unspecified)

Where the harness stops being scaffolding around a narrow agent and becomes the
thing the cornerstone describes: sleep and wake on real consolidation pressure,
the crucible running on real episodic memory, telos above a real mission stream —
and a mind from `RFE-Core2` inside it rather than a task-specific policy.

Not scheduled. Not designed past the cornerstone. Named so the earlier tiers can
be checked against where they are supposed to lead.

---

## Tracked cross-tier items

- **`HORIZON` granularity (B8).** Blocks nothing; decide before T4 so the
  diagram's resolution is consistent when growth work touches it.
- **Dev dependencies.** `pytest` is an optional extra and is not installed in
  the WSL environment, so `tests/` has not been run there. `pip install -e .[dev]`
  in a venv.
- **The open problems** in `docs/BACKLOG.md` §3 are not roadmap items. They are
  standing admissions. Any tier that appears to close one has probably
  misunderstood it.

---

## History

- **2026-07-23** — T2 opened. Linter written; the cornerstone's invariants
  executable for the first time; B4 closed; B1a and B7 found by machine.
  Roadmap, backlog and north star created.
- **2026-07-22** — T1 shipped across PRs #1–#3: milestone-zero vertical slice,
  the dormant-organ tree, and the self-model organ.
- **Before that** — the cornerstone, v1 through v7. See `aamsfc.md` version
  history.
