"""Shared fixtures: build a fully-wired mock organism on temporary stores."""

from __future__ import annotations

import pytest

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


@pytest.fixture
def stores(tmp_path):
    return {
        "wal": SqliteWAL(tmp_path / "wal.db"),
        "episodes": SqliteEpisodeStore(tmp_path / "episodic.db"),
        "skills": SqliteSkillStore(tmp_path / "skills.db"),
        "self_model": SqliteSelfModelStore(tmp_path / "self_model.db"),
        "audit": SqliteAuditStore(tmp_path / "audit.db"),
    }


@pytest.fixture
def organism(stores):
    env = MockEnv(n_contexts=4, n_actions=6, env_seed=1)
    extractor = SkillExtractor(stores["episodes"])
    publisher = SkillPublisher(stores["skills"], ConfidenceGate(), stores["audit"])
    reflector = Reflector(stores["self_model"])
    talos = Talos(
        env,
        stores["wal"],
        stores["episodes"],
        stores["skills"],
        stores["self_model"],
        stores["audit"],
        extractor,
        publisher,
        reflector,
        run_seed=7,
    )
    return talos, stores
