"""verify/fold-agreement — the comparator and the workflow reader, at the grader's own seam.

Eco-system ticket 99. Three adopters carry three hand-written gates answering one question, and
nothing in the estate graded whether they answered it the same way; tuppence diverged for a
fortnight and it was found by a red workflow, not by a check. The grader beside these tests plants
a case, runs each adopter's REAL gate through the flag shape its own `shift-left.yml` uses, and
refuses the day two of them disagree.

These tests pin the pure half: reading the served operation out of a workflow, resolving that
operation's own tokens onto planted values without inventing a flag, and judging agreement. The
estate half — real repositories, real cosign, real exit codes — is verify-fold-agreement.sh.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest

GRADER = Path(__file__).resolve().parent.parent / "verify" / "fold-agreement" / "fold_agreement.py"


@pytest.fixture(scope="module")
def grader() -> ModuleType:
    spec = importlib.util.spec_from_file_location("fold_agreement", GRADER)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


WORKFLOW = """
name: shift-left
jobs:
  gate:
    steps:
      - name: checkout platform at the pinned tag
        uses: actions/checkout@v4
      - name: adopter gate -- verify the pin, verify evidence, compose the bump
        id: adopter_gate
        run: |
          set -euo pipefail
          old_pin=old-platform-pin.yaml
          python3 unit/.github/scripts/adopter-gate.py \\
            --platform-dir platform \\
            --new-pin-yaml unit/gitops/platform/platform-pin.yaml \\
            --old-pin-yaml "$old_pin" \\
            --base-ref "${{ github.event.pull_request.base.sha }}" \\
            --head-ref HEAD \\
            --out adopter-summary.json 2>&1 | tee gate.txt
      - name: fill this institution's own per-institution matrix row
        run: |
          python3 unit/.github/scripts/adopter-gate.py --matrix-row \\
            --platform-dir platform --adopter-dir unit
