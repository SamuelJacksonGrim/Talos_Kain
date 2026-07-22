"""Hypergraph memory adapter (DORMANT — implements HypergraphStore, §3).

Constraints, fallacies, causal relations. Distilled lessons from evicted
episodes land here. Not implemented in milestone zero.
"""

from __future__ import annotations


class SqliteHypergraphStore:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("dormant: no constraint graph in milestone zero")
