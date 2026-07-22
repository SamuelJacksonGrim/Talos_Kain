"""Episodic archive.

Stores full trajectories with their provenance (run_id, seed, env version).
The single step of a milestone-zero episode is serialized as JSON; the schema
is intentionally ready for multi-step trajectories without a migration
(``steps`` is a JSON array).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from talos.domain.types import Action, Episode, Observation, Step
from talos.infrastructure.storage.sqlite.base import connect

_SCHEMA = """
CREATE TABLE IF NOT EXISTS episodes (
    episode_id  TEXT PRIMARY KEY,
    run_id      TEXT NOT NULL,
    seed        INTEGER NOT NULL,
    env_name    TEXT NOT NULL,
    env_version TEXT NOT NULL,
    context_id  TEXT NOT NULL,
    outcome     TEXT,
    steps       TEXT NOT NULL,   -- JSON array
    started_at  REAL NOT NULL,
    finished_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_episodes_context ON episodes (context_id);
CREATE INDEX IF NOT EXISTS idx_episodes_run ON episodes (run_id);
"""


def _steps_to_json(steps: list[Step]) -> str:
    return json.dumps(
        [
            {
                "context_id": s.observation.context_id,
                "available_actions": list(s.observation.available_actions),
                "features": s.observation.features,
                "action_id": s.action.action_id,
                "reward": s.reward,
                "salience": s.salience,
            }
            for s in steps
        ]
    )


def _steps_from_json(blob: str) -> list[Step]:
    out: list[Step] = []
    for d in json.loads(blob):
        obs = Observation(
            context_id=d["context_id"],
            available_actions=tuple(d["available_actions"]),
            features=d.get("features", {}),
        )
        out.append(Step(obs, Action(d["action_id"]), d["reward"], d["salience"]))
    return out


class SqliteEpisodeStore:
    def __init__(self, path: str | Path):
        self._conn = connect(path)
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def save(self, episode: Episode) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO episodes "
            "(episode_id, run_id, seed, env_name, env_version, context_id, outcome, "
            " steps, started_at, finished_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                episode.episode_id,
                episode.run_id,
                episode.seed,
                episode.env_name,
                episode.env_version,
                episode.context_id,
                episode.outcome,
                _steps_to_json(episode.steps),
                episode.started_at,
                episode.finished_at,
            ),
        )
        self._conn.commit()

    def _row_to_episode(self, r) -> Episode:
        return Episode(
            episode_id=r["episode_id"],
            run_id=r["run_id"],
            seed=r["seed"],
            env_name=r["env_name"],
            env_version=r["env_version"],
            context_id=r["context_id"],
            steps=_steps_from_json(r["steps"]),
            outcome=r["outcome"],
            started_at=r["started_at"],
            finished_at=r["finished_at"],
        )

    def get(self, episode_id: str) -> Optional[Episode]:
        r = self._conn.execute(
            "SELECT * FROM episodes WHERE episode_id = ?", (episode_id,)
        ).fetchone()
        return self._row_to_episode(r) if r else None

    def by_context(self, context_id: str) -> list[Episode]:
        rows = self._conn.execute(
            "SELECT * FROM episodes WHERE context_id = ? ORDER BY started_at", (context_id,)
        ).fetchall()
        return [self._row_to_episode(r) for r in rows]

    def recent(self, n: int) -> list[Episode]:
        rows = self._conn.execute(
            "SELECT * FROM episodes ORDER BY started_at DESC LIMIT ?", (n,)
        ).fetchall()
        return [self._row_to_episode(r) for r in rows]
