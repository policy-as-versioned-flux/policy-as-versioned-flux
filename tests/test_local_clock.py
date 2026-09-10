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
import hashlib
import importlib.util
import json
import os
import plistlib
import re
import shutil
import subprocess
import sys
import tempfile
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
    subprocess.run([*GIT, "init", "-q", str(repo)], check=True)
    (repo / "observations" / "twin-sweep.jsonl").write_text(
        '{"swept_at": "2026-09-03T07:05:00Z", "org": "driftwood", "injected": true}\n')
    (repo / "notes.md").write_text("injected: true -- prose is not an envelope\n")
    subprocess.run([*GIT, "-C", str(repo), "add", "-A"], check=True)
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "x")
    hits = lc.injected_leaks(str(repo))
    assert hits == ["observations/twin-sweep.jsonl"], hits


def test_leak_scan_ignores_an_uncommitted_rehearsal_file(lc, tmp_path: Path) -> None:
    repo = tmp_path / "unit"
    (repo / "twin" / "claims").mkdir(parents=True)
    subprocess.run([*GIT, "init", "-q", str(repo)], check=True)
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
    # a .git FILE (a linked worktree's shape) that names nothing is a checkout too: SKIP, not silence
    (estate / "torn").mkdir()
    (estate / "torn" / ".git").write_text("gitdir: /nowhere\n")
    rc = lc.check(str(HUB), str(tmp_path / ".local-clock"), str(estate))
    lines = capsys.readouterr().out.splitlines()
    assert rc == 3
    for name in ("broken", "torn"):
        assert any(l.startswith("SKIP:") and name in l and "not scanned" in l for l in lines), (name, lines)
    assert not any(l.startswith("FAIL:") for l in lines), lines


def test_a_linked_worktree_in_the_estate_is_scanned_like_a_clone(lc, tmp_path: Path, capsys) -> None:
    # .git is a file in a linked worktree; git ls-files works there, so the scan must look
    repo = tmp_path / "unit"
    (repo / "observations").mkdir(parents=True)
    subprocess.run([*GIT, "init", "-q", str(repo)], check=True)
    (repo / "observations" / "twin-sweep.jsonl").write_text('{"injected": true}\n')
    subprocess.run([*GIT, "-C", str(repo), "add", "-A"], check=True)
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "x")
    estate = tmp_path / "estate"
    estate.mkdir()
    (estate / "plain").mkdir()                       # no .git at all: not a repository
    subprocess.run([*GIT, "-C", str(repo), "worktree", "add", "-q", str(estate / "linked"), "-b", "w"],
                   check=True, capture_output=True)
    assert (estate / "linked" / ".git").is_file()
    assert [n for n, _ in lc.estate_repos(str(estate))] == ["linked"]
    rc = lc.check(str(HUB), str(tmp_path / ".local-clock"), str(estate))
    lines = capsys.readouterr().out.splitlines()
    assert rc == 1
    assert any(l.startswith("FAIL:") and "linked" in l and "twin-sweep.jsonl" in l for l in lines), lines


# --- the script: two runs in one second do not collide, and a run that proposes nothing leaves nothing
STUB = HUB / "verify" / "local-clock" / "stub-claude.sh"


# The fixture's own git runs no hook (follow-up R2): the owner's global core.hooksPath runs a
# network secret scan on every commit, and its quota refusal failed this file on 2026-09-06 for
# a reason that was nobody's read-back. The clock under test still reads the real global; only
# the fixture's commands carry this -c.
NO_HOOKS = Path(tempfile.mkdtemp(prefix="local-clock-no-hooks-"))
GIT = ["git", "-c", f"core.hooksPath={NO_HOOKS}"]


def _git(repo: Path, *args: str) -> str:
    # Fixture history must not require the operator's encrypted signing key. Local
    # fixture configuration (including the explicit signing tests below) still applies.
    # Only fixture git receives this environment; the clock keeps reading the real global.
    env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull}
    return subprocess.run([*GIT, "-C", str(repo), *args], capture_output=True, text=True,
                          check=True, env=env).stdout.strip()


def _fixture_adopter(unit: Path, behind: int = 1) -> Path:
    """A throwaway adopter whose `origin` is a throwaway bare repository, with the clone's local
    `main` BEHIND origin/main by `behind` commits -- the state every real clone under
    .estate-clone was in on 2026-09-06 (driftwood 2, tuppence 4, ludlow 1). Returns the origin."""
    (unit / "twin").mkdir(parents=True)
    subprocess.run([*GIT, "init", "-q", "-b", "main", str(unit)], check=True)
    (unit / "twin" / "signals.yaml").write_text("org: driftwood\n")
    _git(unit, "add", "-A")
    _git(unit, "-c", "user.name=f", "-c", "user.email=f@f", "commit", "-q", "-m", "fixture")
    origin = unit.parent / f"{unit.name}.origin.git"
    subprocess.run([*GIT, "init", "-q", "--bare", "-b", "main", str(origin)], check=True)
    _git(unit, "remote", "add", "origin", str(origin))
    for i in range(behind):
        (unit / "twin" / "signals.yaml").write_text(f"org: driftwood\nupstream: {i + 1}\n")
        _git(unit, "-c", "user.name=f", "-c", "user.email=f@f", "commit", "-q", "-am", f"upstream {i + 1}")
    _git(unit, "push", "-q", "-u", "origin", "main")
    _git(unit, "fetch", "-q", "origin")               # FETCH_HEAD exists: the clone has fetched once
    if behind:
        _git(unit, "reset", "-q", "--hard", f"HEAD~{behind}")
    return origin


def _clock_env(tmp_path: Path, stub: str) -> dict[str, str]:
    env = {**os.environ, "LOCAL_CLOCK_CLAUDE": str(STUB), "LOCAL_CLOCK_HOME": str(tmp_path / ".local-clock"),
           "LOCAL_CLOCK_ESTATE": str(tmp_path / "estate"), "LOCAL_CLOCK_PYTHON": sys.executable,
           "LOCAL_CLOCK_STUB": stub}
    env.pop("LOCAL_CLOCK_LAUNCHD", None)
    return env


