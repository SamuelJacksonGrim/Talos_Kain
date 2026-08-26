"""Run-state store (implements RunStateStore, §1/§9).

The durable continuity cursor. One row per run: how far it has committed, the
deterministic stream it indexes (run_seed + env_name), and whether it finished.

This is deliberately tiny. The WAL and episodic archive are the log of record;
this store is just the *pointer into them* that a wake reads to know where to
pick up. Keeping it a single upserted row means a resume reads exactly one row
instead of replaying an experience log — the "pre-compiled delta manifest" the
sleep/wake organ was specced around.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from talos.domain.types import RunState
from talos.infrastructure.storage.sqlite.base import connect

_SCHEMA = """
CREATE TABLE IF NOT EXISTS run_state (
    run_id          TEXT PRIMARY KEY,
    run_seed        INTEGER NOT NULL,
    env_name        TEXT    NOT NULL,
    last_index      INTEGER NOT NULL,
    target_episodes INTEGER NOT NULL,
    status          TEXT    NOT NULL,
    updated_at      REAL    NOT NULL
);
"""


class SqliteRunStore:
    def __init__(self, path: str | Path):
        self._conn = connect(path)
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def save(self, state: RunState) -> None:
        # Upsert: a run keeps one cursor row that advances in place. The commit
        # here is what makes episode ``last_index`` durable — it is called only
        # after every other store for that episode has already committed.
        self._conn.execute(
            "INSERT OR REPLACE INTO run_state "
            "(run_id, run_seed, env_name, last_index, target_episodes, status, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                state.run_id,
                state.run_seed,
                state.env_name,
                state.last_index,
                state.target_episodes,
                state.status,
                state.updated_at,
            ),
        )
        self._conn.commit()

    def load(self, run_id: str) -> Optional[RunState]:
        r = self._conn.execute(
            "SELECT * FROM run_state WHERE run_id = ?", (run_id,)
        ).fetchone()
        if r is None:
            return None
        return RunState(
            run_id=r["run_id"],
            run_seed=r["run_seed"],
            env_name=r["env_name"],
            last_index=r["last_index"],
            target_episodes=r["target_episodes"],
            status=r["status"],
            updated_at=r["updated_at"],
        )
