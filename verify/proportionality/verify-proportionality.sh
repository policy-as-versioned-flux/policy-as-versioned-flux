#!/usr/bin/env bash
# THE MONEY SHOT. "The same control resolves to Audit in driftwood and Deny in
# ludlow because their £ differ." One shared control (encrypt-at-rest), one shared
# FAIR scenario, one shared policy body — evaluated against each institution's
# risk-appetite band. The band alone flips the £-derived verdict. Proportionality
# proven by comparison, not asserted.
#
# Exits non-zero if the beat would fail on stage. OFFLINE core (python3; kyverno
# for the body proof). Optional LIVE tail dry-runs the rendered policies if the
# per-institution kind clusters are reachable.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Post-split (mo-12): platform is a real, separate GitHub repo, not a sibling
# directory. RISK is now an ordinary pinned dependency, fetched by
# clone-estate.sh into .estate-clone/ rather than reached directly.
RISK="$HERE/../../.estate-clone/platform/risk"
SCEN="$HERE/scenarios/encrypt-at-rest.json"
say()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
fail() { echo "FAIL: $*" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }

have python3 || fail "python3 required"
[ -d "$RISK" ] || bash "$HERE/../../clone-estate.sh" || fail "could not assemble .estate-clone/ (needs network — see clone-estate.sh)"

# decide <org> -> prints the enforce.py decision JSON for the shared scenario.
decide() { timeout 90 python3 "$RISK/enforce.py" decide "$SCEN" --org "$1"; }
# field <org> <key> -> pull one value out of that org's decision.
field() { decide "$1" | python3 -c "import sys,json;print(json.load(sys.stdin)['$2'])"; }

say "0. the £ engine's own asserts (band selection, tightening raises £, no timer)"
timeout 90 python3 "$RISK/enforce.py" selfcheck || fail "enforce.py selfcheck failed"

say "1. the SAME control + SAME scenario -> divergent £-derived verdicts"
dw_verdict="$(field driftwood verdict)"
lud_verdict="$(field ludlow verdict)"
[ "$dw_verdict" = "Audit" ] || fail "driftwood should Audit encrypt-at-rest, got '$dw_verdict'"
[ "$lud_verdict" = "Deny" ] || fail "ludlow should Deny encrypt-at-rest, got '$lud_verdict'"

say "2. the £ that DRIVES it — same risk_bought, different appetite band"
dw_rb="$(field driftwood risk_bought)";  dw_tol="$(field driftwood tolerance)"
lud_rb="$(field ludlow risk_bought)";    lud_tol="$(field ludlow tolerance)"
# Same control, same scenario -> risk_bought is IDENTICAL across institutions.
python3 - "$dw_rb" "$lud_rb" <<'PY' || fail "risk_bought differs across orgs — not the same control"
import sys
a, b = float(sys.argv[1]), float(sys.argv[2])
assert abs(a - b) < 1e-6, f"risk_bought must be identical for the shared control: {a} vs {b}"
PY
# The verdict divergence is PURELY the band: rb <= driftwood band, rb > ludlow band.
python3 - "$dw_rb" "$dw_tol" "$lud_tol" <<'PY' || fail "the £ does not straddle the two bands"
import sys
rb, dw_tol, lud_tol = map(float, sys.argv[1:4])
assert rb <= dw_tol, f"risk_bought £{rb:,.0f} must sit UNDER driftwood's £{dw_tol:,.0f} band (Audit)"
assert rb >  lud_tol, f"risk_bought £{rb:,.0f} must sit OVER ludlow's £{lud_tol:,.0f} band (Deny)"
print(f"    risk_bought £{rb:,.0f}  |  driftwood band £{dw_tol:,.0f} -> Audit  |  ludlow band £{lud_tol:,.0f} -> Deny")
PY
[ "${dw_tol%.*}" != "${lud_tol%.*}" ] || fail "the bands must differ for the comparison to mean anything"

say "3. the rendered policies carry the £-derived action (not hand-authored)"
python3 "$HERE/render.py" --check || fail "committed policies drifted from the £-derived render"
grep -q 'validationActions: \[Audit\]' "$HERE/policies/encrypt-at-rest-driftwood.yaml" \
  || fail "driftwood policy must carry validationActions: [Audit]"
grep -q 'validationActions: \[Deny\]'  "$HERE/policies/encrypt-at-rest-ludlow.yaml" \
  || fail "ludlow policy must carry validationActions: [Deny]"
# The bodies are byte-identical EXCEPT the action/org lines — that is the whole point.
diff_lines="$(diff "$HERE/policies/encrypt-at-rest-driftwood.yaml" "$HERE/policies/encrypt-at-rest-ludlow.yaml" \
  | grep -c '^[<>]' || true)"
# Only validationActions + the two org labels (part-of, proportionality-org) differ: 3 lines each side.
[ "$diff_lines" -le 6 ] || fail "policies differ in more than the action+org lines ($diff_lines) — not the same control"

say "4. the shared control body is a real, self-scoping policy (pass/fail/unversioned)"
if have kyverno; then
  timeout 120 kyverno test "$HERE/tests/encrypt-at-rest" >/dev/null \
    || fail "encrypt-at-rest kyverno test failed"
else
  echo "    (skipped: kyverno CLI not found — offline body proof unavailable here)"
fi

# --- optional LIVE tail: dry-run the rendered policies on their clusters --------
live=0
for org in driftwood ludlow; do
  ctx="kind-$org"
  have kubectl && kubectl --context "$ctx" version >/dev/null 2>&1 || continue
  # Needs Kyverno's ValidatingPolicy CRD present to validate server-side.
  if ! kubectl --context "$ctx" get crd validatingpolicies.policies.kyverno.io >/dev/null 2>&1; then
    say "5. live($org): cluster reachable but Kyverno CRDs not installed — skipping dry-run (offline proof stands)"
    continue
  fi
  say "5. live($org): the rendered policy applies clean (server dry-run)"
  timeout 60 kubectl --context "$ctx" apply --dry-run=server \
    -f "$HERE/policies/encrypt-at-rest-$org.yaml" >/dev/null \
    || fail "$org rendered policy failed server dry-run on $ctx"
  live=1
done
[ "$live" = 1 ] || say "5. live dry-run tail skipped (no cluster with Kyverno CRDs reachable) — offline proof stands"

echo "PASS: same control, same £ (risk_bought £${dw_rb%.*}) — Audit in driftwood, Deny in ludlow. Proportionality by comparison."
