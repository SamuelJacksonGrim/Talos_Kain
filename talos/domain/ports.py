"""Ports: the interfaces the infrastructure layer must implement.

These are the seams that keep the domain pure. The learning loop depends on
``Environment`` and the store protocols — never on ``sqlite3`` or ``pysc2``.
Swapping SQLite for Postgres, or the mock world for StarCraft II, is an
infrastructure change behind one of these Protocols, not a domain rewrite.

Runtime-checkable ``Protocol`` is used deliberately: infrastructure classes
satisfy these by shape, with no import dependency pointing inward.
"""

from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable

from talos.domain.types import (
    Action,
    AuditRecord,
    Episode,
    Observation,
    Skill,
    StepResult,
)


@runtime_checkable
class Environment(Protocol):
    """A world the organism can act in. MockEnv is the primary implementation
    for milestone zero; SC2Env is an adapter that arrives once the learning
    loop is proven in the toy world."""

    name: str
    version: str

    def reset(self, seed: int) -> Observation: ...

    def step(self, action: Action) -> StepResult: ...

    def close(self) -> None: ...


@runtime_checkable
class WALStore(Protocol):
    """Append-only write-ahead experience log. Nothing is lost even under
    crash; everything experienced lands here first (§3)."""

    def append(self, kind: str, payload: dict) -> int: ...

    def count(self) -> int: ...


@runtime_checkable
class EpisodeStore(Protocol):
    """Episodic / glacier archive: trajectories, conversations, outcomes."""

    def save(self, episode: Episode) -> None: ...

    def get(self, episode_id: str) -> Optional[Episode]: ...

    def by_context(self, context_id: str) -> list[Episode]: ...

    def recent(self, n: int) -> list[Episode]: ...


@runtime_checkable
class SkillStore(Protocol):
    """Procedural skill library. Single writer: PUBLISH. The domain never
    calls ``publish`` directly — it goes through the admission gate + the
    publisher service (§7)."""

    def publish(self, skill: Skill) -> None: ...

    def for_context(self, context_id: str) -> Optional[Skill]: ...

    def all(self) -> list[Skill]: ...

    def retire(self, skill_id: str) -> None: ...


@runtime_checkable
class AuditStore(Protocol):
    """Immutable, hash-chained audit ledger — the trust root. ``verify``
    proves the chain has not been tampered with; without chained digests
    "immutable" is just a comment (§14)."""

    def record(self, kind: str, payload: dict) -> AuditRecord: ...

    def history(self) -> list[AuditRecord]: ...

    def verify(self) -> bool: ...
