"""The milestone-zero test: the organism measurably learns across episodes,
and the improvement is attributable to a named, provenance-bearing skill."""

from __future__ import annotations


def _win_rate(reports):
    return sum(r.won for r in reports) / len(reports)


def test_win_rate_improves_across_episodes(organism):
    talos, _ = organism
    reports = talos.run(400)

    window = 40
    first = _win_rate(reports[:window])
    last = _win_rate(reports[-window:])

    # The whole thesis: a noisy losing baseline becomes reliable winning.
    assert last > first, f"no improvement: first={first:.2%} last={last:.2%}"
    assert last >= 0.9, f"did not converge: last window win rate {last:.2%}"


def test_learning_is_from_grown_skills(organism):
    talos, stores = organism
    reports = talos.run(400)

    grown = stores["skills"].all()
    # One winning skill per context (4 contexts) should emerge.
    assert len(grown) == 4, f"expected a skill per context, got {len(grown)}"

    # Every skill carries the episode lineage that produced it — provenance is
    # a query, not a story.
    for skill in grown:
        assert skill.provenance, f"skill {skill.skill_id} has no provenance"

    # By the end, decisions are driven by grown skills, not exploration.
    tail_sources = [r.decision_source for r in reports[-40:]]
    assert tail_sources.count("skill") >= 35, tail_sources


def test_run_is_reproducible(stores, tmp_path):
    """Same seeds -> identical trajectory. Nothing hidden from replay."""
    from talos.domain.gate import ConfidenceGate
    from talos.infrastructure.environments.mock.mock_env import MockEnv
    from talos.infrastructure.storage.sqlite.audit import SqliteAuditStore
    from talos.infrastructure.storage.sqlite.episodic import SqliteEpisodeStore
    from talos.infrastructure.storage.sqlite.self_model import SqliteSelfModelStore
    from talos.infrastructure.storage.sqlite.skills import SqliteSkillStore
    from talos.infrastructure.storage.sqlite.wal import SqliteWAL
    from talos.services.organism import Talos
    from talos.services.reflection import Reflector
    from talos.services.skill_extraction import SkillExtractor, SkillPublisher

    def build(tag):
        d = tmp_path / tag
        env = MockEnv(n_contexts=4, n_actions=6, env_seed=3)
        episodes = SqliteEpisodeStore(d / "ep.db")
        skills = SqliteSkillStore(d / "sk.db")
        self_model = SqliteSelfModelStore(d / "sm.db")
        audit = SqliteAuditStore(d / "au.db")
        return Talos(
            env,
            SqliteWAL(d / "wal.db"),
            episodes,
            skills,
            self_model,
            audit,
            SkillExtractor(episodes),
            SkillPublisher(skills, ConfidenceGate(), audit),
            Reflector(self_model),
            run_seed=42,
        )

    a = [(r.context_id, r.action_id, r.won) for r in build("a").run(120)]
    b = [(r.context_id, r.action_id, r.won) for r in build("b").run(120)]
    assert a == b
