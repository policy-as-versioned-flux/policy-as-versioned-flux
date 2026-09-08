"""verify/derived-status/derived_status.py: Status is derived from a named check (ticket 59).

NORTH-STAR §5: "Ticket `Status:` is derived from a named check, in the way `twin grade` already
derives depth from `twin/capabilities/*.yaml`." twin/grades.py's rule is that `full` cannot be
typed -- it is computed, and a stated grade that disagrees with the computed one is refused.
These tests pin the same seam for a ticket: the vocabulary, the file's own contradiction, and the
derivation from the grade table one run of talk/verify-all.sh recorded.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_SPEC = importlib.util.spec_from_file_location(
    "derived_status", _ROOT / "verify" / "derived-status" / "derived_status.py")
assert _SPEC is not None and _SPEC.loader is not None
ds = importlib.util.module_from_spec(_SPEC)
sys.modules["derived_status"] = ds
_SPEC.loader.exec_module(ds)

TRUTH = ("TRUTH 2026-09-06T09:57Z run=122 hub=c9509cc enact=development units=[u=1@main] "
         "pass=2 [observed=1 self=1 simulated=0 meta=0] fail=1 skip=1 [never=0 waits=1] "
         "excluded=0 total=4 ceiling=4")

GRADES = (f"# a header\n# {TRUTH}\n"
          "verify/good/verify-good.sh\tPASS\tPASS: it looked\n"
          "verify/red/verify-red.sh\tFAIL\tFAIL: it did not\n"
          "verify/blind/verify-blind.sh\tSKIP\tSKIP: no cluster\n"
          "verify/gone/verify-gone.sh\tEXCLUDED\t\n")


def ticket(status: str, body: str = "") -> str:
    return f"# 42 — a ticket\n\nType: task\nStatus: {status}\nBlocked by: none\n\n## Question\n\nq?\n{body}"


# ------------------------------------------------------------------ the grade table

def test_the_grade_table_reads_back_its_run_and_every_row() -> None:
    table = ds.parse_grades(GRADES)
    assert table.problems == []
    assert table.truth_line == TRUTH
    assert table.grades["verify/red/verify-red.sh"] == "FAIL"
    assert table.grades["verify/gone/verify-gone.sh"] == "EXCLUDED"


def test_a_grade_table_with_no_truth_line_is_refused() -> None:
    table = ds.parse_grades("verify/good/verify-good.sh\tPASS\tok\n")
    assert any("TRUTH line" in p for p in table.problems)


def test_a_grade_table_whose_line_is_not_the_newest_recorded_one_is_refused() -> None:
    """The table is only an observation of the run whose number the log records newest. An older
    table would grade today's record against a run that measured a different tree."""
    older = TRUTH.replace("run=122", "run=113")
    problems = ds.table_is_the_newest_run(ds.parse_grades(GRADES.replace(TRUTH, older)), TRUTH)
    assert len(problems) == 1 and "113" in problems[0] and "122" in problems[0]
    assert ds.table_is_the_newest_run(ds.parse_grades(GRADES), TRUTH) == []


# ------------------------------------------------------------------ the vocabulary

def test_a_status_word_outside_the_vocabulary_is_a_finding() -> None:
    found = ds.vocabulary_findings({"59.md": ticket("done")})
    assert len(found) == 1 and "done" in found[0].detail


def test_a_status_word_with_free_text_after_it_is_a_finding_naming_the_free_text() -> None:
    text = ticket("resolved (the citable run waits on the owner)")
    found = ds.vocabulary_findings({"59.md": text})
    assert len(found) == 1
    assert "the citable run waits on the owner" in found[0].detail


def test_each_vocabulary_word_passes() -> None:
    for word in ds.VOCABULARY:
        assert ds.vocabulary_findings({"x.md": ticket(word)}) == []


def test_a_file_with_no_status_line_and_a_file_with_two_are_both_findings() -> None:
    assert len(ds.vocabulary_findings({"x.md": "# 42\n\nno status here\n"})) == 1
    assert len(ds.vocabulary_findings({"x.md": ticket("open") + "\nStatus: resolved\n"})) == 1


# ------------------------------------------------------------------ the file's own contradiction

def test_resolved_with_no_answer_section_is_a_finding() -> None:
    found = ds.answer_findings({"x.md": ticket("resolved")})
    assert len(found) == 1 and "## Answer" in found[0].detail


def test_resolved_with_an_answer_section_is_not() -> None:
    assert ds.answer_findings({"x.md": ticket("resolved", "\n## Answer\n\nbuilt it.\n")}) == []


def test_open_needs_no_answer() -> None:
    assert ds.answer_findings({"x.md": ticket("open")}) == []