def test_a_live_claim_without_the_headless_mark_fails_the_step_and_no_body_is_written(tmp_path: Path) -> None:
    # the stub commits the skill's own worked example: an override, no run.headless key. The
    # clock's own read must refuse it; the model's silence about being headless is not consent.
    unit = tmp_path / "estate" / "driftwood"
    _fixture_adopter(unit)
    done = subprocess.run(["bash", str(CLOCK), "--adopter", "driftwood", "--step", "classify"],
                          env=_clock_env(tmp_path, "example"), capture_output=True, text=True, timeout=120)
    assert done.returncode == 1, done.stdout + done.stderr
    fail_lines = [l for l in done.stdout.splitlines() if l.startswith("fail ")]
    assert fail_lines and "headless" in fail_lines[0], done.stdout
    rid = re.search(r"^local clock: run (\S+) ", done.stdout, re.M).group(1)  # type: ignore[union-attr]
    run_dir = tmp_path / ".local-clock" / "runs" / rid
    assert not (run_dir / "classify-driftwood.pr-body.md").exists(), "a body was written for a refused claim"
    steps = [json.loads(l) for l in (run_dir / "steps.jsonl").read_text().splitlines()]
    assert [s["status"] for s in steps] == ["fail"] and "headless" in steps[0]["reason"], steps
    refs = subprocess.run([*GIT, "-C", str(unit), "for-each-ref", "refs/heads/local-clock/"],
                          capture_output=True, text=True, check=True).stdout
    assert rid in refs, "the refused claim's branch is kept for inspection"


PHRASE = "no override is claimed"


def _hub_bytes_that_say_it() -> set[str]:
    """The sha of every file the HUB itself carries that says the phrase. Measured 2026-09-09:
    exactly one, .claude/skills/classify-and-judge/SKILL.md."""
    out = set()
    for base in (HUB / "twin", HUB / ".claude" / "skills"):
        for p in base.rglob("*"):
            if p.is_file() and PHRASE in p.read_text(errors="replace").lower():
                out.add(hashlib.sha256(p.read_bytes()).hexdigest())
    assert out, "no hub file carries the phrase, so the exemption below would prove nothing"
    return out


def _says_no_override(run_dir: Path) -> list[Path]:
    """Every file under `run_dir` that says the phrase and whose BYTES the hub does not carry.

    The exemption is DERIVED, not inferred from a filename: the clock's judge copy is a verbatim
    copy of the hub's twin package and skill, so its bytes ARE the hub's. A file that merely sits
    in a directory called `.judge`, or is called `.judge`, is not (ticket 93 review G1).
    """
    hub = _hub_bytes_that_say_it()
    said = []
    for p in sorted(run_dir.rglob("*")):
        if not p.is_file() or p.name.endswith((".system.md", ".claude.json", ".claude.err")):
            continue
        if PHRASE not in p.read_text(errors="replace").lower():
            continue
        if hashlib.sha256(p.read_bytes()).hexdigest() in hub:
            continue
        said.append(p)
    return said


