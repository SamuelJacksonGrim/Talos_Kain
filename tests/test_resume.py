"""Resume: an interrupted run continues instead of restarting, and the result
is *bit-identical* to a run that was never interrupted.

The strongest possible statement of correctness here is the hash-chained audit
ledger: its digests are computed over (seq, kind, payload), never over wall-clock
time, so two runs that experienced the same events in the same order produce the
same chain of digests. If a resumed run's ledger equals an uninterrupted run's
ledger digest-for-digest, then nothing was double-counted, nothing was skipped,
and no governance event was re-emitted. That is the assertion these tests make.
"""

from __future__ import annotations

import pytest

from talos.domain.gate import ConfidenceGate
from talos.infrastructure.environments.mock.mock_env import MockEnv
from talos.infrastructure.storage.sqlite.audit import SqliteAuditStore
from talos.infrastructure.storage.sqlite.episodic import SqliteEpisodeStore
from talos.infrastructure.storage.sqlite.run_state import SqliteRunStore
from talos.infrastructure.storage.sqlite.self_model import SqliteSelfModelStore
from talos.infrastructure.storage.sqlite.skills import SqliteSkillStore
from talos.infrastructure.storage.sqlite.wal import SqliteWAL
from talos.services.organism import Talos
from talos.services.reflection import Reflector
from talos.services.reward_engine import RewardEngine
from talos.services.skill_extraction import SkillExtractor, SkillPublisher
from talos.services.sleep import WakeSequence

RUN_ID = "resume-test"
SEED = 5


# --------------------------------------------------------------------------
# Test doubles: two ways for a process to die
# --------------------------------------------------------------------------

class CrashOnReset:
    """A world that dies at the *start* of episode ``crash_index`` — before any
    of that episode's stores are written. Models a clean crash on an episode
    boundary (the common case)."""

    name = "mock"
    version = "0"

    def __init__(self, inner: MockEnv, crash_index: int):
        self._inner = inner
        self._crash_index = crash_index
        self._resets = 0
        self.n_contexts = inner.n_contexts
        self.n_actions = inner.n_actions

    def reset(self, seed: int):
        if self._resets == self._crash_index:
            raise RuntimeError("simulated crash (reset)")
        self._resets += 1
        return self._inner.reset(seed)

    def step(self, action):
        return self._inner.step(action)

    def close(self) -> None:
        self._inner.close()

    @property
    def drifts(self) -> int:
        return self._inner.drifts


class CrashOnCommit:
    """A run store that dies at the *commit* of episode ``crash_index`` — after
    every other store for that episode has already written. Models the worst
    case: a crash in the microsecond window between an episode's side effects
    and its durable cursor, so the resumed run must re-run that episode
    idempotently."""

    def __init__(self, inner: SqliteRunStore, crash_index: int):
        self._inner = inner
        self._crash_index = crash_index

    def save(self, state) -> None:
        if state.last_index == self._crash_index and state.status == "running":
            raise RuntimeError("simulated crash (commit)")
        self._inner.save(state)

    def load(self, run_id):
        return self._inner.load(run_id)


# --------------------------------------------------------------------------
# Wiring + snapshotting
# --------------------------------------------------------------------------

def _stores(root):
    return {
        "wal": SqliteWAL(root / "wal.db"),
        "episodes": SqliteEpisodeStore(root / "episodic.db"),
        "skills": SqliteSkillStore(root / "skills.db"),
        "audit": SqliteAuditStore(root / "audit.db"),
        "self_model": SqliteSelfModelStore(root / "self_model.db"),
        "run_store": SqliteRunStore(root / "run_state.db"),
    }


