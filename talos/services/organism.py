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
from dataclasses import dataclass

from talos.domain.ports import (
    AuditStore,
    Environment,
    EpisodeStore,
    RunStateStore,
    SelfModelStore,
    SkillStore,
    WALStore,
)
from talos.domain.reward import is_win
from talos.domain.types import Episode, RunState, Step
from talos.services.motor import Motor
from talos.services.policy import Policy
from talos.services.reflection import Reflector
from talos.services.reward_engine import RewardEngine
from talos.services.sensorium import Sensorium
from talos.services.skill_extraction import SkillExtractor, SkillPublisher
from talos.util.ids import episode_id as make_episode_id
from talos.util.ids import episode_seed, new_run_id


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
        run_store: RunStateStore | None = None,
        start_index: int = 0,
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
        self.run_id = run_id or new_run_id()
        self._run_seed = run_seed
        # Continuity: when a run_store is present the loop records a durable
        # cursor after every episode, and ``start_index`` is where a resumed
        # run picks up (0 for a fresh run). See services/resume.py.
        self._run_store = run_store
        self._start_index = start_index

    def run(self, n_episodes: int) -> list[EpisodeReport]:
        # ``run.start`` is a once-per-run governance event. A resumed run
        # (start_index > 0) already logged it in the process that began the
        # run, so re-logging it would fork the audit history away from an
        # uninterrupted run's. Fresh runs log it; resumed runs do not.
        if self._start_index == 0:
            self._audit.record("run.start", {"run_id": self.run_id, "seed": self._run_seed})

        reports: list[EpisodeReport] = []
        for i in range(self._start_index, n_episodes):
            reports.append(self._run_episode(i))
            self._commit_cursor(i, n_episodes, status="running")

        self._audit.record("run.end", {"run_id": self.run_id, "episodes": n_episodes})
        if n_episodes > 0:
            self._commit_cursor(n_episodes - 1, n_episodes, status="done")
        return reports

    def _commit_cursor(self, last_index: int, target: int, *, status: str) -> None:
        """The durable commit point for an episode. Written *last*, after every
        other store for episode ``last_index`` has committed, so the cursor is
        the single authority on how far the run genuinely got. No-op when the
        run has no store wired (the classic ephemeral mock run)."""
        if self._run_store is None:
            return
        self._run_store.save(
            RunState(
                run_id=self.run_id,
                run_seed=self._run_seed,
                env_name=self._env.name,
                last_index=last_index,
                target_episodes=target,
                status=status,
                updated_at=time.time(),
            )
        )

    def _run_episode(self, index: int) -> EpisodeReport:
        # Deterministic per-episode seed derived from the run seed.
        seed = episode_seed(self._run_seed, index)
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
            episode_id=make_episode_id(self.run_id, index),
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
    parser.add_argument(
        "--state-dir",
        type=str,
        default=None,
        help="persist the stores here so the run survives interruption and can "
        "resume; omit for the classic ephemeral run in a temp dir",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="stable id to resume (with --state-dir); a run resumes from its "
        "durable cursor, or starts fresh if none exists",
    )
    args = parser.parse_args()

    from talos.infrastructure.storage.sqlite.run_state import SqliteRunStore
    from talos.services.sleep import WakeSequence

    persistent = args.state_dir is not None
    if persistent:
        root = Path(args.state_dir)
        root.mkdir(parents=True, exist_ok=True)
    else:
        root = Path(tempfile.mkdtemp(prefix="talos_mock_"))

    env = MockEnv(
        n_contexts=args.contexts,
        n_actions=args.actions,
        env_seed=args.seed,
        drift_every=args.drift_every,
    )
    wal = SqliteWAL(root / "wal.db")
    episodes = SqliteEpisodeStore(root / "episodic.db")
    skills = SqliteSkillStore(root / "skills.db")
    audit = SqliteAuditStore(root / "audit.db")
    self_model = SqliteSelfModelStore(root / "self_model.db")
    reward = RewardEngine()
    extractor = SkillExtractor(episodes, reward)
    publisher = SkillPublisher(skills, ConfidenceGate(), audit)
    reflector = Reflector(self_model)

    run_store = None
    run_id = None
    start_index = 0
    if persistent:
        run_store = SqliteRunStore(root / "run_state.db")
        run_id = args.run_id or new_run_id()
        # Wake: verify the trust root, rebuild volatile state (reward + memo)
        # from the durable log, fast-forward the world, and learn where to
        # resume. A first start with no cursor comes back as resume_from 0.
        manifest = WakeSequence().wake(
            run_store=run_store,
            run_id=run_id,
            run_seed=args.seed,
            env=env,
            episodes=episodes,
            audit=audit,
            reward=reward,
            publisher=publisher,
            target_episodes=args.episodes,
        )
        start_index = manifest.resume_from
        verb = "fresh run" if manifest.fresh else f"resume from episode {start_index}"
        print(
            f"[wake] run {run_id}: {verb}  "
            f"(audit_ok={manifest.audit_ok}, reward_keys={manifest.reward_keys}, "
            f"memo={manifest.memo_contexts})"
        )
        if start_index >= args.episodes:
            print(f"[wake] run already complete at {start_index}/{args.episodes} episodes.")
            return

    talos = Talos(
        env, wal, episodes, skills, self_model, audit,
        extractor, publisher, reflector, reward,
        run_id=run_id,
        run_seed=args.seed,
        run_store=run_store,
        start_index=start_index,
    )
    talos.run(args.episodes)

    # Report the full curve from the durable episodic archive, so the numbers
    # are honest across a resume (reports would only hold this leg's episodes).
    all_eps = episodes.for_run(talos.run_id) if persistent else episodes.recent(args.episodes)
    all_eps = sorted(all_eps, key=lambda e: e.episode_id)
    wins = [1 if e.outcome == "win" else 0 for e in all_eps]
    window = max(1, args.episodes // 10)
    first = sum(wins[:window]) / max(1, len(wins[:window]))
    last = sum(wins[-window:]) / max(1, len(wins[-window:]))
    grown = skills.all()
    recoveries = sum(1 for r in audit.history() if r.kind == "skill.demotion")

    print(f"episodes         : {len(all_eps)}  (contexts={args.contexts}, actions={args.actions})")
    print(f"win rate  first {window:>4}: {first:.2%}")
    print(f"win rate  last  {window:>4}: {last:.2%}")
    print(f"skills grown     : {len(grown)}")
    for s in grown:
        print(f"  - {s.name}  (confidence={s.confidence:.2f}, from {len(s.provenance)} games)")
    mastered = [e for e in self_model.all() if e.mastered]
    print(f"contexts mastered: {len(mastered)} / {args.contexts}  (self-model)")
    print(f"drifts / recover : {env.drifts} / {recoveries}  (reward-surprise)")
    print(f"audit ledger ok  : {audit.verify()}  ({len(audit.history())} records)")
    print(f"({'persistent' if persistent else 'temporary'} stores under {root})")


if __name__ == "__main__":
    main()
