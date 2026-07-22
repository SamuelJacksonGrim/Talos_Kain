"""SQLite implementations of the domain store ports.

These are adapters, nothing more. When Postgres / pgvector / Redis arrive they
are new classes satisfying the same ``talos.domain.ports`` Protocols; no
service or domain code changes.
"""
