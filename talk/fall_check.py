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

WHICH TRANSITION IS GRADED: THE ONE ENDING AT THE RUN BEING RECORDED (ticket 108, 2026-09-09).
The clock's own recording commit appends the run's line and carries `[skip ci]`, so it moves this
module's input and nothing re-measures. Read "the newest line on disk" and the answer is one thing
inside the gate and a different thing one commit later, on a tree no run will ever grade again.

So `report()` takes `recording_run`, the run this process belongs to, and grades the transition
ENDING at it:

  * `recording_run` empty (a builder, a review, a throwaway merge, any checkout with no run in
    flight) -- the run being recorded is the newest line the log carries, and the transition
    ending at it is graded exactly as before. A fall on the record still blocks, and is still
    finishable by a line in talk/verify-falls.txt.
  * `recording_run` equal to the newest recorded run (truth.yml's own step, which runs AFTER the
    cage has appended the line) -- identical, and that step is where NORTH-STAR §5's stop lives.
  * `recording_run` naming a run the log does not carry (the GATE of a clock run: the line does
    not exist yet, and cannot, because this check's own verdict is one of the counts in it) --
    DEFERRED. The transition ending at that run is graded by truth.yml's `a fall is a blocking
    event` step once the line exists. Grading the newest RECORDED transition here instead would
    re-grade a transition the run that recorded it already blocked on, and write that stale red
    into talk/captures/_grades.tsv, where verify/derived-status/ reads it as a live regression.
    The older transition is still COMPARED and its verdict PRINTED; it is counted, not faulted.
  * `recording_run` naming a run the log carries that is NOT the newest -- a problem, not a
    shrug: the log moved under the run and neither reading can be trusted. A RE-RUN of an older
    truth run lands here by construction and is now red where it used to be green, and that run's
    cage would commit the red as this check's grade row (review F6, recorded not fixed).
  * `recording_run` that is not digits -- a problem too, never a defer. Deferring means not
    grading, so the key is checked before it is trusted, and run numbers are compared by value.

WHERE DEFERRED REACHES, said because the first version of this note understated it (review F5a).
`GITHUB_RUN_NUMBER` is set on EVERY truth.yml run, not only the recording one, so a branch or
pull-request CI run defers as well -- where it previously reddened on the DEFAULT branch's newest
unaccounted fall. That is right: a branch records no line (ticket 100), so the newest transition
in the log is main's and not this run's, and truth.yml's own stop step already reports it and
blocks nothing on a branch for exactly that reason. The empty case is a checkout with no run in
flight at all: a builder, a review, a throwaway merge.

THE RESIDUAL IN truth.yml'S OWN STEP (review F8, recorded not fixed). That step's reading is
identical to this one ONLY while the cage actually appended this run's line. If `CAN_RECORD=yes`
but the cage short-circuits -- `git diff --cached --quiet` finding nothing to commit -- the step
grades the PREVIOUS run's transition, and the two readings are not unconditionally the same.

`inversions()` is the size of what remains, as a number rather than a sentence: how many recorded
runs turned this comparison from green to red by the act of recording their own line.

WHAT IS GRADED AND WHAT IS COUNTED. `report()` grades ONE transition -- the one ending at the run
being recorded -- and COUNTS the older unaccounted ones. talk/truth.log is append-only and verify/can-record/ refuses a
hand-edited line, so a fall between two 2026-08-31 runs has no finishing move and grading it
forever would be the shape ticket 55 rules out ("every red is real, explained and finishable").
The count is printed on every run, so the history is on the record rather than in a sentence
somebody wrote once.

    python3 talk/fall_check.py check [--log FILE] [--falls FILE] [--root DIR]
                                     [--recording-run N]
        exit 0 no unaccounted fall on the transition ending at the run being recorded; 1 if there
        is one, or if the escape file is malformed or names a run the log does not record
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
    deferred_to: str = ""          # the run being recorded, whose line is not in the log yet
    deferred_falls: list[Fall] = field(default_factory=list)   # compared, printed, not faulted
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
        # THE CAUSE IS READ, NEVER ASSUMED (review F3, 2026-09-06). The first version said "a pass
        # became a could-not-look" whenever `fail` had not risen, and that is false for the most
        # ordinary movement there is: a re-class moves a PASSING script from one class to another,
        # so one class falls, another rises, the total is unchanged and nothing stopped looking.
        # A checker that reports a cause it cannot see teaches its readers to discount it.
        total_pass_moved = _int(cur, "pass") - _int(prev, "pass")
        skips_rose = _int(cur, "skip") > _int(prev, "skip")
        for key in SPLIT_KEYS:
            was, now = prev["split"].get(key, 0), cur["split"].get(key, 0)
            if now >= was:
                continue
            if total_pass_moved >= 0:
                how = ("while the total number of passes did not fall, so the passes moved "
                       "between classes -- a re-class, not a lost green. It is still a fall by "
                       "the contract, and it needs a line in " + FALLS_NAME)
            elif fail_rose:
                how = "and `fail` rose in the same step, so passes that left became reds"
            elif skips_rose:
                how = ("and `fail` did not move while `skip` rose, so a pass became a "
                       "could-not-look -- a green that stopped looking, which the bare "
                       "pass/fail counts cannot see")
            else:
                how = ("and neither `fail` nor `skip` rose, so those checks left the surface "
                       "altogether (excluded, deleted, or no longer discovered)")
            falls.append(Fall("class-pass",
                              f"class `{key}` fell from {was} passes to {now} {how}"))
    elif _int(cur, "pass") < _int(prev, "pass"):
        which = ("the older line carries no split" if prev["split"] is None and cur["split"]
                 else "the newer line carries no split" if cur["split"] is None and prev["split"]
                 else "no split on either line")
        falls.append(Fall("pass",
                          f"passes fell from {prev['pass']} to {cur['pass']}; {which}, so this "
                          f"is the bare count and no class can be named (a run predating "
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


def _run_key(run: str) -> str:
    """A run number compared by VALUE, so `0200` and `200` are the same run and a non-numeric
    recorded run (`local`, `fixture-2`) is still comparable as itself."""
    run = str(run).strip()
    return str(int(run)) if run.isdigit() else run


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
        # A WHOLE-LINE comment only (review F5, 2026-09-06). Splitting on the first `#` anywhere
        # truncated `run=105 | issue #12 reddened it` to `issue` and refused
        # `# a note` shaped reasons as having none. A reason is prose and prose contains hashes.
        line = raw.strip()
        if not line or line.startswith("#"):
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
           changed: Callable[[str, str], set[str] | None],
           recording_run: str = "") -> Report:
    """Grade the transition ENDING AT THE RUN BEING RECORDED; count the older ones.

    `changed(prev_hub, cur_hub)` returns the paths that moved between the two commits, or None
    when the diff cannot be read. `recording_run` is the run this process belongs to; empty means
    no run is in flight, and then the run being recorded is the newest line the log carries.
    """
    accepted, problems = parse_falls(falls_text)
    lines = [l for l in truth_lines if l.startswith("TRUTH ")]
    parsed = [parse_truth(l) for l in lines]
    recorded = [str(t["run"]) for t in parsed]
    problems += falls_problems(accepted, recorded)

    # WHICH TRANSITION IS THIS PROCESS'S (ticket 108). Not "the newest line on disk": that is one
    # transition inside the gate and a different one a commit later, because the recording commit
    # moves this file and carries the skip-ci marker.
    #
    # THE DEFER KEY IS VALIDATED BEFORE IT IS USED (review F5b, 2026-09-09). Deferring means NOT
    # grading, so a key nobody checks is an escape hatch keyed on an unchecked string -- the exact
    # shape this ticket exists to refuse. Two measured holes it closes: `--recording-run abc`
    # deferred and exited 0, and `--recording-run 0200` deferred where `200` graded, because the
    # membership test was on strings. A run number is digits, and it is compared by VALUE.
    recording_run = str(recording_run or "").strip()
    if recording_run and not re.fullmatch(r"\d+", recording_run):
        problems.append(
            f"--recording-run {recording_run!r} is not a run number, and this module will not "
            f"defer on a key it cannot check: a run number is digits and the clock takes it from "
            f"GITHUB_RUN_NUMBER. The transition ending at the newest recorded line is graded "
            f"instead, and this run is red on the key")
        recording_run = ""
    key = _run_key(recording_run)
    recorded_keys = [_run_key(r) for r in recorded]
    deferred = bool(key) and key not in recorded_keys
    if key and not deferred and recorded_keys and key != recorded_keys[-1]:
        problems.append(
            f"the run being recorded is {recording_run}, which talk/truth.log carries but not as "
            f"its newest line (the newest is run {recorded[-1]}); the log moved under this run, "
            f"so neither reading is this run's and this module does not pick one. A RE-RUN of an "
            f"older recorded run lands here by construction (review F6): it is red, and its cage "
            f"would commit that red as this check's grade row")

    if len(lines) < 2:
        note = ("no recorded TRUTH line in the log yet, so there is no transition to grade"
                if not lines else
                "the log holds one recorded line, so there is no transition to grade")
        return Report(ok=not problems, newest=[], problems=problems, note=note,
                      deferred_to=recording_run if deferred else "")

    older_unaccounted = older_accounted = 0
    fell: set[str] = set()
    for i in range(len(lines) - 1):
        run = str(parsed[i + 1]["run"])
        if not compare(lines[i], lines[i + 1],
                       changed(str(parsed[i]["hub"]), str(parsed[i + 1]["hub"]))):
            continue
        fell.add(run)
        if i == len(lines) - 2 and not deferred:
            continue                          # the newest transition is graded below
        # DEFERRED: the newest RECORDED transition is not this run's either -- the run that
        # recorded it graded it and blocked on it already -- so it is counted here, never faulted.
        if run in accepted:
            older_accounted += 1
        else:
            older_unaccounted += 1

    # A reason for a transition that did not fall (review F5, 2026-09-06). It used to be accepted
    # in silence, so the hatch could fill with entries nobody could check -- the same defect as an
    # exclusion naming a script that no longer exists, which this file's own header calls a hole.
    problems += [f"{FALLS_NAME} accepts a fall at run={run}, but that transition did not fall; "
                 f"remove the line, or the hatch stops being checkable"
                 for run in sorted(accepted) if run not in fell
                 and any(str(t["run"]) == run for t in parsed)]

    prev, cur = lines[-2], lines[-1]
    run = str(parsed[-1]["run"])
    newest = compare(prev, cur, changed(str(parsed[-2]["hub"]), str(parsed[-1]["hub"])))
    span = (f"run {parsed[-2]['run']} ({parsed[-2]['ts']}) -> run {run} ({parsed[-1]['ts']})")
    if deferred:
        return Report(ok=not problems, newest=[], deferred_to=recording_run,
                      deferred_falls=newest, older_unaccounted=older_unaccounted,
                      older_accounted=older_accounted, transitions=len(lines) - 1,
                      problems=problems, span=span)
    reason = accepted.get(run, "") if newest else ""
    ok = not problems and (not newest or bool(reason))
    return Report(ok=ok, newest=newest, accepted_reason=reason,
                  older_unaccounted=older_unaccounted, older_accounted=older_accounted,
                  transitions=len(lines) - 1, problems=problems, span=span)


