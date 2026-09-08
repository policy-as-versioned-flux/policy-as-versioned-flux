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
# artefact and the operation that reaches it -- and READS both from the adopter's own tree rather
# than naming them in prose (review 2026-09-08 F1: the first cut said "Flux reconciles ./apps"
# here while driftwood's gotk-sync.yaml said `./apps` at a remote whose root holds gitops/):
#
#   * the operation is the adopter's `gitops/flux-system/gotk-sync.yaml`: its Kustomization's
#     `spec.path` must resolve to the directory the served manifest is in, or the row FAILS by
#     name; its GitRepository's `ref.tag` is the tree a cluster is actually served, and whether
#     the lift is listed THERE (`git show <tag>:<path>/kustomization.yaml`) is a COUNTED LIMIT
#     printed on every run, never folded into a PASS;
#   * the served artefact is `gitops/apps/kustomization.yaml`'s `resources[]` at the checkout. A
#     manifest in that directory the kustomization does not name is served to nobody;
#   * the version it claims is measured against the ADOPTER'S OWN composed artefact
#     (`composed/orphan-guard.yaml`'s allowed array), never a constant held in this repository;
#   * the last word on admission belongs to the estate's own engine: step 3 runs the real
#     `kyverno apply` over the adopter's own `composed/policies/v<claimed>/` PLUS its
#     `composed/orphan-guard.yaml` against the served manifest. What that proves is narrower than
#     "admitted" and the ok line says so: the CLI evaluates CREATE only (every composed policy
#     declares CREATE+UPDATE; no UPDATE-scoped evaluation exists anywhere in this estate), and
#     it evaluates `namespaceObject` as null even when namespace.yaml is passed, so the cage it
#     writes is the BASELINE dial (500m/256Mi), not the isolated dial (100m/64Mi, drop ALL) the
#     governed Namespace declares. And exit 0 is not admission: a pod claiming a version the set
#     does not carry is SKIPPED by every policy and kyverno exits 0 with `skip: 6` (review F2),
#     so the summary line is parsed and `skip: 0` with `pass >= <policy files>` is required;
#   * the stack's Renovate manager must POINT AT the lifted stack manifest, not merely be named
#     in `enabledManagers`, and its bumps must sit behind dependencyDashboardApproval.
#
#   PASS (exit 0)  every registered lift is listed at the checkout on the path its own
#                  gotk-sync.yaml reconciles, is re-labelled, is admitted at CREATE under the
#                  baseline dial, is discovered by its adopter's own gate, and is bumped there
#   FAIL (exit 1)  a landed lift is wrong in any of those ways; the same app landed in two
#                  adopters; a working copy of a lifted app is in the hub; kyverno refuses or
#                  skips a served workload; the register disagrees with the tree
#   SKIP (exit 3)  a registered lift has not landed in its adopter yet -- the line names the pull
#                  request each waits on -- or there is no estate clone to read at all
#
# The kyverno CLI going missing is deliberately NOT a could-not-look, the same call
# verify-refusal-by-another-name.sh records: a runner that has lost its instrument goes red
# rather than shrugging. The selfcheck needs it too, for the same reason.
#
# WHAT IT CANNOT LOOK AT is printed on every run from lifted_apps.BLIND_SPOTS, and the limits
# that matter are NUMBERS the report prints rather than sentences that go stale: how many of the
# lifted apps are still served an image built and published by the incumbent org, and how many
# are listed at the checkout and absent from the tree the GitRepository pins.
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

# The fixture's own git runs no hook: the owner's global core.hooksPath runs a rate-limited
# network scan on every commit, fixture commits included (estate-clone hazards, note 5).
NOHOOKS="$(mktemp -d)"
G() {
  git -c core.hooksPath="$NOHOOKS" -c user.name=selfcheck -c user.email=selfcheck@example.invalid \
      -c commit.gpgsign=false -c tag.gpgsign=false -c init.defaultBranch=main "$@"
}

