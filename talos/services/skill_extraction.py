"""Skill neurogenesis (extraction + publishing).

Slice of §7. Two responsibilities, deliberately separated to honor the gate
law:

* ``SkillExtractor`` reads episodic memory and *nominates* candidates. It has
  no access to the skill store. It cannot appoint.
* ``SkillPublisher`` submits each candidate to the admission gate, and only
  on ``ADMIT`` writes a ``Skill`` and records the decision to the audit
  ledger. It is the single door.

The distilled candidate carries the episode lineage that produced it, so a
published skill answers "which games grew you?" as a query, not a story.

Two changes came with the reward engine (§5), so skills survive a drifting
world:

* nomination looks only at a recent **window** of episodes, so a winner that
  stopped winning ages out instead of dominating on lifetime count; and
* nomination consults the reward engine's **value**, so a stale action whose
  recency-weighted value has collapsed is never re-published even if its old
  wins are still in the window.
"""

from __future__ import annotations

import time

from talos.domain.gate import Gate
from talos.domain.ports import AuditStore, EpisodeStore, SkillStore
from talos.domain.types import GateDecision, Skill, SkillCandidate
from talos.services.reward_engine import RewardEngine


class SkillExtractor:
    """Nominates a per-context skill candidate from recent, still-valued
    episodic evidence."""

    def __init__(self, episodes: EpisodeStore, reward: RewardEngine, window: int = 25):
        self._episodes = episodes
        self._reward = reward
        self._window = window

    def nominate(self, context_id: str) -> SkillCandidate | None:
        episodes = self._episodes.by_context(context_id)
        if self._window:
            episodes = episodes[-self._window :]

        wins: dict[int, list[str]] = {}
        plays: dict[int, int] = {}
        for ep in episodes:
            if not ep.steps:
                continue
            action_id = ep.steps[0].action.action_id
            plays[action_id] = plays.get(action_id, 0) + 1
            if ep.outcome == "win":
                wins.setdefault(action_id, []).append(ep.episode_id)

        # Only actions the reward engine still trusts are consolidation-worthy.
        # This is what stops a drifted-away winner from being re-crowned on the
        # strength of stale wins still sitting in the window.
        trusted = {
            a: ids for a, ids in wins.items() if self._reward.is_trusted(context_id, a)
        }
        if not trusted:
            return None

        action_id = max(trusted, key=lambda a: len(trusted[a]))
        support = tuple(trusted[action_id])
        confidence = len(support) / plays[action_id]
        return SkillCandidate(
            context_id=context_id,
            action_id=action_id,
            confidence=confidence,
            provenance=support,
        )


class SkillPublisher:
    """The single writer into the skill store. Nothing else touches it.

    Submitting is *idempotent*: a governance write is recorded when the
    organism's skill state for a context actually changes, not on every tick.
    The extractor re-nominates after every episode, but a candidate that would
    re-decide an already-settled (context, action, verdict) is a no-op — it is
    neither re-published nor re-audited. This keeps the audit ledger a log of
    governance *events*, not of heartbeats.

    ``forget`` clears that memo for a context. Recovery calls it after demoting
    a drifted skill, so the replacement can be published even though the last
    settled decision was an ADMIT.
    """

    def __init__(self, skills: SkillStore, gate: Gate, audit: AuditStore):
        self._skills = skills
        self._gate = gate
        self._audit = audit
        # Last settled outcome per context: (action_id, decision).
        self._last: dict[str, tuple[int, GateDecision]] = {}

    def forget(self, context_id: str) -> None:
        self._last.pop(context_id, None)

    def submit(self, candidate: SkillCandidate) -> GateDecision:
        decision = self._gate.admit(candidate)

        outcome = (candidate.action_id, decision)
        if self._last.get(candidate.context_id) == outcome:
            # Nothing changed since the last decision for this context.
            return decision

        published_id = None
        if decision is GateDecision.ADMIT:
            existing = self._skills.for_context(candidate.context_id)
            # Version climbs past every prior skill for this context, retired
            # ones included, so a replacement never collides with a demoted id.
            version = self._skills.max_version(candidate.context_id) + 1
            if existing is not None and existing.action_id != candidate.action_id:
                # A different winning action supersedes the old skill.
                self._skills.retire(existing.skill_id)
            skill = Skill(
                skill_id=f"skill::{candidate.context_id}::v{version}",
                name=f"prefer-action-{candidate.action_id}-in-{candidate.context_id}",
                context_id=candidate.context_id,
                action_id=candidate.action_id,
                version=version,
                confidence=candidate.confidence,
                provenance=candidate.provenance,
                created_at=time.time(),
            )
            self._skills.publish(skill)
            published_id = skill.skill_id

        # A real change in governance state — record it. The gate decision is
        # a governance event; the ledger is where it lives.
        self._audit.record(
            "skill.admission",
            {
                "decision": decision.value,
                "context_id": candidate.context_id,
                "action_id": candidate.action_id,
                "confidence": candidate.confidence,
                "provenance": list(candidate.provenance),
                "published_skill_id": published_id,
            },
        )
        self._last[candidate.context_id] = outcome
        return decision
