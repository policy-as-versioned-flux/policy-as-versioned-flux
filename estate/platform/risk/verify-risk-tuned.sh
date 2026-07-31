#!/usr/bin/env bash
# Beat: "Enforcement is tuned by the £, not a timer." The FAIR residual a Deny
# buys (ALE_warn - ALE_deny) is compared to the org's tolerance band; above it,
# Audit MUST escalate to Deny. Tightening a versioned triple raises that £ and
# flips the verdict — the justification a reviewer reads in the PR is a number.
# Exits non-zero if the beat would fail on stage. Fully offline (python only).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
say()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
fail() { echo "FAIL: $*" >&2; exit 1; }

LOOSE="$HERE/../fair/scenarios/driftwood-cart-pii.json"
TIGHT="$HERE/scenarios/driftwood-cart-pii-tightened.json"

say "0. the engine's own asserts (band selection, tightening raises £, no timer)"
timeout 90 python3 "$HERE/enforce.py" selfcheck || fail "enforce.py selfcheck failed"

say "1. driftwood, loose triple: risk_bought below the £40k band -> Audit"
a="$(timeout 90 python3 "$HERE/enforce.py" action "$LOOSE" --org driftwood)"
[ "$a" = "Audit" ] || fail "loose cart-PII should Audit in driftwood, got '$a'"

say "2. tighten the triple (LM reassessed upward): £ rises over the band -> Deny"
b="$(timeout 90 python3 "$HERE/enforce.py" action "$TIGHT" --org driftwood)"
[ "$b" = "Deny" ] || fail "tightened cart-PII should Deny in driftwood, got '$b'"

say "3. the flip is justified by the number, not a date"
timeout 90 python3 "$HERE/enforce.py" decide "$TIGHT" --org driftwood \
  | grep -q 'justified by the' || fail "decision reason missing the £ justification"

say "4. proportionality: the SAME loose control Denies under ludlow's strict band"
c="$(timeout 90 python3 "$HERE/enforce.py" action "$LOOSE" --org ludlow)"
[ "$c" = "Deny" ] || fail "loose cart-PII should Deny under ludlow's strict band, got '$c'"

echo "PASS: the £ picks Audit vs Deny; tightening a triple flips Audit->Deny by a number."