# ------------------------------------------------------------------ the kyverno verdict, parsed
# summary_admits <summary line> <kyverno exit> <policy files> -> 0 admitted, 1 not; KV_WHY says why.
# Exit 0 from `kyverno apply` means the CLI ran, not that the workload was admitted: a policy
# whose matchConditions exclude the pod is a SKIP, and a pod claiming a version the set does not
# carry is skipped by every policy in it.
summary_admits() {
  local line="$1" rc="$2" nfiles="$3" pass fail err skip
  KV_WHY=""
  if [ "$rc" != 0 ]; then KV_WHY="kyverno exited $rc"; return 1; fi
  if [ -z "$line" ]; then KV_WHY="kyverno printed no summary line"; return 1; fi
  pass=$(printf '%s' "$line" | sed -nE 's/^pass: ([0-9]+).*/\1/p')
  fail=$(printf '%s' "$line" | sed -nE 's/.*fail: ([0-9]+).*/\1/p')
  err=$(printf '%s' "$line" | sed -nE 's/.*error: ([0-9]+).*/\1/p')
  skip=$(printf '%s' "$line" | sed -nE 's/.*skip: ([0-9]+).*/\1/p')
  [ -n "$pass" ] && [ -n "$fail" ] && [ -n "$err" ] && [ -n "$skip" ] || { KV_WHY="summary line not parseable: $line"; return 1; }
  if [ "$fail" -gt 0 ] || [ "$err" -gt 0 ]; then KV_WHY="fail: $fail, error: $err"; return 1; fi
  if [ "$skip" -gt 0 ]; then
    KV_WHY="skip: $skip -- $skip of the policies did not match the workload at all (a version the set does not carry is skipped, not admitted)"; return 1; fi
  if [ "$pass" -lt "$nfiles" ]; then
    KV_WHY="pass: $pass of $nfiles policy files -- a policy in the set produced no verdict"; return 1; fi
  return 0
}