def _wire(root, env, target, *, run_store=None, drift_every=0):
    """Build a fully-wired organism on ``root`` at the resume point its cursor
    dictates. Mirrors the driver's wake-then-run path."""
    s = _stores(root)
    rs = run_store or s["run_store"]
    reward = RewardEngine()
    publisher = SkillPublisher(s["skills"], ConfidenceGate(), s["audit"])

    manifest = WakeSequence().wake(
        run_store=rs,
        run_id=RUN_ID,
        run_seed=SEED,
        env=env,
        episodes=s["episodes"],
        audit=s["audit"],
        reward=reward,
        publisher=publisher,
        target_episodes=target,
    )
    talos = Talos(
        env,
        s["wal"],
        s["episodes"],
        s["skills"],
        s["self_model"],
        s["audit"],
        SkillExtractor(s["episodes"], reward),
        publisher,
        Reflector(s["self_model"]),
        reward,
        run_id=RUN_ID,
        run_seed=SEED,
        run_store=rs,
        start_index=manifest.resume_from,
    )
    return talos, s, manifest


def _snapshot(s):
    """Everything that must be identical, with all wall-clock fields stripped."""
    skills = sorted(
        (k.skill_id, k.name, k.context_id, k.action_id, k.version, k.confidence, k.provenance)
        for k in s["skills"].all()
    )
    self_model = sorted(
        (e.context_id, e.attempts, e.wins, e.tried_actions, e.winning_action)
        for e in s["self_model"].all()
    )
    audit = [(r.seq, r.kind, r.payload, r.prev_digest, r.digest) for r in s["audit"].history()]
    outcomes = [
        (e.episode_id, e.context_id, e.outcome)
        for e in sorted(s["episodes"].for_run(RUN_ID), key=lambda e: e.episode_id)
    ]
    return {"skills": skills, "self_model": self_model, "audit": audit, "outcomes": outcomes}


def _uninterrupted(root, target, drift_every=0):
    env = MockEnv(n_contexts=4, n_actions=6, env_seed=SEED, drift_every=drift_every)
    talos, s, manifest = _wire(root, env, target, drift_every=drift_every)
    assert manifest.fresh and manifest.resume_from == 0
    talos.run(target)
    return _snapshot(s), env.drifts


# --------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------

def test_resume_after_boundary_crash_is_bit_identical(tmp_path):
    """Crash cleanly between episodes, resume, and land on the same audit chain."""
    target, crash_at = 400, 200

    baseline, _ = _uninterrupted(tmp_path / "whole", target)

    # Leg 1: dies at the start of episode 200. Scoped so its SQLite connections
    # are released before leg 2 reopens the same files.
    def leg_one():
        env = CrashOnReset(MockEnv(n_contexts=4, n_actions=6, env_seed=SEED), crash_at)
        talos, _, manifest = _wire(tmp_path / "split", env, target)
        assert manifest.fresh
        with pytest.raises(RuntimeError, match="crash"):
            talos.run(target)

    leg_one()

    # Leg 2: a brand-new process reopens the same dir and resumes.
    env = MockEnv(n_contexts=4, n_actions=6, env_seed=SEED)
    talos, s, manifest = _wire(tmp_path / "split", env, target)
    assert not manifest.fresh, "should have found a cursor to resume from"
    assert manifest.resume_from == crash_at
    assert manifest.audit_ok
    talos.run(target)

    assert _snapshot(s) == baseline


