"""Hot retrieval cache adapter (DORMANT — implements HotCache, §3).

The only memory fast enough for the motor loop: zero-copy pointers, summaries,
active constraints. Milestone zero's single-step loop needs no cache.

Note: this is the leading candidate for the Rust/PyO3 escape hatch. If
profiling the SC2 agent shows the cache is the wall, the *implementation*
behind this port moves to ``rust/hot_cache/`` — the port and every caller stay
put. See ``rust/README.md``.
"""

from __future__ import annotations


class InMemoryHotCache:
    def __init__(self, *args, **kwargs):
        raise NotImplementedError("dormant: no hot cache in milestone zero")
