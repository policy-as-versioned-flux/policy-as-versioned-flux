#!/usr/bin/env python3
"""Ticket `Status:` is derived from a named check (NORTH-STAR §5, eco-system ticket 59).

§5: "Ticket `Status:` is derived from a named check, in the way `twin grade` already derives
depth from `twin/capabilities/*.yaml`." twin/grades.py's rule is the model: `full` cannot be
TYPED, it is computed from the owning ticket's acceptance criteria, and a stated grade that
disagrees with the computed one is refused. Sixteen tickets free-typed `Status: open` when the
ambition review of 2026-08-31 counted them (M14) and seven free-typed a parenthetical after
`resolved` by 2026-09-06. Nothing anywhere derived a Status from anything.

WHAT IT DERIVES FROM, and this is the part that took the work. The TRUTH line carries the
COUNTS; until ticket 59 nothing carried the GRADE of each named script, so there was nothing to
derive from. The captures are not it: talk/verify-all.sh grades a script by its EXIT CODE and a
capture's last line is only the reason -- on 2026-09-06, 29 of 107 captures ended in the
continuation of a multi-line `PASS:` sentence, so reading a grade out of one is a proxy, and
two of the twelve tickets a proxy-based prototype named were named wrongly for exactly that
reason. So talk/verify-all.sh now writes `talk/captures/_grades.tsv`, one row per discovered
script, inside the observation lane the cage already commits, opening with that run's own TRUTH
line. THE OBSERVATION IS THAT FILE. It is refused unless the TRUTH line it opens with is the
newest line talk/truth.log records, so a stale table can never grade today's record.

THE DERIVATION, for a ticket whose written Status is `resolved`:

    the checks it names in its `## Answer` section, and nowhere else -- a check named in the
    Question is what the ticket was ASKED for, and deriving from that would grade a ticket by
    its own brief

    every named check FAIL in the table          -> `regressed`   (any one is enough)
    at least one PASS and none FAIL              -> `resolved`
    only could-not-looks                         -> `resolved-unobserved`
    no check named, or none the table carries    -> `resolved-ungraded`

A DISAGREEMENT -- written `resolved`, derived `regressed` -- is a FAULT unless the ticket file
carries a DATED paragraph (`**Correction, YYYY-MM-DD**`, `**Follow-up, YYYY-MM-DD**`, or any
bolded lead-in with a date) that NAMES THE RED CHECK. Three things that deliberately do not
dispose of it, because ticket 80 was defeated this morning by a check that read the text it
graded and took the fix as input:

  * the Answer naming the check. Every Answer names its own check by definition; if that counted,
    every ticket would dispose of its own red.
  * a dated paragraph naming a DIFFERENT check.
  * an undated paragraph naming the right one.

Everything else is COUNTED, never failed: a resolved ticket that names no check (37 of 79 on
2026-09-06 -- research tickets, org setup, grillings), and a named check the table does not
carry. Those counts are printed on every run, so what is outside the derivation is a number that
moves rather than a sentence somebody wrote once.

ONE LIMIT INHERITED FROM named_checks(), which verify/cited-truth/ records for itself and which
bites harder here. "The check a ticket names" is every check-shaped path in backticks in its
Answer, and no text analysis can tell a check a ticket OWNS from one it merely mentions. So a
ticket that discusses another ticket's check in its Answer will derive its own status partly from
that check, and a red there reads as this ticket's regression. The mitigation is the record's,
not this module's: name in an Answer the checks the ticket built, and refer to other people's by
their ticket number. Ticket 59's own Answer was rewritten once, on the day it was written, for
exactly this reason -- it had named can-record's and cited-truth's directories in passing.

    derived_status.py report --issues DIR --grades FILE --log FILE
    derived_status.py selfcheck
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
HUB = HERE.parents[1]
sys.path.insert(0, str(HUB / "verify" / "cited-truth"))
sys.path.insert(0, str(HUB / "talk"))
from cited_truth import named_checks, unquote_flat          # noqa: E402
from truth_manifest import parse_truth                      # noqa: E402

# docs/agents/issue-tracker.md's words, plus the two the eco-system tracker has used since:
# `open` (the frontier's own word, "files that are open, unblocked and unclaimed") and `closed`
# (ticket 90, taken out of scope by the owner). Nothing else, and nothing after the word.
VOCABULARY = ("open", "claimed", "prepared", "resolved", "closed")

_STATUS = re.compile(r"^Status:[ \t]*(.*)$", re.M)
# A dated bolded lead-in, in every shape this record uses: `**Correction, 2026-09-06.**`,
# `**Follow-up, 2026-08-31**`, `**2026-09-02, ticket 75 resolved.**`. Bounded on both sides and
# forbidding a newline or a second asterisk, so it matches a lead-in and never a whole paragraph.
_DATED = re.compile(r"\*\*[^*\n]{0,60}?(\d{4}-\d{2}-\d{2})[^*\n]{0,40}?\*\*")


@dataclass(frozen=True)
class Finding:
    path: str
    rule: str
    detail: str

    def __str__(self) -> str:
        return f"{self.path}: {self.detail}"


@dataclass
class Table:
    truth_line: str = ""
    grades: dict[str, str] = field(default_factory=dict)
    problems: list[str] = field(default_factory=list)

    def grade_of(self, check: str) -> list[tuple[str, str]]:
        """(path, status) for every row the check names: a script path exactly, a directory by
        prefix. A directory is how half the record names its check, and resolving it here means
        the record does not have to be rewritten to be derivable."""
        if check.endswith(".sh"):
            return [(check, self.grades[check])] if check in self.grades else []
        prefix = check if check.endswith("/") else check + "/"
        return sorted((p, s) for p, s in self.grades.items() if p.startswith(prefix))


@dataclass
class Derived:
    path: str
    written: str
    derived: str = ""
    why: str = ""
    disagrees: bool = False
    acknowledged: str = ""
    checks: list[str] = field(default_factory=list)
    unlisted: list[str] = field(default_factory=list)


@dataclass
class Report:
    ok: bool
    findings: list[Finding]
    derived: list[Derived]
    counts: dict[str, int]
    problems: list[str] = field(default_factory=list)


# ------------------------------------------------------------------ the observation

def parse_grades(text: str) -> Table:
    """`talk/captures/_grades.tsv`: comment lines, one of which is the run's own TRUTH line,
    then `path<TAB>STATUS<TAB>last line` rows."""
    table = Table()
    for raw in text.splitlines():
        if raw.startswith("#"):
            body = raw.lstrip("# ").rstrip()
            if body.startswith("TRUTH "):
                table.truth_line = body
            continue
        if not raw.strip():
            continue
        parts = raw.split("\t")
        if len(parts) < 2 or not parts[0].strip():
            table.problems.append(f"a grade row is not `path<TAB>STATUS<TAB>last`: {raw!r}")
            continue
        table.grades[parts[0].strip()] = parts[1].strip()
    if not table.truth_line:
        table.problems.append("the grade table carries no TRUTH line, so nothing ties it to a "
                              "run and it could be any tree's grades")
    if not table.grades:
        table.problems.append("the grade table carries no rows")
    return table


def table_is_the_newest_run(table: Table, newest: str) -> list[str]:
    """The table may only grade the record if it IS the newest recorded run's."""
    if not table.truth_line:
        return []                       # already a problem of its own
    mine, theirs = parse_truth(table.truth_line), parse_truth(newest)
    if str(mine["run"]) == str(theirs["run"]) and mine["hub"] == theirs["hub"]:
        return []
    return [f"the grade table was written by run {mine['run']} (hub {mine['hub']}) but the "
            f"newest line talk/truth.log records is run {theirs['run']} (hub {theirs['hub']}); "
            f"a table from an older run would grade today's record against a different tree"]


