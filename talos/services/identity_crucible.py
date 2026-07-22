"""Identity crucible (DORMANT — spec §10/§11).

The only autonomous door into the identity kernel. Identity-relevant material
arrives tagged (DISSONANCE_SUPPRESSED / IDENTITY_CANDIDATE / IDENTITY_PROPOSAL)
and faces a forensic gauntlet: lineage audit → poisoning check (shatter if
compromised, IDK untouched) → resonance weight → counterfactual crucible
(replay episodes with the candidate replacing the IDK prior) → continuity
check → annealing (graft a nuance branch, preserve the anchor).

This is the single-writer gate for identity — the §11 analogue of the skill
publisher. Milestone zero has no identity kernel. This is the seam, and it is
deliberately the hardest gate in the system.
"""

from __future__ import annotations

from talos.domain.types import GateDecision


class IdentityCrucible:
    def anneal_or_reject(self, candidate) -> GateDecision:
        raise NotImplementedError(
            "dormant: the identity kernel and its crucible wake only once the "
            "organism has a self worth protecting"
        )
