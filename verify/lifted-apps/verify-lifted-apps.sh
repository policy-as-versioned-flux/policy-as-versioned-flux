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
#     `kyverno apply` over THE SET THE ADOPTER SERVES, read the way its own
#     `gitops/composed/composed-set.yaml` serves it (ticket 135): the ResourceSet's version array
#     ranged into one route per version, plus the composed-machinery route, each read from the
#     tree that file's GitRepository pins (ref.tag, checked against ref.commit), never from the
#     checkout. Only policy objects are asked for a verdict. A served PriorityClass gives none;
#     it is graded by whether the class the cage WRITES onto the pod is one the set serves,
#     because Kubernetes refuses a pod naming a PriorityClass that does not exist. Run 314 went
#     red because platform v3.3.0 put the cage's PriorityClasses in each version directory and
#     this check asked `cage-baseline-4-0-0` for a verdict it can never give.
#     What that proves is narrower than "admitted" and the ok line says so: the CLI evaluates
#     CREATE only (every composed policy declares CREATE+UPDATE; no UPDATE-scoped evaluation
#     exists anywhere in this estate), and it evaluates `namespaceObject` as null even when
#     namespace.yaml is passed, so the cage it writes is the BASELINE dial (500m/256Mi), not the
#     isolated dial (100m/64Mi, drop ALL) the governed Namespace declares. And exit 0 is not
#     admission (review F2): the `--table` output is parsed so that every policy of the CLAIMED
#     version, and the orphan guard, each has a Pass row by its own metadata.name (R2-7), and
#     every other row is a Pass or a Skip. The other versions' policies skip a pod that does not
#     claim them, by design, so the summary's skip count is printed and not required to be 0;
#   * the stack's Renovate manager must POINT AT the lifted stack manifest, not merely be named
#     in `enabledManagers`, and its bumps must sit behind dependencyDashboardApproval.
#
#   PASS (exit 0)  every registered lift is listed at the checkout on the path its own
#                  gotk-sync.yaml reconciles, is re-labelled, is admitted and caged at CREATE
#                  under the baseline dial by the set its adopter serves, is discovered by its
#                  adopter's own gate, and is bumped there
#   FAIL (exit 1)  a landed lift is wrong in any of those ways; the same app landed in two
#                  adopters; a working copy of a lifted app is in the hub; kyverno refuses a
#                  served workload, or a policy of its claimed version skips it or is silent;
#                  the cage writes a PriorityClass the served set does not carry, or none; the
#                  served set cannot be read at its pin; the register disagrees with the tree
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
# summary_admits <summary line> <kyverno exit> -> 0 when the CLI ran and nothing failed or
# errored; 1 with KV_WHY. Exit 0 from `kyverno apply` means the CLI ran, not that the workload
# was admitted. A SKIP is not judged here: the other versions' policies skip a pod that claims
# this one, by design, so whether the RIGHT policies spoke is table_admits' question.
summary_admits() {
  local line="$1" rc="$2" pass fail err skip
  KV_WHY=""
  if [ "$rc" != 0 ]; then KV_WHY="kyverno exited $rc"; return 1; fi
  if [ -z "$line" ]; then KV_WHY="kyverno printed no summary line"; return 1; fi
  pass=$(printf '%s' "$line" | sed -nE 's/^pass: ([0-9]+).*/\1/p')
  fail=$(printf '%s' "$line" | sed -nE 's/.*fail: ([0-9]+).*/\1/p')
  err=$(printf '%s' "$line" | sed -nE 's/.*error: ([0-9]+).*/\1/p')
  skip=$(printf '%s' "$line" | sed -nE 's/.*skip: ([0-9]+).*/\1/p')
  [ -n "$pass" ] && [ -n "$fail" ] && [ -n "$err" ] && [ -n "$skip" ] || { KV_WHY="summary line not parseable: $line"; return 1; }
  if [ "$fail" -gt 0 ] || [ "$err" -gt 0 ]; then KV_WHY="fail: $fail, error: $err"; return 1; fi
  return 0
}

