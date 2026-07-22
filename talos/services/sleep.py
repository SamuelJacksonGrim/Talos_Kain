"""Sleep / wake machinery (DORMANT — spec §1/§8/§9).

The principle is blunt: if the executive supervises sleep, it isn't sleeping.
A drift-diffusion accumulator gains pressure from backlog and fatigue, loses
it on active traffic; crossing thresholds triggers light or deep sleep. Only
an alarm-vector salience spike or a circuit-breaker trip can wake early —
priced by a sleep-debt accumulator so nothing can keep the organism awake
indefinitely. Deep sleep runs on pre-authorized blind leases and never asks
the PFC. Wake ingests a pre-compiled delta manifest for zero-latency restore.

Milestone zero never sleeps — episodes are cheap and synchronous. This is the
seam for the whole autonomic cycle.
"""

from __future__ import annotations


class SleepAccumulator:
    """Drift-diffusion pressure: backlog + fatigue raise it, active traffic
    lowers it (§1)."""

    def pressure(self) -> float:
        raise NotImplementedError("dormant")


class SleepDebt:
    """Grows on wake interrupts while pressure stays high; decays only on a
    completed deep cycle. Prices wake authority (§1)."""

    def level(self) -> float:
        raise NotImplementedError("dormant")


class WakeSequence:
    """Ingest pre-compiled delta manifest, zero-copy pointer updates, PFC boot
    (§9)."""

    def wake(self):
        raise NotImplementedError("dormant")