# ------------------------------------------------------------------ the written word

def status_lines(text: str) -> list[str]:
    return [m.group(1).strip() for m in _STATUS.finditer(text)]


def vocabulary_findings(files: dict[str, str]) -> list[Finding]:
    out: list[Finding] = []
    for path, text in sorted(files.items()):
        found = status_lines(text)
        if len(found) != 1:
            out.append(Finding(path, "vocabulary",
                               f"carries {len(found)} `Status:` line(s); a ticket's state is one "
                               f"field and a checker cannot derive a second one"))
            continue
        value = found[0]
        word = value.split()[0] if value.split() else ""
        if word not in VOCABULARY:
            out.append(Finding(path, "vocabulary",
                               f"`Status: {value}` starts with {word!r}, which is not one of "
                               f"{', '.join(VOCABULARY)} (docs/agents/issue-tracker.md)"))
        elif value != word:
            out.append(Finding(path, "vocabulary",
                               f"`Status: {value}` free-types past the word: "
                               f"{value[len(word):].strip()!r}. The field is derived, so it "
                               f"carries the word and nothing else; the qualification belongs "
                               f"in the ticket's body where a reader and a checker can both "
                               f"find it"))
    return out


def written_status(text: str) -> str:
    found = status_lines(text)
    return found[0].split()[0] if len(found) == 1 and found[0].split() else ""


