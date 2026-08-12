"""The standing scenario library (build ticket 69; decision ticket 13, spec story 43).

One executable scenario per committed class — quantum/HNDL, bus-factor/key-person,
insider/coercion, supply-shock, sanctions, M&A, memory cost, AI-model access, climate event —
plus the opportunity leg and the backtest cases, all swept by the identical schedule ticket 09
built. Assertions are on emitted artefacts and the invariant's own `Result`, never on internals.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from twin import fixtures, invariants, schedule, verbs
from twin.grades import Capabilities
from twin.invariants import FAIL, PASS
from twin.model import Overlay
from twin.regimes import AS_CONSUMED
from twin.repo import ModelRepo
from twin.schema import COMMITTED_SCENARIO_CLASSES, SchemaError


@pytest.fixture(scope="session")
def library_repo_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    return fixtures.build_library_org(tmp_path_factory.mktemp("library") / "repo")


@pytest.fixture()
def library_overlay(library_repo_dir: Path) -> Overlay:
    return Overlay.load(ModelRepo.open(library_repo_dir), fixtures.LIBRARY_ORG)


def test_nine_committed_classes_are_named_and_the_library_covers_all_of_them(
    library_overlay: Overlay,
) -> None:
    assert len(COMMITTED_SCENARIO_CLASSES) == 9
    present = {s["class"] for s in library_overlay.scenarios.values() if s.get("class")}
    assert present == set(COMMITTED_SCENARIO_CLASSES)


def test_every_committed_class_scenario_actually_runs(
    library_repo_dir: Path, caps: Capabilities
) -> None:
    """Executable, not just declared: each of the nine scenarios emits a real forecast."""
    repo = ModelRepo.open(library_repo_dir)
    overlay = Overlay.load(repo, fixtures.LIBRARY_ORG)
    seen_classes = set()
    for scenario_id, scenario in overlay.scenarios.items():
        bundle = verbs.run(
            repo, caps, fixtures.LIBRARY_ORG, scenario_id, AS_CONSUMED,
            ["twin", "run", "--scenario", scenario_id],
        )
        assert bundle.body["forecasts"], f"{scenario_id} emitted no forecasts"
        assert bundle.body["regime"]["scoring_eligible"]
        seen_classes.add(scenario["class"])
    assert seen_classes == set(COMMITTED_SCENARIO_CLASSES)


def test_an_unknown_class_is_refused_at_the_schema(tmp_path: Path) -> None:
    """The closed enum, not a convention: a typo'd or invented class does not load."""
    root = fixtures.build_library_org(tmp_path / "planted")
    scenario_path = root / "orgs" / fixtures.LIBRARY_ORG / "scenarios" / "quantum-hndl-2026.yaml"
    original = scenario_path.read_text(encoding="utf-8")
    scenario_path.write_text(original.replace("class: quantum-hndl", "class: not-a-real-class"),
                              encoding="utf-8")
    fixtures.git(root, "commit", "-a", "-q", "-m", "plant an unknown class")
    with pytest.raises(SchemaError):
        Overlay.load(ModelRepo.open(root), fixtures.LIBRARY_ORG)


def test_the_m_and_a_class_is_framed_as_an_opportunity_not_a_threat(
    library_overlay: Overlay,
) -> None:
    """AC: "opportunity plays represented, not only threats" — demonstrated, not asserted."""
    m_and_a = next(s for s in library_overlay.scenarios.values() if s.get("class") == "m-and-a")
    assert "acquire" in m_and_a["question"].lower()
    threat_words = ("fail", "block", "lose", "coerc", "departs", "suffers")
    assert not any(word in m_and_a["question"].lower() for word in threat_words)


def test_the_standing_library_sweeps_with_no_separate_harness(tmp_path: Path, caps: Capabilities) -> None:
    """AC: backtest cases in the same library. One `sweep()` call, the identical verb ticket 09
    built — no bespoke backtest runner, just the repo list `build_standing_library` returns."""
    repos = [ModelRepo.open(p) for p in fixtures.build_standing_library(tmp_path)]
    artefact = schedule.sweep(repos, caps, ["twin", "sweep"])

    assert not artefact.body["failures"]
    assert artefact.body["counts"]["repos"] == 9
    classes_run = {
        e["body"]["scenario"]["proposition"]
        for e in artefact.body["executions"]
        if e["org"] == fixtures.LIBRARY_ORG
    }
    assert len(classes_run) == 9, "every committed-class scenario ran inside the one sweep"
    # The backtest answer keys sit in the identical executions list — no second code path.
    orgs_run = {e["org"] for e in artefact.body["executions"]}
    for backtest_org in ("carillion", "nmc", "wirecard", "enron", "astrazeneca", "sanofi"):
        assert backtest_org in orgs_run


def test_dropping_a_committed_class_from_the_library_fails_the_invariant(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The whole point: a silently dropped class is a CI failure, not a quiet gap."""
    original_build = fixtures.build_library_org

    def build_with_one_class_missing(dest: Path) -> Path:
        root = original_build(dest)
        scenario_path = root / "orgs" / fixtures.LIBRARY_ORG / "scenarios" / "sanctions-2026.yaml"
        fixtures.git(root, "rm", "-q", str(scenario_path.relative_to(root)))
        fixtures.git(root, "commit", "-q", "-m", "drop a class by mistake")
        return root

    monkeypatch.setattr(fixtures, "build_library_org", build_with_one_class_missing)

    results, ok = invariants.run(only=["standing_library_covers_committed_classes"], tmp=tmp_path)
    assert len(results) == 1
    result = results[0]
    assert result.status == FAIL
    assert "sanctions" in result.detail
    assert not ok


def test_the_live_invariant_passes_against_the_real_library(tmp_path: Path) -> None:
    results, ok = invariants.run(only=["standing_library_covers_committed_classes"], tmp=tmp_path)
    assert len(results) == 1 and results[0].status == PASS and ok
