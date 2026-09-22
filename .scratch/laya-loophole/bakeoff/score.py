#!/usr/bin/env python3
"""Step 3 of the bake-off: score Laya's predictions through the unmodified twin harness.

Map ticket 04 (.scratch/laya-loophole/issues/04-the-bake-off-laya-against-the-six-heuristics.md).

  PYTHONPATH=. .venv/bin/python .scratch/laya-loophole/bakeoff/score.py
  PYTHONPATH=. .venv/bin/python .scratch/laya-loophole/bakeoff/score.py --record   # item 6

THE HARNESS IS NOT TOUCHED (item 2). `twin.skills.evaluate()` is called with each skill's own
`SKILL` name, its own `scorer`, and its own `labelled_corpus()`, exactly as
`twin/record_skill_scores.py` calls them for the heuristic. The only thing that differs is the
callable: instead of the heuristic function, `_replay()` returns a closure that looks the answer
up by corpus position from `predictions.json`. `evaluate()` cannot tell the difference, which is
the point -- a bake-off that needed a harness change would not be comparing like with like.

THE SAME CORPUS DIGEST (item 3). Every corpus is rebuilt here and its digest asserted against the
digest `dump_corpora.py` recorded and `run_laya.py` carried through. A mismatch aborts. A Laya row
and a `heuristic-0.1.0` row that do not share a digest are two different measurements wearing the
same skill name.

WHAT IS REPORTED BESIDE EVERY SCORE, AND WHY.

  95% lower bound (item 10). Clopper-Pearson, exact, one-sided. Ticket 03 measured that five of
  the six corpora are too small for a perfect score to clear their own threshold at 95%
  confidence. A score printed without its lower bound on a 3-item corpus reads as a result when
  it is not one. At k == n this reduces to the rule of three ticket 03 used.

  The best constant baseline. This is the bar a tie at 1.0 has to be read against. On
  `signal-classify` the corpus is 21 economic signals and 2 political ones, so a classifier that
  answers "economic" every time scores 0.913 and CLEARS the 0.8 threshold while knowing nothing.
  Any score at or below its skill's constant baseline is evidence of nothing, whoever produced it.
  Computed by brute force over each skill's own answer space, never assumed.

  Expected calibration error (item 4), raw and uncalibrated (items 7 and 9). Ticket 03 resolved
  that the estate holds one merged human label against the 326 per skill a temperature refit
  needs, so there is nothing held out to refit on and no specialised number exists. Every ECE
  below is therefore the shipped checkpoint's raw output, with 10 equal-width bins over the
  top-class probability. Only questions whose own answer is directly gradeable against a label
  contribute; `causal-claims`' elasticity question is a `noul` and carries no class probability,
  so it is excluded and said to be excluded.

`substrate-generator` IS NOT SCORED. It is reported as not measurable, with the reason
`run_laya.py` records. A skill a model structurally cannot answer is not a zero.
"""

from __future__ import annotations

import argparse
import json
import math
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from twin import causal_claims as cc
from twin import ethics_gate as eg
from twin import evolution_judge as ej
from twin import gameplay_lens as gl
from twin import signal_classify as sc
from twin import substrate_generator as sg
from twin import wardley
from twin.canon import digest_of
from twin.schema import STEEP
from twin.skills import evaluate, history_for, record_score, threshold_for

HERE = Path(__file__).parent

# The weights revision IS the model version: it is the thing that determines every number here,
# and ticket 02 measured `main` moving ten times in two days, so a bare "laya" would name nothing.
MODEL_VERSION = "laya-1c5edc17"

ECE_BINS = 10


# ---------------------------------------------------------------------------
# statistics
# ---------------------------------------------------------------------------


