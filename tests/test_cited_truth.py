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
    assert report.declared_uncitable == 2


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
