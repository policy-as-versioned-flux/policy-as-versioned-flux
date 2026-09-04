"""The clock verdict file, and the red clock that names its owner.

Eco-system tickets 56 and 85. The seam these tests hold is the one that lets the citable run
grade a clock at all: `verify/schedules/schedules.py` reads the live facts either from `gh` (in
a job that holds a credential) or from a JSON file a credentialled job wrote earlier (in the gate
job, which holds none). Everything here is pure: no network, no `gh`, no estate checkout.

The same properties are asserted inside `schedules.py selfcheck`, which is what the gate runs.
These exist so the seam is red-then-green under pytest too, and so a regression names itself in
one line rather than in a 900-line script's assert.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import os
import re
import sys

import pytest

HUB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEDULES = os.path.join(HUB, "verify", "schedules", "schedules.py")


def _load():
    sys.path.insert(0, os.path.join(HUB, "verify"))
    spec = importlib.util.spec_from_file_location("schedules_under_test", SCHEDULES)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


sch = _load()


@pytest.fixture(autouse=True)
def _no_ambient_workflow_run(monkeypatch):
    """These are pure tests and they also run inside Actions, where GITHUB_RUN_ID is set for
    real. A verdict file is bound to the run that wrote it, so an ambient run id would change
    what the unbound fixtures below assert. Every test that cares sets its own."""
    monkeypatch.delenv("GITHUB_RUN_ID", raising=False)
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)


def _write(tmp_path, *, collected_ago_hours=0.05, schema=None, units=None):
    when = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=collected_ago_hours)
    doc = {"schema": schema or sch.VERDICT_SCHEMA,
           "collected_at": when.isoformat(timespec="seconds"),
           "collector": "tests", "units": units if units is not None else {}}
    path = tmp_path / "clocks.json"
    path.write_text(json.dumps(doc))
    return str(path)


def _unit(**workflows):
    return {"feeds": {"remote": "org/feeds", "reachable": True,
                      "ruleset": {"verdict": "unavailable", "reason": "the repository is public"},
                      "workflows": workflows}}


def _run(hours_ago, conclusion, *, database_id=None, status=None):
    when = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours_ago)
    run = {"createdAt": when.isoformat(timespec="seconds").replace("+00:00", "Z"),
           "conclusion": conclusion,
           "status": status or ("completed" if conclusion else "in_progress")}
    if database_id is not None:
        run["databaseId"] = database_id
    return run


def _timed(run):
    return {"remote_state": "timed", "remote_crons": ["17 3 * * *"], "run": run}


# --- the file is read as facts, and every gap in it is a NAMED could-not-look -----------------
def test_a_fresh_verdict_file_answers_the_three_live_questions(tmp_path):
    path = _write(tmp_path, units=_unit(**{"fetch.yml": _timed(_run(6, "success"))}))
    v = sch.Verdict(path)
    assert v.live
    assert v.ruleset_state("org/feeds") == ("unavailable", "the repository is public")
    assert v.remote_crons("org/feeds", "fetch.yml") == ("timed", ["17 3 * * *"])
    assert v.last_run("org/feeds", "fetch.yml")["conclusion"] == "success"


@pytest.mark.parametrize("remote, workflow, expected", [
    ("org/nowhere", "fetch.yml", "carries no entry for"),
    ("org/feeds", "absent.yml", "carries no reading for"),
    ("org/feeds", "errored.yml", "could not be read"),
])
def test_a_missing_fact_is_a_could_not_look_and_never_a_quiet_no(tmp_path, remote, workflow,
                                                                expected):
    path = _write(tmp_path, units=_unit(**{"fetch.yml": _timed(_run(6, "success")),
                                           "errored.yml": {"error": "HTTP 404"}}))
    with pytest.raises(sch.CouldNotLook) as caught:
        sch.Verdict(path).last_run(remote, workflow)
    assert expected in str(caught.value)


def test_an_unreachable_organisation_blinds_only_itself(tmp_path):
    units = _unit(**{"fetch.yml": _timed(_run(6, "success"))})
    units["ico"] = {"remote": "org/ico", "reachable": False, "unreachable_reason": "HTTP 403"}
    v = sch.Verdict(_write(tmp_path, units=units))
    assert v.last_run("org/feeds", "fetch.yml") is not None
    with pytest.raises(sch.CouldNotLook, match="HTTP 403"):
        v.last_run("org/ico", "fetch.yml")


# --- a bad file falls back to OFFLINE, never to a credential the gate is not meant to hold ----
@pytest.mark.parametrize("kwargs, expected", [
    ({"collected_ago_hours": sch.VERDICT_MAX_AGE_HOURS + 2}, "freshness window"),
    ({"schema": "something-else/v9"}, "clock-verdict/v1"),
])
def test_a_stale_or_foreign_verdict_file_is_refused(tmp_path, kwargs, expected):
    path = _write(tmp_path, units=_unit(), **kwargs)
    with pytest.raises(ValueError, match=expected):
        sch.Verdict(path)


@pytest.mark.parametrize("kwargs", [
    {"collected_ago_hours": sch.VERDICT_MAX_AGE_HOURS + 2},
    {"schema": "something-else/v9"},
])
def test_a_refused_verdict_file_does_not_reach_for_gh(tmp_path, monkeypatch, kwargs):
    monkeypatch.setenv("CLOCK_VERDICT", _write(tmp_path, units=_unit(), **kwargs))
    monkeypatch.setattr(sch, "_gh", lambda *a: pytest.fail("the gate must not call gh"))
    source = sch.observer()
    assert not source.live
    assert "does not fall back" in source.unreachable


def test_a_missing_verdict_file_does_not_reach_for_gh(tmp_path, monkeypatch):
    monkeypatch.setenv("CLOCK_VERDICT", str(tmp_path / "never-written.json"))
    monkeypatch.setattr(sch, "_gh", lambda *a: pytest.fail("the gate must not call gh"))
    assert not sch.observer().live


# --- the documented non-zero exit is ONE conclusion (ticket 56) --------------------------------
def test_only_failure_is_excused_for_the_clock_that_re_raises_the_gates_verdict():
    assert sch.RED_GATE_EXITS_NONZERO.get("truth.yml") == "failure"
    for not_a_tick in ("cancelled", "timed_out", "startup_failure", "in_progress", None):
        assert sch.RED_GATE_EXITS_NONZERO.get("truth.yml") != not_a_tick


# --- a run never grades ITSELF, and a run in flight has concluded nothing (ticket 56, round 2) --
# `gh run list --event schedule --limit 1` carries no status filter, so on a SCHEDULED truth.yml
# run the newest scheduled run of truth.yml IS the run doing the grading: conclusion "", status
# in_progress. With `failure` the only excused conclusion, that graded FAIL "in_progress" on every
# scheduled run for ever, blamed ticket 85 for it, and no estate fix could clear it. The same
# false red hits any clock whose newest scheduled run happens to be in flight when the collector
# looks.
def test_the_grading_run_never_grades_itself():
    runs = [_run(0, "", database_id=99), _run(24, "success", database_id=98)]
    assert sch.newest_gradable(runs, "99")["databaseId"] == 98


def test_the_newest_completed_run_is_preferred_over_one_still_in_flight():
    runs = [_run(0, "", database_id=99), _run(24, "success", database_id=98)]
    assert sch.newest_gradable(runs, None)["databaseId"] == 98


def test_an_in_flight_run_with_nothing_completed_behind_it_is_still_returned():
    only = sch.newest_gradable([_run(0, "", database_id=99)], None)
    assert only is not None and not only.get("conclusion")


def test_no_scheduled_run_at_all_is_still_none():
    assert sch.newest_gradable([], None) is None
    assert sch.newest_gradable([_run(0, "", database_id=99)], "99") is None


NOW = dt.datetime.now(dt.timezone.utc)


def test_a_run_still_in_flight_is_a_named_skip_and_never_a_fail():
    status, message = sch.run_line("hub", "truth.yml", _run(0, ""), NOW, " (ticket 85 owns it)")
    assert status == "SKIP", message
    assert "in_progress" in message and "concluded nothing" in message
    assert "ticket 85" not in message, "a could-not-look must not blame a ticket for a red"


def test_a_finished_run_still_grades_exactly_as_before():
    assert sch.run_line("feeds", "fetch.yml", _run(6, "success"), NOW)[0] == "PASS"
    assert sch.run_line("feeds", "fetch.yml", _run(6, "failure"), NOW)[0] == "FAIL"
    assert sch.run_line("hub", "truth.yml", _run(6, "failure"), NOW)[0] == "PASS"
    assert sch.run_line("hub", "truth.yml", _run(6, "cancelled"), NOW)[0] == "FAIL"
    assert sch.run_line("feeds", "fetch.yml",
                        _run(sch.PERIOD_HOURS + 5, "success"), NOW)[0] == "FAIL"


# --- the verdict file is bound to the run and the repository that wrote it (ticket 56, round 2) -
def _bound(tmp_path, **overrides):
    doc = {"schema": sch.VERDICT_SCHEMA,
           "collected_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "collector": "tests", "run_id": "1234", "repository": "org/hub",
           "units": _unit(**{"fetch.yml": _timed(_run(6, "success"))})}
    doc.update(overrides)
    path = tmp_path / "bound.json"
    path.write_text(json.dumps(doc))
    return str(path)


def test_a_verdict_file_from_this_run_and_this_repository_is_accepted(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_RUN_ID", "1234")
    monkeypatch.setenv("GITHUB_REPOSITORY", "org/hub")
    assert sch.Verdict(_bound(tmp_path)).live


@pytest.mark.parametrize("overrides, expected", [
    ({"run_id": "999"}, "run 999"),
    ({"repository": "org/somewhere-else"}, "org/somewhere-else"),
    ({"run_id": ""}, "(none)"),
])
def test_a_verdict_file_from_another_run_or_repository_is_refused(tmp_path, monkeypatch,
                                                                  overrides, expected):
    monkeypatch.setenv("GITHUB_RUN_ID", "1234")
    monkeypatch.setenv("GITHUB_REPOSITORY", "org/hub")
    with pytest.raises(ValueError, match="not this run"):
        sch.Verdict(_bound(tmp_path, **overrides))
    with pytest.raises(ValueError, match=re.escape(expected)):
        sch.Verdict(_bound(tmp_path, **overrides))


def test_an_unbound_verdict_file_is_refused_inside_a_workflow_run(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_RUN_ID", "1234")
    monkeypatch.setenv("GITHUB_REPOSITORY", "org/hub")
    path = _write(tmp_path, units=_unit(**{"fetch.yml": _timed(_run(6, "success"))}))
    with pytest.raises(ValueError, match="not this run"):
        sch.Verdict(path)


def test_a_forged_verdict_file_does_not_reach_for_gh(tmp_path, monkeypatch):
    monkeypatch.setenv("GITHUB_RUN_ID", "1234")
    monkeypatch.setenv("GITHUB_REPOSITORY", "org/hub")
    monkeypatch.setenv("CLOCK_VERDICT", _bound(tmp_path, run_id="999"))
    monkeypatch.setattr(sch, "_gh", lambda *a: pytest.fail("the gate must not call gh"))
    source = sch.observer()
    assert not source.live and "does not fall back" in source.unreachable


def test_outside_a_workflow_run_there_is_nothing_to_bind_to(tmp_path, monkeypatch):
    monkeypatch.delenv("GITHUB_RUN_ID", raising=False)
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    assert sch.Verdict(_bound(tmp_path, run_id="", repository="")).live


def test_the_collector_stamps_the_run_and_the_repository(monkeypatch):
    monkeypatch.setenv("GITHUB_RUN_ID", "4321")
    monkeypatch.setenv("GITHUB_REPOSITORY", "org/hub")
    monkeypatch.setattr(sch, "units", lambda: [])
    doc = sch.collect()
    assert doc["run_id"] == "4321" and doc["repository"] == "org/hub"


# --- a red clock names the open ticket that owns it (ticket 85) --------------------------------
OWNED = {
    "driftwood/twin-sweep.yml": {"ticket": 72, "owns": "the sweep dies under bash -e"},
    "nowhere/none.yml": {"ticket": 999999, "owns": "no such ticket"},
}


def test_a_red_clock_with_an_owner_names_the_ticket():
    assert "ticket 72 owns it" in sch.owner_clause("driftwood", "twin-sweep.yml", OWNED)


def test_a_red_clock_with_no_owner_says_it_is_unowned():
    assert "unowned" in sch.owner_clause("ludlow", "propose-tier.yml", {})


def test_an_entry_naming_a_ticket_that_does_not_exist_is_called_stale():
    assert "the map is stale" in sch.owner_clause("nowhere", "none.yml", OWNED)


def test_the_map_cannot_rot():
    faults = sch.owners_faults(OWNED, {"driftwood/twin-sweep.yml"})
    assert any("no such ticket" in f for f in faults)
    assert any("not a clock this checker grades" in f for f in faults)


def test_the_map_that_ships_names_only_tickets_that_exist():
    shipped = sch.owners()
    assert shipped, "verify/schedules/clock-owners.yaml is empty or unreadable"
    for key, entry in shipped.items():
        assert sch.ticket_status(entry["ticket"]) is not None, key
