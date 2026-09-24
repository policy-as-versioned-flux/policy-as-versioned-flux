"""verify/unreviewed-major — the standing report's own rules, at the grader's own seam.

Eco-system ticket 99. "An institution should not quietly carry a major nobody reviewed" is a real
property, and until this ticket tuppence's adopter gate enforced it as a per-pull-request refusal:
the wrong shape, because the fact does not depend on anyone opening a pull request. It is a report
now, carried by the truth surface on every run, red on its own terms.

These tests pin the pure half: what counts as the composed window, where each adopter's own
identity constant is read from, and what the report says. The estate half — each adopter's real
composed evidence, platform's real signed evidence at the tag that adopter really pins, and a real
cosign verification — is verify-unreviewed-major-in-window.sh.
"""

from __future__ import annotations

import importlib.util
import subprocess
import tempfile
from pathlib import Path
from types import ModuleType

import pytest

GRADER = Path(__file__).resolve().parent.parent / "verify" / "unreviewed-major" / "unreviewed_major.py"


@pytest.fixture(scope="module")
def grader() -> ModuleType:
    spec = importlib.util.spec_from_file_location("unreviewed_major", GRADER)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# -- the window ---------------------------------------------------------------------------------


def test_the_window_is_the_member_versions_deduplicated(grader: ModuleType) -> None:
    doc = {"members": [{"name": "a", "version": "4.0.0"}, {"name": "b", "version": "4.0.0"},
                       {"name": "c", "version": "2.0.1"}]}
    assert grader.window_from_evidence(doc) == ["2.0.1", "4.0.0"]


def test_a_platform_machinery_member_carries_no_version_and_is_not_one(grader: ModuleType) -> None:
    doc = {"members": [{"name": "policy-version-orphan-guard"}, {"name": "a", "version": "4.0.0"}]}
    assert grader.window_from_evidence(doc) == ["4.0.0"]


# -- the pin ------------------------------------------------------------------------------------


def test_the_pinned_tag_is_read_off_the_gitrepository_document_of_a_multi_document_stream(
        grader: ModuleType) -> None:
    text = ("apiVersion: source.toolkit.fluxcd.io/v1\nkind: GitRepository\nmetadata:\n"
            "  name: platform\nspec:\n  ref:\n    tag: v2.0.1\n    commit: " + "d" * 40 + "\n"
            "---\napiVersion: kustomize.toolkit.fluxcd.io/v1\nkind: Kustomization\nspec:\n  path: x\n")
    assert grader.pin_from_pin_yaml(text) == ("v2.0.1", "d" * 40)
    assert grader.pin_from_pin_yaml("kind: Kustomization\nspec:\n  path: x\n") is None


def test_the_commit_the_pin_names_beside_the_tag_is_checked_not_discarded(grader: ModuleType) -> None:
    # ADR-0001's commit pin is load-bearing, and every adopter gate checks it before reading
    # anything. This report reads evidence AT the tag, so it makes the same check first.
    assert grader.pin_disagreement("v2.0.1", "a" * 40, "a" * 40) is None
    message = grader.pin_disagreement("v2.0.1", "a" * 40, "b" * 40)
    assert message is not None and "v2.0.1" in message and "a" * 40 in message and "b" * 40 in message
    unresolvable = grader.pin_disagreement("v2.0.1", "a" * 40, None)
    assert unresolvable is not None and "could not resolve" in unresolvable


def test_an_abbreviated_or_upper_case_sha_in_the_pin_is_not_a_disagreement(grader: ModuleType) -> None:
    # R5-5. Both spellings are valid git, and reading either as "the pin and the tag name different
    # platforms" would be this check inventing a red out of a formatting choice.
    assert grader.pin_disagreement("v2.0.1", ("a" * 40).upper(), "a" * 40) is None
    assert grader.pin_disagreement("v2.0.1", "a" * 12, "a" * 40) is None
    assert grader.pin_disagreement("v2.0.1", "a" * 40, ("a" * 12)) is None
    # a prefix too short to identify a commit is not accepted as one
    assert grader.pin_disagreement("v2.0.1", "aaa", "a" * 40) is not None
    assert grader.pin_disagreement("v2.0.1", "a" * 12, "b" * 40) is not None


# -- the identity constant, read where the adopter's own operation reads it ----------------------


