# ADR 0002 — Run continuity: durable cursor + wake-time state rebuild

**Status:** accepted · **Date:** 2026-08-26

## Context

The milestone-zero loop (`services/organism.py`) runs a fixed
`for i in range(n_episodes)` against throwaway temp-dir stores and stamps a
fresh `run_id` every process. Kill it — a crash, a power-off, a laptop
hibernating mid-run — and it starts over from zero. Nothing reads the durable
state back to continue.

That is the missing half of an *autonomous* organism. The v7 spec already names
it: `services/sleep.py`'s `WakeSequence` — *"wake ingests a pre-compiled delta
manifest for zero-latency restore"* — but it was a `raise NotImplementedError`.
For a resident mind meant to run unattended over long stretches and survive the
machine sleeping, "resume where you were" is not a nicety; it is the difference
between a process and an organism.

The stores of record are already durable (SQLite, one file per store). Two
pieces of live state are **not** — they exist only in memory during a run:

- the reward engine's recency-weighted value table `V(context, action)`;
- the publisher's settled-decision memo (its admission de-dup cache).

Both already document themselves as *rebuildable from the experience log* /
*a de-dup cache, not a store of record*. A restart that ignored them would
stall learning (an empty value table trusts nothing) and corrupt the ledger
(an empty memo re-publishes settled skills and re-audits them).

## Decision

**Add a durable run cursor and a wake step that rebuilds volatile state from
the durable log before the loop turns again.** The contract in one line:
*rebuild the fast, volatile state from the slow, durable state, then continue.*

- **`RunState` + `RunStateStore` (`run_state.db`).** One upserted row per run:
  `last_index` (highest fully-committed episode), `run_seed`, `env_name`,
  target, status. Written **last** in each episode — after episodic, reflection,
  reward, and admission have all committed — so it is the single authority on
  "how far did we genuinely get." This is the small "delta manifest" the spec's
  wake ingests, not a replay of the WAL.
- **`services/resume.py`** rebuilds `V` by replaying the committed episodes'
  outcomes through the reward engine, rebuilds the memo by replaying the audit
  ledger's `skill.admission` / `skill.demotion` events, and fast-forwards the
  environment by replaying `reset()` for the committed episodes (so a *drifting*
  world's hidden state is reproduced exactly, using only the `Environment`
  port). It verifies the audit chain before trusting any of it.
- **`WakeSequence.wake()` is now real**, delegating to `resume`. The autonomic
  *pressure* organs (`SleepAccumulator`, `SleepDebt`) stay dormant — episodes
  are still cheap and synchronous — but the wake half of the cycle is code.
- **The driver gains `--state-dir` / `--run-id`.** With them, a run persists and
  resumes; without them, the classic ephemeral temp-dir run is unchanged. The
  same wake path serves a first start (no cursor → `resume_from == 0`) and a
  restart alike.
- **The per-episode seed formula moves to `util/ids.py`** (`episode_seed`), a
  single source of truth shared by the live loop and the resume replay so they
  can never disagree about what episode `index` means.

## The guarantee, and its honest boundary

Resume is **bit-identical** — same grown skills, same self-model, same
digest-for-digest audit chain — when a run is interrupted **at an episode
boundary**: a kill, a power-off, or a hibernate between episodes. That is the
real-world case for a resident cortex waking from sleep, and it is proven by
`test_resume.py` comparing a crash-and-resume run against an uninterrupted one.

It is **not** bit-identical for a hard crash in the sub-millisecond window
*inside* an episode, between its side effects and its cursor write. Reflection
is non-idempotent by design (the drift organ deliberately re-runs episodes to
re-converge), and there is no atomic commit across the separate store files, so
the re-run of that one in-flight episode can re-apply its self-model fold.
What stays exact even then: the **audit ledger, the grown skills, and the
episodic outcomes** (reward and memo are rebuilt from the durable log, so no
skill is re-published and no ledger entry is duplicated), and the self-model's
behavioral verdict. Only a counter may be off by that single episode, which the
organism self-corrects. Making that window exact too would need per-effect
journaling or a single-transaction store — deferred until an organ needs it.

## Consequences

- A persistent run survives interruption and continues: proven end-to-end
  across two separate OS processes via `--state-dir`/`--run-id`, and in five
  `test_resume.py` cases (boundary crash, commit-window crash, drifting-world
  reconstruction, completed-run no-op, tampered-ledger detection).
- `revive-cortex.ps1`-style process revival (bring the *server* back) and this
  (bring the *run* back) compose: the former is layer 1, this is layers 2–3.
- No third-party dependency added; still stdlib + SQLite. Existing 21 tests
  unchanged and green.
- Follow-ups: the mid-episode exactness window; waking the *sleep* organs so the
  organism decides when to rest, not just how to return.

## Provenance

Pattern origin: the idempotent probe-then-restore shape in an external agent
scaffold's hibernate/revive doc, generalized to "rebuild volatile from durable."
Design + implementation: Claude. Review and final authority: Samuel Grim.
