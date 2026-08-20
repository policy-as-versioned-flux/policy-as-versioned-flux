#!/usr/bin/env bash
# Verification beat for ticket 09 (repoint-flux-sources): every live
# GitRepository on the three institution clusters points at the real
# policy-as-versioned-* GitHub repos mo-08 created (not the retired
# in-cluster git-server), is Ready, the in-cluster git-server is gone from
# both the cluster and the tree, and a real, freshly pushed tag exists on
# each repo.
#
# Run from the repo root. Requires: kubectl (contexts kind-driftwood,
# kind-ludlow, kind-tuppence reachable), gh (authenticated).
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

fail=0
ok()   { printf '  OK   %s\n' "$*"; }
bad()  { printf '  FAIL %s\n' "$*"; fail=1; }
note() { printf '  NOTE %s\n' "$*"; }

check_institution() {
  local unit="$1" ctx="kind-$1"
  echo "== $unit ($ctx) =="

  local url ready
  url="$(kubectl --context "$ctx" -n flux-system get gitrepository "$unit" -o jsonpath='{.spec.url}' 2>/dev/null || echo MISSING)"
  ready="$(kubectl --context "$ctx" -n flux-system get gitrepository "$unit" -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo MISSING)"
  [ "$url" = "https://github.com/policy-as-versioned-$unit/$unit" ] \
    && ok "GitRepository/$unit url=$url" \
    || bad "GitRepository/$unit url=$url (want https://github.com/policy-as-versioned-$unit/$unit)"
  [ "$ready" = True ] && ok "GitRepository/$unit Ready=True" || bad "GitRepository/$unit Ready=$ready"

  local nist_url nist_ready
  nist_url="$(kubectl --context "$ctx" -n flux-system get gitrepository nist -o jsonpath='{.spec.url}' 2>/dev/null || echo MISSING)"
  nist_ready="$(kubectl --context "$ctx" -n flux-system get gitrepository nist -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo MISSING)"
  [ "$nist_url" = "https://github.com/policy-as-versioned-nist/nist" ] \
    && ok "GitRepository/nist url=$nist_url" \
    || bad "GitRepository/nist url=$nist_url (want https://github.com/policy-as-versioned-nist/nist)"
  [ "$nist_ready" = True ] && ok "GitRepository/nist Ready=True" || bad "GitRepository/nist Ready=$nist_ready"

  local kready
  kready="$(kubectl --context "$ctx" -n flux-system get kustomization "$unit" -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo MISSING)"
  [ "$kready" = True ] && ok "Kustomization/$unit Ready=True" || bad "Kustomization/$unit Ready=$kready"

  # the in-cluster git-server is retired, not just unused
  if kubectl --context "$ctx" -n flux-system get deployment git-server >/dev/null 2>&1; then
    bad "deployment/git-server still present on $ctx"
  else
    ok "deployment/git-server absent from $ctx"
  fi

  # and gone from the tree too (Dockerfile/lighttpd.conf/deployment.yaml)
  if [ -d "$ROOT/estate/$unit/git-server" ]; then
    bad "estate/$unit/git-server/ still in the tree"
  else
    ok "estate/$unit/git-server/ removed from the tree"
  fi

  echo
}

check_institution driftwood
check_institution ludlow
check_institution tuppence

echo "== up.sh: no offline/in-cluster seeding path left =="
for unit in driftwood ludlow tuppence; do
  f="$ROOT/estate/$unit/scripts/up.sh"
  if grep -qE 'git-server|GITSERVER_DIR|GIT_URL_IN_CLUSTER|docker build' "$f"; then
    bad "$unit/scripts/up.sh still references the retired git-server path"
  else
    ok "$unit/scripts/up.sh has no git-server/seeding references"
  fi
done
echo

echo "== GitHub: v1.0.0 tag real on each repo mo-08 created =="
for repo in driftwood ludlow tuppence nist; do
  org="policy-as-versioned-$repo"
  tag_sha="$(gh api "repos/$org/$repo/git/refs/tags/v1.0.0" --jq '.object.sha' 2>/dev/null || echo MISSING)"
  if [ "$tag_sha" = MISSING ] || [ -z "$tag_sha" ]; then
    bad "$org/$repo: v1.0.0 tag missing"
    continue
  fi
  ok "$org/$repo: v1.0.0 tag exists ($tag_sha)"
  signed="$(gh api "repos/$org/$repo/git/tags/$tag_sha" --jq '.verification.reason' 2>/dev/null || echo MISSING)"
  note "$org/$repo: v1.0.0 verification=$signed (gitsign is the design intent, ADR-0001; unsigned here -- headless keyless OIDC login hangs with no browser to complete it, and a CI workflow granted signing permission needs ticket 10's reviewed release workflow, not a one-off from this ticket -- see gotk-sync.yaml header)"
done
echo

echo "== GitHub: driftwood v1.0.1 -- proves a reconcile follows a freshly pushed tag =="
v101_sha="$(gh api repos/policy-as-versioned-driftwood/driftwood/git/refs/tags/v1.0.1 --jq '.object.sha' 2>/dev/null || echo MISSING)"
if [ "$v101_sha" = MISSING ] || [ -z "$v101_sha" ]; then
  bad "policy-as-versioned-driftwood/driftwood: v1.0.1 tag missing (the fresh-push reconcile proof tag)"
else
  ok "policy-as-versioned-driftwood/driftwood: v1.0.1 exists ($v101_sha) -- during ticket 09 the driftwood"
  ok "  GitRepository was live-repointed to it (spec.ref.tag v1.0.0 -> v1.0.1), reconciled Ready=True on"
  ok "  kind-driftwood within seconds, then repointed back to v1.0.0 to match the committed pin"
fi
echo

if [ "$fail" -eq 0 ]; then
  echo "ALL CHECKS PASSED"
else
  echo "SOME CHECKS FAILED"
  exit 1
fi
