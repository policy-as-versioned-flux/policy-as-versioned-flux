# policy-as-versioned-driftwood

**Institution — e-comm, PCI + GDPR, the teaching default.** Audit-heavy (loosest
£ — short-life cart data). Owns its own KinD cluster; this is the **provenance
base** the whole talk stacks on: Flux reconciling a pinned, signed
`GitRepository` at admission.

## Bring-up (idempotent, offline-safe, resettable — the touring requirement)

```sh
scripts/up.sh          # KinD -> Flux -> in-cluster git source -> reconcile healthy
verify-reconcile.sh    # asserts the beat (exits non-zero if it would fail on stage)
scripts/reset.sh       # delete the cluster (or: reset.sh soft = re-seed only)
```

`up.sh` is safe to re-run: it skips the cluster/Flux if already up and re-seeds
the source. Everything after the first controller-image pull is offline.

## How the source works

For the tour there is no network luck: `up.sh` seeds the [`gitops/`](gitops/)
tree into a git repo, tags it `v1.0.0`, bakes it into a tiny
[`git-server/`](git-server/) image (busybox-httpd smart-HTTP CGI over
`git-http-backend`), `kind load`s it, and points a `GitRepository` **pinned to
that tag + commit SHA** at the in-cluster service. Git is the only way cluster
state changes; the revision is immutable.

The committed [`gitops/flux-system/gotk-sync.yaml`](gitops/flux-system/gotk-sync.yaml)
is the canonical form pointed at the real `policy-as-versioned-driftwood` GitHub
remote — where the `v1.0.0` tag is **gitsign-signed** (keyless → Rekor) and
verified in the provenance beat (ticket 24). Flux's `GitRepository.spec.verify`
only speaks OpenPGP, so the gitsign signature is verified out-of-band by
`git verify-tag` / Rekor rather than mis-declared as a PGP block; the pin + the
signed tag are the provenance.

## Pinned regulator dependency (`nist`)

`gitops/flux-system/gotk-sync-nist.yaml` pins a specific signed tag+commit of
the real `nist` 800-53 OSCAL catalog (`estate/nist`) as a Flux `GitRepository`
— the same in-cluster git server driftwood's own source uses, serving both
bare repos. `driftwood-nist-pin` (`gitops/apps/nist-pin-configmap.yaml`) is
the human/audit-readable mirror of that pin. `verify-reconcile.sh` asserts
both reconcile Ready and pinned.

A regulator version bump arrives as a reviewable PR:
`scripts/bump-nist-pin.sh v1.1.0` edits the pin on a branch and prints the
diff — propose only, a human merges.

## Pinned platform dependency (the config-base pattern)

`gitops/platform/platform-pin.yaml` pins a specific signed tag+commit of
`platform` and reconciles its `./distribution` — flux-operator fans the version
array out into this cluster (per-version policies + orphan-guard). driftwood
consumes the discipline; it never authors it. Opt-in (not in the Phase-0 `apps`
reconcile) and needs Kyverno + flux-operator installed first — see
[`estate/platform/distribution/README.md`](../platform/distribution/README.md).
A platform bump arrives as a reviewed PR editing `.spec.ref.tag` here.

## What's here now vs later

Phase 0 (this ticket): cluster + Flux + one reconciled version marker. Later
tickets add the Kyverno CEL policy set (fanned out from platform's `ResourceSet`
version array), the `ico` pin, and the risk skin.
