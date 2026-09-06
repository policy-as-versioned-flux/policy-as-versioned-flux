#!/usr/bin/env python3
"""A cited TRUTH line is a real line whose tree carries the check (eco-system ticket 80 item 1).

THE DEFECT THIS EXISTS FOR. Fifteen resolved build tickets (21, 25, 26, 28, 29, 32, 36, 40, 41,
42, 43, 47, 49, 50, 52) closed with the sentence "its check is in `talk/verify-all.sh`. The run
that recorded it is the TRUTH line of 2026-08-29". That line is run 7, `hub=918022b`, graded on
2026-08-29T12:03Z -- BEFORE the build it is offered as proof of. Its tree carries three verify
directories (`party`, `proportionality`, `provenance`) and none of the fifteen checks. The record
cited a measurement that never measured the thing. Correcting fifteen files fixes fifteen files;
this module is what refuses the sixteenth.

THE RULE, in one sentence: a paragraph that offers a TRUTH line as proof that a check is in the
gate must cite a line `talk/truth.log` actually recorded, whose `hub=` commit this checkout can
read, whose TREE carries a check the ticket names -- or the ticket must carry a DATED correction
that names that citation.

The second rule is narrower and older: a TRUTH FIGURE (`pass=`, `fail=`, `skip=`, `excluded=`,
`total=`, `ceiling=`) quoted on the same text line as a run citation must be that run's figure.

WHAT THIS REFUSES TO GRADE, said plainly because a disclosed limit rots like any other claim:

  * It does not judge whether the check a ticket names is the RIGHT check for what the ticket
    built. No script can read that. It grades that the named check EXISTED in the tree that was
    measured -- necessary, never sufficient.
  * It reads `.scratch/ecosystem/issues/*.md` and nothing else. A figure quoted in `map.md`,
    `NORTH-STAR.md`, an ADR or the deck is somebody else's check (ticket 67(d), verify-demo.sh).
  * A figure with NO run citation beside it is out of scope -- prose says "about 70 of 84" and
    means it. The report COUNTS those lines rather than passing over them silently, so the size
    of the ungraded population is on the record every run.
  * A line that says of itself `fixture`, `planted`, `hypothetical`, `not citable` or `Actions
    log` is declared uncitable and is not graded. Those counts are printed too. This is the one
    escape hatch and it is deliberately loud: a builder who wants a figure ungraded must say in
    the text that it is not evidence.
  * `run=local` and `run=fixture` are not run numbers and never resolve. A local rehearsal is not
    a citable measurement (map.md's 2026-08-31 correction), so a claim resting on one fails here
    exactly as it should.

WHAT IT NEVER SHRUGS AT. There is no could-not-look. Every state in which it cannot see is RED,
each on its own named line, following verify/can-record/'s decision:

  * a cited `hub=` commit this checkout cannot resolve is `unreadable-tree` -- a tree nobody can
    read is not proof, and in a SHALLOW clone that is the honest answer rather than a shrug;
  * a cited line `talk/truth.log` does not record is `no-such-line`;
  * no git, no `talk/truth.log` and no issues directory are refusals in the shell wrapper.

The seam is pure: `report()` takes the file texts, the recorded log and a `tree_lookup` callable,
so every rule is exercised in tests/test_cited_truth.py with no git and no estate.

    cited_truth.py grade <hub-root>   # rules 1 and 2 above; 0 nothing false, 1 one or more named
    cited_truth.py record <hub-root>  # ticket 80's other nine corrections, as a fact table
    cited_truth.py selfcheck          # planted defects grade as planted
"""
from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Sequence

HERE = Path(__file__).resolve().parent
HUB = HERE.parents[1]

# The figure keys a TRUTH line carries. The split's inner keys (`observed`, `self`, `never`, ...)
# are deliberately absent: they live inside brackets and nobody quotes them alone.
FIGURE_KEYS = ("pass", "fail", "skip", "excluded", "total", "ceiling")
_FIGURE = re.compile(r"\b(" + "|".join(FIGURE_KEYS) + r")=(\d+)\b")

# "the TRUTH line of 2026-08-29", "TRUTH line of 2026-08-29"
_DATE_CITE = re.compile(r"TRUTH\s+line\s+of\s+(\d{4}-\d{2}-\d{2})", re.I)
# "run 7", "Run 22 of ...", "run=113". A run number is digits; `run=local` and `run=fixture` are
# not run numbers and are not citations. "the /implement run of 2026-08-28" has no digits after
# the word and is not one either.
_RUN_CITE = re.compile(r"\brun[= ](\d{1,4})\b", re.I)

