#!/usr/bin/env python3
"""The map matches the surface (eco-system ticket 67 item (d), widened).

THE DEFECT THIS EXISTS FOR. `.scratch/ecosystem/map.md` is the one live wayfinder: a reader who
wants to know what this estate is starts there. On 2026-08-31 the ambition review found it saying
"65 pass, 0 fail, 16 could-not-look of 83. Nothing is red." That figure was a local rehearsal. No
TRUTH line ever recorded it, and the citable line of the day read `pass=53 fail=7 skip=21`. The
map was corrected by hand at charting time. Correcting a map fixes a map; this module is what
refuses the next one.

THE RULE, in one sentence: a pass/fail figure the map quotes must be a figure `talk/truth.log`
actually recorded, and a check the map names must be one `talk/verify-all.sh` actually discovers.

HOW THIS COMPOSES WITH verify/cited-truth/ (ticket 80, PR 44). That module grades the same class
of claim -- a record citing a measurement that never measured the thing -- in
`.scratch/ecosystem/issues/*.md`, and its own docstring names `map.md` as out of its scope and
ticket 67(d)'s question. The two populations are disjoint and neither reads the other's files:
issues/*.md is 80's, map.md is this one's, and between them the ticket record and the wayfinder
are both covered. The composition point is the PARSER, not the rule: both resolve a citation
through `talk/truth_manifest.py`'s `parse_truth`, so there is one reader of the TRUTH line in the
estate and a change to the line's shape cannot make one of the two checks quietly wrong. This
module does not import 80's, so it stands whether or not PR 44 has merged.

WHAT IT GRADES, five rules over `.scratch/ecosystem/map.md`:

  1. FIGURES. Every pass/fail figure the map quotes -- `57/7/18 of 84`, `65 pass, 0 fail, 16
     could-not-look of 83`, or the `pass= fail= skip=` keys of a quoted TRUTH line -- must equal
     the corresponding figure of some line `talk/truth.log` records. Where a run is cited on the
     same text line it must be THAT run's figure, and a run the log never recorded is red.
  2. CHECKS. Every check the map names in backticks must be one the gate discovers, read from
     `talk/verify-manifest.txt` (which `talk/verify-all.sh` requires a row in for every script it
     runs). A map that names a check the gate does not run is a map of a different estate.
  3. LINKS. Every relative link in the map must resolve to a file that exists. "A reader
     following the map" is the ticket's own definition of done, and a dead link is the cheapest
     way to fail it.
  4. LANES. No unit repository may declare an `OBSERVATION_LANE` path it does not own (item (c)).
     The hub's four-path list was copied verbatim into twelve unit workflows across eight
     repositories. `verify/schedules/lane.py` grades every commit a scheduled identity landed in
     a repository against the union of THAT repository's own declarations, so a copied path is
     not cosmetic: it is a path a clock in that repository may land and be graded green for. It
     is also a promise the cage step reads, and none of the eight had ever owned all four.
     Read at `origin/main`, freshly fetched, and never at the checkout: see SERVED_REF.
  5. RECORD. Ticket 67's items (a) and (c) as literal facts the record must carry or must no
     longer carry, because a correction appended below a claim it never removed leaves the estate
     saying both things at once.

WHAT IT REFUSES TO GRADE, said plainly because a disclosed limit rots like any other claim:

  * whether the figure the map quotes is the RIGHT figure to quote, or whether the check it names
    is the right check. It grades that both exist on the surface: necessary, never sufficient.
  * item (b). `penalty-schema/bump.yaml` is graded by ico's OWN
    `.github/scripts/verify-declared-bump.sh`, which is in the manifest and is the script that
    would refuse a wrong number at release time. Reading a working copy of another party's
    declaration here would be the proxy this ticket exists to end.
  * a figure whose own text line says, in those words, `not citable`, or quotes the runner's own
    `fixture=1` or `run=local` token; and a figure disposed of by the DATED correction in the
    paragraph directly below it. Both are printed BY PATH AND LINE NUMBER on every run, not
    merely counted (review F1): an escape hatch nobody can see being used is one nobody audits.
    Three fixed phrases, not a bag of words, and a negated or code-span-quoted occurrence spends
    nothing -- see `_UNCITABLE` for the three ways the earlier bag laundered on this very map.
  * a key-shaped figure of one key with no run beside it. It identifies no line; the count of
    those is printed too.

WHAT IT NEVER SHRUGS AT. There is no could-not-look, by decision (delegated, ADR-0025,
2026-09-06), following `verify/can-record/` and `verify/cited-truth/`. Rules 1 to 3 and 5 read
only files in this repository; rule 4 reads `.estate-clone/` at `origin/main`, which
`clone-estate.sh` assembles and which `verify/schedules/verify-lane.sh` already refuses (exit 1)
rather than shrugs for. So every state in which this cannot see is RED with its own named line --
a missing unit, and a unit whose `origin/main` does not resolve -- and its manifest row declares
no skip pattern because there is none to declare.

    map_surface.py grade <hub-root>   # the five rules; 0 nothing false, 1 one or more named
    map_surface.py selfcheck          # planted defects grade as planted
"""
from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

HERE = Path(__file__).resolve().parent
HUB = HERE.parents[1]

MAP = ".scratch/ecosystem/map.md"
DRIFT_NORTH_STAR = ".scratch/drift-review-2026-08-27/NORTH-STAR.md"