def test_the_identity_constant_is_read_out_of_the_workflow_env_when_it_lives_there(
        grader: ModuleType) -> None:
    text = ("env:\n"
            "  EVIDENCE_EXPECTED_IDENTITY_REGEXP: ^https://github\\.com/org/platform/x\\.yml@refs/heads/main$\n"
            "  EXPECTED_ISSUER: https://token.actions.githubusercontent.com\n")
    got = grader.identity_from_workflow(text)
    assert got is not None
    regexp, issuer = got
    assert regexp.startswith("^https://github") and issuer.endswith("githubusercontent.com")


def test_the_identity_constant_is_read_out_of_the_gate_script_when_it_lives_there(
        grader: ModuleType) -> None:
    source = ('EXPECTED_PLATFORM_IDENTITY_REGEXP = (\n'
              '    r"^https://github\\.com/org/platform/"\n'
              '    r"\\.github/workflows/cut-release\\.yml@refs/heads/main$"\n'
              ')\n'
              'EXPECTED_PLATFORM_ISSUER = "https://token.actions.githubusercontent.com"\n')
    got = grader.identity_from_script(source)
    assert got is not None
    regexp, issuer = got
    # implicit concatenation across lines is one constant, not two
    assert regexp.endswith("refs/heads/main$") and "cut-release" in regexp
    assert issuer == "https://token.actions.githubusercontent.com"


def test_a_repository_that_holds_no_identity_constant_yields_nothing_rather_than_a_default(
        grader: ModuleType) -> None:
    assert grader.identity_from_workflow("env:\n  FOO: bar\n") is None
    assert grader.identity_from_script("X = 1\n") is None


# -- the report ---------------------------------------------------------------------------------


def test_a_major_standing_in_a_window_is_named_with_its_adopter_and_the_tag_it_was_read_at(
        grader: ModuleType) -> None:
    status, lines = grader.grade([
        {"adopter": "tuppence", "tag": "v2.0.1", "window": ["4.0.0"],
         "computed": {"4.0.0": "major"}, "skip": None},
    ])
    assert status == "FAIL"
    body = " ".join(m for _, m in lines)
    assert "tuppence" in body and "4.0.0" in body and "v2.0.1" in body and "major" in body


def test_a_window_of_no_majors_is_the_pass(grader: ModuleType) -> None:
    status, lines = grader.grade([
        {"adopter": "driftwood", "tag": "v2.0.1", "window": ["2.0.1", "3.0.0"],
         "computed": {"2.0.1": "none", "3.0.0": "patch"}, "skip": None},
    ])
    assert status == "PASS"


def test_an_adopter_that_could_not_be_looked_at_makes_the_whole_report_a_could_not_look(
        grader: ModuleType) -> None:
    status, lines = grader.grade([
        {"adopter": "driftwood", "tag": "v2.0.1", "window": ["2.0.1"],
         "computed": {"2.0.1": "none"}, "skip": None},
        {"adopter": "ludlow", "tag": None, "window": [], "computed": {},
         "skip": "pins platform tag v9.9.9, which this checkout of platform has no tag object for"},
    ])
    assert status == "SKIP"
    assert any("v9.9.9" in m for _, m in lines)


def test_one_unreadable_version_does_not_silence_a_major_already_observed_in_the_same_window(
        grader: ModuleType) -> None:
    # R5-1. The rule "a major that was actually observed is not softened by something that could
    # not be looked at" held ACROSS adopters and not WITHIN one: look() returned on the first
    # version whose evidence the pinned tag does not carry, and grade() read `skip` before
    # `computed`, so appending one unrelated member to composed/evidence.json turned an observed
    # FAIL into a SKIP and the major vanished from the report. The state is reachable: ADR-0011's
    # own 2026-09-03 note records platform's main carrying 4.0.0.json without its bundle.
    status, lines = grader.grade([
        {"adopter": "driftwood", "tag": "v2.0.1", "window": ["1.9.9", "4.0.0"],
         "computed": {"4.0.0": "major"}, "skip": None,
         "unread": [("1.9.9", "pins platform v2.0.1, whose tree carries no signed evidence for "
                              "policy version 1.9.9 that it declares in its window")]},
    ])
    assert status == "FAIL"
    body = " ".join(m for _, m in lines)
    assert "4.0.0" in body and "major" in body
    assert "1.9.9" in body  # the thing that could not be read is named too, not swallowed
    assert any(kind == "FAIL" and "4.0.0" in m for kind, m in lines)
    assert any(kind == "SKIP" and "1.9.9" in m for kind, m in lines)