# A paragraph offering a TRUTH line as proof that a check is in the gate.
_GATE_PROOF = re.compile(r"check(?:s)?\s+(?:is|are)\s+in\b[^.]{0,60}verify-all\.sh", re.I)

# A dated correction. The date is required: an undated correction is a claim with no time on it.
_CORRECTION = re.compile(r"\*\*Correct(?:ed|ion)[^*]*?(\d{4}-\d{2}-\d{2})", re.I)

# The words a line uses to say of itself that it is not evidence.
_UNCITABLE = ("fixture", "planted", "hypothetical", "not citable", "actions log", "rehearsal")

# A backticked token that names a check. `talk/verify-all.sh` is the RUNNER, never the check it
# is being offered as proof of, so it is excluded by name.
_CHECK_TOKEN = re.compile(r"^[\w./-]*verify[\w./-]*(?:\.sh|/)$")


@dataclass(frozen=True)
class Citation:
    kind: str          # "date" or "run"
    value: str
    lineno: int        # 1-based, within the file
    line: str


@dataclass(frozen=True)
class Finding:
    kind: str          # no-such-line | unreadable-tree | tree-lacks-the-check | figure-disagrees
    path: str
    lineno: int
    detail: str

    def __str__(self) -> str:
        return f"{self.path}:{self.lineno}: {self.kind}: {self.detail}"


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    claims_graded: int = 0
    citations_graded: int = 0
    unattributed: int = 0
    declared_uncitable: int = 0


TreeLookup = Callable[[str], "set[str] | None"]


# -- reading -------------------------------------------------------------------------------------

def _parse_truth() -> Callable[[str], dict]:
    """talk/truth_manifest.py's parser. One parser for the TRUTH line, not two."""
    spec = importlib.util.spec_from_file_location(
        "truth_manifest_for_cited_truth", HUB / "talk" / "truth_manifest.py")
    if spec is None or spec.loader is None:      # pragma: no cover - the wrapper refuses first
        raise SystemExit("FAIL: talk/truth_manifest.py is not readable")
    module = importlib.util.module_from_spec(spec)
    # registered before exec: truth_manifest defines dataclasses, and @dataclass reads
    # sys.modules[cls.__module__] while it builds the class
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.parse_truth


def recorded(log_text: str) -> list[dict]:
    """Every TRUTH line talk/truth.log records, parsed, newest last."""
    parse = _parse_truth()
    return [parse(line) for line in log_text.splitlines() if line.startswith("TRUTH ")]


def citations(text: str, lineno: int = 0) -> list[Citation]:
    """Every reference to a specific recorded run in `text`, in the order they appear."""
    out: list[Citation] = []
    for offset, line in enumerate(text.splitlines()):
        here = lineno + offset if lineno else offset + 1
        for m in _DATE_CITE.finditer(line):
            out.append(Citation("date", m.group(1), here, line))
        for m in _RUN_CITE.finditer(line):
            out.append(Citation("run", m.group(1), here, line))
    return out


def figures(line: str) -> dict[str, int]:
    """The TRUTH figures quoted on one text line."""
    return {k: int(v) for k, v in _FIGURE.findall(line)}


def named_checks(text: str) -> list[str]:
    """The check paths a ticket names in backticks, sorted; never the runner itself."""
    found = set()
    for token in re.findall(r"`([^`\n]+)`", text):
        token = token.strip()
        if not _CHECK_TOKEN.match(token):
            continue
        if token.rsplit("/", 1)[-1] == "verify-all.sh":
            continue
        found.add(token)
    return sorted(found)


def corrections(text: str) -> list[tuple[str, str]]:
    """(date, whole paragraph) for each dated correction in the file."""
    out: list[tuple[str, str]] = []
    for para in _paragraphs(text):
        m = _CORRECTION.search(para.text)
        if m:
            out.append((m.group(1), para.text))
    return out


@dataclass(frozen=True)
class _Para:
    lineno: int
    text: str


def _paragraphs(text: str) -> list[_Para]:
    paras: list[_Para] = []
    buf: list[str] = []
    start = 1
    for i, line in enumerate(text.splitlines(), start=1):
        if line.strip():
            if not buf:
                start = i
            buf.append(line)
        elif buf:
            paras.append(_Para(start, "\n".join(buf)))
            buf = []
    if buf:
        paras.append(_Para(start, "\n".join(buf)))
    return paras


