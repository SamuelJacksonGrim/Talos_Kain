"""Identity kernel — domain concepts (DORMANT).

The IDK holds the organism's fixed points: core axioms, bonds, and the
supremacy rule that lets it change without ceasing to be itself (spec §3/§10/
§11). This module defines *what* those are; persistence is an infrastructure
concern, and the only autonomous write path is annealing through the crucible
(``services/identity_crucible.py``).

Nothing here is implemented in milestone zero. It exists so the type and the
invariant have a home before the organ wakes.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FixedPoint:
    """An axiom the organism will not autonomously overwrite. IDK priors win
    pointer-polarity collisions by hardcoded override, zero inference (§10)."""

    key: str
    statement: str
    signed_by: str  # architect signature for architect-set points


# Invariant, stated as code-adjacent documentation for the future writer:
#   The encoder MUST NOT write the IDK. Identity-relevant material is tagged
#   IDENTITY_CANDIDATE and queued for the crucible. Consolidation may
#   nominate; it may not appoint.
IDK_SINGLE_WRITER = "ANNEAL"
