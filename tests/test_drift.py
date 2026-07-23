"""The reward engine in a drifting world.

Without a value/surprise signal, once the organism publishes a skill it exploits
it forever and never re-explores — so when the world moves, it locks into
confident failure. These tests prove the reward engine breaks that lock: it
notices a trusted action has started failing and drives recovery.
"""

from __future__ import annotations

from talos.infrastructure.environments.mock.mock_env import MockEnv
from talos.services.reward_engine import RewardEngine

from tests.conftest import build_talos


def test_prediction_error_flags_a_broken_belief_not_a_blind_guess():
    reward = RewardEngine()

    # A blind exploratory loss on an untried action: mild, not a surprise.
    pe_cold = reward.observe("ctx-0", 1, 0.0)
    assert pe_cold == 0.0
    assert not reward.is_surprise(pe_cold)

    # Build up trust in action 2 by winning with it repeatedly.
    for _ in range(5):
        reward.observe("ctx-0", 2, 1.0)
    assert reward.is_trusted("ctx-0", 2)

    # Now action 2 fails: that is a real surprise, a broken belief.
    pe_hot = reward.observe("ctx-0", 2, 0.0)
    assert pe_hot < 0
    assert reward.is_surprise(pe_hot)


def test_the_world_actually_drifts(stores):
    env = MockEnv(n_contexts=3, n_actions=5, env_seed=2, drift_every=25)
    build_talos(stores, env).run(200)
    assert env.drifts > 0, "drift_every should have moved the world"


def test_organism_stays_afloat_while_the_world_drifts(stores):
    """A stuck organism would lose every drifted context forever, collapsing
    toward chance. Continuous recovery keeps the win rate high throughout."""
    env = MockEnv(n_contexts=3, n_actions=5, env_seed=2, drift_every=25)
    reports = build_talos(stores, env).run(400)

    assert env.drifts > 0
    assert sum(1 for r in reports if r.recovered) > 0

    back_half = reports[200:]
    win_rate = sum(r.won for r in back_half) / len(back_half)
    # Chance is 1/5 and a stuck organism trends toward 0. Recovery keeps it high.
    assert win_rate > 0.6, f"drift not being recovered: back-half win rate {win_rate:.2%}"


def test_organism_reconverges_once_the_world_settles(stores):
    env = MockEnv(n_contexts=3, n_actions=5, env_seed=2, drift_every=25)
    talos = build_talos(stores, env)
    talos.run(400)

    assert env.drifts > 0

    # Freeze the world and let it settle; recovery must drive the self-model to
    # the world's *current* hidden winner for every context.
    env.freeze()
    talos.run(150)

    entries = {e.context_id: e for e in stores["self_model"].all()}
    assert len(entries) == env.n_contexts
    for context_id, entry in entries.items():
        assert entry.winning_action == env._solution(context_id), (
            f"{context_id}: self-model says {entry.winning_action}, "
            f"world now wants {env._solution(context_id)}"
        )


def test_recovery_retires_the_stale_skill_and_publishes_a_replacement(stores):
    """After drift, the demoted skill is retired (not silently mutated) and,
    once settled, a fresh skill for the new winner is live."""
    env = MockEnv(n_contexts=2, n_actions=4, env_seed=5, drift_every=20)
    talos = build_talos(stores, env)
    talos.run(400)
    env.freeze()
    talos.run(120)

    # Some skill was demoted along the way (audited as skill.demotion).
    demotions = [r for r in stores["audit"].history() if r.kind == "skill.demotion"]
    assert demotions, "a drifted skill should have been demoted"

    # Every currently-live skill points at the world's current winner.
    for skill in stores["skills"].all():
        assert skill.action_id == env._solution(skill.context_id)

    # The ledger still verifies after all the churn.
    assert stores["audit"].verify()
