"""Reward calculus — pure functions, no state.

Milestone zero keeps this deliberately thin: a binary win/loss maps to
valence. The §5 limbic-reward axis (streaming TD error, uncertainty, the
ethics-sentinel channel) is a dormant organ — it plugs in here when gameplay
justifies it.
"""

from __future__ import annotations

from talos.domain.types import StepResult


def valence(step: StepResult) -> float:
    """Scalar goodness of an outcome in [-1, 1]."""
    if step.outcome == "win":
        return 1.0
    if step.outcome == "loss":
        return -1.0
    return step.reward


def is_win(step: StepResult) -> bool:
    return step.outcome == "win"
