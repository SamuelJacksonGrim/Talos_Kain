"""The admission gate is the one door; the publisher is the one writer."""

from __future__ import annotations

from talos.domain.gate import AlwaysAdmitGate, ConfidenceGate
from talos.domain.types import GateDecision, SkillCandidate
from talos.infrastructure.storage.sqlite.audit import SqliteAuditStore
from talos.infrastructure.storage.sqlite.skills import SqliteSkillStore
from talos.services.skill_extraction import SkillPublisher


def _candidate(confidence, support):
    return SkillCandidate(
        context_id="ctx-0",
        action_id=2,
        confidence=confidence,
        provenance=tuple(f"ep{i}" for i in range(support)),
    )


def test_always_admit():
    assert AlwaysAdmitGate().admit(_candidate(0.0, 0)) is GateDecision.ADMIT


def test_confidence_gate_defers_low_support():
    gate = ConfidenceGate(threshold=0.75, min_support=3)
    assert gate.admit(_candidate(0.9, 1)) is GateDecision.DEFER


def test_confidence_gate_defers_low_confidence():
    gate = ConfidenceGate(threshold=0.75, min_support=3)
    assert gate.admit(_candidate(0.5, 5)) is GateDecision.DEFER


def test_confidence_gate_admits_strong_candidate():
    gate = ConfidenceGate(threshold=0.75, min_support=3)
    assert gate.admit(_candidate(0.9, 5)) is GateDecision.ADMIT


def test_deferred_candidate_is_not_written_but_is_audited(tmp_path):
    skills = SqliteSkillStore(tmp_path / "skills.db")
    audit = SqliteAuditStore(tmp_path / "audit.db")
    publisher = SkillPublisher(skills, ConfidenceGate(), audit)

    decision = publisher.submit(_candidate(0.5, 5))  # below threshold -> DEFER

    assert decision is GateDecision.DEFER
    assert skills.all() == []                 # nothing written
    assert len(audit.history()) == 1          # but the decision is on the ledger
    assert audit.history()[0].payload["decision"] == "DEFER"


def test_admitted_candidate_is_written_with_provenance(tmp_path):
    skills = SqliteSkillStore(tmp_path / "skills.db")
    audit = SqliteAuditStore(tmp_path / "audit.db")
    publisher = SkillPublisher(skills, ConfidenceGate(), audit)

    decision = publisher.submit(_candidate(0.9, 5))

    assert decision is GateDecision.ADMIT
    published = skills.all()
    assert len(published) == 1
    assert published[0].provenance == tuple(f"ep{i}" for i in range(5))
    assert audit.verify() is True
