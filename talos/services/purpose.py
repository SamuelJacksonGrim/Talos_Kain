"""Telos deliberation (DORMANT — spec §15).

The long-horizon purpose layer that sits above the executive. A mission's
telos-fit is checked on the way in (serves / neutral / conflicts); conflicts
with a standing purpose escalate to a human. Deep-sleep-only purpose
deliberation asks "is there a better problem, same purpose?"; campaign-tier
changes exit through the horizon gate (lineage · telos alignment · identity
continuity · foreclosure). Standing-purpose changes are architect-only,
logged, never self-executing.

Milestone zero has no telos store and no long horizon. This is the seam for
the highest gate in the chain of why.
"""

from __future__ import annotations

from talos.domain.telos import TelosFit


class TelosFitCheck:
    def fit(self, mission) -> TelosFit:
        raise NotImplementedError("dormant")


class HorizonGate:
    """Promotes/retires campaigns; consults the IDK for identity continuity.
    Standing purposes never pass through here — only the architect writes
    them (§15)."""

    def deliberate(self, proposal):
        raise NotImplementedError("dormant")
