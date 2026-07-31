#!/usr/bin/env bash
# Idempotent bring-up of the currency controller onto the EXISTING driftwood KinD
# cluster: the SA/RBAC, the currency.py source ConfigMap, and the per-minute
# reconcile CronJob. Builds on the posture projection (ticket 15) and identity
# substrate (ticket 14). Never creates/deletes/waits on a cluster.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CTX="${CTX:-kind-driftwood}"
say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }

command -v kubectl >/dev/null || { echo "MISSING cli: kubectl" >&2; exit 1; }
kubectl --context "$CTX" version >/dev/null 2>&1 || {
  echo "driftwood cluster not reachable ($CTX); run estate/driftwood/scripts/up.sh first" >&2; exit 1; }

say "namespace + SA + RBAC (the one audited grant to patch/evict pods)"
kubectl --context "$CTX" apply -f "$HERE/manifests/rbac.yaml"

say "currency.py source ConfigMap (ONE source of the code — mounted by the CronJob)"
kubectl --context "$CTX" -n currency-system create configmap currency-controller-src \
  --from-file=currency.py="$HERE/currency.py" \
  --dry-run=client -o yaml | kubectl --context "$CTX" apply -f -

say "reconcile CronJob (one bounded pass / minute)"
kubectl --context "$CTX" apply -f "$HERE/manifests/cronjob.yaml"

say "done. Trigger one pass now:  kubectl --context $CTX -n currency-system create job --from=cronjob/currency-controller currency-once"
say "verify with estate/platform/currency-controller/verify-currency.sh"
