#!/usr/bin/env bash
# Beat (eco-system ticket 118): "a green that rests on luck may not promote."
#
# The skill-eval harness recorded two item states, passed or not, and the threshold graded the
# fraction that passed. A skill that reached the right answer for the wrong reason raised that
# fraction exactly as much as one that reasoned correctly. The harness now reads every item twice
# (was the answer right, and did the basis the skill stated hold against the basis the corpus item
# carries) and gives it one verdict: right, wrong, wrong-basis or unscoreable. The threshold grades
# the ATTRIBUTABLE RATE: right items over measured items. A wrong-basis item stays in the
# denominator and out of the numerator, so luck lowers the rate. An unscoreable item (a right
# answer with no checkable basis) is in neither, so it cannot count for the skill. This script
# grades four things, all offline:
#
#   1. the verdict table: a pure function of the two readings, all six cases
#   2. the harness on a planted 16-item fixture: an honest skill passes; a skill right on every
#      item for a wrong stated reason fails, and the negative control prints the right-answer
#      fraction a two-state harness would have passed it on; four lucky items in twenty still
#      clear 0.8 and a fifth does not; a perfect run on items with no basis is not measurable
#   3. the rate reaches the permission: record_score() writes it beside the score, and model
#      permission condition 1 refuses a row whose score clears and whose rate does not, and a row
#      with no rate at all, with a positive control at the bar
#   4. the seven real metrics: items, measured items, unscoreable and wrong-basis counts and the
#      rate, read off a fresh run; and the committed log carries the rate on each metric's newest row
#
# THE AMBER IS THE ESTATE'S OWN STATE. No real corpus item carries a checkable basis on
# 2026-09-22, so every right answer is unscoreable and no real metric has a rate a threshold can
# grade. That is a corpus not yet labelled, so it is a declared `waits:` SKIP in
# talk/verify-manifest.txt and inside the ceiling. It turns PASS by itself the day every corpus
# carries bases on enough items and every rate clears its bar. Nothing here types which metrics
# are short: the count is read off this run.
#
#   PASS (exit 0)  1-4 observed true and every real metric has a measurable rate at its threshold
#   FAIL (exit 1)  any of 1-4 observed false, or a measurable real rate below its threshold
#   SKIP (exit 3)  1-4 observed true and one or more real metrics have no rate a threshold can
#                  grade (the last line says how many and which), or the twin package could not
#                  be imported at all
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"

PY="$ROOT/.venv/bin/python"
if [ ! -x "$PY" ]; then
  PY=python3
  "$PY" -c 'import yaml' 2>/dev/null || { echo "SKIP: no $ROOT/.venv and python3 lacks pyyaml; the twin package cannot be imported"; exit 3; }
fi
command -v git >/dev/null 2>&1 || { echo "SKIP: git is needed: every skill corpus is built as a fixture repository"; exit 3; }
grep -q "def attribute" "$ROOT/twin/skills.py" 2>/dev/null || { echo "SKIP: twin/skills.py in $ROOT has no attribute(); this is not a checkout of the hub at ticket 118 or later"; exit 3; }

log="$(mktemp)"; trap 'rm -f "$log"' EXIT
ROOT="$ROOT" "$PY" - >"$log" 2>&1 <<'PY'
import os, sys, tempfile
from pathlib import Path

ROOT = Path(os.environ["ROOT"])
sys.path.insert(0, str(ROOT))

import yaml
from twin import model_permission as mp
from twin import record_skill_scores as rss
from twin import skills

fails = 0
def out(ok, msg):
    global fails
    fails += 0 if ok else 1
    print(("PASS: " if ok else "FAIL: ") + msg)

# -- 1. the verdict table -----------------------------------------------------------------------
table = {(a, b): skills.attribute(a, b) for a in (True, False) for b in (True, False, None)}
want = {(True, True): skills.RIGHT, (True, False): skills.WRONG_BASIS, (True, None): skills.UNSCOREABLE,
        (False, True): skills.WRONG, (False, False): skills.WRONG, (False, None): skills.WRONG}
out(table == want, "the verdict is a pure function of (answer right, basis held): %s"
    % ", ".join("%s/%s -> %s" % (a, b, v) for (a, b), v in sorted(table.items(), key=str)))
out(not set(skills.ITEM_VERDICTS) & {skills.PASS, skills.FAIL, skills.NOT_MEASURABLE},
    "no item verdict (%s) shares a word with a run outcome (%s, %s, %s)"
    % (", ".join(skills.ITEM_VERDICTS), skills.PASS, skills.FAIL, skills.NOT_MEASURABLE))

# -- 2. the harness on a planted fixture --------------------------------------------------------
BASIS = "upper-case every letter"
def corpus(n, basis=True):
    extra = {"basis": BASIS} if basis else {}
    return [{"id": str(k), "input": "w%d" % k, "expected": "W%d" % k, **extra} for k in range(n)]
def stated(reason_for):
    return lambda s: skills.Stated(s.upper(), reason_for(s))

with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp) / "t.yaml"
    path.write_text(yaml.safe_dump({"schema": skills.THRESHOLDS_SCHEMA,
                                    "thresholds": {"x": {"threshold": 0.8, "min_items": 16}}}))
    run = lambda fn, items: skills.evaluate("x", fn, items, threshold_path=path)
    honest = run(stated(lambda s: BASIS), corpus(16))
    lucky = run(stated(lambda s: "memorised"), corpus(16))
    def mixed(n_lucky):
        bad = {"w%d" % k for k in range(16, 16 + n_lucky)}
        return run(stated(lambda s: "memorised" if s in bad else BASIS), corpus(16 + n_lucky))
    four, five = mixed(4), mixed(5)
    bare = run(lambda s: s.upper(), corpus(16, basis=False))

