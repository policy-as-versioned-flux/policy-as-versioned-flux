"""Eco-system ticket 115: a loophole round is a procedure this estate can re-run.

The seam is `bench/loophole/loophole_round.py` and `bench/loophole/check_no_prompt_leak.py`,
the estate's own harness around the external loophole tool (ADR-0030). These tests never call a
model and never import loophole: they hold the harness's guards down, so a guard fails the run
rather than living in somebody's memory. What they hold, in ticket order:

  1. the harness imports without `LOOPHOLE_SRC`, so the guards are testable with no clone;
  2. `--bare` never reaches `claude -p`, and the failure shape it produces (exit 0,
     `is_error: true`, "Not logged in") refuses the call rather than reading as zero candidates
     (ADR-0030 point 6, first bullet);
  3. a round is clean only when BOTH counters read zero: a malformed tag fires parse failures,
     a total format collapse fires under-production, and a judge reply with no verdict tag is a
     third failure the upstream judge would silently read as "unresolvable" (points 5 and 6);
  4. the startup control fails when a parser does not make the counters fire;
  5. the prompt-leak check fires on a copied 8-word run, passes clean text, and refuses to run
     when its own negative control does not fire (point 7);
  6. a round's summary carries every field point 9 lists and names its ticket from the caller,
     never from a constant;
  7. the unredacted log and the loophole clone may not sit inside the project tree (points 1
     and 7).

None of this makes loophole a gate check (point 8). What is graded here is the estate's own
deterministic harness, never the tool's output.
"""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
BENCH = ROOT / "bench" / "loophole"


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def harness(monkeypatch_module: pytest.MonkeyPatch) -> Any:
    monkeypatch_module.delenv("LOOPHOLE_SRC", raising=False)
    return _load("loophole_round_t115", BENCH / "loophole_round.py")


@pytest.fixture(scope="module")
def leak() -> Any:
    return _load("check_no_prompt_leak_t115", BENCH / "check_no_prompt_leak.py")


@pytest.fixture(scope="module")
def monkeypatch_module() -> Any:
    mp = pytest.MonkeyPatch()
    yield mp
    mp.undo()


# The upstream parser's regex, restated here as a stand-in so the tests need no clone. The real
# parser is what the harness's startup control runs against (`--controls-only`).
_PAIR = re.compile(
    r"<scenario>\s*<description>(.*?)</description>\s*<explanation>(.*?)</explanation>\s*</scenario>",
    re.DOTALL,
)


def _stand_in_parser(raw: str) -> int:
    return len(_PAIR.findall(raw))


WELL_FORMED = "<scenario><description>d</description><explanation>e</explanation></scenario>"


# 1. The harness is importable with no clone.


def test_the_harness_imports_without_a_clone(harness: Any) -> None:
    assert callable(harness.main)


# 2. --bare, and the failure shape it produces.


def test_the_command_never_carries_bare(harness: Any) -> None:
    cmd = harness.claude_command("sonnet", "a system prompt")
    assert "--bare" not in cmd
    assert not any(arg.startswith("--bare") for arg in cmd)
    assert cmd[:2] == ["claude", "-p"]


@pytest.mark.parametrize("flag", ["--bare", "--bare=true"])
def test_a_command_carrying_bare_is_refused(harness: Any, flag: str) -> None:
    with pytest.raises(harness.GuardError, match="--bare"):
        harness.refuse_forbidden_flags(["claude", "-p", flag, "--model", "sonnet"])


def test_the_harness_source_quotes_bare_only_in_the_guard(harness: Any) -> None:
    # The flag's name may appear in prose. As a quoted string it may appear on one line only,
    # the guard's own table, so no edit can slip it into the command list unnoticed.
    assert "--bare" in harness.FORBIDDEN_FLAGS
    lines = [ln.strip() for ln in (BENCH / "loophole_round.py").read_text().splitlines()
             if '"--bare' in ln]
    assert lines == ['FORBIDDEN_FLAGS = ("--bare",)']


def test_not_logged_in_at_exit_zero_is_refused(harness: Any) -> None:
    stdout = json.dumps({
        "type": "result", "subtype": "success", "is_error": True,
        "result": "Not logged in · Please run /login",
    })
    with pytest.raises(harness.GuardError, match="reported an error"):
        harness.read_cli_result("loophole_finder", 0, stdout)


