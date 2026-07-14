# Shift-left dev workflow (the "usable" -able)

How a developer reproduces the cluster's admission verdict for a sample workload,
on their own laptop, against the *exact* pinned policy versions the cluster
runs — no cluster access required for most of this, no bespoke tooling (the
2022 bash/Docker `policy-checker` stays deleted; every step below is a native
CLI you'd install anyway: `git`, `kyverno`, `kustomize`, `flux`, `gitsign`).

CI runs the *same* commands (not a reimplementation of them), so laptop and
CI cannot drift:
[`policy/.github/workflows/release.yml`](https://github.com/policy-as-versioned-flux/policy/blob/main/.github/workflows/release.yml)
and [`fleet/pr-gate-check.sh`](https://github.com/policy-as-versioned-flux/fleet/blob/main/pr-gate-check.sh)
call `kyverno test`, `gitsign verify-tag`, and `flux build --dry-run` exactly
as shown here — this doc's steps are a subset+narration of what those two
already do, not a parallel invention.

## 0. Find what's actually pinned

The versions a cluster runs live in one place:
[`fleet/clusters/cluster1/policy-versions.yaml`](https://github.com/policy-as-versioned-flux/fleet/blob/main/clusters/cluster1/policy-versions.yaml),
`spec.inputs[0].versions[]`. As of this writing, `cluster1` pins:

| `version` (label workloads use) | `tag` (what to check out) | `commit` |
|---|---|---|
| `1.0.0` | `v1.0.1` | `95a0576f04837b599b5cfbf1fae6908728197fc6` |
| `2.0.0` | `v2.0.1` | `e505587b1f8ab674b6147a8c955f468b49fa9ab4` |
| `2.1.1` | `v2.1.1` | `95579dd567b2c0e490ce56aeb0504290085651f6` |

(`version` and `tag` differ for the first two because those are CI-only-fix
patch releases — see the policy repo's README. Always check out by `tag`.)

## 1. Clone the exact pinned commit

```sh
git clone --branch v2.1.1 https://github.com/policy-as-versioned-flux/policy
cd policy
git rev-parse HEAD   # should print 95579dd567b2c0e490ce56aeb0504290085651f6
```

## 2. Provenance: verify the tag before trusting anything in it

```sh
git fetch origin '+refs/tags/v2.1.1:refs/tags/v2.1.1' --force  # see note below
GITSIGN_REKOR_MODE=offline gitsign verify-tag v2.1.1 \
  --certificate-identity=chris@cns.me.uk \
  --certificate-oidc-issuer=https://accounts.google.com
```
> `git clone --branch` (and GitHub Actions' `actions/checkout`) can leave the
> local tag ref flattened to point straight at the commit instead of the
> annotated tag object `gitsign` needs to verify — found the hard way in
> issue 04. The `git fetch --force` line re-fetches the real tag object.

## 3. Fixtures: does the CEL logic behave as documented?

```sh
./verify.sh   # kyverno test against every policy's tests/*/kyverno-test.yaml
```
Green means the pass/fail/skip fixtures — which double as worked examples,
the **testable** -able — still match the policy body.

## 4. See the rendered manifest (no cluster needed)

```sh
kustomize build workloads/kyverno/require-known-department-label
# or, Flux-aware (same output here, but this is what a Kustomization
# resource would actually apply, including any Flux-specific postBuild):
flux build kustomization require-known-department-label \
  --path=./workloads/kyverno/require-known-department-label \
  --kustomization-file=<(cat <<'EOF'
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: require-known-department-label
  namespace: flux-system
spec:
  sourceRef: {kind: GitRepository, name: policy}
  path: ./workloads/kyverno/require-known-department-label
EOF
) --dry-run
```

## 5. Reproduce the admission verdict for a sample workload — fully offline

This is the step PRD's "usable" -able is actually about: **a dev reproduces
the admission verdict on their laptop, against the same pinned policy
versions the cluster runs.**

```sh
kustomize build workloads/kyverno/require-known-department-label > /tmp/policy.yaml
cat > /tmp/sample-workload.yaml <<'EOF'
apiVersion: v1
kind: Pod
metadata:
  name: sample-workload
  labels:
    mycompany.com/policy-version: "2.1.1"
    department: not-a-real-department
spec:
  containers:
    - name: app
      image: nginx:latest
EOF
kyverno apply /tmp/policy.yaml --resource=/tmp/sample-workload.yaml
```
```
policy require-known-department-label-2.1.1 -> resource default/Pod/sample-workload failed:
1 -  The 'department' label, if set, must be one of: platform, finance, security, engineering, legal.

pass: 0, fail: 1, warn: 0, error: 0, skip: 0
```

**Verified against the live cluster** (`kubectl apply -f /tmp/sample-workload.yaml`,
`cluster1`): identical verdict, identical message, both refused. Fix the
`department` label to `platform` and both `kyverno apply` and the live
cluster admit it — try it.

## 6. `flux diff` — PR preview against a real cluster

Unlike steps 1–5, this one needs `kubectl` access to a real cluster (it's a
diff *against* what's actually running there, not an offline render):

```sh
flux diff kustomization policy-2.1.1-require-known-department-label \
  --path=./workloads/kyverno/require-known-department-label
```

## What this proves, and what it doesn't

Following this doc verbatim reproduces the cluster's actual admit/deny
verdict for a sample workload (step 5, cross-checked against `cluster1`
live) — but it doesn't reach into the **shared Kyverno webhook** bug issue
08 found and fixed (`matchConditions`, not `matchConstraints.objectSelector`):
that bug only manifests when *multiple* policy versions are installed
simultaneously on one cluster, which `kyverno apply`'s offline, single-policy
evaluation has no way to reproduce. It's the right tool for "does this one
policy admit this one workload", not for "is the whole multi-version fleet
internally consistent" (that's what `fleet/verify-coexistence.sh` is for).
