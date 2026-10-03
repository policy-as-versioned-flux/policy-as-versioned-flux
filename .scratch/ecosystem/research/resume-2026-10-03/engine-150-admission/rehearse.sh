#!/usr/bin/env bash
# Ticket 150 measurement only. This never selects or changes an estate cluster.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../../.." && pwd)"
NAME=pavf-engine-150-20261003
NODE='kindest/node@sha256:3489c7674813ba5d8b1a9977baea8a6e553784dab7b84759d1014dbd78f7ebd5'
INSTALL="$HERE/kyverno-1.19.1-install.yaml"
PLATFORM="$ROOT/.estate-clone/platform"
created=0
cleanup() {
  rc=$?
  if [ "$created" = 1 ]; then
    kind delete cluster --name "$NAME" >"$HERE/cleanup.log" 2>&1 || true
  fi
  exit "$rc"
}
trap cleanup EXIT
if kind get clusters 2>/dev/null | rg -qx "$NAME"; then
  echo "Refusing to reuse the existing rehearsal cluster $NAME" >&2
  exit 2
fi
actual="$(shasum -a 256 "$INSTALL" | awk '{print $1}')"
[ "$actual" = d3322cb346d3d42dd0f41e230b0d1d7bc5619960e1c36fdac4d9151d724b88e6 ]
date -u +%FT%TZ >"$HERE/started-at.txt"
kind create cluster --name "$NAME" --image "$NODE" --kubeconfig "$HERE/kubeconfig" --wait 180s >"$HERE/create.log" 2>&1
created=1
k() { kubectl --kubeconfig "$HERE/kubeconfig" --request-timeout=60s "$@"; }
k version -o json >"$HERE/kubernetes-version.json"
k apply --server-side -f "$INSTALL" >"$HERE/install.log" 2>&1
for deploy in kyverno-admission-controller kyverno-background-controller kyverno-cleanup-controller kyverno-reports-controller; do
  k -n kyverno rollout status "deploy/$deploy" --timeout=300s >>"$HERE/rollout.log" 2>&1
done
k -n kyverno get deployments -o json >"$HERE/engine-deployments.json"
k get mutatingwebhookconfigurations -o json >"$HERE/mutating-webhooks.json"
cat >"$HERE/namespace.yaml" <<'YAML'
apiVersion: v1
kind: Namespace
metadata:
  name: engine-150
  labels:
    policy-as-versioned.dev/governed: "true"
    posture.acme.io/tier: baseline
YAML
k apply -f "$HERE/namespace.yaml" >"$HERE/namespace.log" 2>&1
pod() {
  local version="$1" name="$2"
  cat <<YAML
apiVersion: v1
kind: Pod
metadata:
  name: $name
  namespace: engine-150
  labels:
    policy-as-versioned.dev/policy-version: "$version"
spec:
  securityContext:
    runAsNonRoot: true
  containers:
    - name: app
      image: busybox:1.36
      command: ["sleep", "3600"]
YAML
}
for version in 5.0.0 6.0.1; do
  prefix="$HERE/$version"
  k apply -f "$PLATFORM/distribution/policies/v$version/priorityclasses.yaml" >"$prefix-priorityclasses.log" 2>&1
  set +e
  k apply -f "$PLATFORM/distribution/policies/v$version/cage-tier.yaml" >"$prefix-policy-apply.log" 2>&1
  policy_rc=$?
  set -e
  printf '%s\n' "$policy_rc" >"$prefix-policy-apply.rc"
  # Wait for controller status, not a fixed claim that create implies compilation.
  if [ "$policy_rc" = 0 ]; then
    for attempt in $(seq 1 30); do
      k get mutatingpolicies.policies.kyverno.io "cage-tier-${version//./-}" -o json >"$prefix-policy.json"
      if python3 - "$prefix-policy.json" <<'PY'
import json,sys
d=json.load(open(sys.argv[1])); c=d.get('status',{}).get('conditions',[])
sys.exit(0 if any(x.get('type')=='Ready' and x.get('status') in ('True','False') for x in c) else 1)
PY
      then break; fi
      sleep 2
    done
  fi
  pod "$version" "probe-${version//./-}" >"$prefix-pod.yaml"
  set +e
  k create --dry-run=server -f "$prefix-pod.yaml" -o json >"$prefix-pod-result.json" 2>"$prefix-pod-stderr.log"
  pod_rc=$?
  set -e
  printf '%s\n' "$pod_rc" >"$prefix-pod.rc"
  k -n kyverno logs deploy/kyverno-admission-controller --all-containers --tail=250 >"$prefix-admission.log" 2>&1 || true
  k delete mutatingpolicies.policies.kyverno.io "cage-tier-${version//./-}" --ignore-not-found >"$prefix-policy-delete.log" 2>&1
done
python3 - "$HERE" <<'PY'
import json, pathlib, datetime, hashlib
h=pathlib.Path(__import__('sys').argv[1]); rows=[]
for v in ('5.0.0','6.0.1'):
    p=h/f'{v}-pod-result.json'
    pod=json.loads(p.read_text()) if p.stat().st_size else None
    q=h/f'{v}-policy.json'; policy=json.loads(q.read_text()) if q.exists() else None
    rows.append({'policy_version':v,'policy_apply_exit':int((h/f'{v}-policy-apply.rc').read_text()),
                 'policy_conditions':policy.get('status',{}).get('conditions',[]) if policy else [],
                 'pod_admission_exit':int((h/f'{v}-pod.rc').read_text()),
                 'pod_admitted':pod is not None,'pod_caged':pod.get('metadata',{}).get('labels',{}).get('posture.acme.io/caged')=='true' if pod else None,
                 'pod_tier':pod.get('metadata',{}).get('labels',{}).get('posture.acme.io/tier') if pod else None,
                 'priority_class':pod.get('spec',{}).get('priorityClassName') if pod else None,
                 'container_run_as_non_root':pod.get('spec',{}).get('containers',[{}])[0].get('securityContext',{}).get('runAsNonRoot') if pod else None,
                 'pod_stderr':(h/f'{v}-pod-stderr.log').read_text()})
out={'scope':'isolated-kind-admission-rehearsal; no scheduled lane or release evidence',
     'measured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
     'engine':'kyverno','engine_version':'1.19.1','cluster':'pavf-engine-150-20261003',
     'install_sha256':hashlib.sha256((h/'kyverno-1.19.1-install.yaml').read_bytes()).hexdigest(),
     'node_image':'kindest/node@sha256:3489c7674813ba5d8b1a9977baea8a6e553784dab7b84759d1014dbd78f7ebd5',
     'admission_operation':'Pod CREATE, server dry-run, governed baseline namespace',
     'results':rows}
(h/'measurement.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
PY
date -u +%FT%TZ >"$HERE/finished-at.txt"