def test_a_non_json_reply_is_refused(harness: Any) -> None:
    with pytest.raises(harness.GuardError, match="transport"):
        harness.read_cli_result("judge", 0, "Not logged in")


def test_a_nonzero_exit_is_refused(harness: Any) -> None:
    stdout = json.dumps({"is_error": False, "result": WELL_FORMED})
    with pytest.raises(harness.GuardError, match="rc=1"):
        harness.read_cli_result("judge", 1, stdout)


def test_a_good_reply_returns_its_text_and_its_measures(harness: Any) -> None:
    stdout = json.dumps({
        "is_error": False, "result": WELL_FORMED, "total_cost_usd": 0.05,
        "modelUsage": {"claude-sonnet-5": {}}, "usage": {"output_tokens": 12},
    })
    text, fields = harness.read_cli_result("loophole_finder", 0, stdout)
    assert text == WELL_FORMED
    assert fields["total_cost_usd"] == 0.05
    assert fields["model_served"] == ["claude-sonnet-5"]


# 3. Two counters, both at zero, and the judge's missing verdict.


def _audit(harness: Any, raw: str) -> dict[str, int]:
    audit: dict[str, int] = harness.parse_audit(raw, _stand_in_parser(raw), 3)
    return audit


def test_a_well_formed_round_is_clean(harness: Any) -> None:
    audits = {"loophole_finder": _audit(harness, WELL_FORMED * 3),
              "overreach_finder": _audit(harness, WELL_FORMED * 3)}
    verdicts = [{"key": "loophole-1", "verdict_tag_present": True}]
    assert harness.round_failures(audits, verdicts) == []


def test_a_malformed_tag_fails_the_round_on_parse_failures(harness: Any) -> None:
    bad = "<scenario><desc>d</desc><why>e</why></scenario>" * 3
    audits = {"loophole_finder": _audit(harness, bad),
              "overreach_finder": _audit(harness, WELL_FORMED * 3)}
    failures = harness.round_failures(audits, [])
    assert audits["loophole_finder"]["parse_failures"] == 3
    assert audits["loophole_finder"]["under_production"] == 0
    assert failures == ["loophole_finder: 3 parse failures"]


def test_a_total_format_collapse_fails_the_round_on_under_production(harness: Any) -> None:
    # The tag counter alone reads 0 here: no tag was opened, so nothing failed to parse.
    prose = "Here are three loopholes: first, ... second, ... third, ..."
    audits = {"loophole_finder": _audit(harness, WELL_FORMED * 3),
              "overreach_finder": _audit(harness, prose)}
    assert audits["overreach_finder"]["parse_failures"] == 0
    assert harness.round_failures(audits, []) == ["overreach_finder: under-production of 3"]


def test_a_judge_reply_with_no_verdict_fails_the_round(harness: Any) -> None:
    audits = {"loophole_finder": _audit(harness, WELL_FORMED * 3),
              "overreach_finder": _audit(harness, WELL_FORMED * 3)}
    verdicts = [{"key": "overreach-4", "verdict_tag_present": False}]
    assert harness.round_failures(audits, verdicts) == [
        "judge: no <verdict> tag on overreach-4, read upstream as unresolvable"]


@pytest.mark.parametrize("raw, present", [
    ("<verdict>resolvable</verdict>", True),
    ("<verdict> Unresolvable </verdict>", True),
    ("<verdict>maybe</verdict>", False),
    ("the verdict is resolvable", False),
])
def test_a_verdict_counts_only_when_upstream_would_read_it(harness: Any, raw: str, present: bool) -> None:
    assert harness.verdict_tag_present(raw) is present


# 4. The startup control against the parser.


def test_the_counter_control_passes_on_a_parser_that_behaves_like_upstream(harness: Any) -> None:
    assert harness.counter_control_failures(_stand_in_parser) == []


def test_the_counter_control_fails_when_the_parser_takes_everything(harness: Any) -> None:
    # A parser that reports three scenarios whatever it is handed would hide both failures.
    failures = harness.counter_control_failures(lambda raw: 3)
    assert any("wrong inner tags" in f for f in failures)
    assert any("prose only" in f for f in failures)


# 5. The prompt-leak check.


