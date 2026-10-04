# 154 — One repo per app, in its adopter's org

Type: task (AFK)
Status: claimed
Blocked by: none

## Question

Build the app half of [ADR-0036](../../../docs/adr/0036-the-incumbent-org-shrinks-to-the-hub-app-repos-transfer-and-the-rest-are-archived.md).

1. Transfer `policy-as-versioned-flux/ledger` to `policy-as-versioned-tuppence`, `storefront` and `api` to `policy-as-versioned-driftwood`, and `reports` to `policy-as-versioned-ludlow`. Use the owner's `gh` login, as the owner authorised on 2026-09-25 (ticket 35 round 2 Q9). Record each transfer in this ticket.
2. Cut a tag in each transferred repo so that `release.yml` builds under the adopter org. **The four tag cuts are owner authorisations that are not yet given.** The incumbent tags are the owner's own, and the transfer authorisation does not cover a tag cut. Ask on or after 2026-09-26, inside the five-a-day limit. Then make each new package public after its first publish, under the transfer authorisation. First confirm that each adopter org lets `GITHUB_TOKEN` create a package. Give each transferred repo its own Renovate `extends`: its `renovate.json` holds only `$schema`, and the incumbent org's inherited preset does not apply in an adopter org.
3. In each adopter, a reviewed pull request drops `apps/<app>/`, re-points `gitops/apps/<app>.yaml` to the new image by digest, and adds a Renovate manager that bumps that digest. No adopter has one today.
4. Lift api into driftwood beside storefront: re-label it off `mycompany.com/policy-version`, re-pin it to driftwood's composed set, give it a served manifest, and confirm that driftwood's `served-workloads.py` prints api's manifest beside `pod.yaml` and `storefront.yaml`. api's README calls it "the good citizen". Give that a dated correction: on 2026-09-25 its binary carried 8 HIGH CVEs, all in the Go standard library 1.26.5, on an end-of-support alpine 3.20.10 base.
5. Rewrite `verify/lifted-apps` to read each app's source from its app repo. Keep its planted failures. Its register gains api. Its `LIMIT 3 of 3` image line reaches zero only when every served image is built in its adopter's org. Correct its BLIND lines: reading the archived flag needs no credential, and on 2026-09-25 anonymous pulls of all four pinned digests returned HTTP 200.

## Notes

Graduated 2026-09-25 from ticket 35, round 2 Q4, Q5 and Q9. Definition of done includes wiring its check into `talk/verify-all.sh`.

Facts on 2026-09-25: each adopter org held one repo only, so no name collides. Each incumbent `release.yml` publishes to `ghcr.io/${{ github.repository }}`. The Mend `renovate` app and `pavc-other-hand` are installed on all repos in each adopter org. The app's installation does not carry a repo's inherited Renovate config across orgs. `pavc-other-hand` holds `contents`, `pull_requests` and `workflows` write there. GitHub keeps a container package in the old account when its repo moves, so the four old packages stay in the incumbent org.

Order: this ticket before ticket 155 is preferred, so the lane runs the image each adopter builds. Ticket 153 does not wait on it. But a dependency bump moves a price only after this ticket, because only then does a bump change the served digest.

## Answer

**Local implementation, 2026-10-03.** The earlier four transfers, signed v1.0.1 app tags and public packages were already completed and independently verified in the Claude sessions on 2026-09-26. On 2026-10-03 anonymous GHCR reads returned HTTP 200 for all four v1.0.1 manifests; exact immutable digests are recorded in [transferred-image-digests.json](../research/resume-2026-10-03/transferred-image-digests.json). The adopter manifests now name those packages, bundled app sources are dropped, and app tag+digest Renovate managers are added. Driftwood lists API beside checkout-svc and storefront; its claim is 5.0.0 in the governed Namespace. The simple nginx Pod is digest-pinned too. Apps self-pins move from v1.0.0 to the newest existing signed v3.0.0 tag/commit. Today's new images/API are not yet in that older signed tree: another reviewed signed adopter tag and self-pin move remain required. The historical API eight-HIGH finding is recorded; its new image inventory is not guessed. Hub lifted-app grading and app-repo configuration/correction are coordinated by the integrator. No external push or release was made by this continuation.

**Delivered later in this continuation.** Four independent-app maintenance PRs are reviewed and merged: ledger #12, storefront #16, API #6 and reports #11. The app-only adopter PRs driftwood #53, tuppence #51 and ludlow #48 are reviewed and merged, and all three normal cut/release workflows pass. Their genuine signed **v3.0.1** tags now contain the proposed app graph: driftwood `17302ecd20041df61a52428e67246c330294d2a6`, tuppence `d8dead25e0e5e275172640b1a637562e45edb15d`, ludlow `5ff463673cf05af71a5db2ed0c38deaf263464d2`. Exact signature, Rekor and Actions identity checks pass. The stage2 source apps declarations bind to those real tags; all three immutable inventory graph validators pass. Subsequent policy/inventory composition and self-pin delivery still depend on the foundational signed releases. See [delivery evidence](../research/resume-2026-10-03/adopter-apps-bootstrap-final-delivery.json).