def test_a_window_with_nothing_readable_and_no_major_is_a_could_not_look_naming_the_version(
        grader: ModuleType) -> None:
    status, lines = grader.grade([
        {"adopter": "ludlow", "tag": "v2.0.1", "window": ["1.9.9", "2.0.1"],
         "computed": {"2.0.1": "none"}, "skip": None,
         "unread": [("1.9.9", "pins platform v2.0.1, whose tree carries no signed evidence for "
                              "policy version 1.9.9 that it declares in its window")]},
    ])
    assert status == "SKIP"
    assert any(kind == "SKIP" and "1.9.9" in m for kind, m in lines)
    # and it still says what it DID verify, rather than going silent on the rest of the window
    assert any("2.0.1" in m for _, m in lines)


def test_a_major_outranks_a_could_not_look_because_it_was_actually_observed(grader: ModuleType) -> None:
    # A red that was seen is not softened by a second adopter that could not be seen.
    status, _ = grader.grade([
        {"adopter": "tuppence", "tag": "v2.0.1", "window": ["4.0.0"],
         "computed": {"4.0.0": "major"}, "skip": None},
        {"adopter": "ludlow", "tag": None, "window": [], "computed": {}, "skip": "no clone"},
    ])
    assert status == "FAIL"


def test_no_adopter_at_all_is_a_could_not_look(grader: ModuleType) -> None:
    status, lines = grader.grade([])
    assert status == "SKIP"
    assert any("adopter role" in m for _, m in lines)


# -- the acceptance record (eco-system ticket 129) ------------------------------------------------
#
# An institution accepts a major for itself by carrying a record in its OWN repository, under
# `accepted-majors/`, at the commit it serves. The check reads it there and nowhere else. These
# tests plant records; none of them is a real acceptance.

SERVED = "c" * 40


def _record(party: str = "driftwood", version: str = "5.0.0", publisher: str = "platform",
            accepted_by: str = "Example Owner", accepted_on: str = "2026-09-23",
            kind: str = "major-acceptance") -> str:
    return (f"kind: {kind}\nparty: {party}\npublisher: {publisher}\nversion: {version}\n"
            f"accepted_by: {accepted_by}\naccepted_on: {accepted_on}\n")


def _carrying(window: list[str], records: list[tuple[str, str]], adopter: str = "driftwood") -> dict:
    return {"adopter": adopter, "tag": "v3.2.0", "window": window,
            "computed": {v: "major" for v in window}, "skip": None,
            "served": SERVED, "records": records}


def test_a_well_formed_record_parses_to_the_fields_it_carries(grader: ModuleType) -> None:
    got = grader.acceptance_from_text(_record())
    assert got == {"party": "driftwood", "publisher": "platform", "version": "5.0.0",
                   "accepted_by": "Example Owner", "accepted_on": "2026-09-23"}


@pytest.mark.parametrize("text, reason", [
    (_record(kind="waiver"), "kind"),
    (_record(accepted_by="''"), "accepted_by"),
    (_record(accepted_on="yesterday"), "accepted_on"),
    ("kind: major-acceptance\nparty: driftwood\npublisher: platform\n", "version"),
    ("- not\n- a mapping\n", "mapping"),
    ("kind: [unclosed\n", "YAML"),
])
def test_a_malformed_record_is_not_a_record_and_says_why(grader: ModuleType, text: str,
                                                          reason: str) -> None:
    got = grader.acceptance_from_text(text)
    assert isinstance(got, str) and reason in got


def test_an_accepted_major_is_the_pass_and_names_who_when_where_and_at_which_commit(
        grader: ModuleType) -> None:
    status, lines = grader.grade([_carrying(["5.0.0"], [("accepted-majors/platform-5.0.0.yaml",
                                                          _record())])])
    assert status == "PASS"
    body = " ".join(m for _, m in lines)
    for needle in ("driftwood", "5.0.0", "Example Owner", "2026-09-23",
                   "accepted-majors/platform-5.0.0.yaml", SERVED[:12]):
        assert needle in body
    assert not any(kind == "FAIL" for kind, _ in lines)


def test_an_unaccepted_major_is_still_the_fail_and_says_where_a_record_would_be_read(
        grader: ModuleType) -> None:
    status, lines = grader.grade([_carrying(["5.0.0"], [])])
    assert status == "FAIL"
    fail = next(m for k, m in lines if k == "FAIL")
    assert "accepted-majors/" in fail and SERVED[:12] in fail


