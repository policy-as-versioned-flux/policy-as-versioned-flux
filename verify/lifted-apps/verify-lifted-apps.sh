#!/usr/bin/env bash
# Beat (eco-system ticket 33): ledger, storefront and reports belong to their adopters.
#
# Ticket 13 decided (2026-08-28) that the three applications the incumbent org
# `policy-as-versioned-flux` built move to the adopter whose institutional shape they fit --
# ledger to tuppence, storefront to driftwood, reports to ludlow -- and that a lift is a
# re-label to `policy-as-versioned.dev/policy-version`, a re-pin to the adopter's own composed
# artefact, and a renovate.json that enables the stack's manager and the dependency dashboard.
#
# A LIFT THAT LEAVES THE OLD COPY BEING READ HAS LIFTED NOTHING. So this grades the SERVED
# artefact and the operation that reaches it, never the presence of a file:
#
#   * the served artefact is the adopter's `gitops/apps/` tree, which its own Flux Kustomization
#     reconciles at `path: ./apps`; the operation is kustomize's accumulation of
#     `gitops/apps/kustomization.yaml`'s `resources[]`. A manifest in that directory the
#     kustomization does not name is served to nobody, and is graded as the proxy it is;
#   * the version it claims is measured against the ADOPTER'S OWN composed artefact
#     (`composed/orphan-guard.yaml`'s allowed array), never a constant held in this repository;
#   * the last word on whether the workload is admissible belongs to the estate's own engine:
#     step 3 runs the real `kyverno apply` over the adopter's own `composed/policies/v<claimed>/`
#     against the served manifest, offline, exactly as each adopter's shift-left job does;
#   * the stack's Renovate manager must POINT AT the lifted stack manifest, not merely be named
#     in `enabledManagers`.
#
#   PASS (exit 0)  every registered lift has landed in its adopter, is served, is re-labelled, is
#                  admitted by that adopter's own composed policy set, and is bumped there
#   FAIL (exit 1)  a landed lift is wrong in any of those ways; the same app landed in two
#                  adopters; a working copy of a lifted app is in the hub; kyverno refuses a
#                  served workload; the register disagrees with the tree
#   SKIP (exit 3)  a registered lift has not landed in its adopter yet -- the line names the pull
#                  request each waits on -- or there is no estate clone to read at all
#
# The kyverno CLI going missing is deliberately NOT a could-not-look, the same call
# verify-refusal-by-another-name.sh records: a runner that has lost its instrument goes red
# rather than shrugging.
#
# WHAT IT CANNOT LOOK AT is printed on every run from lifted_apps.BLIND_SPOTS, and the limit that
# matters is a NUMBER the report prints rather than a sentence that goes stale: how many of the
# lifted apps are still served an image built and published by the incumbent org. The source and
# the served manifest moved; the image build did not, because it needs a workflow job in the
# adopter and a registry under the adopter's own organisation. Both are on ticket 33's
# `## Waits on the owner`.
#
#   verify-lifted-apps.sh             selfcheck first, then grade the hub and the estate clone
#   verify-lifted-apps.sh --selfcheck selfcheck only: the grader's own asserts over planted trees
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
PY="${PYTHON:-python3}"
REG="${LIFTED_APPS_REGISTER:-$HERE/register.yaml}"
ESTATE="${LIFTED_APPS_ESTATE:-$ROOT/.estate-clone}"
say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }

