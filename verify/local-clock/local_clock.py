#!/usr/bin/env python3
"""local_clock.py -- the local clock (ecosystem ticket 92) made checkable, and its two helpers.

The eco-system has two GitHub clocks (truth.yml on the hub, the per-unit fetch / propose-tier /
twin-sweep clocks, ADR-0024) and, since 2026-09-03, a third: `talk/local-clock.sh`, run by launchd
on the owner's machine, because the model-backed steps can only run inside Claude Code there
(ticket 75 Q10 -- no tokens exist anywhere else). This file is what the gate asks of that clock:

  1. the script exists, is executable, and its README names exactly the flags `--help` prints;
  2. the last run left a dated marker (`.local-clock/last-run.json`), and a scheduled run that
     is older than its declared period plus a day of slack is a clock that has stopped;
  3. no injected signal reached a citable path: every .json/.jsonl/.yaml/.yml file in the
     COMMITTED tree of HEAD and of `origin/main` (the served default branch, as last fetched --
     the check prints how long ago that was, as a number) in the hub and in every unit checkout
     (a clone or a linked worktree) is scanned for an `injected: true` flag, and one hit is a
     FAIL; every local `local-clock/**` branch is scanned too: a rehearsal branch carrying the
     mark is counted and expected, a LIVE one carrying it is a FAIL (the mark escaped its
     rehearsal). A ref that cannot be read is SKIP, never clean. Round 4 (2026-09-06): before
     it, the scan was `git ls-files` over the working tree of whatever branch the checkout
     happened to be on -- a proxy for the served branch, and blind to every other ref;
  4. the local clock never appends talk/truth.log: no `run=local` TRUTH line dated on or after
     2026-09-03 (the one on 2026-08-28 predates the local clock and is a presenter run the
     record already knows about);
  5. the launchd template holds no credential and logs only under the ignored run root.

Two helpers the script shells out to, kept here so the check and the thing it checks read the
same code: `stamp` (the world-simulator envelope, refuses to write outside the run root) and
`record` / `finish` (the per-step log and the marker).

Exit precedence, as in verify/schedules/schedules.py: any FAIL -> 1; else any SKIP -> 3; else 0.
On a machine that is not the owner's (the GitHub runner), the marker is absent and the check
says so as could-not-look; everything else still runs.

Usage:
    local_clock.py check     [--hub H] [--root R] [--estate E]
    local_clock.py selfcheck
    local_clock.py stamp     --signal FILE --out PATH --root R [--by WHO]
    local_clock.py record    --run-dir D --step S --adopter A --status ok|skip|fail [--reason R] [--branch B] [--pr URL]
                             [--base SHA] [--signature-block true|false] [--author "NAME <EMAIL>"]
    local_clock.py finish    --run-dir D --root R --hub H --scheduled 0|1 --period-hours N [--injected FILE] [--model NAME]
    local_clock.py plist     --hour H --minute M [--hub H] [--home DIR]     (prints the filled launchd plist)
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
HUB_DEFAULT = os.path.normpath(os.path.join(HERE, "..", ".."))

SCRIPT = "talk/local-clock.sh"
README = "talk/local-clock.README.md"
PLIST = "talk/local-clock.plist"
RUN_ROOT = ".local-clock"                 # gitignored; the only place a rehearsal may write
MARKER = "last-run.json"
LOCAL_CLOCK_BORN = "2026-09-03"           # a run=local TRUTH line from this date on is a fault
SLACK_HOURS = 24                          # launchd skips a slot when the machine sleeps

ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_FLAG = re.compile(r"(?<![\w-])(--[a-z][a-z0-9-]+)")
# case-insensitive (review F5): YAML reads `Injected: True` as the same boolean
_INJECTED = re.compile(r"""(?:^|[{,\s])["']?injected["']?\s*:\s*true\b""", re.M | re.I)
# the same flag as a POSIX ERE for `git grep -E -i`, which reads a ref's committed tree directly
_INJECTED_ERE = r"""(^|[{,[:space:]])["']?injected["']?[[:space:]]*:[[:space:]]*true"""
_TRUTH_LOCAL = re.compile(r"^TRUTH\s+(\d{4}-\d{2}-\d{2})T\S+\s+run=local\b", re.M)
_CREDENTIAL = re.compile(r"(?i)token|secret|password|api[_-]?key|credential")
_SCANNED = (".json", ".jsonl", ".yaml", ".yml")
_SCANNED_PATHSPECS = ["*.json", "*.jsonl", "*.yaml", "*.yml"]   # git pathspec: `*` crosses `/`
SERVED_REF = "refs/remotes/origin/main"   # the served default branch, as this checkout last fetched it
REAL_MODEL = "claude"                     # a marker left by any other binary is a fixture's, not the clock's


class LocalClockError(ValueError):
    """A refusal the clock makes on purpose, with its reason."""


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _under(path: str, root: str) -> bool:
    path, root = os.path.realpath(path), os.path.realpath(root)
    return path == root or path.startswith(root + os.sep)


# --- the world simulator -----------------------------------------------------------------------
def stamp(signal_path: str, out: str, root: str, by: str, now: str | None = None) -> dict:
    """Read a dated external signal (a headline, a market move, a regulator publish) and write
    it back as an envelope that says on its face that it was injected. The write is refused
    anywhere outside the run root: a rehearsal has exactly one place to live."""
    if not _under(out, root):
        raise LocalClockError(
            f"refusing to write an injected signal to {out!r}: only the run root {root!r} may "
            f"hold one, and everything else is a citable path or could become one")
    with open(signal_path) as fh:
        doc = yaml.safe_load(fh) or {}
    if not isinstance(doc, dict):
        raise LocalClockError(f"{signal_path}: a signal is a mapping, not {type(doc).__name__}")
    for field in ("date", "kind", "statement"):
        if not str(doc.get(field, "")).strip():
            raise LocalClockError(f"{signal_path}: a signal needs a {field}")
    if not ISO_DATE.match(str(doc["date"])):
        raise LocalClockError(f"{signal_path}: date {doc['date']!r} is not YYYY-MM-DD")
    stamped = dict(doc)
    stamped.update({
        "injected": True,
        "injected_at": now or _now(),
        "injected_by": by,
        "injected_from": os.path.abspath(signal_path),
        "citable": False,
        "note": "a world-simulator rehearsal signal (ticket 92). Never cite a run that read it.",
    })
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w") as fh:
        json.dump(stamped, fh, indent=2, sort_keys=True)
        fh.write("\n")
    return stamped


# --- the marker --------------------------------------------------------------------------------
def record(run_dir: str, **fields: object) -> None:
    os.makedirs(run_dir, exist_ok=True)
    fields.setdefault("at", _now())
    with open(os.path.join(run_dir, "steps.jsonl"), "a") as fh:
        fh.write(json.dumps(fields, sort_keys=True) + "\n")


def steps_of(run_dir: str) -> list[dict]:
    path = os.path.join(run_dir, "steps.jsonl")
    if not os.path.exists(path):
        return []
    with open(path) as fh:
        return [json.loads(line) for line in fh if line.strip()]


def finish(run_dir: str, root: str, hub: str, scheduled: bool, period_hours: int,
           injected: str | None, model: str = REAL_MODEL) -> dict:
    """Write the run's marker and copy it to `<root>/last-run.json`, the dated fact the gate
    grades. `mode` is `rehearsal` whenever an injected signal was read: a local run is never
    citable in either mode, and a rehearsal says so twice. `model` is the basename of the
    binary that stood where `claude` stands; a fixture's marker says so and is never graded as
    the clock having run."""
    try:
        commit = subprocess.run(["git", "-C", hub, "rev-parse", "--short", "HEAD"],
                                capture_output=True, text=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        commit = ""
    marker = {
        "ran_at": _now(),
        "scheduled": bool(scheduled),
        "period_hours": int(period_hours),
        "mode": "rehearsal" if injected else "live",
        "injected": bool(injected),
        "injected_signal": os.path.abspath(injected) if injected else None,
        "model": os.path.basename(model) or REAL_MODEL,
        "hub_commit": commit,
        "run_dir": os.path.abspath(run_dir),
        "steps": steps_of(run_dir),
        "citable": False,
    }
    os.makedirs(root, exist_ok=True)
    for path in (os.path.join(run_dir, "marker.json"), os.path.join(root, MARKER)):
        with open(path, "w") as fh:
            json.dump(marker, fh, indent=2, sort_keys=True)
            fh.write("\n")
    return marker


def read_marker(root: str) -> dict | None:
    path = os.path.join(root, MARKER)
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        return json.load(fh)


def marker_verdict(marker: dict | None, now: dt.datetime) -> tuple[str, str]:
    """(PASS|SKIP|FAIL, reason). Absent is could-not-look: the gate runs on a machine that is
    not the owner's most days. A scheduled run older than its period plus a day of slack is a
    clock observed stopped. A run by hand is dated and reported, never graded stale: nobody
    promised it would recur. A marker whose `model` names a stand-in binary was left by a
    fixture and says so: dated, never graded as the clock having run (a marker from before the
    field existed names no binary and is graded as before)."""
    if marker is None:
        return ("SKIP", f"no {RUN_ROOT}/{MARKER} on this machine -- the local clock has not run "
                        f"here, or this is not the owner's machine")
    try:
        ran = dt.datetime.fromisoformat(str(marker.get("ran_at", "")).replace("Z", "+00:00"))
    except ValueError:
        return ("FAIL", f"the marker's ran_at {marker.get('ran_at')!r} is not a date")
    age = (now - ran).total_seconds() / 3600
    model = str(marker.get("model") or REAL_MODEL)
    if model != REAL_MODEL:
        return ("SKIP", f"the last run here ({age:.0f}h ago at {marker['ran_at']}) used a stand-in "
                        f"model ({model}), not {REAL_MODEL} -- a fixture run is not the clock "
                        f"running, so the marker is dated and not graded")
    steps = marker.get("steps") or []
    summary = ", ".join(f"{s.get('step')}/{s.get('adopter')}={s.get('status')}" for s in steps) or "no steps"
    mode = "a rehearsal (injected signal, never citable)" if marker.get("mode") == "rehearsal" \
        else "a live run (local, not citable either)"
    if not marker.get("scheduled"):
        return ("PASS", f"last run by hand {age:.0f}h ago at {marker['ran_at']}: {mode}; {summary}")
    window = int(marker.get("period_hours") or 24) + SLACK_HOURS
    if age > window:
        return ("FAIL", f"the local clock has stopped: last scheduled run {age:.0f}h ago at "
                        f"{marker['ran_at']}, past its {window}h window (declared period plus "
                        f"{SLACK_HOURS}h slack for a sleeping machine)")
    return ("PASS", f"last scheduled run {age:.0f}h ago at {marker['ran_at']}, inside its "
                    f"{window}h window: {mode}; {summary}")


# --- no injected signal reaches a citable path --------------------------------------------------
def _git(repo: str, *args: str, timeout: int = 60) -> subprocess.CompletedProcess[str] | None:
    """Run git in `repo`; None when git itself could not run (then nothing was observed)."""
    try:
        return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True,
                              timeout=timeout)
    except (OSError, subprocess.SubprocessError):
        return None


def injected_leaks(repo: str, ref: str = "HEAD") -> list[str] | None:
    """.json/.jsonl/.yaml/.yml files in the COMMITTED tree of `ref` carrying an `injected: true`
    flag, or None when that tree could not be read (then it was not scanned, and not-scanned
    is never clean). `git grep` reads the ref's tree, not the working directory, so a file that
    is modified or untracked on disk is not seen -- uncommitted is where a rehearsal is allowed
    to be -- and a ref other than the checked-out one (`origin/main`, a `local-clock/**`
    branch) is read the same way. An unborn HEAD (a repository with no commit yet) has an
    empty committed tree and is []."""
    inside = _git(repo, "rev-parse", "--git-dir")
    if inside is None or inside.returncode != 0:
        return None
    resolved = _git(repo, "rev-parse", "--verify", "-q", f"{ref}^{{commit}}")
    if resolved is None:
        return None
    if resolved.returncode != 0:
        if ref == "HEAD":
            unborn = _git(repo, "symbolic-ref", "-q", "HEAD")
            if unborn is not None and unborn.returncode == 0:
                return []
        return None
    tree = resolved.stdout.strip()
    done = _git(repo, "grep", "-I", "-i", "-l", "-E", "-e", _INJECTED_ERE, tree, "--", *_SCANNED_PATHSPECS)
    if done is None or done.returncode not in (0, 1):     # 1 is "no match"
        return None
    hits = []
    for line in done.stdout.splitlines():
        _sha, _sep, rel = line.partition(":")
        if rel:
            hits.append(rel)
    return sorted(hits)


def local_clock_branches(repo: str) -> list[tuple[str, str]]:
    """Every `refs/heads/local-clock/**` branch in the checkout as (name, kind): `rehearsal`
    for `local-clock/rehearsal/...` (the mark is expected there), `live` otherwise."""
    done = _git(repo, "for-each-ref", "--format=%(refname:short)", "refs/heads/local-clock/")
    if done is None or done.returncode != 0:
        return []
    return [(name, "rehearsal" if name.startswith("local-clock/rehearsal/") else "live")
            for name in done.stdout.split()]


def fetched_hours_ago(repo: str, now: dt.datetime) -> float | None:
    """Hours since this checkout last learned what origin/main is: the newest of FETCH_HEAD
    (per worktree, so a linked worktree may have none), the loose ref file and packed-refs.
    None when none of them exists. This is the number that says how stale the served ref may
    be; it is not the ref's commit date, which says how old the tip is, not how old the look."""
    newest: float | None = None
    for name in ("FETCH_HEAD", SERVED_REF, "packed-refs"):
        done = _git(repo, "rev-parse", "--git-path", name)
        if done is None or done.returncode != 0:
            continue
        path = done.stdout.strip()
        if not os.path.isabs(path):
            path = os.path.join(repo, path)
        if os.path.exists(path):
            stamp = os.path.getmtime(path)
            newest = stamp if newest is None else max(newest, stamp)
    if newest is None:
        return None
    return max(0.0, (now.timestamp() - newest) / 3600)


def ref_age_hours(repo: str, ref: str, now: dt.datetime) -> float | None:
    done = _git(repo, "log", "-1", "--format=%ct", ref)
    if done is None or done.returncode != 0 or not done.stdout.strip():
        return None
    return max(0.0, (now.timestamp() - int(done.stdout.strip())) / 3600)


def scan_repo(repo: str, now: dt.datetime | None = None) -> dict:
    """One checkout, every ref that matters: HEAD, the served default branch as last fetched,
    and every local-clock branch. Each value is a list of hits or None (could not read)."""
    now = now or dt.datetime.now(dt.timezone.utc)
    served = _git(repo, "rev-parse", "--verify", "-q", SERVED_REF)
    has_served = served is not None and served.returncode == 0
    return {
        "HEAD": injected_leaks(repo, "HEAD"),
        "origin/main": injected_leaks(repo, SERVED_REF) if has_served else None,
        "fetched_hours_ago": fetched_hours_ago(repo, now),
        "origin_main_age_hours": ref_age_hours(repo, SERVED_REF, now) if has_served else None,
        "branches": [(name, kind, injected_leaks(repo, f"refs/heads/{name}"))
                     for name, kind in local_clock_branches(repo)],
    }


def estate_repos(estate: str) -> list[tuple[str, str]]:
    """Every entry of the estate that is a checkout: `.git` a directory (a clone) or a file (a
    linked worktree, whose `.git` names its gitdir; `git ls-files` works there too). An entry
    with neither is not a repository and is not listed; one whose `.git` is present but broken
    is listed, so the scan reports it SKIP rather than passing it over in silence."""
    if not os.path.isdir(estate):
        return []
    return [(entry, os.path.join(estate, entry)) for entry in sorted(os.listdir(estate))
            if os.path.exists(os.path.join(estate, entry, ".git"))]


def local_truth_lines(log: str) -> list[str] | None:
    """`run=local` TRUTH lines dated on or after the local clock existed; None when there is no
    log to read (could not look, not clean)."""
    if not os.path.exists(log):
        return None
    with open(log, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    return [m.group(0) for m in _TRUTH_LOCAL.finditer(text) if m.group(1) >= LOCAL_CLOCK_BORN]


# --- the README and the template ----------------------------------------------------------------
def script_flags(script: str) -> set[str]:
    done = subprocess.run(["bash", script, "--help"], capture_output=True, text=True, timeout=30)
    return set(_FLAG.findall(done.stdout))


def readme_flags(readme: str) -> set[str]:
    """Flags the README documents, read from its `## Flags` section so prose elsewhere (a
    mention of `--live` on the gate, say) does not count as a documented flag of this script."""
    with open(readme) as fh:
        text = fh.read()
    section = re.search(r"^## Flags\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return set(_FLAG.findall(section.group(1))) if section else set()


def render_plist(template: str, hub: str, home: str, hour: int, minute: int) -> str:
    """The template with its four placeholders filled. Hour and minute become the integers
    launchd wants; the template keeps them as strings so it stays a parseable plist."""
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise LocalClockError(f"{hour:02d}:{minute:02d} is not a time of day")
    with open(template) as fh:
        text = fh.read()
    text = text.replace("<string>__HOUR__</string>", f"<integer>{hour}</integer>")
    text = text.replace("<string>__MINUTE__</string>", f"<integer>{minute}</integer>")
    return text.replace("__HUB__", os.path.abspath(hub)).replace("__HOME__", os.path.abspath(home))


def plist_faults(path: str) -> list[str]:
    faults = []
    with open(path) as fh:
        text = fh.read()
    if _CREDENTIAL.search(text):
        faults.append("holds a credential-shaped word; the plist may hold none")
    if f"/{RUN_ROOT}/" not in text:
        faults.append(f"does not log under {RUN_ROOT}/")
    if "local-clock.sh" not in text:
        faults.append("does not run talk/local-clock.sh")
    if "LOCAL_CLOCK_LAUNCHD" not in text:
        faults.append("does not set LOCAL_CLOCK_LAUNCHD=1, so a scheduled run would be graded as a run by hand")
    return faults


# --- the check -----------------------------------------------------------------------------------
LINES: list[str] = []


def out(status: str, msg: str) -> None:
    LINES.append(status)
    print(f"{status}: {msg}")


def check(hub: str, root: str, estate: str, now: dt.datetime | None = None) -> int:
    LINES.clear()
    now = now or dt.datetime.now(dt.timezone.utc)
    script = os.path.join(hub, SCRIPT)
    readme = os.path.join(hub, README)
    plist = os.path.join(hub, PLIST)

    # 1. the script and its README
    if not os.path.isfile(script):
        out("FAIL", f"{SCRIPT} does not exist")
    elif not os.access(script, os.X_OK):
        out("FAIL", f"{SCRIPT} is not executable")
    elif not os.path.isfile(readme):
        out("FAIL", f"{README} does not exist beside the script")
    else:
        have, documented = script_flags(script), readme_flags(readme)
        if not have:
            out("FAIL", f"{SCRIPT} --help prints no flags")
        elif have != documented:
            out("FAIL", f"{README} and {SCRIPT} --help disagree on the flags: script-only "
                        f"{sorted(have - documented)}, README-only {sorted(documented - have)}")
        else:
            out("PASS", f"{SCRIPT} exists and {README} names its {len(have)} flags exactly")

    # 2. the marker
    status, reason = marker_verdict(read_marker(root), now)
    out(status, reason)

    # 3. no injected signal on a citable path: HEAD and the SERVED default branch (origin/main
    #    as last fetched) of the hub and every unit, plus every local-clock branch. The limits
    #    are printed as numbers, not prose: how long ago origin/main was fetched, how many
    #    checkouts have no origin/main to read, how many rehearsal branches carry the mark.
    repos = [("hub", hub)] + estate_repos(estate)
    leaked, scanned_head, scanned_served = False, 0, 0
    no_served: list[str] = []
    never_fetched: list[str] = []
    oldest_fetch: float | None = None
    live_branches = rehearsal_branches = rehearsal_marked = 0
    for name, repo in repos:
        scan = scan_repo(repo, now)
        if scan["HEAD"] is None:
            out("SKIP", f"{name}: the committed tree of HEAD at {repo} could not be read, so it was "
                        f"not scanned for an injected signal -- not scanned is not clean")
            continue
        scanned_head += 1
        if scan["HEAD"]:
            leaked = True
            out("FAIL", f"{name}: an injected (rehearsal) signal is committed on HEAD at "
                        f"{', '.join(scan['HEAD'])} -- a rehearsal reached a citable path")
        if scan["origin/main"] is None:
            no_served.append(name)
        else:
            scanned_served += 1
            if scan["origin/main"]:
                leaked = True
                out("FAIL", f"{name}: an injected (rehearsal) signal is committed on origin/main at "
                            f"{', '.join(scan['origin/main'])} -- a rehearsal reached the served "
                            f"default branch")
            fetched = scan["fetched_hours_ago"]
            if fetched is None:
                never_fetched.append(name)
            elif oldest_fetch is None or fetched > oldest_fetch:
                oldest_fetch = fetched
        for branch, kind, hits in scan["branches"]:
            if hits is None:
                out("SKIP", f"{name}: the branch {branch} could not be read, so it was not scanned")
                continue
            if kind == "live":
                live_branches += 1
                if hits:
                    leaked = True
                    out("FAIL", f"{name}: the LIVE local-clock branch {branch} carries injected: true "
                                f"at {', '.join(hits)} -- the rehearsal mark escaped its rehearsal, "
                                f"and --push would have offered it as a proposal")
            else:
                rehearsal_branches += 1
                if hits:
                    rehearsal_marked += 1
    if no_served:
        out("SKIP", f"{len(no_served)} repository(ies) ({', '.join(no_served)}) have no origin/main "
                    f"in the checkout, so the served default branch was not scanned there -- not "
                    f"scanned is not clean (HEAD was)")
    if rehearsal_branches:
        print(f"  note: {rehearsal_branches} rehearsal branch(es) in the checkouts, {rehearsal_marked} "
              f"carrying injected: true by design -- never pushed, never citable")
    if not leaked and scanned_head:
        fetch_note = (f"oldest last updated {oldest_fetch:.0f}h ago" if oldest_fetch is not None
                      else "update age unknown")
        if never_fetched:
            fetch_note += f", {len(never_fetched)} with no dated ref ({', '.join(never_fetched)})"
        out("PASS", f"no committed envelope, claim, observation or capture carries injected: true on "
                    f"HEAD of {scanned_head} repositories or origin/main of {scanned_served} "
                    f"({fetch_note}); {live_branches} live local-clock branch(es) carry none, "
                    f"{rehearsal_branches} rehearsal branch(es) may")

    # 4. the local clock never appends the truth log
    local_lines = local_truth_lines(os.path.join(hub, "talk", "truth.log"))
    if local_lines is None:
        out("SKIP", "talk/truth.log is absent, so it could not be read for a run=local line")
    elif local_lines:
        out("FAIL", f"talk/truth.log carries {len(local_lines)} run=local TRUTH line(s) dated "
                    f"{LOCAL_CLOCK_BORN} or later: {local_lines[0][:80]} -- a local run is not citable")
    else:
        out("PASS", f"talk/truth.log carries no run=local TRUTH line since {LOCAL_CLOCK_BORN}")

    # 5. the template
    if not os.path.isfile(plist):
        out("FAIL", f"{PLIST} does not exist")
    else:
        faults = plist_faults(plist)
        for fault in faults:
            out("FAIL", f"{PLIST} {fault}")
        if not faults:
            out("PASS", f"{PLIST} holds no credential and logs under {RUN_ROOT}/")

    if "FAIL" in LINES:
        return 1
    if "SKIP" in LINES:
        return 3
    return 0


# --- selfcheck: planted fixtures, each refusal must bite ---------------------------------------
def selfcheck() -> None:
    now = dt.datetime(2026, 9, 3, 12, tzinfo=dt.timezone.utc)
    with tempfile.TemporaryDirectory() as tmp:
        root = os.path.join(tmp, RUN_ROOT)
        sig = os.path.join(tmp, "signal.yaml")
        with open(sig, "w") as fh:
            yaml.safe_dump({"date": "2026-09-03", "kind": "headline", "statement": "rehearsal"}, fh)
        # the stamp marks, and refuses everywhere but the run root
        doc = stamp(sig, os.path.join(root, "runs", "r", "s.json"), root=root, by="selfcheck")
        assert doc["injected"] is True and doc["citable"] is False, doc
        for citable in ("observations/x.jsonl", "twin/claims/x.claim.yaml", "talk/captures/x.out"):
            try:
                stamp(sig, os.path.join(tmp, citable), root=root, by="selfcheck")
            except LocalClockError:
                pass
            else:
                raise AssertionError(f"stamp wrote to {citable}")
            assert not os.path.exists(os.path.join(tmp, citable))

        # the marker: fresh passes, stale scheduled fails, by hand is dated not graded, absent skips
        good = {"ran_at": "2026-09-03T06:00:00Z", "scheduled": True, "period_hours": 24, "steps": []}
        assert marker_verdict(good, now)[0] == "PASS"
        assert marker_verdict(good, now + dt.timedelta(hours=72))[0] == "FAIL"
        assert marker_verdict({**good, "scheduled": False}, now + dt.timedelta(days=40))[0] == "PASS"
        assert marker_verdict(None, now)[0] == "SKIP"
        assert marker_verdict({**good, "ran_at": "soon"}, now)[0] == "FAIL"

        # the leak scan: a committed injected observation is found, prose and uncommitted are not
        repo = os.path.join(tmp, "unit")
        os.makedirs(os.path.join(repo, "observations"))
        subprocess.run(["git", "init", "-q", repo], check=True)
        with open(os.path.join(repo, "observations", "twin-sweep.jsonl"), "w") as fh:
            fh.write('{"swept_at": "2026-09-03T07:05:00Z", "injected": true}\n')
        with open(os.path.join(repo, "notes.md"), "w") as fh:
            fh.write("injected: true\n")
        with open(os.path.join(repo, "uncommitted.yaml"), "w") as fh:
            fh.write("injected: true\n")
        subprocess.run(["git", "-C", repo, "add", "--", "observations", "notes.md"], check=True)
        subprocess.run(["git", "-C", repo, "-c", "user.name=s", "-c", "user.email=s@s",
                        "commit", "-q", "-m", "x"], check=True)
        assert injected_leaks(repo) == ["observations/twin-sweep.jsonl"], injected_leaks(repo)
        # a repository that cannot be listed is unscanned, never clean
        assert injected_leaks(os.path.join(tmp, "no-such-repo")) is None
        # the estate walk: a clone (.git a directory) and a linked worktree (.git a file) are
        # both checkouts and both scanned; a .git file that names nothing is listed so the scan
        # says SKIP; a directory with no .git at all is not a repository
        estate = os.path.join(tmp, "estate")
        os.makedirs(os.path.join(estate, "plain"))
        os.makedirs(os.path.join(estate, "broken"))
        with open(os.path.join(estate, "broken", ".git"), "w") as fh:
            fh.write("gitdir: /nowhere\n")
        subprocess.run(["git", "-C", repo, "worktree", "add", "-q", os.path.join(estate, "linked"),
                        "-b", "linked"], check=True, capture_output=True)
        os.symlink(repo, os.path.join(estate, "clone"))
        names = [name for name, _ in estate_repos(estate)]
        assert names == ["broken", "clone", "linked"], names
        assert os.path.isfile(os.path.join(estate, "linked", ".git"))
        assert injected_leaks(os.path.join(estate, "linked")) == ["observations/twin-sweep.jsonl"]
        assert injected_leaks(os.path.join(estate, "broken")) is None
        # round 4: the scan reads a REF's committed tree, so a rehearsal branch is read without
        # checking it out, a modified-but-uncommitted file is not seen, and a ref that does not
        # exist is unread rather than clean; a rehearsal branch is told from a live one by name
        subprocess.run(["git", "-C", repo, "checkout", "-q", "-b", "local-clock/rehearsal/classify-r"],
                       check=True, capture_output=True)
        with open(os.path.join(repo, "rehearsal.yaml"), "w") as fh:
            fh.write("injected: true\n")
        subprocess.run(["git", "-C", repo, "add", "rehearsal.yaml"], check=True)
        subprocess.run(["git", "-C", repo, "-c", "user.name=s", "-c", "user.email=s@s",
                        "commit", "-q", "-m", "r"], check=True)
        subprocess.run(["git", "-C", repo, "checkout", "-q", "-"], check=True, capture_output=True)
        with open(os.path.join(repo, "notes.md"), "a") as fh:
            fh.write("still prose\n")
        assert injected_leaks(repo, "refs/heads/local-clock/rehearsal/classify-r") == \
            ["observations/twin-sweep.jsonl", "rehearsal.yaml"]
        assert injected_leaks(repo, "HEAD") == ["observations/twin-sweep.jsonl"]
        assert injected_leaks(repo, "refs/heads/no-such-branch") is None
        # review F5: the mark is read case-insensitively, as YAML reads the boolean
        with open(os.path.join(repo, "shout.yaml"), "w") as fh:
            fh.write("Injected: True\n")
        subprocess.run(["git", "-C", repo, "add", "shout.yaml"], check=True)
        subprocess.run(["git", "-C", repo, "-c", "user.name=s", "-c", "user.email=s@s",
                        "commit", "-q", "-m", "shout"], check=True)
        assert "shout.yaml" in (injected_leaks(repo, "HEAD") or []), injected_leaks(repo, "HEAD")
        assert _INJECTED.search('{"INJECTED": TRUE}')
        assert local_clock_branches(repo) == [("local-clock/rehearsal/classify-r", "rehearsal")]
        scanned = scan_repo(repo, now)
        assert scanned["origin/main"] is None and scanned["branches"][0][1] == "rehearsal", scanned
        # a marker left by a stand-in model is dated, never graded as the clock having run
        assert marker_verdict({**good, "model": "stub-claude.sh"}, now)[0] == "SKIP"
        assert marker_verdict({**good, "model": "claude"}, now)[0] == "PASS"

        # the truth log: absent is unread; the 2026-08-28 presenter line is known; a later
        # run=local is a fault
        log = os.path.join(tmp, "truth.log")
        assert local_truth_lines(log) is None
        with open(log, "w") as fh:
            fh.write("TRUTH 2026-08-28T04:00Z run=local hub=2326f31 pass=40\n"
                     "TRUTH 2026-09-03T10:24Z run=22 hub=14cc731 pass=57\n")
        assert local_truth_lines(log) == []
        with open(log, "a") as fh:
            fh.write("TRUTH 2026-09-04T01:00Z run=local hub=deadbee pass=1\n")
        later = local_truth_lines(log)
        assert later is not None and len(later) == 1, later

        # the template: a credential-shaped word is refused
        bad = os.path.join(tmp, "bad.plist")
        with open(bad, "w") as fh:
            fh.write("<plist><dict><key>GITHUB_TOKEN</key><string>x</string></dict></plist>")
        assert any("credential" in f for f in plist_faults(bad)), plist_faults(bad)

        # the README reader: only the Flags section counts
        readme = os.path.join(tmp, "README.md")
        with open(readme, "w") as fh:
            fh.write("# x\n\nrun the gate with --live sometimes\n\n## Flags\n\n- `--inject FILE` x\n- `--push` y\n\n## Next\n\n--dry-run is not a flag here\n")
        assert readme_flags(readme) == {"--inject", "--push"}, readme_flags(readme)

    print("ok  the local clock's checks bite: the stamp refuses every citable path, a stale "
          "scheduled marker fails while a hand run is only dated, a committed injected envelope "
          "is found and an uncommitted one is not, an unlistable repository or absent truth "
          "log is unscanned rather than clean, a linked worktree (.git a file) is scanned like "
          "a clone, a ref's committed tree is read without checking it out and a missing ref is "
          "unread rather than clean, a stand-in model's marker is dated and not graded, a "
          f"run=local TRUTH line since {LOCAL_CLOCK_BORN} fails, a credential in the plist "
          "fails, and the README's flags are read from its Flags section only")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--hub", default=HUB_DEFAULT)
    c.add_argument("--root", default=None)
    c.add_argument("--estate", default=None)
    sub.add_parser("selfcheck")
    s = sub.add_parser("stamp")
    s.add_argument("--signal", required=True)
    s.add_argument("--out", required=True)
    s.add_argument("--root", required=True)
    s.add_argument("--by", default="talk/local-clock.sh --inject")
    r = sub.add_parser("record")
    r.add_argument("--run-dir", required=True)
    r.add_argument("--step", required=True)
    r.add_argument("--adopter", required=True)
    r.add_argument("--status", required=True, choices=("ok", "skip", "fail"))
    r.add_argument("--reason", default="")
    r.add_argument("--branch", default="")
    r.add_argument("--pr", default="")
    r.add_argument("--base", default="", help="the served tip the proposal was cut from")
    r.add_argument("--commits", type=int, default=None, help="commits between the base and HEAD")
    r.add_argument("--commit", default="", help="the one admitted commit")
    r.add_argument("--signature-block", default=None, choices=("true", "false"))
    r.add_argument("--author", default="")
    r.add_argument("--committer", default="")
    r.add_argument("--origin-main-at-push", default="", help="origin/main as ls-remote saw it just before the push")
    f = sub.add_parser("finish")
    f.add_argument("--run-dir", required=True)
    f.add_argument("--root", required=True)
    f.add_argument("--hub", default=HUB_DEFAULT)
    f.add_argument("--scheduled", default="0")
    f.add_argument("--period-hours", default="24")
    f.add_argument("--injected", default=None)
    f.add_argument("--model", default=REAL_MODEL, help="basename of the binary that ran as the model")
    p = sub.add_parser("plist", help="print the launchd plist with the owner's cadence and paths filled in")
    p.add_argument("--hour", type=int, required=True)
    p.add_argument("--minute", type=int, required=True)
    p.add_argument("--hub", default=HUB_DEFAULT)
    p.add_argument("--home", default=os.path.expanduser("~"))
    args = parser.parse_args(argv[1:])

    try:
        if args.cmd == "selfcheck":
            selfcheck()
            return 0
        if args.cmd == "check":
            hub = os.path.abspath(args.hub)
            return check(hub, args.root or os.path.join(hub, RUN_ROOT),
                         args.estate or os.path.join(hub, ".estate-clone"))
        if args.cmd == "stamp":
            doc = stamp(args.signal, args.out, root=args.root, by=args.by)
            print(f"ok  injected signal stamped at {args.out}: {doc['kind']} dated {doc['date']}")
            return 0
        if args.cmd == "record":
            extra: dict[str, object] = {}
            if args.base:
                extra["base"] = args.base
            if args.commits is not None:
                extra["commits"] = args.commits
            if args.commit:
                extra["commit"] = args.commit
            if args.signature_block is not None:
                extra["signature_block"] = args.signature_block == "true"
            if args.author:
                extra["author"] = args.author
            if args.committer:
                extra["committer"] = args.committer
            if args.origin_main_at_push:
                extra["origin_main_at_push"] = args.origin_main_at_push
            record(args.run_dir, step=args.step, adopter=args.adopter, status=args.status,
                   reason=args.reason, branch=args.branch, pr=args.pr, **extra)
            return 0
        if args.cmd == "plist":
            sys.stdout.write(render_plist(os.path.join(os.path.abspath(args.hub), PLIST),
                                          args.hub, args.home, args.hour, args.minute))
            return 0
        if args.cmd == "finish":
            marker = finish(args.run_dir, args.root, args.hub, args.scheduled == "1",
                            int(args.period_hours), args.injected, args.model)
            print(f"ok  marker written: {os.path.join(args.root, MARKER)} mode={marker['mode']} "
                  f"model={marker['model']} steps={len(marker['steps'])}")
            return 0
    except LocalClockError as exc:
        print(f"FAIL: {exc}")
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
