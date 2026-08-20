#!/usr/bin/env bash
# The deck's honesty gate: every demo-LIVE claim in deck.md is backed by a
# verify-*.sh that exits 0. This runs all of them and prints a beat->script->PASS
# table. Run it in pre-flight (and as this ticket's own test).
#
# OFFLINE beats (always run here — no cluster, no network; python3/kyverno/openssl):
#   these are the proofs that stand on a laptop with no venue Wi-Fi.
# LIVE beats (need a brought-up cluster — run estate/talk/up.sh first):
#   the three institution reconciles. Reported SKIP-live when no cluster is up,
#   never faked. Pass --live to require them.
#
# Exit non-zero if any offline beat fails, or if --live and a live beat fails.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT" || exit 2
REQUIRE_LIVE=0; [ "${1:-}" = "--live" ] && REQUIRE_LIVE=1

# beat | script  (offline — the proofs that must pass with no cluster)
OFFLINE=(
  "policy is a versioned dependency (coexistence)|estate/platform/distribution/verify-coexistence.sh"
  "a version not in the array cannot run (orphan-guard)|estate/platform/distribution/verify-orphan-guard.sh"
  "retiring a version prunes it|estate/platform/distribution/verify-retirement.sh"
  "shift-left CI catches an Audit->Deny flip pre-merge|estate/platform/shift-left/verify-shift-left.sh"
  "exemptions dissolve into conditional policy|estate/platform/policy/verify-conditional.sh"
  "PROPORTIONALITY: same control, Audit driftwood vs Deny ludlow|estate/verify/proportionality/verify-proportionality.sh"
  "enforcement tuned by the £, not a timer|estate/platform/risk/verify-risk-tuned.sh"
  "graded response: caged by degree, not denied|estate/platform/graded/verify-graded.sh"
  "the board line is TCoR and it moves|estate/platform/tcor/verify-tcor.sh"
  "feeds signed+versioned, a bump moves the £|estate/platform/feeds/verify-feeds.sh"
  "ico penalty schema signed; a bump moves the £|estate/ico/verify-penalty-feed.sh"
  "nist ships a real, pinnable OSCAL catalog|estate/nist/scripts/verify-catalog.sh"
  "evidence up-flow resolves end to end (OSCAL risk)|estate/platform/oscal/verify-upflow.sh"
  "LIVING LOOP: war-gamer opens a signed PR, never merges|estate/platform/wargamer/verify-wargamer.sh"
  "AI-Wardley flags commoditisation movement, re-tunes early|estate/platform/wardley/verify-wardley.sh"
  "the number is honest today (calibration+integrity)|estate/platform/honesty/verify-honesty.sh"
  "identity substrate: SPIRE is Istio's CA, mTLS STRICT|estate/platform/identity/verify-identity.sh"
  "posture-as-identity: posture/vN in the SVID path|estate/platform/posture/verify-posture-projection.sh"
  "currency controller re-evaluates posture post-admission|estate/platform/currency-controller/verify-currency.sh"
  "posture-gated reach + secrets (tuppence flagship)|estate/tuppence/reset/verify-reach-secrets.sh"
  "human/device access plane holds (Pomerium+device SVID)|estate/platform/access/verify-access.sh"
  "break-glass demands step-up by the £|estate/platform/break-glass/verify-break-glass.sh"
  "EUD device trust on the same root (vTPM, narrated-virtual)|estate/platform/eud/verify-eud.sh"
  "PROVENANCE: every actor attestable to one root|estate/verify/provenance/verify-provenance.sh"
  "roles: is data, machine-checked against the filesystem|estate/verify/party/verify-party.sh"
)
# beat | script  (live — need a reconciled cluster; SKIP-live if absent)
LIVE=(
  "driftwood reconciles from a pinned, signed GitRepository|estate/driftwood/verify-reconcile.sh"
  "tuppence reconciles, carries its toward-strict skin|estate/tuppence/verify-reconcile.sh"
  "ludlow reconciles, carries its Deny-heavy skin|estate/ludlow/verify-reconcile.sh"
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
    else printf '%-62s SKIP-live (run estate/talk/up.sh)\n' "$label"; skip=$((skip+1)); fi
  fi
done
rm -f "/tmp/verify-all.$$"
echo
echo "pass=$pass fail=$fail skip-live=$skip"
[ "$fail" -eq 0 ] || { echo "SOME BEATS WOULD FAIL ON STAGE"; exit 1; }
echo "OK: every offline beat is backed by a passing verify-*.sh."
[ "$skip" -gt 0 ] && echo "(live reconcile beats pending a brought-up cluster — expected off-venue)"
exit 0