# The three shapes a pass/fail figure takes in this record.
#   57/7/18 of 84
_SLASH = re.compile(r"\b(\d{1,4})/(\d{1,4})/(\d{1,4})\s+of\s+(\d{1,4})\b")
#   40 pass, 16 fail of 56   |   65 pass, 0 fail, 16 could-not-look of 83
_PROSE = re.compile(
    r"\b(\d{1,4})\s+pass(?:es)?,\s*(\d{1,4})\s+fail(?:s|ed)?"
    r"(?:,\s*(\d{1,4})\s+(?:could-not-look|skip|skips|skipped))?"
    r"\s+of\s+(\d{1,4})\b", re.I)
#   pass=53 fail=7 skip=21 excluded=2 total=83 ceiling=90
FIGURE_KEYS = ("pass", "fail", "skip", "excluded", "total", "ceiling")
_KEYS = re.compile(r"\b(" + "|".join(FIGURE_KEYS) + r")=(\d+)\b")

# A run citation is digits. `run=local` and `run=fixture` are not run numbers and never resolve;
# "the /implement run of 2026-08-28" has no digits after the word and is not a citation either.
_RUN = re.compile(r"\brun[= ](\d{1,4})\b", re.I)

# A dated correction. The date is required: an undated correction is a claim with no time on it.
_CORRECTION = re.compile(r"\*\*Correct(?:ed|ion)[^*]*?(\d{4}-\d{2}-\d{2})", re.I)

# THE ESCAPE HATCH (review F1, 2026-09-06). THREE FIXED PHRASES, not a bag of words, following
# verify/cited-truth/ which was fixed for this same defect at 09:00 the same morning.
#
# It used to be seven substrings -- local, rehearsal, fixture, planted, hypothetical, not citable,
# actions log -- matched anywhere on the line. Three ways that laundered, all reachable on THIS
# map: the word `local` appears on line 23 ("a local clock"), line 78 ("[92 -- The local clock]")
# and line 101 ("a local rehearsal"), so any figure ever added to one of those lines was exempt
# for good; a sentence asserting the OPPOSITE of a disclaimer ("and that is NOT a rehearsal")
# exempted itself; and `run 7 recorded 43/11/0 of 56 and was planted` excused a wrong run figure.
# Every one of those surfaced as +1 in a count and nothing more.
#
# A line that wants its figure ungraded now says `not citable`, in those words, or quotes the
# runner's own `fixture=1` or `run=local` token -- the two things talk/verify-all.sh itself writes
# on a line that is not a citable measurement. `_NEGATION` then rejects an occurrence that is
# itself negated; a phrase beginning "not" cannot negate itself, because only the text BEFORE an
# occurrence is examined.
_UNCITABLE = ("not citable", "fixture=1", "run=local")
# The negation must MODIFY the phrase, so the window is short: 12 characters, about one word.
_NEGATION = re.compile(r"(?:\bnot\b|\bno\b|\bwithout\b|\bnever\b)[^.]{0,12}$", re.I)
# A marker inside a `code span` or a [link](target) is QUOTING the phrase, not spending it. Both
# are blanked -- not deleted, so every offset the caller holds still lines up.
_CODE_SPAN = re.compile(r"`[^`\n]*`")
_LINK_TARGET = re.compile(r"\]\([^)\n]*\)")

# A backticked token that names a CHECK: a shell script whose basename starts with `verify`, or a
# directory under `verify/`. Deliberately not "any path with `verify` in it": `verify/schedules/
# lane.py` is a module the gate imports and `verify/deny-is-not-a-rung/register.yaml` is data, and
# neither is a script talk/verify-all.sh discovers, so neither belongs in this rule.
_CHECK_SCRIPT = re.compile(r"^(?:[\w.-]+/)*verify[\w.-]*\.sh$")
_CHECK_DIR = re.compile(r"^verify/(?:[\w.-]+/)*[\w-]+/?$")
_RUNNER = ("verify-all.sh",)


def _is_check_token(token: str) -> bool:
    return bool(_CHECK_SCRIPT.match(token) or _CHECK_DIR.match(token))


# There is NO hatch on rule 2 (review F4, 2026-09-06). It briefly had one -- a check the line
# declared "not yet merged" was counted rather than graded -- and the phrases were ordinary prose:
# map.md line 29 already contains "unmerged", so a check named there that existed NOWHERE was
# exempt. Unmerged work now goes red until it merges, exactly as the lane rule does, and the map
# says so in a sentence rather than in a word the check reads.

# [text](target)
_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


@dataclass(frozen=True)
class Figure:
    lineno: int
    line: str
    counts: dict[str, int]
    shape: str

    def key(self) -> tuple:
        return tuple(sorted(self.counts.items()))


@dataclass(frozen=True)
class Finding:
    kind: str
    where: str
    lineno: int
    detail: str

    def __str__(self) -> str:
        at = f":{self.lineno}" if self.lineno else ""
        return f"{self.where}{at}: {self.kind}: {self.detail}"


@dataclass
class FigureReport:
    findings: list[Finding] = field(default_factory=list)
    graded: int = 0
    declared_uncitable: int = 0
    disposed: int = 0
    unattributed: int = 0
    # every exempted line, NAMED: (path, lineno, the phrase that spent the hatch). A count alone
    # is an escape hatch nobody can see being used (review F1).
    exempted: list[tuple[str, int, str]] = field(default_factory=list)
    # every disposal, NAMED: (path, lineno, the correction's date)
    disposals: list[tuple[str, int, str]] = field(default_factory=list)


