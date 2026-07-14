---
status: accepted
---

# Transport: distribute versioned policy as signed git tags (keyless, gitsign)

Policy is distributed as semantically-versioned **git tags** in the policy repo (faithful to the
2022 original), signed **keyless** with `sigstore/gitsign` (no long-lived GPG keys), and consumed
via a Flux `GitRepository` pinned on **both `spec.ref.tag` and `spec.ref.commit`** (the tag's
resolved SHA — see Consequences: post-merge tamper resistance). We chose this over packaging policy as an
**OCI artifact** signed with cosign, even though OCI is the only path that gives a *Flux-native*
verified-source admission gate today, because OCI's value here was almost entirely working around
a current Flux limitation rather than serving the thesis — and the thesis prizes the git tag as the
most legible, reviewable expression of "what is the policy and what version is it."

## Considered options

- **Signed git tags + gitsign (chosen).** Faithful, keyless, minimal moving parts. Policy stays
  browsable files in git.
- **OCI artifacts + cosign keyless (rejected for the floor).** The only combination that works in
  Flux *today* for keyless signing **plus** a `spec.verify` gate, and the natural carrier for
  signed "why" attestations + SBOM. Rejected as complexity introduced to dodge a Flux gap, not to
  serve the thesis. Retained as the **north-star** option and the home for attestations/SBOM.
- **Git tags + long-lived GPG keys (rejected).** Faithful and Flux-verifiable, but reintroduces
  GPG key custody across a fleet — the operational cost we are explicitly avoiding.

## Consequences

- **No Flux-native verified-source gate on the floor.** `GitRepository.spec.verify` is PGP-only (Flux
  v2.9, Jun 2026, added SSH commit-signature verification — still not Sigstore/gitsign) and cannot
  verify gitsign. Until [fluxcd/source-controller#1068](https://github.com/fluxcd/source-controller/issues/1068)
  lands, signature **verification happens in CI / at-merge** (`gitsign verify`), not at the cluster
  source. Provenance still exists (gitsign + Rekor transparency log).
- **Post-merge tamper resistance — pin the resolved commit, not just the tag.** A `GitRepository`
  pinned on `spec.ref.tag` alone re-resolves the tag every reconcile, so a force-moved tag would be
  pulled silently, and the artifact on the cluster would no longer be the one CI verified. To close
  this, Renovate writes the tag's **resolved commit SHA into `spec.ref.commit`** (via the `git-refs`
  datasource); Flux pins that immutable commit and ignores any later tag force-move, and CI verifies
  that exact SHA. As defence in depth, release tags are **forge-protected/immutable** (GitHub ruleset
  / Immutable Releases; GitLab protected tags) and `notification-controller` alerts on any unexpected
  revision drift.
- **CI verification runs offline against a persisted Rekor bundle** (`GITSIGN_REKOR_MODE=offline`,
  gitsign pinned): the Rekor inclusion proof is captured at tag-creation and verified from the tag
  object, so the CI gate does **not** depend on Sigstore's public-good Rekor search API (which is on
  its own turndown/v2 schedule) and the story is air-gap-friendly.
- **Closing the on-cluster gate is a tracked project action** (encourage/raise upstream; see
  `docs/upstream/fluxcd-source-controller-1068-gitsign.md`). The floor does **not** block on it; the
  commit-pin + forge-immutability above make the accepted residual (no on-cluster keyless gate)
  low-risk.
- **Signed attestations of the "why", and SBOM, are deferred to the north-star report** (they need
  the OCI path). On the floor the rationale rides as versioned files in the policy repo (Kyverno
  annotations + `rationale.md`), travelling with the tag.
- The version **pin** lives on `GitRepository.spec.ref` as the `{tag, commit}` pair; the human-legible
  semver tag remains the identity, the commit SHA is the integrity anchor.