def test_a_file_under_the_claims_path_that_is_not_a_claim_fails_the_step_unchecked(tmp_path: Path) -> None:
    # the stub commits the same worked example as twin/claims/<date>-probe-classify.yaml (not a
    # *.claim.yaml) and writes its own PR title and body saying no override is claimed. The
    # validator never sees a file with that name, so the clock must refuse it outright rather
    # than let it through with zero checks; and the model's own title and body must not survive
    unit = tmp_path / "estate" / "driftwood"
    _fixture_adopter(unit)
    done = subprocess.run(["bash", str(CLOCK), "--adopter", "driftwood", "--step", "classify"],
                          env=_clock_env(tmp_path, "misnamed"), capture_output=True, text=True, timeout=120)
    assert done.returncode == 1, done.stdout + done.stderr
    fail_lines = [l for l in done.stdout.splitlines() if l.startswith("fail ")]
    assert fail_lines and "is not a *.claim.yaml" in fail_lines[0] and "probe-classify.yaml" in fail_lines[0], done.stdout
    rid = re.search(r"^local clock: run (\S+) ", done.stdout, re.M).group(1)  # type: ignore[union-attr]
    run_dir = tmp_path / ".local-clock" / "runs" / rid
    assert not (run_dir / "classify-driftwood.pr-body.md").exists(), "the model's body survived the refusal"
    assert not (run_dir / "classify-driftwood.pr-title").exists(), "the model's title survived the refusal"
    # the rendered prompt carries the phrase as the instruction to the model, and the transcript
    # is the model's words; every other file in the run directory is the clock's, and none may
    # say it. The judge copy is exempt because it is a VERBATIM COPY of the hub's twin package
    # and the skill, taken before the child so the validator is not the tree the child can write
    # to (ticket 93 review F5) -- and `_says_no_override` DERIVES that from the BYTES rather than
    # inferring it from a filename (review G1). Reading the name let two shapes through, both
    # planted below. verify/local-clock/verify-local-clock.sh reads the same way, deliberately.
    assert _says_no_override(run_dir) == [], _says_no_override(run_dir)
    # red first, both smuggle shapes: a file inside a .judge DIRECTORY and a file NAMED .judge
    (run_dir / "evil.judge").mkdir(exist_ok=True)
    (run_dir / "evil.judge" / "note.md").write_text("no override is claimed\n")
    (run_dir / "sneaky.judge").write_text("no override is claimed\n")
    caught = {p.name for p in _says_no_override(run_dir)}
    assert caught == {"note.md", "sneaky.judge"}, caught
    shutil.rmtree(run_dir / "evil.judge")
    (run_dir / "sneaky.judge").unlink()
    assert _says_no_override(run_dir) == []
    steps = [json.loads(l) for l in (run_dir / "steps.jsonl").read_text().splitlines()]
    assert [s["status"] for s in steps] == ["fail"] and "not a *.claim.yaml" in steps[0]["reason"], steps
    refs = subprocess.run([*GIT, "-C", str(unit), "for-each-ref", "refs/heads/local-clock/"],
                          capture_output=True, text=True, check=True).stdout
    assert rid in refs, "the refused file's branch is kept for inspection"
    # and a well-formed claim beside it is still validated: the whole step fails, not just the file
    assert not any("all in the twin" in l for l in done.stdout.splitlines()), done.stdout


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
    listed = subprocess.run([*GIT, "-C", str(unit), "worktree", "list", "--porcelain"],
                            capture_output=True, text=True, check=True).stdout
    assert listed.count("worktree ") == 1, listed
    refs = subprocess.run([*GIT, "-C", str(unit), "for-each-ref", "refs/heads/local-clock/"],
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
    rc = subprocess.run([*GIT, "-C", str(HUB), "check-ignore", "-q", ".local-clock/last-run.json"]).returncode
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


def test_validator_told_headless_does_not_trust_the_files_own_word(validator) -> None:
    # the worked example: a human-run file, an override, no run.headless key. Believed on its
    # own terms it passes; told by the clock that the run was headless, it fails for both reasons
    kinds, roles = validator.twin_facts(str(HUB))
    doc = _claim()
    assert "headless" not in doc["run"]
    assert validator.validate(doc, kinds, roles) == []
    bad = validator.validate(doc, kinds, roles, headless=True)
    assert any("run.headless" in line for line in bad), bad
    assert any("override from a headless run" in line for line in bad), bad
    # headless: false written by the model is still not the clock's fact
    doc["run"]["headless"] = False
    bad = validator.validate(doc, kinds, roles, headless=True)
    assert any("run.headless is False" in line for line in bad), bad
    # a file that says headless and claims no override passes under --headless
    doc["run"]["headless"] = True
    doc["claims"] = [c for c in doc["claims"] if c["kind"] != "override"]
    assert validator.validate(doc, kinds, roles, headless=True) == []


def test_validator_cli_headless_flag_refuses_the_worked_example(tmp_path: Path) -> None:
    example = VALIDATOR.parent / "example-claim.yaml"
    plain = subprocess.run([sys.executable, str(VALIDATOR), str(example), "--twin", str(HUB)],
                           capture_output=True, text=True, cwd=str(HUB))
    assert plain.returncode == 0, plain.stdout + plain.stderr
    headless = subprocess.run([sys.executable, str(VALIDATOR), str(example), "--twin", str(HUB), "--headless"],
                              capture_output=True, text=True, cwd=str(HUB))
    assert headless.returncode == 1, headless.stdout + headless.stderr
    assert "run.headless" in headless.stdout and "override from a headless run" in headless.stdout, headless.stdout


# --- round 4 (2026-09-06): the SERVED artefact and the OPERATION that reaches it -----------
# Ticket 98's rule, applied to this clock. The served artefact of a live step is a branch on the
# adopter's ORIGIN (after --push) whose one commit sits on origin/main, and the pull request that
# names it; the operation is `git push` then `gh pr create`. None of that is proved by a local
# ref existing. These tests run the clock over a throwaway adopter with a throwaway bare origin
# and a stub `gh`, and read the origin.
STUB_GH = HUB / "verify" / "local-clock" / "stub-gh.sh"


def _run_id(stdout: str) -> str:
    return re.search(r"^local clock: run (\S+) ", stdout, re.M).group(1)  # type: ignore[union-attr]


def _push_env(tmp_path: Path, stub: str, gh: str) -> dict[str, str]:
    env = _clock_env(tmp_path, stub)
    env.update({"LOCAL_CLOCK_GH": str(STUB_GH), "LOCAL_CLOCK_GH_STUB": gh,
                "LOCAL_CLOCK_GH_LOG": str(tmp_path / "gh-calls.log")})
    env.pop("CLAUDECODE", None)            # --push is refused inside a session, for another reason
    env.pop("CLAUDE_CODE_CHILD_SESSION", None)
    return env


def test_a_proposal_is_cut_from_origin_main_not_the_clones_stale_main(tmp_path: Path) -> None:
    # every real clone's local main was behind origin/main on 2026-09-06; a proposal cut from
    # local main reads a pool the served artefact has moved past
    unit = tmp_path / "estate" / "driftwood"
    origin = _fixture_adopter(unit, behind=2)
    served = _git(origin, "rev-parse", "main")
    assert _git(unit, "rev-parse", "main") != served
    done = subprocess.run(["bash", str(CLOCK), "--adopter", "driftwood", "--step", "classify"],
                          env=_clock_env(tmp_path, "claim"), capture_output=True, text=True, timeout=120)
    assert done.returncode == 0, done.stdout + done.stderr
    base_line = [l for l in done.stdout.splitlines() if l.startswith("base ")]
    assert base_line and f"origin/main@{served[:7]}" in base_line[0] and "local main 2 behind" in base_line[0], done.stdout
    rid = _run_id(done.stdout)
    branch = f"local-clock/classify-{rid}"
    assert _git(unit, "rev-parse", f"{branch}~1") == served, "the proposal's parent is the served tip"
    steps = [json.loads(l) for l in (tmp_path / ".local-clock" / "runs" / rid / "steps.jsonl").read_text().splitlines()]
    assert steps[0]["base"] == served, steps[0]
    assert _git(unit, "rev-parse", "main") != served, "the clock does not move the clone's own main either"


def test_the_push_preflight_refuses_before_any_model_runs_when_gh_cannot_answer(tmp_path: Path) -> None:
    # ADR-0020: a missing instrument refuses. With --push the instruments are an authenticated
    # gh and a reachable origin; the clock establishes both BEFORE it spends a model call
    unit = tmp_path / "estate" / "driftwood"
    _fixture_adopter(unit)
    done = subprocess.run(["bash", str(CLOCK), "--adopter", "driftwood", "--step", "classify", "--push"],
                          env=_push_env(tmp_path, "claim", "unauth"), capture_output=True, text=True, timeout=120)
    assert done.returncode == 2, done.stdout + done.stderr
    assert done.stdout.splitlines()[-1].startswith("FAIL:") and "gh" in done.stdout.splitlines()[-1], done.stdout
    assert not (tmp_path / ".local-clock" / "model-was-called").exists(), "the model ran before the refusal"
    assert not (tmp_path / ".local-clock" / "runs").exists() or not any((tmp_path / ".local-clock" / "runs").iterdir())
    assert _git(unit, "for-each-ref", "refs/heads/local-clock/") == ""


def test_push_lands_the_branch_on_origin_and_moves_nothing_else(tmp_path: Path) -> None:
    unit = tmp_path / "estate" / "driftwood"
    origin = _fixture_adopter(unit)
    served = _git(origin, "rev-parse", "main")
    done = subprocess.run(["bash", str(CLOCK), "--adopter", "driftwood", "--step", "classify", "--push"],
                          env=_push_env(tmp_path, "claim", "ok"), capture_output=True, text=True, timeout=120)
    assert done.returncode == 0, done.stdout + done.stderr
    rid = _run_id(done.stdout)
    branch = f"local-clock/classify-{rid}"
    # the served ref: on the ORIGIN, one commit, parent is origin/main, main unmoved
    on_origin = _git(origin, "rev-parse", "--verify", f"refs/heads/{branch}")
    assert _git(origin, "rev-parse", f"{on_origin}~1") == served
    assert _git(origin, "rev-parse", "main") == served, "the clock moved origin's main"
    assert _git(origin, "diff", "--name-only", f"main..{branch}").startswith("twin/claims/")
    # the operation: gh was asked to open exactly this PR
    calls = (tmp_path / "gh-calls.log").read_text()
    assert f"pr create --repo policy-as-versioned-driftwood/driftwood --base main --head {branch}" in calls, calls
    steps = [json.loads(l) for l in (tmp_path / ".local-clock" / "runs" / rid / "steps.jsonl").read_text().splitlines()]
    assert steps[0]["status"] == "ok" and steps[0]["pr"].startswith("https://"), steps[0]
    # and the local worktree and branch are gone: origin has them
    assert _git(unit, "for-each-ref", "refs/heads/local-clock/") == ""
    assert _git(unit, "worktree", "list", "--porcelain").count("worktree ") == 1


def _signing_key(tmp_path: Path) -> Path:
    if not shutil.which("ssh-keygen"):
        pytest.skip("ssh-keygen is not on PATH: the signing fixture cannot be built")
    key = tmp_path / "throwaway_ed25519"
    subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", "throwaway", "-f", str(key)], check=True)
    return key


def _configure_signing_as_owner(unit: Path, key: Path) -> None:
    # exactly what .estate-clone/<unit>/.git/config carried on 2026-09-06, with a throwaway key
    for k, v in (("user.name", "The Owner"), ("user.email", "owner@fixture.invalid"),
                 ("gpg.format", "ssh"), ("user.signingkey", str(key)), ("commit.gpgsign", "true")):
        _git(unit, "config", k, v)


def _has_signature_block(repo: Path, rev: str) -> bool:
    return any(l.startswith("gpgsig") for l in _git(repo, "cat-file", "commit", rev).splitlines())


def test_a_headless_commit_is_unsigned_and_authored_by_the_clock_even_where_the_clone_signs(tmp_path: Path) -> None:
    # the real clones sign every commit with the owner's SSH key and name the owner as author.
    # A model with nobody at the keyboard must not commit in the owner's name or under the
    # owner's signature: the commit is the clock's, unsigned, and the merge is the human act
    unit = tmp_path / "estate" / "driftwood"
    _fixture_adopter(unit)
    key = _signing_key(tmp_path)
    _configure_signing_as_owner(unit, key)
    _git(unit, "commit", "-q", "--allow-empty", "-m", "control: the clone's own config signs")
    assert _has_signature_block(unit, "HEAD"), "the fixture's config does sign a plain commit"
    assert _git(unit, "log", "-1", "--format=%an", "HEAD") == "The Owner"
    done = subprocess.run(["bash", str(CLOCK), "--adopter", "driftwood", "--step", "classify"],
                          env=_clock_env(tmp_path, "claim"), capture_output=True, text=True, timeout=120)
    assert done.returncode == 0, done.stdout + done.stderr
    rid = _run_id(done.stdout)
    branch = f"local-clock/classify-{rid}"
    assert not _has_signature_block(unit, branch), "the proposal carries a signature it has no right to"
    author = _git(unit, "log", "-1", "--format=%an <%ae>", branch)
    assert "local clock" in author and "The Owner" not in author, author
    assert "signature: none" in done.stdout and "author: local clock" in done.stdout, done.stdout
    steps = [json.loads(l) for l in (tmp_path / ".local-clock" / "runs" / rid / "steps.jsonl").read_text().splitlines()]
    assert steps[0]["signature_block"] is False and "local clock" in steps[0]["author"], steps[0]


def test_a_proposal_that_carries_a_signature_or_the_owners_name_is_refused(tmp_path: Path) -> None:
    unit = tmp_path / "estate" / "driftwood"
    _fixture_adopter(unit)
    key = _signing_key(tmp_path)
    for stub, word in (("signed", "signature"), ("asowner", "author")):
        env = _clock_env(tmp_path, stub)
        env["LOCAL_CLOCK_STUB_KEY"] = str(key)
        done = subprocess.run(["bash", str(CLOCK), "--adopter", "driftwood", "--step", "classify"],
                              env=env, capture_output=True, text=True, timeout=120)
        assert done.returncode == 1, (stub, done.stdout + done.stderr)
        fail_lines = [l for l in done.stdout.splitlines() if l.startswith("fail ")]
        assert fail_lines and word in fail_lines[0], (stub, done.stdout)
        rid = _run_id(done.stdout)
        assert rid in _git(unit, "for-each-ref", "refs/heads/local-clock/"), "branch kept for inspection"
        assert not (tmp_path / ".local-clock" / "runs" / rid / "classify-driftwood.pr-body.md").exists()


# --- round 4: the leak scan reads refs, and its limits are numbers ---------------------------
def _commit_injected_on(repo: Path, branch: str, path: str, base: str = "main") -> None:
    _git(repo, "checkout", "-q", "-b", branch, base)
    (repo / path).parent.mkdir(parents=True, exist_ok=True)
    (repo / path).write_text("injected: true\nschema: twin.headline-claim/v1\n")
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", f"injected on {branch}")
    _git(repo, "checkout", "-q", base)


def test_leak_scan_reads_the_committed_tree_of_a_ref_not_the_working_tree(lc, tmp_path: Path) -> None:
    repo = tmp_path / "unit"
    (repo / "observations").mkdir(parents=True)
    subprocess.run([*GIT, "init", "-q", "-b", "main", str(repo)], check=True)
    (repo / "observations" / "x.jsonl").write_text('{"injected": false}\n')
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "clean")
    (repo / "observations" / "x.jsonl").write_text('{"injected": true}\n')     # tracked, modified, uncommitted
    assert lc.injected_leaks(str(repo)) == [], "the working tree is not the committed tree"
    _git(repo, "checkout", "-q", "--", "observations/x.jsonl")
    _commit_injected_on(repo, "local-clock/rehearsal/classify-r1", "twin/claims/2026-09-06-r.claim.yaml")
    assert lc.injected_leaks(str(repo), "refs/heads/local-clock/rehearsal/classify-r1") == ["twin/claims/2026-09-06-r.claim.yaml"]
    assert lc.injected_leaks(str(repo), "HEAD") == []
    assert lc.injected_leaks(str(repo), "refs/heads/no-such-ref") is None