def test_a_record_for_another_institution_does_not_count_and_is_named(grader: ModuleType) -> None:
    # tuppence's acceptance, planted in driftwood's tree, accepts nothing for driftwood.
    status, lines = grader.grade([_carrying(["5.0.0"], [("accepted-majors/platform-5.0.0.yaml",
                                                          _record(party="tuppence"))])])
    assert status == "FAIL"
    fail = next(m for k, m in lines if k == "FAIL")
    assert "tuppence" in fail and "accepted-majors/platform-5.0.0.yaml" in fail


def test_a_record_for_another_version_does_not_count(grader: ModuleType) -> None:
    status, lines = grader.grade([_carrying(["5.0.0"], [("accepted-majors/platform-4.0.0.yaml",
                                                          _record(version="4.0.0"))])])
    assert status == "FAIL"


def test_a_record_for_another_publisher_does_not_count(grader: ModuleType) -> None:
    status, _ = grader.grade([_carrying(["5.0.0"], [("accepted-majors/nist-5.0.0.yaml",
                                                     _record(publisher="nist"))])])
    assert status == "FAIL"


def test_a_malformed_record_for_the_carried_version_does_not_count_and_is_named(
        grader: ModuleType) -> None:
    status, lines = grader.grade([_carrying(["5.0.0"], [("accepted-majors/platform-5.0.0.yaml",
                                                          _record(accepted_by="''"))])])
    assert status == "FAIL"
    fail = next(m for k, m in lines if k == "FAIL")
    assert "accepted_by" in fail


def test_before_the_rollout_the_unaccepted_4_0_0_stays_red_beside_an_accepted_5_0_0(
        grader: ModuleType) -> None:
    # The window the owner's 2026-09-23 decision passes through: 5.0.0 accepted and composed in,
    # 4.0.0 not yet retired and never accepted. Accepting one major accepts no other.
    status, lines = grader.grade([_carrying(["4.0.0", "5.0.0"],
                                            [("accepted-majors/platform-5.0.0.yaml", _record())])])
    assert status == "FAIL"
    assert any(k == "FAIL" and "4.0.0" in m for k, m in lines)
    assert not any(k == "FAIL" and "5.0.0" in m and "4.0.0" not in m for k, m in lines)
    assert any(k == "PASS" and "5.0.0" in m for k, m in lines)


def test_an_accepted_major_does_not_soften_another_adopters_unaccepted_one(
        grader: ModuleType) -> None:
    status, _ = grader.grade([
        _carrying(["5.0.0"], [("accepted-majors/platform-5.0.0.yaml", _record())]),
        _carrying(["5.0.0"], [], adopter="ludlow"),
    ])
    assert status == "FAIL"


# -- the record is read from the adopter's own tree at the commit it serves -----------------------

# The fixture's own git runs with no hooks (ticket 92 round 5, R2), so planting a commit makes no
# network call. The reads under test run plain git, as the check does on the real estate.
_NO_HOOKS = tempfile.mkdtemp(prefix="unreviewed-major-no-hooks-")


def _fixture_git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t",
                    "-c", "commit.gpgsign=false", "-c", f"core.hooksPath={_NO_HOOKS}", *args],
                   capture_output=True, text=True, check=True)


def test_only_a_record_committed_at_the_served_commit_is_read(grader: ModuleType,
                                                               tmp_path: Path) -> None:
    repo = tmp_path / "driftwood"
    (repo / "accepted-majors").mkdir(parents=True)
    _fixture_git(repo, "init", "-q", "-b", "main")
    (repo / "accepted-majors" / "platform-5.0.0.yaml").write_text(_record())
    (repo / "party.yaml").write_text("party: driftwood\n")
    _fixture_git(repo, "add", "accepted-majors/platform-5.0.0.yaml", "party.yaml")
    _fixture_git(repo, "commit", "-q", "-m", "plant")
    # Written into the working tree and staged, never committed: not served, so not read.
    (repo / "accepted-majors" / "platform-4.0.0.yaml").write_text(_record(version="4.0.0"))
    _fixture_git(repo, "add", "accepted-majors/platform-4.0.0.yaml")
    # A record anywhere but accepted-majors/ is not one either.
    (repo / "accepted-5.0.0.yaml").write_text(_record())
    served, records = grader.records_at_served_ref(repo)
    assert served is not None and len(served) == 40
    assert [p for p, _ in records] == ["accepted-majors/platform-5.0.0.yaml"]
    assert grader.acceptance_from_text(records[0][1])["version"] == "5.0.0"


