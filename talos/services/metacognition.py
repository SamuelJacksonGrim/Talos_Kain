"""Metacognition + offline evolution (DORMANT — spec §12).

The meta-controller makes control-plane changes only: retune thresholds,
adjust retry budgets, change routing/sharding, rewrite context-packing policy,
trigger deeper training. Success/failure trajectories and reflection critiques
feed a preference-pair generator → training dataset → fine-tune (DPO/RLHF/
RLAIF/distillation) → shadow deployment → canary → hot swap.

This is where the ``learn`` optional-dependency group (torch, the training
stack) eventually lands. Milestone zero learns only through episodic memory +
skills. This is the seam.
"""

from __future__ import annotations


class MetaController:
    """Control-plane changes only — never touches behavior-shaping stores
    directly (§12)."""

    def adjust(self, control_plane):
        raise NotImplementedError("dormant")


class PreferencePairGenerator:
    def generate(self, chosen, rejected, critiques):
        raise NotImplementedError("dormant: no training stack in milestone zero")