def test_closed_wants_a_dated_paragraph_rather_than_an_answer() -> None:
    """`closed` means taken out of scope, so there is nothing to answer; what has to be on the
    record is who closed it and when. Requiring an Answer would make the record write a fake."""
    bare = ds.answer_findings({"x.md": ticket("closed")})
    assert len(bare) == 1 and "dated paragraph" in bare[0].detail
    dated = ticket("closed", "\n## Comments\n\n**2026-09-02, ticket 75 resolved.** Out of scope.\n")
    assert ds.answer_findings({"x.md": dated}) == []


# ------------------------------------------------------------------ the derivation

def derive(body: str, status: str = "resolved"):
    table = ds.parse_grades(GRADES)
    return ds.derive_one("42.md", ticket(status, body), table)


def test_a_resolved_ticket_whose_named_check_passed_derives_resolved() -> None:
    d = derive("\n## Answer\n\nBuilt it; `verify/good/verify-good.sh` grades it.\n")
    assert d.derived == "resolved" and d.disagrees is False


def test_a_resolved_ticket_whose_named_check_failed_derives_regressed() -> None:
    d = derive("\n## Answer\n\nBuilt it; `verify/red/verify-red.sh` grades it.\n")
    assert d.derived == "regressed" and d.disagrees is True
    assert "verify/red/verify-red.sh" in d.why


def test_a_dated_paragraph_after_the_answer_disposes_of_the_disagreement() -> None:
    d = derive("\n## Answer\n\nBuilt it; `verify/red/verify-red.sh` grades it.\n\n"
               "## Follow-up\n\n"
               "> **Correction, 2026-09-06.** `verify/red/verify-red.sh` is red on the clock "
               "because the insurer has not cut its tag; ticket 74 owns it.\n")
    assert d.derived == "regressed" and d.disagrees is False and d.acknowledged


def test_a_dated_paragraph_naming_a_different_check_does_not_dispose() -> None:
    """The adversary case: a correction that says something dated but not about the red check."""
    d = derive("\n## Answer\n\nBuilt it; `verify/red/verify-red.sh` grades it.\n\n"
               "## Follow-up\n\n"
               "> **Correction, 2026-09-06.** `verify/good/verify-good.sh` was renamed.\n")
    assert d.disagrees is True


def test_an_undated_paragraph_naming_the_red_check_does_not_dispose() -> None:
    d = derive("\n## Answer\n\nBuilt it; `verify/red/verify-red.sh` grades it.\n\n"
               "## Follow-up\n\n"
               "> **Correction.** `verify/red/verify-red.sh` is red and we know.\n")
    assert d.disagrees is True


def test_the_answer_itself_naming_the_red_check_does_not_dispose_of_it() -> None:
    """A ticket's Answer names its check by definition -- if that counted as an acknowledgement
    every ticket would dispose of its own red, which is the shape ticket 80 was defeated by."""
    d = derive("\n## Answer\n\n`verify/red/verify-red.sh` grades it and is red, 2026-09-06.\n")
    assert d.disagrees is True


def test_a_check_the_table_does_not_carry_is_counted_not_failed() -> None:
    d = derive("\n## Answer\n\nBuilt it; `verify/absent/verify-absent.sh` grades it.\n")
    assert d.derived == "resolved-ungraded" and d.disagrees is False
    assert d.unlisted == ["verify/absent/verify-absent.sh"]


def test_a_named_check_that_could_not_look_derives_unobserved_and_does_not_fail() -> None:
    d = derive("\n## Answer\n\nBuilt it; `verify/blind/verify-blind.sh` grades it.\n")
    assert d.derived == "resolved-unobserved" and d.disagrees is False


def test_a_resolved_ticket_naming_no_check_is_counted_not_failed() -> None:
    d = derive("\n## Answer\n\nA research ticket. Nothing in the gate grades a reading list.\n")
    assert d.derived == "resolved-ungraded" and d.disagrees is False and d.checks == []


def test_a_directory_named_instead_of_a_script_resolves_through_the_table() -> None:
    d = derive("\n## Answer\n\nBuilt it; `verify/red/` holds the check.\n")
    assert d.derived == "regressed" and d.disagrees is True


def test_only_the_answer_section_is_read_for_the_checks() -> None:
    """A check named in the Question or the Notes is what the ticket asked for, not what it
    built; deriving from it would grade a ticket by its own brief."""
    text = ("# 42\n\nStatus: resolved\n\n## Question\n\nBuild `verify/red/verify-red.sh`.\n\n"
            "## Answer\n\nBuilt `verify/good/verify-good.sh` instead.\n")
    d = ds.derive_one("42.md", text, ds.parse_grades(GRADES))
    assert d.checks == ["verify/good/verify-good.sh"] and d.disagrees is False