PROMPT_MODULE = (
    'LOOPHOLE_FINDER_SYSTEM = """You are an adversarial analyst who reads a legal code and '
    'finds scenarios that the code permits but that a reasonable person would find wrong."""\n'
)


@pytest.fixture()
def clone(tmp_path: Path) -> Path:
    src = tmp_path / "clone"
    (src / "loophole").mkdir(parents=True)
    (src / "loophole" / "prompts.py").write_text(PROMPT_MODULE)
    return src


def test_the_leak_check_fires_on_a_copied_run(leak: Any, clone: Path, tmp_path: Path) -> None:
    needles = leak.load_needles(clone)
    assert leak.control_hits(needles, clone) == len(needles) > 0
    copied = tmp_path / "calls.jsonl"
    copied.write_text('{"response": "an adversarial analyst who reads a legal code and finds it"}')
    clean = tmp_path / "candidates.json"
    clean.write_text('[{"scenario": "a tenant declares infra"}]')
    hits = leak.scan(needles, [copied, clean])
    assert hits[str(copied)]
    assert hits[str(clean)] == []


def test_the_leak_check_walks_a_round_directory(leak: Any, clone: Path, tmp_path: Path) -> None:
    rnd = tmp_path / "round-1"
    rnd.mkdir()
    (rnd / "summary.json").write_text("{}")
    (rnd / "calls.jsonl").write_text("reads a legal code and finds scenarios that the code permits")
    code = subprocess.run(
        [sys.executable, str(BENCH / "check_no_prompt_leak.py"), str(rnd)],
        env={"LOOPHOLE_SRC": str(clone), "PATH": "/usr/bin:/bin"},
        capture_output=True, text=True,
    )
    assert code.returncode == 1, code.stdout + code.stderr
    assert "LEAK" in code.stdout and "calls.jsonl" in code.stdout


def test_the_leak_check_refuses_to_run_when_its_control_does_not_fire(leak: Any, clone: Path) -> None:
    needles = leak.load_needles(clone) | {"a run of eight words the source never held"}
    with pytest.raises(SystemExit, match="CONTROL FAILED"):
        leak.require_control(needles, clone)


# 6. What a round writes down.


POINT_9 = {
    "target", "harness", "model_served", "model_calls", "wall_time_s", "list_price_usd",
    "counters", "candidates", "prompt_digests",
}


def test_the_summary_carries_point_nine(harness: Any, tmp_path: Path) -> None:
    calls = [
        {"role": "loophole_finder", "system_prompt_sha256": "a" * 64, "user_message_sha256": "b" * 64,
         "total_cost_usd": 0.05, "model_served": ["claude-sonnet-5"]},
        {"role": "judge", "system_prompt_sha256": "c" * 64, "user_message_sha256": "d" * 64,
         "total_cost_usd": 0.02, "model_served": ["claude-sonnet-5"]},
    ]
    summary = harness.build_summary(
        ticket="115", round_label="1", target={"path": "docs/adr/x.md", "commit": "f" * 40},
        calls=calls, wall_time_s=12.5, audits={}, verdicts=[], failures=[],
        extra={},
    )
    assert POINT_9 <= set(summary)
    assert summary["ticket"] == "115"
    assert summary["model_calls"] == 2
    assert summary["list_price_usd"] == pytest.approx(0.07)
    assert summary["model_served"] == ["claude-sonnet-5"]
    assert summary["clean"] is True
    assert summary["harness"]["sha256"] == harness.file_sha256(BENCH / "loophole_round.py")
    assert [d["role"] for d in summary["prompt_digests"]] == ["loophole_finder", "judge"]


def test_the_ticket_is_never_a_constant(harness: Any) -> None:
    text = (BENCH / "loophole_round.py").read_text()
    assert '"ticket": "07"' not in text


# 7. Nothing unlicensed lands inside the project tree.


def test_a_full_log_inside_the_tree_is_refused(harness: Any) -> None:
    with pytest.raises(harness.GuardError, match="outside the project tree"):
        harness.refuse_inside_tree(ROOT / "bench" / "full.jsonl", ROOT, "--full-log")


def test_a_full_log_outside_the_tree_is_allowed(harness: Any, tmp_path: Path) -> None:
    harness.refuse_inside_tree(tmp_path / "full.jsonl", ROOT, "--full-log")
