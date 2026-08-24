---
status: accepted
---

# Composed artefact: self-signed by the adopter, reproducible from pinned parent SHAs, verified in CI

A composed policy set (an adopter's effective policy, inherited from several parents' signed
artefacts) is itself published and signed, not computed ephemerally and never signed. The adopter
signs it exactly as it signs any artefact it publishes: a gitsign-signed git tag (ADR-0001), no
second signing mechanism. A parent's "digest" is the resolved git commit SHA Renovate already pins
in `versions.yaml` (ADR-0002), not a newly-invented content hash. That SHA, for every parent, sits
once at the top of the composed file (extending the `composed-for` / `inherited-from` /
`source-path` advisory annotations `cs-06b` already adds per rule), so a verifier can re-render the
composition from the pinned parents and check the result byte-for-byte.

## Considered options

- **Adopter self-signs, reused parent SHA (chosen).** No new signing identity, no new digest
  mechanism — the same tag-level gitsign and the same Renovate-pinned commit the estate already
  trusts, now also covering a derived artefact.
- **A shared composition service signs.** Rejected: introduces a signing identity distinct from any
  party's own key, for no benefit a self-signing adopter doesn't already give a verifier.
- **A fresh content-hash digest per parent.** Rejected: a second integrity mechanism alongside the
  git-SHA one Renovate already maintains, with nothing gained that composition doesn't already get
  from the resolved SHA.

## Consequences

- **Verification stays CI / merge-time only**, the same floor every other artefact gets today
  (ADR-0001's Flux/gitsign gap is not re-litigated here; composition does not raise the bar).
- **The composed artefact carries an explicit marker** distinguishing it from a leaf artefact — a
  verifier checking a leaf only checks its own tag; a verifier checking a composed one also checks
  the parent SHAs recorded at the top of the file.
- **The render remains what `cs-06b`'s `render_is_faithful` already proved**: strip the advisory
  metadata (now including the parent-SHA block) and the file underneath is unchanged — Kyverno never
  reads any of it.
