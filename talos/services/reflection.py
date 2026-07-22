"""Reflection (§11 tail: REFLECT -> SELFMOD -> SELFSTORE).

Woken for the self-model organ. After each episode, the reflector updates the
organism's model of itself for that context: one more attempt, the action it
tried, whether it won, and the winning action once found. Milestone zero
reflects incrementally per episode, which is the light-sleep micro-batch of
the full spec; deep-sleep batch reflection is a later wake.

The scope is deliberately narrow. This is metacognition, not identity. It
records strengths, blind spots, and calibration. The moment a reflection would
touch the identity kernel, the spec routes it as an IDENTITY_PROPOSAL into the
REFLECTQ crucible (``services/identity_crucible.py``, dormant) rather than
writing directly. That escalation seam is where this organ ends and the next
one begins.
"""

from __future__ import annotations

from talos.domain.ports import SelfModelStore
from talos.domain.types import Episode, SelfModelEntry


class Reflector:
    def __init__(self, self_model: SelfModelStore):
        self._self_model = self_model

    def reflect(self, episode: Episode) -> None:
        if not episode.steps:
            return

        context_id = episode.context_id
        action_id = episode.steps[0].action.action_id

        entry = self._self_model.get(context_id) or SelfModelEntry(context_id=context_id)

        entry.attempts += 1
        tried = set(entry.tried_actions)
        tried.add(action_id)
        entry.tried_actions = tuple(sorted(tried))
        if episode.outcome == "win":
            entry.wins += 1
            entry.winning_action = action_id

        self._self_model.put(entry)
