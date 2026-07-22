"""Telos — long-horizon purpose, domain concepts (DORMANT).

The purpose layer sits *above* the executive (spec §15): missions flow through
a telos-fit check on their way to the PFC. Standing purposes are
architect-signed; campaign objectives are promoted/retired through the horizon
gate. This module defines the types; the deliberation machinery is
``services/purpose.py``, the store is behind ``TelosStore``.

Nothing here is implemented in milestone zero.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PurposeTier(str, Enum):
    STANDING = "standing"    # architect-signed; never self-executing
    CAMPAIGN = "campaign"    # HORIZON-gated; months-long


class TelosFit(str, Enum):
    SERVES = "serves"
    NEUTRAL = "neutral"
    CONFLICTS = "conflicts"


@dataclass(frozen=True)
class Purpose:
    purpose_id: str
    tier: PurposeTier
    statement: str
    signed_by: str | None = None  # required for STANDING
