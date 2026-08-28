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
n=$(ls "$T"/scenarios/*.yaml 2>/dev/null | wc -l | tr -d ' ')
if [ "$n" -ge 6 ]; then echo "  ok  $n standing scenarios"
else missing+=("$ADOPTER/twin/scenarios/ holds $n of the six standing scenarios, and the eol-date-passes and penalty-published classes"); fi
# 4. the lookup that binds a pinned feed VERSION to one dated signal, no judgement on the clock.
want "$ADOPTER/twin/signals.yaml (the pinned-feed-version -> dated-signal lookup)" "$T/signals.yaml" "$T/signal-lookup.yaml"
# 5. the twin's evals in the gate, with truth.log as the record.
want "verify/twin-evals/verify-twin-evals.sh (the twin's evals graded by the gate)" "$ROOT/verify/twin-evals/verify-twin-evals.sh"

if [ ${#missing[@]} -gt 0 ]; then
  msg="$(printf '; %s' "${missing[@]}")"
  skip "the twin cannot play a dated signal forward yet -- absent [ticket 29]:${msg#;}"
fi
# Everything ticket 29 owes is on disk, but scoring a forecast is that ticket's own
# verify-twin-evals.sh. ponytail: when it exists, this skip becomes a run of it.
skip "ticket 29's artefacts are all present; step 5 must now run verify/twin-evals/verify-twin-evals.sh rather than re-implement the scoring [ticket 29]"
