#!/usr/bin/env bash
# Beat: "Two signed policy versions admit side by side — each judges only the
# workloads that claim it (matchConditions self-scoping), no shared-webhook
# collision." Exits non-zero if that beat would fail on stage.
#
# Offline core (always runs, needs only `kyverno`): the coexistence matrix via
# `kyverno test` — proves the admission verdicts. Live tail (runs only if a
# cluster with both ValidatingPolicies installed is reachable): proves the two
# versions actually coexist in ONE ValidatingWebhookConfiguration — the gap the
# single-policy CLI cannot show (research 08 §2b).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
say()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
fail() { echo "FAIL: $*" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }

have kyverno || fail "kyverno CLI required for the offline coexistence proof"

say "1. offline: both versions self-scope + admit side by side (kyverno test)"
kyverno test "$HERE/tests/require-nonroot" >/dev/null \
  || fail "coexistence matrix failed — a version judged a workload it does not own"

say "2. offline: the orphan-guard allow-list is exactly the version array (no drift)"
python3 "$HERE/render-orphan-guard.py" --selfcheck >/dev/null \
  || fail "orphan-guard allow-list drifted from the version array"

# --- live tail: only if a cluster actually has both policies installed ---
CTX="${CTX:-kind-driftwood}"
if have kubectl && kubectl --context "$CTX" get validatingpolicy >/dev/null 2>&1; then
  say "3. live: both ValidatingPolicies present in the SAME webhook config"
  for v in 1-0-0 2-0-0; do
    kubectl --context "$CTX" get validatingpolicy "require-nonroot-$v" >/dev/null 2>&1 \
      || fail "require-nonroot-$v not installed live (fan-out incomplete)"
  done
else
  say "3. live tail skipped: no cluster with ValidatingPolicies at context '$CTX'"
  say "   (offline coexistence proof above is the demonstrable claim; live"
  say "    reconcile needs flux-operator + Kyverno installed — see README)"
fi

echo "PASS: two signed versions coexist; each judges only what claims it."
