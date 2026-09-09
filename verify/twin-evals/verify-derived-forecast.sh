#!/usr/bin/env bash
# Ecosystem ticket 93: the twin derives a probability, pre-registered and scored. NORTH-STAR §2's
# twin row says "priced forecasts ... scored against reality"; ticket 75 Q10 (the owner, reasoned)
# said the probability may be DERIVED from signals with a model call on the owner's local clock.
# This script grades the SERVED artefact and the OPERATION that reaches it (ticket 98's rule):
#
#   the artefact   every twin/forecasts/*.forecast.yaml on refs/remotes/origin/main of every
#                  adopter that carries a twin overlay -- read off the ref's committed tree with
#                  `git archive`, never off a working tree or a ticket branch;
#   the operation  a human merging the local clock's pull request onto the adopter's main. Two
#                  first-parent committer dates are read on origin/main: when the file ARRIVED
#                  (on GitHub, the merge, dated by GitHub) and when it was LAST WRITTEN there.
#                  The pre-registration date is the LAST write and both are printed. Measuring
#                  the arrival alone measures the PATH and not the CONTENT: a forecast rewritten
#                  after it landed -- in place, by delete and re-add, or by a squash-add -- kept
#                  the original date and was scored (2026-09-09 review F1). A RENAME still costs
#                  a forecast its registration, which is the honest direction, and is kept. The
#                  answer key is immutable once it is on the ref, and two outcomes resolving one
#                  proposition are refused rather than the first sorted one silently winning
#                  (F2). Nothing the twin writes decides any of it.
#
# What it asks, per forecast: is it a forecast file the twin can read (twin/derived_forecast.py's
# rules: every probability with a perspective, a currency, a basis and the grade the schema
# allows; every derived probability resting on an observation the SERVED feed envelope carries,
# confirmed against origin/main of the feeds publisher; no level read as a probability, no
# arithmetic on ordinal grades; a recorded belief unchanged from the world model)? Was it
# pre-registered? Has its outcome date passed, and does the overlay's own outcomes/ record (which
# must itself have reached main on or after the date it says it resolved, and after the forecast)
# resolve the proposition? If so, the score is COMPUTED here, by twin/scoring.py, and printed --
# never read from a file.
#
# Limits, printed as numbers on every run: how many adopters were read and how old their
# origin/main ref is; how many adopters pin the pool feeds (0 of 3 on 2026-09-06); how many tags
# the publisher has naming either and how many of THOSE carry a signature block, read with
# `git cat-file tag` (ticket 84's rule -- `git tag --list` counts names, and two unsigned
# annotated tags used to print "2 signed tag(s)", review F3): the pool is served unpinned and
# untagged, so nothing derived from it is price-eligible (ticket 23), and every forecast says so.
# How many DISTINCT evidence grades were seen across every signal read: while that is one, the
# reopened ordinal comparison ("no stronger than its weakest signal") has nothing to compare and
# is built for the day a signal at another rung exists (F9). And how many registering commits are
# dated before their own first parent (F10) -- because the pre-registration date is a committer
# date: merged through GitHub it is GitHub's clock; a fast-forward push from a laptop would carry
# the laptop's, and this script cannot tell those two apart offline. That limit stands; a commit
# dated before the commit it sits on is an impossibility, not a clock disagreement, and is counted.
#
# The local validator is ADVISORY, and the run says so. It runs on the owner's machine in a tree
# a headless model can write to; the clock copies the twin package and the skill OUT of the hub
# before the child starts and judges with the copy, and reads the hub's own copies back (F5).
# This script, on the gate, over origin/main, is the measurement of record.
#
# --selfcheck (and the first half of every run): the whole seam over THROWAWAY repositories built
# by derived_forecast_fixture.py, with stub-claude.sh standing in for the model on the local
# clock's derive row. Every line of that half says it is a fixture; nothing in it is the twin
# having run, and its PASS grades what the check DOES, not the estate.
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
command -v git >/dev/null 2>&1 || { echo "SKIP: git is needed: pre-registration is read off git history"; exit 3; }
[ -f "$ROOT/twin/VERSION" ] || { echo "SKIP: no twin/VERSION in $ROOT; this is not a checkout of the hub"; exit 3; }
FIXTURE="$HERE/derived_forecast_fixture.py"
VALIDATOR="$ROOT/.claude/skills/derive-probability/assets/validate_forecast.py"
EXAMPLE="$ROOT/.claude/skills/derive-probability/assets/example-forecast.yaml"
[ -f "$VALIDATOR" ] || { echo "FAIL: $VALIDATOR is missing: the derive row of the local clock has no validator"; exit 1; }
[ -f "$ROOT/.claude/skills/derive-probability/SKILL.md" ] || { echo "FAIL: .claude/skills/derive-probability/SKILL.md is missing"; exit 1; }

