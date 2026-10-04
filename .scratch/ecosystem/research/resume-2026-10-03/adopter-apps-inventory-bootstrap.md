# Adopter apps release before CVE inventory adoption

Prepared 2026-10-03 from local git objects only. No fetch, publication, metadata change, tag creation or shared-clone mutation was performed. Local origin/main refs are observations of the last fetched state, not a claim about current remote state.

## Why there are two stages

The proposed inventory compiler reads the apps GitRepository's exact tag+40-character SHA and follows the matching Flux Kustomization's resource graph at that commit. It includes init/ephemeral containers and refuses unpinned images, unsupported transforms, missing images and any inventory whose complete image set differs. A working-tree manifest is not served by an older immutable tag. Existing proposed inventories therefore cannot be made valid by changing their image names to match a stale pin.

The published adopter cut-release workflow uses an independently authenticated platform-tools pin and verifies the composed artefact byte-for-byte BEFORE creating a signed annotated tag. Platform v4.0.0 has no wargamer/inventory.py; its CVE converter prices the feed headline, with no inventory input. Retaining this actual published compiler and each adopter's published parent pins allows a real app-only release to precede the new inventory contract without changing any gate.

## Local immutable observations

| Adopter | Local origin/main | Published apps pin | Existing signed v3.0.0 commit |
|---|---|---|---|
| driftwood | 529e159397d3e64f94b0270cc7de69c235580961 | v1.0.0 / 92034b0927eb0c15aa9760deddbe6da2960038f0 | bf9889aa6a6d979c87a5633240a1447765d73503 |
| tuppence | 6e164faea7ca51529b35f4485e96ee8b92ce05d1 | v1.0.0 / 9862d846332031d7cb5cf38894d3b0ed321928df | 3d64a4d65d5eb5d81deedc10a0826c8b02d0ad39 |
| ludlow | 9df8efda60b4f4291b0407b4b4b9216c1d416dfb | v1.0.0 / 7bd9973be43de0b5d1d13b7eb46a1a60b01516ec | 45b3fbd21d2838f8882dfa6265b3a6e8fa61b3a9 |

All published compiler and policy-parent pins are platform v4.0.0 / 557c1538fe022c784ea4ffb345c92d2e4b11fe71. Worktrees currently move apps pins to v3.0.0; those edits are pending. The published composed-source declarations independently pin v3.0.0.

At v1.0.0, all three apps resource graphs contain Namespace/ConfigMaps and no workload image. At v3.0.0 driftwood serves bare nginx plus the old hub storefront image; tuppence/ludlow serve the old hub ledger/reports digests. Those trees do not contain the new adopter-owned v1.0.1 image refs. Local platform tags stop at v4.0.0; local feeds tags contain only threat-register/v1.0.0, v2.0.0 and v3.0.0. Tools v5.0.0, policy 7 and cve/v3 must be real signed published objects before any final pin is written; their future SHAs are not guessed here.

## Stage 1: reviewed apps-only release, each adopter separately