def uncitable(line: str) -> bool:
    low = line.lower()
    return any(word in low for word in _UNCITABLE)


def uncitable_context(text: str) -> dict[int, str]:
    """Line number -> the text a `not citable` marker may live in for that line.

    A marker binds ONE LINE. Binding a whole paragraph was measured on the real record on
    2026-09-06 and laundered six figure lines that no sentence had disowned, which is the escape
    hatch swinging the wrong way.

    The single exception is a FENCED BLOCK, which inherits the paragraph directly above it: a
    verbatim TRUTH line quoted from the Actions log cannot carry a marker inside the fence
    without corrupting the quote, and the sentence introducing the fence is where the estate
    already says what the quote is. Nothing else inherits.
    """
    paras = _paragraphs(text)
    out: dict[int, str] = {}
    for i, para in enumerate(paras):
        lines = para.text.splitlines()
        fenced = lines and lines[0].lstrip().startswith("```")
        preamble = paras[i - 1].text + "\n" if fenced and i > 0 else ""
        for offset, line in enumerate(lines):
            out[para.lineno + offset] = preamble + line
    return out


# -- resolving -----------------------------------------------------------------------------------

def resolve(cite: Citation, log: Sequence[dict]) -> list[dict]:
    """The recorded lines a citation names. Empty means the estate never recorded it."""
    if cite.kind == "date":
        return [t for t in log if str(t.get("ts", "")).startswith(cite.value)]
    return [t for t in log if str(t.get("run", "")) == cite.value]


def _disposed(cite: Citation, corrs: Iterable[tuple[str, str]]) -> bool:
    """A dated correction that names this citation disposes of it."""
    for _date, para in corrs:
        if cite.kind == "date" and cite.value in para:
            return True
        if cite.kind == "run" and _RUN_CITE.search(para) and any(
                m.group(1) == cite.value for m in _RUN_CITE.finditer(para)):
            return True
    return False


def _tree_carries(tree: set[str], checks: Sequence[str]) -> list[str]:
    return [c for c in checks if any(p == c or p.startswith(c) for p in tree)]


# -- the rule ------------------------------------------------------------------------------------

def report(files: dict[str, str], log: Sequence[dict], tree_lookup: TreeLookup) -> Report:
    """Grade every citation in every file. `files` maps a display path to its text."""
    rep = Report()
    for path in sorted(files):
        text = files[path]
        corrs = corrections(text)
        checks = named_checks(text)
        context = uncitable_context(text)

        # rule 1: a TRUTH line offered as proof that a check is in the gate
        for para in _paragraphs(text):
            if not _GATE_PROOF.search(para.text):
                continue
            for cite in citations(para.text, para.lineno):
                if uncitable(context.get(cite.lineno, cite.line)):
                    rep.declared_uncitable += 1
                    continue
                rep.claims_graded += 1
                ok, why = _grade_proof(cite, log, tree_lookup, checks)
                if ok or _disposed(cite, corrs):
                    continue
                rep.findings.append(Finding(why[0], path, cite.lineno, why[1]))

        # rule 2: a figure quoted beside its run
        for lineno, line in enumerate(text.splitlines(), start=1):
            quoted = figures(line)
            if not quoted:
                continue
            if uncitable(context.get(lineno, line)):
                rep.declared_uncitable += 1
                continue
            cites = citations(line, lineno)
            if not cites:
                rep.unattributed += 1
                continue
            rep.citations_graded += 1
            cite = cites[0]
            lines = resolve(cite, log)
            if not lines:
                if not _disposed(cite, corrs):
                    rep.findings.append(Finding(
                        "no-such-line", path, lineno,
                        f"{_say(cite)} is quoted with {_show(quoted)}, and talk/truth.log records "
                        f"no such line"))
                continue
            if any(all(t.get(k) == v for k, v in quoted.items()) for t in lines):
                continue
            if _disposed(cite, corrs):
                continue
            got = ", ".join(_show({k: t.get(k) for k in quoted if t.get(k) is not None})
                            for t in lines[:2])
            rep.findings.append(Finding(
                "figure-disagrees", path, lineno,
                f"{_say(cite)} is quoted with {_show(quoted)}; the recorded line carries {got}"))
    return rep


