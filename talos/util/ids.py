"""Identifier helpers."""

from __future__ import annotations

import uuid


def new_run_id() -> str:
    """Short, unique run identifier for provenance stamping."""
    return uuid.uuid4().hex[:12]


def episode_id(run_id: str, index: int) -> str:
    return f"{run_id}::ep{index:06d}"


# A large prime keeps successive episodes' seeds far apart in the RNG space
# while staying a pure function of (run_seed, index) — so the entire curve is
# reproducible, and a resumed run can reconstruct the exact seed of any episode
# it needs to replay.
_SEED_STRIDE = 1_000_003


def episode_seed(run_seed: int, index: int) -> int:
    """The deterministic per-episode seed. The single source of truth for the
    formula, shared by the live loop and the resume path so they can never
    drift out of agreement about what episode ``index`` means."""
    return run_seed * _SEED_STRIDE + index
