# Talos_Kain Roadmap

The organism, from specification to something that runs. Work items live in
[`docs/BACKLOG.md`](docs/BACKLOG.md); the compass lives in
[`docs/north_star.md`](docs/north_star.md). This file is sequencing only.

**Current position: T2.** The spine runs on a mock environment and the
cornerstone is mechanically checkable for the first time. One invariant fails.

## How tiers are judged

Against the north star — **learn by losing, and be able to show it** — not
against their own artifacts. A tier that produces a cleaner document, a greener
lint, or a tidier backlog has produced maintenance. The question for every tier
is what it lets the organism *fail at, survive, and learn from* that it couldn't
before.

Tiers T2 through T4 are governance and hygiene. They are real work and they are
not the road. They earn their place by being cheap now and expensive later, and
each one below says why. If a tier can't answer that question, it should be
deferred behind the organs.

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
drifts / recover : 0 / 0  (reward-surprise)
audit ledger ok  : True   (chain verified)
```

That is the north-star test — measurably learns, names the skill it grew —
passing against a mock. Also shipped: typed stubs for every v7 section (§0–§15),
SQLite implementations for each memory tier, an SC2 environment and curriculum
shell, 21 tests, and two **woken organs** — the self-model (§11 tail) and the
reward engine (§5), which lets the organism recover from a drifting world
instead of locking into confident failure.

---

## T2 — Mature the learning architecture on the mock (current)

**The governing rule, from [`docs/BACKLOG.md`](docs/BACKLOG.md): organs wake
only when gameplay exposes the need, not on speculation.** So this tier is
ordered by forcing function, and the mock world is the cheap place to find them.

1. **Stochastic world.** Outcomes stop being deterministic. Highest value,
   because it forces two things at once: the recovery trigger has to move from
   surprise-threshold to **value-collapse** (which distinguishes an unlucky loss
   from a stale belief), and value learning has to become a real running
   estimate rather than a binary winner.
2. **Multi-step episodes.** Unlocks credit assignment, TD error over a
   trajectory, and makes the cerebellar reflex and motor-yield meaningful —
   there is nothing to yield *to* in a one-step world.

**Exit criterion:** the organism still learns, and still names what it learned,
when outcomes are noisy and rewards are delayed. That is the difference between
a learner and a lookup table, and it is the last thing the mock can teach.

### Maintenance lane, riding alongside

The cornerstone's invariants are executable now (`tools/invariant_lint.py`), and
the linter exits 1. Under the forcing-function rule, only the items whose fix
stops being cheap belong here — see **Spec & governance** in the backlog:

- **META has no edge to `CTRL`**, and the `CTRL` split it requires, and the I10
  rewrite that follows. Forcing function: **before §12 metacognition wakes**,
  because `metacognition.py` is dormant and fixing the spec now costs an edit.
- **Lint the code, not just the diagram.** Forcing function: the next organ
  waking, since every waking is a chance for spec and code to diverge silently.

The governor, the threat-model entries and the grounding paragraph are deferred
in the backlog with the reason written down. **This lane is maintenance. It is
not the road, and it will take everything it is given.**

**Why now:** B1, B1a and B3 are corrections to how self-modification is gated,
and `talos/services/metacognition.py` has not been written against them yet.
Fixing the spec now costs an edit; fixing it after the module exists costs a
refactor of the machinery the whole governance argument rests on. B2, B5 and B6
are prose — they can wait, and they will be better written once there is code to
check them against. **Timebox this tier.** It is the most comfortable pile to
work in and it will take everything it is given.

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

**Why it serves learning:** an organism that learns unattended is one whose
gates nobody is watching in real time. The gates have to hold by construction or
the whole premise of running it for a long time alone is a hope. This is the
tier that turns the governing law from a claim into a property.

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

**Why it serves learning:** learning by losing means accumulating an enormous
number of losses. Every one of them lands in `EPI`, and the crucible replays
through `EPI`. Unbounded growth is not a tidiness problem here — it is the
mechanism by which a system that loses a lot gradually becomes unable to learn
from it. This tier is the price of the north star being *repeated* failure
rather than a demo.

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
