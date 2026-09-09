#!/usr/bin/env bash
# Ecosystem ticket 51: the supply-constraint actor path, and the resolution question and
# pre-registration date of a scenario-library entry and an override. Ticket 23 deferred both to a
# grilling; ADR-0025 makes them the assistant's to decide, and this script is what measures the
# decisions instead of asserting them.
#
# WHAT IT GRADES -- the SERVED artefact and the OPERATION that reaches it (ticket 98's rule):
#
#   the artefact   every twin/orgs/<org>/scenarios/*.yaml and every `kind: override` claim on
#                  refs/remotes/origin/main of every adopter carrying a twin overlay, read off
#                  the ref's committed tree with `git archive`, never off a working tree;
#   the operation  a human merging the pull request that lands one. Registration is the LAST
#                  first-parent write onto origin/main, `twin/derived_forecast.py`'s own
#                  `first_reached()` (imported, never re-implemented), so a question or an
#                  override rewritten after it landed re-registers on the day of the rewrite --
#                  ticket 93's review F1, applied to the QUESTION and to the OVERRIDE. Ticket 93
#                  made the forecast and the answer key immune to a silent rewrite and nothing
#                  measured the third leg: edit a scenario's proposition, horizon or words after
#                  a forecast is registered against it and every score moves.
#
# WHAT IT MEASURES RATHER THAN CITES. Everything this seam says about DATES it derives from git.
# Everything it said about REACHABILITY it used to derive from reading `twin/blast.py` -- and a
# module that reasons about a traversal without running it was wrong about it twice (review F1: a
# causal edge was refused reachability, though radius() walks `influences` forwards; review F2: a
# two-hop dependency path was reported as "no dependency between them, in either direction"). So
# the traversal is RUN here, over the fixture graph with the planted `needs` entries and without
# them, and the unpriced set is asserted as a SET.
#
# The five rules, each a refusal by name:
#   1. a scenario declares a `horizon` -- one is optional in twin/schema.py, and without one the
#      entry names no date an outcome falls on and none a registration could be strictly before;
#   2. that horizon is strictly AFTER the entry's own `at`, or nothing could ever be
#      pre-registered against it;
#   3. its `proposition` is one the world layer carries;
#   4. its own registration date is strictly before its own horizon (rule 2's measurement, on
#      git rather than on the file's own words);
#   5. an `override` claim names a component this model carries, is scoreable only THROUGH the
#      proposition of a scenario that names that component -- never on its own coordinate, which
#      is an interpretive ordinal position with no published answer key -- and registers before
#      that scenario's horizon. An override no scenario reaches is UNSCOREABLE WITH A REASON,
#      which is twin/scoring.py's own first-class result and never a zero.
#
# THE ACTOR PATH, measured rather than argued. `nb-refining-capacity -> pq-cryptanalysis` is not a
# twin `needs` edge, because neither id is a component of any twin model: both are rows in
# platform's wardley/intel/market-intel.json, and BOTH name the same `links_risk`
# (`pq-harvest-now-decrypt-later`, a FAIR risk id, not a component), so neither row points at the
# other. Every run prints those rows off platform's served ref. And the ruling holds whatever the
# graph says: `twin/registration.py`'s `admits()` grades a relation, and no relation of any type
# -- causal, structural or absent -- moves an `evolution_position`, an `evidence_grade`, a
# `weight` or a `probability`. The reopened ordinal ruling (ecosystem ticket 93 on twin 08 Q1)
# admits ONE operation on grades, an order statistic over a derivation's own signals; a coordinate
# move is neither that operation nor on that axis.
#
# --selfcheck (and the first half of every run): the whole seam over THROWAWAY repositories built
# by registration_fixture.py, which PLANTS the pair as components with the `needs` edge between
# them precisely because no real model has it. Every line of that half says fixture; the platform
# intel rows are read only on the real-estate half, and the fixture half says so rather than
# printing a green over a could-not-look.
#
# Exit 0 observed true; 3 could not look, with the reason on the last line; 1 observed false.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
SELFCHECK=0
for a in "$@"; do case "$a" in --selfcheck) SELFCHECK=1;; esac; done

PY="$ROOT/.venv/bin/python"
if [ ! -x "$PY" ]; then
  PY=python3
  "$PY" -c 'import yaml' 2>/dev/null || { echo "SKIP: no .venv and python3 lacks pyyaml; the twin package cannot be imported"; exit 3; }
