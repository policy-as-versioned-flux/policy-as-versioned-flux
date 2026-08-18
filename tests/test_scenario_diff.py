"""`twin scenario-diff` (build ticket 88, decision ticket 13 AC 3): a scenario definition, versioned
by git and diffed as a map-diff. Git already supplies the storage half (`ModelRepo.open(path,
ref=...)`, unchanged); this exercises the renderer against two real refs on a real repository —
`main` and a branch, the branch-per-scenario shape research 03 names.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from twin import fixtures
from twin.grades import Capabilities
from twin.repo import ModelRepo
from twin.scenario_diff import ScenarioDiffError, diff

ORG = "netflix"
SCENARIO = "dvd-decline-2011"


@pytest.fixture()
def branched_repo(tmp_path: Path) -> Path:
    """The default fixture, plus an `explore` branch that changes one scalar scenario field and
    moves one component's evolution stage — a field-level change and a map-level change in the
    same commit, so a single diff call exercises both legs."""
    root = fixtures.build(tmp_path / "repo")
    fixtures.git(root, "checkout", "-q", "-b", "explore")

    scenario_path = root / "orgs" / ORG / "scenarios" / f"{SCENARIO}.yaml"
    scenario_path.write_text(
        scenario_path.read_text(encoding="utf-8").replace(
            "horizon: '2012-12-31'", "horizon: '2013-06-30'"
        ),
        encoding="utf-8",
    )
    component_path = root / "orgs" / ORG / "components" / "dvd-by-mail.yaml"
    component_path.write_text(
        component_path.read_text(encoding="utf-8").replace(
            "evolution: commodity", "evolution: product"
        ),
        encoding="utf-8",
    )
    fixtures.git(root, "commit", "-a", "-q", "-m", "explore: push the horizon, regress the stage")
    return root


def test_a_scalar_field_change_is_reported_before_after(branched_repo: Path, caps: Capabilities) -> None:
    artefact = diff(branched_repo, caps, ORG, SCENARIO, "main", "explore", ["twin", "scenario-diff"])
    assert artefact.body["scenario_fields"]["horizon"] == {"before": "2012-12-31", "after": "2013-06-30"}


def test_a_moved_component_appears_in_the_map_diff(branched_repo: Path, caps: Capabilities) -> None:
    artefact = diff(branched_repo, caps, ORG, SCENARIO, "main", "explore", ["twin", "scenario-diff"])
    moved = {m["component"]: m for m in artefact.body["map"]["moved"]}
    assert "dvd-by-mail" in moved
    assert moved["dvd-by-mail"]["stage"] == {"before": "commodity", "after": "product"}


def test_an_unchanged_field_or_component_is_not_reported(branched_repo: Path, caps: Capabilities) -> None:
    artefact = diff(branched_repo, caps, ORG, SCENARIO, "main", "explore", ["twin", "scenario-diff"])
    assert "proposition" not in artefact.body["scenario_fields"]
    assert "components" not in artefact.body["scenario_fields"]
    moved_components = {m["component"] for m in artefact.body["map"]["moved"]}
    assert "streaming-experience" not in moved_components


def test_identical_refs_diff_to_nothing(tmp_path: Path, caps: Capabilities) -> None:
    root = fixtures.build(tmp_path / "repo")
    artefact = diff(root, caps, ORG, SCENARIO, "HEAD", "HEAD", ["twin", "scenario-diff"])
    assert artefact.body["scenario_fields"] == {}
    assert artefact.body["map"] == {"added": [], "removed": [], "moved": []}


def test_a_scenario_authored_only_on_one_side_is_reported_not_refused(
    tmp_path: Path, caps: Capabilities
) -> None:
    """Mid-flight branch-per-scenario authoring — a scenario not yet merged — is a real state,
    not an error: absence on one side is exactly what `scenario_present` exists to say."""
    root = fixtures.build(tmp_path / "repo")
    fixtures.git(root, "checkout", "-q", "-b", "new-scenario")
    new_scenario = root / "orgs" / ORG / "scenarios" / "new-idea.yaml"
    new_scenario.write_text(
        """\
id: new-idea
question: Does a brand-new idea move the needle?
proposition: dvd-rental-revenue-falls-faster-than-streaming-adds
at: '2011-07-12'
horizon: '2012-12-31'
components:
  - dvd-by-mail
world_models:
  - twin-default
affected_parties:
  - id: nobody-in-particular
    who: A placeholder outsider for this test's own fixture.
    consequence: None modelled; this scenario exists only to exercise the absent side.
""",
        encoding="utf-8",
    )
    fixtures.git(root, "add", "-A")
    fixtures.git(root, "commit", "-q", "-m", "author a scenario only on this branch")

    artefact = diff(root, caps, ORG, "new-idea", "main", "new-scenario", ["twin", "scenario-diff"])
    assert artefact.body["scenario_present"] == {"before": False, "after": True}
    assert artefact.body["scenario_fields"]["question"]["before"] is None


def test_absent_at_both_sides_is_refused(tmp_path: Path, caps: Capabilities) -> None:
    root = fixtures.build(tmp_path / "repo")
    with pytest.raises(ScenarioDiffError):
        diff(root, caps, ORG, "no-such-scenario", "main", "main", ["twin", "scenario-diff"])


def test_the_cli_command_round_trips(branched_repo: Path, tmp_path: Path) -> None:
    from twin.cli import main as cli_main

    out = tmp_path / "diff.json"
    code = cli_main([
        "scenario-diff", "--repo", str(branched_repo), "--org", ORG, "--scenario", SCENARIO,
        "--before", "main", "--after", "explore", "--out", str(out),
    ])
    assert code == 0
    assert out.exists()