# A throwaway estate carrying one correct lift, written by the same shell that then breaks it.
# Nothing here reads the real estate, and the fixture register points at the fixture only.
plant() {
  local t="$1" a="$t/estate/tuppence"
  mkdir -p "$a/composed/policies/v4.0.0" "$a/gitops/apps" "$a/apps/ledger" "$t/hub"
  printf '{}\n' >"$a/composed/policies/v4.0.0/require-nonroot.yaml"
  cat >"$a/composed/orphan-guard.yaml" <<'YAML'
apiVersion: policies.kyverno.io/v1alpha1
kind: ValidatingPolicy
metadata: {name: policy-version-orphan-guard}
spec:
  variables:
  - name: allowed
    expression: '[''4.0.0'']'
YAML
  cat >"$a/gitops/apps/kustomization.yaml" <<'YAML'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ledger.yaml
YAML
  cat >"$a/gitops/apps/ledger.yaml" <<'YAML'
apiVersion: v1
kind: Pod
metadata:
  name: ledger
  namespace: tuppence
  labels: {"policy-as-versioned.dev/policy-version": "4.0.0"}
spec:
  securityContext: {runAsNonRoot: true, runAsUser: 1000}
  containers:
    - name: ledger
      image: ghcr.io/planted/ledger@sha256:0000
      securityContext: {readOnlyRootFilesystem: true}
YAML
  printf '<project/>\n' >"$a/apps/ledger/pom.xml"
  cat >"$a/renovate.json" <<'JSON'
{"enabledManagers": ["maven"], "dependencyDashboard": true,
 "maven": {"managerFilePatterns": ["/^apps/ledger/pom\\.xml$/"]}}
JSON
  cat >"$t/register.yaml" <<'YAML'
lifts:
- app: ledger
  origin: planted/ledger
  origin_commit: 0000000
  adopter: tuppence
  served: gitops/apps/ledger.yaml
  source_dir: apps/ledger
  stack_manifest: apps/ledger/pom.xml
  renovate_manager: maven
  image: ghcr.io/planted/ledger@sha256:0000
  image_publisher: planted
  pull_request: https://example.invalid/pull/1
YAML
}

grade_fixture() {  # $1 = fixture dir -> exit code of the grader
  "$PY" "$HERE/lifted_apps.py" --hub-root "$1/hub" --estate-root "$1/estate" \
    --register "$1/register.yaml" >"$1/out.txt" 2>&1
}