# table_admits <kyverno --table output> <policy name>... -> 0 when every NAMED policy has a row
# whose RESULT is Pass and no row of any policy says anything but Pass or Skip; 1 with KV_WHY
# naming the policy. The summary's `pass:` counts RULE verdicts, so it cannot say whether each
# POLICY spoke (R2-7). The names are the claimed version's policies and the orphan guard: a
# policy of the claimed version that skips the pod, or gives no row, has not caged it (a
# version the set does not carry is skipped, not admitted -- review F2).
table_admits() {
  local table="$1" name result rows other; shift
  rows="$(printf '%s\n' "$table" | sed 's/\x1b\[[0-9;]*m//g' | grep -E '^│ *[0-9]+ *│')"
  [ -n "$rows" ] || { KV_WHY="kyverno --table printed no policy rows"; return 1; }
  for name in "$@"; do
    result="$(printf '%s\n' "$rows" | awk -F'│' -v n="$name" '{gsub(/ /,"",$3); gsub(/ /,"",$6); if ($3==n) print $6}' | sort -u | tr '\n' ',' | sed 's/,$//')"
    case "$result" in
      Pass) ;;
      "")   KV_WHY="policy $name produced no verdict at all (no row in the kyverno table)"; return 1 ;;
      *)    KV_WHY="policy $name: $result"; return 1 ;;
    esac
  done
  other="$(printf '%s\n' "$rows" | awk -F'│' '{gsub(/ /,"",$3); gsub(/ /,"",$6); if ($6!="Pass" && $6!="Skip") print $3": "$6}' | sort -u | tr '\n' ',' | sed 's/,$//')"
  [ -z "$other" ] || { KV_WHY="policy $other"; return 1; }
  return 0
}