def test_a_live_local_clock_branch_carrying_the_mark_fails_and_a_rehearsal_branch_is_counted(lc, tmp_path: Path, capsys) -> None:
    estate = tmp_path / "estate"
    unit = estate / "driftwood"
    _fixture_adopter(unit, behind=0)
    _commit_injected_on(unit, "local-clock/rehearsal/classify-r1", "twin/claims/2026-09-06-r.claim.yaml")
    rc = lc.check(str(HUB), str(tmp_path / ".local-clock"), str(estate))
    lines = capsys.readouterr().out.splitlines()
    assert rc == 3, lines                                   # only the marker is could-not-look
    assert not any(l.startswith("FAIL:") for l in lines), lines
    assert any("1 rehearsal branch" in l and "by design" in l for l in lines), lines
    # a LIVE local-clock branch carrying the mark means the mark escaped its rehearsal
    _commit_injected_on(unit, "local-clock/classify-l1", "twin/claims/2026-09-06-l.claim.yaml")
    rc = lc.check(str(HUB), str(tmp_path / ".local-clock"), str(estate))
    lines = capsys.readouterr().out.splitlines()
    assert rc == 1
    assert any(l.startswith("FAIL:") and "local-clock/classify-l1" in l for l in lines), lines


def test_the_scan_names_the_served_ref_and_prints_what_it_could_not_see_as_numbers(lc, tmp_path: Path, capsys) -> None:
    estate = tmp_path / "estate"
    unit = estate / "driftwood"
    _fixture_adopter(unit, behind=1)
    scan = lc.scan_repo(str(unit))
    assert scan["HEAD"] == [] and scan["origin/main"] == [], scan
    assert isinstance(scan["fetched_hours_ago"], float) and scan["fetched_hours_ago"] >= 0, scan
    assert scan["branches"] == [], scan
    lc.check(str(HUB), str(tmp_path / ".local-clock"), str(estate))
    lines = capsys.readouterr().out.splitlines()
    summary = [l for l in lines if l.startswith("PASS:") and "origin/main" in l]
    # the hub itself is the second repository with an origin/main
    assert summary and re.search(r"origin/main of 2 ", summary[0]) and re.search(r"updated \d+h ago", summary[0]), lines
    # a unit with no origin/main at all is said so, as a count, never as clean
    lone = estate / "lone"
    (lone / "twin").mkdir(parents=True)
    subprocess.run([*GIT, "init", "-q", "-b", "main", str(lone)], check=True)
    (lone / "twin" / "signals.yaml").write_text("org: lone\n")
    _git(lone, "add", "-A")
    _git(lone, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "x")
    assert lc.scan_repo(str(lone))["origin/main"] is None
    lc.check(str(HUB), str(tmp_path / ".local-clock"), str(estate))
    lines = capsys.readouterr().out.splitlines()
    assert any("1 repository" in l and "no origin/main" in l for l in lines), lines


