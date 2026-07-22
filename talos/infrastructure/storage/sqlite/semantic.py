"""Semantic vector store adapter (DORMANT — implements SemanticStore, §3).

Warm retrieval index. Milestone zero has no embeddings and no vector search.
When it wakes, the natural path is SQLite + a vector extension, upgradeable to
Postgres + pgvector behind the same ``talos.domain.ports.SemanticStore`` port
with no change above the infrastructure layer.
"""

from __future__ import annotations


class SqliteSemanticStore:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("dormant: no semantic retrieval in milestone zero")
