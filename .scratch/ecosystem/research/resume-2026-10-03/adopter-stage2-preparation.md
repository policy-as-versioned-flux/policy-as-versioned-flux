# Stage2 authentic apps and inventory preparation

Prepared locally on 2026-10-03. Stage2 is unpublished; foundation release pins remain unchanged.

| Adopter | Apps release | Exact peeled commit | Primary vulnerability rows |
|---|---|---|---|
| driftwood | v3.0.1 | `17302ecd20041df61a52428e67246c330294d2a6` | API: 0; storefront: 212; nginx: 395 |
| tuppence | v3.0.1 | `d8dead25e0e5e275172640b1a637562e45edb15d` | ledger: 9 |
| ludlow | v3.0.1 | `5ff463673cf05af71a5db2ed0c38deaf263464d2` | reports: 228 |

Only `gitops/flux-system/gotk-sync.yaml` and new `inventory/PROVENANCE.json` changed in this task. Existing normalized `inventory/images.json` bytes, party declarations, compiler/policy pins and composed-source self-pins are unchanged. Authentic annotated tag objects were copied locally from the stage1 verified isolated repositories. No external tag or ref was created. Full signature, Rekor and exact Actions identity proofs are in `adopter-apps-bootstrap-final-delivery.json`.

Every image in each exact tagged Flux resource graph is covered, including driftwood nginx. Fresh pinned Trivy 0.69.3 scans used the same cached vulnerability database, dated `2026-10-03T07:01:46.027466673Z`, without a DB update. All five raw ArtifactName values equal the requested digest-pinned image; every RepoDigests list confirms its exact sha256. Native trim recreates all existing normalized rows identically. The scanner archive checksum matches the captured release checksum. Raw reports, both version snapshots and trimmed replay outputs are retained in ignored `adopter-stage2-trivy-raw/`, with hashes in `adopter-stage2-primary-scan-proof.json` and the source provenance records. No scanner row was renamed or invented.

Focused integrity checks passed 32 tests and 46 subtests. All nine sampler, workload and OSCAL selfchecks passed. All three existing cage probes passed offline against declared Kyverno 1.18.2, the pinned composed v3.0.0 and HEAD, and every currently served policy 5.0.0. These are document proofs; no cluster observation, cloud activation or engine upgrade is asserted. Prepared standalone apps/inventory patches apply cleanly to each recorded local source base.

All three candidate compositions return composed, and all three pass byte-for-byte replay after relocation to temporary source copies. The narrow fixes preserve unpriced amounts and tiers as absent; the missing frequency remains a named absence, and path normalization now retains the same portable reason through filesystem aliases. Final proof is in `adopter-stage2-compose-replay.json`; earlier failures and exact diffs are retained as historical diagnostics. The compiler owners' focused regressions and independent standards review passed. This rehearsal uses prepared source worktrees, not authenticated new foundation releases. No shared composed source files were written.

Publication prerequisites:
- A real independently authenticated platform tools 5 release and exact peeled commit. Existing compiler pins remain v4.0.0.
- A real signed policy 7 implementation publication and its exact supported array. Existing policy parent pins remain v4.0.0.
- The real signed individual feeds releases, including cve/v3, with exact tag and commit. A threat-register tag does not establish a cve tag.
- Composition and byte replay with those authenticated, immutable trees before the reviewed stage2 merge and normal cut. Only afterward may the composed source move to the actual resulting signed release commit.
- Cloud activation needs the qualifying modern e2e step 4 signed-clock PASS, a signed cloud package, actual vendor schemas, and signed tuppence composed delivery paths.
- The engine upgrade needs a scheduled 1.18.2 PolicyReport baseline followed by the scheduled 1.19.1 comparison. The current declared engine remains 1.18.2.

Separate exports: `<adopter>-stage2-apps-inventory.patch` includes the exact apps pin, unchanged normalized inventory and primary provenance. `<adopter>-stage2-apps-pin-delta.patch` contains this task's pin delta from the pre-task v3.0.0 declaration. `adopter-stage2-patch-validation.json` records source bases and patch hashes. All execution sessions are drained.
