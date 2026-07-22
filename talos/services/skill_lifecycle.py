"""Skill lifecycle beyond publication (DORMANT — spec §7).

The full skill CI/CD gauntlet: generated tests (unit, property, regression,
adversarial), a sandbox CI gate, version + sign + provenance stamp, a shadow
(recommend-only) mode, a canary, and post-publish monitoring for drift,
latency, and deprecation.

Milestone zero implements only the nominate → gate → publish core in
``skill_extraction.py``. This module is the seam for the test/sandbox/shadow/
canary/monitor stages.
"""

from __future__ import annotations


class SkillSandboxCI:
    def run(self, draft_skill) -> bool:  # pass/fail gate
        raise NotImplementedError("dormant")


class SkillCanary:
    def evaluate(self, shadow_skill) -> str:  # "publish" | "rollback"
        raise NotImplementedError("dormant")


class SkillMonitor:
    """Drift, latency, failure modes, deprecation; can demote trust or
    re-queue for refinement (§7)."""

    def observe(self, skill):
        raise NotImplementedError("dormant")
