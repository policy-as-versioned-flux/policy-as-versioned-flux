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
from .canon import digest_of
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


# One row per metric: the skill name, the function under test, how its corpus is built, and the
# scorer. Walked by `_evaluate_all()` below and by `corpus_facts()`, so the corpus a permission
# is derived from is the same corpus the score was recorded on — two lists would drift.
_SPECS: tuple[tuple[str, Any, Any, Any], ...] = (
    (sc.SKILL, sc.classify, lambda d: sc.labelled_corpus(d / "signal-classify"), sc.scorer),
    (ej.SKILL, ej.judge, lambda d: ej.labelled_corpus(d / "evolution-judge"), ej.scorer),
    (cc.SKILL, cc.propose, lambda d: cc.labelled_corpus(d / "causal-claims"), cc.scorer),
    (cc.GRADE_SKILL, cc.propose, lambda d: cc.labelled_corpus(d / "causal-claims-grade"), cc.grade_scorer),
    (gl.SKILL, gl.propose, lambda d: gl.labelled_corpus(d / "gameplay-lens"), gl.scorer),
    (sg.SKILL, sg.generate_from_recipe_yaml, lambda d: sg.labelled_corpus(), sg.scorer),
    (eg.SKILL, eg.admit, lambda d: eg.labelled_corpus(), eg.scorer),
)

METRICS: tuple[str, ...] = tuple(spec[0] for spec in _SPECS)


def _evaluate_all(tmp_dir: Path) -> list[EvalResult]:
    """Every real skill's own honest `evaluate()` call, against a fixture repository built fresh
    in `tmp_dir` exactly the way each per-skill harness guard already builds its own — the same
    corpus, scored the same way, only actually recorded this time."""
    return [evaluate(skill, fn, build(tmp_dir), scorer=scorer) for skill, fn, build, scorer in _SPECS]


def fitted_models() -> dict[str, str]:
    """Which model version was FITTED on the corpora it is scored against, and under what corpus
    kind — `twin.model_permission`'s condition 10.

    One entry today: the incumbent heuristic. `twin/evolution_judge.py`'s `CORPUS_KIND` declares
    the kind, and its own comment defines the value: `harness-mechanism` while every corpus item
    is one the heuristic was fitted to, `held-out` once any item is not. Read from there rather
    than typed here, so the day a held-out corpus lands, this map changes with it and the
    condition lifts itself.
    """
    return {HEURISTIC_MODEL_VERSION: ej.CORPUS_KIND}


def corpus_facts(skill: str) -> dict[str, Any]:
    """What a model permission has to be derived from, measured off the corpus in the tree.

    Wayfinder ticket 05. Three facts, none of them typed by hand:

    - `corpus_digest` — item 2's comparison. A recorded score whose digest is not this one was
      scored on a corpus that has since moved, and it revokes the permission.
    - `baseline` — item 9's bar, the best constant answer this corpus admits
      (`twin.model_permission.frozen_field_baseline`).
    - `variance` — item 8's input: how many distinct values each field the scorer reads took.

    The incumbent supplies the reference answers, which is what grants the other fields while one
    is frozen. Its own score is returned as `reference_score`: a reference set that is not correct
    understates the baseline, so the caller sees how far it is from 1.000 rather than nothing.
    """
    from . import model_permission as mp

    for name, fn, build, scorer in _SPECS:
        if name != skill:
            continue
        with TemporaryDirectory() as tmp:
            corpus = build(Path(tmp))
            answers = [fn(item["input"]) for item in corpus]
            baseline = mp.frozen_field_baseline(answers, corpus, scorer)
            reference = sum(1 for a, i in zip(answers, corpus) if mp.scores_item(scorer, a, i["expected"]))
            return {
                "skill": skill,
                "corpus_digest": digest_of(corpus),
                "total": len(corpus),
                "baseline": baseline,
                "variance": mp.answer_variance(answers, baseline.reads),
                "reference_score": reference / len(corpus),
            }
    raise KeyError(f"no metric named {skill!r}; have {', '.join(METRICS)}")


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
    # Eco-system ticket 112: three outcomes. Not measurable is not a failure, so it does not fail
    # the run; it is printed as itself so nobody reads it as a pass.
    labels = {"pass": "PASS", "fail": "FAIL", "not-measurable": "NOT MEASURABLE"}
    for entry in entries:
        status = labels[entry["outcome"]]
        print(
            f"{status:<14}  {entry['skill']:<28} score={entry['score']:.3f}  threshold={entry['threshold']}"
            f"  items={entry['total']}  min_items={entry['min_items']}"
        )
    return 1 if any(entry["outcome"] == "fail" for entry in entries) else 0


if __name__ == "__main__":
    raise SystemExit(main())