def test_an_unresolved_ticket_is_not_derived_at_all() -> None:
    d = derive("\n## Answer\n\n`verify/red/verify-red.sh`.\n", status="open")
    assert d.derived == "" and d.disagrees is False


# ------------------------------------------------------------------ the report

def test_the_report_counts_what_it_could_not_derive_and_fails_only_on_a_disagreement() -> None:
    files = {
        "a.md": ticket("resolved", "\n## Answer\n\n`verify/good/verify-good.sh`\n"),
        "b.md": ticket("resolved", "\n## Answer\n\n`verify/red/verify-red.sh`\n"),
        "c.md": ticket("resolved", "\n## Answer\n\nno check here\n"),
        "d.md": ticket("open"),
    }
    rep = ds.report(files, ds.parse_grades(GRADES), TRUTH)
    assert rep.ok is False
    assert [f.path for f in rep.findings] == ["b.md"]
    assert rep.counts["resolved"] == 3
    assert rep.counts["ungraded"] == 1
    assert rep.counts["derived-green"] == 1


def test_a_clean_record_passes() -> None:
    files = {"a.md": ticket("resolved", "\n## Answer\n\n`verify/good/verify-good.sh`\n"),
             "b.md": ticket("open")}
    rep = ds.report(files, ds.parse_grades(GRADES), TRUTH)
    assert rep.ok is True and rep.findings == []


# ------------------------------------------------------------------ review 2026-09-06, F2

def owned(_check: str) -> set[str]:
    """Ownership stub: every check is owned by ticket 42, the number these fixtures use."""
    return {"42"}


def derive2(body: str, status: str = "resolved", owners=owned):
    return ds.derive_one("42-a.md", ticket(status, body), ds.parse_grades(GRADES), owners=owners)


RED = "\n## Answer\n\nBuilt it; `verify/red/verify-red.sh` grades it.\n"


def test_a_dated_paragraph_inside_the_answer_does_not_acknowledge() -> None:
    """F2. Only the FIRST paragraph naming the check was treated as the claim, so a second dated
    paragraph inside the same Answer disposed of the red the Answer itself had just claimed."""
    d = derive2(RED + "\n**Round 2, 2026-09-05.** `verify/red/verify-red.sh` grew a leg.\n")
    assert d.disagrees is True


def test_a_dated_paragraph_that_predates_the_answer_does_not_acknowledge() -> None:
    """F2. A Comments section sits ABOVE the Answer in this record, so a note written before the
    ticket was resolved was disposing of a red discovered long after it."""
    text = ("# 42\n\nStatus: resolved\n\n## Comments\n\n**2026-09-02, review.** "
            "`verify/red/verify-red.sh` was flaky then too.\n\n"
            "## Answer\n\nBuilt it; `verify/red/verify-red.sh` grades it.\n")
    d = ds.derive_one("42-a.md", text, ds.parse_grades(GRADES), owners=owned)
    assert d.disagrees is True


def test_an_acknowledgement_must_carry_the_check_in_backticks() -> None:
    """F2. A bare mention, a URL or a path inside prose is not the ticket naming the check."""
    d = derive2(RED + "\n## Follow-up\n\n**Correction, 2026-09-06.** see "
                      "https://example.invalid/verify/red/verify-red.sh for why\n")
    assert d.disagrees is True
    good = derive2(RED + "\n## Follow-up\n\n**Correction, 2026-09-06.** "
                         "`verify/red/verify-red.sh` is red; ticket 74 owns it.\n")
    assert good.disagrees is False


def test_an_acknowledgement_by_directory_disposes_of_the_scripts_under_it() -> None:
    """F2. grade_of() resolves a directory by prefix, so an acknowledgement must too, or a
    ticket that names its check as a directory could never acknowledge its own red."""
    d = derive2("\n## Answer\n\nBuilt it; `verify/red/` holds the check.\n\n"
                "## Follow-up\n\n**Correction, 2026-09-06.** `verify/red/` is red on the clock; "
                "ticket 74 owns it.\n")
    assert d.derived == "regressed" and d.disagrees is False


# ------------------------------------------------------------------ review 2026-09-06, ownership

def test_a_red_check_the_ticket_does_not_own_is_counted_not_failed() -> None:
    """The narrowing the review asked for. Naming a check in an Answer is not owning it: nine of
    the twelve tickets the first derivation named were discussing somebody else's check."""
    d = derive2(RED, owners=lambda check: {"89"})
    assert d.derived == "resolved-ungraded"
    assert d.mentioned_red == ["verify/red/verify-red.sh"]
    assert d.disagrees is False


def test_ownership_is_read_from_the_number_in_the_filename() -> None:
    d = ds.derive_one(".scratch/ecosystem/issues/99-a-thing.md", ticket("resolved", RED),
                      ds.parse_grades(GRADES), owners=lambda check: {"99", "101"})
    assert d.derived == "regressed" and d.disagrees is True