selfcheck() {
  local t good=1 rc
  t="$(mktemp -d)"

  plant "$t"
  grade_fixture "$t"; rc=$?
  [ "$rc" = 0 ] || { echo "FAIL: selfcheck: a correct planted lift graded $rc (want 0)"; cat "$t/out.txt"; good=0; }

  # Each of these is a way a lift can look done and not be. The grader must fail every one, or it
  # is decoration -- the whole reason this ticket exists is that a lift which leaves the old copy
  # being read has lifted nothing.
  local case desc
  for case in unlisted orphan-version old-label no-stack no-manager wrong-manager no-dashboard hub-copy second-adopter; do
    rm -rf "$t"; t="$(mktemp -d)"; plant "$t"
    case "$case" in
      unlisted)       desc="the served manifest is not listed in the kustomization that renders it"
                      printf 'resources:\n  - namespace.yaml\n' >"$t/estate/tuppence/gitops/apps/kustomization.yaml" ;;
      orphan-version) desc="the served manifest claims a version the adopter's composed artefact does not allow"
                      sed -i.bak 's/"4\.0\.0"/"9.9.9"/' "$t/estate/tuppence/gitops/apps/ledger.yaml" ;;
      old-label)      desc="the incumbent org's label survives the move"
                      sed -i.bak 's|labels: {|labels: {"mycompany.com/policy-version": "1.0.0", |' "$t/estate/tuppence/gitops/apps/ledger.yaml" ;;
      no-stack)       desc="the workload moved and the stack manifest did not"
                      rm "$t/estate/tuppence/apps/ledger/pom.xml" ;;
      no-manager)     desc="the stack's renovate manager is not enabled"
                      printf '{"enabledManagers": ["custom.regex"], "dependencyDashboard": true, "maven": {"managerFilePatterns": ["/^apps/ledger/pom\\\\.xml$/"]}}\n' >"$t/estate/tuppence/renovate.json" ;;
      wrong-manager)  desc="the manager is enabled and reads no file the lift brought"
                      printf '{"enabledManagers": ["maven"], "dependencyDashboard": true, "maven": {"managerFilePatterns": ["/^apps/elsewhere/pom\\\\.xml$/"]}}\n' >"$t/estate/tuppence/renovate.json" ;;
      no-dashboard)   desc="the dependency dashboard is off, so the stale tree is visible nowhere"
                      printf '{"enabledManagers": ["maven"], "dependencyDashboard": false, "maven": {"managerFilePatterns": ["/^apps/ledger/pom\\\\.xml$/"]}}\n' >"$t/estate/tuppence/renovate.json" ;;
      hub-copy)       desc="the hub keeps a working copy of a lifted app"
                      mkdir -p "$t/hub/apps/ledger"; printf '<project/>\n' >"$t/hub/apps/ledger/pom.xml" ;;
      second-adopter) desc="the app is in a second adopter too -- a lift is a move, not a copy"
                      mkdir -p "$t/estate/ludlow/apps/ledger"; printf '<project/>\n' >"$t/estate/ludlow/apps/ledger/pom.xml" ;;
    esac
    grade_fixture "$t"; rc=$?
    if [ "$rc" != 1 ]; then
      echo "FAIL: selfcheck: planted case '${case}' (${desc}) graded ${rc} (want 1)"
      cat "$t/out.txt"; good=0
    fi
  done

  # A lift that has not landed at all is a could-not-look naming its pull request -- never a
  # silent pass, and never a red for work that is proposed and unmerged.
  rm -rf "$t"; t="$(mktemp -d)"; plant "$t"
  rm "$t/estate/tuppence/gitops/apps/ledger.yaml" "$t/estate/tuppence/apps/ledger/pom.xml"
  printf 'resources: []\n' >"$t/estate/tuppence/gitops/apps/kustomization.yaml"
  grade_fixture "$t"; rc=$?
  [ "$rc" = 3 ] || { echo "FAIL: selfcheck: a lift that has not landed graded $rc (want 3)"; cat "$t/out.txt"; good=0; }
  grep -q 'example.invalid/pull/1' "$t/out.txt" || {
    echo "FAIL: selfcheck: the could-not-look does not name the pull request it waits on"; good=0; }

  # The residual is a NUMBER on every run, not a sentence in a document.
  rm -rf "$t"; t="$(mktemp -d)"; plant "$t"
  grade_fixture "$t"
  grep -qE 'LIMIT +1 of 1 lifted apps are still served an image' "$t/out.txt" || {
    echo "FAIL: selfcheck: the report does not count the un-lifted image builds"; cat "$t/out.txt"; good=0; }

  rm -rf "$t"
  [ "$good" = 1 ] || return 1
  echo "  ok   selfcheck: the grader fails nine ways a lift can look done and not be, could-not-looks (naming the pull request) when one has not landed, and counts the residual"
}

case "${1:-}" in
  --selfcheck)
    selfcheck || exit 1
    echo "PASS: selfcheck: an unlisted served manifest, an orphan version claim, a surviving incumbent label, a missing stack manifest, three broken renovate shapes, a hub copy and a second adopter all fail; an unlanded lift could-not-looks and names its pull request"
    exit 0 ;;
esac

say "0. the grader can fail"
selfcheck || exit 1

say "0b. what this check cannot see"
"$PY" - "$HERE" <<'BS'
import importlib.util, sys
spec = importlib.util.spec_from_file_location("la", sys.argv[1] + "/lifted_apps.py")
la = importlib.util.module_from_spec(spec); sys.modules["la"] = la; spec.loader.exec_module(la)
for b in la.BLIND_SPOTS:
    print(f"  ??   blind spot: {b}")
BS

if [ ! -d "$ESTATE" ]; then
  echo "SKIP: there is no estate clone to read (run clone-estate.sh), so no adopter tree was looked at and whether ledger, storefront and reports are served by tuppence, driftwood and ludlow is unknown"
  exit 3
fi