# --- the seam over throwaway repositories -------------------------------------------------------
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
fail() { echo "FAIL: $*"; exit 1; }
check() { (cd "$ROOT" && "$PY" -m twin.derived_forecast check --hub "$ROOT" --adopter driftwood "$@"); }

# 1. a forecast merged before the horizon, an outcome merged after it: scored, by the twin's rules
"$PY" "$FIXTURE" build "$TMP/scored" >/dev/null || fail "could not build the fixture estate"
check --estate "$TMP/scored" --now 2026-09-06T00:00:00Z >"$TMP/scored.out" 2>&1
[ $? -eq 0 ] || fail "the scored fixture did not PASS: $(tail -1 "$TMP/scored.out")"
grep -q 'pre-registered: yes' "$TMP/scored.out" || fail "the fixture's forecast was not read as pre-registered"
grep -Eq 'scored .* brier=[0-9.]+ log_loss=[0-9.]+ .*computed now' "$TMP/scored.out" || fail "no score was computed: $(grep -c scored "$TMP/scored.out") scored lines"
grep -q 'carries no grade' "$TMP/scored.out" || fail "the recorded belief's absent grade was not printed as the finding it is"
grep -q '0 of 1 adopter(s) pin news or market-moves' "$TMP/scored.out" || fail "the unpinned-pool limit was not printed as a number"
# the score printed is twin/scoring.py's own, recomputed here from the same two numbers
expect="$(cd "$ROOT" && "$PY" -c 'from twin import scoring; s = scoring.score(0.27, True); print("brier=%s log_loss=%s" % (s["brier"], s["log_loss"]))')"
grep -q "$expect" "$TMP/scored.out" || fail "the printed score is not twin/scoring.py's for p=0.27 observed=True ($expect): $(grep scored "$TMP/scored.out")"

# 2. no forecast on main: could-not-look, the estate's own state
"$PY" "$FIXTURE" build "$TMP/none" --no-forecast --no-outcome >/dev/null || fail "could not build the empty fixture"
check --estate "$TMP/none" --now 2026-09-06T00:00:00Z >"$TMP/none.out" 2>&1
[ $? -eq 3 ] || fail "an estate with no forecast was not a could-not-look: $(tail -1 "$TMP/none.out")"
tail -1 "$TMP/none.out" | grep -q '^SKIP: no \*\.forecast\.yaml has reached' || fail "the no-forecast reason is not the declared one: $(tail -1 "$TMP/none.out")"

# 3. a forecast merged AFTER the horizon -- branch commit dated early, merge dated late -- is not
#    pre-registered and not scored, whatever its own run_at says
"$PY" "$FIXTURE" late "$TMP/none" >/dev/null || fail "could not merge the late forecast"
check --estate "$TMP/none" --now 2026-09-06T00:00:00Z >"$TMP/late.out" 2>&1
[ $? -eq 1 ] || fail "a forecast merged after its outcome date was not observed false: $(tail -1 "$TMP/late.out")"
grep -q 'reached refs/remotes/origin/main 2026-07-15' "$TMP/late.out" || fail "the late merge's first-parent date was not the one read: $(grep '^    forecast' "$TMP/late.out" | head -1)"
grep -q 'not pre-registered, not scored' "$TMP/late.out" || fail "the late forecast was not refused as unregistered"

# 4. before the outcome date: the score waits on the date; after it with no outcome: waits on the outcome
"$PY" "$FIXTURE" build "$TMP/pending" --no-outcome >/dev/null || fail "could not build the pending fixture"
check --estate "$TMP/pending" --now 2026-03-01T00:00:00Z >"$TMP/pending.out" 2>&1
[ $? -eq 3 ] && tail -1 "$TMP/pending.out" | grep -q 'none has passed its outcome date' || fail "a forecast before its date did not wait on the date: $(tail -1 "$TMP/pending.out")"
check --estate "$TMP/pending" --now 2026-09-06T00:00:00Z >"$TMP/no-outcome.out" 2>&1
[ $? -eq 3 ] && tail -1 "$TMP/no-outcome.out" | grep -q 'no outcome in twin/orgs/driftwood/outcomes resolves' || fail "a forecast past its date with no outcome did not wait on the outcome: $(tail -1 "$TMP/no-outcome.out")"

