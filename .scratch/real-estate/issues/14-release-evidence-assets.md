# 14 — Release evidence assets: rendered bundle + checksums

**What to build:** Each policy release additionally carries audit evidence: a bundle of the rendered per-policy output (exactly what a consumer at that tag adopts) plus a checksums file, both generated in the same CI run that verifies the tag's signature. Framed explicitly as evidence, never transport — the release body states "consume the tag, not this" so no second consumption path emerges beside ADR-0001's. No SBOM (rejected at grilling as hollow for YAML).

**Blocked by:** None — can start immediately (proven at the next tag cut).

**Status:** ready-for-agent

- [ ] Next release carries the rendered bundle + SHA256SUMS as assets
- [ ] Assets generated in the signature-verifying CI run itself, not a separate pipeline
- [ ] The non-consumption note appears in the release body
- [ ] Checksums verify against a locally-rendered build of the same tag
