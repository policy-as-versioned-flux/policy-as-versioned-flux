#!/usr/bin/env bash
# Beat: "the twin's own judgement is graded by the truth surface, and a score that fell is a fail."
#
# Ticket 29, decision ticket 11 answer item 5. The twin's evals run HERE, in the gate, because the
# gate is the only citable source (NORTH-STAR §5). `.github/workflows/twin.yml` keeps running the
# same suite on push and is never cited by any document.
#
# Five things, in one script, all offline:
#   1. the twin self-versions, and its two spellings of the version agree
#   2. the six real skills at their existing thresholds -- seven metrics, since causal-claims
#      carries a second, separately-registered grade-accuracy metric
#   3. the three real-firm beats, in their declared order (twin/beat-sequence.sh)
#   4. cross_architecture_determinism, on this machine's architecture
#   5. the pinned-feed-version -> dated-signal lookup, and its table's coverage of every feed
#      envelope this estate actually publishes (ticket 11 resolution 3; spec user story 45)
#
# WHAT THE SEVEN SCORES ARE (ecosystem ticket 76). Every one of the seven heuristics is scored
# against the corpus it was FITTED ON -- evolution-judge's keyword table returns, for each of the
# four backtest components' own names, the position that component's corpus item expects, and
# signal-classify, causal-claims, gameplay-lens, substrate-generator and ethics-gate each say the
# same of themselves in twin/skill-thresholds.yaml's notes. So a 1.000 here is a HARNESS-MECHANISM
# observation -- the corpus loads, the scorer runs, the declared metric set is the set evaluated,
# the threshold compares, and no score fell against the last recorded value -- and it is NOT a
# measure of the twin's judgement. The lines below say so, because a reader of talk/deck.md was
# being handed "7 skill metrics ... at their thresholds" and could only read it as skill.
# Holding out a corpus the heuristics were not fitted on is a later ticket; until one exists this
# script must not spend the word "skill" unqualified.
#
# A FALL IN ANY SCORE against the last value recorded for that skill in twin/skill-scores.jsonl is
# a FAIL, even when the fallen score is still above its threshold. That file is the committed
# record of the last values; this script never writes to it (it is append-only, guarded by
# `skill_score_log_is_append_only`, and a gate that recorded its own runs would move the bar it
# checks against every time it ran). The record of what the gate saw is talk/truth.log and the
# capture beside it.
#
# Three outcomes only:
#   PASS (exit 0)  every assertion observed true
#   FAIL (exit 1)  an assertion observed false
#   SKIP (exit 3)  could not look, with the reason on the last line
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"

skip() { echo "SKIP: $*"; exit 3; }

PY="$ROOT/.venv/bin/python"
if [ ! -x "$PY" ]; then
  PY=python3
  "$PY" -c 'import yaml' 2>/dev/null || skip "no $ROOT/.venv and python3 lacks pyyaml; the twin package cannot be imported"
fi
command -v git >/dev/null 2>&1 || skip "git is needed: every skill corpus is built as a fixture repository"
[ -f "$ROOT/twin/VERSION" ] || skip "no twin/VERSION in $ROOT; this is not a checkout of the hub"

log="$(mktemp)"; trap 'rm -f "$log"' EXIT

# -- 1 and 2: the version, and the seven skill metrics ----------------------------------------
ROOT="$ROOT" "$PY" - >"$log" 2>&1 <<'PY'
import os, sys, tempfile
from pathlib import Path

ROOT = Path(os.environ["ROOT"])
sys.path.insert(0, str(ROOT))

from twin import TOOL_VERSION
from twin import record_skill_scores as rss
from twin.skills import history_for

fails = 0
def out(ok, msg):
    global fails
    fails += 0 if ok else 1
    print(("PASS: " if ok else "FAIL: ") + msg)

def verdict(score, threshold, last):
    """`fell` even when the score is still above its threshold: a threshold is a floor, and a fall
    against the last recorded value is the regression this harness exists to catch (decision
    ticket 11 answer item 5). Named and asserted below, because a comparison that is only ever
    exercised by scores that all pass cannot tell "correct" from "always says pass"."""
    if score < threshold:
        return "below"
    if last is not None and score < last:
        return "fell"
    return "pass"


assert verdict(0.7, 0.8, None) == "below", verdict(0.7, 0.8, None)
assert verdict(0.9, 0.8, 1.0) == "fell", verdict(0.9, 0.8, 1.0)
assert verdict(1.0, 0.8, 1.0) == "pass", verdict(1.0, 0.8, 1.0)