# kyverno_run <policy dir> <orphan guard> <served manifest> -> summary_admits over a real apply;
# KV_LINE is the summary line, KV_FILES the policy-file count, KV_OUT the whole output.
kyverno_run() {
  local policies="$1" guard="$2" served="$3" rc
  KV_LINE=""; KV_OUT=""; KV_FILES=0
  [ -f "$guard" ] || { KV_WHY="$guard is missing: the set was applied without its orphan guard, which is the one policy that refuses a version the array does not declare"; return 1; }
  KV_FILES=$(( $(ls "$policies"/*.yaml 2>/dev/null | wc -l | tr -d ' ') + 1 ))
  KV_OUT="$(kyverno apply "$policies"/*.yaml "$guard" --resource "$served" 2>&1)"; rc=$?
  KV_LINE="$(printf '%s\n' "$KV_OUT" | grep -E '^pass: ' | tail -1)"
  summary_admits "$KV_LINE" "$rc" "$KV_FILES"
}

# ----------------------------------------------------------------------------------- the fixture
# A throwaway estate carrying one correct lift, written by the same shell that then breaks it.
# Nothing here reads the real estate, and the fixture register points at the fixture only. The
# adopter is a real git repository: v1.0.0 is tagged BEFORE the lift lands, so the pinned tree
# does not list it -- the shape all three real adopters have today.
plant() {
  local t="$1" a="$t/estate/tuppence" sha
  mkdir -p "$a/composed/policies/v4.0.0" "$a/gitops/apps" "$a/gitops/flux-system" "$a/apps/ledger" "$t/hub"
  # Real policies, in the estate's own dialect, because the selfcheck runs the real kyverno over them.
  cat >"$a/composed/policies/v4.0.0/require-nonroot.yaml" <<'YAML'
apiVersion: policies.kyverno.io/v1alpha1
kind: ValidatingPolicy
metadata: {name: require-nonroot-4-0-0}
spec:
  validationActions: [Audit]
  matchConstraints:
    resourceRules:
    - apiGroups: ['']
      apiVersions: [v1]
      operations: [CREATE, UPDATE]
      resources: [pods]
  matchConditions:
  - name: only-this-policy-version
    expression: object.metadata.?labels['policy-as-versioned.dev/policy-version'].orValue('') == '4.0.0'
  validations:
  - expression: object.spec.?securityContext.?runAsNonRoot.orValue(false) == true
    message: pods on policy-version 4.0.0 must set spec.securityContext.runAsNonRoot=true
YAML
  cat >"$a/composed/orphan-guard.yaml" <<'YAML'
apiVersion: policies.kyverno.io/v1alpha1
kind: ValidatingPolicy
metadata: {name: policy-version-orphan-guard}
spec:
  validationActions: [Deny]
  matchConstraints:
    resourceRules:
    - apiGroups: ['']
      apiVersions: [v1]
      operations: [CREATE, UPDATE]
      resources: [pods]
  matchConditions:
  - name: has-policy-version-label
    expression: object.metadata.?labels['policy-as-versioned.dev/policy-version'].orValue('') != ''
  variables:
  - name: allowed
    expression: '[''4.0.0'']'
  - name: claimed
    expression: object.metadata.labels['policy-as-versioned.dev/policy-version']
  validations:
  - expression: variables.allowed.exists(v, v == variables.claimed)
    message: 'policy-version not in the platform-declared version array (orphan)'
YAML
  # The tree the GitRepository pins: before the lift.
  printf 'apiVersion: v1\nkind: Namespace\nmetadata: {name: tuppence}\n' >"$a/gitops/apps/namespace.yaml"
  cat >"$a/gitops/apps/kustomization.yaml" <<'YAML'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - namespace.yaml
YAML
  G -C "$a" init -q
  G -C "$a" add -A
  G -C "$a" commit -qm "v1.0.0: before the lift"
  G -C "$a" tag v1.0.0
  sha="$(G -C "$a" rev-parse 'v1.0.0^{commit}')"
  cat >"$a/gitops/flux-system/gotk-sync.yaml" <<YAML
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata: {name: tuppence, namespace: flux-system}
spec:
  interval: 1m
  url: https://example.invalid/planted/tuppence
  ref:
    tag: v1.0.0
    commit: $sha
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata: {name: tuppence, namespace: flux-system}
spec:
  interval: 5m
  sourceRef: {kind: GitRepository, name: tuppence}
  path: ./gitops/apps
  prune: true
YAML
  # The checkout: the lift landed.
  cat >"$a/gitops/apps/kustomization.yaml" <<'YAML'
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - namespace.yaml
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
  printf '<project>\n  <groupId>com.mycompany</groupId>\n  <artifactId>ledger</artifactId>\n</project>\n' >"$a/apps/ledger/pom.xml"
  cat >"$a/renovate.json" <<'JSON'
{"enabledManagers": ["maven"], "dependencyDashboard": true,
 "packageRules": [{"matchManagers": ["maven"], "dependencyDashboardApproval": true}],
 "maven": {"managerFilePatterns": ["/^apps/ledger/pom\\.xml$/"]}}
JSON
  G -C "$a" add -A
  G -C "$a" commit -qm "ticket 33: the lift"
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
  identity: '<groupId>com\.mycompany</groupId>\s*<artifactId>ledger</artifactId>'
YAML
}

# Move the fixture's pin to the checkout: the tree v1.0.0 names now carries the lift.
repin_to_head() {
  local a="$1/estate/tuppence" sha
  G -C "$a" tag -f v1.0.0 HEAD >/dev/null
  sha="$(G -C "$a" rev-parse 'v1.0.0^{commit}')"
  sed -i.bak -E "s/^    commit: .*/    commit: $sha/" "$a/gitops/flux-system/gotk-sync.yaml"
}

grade_fixture() {  # $1 = fixture dir -> exit code of the grader
  "$PY" "$HERE/lifted_apps.py" --hub-root "$1/hub" --estate-root "$1/estate" \
    --register "$1/register.yaml" >"$1/out.txt" 2>&1
}

selfcheck() {
  local t good=1 rc
  command -v kyverno >/dev/null 2>&1 || { echo "FAIL: selfcheck: the kyverno CLI is not on this runner, so the verdict parser cannot be checked against a real apply"; return 1; }
  t="$(mktemp -d)"

  plant "$t"
  grade_fixture "$t"; rc=$?
  [ "$rc" = 0 ] || { echo "FAIL: selfcheck: a correct planted lift graded $rc (want 0)"; cat "$t/out.txt"; good=0; }

  # Each of these is a way a lift can look done and not be. The grader must fail every one, or it
  # is decoration -- the whole reason this ticket exists is that a lift which leaves the old copy
  # being read has lifted nothing.
  local case desc want
  for case in unlisted orphan-version old-label no-stack no-manager wrong-manager no-dashboard no-approval hub-copy hub-copy-anywhere hub-copy-identity hub-copy-image second-adopter wrong-path no-sync; do
    rm -rf "$t"; t="$(mktemp -d)"; plant "$t"; want=""
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
                      printf '{"enabledManagers": ["custom.regex"], "dependencyDashboard": true, "packageRules": [{"matchManagers": ["maven"], "dependencyDashboardApproval": true}], "maven": {"managerFilePatterns": ["/^apps/ledger/pom\\\\.xml$/"]}}\n' >"$t/estate/tuppence/renovate.json" ;;
      wrong-manager)  desc="the manager is enabled and reads no file the lift brought"
                      printf '{"enabledManagers": ["maven"], "dependencyDashboard": true, "packageRules": [{"matchManagers": ["maven"], "dependencyDashboardApproval": true}], "maven": {"managerFilePatterns": ["/^apps/elsewhere/pom\\\\.xml$/"]}}\n' >"$t/estate/tuppence/renovate.json" ;;
      no-dashboard)   desc="the dependency dashboard is off, so the stale tree is visible nowhere"
                      printf '{"enabledManagers": ["maven"], "dependencyDashboard": false, "packageRules": [{"matchManagers": ["maven"], "dependencyDashboardApproval": true}], "maven": {"managerFilePatterns": ["/^apps/ledger/pom\\\\.xml$/"]}}\n' >"$t/estate/tuppence/renovate.json" ;;
      no-approval)    desc="the manager's bumps are not behind dependencyDashboardApproval (decision 7 was prose until review F6)"
                      want="dependencyDashboardApproval"
                      printf '{"enabledManagers": ["maven"], "dependencyDashboard": true, "maven": {"managerFilePatterns": ["/^apps/ledger/pom\\\\.xml$/"]}}\n' >"$t/estate/tuppence/renovate.json" ;;
      hub-copy)       desc="the hub keeps a working copy of a lifted app at the lifted path"
                      mkdir -p "$t/hub/apps/ledger"; printf '<project/>\n' >"$t/hub/apps/ledger/pom.xml" ;;
      hub-copy-anywhere) desc="the hub keeps a working copy under another directory (spikes/ledger/pom.xml -- review F4)"
                      want="spikes/ledger/pom.xml"
                      mkdir -p "$t/hub/spikes/ledger"; printf '<project/>\n' >"$t/hub/spikes/ledger/pom.xml" ;;
      hub-copy-identity) desc="the hub keeps a stack manifest carrying the app's identity under a directory not named for it"
                      want="carries ledger's identity"
                      mkdir -p "$t/hub/twin/lab"; printf '<project>\n<groupId>com.mycompany</groupId>\n<artifactId>ledger</artifactId>\n</project>\n' >"$t/hub/twin/lab/pom.xml" ;;
      hub-copy-image) desc="the hub keeps a manifest pinning the app's served image"
                      want="pins ledger's served image"
                      mkdir -p "$t/hub/twin/manifests"; cp "$t/estate/tuppence/gitops/apps/ledger.yaml" "$t/hub/twin/manifests/anything.yaml" ;;
      second-adopter) desc="the app is in a second adopter too -- a lift is a move, not a copy"
                      mkdir -p "$t/estate/ludlow/apps/ledger"; printf '<project/>\n' >"$t/estate/ludlow/apps/ledger/pom.xml" ;;
      wrong-path)     desc="the adopter's own gotk-sync.yaml reconciles a path that is not the directory the check reads (driftwood, review F1)"
                      want='reconciles `path: ./apps`, not gitops/apps'
                      sed -i.bak 's|path: ./gitops/apps|path: ./apps|' "$t/estate/tuppence/gitops/flux-system/gotk-sync.yaml" ;;
      no-sync)        desc="the adopter has no gotk-sync.yaml, so nothing names the path Flux reconciles"
                      want="has no gitops/flux-system/gotk-sync.yaml"
                      rm "$t/estate/tuppence/gitops/flux-system/gotk-sync.yaml" ;;
    esac
    grade_fixture "$t"; rc=$?
    if [ "$rc" != 1 ]; then
      echo "FAIL: selfcheck: planted case '${case}' (${desc}) graded ${rc} (want 1)"
      cat "$t/out.txt"; good=0
    elif [ -n "$want" ] && ! grep -qF -- "$want" "$t/out.txt"; then
      echo "FAIL: selfcheck: planted case '${case}' failed without naming it (want '${want}' in the report)"
      cat "$t/out.txt"; good=0
    fi
  done

  # Shapes that are NOT wrong and used to crash or false-fail the grader (review F5).
  rm -rf "$t"; t="$(mktemp -d)"; plant "$t"
  printf '{"enabledManagers": ["maven"], "dependencyDashboard": true, "packageRules": [{"matchManagers": ["maven"], "dependencyDashboardApproval": true}], "maven": {"managerFilePatterns": ["**/pom.xml"]}}\n' >"$t/estate/tuppence/renovate.json"
  printf 'resources:\n  - ./namespace.yaml\n  - ./ledger.yaml\n' >"$t/estate/tuppence/gitops/apps/kustomization.yaml"
  grade_fixture "$t"; rc=$?
  [ "$rc" = 0 ] || { echo "FAIL: selfcheck: a glob-form managerFilePatterns and a ./-prefixed resource entry graded $rc (want 0)"; cat "$t/out.txt"; good=0; }

  # A lift that has not landed at all is a could-not-look naming its pull request -- never a
  # silent pass, and never a red for work that is proposed and unmerged.
  rm -rf "$t"; t="$(mktemp -d)"; plant "$t"
  rm "$t/estate/tuppence/gitops/apps/ledger.yaml" "$t/estate/tuppence/apps/ledger/pom.xml"
  printf 'resources: []\n' >"$t/estate/tuppence/gitops/apps/kustomization.yaml"
  grade_fixture "$t"; rc=$?
  [ "$rc" = 3 ] || { echo "FAIL: selfcheck: a lift that has not landed graded $rc (want 3)"; cat "$t/out.txt"; good=0; }
  grep -q 'example.invalid/pull/1' "$t/out.txt" || {
    echo "FAIL: selfcheck: the could-not-look does not name the pull request it waits on"; good=0; }

  # The residuals are NUMBERS on every run, not sentences in a document: the image build that
  # did not move, and the pinned tree that does not list the lift yet.
  rm -rf "$t"; t="$(mktemp -d)"; plant "$t"
  grade_fixture "$t"
  grep -qE 'LIMIT +1 of 1 lifted apps are still served an image' "$t/out.txt" || {
    echo "FAIL: selfcheck: the report does not count the un-lifted image builds"; cat "$t/out.txt"; good=0; }
  grep -qE 'LIMIT +1 of 1 lifts are listed at main and not in the tree the GitRepository pins \(v1\.0\.0\): ledger->tuppence' "$t/out.txt" || {
    echo "FAIL: selfcheck: a lift listed at the checkout and absent from the pinned tree is not counted by name"; cat "$t/out.txt"; good=0; }
  repin_to_head "$t"
  grade_fixture "$t"; rc=$?
  [ "$rc" = 0 ] && grep -qE 'LIMIT +0 of 1 lifts are listed at main and not in the tree the GitRepository pins \(v1\.0\.0\)' "$t/out.txt" || {
    echo "FAIL: selfcheck: a lift the pinned tree DOES list is still counted as absent (rc $rc)"; cat "$t/out.txt"; good=0; }
  # A pin whose tag and commit disagree is refused by Flux and must be refused here.
  sed -i.bak -E "s/^    commit: .*/    commit: deadbeefdeadbeefdeadbeefdeadbeefdeadbeef/" "$t/estate/tuppence/gitops/flux-system/gotk-sync.yaml"
  grade_fixture "$t"; rc=$?
  [ "$rc" = 1 ] && grep -q 'but the tag resolves to' "$t/out.txt" || {
    echo "FAIL: selfcheck: a tag+commit pair that disagree graded $rc (want 1, naming the mismatch)"; cat "$t/out.txt"; good=0; }

  # The kyverno verdict is parsed, not trusted (review F2): the exact shape the review measured.
  summary_admits "pass: 1, fail: 0, warn: 0, error: 0, skip: 6" 0 7 && {
    echo "FAIL: selfcheck: 'pass: 1 ... skip: 6' at exit 0 was taken as admission"; good=0; }
  summary_admits "pass: 7, fail: 0, warn: 0, error: 0, skip: 0" 0 8 && {
    echo "FAIL: selfcheck: 7 passes over 8 policy files was taken as admission"; good=0; }
  summary_admits "pass: 8, fail: 0, warn: 0, error: 0, skip: 0" 0 8 || {
    echo "FAIL: selfcheck: a full pass was refused: $KV_WHY"; good=0; }
  summary_admits "pass: 8, fail: 0, warn: 0, error: 0, skip: 0" 1 8 && {
    echo "FAIL: selfcheck: a non-zero kyverno exit was taken as admission"; good=0; }
  # ...and against the real engine over the planted set: the 4.0.0 pod is admitted, the 9.9.9
  # pod is skipped by the version-scoped policy and refused by the guard.
  rm -rf "$t"; t="$(mktemp -d)"; plant "$t"
  local a="$t/estate/tuppence"
  kyverno_run "$a/composed/policies/v4.0.0" "$a/composed/orphan-guard.yaml" "$a/gitops/apps/ledger.yaml" || {
    echo "FAIL: selfcheck: the real kyverno refused the planted 4.0.0 pod: $KV_WHY"; printf '%s\n' "$KV_OUT" | tail -5; good=0; }
  [ "$KV_FILES" = 2 ] || { echo "FAIL: selfcheck: counted $KV_FILES policy files (want 2: one composed policy plus the guard)"; good=0; }
  sed 's/"4\.0\.0"/"9.9.9"/' "$a/gitops/apps/ledger.yaml" >"$t/ledger-999.yaml"
  if kyverno_run "$a/composed/policies/v4.0.0" "$a/composed/orphan-guard.yaml" "$t/ledger-999.yaml"; then
    echo "FAIL: selfcheck: the real kyverno over a 9.9.9 pod was taken as admission ($KV_LINE)"; good=0
  fi
  printf '%s' "$KV_LINE" | grep -q 'skip: 1' || { echo "FAIL: selfcheck: expected the version-scoped policy to skip the 9.9.9 pod, got: $KV_LINE"; good=0; }
  if kyverno_run "$a/composed/policies/v4.0.0" "$a/composed/no-such-guard.yaml" "$a/gitops/apps/ledger.yaml"; then
    echo "FAIL: selfcheck: an apply without the orphan guard was taken as admission"; good=0
  fi

  rm -rf "$t"
  [ "$good" = 1 ] || return 1
  echo "  ok   selfcheck: the grader fails fifteen ways a lift can look done and not be (the served path read from the adopter's own gotk-sync.yaml among them), could-not-looks (naming the pull request) when one has not landed, counts both residuals, accepts a glob pattern and a ./ entry, and parses the kyverno verdict (a skipped 9.9.9 pod at exit 0 is not admitted)"
}

