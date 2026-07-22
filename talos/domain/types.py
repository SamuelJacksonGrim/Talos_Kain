"""Core domain types.

Plain, immutable-ish dataclasses that carry organism state across the loop.
These are deliberately storage-agnostic: an ``Episode`` knows its seed and
provenance because the *thesis of the milestone* — "this skill emerged from
these games" — is unfalsifiable otherwise, not because SQLite has a column
for it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


# --------------------------------------------------------------------------
# Perception / action
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Observation:
    """What the sensorium hands the policy for a single decision.

    ``context_id`` is the organism-visible situation label (in SC2 terms: the
    matchup / map state bucket). ``available_actions`` is the discrete action
    set the policy may choose from.
    """

    context_id: str
    available_actions: tuple[int, ...]
    features: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Action:
    action_id: int


@dataclass(frozen=True)
class StepResult:
    """The environment's reply to an action."""

    reward: float
    done: bool
    outcome: Optional[str] = None  # "win" | "loss" | None (mid-episode)
    info: dict[str, Any] = field(default_factory=dict)


# --------------------------------------------------------------------------
# Experience
# --------------------------------------------------------------------------

@dataclass
class Step:
    observation: Observation
    action: Action
    reward: float
    salience: float


@dataclass
class Episode:
    """A single trajectory. Provenance fields are first-class, not optional
    bookkeeping: without ``run_id`` + ``seed`` you cannot tell a grown skill
    from a lucky map."""

    episode_id: str
    run_id: str
    seed: int
    env_name: str
    env_version: str
    context_id: str
    steps: list[Step] = field(default_factory=list)
    outcome: Optional[str] = None  # "win" | "loss"
    started_at: float = 0.0
    finished_at: float = 0.0


# --------------------------------------------------------------------------
# Skills (the thing the organism grows)
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class SkillCandidate:
    """A nomination produced by skill extraction. It is *not* a skill until it
    passes the admission gate. Carries the episode lineage that produced it so
    provenance survives into the published skill."""

    context_id: str
    action_id: int
    confidence: float
    provenance: tuple[str, ...]  # episode_ids that support this candidate


@dataclass(frozen=True)
class Skill:
    """A published, behavior-shaping capability. Only the publisher writes
    these, and only on an ADMIT decision from the gate."""

    skill_id: str
    name: str
    context_id: str
    action_id: int
    version: int
    confidence: float
    provenance: tuple[str, ...]
    created_at: float


# --------------------------------------------------------------------------
# Governance
# --------------------------------------------------------------------------

class GateDecision(str, Enum):
    """The universal admission verdict. Every write to a behavior-shaping
    store passes through a gate that returns one of these — and the decision
    is logged to the audit ledger. Milestone zero exercises ADMIT / DEFER;
    REJECT and ESCALATE exist so the §7 skill CI, §11 identity crucible, and
    §15 horizon gate plug into an existing seam rather than forcing a
    repository-wide refactor."""

    ADMIT = "ADMIT"
    REJECT = "REJECT"
    DEFER = "DEFER"
    ESCALATE = "ESCALATE"


@dataclass(frozen=True)
class AuditRecord:
    """One link in the hash-chained audit ledger."""

    seq: int
    kind: str
    payload: dict[str, Any]
    prev_digest: str
    digest: str
    ts: float