def test_a_check_no_commit_ever_named_a_ticket_for_is_counted_as_unownable() -> None:
    d = derive2(RED, owners=lambda check: set())
    assert d.derived == "resolved-ungraded" and d.unownable == ["verify/red/verify-red.sh"]


# ------------------------------------------------------------------ review 2026-09-06, F4

def test_a_local_grade_table_is_a_could_not_look_not_a_failure() -> None:
    """F4. A developer's own `bash talk/verify-all.sh` writes run=local, which can never be the
    newest recorded run; failing on it would make a local gate run red for looking."""
    local = GRADES.replace("run=122", "run=local").replace("hub=c9509cc", "hub=0000000")
    table = ds.parse_grades(local)
    assert ds.table_is_local(table) is True
    assert ds.table_is_the_newest_run(table, TRUTH) == []


def test_a_fixture_grade_table_is_also_a_could_not_look() -> None:
    table = ds.parse_grades(GRADES.replace("ceiling=4", "ceiling=4 fixture=1"))
    assert ds.table_is_local(table) is True


def test_a_real_table_from_an_older_run_is_still_a_failure() -> None:
    table = ds.parse_grades(GRADES.replace("run=122", "run=113"))
    assert ds.table_is_local(table) is False
    assert len(ds.table_is_the_newest_run(table, TRUTH)) == 1


# ------------------------------------------------------------------ re-review 2026-09-06, R2-1

def test_a_plural_subject_names_every_ticket_in_its_list() -> None:
    """R2-1, blocking. The estate builds two tickets' checks in one commit and says so:
    `Tickets 62 and 77: ...` added verify-branch-refs.sh and `Tickets 56 and 85: ...` added
    verify-schedules.sh. A scan reading only `ticket NN` read NEITHER, so both scripts came back
    unownable or under-owned and four tickets were told, on every run, that a red check they had
    built was "not their own" -- a false ownership statement, which is the exact defect the
    ownership rule exists to prevent."""
    assert ds.ticket_numbers("Tickets 62 and 77: no branch refs, and pins are checked for "
                             "content") == {"62", "77"}
    assert ds.ticket_numbers("Tickets 56 and 85: the clocks are read, graded and named") == \
        {"56", "85"}


def test_every_separator_the_hub_log_uses_is_read() -> None:
    assert ds.ticket_numbers("Ticket 89: deny is not a rung") == {"89"}
    assert ds.ticket_numbers("Tickets 21, 25 and 26: three checks") == {"21", "25", "26"}
    assert ds.ticket_numbers("ecosystem: ticket 21 lands + ticket 52 follows") == {"21", "52"}
    assert ds.ticket_numbers("tickets #62 & #77") == {"62", "77"}


def test_a_number_before_the_word_is_not_a_ticket() -> None:
    """`27 tickets implemented` would otherwise hand ticket 27 a check it never wrote."""
    assert ds.ticket_numbers("Estate build: 27 tickets implemented this week") == set()


def test_a_hyphenated_branch_name_in_a_merge_subject_names_no_ticket() -> None:
    assert ds.ticket_numbers(
        "Merge pull request #24 from policy-as-versioned-flux/ticket-62-and-77-pins") == set()


def test_a_range_is_not_expanded_and_is_read_conservatively() -> None:
    r"""A decision, not an oversight (re-review R2, 2026-09-06). Ticket 102's function refuses a
    range outright (`(?!-\d)`) and does not treat `to` as a separator. Measured over the whole
    hub log: thirteen subjects use a range or a `to` form and NONE of them touches any of the 40
    hub verify scripts -- they are review, charting and worktree-sync commits. So no range
    expansion is added here; under-attributing cannot write a false ownership statement, and
    over-attributing can."""
    assert ds.ticket_numbers("Ambition review: tickets 54-67 chart the remediation") == set()
    assert ds.ticket_numbers("Ticket 75 resolved: tickets 88 to 95 graduated") == {"75", "88"}


def test_a_bare_number_after_a_separator_is_collected_and_that_is_known() -> None:
    """The other behaviour this check inherits: mildly over-inclusive, accepted rather than
    forked around, and loud when it bites."""
    assert ds.ticket_numbers("Ticket 80 and 3 fixes") == {"3", "80"}


def test_the_shared_reading_is_the_only_reading() -> None:
    """R2-2. There is no second copy of the regex in this module; `shared_contract()` declares
    executably which of ticket 102's behaviours this check is built on, and a change over there
    fails this check by name instead of moving its verdicts in silence."""
    assert ds.shared_contract() == []
    assert ds.ticket_numbers.__module__ == "cited_truth"