say "1. every registered lift, against the adopters' own served trees"
"$PY" "$HERE/lifted_apps.py" --hub-root "$ROOT" --estate-root "$ESTATE" --register "$REG" \
  | sed 's/^/  /'
structural=${PIPESTATUS[0]}

say "2. the same discovery the adopters' own shift-left gates run"
# Not a second implementation: this EXECUTES each adopter's own
# .github/scripts/served-workloads.py, which its shift-left job feeds to ci-check.py. If the two
# ever disagree, the gate is grading a different set from the one the cluster is served.
plan_missing=0
while IFS=$'\t' read -r app unit policies served; do
  [ -n "${app:-}" ] || continue
  script="$ESTATE/$unit/.github/scripts/served-workloads.py"
  if [ ! -f "$script" ]; then
    echo "  FAIL $unit serves $app but carries no .github/scripts/served-workloads.py, so its own gate cannot discover what it serves"
    plan_missing=1; continue
  fi
  rel="${served#"$ESTATE/$unit/"}"
  if ( cd "$ESTATE/$unit" && "$PY" .github/scripts/served-workloads.py ) | grep -qx "$rel"; then
    echo "  ok   $unit's own served-workloads.py names $rel"
  else
    echo "  FAIL $unit's own served-workloads.py does not name $rel, so its shift-left gate never grades it"
    plan_missing=1
  fi
done < <("$PY" "$HERE/lifted_apps.py" --estate-root "$ESTATE" --register "$REG" --kyverno-plan)

say "3. the adopter's own composed policy set, run over the served workload (kyverno $(kyverno version 2>/dev/null | awk '/^Version/{print $2}'))"
if ! command -v kyverno >/dev/null 2>&1; then
  echo "FAIL: the kyverno CLI is not on this runner, so no served workload was put through any adopter's composed policy set. A gate that has lost its instrument goes red; it does not shrug"
  exit 1
fi
kyverno_bad=0
graded=0
while IFS=$'\t' read -r app unit policies served; do
  [ -n "${app:-}" ] || continue
  graded=$((graded + 1))
  out="$(kyverno apply "$policies"/*.yaml --resource "$served" 2>&1)"
  rc=$?
  line="$(printf '%s\n' "$out" | grep -E '^pass: ' | tail -1)"
  if [ "$rc" = 0 ]; then
    echo "  ok   $app: ${unit}'s own composed set admits ${served#"$ESTATE/"} -- ${line:-no summary line}"
  else
    echo "  FAIL $app: ${unit}'s composed set refuses ${served#"$ESTATE/"} -- ${line:-no summary line}"
    printf '%s\n' "$out" | tail -20 | sed 's/^/       /'
    kyverno_bad=1
  fi
done < <("$PY" "$HERE/lifted_apps.py" --estate-root "$ESTATE" --register "$REG" --kyverno-plan)

if [ "$kyverno_bad" = 1 ] || [ "$plan_missing" = 1 ]; then
  echo "FAIL: a served workload is refused by its own adopter's composed policy set, or that adopter's own gate cannot discover it"
  exit 1
fi
if [ "$structural" = 1 ]; then
  echo "FAIL: a lift is recorded and the adopters' trees do not carry it that way -- see the rows above"
  exit 1
fi
if [ "$structural" = 3 ]; then
  landed="$graded"
  total="$("$PY" -c "import sys,yaml;print(len(yaml.safe_load(open(sys.argv[1]))['lifts']))" "$REG")"
  echo "SKIP: ${landed} of ${total} lifts have landed in their adopter; the rest are proposed and unmerged, and the rows above name the pull request each one waits on"
  exit 3
fi
echo "PASS: ${graded} lifted applications are served by their own adopter, re-labelled onto that adopter's composed artefact, admitted by that adopter's own composed policy set, discovered by that adopter's own shift-left gate, and bumped by that adopter's own renovate manager; the hub carries no working copy of any of them"
exit 0
