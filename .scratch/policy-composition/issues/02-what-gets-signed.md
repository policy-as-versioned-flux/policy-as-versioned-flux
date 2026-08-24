# 02 — What gets signed

Type: grilling
Status: resolved
Blocked by: none

Graduated from the map's Not yet specified: "What gets signed."

## Question

Each party signs its own artefact today. A composed set is a new artefact. What signs it, and how?
For a verifier to trust a composed set, the render must be reproducible from the signed parent
digests. What does that reproducibility guarantee need to look like, and who or what produces the
signature over the composed result?

## Answer

**Fact-check first (today's reality).** "Signed" today means the git tag carrying a party's
artefact is gitsign-signed (keyless sigstore) — verified only in CI/at-merge, since Flux cannot yet
verify gitsign at admission (`fluxcd/source-controller#1068`, ADR-0001). No party publishes a
content digest; Renovate pins each parent's resolved commit SHA (`versions.yaml`). The `cs-06b`
spike explicitly leaves signing "not addressed" — the map's "signed parent digests" phrase is the
spike's own named gap, not built code.

**Decided.**

1. A composed policy set is a real, published, signed artefact of its own — not computed
   ephemerally and never signed.
2. The adopter signs it, exactly as it signs any artefact it publishes today: a gitsign-signed git
   tag. No second signing mechanism.
3. A parent's "digest" is its resolved git commit SHA — the same one Renovate already pins. Reused,
   not invented (standing preference: reuse the estate's engines).
4. Verification of a composed artefact stays CI/merge-time only, the same floor every other artefact
   gets today. Composition does not raise the bar past ADR-0001's already-known, already-tracked
   Flux/gitsign admission-time gap.
5. A composed artefact carries an explicit marker distinguishing it from a leaf artefact, so a
   verifier knows to also check parent SHAs. This extends the `cs-06b` spike's existing advisory
   metadata (`composed-for` label, `inherited-from`/`source-path` annotations per rule —
   `compose.py:330-355`), which the spike already proved strips cleanly back to the committed file
   Kyverno reads (`render_is_faithful`).
6. The parent-SHA record sits once at the top of the composed artefact, not repeated per rule — one
   file draws from one fixed parent set.
7. The reproducibility bar is byte-for-byte deterministic: CI re-renders the composition from the
   parents' pinned SHAs and compares.

**Recorded in the domain model.** `CONTEXT.md` gains a **Composed artefact** term and a note that an
adopter becomes a publisher of its own composed result. [ADR-0012](../../../docs/adr/0012-composed-artefact-self-signed-pinned-sha.md)
records the decision; ADR-0001 gains a one-line pointer to it.
