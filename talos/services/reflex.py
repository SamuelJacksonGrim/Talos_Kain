"""Cerebellar reflex + ghost-pointer unthaw (DORMANT — spec §4).

Two mechanisms that keep the motor loop from freezing: bounded micro-retries
for known-correctable errors at cerebellar latency (no judge overhead), and
the ghost-pointer protocol that lets the executor act on a tombstoned memory's
semantic centroid while the real payload unthaws asynchronously — yielding to
a parallel sub-goal only when exact fidelity is required.

Milestone zero has no cold memory and no correctable-error class; the motor
loop just executes. This is the seam.
"""

from __future__ import annotations


class CerebellarReflex:
    def correct(self, error):  # -> micro-fix or escalate
        raise NotImplementedError("dormant")


class GhostPointerProtocol:
    """Fire async fetch, ship the packet anyway with a semantic ghost;
    verify the unthawed payload against the tombstone digest before splice
    (§4)."""

    def resolve(self, tombstone):
        raise NotImplementedError("dormant")