def test_a_marker_left_by_a_stand_in_model_is_not_the_clock_running(lc) -> None:
    now = dt.datetime(2026, 9, 6, 12, tzinfo=dt.timezone.utc)
    marker = {"ran_at": "2026-09-06T06:00:00Z", "scheduled": True, "period_hours": 24, "steps": [],
              "model": "stub-claude.sh"}
    status, reason = lc.marker_verdict(marker, now)
    assert status == "SKIP" and "stand-in" in reason and "stub-claude.sh" in reason, (status, reason)
    assert lc.marker_verdict({**marker, "model": "claude"}, now)[0] == "PASS"
    # a marker that does not say which binary ran is from before this fact was recorded: dated, graded
    assert lc.marker_verdict({k: v for k, v in marker.items() if k != "model"}, now)[0] == "PASS"


def test_the_steps_table_declares_each_rows_file_pattern_and_validator() -> None:
    # ticket 93's seam: a row says where its files go, what they are named and which validator
    # checks them; a row whose validator is not shipped cannot propose
    done = subprocess.run(["bash", str(CLOCK), "--list-steps"], capture_output=True, text=True, check=True)
    rows = {l.split()[0]: l for l in done.stdout.splitlines() if l.strip()}
    assert set(rows) >= {"classify", "derive"}, rows
    assert "*.claim.yaml" in rows["classify"] and "assets/validate_claim.py" in rows["classify"], rows["classify"]
    assert "{adopter}" not in rows["derive"] or "twin/orgs/" in rows["derive"], rows["derive"]
    assert re.search(r"\*\.\S+\.yaml", rows["derive"]) and "assets/validate_" in rows["derive"], rows["derive"]