def answer_findings(files: dict[str, str]) -> list[Finding]:
    """A file that says it is done and carries nothing behind it contradicts itself, and no run
    is needed to see it.

    The two done-words want different things, because they mean different things (delegated,
    ADR-0025, 2026-09-06). `resolved` is the tracker's own word and its convention is explicit:
    "append the answer under an `## Answer` heading, set `Status: resolved`"
    (docs/agents/issue-tracker.md), so a resolved ticket with no Answer is a claim with nothing
    behind it. `closed` is a word this tracker added for a ticket taken OUT of scope (ticket 90);
    there is nothing to answer, so what it must carry instead is a DATED paragraph saying who
    closed it and when -- ticket 68's "**2026-09-02, ticket 75 resolved.** ... Closed, out of
    scope" is the shape. Requiring an Answer of it would have made the record write a fake one.
    """
    out: list[Finding] = []
    for path, text in sorted(files.items()):
        word = written_status(text)
        if word == "resolved" and not re.search(r"^## Answer", text, re.M):
            out.append(Finding(path, "answer",
                               "says `Status: resolved` and has no `## Answer` section; the "
                               "record's own convention (docs/agents/issue-tracker.md) is that "
                               "resolving appends the answer, so the written status has nothing "
                               "behind it"))
        elif word == "closed" and not _DATED.search(unquote_flat(text)):
            out.append(Finding(path, "answer",
                               "says `Status: closed` and carries no dated paragraph; a ticket "
                               "taken out of scope has no answer to append, so the date and the "
                               "reason are what has to be on the record instead"))
    return out


def answer_section(text: str) -> str:
    m = re.search(r"^## Answer\b", text, re.M)
    if not m:
        return ""
    rest = text[m.end():]
    nxt = re.search(r"^## ", rest, re.M)
    return rest[:nxt.start()] if nxt else rest


def acknowledges(text: str, answer: str, check: str) -> str:
    """The dated paragraph that acknowledges `check` being red, or "".

    A dated paragraph is one carrying a date inside a bolded lead-in -- `**Correction,
    2026-09-06.**`, `**Follow-up, 2026-08-31**`, `**2026-09-02, review.**` -- which is how every
    dated note in this record is written.

    THE CLAIM CANNOT ACKNOWLEDGE ITSELF. The first paragraph of the Answer that names the check
    is the ticket's claim to have built it; every Answer names its own check, so counting that
    would let each ticket dispose of its own red. Only a LATER dated paragraph naming the same
    check counts. This is the same lesson as verify/cited-truth/'s review finding F1: a
    correction says what a claim failed to prove, it cannot supply the proof.
    """
    paras = re.split(r"\n\s*\n", text)
    claim = next((i for i, p in enumerate(paras)
                  if check in unquote_flat(p) and unquote_flat(p) in unquote_flat(answer)), -1)
    for i, para in enumerate(paras):
        if i == claim:
            continue
        flat = unquote_flat(para)
        if check in flat and _DATED.search(flat):
            return flat
    return ""


# ------------------------------------------------------------------ the derivation

def derive_one(path: str, text: str, table: Table) -> Derived:
    written = written_status(text)
    d = Derived(path=path, written=written)
    if written != "resolved":
        return d
    answer = answer_section(text)
    d.checks = named_checks(answer)
    rows: list[tuple[str, str]] = []
    for check in d.checks:
        hits = table.grade_of(check)
        if hits:
            rows += hits
        else:
            d.unlisted.append(check)
    if not rows:
        d.derived = "resolved-ungraded"
        d.why = ("no check this ticket names in its Answer is in the run's grade table"
                 if d.checks else "the Answer names no check in the gate")
        return d
    red = [p for p, s in rows if s == "FAIL"]
    green = [p for p, s in rows if s == "PASS"]
    if red:
        d.derived = "regressed"
        d.why = (f"{len(red)} of the {len(rows)} check(s) it names graded FAIL on the run the "
                 f"table records: {', '.join(red)}")
        for check in red:
            hit = acknowledges(text, answer, check)
            if hit:
                d.acknowledged = hit[:200]
                break
        d.disagrees = not d.acknowledged
    elif green:
        d.derived = "resolved"
        d.why = f"{len(green)} of {len(rows)} named check(s) graded PASS and none FAIL"
    else:
        d.derived = "resolved-unobserved"
        d.why = (f"every check it names could not look on that run: "
                 f"{', '.join(p for p, _ in rows)}")
    return d


