# 154 — One repo per app, in its adopter's org

Type: task (AFK)
Status: open
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
