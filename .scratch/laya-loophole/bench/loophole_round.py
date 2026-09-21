"""Ticket 07: drive one loophole round against a named norm document.

This file is the estate's own harness. It contains no loophole source and no
loophole prompt text. It imports the upstream package from a path given by
LOOPHOLE_SRC, so the clone stays outside the project tree (map call 5).

Two deliberate departures from loophole/main.py::_run_adversarial_loop, each
recorded in the ticket answer:

1. The legal code is supplied, not drafted. The Legislator never runs, so the
   target document is the estate's real ADR and not a model's paraphrase of it.
2. The Legislator never revises. Every case is judged against the same v1 text,
   so the six verdicts are comparable and the norm document is not mutated.

Everything else runs as published: the same agent classes, the same prompts,
the same parser, the same temperatures where the transport can carry them.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

LOOPHOLE_SRC = os.environ.get("LOOPHOLE_SRC")
if not LOOPHOLE_SRC:
    sys.exit("set LOOPHOLE_SRC to the loophole clone outside the project tree")
sys.path.insert(0, LOOPHOLE_SRC)

from loophole.agents.judge import Judge  # noqa: E402
from loophole.agents.loophole_finder import LoopholeFinder  # noqa: E402
from loophole.agents.overreach_finder import OverreachFinder  # noqa: E402
from loophole.models import LegalCode, SessionState  # noqa: E402

# The transport cannot carry these, but the published config sets them.
PUBLISHED_TEMPERATURES = {"loophole_finder": 0.9, "overreach_finder": 0.9, "judge": 0.3}
PUBLISHED_MODEL = "claude-sonnet-4-20250514"
PUBLISHED_MAX_TOKENS = 4096


class ClaudeCliProvider:
    """LLMProvider over `claude -p`. One process per call, no shared context.

    Implements call() because agents/judge.py reaches past BaseAgent.run and
    calls self.llm.call directly.
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
        cmd = [
            "claude", "-p",
            "--safe-mode",
            "--model", self.model,
            "--system-prompt", system,
            "--output-format", "json",
            "--tools", "",
            "--strict-mcp-config",
            "--mcp-config", '{"mcpServers":{}}',
            "--disable-slash-commands",
            "--no-session-persistence",
            "--permission-prompts", "none",
            "--system-prompt-snapshot", "off",
        ]
        started = time.time()
        proc = subprocess.run(
            cmd, input=user_message, capture_output=True, text=True,
            timeout=self.timeout, cwd=str(self.cwd),
        )
        elapsed = time.time() - started

        record = {
            "role": self.role,
            "requested_temperature": temperature,
            "temperature_carried": False,
            "model_requested": self.model,
            "elapsed_s": round(elapsed, 2),
            "returncode": proc.returncode,
            # loophole carries no licence, so its prompt text may not be stored
            # in the project tree (map call 5). The digest and the length make
            # the run verifiable against a clone without reproducing the text.
            "system_prompt_sha256": _digest(system),
            "system_prompt_chars": len(system),
            "user_message_sha256": _digest(user_message),
            "user_message_chars": len(user_message),
            "stderr": proc.stderr[-4000:],
            "at": datetime.now(timezone.utc).isoformat(),
        }
        text = ""
        try:
            payload = json.loads(proc.stdout)
            text = payload.get("result", "") or ""
            record["is_error"] = payload.get("is_error")
            record["stop_reason"] = payload.get("stop_reason")
            record["num_turns"] = payload.get("num_turns")
            record["total_cost_usd"] = payload.get("total_cost_usd")
            record["model_served"] = list(payload.get("modelUsage", {}).keys())
            record["usage"] = payload.get("usage", {}).get("output_tokens")
            record["transport_ok"] = True
        except json.JSONDecodeError:
            record["transport_ok"] = False
            record["raw_stdout"] = proc.stdout[-4000:]
        record["response"] = text
        with self.log_path.open("a") as fh:
            fh.write(json.dumps(record) + "\n")
        if self.full_log is not None:
            with self.full_log.open("a") as fh:
                fh.write(json.dumps(
                    {**record, "system_prompt": system,
                     "user_message": user_message}) + "\n")
        # A `claude -p` failure exits 0, reports subtype "success", and puts a
        # human-readable error string in `result`. Returning that string would
        # yield zero scenarios and a false clean bill of health, which is the
        # exact defect the map's call 6 names. Refuse instead.
        if not record.get("transport_ok") or proc.returncode != 0:
            raise RuntimeError(f"{self.role}: transport failed, rc={proc.returncode}")
        if record.get("is_error"):
            raise RuntimeError(
                f"{self.role}: the CLI reported an error "
                f"({record.get('stop_reason')}): {text[:200]!r}"
            )
        return text

    def call_messages(self, system: str, messages: list[dict], temperature: float = 0.5) -> str:
        joined = "\n\n".join(m.get("content", "") for m in messages)
        return self.call(system, joined, temperature=temperature)


SCENARIO_OPEN = re.compile(r"<scenario>")
SCENARIO_PAIR = re.compile(
    r"<scenario>\s*<description>(.*?)</description>\s*"
    r"<explanation>(.*?)</explanation>\s*</scenario>",
    re.DOTALL,
)


