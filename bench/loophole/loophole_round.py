"""Drive one loophole round against a named norm document (ADR-0030).

This file is the estate's own harness. It contains no loophole source and no loophole prompt
text. It imports the upstream package from the path in LOOPHOLE_SRC, so the clone stays outside
the project tree (ADR-0030 point 1). The guards below are importable with no clone at all, which
is how `tests/test_loophole_round.py` holds them down.

Moved from `.scratch/laya-loophole/bench/loophole_round.py` by eco-system ticket 115. The round
itself runs as tickets 07 and 11 ran it. What changed is what fails the run:

* `--bare` can never reach `claude -p`, and the failure shape it produces is refused whatever
  flag produced it (point 6);
* the parse counters are checked against loophole's own parser before any model call, and a
  round with a parse failure, under-production, or a judge reply with no verdict exits 1
  (points 5 and 6);
* the prompt-leak check runs over the round's own files before the harness returns (point 7);
* the summary carries every field point 9 lists, and names its ticket from `--ticket`.

Two deliberate departures from loophole/main.py::_run_adversarial_loop, unchanged since ticket 07:

1. The legal code is supplied, not drafted. The Legislator never runs (point 4).
2. The Legislator never revises. Every case is judged against the same v1 text.

Exit codes: 0 clean round; 1 a round ran and is not clean (the summary says why); 2 a guard
refused before or during the round; 3 a negative control did not fire.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
LEAK_CHECK = HERE / "check_no_prompt_leak.py"

# The transport cannot carry these, but the published config sets them.
PUBLISHED_TEMPERATURES = {"loophole_finder": 0.9, "overreach_finder": 0.9, "judge": 0.3}
PUBLISHED_MODEL = "claude-sonnet-4-20250514"
PUBLISHED_MAX_TOKENS = 4096

# Flags that make `claude -p` skip the login it needs and still exit 0 (ADR-0030 point 6).
FORBIDDEN_FLAGS = ("--bare",)


class GuardError(RuntimeError):
    """A guard refused. The run stops here and never reads as a clean bill of health."""


# ---------------------------------------------------------------------------------------------
# The transport guard: what reaches `claude -p`, and what comes back.


def refuse_forbidden_flags(cmd: list[str]) -> list[str]:
    for arg in cmd:
        for flag in FORBIDDEN_FLAGS:
            if arg == flag or arg.startswith(flag + "="):
                raise GuardError(
                    f"{flag} may never reach claude -p: with no API key it fails at exit 0 and "
                    f"the round reads as 'the legal code appears robust' (ADR-0030 point 6)")
    return cmd


def claude_command(model: str, system: str) -> list[str]:
    """One `claude -p` call with no tools, no MCP, no session, and no repo context."""
    return refuse_forbidden_flags([
        "claude", "-p",
        "--safe-mode",
        "--model", model,
        "--system-prompt", system,
        "--output-format", "json",
        "--tools", "",
        "--strict-mcp-config",
        "--mcp-config", '{"mcpServers":{}}',
        "--disable-slash-commands",
        "--no-session-persistence",
        "--permission-prompts", "none",
        "--system-prompt-snapshot", "off",
    ])


def read_cli_result(role: str, returncode: int, stdout: str) -> tuple[str, dict[str, Any]]:
    """The response text and its measures, or a refusal.

    A `claude -p` failure can exit 0, report subtype "success", and put a human-readable error
    in `result`. Returning that string would yield zero scenarios and a false clean bill of
    health. The guard reads the failure shape, not the flag that caused it.
    """
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise GuardError(f"{role}: transport failed, rc={returncode}, reply is not JSON") from exc
    if not isinstance(payload, dict):
        raise GuardError(f"{role}: transport failed, rc={returncode}, reply is not an object")
    text = payload.get("result", "") or ""
    fields: dict[str, Any] = {
        "is_error": payload.get("is_error"),
        "stop_reason": payload.get("stop_reason"),
        "num_turns": payload.get("num_turns"),
        "total_cost_usd": payload.get("total_cost_usd"),
        "model_served": list((payload.get("modelUsage") or {}).keys()),
        "usage": (payload.get("usage") or {}).get("output_tokens"),
    }
    if returncode != 0:
        raise GuardError(f"{role}: transport failed, rc={returncode}")
    if payload.get("is_error"):
        raise GuardError(f"{role}: the CLI reported an error ({payload.get('stop_reason')}): "
                         f"{text[:200]!r}")
    return text, fields


def refuse_inside_tree(path: Path, root: Path, what: str) -> None:
    """ADR-0030 points 1 and 7: the clone and loophole's prompt text stay outside the tree."""
    resolved = path.resolve()
    if resolved == root.resolve() or root.resolve() in resolved.parents:
        raise GuardError(f"{what} must point outside the project tree ({root}): {path}")