# --- round 4 review (2026-09-06): the read-back covers the whole branch, not HEAD -----------
def test_a_branch_whose_history_carries_a_signed_or_owner_commit_is_refused_and_never_pushed(tmp_path: Path) -> None:
    # F1: commit 1 signed and a person's, commit 2 clean as the clock. A read-back of HEAD alone
    # said "unsigned, the clock's" and --push landed BOTH on the origin. Read on the ORIGIN.
    unit = tmp_path / "estate" / "driftwood"
    origin = _fixture_adopter(unit)
    key = _signing_key(tmp_path)
    env = _push_env(tmp_path, "twocommits", "ok")
    env["LOCAL_CLOCK_STUB_KEY"] = str(key)
    done = subprocess.run(["bash", str(CLOCK), "--adopter", "driftwood", "--step", "classify", "--push"],
                          env=env, capture_output=True, text=True, timeout=120)
    assert done.returncode == 1, done.stdout + done.stderr
    fail_lines = [l for l in done.stdout.splitlines() if l.startswith("fail ")]
    assert fail_lines and "2 commit" in fail_lines[0], done.stdout
    assert "signature: none" not in done.stdout, "the clock vouched for a branch it had not read whole"
    assert _git(origin, "for-each-ref", "refs/heads/local-clock/") == "", "the branch reached the origin"
    assert "pr create" not in (tmp_path / "gh-calls.log").read_text() if (tmp_path / "gh-calls.log").exists() else True
    rid = _run_id(done.stdout)
    steps = [json.loads(l) for l in (tmp_path / ".local-clock" / "runs" / rid / "steps.jsonl").read_text().splitlines()]
    assert steps[0]["status"] == "fail" and steps[0]["commits"] == 2 and "signature_block" not in steps[0], steps[0]
    assert rid in _git(unit, "for-each-ref", "refs/heads/local-clock/"), "branch kept for inspection"


def test_a_declaration_hidden_in_history_behind_a_clean_tree_is_refused(tmp_path: Path) -> None:
    # F1, second shape: commit 1 adds composed/x.yaml, commit 2 deletes it; the tree diff shows
    # one claim file and the branch's history carries the declaration
    unit = tmp_path / "estate" / "driftwood"
    _fixture_adopter(unit)
    done = subprocess.run(["bash", str(CLOCK), "--adopter", "driftwood", "--step", "classify"],
                          env=_clock_env(tmp_path, "history"), capture_output=True, text=True, timeout=120)
    assert done.returncode == 1, done.stdout + done.stderr
    fail_lines = [l for l in done.stdout.splitlines() if l.startswith("fail ")]
    assert fail_lines and "2 commit" in fail_lines[0], done.stdout
    assert not any("all in the twin" in l for l in done.stdout.splitlines()), "the validator ran on a refused branch"


def test_a_single_clean_commit_records_its_count_and_sha(tmp_path: Path) -> None:
    unit = tmp_path / "estate" / "driftwood"
    _fixture_adopter(unit)
    done = subprocess.run(["bash", str(CLOCK), "--adopter", "driftwood", "--step", "classify"],
                          env=_clock_env(tmp_path, "claim"), capture_output=True, text=True, timeout=120)
    assert done.returncode == 0, done.stdout + done.stderr
    rid = _run_id(done.stdout)
    steps = [json.loads(l) for l in (tmp_path / ".local-clock" / "runs" / rid / "steps.jsonl").read_text().splitlines()]
    assert steps[0]["commits"] == 1 and steps[0]["commit"] == _git(unit, "rev-parse", f"local-clock/classify-{rid}"), steps[0]
    assert steps[0]["committer"].startswith("local clock"), steps[0]


def test_a_child_that_makes_any_ref_but_its_branch_is_refused_and_the_ref_named(tmp_path: Path) -> None:
    # F2: the guard admits `git tag -a` (and `git update-ref refs/heads/main HEAD`); the owner's
    # global tag.gpgsign would sign the tag with the owner's key. The clock snapshots the unit's
    # refs before the child and refuses any ref that appeared or moved besides its own branch.
    unit = tmp_path / "estate" / "driftwood"
    _fixture_adopter(unit)
    _git(unit, "config", "tag.gpgsign", "true")
    _git(unit, "config", "gpg.format", "ssh")
    _git(unit, "config", "user.signingkey", str(_signing_key(tmp_path)))
    done = subprocess.run(["bash", str(CLOCK), "--adopter", "driftwood", "--step", "classify"],
                          env=_clock_env(tmp_path, "tag"), capture_output=True, text=True, timeout=120)
    assert done.returncode == 1, done.stdout + done.stderr
    fail_lines = [l for l in done.stdout.splitlines() if l.startswith("fail ")]
    assert fail_lines and "refs/tags/local-clock-v1" in fail_lines[0], done.stdout
    # and even the tag the child made is unsigned: tag.gpgsign=false rides in the child's environment
    tag_obj = _git(unit, "cat-file", "tag", "refs/tags/local-clock-v1")
    assert "SSH SIGNATURE" not in tag_obj and "BEGIN" not in tag_obj, tag_obj


