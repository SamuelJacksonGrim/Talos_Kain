"""The organism loop — Talos.

This is milestone zero made executable. It assembles the ports, then runs the
minimal cycle the spec calls the forcing function:

    observe -> score -> choose -> act -> reward -> record -> learn

`learn` is the whole point: after each episode the extractor nominates a
per-context skill candidate and the publisher submits it through the gate.
Over episodes, the policy stops exploring and starts exploiting grown skills,
and the win rate climbs. Everything is a function of (run seed, episode
index), so the curve is reproducible.

The heavy organs of the v7 spec (sleep/wake, identity crucible, telos,
federated cortex, immune system) are intentionally absent. They wake when
gameplay exposes the need — not before.
"""

from __future__ import annotations

import random
import time
import uuid
from dataclasses import dataclass

from talos.domain.ports import (
    AuditStore,
    Environment,
    EpisodeStore,
    SelfModelStore,
    SkillStore,
    WALStore,
)
from talos.domain.reward import is_win
from talos.domain.types import Episode, Step
from talos.services.motor import Motor
from talos.services.policy import Policy
from talos.services.reflection import Reflector
from talos.services.reward_engine import RewardEngine
from talos.services.sensorium import Sensorium
from talos.services.skill_extraction import SkillExtractor, SkillPublisher


@dataclass
class EpisodeReport:
    episode_id: str
    context_id: str
    action_id: int
    won: bool
    decision_source: str  # "skill" | "self_model" | "explore"
    recovered: bool = False  # a reward-surprise triggered drift recovery here


class Talos:
    def __init__(
        self,
        env: Environment,
        wal: WALStore,
        episodes: EpisodeStore,
        skills: SkillStore,
        self_model: SelfModelStore,
        audit: AuditStore,
        extractor: SkillExtractor,
        publisher: SkillPublisher,
        reflector: Reflector,
        reward: RewardEngine,
        run_id: str | None = None,
        run_seed: int = 0,
    ):
        self._env = env
        self._wal = wal
        self._episodes = episodes
        self._skills = skills
        self._self_model = self_model
        self._audit = audit
        self._extractor = extractor
        self._publisher = publisher
        self._reflector = reflector
        self._reward = reward
        self._sensorium = Sensorium()
        self._policy = Policy(skills, self_model)
        self._motor = Motor(env)
        self.run_id = run_id or uuid.uuid4().hex[:12]
        self._run_seed = run_seed

    def run(self, n_episodes: int) -> list[EpisodeReport]:
        self._audit.record("run.start", {"run_id": self.run_id, "seed": self._run_seed})
        reports: list[EpisodeReport] = []
        for i in range(n_episodes):
            reports.append(self._run_episode(i))
        self._audit.record("run.end", {"run_id": self.run_id, "episodes": n_episodes})
        return reports

    def _run_episode(self, index: int) -> EpisodeReport:
        # Deterministic per-episode seed derived from the run seed.
        seed = self._run_seed * 1_000_003 + index
        rng = random.Random(seed)

        raw_obs = self._env.reset(seed)
        observation, salience = self._sensorium.perceive(raw_obs)
        self._wal.append("observe", {"context_id": observation.context_id, "salience": salience})

        action, source = self._policy.choose(observation, rng)
        self._wal.append("choose", {"action_id": action.action_id, "source": source})

        result = self._motor.act(action)
        self._wal.append(
            "act",
            {"action_id": action.action_id, "reward": result.reward, "outcome": result.outcome},
        )

        episode = Episode(
            episode_id=f"{self.run_id}::ep{index:06d}",
            run_id=self.run_id,
            seed=seed,
            env_name=self._env.name,
            env_version=self._env.version,
            context_id=observation.context_id,
            steps=[Step(observation, action, result.reward, salience)],
            outcome=result.outcome,
            started_at=time.time(),
            finished_at=time.time(),
        )
        self._episodes.save(episode)

        # reflect: update the organism's model of itself for this context.
        self._reflector.reflect(episode)

        # reward: prediction error modulates the system. A confidently-good
        # action that just failed is the signal that the world moved under us.
        prediction_error = self._reward.observe(
            observation.context_id, action.action_id, result.reward
        )
        recovered = False
        if self._reward.is_surprise(prediction_error):
            self._recover(observation.context_id, action.action_id)
            recovered = True
        self._wal.append(
            "reward",
            {
                "context_id": observation.context_id,
                "prediction_error": prediction_error,
                "recovered": recovered,
            },
        )

        # learn: nominate a candidate; the publisher decides via the gate.
        candidate = self._extractor.nominate(observation.context_id)
        if candidate is not None:
            self._publisher.submit(candidate)

        return EpisodeReport(
            episode_id=episode.episode_id,
            context_id=observation.context_id,
            action_id=action.action_id,
            won=is_win(result),
            decision_source=source,
            recovered=recovered,
        )

    def _recover(self, context_id: str, failed_action: int) -> None:
        """A trusted action failed — the world drifted. Demote the stale skill
        (audited: removing a behavior-shaping capability is a governance event)
        and reset the self-model belief so the policy re-explores. The
        publisher forgets its memo so the replacement can be published."""
        skill = self._skills.for_context(context_id)
        if skill is not None:
            self._skills.retire(skill.skill_id)
            self._audit.record(
                "skill.demotion",
                {
                    "context_id": context_id,
                    "skill_id": skill.skill_id,
                    "reason": "reward_surprise",
                    "failed_action": failed_action,
                },
            )
        self._publisher.forget(context_id)

        entry = self._self_model.get(context_id)
        if entry is not None:
            entry.winning_action = None
            entry.tried_actions = ()
            self._self_model.put(entry)