declared = (ROOT / "twin" / "VERSION").read_text().strip()
out(declared == TOOL_VERSION,
    "twin self-versions: twin/VERSION=%s, twin.TOOL_VERSION=%s (an adopter pins one number, not two)"
    % (declared, TOOL_VERSION))

# Evaluated honestly and recorded NOWHERE: `path` points at a throwaway file, so the committed
# score log stays the record of the last values rather than becoming a log of gate runs.
with tempfile.TemporaryDirectory() as tmp:
    entries = rss.run("1970-01-01T00:00:00Z", path=Path(tmp) / "scores.jsonl")

# WHICH metrics came back, against the committed list, before any of them is scored. Iterating
# whatever run() returns and then printing the word "seven" underneath means a skill that stops
# being evaluated -- the ethics gate, say -- disappears from the truth surface in silence: with
# one metric deleted this printed "SUBTOTAL: 6 skill metric(s)" and then "PASS: seven skill
# metrics ..." and exited 0 (found 2026-08-29).
import yaml
declared = yaml.safe_load((ROOT / "twin" / "skill-thresholds.yaml").read_text())["thresholds"]
# toy-classifier is the fixture skill the harness proves itself against, never one of the real
# metrics; the file says so in its own header.
expected = set(declared) - {"toy-classifier"}
observed = {e["skill"] for e in entries}
out(observed == expected,
    "the metrics evaluated are exactly the ones twin/skill-thresholds.yaml declares "
    "(%d): missing %s, unexpected %s"
    % (len(expected), sorted(expected - observed) or "none", sorted(observed - expected) or "none"))

for entry in entries:
    skill, score, threshold = entry["skill"], entry["score"], entry["threshold"]
    # The last value recorded for this skill, whatever model version recorded it. Deliberately
    # not `detect_regression()`, which compares the latest two *model versions* and so says
    # nothing at all while only one has ever been recorded: a swap that scores lower is exactly
    # the case this must fail on, and a re-run that scores lower is the other one.
    prior = history_for(skill)
    last = prior[-1]["score"] if prior else None
    shown = "none recorded" if last is None else "%.3f" % last
    said = verdict(score, threshold, last)
    why = {"below": "  -- below its threshold",
           "fell": "  -- FELL against the last recorded value in twin/skill-scores.jsonl",
           "pass": ""}[said]
    out(said == "pass", "%-28s score=%.3f  threshold=%.3f  last=%s  [harness-mechanism: scored "
                        "on the corpus it was fitted on]%s"
                        % (skill, score, threshold, shown, why))

# The label is read from the skill module, not typed here: evolution_judge declares what its own
# corpus is, so if someone later holds a corpus out and flips the constant, this line follows.
from twin.evolution_judge import CORPUS_KIND
out(CORPUS_KIND == "harness-mechanism",
    "evolution-judge declares its corpus kind as %r -- the keyword table is scored against the "
    "four items it was fitted to, so its 1.000 grades the harness, not the twin's judgement"
    % CORPUS_KIND)

print("METRICS: %d" % len(entries))
print("SUBTOTAL: %d skill metric(s), %d observed false" % (len(entries), fails))
sys.exit(1 if fails else 0)
PY
rc=$?
cat "$log"
[ "$rc" -le 1 ] || skip "the skill-eval harness could not run: $(tail -1 "$log")"
fail=$rc

# -- 3: the three real-firm beats, in their declared order -------------------------------------
beats="$(mktemp)"
if bash "$ROOT/twin/beat-sequence.sh" >"$beats" 2>&1; then
  echo "PASS: the three real-firm beats ran in their declared order (royal-mail, intel, netflix)"
else
  echo "FAIL: twin/beat-sequence.sh exited non-zero: $(tail -1 "$beats" | cut -c1-160)"
  fail=1
fi
rm -f "$beats"

# -- 4: determinism on this architecture -------------------------------------------------------
# TWIN_CI_ARCH_MATRIX=1 is what turns the check on: without it the invariant skips itself and
# says the same-machine leg is asserted elsewhere. The gate asks for the real comparison.
det="$(mktemp)"
# The exit code alone is not the observation: the invariant SELF-SKIPS when it decides the CI
# matrix is absent and `bin/twin verify` still exits 0, which printed
# "PASS: cross_architecture_determinism --" with an empty claim after the dash. The sentence is
# the evidence, so its absence is the failure.
claim="$(TWIN_CI_ARCH_MATRIX=1 "$ROOT/bin/twin" verify --only cross_architecture_determinism >"$det" 2>&1; \
         grep -o '[0-9]* artefacts byte-identical on .*' "$det" | head -1)"
