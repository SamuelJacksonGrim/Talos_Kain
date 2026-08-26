"""Sleep / wake machinery (spec §1/§8/§9).

The principle is blunt: if the executive supervises sleep, it isn't sleeping.
A drift-diffusion accumulator gains pressure from backlog and fatigue, loses
it on active traffic; crossing thresholds triggers light or deep sleep. Only
an alarm-vector salience spike or a circuit-breaker trip can wake early —
priced by a sleep-debt accumulator so nothing can keep the organism awake
indefinitely. Deep sleep runs on pre-authorized blind leases and never asks
the PFC. Wake ingests a pre-compiled delta manifest for zero-latency restore.

Milestone zero never *sleeps* — episodes are cheap and synchronous, so the
autonomic pressure organs (``SleepAccumulator``, ``SleepDebt``) stay dormant
until gameplay makes rest cost something. But the other half of the cycle —
**wake** — is now real: it is what lets a run survive a crash, a power-off, or
a hibernate and continue rather than restart. ``WakeSequence`` is the named
seam; the reconstruction itself lives in ``services/resume.py`` so this organ
stays a thin, honest boundary rather than swallowing the whole restore.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from talos.domain.ports import (
        AuditStore,
        Environment,
        EpisodeStore,
        RunStateStore,
    )
    from talos.services.resume import ResumeManifest
    from talos.services.reward_engine import RewardEngine
    from talos.services.skill_extraction import SkillPublisher


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
    """Ingest the pre-compiled delta manifest and restore the organism to the
    point of interruption (§9).

    Wake verifies the audit ledger (the trust root — a run must not resume onto
    a tampered history), rebuilds the volatile modulation state from the durable
    log, fast-forwards the environment, and hands back a ``ResumeManifest``
    saying where the loop turns next. It is deliberately a delegating boundary:
    the mechanism is in ``services/resume.py``, and the same call serves a first
    start (no cursor → resume_from 0) and a restart alike.
    """

    def wake(
        self,
        *,
        run_store: "RunStateStore",
        run_id: str,
        run_seed: int,
        env: "Environment",
        episodes: "EpisodeStore",
        audit: "AuditStore",
        reward: "RewardEngine",
        publisher: "SkillPublisher",
        target_episodes: int,
    ) -> "ResumeManifest":
        from talos.services import resume

        return resume.wake(
            run_store=run_store,
            run_id=run_id,
            run_seed=run_seed,
            env=env,
            episodes=episodes,
            audit=audit,
            reward=reward,
            publisher=publisher,
            target_episodes=target_episodes,
        )
