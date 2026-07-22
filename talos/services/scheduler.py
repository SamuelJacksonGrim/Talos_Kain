"""Brainstem scheduler + lease allocation (DORMANT — spec §1/§2).

Homeostatic admission (can we afford this: load, cost, latency, queue depth,
fatigue) and rights (should we do this at all: refusal, continuity, temporal
integrity) before the executive spends a cycle. Work that passes is wrapped in
a mission envelope. Deep-sleep work runs on pre-authorized blind leases with a
fixed offline compute/token budget.

Milestone zero runs a fixed episode count with no admission control or leases.
This is the seam for homeostasis and the mission envelope.
"""

from __future__ import annotations


class HomeostaticMonitor:
    def can_afford(self, task) -> bool:
        raise NotImplementedError("dormant")


class LeaseAllocator:
    """Pre-authorized blind leases: fixed offline budget the batch controller
    consumes without asking the PFC (§1)."""

    def issue(self, budget):
        raise NotImplementedError("dormant")