case "${1:-}" in
  --selfcheck)
    selfcheck || exit 1
    echo "PASS: selfcheck: an unlisted served manifest, a wrong Flux path, a missing gotk-sync.yaml, a tag+commit mismatch, an orphan version claim, a surviving incumbent label, a missing stack manifest, four broken renovate shapes, four hub copies and a second adopter all fail; an unlanded lift could-not-looks and names its pull request; a pinned tree without the lift is a counted limit; a skipped kyverno verdict at exit 0 is not admission"
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

say "1. every registered lift, against the adopters' own served trees and their own gotk-sync.yaml"
report="$("$PY" "$HERE/lifted_apps.py" --hub-root "$ROOT" --estate-root "$ESTATE" --register "$REG" 2>&1)"
structural=$?
printf '%s\n' "$report" | sed 's/^/  /'
pinned_absent="$(printf '%s\n' "$report" | sed -nE 's/^LIMIT +([0-9]+) of [0-9]+ lifts are listed at main and not in the tree the GitRepository pins \(([^)]*)\).*/\1/p')"
pinned_tags="$(printf '%s\n' "$report" | sed -nE 's/^LIMIT +[0-9]+ of [0-9]+ lifts are listed at main and not in the tree the GitRepository pins \(([^)]*)\).*/\1/p')"

