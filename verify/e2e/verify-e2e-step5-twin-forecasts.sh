#!/usr/bin/env bash
# NORTH-STAR §4 step 5: "The twin, on its schedule, plays a dated external signal forward on the
# value chain, emits a scored forecast, and publishes forward intelligence the platform consumes."
#
# Exit 3 until ticket 29 lands. This script does not pretend to look at a forecast; it looks at
# the five things step 5 needs and names, by path, which of them are not there yet, so the SKIP
# line says what is missing rather than "not built".
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
step 5 "twin forecasts"

ADOPTER="${E2E_ADOPTER:-driftwood}"
T="$ESTATE/$ADOPTER/twin"
[ -d "$T" ] || skip "no .estate-clone/$ADOPTER/twin (run clone-estate.sh)"

missing=()
want() {  # want <what> <path...>: present -> ok line, absent -> one named missing entry
  local what="$1"; shift
  for p in "$@"; do [ -e "$p" ] && { echo "  ok  $what"; return; }; done
  missing+=("$what")
}

# 1. the adopter owns its overlay with the world layer vendored (ticket 25 landed this).
want "$ADOPTER/twin/orgs/$ADOPTER/meta.yaml (the adopter's own overlay)" "$T/orgs/$ADOPTER/meta.yaml"
want "$ADOPTER/twin/world/ (the world layer, vendored)"                  "$T/world"
# 2. the forward-intel feed the estate consumes (ticket 25 landed v1).
want "$ADOPTER/twin/forward-intel/v1/feed.json (the feed the estate consumes)" "$T/forward-intel/v1/feed.json"
# 3. the six standing scenarios, with the eol-date-passes and penalty-published classes.
# They live under the OVERLAY (orgs/<adopter>/scenarios/), which is the only path
# twin.Overlay.load reads -- a directory at twin/scenarios/ would be files nothing loads
# (ticket 29). Both are looked at so this line names what is there, not where I guessed.
SC="$T/orgs/$ADOPTER/scenarios"; [ -d "$SC" ] || SC="$T/scenarios"
n=$(ls "$SC"/*.yaml 2>/dev/null | wc -l | tr -d ' ')
if [ "$n" -ge 6 ]; then echo "  ok  $n standing scenarios in ${SC#"$ESTATE"/}"
else missing+=("${SC#"$ESTATE"/} holds $n of the six standing scenarios, and the eol-date-passes and penalty-published classes"); fi
# 4. the lookup that binds a pinned feed VERSION to one dated signal, no judgement on the clock.
# TWO halves, because it is two things and checking one of them was checking half a seam: the
# adopter's own table binds a PIN to a standing scenario (it lives in the adopter's repo because
# the scenario library does), and twin/feed_signal.py turns the pinned VERSION into the dated
# signal itself -- steep from a fixed table keyed by feed name, provenance carrying published_at,
# tag and commit, grade 5. verify-twin-evals.sh below is what runs the second one against every
# feed envelope the estate publishes (added 2026-08-29; the module was the piece ticket 29 left).
want "$ADOPTER/twin/signals.yaml (the pin -> standing-scenario table)" "$T/signals.yaml" "$T/signal-lookup.yaml"
want "twin/feed_signal.py (the pinned-feed-version -> dated-signal lookup)" "$ROOT/twin/feed_signal.py"
# 5. the twin's evals in the gate, with truth.log as the record.
want "verify/twin-evals/verify-twin-evals.sh (the twin's evals graded by the gate)" "$ROOT/verify/twin-evals/verify-twin-evals.sh"

if [ ${#missing[@]} -gt 0 ]; then
  msg="$(printf '; %s' "${missing[@]}")"
  skip "the twin cannot play a dated signal forward yet -- absent [ticket 29]:${msg#;}"
fi
# Everything ticket 29 owes is on disk, so the score is the twin's own evals -- run, not
# re-implemented here. This used to be an unconditional `skip`, which made step 5 structurally
# incapable of two of its three verdicts: it read could-not-look on the deck even with every
# artefact present and verify-twin-evals.sh green (found 2026-08-29).
#
# And the presence of those paths is not the step's claim. Step 5 once passed in the same run in
# which driftwood's own verify-twin-overlay.sh and twin/verify-twin-scenarios.sh observed FALSE on
# the very files it had just ticked off (review 2026-09-02): it graded existence, and existence is
# not a forecast. So the ADOPTER'S OWN verdicts are consumed here rather than re-derived --
# running each script is what makes step 5 incapable of disagreeing with the repo that owns the
# artefact. (emit-forward-intel.py --check would re-implement half of that seam in the hub and
# could pass while the adopter's own check failed; that is the shape this ticket exists to end.)
# Ticket 64 loops this list over three adopters; it is a list for that reason.
# Ticket 72's twin/verify-twin-sweep-moved.sh is the third, and it is the one that holds step 5
# at could-not-look until observations/twin-sweep.jsonl carries a dated live firing: the sweep is
# the "on its schedule" half of step 5's own sentence, and only the clock can supply it.
log="$(mktemp)"; trap 'rm -f "$log"' EXIT
verdicts=()
for check in verify-twin-overlay.sh twin/verify-twin-scenarios.sh twin/verify-twin-sweep-moved.sh; do
  [ -f "$ESTATE/$ADOPTER/$check" ] || { verdicts+=("skip|$ADOPTER/$check is not in this estate"); continue; }
  (cd "$ESTATE/$ADOPTER" && timeout 300 bash "$check") >"$log" 2>&1
  case $? in
    0) echo "  ok  $ADOPTER/$check: $(tail -1 "$log")" ;;
    3) verdicts+=("skip|$ADOPTER/$check could not look: $(tail -1 "$log")") ;;
    *) verdicts+=("fail|$ADOPTER/$check observed false: $(tail -1 "$log")") ;;
  esac
done

EVALS="$ROOT/verify/twin-evals/verify-twin-evals.sh"
bash "$EVALS" >"$log" 2>&1
case $? in
  0) echo "  ok  the twin's own evals scored the artefacts: $(tail -1 "$log")" ;;
  3) verdicts+=("skip|the twin's evals could not look: $(tail -1 "$log")") ;;
  *) verdicts+=("fail|the twin's evals observed false: $(tail -1 "$log")") ;;
esac

# An observed-false anywhere is step 5's answer; a could-not-look anywhere means step 5 did not
# see the forecast played forward, whatever the paths on disk say.
for v in "${verdicts[@]:-}"; do
  case "$v" in fail\|*) fail "step 5 is false where the adopter's own checks are: ${v#fail|}" ;; esac
done
if [ -n "${verdicts[0]:-}" ]; then
  msg="$(printf '; %s' "${verdicts[@]#skip|}")"
  skip "the twin's artefacts are present and $ADOPTER's own checks did not all look [ticket 72 supplies the dated observations/twin-sweep.jsonl firing]:${msg#;}"
fi
pass "the twin's overlay, feed, $n scenarios and signal lookup are all present; $ADOPTER's own twin-overlay, twin-scenarios and twin-sweep-moved checks each observed true, including a dated live firing in observations/twin-sweep.jsonl; and the twin's own evals scored them: $(tail -1 "$log")"
