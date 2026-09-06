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

WHAT "NAMES A CHECK" MEANS, and why it is narrow (review F1, 2026-09-06). The first cut of this
module asked whether the cited tree carried ANY backticked token containing the word `verify`,
anywhere in the file, by string prefix. Three ways that was cheaper than resolving the check:
a bare `verify/` is a prefix of every hub check that has ever existed; a directory naming no
script satisfied it; and ticket 80's OWN twelve corrections name `verify/party/`,
`verify/proportionality/` and `verify/provenance/` -- run 7's three directories -- so all twelve
passed on the correction's own words and the dated correction never did any work. Now: the token
must be a `verify*.sh` matched by path suffix, or a directory the CITED TREE carries a
`verify*.sh` under; it is read from the SECTION the claim is made in, with correction paragraphs
stripped whether or not they are dated. What remains, and is not closable by reading text: a
ticket that names, in its own Answer, a check it does not own and the cited tree happens to
carry, passes. That is the reason rule 1 is necessary and never sufficient.

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
  * A line that says of itself, in those words, `not citable` -- or quotes a TRUTH line carrying
    the runner's own `fixture=1` token -- is not graded. This is the one escape hatch and it is
    deliberately loud. It is TWO FIXED PHRASES and not a bag of words: a bag of words exempted
    "no fixture was used", "this is not a rehearsal" and "as the Actions log confirms", each of
    which asserts the opposite of a disclaimer (review F2). A negated occurrence is refused, the
    hatch is spent only where it actually suppresses a grade, and EVERY exempted line is printed
    by path and line, not merely counted -- an escape hatch nobody can see is not an escape hatch.
  * A citation in a paragraph that is not a gate-proof at all: outside rule 1 by construction,
    and counted as a third printed population.
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
# "run 7", "Run 22 of ...", "run=113", "Run #7". A run number is digits; `run=local` and
# `run=fixture` are not run numbers and are not citations. "the /implement run of 2026-08-28" has
# no digits after the word and is not one either.
# `(?!-\d)` keeps a DATE out: "the /implement run 2026-09-04" is not a citation of run 2026.
_RUN_CITE = re.compile(r"\brun(?:\s*[=#]\s*|\s+#?)(\d{1,4})\b(?!-\d)", re.I)

# A paragraph offering a TRUTH line as proof that a check is in the gate. Matched against the
# paragraph with its newlines COLLAPSED (review F3, 2026-09-06): the sentence is line-wrapped in
# most tickets, and matching per physical line missed the wrap. Three spellings, because the
# estate uses all three: the done-line's "its check is in `talk/verify-all.sh`", "wired into the
# gate" (the map's own words for the same obligation) and a bare "in the gate". Each only counts
# as a gate-proof where the same paragraph also carries a TRUTH citation.
_GATE_PROOF = re.compile(
    r"check(?:s)?\s+(?:is|are)\s+in\b[^.]{0,80}verify-all\.sh"
    r"|wired\s+into\s+the\s+gate"
    r"|\bin\s+the\s+gate\b", re.I)

# A dated correction. The date must follow the word DIRECTLY (review F4): `**Correction,
# 2026-09-06`, `**Corrected 2026-09-04`. Before that it was `[^*]*?`, so an UNDATED correction
# that merely mentioned a date somewhere in its body read as dated.
_CORRECTION = re.compile(r"\*\*Correct(?:ed|ion)[^*\n]{0,3}?(\d{4}-\d{2}-\d{2})", re.I)
# ...and the looser shape, used ONLY to strip a paragraph out of `named_checks`. A correction
# says what a citation failed to prove and may never supply the proof, and that holds whether or
# not it carries a date -- otherwise deleting the date from a correction hands its tokens back.
_CORRECTION_ANY = re.compile(r"\*\*Correct(?:ed|ion)\b", re.I)