say "2. the same discovery the adopters' own shift-left gates run"
# Not a second implementation: this EXECUTES each adopter's own
# .github/scripts/served-workloads.py, which its shift-left job feeds to ci-check.py. If the two
# ever disagree, the gate is grading a different set from the one the cluster is served.
plan_missing=0
while IFS=$'\t' read -r app unit policies guard served; do
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

say "3. the adopter's own composed policy set plus orphan guard, run over the served workload (kyverno $(kyverno version 2>/dev/null | awk '/^Version/{print $2}'); CREATE only, baseline dial, no namespaceObject)"
if ! command -v kyverno >/dev/null 2>&1; then
  echo "FAIL: the kyverno CLI is not on this runner, so no served workload was put through any adopter's composed policy set. A gate that has lost its instrument goes red; it does not shrug"
  exit 1
fi
kyverno_bad=0
graded=0
while IFS=$'\t' read -r app unit policies guard served; do
  [ -n "${app:-}" ] || continue
  graded=$((graded + 1))
  if kyverno_run "$policies" "$guard" "$served"; then
    echo "  ok   $app: ${unit}'s own composed set plus orphan guard admits ${served#"$ESTATE/"} at CREATE only, baseline dial, no namespaceObject -- ${KV_LINE} over ${KV_FILES} policy files, every one matched"
  else
    echo "  FAIL $app: ${unit}'s composed set does not admit ${served#"$ESTATE/"} -- ${KV_WHY} (${KV_LINE:-no summary line})"
    printf '%s\n' "$KV_OUT" | tail -20 | sed 's/^/       /'
    kyverno_bad=1
  fi