def test_a_tree_with_no_record_directory_reads_as_no_records(grader: ModuleType,
                                                             tmp_path: Path) -> None:
    repo = tmp_path / "ludlow"
    repo.mkdir()
    _fixture_git(repo, "init", "-q", "-b", "main")
    (repo / "party.yaml").write_text("party: ludlow\n")
    _fixture_git(repo, "add", "party.yaml")
    _fixture_git(repo, "commit", "-q", "-m", "plant")
    served, records = grader.records_at_served_ref(repo)
    assert served is not None and records == []


# -- one format, one reader, copied into every adopter gate (eco-system ticket 132) ---------------
#
# The adopter gates now read the same records. The reader is defined once, in the hub module,
# between two marker lines. Each gate carries that block byte for byte, and the check grades every
# served copy against the hub's own on every run, so the two readers cannot drift apart quietly.


def _hub_block(grader: ModuleType) -> str:
    block = grader.reader_block(GRADER.read_text())
    assert block is not None
    return block


def test_the_reader_is_one_marked_block_in_the_hub_module(grader: ModuleType) -> None:
    block = _hub_block(grader)
    assert block.startswith(grader.READER_BEGIN)
    assert block.rstrip("\n").endswith(grader.READER_END)
    for name in ("RECORD_KIND", "def acceptance_from_text", "def acceptance_for",
                 "def acceptance_records_at"):
        assert name in block


def test_a_gate_carrying_the_block_byte_for_byte_has_not_drifted(grader: ModuleType) -> None:
    gate = "#!/usr/bin/env python3\nimport yaml\n\n" + _hub_block(grader) + "\n\ndef main():\n    pass\n"
    assert grader.reader_drift(gate) is None


def test_a_gate_without_the_block_has_drifted_and_says_so(grader: ModuleType) -> None:
    got = grader.reader_drift("#!/usr/bin/env python3\ndef main():\n    pass\n")
    assert got is not None and "carries no" in got


def test_a_gate_whose_copy_differs_by_one_character_has_drifted_and_names_the_line(
        grader: ModuleType) -> None:
    block = _hub_block(grader)
    changed = block.replace('RECORD_KIND = "major-acceptance"', 'RECORD_KIND = "major-acceptence"')
    assert changed != block
    got = grader.reader_drift("import yaml\n" + changed)
    assert got is not None and "differs" in got and "major-acceptence" in got


def test_a_drifted_reader_is_a_fail_even_when_every_major_is_accepted(grader: ModuleType) -> None:
    finding = _carrying(["5.0.0"], [("accepted-majors/platform-5.0.0.yaml", _record())])
    finding["reader_drift"] = "carries a major-acceptance reader that differs from the hub's"
    status, lines = grader.grade([finding])
    assert status == "FAIL"
    fail = next(m for k, m in lines if k == "FAIL")
    assert "driftwood" in fail and "differs" in fail


def test_the_records_are_read_at_the_ref_named_not_at_head(grader: ModuleType,
                                                           tmp_path: Path) -> None:
    # The gate grades a pull request's head, which is not the commit the repository serves.
    repo = tmp_path / "tuppence"
    (repo / "accepted-majors").mkdir(parents=True)
    _fixture_git(repo, "init", "-q", "-b", "main")
    (repo / "accepted-majors" / "platform-5.0.0.yaml").write_text(_record(party="tuppence"))
    _fixture_git(repo, "add", "accepted-majors/platform-5.0.0.yaml")
    _fixture_git(repo, "commit", "-q", "-m", "accept")
    accepted = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True,
                              text=True, check=True).stdout.strip()
    _fixture_git(repo, "rm", "-q", "accepted-majors/platform-5.0.0.yaml")
    _fixture_git(repo, "commit", "-q", "-m", "withdraw")
    assert [p for p, _ in grader.acceptance_records_at(repo, accepted)] == [
        "accepted-majors/platform-5.0.0.yaml"]
    assert grader.acceptance_records_at(repo, "HEAD") == []


def test_a_ref_that_does_not_resolve_is_an_error_not_an_empty_directory(grader: ModuleType,
                                                                        tmp_path: Path) -> None:
    repo = tmp_path / "ludlow"
    repo.mkdir()
    _fixture_git(repo, "init", "-q", "-b", "main")
    (repo / "party.yaml").write_text("party: ludlow\n")
    _fixture_git(repo, "add", "party.yaml")
    _fixture_git(repo, "commit", "-q", "-m", "plant")
    with pytest.raises(ValueError, match="f" * 12):
        grader.acceptance_records_at(repo, "f" * 40)
