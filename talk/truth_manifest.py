#!/usr/bin/env python3
"""The verify manifest: what each script in the gate measures (eco-system ticket 83).

`pass=57 fail=7 skip=18 total=84` cannot tell a loosely coupled eco-system from one party
testing itself. This module is the one place the arithmetic behind the TRUTH line lives.
talk/verify-all.sh calls it (check, paths, judge, summarise) and talk/build_deck.py imports it
(parse_truth, measured), so the split is computed once and quoted, never re-derived by hand.

THE MANIFEST  talk/verify-manifest.txt, one line per script the gate discovers:

    path | class | skip        # a trailing comment is the place for a borderline note

  class       estate-observation  the verdict turns on the CONTENT of another party's artefact
                                  (a pin resolving on a real remote, a price moving with a
                                  parent's feed, a catalogue's control ids) or on live state
                                  outside the script's own repository. Using another party's
                                  schema or engine as the ruler to grade your OWN artefact is
                                  not an observation of the estate: that is self-proof.
              self-proof          a party grading its own code, fixtures or artefacts.
              simulation          the material is synthetic or throwaway (a scratch repo, a
                                  planted residual), and the script says so in its own verdict.
              meta                the script grades other checks or the record, not the estate.
  skip        -                   no could-not-look is expected on the runner. One that happens
                                  is UNDECLARED and fails the gate.
              never: <pattern>    this script cannot pass on the scheduled runner as the runner
                                  is built (no persistent cluster, no cross-org credential). It
                                  is outside the CEILING.
              waits: <pattern>    the estate's own state has not arrived yet (one declared
                                  version line, a tag not cut, a lane sample not landed). Inside
                                  the ceiling: the day the state arrives, the script can pass.
              <pattern> is a python regular expression matched case-insensitively (re.search)
              against the script's LAST line when it exits 3. A SKIP line the pattern does not
              match is undeclared and fails the gate, so a new reason for not looking cannot
              hide inside an old declaration. The skip column runs to the end of the line, so
              alternation (`a|b`) is fine; '#' starts a comment and cannot appear in a pattern.

  A script in talk/verify-exclusions.txt is declared there (it is not run); a manifest line for
  it is allowed and inert, and says what the script would have measured had it run. Every other
  discovered script must have a manifest line -- that direction fails the gate, because a
  surface that grows without its record lets the number lie. The other direction is asymmetric:
  a hub line naming a script that is gone fails (hub script and hub line are committed
  together), while a `.estate-clone/` line naming a script this checkout of the unit does not
  carry is a NOTE, since a unit publishes on its own train. See coverage_problems().

THE TRUTH LINE  what talk/verify-all.sh prints, and what parse_truth reads back:

    TRUTH <utc> run=N hub=H units=[u=sha ...] pass=P [observed=a self=b simulated=c meta=d]
      fail=F skip=S [never=x waits=y] excluded=E total=T ceiling=C [live=1] [fixture=1]

  a+b+c+d == P (the split is of PASSES, by manifest class)
  x+y == S     (the split is of SKIPS, by the manifest's skip kind; both declared)
  C == T - E - (number of run scripts whose manifest line says never)
  T - E - C is therefore the never-classed POPULATION, and it equals x only when every
  never-classed script skipped. One that fails instead makes x smaller. measured() states
  T - E - C when it says how many can never pass, and x only inside the skip split, so the
  published sentence adds up whatever the never-classed scripts did.
  A `never` script that passes is a FAIL (the ceiling it was excluded from is stale; fix the
  manifest). A script that passes with no manifest line is a FAIL (the split cannot place it).
  `fixture=1` marks a run over a fixture list (the selfcheck) and is never citable.
  `units=[...]` is written by verify-all.sh; ticket 77 adds the tag beside each sha there and
  parse_truth keeps the text of each unit's value, so that seam is clean.

CONTRACT FOR TICKET 59 (the fall-checker), so it can build without reopening this ticket:
  - Read two consecutive TRUTH lines with parse_truth(); compare class by class. A FALL is any
    of: a class's pass count lower than the previous line's; fail higher; ceiling lower with no
    manifest change in the same commit; total lower with no exclusions change. A pass that
    became a skip inside one class is a fall even when fail is unchanged.
  - The escape hatch mirrors the exclusions file: a committed `talk/verify-falls.txt` of
    `run=N | reason` lines, one per accepted fall, validated the way exclusions are (a line
    naming a run the log does not record is itself a fail).
  - The manifest is the shared input: never re-derive a class from a script header at check
    time; read this file through load_manifest().
  This module deliberately implements parse_truth() and nothing of the comparison.

  python3 talk/truth_manifest.py check MANIFEST [--exclusions FILE] [--scripts FILE]
      validate; print one `FAIL manifest: ...` line per problem and one `NOTE manifest: ...`
      per unit line whose script is not in this checkout; exit 1 if there is any problem
  python3 talk/truth_manifest.py paths MANIFEST
      the valid manifest paths, one per line (a malformed line is dropped, and was reported)
  python3 talk/truth_manifest.py judge MANIFEST PATH "LAST LINE"
      exit 0 `declared <kind>` or exit 1 `undeclared: <why>`
  python3 talk/truth_manifest.py isnever MANIFEST PATH
      exit 0 if the manifest says this script can never pass on the runner, else 1 (silent);
      verify-all.sh asks before printing a PASS, so a stale ceiling is visible in the row too
  python3 talk/truth_manifest.py summarise MANIFEST RESULTS [--extra-fail N]
      RESULTS is `path<TAB>STATUS<TAB>last line` rows (PASS/SKIP/FAIL/EXCLUDED); prints any
      manifest-driven FAIL rows, then the counts fragment as the last line; exit 1 if fail>0
  python3 talk/truth_manifest.py selfcheck
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass

CLASSES = {"estate-observation": "observed", "self-proof": "self", "simulation": "simulated",
           "meta": "meta"}
SPLIT_KEYS = tuple(CLASSES.values())          # observed self simulated meta, in TRUTH order
SKIP_KINDS = ("never", "waits")
MANIFEST_NAME = "talk/verify-manifest.txt"


class ManifestError(Exception):
    """Every problem in the file at once, one per line, so a builder fixes them in one go."""

    def __init__(self, problems: list[str]) -> None:
        super().__init__("\n".join(problems))
        self.problems = problems


@dataclass(frozen=True)
class Entry:
    path: str
    cls: str
    skip_kind: str | None      # never | waits | None
    pattern: str | None

    @property
    def split_key(self) -> str:
        return CLASSES[self.cls]

    def declares(self, last_line: str) -> bool:
        return bool(self.pattern) and re.search(self.pattern or "", last_line, re.I) is not None


# ------------------------------------------------------------------ the manifest

def parse_manifest(text: str) -> tuple[dict[str, Entry], list[str]]:
    """(entries by path, problems). A malformed line is reported and dropped, never guessed."""
    entries: dict[str, Entry] = {}
    problems: list[str] = []
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        cols = [c.strip() for c in line.split("|", 2)]     # the skip column keeps its '|'
        if len(cols) < 3:
            problems.append(f"line {n}: needs `path | class | skip`, got {raw.strip()!r}")
            continue
        path, cls, skip = cols
        if not path:
            problems.append(f"line {n}: empty path")
            continue
        if path in entries:
            problems.append(f"line {n}: {path} is listed twice")
            continue
        if cls not in CLASSES:
            problems.append(f"line {n}: {path}: class {cls!r} is not one of "
                            f"{', '.join(CLASSES)}")
            continue
        kind: str | None = None
        pattern: str | None = None
        if skip != "-":
            m = re.fullmatch(r"(never|waits)\s*:\s*(.+)", skip)
            if not m:
                problems.append(f"line {n}: {path}: skip must be `-`, `never: <pattern>` or "
                                f"`waits: <pattern>`, got {skip!r}")
                continue
            kind, pattern = m.group(1), m.group(2).strip()
            try:
                re.compile(pattern)
            except re.error as e:
                problems.append(f"line {n}: {path}: the skip pattern does not compile ({e})")
                continue
        entries[path] = Entry(path, cls, kind, pattern)
    return entries, problems


def load_manifest(path: str) -> dict[str, Entry]:
    """The manifest, or ManifestError carrying every problem."""
    with open(path, encoding="utf-8") as fh:
        entries, problems = parse_manifest(fh.read())
    if problems:
        raise ManifestError(problems)
    return entries


def parse_exclusions(text: str) -> dict[str, str]:
    """`path | reason` lines, as talk/verify-all.sh reads them. Validation stays in the shell
    (it predates this file); this reader only needs the paths."""
    out: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.split("#", 1)[0]
        if not line.strip():
            continue
        p, _, r = line.partition("|")
        out[p.strip()] = r.strip()
    return out


def coverage_problems(entries: dict[str, Entry], scripts: list[str],
                      excluded: dict[str, str],
                      exists=os.path.exists) -> tuple[list[str], list[str], list[str]]:
    """(problems, row_level, notes), both directions, but not symmetrically.

    A discovered script with no line is a fail: its grade cannot be placed in the split, so the
    surface would grow without the record of what it measures growing with it. That is the
    direction that lets the number lie. It comes back separately as ROW_LEVEL because the gate
    also prints a FAIL row for that script whatever it exited, and one wrong script must be
    counted once.

    A line naming a script that is not in this checkout is a NOTE for a unit and a PROBLEM for
    the hub (delegated, ADR-0025, 2026-09-04). The hub commits a verify script and its manifest
    line in the same commit, so a hub line with no script is rot. A unit is an independently
    versioned repository the hub only clones: a script that exists on the unit's build branch
    and not yet on its main is the normal state of this eco-system between the builder's commit
    and the owner's push, and failing the gate for it would make the hub's record hostage to
    another party's release train -- the thing NORTH-STAR §2 says the platform must never be.
    The note is printed on every run, so the rot is still loud."""
    problems: list[str] = []
    row_level: list[str] = []
    notes: list[str] = []
    for s in scripts:
        if s not in entries and s not in excluded:
            row_level.append(f"{s} is discovered but has no line in {MANIFEST_NAME}; add "
                             f"`{s} | <class> | -` (or a declared skip) so its grade can be "
                             f"placed")
    for p in entries:
        if exists(p):
            continue
        if p.startswith(".estate-clone/"):
            notes.append(f"{p} is listed in {MANIFEST_NAME} but is not in this checkout of the "
                         f"unit; it is graded on the run where the unit publishes it")
        else:
            problems.append(f"{p} is listed in {MANIFEST_NAME} but no longer exists; remove it")
    return problems, row_level, notes


def judge(entries: dict[str, Entry], path: str, last_line: str) -> tuple[bool, str]:
    """(declared?, why) for a script that exited 3 with `last_line`."""
    e = entries.get(path)
    if e is None:
        return False, f"{path} has no line in {MANIFEST_NAME}"
    if e.skip_kind is None:
        return False, (f"{MANIFEST_NAME} declares no skip for {path} (skip column is `-`); "
                       f"declare `never:` or `waits:` with a pattern, or make it look")
    if not e.declares(last_line):
        return False, (f"the SKIP line does not match the {e.skip_kind} pattern "
                       f"{e.pattern!r} in {MANIFEST_NAME}; a new reason for not looking must "
                       f"be declared there")
    return True, f"declared {e.skip_kind}"


# ------------------------------------------------------------------ the arithmetic

@dataclass
class Summary:
    passed: int
    split: dict[str, int]
    failed: int
    skipped: int
    skip_split: dict[str, int]
    excluded: int
    total: int
    ceiling: int
    extra_rows: list[str]

    def fragment(self) -> str:
        split = " ".join(f"{k}={self.split[k]}" for k in SPLIT_KEYS)
        skips = " ".join(f"{k}={self.skip_split[k]}" for k in SKIP_KINDS)
        return (f"pass={self.passed} [{split}] fail={self.failed} skip={self.skipped} [{skips}] "
                f"excluded={self.excluded} total={self.total} ceiling={self.ceiling}")


def parse_results(text: str) -> list[tuple[str, str, str]]:
    rows = []
    for raw in text.splitlines():
        if not raw.strip():
            continue
        parts = raw.split("\t", 2)
        while len(parts) < 3:
            parts.append("")
        rows.append((parts[0], parts[1], parts[2]))
    return rows


def summarise(entries: dict[str, Entry], rows: list[tuple[str, str, str]],
              extra_fail: int = 0) -> Summary:
    """The counts, from the rows the gate recorded and the manifest. This is the only counter.

    A row's STATUS is what the gate printed for it. Two manifest-driven corrections are made
    here, each producing a FAIL row the gate prints before the TRUTH line: a PASS with no
    manifest line (cannot be placed in the split) and a PASS from a `never` script (the
    ceiling that excluded it is stale). Everything else is counted as recorded."""
    split = {k: 0 for k in SPLIT_KEYS}
    skip_split = {k: 0 for k in SKIP_KINDS}
    passed = failed = skipped = excluded = 0
    never = 0
    extra: list[str] = []
    for path, status, last in rows:
        e = entries.get(path)
        if status == "EXCLUDED":
            excluded += 1
            continue
        if e is not None and e.skip_kind == "never":
            never += 1
        if status == "PASS":
            if e is None:
                failed += 1
                extra.append(f"FAIL manifest: {path} passed but has no line in {MANIFEST_NAME}, "
                             f"so the split cannot place it; add `{path} | <class> | -`")
            elif e.skip_kind == "never":
                failed += 1
                extra.append(f"FAIL manifest: {path} passed, but {MANIFEST_NAME} says it can "
                             f"never pass on this runner -- the ceiling is stale; change its "
                             f"skip column")
            else:
                passed += 1
                split[e.split_key] += 1
        elif status == "SKIP":
            skipped += 1
            kind = e.skip_kind if e is not None and e.skip_kind else "waits"
            skip_split[kind] += 1
        else:
            failed += 1
    failed += extra_fail
    total = len(rows)
    return Summary(passed, split, failed, skipped, skip_split, excluded, total,
                   total - excluded - never, extra)


# ------------------------------------------------------------------ the line, read back

_KV = re.compile(r"\b(\w+)=(\[[^\]]*\]|\S+)")


def parse_truth(line: str) -> dict:
    """A TRUTH line as a dict. Old lines (no split, no ceiling) parse too: their `split`,
    `skip_split` and `ceiling` are None, so a reader can tell "unmeasured" from zero.

    Keys: ts, run, hub, units (dict unit -> text after '='), pass, split (dict by SPLIT_KEYS),
    fail, skip, skip_split (dict by SKIP_KINDS), excluded, total, ceiling, live, fixture."""
    line = line.strip()
    if not line.startswith("TRUTH "):
        raise ValueError("not a TRUTH line")
    m = re.match(r"TRUTH (\S+)", line)
    out: dict = {"ts": m.group(1) if m else "", "split": None, "skip_split": None,
                 "ceiling": None, "live": False, "fixture": False, "units": {}}
    counts = {}
    for key, val in _KV.findall(line):
        counts[key] = val
    out["run"] = counts.get("run", "")
    out["hub"] = counts.get("hub", "")
    units_txt = counts.get("units", "[]").strip("[]")
    for tok in units_txt.split():
        u, _, v = tok.partition("=")
        out["units"][u] = v
    for k in ("pass", "fail", "skip", "excluded", "total"):
        out[k] = int(counts[k]) if k in counts and counts[k].isdigit() else None
    if "ceiling" in counts and counts["ceiling"].isdigit():
        out["ceiling"] = int(counts["ceiling"])
    out["live"] = counts.get("live") == "1"
    out["fixture"] = counts.get("fixture") == "1"
    sp = re.search(r"\bpass=\d+ \[([^\]]*)\]", line)
    if sp:
        out["split"] = {k: int(v) for k, v in re.findall(r"(\w+)=(\d+)", sp.group(1))}
    sk = re.search(r"\bskip=\d+ \[([^\]]*)\]", line)
    if sk:
        out["skip_split"] = {k: int(v) for k, v in re.findall(r"(\w+)=(\d+)", sk.group(1))}
    return out


def measured(line: str) -> str:
    """The sentence the deck quotes under a TRUTH line: the split and the ceiling in words,
    computed from the line itself so the deck cannot state a split the line does not carry."""
    t = parse_truth(line)
    if t["split"] is None or t["ceiling"] is None:
        return (f"measured: run {t['run']}'s line carries no split and no ceiling; "
                f"{MANIFEST_NAME} landed after it (ticket 83), so the bare count "
                f"pass={t['pass']} of total={t['total']} is all that run says about itself")
    s, k = t["split"], t["skip_split"] or {}
    # Two different `never` numbers, and the sentence has to use the ceiling's one. The skip
    # split's `never` counts only the never-classed scripts that SKIPPED; the ceiling subtracts
    # every non-excluded never-classed script, however it exited. A never-classed script that
    # fails instead of skipping makes the two diverge, and the published sentence then stops
    # adding up. total - excluded - ceiling recovers the ceiling's own population from the line.
    never_pop = t["total"] - t["excluded"] - t["ceiling"]
    never_skipped = k.get("never", 0)
    parts = " + ".join(f"{key} {s.get(key, 0)}" for key in SPLIT_KEYS)
    return (f"measured: {t['pass']} passes are {parts}, against a ceiling of {t['ceiling']} "
            f"of {t['total']} ({t['excluded']} excluded, {never_pop} can never pass on this "
            f"runner); fail {t['fail']}, skip {t['skip']} (never {never_skipped}, "
            f"waits {k.get('waits', 0)})")


# ------------------------------------------------------------------ selfcheck

def selfcheck() -> None:
    good = ("a/verify-a.sh | estate-observation | -\n"
            "b/verify-b.sh | self-proof | never: kind cluster 'x' (is not listed|does not exist)\n"
            "c/verify-c.sh | simulation | waits: declares one version   # borderline: note\n"
            "d/verify-d.sh | meta | -   # trailing comment\n")
    entries, problems = parse_manifest(good)
    assert problems == [], problems
    assert set(entries) == {"a/verify-a.sh", "b/verify-b.sh", "c/verify-c.sh", "d/verify-d.sh"}
    assert entries["b/verify-b.sh"].skip_kind == "never"
    assert entries["b/verify-b.sh"].pattern == "kind cluster 'x' (is not listed|does not exist)"
    assert entries["d/verify-d.sh"].split_key == "meta"

    bad = ("x/verify-x.sh | unit-test | -\n"          # not a class
           "y/verify-y.sh | meta | sometimes: foo\n"  # not a skip kind
           "y/verify-y.sh | meta | -\n"               # duplicate (first was dropped, so this is the entry)
           "z/verify-z.sh | meta\n"                    # too few columns
           "w/verify-w.sh | meta | never: (unclosed\n")
    entries, problems = parse_manifest(bad)
    assert len(problems) == 4, problems
    assert any("not one of" in p for p in problems)
    assert any("skip must be" in p for p in problems)
    assert any("needs `path | class | skip`" in p for p in problems)
    assert any("does not compile" in p for p in problems)

    # judge: declared by pattern, undeclared by a new reason, undeclared with no skip column
    entries, _ = parse_manifest(good)
    assert judge(entries, "b/verify-b.sh", "SKIP: kind cluster 'x' is not listed here")[0]
    assert judge(entries, "b/verify-b.sh", "SKIP: Kind Cluster 'x' does not exist")[0]
    ok, why = judge(entries, "b/verify-b.sh", "SKIP: the API server returned no pods")
    assert not ok and "does not match" in why, why
    ok, why = judge(entries, "a/verify-a.sh", "SKIP: anything")
    assert not ok and "declares no skip" in why, why
    ok, why = judge(entries, "nope/verify-nope.sh", "SKIP: anything")
    assert not ok and "no line" in why, why

    # coverage: an undiscovered script fails; a hub line with no script fails; a unit line whose
    # script is not in this checkout is a note
    entries2, _ = parse_manifest(good + ".estate-clone/u/verify-u.sh | meta | -\n")
    probs, rows_, notes = coverage_problems(
        entries2, ["a/verify-a.sh", "e/verify-e.sh", "ex/verify.sh"], {"ex/verify.sh": "helper"},
        exists=lambda p: p not in ("d/verify-d.sh", ".estate-clone/u/verify-u.sh"))
    assert len(probs) == 1 and "d/verify-d.sh" in probs[0], probs
    assert len(rows_) == 1 and "e/verify-e.sh" in rows_[0], rows_
    assert len(notes) == 1 and "verify-u.sh" in notes[0], notes

    # arithmetic: the split sums to pass; ceiling = total - excluded - never; a never that
    # passes and a pass with no line are both fails, with a row each
    rows = [("a/verify-a.sh", "PASS", ""), ("b/verify-b.sh", "SKIP", "SKIP: kind cluster"),
            ("c/verify-c.sh", "SKIP", "SKIP: declares one version"), ("d/verify-d.sh", "FAIL", ""),
            ("ex/verify.sh", "EXCLUDED", ""), ("un/verify-un.sh", "PASS", "")]
    s = summarise(entries, rows)
    assert s.fragment() == ("pass=1 [observed=1 self=0 simulated=0 meta=0] fail=2 skip=2 "
                            "[never=1 waits=1] excluded=1 total=6 ceiling=4"), s.fragment()
    assert len(s.extra_rows) == 1 and "no line" in s.extra_rows[0]
    rows[1] = ("b/verify-b.sh", "PASS", "")
    s = summarise(entries, rows, extra_fail=1)
    assert s.failed == 4 and s.passed == 1 and any("stale" in r for r in s.extra_rows), s
    assert sum(s.split.values()) == s.passed

    # the line, read back, old and new shapes
    old = ("TRUTH 2026-09-03T19:09Z run=23 hub=b75eecb units=[driftwood=4b28aa3 feeds=69c89b0] "
           "pass=58 fail=7 skip=18 excluded=2 total=85")
    t = parse_truth(old)
    assert (t["run"], t["hub"], t["pass"], t["total"]) == ("23", "b75eecb", 58, 85)
    assert t["units"] == {"driftwood": "4b28aa3", "feeds": "69c89b0"}
    assert t["split"] is None and t["ceiling"] is None and not t["fixture"]
    assert "carries no split" in measured(old) and "pass=58 of total=85" in measured(old)
    new = ("TRUTH 2026-09-05T05:47Z run=24 hub=abc1234 units=[driftwood=4b28aa3@v1.2.0] "
           "pass=57 [observed=20 self=31 simulated=5 meta=1] fail=7 skip=18 [never=12 waits=6] "
           "excluded=2 total=84 ceiling=70 live=1 fixture=1")
    t = parse_truth(new)
    assert t["split"] == {"observed": 20, "self": 31, "simulated": 5, "meta": 1}
    assert t["skip_split"] == {"never": 12, "waits": 6} and t["ceiling"] == 70
    assert t["units"] == {"driftwood": "4b28aa3@v1.2.0"}      # ticket 77's seam: text kept
    assert t["live"] and t["fixture"]
    m = measured(new)
    assert m.startswith("measured: 57 passes are observed 20 + self 31 + simulated 5 + meta 1")
    assert "ceiling of 70 of 84 (2 excluded, 12 can never pass on this runner)" in m
    assert "skip 18 (never 12, waits 6)" in m

    # a never-classed script that FAILED instead of skipping: the skip split's never (1) is
    # smaller than the ceiling's population (11 - 1 - 7 = 3). The sentence must state 3.
    diverged = ("TRUTH 2026-09-04T12:00Z run=71 hub=abc1234 units=[platform=46cd775] "
                "pass=5 [observed=2 self=2 simulated=1 meta=0] fail=3 skip=2 [never=1 waits=1] "
                "excluded=1 total=11 ceiling=7")
    m = measured(diverged)
    assert "ceiling of 7 of 11 (1 excluded, 3 can never pass on this runner)" in m, m
    assert "skip 2 (never 1, waits 1)" in m, m
    print("selfcheck ok")


# ------------------------------------------------------------------ cli

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check"); c.add_argument("manifest")
    c.add_argument("--exclusions"); c.add_argument("--scripts")
    p = sub.add_parser("paths"); p.add_argument("manifest")
    j = sub.add_parser("judge"); j.add_argument("manifest"); j.add_argument("path")
    j.add_argument("last")
    n = sub.add_parser("isnever"); n.add_argument("manifest"); n.add_argument("path")
    s = sub.add_parser("summarise"); s.add_argument("manifest"); s.add_argument("results")
    s.add_argument("--extra-fail", type=int, default=0)
    sub.add_parser("selfcheck")
    a = ap.parse_args(argv)

    if a.cmd == "selfcheck":
        selfcheck()
        return 0
    with open(a.manifest, encoding="utf-8") as fh:
        entries, problems = parse_manifest(fh.read())
    if a.cmd == "check":
        excluded: dict[str, str] = {}
        if a.exclusions and os.path.exists(a.exclusions):
            with open(a.exclusions, encoding="utf-8") as fh:
                excluded = parse_exclusions(fh.read())
        scripts: list[str] = []
        if a.scripts:
            with open(a.scripts, encoding="utf-8") as fh:
                scripts = [l.strip() for l in fh if l.strip()]
        more, row_level, notes = coverage_problems(entries, scripts, excluded)
        problems += more
        for pr in problems:
            print(f"FAIL manifest: {pr}")
        for pr in row_level:
            # `[row]`: the script has a FAIL row of its own below, whatever it exited, so the
            # gate counts this one there and not here. Without the marker the same red would be
            # counted twice and fail= would overstate how many scripts are wrong.
            print(f"FAIL manifest[row]: {pr}")
        for note in notes:
            print(f"NOTE manifest: {note}")
        return 1 if problems or row_level else 0
    if a.cmd == "paths":
        for path in entries:
            print(path)
        return 0
    if a.cmd == "isnever":
        e = entries.get(a.path)
        return 0 if e is not None and e.skip_kind == "never" else 1
    if a.cmd == "judge":
        ok, why = judge(entries, a.path, a.last)
        print(why if ok else f"undeclared: {why}")
        return 0 if ok else 1
    if a.cmd == "summarise":
        with open(a.results, encoding="utf-8") as fh:
            rows = parse_results(fh.read())
        summary = summarise(entries, rows, a.extra_fail)
        for row in summary.extra_rows:
            print(row)
        print(summary.fragment())
        return 1 if summary.failed else 0
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
