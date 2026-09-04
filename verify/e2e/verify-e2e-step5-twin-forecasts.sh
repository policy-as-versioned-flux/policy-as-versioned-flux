#!/usr/bin/env bash
# NORTH-STAR §4 step 5: "The twin, on its schedule, plays a dated external signal forward on the
# value chain, emits a scored forecast, and publishes forward intelligence the platform consumes."
#
# THREE ADOPTERS, NOT ONE (eco-system ticket 64). This script hardcoded `driftwood` until
# 2026-09-04, so the two adopters REGRILL answer 39 promises and ticket 29's Answer claimed could
# be entirely absent while step 5 read green on the deck. The adopter list is now DERIVED from the
# party artefacts that claim the adopter role -- the same rule verify/twin-per-adopter uses -- so a
# fourth adopter joins this step by publishing a party artefact, and a missing overlay is named.
#
# ON ITS SCHEDULE (eco-system ticket 64, the second half). Step 5's own sentence begins "on its
# schedule", and this script used to grade six path-existence checks: an overlay on disk is not a
# sweep that ran. It now reads each adopter's own `observations/twin-sweep.jsonl` and requires at
# least one line carrying a parseable `swept_at`. Until the clock has appended one, that half is a
# could-not-look that names the file and the cron it waits for -- never a pass, and never a PASS
# line that says a sweep happened.
source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"
step 5 "twin forecasts"

# E2E_ADOPTER still names one adopter, for a run that wants to look at exactly one. With it unset,
# every party claiming the adopter role is graded.
if [ -n "${E2E_ADOPTER:-}" ]; then
  ADOPTERS=("$E2E_ADOPTER")
else
  mapfile -t ADOPTERS < <("$PY" "$ROOT/verify/twin-per-adopter/twin_per_adopter.py" --list "$ESTATE" 2>/dev/null)
fi
[ "${#ADOPTERS[@]}" -gt 0 ] || skip "no party in .estate-clone/ claims the adopter role (run clone-estate.sh), so there is no twin to look at"

verdicts=()   # "fail|<why>" or "skip|<why>", collected across every adopter
log="$(mktemp)"; trap 'rm -f "$log"' EXIT

