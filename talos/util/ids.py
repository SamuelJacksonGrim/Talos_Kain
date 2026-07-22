"""Identifier helpers."""

from __future__ import annotations

import uuid


def new_run_id() -> str:
    """Short, unique run identifier for provenance stamping."""
    return uuid.uuid4().hex[:12]


def episode_id(run_id: str, index: int) -> str:
    return f"{run_id}::ep{index:06d}"