out(honest.outcome == skills.PASS and honest.attributable_rate == 1.0,
    "an honest skill on 16 items with a checkable basis passes at rate %.3f" % honest.attributable_rate)
two_state = lucky.answered_right / len(lucky.items)
out(lucky.outcome == skills.FAIL and lucky.score == 0.0 and lucky.attributable_rate == 0.0
    and lucky.measured_count == 16 and two_state >= lucky.threshold,
    "a skill right on all 16 items for a wrong stated reason FAILS at rate %.3f and score %.3f; "
    "NEGATIVE CONTROL: a two-state harness counts %d of 16 right and would have passed it at %.3f "
    "against %.2f" % (lucky.attributable_rate, lucky.score, lucky.answered_right, two_state, lucky.threshold))
out(four.outcome == skills.PASS and five.outcome == skills.FAIL
    and (four.measured_count, five.measured_count) == (20, 21),
    "luck lowers the rate through the denominator: 16 right and 4 wrong-basis rate %.3f (%s), "
    "16 right and 5 wrong-basis rate %.3f (%s); every wrong-basis item is measured"
    % (four.attributable_rate, four.outcome, five.attributable_rate, five.outcome))
out(bare.outcome == skills.NOT_MEASURABLE and bare.score == 1.0 and bare.attributable_rate is None
    and bare.unscoreable == 16,
    "a perfect score (%.3f) on 16 items with no checkable basis is %s: %d unscoreable, rate %s, "
    "never 0 and never a pass" % (bare.score, bare.outcome, bare.unscoreable, bare.attributable_rate))

# -- 3. the rate reaches the permission ---------------------------------------------------------
with tempfile.TemporaryDirectory() as tmp:
    row = skills.record_score(lucky, "fixture-lucky", "1970-01-01T00:00:00Z", path=Path(tmp) / "s.jsonl")
out(row["attributable_rate"] == 0.0 and row["wrong_basis"] == 16 and row["measured_count"] == 16,
    "record_score() writes the rate beside the score: attributable_rate=%s wrong_basis=%s "
    "unscoreable=%s measured_count=%s score=%s"
    % (row["attributable_rate"], row["wrong_basis"], row["unscoreable"], row["measured_count"], row["score"]))

def item1(r):
    perm = mp.permission_for("x", "m", scores=[{"skill": "x", "model_version": "m", **r}],
                             corpus_digest_now="d", threshold_now=0.8, min_items_now=16,
                             baseline=None, variance=None)
    return next(c for c in perm.conditions if c.item == 1)

base = {"score": 1.0, "threshold": 0.8, "min_items": 16, "measured_count": 16, "total": 16,
        "outcome": "pass", "corpus_digest": "d"}
at_bar = item1({**base, "attributable_rate": 0.8})
luck = item1({**base, "attributable_rate": 0.5, "outcome": "fail"})
legacy = item1(base)
out(at_bar.passed and not luck.passed and not legacy.passed,
    "condition 1 grades the rate: POSITIVE control at the bar holds (%s); a score of 1.000 on a "
    "rate of 0.500 is refused (%s); a row with no rate is refused (%s)"
    % (at_bar.detail, luck.detail, legacy.detail))

# -- 4. the seven real metrics ------------------------------------------------------------------
with tempfile.TemporaryDirectory() as tmp:
    entries = rss.run("1970-01-01T00:00:00Z", path=Path(tmp) / "scores.jsonl")
short = []
for e in entries:
    rate = e["attributable_rate"]
    line = ("%-28s items=%-3d measured=%-3d unscoreable=%-3d wrong-basis=%-3d score=%.3f rate=%s "
            "threshold=%.2f min_items=%d" % (e["skill"], e["total"], e["measured_count"], e["unscoreable"],
                                             e["wrong_basis"], e["score"],
                                             "none" if rate is None else "%.3f" % rate,
                                             e["threshold"], e["min_items"]))
    if e["outcome"] == skills.NOT_MEASURABLE:
        short.append("%s %d<%d" % (e["skill"], e["measured_count"], e["min_items"]))
        print("NO RATE: " + line)
    else:
        out(e["outcome"] == skills.PASS, line)

logged = skills.load_scores()
newest = {}
for r in logged:
    newest[r["skill"]] = r
missing = sorted(m for m in rss.METRICS if m not in newest or "attributable_rate" not in newest[m])
out(not missing, "twin/skill-scores.jsonl records the attributable rate on the newest row of every "
                 "one of the %d metrics (%d of %d rows carry it; missing on: %s)"
    % (len(rss.METRICS), sum(1 for r in logged if "attributable_rate" in r), len(logged),
       ", ".join(missing) or "none"))

print("SHORT: %d of %d skill metrics (%s)" % (len(short), len(entries), ", ".join(short)))
sys.exit(1 if fails else (3 if short else 0))
PY
rc=$?
cat "$log"
short="$(sed -n 's/^SHORT: //p' "$log" | tail -1)"
case "$rc" in
  0) echo "PASS: the harness gives every item one of four verdicts, the threshold grades the attributable rate, luck lowers it, the permission reads it, and every real metric has a rate at its threshold"; exit 0 ;;
  3) echo "SKIP: $short have no attributable rate a threshold can grade: too few of their items carry a checkable basis; the verdict table, the rate, its reach into the permission and the log were all observed true"; exit 3 ;;
  *) echo "FAIL: the verdict table, the attributable rate, the permission or the log observed false; see the lines above"; exit 1 ;;
esac