def inversions(truth_lines: Sequence[str], falls_text: str,
               changed: Callable[[str, str], set[str] | None]) -> tuple[int, int]:
    """(inverted, transitions) -- ticket 108's defect as a number over the whole recorded log.

    An INVERSION is a run whose own recording commit turned this comparison from green to red:
    before the append the graded transition was the one ending at the previous line and it was
    clean or accepted; after it, the graded transition is this run's and it falls unaccounted.
    That is the state `[skip ci]` then freezes, because no run measures the tree the recording
    commit made. Counted, never asserted: the day the number is 0 the coupling has gone.
    """
    accepted, _ = parse_falls(falls_text)
    lines = [l for l in truth_lines if l.startswith("TRUTH ")]
    parsed = [parse_truth(l) for l in lines]
    red: list[bool] = []
    for i in range(len(lines) - 1):
        fallen = bool(compare(lines[i], lines[i + 1],
                              changed(str(parsed[i]["hub"]), str(parsed[i + 1]["hub"]))))
        red.append(fallen and str(parsed[i + 1]["run"]) not in accepted)
    return sum(1 for i, r in enumerate(red) if r and (i == 0 or not red[i - 1])), len(red)


# ------------------------------------------------------------------ git, the one impure part

def _meaning(text: str) -> list[str]:
    """A record file's meaning: its lines with comments and blanks removed.

    Both files this module consults are read that way by the code that owns them --
    talk/truth_manifest.py's parse_manifest and talk/verify-all.sh's exclusion reader both take
    the text before the first `#` -- so normalising the same way is not a guess about the format.
    """
    out = []
    for raw in text.splitlines():
        body = raw.split("#", 1)[0].strip()
        if body:
            out.append(body)
    return out