# ---------------------------------------------------------------------------------------------
# The two counters, and the judge's missing verdict.

SCENARIO_OPEN = re.compile(r"<scenario>")
SCENARIO_PAIR = re.compile(
    r"<scenario>\s*<description>(.*?)</description>\s*"
    r"<explanation>(.*?)</explanation>\s*</scenario>",
    re.DOTALL,
)
# The upstream judge reads its verdict with this pattern and treats no match as "unresolvable".
VERDICT = re.compile(r"<verdict>\s*(.*?)\s*</verdict>", re.DOTALL)


def parse_audit(raw: str, parsed_count: int, requested: int) -> dict[str, int]:
    """Tell zero candidates apart from a failed parse."""
    opens = len(SCENARIO_OPEN.findall(raw))
    return {
        "requested_cases": requested,
        "scenario_open_tags": opens,
        "well_formed_scenarios": len(SCENARIO_PAIR.findall(raw)),
        "cases_parsed": parsed_count,
        # A scenario the model opened but the parser did not take.
        "parse_failures": max(0, opens - parsed_count),
        # The model produced fewer than asked, including a total format collapse with no tag.
        "under_production": max(0, requested - opens),
        "raw_chars": len(raw),
    }


def verdict_tag_present(raw: str) -> bool:
    m = VERDICT.search(raw)
    return m is not None and m.group(1).strip().lower() in {"resolvable", "unresolvable"}


def round_failures(audits: dict[str, dict[str, int]], verdicts: list[dict[str, Any]]) -> list[str]:
    """Every reason this round is not clean. An empty list is the only clean round."""
    failures: list[str] = []
    for role, audit in audits.items():
        if audit["parse_failures"]:
            failures.append(f"{role}: {audit['parse_failures']} parse failures")
        if audit["under_production"]:
            failures.append(f"{role}: under-production of {audit['under_production']}")
    for v in verdicts:
        if not v["verdict_tag_present"]:
            failures.append(f"judge: no <verdict> tag on {v['key']}, read upstream as unresolvable")
    return failures


# The five inputs ticket 07 fed the upstream parser, and what the counters must read on each.
# (parsed, parse_failures, under_production) at three requested cases.
COUNTER_CONTROLS: list[tuple[str, str, tuple[int, int, int]]] = [
    ("well-formed, 3 scenarios",
     "<scenario><description>d1</description><explanation>e1</explanation></scenario>" * 3,
     (3, 0, 0)),
    ("truncated: tag opened, never closed",
     "<scenario><description>d1</description><explanation>e1</explanation></scenario>"
     "<scenario><description>d2</description><explanation>e2",
     (1, 1, 1)),
    ("wrong inner tags (weak model)",
     "<scenario><desc>d1</desc><why>e1</why></scenario>" * 3,
     (0, 3, 0)),
    ("prose only, no tags at all",
     "Here are three loopholes: first, ... second, ... third, ...",
     (0, 0, 3)),
    ("markdown fence round the XML",
     "```xml\n<scenario><description>d1</description><explanation>e1</explanation></scenario>\n```",
     (1, 0, 2)),
]


