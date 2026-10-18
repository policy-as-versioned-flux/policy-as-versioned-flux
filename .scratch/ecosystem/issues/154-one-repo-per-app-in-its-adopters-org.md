# 154 — One repo per app, in its adopter's org

Type: task (AFK)
Status: resolved
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

**2026-10-18, delivered app lift reconciled.** The five original conditions are delivered.
The older pending statements above describe their dated stages; the later source deletion and
served self-pins below complete the lift. This is a record correction from immutable public
sources and existing delivery receipts, not a new image build, scan or cluster observation.

1. **Transferred repositories, app releases and public images.** The four adopter-owned repos
   retain their genuine signed app `v1.0.1` releases and the exact image digests the adopters
   serve. The transfers and first releases were completed on 2026-09-26. The preserved
   anonymous manifest receipt linked in the historical Answer records HTTP 200 for all four
   on 2026-10-03; it is dated evidence, not a fresh anonymous pull.
   Each app's release workflow publishes from `github.repository`, and those successful
   adopter-org publications exercised the required package-create capability.

   | App | Adopter-owned release and immutable app source | Served image digest |
   |---|---|---|
   | ledger | [v1.0.1](https://github.com/policy-as-versioned-tuppence/ledger/releases/tag/v1.0.1), [036bb972](https://github.com/policy-as-versioned-tuppence/ledger/tree/036bb972dd733eb12c00791415b145648d453e18) | `sha256:4c769ab891a1e1b19b4f5f6884cf9a6ac37ef1cbc0f4aaeae02fdd7c2004d4c5` |
   | storefront | [v1.0.1](https://github.com/policy-as-versioned-driftwood/storefront/releases/tag/v1.0.1), [a97344e4](https://github.com/policy-as-versioned-driftwood/storefront/tree/a97344e4ba767564192240278492456ef76b8b2d) | `sha256:6affc441f4181ec9e43976ab4115e8b239fe5a73ba30de8f61f5ff691de303d6` |
   | api | [v1.0.1](https://github.com/policy-as-versioned-driftwood/api/releases/tag/v1.0.1), signed tag `5881a81d0dbfd4835872a6d84bbe1de070763770` → [release target 63619ae0](https://github.com/policy-as-versioned-driftwood/api/tree/63619ae094c435f9eb3ffa5df0d567a067abeb5b); original register [lift-origin c1d92aa6](https://github.com/policy-as-versioned-driftwood/api/tree/c1d92aa61c21f0363da188dbd3b4f4c81f40cda2) is a distinct ancestor | `sha256:90ccb85d903b8137863695681c2cf6b8cb85ba59835be5e24857e72895b977a3` |
   | reports | [v1.0.1](https://github.com/policy-as-versioned-ludlow/reports/releases/tag/v1.0.1), [b809e063](https://github.com/policy-as-versioned-ludlow/reports/tree/b809e063514dedee5a1df8701d71d3a1856d5693) | `sha256:fa1b651ace9b00a636a4c0622fa9be63667fcdfe61a34e3ed8b618f07f0397e2` |

2. **Each app owns its Renovate preset.** The maintenance changes are reviewed and merged:
   [ledger #12](https://github.com/policy-as-versioned-tuppence/ledger/pull/12),
   [storefront #16](https://github.com/policy-as-versioned-driftwood/storefront/pull/16),
   [API #6](https://github.com/policy-as-versioned-driftwood/api/pull/6) and
   [reports #11](https://github.com/policy-as-versioned-ludlow/reports/pull/11). Their immutable
   configurations at [ledger d3255fa6](https://github.com/policy-as-versioned-tuppence/ledger/blob/d3255fa6fc0ccd25c84043f61b128b4d2e929ac0/renovate.json),
   [storefront deb25d34](https://github.com/policy-as-versioned-driftwood/storefront/blob/deb25d3467c9b7c59a83b39bbb8023c790fbad31/renovate.json),
   [api d9b5f4f9](https://github.com/policy-as-versioned-driftwood/api/blob/d9b5f4f922cb4ff4b30d75733d48975c86c6df61/renovate.json)
   and [reports f21bff06](https://github.com/policy-as-versioned-ludlow/reports/blob/f21bff06fac89401bf180ffc40dd46a37c36db51/renovate.json)
   each set `extends: ["config:recommended"]`, a dependency dashboard and no automerge.
   “Holds only `$schema`” in the Question describes the old deficiency; the fix gives each
   transferred repo its own preset rather than relying on the incumbent org's inheritance.

3. **Reviewed adopter delivery, including actual deletion and served pins.** Initial app graph
   PRs [Driftwood #53](https://github.com/policy-as-versioned-driftwood/driftwood/pull/53),
   [Tuppence #51](https://github.com/policy-as-versioned-tuppence/tuppence/pull/51) and
   [Ludlow #48](https://github.com/policy-as-versioned-ludlow/ludlow/pull/48) delivered the new
   target-org digest manifests. The later 2026-10-05 cleanup PRs
   [Driftwood #58](https://github.com/policy-as-versioned-driftwood/driftwood/pull/58),
   [Tuppence #58](https://github.com/policy-as-versioned-tuppence/tuppence/pull/58) and
   [Ludlow #55](https://github.com/policy-as-versioned-ludlow/ludlow/pull/55) removed the bundled
   `apps/<app>/` sources; the initial app graph PRs did not perform that later deletion.
   The actual normal cleanup merges are
   [DW bb699572](https://github.com/policy-as-versioned-driftwood/driftwood/commit/bb6995722a34eb09568a9ca043b9f64b4fcc1407),
   [TU e522c9c8](https://github.com/policy-as-versioned-tuppence/tuppence/commit/e522c9c876937b37810eba70d4a33ee5e72af891)
   and [LU 9f76b2af](https://github.com/policy-as-versioned-ludlow/ludlow/commit/9f76b2af169e76030538f0816db54e30f817b220).
   At public snapshots [DW 611c29e0](https://github.com/policy-as-versioned-driftwood/driftwood/tree/611c29e0b1f43f30ce1d564f302f4d8f7571d670),
   [TU ac948618](https://github.com/policy-as-versioned-tuppence/tuppence/tree/ac9486182ce7eac165366acf4a18a8a5542e5ee0)
   and [LU 5b22df85](https://github.com/policy-as-versioned-ludlow/ludlow/tree/5b22df857636660c5f31e39cbfe6cf5544c1ae4b),
   no tracked `apps/` sources remain and the adopters own the image-digest Renovate managers.
   The app GitRepositories actually pin signed `v4.0.0` trees:
   [DW 1cd446f6](https://github.com/policy-as-versioned-driftwood/driftwood/tree/1cd446f62a531c0aeee7e50c0a59a11ac5d00d67),
   [TU f575dc12](https://github.com/policy-as-versioned-tuppence/tuppence/tree/f575dc12de130c444d98a831de0ca21fd68b9c46)
   and [LU c5f33cc8](https://github.com/policy-as-versioned-ludlow/ludlow/tree/c5f33cc8982fc9bfeb7fcc2068ea8de0dda63dae).
   Those immutable served trees contain every app, including API; this is not a HEAD-only lift.

4. **API's policy claim, discovery and correction.** Driftwood's served API manifest carries
   `policy-as-versioned.dev/policy-version`, not `mycompany.com/policy-version`, and its image
   is the target-org digest above. Its own `served-workloads.py` discovers API beside
   `pod.yaml` and `storefront.yaml`, and the served composed routes admit and cage it at
   CREATE. The [dated API README correction](https://github.com/policy-as-versioned-driftwood/api/blob/d9b5f4f922cb4ff4b30d75733d48975c86c6df61/README.md#correction-2026-10-03-eco-system-ticket-154)
   explicitly records the 2026-09-25 eight HIGH CVEs in Go 1.26.5 on EOL Alpine 3.20.10.
   It qualifies “good citizen” without inventing a clean scan for the served image.

5. **The independent-source grader is registered and observes the delivered lift.** The
   [recorded TRUTH run 432 grade table](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/blob/d096cd2f0515a8aa2f9de1b671f5f227beba5478/talk/captures/_grades.tsv)
   gives `verify/lifted-apps/verify-lifted-apps.sh` PASS. Its
   [unchanged original capture](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/blob/d096cd2f0515a8aa2f9de1b671f5f227beba5478/talk/captures/verify_lifted-apps_verify-lifted-apps.out)
   retains fifteen structural failure plants, could-not-look controls and nine served-set
   failure plants, reads all four independent app repositories, discovers all four served
   workloads and verifies the actual composed routes at their pins. Both residual metrics
   are zero: **0 of 4 incumbent-org served images, with 0 unread pinned images**, and
   **0 of 4 lifts absent from the app-source pinned tree, with 0 unread pinned trees**.
   These observations, rather than an aggregate estate PASS, complete this ticket's check.

**Limits retained.** The capture does not observe whether the containers actually start; it
evaluates CREATE through the CLI, not UPDATE. Its anonymous-read evidence comes from the
separate clocks collector and the dated manifest receipt, not a new pull performed by this
offline grader. Public archived flags need no private credential; the collector uses its
credential for rate allowance. None of these limits is upgraded to a new observation here.
No fresh image, policy, inventory, acceptance, price or runtime change is made by this record
correction. Ticket 153's missing current NVD or dated EPSS instrument remains separate; its
status and recorded grades are unchanged.