def parse_audit(raw: str, parsed_count: int, requested: int) -> dict:
    """Ticket 07 item 6: tell zero candidates apart from a failed parse."""
    opens = len(SCENARIO_OPEN.findall(raw))
    pairs = len(SCENARIO_PAIR.findall(raw))
    return {
        "requested_cases": requested,
        "scenario_open_tags": opens,
        "well_formed_scenarios": pairs,
        "cases_parsed": parsed_count,
        # A scenario the model opened but the parser did not take.
        "parse_failures": max(0, opens - parsed_count),
        # The model simply produced fewer than asked. Not a parse failure.
        "under_production": max(0, requested - opens),
        "raw_chars": len(raw),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--code", required=True, help="the norm document, as prose")
    ap.add_argument("--principles", required=True)
    ap.add_argument("--domain", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--cases-per-agent", type=int, default=3)
    ap.add_argument("--full-log", default=None,
                    help="optional unredacted log. Point it OUTSIDE the project "
                         "tree: it holds loophole's prompt text verbatim.")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    log_path = out / "calls.jsonl"

    code_text = Path(args.code).read_text()
    principles = Path(args.principles).read_text().strip()

    state = SessionState(
        session_id=f"cage-ladder-{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        domain=args.domain,
        moral_principles=principles,
        current_code=LegalCode(version=1, text=code_text),
    )
    state.code_history.append(state.current_code)
    state.current_round = 1

    # claude -p runs in a clean directory so nothing in the repo reaches the
    # prompt. --safe-mode already disables CLAUDE.md, skills, hooks and MCP.
    run_cwd = out / "cwd"
    run_cwd.mkdir(exist_ok=True)

    full_log = Path(args.full_log) if args.full_log else None

    def provider(role: str) -> ClaudeCliProvider:
        return ClaudeCliProvider(role, args.model, log_path, run_cwd, full_log)

    finder = LoopholeFinder(
        provider("loophole_finder"),
        temperature=PUBLISHED_TEMPERATURES["loophole_finder"],
        cases_per_agent=args.cases_per_agent,
    )
    overreach = OverreachFinder(
        provider("overreach_finder"),
        temperature=PUBLISHED_TEMPERATURES["overreach_finder"],
        cases_per_agent=args.cases_per_agent,
    )
    judge = Judge(provider("judge"), temperature=PUBLISHED_TEMPERATURES["judge"])

    audits = {}
    calls_made = 0

    print("phase 1: loophole finder", flush=True)
    loopholes = finder.find(state)
    calls_made += 1
    audits["loophole_finder"] = parse_audit(
        _tail_raw(log_path), len(loopholes), args.cases_per_agent
    )
    print(f"  parsed {len(loopholes)} | {audits['loophole_finder']}", flush=True)

    print("phase 1: overreach finder", flush=True)
    overreaches = overreach.find(state)
    calls_made += 1
    audits["overreach_finder"] = parse_audit(
        _tail_raw(log_path), len(overreaches), args.cases_per_agent
    )
    print(f"  parsed {len(overreaches)} | {audits['overreach_finder']}", flush=True)

    all_cases = loopholes + overreaches
    for case in all_cases:
        state.cases.append(case)

    print(f"phase 2: judge, {len(all_cases)} cases", flush=True)
    verdicts = []
    for idx, case in enumerate(all_cases, start=1):
        result = judge.evaluate(state, case)
        calls_made += 1
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
            # Judge parse audit: a missing <verdict> tag silently reads
            # "unresolvable" at agents/judge.py:63.
            "verdict_tag_present": "<verdict>" in raw,
            "reasoning_tag_present": "<reasoning>" in raw,
        })
        print(f"  {idx}/{len(all_cases)} {case.case_type.value} "
              f"resolvable={result.resolvable} "
              f"verdict_tag={'<verdict>' in raw}", flush=True)

    judge_parse_failures = sum(1 for v in verdicts if not v["verdict_tag_present"])

    summary = {
        "ticket": "07",
        "at": datetime.now(timezone.utc).isoformat(),
        "session_id": state.session_id,
        "domain": args.domain,
        "code_file": args.code,
        "code_chars": len(code_text),
        "code_sha256": _sha256(args.code),
        "principles_file": args.principles,
        "principles_sha256": _sha256(args.principles),
        "loophole_src_commit": _git_head(LOOPHOLE_SRC),
        "model_requested": args.model,
        "published_model": PUBLISHED_MODEL,
        "cases_per_agent": args.cases_per_agent,
        "model_calls": calls_made,
        "candidates": {
            "loophole": len(loopholes),
            "overreach": len(overreaches),
            "total": len(all_cases),
        },
        "parse_audit": audits,
        "judge_parse_failures": judge_parse_failures,
        "limitations": [
            "claude -p carries no temperature flag; the published 0.9 finder / "
            "0.3 judge split is lost (config.yaml:24-28).",
            "claude -p carries no max_tokens flag; the published 4096 cap is not applied.",
            f"the published config names {PUBLISHED_MODEL}; this run asked for "
            f"'{args.model}' and the harness served a newer checkpoint.",
            "the Legislator never ran: the code is supplied and never revised.",
        ],
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    (out / "candidates.json").write_text(json.dumps(verdicts, indent=2))
    print(json.dumps(summary["candidates"]), flush=True)
    print(f"parse failures: finders="
          f"{sum(a['parse_failures'] for a in audits.values())} "
          f"judge={judge_parse_failures}", flush=True)
    return 0


def _tail_raw(log_path: Path) -> str:
    """Return the newest logged response, or '' when nothing is logged yet."""
    if not log_path.exists():
        return ""
    lines = [ln for ln in log_path.read_text().splitlines() if ln.strip()]
    if not lines:
        return ""
    return json.loads(lines[-1]).get("response", "")


def _digest(text: str) -> str:
    import hashlib
    return hashlib.sha256(text.encode()).hexdigest()


def _sha256(path: str) -> str:
    import hashlib
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _git_head(path: str) -> str:
    try:
        return subprocess.run(
            ["git", "-C", path, "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except Exception:
        return "unknown"


if __name__ == "__main__":
    raise SystemExit(main())
