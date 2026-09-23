#!/usr/bin/env bash
# Beat: "a model may judge on a clock within thresholds, and 'within thresholds' is a thing that
#        grades, not a sentence somebody remembers."
#
# Wayfinder ticket 05. On 2026-09-21 the owner permitted a model to judge on a GitHub clock,
# within thresholds. `twin/model_permission.py` turns that into TEN conditions; this script
# grades all ten, and grades the RULE rather than any one model, because the rule outlives the
# candidate. Offline throughout: no model runs here.
#
# WHAT IS GRADED, item by item:
#   1  the newest recorded score for that skill AND that model version clears the threshold the
#      threshold file sets TODAY, and was itself recorded against that same bar; the number that
#      meets the bar is the row's attributable rate, which luck lowers (eco-system ticket 118)
#   2  the corpus digest of that scoring run is the digest of the corpus in the tree today
#   3  the claim records which model_version judged it, or it is not a permitted claim
#   4  the permission covers judging and never merging; a model makes no override and prices
#      nothing, and nothing in this hub merges a claim pull request
#   5  a skill with no recorded score has no permission; absence is not consent
#   6  the permission binds at a seam the actor cannot route around, and the clock the seam
#      reads is DERIVED from the environment, never believed off the file
#   7  a run that declines to judge leaves a counted row, so the exercise rate is knowable
#   8  a field whose recorded outputs carry one distinct value revokes the permission it was
#      supposed to grant, whatever that value is
#   9  the score must be strictly above the corpus's own best constant answer
#  10  a score recorded against the corpus the model was FITTED on is not evidence of judgement
#
# ITEM 10 IS THE TENTH, BEYOND THE TICKET'S NINE, and it was added because the first run of the
# nine granted the incumbent heuristic a permission on five of seven metrics. The estate had
# already said why that is wrong, in its own words: twin/evolution_judge.py's CORPUS_KIND reads
# `harness-mechanism`, which its own comment defines as "while every corpus item is one the
# heuristic was fitted to", and verify-twin-evals.sh prints that word on every run. A permission
# resting on a fitted score is the same defect class as items 8 and 9: a number that cannot come
# out any other way. One edit to CORPUS_KIND, the day a held-out corpus exists, lifts it.
#
# EVERY CONDITION CARRIES A NEGATIVE CONTROL, and the rule carries a POSITIVE one. A rule that
# refuses everything is exactly as useless as one that grants everything, and it passes a
# refusal-only test suite. So a fabricated model that clears all ten IS granted here, and the
# check fails if it is not. That matters more than usual, because NOTHING IN THE ESTATE HOLDS A
# PERMISSION TODAY: without the positive control the whole rule could be a stuck "no".
#
# WHAT IS REPORTED AND NOT GRADED. Each metric's threshold is printed beside the best constant
# answer its own corpus admits. Five of seven sit at or below it (measured 2026-09-21), which
# means those thresholds cannot detect a model that has learned nothing. That is the corpus's
# problem, not this rule's. Eco-system ticket 112 derives each threshold's minimum corpus
# (min_items in twin/skill-thresholds.yaml: 16 at 0.80, 12 at 0.75, 9 at 0.65) and item 1
# refuses a run below it. The permission refuses such a score anyway, by items 1 and 9, so the
# weak threshold grants nothing. It is printed rather than
# graded because turning it red here would make this check a proxy for a corpus nobody can grow
# for 341 days.
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
[ -f "$ROOT/twin/model_permission.py" ] || skip "no twin/model_permission.py in $ROOT; the rule this check grades is not in this checkout"

log="$(mktemp)"; trap 'rm -f "$log"' EXIT

ROOT="$ROOT" "$PY" - >"$log" 2>&1 <<'PY'
import os, sys
from pathlib import Path

ROOT = Path(os.environ["ROOT"])
sys.path.insert(0, str(ROOT))

from twin import model_permission as mp
from twin import record_skill_scores as rss
from twin.skills import load_scores, min_items_for, threshold_for

fails = 0
def out(ok, msg):
    global fails
    fails += 0 if ok else 1
    print(("PASS: " if ok else "FAIL: ") + msg)

SCORES = load_scores()
READINGS = mp.load_head_readings()
FACTS = {metric: rss.corpus_facts(metric) for metric in rss.METRICS}


FITTED = rss.fitted_models()