def report(files: dict[str, str], table: Table, newest_truth: str) -> Report:
    problems = list(table.problems) + table_is_the_newest_run(table, newest_truth)
    findings = vocabulary_findings(files) + answer_findings(files)
    derived: list[Derived] = []
    counts = {"tickets": len(files), "resolved": 0, "derived-green": 0, "regressed": 0,
              "acknowledged": 0, "unobserved": 0, "ungraded": 0, "checks-not-in-the-table": 0}
    for path, text in sorted(files.items()):
        d = derive_one(path, text, table)
        if not d.derived:
            continue
        derived.append(d)
        counts["resolved"] += 1
        counts["checks-not-in-the-table"] += len(d.unlisted)
        if d.derived == "resolved":
            counts["derived-green"] += 1
        elif d.derived == "resolved-unobserved":
            counts["unobserved"] += 1
        elif d.derived == "resolved-ungraded":
            counts["ungraded"] += 1
        else:
            counts["regressed"] += 1
            if d.acknowledged:
                counts["acknowledged"] += 1
            else:
                findings.append(Finding(
                    path, "derived",
                    f"is written `Status: resolved` and derives `regressed`: {d.why}. No dated "
                    f"paragraph in the file names that check, so the record does not say the "
                    f"thing this ticket built is currently red. Either the check goes green "
                    f"again, or the ticket carries a dated line naming it and what owns it"))
    return Report(ok=not findings and not problems, findings=findings, derived=derived,
                  counts=counts, problems=problems)


# ------------------------------------------------------------------ selfcheck

_TRUTH = ("TRUTH 2026-09-06T09:57Z run=122 hub=c9509cc enact=development units=[u=1@main] "
          "pass=2 [observed=1 self=1 simulated=0 meta=0] fail=1 skip=1 [never=0 waits=1] "
          "excluded=0 total=4 ceiling=4")
_GRADES = (f"# header\n# {_TRUTH}\n"
           "verify/good/verify-good.sh\tPASS\tPASS: it looked\n"
           "verify/red/verify-red.sh\tFAIL\tFAIL: it did not\n"
           "verify/blind/verify-blind.sh\tSKIP\tSKIP: no cluster\n")


def _t(status: str, body: str = "") -> str:
    return f"# 42 — a ticket\n\nType: task\nStatus: {status}\n\n## Question\n\nq?\n{body}"


def selfcheck() -> int:
    table = parse_grades(_GRADES)
    assert table.problems == [] and table.truth_line == _TRUTH
    assert table.grades["verify/red/verify-red.sh"] == "FAIL"
    assert any("no TRUTH line" in p or "TRUTH line" in p
               for p in parse_grades("a\tPASS\tb\n").problems)
    assert len(table_is_the_newest_run(parse_grades(_GRADES.replace("run=122", "run=113")),
                                       _TRUTH)) == 1
    assert table_is_the_newest_run(table, _TRUTH) == []

    assert len(vocabulary_findings({"x.md": _t("done")})) == 1
    assert len(vocabulary_findings({"x.md": _t("resolved (waits on the owner)")})) == 1
    assert vocabulary_findings({"x.md": _t("resolved")}) == []
    assert len(vocabulary_findings({"x.md": "# 42\n\nno status\n"})) == 1
    assert len(answer_findings({"x.md": _t("resolved")})) == 1
    assert answer_findings({"x.md": _t("resolved", "\n## Answer\n\nbuilt.\n")}) == []

    green = derive_one("a.md", _t("resolved", "\n## Answer\n\n`verify/good/verify-good.sh`\n"),
                       table)
    assert green.derived == "resolved" and not green.disagrees
    red = derive_one("b.md", _t("resolved", "\n## Answer\n\n`verify/red/verify-red.sh`\n"), table)
    assert red.derived == "regressed" and red.disagrees
    ack = derive_one("b.md", _t("resolved", "\n## Answer\n\n`verify/red/verify-red.sh`\n\n"
                                "> **Correction, 2026-09-06.** `verify/red/verify-red.sh` is red "
                                "on the clock; ticket 74 owns it.\n"), table)
    assert ack.derived == "regressed" and not ack.disagrees and ack.acknowledged
    wrong = derive_one("b.md", _t("resolved", "\n## Answer\n\n`verify/red/verify-red.sh`\n\n"
                                  "> **Correction, 2026-09-06.** `verify/good/verify-good.sh` "
                                  "was renamed.\n"), table)
    assert wrong.disagrees, "a dated note about another check disposed of the red"
    undated = derive_one("b.md", _t("resolved", "\n## Answer\n\n`verify/red/verify-red.sh`\n\n"
                                    "> **Correction.** `verify/red/verify-red.sh` is red.\n"),
                         table)
    assert undated.disagrees, "an undated note disposed of the red"
    inline = derive_one("b.md", _t("resolved", "\n## Answer\n\n`verify/red/verify-red.sh` is red, "
                                   "**2026-09-06**.\n"), table)
    assert inline.disagrees, "the Answer's own words disposed of its own red"
    blind = derive_one("c.md", _t("resolved", "\n## Answer\n\n`verify/blind/verify-blind.sh`\n"),
                       table)
    assert blind.derived == "resolved-unobserved" and not blind.disagrees
    none = derive_one("d.md", _t("resolved", "\n## Answer\n\nnothing in the gate grades a "
                                 "reading list.\n"), table)
    assert none.derived == "resolved-ungraded" and none.checks == []
    absent = derive_one("e.md", _t("resolved", "\n## Answer\n\n`verify/absent/verify-absent.sh`\n"),
                        table)
    assert absent.derived == "resolved-ungraded" and absent.unlisted
    assert derive_one("f.md", _t("open", "\n## Answer\n\n`verify/red/verify-red.sh`\n"),
                      table).derived == ""

    rep = report({"a.md": _t("resolved", "\n## Answer\n\n`verify/good/verify-good.sh`\n"),
                  "b.md": _t("resolved", "\n## Answer\n\n`verify/red/verify-red.sh`\n"),
                  "c.md": _t("open")}, table, _TRUTH)
    assert not rep.ok and [f.path for f in rep.findings] == ["b.md"]
    assert rep.counts["resolved"] == 2 and rep.counts["derived-green"] == 1
    print("selfcheck ok")
    return 0


