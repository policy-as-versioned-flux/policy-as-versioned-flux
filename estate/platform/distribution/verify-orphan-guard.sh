#!/usr/bin/env bash
# Beat: "A version not in the array cannot run." A pod claiming a policy-version
# the array does not declare is DENIED by the orphan-guard; a pod claiming a
# declared version is admitted; an unversioned pod is out of scope. The
# allow-list is rendered from the same array, so it cannot drift from the
# installed set. Exits non-zero if the beat would fail on stage.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
say()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
fail() { echo "FAIL: $*" >&2; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }

have kyverno || fail "kyverno CLI required"
WORK="$(mktemp -d)"; trap 'rm -rf "$WORK"' EXIT

say "1. render the orphan-guard from the version array (declares 1.0.0, 2.0.0)"
python3 "$HERE/render-orphan-guard.py" > "$WORK/orphan-guard.yaml"

cat > "$WORK/pods.yaml" <<'YAML'
apiVersion: v1
kind: Pod
metadata: { name: declared, labels: { "policy-as-versioned.dev/policy-version": "1.0.0" } }
spec: { containers: [{ name: c, image: nginx }] }
---
apiVersion: v1
kind: Pod
metadata: { name: orphan, labels: { "policy-as-versioned.dev/policy-version": "3.0.0" } }
spec: { containers: [{ name: c, image: nginx }] }
---
apiVersion: v1
kind: Pod
metadata: { name: unversioned }
spec: { containers: [{ name: c, image: nginx }] }
YAML

say "2. an undeclared version (3.0.0) is denied; a declared one (1.0.0) admits"
# kyverno apply exits non-zero when a resource is denied — that IS the pass
# condition here, so capture (|| true) and assert on the text, not the code.
out="$(kyverno apply "$WORK/orphan-guard.yaml" --resource "$WORK/pods.yaml" 2>&1 || true)"
grep -q "resource default/Pod/orphan failed" <<<"$out" \
  || fail "orphan pod (3.0.0) was NOT denied — a version outside the array could run"
if grep -q "resource default/Pod/declared failed" <<<"$out"; then
  fail "a DECLARED version (1.0.0) was wrongly denied by the orphan-guard"
fi
# exactly one fail (the orphan), one skip (unversioned, out of scope)
grep -qE 'pass: 1, fail: 1, warn: 0, error: 0, skip: 1' <<<"$out" \
  || fail "unexpected verdict spread: $(tail -1 <<<"$out")"

echo "PASS: only versions the array declares can run; the allow-list is the array."