# class_served <kyverno summary output> <served class names, comma-separated> -> 0 when the
# pod the cage mutated names a priorityClassName and the served set carries that class; 1 with
# KV_WHY. KV_CLASS is the class written. Kubernetes' Priority admission refuses a pod whose
# priorityClassName names no PriorityClass, so a class the set does not serve is a refusal at
# CREATE, and no class at all is a pod the cage never touched.
class_served() {
  local out="$1" classes=",$2,"
  KV_CLASS="$(printf '%s\n' "$out" | sed -nE 's/^ *priorityClassName: *"?([^" ]+)"? *$/\1/p' | tail -1)"
  if [ -z "$KV_CLASS" ]; then
    KV_WHY="no policy in the served set wrote a priorityClassName onto the pod, so nothing caged it"; return 1; fi
  case "$classes" in
    *",$KV_CLASS,"*) return 0 ;;
  esac
  KV_WHY="the cage writes priorityClassName $KV_CLASS, which the served set does not carry, so Kubernetes refuses the pod at CREATE (it serves: ${2:--})"
  return 1
}

# kyverno_run <policy dir> <served manifest> <must-pass names, comma> <served classes, comma>
# -> summary_admits over a real apply of every policy the served set carries, then
# table_admits over a second apply with --table (the CLI prints one or the other), then
# class_served over the mutated pod. KV_LINE is the summary line, KV_FILES the policy count,
# KV_OUT the whole summary output.
kyverno_run() {
  local policies="$1" served="$2" must="$3" classes="$4" rc table
  KV_LINE=""; KV_OUT=""; KV_FILES=0; KV_CLASS=""
  KV_FILES=$(ls "$policies"/*.yaml 2>/dev/null | wc -l | tr -d ' ')
  [ "$KV_FILES" -gt 0 ] || { KV_WHY="the served set carries no policy at all"; return 1; }
  KV_OUT="$(kyverno apply "$policies"/*.yaml --resource "$served" 2>&1)"; rc=$?
  KV_LINE="$(printf '%s\n' "$KV_OUT" | grep -E '^pass: ' | tail -1 | sed 's/ *$//')"
  if ! summary_admits "$KV_LINE" "$rc"; then
    local failed
    failed="$(printf '%s\n' "$KV_OUT" | sed -nE 's/.*policy ([^ ]+) -> resource [^ ]+ failed.*/\1/p' | sort -u | tr '\n' ',' | sed 's/,$//')"
    [ -z "$failed" ] || KV_WHY="$KV_WHY; failed: $failed"
    return 1
  fi
  table="$(kyverno apply "$policies"/*.yaml --resource "$served" --table 2>&1)"
  # shellcheck disable=SC2086
  table_admits "$table" $(printf '%s' "$must" | tr ',' ' ') || return 1
  class_served "$KV_OUT" "$classes"
}

# cage_grade <estate root> <register> -> one line per landed lift: what the set its adopter
# serves does to the served workload. 0 when every one is admitted and caged, 1 otherwise.
cage_grade() {
  local estate="$1" reg="$2" work bad=0 app unit pin policies served must classes err prc
  work="$(mktemp -d)"
  # The planner writes to a file so its exit code is seen. Read through process substitution, a
  # planner that died printed no rows, graded nothing and passed (review round, PR #119).
  "$PY" "$HERE/lifted_apps.py" --estate-root "$estate" --register "$reg" --kyverno-plan "$work/policies" >"$work/plan.tsv" 2>"$work/plan.err"; prc=$?
  if [ "$prc" != 0 ]; then
    echo "  FAIL the planner (lifted_apps.py --kyverno-plan) exited $prc, so no served set was graded:"
    tail -5 "$work/plan.err" | sed 's/^/       /'
    rm -rf "$work"
    return 1
  fi
  while IFS=$'\t' read -r app unit pin policies served must classes err; do
    [ -n "${app:-}" ] || continue
    CAGE_GRADED=$((CAGE_GRADED + 1))
    if [ "$err" != "-" ]; then
      echo "  FAIL $app: ${unit}'s served set cannot grade ${served#"$estate/"} -- $err"
      bad=1; continue
    fi
    if kyverno_run "$policies" "$served" "$must" "$classes"; then
      echo "  ok   $app: the set ${unit} serves (gitops/composed/composed-set.yaml at $pin, ${KV_FILES} policies across every route its ResourceSet renders) admits ${served#"$estate/"} at CREATE only, baseline dial, no namespaceObject -- ${KV_LINE}; each policy of its claimed version and the orphan guard has a Pass row of its own (${must//,/ }), every other row is Pass or Skip, and the cage writes priorityClassName ${KV_CLASS}, which the set serves"
    else
      echo "  FAIL $app: the set ${unit} serves (${pin}) does not admit and cage ${served#"$estate/"} -- ${KV_WHY} (${KV_LINE:-no summary line})"
      printf '%s\n' "$KV_OUT" | tail -20 | sed 's/^/       /'
      bad=1
    fi
  done <"$work/plan.tsv"
  rm -rf "$work"
  return "$bad"
}

# graded_floor <graded> <landed> -> 0 when every landed lift got a graded row; 1 with KV_WHY.
# A PASS that graded fewer apps than have landed has stopped looking (review round, PR #119).
graded_floor() {
  [ "$1" -ge "$2" ] 2>/dev/null && return 0
  KV_WHY="${1:-0} of ${2:-?} landed lifts were put through the served set, so the rest were never looked at"
  return 1
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
  # The cage, in the shape platform v3.3.0 serves it (ticket 111): a MutatingPolicy that writes
  # the rung's priorityClassName, and the PriorityClass itself in the SAME version directory.
  # The class is a served object, not a policy: run 314 asked it for a verdict (ticket 135).
  cat >"$a/composed/policies/v4.0.0/cage-tier.yaml" <<'YAML'
apiVersion: policies.kyverno.io/v1alpha1
kind: MutatingPolicy
metadata: {name: cage-tier-4-0-0}
spec:
  matchConstraints:
    resourceRules:
    - apiGroups: ['']
      apiVersions: [v1]
      operations: [CREATE, UPDATE]
      resources: [pods]
  matchConditions:
  - name: only-this-policy-version
    expression: object.metadata.?labels['policy-as-versioned.dev/policy-version'].orValue('') == '4.0.0'
  mutations:
  - patchType: ApplyConfiguration
    applyConfiguration:
      expression: 'Object{spec: Object.spec{priorityClassName: "cage-baseline-4-0-0", priority: -10}}'
YAML
  cat >"$a/composed/policies/v4.0.0/cage-baseline.yaml" <<'YAML'
apiVersion: scheduling.k8s.io/v1
kind: PriorityClass
metadata: {name: cage-baseline-4-0-0}
value: -10
preemptionPolicy: Never
globalDefault: false
YAML
  # A second served version, whose policies skip a pod that claims 4.0.0.
  mkdir -p "$a/composed/policies/v5.0.0"
  sed 's/4\.0\.0/5.0.0/g; s/4-0-0/5-0-0/g' "$a/composed/policies/v4.0.0/require-nonroot.yaml" >"$a/composed/policies/v5.0.0/require-nonroot.yaml"
  printf 'resources:\n  - orphan-guard.yaml\n' >"$a/composed/kustomization.yaml"
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
    expression: '[''4.0.0'', ''5.0.0'']'
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
  # The composed set, pinned to its own tag at the checkout (ticket 130's shape: gotk-sync.yaml
  # still pins v1.0.0 while composed-set.yaml pins v2.0.0).
  G -C "$a" tag v2.0.0
  composed_set "$a" "4.0.0 5.0.0"
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

# composed_set <adopter> <versions> -> write gitops/composed/composed-set.yaml pinning v2.0.0
# at the commit it resolves to, with the ResourceSet shape all three adopters serve.
composed_set() {
  local a="$1" versions="$2" sha v
  sha="$(G -C "$a" rev-parse 'v2.0.0^{commit}')"
  mkdir -p "$a/gitops/composed"
  {
    cat <<YAML
apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata: {name: tuppence-composed, namespace: flux-system}
spec:
  url: https://example.invalid/planted/tuppence
  ref: {tag: v2.0.0, commit: $sha}
---
apiVersion: fluxcd.controlplane.io/v1
kind: ResourceSet
metadata: {name: composed-set, namespace: flux-system}
spec:
  inputs:
    - versions:
YAML
    for v in $versions; do printf '        - { version: "%s" }\n' "$v"; done
    [ -n "$versions" ] || printf '        []\n'
    cat <<'YAML'
  resourcesTemplate: |
    << range $v := (index (inputs) "versions") >>
    ---
    apiVersion: kustomize.toolkit.fluxcd.io/v1
    kind: Kustomization
    metadata: {name: composed-v<< $v.version | slugify >>, namespace: flux-system}
    spec:
      sourceRef: {kind: GitRepository, name: tuppence-composed}
      path: ./composed/policies/v<< $v.version >>
    << end >>
    ---
    apiVersion: kustomize.toolkit.fluxcd.io/v1
    kind: Kustomization
    metadata: {name: composed-machinery, namespace: flux-system}
    spec:
      sourceRef: {kind: GitRepository, name: tuppence-composed}
      path: ./composed
YAML
  } >"$a/gitops/composed/composed-set.yaml"
}

# recut_composed <fixture dir> [versions] -> commit the adopter's working tree, move v2.0.0 to
# it, and re-pin composed-set.yaml there: a planted change to the SERVED set.
recut_composed() {
  local a="$1/estate/tuppence"
  G -C "$a" add -A
  G -C "$a" commit -qm "planted: recut the composed tag"
  G -C "$a" tag -f v2.0.0 HEAD >/dev/null
  composed_set "$a" "${2:-4.0.0 5.0.0}"
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
  grep -qE 'pins \(v1\.0\.0\): ledger->tuppence; 0 of 1 pinned trees could not be read' "$t/out.txt" || {
    echo "FAIL: selfcheck: the headline LIMIT does not carry the count of pinned trees that could not be read"; cat "$t/out.txt"; good=0; }
  repin_to_head "$t"
  grade_fixture "$t"; rc=$?
  [ "$rc" = 0 ] && grep -qE 'LIMIT +0 of 1 lifts are listed at main and not in the tree the GitRepository pins \(v1\.0\.0\)' "$t/out.txt" || {
    echo "FAIL: selfcheck: a lift the pinned tree DOES list is still counted as absent (rc $rc)"; cat "$t/out.txt"; good=0; }
  # A pin naming a tag this clone does not carry is a COUNT on the same line, never a zero
  # derived from nothing read (tidy 2026-09-08, R2-1).
  sed -i.bak -E "s/^    tag: .*/    tag: v9.9.9/" "$t/estate/tuppence/gitops/flux-system/gotk-sync.yaml"
  grade_fixture "$t"; rc=$?
  [ "$rc" = 0 ] && grep -qE 'LIMIT +0 of 1 lifts are listed at main and not in the tree the GitRepository pins \(v9\.9\.9\); 1 of 1 pinned trees could not be read' "$t/out.txt" || {
    echo "FAIL: selfcheck: a pinned tag this clone cannot read graded $rc or was folded into '0 of 1 not in the pinned tree' with no count of what could not be read"; cat "$t/out.txt"; good=0; }
  sed -i.bak -E "s/^    tag: .*/    tag: v1.0.0/" "$t/estate/tuppence/gitops/flux-system/gotk-sync.yaml"
  # A pin whose tag and commit disagree is refused by Flux and must be refused here.
  sed -i.bak -E "s/^    commit: .*/    commit: deadbeefdeadbeefdeadbeefdeadbeefdeadbeef/" "$t/estate/tuppence/gitops/flux-system/gotk-sync.yaml"
  grade_fixture "$t"; rc=$?
  [ "$rc" = 1 ] && grep -q 'but the tag resolves to' "$t/out.txt" || {
    echo "FAIL: selfcheck: a tag+commit pair that disagree graded $rc (want 1, naming the mismatch)"; cat "$t/out.txt"; good=0; }

  # The kyverno verdict is parsed, not trusted (review F2).
  summary_admits "pass: 8, fail: 0, warn: 0, error: 0, skip: 0" 0 || {
    echo "FAIL: selfcheck: a full pass was refused: $KV_WHY"; good=0; }
  summary_admits "pass: 8, fail: 1, warn: 0, error: 0, skip: 0" 0 && {
    echo "FAIL: selfcheck: 'fail: 1' at exit 0 was taken as admission"; good=0; }
  summary_admits "pass: 8, fail: 0, warn: 0, error: 0, skip: 0" 1 && {
    echo "FAIL: selfcheck: a non-zero kyverno exit was taken as admission"; good=0; }
  # ...and per POLICY by name (R2-7): a table where a named policy is silent or skips, or any
  # row is neither Pass nor Skip, is not admission however the rule count adds up. A PriorityClass
  # is never a name here (ticket 135): the plan names policies only.
  local tbl
  tbl="$(printf '│ 1  │ a-4-0-0 │      │ ns/Pod/x │ Pass   │        │\n│ 2  │ guard   │      │ ns/Pod/x │ Pass   │        │\n│ 3  │ a-5-0-0 │      │ ns/Pod/x │ Skip   │        │\n')"
  table_admits "$tbl" a-4-0-0 guard || { echo "FAIL: selfcheck: a table with every named policy passing and another version skipping was refused: $KV_WHY"; good=0; }
  table_admits "$tbl" a-4-0-0 b-4-0-0 guard && { echo "FAIL: selfcheck: a policy with no row in the table was taken as admitted"; good=0; }
  table_admits "$tbl" a-4-0-0 a-5-0-0 guard && { echo "FAIL: selfcheck: a Skip row of a named policy was taken as admission"; good=0; }
  tbl="$(printf '│ 1  │ a-4-0-0 │      │ ns/Pod/x │ Pass   │        │\n│ 2  │ guard   │      │ ns/Pod/x │ Pass   │        │\n│ 3  │ a-5-0-0 │      │ ns/Pod/x │ Fail   │        │\n')"
  table_admits "$tbl" a-4-0-0 guard && { echo "FAIL: selfcheck: a Fail row of an unnamed policy was taken as admission"; good=0; }

  # ...and against the real engine over the set the planted adopter SERVES (ticket 135): its
  # composed-set.yaml at v2.0.0, both versions, the machinery route, a PriorityClass in the
  # version directory. This is run 314's shape, and it is admitted and caged.
  rm -rf "$t"; t="$(mktemp -d)"; plant "$t"
  CAGE_GRADED=0
  cage_grade "$t/estate" "$t/register.yaml" >"$t/cage.txt" 2>&1 || {
    echo "FAIL: selfcheck: the set the planted adopter serves (a PriorityClass in its version directory, run 314's shape) did not admit and cage the planted 4.0.0 pod"; cat "$t/cage.txt"; good=0; }
  grep -q 'priorityClassName cage-baseline-4-0-0, which the set serves' "$t/cage.txt" || {
    echo "FAIL: selfcheck: the ok line does not name the class the cage wrote"; cat "$t/cage.txt"; good=0; }
  grep -q '4 policies across every route' "$t/cage.txt" || {
    echo "FAIL: selfcheck: expected the 4 policies the planted set serves (cage-tier and require-nonroot at 4.0.0, require-nonroot at 5.0.0, the orphan guard) and not its PriorityClass"; cat "$t/cage.txt"; good=0; }
  # The 9.9.9 pod through the real engine: the claimed version's policies skip it and the guard
  # refuses it. (The plan names it first: 9.9.9 is not in the array.)
  local w="$t/w" pr
  "$PY" "$HERE/lifted_apps.py" --estate-root "$t/estate" --register "$t/register.yaml" --kyverno-plan "$w" >"$t/plan.tsv"
  pr="$(cut -f4 "$t/plan.tsv")"
  sed 's/"4\.0\.0"/"9.9.9"/' "$t/estate/tuppence/gitops/apps/ledger.yaml" >"$t/ledger-999.yaml"
  if kyverno_run "$pr" "$t/ledger-999.yaml" "$(cut -f6 "$t/plan.tsv")" "$(cut -f7 "$t/plan.tsv")"; then
    echo "FAIL: selfcheck: the real kyverno over a 9.9.9 pod was taken as admission ($KV_LINE)"; good=0
  fi
  # Each of these is a way the SERVED set can leave the lifted app unadmitted or uncaged.
  for case in class-not-served uncaged other-version-refuses pin-not-checkout version-not-served no-guard no-composed-set composed-unparseable composed-pin-mismatch; do
    rm -rf "$t"; t="$(mktemp -d)"; plant "$t"; a="$t/estate/tuppence"
    case "$case" in
      class-not-served) desc="the cage writes a PriorityClass the served set does not carry"
                        want="cage-baseline-4-0-0, which the served set does not carry"
                        rm "$a/composed/policies/v4.0.0/cage-baseline.yaml"; recut_composed "$t" ;;
      uncaged)          desc="no served policy writes a priorityClassName"
                        want="nothing caged it"
                        rm "$a/composed/policies/v4.0.0/cage-tier.yaml"; recut_composed "$t" ;;
      other-version-refuses) desc="a policy of ANOTHER served version refuses the pod"
                        want="failed: require-nonroot-5-0-0"
                        sed -i.bak '/matchConditions:/,/orValue/d; s/validationActions: \[Audit\]/validationActions: [Deny]/; s/expression: object.spec.*/expression: "false"/' "$a/composed/policies/v5.0.0/require-nonroot.yaml"
                        rm -f "$a/composed/policies/v5.0.0/require-nonroot.yaml.bak"; recut_composed "$t" ;;
      pin-not-checkout) desc="the set at the PIN refuses the pod while the checkout would admit it"
                        want="require-nonroot-4-0-0"
                        cp "$a/composed/policies/v4.0.0/require-nonroot.yaml" "$t/keep.yaml"
                        sed -i.bak 's/runAsNonRoot.orValue(false) == true/runAsNonRoot.orValue(false) == false/' "$a/composed/policies/v4.0.0/require-nonroot.yaml"
                        rm -f "$a/composed/policies/v4.0.0/require-nonroot.yaml.bak"; recut_composed "$t"
                        cp "$t/keep.yaml" "$a/composed/policies/v4.0.0/require-nonroot.yaml" ;;
      version-not-served) desc="composed-set.yaml does not serve the version the pod claims"
                        want="claims 4.0.0"
                        composed_set "$a" "5.0.0" ;;
      no-guard)         desc="the machinery route does not serve the orphan guard"
                        want="carries no orphan-guard.yaml"
                        printf 'resources: []\n' >"$a/composed/kustomization.yaml"; recut_composed "$t" ;;
      no-composed-set)  desc="the adopter serves no composed set at all"
                        want="has no gitops/composed/composed-set.yaml"
                        rm "$a/gitops/composed/composed-set.yaml" ;;
      composed-unparseable) desc="composed-set.yaml does not parse as YAML (review round, PR #119)"
                        want="does not parse as YAML"
                        printf 'apiVersion: [unclosed\n' >"$a/gitops/composed/composed-set.yaml" ;;
      composed-pin-mismatch) desc="composed-set.yaml's tag and commit disagree"
                        want="but the tag resolves to"
                        sed -i.bak -E 's/commit: [0-9a-f]+/commit: deadbeefdeadbeefdeadbeefdeadbeefdeadbeef/' "$a/gitops/composed/composed-set.yaml" ;;
    esac
    CAGE_GRADED=0
    if cage_grade "$t/estate" "$t/register.yaml" >"$t/cage.txt" 2>&1; then
      echo "FAIL: selfcheck: planted cage case '${case}' (${desc}) was admitted"; cat "$t/cage.txt"; good=0
    elif ! grep -qF -- "$want" "$t/cage.txt"; then
      echo "FAIL: selfcheck: planted cage case '${case}' failed without naming it (want '${want}')"; cat "$t/cage.txt"; good=0
    fi
  done

  # A planner that dies grades nothing. Review round, PR #119: the shell read it through
  # process substitution, never saw its exit code, and printed `PASS: 0 lifted applications`.
  rm -rf "$t"; t="$(mktemp -d)"; plant "$t"
  printf '#!/usr/bin/env bash\nfor a in "$@"; do [ "$a" = --kyverno-plan ] && { echo "Traceback: planted planner crash" >&2; exit 1; }; done\nexec %q "$@"\n' "$PY" >"$t/py-crash"
  chmod +x "$t/py-crash"
  CAGE_GRADED=0
  if PY="$t/py-crash" cage_grade "$t/estate" "$t/register.yaml" >"$t/cage.txt" 2>&1; then
    echo "FAIL: selfcheck: a planner that exits 1 was taken as a clean grade"; cat "$t/cage.txt"; good=0
  elif ! grep -qF "kyverno-plan) exited 1" "$t/cage.txt"; then
    echo "FAIL: selfcheck: a planner that exits 1 failed without naming it"; cat "$t/cage.txt"; good=0
  fi
  # ...and fewer graded rows than landed lifts is never a PASS, whatever the planner said.
  graded_floor 1 1 || { echo "FAIL: selfcheck: one graded lift of one landed was refused: $KV_WHY"; good=0; }
  graded_floor 0 3 && { echo "FAIL: selfcheck: 0 graded lifts of 3 landed was taken as a PASS"; good=0; }

  rm -rf "$t"
  [ "$good" = 1 ] || return 1
  echo "  ok   selfcheck: the grader fails fifteen ways a lift can look done and not be (the served path read from the adopter's own gotk-sync.yaml among them), could-not-looks (naming the pull request) when one has not landed, counts both residuals and the pinned trees it could not read, accepts a glob pattern and a ./ entry, parses the kyverno verdict per policy by name (a skipped 9.9.9 pod at exit 0 is not admitted), and grades the set the adopter's composed-set.yaml serves at its pin (a PriorityClass in a version directory gives no verdict and is admitted; nine ways that set can leave the app unadmitted or uncaged all fail by name; a planner that dies, or grades fewer apps than have landed, fails)"
}