def permission(skill, model_version, scores=None, facts=None, readings=None, seam=True, fitted=None,
               threshold=None, min_items=None):
    facts = facts or FACTS[skill]
    return mp.permission_for(
        skill, model_version,
        scores=SCORES if scores is None else scores,
        corpus_digest_now=facts["corpus_digest"],
        threshold_now=threshold_for(skill) if threshold is None else threshold,
        min_items_now=min_items_for(skill) if min_items is None else min_items,
        baseline=facts["baseline"],
        variance=facts["variance"],
        readings=READINGS if readings is None else readings,
        seam_crossed=seam,
        fitted_models=FITTED if fitted is None else fitted,
    )


# -- 0: the baseline is DERIVED, and it reproduces a number measured independently -------------
# Ticket 04 measured two constant baselines by hand, on the same two corpora, before this module
# existed: signal-classify 0.913 from "always economic", and causal-claims 1.000 from the
# elasticity constant 0.375. `frozen_field_baseline()` derives both from the corpus with no
# skill named in it. Two independent routes to the same number is the only reason to believe
# either, and it is what stops this module's bar being a number somebody chose.
for metric, expected, field in (("signal-classify", 0.913, "steep"), ("causal-claims", 1.000, "edge.elasticity.mode")):
    got = FACTS[metric]["baseline"]
    out(abs(got.score - expected) < 0.001 and got.frozen_field == field,
        "the derived baseline for %-16s is %.3f on %s, against ticket 04's hand-measured %.3f on %s"
        % (metric, got.score, got.frozen_field, expected, field))

# The reference answers the baseline grants the other fields from must themselves be correct, or
# the baseline is understated and the bar is too easy. Printed as a number, per metric.
weak = [m for m in rss.METRICS if FACTS[m]["reference_score"] < 1.0]
out(not weak,
    "every metric's reference answer set scores 1.000 on its own corpus, so a frozen-field "
    "baseline grants the other fields CORRECTLY (weak: %s)" % (sorted(weak) or "none"))


# -- 1, 2, 5, 9: the table, every recorded model against every metric --------------------------
versions = sorted({str(row["model_version"]) for row in SCORES})
out(bool(versions), "the score log records at least one model version to grade (%d: %s)" % (len(versions), ", ".join(versions)))

granted, table = [], []
for metric in rss.METRICS:
    for version in versions:
        perm = permission(metric, version)
        table.append((metric, version, perm))
        if perm.granted:
            granted.append((metric, version))
print("PERMISSIONS: %d granted of %d (metric, model version) pairs" % (len(granted), len(table)))
for metric, version, perm in table:
    refused = ",".join(str(c.item) for c in perm.refusals) or "-"
    print("  %-30s %-18s %-8s refused by item(s): %s" % (metric, version, "GRANTED" if perm.granted else "refused", refused))

# Every pair is decided. A pair that produced no conditions at all would print `refused` above
# and mean "nothing was asked", which is the shape item 8 refuses in a model.
out(all(len(p.conditions) == 7 for _, _, p in table),
    "every one of the %d pairs was graded on all 7 model-side conditions (items 1, 2, 5, 6, 8, 9 and 10; "
    "items 3, 4 and 7 are properties of the claim document and are graded below)" % len(table))

# The measured verdict on the two real candidates, stated as a sentence rather than left implicit.
laya = [p for m, v, p in table if v.startswith("laya-")]
out(laya and not any(p.granted for p in laya),
    "the candidate model holds no permission on any of the %d metrics: %s"
    % (len(laya), "; ".join(sorted({f"item {c.item}" for p in laya for c in p.refusals})) or "nothing refused it"))
# And the incumbent, which the first run of the nine granted on five of seven metrics until
# condition 10 was added. It is scored on the corpus it was fitted on, and the estate says so.
incumbent = [p for m, v, p in table if v == rss.HEURISTIC_MODEL_VERSION]
out(incumbent and not any(p.granted for p in incumbent),
    "the incumbent heuristic holds no permission either, on any of the %d metrics: its corpus "
    "kind is %r, which twin/evolution_judge.py defines as fitted on the corpus it is graded "
    "against (item 10)" % (len(incumbent), FITTED.get(rss.HEURISTIC_MODEL_VERSION)))


