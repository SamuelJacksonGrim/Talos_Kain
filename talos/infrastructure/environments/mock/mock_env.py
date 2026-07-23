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

**Drift (opt-in).** With ``drift_every > 0`` the world stops being stationary:
every ``drift_every`` episodes, one context's winning action silently changes
to a different action. This is the forcing function for the reward engine —
memory and skills alone would lock the organism into confidently exploiting an
action that no longer wins. Drift is deterministic in ``env_seed`` (its own RNG
stream advances only on drift events), so a drifting run is still fully
reproducible. Default ``drift_every=0`` keeps the classic stationary world.
"""

from __future__ import annotations

import random

from talos.domain.types import Action, Observation, StepResult


class MockEnv:
    name = "mock"
    version = "0"

    def __init__(
        self,
        n_contexts: int = 4,
        n_actions: int = 6,
        env_seed: int = 0,
        drift_every: int = 0,
    ):
        if n_contexts < 1 or n_actions < 2:
            raise ValueError("need >=1 context and >=2 actions")
        self.n_contexts = n_contexts
        self.n_actions = n_actions
        self._env_seed = env_seed
        self._drift_every = drift_every

        # Hidden, stable winning action per context — set once from env_seed.
        env_rng = random.Random(env_seed)
        self._winning_action = {
            f"ctx-{i}": env_rng.randrange(n_actions) for i in range(n_contexts)
        }

        # Drift machinery: a separate RNG stream so it never disturbs the
        # context-selection determinism, and it only advances on drift events.
        self._drift_rng = random.Random(env_seed * 7 + 1)
        self._episode_count = 0
        self.drifts = 0  # exposed for tests/telemetry

        self._current_context: str | None = None

    def reset(self, seed: int) -> Observation:
        self._episode_count += 1
        self._maybe_drift()
        # Which context this episode presents is a deterministic function of
        # the episode seed — so a run visits contexts in a reproducible order.
        idx = seed % self.n_contexts
        self._current_context = f"ctx-{idx}"
        return Observation(
            context_id=self._current_context,
            available_actions=tuple(range(self.n_actions)),
        )

    def _maybe_drift(self) -> None:
        if not self._drift_every:
            return
        if self._episode_count % self._drift_every != 0:
            return
        context_id = f"ctx-{self._drift_rng.randrange(self.n_contexts)}"
        current = self._winning_action[context_id]
        # Move to a genuinely different winning action.
        choices = [a for a in range(self.n_actions) if a != current]
        self._winning_action[context_id] = self._drift_rng.choice(choices)
        self.drifts += 1

    def step(self, action: Action) -> StepResult:
        if self._current_context is None:
            raise RuntimeError("step() called before reset()")
        won = action.action_id == self._winning_action[self._current_context]
        self._current_context = None  # single-step episode
        if won:
            return StepResult(reward=1.0, done=True, outcome="win")
        return StepResult(reward=0.0, done=True, outcome="loss")

    def freeze(self) -> None:
        """Stop drifting. Used to give the organism a stable settling window
        after a drifting run, so recovery can be observed converging."""
        self._drift_every = 0

    def close(self) -> None:  # pragma: no cover - nothing to release
        pass

    # Exposed for tests/telemetry only; the organism never reads this.
    def _solution(self, context_id: str) -> int:
        return self._winning_action[context_id]
