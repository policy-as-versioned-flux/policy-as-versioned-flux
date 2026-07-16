# 14 — Release evidence assets: rendered bundle + checksums

**What to build:** Each policy release additionally carries audit evidence: a bundle of the rendered per-policy output (exactly what a consumer at that tag adopts) plus a checksums file, both generated in the same CI run that verifies the tag's signature. Framed explicitly as evidence, never transport — the release body states "consume the tag, not this" so no second consumption path emerges beside ADR-0001's. No SBOM (rejected at grilling as hollow for YAML).

**Blocked by:** None — can start immediately (proven at the next tag cut).

**Status:** done

- [x] Next release carries the rendered bundle + SHA256SUMS as assets
- [x] Assets generated in the signature-verifying CI run itself, not a separate pipeline
- [x] The non-consumption note appears in the release body
- [x] Checksums verify against a locally-rendered build of the same tag

## Comments

Done 2026-07-16, live-proven with a real tag cut (user confirmed cutting a new release
specifically to prove this, since the mechanism can't be verified without one).

`v2.2.1` cut as a CI-only-fix patch (zero verdict impact — no `workloads/kyverno/` or `cloud/`
change; every policy still declares itself `2.2.0` internally, same `version != tag` pattern
`v1.0.1`/`v2.0.1` established) carrying ticket 05's handbook extraction and this ticket's own
workflow change. Gitsign-signed with the real cached credential
(`chris@cns.me.uk` via `accounts.google.com`), verified.

**All four criteria proven against the real release, not assumed:**
- `gh release view v2.2.1 --json assets` lists all 5 rendered policy YAMLs +
  `SHA256SUMS` — real GitHub Release assets, not a local artifact.
- Generated inside `release.yml`'s existing signature-verifying job (a new step ahead of the
  publish step, same run, same `GITHUB_SHA`) — confirmed by reading the merged workflow file, not
  a separate pipeline.
- The release body's tail contains the exact "Evidence, not transport... Consume the tag, not
  this" text, confirmed via `gh release view --json body`.
- Downloaded the real assets (`gh release download v2.2.1`), `sha256sum -c SHA256SUMS` — all 5
  verify. Then independently re-rendered the same tag from a **fresh `git checkout v2.2.1` +
  `kustomize build`**, outside the CI run entirely, and diffed the checksums by hand: all 5 match
  byte-for-byte. The assets are exactly what the tag renders to, not merely internally consistent
  with themselves.
