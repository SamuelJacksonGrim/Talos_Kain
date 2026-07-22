"""Memory consolidation (DORMANT — spec §3/§8).

The async memory encoder fans experience out by type — trajectories to
episodic, compressed meaning to semantic, causal structure to the hypergraph,
procedural candidates to the skill CI, temporal density to CrystalStore. The
anti-lobotomy eviction rules live here too: cryptographic pinning, terminal
distillation (strip narrative, keep the causal lesson), tombstones, and dream
rehearsal.

The two hardening rules are load-bearing and belong in code the moment this
wakes: the encoder writes NEITHER the identity kernel NOR the skill library.
Both go through their gates (crucible, skill CI). Consolidation may nominate;
it may not appoint.

Milestone zero writes episodes synchronously and does no eviction. This is the
seam.
"""

from __future__ import annotations


class MemoryEncoder:
    def encode(self, batch):
        raise NotImplementedError("dormant: milestone zero writes episodes directly")


class EvictionProtocol:
    """Three exits, none of them deletion: shield (pinned), distill (keep the
    lesson), tombstone (cold, reversible) (§3)."""

    def evict(self, node):
        raise NotImplementedError("dormant")


class DreamRehearsal:
    """Collide aging nodes with new data; any minted constraint carries a
    SYNTH provenance tag (§8)."""

    def rehearse(self):
        raise NotImplementedError("dormant")