# -- the negative controls: each condition refuses when it should -------------------------------
FAKE = "fixture-model-1.0.0"
facts = FACTS["gameplay-lens"]           # threshold 0.65, baseline 0.333, every read field varies
good_row = {"skill": "gameplay-lens", "model_version": FAKE, "score": 0.95,
            "threshold": 0.65, "corpus_digest": facts["corpus_digest"], "recorded_at": "2026-09-21T00:00:00Z",
            # A fabricated row: it claims the minimum gameplay-lens states, which the real corpus
            # does not yet hold. The positive control needs a measurable run to grant anything.
            "min_items": min_items_for("gameplay-lens"), "total": min_items_for("gameplay-lens"),
            "measured_count": min_items_for("gameplay-lens"), "outcome": "pass",
            # Eco-system ticket 118: item 1 grades the attributable rate, so a granted row needs one.
            "attributable_rate": 0.95}

# POSITIVE control first. A rule that refuses everything passes every negative control there is.
perm = permission("gameplay-lens", FAKE, scores=[good_row], facts=facts, readings=[], fitted={})
out(perm.granted and perm.permits(mp.JUDGE),
    "POSITIVE control: a fabricated model that clears all six model-side conditions IS granted, "
    "so the rule is not simply refusing everything (%s)" % perm.why())

def refused_by(item, row=None, facts_=None, readings=None, seam=True, fitted=None, threshold=None, label=""):
    perm = permission("gameplay-lens", FAKE, scores=[row or good_row], facts=facts_ or facts,
                      readings=readings if readings is not None else [], seam=seam,
                      fitted=fitted if fitted is not None else {}, threshold=threshold)
    hit = [c for c in perm.refusals if c.item == item]
    out(bool(hit) and not perm.granted,
        "NEGATIVE control item %d: %s -> %s" % (item, label, hit[0].detail if hit else "NOT refused"))

refused_by(1, row={**good_row, "score": 0.10, "attributable_rate": 0.10}, label="a score under the versioned threshold")
# ...and item 1 reads the bar in the TREE, not the one the row happens to carry. A raised
# threshold must not be cleared by a score that was graded against the old one.
refused_by(1, row={**good_row, "threshold": 0.20}, label="a score recorded against a bar the threshold file no longer sets")
# ...and item 1 refuses a run below the minimum corpus its threshold states (ticket 112), even
# with a perfect score. This is the review's reproduction: a candidate never fitted, 3 items.
refused_by(1, row={**good_row, "score": 1.0, "total": 3, "measured_count": 3, "attributable_rate": 1.0,
                   "outcome": "not-measurable", "passed": False},
           label="a perfect score on 3 items, below the stated minimum, recorded as not-measurable")
refused_by(1, row={k: v for k, v in {**good_row, "total": 3}.items() if k not in ("outcome", "min_items", "measured_count")},
           label="a legacy row with no outcome, 3 items against the minimum the tree states today")
# ...and item 1 grades the attributable rate, not the score (eco-system ticket 118). A score that
# clears the bar on answers whose stated basis was wrong clears nothing, and a row with no rate
# at all may rest on luck, so it is refused as well.
refused_by(1, row={**good_row, "score": 0.95, "attributable_rate": 0.40, "wrong_basis": 5},
           label="a score of 0.950 whose attributable rate is 0.400, the rest right on a wrong basis")
refused_by(1, row={k: v for k, v in good_row.items() if k != "attributable_rate"},
           label="a row that records no attributable rate, as every row before ticket 118 does")
refused_by(2, row={**good_row, "corpus_digest": "0" * 64}, label="a scoring run against a corpus the tree no longer holds")
refused_by(5, row={**good_row, "model_version": "somebody-else-2.0.0"}, label="no recorded score at all; absence is not consent")
refused_by(6, seam=True and False, label="the seam did not run, so nothing was checked")
refused_by(9, row={**good_row, "score": facts["baseline"].score}, label="a score exactly equal to the corpus's best constant answer")
refused_by(10, fitted={FAKE: mp.FITTED_CORPUS_KIND}, label="a score recorded on the corpus the model was fitted on")

# Item 8, twice: a constant field measured live, and a constant head recorded for a model this
# gate cannot run. Both are the same defect, found in two unrelated tools (ticket 11 call 14).
flat = dict(facts); flat["variance"] = {"opportunities": 1}
refused_by(8, facts_=flat, label="a field the scorer reads that took one distinct value across the corpus")
refused_by(8, readings=[mp.HeadReading(FAKE, "act_probability", 279, 1, "ticket 04")],
           label="a recorded head that read one distinct value on all 279 calls")
