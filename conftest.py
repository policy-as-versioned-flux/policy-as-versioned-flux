"""Shared test fixtures.

Lives at the repository root so `import twin` resolves without an install step — the repository
is the package.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from twin import fixtures
from twin.grades import Capabilities
from twin.repo import ModelRepo


@pytest.fixture(scope="session")
def model_repo_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """The deterministic fixture model repository, built once and never mutated."""
    return fixtures.build(tmp_path_factory.mktemp("model") / "repo")


@pytest.fixture()
def repo(model_repo_dir: Path) -> ModelRepo:
    return ModelRepo.open(model_repo_dir)


@pytest.fixture(scope="session")
def caps() -> Capabilities:
    return Capabilities.load()


@pytest.fixture()
def scratch_repo(tmp_path: Path) -> Path:
    """A throwaway model repository for tests that dirty or move the tree."""
    return fixtures.build(tmp_path / "scratch-repo")