# ------------------------------------------------------------------ cli

def _issues(args: argparse.Namespace) -> dict[str, str]:
    return {str(p.relative_to(HUB)): p.read_text(encoding="utf-8")
            for p in sorted(Path(args.issues).glob("*.md"))}


def _record(args: argparse.Namespace) -> int:
    """The half that needs no run: the vocabulary, and a file that says it is done with nothing
    behind it. Kept separate so the gate can be RED about the record even on a day when no grade
    table has landed and the derivation itself can only be a could-not-look."""
    issues = _issues(args)
    if not issues:
        print(f"no ticket files under {args.issues}")
        return 1
    findings = vocabulary_findings(issues) + answer_findings(issues)
    words: dict[str, int] = {}
    for text in issues.values():
        words[written_status(text) or "(none)"] = words.get(written_status(text) or "(none)", 0) + 1
    print(f"  {len(issues)} tickets: " + ", ".join(f"{k}={v}" for k, v in sorted(words.items())))
    for f in findings:
        print(f"  !! {f}")
    return 0 if not findings else 1


def _run(args: argparse.Namespace) -> int:
    issues = _issues(args)
    if not issues:
        print(f"FAIL derived-status: no ticket files under {args.issues}")
        return 1
    lines = [l for l in Path(args.log).read_text(encoding="utf-8").splitlines()
             if l.startswith("TRUTH ")]
    if not lines:
        print("FAIL derived-status: talk/truth.log records no TRUTH line, so no run's grade "
              "table could be the newest one")
        return 1
    table = parse_grades(Path(args.grades).read_text(encoding="utf-8"))
    rep = report(issues, table, lines[-1])
    run = parse_truth(table.truth_line)["run"] if table.truth_line else "?"
    print(f"  derived from the grade table run {run} recorded, "
          f"{len(table.grades)} script(s) graded")
    c = rep.counts
    print(f"  {c['resolved']} of {c['tickets']} tickets are written `resolved`: "
          f"{c['derived-green']} derive resolved from a named check that passed, "
          f"{c['regressed']} derive regressed ({c['acknowledged']} of those acknowledged by a "
          f"dated line in the ticket), {c['unobserved']} rest only on checks that could not "
          f"look, and {c['ungraded']} name no check the table carries")
    print(f"  {c['checks-not-in-the-table']} check(s) named by a resolved ticket are not rows in "
          f"the table at all (a unit's script this run did not discover, or a renamed one)")
    for p in rep.problems:
        print(f"  !! {p}")
    for f in rep.findings:
        print(f"  !! {f}")
    return 0 if rep.ok else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Status is derived from a named check (ticket 59)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("report", "record"):
        r = sub.add_parser(name)
        r.add_argument("--issues", default=str(HUB / ".scratch" / "ecosystem" / "issues"))
        r.add_argument("--grades", default=str(HUB / "talk" / "captures" / "_grades.tsv"))
        r.add_argument("--log", default=str(HUB / "talk" / "truth.log"))
    sub.add_parser("selfcheck")
    a = ap.parse_args(argv)
    if a.cmd == "selfcheck":
        return selfcheck()
    return _record(a) if a.cmd == "record" else _run(a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
