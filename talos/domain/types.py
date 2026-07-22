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
# Self-model (the organism modeling itself)
# --------------------------------------------------------------------------

@dataclass
class SelfModelEntry:
    """The organism's model of *itself* for one context: what it has tried,
    what works, and how sure it is — strengths, blind spots, calibration (§11).

    Distinct from a Skill. A Skill is a published, gated capability. A
    SelfModelEntry is metacognition: a consolidated read of the organism's own
    track record that shapes where it still needs to explore. It is derived
    from logged experience, so it is a summary of fact, not an autonomous
    behavior injection — which is why it does not pass through the gate.
    """

    context_id: str
    attempts: int = 0
    wins: int = 0
    tried_actions: tuple[int, ...] = ()
    winning_action: Optional[int] = None

    @property
    def confidence(self) -> float:
        return self.wins / self.attempts if self.attempts else 0.0

    @property
    def mastered(self) -> bool:
        return self.winning_action is not None


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
