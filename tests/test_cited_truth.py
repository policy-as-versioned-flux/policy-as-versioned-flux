"""Eco-system ticket 80 item 1: a cited TRUTH line must be a real line whose tree carries the check.

The seam is verify/cited-truth/cited_truth.py. It is pure: it takes the text of the ticket files,
the text of talk/truth.log, and a `tree_lookup` callable that answers "what paths did this commit's
tree carry" -- so every rule below is exercised here without a git object database and without the
estate. The gate script verify-cited-truth.sh supplies the real three.

What these tests pin down is the defect the ticket was raised for: fifteen resolved tickets cite
"the TRUTH line of 2026-08-29" as proof their check is in the gate, and that line's tree carries
none of them. A sweep fixes fifteen files; this seam refuses the sixteenth.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    # registered before exec: the module defines dataclasses, and @dataclass reads
    # sys.modules[cls.__module__] while it builds the class
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ct = _load("cited_truth", ROOT / "verify" / "cited-truth" / "cited_truth.py")

LOG = (
    "TRUTH 2026-08-29T12:03Z run=7 hub=918022b units=[platform=58ef9c5] "
    "pass=43 fail=11 skip=0 excluded=2 total=56\n"
    "TRUTH 2026-09-05T20:04Z run=113 hub=2a1bb3a units=[platform=e27187e@main] "
    "pass=69 [observed=16 self=40 simulated=6 meta=7] fail=11 skip=21 [never=9 waits=12] "
    "excluded=8 total=109 ceiling=90\n"
)


def trees(**mapping: set[str]) -> Any:
    """A tree_lookup over a literal {commit: paths} map; an unknown commit is unresolvable."""
    return lambda commit: mapping.get(commit)


# -- reading a citation out of prose --------------------------------------------------------------

def test_a_dated_citation_is_found_with_its_date() -> None:
    found = ct.citations("The run that recorded it is the TRUTH line of 2026-08-29.")
    assert [(c.kind, c.value) for c in found] == [("date", "2026-08-29")]


def test_a_run_number_is_found_however_it_is_spelt() -> None:
    assert [c.value for c in ct.citations("Run 22 of 2026-09-03 shows skip=18.")] == ["22"]
    assert [c.value for c in ct.citations("the line says run=113")] == ["113"]


def test_a_bare_date_that_names_no_truth_line_is_not_a_citation() -> None:
    assert ct.citations("Built 2026-08-29 by the /implement run of 2026-08-28 to 29.") == []


def test_a_run_word_that_is_not_a_run_number_is_not_a_citation() -> None:
    assert ct.citations("a scheduled run of the sampler; the run opens a PR") == []


# -- resolving it against the recorded log --------------------------------------------------------

def test_a_citation_resolves_to_the_recorded_line() -> None:
    log = ct.recorded(LOG)
    assert [t["run"] for t in ct.resolve(ct.citations("the TRUTH line of 2026-08-29")[0], log)] == ["7"]
    assert [t["hub"] for t in ct.resolve(ct.citations("run 113")[0], log)] == ["2a1bb3a"]


def test_a_citation_of_a_line_nobody_recorded_resolves_to_nothing() -> None:
    log = ct.recorded(LOG)
    assert ct.resolve(ct.citations("the TRUTH line of 2026-08-30")[0], log) == []
    assert ct.resolve(ct.citations("run 999")[0], log) == []


# -- the check paths a ticket names ---------------------------------------------------------------

def test_the_named_checks_are_the_backticked_verify_paths() -> None:
    text = "`verify/feed-contract/` grades every publisher, and `talk/verify-demo.sh` rebuilds it."
    assert ct.named_checks(text) == ["talk/verify-demo.sh", "verify/feed-contract/"]


def test_verify_all_is_never_the_named_check() -> None:
    # every gate-proof sentence names the runner; the runner is not the check it is proving
    assert ct.named_checks("its check is in `talk/verify-all.sh`") == []


# -- the rule --------------------------------------------------------------------------------------

CLAIM = (
    "## Answer\n\n"
    "Built it. `verify/feed-contract/` grades every publisher.\n\n"
    "Definition of done: its check is in `talk/verify-all.sh`. "
    "The run that recorded it is the TRUTH line of 2026-08-29.\n"
)


def test_a_gate_proof_whose_cited_tree_carries_the_check_passes() -> None:
    findings = ct.grade({"21.md": CLAIM}, ct.recorded(LOG),
                        trees(**{"918022b": {"verify/feed-contract/verify-feed-contract.sh"}}))
    assert findings == []


def test_a_gate_proof_whose_cited_tree_lacks_the_check_is_named() -> None:
    findings = ct.grade({"21.md": CLAIM}, ct.recorded(LOG),
                        trees(**{"918022b": {"verify/party/verify-party.sh"}}))
    assert len(findings) == 1
    assert findings[0].kind == "tree-lacks-the-check"
    assert "918022b" in findings[0].detail and "verify/feed-contract/" in findings[0].detail


def test_a_dated_correction_in_the_same_file_disposes_of_it() -> None:
    corrected = CLAIM + (
        "\n> **Correction, 2026-09-06 (ticket 80).** The TRUTH line of 2026-08-29 is run 7, "
        "graded before the build, and its tree carries no such check.\n"
    )
    assert ct.grade({"21.md": corrected}, ct.recorded(LOG),
                    trees(**{"918022b": {"verify/party/verify-party.sh"}})) == []


def test_a_correction_carrying_no_date_does_not_dispose_of_it() -> None:
    corrected = CLAIM + "\n> **Correction (ticket 80).** That over-claimed.\n"
    findings = ct.grade({"21.md": corrected}, ct.recorded(LOG),
                        trees(**{"918022b": {"verify/party/verify-party.sh"}}))
    assert [f.kind for f in findings] == ["tree-lacks-the-check"]


def test_a_correction_that_names_a_different_run_does_not_dispose_of_it() -> None:
    corrected = CLAIM + "\n> **Correction, 2026-09-06.** Run 113 was fine.\n"
    findings = ct.grade({"21.md": corrected}, ct.recorded(LOG),
                        trees(**{"918022b": {"verify/party/verify-party.sh"}}))
    assert [f.kind for f in findings] == ["tree-lacks-the-check"]


def test_a_gate_proof_naming_no_check_at_all_needs_the_correction_too() -> None:
    bare = ("Definition of done: its check is in `talk/verify-all.sh`. "
            "The run that recorded it is the TRUTH line of 2026-08-29.\n")
    findings = ct.grade({"52.md": bare}, ct.recorded(LOG), trees(**{"918022b": set()}))
    assert [f.kind for f in findings] == ["tree-lacks-the-check"]


def test_a_citation_of_a_line_nobody_recorded_is_named_as_such() -> None:
    text = ("Definition of done: its check is in `talk/verify-all.sh`. "
            "The run that recorded it is the TRUTH line of 2026-08-30.\n")
    findings = ct.grade({"x.md": text}, ct.recorded(LOG), trees())
    assert [f.kind for f in findings] == ["no-such-line"]


def test_a_commit_this_checkout_cannot_resolve_is_not_proof_and_is_named() -> None:
    # the honest half of "make a disclosed limit checkable": a tree we cannot read never passes
    findings = ct.grade({"21.md": CLAIM}, ct.recorded(LOG), trees())
    assert [f.kind for f in findings] == ["unreadable-tree"]


# -- the figures ------------------------------------------------------------------------------------

def test_a_figure_quoted_beside_its_run_must_match_that_run() -> None:
    good = "Run 7 shows pass=43 fail=11 total=56.\n"
    bad = "Run 7 shows pass=57 fail=7 skip=18.\n"
    assert ct.grade({"a.md": good}, ct.recorded(LOG), trees()) == []
    findings = ct.grade({"b.md": bad}, ct.recorded(LOG), trees())
    assert [f.kind for f in findings] == ["figure-disagrees"]
    assert "pass=57" in findings[0].detail


def test_a_figure_with_no_run_beside_it_is_out_of_scope_and_counted() -> None:
    report = ct.report({"c.md": "Twelve scripts can never exit 0; pass=57 of total=84 that day.\n"},
                       ct.recorded(LOG), trees())
    assert report.findings == []
    assert report.unattributed == 1


def test_a_fenced_quote_inherits_the_marker_from_the_sentence_above_it() -> None:
    # a verbatim branch TRUTH line cannot carry a marker inside the fence without corrupting
    # the quote, so the sentence that introduces the fence is where the estate disowns it
    text = ("Run 92 produced this line and it never landed, so it is not citable:\n\n"
            "```\n"
            "TRUTH 2026-09-05T02:03Z run=92 hub=c28541e pass=65 fail=13 total=105\n"
            "```\n")
    report = ct.report({"e.md": text}, ct.recorded(LOG), trees())
    assert report.findings == []
    assert report.declared_uncitable == 1   # the fenced line; the prose above quotes no figure


def test_a_paragraph_next_to_a_marked_one_is_not_laundered_by_it() -> None:
    text = ("A planted line, fixture only.\n\n"
            "Run 7 shows pass=99.\n")
    findings = ct.report({"f.md": text}, ct.recorded(LOG), trees()).findings
    assert [f.kind for f in findings] == ["figure-disagrees"]


def test_a_line_marked_fixture_or_not_citable_is_declared_not_graded() -> None:
    text = ("A planted line: run=fixture pass=5 fail=3 (fixture=1).\n"
            "Run 7 shows pass=99, quoted from the Actions log and not citable.\n")
    report = ct.report({"d.md": text}, ct.recorded(LOG), trees())
    assert report.findings == []
    # only the second line spends the hatch: `run=fixture` is no run number, so the first line
    # carries no citation and nothing was going to be graded on it
    assert report.declared_uncitable == 1
    assert report.unattributed == 1
    assert report.exempted == [("d.md", 2, "not citable")]


# -- the other nine items' facts, as a table of greps ----------------------------------------------

def test_the_record_fact_table_names_every_file_it_grades() -> None:
    # a fact whose file is not in the map is a grader bug, not a record defect
    for fact in ct.RECORD_FACTS:
        assert fact.file in ct.RECORD_FILES, fact.file


def test_a_missing_fact_is_named_with_its_item_and_its_file() -> None:
    files = {name: "" for name in ct.RECORD_FILES}
    findings = ct.record_facts(files)
    assert len(findings) == len([f for f in ct.RECORD_FACTS if f.want])
    assert all(f.kind == "record-fact" for f in findings)
    assert any("item 3" in f.detail for f in findings)


def test_a_fact_the_record_carries_is_not_named() -> None:
    files = {name: "" for name in ct.RECORD_FILES}
    fact = next(f for f in ct.RECORD_FACTS if f.want and f.item == 5)
    files[fact.file] = fact.example
    assert not [f for f in ct.record_facts(files)
                if f.path == fact.file and fact.pattern in f.detail]


def test_a_sentence_the_correction_had_to_remove_is_named_when_it_comes_back() -> None:
    # the `want=False` half: a fact is not only "the new words are there", it is also "the old
    # words are gone", or a correction can be appended below a claim it never removed
    banned = next(f for f in ct.RECORD_FACTS if not f.want)
    clean = {name: "" for name in ct.RECORD_FILES}
    dirty = dict(clean, **{banned.file: banned.example})
    assert [f for f in ct.record_facts(dirty) if "still says" in f.detail]
    assert not [f for f in ct.record_facts(clean) if "still says" in f.detail]


# -- F1: a named check must RESOLVE to a script, and a correction may not supply it ----------------

def test_a_bare_verify_directory_is_not_a_named_check() -> None:
    # `verify/` is a prefix of every hub check path, so under a startswith test it satisfied
    # every tree that has ever existed. It names no check.
    assert ct.named_checks("its check lives under `verify/`") == []
    assert ct.named_checks("see `verify`") == []


def test_a_directory_token_counts_only_where_the_cited_tree_carries_a_script_under_it() -> None:
    assert ct.tree_carries({"verify/party/verify-party.sh"}, ["verify/party/"]) == ["verify/party/"]
    assert ct.tree_carries({"verify/party/README.md", "verify/party/party.py"},
                           ["verify/party/"]) == []


def test_a_script_token_matches_by_path_suffix_not_by_prefix() -> None:
    # tickets name `verify-demo.sh`; the tree carries `talk/verify-demo.sh`
    assert ct.tree_carries({"talk/verify-demo.sh"}, ["verify-demo.sh"]) == ["verify-demo.sh"]
    assert ct.tree_carries({"talk/verify-demonstrate.sh"}, ["verify-demo.sh"]) == []


def test_a_check_named_only_inside_a_correction_cannot_prove_the_citation() -> None:
    # the defect the reviewer measured: ticket 80's own correction names run 7's three
    # directories, which run 7's tree of course carries, so the citation passed on the
    # correction's own words and the dated correction never did any work
    corrected = CLAIM + (
        "\n> **Correction, 2026-09-06 (ticket 80).** The TRUTH line of 2026-08-29 is run 7, "
        "whose tree carries `verify/party/`, `verify/proportionality/` and "
        "`verify/provenance/` and none of the checks this ticket names.\n"
    )
    tree = trees(**{"918022b": {"verify/party/verify-party.sh",
                                "verify/proportionality/verify-proportionality.sh",
                                "verify/provenance/verify-provenance.sh"}})
    # it is disposed of by the dated correction, and by nothing else
    assert ct.grade({"21.md": corrected}, ct.recorded(LOG), tree) == []
    undated = corrected.replace("**Correction, 2026-09-06 (ticket 80).**",
                                "**Correction (ticket 80).**")
    assert [f.kind for f in ct.grade({"21.md": undated}, ct.recorded(LOG), tree)] == \
        ["tree-lacks-the-check"]


# -- F2: the escape hatch is a phrase, and a negated one is not one --------------------------------

def test_a_negated_marker_word_does_not_exempt_a_line() -> None:
    for line in ("Run 7 shows pass=99, and no fixture was used.\n",
                 "Run 7 shows pass=99; this is not a rehearsal.\n",
                 "Run 7 shows pass=99, as the Actions log confirms.\n"):
        rep = ct.report({"g.md": line}, ct.recorded(LOG), trees())
        assert [f.kind for f in rep.findings] == ["figure-disagrees"], line
        assert rep.declared_uncitable == 0, line


def test_the_exempted_lines_are_printed_and_not_only_counted() -> None:
    rep = ct.report({"h.md": "Run 7 shows pass=99 -- not citable, a branch run.\n"},
                    ct.recorded(LOG), trees())
    assert rep.findings == []
    assert rep.exempted == [("h.md", 1, "not citable")]


# -- F3: the gate-proof trigger reads a paragraph, not a physical line ------------------------------

def test_a_gate_proof_wrapped_across_lines_is_still_matched() -> None:
    wrapped = ("Definition of done: its check is in `talk/verify-all.sh`. The run that\n"
               "recorded it is the TRUTH line of 2026-08-29.\n")
    assert [f.kind for f in ct.grade({"a.md": wrapped}, ct.recorded(LOG),
                                     trees(**{"918022b": set()}))] == ["tree-lacks-the-check"]


def test_in_the_gate_beside_a_citation_is_a_gate_proof_too() -> None:
    for phrase in ("wired into the gate", "its check is in the gate"):
        text = f"{phrase}, proven by run 7.\n"
        assert [f.kind for f in ct.grade({"a.md": text}, ct.recorded(LOG),
                                         trees(**{"918022b": set()}))] == ["tree-lacks-the-check"]


def test_a_run_written_with_a_hash_is_a_citation() -> None:
    assert [c.value for c in ct.citations("as Run #7 recorded")] == ["7"]


def test_a_citation_that_is_no_gate_proof_is_counted_as_outside_the_rule() -> None:
    rep = ct.report({"a.md": "Run 7 was the last one before the build.\n"},
                    ct.recorded(LOG), trees())
    assert rep.findings == []
    assert rep.outside_the_rule == 1


# -- F4: a correction's date must follow the word, and it must name the citation --------------------

def test_an_undated_correction_that_merely_mentions_the_cited_date_does_not_dispose() -> None:
    text = CLAIM + ("\n> **Correction (ticket 80).** The TRUTH line of 2026-08-29 was a "
                    "rehearsal.\n")
    assert [f.kind for f in ct.grade({"a.md": text}, ct.recorded(LOG),
                                     trees(**{"918022b": set()}))] == ["tree-lacks-the-check"]


def test_a_dated_correction_naming_the_date_only_in_passing_does_not_dispose() -> None:
    # a bare date is not a citation; the correction has to name the LINE
    text = CLAIM + "\n> **Correction, 2026-09-07.** Something else happened on 2026-08-29.\n"
    assert [f.kind for f in ct.grade({"a.md": text}, ct.recorded(LOG),
                                     trees(**{"918022b": set()}))] == ["tree-lacks-the-check"]


# -- F5: a record fact is matched with whitespace normalised ---------------------------------------

def test_a_record_fact_matches_across_a_line_wrap() -> None:
    fact = next(f for f in ct.RECORD_FACTS if f.want and " " in f.pattern)
    wrapped = fact.example.replace(" ", "\n", 1)
    files = {name: "" for name in ct.RECORD_FILES}
    files[fact.file] = wrapped
    assert not [f for f in ct.record_facts(files)
                if f.path == fact.file and fact.pattern in f.detail]


def test_a_banned_sentence_restored_on_one_line_is_still_named() -> None:
    banned = next(f for f in ct.RECORD_FACTS if not f.want and "\n" in f.example)
    files = {name: "" for name in ct.RECORD_FILES}
    files[banned.file] = " ".join(banned.example.split())
    assert [f for f in ct.record_facts(files) if "still says" in f.detail]


def test_a_check_named_in_another_section_does_not_prove_the_citation() -> None:
    # narrowing beyond "somewhere in the file": the proof must be named where the claim is made
    text = ("## Notes\n\n`verify/party/` is somebody else's check.\n\n"
            "## Answer\n\nDefinition of done: its check is in `talk/verify-all.sh`. "
            "The run that recorded it is the TRUTH line of 2026-08-29.\n")
    tree = trees(**{"918022b": {"verify/party/verify-party.sh"}})
    assert [f.kind for f in ct.grade({"a.md": text}, ct.recorded(LOG), tree)] == \
        ["tree-lacks-the-check"]


def test_a_check_named_in_the_same_section_does_prove_it() -> None:
    text = ("## Answer\n\n`verify/party/` grades it.\n\n"
            "Definition of done: its check is in `talk/verify-all.sh`. "
            "The run that recorded it is the TRUTH line of 2026-08-29.\n")
    tree = trees(**{"918022b": {"verify/party/verify-party.sh"}})
    assert ct.grade({"a.md": text}, ct.recorded(LOG), tree) == []


def test_the_hatch_is_only_spent_where_it_actually_suppresses_a_grade() -> None:
    # measured on ticket 75 line 45: "not citable" appeared in a neighbouring clause about
    # something else, on a line whose figure had no run citation and so was never graded. An
    # exemption that suppresses nothing must not be reported as one, or the printed list of
    # exemptions stops meaning what it says.
    text = "No line has ever had fail=0. Option (c) is a private alarm, not citable evidence.\n"
    rep = ct.report({"i.md": text}, ct.recorded(LOG), trees())
    assert rep.exempted == []
    assert rep.declared_uncitable == 0
    assert rep.unattributed == 1


# -- R2-1: the hatch reads prose, not code spans, link targets or a negated clause ------------------

def test_a_marker_inside_a_code_span_or_a_link_does_not_exempt_the_prose() -> None:
    for line in ("Run 7 shows pass=99; grep for `not citable` in the log.\n",
                 "Run 7 shows pass=99, see [the note](docs/why-it-is-not-citable.md).\n"):
        rep = ct.report({"j.md": line}, ct.recorded(LOG), trees())
        assert [f.kind for f in rep.findings] == ["figure-disagrees"], line
        assert rep.exempted == [], line


def test_a_marker_negated_by_not_or_does_not_is_not_a_marker() -> None:
    for line in ("Run 7 shows pass=99, and it is not a not citable line.\n",
                 "Run 7 shows pass=99; this does not make it not citable.\n"):
        rep = ct.report({"k.md": line}, ct.recorded(LOG), trees())
        assert [f.kind for f in rep.findings] == ["figure-disagrees"], line


def test_a_plain_prose_marker_still_exempts() -> None:
    rep = ct.report({"l.md": "Run 7 shows pass=99, a branch run and not citable.\n"},
                    ct.recorded(LOG), trees())
    assert rep.findings == []
    assert rep.exempted == [("l.md", 1, "not citable")]


def test_a_negation_further_off_than_a_word_does_not_reach_the_phrase() -> None:
    # the window is a modifier's distance, not a sentence's: this line disowns its own figure
    rep = ct.report({"m.md": "Run 7: no run recorded it, so it is not citable. pass=99\n"},
                    ct.recorded(LOG), trees())
    assert rep.findings == []
    assert rep.exempted == [("m.md", 1, "not citable")]
