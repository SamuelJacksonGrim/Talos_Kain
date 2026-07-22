"""The self-model organ: the organism models itself, and that model makes
exploration bounded instead of a blind random walk."""

from __future__ import annotations

from collections import defaultdict


def test_self_model_learns_the_true_winner_per_context(organism):
    talos, stores = organism
    talos.run(400)

    env = talos._env  # the mock world, for its hidden answer key
    entries = {e.context_id: e for e in stores["self_model"].all()}

    # Every context is modeled, mastered, and the modeled winner is the
    # environment's actual hidden winner. The organism knows itself correctly.
    assert len(entries) == env.n_contexts
    for context_id, entry in entries.items():
        assert entry.mastered, f"{context_id} never mastered"
        assert entry.winning_action == env._solution(context_id)


def test_exploration_never_repeats_a_known_loser(organism):
    """Before the self-model, exploration could re-pick an action already known
    to lose. With it, systematic elimination means at most (n_actions - 1)
    losses can precede the first win in any context."""
    talos, _ = organism
    reports = talos.run(400)

    env = talos._env
    losses_before_first_win = defaultdict(int)
    won_yet = set()
    # Reconstruct per-context loss count prior to that context's first win.
    for r in reports:
        if r.context_id in won_yet:
            continue
        if r.won:
            won_yet.add(r.context_id)
        else:
            losses_before_first_win[r.context_id] += 1

    for context_id, losses in losses_before_first_win.items():
        assert losses <= env.n_actions - 1, (
            f"{context_id} lost {losses} times before its first win, "
            f"more than the {env.n_actions - 1} a clean elimination allows"
        )


def test_reflection_is_a_faithful_summary_of_episodes(organism):
    """The self-model is derived fact: its attempt/win counts must match the
    episodic log it was built from, per context."""
    talos, stores = organism
    talos.run(200)

    for entry in stores["self_model"].all():
        episodes = stores["episodes"].by_context(entry.context_id)
        assert entry.attempts == len(episodes)
        assert entry.wins == sum(1 for e in episodes if e.outcome == "win")