def main() -> None:
    """`talos-mock` entry point: run the mock organism and print the learning
    curve. Uses temporary on-disk stores so a run leaves no committed state.
    """
    import argparse
    import tempfile
    from pathlib import Path

    from talos.domain.gate import ConfidenceGate
    from talos.infrastructure.environments.mock.mock_env import MockEnv
    from talos.infrastructure.storage.sqlite.audit import SqliteAuditStore
    from talos.infrastructure.storage.sqlite.episodic import SqliteEpisodeStore
    from talos.infrastructure.storage.sqlite.self_model import SqliteSelfModelStore
    from talos.infrastructure.storage.sqlite.skills import SqliteSkillStore
    from talos.infrastructure.storage.sqlite.wal import SqliteWAL

    parser = argparse.ArgumentParser(description="Run the Talos_Kain mock organism.")
    parser.add_argument("--episodes", type=int, default=400)
    parser.add_argument("--contexts", type=int, default=4)
    parser.add_argument("--actions", type=int, default=6)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--drift-every",
        type=int,
        default=0,
        help="episodes between drift events (0 = stationary world)",
    )
    args = parser.parse_args()

    tmp = Path(tempfile.mkdtemp(prefix="talos_mock_"))
    env = MockEnv(
        n_contexts=args.contexts,
        n_actions=args.actions,
        env_seed=args.seed,
        drift_every=args.drift_every,
    )
    wal = SqliteWAL(tmp / "wal.db")
    episodes = SqliteEpisodeStore(tmp / "episodic.db")
    skills = SqliteSkillStore(tmp / "skills.db")
    audit = SqliteAuditStore(tmp / "audit.db")
    self_model = SqliteSelfModelStore(tmp / "self_model.db")
    reward = RewardEngine()
    extractor = SkillExtractor(episodes, reward)
    publisher = SkillPublisher(skills, ConfidenceGate(), audit)
    reflector = Reflector(self_model)

    talos = Talos(
        env, wal, episodes, skills, self_model, audit,
        extractor, publisher, reflector, reward,
        run_seed=args.seed,
    )
    reports = talos.run(args.episodes)

    window = max(1, args.episodes // 10)
    first = sum(r.won for r in reports[:window]) / window
    last = sum(r.won for r in reports[-window:]) / window
    grown = skills.all()

    print(f"episodes         : {args.episodes}  (contexts={args.contexts}, actions={args.actions})")
    print(f"win rate  first {window:>4}: {first:.2%}")
    print(f"win rate  last  {window:>4}: {last:.2%}")
    print(f"skills grown     : {len(grown)}")
    for s in grown:
        print(f"  - {s.name}  (confidence={s.confidence:.2f}, from {len(s.provenance)} games)")
    mastered = [e for e in self_model.all() if e.mastered]
    print(f"contexts mastered: {len(mastered)} / {args.contexts}  (self-model)")
    recoveries = sum(1 for r in reports if r.recovered)
    print(f"drifts / recover : {env.drifts} / {recoveries}  (reward-surprise)")
    print(f"audit ledger ok  : {audit.verify()}  ({len(audit.history())} records)")
    print(f"(temporary stores under {tmp})")


if __name__ == "__main__":
    main()
