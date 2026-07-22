"""Self-model store (implements SelfModelStore, §3 SELFSTORE).

Woken for the self-model organ. Holds one row per context: how many times the
organism has acted there, how often it won, which actions it has already
tried, and which one wins. A consolidated, fast-read summary of the organism's
own track record.

``tried_actions`` is stored as a JSON array. The store is a dumb sink; the
reflection pass (``services/reflection.py``) is the only writer, and it writes
facts derived from the episodic log.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from talos.domain.types import SelfModelEntry
from talos.infrastructure.storage.sqlite.base import connect

_SCHEMA = """
CREATE TABLE IF NOT EXISTS self_model (
    context_id     TEXT PRIMARY KEY,
    attempts       INTEGER NOT NULL,
    wins           INTEGER NOT NULL,
    tried_actions  TEXT NOT NULL,   -- JSON array
    winning_action INTEGER          -- NULL until found
);
"""


class SqliteSelfModelStore:
    def __init__(self, path: str | Path):
        self._conn = connect(path)
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def _row_to_entry(self, r) -> SelfModelEntry:
        return SelfModelEntry(
            context_id=r["context_id"],
            attempts=r["attempts"],
            wins=r["wins"],
            tried_actions=tuple(json.loads(r["tried_actions"])),
            winning_action=r["winning_action"],
        )

    def get(self, context_id: str) -> Optional[SelfModelEntry]:
        r = self._conn.execute(
            "SELECT * FROM self_model WHERE context_id = ?", (context_id,)
        ).fetchone()
        return self._row_to_entry(r) if r else None

    def put(self, entry: SelfModelEntry) -> None:
        self._conn.execute(
            "INSERT OR REPLACE INTO self_model "
            "(context_id, attempts, wins, tried_actions, winning_action) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                entry.context_id,
                entry.attempts,
                entry.wins,
                json.dumps(list(entry.tried_actions)),
                entry.winning_action,
            ),
        )
        self._conn.commit()

    def all(self) -> list[SelfModelEntry]:
        rows = self._conn.execute(
            "SELECT * FROM self_model ORDER BY context_id"
        ).fetchall()
        return [self._row_to_entry(r) for r in rows]
