"""Planner agent (DORMANT — spec §2).

Decomposes a mission envelope into subgoals and a plan the executor can carry.
Milestone zero is single-step and needs no planning; this is the seam for the
planning/retrieval pod.
"""

from __future__ import annotations


class Planner:
    def plan(self, mission):
        raise NotImplementedError("dormant: milestone zero is single-step")