fi
command -v git >/dev/null 2>&1 || { echo "SKIP: git is needed: a registration date is read off git history"; exit 3; }
[ -f "$ROOT/twin/VERSION" ] || { echo "SKIP: no twin/VERSION in $ROOT; this is not a checkout of the hub"; exit 3; }
FIXTURE="$HERE/registration_fixture.py"
[ -f "$FIXTURE" ] || { echo "FAIL: $FIXTURE is missing: the seam has no throwaway estate to run over"; exit 1; }

TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
fail() { echo "FAIL: $*"; exit 1; }
check() { (cd "$ROOT" && "$PY" -m twin.registration check --hub "$ROOT" "$@"); }
fx() { "$PY" "$FIXTURE" "$@" >/dev/null || fail "could not build the fixture ($*)"; }

# 1. the planted estate is clean: one resolvable question, one override scoreable through it
fx build "$TMP/clean"
check --estate "$TMP/clean" >"$TMP/clean.out" 2>&1
[ $? -eq 0 ] || fail "the clean fixture did not PASS: $(tail -1 "$TMP/clean.out")"
grep -q 'scoreable through planted-supply-2026' "$TMP/clean.out" || fail "the override was not read as scoreable through the question that names its component"
grep -q '1 override(s), 1 scoreable' "$TMP/clean.out" || fail "the override count was not printed as a number"

# 2. RED (a): the actor path. The pair is PLANTED here as two components with the `needs` edge
#    between them -- no real model has either -- and the ruling still refuses every move but
#    reachability, each by name. `refuse_move` is the callable form of the ruling.
#
#    What the ruling says about REACHABILITY is measured against `twin/blast.py`'s own traversal,
#    run over the same model, and never against the admission's own sentence (review F1, F2, F4:
#    the module reasoned about a traversal it had never run, and was wrong twice in the same way).
(cd "$ROOT" && EST="$TMP/clean" "$PY" - <<'PY'
import os, pathlib, sys
sys.path.insert(0, os.getcwd())
from twin import registration as reg
model = reg.read_model(pathlib.Path(os.environ["EST"]) / "driftwood", "driftwood")
adm = reg.admits(model, *reg.SUPPLY_CONSTRAINT_PATH)
assert adm.verdict == reg.UNPRICED_STRUCTURAL, adm.verdict
reg.refuse_move(adm, "reachability")          # the one thing it does move
for asked in ("evolution_position", "evidence_grade", "weight", "probability", "magnitude", "price"):
    try:
        reg.refuse_move(adm, asked)
    except reg.RegistrationError as exc:
        assert asked in str(exc), (asked, str(exc))
    else:
        raise SystemExit(f"a {reg.UNPRICED_STRUCTURAL} relation was allowed to move {asked!r}")
try:
    reg.refuse_move(adm, "everything")
except reg.RegistrationError as exc:
    assert "is not one of the things a relation could move" in str(exc), str(exc)
else:
    raise SystemExit("a move nobody named was admitted by omission")

# A REAL causal edge, planted rather than hand-constructed as an Admission: it moves a MAGNITUDE
# and it moves REACHABILITY -- twin/blast.py walks `influences` forwards, so a causal edge is a
# dependency path as well as a priced one -- and it still moves no coordinate. Measured on the
# BLAST SET, which is the thing the claim is about.
before = reg.reached_set(model, "nb-refining-capacity")
model.edges["planted-influence"] = {
    "id": "planted-influence", "type": "influences",
    "from": "nb-refining-capacity", "to": "island-thing",
    "sign": "increases", "lag_days": 30,
    "elasticity": {"min": 0.1, "mode": 0.2, "max": 0.3}, "evidence_grade": 2,
}
after = reg.reached_set(model, "nb-refining-capacity")
if [c for c, _ in after] != sorted([c for c, _ in before] + ["island-thing"]):
    raise SystemExit(f"a planted influences edge did not move the blast set: {before} -> {after}")
causal = reg.admits(model, "nb-refining-capacity", "island-thing")
assert causal.verdict == reg.PRICED_CAUSAL, causal.verdict
reg.refuse_move(causal, "magnitude")
reg.refuse_move(causal, "reachability")
for asked in ("evolution_position", "evidence_grade", "weight", "probability"):
    try:
        reg.refuse_move(causal, asked)
    except reg.RegistrationError:
        pass
    else:
        raise SystemExit(f"a {reg.PRICED_CAUSAL} relation was allowed to move {asked!r}")
PY
) || fail "the needs-edge ruling admitted something it does not admit"

