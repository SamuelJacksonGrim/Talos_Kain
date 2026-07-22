"""Storage adapters.

Milestone zero splits state across separate SQLite files — wal.db,
episodic.db, skills.db, audit.db — rather than one database. The split is not
premature optimization: it is bulkhead containment (§2/§14). Corruption or a
bad migration in one store cannot take the others down with it, and the
append-only / immutable stores can be backed up and verified independently of
the mutable ones.
"""