# -- reading -------------------------------------------------------------------------------------

def _parse_truth() -> Callable[[str], dict]:
    """talk/truth_manifest.py's parser. One reader of the TRUTH line in this estate, shared with
    verify/cited-truth/ rather than copied beside it."""
    spec = importlib.util.spec_from_file_location(
        "truth_manifest_for_map_surface", HUB / "talk" / "truth_manifest.py")
    if spec is None or spec.loader is None:      # pragma: no cover - the wrapper refuses first
        raise SystemExit("FAIL: talk/truth_manifest.py is not readable")
    module = importlib.util.module_from_spec(spec)
    # registered before exec: truth_manifest defines dataclasses, and @dataclass reads
    # sys.modules[cls.__module__] while it builds the class
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.parse_truth


def recorded(log_text: str) -> list[dict]:
    """Every TRUTH line talk/truth.log records, parsed, oldest first."""
    parse = _parse_truth()
    return [parse(line) for line in log_text.splitlines() if line.startswith("TRUTH ")]


def run_cited(line: str) -> str | None:
    """The run number cited on one text line, or None. The first wins: a line naming two runs is
    graded on the one it leads with, and the second is caught on its own line or not at all."""
    m = _RUN.search(line)
    return m.group(1) if m else None


def figures_quoted(text: str) -> list[Figure]:
    """Every pass/fail figure quoted in `text`, one per match, in the order they appear.

    A key-shaped figure of ONE key identifies no line on its own -- the map uses exactly that
    shape for a local decomposition (`fail=24`) -- so it is returned here and counted as
    unattributed by grade_figures unless a run citation stands beside it. Counting it there rather
    than dropping it here keeps the ungraded population on the record instead of invisible.
    """
    out: list[Figure] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for m in _SLASH.finditer(line):
            out.append(Figure(lineno, line, {
                "pass": int(m.group(1)), "fail": int(m.group(2)),
                "skip": int(m.group(3)), "total": int(m.group(4))}, "slash"))
        for m in _PROSE.finditer(line):
            counts = {"pass": int(m.group(1)), "fail": int(m.group(2)),
                      "total": int(m.group(4))}
            if m.group(3) is not None:
                counts["skip"] = int(m.group(3))
            out.append(Figure(lineno, line, counts, "prose"))
        keys = {k: int(v) for k, v in _KEYS.findall(line)}
        if keys:
            out.append(Figure(lineno, line, keys, "keys"))
    return out


@dataclass(frozen=True)
class _Para:
    lineno: int
    text: str


def paragraphs(text: str) -> list[_Para]:
    out: list[_Para] = []
    buf: list[str] = []
    start = 1
    for i, line in enumerate(text.splitlines(), start=1):
        if line.strip():
            if not buf:
                start = i
            buf.append(line)
        elif buf:
            out.append(_Para(start, "\n".join(buf)))
            buf = []
    if buf:
        out.append(_Para(start, "\n".join(buf)))
    return out


@dataclass(frozen=True)
class Correction:
    """A dated correction, and the ONE paragraph it may dispose for.

    Review F2, 2026-09-06. A correction used to dispose of its figure ANYWHERE in the map, so the
    2026-08-31 correction of "65 pass, 0 fail, 16 could-not-look of 83" laundered a FRESH
    occurrence of that same sentence written into a new section today — the exact sentence this
    ticket was charted to refuse, excused by the correction of it.

    A correction now disposes only for the paragraph it IMMEDIATELY FOLLOWS, which is where the
    estate writes one and is the only place a reader meets the two together. A claim anywhere else
    must be rewritten in place under a banner, as ticket 67 item (a) did to the drift-review
    NORTH-STAR, or it is graded.
    """
    date: str
    first: int          # first line of the correction paragraph
    last: int           # last line of the correction paragraph
    text: str
    covers_first: int   # first line of the paragraph it immediately follows
    covers_last: int    # last line of that paragraph


def dated_corrections(text: str) -> list[Correction]:
    paras = paragraphs(text)
    out: list[Correction] = []
    for i, para in enumerate(paras):
        m = _CORRECTION.search(para.text)
        if not m:
            continue
        last = para.lineno + para.text.count("\n")
        if i == 0:
            covers = (0, -1)                     # nothing above it to correct
        else:
            above = paras[i - 1]
            covers = (above.lineno, above.lineno + above.text.count("\n"))
        out.append(Correction(m.group(1), para.lineno, last, para.text, covers[0], covers[1]))
    return out


def _blank(pattern: re.Pattern[str], text: str) -> str:
    """Replace each match with spaces of the same length, so offsets do not move."""
    return pattern.sub(lambda m: " " * len(m.group(0)), text)


def uncitable(line: str) -> str | None:
    """The fixed phrase by which this line disowns its own figure, or None.

    A negated occurrence is not a disclaimer: "this does not make it not citable" asserts the
    opposite of one. Only the text BEFORE an occurrence is examined, so a phrase beginning "not"
    never negates itself. A marker inside a `code span` or a [link](target) is the phrase being
    QUOTED and spends nothing.
    """
    low = _blank(_CODE_SPAN, _blank(_LINK_TARGET, line)).lower()
    for phrase in _UNCITABLE:
        start = low.find(phrase)
        while start != -1:
            if not _NEGATION.search(low[:start]):
                return phrase
            start = low.find(phrase, start + 1)
    return None


