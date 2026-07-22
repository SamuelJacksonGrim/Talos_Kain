"""SC2Env — the StarCraft II adapter. Deliberately a stub.

This is the *first milestone* of the README ("a StarCraft II agent that
measurably learns across games"), but it is intentionally not implemented yet.
The order is: prove the learning architecture in MockEnv, *then* attach the
game. When that happens, SC2Env becomes a real ``Environment`` implementation
wrapping PySC2 / python-sc2 — and because it satisfies the same port as
MockEnv, nothing in the domain or services layer changes.

Implementation notes for when this wakes up:

* Depends on the ``sc2`` optional-dependency group (pysc2 + the StarCraft II
  binary + map packs) — none of which run in a bare CI container.
* ``reset`` maps the SC2 observation into a ``context_id`` bucket (matchup /
  macro state) + the discrete action set the policy chooses from.
* ``step`` issues the action via the SC2 API and reports win/loss on episode
  end; mid-episode steps carry shaped reward.
* Curriculum lives in ``curriculum.py`` (beat built-in AI on Easy, then
  re-baseline at Medium — see the README).
"""

from __future__ import annotations

from talos.domain.types import Action, Observation, StepResult


class SC2Env:
    name = "sc2"
    version = "0-unimplemented"

    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            "SC2Env is a dormant organ. Prove the learning loop in MockEnv "
            "first; then implement this adapter against PySC2 (install the "
            "'sc2' optional-dependency group and the StarCraft II binary)."
        )

    def reset(self, seed: int) -> Observation:  # pragma: no cover
        raise NotImplementedError

    def step(self, action: Action) -> StepResult:  # pragma: no cover
        raise NotImplementedError

    def close(self) -> None:  # pragma: no cover
        raise NotImplementedError
