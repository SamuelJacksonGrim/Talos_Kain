"""Sensorium: intake + salience scoring.

Milestone-zero slice of §0. The full sensorium (fast hygiene gate, novelty
lane, deep immune review, adaptive tuner) is a dormant organ. What survives
into the slice is the shape that matters for learning: normalize what the
environment reports into a domain ``Observation`` and attach a salience
score, so downstream code already speaks in salience even though the scorer
is trivial today.
"""

from __future__ import annotations

from talos.domain.types import Observation


class Sensorium:
    def __init__(self) -> None:
        self._seen_contexts: set[str] = set()

    def perceive(self, observation: Observation) -> tuple[Observation, float]:
        """Return the observation and a salience score in [0, 1].

        Novelty-only heuristic for now: a context never seen before is
        maximally salient; a familiar one is baseline. Urgency, affect,
        stakes, and reversibility (the other §0 dimensions) arrive with the
        organs that need them.
        """
        novelty = 0.0 if observation.context_id in self._seen_contexts else 1.0
        self._seen_contexts.add(observation.context_id)
        salience = max(novelty, 0.1)
        return observation, salience
