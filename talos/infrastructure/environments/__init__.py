"""Environments the organism can act in.

Both implement ``talos.domain.ports.Environment``. MockEnv is the *primary*
world for milestone zero, not a fallback: if the learning loop cannot show
improvement in a deterministic toy world, attaching StarCraft II only makes
debugging harder. Once the organism reliably learns in the mock, SC2 becomes
an adapter problem rather than a learning-architecture problem.
"""