# 5. an outcome that reached main before the date it says it resolved is an answer recorded
#    before the question closed
"$PY" "$FIXTURE" build "$TMP/early-outcome" --outcome-committed 2026-06-01T00:00:00+00:00 >/dev/null || fail "could not build the early-outcome fixture"
check --estate "$TMP/early-outcome" --now 2026-09-06T00:00:00Z >"$TMP/early.out" 2>&1
[ $? -eq 1 ] && grep -q 'before the date it says it resolved' "$TMP/early.out" || fail "an outcome merged before its resolution date was admitted: $(tail -1 "$TMP/early.out")"

# 6. the worked example validates against the fixture through the CLI, and the CLI cannot look
#    without the served feeds (exit 2, never a pass)
"$PY" "$VALIDATOR" "$TMP/scored/driftwood/twin/forecasts/2026-02-01-fixture.forecast.yaml" --twin "$ROOT" --headless --feeds "$TMP/scored/feeds" >"$TMP/cli.out" 2>&1 \
  || fail "the worked example did not validate against the fixture: $(tail -1 "$TMP/cli.out")"
grep -q '1 derived' "$TMP/cli.out" && grep -q '1 recorded' "$TMP/cli.out" || fail "the validator's summary did not count one derived and one recorded"
"$PY" "$VALIDATOR" "$TMP/scored/driftwood/twin/forecasts/2026-02-01-fixture.forecast.yaml" --twin "$ROOT" --headless --feeds "$TMP/absent" >"$TMP/cli2.out" 2>&1
[ $? -eq 2 ] && tail -1 "$TMP/cli2.out" | grep -q '^SKIP:' || fail "the validator passed or failed a file it could not check: $(tail -1 "$TMP/cli2.out")"
"$PY" "$VALIDATOR" "$EXAMPLE" --twin "$ROOT" --headless --feeds "$TMP/scored/feeds" --adopter "$TMP/scored/driftwood" >/dev/null 2>&1 \
  || fail "the worked example in the skill's assets does not validate with --adopter"

# 7. the local clock's derive row, end to end with a stand-in model over the empty fixture: the
#    forecast is committed on a branch cut from origin/main, validated with the row's validator,
#    and a forecast citing a level the feed does not carry is refused with the branch kept
"$PY" "$FIXTURE" build "$TMP/clock" --no-forecast --no-outcome >/dev/null || fail "could not build the clock fixture"
export LOCAL_CLOCK_CLAUDE="$ROOT/verify/local-clock/stub-claude.sh" LOCAL_CLOCK_HOME="$TMP/.local-clock" \
       LOCAL_CLOCK_ESTATE="$TMP/clock" LOCAL_CLOCK_PYTHON="$PY"
unset LOCAL_CLOCK_LAUNCHD
LOCAL_CLOCK_STUB=forecast bash "$ROOT/talk/local-clock.sh" --adopter driftwood --step derive >"$TMP/derive.out" 2>&1 \
  || fail "the derive row with a stub model did not exit 0: $(grep -E '^(fail|FAIL)' "$TMP/derive.out" | head -1)"
grep -q '^ok    derive-driftwood: .*1 derived' "$TMP/derive.out" || fail "the derive row did not validate the stub forecast: $(grep -E '^(ok|fail)' "$TMP/derive.out" | head -3 | tr '\n' ' ')"
dbranch="$(git -C "$TMP/clock/driftwood" for-each-ref --format='%(refname:short)' 'refs/heads/local-clock/derive-*' | head -1)"
[ -n "$dbranch" ] || fail "no local-clock/derive-* branch in the fixture adopter"
[ "$(git -C "$TMP/clock/driftwood" diff --name-only "origin/main...$dbranch")" = "twin/forecasts/$(date -u +%Y-%m-%d)-stub-derive.forecast.yaml" ] \
  || fail "the derive branch carries something other than one forecast file under twin/forecasts"
