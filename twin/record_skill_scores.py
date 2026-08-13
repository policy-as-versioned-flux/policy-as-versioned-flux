"""Actually running the seam-3 harness against the six real skills, for real (build ticket 56).

Build ticket 42's `twin/skills.py` built `evaluate()`/`record_score()`; build tickets 43-49 built
the six real skills; `twin/invariants/harness.py`'s per-skill guards already call `evaluate()`
against each one's own real labelled corpus on every CI run. None of that ever called
`record_score()` against the real, committed `twin/skill-scores.jsonl` — every existing call site
(`tests/test_skills.py`, `tests/test_causal_claims.py`, the harness guards themselves) records
into a throwaway `tmp_path` log or does not record at all. Build ticket 56's coherence audit found
the score-over-time log this module exists to keep either missing or empty: the harness had been
built and unit-tested against a fixture skill, never actually run and recorded for the real
skills it exists to monitor.

`run()` is that run, made reproducible rather than a one-off: it evaluates each of the six real
skills — plus `causal-claims`' second, separately-registered grade-accuracy metric
(`twin/skill-thresholds.yaml`'s own `causal-claims-grade-accuracy` entry) — against its own real
corpus, honestly (the skill's real function, never the degraded stand-in the harness guards use
to prove a threshold gates something), and appends one score-over-time entry per skill via
`record_score()`. Re-running it later — after a real model swap, on a schedule — appends a fresh,
genuinely-computed entry rather than a hand-typed line.

`ponytail:` no `bin/twin` subcommand — the same reasoning `twin/ingest.py` (build ticket 53) and
`twin/market_signals.py` (build ticket 59) already give for their own unattended pipelines: this
is a standalone, re-runnable script with its own `main()`, exercised at seam 2, not a thing a
model repository gives a CLI invocation something to point `--repo` at.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from . import TOOL_VERSION
from . import causal_claims as cc
from . import ethics_gate as eg
from . import evolution_judge as ej
from . import gameplay_lens as gl
from . import signal_classify as sc
from . import substrate_generator as sg
from .skills import EvalResult, evaluate, record_score

# The six real skills are heuristic stand-ins, not live model calls — every one of their own
# module docstrings says so. Versioned to the tool rather than to a model provider's name, so a
# later swap to a real model call is a genuinely different tag `detect_regression()` can compare
# against, not a same-version re-run.
HEURISTIC_MODEL_VERSION = f"heuristic-{TOOL_VERSION}"


def _evaluate_all(tmp_dir: Path) -> list[EvalResult]:
    """Every real skill's own honest `evaluate()` call, against a fixture repository built fresh
    in `tmp_dir` exactly the way each per-skill harness guard already builds its own — the same
    corpus, scored the same way, only actually recorded this time."""
    return [
        evaluate(sc.SKILL, sc.classify, sc.labelled_corpus(tmp_dir / "signal-classify"), scorer=sc.scorer),
        evaluate(ej.SKILL, ej.judge, ej.labelled_corpus(tmp_dir / "evolution-judge"), scorer=ej.scorer),
        evaluate(cc.SKILL, cc.propose, cc.labelled_corpus(tmp_dir / "causal-claims"), scorer=cc.scorer),
        evaluate(
            cc.GRADE_SKILL, cc.propose, cc.labelled_corpus(tmp_dir / "causal-claims-grade"), scorer=cc.grade_scorer
        ),
        evaluate(gl.SKILL, gl.propose, gl.labelled_corpus(tmp_dir / "gameplay-lens"), scorer=gl.scorer),
        evaluate(sg.SKILL, sg.generate_from_recipe_yaml, sg.labelled_corpus(), scorer=sg.scorer),
        evaluate(eg.SKILL, eg.admit, eg.labelled_corpus(), scorer=eg.scorer),
    ]


def run(
    recorded_at: str, model_version: str = HEURISTIC_MODEL_VERSION, path: Path | None = None
) -> list[dict[str, Any]]:
    """Evaluate every real skill against its real corpus and append one score-over-time entry
    each. `recorded_at` is supplied by the caller — `record_score`'s own discipline — never read
    from the clock inside this function."""
    with TemporaryDirectory() as tmp:
        results = _evaluate_all(Path(tmp))
    return [record_score(result, model_version, recorded_at, path=path) for result in results]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-version", default=HEURISTIC_MODEL_VERSION)
    parser.add_argument("--at", default=None, help="ISO 8601 UTC timestamp; defaults to the current wall clock")
    args = parser.parse_args(argv)
    recorded_at = args.at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    entries = run(recorded_at, args.model_version)
    for entry in entries:
        status = "PASS" if entry["passed"] else "FAIL"
        print(f"{status}  {entry['skill']:<28} score={entry['score']:.3f}  threshold={entry['threshold']}")
    return 0 if all(entry["passed"] for entry in entries) else 1


if __name__ == "__main__":
    raise SystemExit(main())
