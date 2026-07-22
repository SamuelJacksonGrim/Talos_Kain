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
"""

from __future__ import annotations

import time

from talos.domain.gate import Gate
from talos.domain.ports import AuditStore, EpisodeStore, SkillStore
from talos.domain.types import GateDecision, Skill, SkillCandidate


class SkillExtractor:
    """Nominates a per-context skill candidate from episodic evidence."""

    def __init__(self, episodes: EpisodeStore, min_support: int = 3):
        self._episodes = episodes
        self._min_support = min_support

    def nominate(self, context_id: str) -> SkillCandidate | None:
        wins: dict[int, list[str]] = {}
        plays: dict[int, int] = {}
        for ep in self._episodes.by_context(context_id):
            if not ep.steps:
                continue
            action_id = ep.steps[0].action.action_id
            plays[action_id] = plays.get(action_id, 0) + 1
            if ep.outcome == "win":
                wins.setdefault(action_id, []).append(ep.episode_id)

        if not wins:
            return None

        # Winning action with the most supporting episodes.
        action_id = max(wins, key=lambda a: len(wins[a]))
        support = tuple(wins[action_id])
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
    """

    def __init__(self, skills: SkillStore, gate: Gate, audit: AuditStore):
        self._skills = skills
        self._gate = gate
        self._audit = audit
        # Last settled outcome per context: (action_id, decision).
        self._last: dict[str, tuple[int, GateDecision]] = {}

    def submit(self, candidate: SkillCandidate) -> GateDecision:
        decision = self._gate.admit(candidate)

        outcome = (candidate.action_id, decision)
        if self._last.get(candidate.context_id) == outcome:
            # Nothing changed since the last decision for this context.
            return decision

        published_id = None
        if decision is GateDecision.ADMIT:
            existing = self._skills.for_context(candidate.context_id)
            version = (existing.version + 1) if existing else 1
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
