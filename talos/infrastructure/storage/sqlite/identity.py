"""Identity kernel persistence (DORMANT — implements IdentityKernel, §3/§11).

Core axioms, bonds, fixed points, supremacy. The only autonomous writer is
ANNEAL, and that call must carry an audit token proving it came through the
crucible — enforced when this wakes. Architect writes are out-of-band, signed,
full-diff. Not implemented in milestone zero.
"""

from __future__ import annotations


class SqliteIdentityKernel:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            "dormant: the identity kernel wakes only with the crucible that guards it"
        )
