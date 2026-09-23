#!/usr/bin/env bash
# Beat (eco-system ticket 112): "a threshold states the corpus it needs, and a run below it is not
# measurable."
#
# twin/skill-thresholds.yaml carried no minimum corpus size, and twin/skills.py refused only an
# empty corpus, so a one-item corpus passed. Every threshold now states `min_items`, derived by
# twin/corpus_size.py and never typed. This script grades four things, all offline:
#
#   1. every stated minimum is the derived one, and the derivation refuses the two ways a typed
#      number goes wrong (too low, and the imported ~50); a negative control for each
#   2. the harness reports the third outcome: a perfect run and a zero run on a corpus below the
#      minimum are both NOT MEASURABLE, and a run at the minimum passes or fails on its score
#   3. a lowered minimum or threshold with no decision-ticket citation is refused, with a planted
#      lowering as the negative control, and the real file is checked against its own baseline
#   4. the seven real metrics, each with its corpus size, its minimum and the 95% lower bound a
#      perfect score on that corpus actually supports
#
# THE AMBER IS THE POINT. The ticket says several greens go amber when it lands. On 2026-09-22 six
# of the seven metrics sit below their minimum. That is the estate's own state, a corpus that has
# not been grown, so it is a declared `waits:` SKIP in talk/verify-manifest.txt and inside the
# ceiling. It turns PASS by itself the day every corpus reaches its minimum. Nothing here types
# which metrics are short: the count is read off this run.
#
#   PASS (exit 0)  1-3 observed true and every metric is measurable and at its threshold
#   FAIL (exit 1)  any of 1-3 observed false, or a measurable metric below its threshold
#   SKIP (exit 3)  1-3 observed true and one or more metrics are not measurable (the last line
#                  says how many and which), or the real thresholds file has fewer than two
#                  committed versions so leg 3 could not look at it, or the twin package could
#                  not be imported at all
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"

PY="$ROOT/.venv/bin/python"
if [ ! -x "$PY" ]; then
  PY=python3
  "$PY" -c 'import yaml' 2>/dev/null || { echo "SKIP: no $ROOT/.venv and python3 lacks pyyaml; the twin package cannot be imported"; exit 3; }
fi
command -v git >/dev/null 2>&1 || { echo "SKIP: git is needed: every skill corpus is built as a fixture repository"; exit 3; }
[ -f "$ROOT/twin/corpus_size.py" ] || { echo "SKIP: no twin/corpus_size.py in $ROOT; this is not a checkout of the hub at ticket 112 or later"; exit 3; }

log="$(mktemp)"; trap 'rm -f "$log"' EXIT
ROOT="$ROOT" "$PY" - >"$log" 2>&1 <<'PY'
import os, sys, tempfile
from pathlib import Path

ROOT = Path(os.environ["ROOT"])
sys.path.insert(0, str(ROOT))

import yaml
from twin import corpus_size as cs
from twin import record_skill_scores as rss
from twin import skills
from twin.invariants.harness import _lowered_without_citation, _thresholds_baseline

fails = 0
def out(ok, msg):
    global fails
    fails += 0 if ok else 1
    print(("PASS: " if ok else "FAIL: ") + msg)

# -- 1. every stated minimum is the derived one ------------------------------------------------
doc = yaml.safe_load((ROOT / "twin" / "skill-thresholds.yaml").read_text())
rows = doc["thresholds"]
wrong = []
for name, entry in rows.items():
    d = cs.derivation(entry["threshold"])
    stated = entry.get("min_items")
    print("  %-28s threshold=%.2f  effect=%.2f  se-route=%d  rule-of-three=%d  bins=%d  derived=%d  stated=%s"
          % (name, d["threshold"], d["effect"], d["standard_error_route"], d["rule_of_three_route"],
             d["bins"], d["min_items"], stated))
    if stated != d["min_items"]:
        wrong.append(name)
out(not wrong, "every one of %d thresholds states the minimum twin/corpus_size.py derives from it "
               "(mismatched: %s)" % (len(rows), ", ".join(wrong) or "none"))

# Negative controls: the harness refuses a stated number the method does not give, below it and
# above it. 50 is the prior art's figure (Laya map ticket 10), which no threshold here derives.
with tempfile.TemporaryDirectory() as tmp:
    refused = []
    for stated in (1, 50, None):
        entry = {"threshold": 0.8}
        if stated is not None:
            entry["min_items"] = stated
        path = Path(tmp) / ("t-%s.yaml" % stated)
        path.write_text(yaml.safe_dump({"schema": skills.THRESHOLDS_SCHEMA, "thresholds": {"x": entry}}))
        try:
            skills.threshold_for("x", path)
        except skills.SkillError:
            refused.append(stated)
    out(refused == [1, 50, None], "the harness refuses a stated minimum of 1, of 50 (the imported "
                                  "figure) and none at all at threshold 0.8, which derives %d; refused: %s"
                                  % (cs.derived_min_items(0.8), refused))