[ "$(git -C "$TMP/clock/driftwood.origin.git" rev-parse main)" = "$(git -C "$TMP/clock/driftwood" rev-parse origin/main)" ] || fail "the clock moved origin's main"
LOCAL_CLOCK_STUB=forecast-fabricated bash "$ROOT/talk/local-clock.sh" --adopter driftwood --step derive >"$TMP/fab.out" 2>&1 \
  && fail "a forecast citing a level the feed does not carry was admitted"
grep -Eq '^fail  derive-driftwood: .*does not carry' "$TMP/fab.out" || fail "the fabricated observation was refused for the wrong reason: $(grep '^fail' "$TMP/fab.out" | head -1)"
frid="$(sed -n 's/^local clock: run \([^ ]*\) .*/\1/p' "$TMP/fab.out" | head -1)"
git -C "$TMP/clock/driftwood" for-each-ref 'refs/heads/local-clock/' | grep -q -- "$frid" || fail "the refused forecast's branch was not kept for inspection"
[ ! -e "$TMP/.local-clock/runs/$frid/derive-driftwood.pr-body.md" ] || fail "a PR body survived the refusal"
# a rehearsal forecast says injected on its face and the validator refuses it, by design
# (the date is quoted: local_clock.py's stamp writes the signal as JSON and an unquoted YAML date
# is a date object it cannot serialise -- verify-local-clock.sh quotes its fixture date too)
printf "date: '%s'\nkind: headline\nstatement: rehearsal\nsource: fixture\n" "$(date -u +%Y-%m-%d)" >"$TMP/signal.yaml"
LOCAL_CLOCK_STUB=forecast bash "$ROOT/talk/local-clock.sh" --adopter driftwood --step derive --inject "$TMP/signal.yaml" >"$TMP/rehearsal.out" 2>&1 \
  || fail "a rehearsal of the derive row did not exit 0: $(grep -E '^fail' "$TMP/rehearsal.out" | head -1)"
grep -q 'is marked injected and the validator refused it' "$TMP/rehearsal.out" || fail "the rehearsal forecast was not refused by the validator: $(grep -E '^(ok|fail)' "$TMP/rehearsal.out" | head -2 | tr '\n' ' ')"

# 8. REVIEW F8: "it writes one file and stops" was prose. TWO valid forecast files in one
#     derive commit were accepted -- two proposals in one review, and the pull-request body the
#     clock writes speaks about one. The count is asserted now.
export LOCAL_CLOCK_CLAUDE="$ROOT/verify/local-clock/stub-claude.sh" LOCAL_CLOCK_HOME="$TMP/.local-clock-two" \
       LOCAL_CLOCK_ESTATE="$TMP/clock" LOCAL_CLOCK_PYTHON="$PY"
LOCAL_CLOCK_STUB=forecast-two bash "$ROOT/talk/local-clock.sh" --adopter driftwood --step derive >"$TMP/two.out" 2>&1 \
  && fail "the derive row accepted a commit carrying two forecast files"
grep -q 'the commit carries 2 files under twin/forecasts' "$TMP/two.out" \
  || fail "two forecast files were refused for the wrong reason: $(grep '^fail' "$TMP/two.out" | head -1)"

# 9. REVIEW F4 through the clock: a forecast whose visible number is not the validated one
LOCAL_CLOCK_STUB=forecast-dupkey bash "$ROOT/talk/local-clock.sh" --adopter driftwood --step derive >"$TMP/dup.out" 2>&1 \
  && fail "the derive row committed a forecast a human reads as 0.999 and the validator reads as 0.27"
grep -q 'the validator refused live claim' "$TMP/dup.out" || fail "the duplicate-key forecast was not refused by the validator: $(grep '^fail' "$TMP/dup.out" | head -1)"
grep -q "duplicate key 'probability'" "$TMP/derive-dupkey.validate.out" 2>/dev/null \
  || grep -rq "duplicate key 'probability'" "$TMP/.local-clock-two/runs" \
  || fail "the duplicate key was not the reason the validator gave"

