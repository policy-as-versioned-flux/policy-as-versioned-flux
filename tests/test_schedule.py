"""Seam 2 — the scheduled sweep (build ticket 09).

Assertions are on the emitted `sweep` artefact's body, not on internals: `schedule.py` is as
disposable as the rest of this system.
"""

from __future__ import annotations

from pathlib import Path

from twin import fixtures, schedule
from twin.grades import Capabilities
from twin.repo import ModelRepo

COMMAND = ["twin", "sweep"]


def test_a_sweep_runs_every_scenario_in_every_org_of_the_named_repository(
    repo: ModelRepo, caps: Capabilities
) -> None:
    """The default fixture carries two orgs, one scenario each — both run, unconditionally."""
    artefact = schedule.sweep([repo], caps, COMMAND)

    counts = artefact.body["counts"]
    assert counts == {"repos": 1, "executed": 2, "failed": 0, "forecasts": 6}
    assert {e["org"] for e in artefact.body["executions"]} == {"netflix", "intel"}
    assert {e["scenario"] for e in artefact.body["executions"]} == {"dvd-decline-2011", "euv-slip-2026"}
    assert not artefact.body["failures"]
    assert artefact.body["regime"] == "as-consumed"


def test_a_sweep_spans_an_org_of_repositories_not_one(tmp_path: Path, caps: Capabilities) -> None:
    """The adaptation this ticket names: `sweep()` takes a list, not a single `--repo`."""
    pocket_dir = fixtures.build_pocket_org(tmp_path / "pocket")
    default_dir = fixtures.build(tmp_path / "default")
    repos = [ModelRepo.open(default_dir), ModelRepo.open(pocket_dir)]

    artefact = schedule.sweep(repos, caps, COMMAND)

    counts = artefact.body["counts"]
    assert counts["repos"] == 2
    assert counts["executed"] == 3  # netflix + intel from the default fixture, one from pocket
    assert counts["forecasts"] == 7  # 3 + 3 world models, plus pocket's single one
    assert "pocket" in {e["org"] for e in artefact.body["executions"]}


def test_two_sweeps_over_an_unchanged_repository_emit_the_same_volume(
    repo: ModelRepo, caps: Capabilities
) -> None:
    """No staleness check exists (deliberately) — this is the property harness guard

    `scheduled_emission_ignores_signal_presence` also asserts at the suite level; it is exercised
    here too because it is the load-bearing claim this build ticket makes, not an incidental one.
    """
    first = schedule.sweep([repo], caps, COMMAND)
    second = schedule.sweep([repo], caps, COMMAND)
    assert first.body["counts"]["forecasts"] == second.body["counts"]["forecasts"] > 0


def test_a_scenario_that_cannot_run_is_recorded_as_a_failure_and_the_sweep_continues(
    tmp_path: Path, caps: Capabilities
) -> None:
    """A malformed scenario must not stop a scheduler nobody is watching from emitting the rest.

    The break has to be schema-valid — a scenario field the schema itself refuses would fail
    while `Overlay.load` reads the whole org, before the sweep gets a chance to isolate it. Naming
    a world model nothing declares is schema-valid and fails inside `verbs.run` instead, which is
    exactly the failure shape a scheduler with nobody watching it has to survive.
    """
    root = fixtures.build(tmp_path / "broken")
    scenario = root / "orgs" / "netflix" / "scenarios" / "dvd-decline-2011.yaml"
    scenario.write_text(
        scenario.read_text(encoding="utf-8").replace("netflix-believed", "no-such-world-model"),
        encoding="utf-8", newline="\n",
    )
    fixtures.git(root, "add", "-A")
    fixtures.git(root, "commit", "-q", "-m", "point the scenario at a world model nothing declares")

    artefact = schedule.sweep([ModelRepo.open(root)], caps, COMMAND)

    failures = artefact.body["failures"]
    assert any(f["scenario"] == "dvd-decline-2011" for f in failures)
    # intel's scenario is untouched, so the sweep still produced it.
    assert any(e["scenario"] == "euv-slip-2026" for e in artefact.body["executions"])
    assert artefact.body["counts"]["executed"] == 1
    assert artefact.body["counts"]["failed"] == 1


def test_at_override_applies_to_every_scenario_in_the_sweep(repo: ModelRepo, caps: Capabilities) -> None:
    artefact = schedule.sweep([repo], caps, COMMAND, at="2011-07-12")
    assert artefact.body["at_override"] == "2011-07-12"
    for execution in artefact.body["executions"]:
        assert execution["body"]["scenario"]["at"] == "2011-07-12"


def test_repos_are_pinned_by_git_identity_not_by_filesystem_path(repo: ModelRepo, caps: Capabilities) -> None:
    artefact = schedule.sweep([repo], caps, COMMAND)
    assert artefact.pins["repos"] == [repo.pin.as_dict()]
    assert str(repo.model_root) not in str(artefact.pins)
