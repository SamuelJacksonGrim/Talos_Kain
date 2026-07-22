"""Telos store persistence (DORMANT — implements TelosStore, §15).

Standing purposes (architect-signed) and campaign objectives (HORIZON-gated).
Architect writes to standing purposes are signed and out-of-band; campaigns
are promoted/retired only through the horizon gate. Not implemented in
milestone zero.
"""

from __future__ import annotations


class SqliteTelosStore:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("dormant: no telos layer in milestone zero")