case "${1:-}" in
  --selfcheck)
    selfcheck || exit 1
    echo "PASS: selfcheck: an unlisted served manifest, a wrong Flux path, a missing gotk-sync.yaml, a tag+commit mismatch, an orphan version claim, a surviving incumbent label, a missing stack manifest, four broken renovate shapes, four hub copies and a second adopter all fail; an unlanded lift could-not-looks and names its pull request; a pinned tree without the lift, and a pinned tag this clone cannot read, are counted limits on one line; a skipped kyverno verdict at exit 0, and a policy with no row of its own in the kyverno table, are not admission; the set an adopter serves is read from its composed-set.yaml at its pin, a PriorityClass in a version directory is not asked for a verdict (run 314), and a class the set does not serve, no cage at all, another version refusing, a refusal only at the pin, an unserved version, no orphan guard, no composed set, a composed set that does not parse and a tag+commit mismatch all fail; a planner that exits non-zero, and fewer graded apps than landed lifts, are never a PASS"
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
pinned_unread="$(printf '%s\n' "$report" | sed -nE 's/^LIMIT +[0-9]+ of [0-9]+ lifts are listed at main and not in the tree the GitRepository pins .*; ([0-9]+) of [0-9]+ pinned trees could not be read.*/\1/p')"

say "2. the same discovery the adopters' own shift-left gates run"
# Not a second implementation: this EXECUTES each adopter's own
# .github/scripts/served-workloads.py, which its shift-left job feeds to ci-check.py. If the two
# ever disagree, the gate is grading a different set from the one the cluster is served.
plan_missing=0
PLAN_WORK="$(mktemp -d)"
"$PY" "$HERE/lifted_apps.py" --estate-root "$ESTATE" --register "$REG" --kyverno-plan "$PLAN_WORK/policies" >"$PLAN_WORK/plan.tsv" 2>"$PLAN_WORK/plan.err"
prc=$?
if [ "$prc" != 0 ]; then
  echo "  FAIL the planner (lifted_apps.py --kyverno-plan) exited $prc, so no adopter's discovery was checked:"
  tail -5 "$PLAN_WORK/plan.err" | sed 's/^/       /'
  plan_missing=1
