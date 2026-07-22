"""Immune system + adaptive intake (DORMANT — spec §0).

The sensorium's hard problem: tighten the gate and novelty starves; loosen it
and injection walks in. The design splits it — a fast hygiene gate for
known-bad patterns, a low-privilege novelty lane for the ambiguous, deep
immune review that can take its time, a bounded deferral queue so review can't
be flooded, and an adaptive tuner closing the loop on false positives and
novelty starvation.

Milestone zero ships only the trivial salience scorer in ``sensorium.py``.
This module is the seam for the real thing.
"""

from __future__ import annotations


class FastHygieneGate:
    """Wire-speed block of known-bad patterns only (§0)."""

    def screen(self, signal) -> str:  # -> "clear" | "ambiguous" | "known_bad"
        raise NotImplementedError("dormant: milestone zero has no hostile intake")


class NoveltyLane:
    """Sandboxed probe for ambiguous input — no secrets, no actuation (§0)."""

    def probe(self, signal):
        raise NotImplementedError("dormant")


class AdaptiveImmuneTuner:
    """Retunes both gates from quarantine false-positive feedback and the
    novelty-starvation metric (§0)."""

    def retune(self) -> None:
        raise NotImplementedError("dormant")
