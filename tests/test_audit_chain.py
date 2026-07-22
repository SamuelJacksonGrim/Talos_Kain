"""The audit ledger is the trust root: tampering must be detectable."""

from __future__ import annotations

import sqlite3

from talos.infrastructure.storage.sqlite.audit import SqliteAuditStore


def test_clean_chain_verifies(tmp_path):
    audit = SqliteAuditStore(tmp_path / "audit.db")
    for i in range(5):
        audit.record("event", {"i": i})
    assert audit.verify() is True
    assert len(audit.history()) == 5


def test_chaining_links_each_row(tmp_path):
    audit = SqliteAuditStore(tmp_path / "audit.db")
    r1 = audit.record("a", {"x": 1})
    r2 = audit.record("b", {"x": 2})
    # Second row's prev_digest is the first row's digest.
    assert r2.prev_digest == r1.digest


def test_edited_payload_breaks_verification(tmp_path):
    path = tmp_path / "audit.db"
    audit = SqliteAuditStore(path)
    for i in range(5):
        audit.record("event", {"i": i})
    assert audit.verify() is True

    # Tamper: edit a payload in place, leaving digests untouched.
    raw = sqlite3.connect(path)
    raw.execute("UPDATE audit_log SET payload = ? WHERE seq = 3", ('{"seq":3,"kind":"event","payload":{"i":999}}',))
    raw.commit()
    raw.close()

    assert audit.verify() is False


def test_deleted_row_breaks_verification(tmp_path):
    path = tmp_path / "audit.db"
    audit = SqliteAuditStore(path)
    for i in range(5):
        audit.record("event", {"i": i})

    raw = sqlite3.connect(path)
    raw.execute("DELETE FROM audit_log WHERE seq = 3")
    raw.commit()
    raw.close()

    # Sequence gap + broken chain both trip verification.
    assert audit.verify() is False
