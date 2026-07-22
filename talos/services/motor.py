"""Motor executor: actuate a chosen action against the environment.

Thin slice of §4. The ghost-pointer unthaw protocol, cerebellar micro-fixes,
and the local motor yield are dormant — milestone zero is single-step, so the
motor loop is just "execute and report". The seam exists so those mechanisms
have somewhere to land.
"""

from __future__ import annotations

from talos.domain.ports import Environment
from talos.domain.types import Action, StepResult


class Motor:
    def __init__(self, env: Environment):
        self._env = env

    def act(self, action: Action) -> StepResult:
        return self._env.step(action)
