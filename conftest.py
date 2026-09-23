"""Shared test fixtures.

Lives at the repository root so `import twin` resolves without an install step — the repository
is the package.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator

import pytest

from twin import fixtures
from twin.grades import Capabilities
from twin.repo import ModelRepo
from twin.sign import KEY_ENV


# What the worker process started with: the shell's own key, or none. Read at import, before any
# fixture of any scope has run.
_KEY_AT_START = os.environ.get(KEY_ENV)


@pytest.fixture(autouse=True)
def _signing_key_does_not_leak(request: pytest.FixtureRequest) -> Iterator[None]:
    """Fail the test that leaves `TWIN_SIGNING_KEY` other than the worker started with (ticket 125).

    A key left in the environment signs every later artefact in the same xdist worker with a key
    nobody passed. Function-scoped `monkeypatch` changes are undone before this checks, because an
    autouse fixture is torn down after the fixtures the test asked for. A session- or
    module-scoped fixture that holds a key is not undone, and this names the first test it ran for.
    """
    yield
    after = os.environ.get(KEY_ENV)
    if after == _KEY_AT_START:
        return
    if _KEY_AT_START is None:
        os.environ.pop(KEY_ENV, None)
    else:
        os.environ[KEY_ENV] = _KEY_AT_START
    pytest.fail(
        f"{request.node.nodeid} left {KEY_ENV} other than the worker started with; a key that "
        "outlives the test that set it signs later artefacts in the same worker",
        pytrace=False,
    )


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
