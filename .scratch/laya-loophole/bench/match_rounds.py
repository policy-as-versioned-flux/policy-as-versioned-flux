"""Ticket 11: a blind, repeated matcher over two rounds of loophole candidates.

The ticket's match test is "same clause for the same reason, not the same
words". That is a judgement. This script does not replace the assistant's own
judgement; it measures whether an independent reader, given the candidates
anonymised and shuffled, reaches the same matching, and whether that reader
reaches it twice.

Design notes:

* Labels are stripped and re-issued as A1..An / B1..Bn, and the order is
  shuffled per repeat from a fixed seed, so neither list position nor the
  original candidate key can carry the answer.
* Each repeat is an independent `claude -p` call. Three repeats give an
  agreement count, so a matching every repeat produces is separable from one a
  single draw produced. The matcher is the same non-deterministic instrument
  the round itself used, so it is reported with its own stability, never as a
  bare number.
* The prompt is this file's own text. No loophole prompt is used or stored.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SYSTEM = (
    "You compare two independent lists of attacks on the same policy document. "
    "Each attack names a scenario and an explanation. Two attacks MATCH only "
    "when they attack the same clause of the document FOR THE SAME REASON. "
    "Identical wording is not a match. A different route to the same defect is "
    "a match. The same clause attacked for a different reason is NOT a match: "
    "report it separately as a clause-only pair. Be strict. Most pairs match "
    "nothing. Reply with JSON only, no prose and no code fence."
)

SCHEMA = """Reply with exactly this JSON shape:
{
  "matches": [{"a": "A1", "b": "B3", "clause": "<the clause both attack>", "reason": "<the shared reason, one line>"}],
  "clause_only": [{"a": "A2", "b": "B5", "clause": "<the shared clause>", "why_not": "<how the reasons differ, one line>"}]
}
A candidate may appear at most once in "matches"."""


def load(path: Path) -> list[dict]:
    return json.loads(path.read_text())


def render(tag: str, items: list[dict], order: list[int]) -> tuple[str, dict]:
    lines, mapping = [], {}
    for n, idx in enumerate(order, start=1):
        label = f"{tag}{n}"
        mapping[label] = items[idx]["key"]
        lines.append(
            f"### {label}\nScenario: {items[idx]['scenario'].strip()}\n"
            f"Explanation: {items[idx]['explanation'].strip()}\n"
        )
    return "\n".join(lines), mapping


def call(system: str, user: str, cwd: Path, model: str, timeout: int = 900) -> dict:
    cmd = [
        "claude", "-p", "--safe-mode", "--model", model,
        "--system-prompt", system, "--output-format", "json",
        "--tools", "", "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
        "--disable-slash-commands", "--no-session-persistence",
        "--permission-prompts", "none", "--system-prompt-snapshot", "off",
    ]
    started = time.time()
    proc = subprocess.run(cmd, input=user, capture_output=True, text=True,
                          timeout=timeout, cwd=str(cwd))
    payload = json.loads(proc.stdout)
    if payload.get("is_error") or proc.returncode != 0:
        raise RuntimeError(f"transport failed rc={proc.returncode}: {payload.get('result')!r}")
    return {
        "result": payload.get("result", ""),
        "elapsed_s": round(time.time() - started, 2),
        "total_cost_usd": payload.get("total_cost_usd"),
        "model_served": list(payload.get("modelUsage", {}).keys()),
        "output_tokens": payload.get("usage", {}).get("output_tokens"),
    }


def parse_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("no JSON object in the reply")
    return json.loads(m.group(0))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True, help="round A candidates.json")
    ap.add_argument("--b", required=True, help="round B candidates.json")
    ap.add_argument("--a-name", required=True)
    ap.add_argument("--b-name", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--model", default="sonnet")
    args = ap.parse_args()

    a_items, b_items = load(Path(args.a)), load(Path(args.b))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    cwd = out.parent / "cwd"
    cwd.mkdir(parents=True, exist_ok=True)

    rng = random.Random(args.seed)
    repeats, cost = [], 0.0
    for r in range(args.repeats):
        a_order = list(range(len(a_items)))
        b_order = list(range(len(b_items)))
        rng.shuffle(a_order)
        rng.shuffle(b_order)
        a_text, a_map = render("A", a_items, a_order)
        b_text, b_map = render("B", b_items, b_order)
        user = (f"# List A\n\n{a_text}\n\n# List B\n\n{b_text}\n\n{SCHEMA}")
        res = call(SYSTEM, user, cwd, args.model)
        cost += res["total_cost_usd"] or 0.0
        parsed = parse_json(res["result"])
        # Translate the anonymous labels back to the real candidate keys.
        named = {
            "matches": [
                {**m, "a_key": a_map.get(m.get("a")), "b_key": b_map.get(m.get("b"))}
                for m in parsed.get("matches", [])
            ],
            "clause_only": [
                {**m, "a_key": a_map.get(m.get("a")), "b_key": b_map.get(m.get("b"))}
                for m in parsed.get("clause_only", [])
            ],
        }
        repeats.append({"repeat": r + 1, "a_map": a_map, "b_map": b_map,
                        "raw": res["result"], "named": named,
                        "elapsed_s": res["elapsed_s"],
                        "total_cost_usd": res["total_cost_usd"],
                        "model_served": res["model_served"]})
        pairs = {(m["a_key"], m["b_key"]) for m in named["matches"]}
        print(f"repeat {r+1}: {len(pairs)} matches "
              f"{sorted(pairs)}", flush=True)

    def tally(field: str) -> dict:
        counts: dict[str, int] = {}
        for rep in repeats:
            for m in rep["named"][field]:
                key = f"{m['a_key']} ~ {m['b_key']}"
                counts[key] = counts.get(key, 0) + 1
        return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))

    summary = {
        "ticket": "11",
        "at": datetime.now(timezone.utc).isoformat(),
        "a_round": args.a_name,
        "b_round": args.b_name,
        "repeats": args.repeats,
        "seed": args.seed,
        "model_requested": args.model,
        "match_counts": tally("matches"),
        "clause_only_counts": tally("clause_only"),
        "unanimous_matches": [k for k, v in tally("matches").items() if v == args.repeats],
        "split_matches": [k for k, v in tally("matches").items() if 0 < v < args.repeats],
        "total_cost_usd": round(cost, 6),
    }
    out.write_text(json.dumps({"summary": summary, "repeats": repeats}, indent=2))
    print(json.dumps(summary, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