if [ -n "$claim" ]; then
  echo "PASS: cross_architecture_determinism -- $claim"
elif grep -q 'SKIP cross_architecture_determinism' "$det"; then
  echo "FAIL: cross_architecture_determinism skipped itself and claimed nothing: $(grep -o 'SKIP cross_architecture_determinism.*' "$det" | head -1 | cut -c1-160)"
  fail=1
else
  echo "FAIL: cross_architecture_determinism: $(grep -E 'FAIL|Violated|RESULT' "$det" | head -1 | cut -c1-160)"
  fail=1
fi
rm -f "$det"

# -- 5: the pinned-feed-version -> dated-signal lookup ------------------------------------------
# Ticket 11 resolution 3 / spec user story 45. Two observations, both offline and neither needing
# a tag: the lookup's own self-check (one signal per envelope, steep from the fixed table,
# provenance carrying published_at + tag + commit, a hole named rather than guessed), and the
# COVERAGE of that table against every feed the estate actually publishes. The second is the one
# that rots: a publisher ships a new feed, nobody adds a row, and the clock meets a version it
# cannot bind. That is a red gate here rather than a 06:20 surprise.
lookup="$(mktemp)"
if ROOT="$ROOT" "$PY" - >"$lookup" 2>&1 <<'PY'
import os, sys
from pathlib import Path

ROOT = Path(os.environ["ROOT"])
sys.path.insert(0, str(ROOT))
from twin import feed_signal
from twin.feed_signal import EXCLUDED_FROM_LOOKUP, FeedSignalError, signal_for, steep_for

feed_signal.demo()

estate = ROOT / ".estate-clone"
if not estate.is_dir():
    print("note: no .estate-clone, so table coverage was not checked against published feeds")
    sys.exit(0)

import json
holes, bound = [], []
for path in sorted(estate.glob("*/**/feed.json")):
    envelope = json.loads(path.read_text(encoding="utf-8"))
    if envelope.get("kind") != "feed":
        continue
    name = envelope["name"]
    try:
        steep_for(name)
    except FeedSignalError as exc:
        holes.append(f"{name} ({path.relative_to(estate)}): {exc}")
        continue
    # A published envelope really does map to exactly one signal, not just to a STEEP letter.
    # The tag and commit here are PLACEHOLDERS and the output says so: the real ones are the
    # caller's, handed in by whatever verified the signature, and no tag for these feeds exists
    # locally (they are cut by cut-release.yml in Actions). What is observed is the mapping.
    doc = signal_for(envelope, tag="placeholder-tag", commit="0" * 40)
    bound.append((name, doc["steep"], doc["date"]))

holes = [h for h in holes if not any(x in h for x in EXCLUDED_FROM_LOOKUP)]
if holes:
    print("the lookup has no row for a feed this estate publishes:")
    for h in holes:
        print("  " + h)
    sys.exit(1)
print("ok  every one of %d published feed envelope(s) maps to exactly one dated signal, shape "
      "checked with a placeholder tag/commit (%d feed(s) excluded by name, with a reason)"
      % (len(bound), len(EXCLUDED_FROM_LOOKUP)))
PY
then
  echo "PASS: the pinned-feed-version -> dated-signal lookup: $(tail -1 "$lookup")"
else
  echo "FAIL: the feed-version -> signal lookup observed false: $(tail -2 "$lookup" | tr '\n' ' ')"
  fail=1
fi
rm -f "$lookup"

if [ "$fail" -eq 0 ]; then
  echo "PASS: $(sed -n 's/^METRICS: //p' "$log" | tail -1) harness-mechanism metrics (each heuristic scored against the corpus it was fitted on, so this grades the harness, not the twin's judgement -- a held-out corpus is not built yet), exactly the set twin/skill-thresholds.yaml declares, at their thresholds and none fallen, three real-firm beats, identical bytes on this architecture, and every published feed envelope binding to one dated signal"
  exit 0
fi
echo "FAIL: the twin's evals observed false; see the lines above"
exit 1
