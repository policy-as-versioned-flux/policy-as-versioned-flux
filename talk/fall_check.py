#!/usr/bin/env python3
"""A fall is a blocking event (NORTH-STAR §5, eco-system ticket 59).

§5's last bullet is two sentences: "The number and its date are recorded on every run. A fall is
a blocking event." The first has been true since GAPS 2.1; the second had no implementation, and
run 13 fell 54 -> 53 with nothing firing. This module is the comparison, and only the comparison:
talk/truth_manifest.py implements parse_truth() and deliberately none of it (its CONTRACT FOR
TICKET 59 is what this file builds).

WHAT A FALL IS, class by class, between two CONSECUTIVE recorded TRUTH lines:

  class-pass  any class's pass count is lower than the previous line's. When `fail` did not rise
              in the same step, the passes that left the class became could-not-looks, and the
              message says so: a green that stopped looking is the degradation a bare
              pass/fail reading cannot see (a pass-to-skip with zero new fails goes green).
  pass        the two lines predate talk/verify-manifest.txt and carry no split, so only the bare
              count can be compared. Said in the message, because a class-blind comparison is a
              weaker instrument and a reader must not take it for the other one.
  fail        `fail` is higher.
  ceiling     `ceiling` is lower AND talk/verify-manifest.txt did not change between the two
              commits the lines name.
  total       `total` is lower AND talk/verify-exclusions.txt did not change between them.

WHAT A FALL IS NOT, and this is the half that takes the care (ticket 83). `ceiling` moves for two
different reasons and only one of them is a loss: a script re-classed `never` lowers it, and that
is the manifest becoming more honest about what can never pass on the runner. An exclusion lowers
`total` the same way. So those two rules are graded against the DIFF between the commits the two
lines name -- `hub=` to `hub=` -- and never against the numbers alone. The diff excuses those two
and nothing else: a manifest commit does not excuse a lost pass.

If the diff cannot be read at all (a shallow clone, a commit this checkout does not carry), the
drop is reported as a fall and the message says the diff could not be read. Conservative on
purpose: this mechanism exists to stop a citable green, and guessing "probably the manifest"
is how a fall goes quiet.

THE ESCAPE HATCH mirrors talk/verify-exclusions.txt: a committed `talk/verify-falls.txt` of

    run=N | reason

lines, one per accepted fall, where N is the run number of the LATER line of the transition. A
line naming a run talk/truth.log does not record is itself a fault, exactly as an exclusion for a
script that does not exist is: an escape hatch nobody can check is a hole.

WHAT IS GRADED AND WHAT IS COUNTED. `report()` grades the NEWEST transition only and COUNTS the
older unaccounted ones. talk/truth.log is append-only and verify/can-record/ refuses a
hand-edited line, so a fall between two 2026-08-31 runs has no finishing move and grading it
forever would be the shape ticket 55 rules out ("every red is real, explained and finishable").
The count is printed on every run, so the history is on the record rather than in a sentence
somebody wrote once.

    python3 talk/fall_check.py check [--log FILE] [--falls FILE] [--root DIR]
        exit 0 no unaccounted fall on the newest transition; 1 if there is one, or if the escape
        file is malformed or names a run the log does not record
    python3 talk/fall_check.py selfcheck
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Callable, Iterable, Sequence

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from truth_manifest import SPLIT_KEYS, parse_truth      # noqa: E402

FALLS_NAME = "talk/verify-falls.txt"
MANIFEST_FILE = "talk/verify-manifest.txt"
EXCLUSIONS_FILE = "talk/verify-exclusions.txt"

# The two files whose change legitimately moves a number down, and the number each one moves.
EXCUSES = {"ceiling": MANIFEST_FILE, "total": EXCLUSIONS_FILE}


@dataclass(frozen=True)
class Fall:
    kind: str          # class-pass | pass | fail | ceiling | total
    detail: str

    def __str__(self) -> str:
        return f"{self.kind}: {self.detail}"


@dataclass
class Report:
    ok: bool
    newest: list[Fall]
    accepted_reason: str = ""
    older_unaccounted: int = 0
    older_accounted: int = 0
    transitions: int = 0
    problems: list[str] = field(default_factory=list)
    note: str = ""
    span: str = ""


# ------------------------------------------------------------------ the comparison

def compare(prev_line: str, cur_line: str, changed: set[str] | None) -> list[Fall]:
    """The falls between two consecutive TRUTH lines.

    `changed` is the set of paths that changed between the two commits the lines name, or None
    when the diff could not be read at all.
    """
    prev, cur = parse_truth(prev_line), parse_truth(cur_line)
    falls: list[Fall] = []
    fail_rose = _int(cur, "fail") > _int(prev, "fail")

    if prev["split"] is not None and cur["split"] is not None:
        for key in SPLIT_KEYS:
            was, now = prev["split"].get(key, 0), cur["split"].get(key, 0)
            if now >= was:
                continue
            how = ("and `fail` rose in the same step, so the passes that left became reds"
                   if fail_rose else
                   "and `fail` did not move, so a pass became a could-not-look inside the class "
                   "-- a green that stopped looking, which the bare pass/fail counts cannot see")
            falls.append(Fall("class-pass",
                              f"class `{key}` fell from {was} passes to {now} {how}"))
    elif _int(cur, "pass") < _int(prev, "pass"):
        falls.append(Fall("pass",
                          f"passes fell from {prev['pass']} to {cur['pass']}; neither line "
                          f"carries a split -- no split on either line, so this is the bare "
                          f"count and no class can be named (both runs predate "
                          f"{MANIFEST_FILE})"))

    if fail_rose:
        falls.append(Fall("fail", f"`fail` rose from {prev['fail']} to {cur['fail']}"))

    for key in ("ceiling", "total"):
        was, now = prev.get(key), cur.get(key)
        if was is None or now is None or now >= was:
            continue
        excuse = EXCUSES[key]
        if changed is None:
            falls.append(Fall(key, f"`{key}` fell from {was} to {now} and this checkout could "
                                   f"not read the diff between {prev['hub']} and {cur['hub']}, "
                                   f"so it cannot tell whether {excuse} moved with it"))
        elif excuse not in changed:
            falls.append(Fall(key, f"`{key}` fell from {was} to {now} with no change to "
                                   f"{excuse} between {prev['hub']} and {cur['hub']}"))
    return falls


def _int(t: dict, key: str) -> int:
    value = t.get(key)
    return int(value) if isinstance(value, int) else 0


# ------------------------------------------------------------------ the escape hatch

_FALL_LINE = re.compile(r"^run\s*=\s*([A-Za-z0-9_-]+)\s*\|\s*(.*)$")


def parse_falls(text: str) -> tuple[dict[str, str], list[str]]:
    """({run: reason}, problems). Validated the way talk/verify-exclusions.txt is: a malformed
    line is reported and dropped, never guessed at."""
    accepted: dict[str, str] = {}
    problems: list[str] = []
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        m = _FALL_LINE.match(line)
        if not m:
            problems.append(f"{FALLS_NAME} line {n}: needs `run=N | reason`, got {raw.strip()!r}")
            continue
        run, reason = m.group(1), m.group(2).strip()
        if not reason:
            problems.append(f"{FALLS_NAME} line {n}: run={run} has no reason; an accepted fall "
                            f"with no reason is a fall nobody accepted")
            continue
        if run in accepted:
            problems.append(f"{FALLS_NAME} line {n}: run={run} is listed twice")
            continue
        accepted[run] = reason
    return accepted, problems


def falls_problems(accepted: dict[str, str], recorded: Iterable[str]) -> list[str]:
    """A committed reason for a run talk/truth.log does not record is itself a fault."""
    known = set(recorded)
    return [f"{FALLS_NAME} accepts a fall at run={run}, which talk/truth.log does not record; "
            f"an escape hatch nobody can check against the log is a hole"
            for run in sorted(accepted) if run not in known]


# ------------------------------------------------------------------ the report

def report(truth_lines: Sequence[str], falls_text: str,
           changed: Callable[[str, str], set[str] | None]) -> Report:
    """Grade the newest transition; count the older ones. `changed(prev_hub, cur_hub)` returns
    the paths that moved between the two commits, or None when the diff cannot be read."""
    accepted, problems = parse_falls(falls_text)
    lines = [l for l in truth_lines if l.startswith("TRUTH ")]
    parsed = [parse_truth(l) for l in lines]
    problems += falls_problems(accepted, (str(t["run"]) for t in parsed))

    if len(lines) < 2:
        note = ("no recorded TRUTH line in the log yet, so there is no transition to grade"
                if not lines else
                "the log holds one recorded line, so there is no transition to grade")
        return Report(ok=not problems, newest=[], problems=problems, note=note)

    older_unaccounted = older_accounted = 0
    for i in range(len(lines) - 2):
        run = str(parsed[i + 1]["run"])
        if compare(lines[i], lines[i + 1], changed(str(parsed[i]["hub"]), str(parsed[i + 1]["hub"]))):
            if run in accepted:
                older_accounted += 1
            else:
                older_unaccounted += 1

    prev, cur = lines[-2], lines[-1]
    run = str(parsed[-1]["run"])
    newest = compare(prev, cur, changed(str(parsed[-2]["hub"]), str(parsed[-1]["hub"])))
    reason = accepted.get(run, "") if newest else ""
    ok = not problems and (not newest or bool(reason))
    return Report(ok=ok, newest=newest, accepted_reason=reason,
                  older_unaccounted=older_unaccounted, older_accounted=older_accounted,
                  transitions=len(lines) - 1, problems=problems,
                  span=f"run {parsed[-2]['run']} ({parsed[-2]['ts']}) -> run {run} "
                       f"({parsed[-1]['ts']})")


# ------------------------------------------------------------------ git, the one impure part

def git_changed(root: str) -> Callable[[str, str], set[str] | None]:
    """The paths that changed between two commits, or None if this checkout cannot read them."""

    def changed(a: str, b: str) -> set[str] | None:
        if not a or not b:
            return None
        try:
            out = subprocess.run(["git", "-C", root, "diff", "--name-only", f"{a}..{b}", "--",
                                  MANIFEST_FILE, EXCLUSIONS_FILE],
                                 capture_output=True, text=True, check=False)
        except OSError:
            return None
        if out.returncode != 0:
            return None
        return {p.strip() for p in out.stdout.splitlines() if p.strip()}

    return changed


# ------------------------------------------------------------------ selfcheck

def selfcheck() -> None:
    def line(run: str, hub: str = "aaaaaaa", observed: int = 10, meta: int = 3, fail: int = 4,
             waits: int = 3, total: int = 60, ceiling: int = 55) -> str:
        passed = observed + 20 + 5 + meta
        return (f"TRUTH 2026-09-06T09:00Z run={run} hub={hub} units=[u=1@main] pass={passed} "
                f"[observed={observed} self=20 simulated=5 meta={meta}] fail={fail} "
                f"skip={2 + waits} [never=2 waits={waits}] excluded=8 total={total} "
                f"ceiling={ceiling}")

    assert compare(line("1"), line("2"), set()) == []
    f = compare(line("1", observed=10), line("2", observed=9, waits=4), set())
    assert [x.kind for x in f] == ["class-pass"] and "observed" in f[0].detail
    assert "became a could-not-look" in f[0].detail
    assert any(x.kind == "fail" for x in compare(line("1"), line("2", fail=5), set()))
    assert compare(line("1"), line("2", ceiling=54), {MANIFEST_FILE}) == []
    assert [x.kind for x in compare(line("1"), line("2", ceiling=54), set())] == ["ceiling"]
    assert compare(line("1"), line("2", total=59), {EXCLUSIONS_FILE}) == []
    assert [x.kind for x in compare(line("1"), line("2", total=59), set())] == ["total"]
    # the diff excuses the ceiling and nothing else
    assert [x.kind for x in compare(line("1"), line("2", observed=9, waits=4, ceiling=54),
                                    {MANIFEST_FILE, EXCLUSIONS_FILE})] == ["class-pass"]
    # unreadable diff: reported, and said
    unread = compare(line("1"), line("2", ceiling=54), None)
    assert [x.kind for x in unread] == ["ceiling"] and "could not read" in unread[0].detail
    # lines with no split fall back to the bare count and say so
    old = "TRUTH 2026-09-03T19:09Z run=1 hub=a units=[] pass=58 fail=7 skip=18 excluded=2 total=85"
    new = "TRUTH 2026-09-03T20:09Z run=2 hub=b units=[] pass=57 fail=7 skip=19 excluded=2 total=85"
    assert [x.kind for x in compare(old, new, set())] == ["pass"]

    accepted, problems = parse_falls("run=105 | a reason\n# comment\n")
    assert accepted == {"105": "a reason"} and problems == []
    assert len(parse_falls("105 no pipe\n")[1]) == 1
    assert len(parse_falls("run=105 |\n")[1]) == 1
    assert len(falls_problems({"113": "r"}, {"105"})) == 1

    log = [line("1", observed=10), line("2", observed=9, waits=4), line("3", observed=9)]
    rep = report(log, "", lambda a, b: set())
    assert rep.ok and rep.newest == [] and rep.older_unaccounted == 1
    rep = report(log[:2], "", lambda a, b: set())
    assert not rep.ok and len(rep.newest) == 1
    rep = report(log[:2], "run=2 | owned by ticket 61", lambda a, b: set())
    assert rep.ok and rep.accepted_reason
    rep = report(log[:2], "run=1 | the wrong transition", lambda a, b: set())
    assert not rep.ok
    assert report([line("1")], "", lambda a, b: set()).ok
    assert "no recorded" in report([], "", lambda a, b: set()).note
    print("selfcheck ok")


# ------------------------------------------------------------------ cli

def _render(rep: Report) -> None:
    for p in rep.problems:
        print(f"FAIL falls: {p}")
    if rep.note:
        print(f"  {rep.note}")
        return
    print(f"  newest transition: {rep.span}")
    if not rep.newest:
        print("  no fall: no class lost a pass, `fail` did not rise, and neither the ceiling "
              "nor the total fell unexplained")
    for f in rep.newest:
        print(f"  FALL {f}")
    if rep.newest and rep.accepted_reason:
        print(f"  accepted by {FALLS_NAME}: {rep.accepted_reason}")
    print(f"  history: {rep.transitions} recorded transition(s); {rep.older_unaccounted} older "
          f"one(s) carry an unaccounted fall and {rep.older_accounted} carry an accepted one "
          f"(older transitions are counted, never graded: the log is append-only)")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="a fall is a blocking event (ticket 59)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("--log", default="talk/truth.log")
    c.add_argument("--falls", default=FALLS_NAME)
    c.add_argument("--root", default=".")
    sub.add_parser("selfcheck")
    a = ap.parse_args(argv)
    if a.cmd == "selfcheck":
        selfcheck()
        return 0
    try:
        with open(a.log, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError as e:
        print(f"FAIL falls: cannot read {a.log}: {e}")
        return 1
    try:
        with open(a.falls, encoding="utf-8") as fh:
            falls_text = fh.read()
    except FileNotFoundError:
        falls_text = ""
    rep = report(lines, falls_text, git_changed(a.root))
    _render(rep)
    return 0 if rep.ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