# 10. REVIEW F5: the validator ran from the tree the child could WRITE to. The clock now copies
#     the twin package and the skill OUT of the hub before the model starts, judges with the
#     copy, and reads the hub's own copies back. Both facts are asserted here; the full tamper
#     (a model overwriting the hub's validator with an always-pass stub) is
#     tests/test_derived_forecast.py, which can afford a throwaway copy of the whole hub.
grep -q 'copied to .* BEFORE the model started and run from there' "$TMP/derive.out" \
  || fail "the run does not say the judge was copied before the child: $(grep '^note' "$TMP/derive.out" | head -1)"
grep -q 'This local layer is ADVISORY' "$TMP/derive.out" \
  || fail "the run does not say the local layer is advisory and the gate is the measurement"
unset LOCAL_CLOCK_CLAUDE LOCAL_CLOCK_HOME LOCAL_CLOCK_ESTATE LOCAL_CLOCK_PYTHON

# 11. REVIEW F1: a forecast whose number is REWRITTEN after the outcome is already on main --
#    deleted and re-added, or edited in place -- is not pre-registered. Pre-registration is the
#    LAST first-parent write onto the served ref, not the path's first add, and both are printed.
for shape in "" --in-place; do
  "$PY" "$FIXTURE" build "$TMP/rw$shape" >/dev/null || fail "could not build the rewrite fixture"
  # shellcheck disable=SC2086
  "$PY" "$FIXTURE" rewrite "$TMP/rw$shape" $shape >/dev/null || fail "could not rewrite the forecast ($shape)"
  check --estate "$TMP/rw$shape" --now 2026-09-06T00:00:00Z >"$TMP/rw$shape.out" 2>&1
  [ $? -eq 1 ] || fail "a forecast rewritten after the answer was on main was not observed false (${shape:-delete-and-re-add}): $(tail -1 "$TMP/rw$shape.out")"
  grep -q 'rewritten after it landed' "$TMP/rw$shape.out" || fail "the rewrite was not named on the forecast line (${shape:-delete-and-re-add}): $(grep '^    forecast' "$TMP/rw$shape.out" | head -1)"
  grep -q 'registered on the day of the rewrite' "$TMP/rw$shape.out" || fail "the refusal did not say the rewrite re-registers the forecast (${shape:-delete-and-re-add})"
  grep -q 'reached refs/remotes/origin/main 2026-02-01' "$TMP/rw$shape.out" || fail "the original arrival date is no longer printed (${shape:-delete-and-re-add}): the limit stopped being a number"
  grep -q 'brier=' "$TMP/rw$shape.out" && fail "a rewritten forecast was still scored (${shape:-delete-and-re-add})"
done

# 12. REVIEW F1, the honest direction, KEPT: a RENAME costs a forecast its registration (the new
#    path's first add is the rename commit), so a rename cannot launder one
"$PY" "$FIXTURE" build "$TMP/renamed" >/dev/null || fail "could not build the rename fixture"
"$PY" "$FIXTURE" rename "$TMP/renamed" >/dev/null || fail "could not rename the forecast"
check --estate "$TMP/renamed" --now 2026-09-06T00:00:00Z >"$TMP/renamed.out" 2>&1
[ $? -eq 1 ] && grep -q 'pre-registered: no' "$TMP/renamed.out" || fail "a renamed forecast kept its registration: $(tail -1 "$TMP/renamed.out")"

# 13. REVIEW F2: the answer key is immutable once it is on the served ref. An outcome EDITED
#     afterwards silently rescores every forecast it resolves while the run prints the old date.
"$PY" "$FIXTURE" build "$TMP/edited" >/dev/null || fail "could not build the edited-outcome fixture"
"$PY" "$FIXTURE" edit-outcome "$TMP/edited" >/dev/null || fail "could not edit the answer key"
check --estate "$TMP/edited" --now 2026-09-06T00:00:00Z >"$TMP/edited.out" 2>&1
[ $? -eq 1 ] || fail "an answer key edited after it reached main was admitted: $(tail -1 "$TMP/edited.out")"
grep -q 'an answer key edited after it landed rescores every forecast it resolves' "$TMP/edited.out" || fail "the edited answer key was refused for the wrong reason: $(grep FAIL: "$TMP/edited.out" | head -1)"
grep -q 'brier=' "$TMP/edited.out" && fail "a forecast was scored against an edited answer key"

