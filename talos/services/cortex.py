"""Federated cortex (DORMANT — spec §2).

The PFC writes constitution — goals, priorities, stop conditions — and
pre-authorizes budgets; it does not carry traffic. Local router pods carry
execution, tiered by risk, with high/irreversible objectives escalating to a
human/sentinel lane. The context broker compresses relevance into a bounded
context packet so no component ever drinks the firehose.

Milestone zero has no multi-agent mesh; the policy chooses directly. This is
the seam for the executive and the router pods.
"""

from __future__ import annotations


class PrefrontalCortex:
    """Goal constitution, priorities, stop conditions (§2)."""

    def constitute(self, mission):
        raise NotImplementedError("dormant")


class ContextBroker:
    """Summary, filtering, token packing into a bounded context packet (§2)."""

    def pack(self, goal_slice, constraints, pointers, exemplars):
        raise NotImplementedError("dormant")
