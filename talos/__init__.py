"""Talos_Kain — the organism.

A governed, continuously-learning autonomous-agent harness. This package is
the milestone-zero vertical slice of the v7 spec (see ``aamsfc.md``): the
minimal loop that can *measurably learn across episodes* and point at the
named skill it grew to get there.

Layering (dependencies point inward only):

    domain/          pure organism logic — no SQLite, no environment, no I/O
    services/        orchestration — the learning loop, sensorium, policy, motor
    infrastructure/  adapters — SQLite stores, environments (mock, sc2), logging

The one law that runs through the whole family: *nothing modifies a
behavior-shaping store except through one audited gate.* Consolidation may
nominate; it may not appoint.
"""

__version__ = "0.0.1"
