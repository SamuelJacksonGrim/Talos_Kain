"""Limbic-reward axis (DORMANT — spec §5).

The judge's verdict fans into valence and uncertainty estimates, streams into
a reward queue alongside the ethics-sentinel channel, and produces a
prediction-error signal. Everything dopamine does is asynchronous — trust
updates, learning-rate modulation, action-prior biasing — never blocking the
executor.

Milestone zero uses only the pure ``domain/reward.py`` valence. This is the
seam for streaming TD error and the async modulation fan-out.
"""

from __future__ import annotations


class RewardEngine:
    def prediction_error(self, expected: float, observed: float) -> float:
        raise NotImplementedError("dormant: milestone zero has no value model")