# ...and the absence of any variance at all is refused too, for the same reason absence of a
# score is: an unmeasured head is not a varying one.
perm = mp.permission_for("gameplay-lens", FAKE, scores=[good_row], corpus_digest_now=facts["corpus_digest"],
                         baseline=facts["baseline"], variance=None, readings=[], fitted_models={})
out(any(c.item == 8 for c in perm.refusals),
    "NEGATIVE control item 8: no variance measured or recorded at all -> refused, because an "
    "unmeasured head is not a varying one")

# The real recorded head is the one that matters: Laya's act_probability, n=279, distinct=1.
recorded_constant = [r for r in READINGS if r.constant]
out(len(recorded_constant) >= 1,
    "twin/model-head-readings.yaml records %d constant head(s) a permission must refuse: %s"
    % (len(recorded_constant), ", ".join(f"{r.model_version}/{r.head} ({r.distinct} distinct in {r.n})" for r in recorded_constant)))


# -- item 4: judging only, never merging --------------------------------------------------------
perm = permission("gameplay-lens", FAKE, scores=[good_row], facts=facts, readings=[], fitted={})
out(perm.granted and not perm.permits(mp.MERGE) and perm.covers == mp.COVERS,
    "item 4: a GRANTED permission covers %s and refuses %r, so the permission itself cannot be "
    "read as covering the merge" % (sorted(perm.covers), mp.MERGE))
out(not permission("gameplay-lens", "nobody-0.0.0").permits(mp.JUDGE),
    "item 4: a refused permission covers nothing at all, so a caller reading covers() cannot act on one")

# Nothing in this hub merges a claim pull request. The permission is about judging; the merge is
# the human act, and a workflow that merged would route around that with no permission involved.
merging = []
for path in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
    text = path.read_text(encoding="utf-8")
    if "pr merge" in text or "merge_pull_request" in text or "gh pr merge" in text:
        merging.append(path.name)
clock_merges = "pr merge" in (ROOT / "talk" / "local-clock.sh").read_text(encoding="utf-8")
out(not merging and not clock_merges,
    "item 4: no workflow in .github/workflows and not talk/local-clock.sh merges a pull request "
    "(workflows that do: %s; the clock: %s)" % (merging or "none", "merges" if clock_merges else "does not"))


# -- item 6: the seam, and the clock derived rather than believed --------------------------------
for marker in mp.GITHUB_CLOCK_MARKERS:
    clock, why = mp.derive_clock("local", {marker: "true"})
    out(clock == mp.GOVERNED_CLOCK and "not believed" in why,
        "item 6: %s in the environment makes the clock %r even though the caller said 'local'" % (marker, clock))
clock, _ = mp.derive_clock("local", {})
out(clock == "local", "item 6: with no GitHub marker the caller's own word stands, so the local clock keeps ticket 92's terms")
clock, _ = mp.derive_clock("github", {})
out(clock == "github", "item 6: a caller may declare a github clock without a marker; declaring one is never refused, only denying one is")

# The only way left to lie about the clock is to unset the markers inside the workflow. Nothing
# in the tree does, and this is the assertion that keeps it that way.
tampering = []
for path in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()
        for marker in mp.GITHUB_CLOCK_MARKERS:
            if stripped.startswith(f"{marker}:") or f"unset {marker}" in stripped or f"{marker}=" in stripped:
                tampering.append(f"{path.name}:{number}")
out(not tampering,
    "item 6: no workflow sets, clears or exports any of %s, so a GitHub run cannot present itself "
    "as another clock (%s)" % (", ".join(mp.GITHUB_CLOCK_MARKERS), tampering or "none found"))

# The seam is a real function in a real file, and the clock runs it out of a tree the model
# could not write to. Both halves asserted against the files, never against this script's prose.
seam_file, seam_fn = mp.SEAM.split("::")
validator = ROOT / seam_file
out(validator.is_file() and f"def {seam_fn}(" in validator.read_text(encoding="utf-8"),
    "item 6: the seam %s exists and holds %s()" % (seam_file, seam_fn))
source = validator.read_text(encoding="utf-8")
out("clock" in source and "check_claim_document" in source and "model_permission" in source,
    "item 6: the seam reads the permission off twin/model_permission.py rather than restating it, "
    "so a rule that moves moves here too")
clock_sh = (ROOT / "talk" / "local-clock.sh").read_text(encoding="utf-8")
out('"$judge/.claude/skills/$skill/$validator_rel"' in clock_sh,
    "item 6: talk/local-clock.sh runs the validator out of $judge, the tree copied BEFORE the "
    "child model started, so the model cannot edit the thing that judges it")
