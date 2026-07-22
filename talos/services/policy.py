"""Policy: action selection.

Slice of §2/§4 (cortex -> basal-ganglia action selection). The decision order
encodes the whole point of the milestone — that behavior improves because the
organism *remembers*, *grows skills*, and now *models itself*:

    1. Published skill for this context?  -> exploit it (the grown capability).
    2. Else, self-model knows the winning action here? -> exploit it.
    3. Else, explore an action the self-model has NOT already tried and lost
       (systematic elimination) -> only fall back to a blind guess if every
       action has been tried.

Step 3 is what the self-model organ bought. Before it, exploration was a blind
guess that could re-pick an action already known to lose, wasting episodes.
Now the organism reads its own track record and never repeats a known loser,
so it masters each context in at most (number of actions) tries instead of an
unbounded random walk. Every choice remains a function of (seed, history),
nothing hidden, so the curve stays reproducible.
"""

from __future__ import annotations

import random

from talos.domain.ports import SelfModelStore, SkillStore
from talos.domain.types import Action, Observation


class Policy:
    def __init__(self, skills: SkillStore, self_model: SelfModelStore):
        self._skills = skills
        self._self_model = self_model

    def choose(self, observation: Observation, rng: random.Random) -> tuple[Action, str]:
        """Return the chosen action and a short provenance tag describing why
        (``skill`` / ``self_model`` / ``explore``) — useful for telemetry and
        for the tests that assert learning came from the intended source."""

        # 1. Grown skill takes precedence.
        skill = self._skills.for_context(observation.context_id)
        if skill is not None and skill.action_id in observation.available_actions:
            return Action(skill.action_id), "skill"

        entry = self._self_model.get(observation.context_id)
        if entry is not None:
            # 2. Self-model already found the winner here.
            if entry.winning_action is not None and entry.winning_action in observation.available_actions:
                return Action(entry.winning_action), "self_model"

            # 3. Systematic elimination: try something not yet tried.
            untried = [a for a in observation.available_actions if a not in entry.tried_actions]
            if untried:
                return Action(rng.choice(untried)), "explore"

        # First visit to this context, or everything tried: blind guess.
        return Action(rng.choice(observation.available_actions)), "explore"