def _grade_proof(cite: Citation, log: Sequence[dict], tree_lookup: TreeLookup,
                 checks: Sequence[str]) -> tuple[bool, tuple[str, str]]:
    lines = resolve(cite, log)
    if not lines:
        return False, ("no-such-line",
                       f"{_say(cite)} is offered as proof that a check is in the gate, and "
                       f"talk/truth.log records no such line")
    unreadable = []
    lacking = []
    for t in lines:
        hub = str(t.get("hub", ""))
        tree = tree_lookup(hub)
        if tree is None:
            unreadable.append(hub)
            continue
        if _tree_carries(tree, checks):
            return True, ("", "")
    if unreadable and not lacking:
        return False, ("unreadable-tree",
                       f"{_say(cite)} names hub commit(s) {', '.join(unreadable)}, which this "
                       f"checkout cannot read, so the tree that was measured cannot be shown to "
                       f"carry the check")
    named = ", ".join(checks) if checks else "no check path at all"
    hubs = ", ".join(str(t.get("hub", "")) for t in lines)
    return False, ("tree-lacks-the-check",
                   f"{_say(cite)} is offered as proof that a check is in the gate, but the tree "
                   f"of {hubs} carries none of the checks this ticket names ({named})")


def _say(cite: Citation) -> str:
    return (f"the TRUTH line of {cite.value}" if cite.kind == "date" else f"run {cite.value}")


def _show(d: dict) -> str:
    return " ".join(f"{k}={v}" for k, v in d.items())


def grade(files: dict[str, str], log: Sequence[dict], tree_lookup: TreeLookup) -> list[Finding]:
    return report(files, log, tree_lookup).findings


# -- ticket 80's other nine items, as a table of facts --------------------------------------------
#
# Item 1 is the rule above; it is the one that stops the NEXT defect. These are the nine
# corrections themselves: each is one sentence the record must carry, or one sentence it must no
# longer carry -- because a correction appended below a claim it never removed leaves the estate
# saying both things at once, which is the shape ticket 80 exists to end.
#
# NOT HERE, on purpose, and graded elsewhere:
#   * item 6 (the currency controller) closed on 2026-09-05 with ticket 91 and is graded by
#     platform's own `verify-currency.sh`. The one hub-side residue is in the table.
#   * item 10 (platform/README.md) is another party's repository. It is graded by that
#     repository's gate, on the pull request platform#15, and reading a working copy of somebody
#     else's README here would be the proxy this ticket is about.

@dataclass(frozen=True)
class Fact:
    item: int
    file: str
    pattern: str      # ERE-free: a literal substring, so the record can be read by eye
    want: bool        # True: the record must say it. False: the record must no longer say it.
    why: str
    example: str      # a text that satisfies this fact; the selfcheck and the tests use it


RECORD_FILES = {
    "adr/0004": "docs/adr/0004-cloud-plane-fork-collie.md",
    "adr/0007": "docs/adr/0007-agent-assisted-editorial-governance.md",
    "adr/0008": "docs/adr/0008-measurable-layered-ground-truth.md",
    "adr/0010": "docs/adr/0010-sunset-scheduled-proposals-not-application.md",
    "adr/0019": "docs/adr/0019-one-feed-envelope-signed-by-the-tag.md",
    "adr/0020": "docs/adr/0020-a-missing-instrument-refuses-a-missing-behaviour-is-priced.md",
    "adr/0021": "docs/adr/0021-the-twin-emits-a-scenario-the-estate-selects-the-tier.md",
    "adr/0022": "docs/adr/0022-the-cage-ladder-tier-per-namespace-isolated-rung-floor-and-infra.md",
    "adr/0023": "docs/adr/0023-a-clock-appends-observations-and-one-signature-verified-by-a-controller.md",
    "map": ".scratch/ecosystem/map.md",
    "runbook": "talk/RUNBOOK.md",
    "ticket75": ".scratch/ecosystem/issues/75-grilling-what-is-this-for-the-twelve-questions.md",
    "signpost": ".scratch/ecosystem/patches/ticket-80/legacy-signpost.md",
}

_DELEGATED = "**Delegated** ([ADR-0025](0025-the-assistant-decides-architecture-and-records-it.md)"

