"""Resume — reconstruct volatile state so an interrupted run continues.

This is the working body behind the sleep/wake seam (§1/§9). The organism's
stores of record — episodic archive, skills, self-model, audit ledger — are
durable SQLite and survive a crash untouched. But two pieces of state live
only in memory during a run, and a freshly started process has neither:

* the **reward engine's** recency-weighted value table, ``V(context, action)``;
* the **publisher's** settled-decision memo, its admission de-dup cache.

Both are pure functions of the durable log, exactly as their own docstrings
promise ("rebuildable from the experience log", "a de-dup cache, not a store of
record"). This module rebuilds them, and fast-forwards the environment's own
internal state, so the resumed loop is bit-identical to one that never stopped.

The contract in one line: **rebuild the fast, volatile state from the slow,
durable state, then continue.** That is what "wake ingests a delta manifest for
zero-latency restore" means once it is code instead of a docstring.
"""

from __future__ import annotations

from dataclasses import dataclass

from talos.domain.ports import (
    AuditStore,
    Environment,
    EpisodeStore,
    RunStateStore,
)
from talos.domain.types import GateDecision
from talos.services.reward_engine import RewardEngine
from talos.services.skill_extraction import SkillPublisher
from talos.util.ids import episode_seed


@dataclass(frozen=True)
class ResumeManifest:
    """What a wake resolved before the loop turns again. Small on purpose —
    it is the compiled pointer-and-summary a restore reads, and it doubles as
    an inspectable receipt of what was rebuilt."""

    run_id: str
    run_seed: int
    env_name: str
    resume_from: int          # first episode index still to run
    target_episodes: int
    fresh: bool               # True: no prior cursor, a brand-new run
    reward_keys: int          # (context, action) values rebuilt into the reward engine
    memo_contexts: int        # contexts whose admission memo was rehydrated
    audit_ok: bool            # the durable ledger verified before we trusted it

    @property
    def complete(self) -> bool:
        return self.resume_from >= self.target_episodes


def rebuild_reward(
    episodes: EpisodeStore,
    run_id: str,
    resume_from: int,
    *,
    reward: RewardEngine | None = None,
) -> RewardEngine:
    """Replay the committed episodes in order, folding each outcome back into a
    reward engine exactly as the live loop did. Only episodes strictly before
    ``resume_from`` are folded: an episode that was saved but not fully
    committed (a crash mid-episode) is left for the loop to re-run, so its
    reward is counted once, by the re-run, not here."""
    engine = reward or RewardEngine()
    for ep in episodes.for_run(run_id)[:resume_from]:
        if not ep.steps:
            continue
        step = ep.steps[0]
        engine.observe(ep.context_id, step.action.action_id, step.reward)
    return engine


def rebuild_publisher_memo(
    audit: AuditStore,
) -> dict[str, tuple[int, GateDecision]]:
    """Reconstruct the publisher's settled-decision memo from the audit ledger.

    The ledger is the durable record of every governance event. Replaying it in
    order reproduces the exact memo the live publisher held: an ``skill.admission``
    settles ``(action_id, decision)`` for its context; a ``skill.demotion``
    (emitted by drift recovery, which calls ``publisher.forget``) clears it, so
    the replacement can be published afterwards."""
    memo: dict[str, tuple[int, GateDecision]] = {}
    for rec in audit.history():
        if rec.kind == "skill.admission":
            ctx = rec.payload["context_id"]
            memo[ctx] = (rec.payload["action_id"], GateDecision(rec.payload["decision"]))
        elif rec.kind == "skill.demotion":
            memo.pop(rec.payload["context_id"], None)
    return memo


def fast_forward_env(env: Environment, run_seed: int, resume_from: int) -> None:
    """Advance the environment's internal state to the resume point by replaying
    the resets of already-committed episodes. ``reset`` is a pure function of
    the episode seed for a stationary world (a no-op to fast-forward), but a
    drifting world advances hidden state on every reset; replaying those resets
    reproduces that state exactly, using only the ``Environment`` port."""
    for index in range(resume_from):
        env.reset(episode_seed(run_seed, index))


def plan_resume(
    run_store: RunStateStore,
    run_id: str,
    default_seed: int,
    env_name: str,
    target_episodes: int,
) -> tuple[int, bool]:
    """Read the durable cursor. Returns ``(resume_from, fresh)``: where the loop
    should start, and whether this is a brand-new run (no cursor yet)."""
    state = run_store.load(run_id)
    if state is None:
        return 0, True
    return state.resume_from, False


def wake(
    *,
    run_store: RunStateStore,
    run_id: str,
    run_seed: int,
    env: Environment,
    episodes: EpisodeStore,
    audit: AuditStore,
    reward: RewardEngine,
    publisher: SkillPublisher,
    target_episodes: int,
) -> ResumeManifest:
    """The one call a driver makes to bring a run back. Verifies the trust root,
    rebuilds the volatile state in place (``reward`` and ``publisher`` are
    mutated to match the durable log), fast-forwards the environment, and
    returns the manifest describing where the loop resumes.

    On a fresh run (no cursor) it verifies the ledger and returns a
    ``resume_from == 0`` manifest without rebuilding anything — there is nothing
    yet to rebuild — so the same path serves both first start and restart.
    """
    audit_ok = audit.verify()
    resume_from, fresh = plan_resume(run_store, run_id, run_seed, env.name, target_episodes)

    if not fresh and resume_from > 0:
        rebuild_reward(episodes, run_id, resume_from, reward=reward)
        memo = rebuild_publisher_memo(audit)
        publisher.restore_memo(memo)
        fast_forward_env(env, run_seed, resume_from)
    else:
        memo = {}

    return ResumeManifest(
        run_id=run_id,
        run_seed=run_seed,
        env_name=env.name,
        resume_from=resume_from,
        target_episodes=target_episodes,
        fresh=fresh,
        reward_keys=reward.known_pairs(),  # receipt of the rebuild
        memo_contexts=len(memo),
        audit_ok=audit_ok,
    )