# -- 2. the third outcome -----------------------------------------------------------------------
with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "t.yaml"
    path.write_text(yaml.safe_dump({"schema": skills.THRESHOLDS_SCHEMA,
                                    "thresholds": {"x": {"threshold": 0.8, "min_items": 16}}}))
    # Every item carries a basis and the right skill states it (eco-system ticket 118): a right
    # answer on no checkable basis is unscoreable, so without one nothing here could pass.
    corpus = lambda n: [{"id": str(k), "input": "w%d" % k, "expected": "W%d" % k, "basis": "upper"} for k in range(n)]
    right, wrong_fn = (lambda s: skills.Stated(s.upper(), "upper")), (lambda s: "?")
    seen = {
        "perfect on 3": skills.evaluate("x", right, corpus(3), threshold_path=path).outcome,
        "zero on 3": skills.evaluate("x", wrong_fn, corpus(3), threshold_path=path).outcome,
        "perfect on 16": skills.evaluate("x", right, corpus(16), threshold_path=path).outcome,
        "zero on 16": skills.evaluate("x", wrong_fn, corpus(16), threshold_path=path).outcome,
    }
    small = skills.evaluate("x", right, corpus(3), threshold_path=path)
want = {"perfect on 3": skills.NOT_MEASURABLE, "zero on 3": skills.NOT_MEASURABLE,
        "perfect on 16": skills.PASS, "zero on 16": skills.FAIL}
out(seen == want and not small.passed and not small.failed,
    "the harness has three outcomes: %s; a not-measurable run is neither passed nor failed"
    % ", ".join("%s -> %s" % kv for kv in seen.items()))

# -- 3. a lowering needs a citation -------------------------------------------------------------
planted = _lowered_without_citation({"thresholds": {"x": {"threshold": 0.8, "min_items": 16}}},
                                    {"thresholds": {"x": {"threshold": 0.8, "min_items": 9}}})
cited = _lowered_without_citation({"thresholds": {"x": {"threshold": 0.8, "min_items": 16}}},
                                  {"thresholds": {"x": {"threshold": 0.65, "min_items": 9,
                                                        "authorised_by": "decision ticket 20 - reason"}}})
out(planted == ["x min_items 16 -> 9"] and cited == [],
    "a planted uncited lowering of a minimum is refused (%s) and a cited one is not" % planted)
current = skills.load_thresholds()
baseline = _thresholds_baseline(ROOT, current)
unlooked = []
if baseline is None:
    # Not a PASS: the guard could not look. The harness check raises Skip in the same state
    # (review round 2 of ticket 112), and so does this script.
    unlooked.append("the citation guard on the real file (twin/skill-thresholds.yaml has fewer "
                    "than two committed versions here, so there is no earlier one to compare with)")
    print("NOT LOOKED: " + unlooked[-1])
else:
    lowered = _lowered_without_citation(baseline[0], current)
    out(not lowered, "no threshold or minimum in twin/skill-thresholds.yaml was lowered without a "
                     "citation against %s (lowered: %s)" % (baseline[1], "; ".join(lowered) or "none"))

# -- 4. the seven real metrics ------------------------------------------------------------------
with tempfile.TemporaryDirectory() as tmp:
    entries = rss.run("1970-01-01T00:00:00Z", path=Path(tmp) / "scores.jsonl")
short = []
for e in entries:
    bound = cs.accuracy_lower_bound(e["total"])
    bound_s = "bounds nothing" if bound is None else ">= %.3f" % bound
    # Eco-system ticket 118: the minimum is met by MEASURED items, those with a checkable basis or
    # a wrong answer. An item right on no checkable basis is unscoreable and does not count.
    line = ("%-28s items=%-3d measured=%-3d min_items=%-3d threshold=%.2f score=%.3f  a perfect score on "
            "%d item(s) puts true accuracy %s (95%%)" % (e["skill"], e["total"], e["measured_count"],
                                                         e["min_items"], e["threshold"], e["score"],
                                                         e["total"], bound_s))
    if e["outcome"] == skills.NOT_MEASURABLE:
        short.append("%s %d<%d" % (e["skill"], e["measured_count"], e["min_items"]))
        print("NOT MEASURABLE: " + line)
    else:
        out(e["outcome"] == skills.PASS, line)

print("SHORT: %d of %d skill metrics (%s)" % (len(short), len(entries), ", ".join(short)))
print("UNLOOKED: %s" % ("; ".join(unlooked) or "none"))
sys.exit(1 if fails else (3 if short or unlooked else 0))
PY
rc=$?
cat "$log"
short="$(sed -n 's/^SHORT: //p' "$log" | tail -1)"
unlooked="$(sed -n 's/^UNLOOKED: //p' "$log" | tail -1)"
case "$rc" in
  0) echo "PASS: every threshold states the minimum corpus its own derivation gives, the harness reports not measurable below it, a lowered minimum needs a citation, and every real metric is measurable and at its threshold"; exit 0 ;;
  3) if [ "$unlooked" != "none" ]; then
       echo "SKIP: not looked at: $unlooked. Short: $short"; exit 3
     fi
     echo "SKIP: $short are not measurable, each corpus below the minimum its threshold states in measured items (an item right on no checkable basis is not measured, eco-system ticket 118); the derivation, the third outcome and the citation guard were all observed true"; exit 3 ;;
  *) echo "FAIL: a threshold's stated corpus, the third outcome or the citation guard observed false; see the lines above"; exit 1 ;;
esac
