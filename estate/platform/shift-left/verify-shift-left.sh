#!/usr/bin/env bash
# verify-shift-left.sh -- the offline proof behind the "CI catches an
# Audit->Deny flip pre-merge" beat (ticket 12). Runs the REAL kyverno CLI,
# needs no cluster. Exits non-zero if the beat would fail on stage.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

if ! command -v kyverno >/dev/null; then
  echo "SKIP: kyverno CLI not found -- shift-left check needs it (offline, no cluster)"
  exit 0
fi

echo "== a compliant change passes across its ±1 supported window =="
python3 ci-check.py --resource fixtures/workload-compliant.yaml

echo
echo "== an unversioned workload is out of scope, passes trivially =="
python3 ci-check.py --resource fixtures/workload-unversioned.yaml

echo
echo "== an Audit->Deny flip is caught pre-merge (must fail CI) =="
if python3 ci-check.py --resource fixtures/workload-flip.yaml; then
  echo "FAIL: ci-check.py passed a workload that fails its target version's real rule" >&2
  exit 1
fi
echo "(non-zero above is expected -- the flip was caught)"

echo
echo "== a version the array doesn't declare is refused, not silently skipped =="
if python3 ci-check.py --resource fixtures/workload-compliant.yaml --target 9.9.9 2>/tmp/shift-left-orphan.err; then
  echo "FAIL: ci-check.py did not reject an orphan target version" >&2
  exit 1
fi
grep -q "not in the platform-declared array" /tmp/shift-left-orphan.err

echo
echo "shift-left: all offline proofs passed"
