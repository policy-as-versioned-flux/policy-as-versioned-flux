#!/usr/bin/env bash
# Hosted substrate for citable TRUTH clocks and opt-in nondefault previews.
# No provider controller, ProviderConfig, cloud credential or AWS resource.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if [ "${GITHUB_ACTIONS:-}" != true ] || [ "${RUNNER_ENVIRONMENT:-}" != github-hosted ]; then
  echo 'FAIL: cloud admission substrate is restricted to a GitHub-hosted runner; local clusters stay off' >&2
  exit 1
fi
if ! [[ "${GITHUB_RUN_ID:-}" =~ ^[0-9]+$ && "${GITHUB_RUN_ATTEMPT:-}" =~ ^[0-9]+$ ]]; then
  echo 'FAIL: cloud admission substrate needs the real numeric run and attempt' >&2
  exit 1
fi
unset GH_TOKEN GITHUB_TOKEN
PY="${CLOUD_PYTHON:-python3}"
PLATFORM="$ROOT/.estate-clone/platform"
TUPPENCE="$ROOT/.estate-clone/tuppence"
NAME="cloud-tuppence-${GITHUB_RUN_ID}-${GITHUB_RUN_ATTEMPT}"
CTX="kind-$NAME"
printf 'CLOUD_PLANE_CONTEXT=%s\n' "$CTX" >> "${GITHUB_ENV:?}"
export CLOUD_PLANE_CONTEXT="$CTX"

# This must finish before downloading tools or creating any cluster. Missing
# signed cloud delivery stays the existing declared wait in the native check.
"$PY" "$ROOT/verify/cloud-plane/cloud_plane.py" --preflight

work="${RUNNER_TEMP:?}/cloud-admission"
mkdir -p "$work"
curl -fsSL -o "$work/kind" https://github.com/kubernetes-sigs/kind/releases/download/v0.32.0/kind-linux-amd64
echo '50030de23cf40a18505f20426f6a8506bedf13c6e509244bd1fa9463721b0f54  '"$work/kind" | sha256sum -c -
chmod +x "$work/kind"
sudo mv "$work/kind" /usr/local/bin/kind
curl -fsSL -o "$work/flux-operator.yaml" https://github.com/controlplaneio-fluxcd/flux-operator/releases/download/v0.58.1/install.yaml
echo 'd674546f8cd6c9a09c55a279b119c880ae6d79c726ff7c57ec4d92b26827a04d  '"$work/flux-operator.yaml" | sha256sum -c -
install_url=''
install_sha256=''
while IFS='=' read -r key value; do
  case "$key" in
    install_url) install_url="$value" ;;
    install_sha256) install_sha256="$value" ;;
  esac
done < <("$PY" "$TUPPENCE/.github/scripts/engine_declaration.py" outputs "$TUPPENCE/gitops/engine/kyverno.yaml")
[ -n "$install_url" ] && [ -n "$install_sha256" ]
curl -fsSL -o "$work/kyverno.yaml" "$install_url"
printf '%s  %s\n' "$install_sha256" "$work/kyverno.yaml" | sha256sum -c -

kind create cluster --name "$NAME" --wait 120s
kubectl --context "$CTX" apply --server-side --force-conflicts -f "$work/kyverno.yaml"
kubectl --context "$CTX" apply --server-side --force-conflicts -f "$work/flux-operator.yaml"
flux --context "$CTX" install --components=source-controller,kustomize-controller
kubectl --context "$CTX" -n kyverno rollout status deploy/kyverno-admission-controller --timeout=180s
kubectl --context "$CTX" -n flux-system rollout status deploy/flux-operator --timeout=180s

# Bootstrap the existing source verifier from the implementation tag Tuppence
# already accepts, independently of its new cloud and compiler package pins.
platform_tag="$($PY - "$TUPPENCE/gitops/platform/platform-pin.yaml" <<'PY'
from pathlib import Path
import sys,yaml
docs=yaml.safe_load_all(Path(sys.argv[1]).read_text())
print(next(doc['spec']['ref']['tag'] for doc in docs if doc and doc.get('kind')=='GitRepository'))
PY
)"
git -C "$PLATFORM" archive "$platform_tag" identity/gitsign-verifier | tar -xf - -C "$work"
kubectl --context "$CTX" apply -k "$work/identity/gitsign-verifier"
kubectl --context "$CTX" -n flux-system rollout status deploy/gitsign-verifier --timeout=180s
kubectl --context "$CTX" apply -f "$TUPPENCE/gitops/flux-system/"
kubectl --context "$CTX" apply -f "$TUPPENCE/gitops/platform/platform-pin.yaml"
kubectl --context "$CTX" apply -k "$TUPPENCE/gitops/composed/"
kubectl --context "$CTX" apply -k "$TUPPENCE/gitops/cloud/"
kubectl --context "$CTX" -n flux-system wait gitrepository/tuppence-composed --for=condition=Ready --timeout=180s
for route in crossplane-crds cloud-policies cloud-claims; do
  kubectl --context "$CTX" -n flux-system wait "kustomization/$route" --for=condition=Ready --timeout=300s
done
kubectl --context "$CTX" -n flux-system get gitrepositories,kustomizations,resourcesets -o wide
echo 'PASS: hosted cloud substrate is ready; the ordinary native check must still observe admission'
