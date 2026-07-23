"""Limbic-reward axis (§5) — woken.

The reward engine turns outcomes into a *prediction-error* signal: the gap
between what the organism expected and what actually happened. It keeps a
recency-weighted value estimate V(context, action), updated each outcome by a
learning rate, so a confidently-good action that starts losing is visible as a
large negative surprise.

Everything here is async modulation, exactly as the spec insists — the reward
engine never sits in the action-selection path. It runs *after* the motor
loop, and its output modulates the rest of the system:

* **Surprise drives recovery.** When a believed-good action fails (prediction
  error well below zero), the organism demotes the stale skill and resets its
  self-model belief so it re-explores. This is the whole reason §5 exists:
  value is what lets a confident agent notice it is wrong.
* **Value gates consolidation.** Because V is recency-weighted, it tracks the
  *current* best action after drift, not the lifetime champion. Skill
  nomination reads it so a stale winner is never re-published.

Milestone note: the value table is in-memory modulation state, rebuildable
from the experience log. It is not a store of record — the WAL and episodic
archive are.
"""

from __future__ import annotations


class RewardEngine:
    def __init__(
        self,
        learning_rate: float = 0.5,
        surprise_threshold: float = 0.5,
        exploit_value: float = 0.5,
    ):
        self._alpha = learning_rate
        self._surprise_threshold = surprise_threshold
        self._exploit_value = exploit_value
        self._value: dict[tuple[str, int], float] = {}

    def observe(self, context_id: str, action_id: int, reward: float) -> float:
        """Fold one outcome into the value estimate and return the prediction
        error (observed - expected). Positive is a happy surprise, negative is
        a disappointment; a large negative means a trusted action just failed.
        """
        key = (context_id, action_id)
        expected = self._value.get(key, 0.0)
        prediction_error = reward - expected
        self._value[key] = expected + self._alpha * prediction_error
        return prediction_error

    def value(self, context_id: str, action_id: int) -> float:
        return self._value.get((context_id, action_id), 0.0)

    def is_surprise(self, prediction_error: float) -> bool:
        """True when a confidently-good action failed. Only actions whose value
        had climbed above the threshold can produce a drop this steep, so blind
        exploratory losses never trip it — only a broken belief does."""
        return prediction_error <= -self._surprise_threshold

    def is_trusted(self, context_id: str, action_id: int) -> bool:
        """Whether an action's current (recency-weighted) value is high enough
        to be worth consolidating into a skill. After drift, a stale winner's
        value decays below this fast, so it stops qualifying."""
        return self.value(context_id, action_id) >= self._exploit_value
