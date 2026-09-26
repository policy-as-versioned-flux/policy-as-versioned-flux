#!/usr/bin/env bash
# The engine layer on a named demo cluster, from the declaration of the adopter that owns it
# (eco-system ticket 147, hub ADR-0033 point 2). talk/up.sh runs this where it used to run the
# platform's engine/up.sh. In order:
#   1. the platform's substrate Namespaces, platform engine/namespaces.yaml (kyverno, flux-system
#      and kube-system declared `infra`), which the posture layer reads, as engine/up.sh applied;
#   2. Kyverno from the OWNER's own gitops/engine/kyverno.yaml: the install.yaml at the URL the
#      file states, refused unless it hashes to the file's sha256, applied once and server-side
#      (two Kyverno CRDs are larger than a client-side apply can annotate). The admission
#      controller must then run the declared version;
#   3. the platform's flux-operator, platform engine/flux-operator/helmrelease.yaml, as
#      engine/up.sh installed it. It serves the ResourceSet CRD.
# The platform's engine/kyverno/helmrelease.yaml stays the platform's reference install only.
#
# The cluster is the one the owner's own scripts create, read by the same module that grades it
# (verify/adopter-engines/adopter_engines.py owned-cluster), so `talk/engine-up.sh driftwood`
# installs on kind-driftwood. Another adopter that uses that cluster (tuppence's workload
# flagship) runs this one engine, and verify/adopter-engines asserts that it declares the same.
#
#   talk/engine-up.sh <owner>        CTX=<context> and CLONE=<estate dir> override the defaults
#
# Idempotent. It refuses a cluster whose Kyverno came from the platform's Flux HelmRelease (one
# brought up before ticket 147): installing over it would give one engine two owners, and removing
# that release uninstalls Kyverno's CRDs and every policy with them. The refusal says how to
# recover. It never creates or deletes a cluster.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLONE="${CLONE:-$ROOT/.estate-clone}"
OWNER="${1:?usage: talk/engine-up.sh <the adopter that owns the cluster>}"
READER="$ROOT/verify/adopter-engines/adopter_engines.py"
PY="$ROOT/.venv/bin/python"; [ -x "$PY" ] || PY=python3
say() { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
die() { echo "engine-up: $*" >&2; exit 1; }
sha256() { if command -v sha256sum >/dev/null; then sha256sum "$1"; else shasum -a 256 "$1"; fi | cut -d' ' -f1; }

for c in kubectl flux curl; do command -v "$c" >/dev/null || die "MISSING cli: $c"; done
"$PY" -c 'import yaml' 2>/dev/null || die "$PY cannot import yaml, so the declaration cannot be read (make the hub .venv)"
DECLARATION="$CLONE/$OWNER/gitops/engine/kyverno.yaml"
declared="$("$PY" "$READER" read "$DECLARATION")" || die "$OWNER's $DECLARATION is not a readable declaration"
read -r VERSION URL SHA <<<"$declared"
cluster="$("$PY" "$READER" owned-cluster "$CLONE/$OWNER")" || die "cannot tell which cluster $OWNER owns"
CTX="${CTX:-kind-$cluster}"

kubectl --context "$CTX" version >/dev/null 2>&1 || die "cluster not reachable ($CTX); run $OWNER's scripts/up.sh first"
flux check --context "$CTX" >/dev/null 2>&1 || die "Flux not installed on $CTX; run $OWNER's scripts/up.sh first"
if kubectl --context "$CTX" -n kyverno get helmreleases.helm.toolkit.fluxcd.io kyverno >/dev/null 2>&1; then
  die "$CTX runs Kyverno from the platform's HelmRelease kyverno/kyverno, installed before ticket 147. Installing $OWNER's declared engine over it would give one engine two owners. Recreate the cluster ($OWNER's scripts/reset.sh, then talk/up.sh). Deleting that HelmRelease by hand also works, and it uninstalls Kyverno's CRDs and every policy with them."
fi

say "substrate Namespaces (platform engine/namespaces.yaml)"
kubectl --context "$CTX" apply -f "$CLONE/platform/engine/namespaces.yaml"

say "Kyverno $VERSION from $OWNER's own gitops/engine/kyverno.yaml"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
curl -fsSL -o "$tmp/install.yaml" "$URL" || die "could not download $URL"
got="$(sha256 "$tmp/install.yaml")"
[ "$got" = "$SHA" ] || die "$URL hashes to $got, and $OWNER's gitops/engine/kyverno.yaml states $SHA"
echo "   $URL: sha256 $got, as declared"
kubectl --context "$CTX" apply --server-side --force-conflicts -f "$tmp/install.yaml"
# Both waits together stay inside the 600s talk/up.sh gives a step.
kubectl --context "$CTX" -n kyverno rollout status deploy/kyverno-admission-controller --timeout=240s \
  || die "the admission controller did not become ready within 240s; re-run to converge"
image="$(kubectl --context "$CTX" -n kyverno get deploy kyverno-admission-controller \
  -o jsonpath='{.spec.template.spec.containers[?(@.name=="kyverno")].image}')"
case "$image" in
  *":v$VERSION") echo "   the admission controller runs $image" ;;
  *) die "the admission controller runs ${image:-no image}, and $OWNER declares kyverno $VERSION" ;;
esac

say "flux-operator (platform engine/flux-operator/helmrelease.yaml: the ResourceSet CRD)"
kubectl --context "$CTX" apply -f "$CLONE/platform/engine/flux-operator/helmrelease.yaml"
flux --context "$CTX" --timeout 4m reconcile helmrelease -n flux-system flux-operator \
  || echo "  (reconcile of flux-operator not finished within 4m; safe to re-run)"

say "done: $CTX runs kyverno $VERSION, the engine $OWNER declares"
