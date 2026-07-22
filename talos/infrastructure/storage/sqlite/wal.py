"""Write-ahead experience log: append-only.

Everything the organism experiences lands here first (§3). Milestone zero
stores each event as (kind, canonical-JSON payload, timestamp). There is no
update or delete path by design — the only operations are append and read.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from talos.infrastructure.storage.sqlite.base import connect

_SCHEMA = """
CREATE TABLE IF NOT EXISTS wal (
    seq     INTEGER PRIMARY KEY AUTOINCREMENT,
    kind    TEXT NOT NULL,
    payload TEXT NOT NULL,
    ts      REAL NOT NULL
);
"""


class SqliteWAL:
    def __init__(self, path: str | Path):
        self._conn = connect(path)
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def append(self, kind: str, payload: dict) -> int:
        cur = self._conn.execute(
            "INSERT INTO wal (kind, payload, ts) VALUES (?, ?, ?)",
            (kind, json.dumps(payload, sort_keys=True), time.time()),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def count(self) -> int:
        return int(self._conn.execute("SELECT COUNT(*) AS n FROM wal").fetchone()["n"])