RECORD_FACTS: tuple[Fact, ...] = (
    # item 2 -- the two ADRs whose decisions were taken away and never said so
    Fact(2, "adr/0008", "> **Superseded in part, 2026-07-20 (the owner)", True,
         "the owner rejected the dashboard this ADR delivers 'measurable' through, on 2026-07-20",
         "> **Superseded in part, 2026-07-20 (the owner), written 2026-09-06.** dashboard"),
    Fact(2, "adr/0008", "dashboard", True,
         "the banner has to name the thing that was rejected",
         "> **Superseded in part, 2026-07-20 (the owner), written 2026-09-06.** dashboard"),
    Fact(2, "adr/0010", "> **Superseded in part, 2026-08-28 (eco-system ticket 13 D5)", True,
         "ticket 13 D5 decided the consumer-side `sunset:` away on 2026-08-28",
         "> **Superseded in part, 2026-08-28 (eco-system ticket 13 D5), written 2026-09-06.**"),
    # item 3 -- four accepted ADRs that never said what their acceptance rests on, and the fifth
    # whose line still used the word ADR-0025 point 4 retired
    Fact(3, "adr/0019", _DELEGATED, True, "ADR-0019 rests on a bare agree and must say so",
         _DELEGATED + " point 3): the owner agreed twice without a reason."),
    Fact(3, "adr/0020", _DELEGATED, True, "ADR-0020 rests on a bare agree and must say so",
         _DELEGATED + " point 3): reason given for the currency default only."),
    Fact(3, "adr/0021", _DELEGATED, True, "ADR-0021 rests on a bare agree and must say so",
         _DELEGATED + ' point 3): the owner answered "Lgtm".'),
    Fact(3, "adr/0022", _DELEGATED, True, "ADR-0022's line is re-labelled, not deleted",
         _DELEGATED + " point 3, re-labelled by ticket 80 item 3)."),
    Fact(3, "adr/0023", _DELEGATED, True, "ADR-0023 rests on a bare agree and must say so",
         _DELEGATED + " point 3): an endorsement is not a reason."),
    Fact(3, "adr/0022", "Provisional: the owner agreed", False,
         "ADR-0025 point 4 retires the word and names ticket 80 as what re-labels it",
         "Decided 2026-08-28. Provisional: the owner agreed\nwithout a reason."),
    # item 4 -- the Deny promotion, listed as an assistant-made call, not re-decided
    Fact(4, "ticket75", "## Assistant-made calls listed here, not re-decided", True,
         "ADR-0022's 2026-08-28 addendum promoted a rule to Deny inside an implementation run "
         "with no round, and nothing recorded whose call it was",
         "## Assistant-made calls listed here, not re-decided\ngoverned-namespace-requires-claim"),
    Fact(4, "ticket75", "governed-namespace-requires-claim", True,
         "the entry has to name the rule that was promoted",
         "## Assistant-made calls listed here, not re-decided\ngoverned-namespace-requires-claim"),
    # item 5 -- GAPS process rule 1, dropped when the rules were copied into the map
    Fact(5, "map", "No recommendation is attached to a question put to the owner", True,
         "GAPS process rule 1 was dropped in the copy; its first half still binds the questions "
         "that reach the owner",
         "**No recommendation is attached to a question put to the owner: state the trade.** "
         "(GAPS process rule 1, restored 2026-09-06.)"),
    # item 6 -- the hub-side residue of the un-retirement (the module itself is platform's)
    Fact(6, "map", "The currency controller is retired", False,
         "ticket 75 Q13 withdrew the retirement and ticket 91 executed it on 2026-09-05",
         "Not yet specified: The currency controller is retired (ticket 13)."),
    # item 7 -- the three ADR notes ticket 13 assigned itself and never wrote
    Fact(7, "adr/0004", "Sequencing note, 2026-08-28 (eco-system ticket 13 Q3)", True,
         "ticket 13 Q3 settled where the cloud plane lands and when it is built",
         "## Sequencing note, 2026-08-28 (eco-system ticket 13 Q3)"),
    Fact(7, "adr/0007", "**Confirmed 2026-08-28 (eco-system ticket 13 Q4)", True,
         "the last-mile section carried '(proposed - confirm)' inside an accepted ADR",
         "> **Confirmed 2026-08-28 (eco-system ticket 13 Q4).** a compose-time render"),
    Fact(7, "adr/0007", "Last-mile to non-technical consumers (proposed", False,
         "an accepted ADR does not carry an unconfirmed section",
         "## Last-mile to non-technical consumers (proposed — confirm)"),
    # item 8 -- the runbook's untrue reconcile line
    Fact(8, "runbook", "Corrected 2026-09-06 (eco-system ticket 80 item 8)", True,
         "section 1 said driftwood's bring-up reconciles the real signed GitHub remote; "
         "scripts/up.sh reconciles an unsigned tag from a git server built on the laptop",
         "> **Corrected 2026-09-06 (eco-system ticket 80 item 8).** the in-cluster git server"),
    Fact(8, "runbook", "pointed at the\n   real `policy-as-versioned-driftwood` GitHub repo", False,
         "the false sentence is removed, not merely annotated",
         "1. `up.sh` — KinD `driftwood` + Flux, pointed at the\n"
         "   real `policy-as-versioned-driftwood` GitHub repo + reconcile."),
    # item 9 -- declined, with the material recorded and marked as not applied
    Fact(9, "signpost", "**Nothing in this file has been applied to any repository.**", True,
         "the legacy signpost is an enactment the build brief does not authorise and an org "
         "description this token cannot write; the material is held, and says it is not applied",
         "**Nothing in this file has been applied to any repository.**"),
)