def clopper_pearson_lower(k: int, n: int, alpha: float = 0.05) -> float:
    """Exact one-sided 95% lower confidence bound on a binomial proportion.

    At k == n this equals `alpha ** (1/n)`, which is the rule of three ticket 03 applied by hand
    (0.05 ** (1/3) = 0.368 -> ticket 03 reports 0.000 for n=3 against a 0.8 threshold because it
    rounds the comparison, not the bound; both say the same thing about a 3-item corpus).
    """
    if n == 0:
        return 0.0
    if k == 0:
        return 0.0
    # Inverse of the regularised incomplete beta, by bisection -- no scipy in this environment.
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        # P(X >= k | p = mid) with X ~ Binomial(n, mid)
        tail = sum(math.comb(n, i) * mid**i * (1 - mid) ** (n - i) for i in range(k, n + 1))
        if tail < alpha:
            lo = mid
        else:
            hi = mid
    return round((lo + hi) / 2, 4)


def expected_calibration_error(pairs: list[tuple[float, bool]], bins: int = ECE_BINS) -> dict:
    """Standard ECE over equal-width bins of the top-class probability."""
    if not pairs:
        return {"ece": None, "n": 0, "bins": []}
    buckets: list[list[tuple[float, bool]]] = [[] for _ in range(bins)]
    for confidence, correct in pairs:
        index = min(bins - 1, int(confidence * bins))
        buckets[index].append((confidence, correct))
    total = len(pairs)
    ece = 0.0
    rows = []
    for index, bucket in enumerate(buckets):
        if not bucket:
            continue
        mean_confidence = sum(c for c, _ in bucket) / len(bucket)
        accuracy = sum(1 for _, ok in bucket if ok) / len(bucket)
        ece += (len(bucket) / total) * abs(accuracy - mean_confidence)
        rows.append(
            {
                "bin": "%.1f-%.1f" % (index / bins, (index + 1) / bins),
                "n": len(bucket),
                "mean_confidence": round(mean_confidence, 4),
                "accuracy": round(accuracy, 4),
            }
        )
    return {"ece": round(ece, 4), "n": total, "bins": rows}


# ---------------------------------------------------------------------------
# the best constant baseline, per skill, by brute force
# ---------------------------------------------------------------------------


def _best_constant(corpus: list[dict], scorer, candidates) -> dict:
    """The highest score any single constant answer reaches on this corpus."""
    best = {"score": -1.0, "answer": None}
    for label, answer in candidates:
        correct = sum(1 for item in corpus if scorer(answer(item), item["expected"]))
        score = correct / len(corpus)
        if score > best["score"]:
            best = {"score": round(score, 4), "answer": label, "correct": correct, "total": len(corpus)}
    return best


