"""Shared SQLite plumbing.

One tiny helper so every store opens its connection the same way. Each store
owns its *own* database file (bulkhead containment), so there is no shared
connection here by design — just consistent pragmas and a schema-init helper.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path


def connect(path: str | Path) -> sqlite3.Connection:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    # WAL journaling + foreign keys: sensible defaults for every store.
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