def _disposed(fig: Figure, corrections: Iterable[Correction]) -> str | None:
    """The date of the correction that disposes of this figure, or None.

    A correction disposes when it names the figure's own numbers AND the figure stands in the
    paragraph it immediately follows. `65/0/16` in the correction disposes of `65 pass, 0 fail,
    16 could-not-look of 83` directly above it; the same correction disposes of nothing in a
    section written later.

    A correction never disposes of a figure standing INSIDE itself. The replacement figure it
    offers is the one thing in the paragraph that must be true, so it is graded like any other.
    """
    wanted = [str(fig.counts[k]) for k in ("pass", "fail", "skip") if k in fig.counts]
    if len(wanted) < 2:
        return None
    slash = "/".join(wanted)
    for corr in corrections:
        if corr.first <= fig.lineno <= corr.last:
            continue
        if not (corr.covers_first <= fig.lineno <= corr.covers_last):
            continue
        if slash in corr.text:
            return corr.date
        got = {k: int(v) for k, v in _KEYS.findall(corr.text)}
        if all(k in got and got[k] == v for k, v in fig.counts.items()):
            return corr.date
    return None


# -- rule 1: every figure the map quotes is a figure the log recorded ----------------------------

def grade_figures(map_text: str, log_text: str) -> FigureReport:
    report = FigureReport()
    lines = recorded(log_text)
    by_run: dict[str, list[dict]] = {}
    for line in lines:
        by_run.setdefault(str(line.get("run")), []).append(line)
    corrections = dated_corrections(map_text)

    for fig in figures_quoted(map_text):
        run = run_cited(fig.line)
        # A key-shaped figure of one key is only a figure when a run stands beside it; without
        # one it identifies nothing and is counted, never graded or exempted.
        if len(fig.counts) < 2 and run is None:
            report.unattributed += 1
            continue
        # The hatch is spent only where it actually SUPPRESSES a grade, so the printed list of
        # exemptions means what it says (review F1, following verify/cited-truth/).
        phrase = uncitable(fig.line)
        if phrase:
            report.declared_uncitable += 1
            report.exempted.append((MAP, fig.lineno, phrase))
            continue
        date = _disposed(fig, corrections)
        if date:
            report.disposed += 1
            report.disposals.append((MAP, fig.lineno, date))
            continue
        shown = " ".join(f"{k}={v}" for k, v in fig.counts.items())
        if run is not None:
            candidates = by_run.get(run)
            if not candidates:
                report.findings.append(Finding(
                    "no-such-line", MAP, fig.lineno,
                    f"run {run} is quoted with {shown}, and talk/truth.log records no such run"))
                continue
            report.graded += 1
            if not any(_agrees(fig, line) for line in candidates):
                got = candidates[-1]
                report.findings.append(Finding(
                    "figure-disagrees", MAP, fig.lineno,
                    f"run {run} is quoted with {shown}, and the line talk/truth.log records for "
                    f"run {run} reads " + " ".join(
                        f"{k}={got.get(k)}" for k in fig.counts)))
            continue
        report.graded += 1
        if not any(_agrees(fig, line) for line in lines):
            report.findings.append(Finding(
                "no-such-figure", MAP, fig.lineno,
                f"{shown} is quoted as a measurement, and no line in talk/truth.log carries "
                f"that figure; no run is named beside it and no dated correction disposes of it"))
    return report


def _agrees(fig: Figure, line: dict) -> bool:
    return all(line.get(k) == v for k, v in fig.counts.items())


# -- rule 2: every check the map names is one the gate discovers ---------------------------------

def grade_checks(map_text: str, manifest_paths: Iterable[str]) -> list[Finding]:
    """Every check the map names in backticks must be one the gate discovers.

    NO HATCH (review F4, 2026-09-06). This briefly excused a check whose line said "not yet
    merged", "unmerged" or "not in the gate yet". Those are ordinary prose: map.md line 29 already
    contains "unmerged", so a check named on that line that existed NOWHERE was exempt, and the
    excuse never checked that the named script existed anywhere at all. Unmerged work goes red
    until it merges, exactly as the lane rule does, and a map that wants to point at it says so in
    a sentence a reader reads rather than in a word this check reads.
    """
    paths = sorted(manifest_paths)
    basenames = {p.rsplit("/", 1)[-1] for p in paths}
    findings: list[Finding] = []
    for lineno, line in enumerate(map_text.splitlines(), start=1):
        for token in re.findall(r"`([^`\n]+)`", line):
            token = token.strip().split()[0] if token.strip() else ""
            if not token or not _is_check_token(token):
                continue
            if token.rsplit("/", 1)[-1] in _RUNNER:
                continue
            stem = token.rstrip("/")
            if stem in basenames or any(p == stem or p.endswith("/" + stem)
                                        or p.startswith(stem + "/") for p in paths):
                continue
            findings.append(Finding(
                "check-not-in-the-gate", MAP, lineno,
                f"names {token!r} as a check, and talk/verify-manifest.txt -- the row every "
                f"script talk/verify-all.sh runs must have -- carries no such path"))
    return findings


# -- rule 3: a reader following the map meets no dead link ---------------------------------------

def grade_links(map_text: str, exists: Callable[[str], bool]) -> list[Finding]:
    findings: list[Finding] = []
    for lineno, line in enumerate(map_text.splitlines(), start=1):
        for target in _LINK.findall(line):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target = target.split("#", 1)[0]
            if not target or exists(target):
                continue
            findings.append(Finding(
                "dead-link", MAP, lineno,
                f"links {target!r}, which does not exist: a reader following the map meets "
                f"nothing there"))
    return findings