# THE ESCAPE HATCH (review F2, 2026-09-06). Two FIXED PHRASES, not a bag of words. A bag of words
# exempted "no fixture was used", "this is not a rehearsal" and "as the Actions log confirms",
# each of which asserts the OPPOSITE of a disclaimer, and each surfaced only as +1 in a count. A
# line that wants its figure ungraded says `not citable`, in those words, or quotes a TRUTH line
# carrying the runner's own `fixture=1` token. `_NEGATION` then rejects an occurrence that is
# itself negated; phrases beginning "not" are exempt from that test, being negative already.
_UNCITABLE = ("not citable", "fixture=1")
# The negation must MODIFY the phrase, so the window is short: 12 characters, about one word.
# At 30 it swallowed "no run recorded it, so it is not citable", which disowns its figure
# perfectly well. `not` is in the list since R2-1, which is why the phrase's own leading
# "not" must not be visible here -- it never is, because only the text BEFORE it is tested.
_NEGATION = re.compile(
    r"(?:\bnot\b|\bno\b|\bwithout\b|\bnever\b)[^.]{0,12}$", re.I)
# A marker inside a `code span` or a [link](target) is quoting the phrase, not spending it
# (review R2-1). Both are blanked -- not deleted, so every offset the caller holds still lines
# up with the text it came from.
_CODE_SPAN = re.compile(r"`[^`\n]*`")
_LINK_TARGET = re.compile(r"\]\([^)\n]*\)")

# A backticked token that names a check. Two shapes and nothing else (review F1):
#   * a SCRIPT, `[path/]verify*.sh` -- matched against a tree by path suffix, because tickets
#     name `verify-demo.sh` and the tree carries `talk/verify-demo.sh`;
#   * a DIRECTORY, `.../verify.../`, which counts only where the CITED TREE carries a
#     `verify*.sh` under it. A directory that resolves to no script names no check.
# `talk/verify-all.sh` is the RUNNER, never the check it is offered as proof of, and a bare
# `verify/` is a prefix of every hub check that has ever existed. Both are excluded by name.
_CHECK_TOKEN = re.compile(r"^[\w./-]*verify[\w./-]*(?:\.sh|/)$")
_SCRIPT_NAME = re.compile(r"(?:^|/)verify[\w.-]*\.sh$")

# How near a citation must sit to a gate-proof phrase, in the flattened paragraph, to be read as
# offered in support of it. The done-line's own two sentences span about 90 characters.
GATE_PROOF_REACH = 200


@dataclass(frozen=True)
class Citation:
    kind: str          # "date" or "run"
    value: str
    lineno: int        # 1-based, within the file
    line: str
    at: int = -1       # offset in the flattened paragraph, for the proximity test


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
    # every exempted line, named: (path, lineno, the phrase that exempted it). A count alone
    # cannot be read, and an escape hatch nobody can see is not an escape hatch (review F2).
    exempted: list[tuple[str, int, str]] = field(default_factory=list)
    # citations in a paragraph that is NOT a gate-proof: outside rule 1 by construction, counted
    # so the size of what rule 1 never looks at is on the record too (review F3).
    outside_the_rule: int = 0


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
            out.append(Citation("date", m.group(1), here, line, m.start()))
        for m in _RUN_CITE.finditer(line):
            out.append(Citation("run", m.group(1), here, line, m.start()))
    return out


def figures(line: str) -> dict[str, int]:
    """The TRUTH figures quoted on one text line."""
    return {k: int(v) for k, v in _FIGURE.findall(line)}


def named_checks(text: str) -> list[str]:
    """The check paths a ticket names in backticks, sorted.

    CORRECTION PARAGRAPHS ARE STRIPPED FIRST (review F1, 2026-09-06). Ticket 80's own correction
    names `verify/party/`, `verify/proportionality/` and `verify/provenance/` -- the three
    directories run 7's tree actually carries -- so with corrections in scope the twelve corrected
    tickets satisfied rule 1 on the correction's own words, and the dated correction never did
    any work. A correction says what the citation FAILED to prove; it cannot supply the proof.

    Never the runner (`talk/verify-all.sh`), and never a bare `verify/`, which is a prefix of
    every hub check that has ever existed.
    """
    body = "\n\n".join(para.text for para in _paragraphs(text)
                        if not _CORRECTION_ANY.search(para.text))
    found = set()
    for token in re.findall(r"`([^`\n]+)`", body):
        token = token.strip()
        if not _CHECK_TOKEN.match(token):
            continue
        if token.rsplit("/", 1)[-1] == "verify-all.sh":
            continue
        if token.strip("/") == "verify":
            continue
        found.add(token)
    return sorted(found)


