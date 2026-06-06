---
status: accepted
---

# Transport: distribute versioned policy as signed git tags (keyless, gitsign)

Policy is distributed as semantically-versioned **git tags** in the policy repo (faithful to the
2022 original), signed **keyless** with `sigstore/gitsign` (no long-lived GPG keys), and consumed
via a Flux `GitRepository` pinned on `spec.ref.tag`. We chose this over packaging policy as an
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

- **No Flux-native verified-source gate on the floor.** `GitRepository.spec.verify` is PGP-only and
  cannot verify gitsign. Until [fluxcd/source-controller#1068](https://github.com/fluxcd/source-controller/issues/1068)
  lands, signature **verification happens in CI / at-merge** (`gitsign verify` against Rekor), not
  at the cluster source. Provenance still exists (gitsign + Rekor transparency log).
- **Closing the gap is a tracked project action** (encourage/raise upstream; see
  `docs/upstream/fluxcd-source-controller-1068-gitsign.md`). The floor does **not** block on it.
- **Signed attestations of the "why", and SBOM, are deferred to the north-star report** (they need
  the OCI path). On the floor the rationale rides as versioned files in the policy repo (Kyverno
  annotations + `rationale.md`), travelling with the tag.
- The version **pin** lives on `GitRepository.spec.ref.tag`.
