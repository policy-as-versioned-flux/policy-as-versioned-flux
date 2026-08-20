# policy-as-versioned-driftwood

**Institution — e-comm, PCI + GDPR, the teaching default.** Audit-heavy (loosest
£ — short-life cart data). Owns its own KinD cluster; this is the **provenance
base** the whole talk stacks on: Flux reconciling a pinned, signed
`GitRepository` at admission.

## Bring-up (idempotent, resettable — requires internet)

```sh
scripts/up.sh          # KinD -> Flux -> real GitHub source -> reconcile healthy
verify-reconcile.sh    # asserts the beat (exits non-zero if it would fail on stage)
scripts/reset.sh       # delete the cluster (or: reset.sh soft = re-apply sources only)
```

`up.sh` is safe to re-run: it skips the cluster/Flux if already up. It needs
`github.com` reachable — there is no offline fallback (ticket 09) — and fails
fast with a clear message if it isn't, rather than hanging on Flux's retries.

## How the source works

The committed [`gitops/flux-system/gotk-sync.yaml`](gitops/flux-system/gotk-sync.yaml)
is applied as-is: a `GitRepository` pointed straight at the real
`policy-as-versioned-driftwood` GitHub remote, pinned to tag `v1.0.0`. Git is
the only way cluster state changes; the revision is immutable. The design
intent (ADR-0001) is a **gitsign-signed** (keyless → Rekor) tag, verified in
the provenance beat (ticket 24); Flux's `GitRepository.spec.verify` only
speaks OpenPGP, so the signature is verified out-of-band by `git verify-tag`
/ Rekor rather than mis-declared as a PGP block. **`v1.0.0` itself is
unsigned** — see the file's own header and ticket 09's Status for why, and
ticket 10 for the per-org signed-release workflow that replaces it.

## Pinned regulator dependency (`nist`)

`gitops/flux-system/gotk-sync-nist.yaml` pins a specific tag of the real
`nist` 800-53 OSCAL catalog (`estate/nist`) as a Flux `GitRepository`,
straight from `policy-as-versioned-nist` on GitHub. `driftwood-nist-pin`
(`gitops/apps/nist-pin-configmap.yaml`) is the human/audit-readable mirror
of that pin. `verify-reconcile.sh` asserts both reconcile Ready and pinned.

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
