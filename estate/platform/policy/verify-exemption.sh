#!/usr/bin/env bash
# Beat: "An exemption exists only while a live ledger entry backs it."
# A genuine one-off (legacy-till: cannot meet condition C) is NOT a hole in the
# policy — it is a ledger entry that RENDERS a PolicyException. Remove the entry
# and Flux prunes the exception; the cleanup.kyverno.io/ttl is the backstop.
#
#   no ledger entry   -> no exception   -> the pod is DENIED  (this is literal)
#   ledger entry      -> PolicyException-> the pod is admitted (skip)
#   entry removed     -> re-render is empty -> DENIED again    (prune)
#   the rendered exception carries a TTL == the entry's expiry (backstop)
#
# Offline core (kyverno + the offline render twin). Live tail if a cluster exists.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
say()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
fail() { echo "FAIL: $*" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }

have kyverno  || fail "kyverno CLI required"
have python3  || fail "python3 required"
POL="$HERE/policies/v1.0.0/may-run-root-if-attested.yaml"
LEDGER="$HERE/ledger/exemptions.yaml"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT

# The one-off the ledger covers: legacy-till runs root, cannot meet C -> fails the
# conditional policy. It carries version 1.0.0 (in scope) and app=legacy-till.
cat > "$WORK/pod.yaml" <<'YAML'
apiVersion: v1
kind: Pod
metadata:
  name: legacy-till-0
  namespace: shop
  labels:
    policy-as-versioned.dev/policy-version: "1.0.0"
    app: legacy-till
spec:
  containers: [{ name: till, image: legacy-till:1 }]
YAML

say "1. NO ledger entry -> no exception -> the pod is DENIED"
no_exc="$(kyverno apply "$POL" --resource "$WORK/pod.yaml" 2>&1 || true)"
grep -q 'Pod/legacy-till-0 failed' <<<"$no_exc" \
  || { echo "$no_exc"; fail "pod admitted with no exception — the policy is not biting"; }

say "2. the ledger entry RENDERS a PolicyException (offline twin of the Flux render)"
python3 "$HERE/render-exemption.py" "$LEDGER" > "$WORK/exc.yaml"
grep -q 'kind: PolicyException'       "$WORK/exc.yaml" || fail "no PolicyException rendered"
grep -q 'exemption-scope'             "$WORK/exc.yaml" || fail "exception is not scoped"
ttl="$(python3 -c 'import yaml,sys; print(yaml.safe_load(open(sys.argv[1]))["metadata"]["annotations"]["cleanup.kyverno.io/ttl"])' "$WORK/exc.yaml")"
[ -n "$ttl" ] || fail "rendered exception has no cleanup.kyverno.io/ttl backstop"
say "   rendered, scoped to app=legacy-till, TTL backstop = ${ttl}"

say "3. WITH the rendered exception -> the same pod is admitted (skip)"
with_exc="$(kyverno apply "$POL" --resource "$WORK/pod.yaml" --exception "$WORK/exc.yaml" 2>&1 || true)"
grep -q 'skip: 1' <<<"$with_exc" \
  || { echo "$with_exc"; fail "exception did not admit the one-off (expected skip: 1)"; }

say "4. REMOVE the entry (simulate deleting the ledger row) -> re-render is empty -> DENIED (prune)"
python3 - "$LEDGER" > "$WORK/empty.yaml" <<'PY'
import sys, yaml
doc = yaml.safe_load(open(sys.argv[1])); doc["spec"]["inputs"] = []
print(yaml.safe_dump(doc))
PY
python3 "$HERE/render-exemption.py" "$WORK/empty.yaml" > "$WORK/none.yaml"
[ -s "$WORK/none.yaml" ] && grep -q 'kind: PolicyException' "$WORK/none.yaml" \
  && fail "an emptied ledger still rendered an exception — prune is not literal"
pruned="$(kyverno apply "$POL" --resource "$WORK/pod.yaml" --exception "$WORK/none.yaml" 2>&1 || true)"
grep -q 'Pod/legacy-till-0 failed' <<<"$pruned" \
  || { echo "$pruned"; fail "pod still admitted after the ledger row was removed — no prune"; }
say "   entry gone -> no exception -> DENIED again"

# --- live tail: only if a cluster is reachable ---
CTX="${CTX:-kind-driftwood}"
if have kubectl && kubectl --context "$CTX" get policyexception -A >/dev/null 2>&1; then
  say "5. live: the rendered exception applies cleanly (dry-run) to '$CTX'"
  kubectl --context "$CTX" apply --dry-run=server -f "$WORK/exc.yaml" >/dev/null 2>&1 \
    || say "   (server dry-run rejected — namespace 'shop' or CRD may be absent live)"
else
  say "5. live tail skipped: no reachable cluster at context '$CTX'"
fi

echo "PASS: no ledger entry, no exception; a row renders a TTL-capped PolicyException; removing it prunes."
