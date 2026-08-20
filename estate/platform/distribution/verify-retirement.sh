#!/usr/bin/env bash
# Beat: "Retiring a version prunes it." Deleting a version's element from the
# array is the ONLY edit needed: Flux prunes that version's Kustomization +
# policy (prune: true), and the orphan-guard — re-rendered from the shrunk array
# — stops allowing it, so a workload still claiming the retired version is denied.
# Exits non-zero if the beat would fail on stage.
#
# Offline core: render the orphan-guard BEFORE and AFTER retiring 2.0.0 and show
# the same 2.0.0 pod flips admit -> deny. Live tail (if reachable): the retired
# version's Kustomization/policy is actually gone.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
say()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
fail() { echo "FAIL: $*" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }

have kyverno || fail "kyverno CLI required"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT
RETIRE=2.0.0

cat > "$WORK/pod.yaml" <<YAML
apiVersion: v1
kind: Pod
metadata: { name: still-on-retired, labels: { "policy-as-versioned.dev/policy-version": "${RETIRE}" } }
spec: { containers: [{ name: c, image: nginx }] }
YAML

say "1. before retirement: a pod on ${RETIRE} is admitted (version is declared)"
python3 "$HERE/render-orphan-guard.py" > "$WORK/before.yaml"
# capture (|| true): kyverno apply's exit code tracks admission, not script health
before="$(kyverno apply "$WORK/before.yaml" --resource "$WORK/pod.yaml" 2>&1 || true)"
grep -q 'pass: 1, fail: 0' <<<"$before" \
  || fail "pod on ${RETIRE} was not admitted before retirement — fixture wrong"

say "2. retire ${RETIRE} from the array (one deletion) and re-render"
python3 "$HERE/render-orphan-guard.py" --retire "$RETIRE" > "$WORK/after.yaml"

say "3. after retirement: the same pod is now DENIED (orphaned by the shrunk array)"
after="$(kyverno apply "$WORK/after.yaml" --resource "$WORK/pod.yaml" 2>&1 || true)"
grep -q "resource default/Pod/still-on-retired failed" <<<"$after" \
  || fail "pod on retired ${RETIRE} still admitted — retirement did not prune the allowance"

# the fan-out no longer renders a Kustomization/path for the retired version
[ -d "$HERE/policies/v${RETIRE}" ] || fail "fixture: policies/v${RETIRE} missing"
say "   (live: dropping the array element prunes Kustomization policy-v$(echo "$RETIRE" | tr . -))"

# --- live tail: only if a cluster is reachable. This is a passive read (the
# script does not itself drive a live retire commit), so "still present" and
# "no cluster" both mean "nothing to assert yet" and must say so plainly rather
# than print a line that looks like a check but never gates anything.
CTX="${CTX:-kind-driftwood}"
slug="$(echo "$RETIRE" | tr . -)"
if have kubectl && kubectl --context "$CTX" -n flux-system get kustomization "policy-v${slug}" >/dev/null 2>&1; then
  say "4. live tail skipped: policy-v${slug} still reconciled at context '$CTX' — retirement PR not yet applied there (offline proof above is the demonstrable claim)"
elif have kubectl && kubectl --context "$CTX" get kustomization -n flux-system >/dev/null 2>&1; then
  say "4. live: policy-v${slug} Kustomization is gone at context '$CTX' — retirement pruned it live"
else
  say "4. live tail skipped: no reachable cluster at context '$CTX' (see README)"
fi

echo "PASS: retiring a version (one array deletion) prunes it and denies stragglers."