def counter_control_failures(parse: Callable[[str], int]) -> list[str]:
    """Feed the control inputs to a parser; every counter must read what the table says."""
    failures = []
    for name, raw, expected in COUNTER_CONTROLS:
        a = parse_audit(raw, parse(raw), 3)
        got = (a["cases_parsed"], a["parse_failures"], a["under_production"])
        if got != expected:
            failures.append(f"{name}: (parsed, parse_failures, under_production) = {got}, "
                            f"expected {expected}")
    return failures


# ---------------------------------------------------------------------------------------------
# What a round writes down (ADR-0030 point 9).


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def build_summary(*, ticket: str, round_label: str, target: dict[str, Any],
                  calls: list[dict[str, Any]], wall_time_s: float,
                  audits: dict[str, dict[str, int]], verdicts: list[dict[str, Any]],
                  failures: list[str], extra: dict[str, Any]) -> dict[str, Any]:
    served = sorted({m for c in calls for m in c.get("model_served") or []})
    return {
        "ticket": ticket,
        "round": round_label,
        "at": datetime.now(timezone.utc).isoformat(),
        "clean": not failures,
        "failures": failures,
        "target": target,
        "harness": {
            "path": "bench/loophole/loophole_round.py",
            "sha256": file_sha256(Path(__file__)),
            "leak_check_sha256": file_sha256(LEAK_CHECK),
        },
        "model_served": served,
        "model_calls": len(calls),
        "wall_time_s": round(wall_time_s, 1),
        "list_price_usd": round(sum(c.get("total_cost_usd") or 0 for c in calls), 4),
        "counters": {
            "parse_failures": sum(a["parse_failures"] for a in audits.values()),
            "under_production": sum(a["under_production"] for a in audits.values()),
            "judge_missing_verdict": sum(1 for v in verdicts if not v["verdict_tag_present"]),
            "per_finder": audits,
        },
        "candidates": {
            "total": len(verdicts),
            "by_type": {t: sum(1 for v in verdicts if v.get("case_type") == t)
                        for t in sorted({str(v["case_type"]) for v in verdicts
                                         if v.get("case_type")})},
            "judge_resolvable": sum(1 for v in verdicts if v.get("judge_resolvable")),
            "file": "candidates.json",
        },
        "prompt_digests": [
            {"role": c["role"], "system_prompt_sha256": c["system_prompt_sha256"],
             "user_message_sha256": c["user_message_sha256"]}
            for c in calls
        ],
        **extra,
    }