# -- rule 4: a unit declares only the lane paths it owns -----------------------------------------

def grade_lanes(declared: dict[str, dict[str, list[str]]],
                owned: dict[str, set[str]]) -> list[Finding]:
    findings: list[Finding] = []
    for unit in sorted(declared):
        mine = owned.get(unit, set())
        for workflow in sorted(declared[unit]):
            for path in declared[unit][workflow]:
                if path in mine:
                    continue
                findings.append(Finding(
                    "lane-not-owned", f"{unit}/{workflow}", 0,
                    f"declares {path!r} in OBSERVATION_LANE, and {unit} owns no such path -- "
                    f"it owns {sorted(mine) or 'nothing in the lane'}. "
                    f"verify/schedules/lane.py grades every commit a scheduled identity landed "
                    f"in {unit} against the union of {unit}'s OWN declarations, so a path "
                    f"copied in from another repository widens what a clock here may land"))
    return findings


# -- rule 5: ticket 67's own record corrections stay corrected ------------------------------------

# (path, carries?, sentence, why). carries=True: the record must carry it. carries=False: the
# record must no longer carry it.
RECORD_FACTS: tuple[tuple[str, bool, str, str], ...] = (
    (MAP, True, "](../../NORTH-STAR.md)",
     "item (a): the map's Destination links the ROOT NORTH-STAR.md, the one referent "
     "(ticket 02), not the drift-review copy"),
    (MAP, False, "](../drift-review-2026-08-27/NORTH-STAR.md)",
     "item (a): the map no longer links the drift-review copy, which diverged from the root "
     "copy on 2026-09-03 when ticket 95 added §0"),
    (DRIFT_NORTH_STAR, False, "still await the owner's yes or no",
     "item (a): the drift-review copy no longer says the 22 reversals await an answer; they "
     "were confirmed on 2026-08-28 (REGRILL-ANSWERS.md)"),
    (DRIFT_NORTH_STAR, True, "confirmed on 2026-08-28",
     "item (a): the drift-review copy carries the dated reversals-confirmed line, so the two "
     "copies do not disagree about whether the owner answered"),
)


def grade_record(files: dict[str, str]) -> list[Finding]:
    findings: list[Finding] = []
    for path, carries, sentence, why in RECORD_FACTS:
        text = files.get(path)
        if text is None:
            findings.append(Finding("record-unreadable", path, 0,
                                    f"cannot be read, so {why} cannot be graded"))
            continue
        found = sentence in text
        if found and not carries:
            findings.append(Finding("record-carries", path, 0,
                                    f"still carries {sentence!r} -- {why}"))
        elif not found and carries:
            findings.append(Finding("record-lacks", path, 0,
                                    f"does not carry {sentence!r} -- {why}"))
    return findings


# -- the filesystem wiring ------------------------------------------------------------------------

LANE_ENV = re.compile(r"^\s*OBSERVATION_LANE:\s*\"([^\"]*)\"\s*$", re.M)
UNITS = ("driftwood", "feeds", "ico", "insurer", "ludlow", "nist", "platform", "tuppence")

# What each repository owns in the lane, read from the repository rather than asserted.
LANE_PATHS = ("talk/truth.log", "drift/samples.jsonl", "talk/captures", "observations")

# THE REF THIS GRADES (review F3, 2026-09-06). What GitHub serves is `origin/main`, not whatever
# happens to be checked out in `.estate-clone/<unit>`. Reading the working copy made the verdict
# turn on the VENUE: the reviewer checked the units out at this ticket's branch and got 0
# findings, at origin/main and got 33, and an uncommitted `git checkout <branch> -- fetch.yml` in
# ico made ico's three findings disappear. It read green on CI only because clone-estate.sh clones
# fresh there, and four units in the real local clone were behind origin/main that morning.
#
# So both halves -- what a unit DECLARES and what it OWNS -- are read from `origin/main`, freshly
# fetched per unit, and the checkout is only compared and reported (a note, graded by nothing).
# NOT unioned with the checkout, and deliberately unlike verify/schedules/lane.py, which unions:
# lane.py grades commits a clock LANDED and a landed commit was governed by whichever copy was in
# force, so it must read both; this rule grades what the estate DECLARES, and the only declaration
# a reader can meet is the served one. A union here re-created the venue dependence the other way
# round -- two `.work/`-kept stale clones produced 12 findings against an estate that had none.
# The recorded sentence is then true by code rather than by where the check happened to run.
# (An earlier draft of this comment said "UNIONED"; the code never was. Corrected 2026-09-06.)
SERVED_REF = "origin/main"


