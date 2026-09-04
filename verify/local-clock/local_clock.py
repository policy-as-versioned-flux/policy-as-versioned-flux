#!/usr/bin/env python3
"""local_clock.py -- the local clock (ecosystem ticket 92) made checkable, and its two helpers.

The eco-system has two GitHub clocks (truth.yml on the hub, the per-unit fetch / propose-tier /
twin-sweep clocks, ADR-0024) and, since 2026-09-03, a third: `talk/local-clock.sh`, run by launchd
on the owner's machine, because the model-backed steps can only run inside Claude Code there
(ticket 75 Q10 -- no tokens exist anywhere else). This file is what the gate asks of that clock:

  1. the script exists, is executable, and its README names exactly the flags `--help` prints;
  2. the last run left a dated marker (`.local-clock/last-run.json`), and a scheduled run that
     is older than its declared period plus a day of slack is a clock that has stopped;
  3. no injected signal reached a citable path: every committed .json/.jsonl/.yaml/.yml file in
     the hub and in every unit checkout is scanned for an `injected: true` flag, and one hit is
     a FAIL. A world-simulator rehearsal is never cited;
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
    local_clock.py finish    --run-dir D --root R --hub H --scheduled 0|1 --period-hours N [--injected FILE]
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
_INJECTED = re.compile(r"""(?:^|[{,\s])["']?injected["']?\s*:\s*true\b""", re.M)
_TRUTH_LOCAL = re.compile(r"^TRUTH\s+(\d{4}-\d{2}-\d{2})T\S+\s+run=local\b", re.M)
_CREDENTIAL = re.compile(r"(?i)token|secret|password|api[_-]?key|credential")
_SCANNED = (".json", ".jsonl", ".yaml", ".yml")


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
def record(run_dir: str, **fields: str) -> None:
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
           injected: str | None) -> dict:
    """Write the run's marker and copy it to `<root>/last-run.json`, the dated fact the gate
    grades. `mode` is `rehearsal` whenever an injected signal was read: a local run is never
    citable in either mode, and a rehearsal says so twice."""
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
    promised it would recur."""
    if marker is None:
        return ("SKIP", f"no {RUN_ROOT}/{MARKER} on this machine -- the local clock has not run "
                        f"here, or this is not the owner's machine")
    try:
        ran = dt.datetime.fromisoformat(str(marker.get("ran_at", "")).replace("Z", "+00:00"))
    except ValueError:
        return ("FAIL", f"the marker's ran_at {marker.get('ran_at')!r} is not a date")
    age = (now - ran).total_seconds() / 3600
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
def injected_leaks(repo: str) -> list[str] | None:
    """Committed .json/.jsonl/.yaml/.yml files carrying an `injected: true` flag, or None when
    the repository could not be listed (then it was not scanned, and not-scanned is never
    clean). Committed is the line: `git ls-files` sees the checked-out branch, so a rehearsal
    branch that was never merged or checked out is invisible to it, and a rehearsal file that is
    not committed at all is where a rehearsal is allowed to be."""
    try:
        listed = subprocess.run(["git", "-C", repo, "ls-files", "-z"], capture_output=True,
                                text=True, timeout=60, check=True).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    hits = []
    for rel in listed.split("\0"):
        if not rel.endswith(_SCANNED):
            continue
        path = os.path.join(repo, rel)
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                if _INJECTED.search(fh.read()):
                    hits.append(rel)
        except OSError:
            continue
    return sorted(hits)


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

    # 3. no injected signal on a citable path, hub and every unit
    repos = [("hub", hub)]
    if os.path.isdir(estate):
        for entry in sorted(os.listdir(estate)):
            if os.path.isdir(os.path.join(estate, entry, ".git")):
                repos.append((entry, os.path.join(estate, entry)))
    leaked, scanned = False, 0
    for name, repo in repos:
        hits = injected_leaks(repo)
        if hits is None:
            out("SKIP", f"{name}: git ls-files failed at {repo}, so it was not scanned for an "
                        f"injected signal -- not scanned is not clean")
        elif hits:
            leaked = True
            out("FAIL", f"{name}: an injected (rehearsal) signal is committed at "
                        f"{', '.join(hits)} -- a rehearsal reached a citable path")
        else:
            scanned += 1
    if not leaked and scanned:
        out("PASS", f"no committed envelope, claim, observation or capture in {scanned} "
                    f"repositories carries injected: true")

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
          "log is unscanned rather than clean, a run=local TRUTH line since "
          f"{LOCAL_CLOCK_BORN} fails, a credential in the plist fails, and the README's flags "
          "are read from its Flags section only")


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
    f = sub.add_parser("finish")
    f.add_argument("--run-dir", required=True)
    f.add_argument("--root", required=True)
    f.add_argument("--hub", default=HUB_DEFAULT)
    f.add_argument("--scheduled", default="0")
    f.add_argument("--period-hours", default="24")
    f.add_argument("--injected", default=None)
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
            record(args.run_dir, step=args.step, adopter=args.adopter, status=args.status,
                   reason=args.reason, branch=args.branch, pr=args.pr)
            return 0
        if args.cmd == "plist":
            sys.stdout.write(render_plist(os.path.join(os.path.abspath(args.hub), PLIST),
                                          args.hub, args.home, args.hour, args.minute))
            return 0
        if args.cmd == "finish":
            marker = finish(args.run_dir, args.root, args.hub, args.scheduled == "1",
                            int(args.period_hours), args.injected)
            print(f"ok  marker written: {os.path.join(args.root, MARKER)} mode={marker['mode']} "
                  f"steps={len(marker['steps'])}")
            return 0
    except LocalClockError as exc:
        print(f"FAIL: {exc}")
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