def material_paths(before: dict[str, str], after: dict[str, str]) -> set[str]:
    """The files whose MEANING moved, not the files that were touched (review F5, 2026-09-06).

    The ceiling and total excuses were graded by file NAME, so any commit in the span that
    retyped a comment in the manifest excused any ceiling drop at all -- and this repository
    edits those comments constantly. A file added or removed in the span is material by
    definition."""
    moved = set()
    for path in set(before) | set(after):
        if path not in before or path not in after:
            moved.add(path)
        elif _meaning(before[path]) != _meaning(after[path]):
            moved.add(path)
    return moved


def git_changed(root: str) -> Callable[[str, str], set[str] | None]:
    """The record files whose meaning moved between two commits, or None if this checkout cannot
    read them at all."""

    def show(commit: str, path: str) -> str | None:
        try:
            out = subprocess.run(["git", "-C", root, "show", f"{commit}:{path}"],
                                 capture_output=True, text=True, check=False)
        except OSError:
            return None
        return out.stdout if out.returncode == 0 else None

    def changed(a: str, b: str) -> set[str] | None:
        if not a or not b:
            return None
        # ONE commit per call: `git rev-parse --verify` takes exactly one parameter and exits 128
        # on two, so the two-argument form said "unreadable" for every span and turned both
        # excused states into falls. Caught by the fixture the moment the material-change rule
        # landed, which is what the fixture is for.
        for commit in (a, b):
            try:
                probe = subprocess.run(["git", "-C", root, "rev-parse", "--verify",
                                        f"{commit}^{{commit}}"],
                                       capture_output=True, text=True, check=False)
            except OSError:
                return None
            if probe.returncode != 0:
                return None                   # a commit this checkout does not carry
        before: dict[str, str] = {}
        after: dict[str, str] = {}
        for path in (MANIFEST_FILE, EXCLUSIONS_FILE):
            was, now = show(a, path), show(b, path)
            if was is not None:
                before[path] = was
            if now is not None:
                after[path] = now
        return material_paths(before, after)

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
    # review F5: a hash inside a reason survives; only a whole-line comment is a comment
    assert parse_falls("run=105 | issue #12 reddened it\n")[0] == {"105": "issue #12 reddened it"}
    assert parse_falls("  # run=1 | not real\nrun=2 | real\n")[0] == {"2": "real"}
    # review F3: a re-class of a passing script is a fall, and is not called a lost look
    reclass = compare(line("1", observed=10, meta=3), line("2", observed=9, meta=4),
                      {MANIFEST_FILE})
    assert [x.kind for x in reclass] == ["class-pass"]
    assert "between classes" in reclass[0].detail
    assert "became a could-not-look" not in reclass[0].detail
    # review F5: meaning, not file names
    assert material_paths({MANIFEST_FILE: "a.sh | meta | -  # one\n"},
                          {MANIFEST_FILE: "a.sh | meta | -  # two\n"}) == set()
    assert material_paths({MANIFEST_FILE: "a.sh | meta | -\n"},
                          {MANIFEST_FILE: "a.sh | self-proof | -\n"}) == {MANIFEST_FILE}
    # review F5: a reason for a transition that did not fall is a fault
    flat = report([line("1"), line("2"), line("3")], "run=2 | nothing fell", lambda a, b: set())
    assert not flat.ok and any("did not fall" in q for q in flat.problems)

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

    # ---- ticket 108: the transition graded is the one ending at the RUN BEING RECORDED --------
    flat_then_fall = [line("1", observed=10), line("2", observed=10),
                      line("3", observed=9, waits=4)]
    # no run in flight: the newest recorded transition is the run being recorded. Unchanged.
    r = report(flat_then_fall, "", lambda a, b: set())
    assert not r.ok and [x.kind for x in r.newest] == ["class-pass"] and not r.deferred_to
    # the run being recorded IS the newest recorded line (truth.yml's step, after the cage):
    # identical, and the fall still blocks. This is the stop, and this change does not touch it.
    r = report(flat_then_fall, "", lambda a, b: set(), recording_run="3")
    assert not r.ok and [x.kind for x in r.newest] == ["class-pass"] and not r.deferred_to
    # the run being recorded has NO line yet (the gate of a clock run): deferred. The older
    # transition is still compared and still printed -- nothing stops looking -- and counted.
    r = report(flat_then_fall, "", lambda a, b: set(), recording_run="4")
    assert r.ok and r.deferred_to == "4" and r.newest == []
    assert [x.kind for x in r.deferred_falls] == ["class-pass"]
    assert r.older_unaccounted == 1
    # a malformed escape hatch is STILL a fault while deferred: the append cannot fix a hole
    assert not report(flat_then_fall, "run=99 | not recorded", lambda a, b: set(),
                      recording_run="4").ok
    # the run being recorded is in the log but is not the newest: the log moved under the run
    r = report(flat_then_fall, "", lambda a, b: set(), recording_run="2")
    assert not r.ok and any("moved under this run" in q for q in r.problems)
    # review F5b: the defer key is validated before it is used, never deferred on
    r = report(flat_then_fall, "", lambda a, b: set(), recording_run="abc")
    assert not r.ok and not r.deferred_to and any("not a run number" in q for q in r.problems)
    assert [x.kind for x in r.newest] == ["class-pass"]        # it graded, it did not shrug
    # `0200` is run 200, not a run the log has never heard of
    assert report(flat_then_fall, "", lambda a, b: set(), recording_run="003").ok is False
    assert report(flat_then_fall, "", lambda a, b: set(),
                  recording_run="003").deferred_to == ""
    assert _run_key("0200") == "200" and _run_key("fixture-2") == "fixture-2"

    # ---- ticket 108: the coupling, counted ---------------------------------------------------
    # run 3's own recording commit is what turns the comparison red: before it the graded
    # transition (1 -> 2) was clean.
    assert inversions(flat_then_fall, "", lambda a, b: set()) == (1, 2)
    # a committed reason removes it from the count as well as from the grade
    assert inversions(flat_then_fall, "run=3 | accepted", lambda a, b: set()) == (0, 2)
    # a fall that stays red across two recordings inverted once, not twice
    stays = flat_then_fall + [line("4", observed=8, waits=5)]
    assert inversions(stays, "", lambda a, b: set()) == (1, 3)
    assert inversions([line("1")], "", lambda a, b: set()) == (0, 0)
    print("selfcheck ok")


