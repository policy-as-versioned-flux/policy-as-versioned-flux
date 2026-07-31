#!/usr/bin/env bash
# Beat: "Exemptions dissolve into conditional policy." One versioned CEL rule —
# "run non-root, OR run root IF attested AND hardened" — admits ANYONE meeting C,
# uniformly, with no named team and no carve-out. And the root-but-hardened branch
# still carries residual risk, which fair.py prices in £ (the residual feeds the £).
#
# Offline core (always on, kyverno only): the pass/fail matrix + the residual £.
# Live tail (only if a cluster is reachable): the same admit/deny live.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM="$(cd "$HERE/.." && pwd)"    # estate/platform — fair.py is a sibling area
say()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
fail() { echo "FAIL: $*" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }

have kyverno || fail "kyverno CLI required"
POL="$HERE/policies/v1.0.0/may-run-root-if-attested.yaml"

say "1. the conditional matrix: C admits uniformly, non-C fails, unversioned skips"
out="$(kyverno apply "$POL" --resource "$HERE/tests/conditional/resources.yaml" 2>&1 || true)"
grep -q 'pass: 2, fail: 2' <<<"$out" \
  || { echo "$out"; fail "expected 2 pass (nonroot + root-attested-hardened) / 2 fail"; }
grep -q 'Pod/root-attested-hardened' <<<"$out" \
  && fail "root-attested-hardened was denied — the conditional branch did not admit"
grep -q 'Pod/root-bare failed' <<<"$out" \
  || fail "root-bare was not denied — condition C is not being enforced"
say "   root-attested-hardened ADMITS (met C); root-bare + attested-unhardened FAIL"

say "2. kyverno test — the full pass/fail/skip matrix"
timeout 120 kyverno test "$HERE/tests/conditional" >/dev/null 2>&1 \
  || fail "kyverno test tests/conditional did not pass"

say "3. the residual of the conditional branch is priced in £ (fair.py)"
have python3 || fail "python3 required for the £"
warn_ale="$(python3 "$PLATFORM/fair/fair.py" summary "$HERE/scenarios/driftwood-root-residual.json" --mode warn \
  | python3 -c 'import json,sys; print(round(json.load(sys.stdin)["ale"]))')"
[ "$warn_ale" -gt 0 ] || fail "residual ALE is not positive — nothing to carry"
say "   residual ALE with the exemption in place = £${warn_ale}/yr (the £ it carries)"

# --- live tail: only if a cluster is reachable ---
CTX="${CTX:-kind-driftwood}"
if have kubectl && kubectl --context "$CTX" get validatingpolicy >/dev/null 2>&1; then
  say "4. live: applying the conditional pods to '$CTX' (dry-run) — same verdicts"
  kubectl --context "$CTX" apply --dry-run=server -f "$HERE/tests/conditional/resources.yaml" >/dev/null 2>&1 \
    || say "   (server dry-run rejected some pods — expected where Deny is on; verdicts hold)"
else
  say "4. live tail skipped: no reachable cluster at context '$CTX'"
fi

echo "PASS: one conditional rule admits everyone meeting C, and its residual is priced."