def unquote_flat(text: str) -> str:
    """A paragraph as one line: blockquote and list markers stripped, whitespace collapsed.

    Review F3/F4, 2026-09-06. Every sentence in these files is hard-wrapped at about 96 columns
    and most corrections are blockquotes, so "the TRUTH\n> line of 2026-08-29" was invisible to a
    per-line scan -- including inside ticket 80's OWN twelve corrections, which is how a
    correction that names its citation perfectly could fail to dispose of it.
    """
    lines = [re.sub(r"^\s*(?:>\s?)+", "", line) for line in text.splitlines()]
    return " ".join(" ".join(lines).split())


def para_citations(para_text: str, lineno: int) -> list[Citation]:
    """Citations in one paragraph, read from its FLATTENED text, reported at the line the value
    appears on so a finding still points somewhere a reader can look."""
    lines = para_text.splitlines()
    out: list[Citation] = []
    for cite in citations(unquote_flat(para_text)):
        at, line = lineno, lines[0] if lines else ""
        for offset, raw in enumerate(lines):
            if cite.value in raw:
                at, line = lineno + offset, raw
                break
        out.append(Citation(cite.kind, cite.value, at, line, cite.at))
    return out


def section_of(text: str, lineno: int) -> str:
    """The `## ...` section a line falls in (review F1): the proof must be named where the claim
    is made, not anywhere in a 300-line ticket. Text before the first heading is one section."""
    starts = [1] + [n for n, line in enumerate(text.splitlines(), start=1)
                    if line.startswith("## ")]
    lines = text.splitlines()
    begin = max(s for s in starts if s <= lineno)
    later = [s for s in starts if s > begin]
    end = (later[0] - 1) if later else len(lines)
    return "\n".join(lines[begin - 1:end])


def corrections(text: str) -> list[tuple[str, str]]:
    """(date, the paragraph flattened) for each dated correction in the file."""
    out: list[tuple[str, str]] = []
    for para in _paragraphs(text):
        m = _CORRECTION.search(para.text)
        if m:
            out.append((m.group(1), unquote_flat(para.text)))
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


def _blank(pattern: re.Pattern[str], text: str) -> str:
    """Replace each match with spaces of the same length, so offsets do not move."""
    return pattern.sub(lambda m: " " * len(m.group(0)), text)


def uncitable(line: str) -> str | None:
    """The fixed phrase by which this text disowns its own figure, or None.

    A negated occurrence is not a disclaimer: "it is not a not citable line" and "this does not
    make it not citable" each assert the opposite of one. Every phrase is put through that test,
    including the ones beginning "not": only the text BEFORE an occurrence is examined, so a
    phrase never negates itself.

    Code spans and link targets are blanked first (review R2-1): `not citable` inside backticks or
    inside a URL is the phrase being QUOTED, not a line disowning its own figure.
    """
    low = _blank(_CODE_SPAN, _blank(_LINK_TARGET, line)).lower()
    for phrase in _UNCITABLE:
        start = low.find(phrase)
        while start != -1:
            if not _NEGATION.search(low[:start]):
                return phrase
            start = low.find(phrase, start + 1)
    return None


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
    """A dated correction that names this citation AS A CITATION disposes of it.

    Review F4: a bare date is not a citation. "Something else happened on 2026-08-29" in a dated
    correction used to dispose of a claim resting on the TRUTH line of that day, because the test
    was a substring match on the date. The correction must name the LINE -- "the TRUTH line of
    2026-08-29", "run 7" -- which is exactly what `citations()` reads.
    """
    for _date, para in corrs:
        for named in citations(para):
            if named.kind == cite.kind and named.value == cite.value:
                return True
    return False