def constant_baselines(corpora: dict) -> dict:
    out = {}

    # signal-classify: the component is forced (every corpus item carries exactly one candidate),
    # so the only free choice is the STEEP tag.
    corpus = corpora[sc.SKILL]
    out[sc.SKILL] = _best_constant(
        corpus,
        sc.scorer,
        [
            (
                "always %r" % tag,
                lambda item, tag=tag: {"steep": tag, "claim": {"component": item["input"]["candidates"][0]["id"]}},
            )
            for tag in STEEP
        ],
    )

    # evolution-judge: a constant position. The four band midpoints are the constants a stage
    # classifier can express; the tolerance is 0.15 and a band is 0.25 wide.
    corpus = corpora[ej.SKILL]
    out[ej.SKILL] = _best_constant(
        corpus,
        ej.scorer,
        [
            ("always %s (%.3f)" % (name, (low + high) / 2), lambda item, p=(low + high) / 2: {"evolution_position": p})
            for name, low, high in wardley.BANDS
        ],
    )

    # causal-claims: sign x lag bucket x elasticity mode, swept.
    corpus = corpora[cc.SKILL]
    combos = []
    for sign in ("positive", "negative"):
        for lag in (30, 60, 180, 365):
            for step in range(0, 21):
                mode = step / 20
                combos.append(
                    (
                        "always (%s, %d days, mode %.2f)" % (sign, lag, mode),
                        lambda item, s=sign, l=lag, m=mode: {
                            "edge": {"sign": s, "lag_days": l, "elasticity": {"mode": m}, "evidence_grade": 5}
                        },
                    )
                )
    out[cc.SKILL] = _best_constant(corpus, cc.scorer, combos)
    out[cc.GRADE_SKILL] = _best_constant(
        corpus,
        cc.grade_scorer,
        [("always grade %d" % g, lambda item, g=g: {"edge": {"evidence_grade": g}}) for g in (1, 2, 3, 4, 5)],
    )

    # gameplay-lens: propose nothing, or propose every play on every component the org owns.
    corpus = corpora[gl.SKILL]
    out[gl.SKILL] = _best_constant(
        corpus,
        gl.scorer,
        [
            ("always propose nothing", lambda item: {"opportunities": []}),
            (
                "always propose every play on every owned component",
                lambda item: {
                    "opportunities": [
                        {"play": play, "component": component}
                        for component in item["input"]["org_components"]
                        for play in gl.PLAYS
                    ]
                },
            ),
        ],
    )

    # ethics-gate: a constant (admitted, stopped_at) outcome.
    corpus = corpora[eg.SKILL]
    outcomes = [
        ("always admit", True, None),
        ("always stop at purpose", False, "purpose"),
        ("always stop at necessity", False, "necessity"),
        ("always stop at proportionality", False, "proportionality"),
        ("always refuse with no ladder stop", False, None),
    ]
    out[eg.SKILL] = _best_constant(
        corpus,
        eg.scorer,
        [
            (label, lambda item, a=admitted, s=stop: {"admitted": a, "ladder": {"stopped_at": s}})
            for label, admitted, stop in outcomes
        ],
    )
    return out


# ---------------------------------------------------------------------------
# gradeable questions, for the calibration table
# ---------------------------------------------------------------------------


def _top_probability(answer: dict) -> float | None:
    probs = answer.get("probabilities")
    if not probs:
        return None
    return float(max(probs.values()))


def calibration_pairs(skill: str, corpus: list[dict], raw: dict) -> tuple[list[tuple[float, bool]], list[str]]:
    """(top-class probability, was it right) for every question whose own answer is directly
    gradeable against a label. Returns the pairs and the names of the questions used."""
    pairs: list[tuple[float, bool]] = []
    used: set[str] = set()
    by_id = {item["id"]: item for item in corpus}
    for item_id, record in raw.items():
        expected = by_id[item_id]["expected"]
        answers = record["answers"]
        if skill == sc.SKILL:
            pairs.append((_top_probability(answers["steep"]), answers["steep"]["choice"] == expected["steep"]))
            pairs.append(
                (_top_probability(answers["component"]), answers["component"]["choice"] == expected["component"])
            )
            used |= {"steep", "component"}
        elif skill == ej.SKILL:
            probs = answers["stage"]["probabilities"]
            best = max(probs, key=lambda k: probs[k])
            name, low, high = wardley.BANDS[int(best)]
            position = (low + high) / 2
            pairs.append((float(probs[best]), abs(position - float(expected["evolution_position"])) <= 0.15))
            used.add("stage")
        elif skill == cc.SKILL:
            pairs.append((_top_probability(answers["sign"]), answers["sign"]["choice"] == expected["sign"]))
            lag_probs = answers["lag"]["probabilities"]
            best = max(lag_probs, key=lambda k: lag_probs[k])
            days = (30, 60, 180, 365)[int(best)]
            pairs.append((float(lag_probs[best]), abs(days - int(expected["lag_days"])) <= 60))
            grade_probs = answers["grade"]["probabilities"]
            best_grade = max(grade_probs, key=lambda k: grade_probs[k])
            predicted = int(best_grade) + 1
            delta = predicted - int(expected["evidence_grade"])
            pairs.append((float(grade_probs[best_grade]), delta >= 0 and delta <= 1))
            used |= {"sign", "lag", "grade"}
        elif skill == gl.SKILL:
            wanted = {(p[0], p[1]) for p in expected["opportunities"]}
            for key, answer in answers.items():
                play, component = key.split("|", 1)
                said_available = answer["choice"] == "available"
                pairs.append((_top_probability(answer), said_available == ((play, component) in wanted)))
            used.add("one per (play, component) pair")
        elif skill == eg.SKILL:
            admitted, stop = {
                "admit": (True, None),
                "stop-at-purpose": (False, "purpose"),
                "stop-at-necessity": (False, "necessity"),
                "stop-at-proportionality": (False, "proportionality"),
                "refuse-for-missing-dpia": (False, None),
            }[answers["outcome"]["choice"]]
            right = admitted == expected["admitted"] and stop == expected.get("stopped_at")
            pairs.append((_top_probability(answers["outcome"]), right))
            used.add("outcome")
    return [(c, ok) for c, ok in pairs if c is not None], sorted(used)


