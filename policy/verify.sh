#!/usr/bin/env bash
# Runnable check for the policy repo scaffold (issue 02):
#   1. kyverno test fixtures pass/fail/skip as expected (the CEL logic + version
#      self-scoping).
#   2. kustomize renders the nameSuffix and the objectSelector's policy-version
#      value from the one substituted value in kustomization.yaml.
set -euo pipefail
cd "$(dirname "$0")"

echo "== kyverno test =="
kyverno test tests/require-department-label

echo "== kustomize build: nameSuffix + selector substitution =="
out=$(kustomize build workloads/kyverno/require-department-label)
name=$(yq '.metadata.name' <<<"$out")
selector=$(yq '.spec.matchConstraints.objectSelector.matchLabels."mycompany.com/policy-version"' <<<"$out")
[ "$name" = "require-department-label-1.0.0" ] || { echo "FAIL: nameSuffix not applied (got '$name')"; exit 1; }
[ "$selector" = "1.0.0" ] || { echo "FAIL: version not substituted into objectSelector (got '$selector')"; exit 1; }
echo "OK: name=$name, policy-version selector=$selector"
