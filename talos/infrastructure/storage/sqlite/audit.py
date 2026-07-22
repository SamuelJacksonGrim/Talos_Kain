"""Hash-chained audit ledger — the trust root.

Each row carries the digest of the previous row, so the ledger is a chain:

    digest[n] = sha256( digest[n-1] || canonical(payload[n]) )

``verify()`` walks the chain and recomputes every digest. If any row's
payload was altered, or a row was inserted/removed/reordered, the recomputed
chain diverges and verification fails. This is what makes "immutable" more
than a comment: the ledger cannot be edited in place without detection.

Milestone zero uses SHA-256 over a canonical (sorted-key, compact) JSON
encoding of the payload plus a monotonically increasing sequence number. The
genesis link's ``prev_digest`` is 64 zeros.
"""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

from talos.domain.types import AuditRecord
from talos.infrastructure.storage.sqlite.base import connect

GENESIS = "0" * 64

_SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_log (
    seq         INTEGER PRIMARY KEY,
    kind        TEXT    NOT NULL,
    payload     TEXT    NOT NULL,   -- canonical JSON
    prev_digest TEXT    NOT NULL,
    digest      TEXT    NOT NULL,
    ts          REAL    NOT NULL
);
"""


def _canonical(seq: int, kind: str, payload: dict) -> str:
    return json.dumps(
        {"seq": seq, "kind": kind, "payload": payload},
        sort_keys=True,
        separators=(",", ":"),
    )


def _digest(prev_digest: str, canonical: str) -> str:
    h = hashlib.sha256()
    h.update(prev_digest.encode("utf-8"))
    h.update(canonical.encode("utf-8"))
    return h.hexdigest()


class SqliteAuditStore:
    def __init__(self, path: str | Path):
        self._conn = connect(path)
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def _last_digest(self) -> tuple[int, str]:
        row = self._conn.execute(
            "SELECT seq, digest FROM audit_log ORDER BY seq DESC LIMIT 1"
        ).fetchone()
        if row is None:
            return 0, GENESIS
        return row["seq"], row["digest"]

    def record(self, kind: str, payload: dict) -> AuditRecord:
        last_seq, prev_digest = self._last_digest()
        seq = last_seq + 1
        canonical = _canonical(seq, kind, payload)
        digest = _digest(prev_digest, canonical)
        ts = time.time()
        self._conn.execute(
            "INSERT INTO audit_log (seq, kind, payload, prev_digest, digest, ts) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (seq, kind, canonical, prev_digest, digest, ts),
        )
        self._conn.commit()
        return AuditRecord(seq, kind, payload, prev_digest, digest, ts)

    def history(self) -> list[AuditRecord]:
        rows = self._conn.execute(
            "SELECT seq, kind, payload, prev_digest, digest, ts FROM audit_log ORDER BY seq"
        ).fetchall()
        out: list[AuditRecord] = []
        for r in rows:
            payload = json.loads(r["payload"])["payload"]
            out.append(
                AuditRecord(r["seq"], r["kind"], payload, r["prev_digest"], r["digest"], r["ts"])
            )
        return out

    def verify(self) -> bool:
        """Recompute the whole chain. Any tamper — edited payload, altered
        digest, inserted/removed/reordered row — breaks it."""
        rows = self._conn.execute(
            "SELECT seq, kind, payload, prev_digest, digest FROM audit_log ORDER BY seq"
        ).fetchall()
        prev = GENESIS
        expected_seq = 1
        for r in rows:
            if r["seq"] != expected_seq:
                return False
            if r["prev_digest"] != prev:
                return False
            # r["payload"] is already canonical JSON; recompute over it.
            recomputed = _digest(prev, r["payload"])
            if recomputed != r["digest"]:
                return False
            prev = r["digest"]
            expected_seq += 1
        return True