# ---------------------------------------------------------------------------
# the replay callable
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# the legs under a conjunction, and the declared sensitivity route
# ---------------------------------------------------------------------------


def leg_breakdown(corpora: dict, run: dict) -> dict:
    """A scorer that ANDs several legs together hides which leg failed. `causal-claims` scores
    sign, lag and elasticity as one boolean, and `signal-classify` scores a STEEP tag whose corpus
    is 21 items of one class and 2 of another. A headline score that does not break those apart
    says the model is bad without saying at what, and it lets a heuristic's corpus-fitted constant
    pass unremarked. Both are broken out here."""
    out = {}

    corpus = corpora[sc.SKILL]
    raw = run["raw"][sc.SKILL]
    steep_right = component_right = 0
    minority_total = minority_right = 0
    predicted = {}
    for item in corpus:
        answers = raw[item["id"]]["answers"]
        got = answers["steep"]["choice"]
        predicted[got] = predicted.get(got, 0) + 1
        if got == item["expected"]["steep"]:
            steep_right += 1
        if answers["component"]["choice"] == item["expected"]["component"]:
            component_right += 1
        if item["expected"]["steep"] == "political":
            minority_total += 1
            if got == "political":
                minority_right += 1
    label_counts: dict[str, int] = {}
    for item in corpus:
        label_counts[item["expected"]["steep"]] = label_counts.get(item["expected"]["steep"], 0) + 1
    out[sc.SKILL] = {
        "steep_accuracy": round(steep_right / len(corpus), 4),
        "component_accuracy": round(component_right / len(corpus), 4),
        "component_note": (
            "every corpus item carries exactly one candidate component, so the binding half is a "
            "forced choice and measures nothing for either side"
        ),
        "label_counts": label_counts,
        "predicted_counts": predicted,
        "minority_class_recall": {
            "class": "political",
            "total": minority_total,
            "caught": minority_right,
            "note": (
                "the only two items on this corpus that a majority-class guesser gets wrong; the "
                "heuristic catches both with a three-keyword list fitted to these two items "
                "(signal_classify._POLITICAL_KEYWORDS)"
            ),
        },
    }

    corpus = corpora[cc.SKILL]
    raw = run["raw"][cc.SKILL]
    legs = {"sign": 0, "lag": 0, "elasticity": 0}
    for item in corpus:
        prediction = run["predictions"][cc.SKILL]["by_item"][item["id"]]["edge"]
        expected = item["expected"]
        legs["sign"] += prediction["sign"] == expected["sign"]
        legs["lag"] += abs(int(prediction["lag_days"]) - int(expected["lag_days"])) <= 60
        legs["elasticity"] += (
            abs(float(prediction["elasticity"]["mode"]) - float(expected["elasticity_mode"])) <= 0.15
        )
    modes = [float(i["expected"]["elasticity_mode"]) for i in corpus]
    mean_mode = sum(modes) / len(modes)
    out[cc.SKILL] = {
        "legs": {name: round(hits / len(corpus), 4) for name, hits in legs.items()},
        "conjunction_note": (
            "the claim scorer ANDs sign, lag and elasticity, so one failing leg fails the item"
        ),
        "heuristic_elasticity_is_a_fitted_constant": {
            "constant": cc._BASE_MODE,
            "corpus_modes": modes,
            "corpus_mean": round(mean_mode, 4),
            "constant_equals_corpus_mean": abs(cc._BASE_MODE - mean_mode) < 1e-9,
            "all_labels_within_tolerance_of_the_constant": all(
                abs(cc._BASE_MODE - m) <= cc._ELASTICITY_MODE_TOLERANCE for m in modes
            ),
            "note": (
                "twin/causal_claims.py's `_BASE_MODE` is 0.375, which is exactly the mean of this "
                "corpus's own four elasticity labels, and the scorer's tolerance is 0.15. So the "
                "heuristic's elasticity leg cannot fail on this corpus by construction, whatever "
                "the evidence text says. That is where its 1.000 on this metric comes from."
            ),
        },
    }
    return out