# 2b. The module's ONE affirmative claim, converted from a citation into a measurement. The
#     fixture builds the same overlay twice -- with the planted `needs` entries and without -- and
#     the unpriced reachability set moves from EMPTY to two components. Nothing in this seam ran
#     the traversal before review F4: everything it said about dates it derived from git, and
#     everything it said about reachability it derived from reading twin/blast.py.
fx build "$TMP/no-needs" --no-needs
(cd "$ROOT" && WITH="$TMP/clean" WITHOUT="$TMP/no-needs" "$PY" - <<'PY'
import os, pathlib, sys
sys.path.insert(0, os.getcwd())
from twin import registration as reg
with_needs = reg.read_model(pathlib.Path(os.environ["WITH"]) / "driftwood", "driftwood")
without = reg.read_model(pathlib.Path(os.environ["WITHOUT"]) / "driftwood", "driftwood")
moved = reg.reached_set(with_needs, "nb-refining-capacity")
empty = reg.reached_set(without, "nb-refining-capacity")
if empty != ():
    raise SystemExit(f"with every `needs` removed the traversal still reached {empty}")
if moved != (("pq-cryptanalysis", 1), ("unwatched-thing", 2)):
    raise SystemExit(f"the planted needs entries did not produce the expected blast set: {moved}")
print(f"    fixture: the unpriced reachability set from 'nb-refining-capacity' is {list(empty)} "
      f"without the planted needs entries and {[f'{c} (depth {d})' for c, d in moved]} with them")
# and the two-hop end is REACHED without being ADJACENT: the distinction review F2 found being
# reported as "there is no dependency between them, in either direction"
two_hops = reg.admits(with_needs, "unwatched-thing", "nb-refining-capacity")
if two_hops.verdict != reg.REACHABLE_NOT_ADJACENT:
    raise SystemExit(f"a two-hop dependency path was graded {two_hops.verdict}")
reg.refuse_move(two_hops, "reachability")
for asked in ("magnitude", "price", "evolution_position", "evidence_grade", "weight", "probability"):
    try:
        reg.refuse_move(two_hops, asked)
    except reg.RegistrationError:
        pass
    else:
        raise SystemExit(f"a {reg.REACHABLE_NOT_ADJACENT} relation was allowed to move {asked!r}")
# a pair the traversal genuinely cannot connect still says so, and says it as a measurement
island = reg.admits(with_needs, "island-thing", "nb-refining-capacity")
if island.verdict != reg.NO_RELATION:
    raise SystemExit(f"an unconnected pair was graded {island.verdict}")
if "at no depth up to its max_depth of" not in island.refused["reachability"]:
    raise SystemExit(f"the no-relation refusal is not bounded by the traversal: {island.refused['reachability']}")
PY
) || fail "the reachability set did not move when the planted needs edge did"

# 3. RED (b): a scenario whose horizon is its own authoring date. Measured ACCEPTED by
#    twin/schema.py before this ticket -- `validate('scenario', ...)` returns cleanly -- so the
#    entry merged and nothing said that nothing could ever be registered against it.
fx build "$TMP/same-day"
fx bad-horizon "$TMP/same-day"
check --estate "$TMP/same-day" >"$TMP/same-day.out" 2>&1
[ $? -eq 1 ] || fail "a question that resolves on the day it was asked was admitted: $(tail -1 "$TMP/same-day.out")"
grep -q "horizon 2026-01-01 is not after its own at 2026-01-01" "$TMP/same-day.out" \
  || fail "the same-day question was refused for the wrong reason: $(grep 'FAIL:' "$TMP/same-day.out" | head -1)"
grep -q "nothing could ever be registered against it" "$TMP/same-day.out" \
  || fail "the refusal does not say why a same-day horizon can never be pre-registered against"