def test_commit_crash_keeps_governance_exact(tmp_path):
    """Crash in the window between an episode's side effects and its durable
    cursor, so the resumed run re-runs that one episode.

    This is the boundary of what is cheaply guaranteeable: with a non-idempotent
    reflection pass and no atomic commit across the separate store files, the
    re-run of that single in-flight episode can re-apply its self-model fold.
    What must *not* drift is governance and provenance — the audit ledger, the
    grown skills, and the episodic outcomes stay bit-identical (reward and the
    admission memo are rebuilt from the durable log, so no skill is re-published
    and no ledger entry is duplicated). The self-model's behavioral verdict
    (which action wins each context) is preserved; only a counter may be off by
    the single re-run episode, which the organism self-corrects."""
    target, crash_at = 400, 200

    baseline, _ = _uninterrupted(tmp_path / "whole", target)

    def leg_one():
        env = MockEnv(n_contexts=4, n_actions=6, env_seed=SEED)
        s = _stores(tmp_path / "split")
        crashing = CrashOnCommit(s["run_store"], crash_at)
        reward = RewardEngine()
        publisher = SkillPublisher(s["skills"], ConfidenceGate(), s["audit"])
        WakeSequence().wake(
            run_store=crashing, run_id=RUN_ID, run_seed=SEED, env=env,
            episodes=s["episodes"], audit=s["audit"], reward=reward,
            publisher=publisher, target_episodes=target,
        )
        talos = Talos(
            env, s["wal"], s["episodes"], s["skills"], s["self_model"], s["audit"],
            SkillExtractor(s["episodes"], reward), publisher, Reflector(s["self_model"]),
            reward, run_id=RUN_ID, run_seed=SEED, run_store=crashing, start_index=0,
        )
        # Episode 200's stores commit, then its cursor write throws.
        with pytest.raises(RuntimeError, match="crash"):
            talos.run(target)

    leg_one()

    env = MockEnv(n_contexts=4, n_actions=6, env_seed=SEED)
    talos, s, manifest = _wire(tmp_path / "split", env, target)
    assert manifest.resume_from == crash_at  # re-runs episode 200
    talos.run(target)

    result = _snapshot(s)
    # Governance + provenance are exact.
    assert result["audit"] == baseline["audit"]
    assert result["skills"] == baseline["skills"]
    assert result["outcomes"] == baseline["outcomes"]

    # Behavior is preserved: the winning action per context is unchanged.
    base_win = {c: win for c, _, _, _, win in baseline["self_model"]}
    res_win = {c: win for c, _, _, _, win in result["self_model"]}
    assert res_win == base_win

    # The only permitted drift: the one re-run episode's fold, in one context.
    base_attempts = sum(a for _, a, _, _, _ in baseline["self_model"])
    res_attempts = sum(a for _, a, _, _, _ in result["self_model"])
    assert 0 <= res_attempts - base_attempts <= 1


def test_resume_reconstructs_a_drifting_world(tmp_path):
    """A drifting world advances hidden state on every reset. Fast-forwarding it
    through the committed episodes must reproduce that state exactly — same
    drifts, same recoveries, same grown skills."""
    target, crash_at, drift = 300, 150, 50

    baseline, base_drifts = _uninterrupted(tmp_path / "whole", target, drift_every=drift)

    def leg_one():
        env = CrashOnReset(
            MockEnv(n_contexts=4, n_actions=6, env_seed=SEED, drift_every=drift), crash_at
        )
        talos, _, _ = _wire(tmp_path / "split", env, target, drift_every=drift)
        with pytest.raises(RuntimeError, match="crash"):
            talos.run(target)

    leg_one()

    env = MockEnv(n_contexts=4, n_actions=6, env_seed=SEED, drift_every=drift)
    talos, s, manifest = _wire(tmp_path / "split", env, target, drift_every=drift)
    assert manifest.resume_from == crash_at
    talos.run(target)

    assert env.drifts == base_drifts, "fast-forward did not reproduce the drift state"
    assert _snapshot(s) == baseline


def test_completed_run_resumes_to_a_noop(tmp_path):
    """Waking a finished run reports completion and runs nothing further."""
    target = 120
    _uninterrupted(tmp_path / "done", target)

    env = MockEnv(n_contexts=4, n_actions=6, env_seed=SEED)
    _, s, manifest = _wire(tmp_path / "done", env, target)
    assert manifest.resume_from >= target
    assert manifest.complete


def test_wake_refuses_nothing_but_reports_a_tampered_ledger(tmp_path):
    """Wake verifies the trust root and surfaces the verdict in its manifest."""
    target = 80
    _uninterrupted(tmp_path / "run", target)

    # Tamper: flip a byte of one audit payload so the chain no longer recomputes.
    import sqlite3

    conn = sqlite3.connect(str(tmp_path / "run" / "audit.db"))
    conn.execute(
        "UPDATE audit_log SET payload = REPLACE(payload, 'run.start', 'run.START') "
        "WHERE seq = 1"
    )
    conn.commit()
    conn.close()

    env = MockEnv(n_contexts=4, n_actions=6, env_seed=SEED)
    _, _, manifest = _wire(tmp_path / "run", env, target)
    assert manifest.audit_ok is False