"""


# -- reading the served operation ---------------------------------------------------------------


def test_the_gate_argv_is_read_off_the_step_the_workflow_names_adopter_gate(grader: ModuleType) -> None:
    argv = grader.gate_argv(WORKFLOW, "adopter-gate.py")
    assert argv[0] == "python3"
    assert argv[1] == "unit/.github/scripts/adopter-gate.py"
    # the shell tail is not part of the operation that reaches the artefact
    assert "|" not in argv and "tee" not in argv and "2>&1" not in argv
    assert argv[-2:] == ["--out", "adopter-summary.json"]


def test_the_matrix_row_invocation_of_the_same_script_is_not_the_gate(grader: ModuleType) -> None:
    assert "--matrix-row" not in grader.gate_argv(WORKFLOW, "adopter-gate.py")


def test_a_workflow_with_no_adopter_gate_step_is_a_could_not_look_not_a_guess(grader: ModuleType) -> None:
    with pytest.raises(grader.NoGateStep):
        grader.gate_argv("jobs:\n  x:\n    steps:\n      - name: build\n        run: make\n",
                         "adopter-gate.py")


def test_long_flags_are_the_flags_and_not_the_values(grader: ModuleType) -> None:
    assert grader.long_flags(grader.gate_argv(WORKFLOW, "adopter-gate.py")) == {
        "--platform-dir", "--new-pin-yaml", "--old-pin-yaml", "--base-ref", "--head-ref", "--out"}


# -- resolving that operation onto planted values -----------------------------------------------


def test_resolve_substitutes_only_what_it_was_given(grader: ModuleType) -> None:
    argv = grader.resolve_argv(
        ["python3", "unit/.github/scripts/adopter-gate.py", "--platform-dir", "platform",
         "--base-ref", "${{ github.event.pull_request.base.sha }}", "--head-ref", "HEAD"],
        {"unit/.github/scripts/adopter-gate.py": "/plant/gate.py",
         "platform": "/plant/platform",
         "${{ github.event.pull_request.base.sha }}": "abc123",
         # `HEAD` is a value like any other: planted explicitly, never waved through because it
         # happens to be a literal that would have worked.
         "HEAD": "def456"},
    )
    assert argv == ["python3", "/plant/gate.py", "--platform-dir", "/plant/platform",
                    "--base-ref", "abc123", "--head-ref", "def456"]


def test_an_unmapped_expression_refuses_rather_than_running_a_literal_dollar_sign(grader: ModuleType) -> None:
    # A workflow that grows a new templated argument must break this grader loudly. Passing
    # `${{ ... }}` through to a real gate would run a case nobody planted.
    with pytest.raises(grader.Unresolved):
        grader.resolve_argv(["python3", "g.py", "--new-ref", "${{ github.event.pull_request.head.sha }}"],
                            {"g.py": "/plant/gate.py"})
    with pytest.raises(grader.Unresolved):
        grader.resolve_argv(["python3", "g.py", "--old-pin-yaml", "$old_pin"], {"g.py": "/plant/gate.py"})


def test_a_new_long_flag_with_a_plain_literal_value_refuses_too(grader: ModuleType) -> None:
    # The narrowing, 2026-09-05. Templating was never the thing that made an argument dangerous:
    # `--corpus-dir corpus/generated` carries no `${{ }}` at all, and before this it went straight
    # to the real gate. The run only went red because argparse happens to reject an unknown flag --
    # a gate parsing with parse_known_args, or one that accepts the flag (`--skip-cosign-verify` is
    # in tuppence's gate), would have carried it into the planted run in silence.
    mapping = {"g.py": "/plant/gate.py", "platform": "/plant/platform",
               "corpus/generated": "/plant/corpus"}
    with pytest.raises(grader.Unresolved) as caught:
        grader.resolve_argv(
            ["python3", "g.py", "--platform-dir", "platform", "--corpus-dir", "corpus/generated"],
            mapping)
    assert "--corpus-dir" in str(caught.value)


def test_the_value_of_a_known_flag_that_was_not_planted_refuses(grader: ModuleType) -> None:
    with pytest.raises(grader.Unresolved) as caught:
        grader.resolve_argv(["python3", "g.py", "--platform-dir", "somewhere-else"],
                            {"g.py": "/plant/gate.py"})
    assert "somewhere-else" in str(caught.value)


def test_a_positional_nobody_planted_refuses(grader: ModuleType) -> None:
    with pytest.raises(grader.Unresolved) as caught:
        grader.resolve_argv(["python3", "g.py", "compose", "platform"], {"g.py": "/plant/gate.py"})
    assert "compose" in str(caught.value)


def test_one_literal_claimed_by_two_roles_refuses_instead_of_collapsing(grader: ModuleType,
                                                                        tmp_path) -> None:
    # R5-4. The plant is keyed by token TEXT. A workflow spelling two different arguments with the
    # same literal -- `--base-ref HEAD --head-ref HEAD` -- would collapse to one mapping entry and
    # hand base-ref the head commit, running a case nobody planted. It refuses instead.
    planted = {"base_sha": "aaa", "head_sha": "bbb", "base_tag": "v1", "head_tag": "v2"}
    with pytest.raises(grader.Unresolved) as caught:
        grader.build_mapping(
            ["python3", "g.py", "--base-ref", "HEAD", "--head-ref", "HEAD"],
            tmp_path / "gate.py", planted, tmp_path / "platform", tmp_path / "repo",
            tmp_path / "out.json", tmp_path / "out.md", ("regexp", "issuer"))
    assert "HEAD" in str(caught.value)


def test_two_roles_planting_the_same_value_for_one_literal_is_fine(grader: ModuleType,
                                                                   tmp_path) -> None:
    planted = {"base_sha": "aaa", "head_sha": "aaa", "base_tag": "v1", "head_tag": "v2"}
    mapping = grader.build_mapping(
        ["python3", "g.py", "--base-ref", "HEAD", "--head-ref", "HEAD"],
        tmp_path / "gate.py", planted, tmp_path / "platform", tmp_path / "repo",
        tmp_path / "out.json", tmp_path / "out.md", ("regexp", "issuer"))
    assert mapping["HEAD"] == "aaa"


# -- reading a verdict back ---------------------------------------------------------------------


def test_the_composed_bump_is_read_out_of_the_rendered_comment_table(grader: ModuleType) -> None:
    md = ("### computed-semver adopter gate\n\n"
          "| | declared (publisher's tag) | composed (this institution) |\n"
          "|---|---|---|\n"
          "| bump | **patch** | **none** |\n")
    assert grader.composed_from_markdown(md) == "none"
    assert grader.composed_from_markdown("nothing here") is None


# -- judging agreement --------------------------------------------------------------------------


def _r(verdict: str, composed: str) -> dict:
    return {"verdict": verdict, "composed": composed}


def test_three_gates_that_answer_alike_diverge_on_nothing(grader: ModuleType) -> None:
    assert grader.divergences("standing", {"driftwood": _r("adopt", "none"),
                                           "ludlow": _r("adopt", "none"),
                                           "tuppence": _r("adopt", "none")}) == []


def test_the_verdict_that_broke_the_estate_is_named_when_one_gate_refuses_alone(grader: ModuleType) -> None:
    lines = grader.divergences("standing", {"driftwood": _r("adopt", "none"),
                                            "ludlow": _r("adopt", "none"),
                                            "tuppence": _r("refuse", "major")})
    assert len(lines) == 1
    assert "standing" in lines[0] and "tuppence" in lines[0]
    assert "refuse" in lines[0] and "adopt" in lines[0]


def test_the_same_verdict_reached_with_a_different_composed_bump_is_still_a_divergence(grader: ModuleType) -> None:
    # Two gates that both adopt, one calling the movement `patch` and one `none`, disagree about
    # the number the reviewer reads even though the required check is green in both.
    lines = grader.divergences("arrival", {"driftwood": _r("adopt", "patch"),
                                           "ludlow": _r("adopt", "none"),
                                           "tuppence": _r("adopt", "none")})
    assert len(lines) == 1 and "patch" in lines[0] and "driftwood" in lines[0]


def test_a_gate_that_refused_without_stating_a_bump_has_still_answered_and_is_compared(
        grader: ModuleType) -> None:
    # ludlow's gate refuses when its own cosign invocation errors, and its exit code is what its
    # own required check grades. That is an answer, and one that differs from the other two. It is
    # named -- with the output that explains it -- never excused as a could-not-look.
    refused = {"verdict": "refuse", "composed": None,
               "output": "error during command execution: --trusted-root only supported with ..."}
    lines = grader.divergences("quiet", {"driftwood": _r("adopt", "none"),
                                         "tuppence": _r("adopt", "none"),
                                         "ludlow": refused})
    assert len(lines) == 1
    assert "ludlow" in lines[0] and "no composed bump" in lines[0] and "--trusted-root" in lines[0]
    assert grader.grade({"quiet": {"driftwood": _r("adopt", "none"),
                                   "tuppence": _r("adopt", "none"),
                                   "ludlow": refused}})[0] == "FAIL"


def test_a_gate_that_could_not_be_run_at_all_is_a_could_not_look_never_an_agreement(grader: ModuleType) -> None:
    status, lines = grader.grade({"standing": {"driftwood": _r("adopt", "none"),
                                               "ludlow": None,
                                               "tuppence": _r("adopt", "none")}})
    assert status == "SKIP"
    assert any("ludlow" in message for _, message in lines)


def test_one_gate_agreeing_with_itself_is_not_agreement(grader: ModuleType) -> None:
    status, lines = grader.grade({"standing": {"driftwood": _r("adopt", "none")}})
    assert status == "SKIP"
    assert any("fewer than two" in message for _, message in lines)


def test_agreement_on_every_case_is_the_only_pass(grader: ModuleType) -> None:
    status, _ = grader.grade({"standing": {"driftwood": _r("adopt", "none"),
                                           "ludlow": _r("adopt", "none"),
                                           "tuppence": _r("adopt", "none")},
                              "retirement": {"driftwood": _r("refuse", "major"),
                                             "ludlow": _r("refuse", "major"),
                                             "tuppence": _r("refuse", "major")}})
    assert status == "PASS"
    status, _ = grader.grade({"standing": {"driftwood": _r("adopt", "none"),
                                           "ludlow": _r("adopt", "none"),
                                           "tuppence": _r("refuse", "major")}})
    assert status == "FAIL"