(cd "$ROOT" && "$PY" -c "
import sys, yaml; sys.path.insert(0, '.')
from twin import schema
doc = yaml.safe_load(open('$TMP/same-day/driftwood/twin/orgs/driftwood/scenarios/planted-same-day-2026.yaml'))
schema.validate('scenario', doc, 'planted')
") || fail "the same-day scenario no longer validates: the RED this refusal exists for cannot be reproduced"

# 4. RED (c): the override's number, rewritten after it landed on the served ref. Ticket 93's F1
#    applied to an override: the rewrite is a NEW claim and registers on the day of the rewrite,
#    with BOTH dates printed, so the limit stays a number.
fx build "$TMP/rewritten"
fx rewrite-override "$TMP/rewritten"
check --estate "$TMP/rewritten" >"$TMP/rewritten.out" 2>&1
[ $? -eq 1 ] || fail "an override rewritten after it landed kept its registration: $(tail -1 "$TMP/rewritten.out")"
grep -q "registered on 2026-07-20, not before 2026-06-30" "$TMP/rewritten.out" \
  || fail "the rewritten override was not registered on the day of the rewrite: $(grep 'FAIL:' "$TMP/rewritten.out" | head -1)"
grep -q "reached refs/remotes/origin/main 2026-02-01" "$TMP/rewritten.out" \
  || fail "the original arrival date is no longer printed: the limit stopped being a number"
grep -q "rewritten after it landed" "$TMP/rewritten.out" || fail "the rewrite is not named on the override's line"

# 5. the same measurement on the QUESTION, which is the leg ticket 93 did not have: a scenario
#    rewritten after its own horizon has moved every score taken against it
fx build "$TMP/moved"
fx rewrite-question "$TMP/moved"
check --estate "$TMP/moved" >"$TMP/moved.out" 2>&1
[ $? -eq 1 ] || fail "a question rewritten after its own horizon was admitted: $(tail -1 "$TMP/moved.out")"
grep -q "the resolution question of scenario 'planted-supply-2026' registered on 2026-07-20" "$TMP/moved.out" \
  || fail "the rewritten question was not re-registered on the day of the rewrite: $(grep 'FAIL:' "$TMP/moved.out" | head -1)"
grep -q "moves every score taken against it" "$TMP/moved.out" \
  || fail "the refusal does not say what a rewritten question does to the scores already taken"
grep -q "question: 'Does the planted supplier fail inside the horizon?' -> 'A DIFFERENT question" "$TMP/moved.out" \
  || fail "the rewrite does not say WHICH field moved: $(grep 'FAIL:' "$TMP/moved.out" | head -1)"

# 5b. and the same measurement on a rewrite that appended a NOTE and left the question alone. It
#     re-registers all the same -- the rule is blob identity -- but a report that could not tell
#     the two apart is what ticket 93's review G2 refused for a forecast's numbers. The niobium
#     entry in this ticket's own driftwood PR is exactly this shape.
fx build "$TMP/noted"
fx append-note "$TMP/noted"
check --estate "$TMP/noted" >"$TMP/noted.out" 2>&1
grep -q "none of proposition, horizon, question moved" "$TMP/noted.out" \
  || fail "an appended note was reported as the question moving: $(grep 'FAIL:' "$TMP/noted.out" | head -1)"
grep -q "rewritten after it landed" "$TMP/noted.out" \
  || fail "an appended note stopped counting as a rewrite: the registration rule is blob identity"

# 6. an override no question reaches is UNSCOREABLE WITH A REASON, not a zero and not a failure
fx build "$TMP/orphan"
fx orphan-override "$TMP/orphan"
check --estate "$TMP/orphan" >"$TMP/orphan.out" 2>&1
[ $? -eq 0 ] || fail "an override nothing resolves was graded as a failure rather than as unscoreable: $(tail -1 "$TMP/orphan.out")"
grep -q "UNSCOREABLE -- no scenario in overlay 'driftwood' names component 'unwatched-thing'" "$TMP/orphan.out" \
  || fail "the orphan override was not named unscoreable with its reason"
grep -q "not a zero" "$TMP/orphan.out" || fail "the unscoreable result does not say it is not a zero"
grep -q "2 override(s), 1 scoreable" "$TMP/orphan.out" || fail "the scoreable count did not separate the two overrides"

# 7. the coordinate is never the thing scored, and the module says so on every override it reads
grep -q "an interpretive ordinal coordinate with no published answer key" "$TMP/clean.out" \
  || (cd "$ROOT" && "$PY" -m twin.registration override --adopter "$TMP/clean/driftwood" --org driftwood \
        planted-supply-position | grep -q "arithmetic on an ordinal scale") \
  || fail "nothing says the override is never scored on its own coordinate"

# 8. an override on a component the model does not carry is refused, not silently unscoreable
(cd "$ROOT" && EST="$TMP/clean" "$PY" - <<'PY'
import os, pathlib, sys
sys.path.insert(0, os.getcwd())
from twin import registration as reg
model = reg.read_model(pathlib.Path(os.environ["EST"]) / "driftwood", "driftwood")
model.claims["planted-supply-position"]["component"] = "a-component-nobody-declared"
try:
    reg.override_resolution(model, "planted-supply-position")
except reg.RegistrationError as exc:
    assert "a-component-nobody-declared" in str(exc), str(exc)
else:
    raise SystemExit("an override on a component the model does not carry was admitted")
PY
) || fail "a dangling override component was admitted"

# 9. Decision 1's factual half is a claim about PLATFORM's file, so it is graded and not only
#    printed (review F5). RED: before this, editing platform's intel so one row's links_risk names
#    the other id left the check at exit 0 -- the finding the whole decision rests on was printed
#    on every run and observed on none.
fx build "$TMP/intel"
fx platform "$TMP/intel"
check --estate "$TMP/intel" >"$TMP/intel.out" 2>&1
[ $? -eq 0 ] || fail "a platform whose two rows both name the FAIR risk was graded false: $(tail -1 "$TMP/intel.out")"
grep -q "which is a FAIR risk id and not a component, so neither row points at the other" "$TMP/intel.out" \
  || fail "the intel rows were not read off the planted platform's served ref"
fx build "$TMP/intel-crossed"
fx platform-cross-linked "$TMP/intel-crossed"
check --estate "$TMP/intel-crossed" >"$TMP/intel-crossed.out" 2>&1
[ $? -eq 1 ] || fail "one intel row naming the other id left the decision's own premise ungraded: $(tail -1 "$TMP/intel-crossed.out")"
grep -q "which is the OTHER id in the pair" "$TMP/intel-crossed.out" \
  || fail "the cross-linked intel row was not named: $(grep 'FAIL:' "$TMP/intel-crossed.out" | head -1)"
grep -q "needs re-reading, not re-asserting" "$TMP/intel-crossed.out" \
  || fail "the finding does not say what a reader should do with it"

echo "PASS: offline, over throwaway repositories the fixture PLANTS (a fixture, not a real model: no twin model anywhere carries nb-refining-capacity or pq-cryptanalysis, which is the ticket's finding, so the pair is planted here as two components with a needs edge to exercise the ruling on). REACHABILITY IS MEASURED, NOT CITED: twin/blast.py's own traversal is run over the fixture graph with the planted needs entries and without them, and the unpriced set from nb-refining-capacity moves from [] to pq-cryptanalysis at depth 1 and unwatched-thing at depth 2. The planted needs edge moves that reachability and nothing else -- an evolution_position, an evidence_grade, a weight, a probability, a magnitude and a price are each refused by name; a planted causal edge moves a magnitude AND reachability (blast.py walks influences forwards) and still no coordinate; a two-hop path is reachable-not-adjacent rather than unrelated; a component on no chain is unrelated and says so as a depth-bounded measurement; and a move nobody named is refused rather than admitted by omission. A scenario whose horizon is its own authoring date validates under twin/schema.py (re-run here, so the RED is reproducible) and is refused here, because nothing could ever be registered against it. An override rewritten after it landed on the served ref registers on the day of the rewrite with both dates printed, and so does a QUESTION rewritten after its own horizon -- the leg ticket 93 did not have -- and each names WHICH field moved, so an appended note is not reported as the question changing. An override no question reaches is unscoreable with a reason rather than a zero or a failure, one on a component the model does not carry is refused, and no override is ever scored on its own coordinate. The claim Decision 1 rests on -- that platform's two intel rows name a FAIR risk and never each other -- is GRADED, not printed: a planted platform whose rows cross-link turns this half red. The REAL platform's rows are read on the real-estate half below, never here"
[ "$SELFCHECK" = 1 ] && exit 0

# --- the real estate: every adopter's origin/main ---------------------------------------------
[ -d "$ROOT/.estate-clone/platform" ] || bash "$ROOT/clone-estate.sh" >/dev/null \
  || { echo "FAIL: could not assemble .estate-clone/"; exit 1; }
log="$(mktemp)"; trap 'rm -rf "$TMP" "$log"' EXIT
(cd "$ROOT" && "$PY" -m twin.registration check --estate "$ROOT/.estate-clone" --hub "$ROOT") | tee "$log" | sed 's/^/    /'
rc=${PIPESTATUS[0]}
case $rc in
  0) echo "PASS: $(grep '^PASS:' "$log" | tail -1 | cut -c7-)";;
  3) echo "SKIP: $(grep '^SKIP:' "$log" | tail -1 | cut -c7-)";;
  *) echo "FAIL: $(grep '^FAIL:' "$log" | tail -1 | cut -c7-)";;
esac
exit "$rc"