def record_facts(files: dict[str, str]) -> list[Finding]:
    """Grade ticket 80's corrections themselves. `files` maps a RECORD_FILES key to its text."""
    out: list[Finding] = []
    for fact in RECORD_FACTS:
        text = files.get(fact.file)
        if text is None:
            out.append(Finding("record-fact", fact.file, 0,
                               f"item {fact.item}: {RECORD_FILES.get(fact.file, fact.file)} is "
                               f"not readable, so the correction cannot be graded"))
            continue
        present = fact.pattern in text
        if fact.want and not present:
            out.append(Finding("record-fact", fact.file, 0,
                               f"item {fact.item}: {fact.pattern!r} is not in "
                               f"{RECORD_FILES[fact.file]} -- {fact.why}"))
        elif not fact.want and present:
            out.append(Finding("record-fact", fact.file, 0,
                               f"item {fact.item}: {RECORD_FILES[fact.file]} still says "
                               f"{fact.pattern!r} -- {fact.why}"))
    return out


def _read_record(root: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for name, rel in RECORD_FILES.items():
        p = root / rel
        if p.is_file():
            out[name] = p.read_text(encoding="utf-8")
    return out


# -- the real three ------------------------------------------------------------------------------

def git_tree_lookup(root: Path) -> TreeLookup:
    """Paths in a commit's tree, or None when this checkout cannot read that commit."""
    cache: dict[str, set[str] | None] = {}

    def lookup(commit: str) -> set[str] | None:
        if commit not in cache:
            try:
                out = subprocess.run(["git", "-C", str(root), "ls-tree", "-r", "--name-only",
                                      commit], capture_output=True, text=True, timeout=60)
            except (OSError, subprocess.SubprocessError):
                cache[commit] = None
                return None
            cache[commit] = set(out.stdout.split()) if out.returncode == 0 else None
        return cache[commit]

    return lookup


def _issue_files(root: Path) -> dict[str, str]:
    issues = root / ".scratch" / "ecosystem" / "issues"
    return {str(p.relative_to(root)): p.read_text(encoding="utf-8")
            for p in sorted(issues.glob("*.md"))}


def _run_record(root: Path) -> int:
    findings = record_facts(_read_record(root))
    for f in findings:
        print(f"  !! {f}")
    items = sorted({fact.item for fact in RECORD_FACTS})
    print(f"  {len(RECORD_FACTS)} sentence(s) graded across items {items}, in "
          f"{len(RECORD_FILES)} files")
    print("  item 1 is graded above; item 6 by platform's verify-currency.sh (only its hub-side "
          "residue is here); item 10 by platform's own gate on that repository's pull request")
    return 1 if findings else 0


def _run(root: Path) -> int:
    log = recorded((root / "talk" / "truth.log").read_text(encoding="utf-8"))
    files = _issue_files(root)
    rep = report(files, log, git_tree_lookup(root))
    for f in sorted(rep.findings, key=lambda f: (f.path, f.lineno)):
        print(f"  !! {f}")
    print(f"  {len(files)} ticket files, {len(log)} recorded TRUTH lines, "
          f"{rep.claims_graded} gate-proof citation(s) and {rep.citations_graded} quoted "
          f"figure line(s) graded")
    print(f"  not graded, on the record: {rep.unattributed} line(s) quote a figure with no run "
          f"beside it; {rep.declared_uncitable} line(s) say of themselves that they are not "
          f"citable")
    return 1 if rep.findings else 0


# -- selfcheck -----------------------------------------------------------------------------------

_LOG = ("TRUTH 2026-08-29T12:03Z run=7 hub=aaaaaaa units=[p=1] pass=43 fail=11 skip=0 "
        "excluded=2 total=56\n")
_PROOF = ("Built it. `verify/thing/verify-thing.sh` grades it.\n\n"
          "Definition of done: its check is in `talk/verify-all.sh`. The run that recorded it "
          "is the TRUTH line of 2026-08-29.\n")


def selfcheck() -> int:
    log = recorded(_LOG)
    good: TreeLookup = lambda c: {"verify/thing/verify-thing.sh"} if c == "aaaaaaa" else None
    bad: TreeLookup = lambda c: {"verify/other/verify-other.sh"} if c == "aaaaaaa" else None
    blind: TreeLookup = lambda c: None
    problems = []
    if grade({"a.md": _PROOF}, log, good):
        problems.append("a proof whose cited tree carries the check was graded false")
    if [f.kind for f in grade({"a.md": _PROOF}, log, bad)] != ["tree-lacks-the-check"]:
        problems.append("a proof whose cited tree lacks the check was not named")
    if [f.kind for f in grade({"a.md": _PROOF}, log, blind)] != ["unreadable-tree"]:
        problems.append("a proof whose cited commit cannot be read was not named")
    missing = _PROOF.replace("2026-08-29", "2026-08-30")
    if [f.kind for f in grade({"a.md": missing}, log, good)] != ["no-such-line"]:
        problems.append("a proof citing a line nobody recorded was not named")
    fixed = _PROOF + ("\n> **Correction, 2026-09-06 (ticket 80).** The TRUTH line of 2026-08-29 "
                      "is run 7, graded before the build.\n")
    if grade({"a.md": fixed}, log, bad):
        problems.append("a dated correction naming the citation did not dispose of it")
    undated = _PROOF + "\n> **Correction (ticket 80).** It over-claimed.\n"
    if not grade({"a.md": undated}, log, bad):
        problems.append("an UNDATED correction disposed of a false proof")
    if [f.kind for f in grade({"a.md": "Run 7 shows pass=99.\n"}, log, good)] != \
            ["figure-disagrees"]:
        problems.append("a figure that disagrees with its own run was not named")
    if grade({"a.md": "Run 7 shows pass=43 fail=11.\n"}, log, good):
        problems.append("a figure that agrees with its own run was graded false")
    rep = report({"a.md": "a planted line: pass=5 fail=3\n\nsomewhere pass=57 total=84\n"},
                 log, good)
    if (rep.findings, rep.declared_uncitable, rep.unattributed) != ([], 1, 1):
        problems.append("the declared-uncitable and unattributed counts do not add up")
    clean = {name: "" for name in RECORD_FILES}
    if len(record_facts(clean)) != len([f for f in RECORD_FACTS if f.want]):
        problems.append("an empty record did not produce one finding per required sentence")
    banned = next(f for f in RECORD_FACTS if not f.want)
    if not [f for f in record_facts(dict(clean, **{banned.file: banned.example}))
            if "still says" in f.detail]:
        problems.append("a sentence the correction had to remove came back and was not named")
    if record_facts({}) == []:
        problems.append("an unreadable record file graded as if it were fine")
    if problems:
        for p in problems:
            print(f"  !! {p}")
        print("FAIL: selfcheck: the grader does not grade")
        return 1
    print("  ok   selfcheck: a carried check passes; a lacking tree, an unreadable commit, an "
          "unrecorded line and a disagreeing figure each fail by name; a dated correction "
          "disposes and an undated one does not; the ungraded populations are counted; the "
          "fact table names a missing sentence, a removed sentence that came back and an "
          "unreadable file")
    return 0


def main(argv: Sequence[str]) -> int:
    if len(argv) >= 2 and argv[1] == "selfcheck":
        return selfcheck()
    if len(argv) >= 2 and argv[1] == "grade":
        return _run(Path(argv[2]) if len(argv) > 2 else HUB)
    if len(argv) >= 2 and argv[1] == "record":
        return _run_record(Path(argv[2]) if len(argv) > 2 else HUB)
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