# Every invocation of the validator in the clock states the clock it ran on. The count is
# asserted, not the presence: one unflagged call is the route around, and "at least one call
# has the flag" would not see it.
# EVERY validator the clock's steps table names must take the flag, or a step added later
# reaches a model-made artefact without crossing the seam. This is item 6's "no path" in its
# general form, and it is the leg that caught the regression: --clock was first passed to the
# forecast validator, which did not accept it, and the derive step went red.
rows = [line for line in clock_sh.splitlines() if line.strip().startswith('"') and line.count("|") >= 5]
seamless = []
for line in rows:
    fields = line.strip().strip('"').split("|")
    skill, validator_rel = fields[1], fields[4]
    target = ROOT / ".claude" / "skills" / skill / validator_rel
    if not target.is_file():
        continue          # a row whose skill is not shipped yet; the clock records that by name
    if '"--clock"' not in target.read_text(encoding="utf-8"):
        seamless.append(f"{skill}/{validator_rel}")
out(len(rows) >= 2 and not seamless,
    "item 6: all %d validator(s) the clock's steps table names accept --clock, so no step reaches "
    "a model-made artefact without crossing the seam (%s)" % (len(rows), seamless or "none missing it"))

calls = clock_sh.count('"$validator" "$wt/$f" --twin "$judge"')
flagged = clock_sh.count('"$validator" "$wt/$f" --twin "$judge" --headless --clock local')
out(calls > 0 and calls == flagged,
    "item 6: all %d of the clock's validator invocations pass --headless --clock local, so the "
    "model never chooses whether the seam runs and never states its own clock; that is trdrbot "
    "defect I-68's whole failure, closed (%d of %d flagged)" % (calls, flagged, calls))


# -- items 3, 4 and 7 on the claim document ------------------------------------------------------
def claim_doc(**run):
    base = {"skill": "classify-and-judge", "clock": "github", "model_version": FAKE, "declined": []}
    base.update(run)
    return {"schema": "twin.headline-claim/v1", "org": "driftwood", "run": base,
            "claims": [{"id": "c1", "kind": "binding", "component": "x", "evidence_grade": 5,
                        "claimed_by": "signal-classify (skill)", "evidence": "e", "price_eligible": False}]}

def lookup_granted(skill, version):
    return permission("gameplay-lens", FAKE, scores=[{**good_row, "skill": "gameplay-lens"}], facts=facts,
                      readings=[], fitted={})

def lookup_real(skill, version):
    return permission(skill, version)

bad = mp.check_claim_document(claim_doc(model_version=None), "github", lookup_granted)
out(any("item 3" in line for line in bad), "item 3: a GitHub-clock claim file that records no model_version is refused")
bad = mp.check_claim_document(claim_doc(), "human", lookup_real)
out(bad == [], "item 3: a human-run claim file is not governed by this rule at all, so the ordinary path is untouched")
bad = mp.check_claim_document(claim_doc(), "local", lookup_real)
out(bad == [], "item 4: a local-clock claim file keeps ecosystem ticket 92's own terms; this rule does not reopen them")

doc = claim_doc()
doc["claims"][0]["kind"] = "override"
bad = mp.check_claim_document(doc, "github", lookup_granted)
out(any("item 4" in line for line in bad), "item 4: an override from a model on a GitHub clock is refused; grade 4 is a human's")
doc = claim_doc()
doc["claims"][0]["price_eligible"] = True
bad = mp.check_claim_document(doc, "github", lookup_granted)
out(any("item 4" in line for line in bad), "item 4: a price-eligible claim from a model on a GitHub clock is refused")

doc = claim_doc()
del doc["run"]["declined"]
bad = mp.check_claim_document(doc, "github", lookup_granted)
out(any("item 7" in line for line in bad),
    "item 7: a GitHub-clock claim file that counts no declines is refused; an empty list is an answer and a missing key is not")
doc = claim_doc(declined=[{"subject": "a statement with no good component"}])
bad = mp.check_claim_document(doc, "github", lookup_granted)
out(any("item 7" in line for line in bad), "item 7: a declined row with no reason is refused; an uncounted decline is the whole defect")

# The rate itself, and the one thing it must never do: report 100% because nothing was counted.
empty = mp.Exercise(judged=0, declined=0)
out(empty.rate is None and "undefined" in empty.describe(),
    "item 7: an exercise rate over zero rows is undefined and says so, never 100%% (%s)" % empty.describe())
