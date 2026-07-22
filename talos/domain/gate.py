"""The admission gate — the one door into behavior-shaping stores.

This is the code-level home of the family's governing law: *consolidation may
nominate; it may not appoint.* Skill extraction produces
``SkillCandidate``s; it never writes them. The publisher submits each
candidate to a gate, and only an ``ADMIT`` verdict — logged to the audit
ledger — results in a write.

Milestone zero ships two policies:

* ``AlwaysAdmitGate`` — the trivial pass-through, so the seam is real from
  commit one even before any real policy exists.
* ``ConfidenceGate`` — admits above a confidence threshold, otherwise
  ``DEFER``. This is the first non-trivial gate and the one the mock
  organism runs with.

When the §7 skill CI, §11 identity crucible, and §15 horizon gate arrive,
they are new ``Gate`` implementations — not a refactor of every writer.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from talos.domain.types import GateDecision, SkillCandidate


@runtime_checkable
class Gate(Protocol):
    def admit(self, candidate: SkillCandidate) -> GateDecision: ...


class AlwaysAdmitGate:
    """Pass-through. The point is not the policy — it is that writes go
    *through a gate at all*, so tightening the policy later touches one class
    instead of every call site."""

    def admit(self, candidate: SkillCandidate) -> GateDecision:  # noqa: D401
        return GateDecision.ADMIT


class ConfidenceGate:
    """Admit a candidate only once its support is strong enough."""

    def __init__(self, threshold: float = 0.75, min_support: int = 3):
        self.threshold = threshold
        self.min_support = min_support

    def admit(self, candidate: SkillCandidate) -> GateDecision:
        if len(candidate.provenance) < self.min_support:
            return GateDecision.DEFER
        if candidate.confidence >= self.threshold:
            return GateDecision.ADMIT
        return GateDecision.DEFER