fi
while IFS=$'\t' read -r app unit _pin _policies served _rest; do
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
done <"$PLAN_WORK/plan.tsv"
rm -rf "$PLAN_WORK"

say "3. the set each adopter serves (gitops/composed/composed-set.yaml at its pin, every route its ResourceSet renders), run over the served workload (kyverno $(kyverno version 2>/dev/null | awk '/^Version/{print $2}'); CREATE only, baseline dial, no namespaceObject)"
if ! command -v kyverno >/dev/null 2>&1; then
  echo "FAIL: the kyverno CLI is not on this runner, so no served workload was put through any adopter's composed policy set. A gate that has lost its instrument goes red; it does not shrug"
  exit 1
fi
kyverno_bad=0
CAGE_GRADED=0
cage_grade "$ESTATE" "$REG" || kyverno_bad=1
graded=$CAGE_GRADED

if [ "$kyverno_bad" = 1 ] || [ "$plan_missing" = 1 ]; then
  echo "FAIL: a served workload is not admitted and caged at CREATE by the set its own adopter serves, or that adopter's own gate cannot discover it"
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
if ! graded_floor "$graded" "$total"; then
  echo "FAIL: every registered lift has landed and ${KV_WHY}"
  exit 1
fi
echo "PASS: ${graded} lifted applications are listed by their adopter's gitops/apps/kustomization.yaml at the checked-out tree, on the path that adopter's own gotk-sync.yaml reconciles; admitted and caged at CREATE under the baseline dial by the set that adopter's gitops/composed/composed-set.yaml serves at its pin, every version and the machinery route (kyverno apply, no namespaceObject), onto a PriorityClass that set carries; discovered by that adopter's own served-workloads.py; bumped by that adopter's own renovate manager behind dashboard approval; ${pinned_absent:-?} of ${total} are not in the tree the GitRepository pins (${pinned_tags:-unread}) and ${pinned_unread:-?} of ${total} pinned trees could not be read; the hub carries no working copy of any of them"
exit 0
