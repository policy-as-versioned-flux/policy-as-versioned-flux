"""Ecosystem ticket 76: every green rests on an observation.

Two seams. The pure one is verify/every-green/every_green.py, which names a `SKIP` printed and
then `exit 0` by file and line; the gate script verify-every-green.sh runs it over the estate. The
other is the text of the hub's own verify scripts the ticket names: the shapes that produced the
false greens must be gone from the hub, and this file is what turns red when one comes back. The
estate's scripts are graded by the gate script, not here: hub CI clones the units' pushed heads,
which the hub cannot move.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


every_green = _load("every_green", ROOT / "verify" / "every-green" / "every_green.py")
feed_contract = _load("feed_contract", ROOT / "verify" / "feed-contract" / "feed_contract.py")


# -- the scanner ---------------------------------------------------------------------------------

def test_a_skip_followed_by_exit_zero_is_named_by_line() -> None:
    assert every_green.offenders('echo "SKIP: no kyverno"\nexit 0\n') == [1]
    assert every_green.offenders('if x; then\n  echo "SKIP: no kyverno"\n  exit 0\nfi\n') == [2]


def test_a_skip_followed_by_exit_three_is_not_an_offender() -> None:
    assert every_green.offenders('echo "SKIP: no kyverno"\nexit 3\n') == []


def test_a_two_line_skip_reason_is_still_caught() -> None:
    text = 'echo "SKIP (step 5): kyverno CLI not found -- cannot prove"\necho "the second half"\nexit 0\n'
    assert every_green.offenders(text) == [1]


def test_comments_are_not_statements() -> None:
    text = '# SKIPs (exit 0) if absent, same convention as the others\necho ok\nexit 0\n'
    assert every_green.offenders(text) == []
    text = 'echo "SKIP: x"\n# exit 0 would be wrong here\nexit 3\n'
    assert every_green.offenders(text) == []


def test_a_fixture_written_by_printf_into_a_file_is_not_the_script_itself() -> None:
    # verify-e2e-step7-honesty.sh plants 'echo "SKIP: honest reason"\nexit 0' INSIDE one printf
    # line that writes a fixture file; that is the harness proving itself, not a green on absence.
    text = "printf 'echo \"SKIP: honest reason\"\\nexit 0\\n' >\"$t/verify-e2e-step2-mismatch.sh\"\n"
    assert every_green.offenders(text) == []


def test_a_skip_that_exits_on_its_own_line_is_not_an_offender() -> None:
    # the commonest honest shape in the estate: `echo "SKIP: ..."; exit 3` in one statement
    assert every_green.offenders('  echo "SKIP: no clone"; exit 3\n') == []
    assert every_green.offenders('x || { echo "SKIP: no clone"; exit 3; }\n') == []


def test_a_skip_that_falls_through_to_the_rest_of_the_script_is_an_offender() -> None:
    # verify-witness-set.sh's original step 5: SKIP printed over two echo lines, no exit at all,
    # then the script carried on and ended PASS. The shape the exit-0 rule alone cannot see.
    text = ('if ! command -v kyverno >/dev/null; then\n'
            '  echo "SKIP (step 5): kyverno CLI not found -- cannot prove the require-nonroot"\n'
            '  echo "satisfied probe passes real admission"\n'
            'else\n'
            '  do_the_real_check\n'
            'fi\n'
            'echo "PASS: witness set holds"\n')
    assert every_green.offenders(text) == [2]
    assert every_green.offences(text) == [(2, "falls through")]


def test_the_two_shapes_are_named_apart() -> None:
    assert every_green.offences('echo "SKIP: x"\nexit 0\n') == [(1, "exit 0")]
    assert every_green.offences('echo "SKIP: x"\nexit 3\n') == []


def test_a_multi_line_quoted_skip_reason_is_one_statement() -> None:
    # an echo whose string runs over two lines, then exit 3: honest, and not two statements
    assert every_green.offenders('echo "SKIP: no platform clone\n  (run clone-estate.sh)"\nexit 3\n') == []


def test_scan_walks_verify_scripts_and_skips_work_and_git(tmp_path: Path) -> None:
    (tmp_path / "u" / ".work" / "t").mkdir(parents=True)
    (tmp_path / "u" / ".git").mkdir()
    (tmp_path / "u" / "verify-bad.sh").write_text('echo "SKIP: x"\nexit 0\n')
    (tmp_path / "u" / "verify-good.sh").write_text('echo "SKIP: x"\nexit 3\n')
    (tmp_path / "u" / ".work" / "t" / "verify-bad.sh").write_text('echo "SKIP: x"\nexit 0\n')
    (tmp_path / "u" / ".git" / "verify-bad.sh").write_text('echo "SKIP: x"\nexit 0\n')
    (tmp_path / "u" / "not-a-verify.sh").write_text('echo "SKIP: x"\nexit 0\n')
    assert every_green.scan(str(tmp_path)) == [
        str(tmp_path / "u" / "verify-bad.sh") + ":1: exit 0"]


def test_the_skip_verdict_token_is_named_in_every_print_form() -> None:
    # widened 2026-09-04: the wrappers and flags the estate's scripts actually use
    assert every_green.offenders('say "SKIP: no kyverno"\nexit 0\n') == [1]
    assert every_green.offenders('echo -e "SKIP: no kyverno"\nexit 0\n') == [1]
    assert every_green.offenders("printf -- '\\033[1;36mSKIP: %s\\n' \"no kyverno\"\nexit 0\n") == [1]
    assert every_green.offenders('echo SKIP: no kyverno\nexit 0\n') == [1]
    assert every_green.offenders('say "SKIPPED nothing here"\nexit 0\n') == []


def test_a_prose_could_not_look_is_not_graded_by_this_net() -> None:
    """The boundary the PASS line states. `echo "(skipped: kyverno not found)"` then a PASS is
    sometimes a false green (verify-proportionality.sh:75 on main) and sometimes an honest
    narrowing (tuppence/reset/verify-reach-secrets.sh), and the difference is in the PASS
    sentence, which no regex reads. Execution grades those only where a script calls a
    selfcheck_absent leg; where none is called, nothing grades them, which the PASS line says
    after counting the callers. This net grades the verdict token."""
    prose = ('echo "    (skipped: kyverno CLI not found -- offline body proof unavailable here)"\n'
             'echo "PASS: the shared control body is a real policy"\n')
    assert every_green.offenders(prose) == []


def test_a_script_that_cannot_be_read_is_reported_unlooked_not_clean(tmp_path: Path) -> None:
    """A dangling symlink (verify/demo/verify-demo.sh is one when talk/ is not beside it) used to
    raise FileNotFoundError out of scan() and the shell printed a FAIL that named nothing."""
    (tmp_path / "verify-good.sh").write_text('echo "SKIP: x"\nexit 3\n')
    (tmp_path / "verify-dangling.sh").symlink_to(tmp_path / "gone.sh")
    hits, unread = every_green.read_tree(str(tmp_path))
    assert hits == []
    assert len(unread) == 1 and unread[0].startswith(str(tmp_path / "verify-dangling.sh"))
    assert every_green.main(["scan", str(tmp_path)]) == 3
    assert every_green.main(["scan", str(tmp_path / "no-such-dir")]) == 3


def test_the_scanner_selfcheck_holds() -> None:
    every_green.selfcheck()


# -- the hub's own verify scripts carry none of the shapes ---------------------------------------

def test_no_hub_verify_script_prints_skip_then_exits_zero() -> None:
    assert every_green.scan(str(ROOT / "verify")) == []


def _text(*parts: str) -> str:
    return (ROOT.joinpath(*parts)).read_text(encoding="utf-8")


def test_provenance_and_proportionality_have_an_exit_three_path_and_a_selfcheck() -> None:
    for rel in (("verify", "provenance", "verify-provenance.sh"),
                ("verify", "proportionality", "verify-proportionality.sh")):
        text = _text(*rel)
        assert "lib-observation.sh" in text, f"{rel[-1]} does not source the could-not-look helpers"
        assert "could_not_look" in text, f"{rel[-1]} names no tail that could fail to look"
        assert "pass_or_skip" in text, f"{rel[-1]} still asserts PASS unconditionally"
        assert "--selfcheck" in text, f"{rel[-1]} has no selfcheck leg"
    helpers = _text("verify", "lib-observation.sh")
    assert "exit 3" in helpers, "pass_or_skip must exit 3 when a tail could not look"


def test_step6_resolves_tags_from_publishes_and_infers_no_absence() -> None:
    text = _text("verify", "e2e", "verify-e2e-step6-provenance.sh")
    assert "tag -l 'v*.*.*'" not in text, "a typed tag shape cannot match feeds' threat-register/v2.0.0"
    assert "no signed tag yet" not in text, "an absence inferred from a failed lookup is not an observation"
    assert "newest_tag_per_line" in text, "the tag shape is each unit's own publishes[]"


def test_step5_consumes_the_overlay_verdicts_and_names_ticket_72() -> None:
    text = _text("verify", "e2e", "verify-e2e-step5-twin-forecasts.sh")
    assert "verify-twin-overlay.sh" in text and "verify-twin-scenarios.sh" in text
    assert "ticket 72" in text
    assert "twin-sweep.jsonl" in text, "the dated sweep observation is what ticket 72 supplies"


def test_twin_evals_reads_the_label_it_spends_from_the_twin() -> None:
    """Ticket 76 review, 2026-09-04: the Answer claimed the label was read from
    twin.evolution_judge.CORPUS_KIND and not typed into the shell, and it was typed in twice. Both
    surfaces -- the per-metric line inside the harness and the closing PASS line -- now carry the
    constant, and the only assertion made about the word is that the two agree."""
    text = _text("verify", "twin-evals", "verify-twin-evals.sh")
    assert "from twin.evolution_judge import CORPUS_KIND; print(CORPUS_KIND)" in text, \
        "the shell does not read the label from the twin"
    closing = [l for l in text.splitlines() if l.strip().startswith('echo "PASS: $(sed')]
    assert closing and "$CORPUS_KIND metrics" in closing[0], closing
    # the word may still appear as a definition of what that label means; what it may not be is
    # the label the line spends about this run's seven scores
    assert "harness-mechanism metrics" not in closing[0], "the closing line types the label"
    assert 'out(LABEL == CORPUS_KIND,' in text, "the label and the surface are not asserted to agree"
    assert 'CORPUS_KIND == "harness-mechanism"' not in text, \
        "a typed label in the assertion turns the check red when the corpus is held out"


# -- the tag resolution step 6 uses --------------------------------------------------------------

def test_newest_tag_per_line_reads_each_lines_own_shape() -> None:
    feeds = {"publishes": [{"name": "threat-register"}, {"name": "cve"}]}
    tags = {"threat-register/v1.0.0", "threat-register/v2.0.0"}
    assert feed_contract.newest_tag_per_line(feeds, tags) == {
        "threat-register": "threat-register/v2.0.0", "cve": None}


def test_a_bare_tag_signs_every_published_line() -> None:
    platform = {"publishes": [{"name": "policy"}, {"name": "identity-substrate"}]}
    assert feed_contract.newest_tag_per_line(platform, {"v1.0.0", "v2.0.1", "v2.0.0"}) == {
        "policy": "v2.0.1", "identity-substrate": "v2.0.1"}


def test_newest_is_by_version_not_by_string() -> None:
    assert feed_contract.newest_tag_per_line({"publishes": [{"name": "x"}]},
                                             {"v1.9.0", "v1.10.0"}) == {"x": "v1.10.0"}


def test_another_lines_tag_and_a_bare_major_are_not_this_lines() -> None:
    assert feed_contract.newest_tag_per_line({"publishes": [{"name": "x"}]},
                                             {"x/v1.0.0", "y/v9.9.9", "v1"}) == {"x": "x/v1.0.0"}