# 14. REVIEW F2: two outcomes resolving one proposition -- matching[0] silently won and the run
#     PASSed with no word that two answer keys disagree
"$PY" "$FIXTURE" build "$TMP/two-keys" >/dev/null || fail "could not build the two-answer-key fixture"
"$PY" "$FIXTURE" second-outcome "$TMP/two-keys" >/dev/null || fail "could not add the second answer key"
check --estate "$TMP/two-keys" --now 2026-09-06T00:00:00Z >"$TMP/two-keys.out" 2>&1
[ $? -eq 1 ] || fail "two contradicting answer keys were admitted: $(tail -1 "$TMP/two-keys.out")"
grep -q 'two answer keys for one question' "$TMP/two-keys.out" || fail "the two answer keys were not named: $(grep FAIL: "$TMP/two-keys.out" | head -1)"
grep -q 'brier=' "$TMP/two-keys.out" && fail "a forecast was scored while two answer keys disagreed"

# 15. REVIEW F3: a tag that EXISTS is not a tag that is SIGNED. Two annotated UNSIGNED tags and
#     one lightweight tag must count as 3 tags and 0 signatures, read with `git cat-file tag`.
"$PY" "$FIXTURE" build "$TMP/tagged" >/dev/null || fail "could not build the tagged fixture"
"$PY" "$FIXTURE" tag-feeds "$TMP/tagged" >/dev/null || fail "could not tag the fixture publisher"
check --estate "$TMP/tagged" --now 2026-09-06T00:00:00Z >"$TMP/tagged.out" 2>&1
grep -q '3 tag(s) naming either, 0 of them carrying a signature block' "$TMP/tagged.out" \
  || fail "an unsigned tag was counted as signed: $(grep 'the feeds publisher has' "$TMP/tagged.out")"
if command -v ssh-keygen >/dev/null 2>&1; then
  ssh-keygen -q -t ed25519 -N '' -C throwaway -f "$TMP/tagkey" || fail "could not make a throwaway signing key"
  "$PY" "$FIXTURE" build "$TMP/signed" >/dev/null || fail "could not build the signed-tag fixture"
  "$PY" "$FIXTURE" tag-feeds "$TMP/signed" --sign-with "$TMP/tagkey" >/dev/null || fail "could not sign the fixture tag"
  check --estate "$TMP/signed" --now 2026-09-06T00:00:00Z >"$TMP/signed.out" 2>&1
  grep -q '3 tag(s) naming either, 1 of them carrying a signature block' "$TMP/signed.out" \
    || fail "a really signed tag was not seen, so the 0 above proves nothing: $(grep 'the feeds publisher has' "$TMP/signed.out")"
else
  echo "    note: ssh-keygen is absent, so the OTHER half of F3 (a really signed tag counts as 1) was not measured here"
fi

# 16. REVIEW F4: a duplicate YAML key. PyYAML keeps the last, so a visible `probability: 0.999`
#     above a real 0.27 validated as 0.27 and the clock committed it: the file a human reviews
#     in the pull request is not the file the validator read.
"$PY" "$FIXTURE" build "$TMP/dupkey" --no-forecast --no-outcome >/dev/null || fail "could not build the duplicate-key fixture"
"$PY" "$FIXTURE" duplicate-key "$TMP/dupkey" >/dev/null || fail "could not write the duplicate-key forecast"
check --estate "$TMP/dupkey" --now 2026-09-06T00:00:00Z >"$TMP/dupkey.out" 2>&1
[ $? -eq 1 ] && grep -q "duplicate key 'probability'" "$TMP/dupkey.out" \
  || fail "a forecast whose visible number is not the validated one was admitted: $(tail -1 "$TMP/dupkey.out")"
"$PY" "$VALIDATOR" "$TMP/dupkey/driftwood/twin/forecasts/2026-02-01-fixture.forecast.yaml" --twin "$ROOT" --headless --feeds "$TMP/dupkey/feeds" >"$TMP/dupkey.cli" 2>&1
[ $? -eq 1 ] && grep -q "duplicate key 'probability'" "$TMP/dupkey.cli" || fail "the validator CLI read the duplicate-key file: $(tail -1 "$TMP/dupkey.cli")"

