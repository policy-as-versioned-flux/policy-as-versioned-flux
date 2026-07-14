#!/usr/bin/env bash
# Runnable check for the policy repo scaffold (issues 02, 03):
#   1. kyverno test fixtures pass/fail/skip as expected (the CEL logic + version
#      self-scoping), for both the Audit lane-keeper and the Deny gate.
#   2. kustomize renders the nameSuffix and the objectSelector's policy-version
#      value from the one substituted value in kustomization.yaml, for both.
#
# What this does NOT prove: `kyverno test` evaluates the CEL rule, not the
# admission-webhook behaviour that validationActions actually controls (Audit
# reports-but-admits vs Deny refuses). See ./verify-live.sh for that, run
# against a live cluster (fleet/up.sh).
set -euo pipefail
cd "$(dirname "$0")"

for name in require-department-label require-known-department-label; do
  echo "== kyverno test: $name =="
  kyverno test "tests/$name"

  echo "== kustomize build: nameSuffix + selector substitution ($name) =="
  out=$(kustomize build "workloads/kyverno/$name")
  got_name=$(yq '.metadata.name' <<<"$out")
  selector=$(yq '.spec.matchConstraints.objectSelector.matchLabels."mycompany.com/policy-version"' <<<"$out")
  [ "$got_name" = "$name-1.0.0" ] || { echo "FAIL: nameSuffix not applied (got '$got_name')"; exit 1; }
  [ "$selector" = "1.0.0" ] || { echo "FAIL: version not substituted into objectSelector (got '$selector')"; exit 1; }
  echo "OK: name=$got_name, policy-version selector=$selector"
done