def sensitivity_routes(corpora: dict, run: dict) -> dict:
    """`evolution-judge` asks for a number on a continuous axis, and Laya can answer that two
    ways. Both were declared in `run_laya.py` BEFORE any result was seen: the primary is the
    ordered `score` question over the four Wardley bands, read as the argmax band's midpoint, and
    the sensitivity route is the bare `noul`.

    The primary is the score of record and the one `--record` writes. The sensitivity route is
    reported here with its own number and nothing else: switching to it after seeing which one
    won would be fitting the translation to a four-item corpus, which is the same flattery map
    call 12 refuses ("so the tool is not flattered by the measurement's own work")."""
    corpus = corpora[ej.SKILL]
    rows = []
    hits = 0
    for item in corpus:
        noul = float(run["predictions"][ej.SKILL]["by_item"][item["id"]]["_noul_position"])
        passed = bool(ej.scorer({"evolution_position": noul}, item["expected"]))
        hits += passed
        rows.append(
            {
                "id": item["id"],
                "noul": round(noul, 4),
                "label": item["expected"]["evolution_position"],
                "abs_error": round(abs(noul - float(item["expected"]["evolution_position"])), 4),
                "passed": passed,
            }
        )
    ordered_by_noul = [r["id"] for r in sorted(rows, key=lambda r: r["noul"])]
    ordered_by_label = [r["id"] for r in sorted(rows, key=lambda r: r["label"])]
    return {
        ej.SKILL: {
            "route": "raw `noul`, read straight as the evolution position",
            "score": round(hits / len(corpus), 4),
            "correct": hits,
            "total": len(corpus),
            "lower_bound_95": clopper_pearson_lower(hits, len(corpus)),
            "threshold": threshold_for(ej.SKILL),
            "rank_order_matches_the_labels": ordered_by_noul == ordered_by_label,
            "items": rows,
            "note": (
                "declared before the run, reported after it, and NOT recorded as the score. On a "
                "four-item corpus the 95% lower bound cannot clear the 0.75 threshold even at 4/4, "
                "so this route and the primary one are not distinguishable here."
            ),
        }
    }


