"""Policy: action selection.

Slice of §2/§4 (cortex → basal-ganglia action selection). The decision order
encodes the whole point of the milestone — that behavior improves because the
organism *remembers* and *grows skills*:

    1. Published skill for this context?  -> exploit it (the grown capability).
    2. Else, episodic memory of a past win here? -> exploit that action.
    3. Else -> explore (seeded, reproducible).

Because the mock world is deterministic, once a context's winning action is
known the greedy choice is optimal; exploration only happens on genuinely
unseen contexts. That makes the learning curve honest and reproducible: every
choice is a function of (seed, history), nothing hidden.
"""

from __future__ import annotations

import random

from talos.domain.ports import EpisodeStore, SkillStore
from talos.domain.types import Action, Observation


class Policy:
    def __init__(self, episodes: EpisodeStore, skills: SkillStore):
        self._episodes = episodes
        self._skills = skills

    def choose(self, observation: Observation, rng: random.Random) -> tuple[Action, str]:
        """Return the chosen action and a short provenance tag describing why
        (``skill`` / ``memory`` / ``explore``) — useful for telemetry and for
        the tests that assert learning came from the intended source."""

        # 1. Grown skill takes precedence over raw memory.
        skill = self._skills.for_context(observation.context_id)
        if skill is not None and skill.action_id in observation.available_actions:
            return Action(skill.action_id), "skill"

        # 2. Episodic memory: best win-rate action for this context.
        best = self._best_remembered_action(observation)
        if best is not None and best in observation.available_actions:
            return Action(best), "memory"

        # 3. Explore, seeded for reproducibility.
        return Action(rng.choice(observation.available_actions)), "explore"

    def _best_remembered_action(self, observation: Observation) -> int | None:
        wins: dict[int, int] = {}
        plays: dict[int, int] = {}
        for ep in self._episodes.by_context(observation.context_id):
            if not ep.steps:
                continue
            action_id = ep.steps[0].action.action_id
            plays[action_id] = plays.get(action_id, 0) + 1
            if ep.outcome == "win":
                wins[action_id] = wins.get(action_id, 0) + 1

        if not plays:
            return None

        # Prefer an action with a recorded win; break ties by win rate.
        best_action, best_rate = None, -1.0
        for action_id, n in plays.items():
            rate = wins.get(action_id, 0) / n
            if wins.get(action_id, 0) > 0 and rate > best_rate:
                best_action, best_rate = action_id, rate
        return best_action
