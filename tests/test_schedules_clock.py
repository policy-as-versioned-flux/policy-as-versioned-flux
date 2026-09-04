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


def _run(hours_ago, conclusion):
    when = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=hours_ago)
    return {"createdAt": when.isoformat(timespec="seconds").replace("+00:00", "Z"),
            "conclusion": conclusion}


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