def tree_carries(tree: set[str], checks: Sequence[str]) -> list[str]:
    """Which of `checks` this tree actually RESOLVES to a script (review F1).

    A script token matches by path SUFFIX at a path boundary, because tickets name
    `verify-demo.sh` and the tree carries `talk/verify-demo.sh`. A directory token matches only
    where the tree carries a `verify*.sh` UNDER it -- a directory that resolves to no script
    names no check, which is what `startswith` alone could not tell.
    """
    out = []
    for c in checks:
        if c.endswith("/"):
            if any(p.startswith(c) and _SCRIPT_NAME.search(p) for p in tree):
                out.append(c)
        elif any(p == c or p.endswith("/" + c) for p in tree):
            out.append(c)
    return out


# -- the rule ------------------------------------------------------------------------------------

def report(files: dict[str, str], log: Sequence[dict], tree_lookup: TreeLookup) -> Report:
    """Grade every citation in every file. `files` maps a display path to its text."""
    rep = Report()
    for path in sorted(files):
        text = files[path]
        corrs = corrections(text)
        context = uncitable_context(text)

        # rule 1: a TRUTH line offered as proof that a check is in the gate.
        # The trigger is matched against the paragraph with its NEWLINES COLLAPSED (review F3):
        # the done-line is wrapped in most tickets and a per-line match missed the wrap.
        for para in _paragraphs(text):
            flat = unquote_flat(para.text)
            # PROXIMITY, not mere co-occurrence (2026-09-06, after the widened trigger fired on a
            # ticket-18 sentence 700 characters from the words "in the gate"). A gate-proof
            # citation is one that sits within GATE_PROOF_REACH characters of the phrase in the
            # flattened paragraph -- about a sentence either side, which is the distance the
            # done-line's own two sentences span.
            spans = [m.start() for m in _GATE_PROOF.finditer(flat)]
            for cite in para_citations(para.text, para.lineno):
                proof = any(abs(s - cite.at) <= GATE_PROOF_REACH for s in spans)
                if not proof:
                    rep.outside_the_rule += 1
                    continue
                phrase = uncitable(context.get(cite.lineno, cite.line))
                if phrase:
                    rep.declared_uncitable += 1
                    rep.exempted.append((path, cite.lineno, phrase))
                    continue
                rep.claims_graded += 1
                checks = named_checks(section_of(text, para.lineno))
                ok, why = _grade_proof(cite, log, tree_lookup, checks)
                if ok or _disposed(cite, corrs):
                    continue
                rep.findings.append(Finding(why[0], path, cite.lineno, why[1]))

        # rule 2: a figure quoted beside its run
        for lineno, line in enumerate(text.splitlines(), start=1):
            quoted = figures(line)
            if not quoted:
                continue
            # the citation comes FIRST: the hatch may only be spent where it actually suppresses
            # a grade. Measured on ticket 75 line 45, where "not citable" belonged to a
            # neighbouring clause about something else and the figure on that line had no run
            # beside it, so nothing was ever going to be graded. An exemption that suppresses
            # nothing must not be reported as one, or the printed list stops meaning what it says.
            cites = citations(line, lineno)
            if not cites:
                rep.unattributed += 1
                continue
            phrase = uncitable(context.get(lineno, line))
            if phrase:
                rep.declared_uncitable += 1
                rep.exempted.append((path, lineno, phrase))
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
        if tree_carries(tree, checks):
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
    "ticket13": ".scratch/ecosystem/issues/13-lift-or-retire-the-original-mechanisms.md",
    "adr/0025": "docs/adr/0025-the-assistant-decides-architecture-and-records-it.md",
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
    # ONE LOAD-BEARING SENTENCE PER ITEM (review F5, 2026-09-06). A marker sentence alone is a
    # heading: ADR-0019 gutted to its `**Delegated**` prefix, or the runbook with its correction
    # reduced to a title, both stayed green. These are the sentences that carry the correction's
    # meaning, so gutting one is a red.
    Fact(2, "adr/0008", "What survives:", True,
         "the ADR-0008 banner has to say what the supersession leaves standing, or it reads as a "
         "retraction of the whole ADR",
         "**What survives:** the four signals. **What is superseded:** the dashboard."),
    Fact(2, "adr/0010", "consumer-side `sunset:` field is not carried", True,
         "the ADR-0010 banner's load-bearing clause",
         "The **consumer-side `sunset:` field is not carried into the eco-system.**"),
    Fact(3, "adr/0019", "rests on a bare agree, not a ratification", True,
         "the sentence is the point; the label alone is a heading",
         "It rests on a bare agree, not a ratification."),
    Fact(3, "adr/0023", "rests on a bare agree, not a ratification", True,
         "the sentence is the point; the label alone is a heading",
         "It rests on a bare agree, not a ratification."),
    Fact(7, "adr/0004", "cloud plane lands in **tuppence**", True,
         "the sequencing note's load-bearing clause: WHERE it lands",
         "The cloud plane lands in **tuppence**, beside the lifted `ledger` workload."),
    Fact(7, "adr/0007", "compose-time render", True,
         "the confirmed section's mechanism; without it the confirmation confirms nothing",
         "the handbook is a **compose-time render**."),
    Fact(8, "runbook", "an unsigned tag from a git server built on this machine", True,
         "the runbook correction's load-bearing clause: what the beat actually reconciles",
         "reconciles **an unsigned tag from a git server built on this machine out of the local "
         "working tree**"),
    # item 3 -- the ruling that came with the re-labelling, recorded where it contradicts the
    # older record (review F6): ticket 13's Answer, the map's batch record and ADR-0025 itself
    Fact(3, "ticket13", "Re-labelled 2026-09-06 (ticket 80 item 3", True,
         "ticket 13 still read 'Q5 is recorded as DECIDED'; the record cannot say both",
         "**Re-labelled 2026-09-06 (ticket 80 item 3, delegated under ADR-0025).**"),
    Fact(3, "map", "re-labelled delegated 2026-09-06", True,
         "map.md's batch record still read 'those five are decided'",
         "those five were recorded as decided -- **re-labelled delegated 2026-09-06**"),
    Fact(3, "adr/0025", "what point 3 does to the five panel decisions", True,
         "the ruling is an interpretation of point 3, not an application of point 4, and belongs "
         "in the ADR it interprets rather than inside one banner",
         "## Note, 2026-09-06: what point 3 does to the five panel decisions"),
    # item 9 -- declined, with the material recorded and marked as not applied
    Fact(9, "signpost", "**Nothing in this file has been applied to any repository.**", True,
         "the legacy signpost is an enactment the build brief does not authorise and an org "
         "description this token cannot write; the material is held, and says it is not applied",
         "**Nothing in this file has been applied to any repository.**"),
)