1. Use a clean isolated checkout based on that adopter's published main. Preserve the published .github/platform-tools-pin.yaml, every parent pin, party.yaml, accepted-major records and absent inventory state. Do not carry over the large pending final-adoption worktree wholesale.
2. Change only workload app manifests and their resource membership to the real published image version+digest. Driftwood includes its nginx Pod digest as well as storefront and the newly listed API; tuppence includes ledger; ludlow includes reports. Keep the existing policy 5.0.0 claims. Keep deploy/pod.yaml consistent with its served mirror where required. App source migration/deletion and other unrelated prepared work belong in the final adoption unless necessary for this app graph.
3. If app membership changes composition inputs (for example workload-share prices), recompose and commit the resulting derived files using the exact independently verified v4.0.0 compiler and the unchanged published parent trees. Never accept stale composed bytes. Run the unchanged wrapper check/verify and normal shift-left/served-workloads/reach checks. Compare the composed member sets with the ordinary adopter bump grader; preserve its result, including none, rather than lowering a major. The available next patch candidate v3.0.1 is prospective until the ordinary grading and unused-tag checks pass.
4. Open the concrete app-only PR with the exact diff, complete digest set and gate evidence. Delegated owner acceptance covers this prepared scope. Merge only through the existing reviewed-PR path.
5. Dispatch the adopter's existing cut-release.yml from merged main. It authenticates tools, resolves/grades parents, verifies composition, rejects an existing tag, then gitsign-signs using the adopter cut-release Actions identity and pushes the tag through git. No unsigned/local stand-in tag, tag force-move, REST git-data tag, gate weakening or invented self-reference.
6. Explicitly dispatch release.yml for the new tag if required because GITHUB_TOKEN tag pushes do not trigger a second workflow. Record identity-pinned signature verification, tag object, peeled commit and release result. This real signed tag+SHA is the prerequisite consumed in stage 2. The tag's own apps declaration may still reference the previous release; that is normal and avoids pretending a future commit is already known.

## Stage 2: adopt the real app tag, inventory and policy/feed/tools changes

1. Only after stage 1's signed tag exists, update gitops/flux-system/gotk-sync.yaml tag AND commit to that exact observed object. Preserve path ./gitops/apps and matching sourceRef. Verify the tag with the adopter's own cut-release identity and Actions issuer.
2. Scan every image in that immutable tag's apps resource graph using pinned Trivy 0.69.3; record the actual scanner version, DB date, digest and full vulnerability rows. Existing cached rows are reusable only if their requested and observed digests and complete graph match exactly. If app maintenance changes an image digest again, regenerate that image's scan before composition. Do not rename rows to cover an unscanned image. Driftwood's nginx row is mandatory while its Pod remains listed.
3. Use the real signed tools v5.0.0 tag+SHA independently from the policy parent. Adopt the actual policy 7 release/implementation tag+SHA and feed 3 tags+SHAs as the final prepared changes require. Resolve each individual feed by its own published tag and path; one threat-register tag does not attest cve/v3. Add/retain the owner-delegated exact-version acceptance records and preserve the ordinary grader's major result.
4. Bind inventory/images.json to the new apps pin with the unmodified complete-set validator. Recompose all final changes using the authenticated tools and exact parent trees; retain honest absences, refused instruments and evidence. Run composition replay, normal shift-left, exact-pin/signature and reach checks. This is where the remaining prepared architecture, twin/drift workflows, app-source migration and cloud opt-in work can be included at their own declared waits.
5. Review/merge the complete final-adoption PR, cut its real signed adopter release, and then move gitops/composed/composed-set.yaml to that observed tag+peeled SHA with the exact supported array and signature-gates list. This is an ordinary reviewed follow-up self-pin commit, not a future-commit pin. The apps source can remain at stage 1's immutable app-containing tag if its resource graph and inventory remain unchanged; it does not need to follow the policy release merely to share a number.

## Public repository/admin proof boundary

No repository visibility/admin write is performed by this task. Before any parent-led metadata or public publication action, the reviewable payload must prove this is already public demonstration source: concrete repository identity, current local content/diff and public-demo disclosures, absence of credentials/private customer payload, and any materially newly exposed history. A signed historical tag carrying a public workflow identity is historical evidence, not proof of current repository admin state. The parent must read current repo metadata through the approved path before changing it; authorization alone does not substitute for payload proof. Publication is authorized only after that low-risk proof is recorded.

## Evidence seams