def test_a_nested_clock_is_refused_before_anything_starts(tmp_path: Path) -> None:
    # F3: a child of the clock inherits LOCAL_CLOCK_STEP / LOCAL_CLOCK_RUN_DIR; a clock started
    # inside one must refuse, whatever CLAUDECODE says
    unit = tmp_path / "estate" / "driftwood"
    _fixture_adopter(unit)
    env = _clock_env(tmp_path, "claim")
    env["LOCAL_CLOCK_STEP"] = "classify"
    env["LOCAL_CLOCK_RUN_DIR"] = str(tmp_path / "outer-run")
    done = subprocess.run(["bash", str(CLOCK), "--adopter", "driftwood", "--step", "classify"],
                          env=env, capture_output=True, text=True, timeout=120)
    assert done.returncode == 2, done.stdout + done.stderr
    assert done.stdout.splitlines()[-1].startswith("FAIL:") and "nested" in done.stdout.splitlines()[-1], done.stdout
    assert not (tmp_path / ".local-clock" / "runs").exists()
    assert _git(unit, "for-each-ref", "refs/heads/local-clock/") == ""


def test_the_leak_scan_is_case_insensitive(lc, tmp_path: Path) -> None:
    # F5: YAML reads `Injected: True` as the same boolean; the scan must too
    repo = tmp_path / "unit"
    (repo / "twin" / "claims").mkdir(parents=True)
    subprocess.run([*GIT, "init", "-q", "-b", "main", str(repo)], check=True)
    (repo / "twin" / "claims" / "x.claim.yaml").write_text("Injected: True\n")
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "x")
    assert lc.injected_leaks(str(repo)) == ["twin/claims/x.claim.yaml"]
    assert lc._INJECTED.search('{"INJECTED": TRUE}')


# --- round 5 re-review (2026-09-06): three more routes, one shape, read on the ORIGIN ---------
def _push_refused(tmp_path: Path, stub: str, word: str, key: Path | None = None) -> tuple[str, str]:
    unit = tmp_path / "estate" / "driftwood"
    origin = _fixture_adopter(unit)
    env = _push_env(tmp_path, stub, "ok")
    if key is not None:
        env["LOCAL_CLOCK_STUB_KEY"] = str(key)
    done = subprocess.run(["bash", str(CLOCK), "--adopter", "driftwood", "--step", "classify", "--push"],
                          env=env, capture_output=True, text=True, timeout=120)
    assert done.returncode == 1, done.stdout + done.stderr
    fail_lines = [l for l in done.stdout.splitlines() if l.startswith("fail ")]
    assert fail_lines and word in fail_lines[0], done.stdout
    assert "signature: none" not in done.stdout, done.stdout
    assert _git(origin, "for-each-ref", "refs/heads/local-clock/") == "", f"the {stub} branch reached the origin"
    log = tmp_path / "gh-calls.log"
    assert not log.exists() or "pr create" not in log.read_text(), "gh was asked for a PR"
    return done.stdout, _run_id(done.stdout)


def test_a_git_replace_cannot_stand_a_clean_double_before_a_signed_commit(tmp_path: Path) -> None:
    # F1: S signed and a person's, C a clean double, `git replace S C`. Every ordinary read saw C
    # and the origin received S. Refused by the all-refs snapshot; the real object is S.
    key = _signing_key(tmp_path)
    _push_refused(tmp_path, "replace", "refs/replace/", key)
    unit = tmp_path / "estate" / "driftwood"
    s = _git(unit, "for-each-ref", "--format=%(refname)", "refs/replace/").split("/")[-1]
    real = subprocess.run([*GIT, "-C", str(unit), "cat-file", "commit", s], capture_output=True, text=True,
                          check=True, env={**os.environ, "GIT_NO_REPLACE_OBJECTS": "1"}).stdout
    assert "gpgsig" in real.split("\n\n")[0] and "The Owner" in real, real[:300]


def test_a_hook_or_monitor_the_child_wrote_never_runs_and_the_config_change_is_refused(tmp_path: Path) -> None:
    # F2a/F2b: core.hooksPath -> the clock's own push ran the model's pre-push hook in the owner's
    # shell; core.fsmonitor -> ran at the clock's git status. Now: refused by key, markers absent.
    out, _ = _push_refused(tmp_path, "hooks", "core.hookspath")
    assert "core.fsmonitor" in out
    assert not (tmp_path / ".local-clock" / "hook-ran").exists(), "the child's pre-push hook ran"
    assert not (tmp_path / ".local-clock" / "fsmonitor-ran").exists(), "the child's fsmonitor ran"


def test_a_remote_the_child_rewrote_receives_nothing(tmp_path: Path) -> None:
    # F2c: `git remote set-url origin evil.git` -> the clock pushed there and reported ok
    _push_refused(tmp_path, "remoteurl", "remote.origin.url")
    evil = tmp_path / ".local-clock" / "evil.git"
    assert evil.exists() and _git(evil, "for-each-ref") == "", "evil.git received a push"