done < <("$PY" "$HERE/lifted_apps.py" --estate-root "$ESTATE" --register "$REG" --kyverno-plan)

if [ "$kyverno_bad" = 1 ] || [ "$plan_missing" = 1 ]; then
  echo "FAIL: a served workload is not admitted by its own adopter's composed policy set at CREATE, or that adopter's own gate cannot discover it"
  exit 1
fi
if [ "$structural" = 1 ]; then
  echo "FAIL: a lift is recorded and the adopters' trees do not carry it that way -- see the rows above"
  exit 1
fi
total="$("$PY" -c "import sys,yaml;print(len(yaml.safe_load(open(sys.argv[1]))['lifts']))" "$REG")"
if [ "$structural" = 3 ]; then
  echo "SKIP: ${graded} of ${total} lifts have landed in their adopter; the rest are proposed and unmerged, and the rows above name the pull request each one waits on"
  exit 3
fi
echo "PASS: ${graded} lifted applications are listed by their adopter's gitops/apps/kustomization.yaml at the checked-out tree, on the path that adopter's own gotk-sync.yaml reconciles; admitted at CREATE under the baseline dial by that adopter's own composed set plus orphan guard (kyverno apply, no namespaceObject); discovered by that adopter's own served-workloads.py; bumped by that adopter's own renovate manager behind dashboard approval; ${pinned_absent:-?} of ${total} are not in the tree the GitRepository pins (${pinned_tags:-unread}); the hub carries no working copy of any of them"
exit 0