- Adopter origin/main:.github/workflows/cut-release.yml: independently pinned tools; exact parent pair verification; byte-for-byte composition before sign; immutable signed tag through git push.
- Adopter origin/main:.github/scripts/platform-tools.py: exact tool HEAD/tag/SHA, clean checkout, expected platform cut-release identity and Actions issuer.
- Platform v4.0.0:compose/composition.py verify() and _feed_scenario(): headline CVE pricing and recorded replay, no inventory reader.
- Proposed platform/wargamer/inventory.py served_images(), trim(), validate(): exact tagged app graph, pinned digest/scanner/DB, whole image-set equality.
- Adopter origin/main:.github/scripts/adopter-gate.py compose(): ordinary maximum added-member bump and forced-major retirement; owner acceptance admits a major without reducing its grade.

Prepared stage-1 patches/commits and exact local verification evidence will be linked here after the isolated checks finish. No activation or publication is inferred from their presence.

## Stage 1 local delivery checkpoint

Isolated checkouts: /private/tmp/pavf-apps-bootstrap-lnuADR/<adopter>-estate/<adopter>. Durable locator: adopter-apps-bootstrap-isolated.json. All three published-source compositions and byte replays PASS; all ordinary adopter graders report none, and every served app plus deploy Pod passes Kyverno 1.18.2. The globally installed 1.19.1 fails legacy cage compilation and is not the declared stage-1 engine. Prospective v3.0.1 is unclaimed in all inspected local tag namespaces.

Prepared patches and PR bodies: <adopter>-apps-bootstrap.patch and <adopter>-apps-bootstrap-pr.md. Stage-1 changed only app manifests/resource membership, driftwood deploy Pod image mirror, and the rederived composed/HEADER.yaml comparison-input hash. Compiler/parent/party/self-pin declarations and absent inventory state remain unchanged.

Full authenticated wrapper verification remains WAIT. Exact compiler commit and annotated signed object exist, but cached TUF timestamp expired 2026-09-29, and the installed verifier attempted an online Rekor lookup despite the wrapper offline environment. Sandbox DNS rejected it; no external connection succeeded. No insecure flag or fake signature proof was accepted. Parent must complete genuine authentication before publishing.

Normal local git commit was attempted with existing SSH signing and hooks untouched. Each attempt timed out after 15 seconds with no output and no new commit. The staged patches/bodies are concrete and reviewable; commit creation remains WAIT for normal local signing to work. No unsigned commit/tag or signing/hook override was substituted. Detailed statuses: adopter-apps-bootstrap-delivery.json and verification/shift-left JSON files alongside this report.

## Authorized publication checkpoint

Root completed the former authentication and signing waits: every unmodified compiler wrapper passed genuine Sigstore/Rekor identity verification, and normal configured SSH-signed source commits were created. Latest public mains advanced only the two observation lanes; the source commits were normally rebased and their signatures and exact payload reviewed again. All three repositories were confirmed public, unarchived, default main, with administrator access. No repository metadata was changed.

Published app-only PRs: driftwood #53, tuppence #51, ludlow #48. Both GitHub shift-left and compose-check checks PASS for all three exact reviewed heads. Branch/PR command sessions are drained. Matching-head second App approval and normal merge remain prerequisites for the existing v3.0.1 cut/release workflows. No tag/release/source self-pin has been fabricated. Current evidence: adopter-apps-bootstrap-publication-proof.json, adopter-apps-bootstrap-rebased.json, adopter-apps-bootstrap-github-ci.json, adopter-apps-bootstrap-release-checkpoint.json.

## Stage 1 complete — actual published bootstrap objects

All three app-only PRs were App-approved at the exact independently reviewed signed heads and normally merged, and the existing cut and explicit release workflows passed. Real v3.0.1 tag/commit pairs: driftwood 17302ecd20041df61a52428e67246c330294d2a6; tuppence d8dead25e0e5e275172640b1a637562e45edb15d; ludlow 5ff463673cf05af71a5db2ed0c38deaf263464d2. Full signature/Rekor/identity proof and published release URLs: adopter-apps-bootstrap-release-delivered.md and adopter-apps-bootstrap-final-delivery.json. No stage2/pin/inventory change occurred. All prior authentication/signing waits are superseded; all execution sessions drained.