def target_provenance(path: Path) -> dict[str, Any]:
    """The target's commit. A target with uncommitted changes has no commit to name."""
    folder = path.resolve().parent
    git = ["git", "-C", str(folder)]
    top = subprocess.run(git + ["rev-parse", "--show-toplevel"],
                         capture_output=True, text=True, check=True).stdout.strip()
    rel = str(path.resolve().relative_to(Path(top).resolve()))
    dirty = subprocess.run(git + ["status", "--porcelain", "--", str(path.resolve())],
                           capture_output=True, text=True, check=True).stdout.strip()
    if dirty:
        raise GuardError(f"the target has uncommitted changes, so no commit names its text: {rel}")
    head = subprocess.run(git + ["rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()
    last = subprocess.run(git + ["log", "-1", "--format=%H", "--", str(path.resolve())],
                          capture_output=True, text=True, check=True).stdout.strip()
    return {"path": rel, "commit": head, "last_changed_in": last,
            "sha256": file_sha256(path), "chars": len(path.read_text())}


# ---------------------------------------------------------------------------------------------
# The provider loophole's agents call.


class ClaudeCliProvider:
    """LLMProvider over `claude -p`. One process per call, no shared context.

    Implements call() because agents/judge.py reaches past BaseAgent.run and calls
    self.llm.call directly.
    """

    def __init__(self, role: str, model: str, log_path: Path, cwd: Path,
                 full_log: Path | None = None, timeout: int = 900):
        self.role = role
        self.full_log = full_log
        self.model = model
        self.max_tokens = PUBLISHED_MAX_TOKENS  # declared for the Protocol; not enforced
        self.log_path = log_path
        self.cwd = cwd
        self.timeout = timeout

    def call(self, system: str, user_message: str, temperature: float = 0.5) -> str:
        cmd = claude_command(self.model, system)
        started = time.time()
        proc = subprocess.run(cmd, input=user_message, capture_output=True, text=True,
                              timeout=self.timeout, cwd=str(self.cwd))
        record: dict[str, Any] = {
            "role": self.role,
            "requested_temperature": temperature,
            "temperature_carried": False,
            "model_requested": self.model,
            "elapsed_s": round(time.time() - started, 2),
            "returncode": proc.returncode,
            # loophole carries no licence, so its prompt text may not be stored in the project
            # tree (point 7). The digest and the length make the run verifiable against a
            # clone without reproducing the text.
            "system_prompt_sha256": _digest(system),
            "system_prompt_chars": len(system),
            "user_message_sha256": _digest(user_message),
            "user_message_chars": len(user_message),
            "stderr": proc.stderr[-4000:],
            "at": datetime.now(timezone.utc).isoformat(),
        }
        error: GuardError | None = None
        text = ""
        try:
            text, fields = read_cli_result(self.role, proc.returncode, proc.stdout)
            record.update(fields)
            record["transport_ok"] = True
        except GuardError as exc:
            error = exc
            record["transport_ok"] = False
            record["raw_stdout"] = proc.stdout[-4000:]
        record["response"] = text
        with self.log_path.open("a") as fh:
            fh.write(json.dumps(record) + "\n")
        if self.full_log is not None:
            with self.full_log.open("a") as fh:
                fh.write(json.dumps({**record, "system_prompt": system,
                                     "user_message": user_message}) + "\n")
        if error is not None:
            raise error
        return text

    def call_messages(self, system: str, messages: list[dict[str, Any]],
                      temperature: float = 0.5) -> str:
        joined = "\n\n".join(m.get("content", "") for m in messages)
        return self.call(system, joined, temperature=temperature)


def _tail_raw(log_path: Path) -> str:
    """Return the newest logged response, or '' when nothing is logged yet."""
    if not log_path.exists():
        return ""
    lines = [ln for ln in log_path.read_text().splitlines() if ln.strip()]
    return str(json.loads(lines[-1]).get("response", "")) if lines else ""


def _git_head(path: str) -> str:
    try:
        return subprocess.run(["git", "-C", path, "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _load_leak_check() -> Any:
    import importlib.util
    spec = importlib.util.spec_from_file_location("check_no_prompt_leak", LEAK_CHECK)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--code", help="the norm document, committed, as prose")
    ap.add_argument("--principles", help="the estate's own principles the document serves")
    ap.add_argument("--domain")
    ap.add_argument("--out", help="the round's directory")
    ap.add_argument("--ticket", help="the ticket this round is run under")
    ap.add_argument("--round", dest="round_label", help="which of the three rounds, 1 to 3")
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--cases-per-agent", type=int, default=3)
    ap.add_argument("--full-log", default=None,
                    help="optional unredacted log; must point OUTSIDE the project tree, "
                         "because it holds loophole's prompt text verbatim")
    ap.add_argument("--controls-only", action="store_true",
                    help="run both negative controls and stop; no model call")
    args = ap.parse_args(argv)

    src = os.environ.get("LOOPHOLE_SRC")
    if not src:
        print("set LOOPHOLE_SRC to the loophole clone outside the project tree", file=sys.stderr)
        return 2
    project = HERE.parents[1]
    try:
        refuse_inside_tree(Path(src), project, "LOOPHOLE_SRC")
        if args.full_log:
            refuse_inside_tree(Path(args.full_log), project, "--full-log")
    except GuardError as exc:
        print(f"GUARD: {exc}", file=sys.stderr)
        return 2

    sys.path.insert(0, src)
    from loophole.agents.judge import Judge
    from loophole.agents.loophole_finder import LoopholeFinder, _parse_scenarios
    from loophole.agents.overreach_finder import OverreachFinder
    from loophole.models import LegalCode, SessionState

    # Control 1: the counters fire on loophole's own parser, before any call is spent.
    nc_state = SessionState(session_id="nc", domain="nc", moral_principles="nc",
                            current_code=LegalCode(version=1, text="nc"))
    control = counter_control_failures(lambda raw: len(_parse_scenarios(raw, nc_state)))
    if control:
        print("CONTROL FAILED: the counters do not fire on loophole's parser", file=sys.stderr)
        for line in control:
            print(f"  {line}", file=sys.stderr)
        return 3
    print(f"counter control: {len(COUNTER_CONTROLS)}/{len(COUNTER_CONTROLS)} inputs read as "
          f"expected on loophole's own parser", flush=True)

    # Control 2: the prompt-leak detector fires on the prompt module itself.
    leak = _load_leak_check()
    needles = leak.load_needles(Path(src))
    control_hits = leak.require_control(needles, Path(src))
    print(f"leak control: {control_hits}/{len(needles)} runs found in the source itself",
          flush=True)
    if args.controls_only:
        return 0

    missing = [f"--{n.replace('_', '-')}" for n in
               ("code", "principles", "domain", "out", "ticket", "round_label")
               if not getattr(args, n)]
    if missing:
        print(f"a round needs {', '.join(missing)}", file=sys.stderr)
        return 2
    try:
        target = target_provenance(Path(args.code))
    except GuardError as exc:
        print(f"GUARD: {exc}", file=sys.stderr)
        return 2

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    log_path = out / "calls.jsonl"
    if log_path.exists():
        print(f"GUARD: {log_path} exists; a round writes into an empty directory", file=sys.stderr)
        return 2

    code_text = Path(args.code).read_text()
    principles = Path(args.principles).read_text().strip()
    state = SessionState(
        session_id=f"round-{args.round_label}-{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        domain=args.domain,
        moral_principles=principles,
        current_code=LegalCode(version=1, text=code_text),
    )
    state.code_history.append(state.current_code)
    state.current_round = 1

    # claude -p runs in an empty directory outside the tree, so nothing in the repo reaches the
    # prompt. --safe-mode already disables CLAUDE.md, skills, hooks and MCP.
    run_cwd = Path(tempfile.mkdtemp(prefix="loophole-cwd-"))
    full_log = Path(args.full_log) if args.full_log else None

    def provider(role: str) -> ClaudeCliProvider:
        return ClaudeCliProvider(role, args.model, log_path, run_cwd, full_log)

    finder = LoopholeFinder(provider("loophole_finder"),
                            temperature=PUBLISHED_TEMPERATURES["loophole_finder"],
                            cases_per_agent=args.cases_per_agent)
    overreach = OverreachFinder(provider("overreach_finder"),
                                temperature=PUBLISHED_TEMPERATURES["overreach_finder"],
                                cases_per_agent=args.cases_per_agent)
    judge = Judge(provider("judge"), temperature=PUBLISHED_TEMPERATURES["judge"])

    started = time.time()
    audits: dict[str, dict[str, int]] = {}
    verdicts: list[dict[str, Any]] = []
    try:
        print("phase 1: loophole finder", flush=True)
        loopholes = finder.find(state)
        audits["loophole_finder"] = parse_audit(_tail_raw(log_path), len(loopholes),
                                                args.cases_per_agent)
        print(f"  parsed {len(loopholes)} | {audits['loophole_finder']}", flush=True)

        print("phase 1: overreach finder", flush=True)
        overreaches = overreach.find(state)
        audits["overreach_finder"] = parse_audit(_tail_raw(log_path), len(overreaches),
                                                 args.cases_per_agent)
        print(f"  parsed {len(overreaches)} | {audits['overreach_finder']}", flush=True)

        all_cases = loopholes + overreaches
        state.cases.extend(all_cases)
        print(f"phase 2: judge, {len(all_cases)} cases", flush=True)
        for idx, case in enumerate(all_cases, start=1):
            result = judge.evaluate(state, case)
            raw = _tail_raw(log_path)
            verdicts.append({
                "key": f"{case.case_type.value}-{idx}",
                "upstream_case_id": case.id,
                "case_type": case.case_type.value,
                "scenario": case.scenario,
                "explanation": case.explanation,
                "judge_resolvable": result.resolvable,
                "judge_reasoning": result.reasoning,
                "judge_resolution_summary": result.resolution_summary,
                "judge_conflict_explanation": result.conflict_explanation,
                "judge_proposed_revision": result.proposed_revision,
                "verdict_tag_present": verdict_tag_present(raw),
                "reasoning_tag_present": "<reasoning>" in raw,
            })
            print(f"  {idx}/{len(all_cases)} {case.case_type.value} "
                  f"resolvable={result.resolvable} verdict_tag={verdict_tag_present(raw)}",
                  flush=True)
    except GuardError as exc:
        print(f"GUARD: {exc}", file=sys.stderr)
        return 2
    wall = time.time() - started

    (out / "candidates.json").write_text(json.dumps(verdicts, indent=2) + "\n")
    failures = round_failures(audits, verdicts)

    # Point 7: the round's own files are checked before the harness returns.
    round_files = [log_path, out / "candidates.json"]
    hits = leak.scan(needles, round_files)
    leaked = {Path(p).name: len(h) for p, h in hits.items()}
    if any(leaked.values()):
        failures.append(f"prompt leak: {leaked}")

    calls = [json.loads(ln) for ln in log_path.read_text().splitlines() if ln.strip()]
    summary = build_summary(
        ticket=args.ticket, round_label=args.round_label, target=target, calls=calls,
        wall_time_s=wall, audits=audits, verdicts=verdicts, failures=failures,
        extra={
            "session_id": state.session_id,
            "domain": args.domain,
            "principles": {"path": args.principles, "sha256": file_sha256(Path(args.principles))},
            "loophole_src_commit": _git_head(src),
            "model_requested": args.model,
            "published_model": PUBLISHED_MODEL,
            "cases_per_agent": args.cases_per_agent,
            "counter_control": f"{len(COUNTER_CONTROLS)}/{len(COUNTER_CONTROLS)}",
            "leak_check": {"distinct_runs": len(needles), "control_hits": control_hits,
                           "leaked_runs": leaked},
            "limitations": [
                "claude -p carries no temperature flag; the published 0.9 finder / 0.3 judge "
                "split is lost (config.yaml:24-28).",
                "claude -p carries no max_tokens flag; the published 4096 cap is not applied.",
                f"the published config names {PUBLISHED_MODEL}; this run asked for "
                f"'{args.model}', and model_served says what answered.",
                "the Legislator never ran: the code is supplied and never revised.",
            ],
        },
    )
    (out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    if leak.scan(needles, [out / "summary.json"])[str(out / "summary.json")]:
        print("prompt leak in summary.json", file=sys.stderr)
        return 1
    print(json.dumps({"clean": summary["clean"], "calls": summary["model_calls"],
                      "wall_time_s": summary["wall_time_s"],
                      "list_price_usd": summary["list_price_usd"],
                      "candidates": summary["candidates"]["total"]}), flush=True)
    for f in failures:
        print(f"NOT CLEAN: {f}", file=sys.stderr)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