def _flat(text: str) -> str:
    """Whitespace normalised to single spaces (review F5).

    Every sentence in these files is hard-wrapped at about 96 columns, so a literal pattern that
    spans a wrap matched neither the record nor a restored false claim written on one line. The
    fact table is about what the record SAYS, not how it is folded.
    """
    return " ".join(text.split())


def record_facts(files: dict[str, str]) -> list[Finding]:
    """Grade ticket 80's corrections themselves. `files` maps a RECORD_FILES key to its text."""
    out: list[Finding] = []
    unreadable: set[str] = set()
    for fact in RECORD_FACTS:
        text = files.get(fact.file)
        if text is None:
            # one line per missing FILE, not per fact that wanted it (review F9)
            if fact.file not in unreadable:
                unreadable.add(fact.file)
                items = sorted({f.item for f in RECORD_FACTS if f.file == fact.file})
                out.append(Finding("record-fact", fact.file, 0,
                                   f"item(s) {items}: {RECORD_FILES.get(fact.file, fact.file)} "
                                   f"is not readable, so the correction cannot be graded"))
            continue
        body = text if fact.want else "\n\n".join(
            para.text for para in _paragraphs(text) if not _CORRECTION_ANY.search(para.text))
        present = _flat(fact.pattern) in _flat(body)
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
    truth = root / "talk" / "truth.log"
    issues = root / ".scratch" / "ecosystem" / "issues"
    missing = [str(q.relative_to(root)) for q in (truth, issues) if not q.exists()]
    if missing:
        # review F9: the wrapper has already named these; do not print them twice, and never
        # let a traceback follow a red that was reported properly
        print(f"  not graded: {', '.join(missing)} is missing (named above)")
        return 1
    log = recorded(truth.read_text(encoding="utf-8"))
    files = _issue_files(root)
    rep = report(files, log, git_tree_lookup(root))
    for f in sorted(rep.findings, key=lambda f: (f.path, f.lineno)):
        print(f"  !! {f}")
    print(f"  {len(files)} ticket files, {len(log)} recorded TRUTH lines, "
          f"{rep.claims_graded} gate-proof citation(s) and {rep.citations_graded} quoted "
          f"figure line(s) graded")
    print(f"  not graded, on the record: {rep.unattributed} line(s) quote a figure with no run "
          f"beside it; {rep.declared_uncitable} line(s) say of themselves that they are not "
          f"citable; {rep.outside_the_rule} citation(s) sit in no gate-proof paragraph")
    # every exemption is NAMED, not only counted (review F2): an escape hatch nobody can see is
    # not an escape hatch, and the reader has to be able to check each one by eye.
    for path, lineno, phrase in rep.exempted:
        print(f"  -- exempt  {path}:{lineno}  ({phrase})")
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
    rep = report({"a.md": "run 7, not citable here: pass=5 fail=3\n\nsomewhere pass=57 "
                          "total=84\n"}, log, good)
    if (rep.findings, rep.declared_uncitable, rep.unattributed) != ([], 1, 1):
        problems.append("the declared-uncitable and unattributed counts do not add up")
    if rep.exempted != [("a.md", 1, "not citable")]:
        problems.append("the exempted line was counted but not named")
    spent = report({"a.md": "no run beside it, and not citable anyway: pass=5\n"}, log, good)
    if spent.exempted or spent.unattributed != 1:
        problems.append("the hatch was spent on a line that was never going to be graded")
    for quoted in ("run 7: grep for `not citable` in the log, pass=99\n",
                   "run 7, see [why](docs/it-is-not-citable.md), pass=99\n",
                   "run 7: this does not make it not citable, pass=99\n"):
        q = report({"a.md": quoted}, log, good)
        if [f.kind for f in q.findings] != ["figure-disagrees"] or q.exempted:
            problems.append(f"a quoted or negated marker exempted a line: {quoted.strip()!r}")
    for negated in ("Run 7 shows pass=99, and no fixture was used.\n",
                    "Run 7 shows pass=99; this is not a rehearsal.\n"):
        neg = report({"a.md": negated}, log, good)
        if [f.kind for f in neg.findings] != ["figure-disagrees"] or neg.declared_uncitable:
            problems.append(f"a negated marker exempted a line: {negated.strip()!r}")
    if ct_named := named_checks("under `verify/`"):
        problems.append(f"a bare `verify/` was read as a named check: {ct_named}")
    if tree_carries({"verify/party/README.md"}, ["verify/party/"]):
        problems.append("a directory carrying no verify script was read as a named check")
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
          "disposes and an undated one does not; a bare `verify/` and a directory carrying "
          "no script name no check; a marker that is negated, quoted in a code span or "
          "sitting in a link target exempts nothing; every exempted "
          "line is named as well as counted; the fact table names a missing sentence, a "
          "removed sentence that came back and an unreadable file")
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
