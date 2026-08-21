#!/usr/bin/env bash
# The deck's honesty gate: every demo-LIVE claim in deck.md is backed by a
# verify-*.sh that exits 0. This runs all of them and prints a beat->script->PASS
# table. Run it in pre-flight (and as this ticket's own test).
#
# Post-split (mo-12): the six units are real, separate GitHub repos, not
# sibling directories of this hub — this script clones them into
# .estate-clone/ (via clone-estate.sh) before running their beats. That
# clone needs network on first run (or after --refresh); once present, a
# re-run reuses it, so OFFLINE below still means "no cluster required", not
# "no network ever" — the venue-Wi-Fi-independence claim this comment used to
# make is retired (see talk/RUNBOOK.md, mo-12: internet is now assumed).
#
# OFFLINE beats (no cluster required; python3/kyverno/openssl):
#   proofs that stand on a laptop once .estate-clone/ is assembled.
# LIVE beats (need a brought-up cluster — run talk/up.sh first):
#   the three institution reconciles. Reported SKIP-live when no cluster is up,
#   never faked. Pass --live to require them.
#
# Exit non-zero if any offline beat fails, or if --live and a live beat fails.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 2
REQUIRE_LIVE=0; [ "${1:-}" = "--live" ] && REQUIRE_LIVE=1

bash "$ROOT/clone-estate.sh" || { echo "FAIL: could not assemble .estate-clone/ (needs network)" >&2; exit 2; }

# beat | script  (offline — the proofs that must pass with no cluster)
OFFLINE=(
  "policy is a versioned dependency (coexistence)|.estate-clone/platform/distribution/verify-coexistence.sh"
  "a version not in the array cannot run (orphan-guard)|.estate-clone/platform/distribution/verify-orphan-guard.sh"
  "retiring a version prunes it|.estate-clone/platform/distribution/verify-retirement.sh"
  "shift-left CI catches an Audit->Deny flip pre-merge|.estate-clone/platform/shift-left/verify-shift-left.sh"
  "exemptions dissolve into conditional policy|.estate-clone/platform/policy/verify-conditional.sh"
  "PROPORTIONALITY: same control, Audit driftwood vs Deny ludlow|verify/proportionality/verify-proportionality.sh"
  "enforcement tuned by the £, not a timer|.estate-clone/platform/risk/verify-risk-tuned.sh"
  "graded response: caged by degree, not denied|.estate-clone/platform/graded/verify-graded.sh"
  "the board line is TCoR and it moves|.estate-clone/platform/tcor/verify-tcor.sh"
  "feeds signed+versioned, a bump moves the £|.estate-clone/platform/feeds/verify-feeds.sh"
  "ico penalty schema signed; a bump moves the £|.estate-clone/ico/verify-penalty-feed.sh"
  "nist ships a real, pinnable OSCAL catalog|.estate-clone/nist/scripts/verify-catalog.sh"
  "evidence up-flow resolves end to end (OSCAL risk)|.estate-clone/platform/oscal/verify-upflow.sh"
  "LIVING LOOP: war-gamer opens a signed PR, never merges|.estate-clone/platform/wargamer/verify-wargamer.sh"
  "AI-Wardley flags commoditisation movement, re-tunes early|.estate-clone/platform/wardley/verify-wardley.sh"
  "the number is honest today (calibration+integrity)|.estate-clone/platform/honesty/verify-honesty.sh"
  "identity substrate: SPIRE is Istio's CA, mTLS STRICT|.estate-clone/platform/identity/verify-identity.sh"
  "posture-as-identity: posture/vN in the SVID path|.estate-clone/platform/posture/verify-posture-projection.sh"
  "currency controller re-evaluates posture post-admission|.estate-clone/platform/currency-controller/verify-currency.sh"
  "posture-gated reach + secrets (tuppence flagship)|.estate-clone/tuppence/reset/verify-reach-secrets.sh"
  "human/device access plane holds (Pomerium+device SVID)|.estate-clone/platform/access/verify-access.sh"
  "break-glass demands step-up by the £|.estate-clone/platform/break-glass/verify-break-glass.sh"
  "EUD device trust on the same root (vTPM, narrated-virtual)|.estate-clone/platform/eud/verify-eud.sh"
  "PROVENANCE: every actor attestable to one root|verify/provenance/verify-provenance.sh"
  "roles: is data, machine-checked against the filesystem|verify/party/verify-party.sh"
)
# beat | script  (live — need a reconciled cluster; SKIP-live if absent)
LIVE=(
  "driftwood reconciles from a pinned, signed GitRepository|.estate-clone/driftwood/verify-reconcile.sh"
  "tuppence reconciles, carries its toward-strict skin|.estate-clone/tuppence/verify-reconcile.sh"
  "ludlow reconciles, carries its Deny-heavy skin|.estate-clone/ludlow/verify-reconcile.sh"
)

pass=0; fail=0; skip=0
run() { # label script  -> echoes result, updates counters; returns script rc
  local label="$1" script="$2" rc
  timeout 150 bash "$script" >/tmp/verify-all.$$ 2>&1; rc=$?
  return $rc
}
printf '%-62s %s\n' "BEAT" "STATUS"
printf '%s\n' "----------------------------------------------------------------------"
for e in "${OFFLINE[@]}"; do
  label="${e%%|*}"; script="${e##*|}"
  if run "$label" "$script"; then printf '%-62s PASS\n' "$label"; pass=$((pass+1))
  else printf '%-62s FAIL (exit)\n' "$label"; fail=$((fail+1)); echo "    last: $(tail -1 /tmp/verify-all.$$)"; fi
done
echo
for e in "${LIVE[@]}"; do
  label="${e%%|*}"; script="${e##*|}"
  if run "$label" "$script"; then printf '%-62s PASS (live)\n' "$label"; pass=$((pass+1))
  else
    if [ "$REQUIRE_LIVE" = 1 ]; then printf '%-62s FAIL (live)\n' "$label"; fail=$((fail+1))
    else printf '%-62s SKIP-live (run talk/up.sh)\n' "$label"; skip=$((skip+1)); fi
  fi
done
rm -f "/tmp/verify-all.$$"
echo
echo "pass=$pass fail=$fail skip-live=$skip"
[ "$fail" -eq 0 ] || { echo "SOME BEATS WOULD FAIL ON STAGE"; exit 1; }
echo "OK: every offline beat is backed by a passing verify-*.sh."
[ "$skip" -gt 0 ] && echo "(live reconcile beats pending a brought-up cluster — expected off-venue)"
exit 0
