"""The local clock (ecosystem ticket 92): the model-backed half of the eco-system's clock, run
from the owner's machine.

Four seams, all pure code, none needing a token or a network:

  * the world-simulator envelope: an injected signal is stamped `injected: true` with its
    provenance, and the stamp REFUSES to write anywhere but the clock's own run root;
  * the twin refuses an injected envelope outright (`twin.feed_signal.signal_for`), so a
    rehearsal can never become a grade-5 signal by lookup;
  * the dated marker the last run leaves, and how the gate grades it (fresh, stale, absent);
  * the launchd template holds no credential and logs only under the ignored run root, and the
    README's flags are the script's flags.
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
import os
import plistlib
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from twin import feed_signal

HUB = Path(__file__).resolve().parents[1]
CLOCK = HUB / "talk" / "local-clock.sh"
README = HUB / "talk" / "local-clock.README.md"
PLIST = HUB / "talk" / "local-clock.plist"
HELPER = HUB / "verify" / "local-clock" / "local_clock.py"
VALIDATOR = HUB / ".claude" / "skills" / "classify-and-judge" / "assets" / "validate_claim.py"


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader, path
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def lc():
    return _load(HELPER, "local_clock")


@pytest.fixture(scope="module")
def validator():
    return _load(VALIDATOR, "validate_claim")


SIGNAL = {
    "date": "2026-09-03",
    "kind": "headline",
    "statement": "A rehearsal headline: the niobium supply shock from driftwood's own scenario library.",
    "source": "twin/orgs/driftwood/scenarios/niobium-supply-shock-2026.yaml",
}


# --- the world simulator ---------------------------------------------------------------------
def test_stamp_marks_the_envelope_injected_with_its_provenance(lc, tmp_path: Path) -> None:
    root = tmp_path / ".local-clock"
    src = tmp_path / "signal.yaml"
    src.write_text(yaml.safe_dump(SIGNAL))
    out = root / "runs" / "r1" / "injected-signal.json"
    doc = lc.stamp(str(src), str(out), root=str(root), by="test", now="2026-09-03T10:00:00Z")
    assert doc["injected"] is True
    assert doc["injected_at"] == "2026-09-03T10:00:00Z"
    assert doc["injected_by"] == "test"
    assert doc["injected_from"].endswith("signal.yaml")
    assert doc["statement"] == SIGNAL["statement"] and doc["date"] == "2026-09-03"
    assert json.loads(out.read_text())["injected"] is True


def test_stamp_refuses_to_write_outside_the_run_root(lc, tmp_path: Path) -> None:
    root = tmp_path / ".local-clock"
    src = tmp_path / "signal.yaml"
    src.write_text(yaml.safe_dump(SIGNAL))
    for citable in ("observations/x.jsonl", "twin/claims/2026-09-03-x.claim.yaml", "talk/captures/x.out"):
        with pytest.raises(lc.LocalClockError, match="citable|run root"):
            lc.stamp(str(src), str(tmp_path / citable), root=str(root), by="test")
    assert not (tmp_path / "observations").exists()


def test_stamp_refuses_an_undated_signal(lc, tmp_path: Path) -> None:
    root = tmp_path / ".local-clock"
    src = tmp_path / "signal.yaml"
    src.write_text(yaml.safe_dump({**SIGNAL, "date": "yesterday"}))
    with pytest.raises(lc.LocalClockError, match="date"):
        lc.stamp(str(src), str(root / "runs" / "r" / "s.json"), root=str(root), by="test")


def test_feed_signal_refuses_an_injected_envelope() -> None:
    envelope = {
        "kind": "feed", "name": "penalty-schema", "version": "3.0.0", "published_by": "ico",
        "published_at": "2026-09-03T00:00:00Z", "payload": {}, "injected": True,
    }
    with pytest.raises(feed_signal.FeedSignalError, match="injected"):
        feed_signal.signal_for(envelope, tag="v3.0.0", commit="a" * 40)
    # the same envelope with the stamp removed is looked up as ever
    clean = {k: v for k, v in envelope.items() if k != "injected"}
    assert feed_signal.signal_for(clean, tag="v3.0.0", commit="a" * 40)["steep"] == "political"


# --- the marker ------------------------------------------------------------------------------
def _marker(**over):
    base = {
        "ran_at": "2026-09-03T06:00:00Z", "scheduled": True, "period_hours": 24,
        "mode": "live", "injected": False, "hub_commit": "abc1234", "run_dir": "/x",
        "steps": [{"step": "classify", "adopter": "driftwood", "status": "ok"}],
    }
    base.update(over)
    return base


def test_marker_fresh_scheduled_run_passes(lc) -> None:
    now = dt.datetime(2026, 9, 3, 12, tzinfo=dt.timezone.utc)
    status, _ = lc.marker_verdict(_marker(), now)
    assert status == "PASS"


def test_marker_stale_scheduled_run_fails_past_period_plus_slack(lc) -> None:
    now = dt.datetime(2026, 9, 6, 12, tzinfo=dt.timezone.utc)      # 78h later, window is 24+24
    status, reason = lc.marker_verdict(_marker(), now)
    assert status == "FAIL" and "stopped" in reason


def test_marker_hand_run_is_never_graded_stale(lc) -> None:
    now = dt.datetime(2026, 10, 1, tzinfo=dt.timezone.utc)
    status, reason = lc.marker_verdict(_marker(scheduled=False), now)
    assert status == "PASS" and "by hand" in reason


def test_marker_missing_or_undated_is_could_not_look(lc) -> None:
    now = dt.datetime(2026, 9, 3, tzinfo=dt.timezone.utc)
    assert lc.marker_verdict(None, now)[0] == "SKIP"
    assert lc.marker_verdict(_marker(ran_at="soon"), now)[0] == "FAIL"


def test_marker_of_a_rehearsal_says_so_and_is_not_a_live_run(lc) -> None:
    now = dt.datetime(2026, 9, 3, 12, tzinfo=dt.timezone.utc)
    status, reason = lc.marker_verdict(_marker(mode="rehearsal", injected=True), now)
    assert status == "PASS" and "rehearsal" in reason


# --- no injected signal reaches a citable path ---------------------------------------------
def test_leak_scan_finds_an_injected_flag_in_a_committed_observation(lc, tmp_path: Path) -> None:
    repo = tmp_path / "unit"
    (repo / "observations").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    (repo / "observations" / "twin-sweep.jsonl").write_text(
        '{"swept_at": "2026-09-03T07:05:00Z", "org": "driftwood", "injected": true}\n')
    (repo / "notes.md").write_text("injected: true -- prose is not an envelope\n")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t",
                    "commit", "-q", "-m", "x"], check=True)
    hits = lc.injected_leaks(str(repo))
    assert hits == ["observations/twin-sweep.jsonl"], hits


def test_leak_scan_ignores_an_uncommitted_rehearsal_file(lc, tmp_path: Path) -> None:
    repo = tmp_path / "unit"
    (repo / "twin" / "claims").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    (repo / "twin" / "claims" / "2026-09-03-rehearsal.claim.yaml").write_text("injected: true\n")
    assert lc.injected_leaks(str(repo)) == []


def test_truth_log_carries_no_local_run_since_the_local_clock_existed(lc, tmp_path: Path) -> None:
    log = tmp_path / "truth.log"
    log.write_text(
        "TRUTH 2026-08-28T04:00Z run=local hub=2326f31 pass=40 fail=16\n"
        "TRUTH 2026-09-03T10:24Z run=22 hub=14cc731 pass=57 fail=7\n")
    assert lc.local_truth_lines(str(log)) == []
    log.write_text(log.read_text() + "TRUTH 2026-09-04T01:00Z run=local hub=deadbee pass=1 fail=0\n")
    assert len(lc.local_truth_lines(str(log))) == 1


def test_a_repo_that_cannot_be_listed_is_not_clean_it_is_unscanned(lc, tmp_path: Path) -> None:
    # absence is never a pass: git ls-files failing means could-not-look, not "no leak"
    assert lc.injected_leaks(str(tmp_path / "no-such-repo")) is None
    broken = tmp_path / "broken"
    (broken / ".git").mkdir(parents=True)          # looks like a checkout, is not one
    assert lc.injected_leaks(str(broken)) is None


def test_an_absent_truth_log_is_not_clean_it_is_unread(lc, tmp_path: Path) -> None:
    assert lc.local_truth_lines(str(tmp_path / "truth.log")) is None


def test_check_surfaces_an_unscannable_unit_as_skip(lc, tmp_path: Path, capsys) -> None:
    estate = tmp_path / "estate"
    (estate / "broken" / ".git").mkdir(parents=True)
    rc = lc.check(str(HUB), str(tmp_path / ".local-clock"), str(estate))
    lines = capsys.readouterr().out.splitlines()
    assert rc == 3
    assert any(l.startswith("SKIP:") and "broken" in l and "not scanned" in l for l in lines), lines
    assert not any(l.startswith("FAIL:") for l in lines), lines


# --- the script: two runs in one second do not collide, and a run that proposes nothing leaves nothing
STUB = HUB / "verify" / "local-clock" / "stub-claude.sh"


def _fixture_adopter(unit: Path) -> None:
    (unit / "twin").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(unit)], check=True)
    (unit / "twin" / "signals.yaml").write_text("org: driftwood\n")
    subprocess.run(["git", "-C", str(unit), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(unit), "-c", "user.name=f", "-c", "user.email=f@f",
                    "commit", "-q", "-m", "fixture"], check=True)


def test_two_runs_in_the_same_second_get_distinct_ids_and_clean_up_after_themselves(tmp_path: Path) -> None:
    unit = tmp_path / "estate" / "driftwood"
    _fixture_adopter(unit)
    # a `date` shim pins the stamp, so the two runs collide on the second by construction
    shim = tmp_path / "bin"
    shim.mkdir()
    (shim / "date").write_text('#!/bin/sh\ncase "$*" in *%Y%m%dT%H%M%SZ*) echo 20260904T101500Z;; *) exec /bin/date "$@";; esac\n')
    (shim / "date").chmod(0o755)
    home = tmp_path / ".local-clock"
    env = {**os.environ, "PATH": f"{shim}:{os.environ['PATH']}",
           "LOCAL_CLOCK_CLAUDE": str(STUB), "LOCAL_CLOCK_HOME": str(home),
           "LOCAL_CLOCK_ESTATE": str(tmp_path / "estate"), "LOCAL_CLOCK_PYTHON": sys.executable,
           "LOCAL_CLOCK_STUB": "nothing"}
    env.pop("LOCAL_CLOCK_LAUNCHD", None)

    def clock(*args: str) -> subprocess.CompletedProcess:
        return subprocess.run(["bash", str(CLOCK), "--adopter", "driftwood", "--step", "classify", *args],
                              env=env, capture_output=True, text=True, timeout=120)

    runs = [clock(), clock(), clock("--dry-run")]
    for done in runs:
        assert done.returncode == 0, done.stdout + done.stderr
    ids = [re.search(r"^local clock: run (\S+) ", d.stdout, re.M).group(1) for d in runs]  # type: ignore[union-attr]
    assert len(set(ids)) == 3 and all(i.startswith("20260904T101500Z") for i in ids), ids
    assert sorted(p.name for p in (home / "runs").iterdir()) == sorted(ids)
    for rid in ids:                                  # one step per run: nothing appended across runs
        assert len((home / "runs" / rid / "steps.jsonl").read_text().splitlines()) == 1, rid
    for done in runs:
        assert "worktree and branch removed" in done.stdout, done.stdout
    # and the removal is a fact, not a sentence: no worktree, no branch, no directory left
    listed = subprocess.run(["git", "-C", str(unit), "worktree", "list", "--porcelain"],
                            capture_output=True, text=True, check=True).stdout
    assert listed.count("worktree ") == 1, listed
    refs = subprocess.run(["git", "-C", str(unit), "for-each-ref", "refs/heads/local-clock/"],
                          capture_output=True, text=True, check=True).stdout
    assert refs == "", refs
    work = unit / ".work" / "local-clock"
    assert not work.exists() or not any(work.iterdir()), list(work.iterdir())


# --- the template and the README -------------------------------------------------------------
def test_plist_holds_no_credential_and_logs_under_the_ignored_root() -> None:
    doc = plistlib.loads(PLIST.read_bytes())
    assert doc["Label"] == "uk.me.cns.pavc.local-clock"
    args = doc["ProgramArguments"]
    assert any(a.endswith("talk/local-clock.sh") for a in args), args
    for key in ("StandardOutPath", "StandardErrorPath"):
        assert "/.local-clock/" in doc[key], (key, doc[key])
    env = doc.get("EnvironmentVariables", {})
    assert env.get("LOCAL_CLOCK_LAUNCHD") == "1"
    text = PLIST.read_text()
    assert not re.search(r"(?i)token|secret|password|api[_-]?key|credential", text), "a credential-shaped word"
    assert "__HUB__" in text and "__HOUR__" in text and "__MINUTE__" in text, "the owner fills these in"
    assert doc["StartCalendarInterval"] == {"Hour": "__HOUR__", "Minute": "__MINUTE__"}


def test_readme_flags_are_the_scripts_flags(lc) -> None:
    help_flags = lc.script_flags(str(CLOCK))
    readme_flags = lc.readme_flags(str(README))
    assert help_flags, "the script prints its flags under --help"
    assert help_flags == readme_flags, (sorted(help_flags ^ readme_flags))


def test_run_root_is_ignored_by_git() -> None:
    rc = subprocess.run(["git", "-C", str(HUB), "check-ignore", "-q", ".local-clock/last-run.json"]).returncode
    assert rc == 0, ".local-clock/ must be gitignored: it is the one place a rehearsal may write"


def test_script_never_writes_the_truth_log() -> None:
    text = CLOCK.read_text()
    assert "truth.log" not in text.replace("never appends talk/truth.log", ""), \
        "the local clock's TRUTH line, if it had one, would not be citable"
    assert "--dangerously-skip-permissions" not in text
    assert "TWIN_ENACT_MODE=operations" in text, "the headless child runs under the refusing mode"


# --- the validator refuses what a rehearsal or a headless run may not claim -----------------
def _claim(**over):
    doc = yaml.safe_load((VALIDATOR.parent / "example-claim.yaml").read_text())
    doc.update(over)
    return doc


def test_validator_refuses_an_injected_claim_file(validator) -> None:
    kinds, roles = validator.twin_facts(str(HUB))
    assert validator.validate(_claim(), kinds, roles) == []
    bad = validator.validate(_claim(injected=True), kinds, roles)
    assert any("injected" in line and "rehearsal" in line for line in bad), bad
    doc = _claim()
    doc["claims"][0]["injected"] = True
    bad = validator.validate(doc, kinds, roles)
    assert any("injected" in line for line in bad), bad


def test_validator_refuses_an_override_from_a_headless_run(validator) -> None:
    kinds, roles = validator.twin_facts(str(HUB))
    doc = _claim()
    doc["run"]["headless"] = True
    doc["run"]["clock"] = "local-clock"
    bad = validator.validate(doc, kinds, roles)
    assert any("override" in line and "headless" in line for line in bad), bad
    doc["claims"] = [c for c in doc["claims"] if c["kind"] != "override"]
    assert validator.validate(doc, kinds, roles) == []
