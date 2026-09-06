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
  * a figure with no run beside it and no recorded line to match, where the text line says of
    itself that it is `local`, a `rehearsal`, a `fixture`, `planted`, `hypothetical`, `not
    citable` or from the `Actions log`; and a figure a DATED correction elsewhere in the map
    names. Both populations are COUNTED and printed on every run, so the size of what is not
    graded is a number that moves rather than a sentence somebody wrote once.

WHAT IT NEVER SHRUGS AT. There is no could-not-look, by decision (delegated, ADR-0025,
2026-09-06), following `verify/can-record/` and `verify/cited-truth/`. Rules 1 to 3 and 5 read
only files in this repository; rule 4 reads `.estate-clone/`, which `clone-estate.sh` assembles
and which `verify/schedules/verify-lane.sh` already refuses (exit 1) rather than shrugs for. So
every state in which this cannot see is RED with its own named line, and its manifest row declares
no skip pattern because there is none to declare.

    map_surface.py grade <hub-root>   # the five rules; 0 nothing false, 1 one or more named
    map_surface.py selfcheck          # planted defects grade as planted
"""
from __future__ import annotations

import importlib.util
import re
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

# The words a text line uses to say of itself that it is not evidence.
_UNCITABLE = ("local", "rehearsal", "fixture", "planted", "hypothetical", "not citable",
              "actions log")

# A backticked token that names a CHECK: a shell script whose basename starts with `verify`, or a
# directory under `verify/`. Deliberately not "any path with `verify` in it": `verify/schedules/
# lane.py` is a module the gate imports and `verify/deny-is-not-a-rung/register.yaml` is data, and
# neither is a script talk/verify-all.sh discovers, so neither belongs in this rule.
_CHECK_SCRIPT = re.compile(r"^(?:[\w.-]+/)*verify[\w.-]*\.sh$")
_CHECK_DIR = re.compile(r"^verify/(?:[\w.-]+/)*[\w-]+/?$")
_RUNNER = ("verify-all.sh",)


def _is_check_token(token: str) -> bool:
    return bool(_CHECK_SCRIPT.match(token) or _CHECK_DIR.match(token))

# The words a text line uses to say that the check it names is not in the gate yet. A map may
# point at work that is built and unmerged; it may not present it as something the gate runs.
_NOT_YET = ("not yet merged", "not merged", "unmerged", "not yet in the gate",
            "waits on the integrator")

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

    A key-shaped figure needs two of the six keys, or one key with a run citation beside it: a
    lone `fail=24` names no run and identifies no line, and the map uses exactly that shape for a
    local decomposition. Those are counted as unattributed by grade_figures, never graded.
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
        if keys and (len(keys) >= 2 or run_cited(line)):
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


def dated_corrections(text: str) -> list[tuple[int, int, str]]:
    """(first line, last line, text) for each paragraph carrying a DATED correction."""
    return [(p.lineno, p.lineno + p.text.count("\n"), p.text)
            for p in paragraphs(text) if _CORRECTION.search(p.text)]


def _declared_uncitable(line: str) -> bool:
    low = line.lower()
    return any(word in low for word in _UNCITABLE)


def _disposed(fig: Figure, corrections: Iterable[tuple[int, int, str]]) -> bool:
    """A dated correction disposes of a figure when it names that figure's own numbers. `65/0/16`
    in the correction disposes of `65 pass, 0 fail, 16 could-not-look of 83`; a correction naming
    a different figure disposes of nothing.

    A correction never disposes of a figure standing INSIDE itself. The replacement figure a
    correction offers is the one thing in the paragraph that must be true, so it is graded like
    any other; otherwise a correction could excuse its own wrong number by carrying it.
    """
    wanted = [str(fig.counts[k]) for k in ("pass", "fail", "skip") if k in fig.counts]
    if len(wanted) < 2:
        return False
    slash = "/".join(wanted)
    for first, last, para in corrections:
        if first <= fig.lineno <= last:
            continue
        if slash in para:
            return True
        got = {k: int(v) for k, v in _KEYS.findall(para)}
        if all(k in got and got[k] == v for k, v in fig.counts.items()):
            return True
    return False


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
        if _declared_uncitable(fig.line):
            report.declared_uncitable += 1
            continue
        if _disposed(fig, corrections):
            report.disposed += 1
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

def grade_checks(map_text: str, manifest_paths: Iterable[str],
                 pending: list[int] | None = None) -> list[Finding]:
    """`pending`, when given, receives one entry per check the map names and declares, on the same
    text line, as not in the gate yet. That population is COUNTED and printed, never graded: a map
    may name a check that is built and unmerged, but it must say so where it names it."""
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
            if any(word in line.lower() for word in _NOT_YET):
                if pending is not None:
                    pending.append(lineno)
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

# What each repository owns in the lane, read from the repository rather than asserted: a path
# that exists in its checkout, or one its own scheduled workflows write outside the cage loop.
LANE_PATHS = ("talk/truth.log", "drift/samples.jsonl", "talk/captures", "observations")


def owned_lane_paths(unit_root: Path) -> set[str]:
    """The lane paths this repository owns: one that exists in its checkout, one that exists on
    any ref it holds, or one its own workflow shell writes. Read, never assumed."""
    owned: set[str] = set()
    workflows = unit_root / ".github" / "workflows"
    texts = []
    if workflows.is_dir():
        texts = [p.read_text(errors="replace") for p in sorted(workflows.glob("*.yml"))]
    for path in LANE_PATHS:
        if (unit_root / path).exists():
            owned.add(path)
            continue
        # a path the repository's own clock writes: named in a shell line that is not the
        # OBSERVATION_LANE declaration and not the cage's loop over it
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
        workflows = estate / unit / ".github" / "workflows"
        if not workflows.is_dir():
            continue
        found: dict[str, list[str]] = {}
        for wf in sorted(workflows.glob("*.yml")):
            for m in LANE_ENV.finditer(wf.read_text(errors="replace")):
                found.setdefault(wf.name, [])
                for path in m.group(1).split():
                    if path not in found[wf.name]:
                        found[wf.name].append(path)
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
    pending: list[int] = []
    findings += grade_checks(map_text, manifest_paths(root), pending)
    findings += grade_links(map_text, lambda t: (map_path.parent / t).exists())

    estate = root / ".estate-clone"
    declared = declared_lanes(estate)
    missing = [u for u in UNITS if not (estate / u).is_dir()]
    if missing:
        print(f"  !! .estate-clone is missing {missing}: a lane declaration cannot be read "
              f"against a repository that is not here. clone-estate.sh assembles it; this is a "
              f"red, not a shrug")
        findings.append(Finding("estate-unreadable", ".estate-clone", 0,
                                f"{len(missing)} unit(s) absent"))
    else:
        owned = {u: owned_lane_paths(estate / u) for u in UNITS}
        findings += grade_lanes(declared, owned)

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
    print(f"  -- {fr.graded} figure(s) graded against talk/truth.log; "
          f"{fr.declared_uncitable} declared uncitable on their own line and "
          f"{fr.disposed} disposed of by a dated correction, both counted and not graded")
    print(f"  -- {len(pending)} check(s) named and declared not in the gate yet "
          f"(line{'s' if len(pending) != 1 else ''} {pending or 'none'}), counted and not graded")
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

    excused = grade_figures("a local rehearsal reached 65 pass, 0 fail of 83\n", log)
    assert excused.findings == [] and excused.declared_uncitable == 1
    disposed = grade_figures(
        "the surface reached 65 pass, 0 fail, 16 could-not-look of 83.\n\n"
        "> **Correction, 2026-08-31.** The 65/0/16 figure was a rehearsal.\n", log)
    assert disposed.findings == [] and disposed.disposed == 1
    undated = grade_figures(
        "the surface reached 65 pass, 0 fail, 16 could-not-look of 83.\n\n"
        "> **Correction.** The 65/0/16 figure was a rehearsal.\n", log)
    assert [f.kind for f in undated.findings] == ["no-such-figure"], undated.findings
    print("ok  a declared rehearsal and a dated correction excuse a figure; an undated one does "
          "not")

    own = grade_figures(
        "the surface reached 65 pass, 0 fail, 16 could-not-look of 83.\n\n"
        "> **Correction, 2026-08-31.** The 65/0/16 figure was a rehearsal; the citable line is\n"
        "> run 13, 52/7/21 of 83.\n", log)
    assert [f.kind for f in own.findings] == ["figure-disagrees"], own.findings
    print("ok  a correction does not excuse the replacement figure it offers: that one is graded")

    manifest = {"verify/misuse/verify-misuse.sh", ".estate-clone/platform/verify-graded.sh"}
    assert grade_checks("`verify-graded.sh` and `verify/misuse`\n", manifest) == []
    absent = grade_checks("graded by `verify-nothing.sh`\n", manifest)
    assert [f.kind for f in absent] == ["check-not-in-the-gate"], absent
    assert grade_checks("`talk/verify-all.sh` discovers them\n", manifest) == []
    waiting: list[int] = []
    assert grade_checks("`verify-later.sh` (built, not yet merged)\n", manifest, waiting) == []
    assert waiting == [1], waiting
    print("ok  a check the manifest carries passes; one it does not is red unless the line says "
          "it is not in the gate yet, and then it is counted; the runner is not a check")

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