def _replay(skill: str, predictions: dict):
    """A `skill_fn` `evaluate()` cannot tell from the heuristic. It receives only `item["input"]`,
    the same as the heuristic, and looks the recorded answer up by the input's own digest -- never
    by position, so a corpus that reordered would fail loudly rather than score the wrong rows
    against each other."""
    by_input_digest = predictions[skill]["_by_input_digest"]

    def call(item_input):
        key = digest_of(item_input)
        if key not in by_input_digest:
            raise KeyError("%s: no Laya prediction recorded for this corpus input" % skill)
        return by_input_digest[key]

    return call


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--predictions", default=str(HERE / "predictions.json"))
    ap.add_argument("--out", default=str(HERE / "bakeoff.json"))
    ap.add_argument("--record", action="store_true", help="item 6: append to twin/skill-scores.jsonl")
    ap.add_argument("--at", default=None)
    args = ap.parse_args()

    run = json.loads(Path(args.predictions).read_text())
    predictions = run["predictions"]

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        corpora = {
            sc.SKILL: sc.labelled_corpus(tmp_dir / "signal-classify"),
            ej.SKILL: ej.labelled_corpus(tmp_dir / "evolution-judge"),
            cc.SKILL: cc.labelled_corpus(tmp_dir / "causal-claims"),
            gl.SKILL: gl.labelled_corpus(tmp_dir / "gameplay-lens"),
            sg.SKILL: sg.labelled_corpus(),
            eg.SKILL: eg.labelled_corpus(),
        }

    # Item 3, asserted rather than trusted.
    for skill, corpus in corpora.items():
        if skill not in predictions:
            continue
        here_digest = digest_of(corpus)
        there_digest = predictions[skill]["corpus_digest"]
        if here_digest != there_digest:
            print("FAIL: %s corpus digest %s here, %s in the run" % (skill, here_digest, there_digest))
            return 1
        predictions[skill]["_by_input_digest"] = {
            digest_of(item["input"]): predictions[skill]["by_item"][item["id"]] for item in corpus
        }

    baselines = constant_baselines(corpora)

    # `evaluate()` untouched: the skill's own name, the skill's own scorer, the skill's own corpus.
    runs = [
        (sc.SKILL, sc.SKILL, corpora[sc.SKILL], sc.scorer),
        (ej.SKILL, ej.SKILL, corpora[ej.SKILL], ej.scorer),
        (cc.SKILL, cc.SKILL, corpora[cc.SKILL], cc.scorer),
        (cc.GRADE_SKILL, cc.SKILL, corpora[cc.SKILL], cc.grade_scorer),
        (gl.SKILL, gl.SKILL, corpora[gl.SKILL], gl.scorer),
        (eg.SKILL, eg.SKILL, corpora[eg.SKILL], eg.scorer),
    ]

    rows = []
    for metric, source_skill, corpus, scorer in runs:
        result = evaluate(metric, _replay(source_skill, predictions), corpus, scorer=scorer)
        correct = sum(1 for i in result.items if i.passed)
        total = len(result.items)
        pairs, used = calibration_pairs(source_skill, corpus, run["raw"][source_skill])
        # `causal-claims` and `causal-claims-grade-accuracy` are two metrics over ONE question
        # set, so they share one calibration figure. Printing it twice without saying so would
        # read as two independent measurements.
        shared = " (shared with %s: one question set, two metrics)" % source_skill if metric != source_skill else ""
        prior = [e for e in history_for(metric) if e["model_version"] == "heuristic-0.1.0"]
        rows.append(
            {
                "metric": metric,
                "corpus_digest": result.corpus_digest,
                "total": total,
                "correct": correct,
                "score": round(result.score, 4),
                "threshold": result.threshold,
                "passed": result.passed,
                "lower_bound_95": clopper_pearson_lower(correct, total),
                "clears_threshold_at_95": clopper_pearson_lower(correct, total) >= result.threshold,
                "constant_baseline": baselines[metric],
                "beats_constant_baseline": round(result.score, 4) > baselines[metric]["score"],
                "heuristic_score": prior[-1]["score"] if prior else None,
                "calibration": {**expected_calibration_error(pairs), "questions": used, "shared_with": shared.strip() or None},
                "per_item": [{"id": i.item_id, "passed": i.passed} for i in result.items],
                "_result": result,
            }
        )

    verdicts = {}
    for row in rows:
        if row["score"] > (row["heuristic_score"] or 0):
            verdict = "better"
        elif row["score"] < (row["heuristic_score"] or 0):
            verdict = "worse"
        else:
            verdict = "tied"
        if not row["beats_constant_baseline"]:
            verdict += ", and not measurable on this corpus (at or below the constant baseline)"
        elif not row["clears_threshold_at_95"]:
            verdict += ", but the corpus is too small to clear the threshold at 95% confidence"
        verdicts[row["metric"]] = verdict
        row["verdict"] = verdict

    recorded = []
    if args.record:
        at = args.at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        for row in rows:
            recorded.append(record_score(row.pop("_result"), MODEL_VERSION, at))
    for row in rows:
        row.pop("_result", None)

    # Item 8 asks for one number to compare against the vendor's own typed-decisions figure, so
    # the per-skill errors are pooled over the question sets that produced them. `causal-claims`
    # and its grade metric share one question set and are counted once, not twice.
    seen: set[str] = set()
    pooled: list[tuple[int, float]] = []
    for row in rows:
        if row["calibration"]["shared_with"] or row["calibration"]["ece"] is None:
            continue
        key = row["metric"]
        if key in seen:
            continue
        seen.add(key)
        pooled.append((row["calibration"]["n"], row["calibration"]["ece"]))
    pooled_n = sum(n for n, _ in pooled)
    pooled_ece = round(sum(n * e for n, e in pooled) / pooled_n, 4) if pooled_n else None
    unweighted = round(sum(e for _, e in pooled) / len(pooled), 4) if pooled else None

    doc = {
        "ticket": "04",
        "pooled_calibration": {
            "ece_weighted_by_question_count": pooled_ece,
            "ece_unweighted_mean_over_skills": unweighted,
            "questions": pooled_n,
            "expected_by_item_8": 0.129,
            "note": (
                "raw and uncalibrated. The vendor's own typed-decisions file records 0.207 raw "
                "falling to 0.129 after a refit; item 8 told this ticket to expect about 0.13. "
                "The pooled raw figure here lands on that refit number without any refit, on a "
                "different question distribution, so the agreement is suggestive and not a "
                "like-for-like comparison. It is reported as such."
            ),
        },
        "leg_breakdown": leg_breakdown(corpora, run),
        "sensitivity_routes": sensitivity_routes(corpora, run),
        "model_version": MODEL_VERSION,
        "pin": {"repo_id": run["repo_id"], "revision": run["revision"], "weights_sha256": run["weights_sha256"]},
        "run": {
            k: run[k]
            for k in ("device", "dtype", "torch_threads", "load_seconds", "calls", "questions", "wall_seconds",
                      "ms_per_question", "torch", "act_probability", "predictions_sha256", "measured_at")
        },
        "calibration_note": (
            "raw and uncalibrated: the shipped per-type temperatures are dead code (ticket 01) and "
            "the estate holds one merged human label against the 326 per skill a refit needs "
            "(ticket 03), so nothing was fitted here"
        ),
        "not_measurable": run["not_measurable"],
        "metrics": rows,
        "recorded": recorded,
    }
    Path(args.out).write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")

    header = "%-28s %7s %7s %9s %9s %-38s" % ("metric", "laya", "heur", "thr", "lb95", "best constant baseline")
    print(header)
    print("-" * len(header))
    for row in rows:
        print(
            "%-28s %7.3f %7.3f %9.2f %9.3f %-38s"
            % (
                row["metric"],
                row["score"],
                row["heuristic_score"],
                row["threshold"],
                row["lower_bound_95"],
                "%.3f  %s" % (row["constant_baseline"]["score"], row["constant_baseline"]["answer"]),
            )
        )
    print()
    for row in rows:
        ece = row["calibration"]["ece"]
        print("%-28s ECE %s over n=%d%s  ->  %s"
              % (row["metric"], "n/a" if ece is None else "%.4f" % ece, row["calibration"]["n"],
                 " [shared]" if row["calibration"]["shared_with"] else "", row["verdict"]))
    print()
    print("%-28s NOT MEASURABLE: %s" % (sg.SKILL, run["not_measurable"][sg.SKILL][:60] + "..."))
    if recorded:
        print("\nrecorded %d row(s) into twin/skill-scores.jsonl at model_version %s" % (len(recorded), MODEL_VERSION))
    print("pooled ECE %.4f over %d questions (raw, uncalibrated; item 8 expected ~0.13)"
          % (pooled_ece, pooled_n))
    print("wrote %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