def _git(root: Path, *args: str) -> str | None:
    """git output, or None when the command cannot run or the ref is not there."""
    try:
        done = subprocess.run(["git", "-C", str(root), *args],
                              capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout if done.returncode == 0 else None


def _workflow_texts(unit_root: Path) -> dict[str, str]:
    """{filename: text} for the unit's workflows AS `origin/main` SERVES THEM. The checkout is not
    read, and the difference matters in both directions.

    verify/schedules/lane.py unions the ref with the checkout, and is right to: it grades commits
    a clock LANDED, and a clock is judged by the configuration that was in force when it landed,
    whichever copy carries it. This rule asks a different question -- what does the estate DECLARE
    -- and the only declaration a reader of the estate can meet is the served one.

    Unioning here made the verdict turn on the venue in the other direction, measured 2026-09-06:
    after the eight unit pull requests merged, `clone-estate.sh --refresh` KEPT platform and
    tuppence because they carried `.work/` worktrees, so their working copies still held the old
    four-path list while `origin/main` held the trimmed one. The union reported twelve findings
    against an estate that had none. A stale checkout is the venue, not a claim.

    Where the checkout disagrees it is REPORTED (`checkout_behind`), never graded, so a builder
    sees their copy is behind without the verdict moving.
    """
    found: dict[str, str] = {}
    names = _git(unit_root, "ls-tree", "--name-only", SERVED_REF, "--", ".github/workflows/")
    for path in (names or "").split():
        if not path.endswith((".yml", ".yaml")):
            continue
        text = _git(unit_root, "show", f"{SERVED_REF}:{path}")
        if text is not None:
            found[path.rsplit("/", 1)[-1]] = text
    return found


def checkout_behind(unit_root: Path) -> list[str]:
    """Workflow files whose checkout copy declares a different lane from the served copy."""
    differs = []
    local = unit_root / ".github" / "workflows"
    if not local.is_dir():
        return differs
    served = _workflow_texts(unit_root)
    for wf in sorted(local.glob("*.yml")):
        mine = LANE_ENV.findall(wf.read_text(errors="replace"))
        theirs = LANE_ENV.findall(served.get(wf.name, ""))
        if mine != theirs:
            differs.append(wf.name)
    return differs


def refresh_served_ref(unit_root: Path) -> str | None:
    """Fetch `origin/main`, then confirm it resolves. The reason it cannot be trusted, or None.

    Fetching is part of the rule, not a convenience. `origin/main` in a local clone is only what
    GitHub serves if somebody fetched it: on 2026-09-06 the eight unit pull requests were merged
    and `clone-estate.sh --refresh` KEPT platform and tuppence because they carried `.work/`, so
    their `origin/main` was two hours stale and this check reported twelve findings that the
    served estate no longer had. A stale ref is the same venue-dependent reading as a working
    copy, one level down, so a fetch that fails is RED with its reason rather than a quiet read of
    whatever is local.
    """
    if _git(unit_root, "rev-parse", "--git-dir") is None:
        return "not a git checkout"
    if _git(unit_root, "fetch", "--quiet", "origin",
            "+refs/heads/main:refs/remotes/origin/main") is None:
        return "could not fetch origin/main, so what is here may be behind what GitHub serves"
    if _git(unit_root, "rev-parse", "--verify", f"{SERVED_REF}^{{commit}}") is None:
        return f"{SERVED_REF} does not resolve"
    return None


def owned_lane_paths(unit_root: Path) -> set[str]:
    """The lane paths this repository owns. Read from git, never from the working copy alone:

      * the path is in the tree `origin/main` serves;
      * the path is the root of an observation ref the repository has (`origin/observations`);
      * the repository's own workflow shell writes it, outside the OBSERVATION_LANE declaration
        and outside the cage's loop over it. driftwood owns `observations` this way and by no
        other: its twin-sweep appends `observations/twin-sweep.jsonl` on main.
    """
    owned: set[str] = set()
    texts = list(_workflow_texts(unit_root).values())
    refs = _git(unit_root, "for-each-ref", "--format=%(refname:short)", "refs/remotes/origin") or ""
    ref_roots = {r.split("/", 1)[1] for r in refs.split() if "/" in r}
    for path in LANE_PATHS:
        listed = _git(unit_root, "ls-tree", "-r", "--name-only", SERVED_REF, "--", path)
        if listed:
            owned.add(path)
            continue
        if path in ref_roots:
            owned.add(path)
            continue
        for text in texts:
            for line in text.splitlines():
                if "OBSERVATION_LANE" in line or path not in line:
                    continue
                if re.search(r"(>>|>|mkdir -p|git add[^;]*|cat )\s*[\"']?" + re.escape(path),
                             line):
                    owned.add(path)
                    break
            if path in owned:
                break
    return owned


def declared_lanes(estate: Path) -> dict[str, dict[str, list[str]]]:
    out: dict[str, dict[str, list[str]]] = {}
    for unit in UNITS:
        unit_root = estate / unit
        if not unit_root.is_dir():
            continue
        found: dict[str, list[str]] = {}
        for name, text in sorted(_workflow_texts(unit_root).items()):
            for m in LANE_ENV.finditer(text):
                found.setdefault(name, [])
                for path in m.group(1).split():
                    if path not in found[name]:
                        found[name].append(path)
        if found:
            out[unit] = found
    return out


def manifest_paths(root: Path) -> set[str]:
    text = (root / "talk" / "verify-manifest.txt").read_text()
    found = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        found.add(line.split("|", 1)[0].strip())
    return found


def grade(root: Path) -> int:
    map_path = root / MAP
    if not map_path.is_file():
        print(f"  !! {MAP} does not exist: there is no map to grade")
        return 1
    map_text = map_path.read_text()
    log_path = root / "talk" / "truth.log"
    if not log_path.is_file():
        print("  !! talk/truth.log does not exist: no figure the map quotes can be resolved")
        return 1
    log_text = log_path.read_text()

    findings: list[Finding] = []
    fr = grade_figures(map_text, log_text)
    findings += fr.findings
    findings += grade_checks(map_text, manifest_paths(root))
    findings += grade_links(map_text, lambda t: (map_path.parent / t).exists())

    estate = root / ".estate-clone"
    missing = [u for u in UNITS if not (estate / u).is_dir()]
    unserved = {u: why for u in UNITS if (estate / u).is_dir()
                and (why := refresh_served_ref(estate / u))}
    declared = declared_lanes(estate)
    if missing:
        print(f"  !! .estate-clone is missing {missing}: a lane declaration cannot be read "
              f"against a repository that is not here. clone-estate.sh assembles it; this is a "
              f"red, not a shrug")
        findings.append(Finding("estate-unreadable", ".estate-clone", 0,
                                f"{len(missing)} unit(s) absent"))
    for unit, why in unserved.items():
        print(f"  !! {unit}: {why} -- so what GitHub SERVES cannot be read here and only a local "
              f"copy could be graded, which is the venue-dependent reading this rule was "
              f"corrected for. A red, not a shrug")
        findings.append(Finding("served-ref-unreadable", unit, 0, why))
    if not missing and not unserved:
        owned = {u: owned_lane_paths(estate / u) for u in UNITS}
        findings += grade_lanes(declared, owned)
        print(f"  -- lane declarations and ownership read at {SERVED_REF}, freshly fetched; the "
              f"checkout is never graded")
        for unit in UNITS:
            stale = checkout_behind(estate / unit)
            if stale:
                print(f"  -- note     .estate-clone/{unit}: the checkout declares a different "
                      f"lane from {SERVED_REF} in {stale} -- reported, never graded; a stale "
                      f"clone is the venue, not a claim")

    files = {}
    for path in {f[0] for f in RECORD_FACTS}:
        p = root / path
        if p.is_file():
            files[path] = p.read_text()
    findings += grade_record(files)

    for f in findings:
        print(f"  !! {f}")
    if findings:
        tally: dict[str, int] = {}
        for f in findings:
            tally[f.kind] = tally.get(f.kind, 0) + 1
        print("  == " + str(len(findings)) + " finding(s): "
              + ", ".join(f"{k} x{v}" for k, v in sorted(tally.items())))
    print(f"  -- {fr.graded} figure(s) graded against talk/truth.log; {fr.unattributed} "
          f"identified no line and were not graded")
    # every exemption and every disposal is NAMED, not only counted (review F1): an escape hatch
    # nobody can see being used is an escape hatch nobody audits.
    print(f"  -- {fr.declared_uncitable} figure(s) exempted by a fixed disclaimer, "
          f"{fr.disposed} disposed of by the dated correction directly below them:")
    for path, lineno, phrase in fr.exempted:
        print(f"  -- exempt   {path}:{lineno}  ({phrase})")
    for path, lineno, date in fr.disposals:
        print(f"  -- disposed {path}:{lineno}  (correction of {date}, the paragraph below it)")
    if not fr.exempted and not fr.disposals:
        print("  -- exempt   none")
    print(f"  -- {sum(len(v) for v in declared.values())} lane declaration(s) read across "
          f"{len(declared)} unit(s)")
    return 1 if findings else 0


# -- selfcheck -------------------------------------------------------------------------------------

def selfcheck() -> int:
    """Every rule, planted red and planted green, with no filesystem and no estate."""
    log = ("TRUTH 2026-08-31T17:22Z run=13 hub=eba3569 units=[ico=9d09222] "
           "pass=53 fail=7 skip=21 excluded=2 total=83\n")

    ok = grade_figures("the surface stood at 53/7/21 of 83\n", log)
    assert ok.findings == [], "a figure the log records must pass"
    assert ok.graded == 1, "a graded figure must be counted"
    print("ok  a figure talk/truth.log records passes, and is counted")

    bad = grade_figures("the surface stood at 65 pass, 0 fail, 16 could-not-look of 83\n", log)
    assert [f.kind for f in bad.findings] == ["no-such-figure"], bad.findings
    print("ok  a figure no recorded line carries is red")

    wrong = grade_figures("run 13 recorded 65/0/16 of 83\n", log)
    assert [f.kind for f in wrong.findings] == ["figure-disagrees"], wrong.findings
    print("ok  a figure quoted beside a run that is not that run's figure is red")

    gone = grade_figures("run 92 recorded 65/13/19 of 105\n", log)
    assert [f.kind for f in gone.findings] == ["no-such-line"], gone.findings
    print("ok  a run talk/truth.log never recorded is red")

    excused = grade_figures("65 pass, 0 fail of 83, from a run that is not citable\n", log)
    assert excused.findings == [] and excused.declared_uncitable == 1, excused
    assert excused.exempted == [(MAP, 1, "not citable")], excused.exempted
    print("ok  a figure whose line says `not citable` is exempt, and the exemption is NAMED, not "
          "only counted")

    # review F1: the hatch used to be seven substrings matched anywhere on the line. Each of these
    # went green and reported nothing but +1 in a count.
    for laundered in (
            "verify/local-clock: the surface stood at 65 pass, 0 fail, 16 could-not-look of 83\n",
            "the surface stood at 65 pass, 0 fail of 83, and that is NOT a rehearsal\n",
            "run 13 recorded 43/11/0 of 56 and was planted\n",
            "as the Actions log confirms, the surface stood at 65 pass, 0 fail of 83\n",
            "no fixture was used: the surface stood at 65 pass, 0 fail of 83\n"):
        got = grade_figures(laundered, log)
        assert got.findings and not got.exempted, f"laundered: {laundered.strip()!r} -> {got}"
    print("ok  a bag-of-words disclaimer launders nothing: an ordinary word, a NEGATED marker and "
          "a claim about the Actions log are each graded")
    quoted = grade_figures("grep for `not citable`: the surface stood at 65 pass, 0 fail of 83\n",
                           log)
    assert quoted.findings and not quoted.exempted, quoted
    print("ok  a marker quoted in a code span is the phrase, not a line disowning its figure")

    spent = grade_figures("run 13 recorded fail=7, which is not citable anyway\n", log)
    assert spent.declared_uncitable == 1 and spent.exempted, spent
    unspent = grade_figures("decomposes the local `fail=24` row by row\n", log)
    assert unspent.findings == [] and unspent.exempted == [] and unspent.unattributed == 1, unspent
    print("ok  the hatch is spent only where it suppresses a grade; a lone key with no run beside "
          "it is counted as identifying nothing, not exempted")

    disposed = grade_figures(
        "the surface reached 65 pass, 0 fail, 16 could-not-look of 83.\n\n"
        "> **Correction, 2026-08-31.** The 65/0/16 figure was from a run nobody recorded.\n", log)
    assert disposed.findings == [] and disposed.disposed == 1, disposed
    assert disposed.disposals == [(MAP, 1, "2026-08-31")], disposed.disposals
    undated = grade_figures(
        "the surface reached 65 pass, 0 fail, 16 could-not-look of 83.\n\n"
        "> **Correction.** The 65/0/16 figure was from a run nobody recorded.\n", log)
    assert [f.kind for f in undated.findings] == ["no-such-figure"], undated.findings
    print("ok  the dated correction directly below a claim disposes of it and says so by line; an "
          "undated one disposes of nothing")

    # review F2: a correction used to dispose of its figure ANYWHERE in the map, so the correction
    # of a sentence laundered a fresh copy of that sentence written into a new section.
    elsewhere = grade_figures(
        "the surface reached 65 pass, 0 fail, 16 could-not-look of 83.\n\n"
        "> **Correction, 2026-08-31.** The 65/0/16 figure was from a run nobody recorded.\n\n"
        "## A section written later\n\n"
        "Nothing is red: 65 pass, 0 fail, 16 could-not-look of 83.\n", log)
    assert [f.kind for f in elsewhere.findings] == ["no-such-figure"], elsewhere.findings
    assert elsewhere.findings[0].lineno == 7, elsewhere.findings
    assert elsewhere.disposed == 1, elsewhere
    print("ok  a correction disposes only for the paragraph directly above it: the same sentence "
          "written into a later section is graded, and red")

    own = grade_figures(
        "the surface reached 65 pass, 0 fail, 16 could-not-look of 83.\n\n"
        "> **Correction, 2026-08-31.** The 65/0/16 figure was unrecorded; the citable line is\n"
        "> run 13, 52/7/21 of 83.\n", log)
    assert [f.kind for f in own.findings] == ["figure-disagrees"], own.findings
    print("ok  a correction does not excuse the replacement figure it offers: that one is graded")

    manifest = {"verify/misuse/verify-misuse.sh", ".estate-clone/platform/verify-graded.sh"}
    assert grade_checks("`verify-graded.sh` and `verify/misuse`\n", manifest) == []
    absent = grade_checks("graded by `verify-nothing.sh`\n", manifest)
    assert [f.kind for f in absent] == ["check-not-in-the-gate"], absent
    assert grade_checks("`talk/verify-all.sh` discovers them\n", manifest) == []
    # review F4: there is no "not yet merged" hatch, and there must not be one -- the phrases were
    # ordinary prose and the excuse never checked the named script existed anywhere.
    still = grade_checks("`verify-later.sh` (built, unmerged, not yet in the gate)\n", manifest)
    assert [f.kind for f in still] == ["check-not-in-the-gate"], still
    print("ok  a check the manifest carries passes and one it does not is red, whatever the line "
          "says about it being unmerged; the runner is not a check")

    dead = grade_links("see [a](issues/gone.md)\n", lambda p: False)
    assert [f.kind for f in dead] == ["dead-link"], dead
    assert grade_links("see [a](https://example.invalid)\n", lambda p: False) == []
    print("ok  a dead relative link is red and an absolute one is not a file claim")

    lanes = grade_lanes({"ico": {"fetch.yml": ["talk/truth.log", "observations"]}},
                        {"ico": {"observations"}})
    assert [f.kind for f in lanes] == ["lane-not-owned"], lanes
    assert grade_lanes({"ico": {"fetch.yml": ["observations"]}}, {"ico": {"observations"}}) == []
    print("ok  a lane path the repository does not own is red, and a trimmed lane passes")

    good = {MAP: "[NORTH-STAR.md](../../NORTH-STAR.md)",
            DRIFT_NORTH_STAR: "All 22 reversals were confirmed on 2026-08-28."}
    assert grade_record(good) == [], grade_record(good)
    broken = dict(good)
    broken[MAP] = "[NORTH-STAR.md](../drift-review-2026-08-27/NORTH-STAR.md)"
    kinds = sorted(f.kind for f in grade_record(broken))
    assert kinds == ["record-carries", "record-lacks"], kinds
    assert all(f.kind == "record-unreadable" for f in grade_record({}))
    print("ok  a record fact that came back and one that went missing are each red by name, and "
          "an unreadable file is red rather than a shrug")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "selfcheck":
        return selfcheck()
    if len(argv) == 3 and argv[1] == "grade":
        return grade(Path(argv[2]).resolve())
    print("usage: map_surface.py grade <hub-root> | selfcheck", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
