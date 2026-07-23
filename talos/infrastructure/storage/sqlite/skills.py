"""Procedural skill library.

Single writer: PUBLISH (enforced upstream by the publisher + gate, not by this
class — the store is a dumb, honest sink). Provenance is stored as a JSON
array of episode ids so "which games grew this skill?" is a query.

``for_context`` returns the highest-version live skill for a context, which is
what the policy exploits.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from talos.domain.types import Skill
from talos.infrastructure.storage.sqlite.base import connect

_SCHEMA = """
CREATE TABLE IF NOT EXISTS skills (
    skill_id   TEXT PRIMARY KEY,
    name       TEXT NOT NULL,
    context_id TEXT NOT NULL,
    action_id  INTEGER NOT NULL,
    version    INTEGER NOT NULL,
    confidence REAL NOT NULL,
    provenance TEXT NOT NULL,   -- JSON array of episode_ids
    created_at REAL NOT NULL,
    retired    INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_skills_context ON skills (context_id);
"""


class SqliteSkillStore:
    def __init__(self, path: str | Path):
        self._conn = connect(path)
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def _row_to_skill(self, r) -> Skill:
        return Skill(
            skill_id=r["skill_id"],
            name=r["name"],
            context_id=r["context_id"],
            action_id=r["action_id"],
            version=r["version"],
            confidence=r["confidence"],
            provenance=tuple(json.loads(r["provenance"])),
            created_at=r["created_at"],
        )

    def publish(self, skill: Skill) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO skills "
            "(skill_id, name, context_id, action_id, version, confidence, provenance, "
            " created_at, retired) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)",
            (
                skill.skill_id,
                skill.name,
                skill.context_id,
                skill.action_id,
                skill.version,
                skill.confidence,
                json.dumps(list(skill.provenance)),
                skill.created_at,
            ),
        )
        self._conn.commit()

    def for_context(self, context_id: str) -> Optional[Skill]:
        r = self._conn.execute(
            "SELECT * FROM skills WHERE context_id = ? AND retired = 0 "
            "ORDER BY version DESC LIMIT 1",
            (context_id,),
        ).fetchone()
        return self._row_to_skill(r) if r else None

    def all(self) -> list[Skill]:
        rows = self._conn.execute(
            "SELECT * FROM skills WHERE retired = 0 ORDER BY context_id, version"
        ).fetchall()
        return [self._row_to_skill(r) for r in rows]

    def retire(self, skill_id: str) -> None:
        self._conn.execute("UPDATE skills SET retired = 1 WHERE skill_id = ?", (skill_id,))
        self._conn.commit()

    def max_version(self, context_id: str) -> int:
        # Across all rows, retired ones included, so a replacement skill never
        # reuses a demoted skill's version/id.
        r = self._conn.execute(
            "SELECT MAX(version) AS v FROM skills WHERE context_id = ?", (context_id,)
        ).fetchone()
        return r["v"] if r and r["v"] is not None else 0