for ADOPTER in "${ADOPTERS[@]}"; do
  T="$ESTATE/$ADOPTER/twin"
  if [ ! -d "$T" ]; then
    verdicts+=("skip|$ADOPTER carries no twin/ at all, so it plays no signal forward [ticket 64 authors the overlay]")
    continue
  fi

  missing=()
  want() {  # want <what> <path...>: present -> ok line, absent -> one named missing entry
    local what="$1"; shift
    for p in "$@"; do [ -e "$p" ] && { echo "  ok  $what"; return; }; done
    missing+=("$what")
  }

  # 1. the adopter owns its overlay with the world layer vendored (ticket 25 for driftwood,
  #    ticket 64 for the other two).
  want "$ADOPTER/twin/orgs/$ADOPTER/meta.yaml (the adopter's own overlay)" "$T/orgs/$ADOPTER/meta.yaml"
  want "$ADOPTER/twin/world/ (the world layer, vendored)"                  "$T/world"
  # 2. the emitter. NOT the emitted feed: an adopter whose party artefact signs no size and whose
  #    one causal edge to its declared cash flow is graded outside the admission threshold has an
  #    emitter that REFUSES with those reasons named, and refusing is the correct behaviour, not a
  #    missing artefact. Whether a feed exists is the emitter's own verdict, consumed below.
  want "$ADOPTER/twin/emit-forward-intel.py (the forward-intel emitter)" "$T/emit-forward-intel.py"
  # 3. the six standing scenarios, with the eol-date-passes and penalty-published classes.
  # They live under the OVERLAY (orgs/<adopter>/scenarios/), which is the only path
  # twin.Overlay.load reads -- a directory at twin/scenarios/ would be files nothing loads
  # (ticket 29). Both are looked at so this line names what is there, not where I guessed.
  SC="$T/orgs/$ADOPTER/scenarios"; [ -d "$SC" ] || SC="$T/scenarios"
  n=$(ls "$SC"/*.yaml 2>/dev/null | wc -l | tr -d ' ')
  if [ "$n" -ge 6 ]; then echo "  ok  $ADOPTER: $n standing scenarios in ${SC#"$ESTATE"/}"
  else missing+=("${SC#"$ESTATE"/} holds $n of the six standing scenarios, and the eol-date-passes and penalty-published classes"); fi
  # 4. the lookup that binds a pinned feed VERSION to one dated signal, no judgement on the clock.
  # TWO halves, because it is two things: the adopter's own table binds a PIN to a standing
  # scenario (it lives in the adopter's repo because the scenario library does), and
  # twin/feed_signal.py turns the pinned VERSION into the dated signal itself.
  want "$ADOPTER/twin/signals.yaml (the pin -> standing-scenario table)" "$T/signals.yaml" "$T/signal-lookup.yaml"

  if [ ${#missing[@]} -gt 0 ]; then
    msg="$(printf '; %s' "${missing[@]}")"
    verdicts+=("skip|$ADOPTER cannot play a dated signal forward yet -- absent:${msg#;}")
    continue
  fi

  # The presence of those paths is not this step's claim. Step 5 once passed in the same run in
  # which driftwood's own verify-twin-overlay.sh and twin/verify-twin-scenarios.sh observed FALSE
  # on the very files it had just ticked off (review 2026-09-02): it graded existence, and
  # existence is not a forecast. So the ADOPTER'S OWN verdicts are consumed rather than re-derived
  # -- running each script is what makes step 5 incapable of disagreeing with the repository that
  # owns the artefact.
  for check in verify-twin-overlay.sh twin/verify-twin-scenarios.sh twin/verify-twin-sweep-moved.sh; do
    [ -f "$ESTATE/$ADOPTER/$check" ] || { verdicts+=("skip|$ADOPTER/$check is not in this estate"); continue; }
    (cd "$ESTATE/$ADOPTER" && timeout 300 bash "$check") >"$log" 2>&1
    case $? in
      0) echo "  ok  $ADOPTER/$check: $(tail -1 "$log")" ;;
      3) verdicts+=("skip|$ADOPTER/$check could not look: $(tail -1 "$log")") ;;
      *) verdicts+=("fail|$ADOPTER/$check observed false: $(tail -1 "$log")") ;;
    esac
  done

  # "ON ITS SCHEDULE". The half only the clock can supply, and the half this script asserted by
  # implication until 2026-09-04. A dated observation, appended by the scheduled sweep, or a
  # could-not-look naming the series and the cron. Note what is NOT asserted: that the sweep found
  # a change. `moved` is twin/verify-twin-sweep-moved.sh's subject and is graded above; this is
  # the weaker, prior claim that the sweep RAN and wrote down when.
  "$PY" - "$ESTATE/$ADOPTER" "$ADOPTER" >"$log" 2>&1 <<'PY'
import json, re, sys
from pathlib import Path

repo, adopter = Path(sys.argv[1]), sys.argv[2]
series = repo / "observations" / "twin-sweep.jsonl"
workflow = repo / ".github" / "workflows" / "twin-sweep.yml"
if not workflow.is_file():
    print("skip|%s has no .github/workflows/twin-sweep.yml, so nothing sweeps this overlay on a "
          "schedule" % adopter)
    raise SystemExit(0)
cron = re.search(r'cron:\s*"([^"]+)"', workflow.read_text())
cron = cron.group(1) if cron else "an unparsed schedule"
if not series.is_file():
    print("skip|%s/observations/twin-sweep.jsonl does not exist, so the sweep on `%s` has never "
          "appended a dated observation; the overlay is on disk and the schedule is declared, and "
          "only the clock can close this" % (adopter, cron))
    raise SystemExit(0)
DATED = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
dated, bad = [], []
for i, line in enumerate(series.read_text().splitlines(), 1):
    line = line.strip()
    if not line:
        continue
    try:
        rec = json.loads(line)
    except ValueError:
        bad.append("line %d is not JSON" % i)
        continue
    at = str(rec.get("swept_at") or "")
    (dated if DATED.match(at) else bad).append(at or ("line %d carries no swept_at" % i))
if bad:
    print("fail|%s/observations/twin-sweep.jsonl carries %d record(s) with no parseable swept_at: "
          "%s" % (adopter, len(bad), "; ".join(bad[:3])))
elif dated:
    print("ok|%s's scheduled sweep (`%s`) has appended %d dated observation(s); the most recent "
          "swept_at is %s" % (adopter, cron, len(dated), max(dated)))
else:
    print("skip|%s/observations/twin-sweep.jsonl exists and is empty, so the sweep on `%s` has "
          "appended no dated observation yet" % (adopter, cron))
PY
  said="$(tail -1 "$log")"
  case "$said" in
    ok\|*)   echo "  ok  ${said#ok|}" ;;
    fail\|*) verdicts+=("$said") ;;
    *)       verdicts+=("${said}") ;;
  esac
done

# The twin's own evals, once: they score the twin package's skills, not any one adopter's overlay.
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
  case "$v" in fail\|*) fail "step 5 is false where an adopter's own checks are: ${v#fail|}" ;; esac
done
if [ -n "${verdicts[0]:-}" ]; then
  msg="$(printf '; %s' "${verdicts[@]#skip|}")"
  skip "the twin did not play a dated signal forward for every adopter:${msg#;}"
fi
pass "all ${#ADOPTERS[@]} adopter(s) (${ADOPTERS[*]}) carry their own overlay, vendored world layer, emitter, six standing scenarios and signal lookup; each one's own twin-overlay, twin-scenarios and twin-sweep-moved checks observed true; each one's scheduled sweep has appended a dated swept_at observation; and the twin's own evals scored them: $(tail -1 "$log")"