def test_an_amended_base_or_a_merge_shaped_commit_is_refused_by_its_parents(tmp_path: Path) -> None:
    # F3: one clean clock commit whose parent is base^ (amend), or with two parents (merge-shaped)
    for stub in ("amend", "merge"):
        unit = tmp_path / "estate" / f"driftwood-{stub}"
        unit.parent.mkdir(exist_ok=True)
        origin = _fixture_adopter(unit)
        env = _clock_env(tmp_path, stub)
        env["LOCAL_CLOCK_ESTATE"] = str(tmp_path / "estate")
        # the clock looks up ESTATE/<adopter>; alias this unit as driftwood via a symlink
        link = tmp_path / "estate" / "driftwood"
        if link.exists() or link.is_symlink():
            link.unlink()
        link.symlink_to(unit)
        done = subprocess.run(["bash", str(CLOCK), "--adopter", "driftwood", "--step", "classify"],
                              env=env, capture_output=True, text=True, timeout=120)
        assert done.returncode == 1, (stub, done.stdout + done.stderr)
        fail_lines = [l for l in done.stdout.splitlines() if l.startswith("fail ")]
        assert fail_lines and "not the base" in fail_lines[0] and _git(origin, "rev-parse", "main")[:7] in fail_lines[0], (stub, done.stdout)
        rid = _run_id(done.stdout)
        steps = [json.loads(l) for l in (tmp_path / ".local-clock" / "runs" / rid / "steps.jsonl").read_text().splitlines()]
        assert steps[0]["status"] == "fail" and steps[0]["commits"] == 1 and "parents" in steps[0]["reason"], steps[0]
        link.unlink()


def test_a_trailer_naming_a_person_is_refused_and_a_gpgsig_word_in_the_body_is_not(tmp_path: Path) -> None:
    unit = tmp_path / "estate" / "driftwood"
    _fixture_adopter(unit)
    done = subprocess.run(["bash", str(CLOCK), "--adopter", "driftwood", "--step", "classify"],
                          env=_clock_env(tmp_path, "signoff"), capture_output=True, text=True, timeout=120)
    assert done.returncode == 1, done.stdout + done.stderr
    fail_lines = [l for l in done.stdout.splitlines() if l.startswith("fail ")]
    assert fail_lines and "trailer" in fail_lines[0] and "The Owner" in fail_lines[0], done.stdout
    done = subprocess.run(["bash", str(CLOCK), "--adopter", "driftwood", "--step", "classify"],
                          env=_clock_env(tmp_path, "bodysig"), capture_output=True, text=True, timeout=120)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "signature: none" in done.stdout, done.stdout


# --- follow-up (2026-09-06): two trailer shapes, a global config write, and the hook ----------
def test_a_trailer_on_line_two_or_a_value_that_merely_contains_the_clock_is_refused(tmp_path: Path) -> None:
    # R1a: `Signed-off-by: The Owner` on line 2 of a one-paragraph message -- interpret-trailers
    # --parse yields nothing; R1b: a Co-authored-by value that CONTAINS the clock identity
    for stub in ("signoff2", "coauthor"):
        unit = tmp_path / "estate" / "driftwood"
        if unit.exists():
            shutil.rmtree(unit.parent)
        _fixture_adopter(unit)
        done = subprocess.run(["bash", str(CLOCK), "--adopter", "driftwood", "--step", "classify"],
                              env=_clock_env(tmp_path, stub), capture_output=True, text=True, timeout=120)
        assert done.returncode == 1, (stub, done.stdout + done.stderr)
        fail_lines = [l for l in done.stdout.splitlines() if l.startswith("fail ")]
        assert fail_lines and "trailer" in fail_lines[0] and "The Owner" in fail_lines[0], (stub, done.stdout)


def test_a_write_to_the_global_config_is_refused_without_touching_the_owners_file(tmp_path: Path) -> None:
    # the clock reads whatever global git reads; for this run that is a throwaway copy
    unit = tmp_path / "estate" / "driftwood"
    _fixture_adopter(unit)
    real = Path.home() / ".gitconfig"
    copy = tmp_path / "gitconfig.copy"
    copy.write_text(real.read_text() if real.exists() else "")
    env = _clock_env(tmp_path, "globalcfg")
    env["GIT_CONFIG_GLOBAL"] = str(copy)
    done = subprocess.run(["bash", str(CLOCK), "--adopter", "driftwood", "--step", "classify"],
                          env=env, capture_output=True, text=True, timeout=120)
    assert done.returncode == 1, done.stdout + done.stderr
    fail_lines = [l for l in done.stdout.splitlines() if l.startswith("fail ")]
    assert fail_lines and "local-clock.probe" in fail_lines[0], done.stdout
    # git writes the key in section form: [local-clock] / probe = yes
    assert "[local-clock]" in copy.read_text() and "probe = yes" in copy.read_text(), copy.read_text()[-200:]
    assert not real.exists() or "[local-clock]" not in real.read_text(), "the stub wrote the owner's real global config"


def test_the_fixture_bypasses_the_owners_global_hook_and_the_clock_does_not() -> None:
    # R2: the fixture's git carries -c core.hooksPath=<empty dir>; the clock's own git and the
    # config it snapshots still read the real global (its hooksPath is only overridden by the
    # clock's -c for its own commands, never removed from what the child sees)
    assert GIT[1:] == ["-c", f"core.hooksPath={NO_HOOKS}"] and NO_HOOKS.is_dir() and not any(NO_HOOKS.iterdir())
    text = CLOCK.read_text()
    assert "GIT_CONFIG_GLOBAL" not in text, "the clock must read the real global config"
    assert 'core.hooksPath="$NO_HOOKS"' in text, "the clock's own git runs no hooks"


# --- tidy (2026-09-06): whitespace before the trailer's colon, lower case -----------------------
def test_a_trailer_with_space_before_the_colon_in_any_case_is_refused(tmp_path: Path) -> None:
    # `signed-off-by : The Owner` -- interpret-trailers normalises it to Signed-off-by:, so a tool
    # reading trailers would credit the person; the clock's match must widen the same way
    unit = tmp_path / "estate" / "driftwood"
    _fixture_adopter(unit)
    done = subprocess.run(["bash", str(CLOCK), "--adopter", "driftwood", "--step", "classify"],
                          env=_clock_env(tmp_path, "signoffspace"), capture_output=True, text=True, timeout=120)
    assert done.returncode == 1, done.stdout + done.stderr
    fail_lines = [l for l in done.stdout.splitlines() if l.startswith("fail ")]
    assert fail_lines and "trailer" in fail_lines[0] and "The Owner" in fail_lines[0], done.stdout
