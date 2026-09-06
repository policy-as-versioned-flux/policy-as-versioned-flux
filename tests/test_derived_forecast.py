"""The twin derives a probability (ecosystem ticket 93; ticket 75 Q10, owner-reasoned).

Seams, all pure code, none needing a token or a network:

  * the forecast artefact `twin.derived-forecast/v1` and its validator: every probability
    carries a perspective, a currency, a basis (derived or recorded) and the grade the ladder
    allows -- 5 for a derivation, none for a recorded belief, which the world-model schema
    forbids a grade for (a finding, not a schema change);
  * a derived probability's basis names a REAL feed observation: a market MOVE between two
    dated levels the served envelope carries, or a news event with its URL -- never a level
    read as a probability, never a weight or a score on an ordinal grade;
  * pre-registration is read off GIT HISTORY, not off a field the twin writes: the first-parent
    commit that brought the file onto the served ref is dated before the outcome date, or the
    forecast is not scored;
  * the score is `twin/scoring.py`'s, computed by the check from the forecast and the overlay's
    own `outcome` record, never read from a file;
  * the local clock's `derive` row runs the seam end to end with a stand-in model, and refuses
    a forecast that cites an observation the feed does not carry.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from twin import derived_forecast as df
from twin import scoring

HUB = Path(__file__).resolve().parents[1]
CLOCK = HUB / "talk" / "local-clock.sh"
VALIDATOR = HUB / ".claude" / "skills" / "derive-probability" / "assets" / "validate_forecast.py"
EXAMPLE = HUB / ".claude" / "skills" / "derive-probability" / "assets" / "example-forecast.yaml"
FIXTURE = HUB / "verify" / "twin-evals" / "derived_forecast_fixture.py"
STUB = HUB / "verify" / "local-clock" / "stub-claude.sh"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader, path
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def fx():
    return _load(FIXTURE, "derived_forecast_fixture")


@pytest.fixture(scope="module")
def validator():
    return _load(VALIDATOR, "validate_forecast")


@pytest.fixture()
def estate(fx, tmp_path: Path) -> Path:
    """A throwaway feeds publisher and a throwaway adopter with a bare origin: the served
    artefact is origin/main, the same way verify-local-clock.sh builds its fixture."""
    return fx.build(tmp_path / "estate")


def _roles() -> set[str]:
    register = yaml.safe_load((HUB / "twin" / "roles.yaml").read_text())
    return {str(r["id"]) for r in register["roles"]}


# --- the artefact and its validator --------------------------------------------------------
def test_the_worked_example_validates_against_the_fixture_estate(fx, estate: Path) -> None:
    doc = yaml.safe_load(EXAMPLE.read_text())
    bad = df.validate(doc, _roles(), headless=True, adopter_root=estate / "driftwood",
                      feeds_root=estate / "feeds")
    assert bad == [], bad


def test_every_probability_carries_perspective_currency_basis_and_the_allowed_grade(fx, estate: Path) -> None:
    doc = fx.forecast_doc()
    derived = [f for f in doc["forecasts"] if f["basis"] == "derived"]
    recorded = [f for f in doc["forecasts"] if f["basis"] == "recorded"]
    assert derived and recorded
    for f in doc["forecasts"]:
        assert f["perspective"] == "driftwood" and f["currency"] == "GBP"
        assert 0.0 < f["probability"] < 1.0
        assert f["price_eligible"] is False
    assert all(f["evidence_grade"] == df.DERIVED_GRADE for f in derived)
    # the world-model schema forbids a grade on a belief: the artefact says so rather than
    # inventing a rung -- `null`, with the reason, and the validator requires exactly that
    assert all(f["evidence_grade"] is None and f["grade_absent_because"] for f in recorded)
    doc["forecasts"][1]["evidence_grade"] = 4
    bad = df.validate(doc, _roles(), headless=True, adopter_root=estate / "driftwood",
                      feeds_root=estate / "feeds")
    assert any("recorded belief" in b and "grade" in b for b in bad), bad


@pytest.mark.parametrize("mutate, phrase", [
    (lambda f: f.__setitem__("probability", 1.0), "strictly between 0 and 1"),
    (lambda f: f.__setitem__("probability", 0.0), "strictly between 0 and 1"),
    (lambda f: f.__delitem__("perspective"), "perspective"),
    (lambda f: f.__setitem__("currency", "pounds"), "currency"),
    (lambda f: f.__setitem__("price_eligible", True), "never prices"),
    (lambda f: f.__setitem__("evidence_grade", 2), "weakest"),
    (lambda f: f.__setitem__("basis", "guessed"), "basis"),
    (lambda f: f.__setitem__("resolves_on", "2099-01-01"), "horizon"),
    (lambda f: f["signals"].__delitem__(0) or f["signals"].clear(), "no signal"),
    (lambda f: f["signals"][0].__setitem__("weight", 0.7), "ordinal"),
    (lambda f: f["signals"][0].__setitem__("probability", 0.45), "level"),
    (lambda f: f["signals"][0].__setitem__("to_level", 0.99), "does not carry"),
    (lambda f: f["signals"][0].__setitem__("evidence_grade", 1), "grade 5"),
    (lambda f: f.__setitem__("recorded_belief", {"world_model": "reference-map", "probability": 0.9}), "recorded belief"),
])
def test_the_validator_refuses_each_way_a_derived_probability_can_lie(fx, estate: Path, mutate, phrase) -> None:
    doc = fx.forecast_doc()
    mutate(doc["forecasts"][0])
    bad = df.validate(doc, _roles(), headless=True, adopter_root=estate / "driftwood",
                      feeds_root=estate / "feeds")
    assert any(phrase in b for b in bad), (phrase, bad)


def test_a_recorded_belief_is_the_number_read_from_the_world_model_unchanged(fx, estate: Path) -> None:
    doc = fx.forecast_doc()
    rec = next(f for f in doc["forecasts"] if f["basis"] == "recorded")
    rec["probability"] = rec["probability"] + 0.05
    bad = df.validate(doc, _roles(), headless=True, adopter_root=estate / "driftwood",
                      feeds_root=estate / "feeds")
    assert any("recorded" in b and "unchanged" in b for b in bad), bad
    rec["probability"] -= 0.05
    rec["signals"] = list(doc["forecasts"][0]["signals"])
    bad = df.validate(doc, _roles(), headless=True, adopter_root=estate / "driftwood",
                      feeds_root=estate / "feeds")
    assert any("recorded" in b and "signal" in b for b in bad), bad


def test_headless_and_injected_rules_are_the_clocks_not_the_files(fx, estate: Path) -> None:
    doc = fx.forecast_doc()
    del doc["run"]["headless"]
    bad = df.validate(doc, _roles(), headless=True, adopter_root=estate / "driftwood",
                      feeds_root=estate / "feeds")
    assert any("run.headless" in b for b in bad), bad
    assert df.validate(doc, _roles(), headless=False, adopter_root=estate / "driftwood",
                       feeds_root=estate / "feeds") == []
    doc = fx.forecast_doc()
    doc["injected"] = True
    bad = df.validate(doc, _roles(), headless=True, adopter_root=estate / "driftwood",
                      feeds_root=estate / "feeds")
    assert any("rehearsal" in b for b in bad), bad


def test_the_validator_cannot_look_without_the_feeds_and_says_so(fx, estate: Path) -> None:
    doc = fx.forecast_doc()
    with pytest.raises(df.CannotLook):
        df.validate(doc, _roles(), headless=True, adopter_root=estate / "driftwood",
                    feeds_root=estate / "no-feeds")


def test_the_validator_cli_finds_the_adopter_from_the_file_path(fx, estate: Path, tmp_path: Path) -> None:
    doc = fx.forecast_doc()
    target = estate / "driftwood" / "twin" / "forecasts" / "2026-02-01-fixture.forecast.yaml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(yaml.safe_dump(doc, sort_keys=False))
    env = {**os.environ, "LOCAL_CLOCK_ESTATE": str(estate)}
    env.pop("TWIN_FEEDS_ROOT", None)
    run = subprocess.run([sys.executable, str(VALIDATOR), str(target), "--twin", str(HUB), "--headless"],
                         capture_output=True, text=True, env=env)
    assert run.returncode == 0, run.stdout + run.stderr
    assert "1 derived" in run.stdout and "1 recorded" in run.stdout, run.stdout
    run = subprocess.run([sys.executable, str(VALIDATOR), str(target), "--twin", str(HUB), "--headless",
                          "--feeds", str(estate / "absent")], capture_output=True, text=True, env=env)
    assert run.returncode == 2 and "SKIP:" in run.stdout, run.stdout + run.stderr


# --- inputs: what the model reads is a deterministic listing, not its own reading of the feeds --
def test_inputs_lists_scenarios_recorded_beliefs_and_the_pool_as_moves_never_levels(fx, estate: Path) -> None:
    listing = df.inputs(estate / "driftwood", "driftwood", estate / "feeds")
    assert [s["id"] for s in listing["scenarios"]] == ["fixture-quiet-2026", "fixture-supply-2026"]
    assert listing["scenarios"][1]["recorded_beliefs"] == {"reference-map": 0.2}
    moves = listing["pool"]["market-moves"]["moves"]
    assert moves and all({"from_level", "to_level", "from_date", "to_date", "statement"} <= set(m) for m in moves)
    assert not any("probability" in m for m in moves)
    assert listing["pool"]["news"]["events"][0]["url"].startswith("https://")
    assert listing["subscribed"] == {"market-moves": False, "news": False}


# --- pre-registration is git history ---------------------------------------------------------
def test_pre_registration_is_the_first_parent_arrival_on_the_served_ref(fx, estate: Path) -> None:
    repo = estate / "driftwood"
    path = "twin/forecasts/2026-02-01-fixture.forecast.yaml"
    reached = df.first_reached(repo, path, "refs/remotes/origin/main")
    assert reached is not None and reached[0].startswith("2026-02-01"), reached
    assert df.pre_registered(reached[0], "2026-06-30") is True
    assert df.pre_registered(reached[0], "2026-02-01") is False
    assert df.pre_registered("2026-06-30T00:00:00+00:00", "2026-06-30") is False


def test_a_late_merge_is_not_pre_registered_whatever_the_file_says(fx, estate: Path) -> None:
    """The branch commit is dated before the horizon; the MERGE that brought it onto main is
    after. The served ref's first-parent history says late, and the file's own `run_at`
    says early -- the check believes the history."""
    repo = estate / "driftwood"
    late = fx.merge_late_forecast(estate)
    reached = df.first_reached(repo, late, "refs/remotes/origin/main")
    assert reached is not None and reached[0].startswith("2026-07-15"), reached
    assert df.pre_registered(reached[0], "2026-06-30") is False


# --- scoring is the twin's own rule, computed, never read ------------------------------------
def test_the_score_is_twin_scoring_and_the_outcome_is_the_overlays_own_record(fx, estate: Path) -> None:
    doc = fx.forecast_doc()
    outcome = fx.outcome_doc()
    scored = df.score(doc["forecasts"][0], outcome)
    assert scored == scoring.score(doc["forecasts"][0]["probability"], outcome["observed"])
    assert set(scored) == set(scoring.RULES)


def test_check_scores_the_fixture_and_prints_the_history_it_read(fx, estate: Path, capsys) -> None:
    rc = df.check(str(estate), str(HUB), adopters=["driftwood"], now="2026-09-06T00:00:00Z")
    out = capsys.readouterr().out
    assert rc == 0, out
    assert "pre-registered: yes" in out and "brier=" in out and "log_loss=" in out, out
    assert "recorded belief" in out and "carries no grade" in out, out
    assert "0 of 1 adopter(s) pin" in out, out
    assert out.strip().splitlines()[-1].startswith("PASS:"), out


def test_check_waits_when_no_forecast_has_reached_main_and_fails_when_one_is_late(fx, tmp_path: Path, capsys) -> None:
    estate = fx.build(tmp_path / "estate", with_forecast=False, with_outcome=False)
    rc = df.check(str(estate), str(HUB), adopters=["driftwood"], now="2026-09-06T00:00:00Z")
    out = capsys.readouterr().out
    assert rc == 3 and out.strip().splitlines()[-1].startswith("SKIP: no *.forecast.yaml"), out
    fx.merge_late_forecast(estate)
    rc = df.check(str(estate), str(HUB), adopters=["driftwood"], now="2026-09-06T00:00:00Z")
    out = capsys.readouterr().out
    assert rc == 1 and "not pre-registered" in out and out.strip().splitlines()[-1].startswith("FAIL:"), out


def test_check_waits_for_the_outcome_date_and_then_for_the_outcome(fx, tmp_path: Path, capsys) -> None:
    estate = fx.build(tmp_path / "estate", with_outcome=False)
    rc = df.check(str(estate), str(HUB), adopters=["driftwood"], now="2026-03-01T00:00:00Z")
    out = capsys.readouterr().out
    assert rc == 3 and "has passed its outcome date" in out.strip().splitlines()[-1], out
    rc = df.check(str(estate), str(HUB), adopters=["driftwood"], now="2026-09-06T00:00:00Z")
    out = capsys.readouterr().out
    assert rc == 3 and "no outcome in" in out.strip().splitlines()[-1], out


def test_an_outcome_recorded_before_its_own_resolution_date_fails(fx, tmp_path: Path, capsys) -> None:
    estate = fx.build(tmp_path / "estate", outcome_committed="2026-06-01T00:00:00+00:00")
    rc = df.check(str(estate), str(HUB), adopters=["driftwood"], now="2026-09-06T00:00:00Z")
    out = capsys.readouterr().out
    assert rc == 1 and "before the date it says it resolved" in out, out


# --- the clock's derive row, end to end with a stand-in ---------------------------------------
def _clock(estate: Path, home: Path, stub: str, extra: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("LOCAL_CLOCK_")}
    env.update({
        "LOCAL_CLOCK_CLAUDE": str(STUB), "LOCAL_CLOCK_HOME": str(home), "LOCAL_CLOCK_ESTATE": str(estate),
        "LOCAL_CLOCK_PYTHON": sys.executable, "LOCAL_CLOCK_STUB": stub,
    })
    env.pop("LOCAL_CLOCK_LAUNCHD", None)
    env.update(extra or {})
    return subprocess.run(["bash", str(CLOCK), "--adopter", "driftwood", "--step", "derive"],
                          capture_output=True, text=True, env=env, cwd=str(HUB))


def test_the_derive_row_names_its_path_pattern_and_validator() -> None:
    rows = subprocess.run(["bash", str(CLOCK), "--list-steps"], capture_output=True, text=True, cwd=str(HUB)).stdout
    derive = next(line for line in rows.splitlines() if line.startswith("derive "))
    assert "twin/forecasts" in derive and "*.forecast.yaml" in derive and "assets/validate_forecast.py" in derive, derive
    assert "twin/orgs/" not in derive, "a forecasts/ directory under the overlay is refused by Overlay.load"


def test_the_clock_runs_the_derive_row_and_validates_the_forecast(fx, tmp_path: Path) -> None:
    estate = fx.build(tmp_path / "estate", with_forecast=False, with_outcome=False)
    run = _clock(estate, tmp_path / ".local-clock", "forecast")
    assert run.returncode == 0, run.stdout + run.stderr
    assert "ok    derive-driftwood:" in run.stdout and "1 derived" in run.stdout, run.stdout
    branch = subprocess.run(["git", "-C", str(estate / "driftwood"), "for-each-ref", "--format=%(refname:short)",
                             "refs/heads/local-clock/derive-*"], capture_output=True, text=True).stdout.strip()
    assert branch, run.stdout
    changed = subprocess.run(["git", "-C", str(estate / "driftwood"), "diff", "--name-only", f"origin/main...{branch}"],
                             capture_output=True, text=True).stdout.split()
    assert changed and all(c.startswith("twin/forecasts/") and c.endswith(".forecast.yaml") for c in changed), changed
    steps = [json.loads(line) for line in (tmp_path / ".local-clock" / "runs").glob("*/steps.jsonl").__next__().read_text().splitlines()]
    assert [s["status"] for s in steps] == ["ok"], steps


def test_the_clock_refuses_a_forecast_citing_an_observation_the_feed_does_not_carry(fx, tmp_path: Path) -> None:
    estate = fx.build(tmp_path / "estate", with_forecast=False, with_outcome=False)
    run = _clock(estate, tmp_path / ".local-clock", "forecast-fabricated")
    assert run.returncode != 0, run.stdout
    assert "fail  derive-driftwood:" in run.stdout and "does not carry" in run.stdout, run.stdout
    branch = subprocess.run(["git", "-C", str(estate / "driftwood"), "for-each-ref", "refs/heads/local-clock/derive-*"],
                            capture_output=True, text=True).stdout
    assert branch, "the refused forecast's branch was not kept for inspection"


def test_a_rehearsal_forecast_is_marked_and_refused(fx, tmp_path: Path) -> None:
    estate = fx.build(tmp_path / "estate", with_forecast=False, with_outcome=False)
    signal = tmp_path / "signal.yaml"
    signal.write_text(yaml.safe_dump({"date": "2026-09-06", "kind": "headline", "statement": "rehearsal", "source": "x"}))
    env = {k: v for k, v in os.environ.items() if not k.startswith("LOCAL_CLOCK_")}
    env.update({"LOCAL_CLOCK_CLAUDE": str(STUB), "LOCAL_CLOCK_HOME": str(tmp_path / ".local-clock"),
                "LOCAL_CLOCK_ESTATE": str(estate), "LOCAL_CLOCK_PYTHON": sys.executable,
                "LOCAL_CLOCK_STUB": "forecast"})
    run = subprocess.run(["bash", str(CLOCK), "--adopter", "driftwood", "--step", "derive", "--inject", str(signal)],
                         capture_output=True, text=True, env=env, cwd=str(HUB))
    assert run.returncode == 0, run.stdout + run.stderr
    assert "is marked injected and the validator refused it" in run.stdout, run.stdout
