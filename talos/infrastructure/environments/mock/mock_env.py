"""MockEnv — a deterministic, learnable toy world.

The world is a set of *contexts* (think: matchups). Each context has one
hidden winning action, fixed for the life of the environment by ``env_seed``.
A single-step episode presents one context; picking its winning action is a
win, anything else is a loss.

Why this shape:

* **Random play loses.** With ``n_actions`` choices the blind win rate is
  1/n. A losing streak is the default — exactly the noisy baseline the
  milestone wants to turn into a win.
* **Memory + skills win.** The winning action per context is stable, so an
  organism that remembers past outcomes and grows a per-context skill climbs
  toward a ~100% win rate. The improvement is attributable to a *named skill*,
  not to variance — which is the falsifiable claim the milestone is built on.
* **Fully deterministic.** ``reset(seed)`` selects the context from the seed,
  and the hidden mapping depends only on ``env_seed``. Given a run seed the
  entire curve is reproducible; nothing is hidden from replay.

This mirrors the StarCraft II milestone one-to-one — noisy losing streak →
win → point at the grown skill — minus the 30 GB game binary.
"""

from __future__ import annotations

import random

from talos.domain.types import Action, Observation, StepResult


class MockEnv:
    name = "mock"
    version = "0"

    def __init__(self, n_contexts: int = 4, n_actions: int = 6, env_seed: int = 0):
        if n_contexts < 1 or n_actions < 2:
            raise ValueError("need >=1 context and >=2 actions")
        self.n_contexts = n_contexts
        self.n_actions = n_actions
        self._env_seed = env_seed

        # Hidden, stable winning action per context — set once from env_seed.
        env_rng = random.Random(env_seed)
        self._winning_action = {
            f"ctx-{i}": env_rng.randrange(n_actions) for i in range(n_contexts)
        }

        self._current_context: str | None = None

    def reset(self, seed: int) -> Observation:
        # Which context this episode presents is a deterministic function of
        # the episode seed — so a run visits contexts in a reproducible order.
        idx = seed % self.n_contexts
        self._current_context = f"ctx-{idx}"
        return Observation(
            context_id=self._current_context,
            available_actions=tuple(range(self.n_actions)),
        )

    def step(self, action: Action) -> StepResult:
        if self._current_context is None:
            raise RuntimeError("step() called before reset()")
        won = action.action_id == self._winning_action[self._current_context]
        self._current_context = None  # single-step episode
        if won:
            return StepResult(reward=1.0, done=True, outcome="win")
        return StepResult(reward=0.0, done=True, outcome="loss")

    def close(self) -> None:  # pragma: no cover - nothing to release
        pass

    # Exposed for tests/telemetry only; the organism never reads this.
    def _solution(self, context_id: str) -> int:
        return self._winning_action[context_id]
