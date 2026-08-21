#!/usr/bin/env bash
# Verification beat for ticket 09 (repoint-flux-sources).
#
# Hard-asserts the two things this ticket actually finished:
#   1. Every GitRepository source file declares the real GitHub org/repo URL
#      (not the retired in-cluster git-server), and the in-cluster git-server
#      deployment/seeding path is gone from each unit's scripts/up.sh.
#   2. The three live clusters (kind-driftwood/kind-ludlow/kind-tuppence) have
#      GitRepository objects pointed at those same real URLs.
#
# Reports READY status informationally, not as a hard assertion: no v1.0.0 tag
# exists yet in policy-as-versioned-{driftwood,ludlow,tuppence,nist} (a gitsign
# signed tag needs a human to complete the interactive Sigstore OIDC login --
# this agent session could not, see ticket 09's own Status/Comments), so Flux
# correctly and legibly reports FetchFailed / "couldn't find remote ref
# refs/tags/v1.0.0" rather than Ready=True. That failure message, appearing
# fast (~30s, this script's own reconcile timeout) rather than as a multi-
# minute hang, is itself part of what this ticket asked for.
#
# Run from the repo root. Requires: kubectl (contexts kind-driftwood,
# kind-ludlow, kind-tuppence reachable), grep, git (to clone the units).
#
# mo-12 update: estate/ is gone from this hub (the six units are real,
# separate GitHub repos now). The two file-content checks below used to read
# the hub's committed estate/$unit/ copy; they now read ../../clone-estate.sh's
# fresh checkout instead -- the same content ticket 09 actually fixed, just
# fetched rather than committed. This is a stronger check than before: it
# reads the real repos' current state, not a possibly-stale hub mirror.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CLONE="$ROOT/.estate-clone"
bash "$ROOT/clone-estate.sh" >/dev/null || { echo "FAIL: could not assemble $CLONE (needs network)"; exit 2; }
fail=0
ok()   { printf '  OK   %s\n' "$*"; }
bad()  { printf '  FAIL %s\n' "$*"; fail=1; }
info() { printf '  INFO %s\n' "$*"; }

echo "== source files declare the real GitHub URLs =="
for unit in driftwood ludlow tuppence; do
  f="$CLONE/$unit/gitops/flux-system/gotk-sync.yaml"
  grep -q "url: https://github.com/policy-as-versioned-$unit/$unit\$" "$f" \
    && ok "$unit gotk-sync.yaml -> https://github.com/policy-as-versioned-$unit/$unit" \
    || bad "$unit gotk-sync.yaml does not declare the real GitHub URL"

  nf="$CLONE/$unit/gitops/flux-system/gotk-sync-nist.yaml"
  grep -q "url: https://github.com/policy-as-versioned-nist/nist\$" "$nf" \
    && ok "$unit gotk-sync-nist.yaml -> https://github.com/policy-as-versioned-nist/nist" \
    || bad "$unit gotk-sync-nist.yaml does not declare the real nist GitHub URL"
done

echo
echo "== in-cluster git-server removed from each unit's up.sh =="
for unit in driftwood ludlow tuppence; do
  up="$CLONE/$unit/scripts/up.sh"
  if grep -qE 'git-server|GIT_URL_IN_CLUSTER|docker build|kind load docker-image' "$up"; then
    bad "$unit/scripts/up.sh still references the in-cluster git-server"
  else
    ok "$unit/scripts/up.sh no longer seeds/deploys an in-cluster git-server"
  fi
  grep -q 'gotk-sync.yaml' "$up" \
    && ok "$unit/scripts/up.sh applies the committed gotk-sync.yaml directly" \
    || bad "$unit/scripts/up.sh does not apply gotk-sync.yaml"
done

echo
echo "== live clusters point at the real GitHub URLs =="
for ctx_unit in "kind-driftwood driftwood" "kind-ludlow ludlow" "kind-tuppence tuppence"; do
  set -- $ctx_unit
  ctx="$1"; unit="$2"
  url="$(kubectl --context "$ctx" -n flux-system get gitrepository "$unit" -o jsonpath='{.spec.url}' 2>/dev/null)"
  [ "$url" = "https://github.com/policy-as-versioned-$unit/$unit" ] \
    && ok "$ctx: GitRepository/$unit url = $url" \
    || bad "$ctx: GitRepository/$unit url = '$url' (want the real GitHub URL)"

  nurl="$(kubectl --context "$ctx" -n flux-system get gitrepository nist -o jsonpath='{.spec.url}' 2>/dev/null)"
  [ "$nurl" = "https://github.com/policy-as-versioned-nist/nist" ] \
    && ok "$ctx: GitRepository/nist url = $nurl" \
    || bad "$ctx: GitRepository/nist url = '$nurl' (want the real nist GitHub URL)"

  ready="$(kubectl --context "$ctx" -n flux-system get gitrepository "$unit" -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}' 2>/dev/null)"
  msg="$(kubectl --context "$ctx" -n flux-system get gitrepository "$unit" -o jsonpath='{.status.conditions[?(@.type=="Ready")].message}' 2>/dev/null)"
  info "$ctx: GitRepository/$unit Ready=$ready ($msg)"
done

echo
if [ "$fail" -eq 0 ]; then
  echo "ALL HARD CHECKS PASSED (repointed at GitHub, git-server retired)."
  echo "Ready=True is NOT asserted here -- it needs a real gitsign-signed v1.0.0"
  echo "tag, which this ticket could not cut (see ticket 09 Status)."
else
  echo "SOME CHECKS FAILED"
  exit 1
fi