# 17. REVIEW F7: `prices_through` and `recorded_belief` are promised on EVERY forecast by
#     SKILL.md section 2 and were required on neither
for field in prices_through recorded_belief; do
  (cd "$ROOT" && FIELD="$field" EX="$EXAMPLE" EST="$TMP/scored" "$PY" - <<'PY'
import os, sys, yaml
sys.path.insert(0, os.getcwd())
from twin import derived_forecast as df
roles = {str(r["id"]) for r in yaml.safe_load(open("twin/roles.yaml"))["roles"]}
doc = yaml.safe_load(open(os.environ["EX"]))
doc["forecasts"][0].pop(os.environ["FIELD"], None)
bad = df.validate(doc, roles, headless=True, adopter_root=os.environ["EST"] + "/driftwood",
                  feeds_root=os.environ["EST"] + "/feeds")
sys.exit(0 if any(os.environ["FIELD"] in b for b in bad) else 1)
PY
  ) || fail "a forecast with no $field was accepted, and SKILL.md section 2 promises it on every forecast"
done

# 18. REVIEW F9/F10, the two limits that were prose: the run prints how many DISTINCT evidence
#     grades it saw across every signal (while that is one, "no stronger than its weakest signal"
#     is a comparison with nothing to compare), and how many registering commits are dated before
#     their own first parent (a committer date this check cannot otherwise vouch for).
"$PY" "$FIXTURE" build "$TMP/backdated" --no-forecast --no-outcome >/dev/null || fail "could not build the backdated fixture"
"$PY" "$FIXTURE" backdated "$TMP/backdated" >/dev/null || fail "could not write the backdated forecast"
check --estate "$TMP/backdated" --now 2026-09-06T00:00:00Z >"$TMP/backdated.out" 2>&1
grep -q '1 distinct evidence grade(s) across every signal read (5)' "$TMP/backdated.out" \
  || fail "the reopened ordinal comparison's one-rung tautology is not printed as a number: $(grep '^    limits' "$TMP/backdated.out")"
grep -q '1 registering commit(s) dated before their own first parent' "$TMP/backdated.out" \
  || fail "a commit dated 2025-01-01 on a 2026-01-01 parent was not counted: $(grep '^    limits' "$TMP/backdated.out")"
grep -q 'cannot tell those two apart offline' "$TMP/backdated.out" || fail "the clock-provenance limit is no longer stated"

echo "PASS: offline, over throwaway repositories with stub-claude.sh standing in for the model (a fixture, not the twin having run) -- a forecast merged before its horizon is validated against the served overlay and feeds, read as pre-registered off origin/main's first-parent history and scored by twin/scoring.py against the overlay's own outcome; no forecast waits, a late merge fails whatever the file says, a forecast before its date waits on the date and after it waits on the outcome, an outcome merged before its resolution date fails, the validator cannot look without the served feeds, and the local clock's derive row commits and validates a forecast, refuses one citing a level the feed does not carry, and refuses a rehearsal. The 2026-09-09 review, every attack re-run and refused: a forecast rewritten after the answer was on main (deleted and re-added, or edited in place) is registered on the day of the rewrite and both dates are printed; a rename still costs a forecast its registration; an answer key edited after it reached main is refused, and so are two answer keys for one question; three tags of which none carries a signature block count as 0 signed, and a really signed one counts as 1; a duplicate YAML key is refused by the validator and the check; prices_through and recorded_belief are required on every forecast; the clock refuses two files in one commit, judges with a copy of the twin package and the skill taken BEFORE the model started, and says the local layer is advisory; and the two remaining limits (one evidence rung, a committer date) are printed as numbers"
[ "$SELFCHECK" = 1 ] && exit 0

# --- the real estate: every adopter's origin/main ---------------------------------------------
[ -d "$ROOT/.estate-clone/platform" ] || bash "$ROOT/clone-estate.sh" >/dev/null \
  || { echo "FAIL: could not assemble .estate-clone/"; exit 1; }
log="$(mktemp)"; trap 'rm -rf "$TMP" "$log"' EXIT
(cd "$ROOT" && "$PY" -m twin.derived_forecast check --estate "$ROOT/.estate-clone" --hub "$ROOT") | tee "$log" | sed 's/^/    /'
rc=${PIPESTATUS[0]}
case $rc in
  0) echo "PASS: $(grep '^PASS:' "$log" | tail -1 | cut -c7-)";;
  3) echo "SKIP: $(grep '^SKIP:' "$log" | tail -1 | cut -c7-)";;
  *) echo "FAIL: $(grep '^FAIL:' "$log" | tail -1 | cut -c7-)";;
esac
exit "$rc"