# ------------------------------------------------------------------ cli

def _render(rep: Report) -> None:
    for p in rep.problems:
        print(f"FAIL falls: {p}")
    if rep.note:
        print(f"  {rep.note}")
        if rep.deferred_to:
            print(f"  DEFERRED: the run being recorded is {rep.deferred_to} and its line is not "
                  f"in the log yet; the transition ending at it is graded by truth.yml's `a fall "
                  f"is a blocking event` step, after the cage records the line (ticket 108)")
        return
    if rep.deferred_to:
        print(f"  DEFERRED: the run being recorded is {rep.deferred_to}. Its TRUTH line is not in "
              f"talk/truth.log yet -- and cannot be, because this comparison's own verdict is one "
              f"of the counts in it -- so the transition ending at it is graded by truth.yml's "
              f"`a fall is a blocking event` step once the cage has recorded the line (ticket "
              f"108). What follows is the newest RECORDED transition, which the run "
              f"that recorded it already graded and blocked on: it is compared and "
              f"printed here, and never faulted here, because re-grading it writes "
              f"another run's red into this run's grade row, where "
              f"verify/derived-status/ reads it as a live regression.")
    print(f"  newest recorded transition: {rep.span}")
    shown = rep.newest or rep.deferred_falls
    if not shown:
        print("  no fall: no class lost a pass, `fail` did not rise, and neither the ceiling "
              "nor the total fell unexplained")
    label = ("fall, already graded by the run that recorded it:" if rep.deferred_to
             else "FALL")
    for f in shown:
        print(f"  {label} {f}")
    if shown and rep.accepted_reason:
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
    # NOT read from the environment inside this module, on purpose (ticket 108). The gate's
    # fixture lifts truth.yml's own step shell and runs it over planted logs whose runs are named
    # `fixture-N`; a GITHUB_RUN_NUMBER picked up implicitly would defer every one of those states
    # in CI and grade nothing. The caller that knows it is inside a run says so.
    c.add_argument("--recording-run", default="",
                   help="the run this process belongs to; empty means no run is in flight and "
                        "the newest recorded line is the run being recorded")
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
    changed = git_changed(a.root)
    rep = report(lines, falls_text, changed, recording_run=a.recording_run)
    _render(rep)
    inverted, spans = inversions(lines, falls_text, changed)
    print(f"  the recording commit's reach: {inverted} of {spans} recorded transition(s) went "
          f"from green to red at the moment the run recorded its own line (ticket 108). That is "
          f"the window this split does not close: a fall is still graded twice, once by the run "
          f"that records it and once by every later checkout of the record, and `[skip ci]` "
          f"means no run measures the tree the recording commit made")
    return 0 if rep.ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