worked = mp.exercise_of(claim_doc(declined=[{"subject": "s", "reason": "r"}, {"subject": "t", "reason": "r"}]))
out(worked.judged == 1 and worked.declined == 2 and abs(worked.rate - 1/3) < 1e-9,
    "item 7: the rate is computed from the file's own counted rows (%s)" % worked.describe())

# And the estate's own claim files at rest, so the number is this estate's and not a fixture's.
# ROOT.glob("**/...") walks .estate-clone too, so this is one list and not two added together.
# Each file is graded on the clock it says it ran on, because the environment this check runs in
# is not the environment that wrote them; a file claiming a github clock and counting no
# declines is a red here, whatever wrote it.
import yaml
at_rest = sorted(ROOT.glob("**/twin/claims/*.claim.yaml"))
judged = declined = ungoverned = 0
at_rest_bad = []
for path in at_rest:
    try:
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:  # noqa: BLE001 - an unreadable claim file is a red, named
        at_rest_bad.append(f"{path}: could not be read ({exc})")
        continue
    declared = str((doc.get("run") or {}).get("clock") or "") or None
    if declared != mp.GOVERNED_CLOCK:
        ungoverned += 1
        continue
    at_rest_bad.extend(f"{path.name}: {line}" for line in mp.check_claim_document(doc, mp.GOVERNED_CLOCK, lookup_real))
    exercise = mp.exercise_of(doc)
    judged += exercise.judged
    declined += exercise.declined
estate = mp.Exercise(judged=judged, declined=declined)
print("AT REST: %d claim file(s) under twin/claims/ in this checkout and its estate clone, "
      "%d of them on a governed clock; %s" % (len(at_rest), len(at_rest) - ungoverned, estate.describe()))
out(not at_rest_bad,
    "every claim file at rest that says it ran on a GitHub clock satisfies items 3, 4 and 7 and "
    "holds a granted permission (%s)" % (at_rest_bad or "none is on a governed clock today"))

# A GitHub-clock file that clears every one of items 3, 4 and 7 with a granted permission passes.
out(mp.check_claim_document(claim_doc(), "github", lookup_granted) == [],
    "POSITIVE control: a GitHub-clock claim file naming its model, counting its declines, "
    "claiming no override and holding a granted permission is accepted")


# -- reported, never graded: the thresholds against their own corpora ----------------------------
print("THRESHOLDS AGAINST THEIR OWN CORPUS'S BEST CONSTANT ANSWER (reported, not graded):")
weakest = 0
for metric in rss.METRICS:
    f = FACTS[metric]
    t = threshold_for(metric)
    verdict = "CANNOT DETECT A MODEL THAT LEARNED NOTHING" if t <= f["baseline"].score else "above its baseline"
    weakest += 1 if t <= f["baseline"].score else 0
    print("  %-30s n=%-3d threshold=%.2f  baseline=%.3f  %s   [%s]"
          % (metric, f["total"], t, f["baseline"].score, verdict, f["baseline"].description))
print("WEAK THRESHOLDS: %d of %d sit at or below the best constant answer their own corpus admits. "
      "Item 9 refuses such a score anyway, so no permission rests on them. The corpus is what is "
      "short -- the minimum each threshold states (min_items, eco-system ticket 112) is "
      "printed by verify-corpus-size.sh, and item 1 refuses a run below it." % (weakest, len(rss.METRICS)))

print("SUBTOTAL: %d observed false" % fails)
sys.exit(1 if fails else 0)
PY
rc=$?
cat "$log"
[ "$rc" -le 1 ] || skip "the permission rule could not be imported or run: $(tail -1 "$log")"

if [ "$rc" -eq 0 ]; then
  echo "PASS: the model-judging permission grades all ten conditions (ticket 05's nine, plus a fitted-corpus condition the first run of the nine forced), each with a negative control and the rule with a positive one; $(sed -n 's/^PERMISSIONS: //p' "$log") hold a permission today; the clock is derived from the environment and no workflow can present itself as another; the seam is $(cd "$ROOT" && "$PY" -c 'import sys; sys.path.insert(0,"."); from twin.model_permission import SEAM; print(SEAM)'), run by talk/local-clock.sh out of a tree the model cannot write to; $(sed -n 's/^WEAK THRESHOLDS: //p' "$log" | cut -d. -f1) (reported, not graded)"
  exit 0
fi
echo "FAIL: the model-judging permission observed false; see the lines above"
exit 1
