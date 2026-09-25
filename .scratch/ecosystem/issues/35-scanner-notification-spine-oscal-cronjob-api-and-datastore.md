# 35 — scanner, notification spine, OSCAL CronJob, api and datastore

Type: grilling (HITL)
Status: claimed
Blocked by: 16, 21, 33

## Question

Lift or retire trivy-operator, the Flux Alert/Provider/Receiver spine and the OSCAL CronJob on the adopter cluster; place api and datastore; sequence per-repo archiving.

## Notes

Graduated 2026-08-28 from ticket 13's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.

## Facts found (2026-09-25, before round 1)

- Blockers 16, 21 and 33 are `resolved`, read from each file's `Status:` line. The whole ticket is on the frontier.
- The incumbent org has 16 repos. Only `apps` is archived. The 14 live repos other than the hub are api, c2p-collector, cloud, datastore, fleet, governance-agent, handbook-generator, ledger, policy, pr-gate-action, readiness-collector, renovate-config, reports and storefront. [`gh repo list policy-as-versioned-flux --json name,isArchived,pushedAt`]
- fleet's `sunset escalator` still runs every day. The newest run was 2026-09-25T13:15Z, `success`. The `weekly governance nag` ran 2026-09-21. Eight incumbent repos hold 39 open pull requests between them. [`gh run list -R policy-as-versioned-flux/fleet`; `gh pr list` per repo]
- The drift lane recorded facts 1 to 6 `true` in all three adopters on 2026-09-25: driftwood 11:54Z, tuppence 13:57Z, ludlow 14:36Z. Fact 7 is `null` in all three. So each adopter's composed fan-out reconciles from signed sources. That is the condition ticket 13 item 2 set for fleet. [`drift/samples.jsonl` at each adopter's `origin/main`, last line]
- The drift lane does not run the lifted apps. `drift-sample.yml` names no file under `gitops/apps`. Each adopter's `gotk-sync.yaml` still pins its own `v1.0.0`, whose tree does not list the lifted workload. tuppence's `v2.0.0` tree does list `gitops/apps/ledger.yaml`. [`git show origin/main:gitops/flux-system/gotk-sync.yaml`; `git ls-tree v2.0.0`]
- The three served manifests pin images that the incumbent org published: `ghcr.io/policy-as-versioned-flux/{ledger,storefront,reports}@sha256:…`. Each incumbent `release.yml` publishes to `ghcr.io/${{ github.repository }}`.
- The cve converter prices one entry per feed, the headline. Its own docstring says composition "has no cve id or component of its own to name". So every subscriber pays the same CVE price, whatever it runs. [`platform/feeds/to_fair_scenario.py:27-35`]
- The CVE feed is illustrative. Its entries carry ids such as `CVE-2024-1234-envoy` and the source line "illustrative, shape-accurate". `feeds/fetch/cve.py` reads a committed fixture. Its written upgrade path is "`trivy image --format json` over the estate's running images, joined to the FIRST EPSS daily CSV". [`feeds/cve/v2/feed.json`; `feeds/fetch/cve.py:7-10`]
- The CISA Known Exploited Vulnerabilities catalogue held 1,725 entries at `catalogVersion` 2026.09.25, 1.75 MB of JSON. It lists CVE-2021-44228, "Apache Log4j2 Remote Code Execution Vulnerability". The FIRST EPSS API gives CVE-2021-44228 an `epss` of 0.99999 on 2026-09-25. [`curl https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json`; `curl https://api.first.org/data/v1/epss?cve=CVE-2021-44228`]
- OSCAL runs only offline. `platform/oscal/result2oscal.py` reads three hand-written PolicyReports in `fixtures/policyreports.yaml`. No adopter file names OSCAL. Each adopter's composed set serves 4 ValidatingPolicy, 6 MutatingPolicy, 2 GeneratingPolicy and 5 PriorityClass documents.
- No Flux `Alert`, `Provider` or `Receiver` exists in any unit. The claims that name the notification spine are `docs/PRD.md:110`, `docs/PRD.md:149`, `docs/adr/0001-transport-signed-git-tags-gitsign.md:44`, `docs/modern-reference-transport.md:73`, `.scratch/talk-spec/spec.md:181-184` and `.scratch/talk-spec/research/08-enforcement-engines.md:192`.
- The cloud plane has no build ticket. ADR-0004's sequencing note says ticket 13 files a Crossplane item on ticket 09. Ticket 09 has no such item.
- Ticket 33 says "reading the archived flag needs a credential the gate does not hold". That is false. An unauthenticated `GET https://api.github.com/repos/policy-as-versioned-flux/apps` returns `archived: true`.
- The GitHub archive documentation does not say whether a GHCR package stays pullable after its repo is archived. Anonymous `tags/list` on `ghcr.io/policy-as-versioned-flux/ledger` and `/readiness-collector` returned HTTP 200 on 2026-09-25, before any archive.
- The incumbent `governance-agent` was lifted as platform's `wargamer/` (`wargamer/README.md:1`). The handbook generator's `verify.sh` was retired by ticket 34 (`platform/compose/README.md:400`).
- The owner's words on app repos, 2026-07-16: "we should consider seperating these to one repo/app rather than a monorepo". Ticket 33 lifted each app into its adopter's own repo, under `apps/<app>/`. [`.scratch/drift-review-2026-08-27/evidence/DECISION_AUDIT.json` P169]

## Grilling round 1 (put 2026-09-25, answered 2026-09-25)

The owner answered the whole round with one word: "agree". Under ADR-0025 point 3, Q1 to Q5 and Q7 are **delegated**: the assistant's decisions, with the assistant's reasons. Q6 is an authorisation, which only the owner can give. The owner was asked "give your answer to Q6", with option (a) stated in full. The answer "agree" is recorded as the owner's authorisation of Q6 (a), within the bound that (a) states. It was the fourth owner decision of 2026-09-25 across sessions 30, 71 and 35.

1. **Q1, the vulnerability scanner. Delegated.** Drop trivy-operator. Lift the scan. A scheduled job in each adopter runs `trivy image` on the digests that its served manifests pin. The job writes an image inventory to an observation branch, and opens a pull request when the inventory changes. Composition prices the CVE feed entries that the inventory names. Reason: a scan result changes a price, and an **Observation** never changes priced evidence. So the inventory is a **Declaration** and reaches main only by a reviewed pull request. The scan needs no cluster, and each org verifies itself (re-grill 4). A publisher-side scan makes the feeds org depend on its subscribers. trivy-operator gives continuous scans on a cluster that lives for one run, with five known KinD quirks.
2. **Q2, the Flux notification spine. Delegated.** Drop it. Correct the four live claims in `docs/`, and put a dated note on the two superseded talk-spec files. Reason: fact 3 already records the applied revision, and facts 4 and 5 are stricter. A commit status would be a second, weaker report of the same fact. A Receiver cannot reach an ephemeral cluster. The eco-system broadcasts a new version as a Renovate pull request in each adopter.
3. **Q3, OSCAL collection. Delegated.** A step in each adopter's drift lane, after the facts, reads the PolicyReports on the lane cluster. It runs `result2oscal.py` from the platform tag the lane pins. It appends the assessment-results next to the sample, as an observation. There is no CronJob, because the cluster lives for one run. The `c2p-collector` image is dropped, because platform owns the glue (ADR-0009). Limit: the document names only the pods the lane runs. Today these are the two cage probe pods.
4. **Q4, the cloud plane. Delegated.** Graduate one build ticket, number 151, when this ticket resolves. It carries the datastore claims, the RDS and S3 policies as platform members (ADR-0017), the dials for a Crossplane CR, and an admission check. It stays blocked until all seven `verify/e2e/verify-e2e-step*.sh` scripts pass on one citable truth run. Reason: a sequencing rule with no ticket is a deferral in practice, and the seven steps make the trigger a grade.
5. **Q5, the archive register and order. Delegated.** One register row per incumbent repo, with its disposition and the check whose PASS lets it be archived:

   | repo | disposition | archive when |
   |---|---|---|
   | readiness-collector | dropped (ticket 13) | now. It is the first archive and the GHCR probe |
   | pr-gate-action | dropped. The adopter gate replaces it | now |
   | renovate-config | dropped. No eco-system repo extends it | now |
   | handbook-generator | lifted (ticket 34) | `verify/handbook` passes |
   | governance-agent | lifted as platform's wargamer. Its escalator was dropped by D5 | `verify-wargamer.sh` and `verify/supersede` pass |
   | ledger, storefront, reports | lifted (ticket 33) | `verify/lifted-apps` passes and the GHCR probe passes |
   | c2p-collector | dropped by Q3 | the lane's OSCAL check passes |
   | api | round 2 | its lift or drop is graded |
   | datastore, cloud | ticket 151 | ticket 151's check passes |
   | policy, fleet | superseded by platform and the adopter lanes | last, together |

   The probe: after readiness-collector is archived, pull its image anonymously again. If the pull fails, the three app repos wait until their image builds move. A hub check, `verify/incumbent-org/`, reads the register and the unauthenticated archived flag. It FAILS when a repo is archived before its condition holds. A repo whose condition holds and that is not archived yet is a counted LIMIT, not a FAIL. Ticket 33's credential claim gets a dated correction.
6. **Q6, archiving. Owner-authorised, 2026-09-25, "agree" to option (a).** The assistant archives each incumbent repo with the owner's `gh` login, only when that repo's register row passes, and records each archive in this ticket. An archive can be reversed.
7. **Q7, the glossary. Delegated.** `CONTEXT.md`'s posture line "Sunset = scheduled proposal" gets a dated pointer to **Supersede**. **Incumbent org** and **Drop** become terms. "Retire" keeps one meaning: a policy version leaves the array. In new text a mechanism is lifted or dropped. Old tickets stay as the record.

## Comments

**2026-09-02, review.** Ordering from the review: composition prices exactly two feed names and reads no workload, image, SBOM or dependency, so lifting the apps (ticket 33) cannot make a feed re-price anything until the cve and eol converters exist. Ticket 84 item 1 carries the converters. Put 84 before or with 33, and restate 33's definition of done as a price check. Record: REVIEW-2026-09-02.md, legacy/L1 (refuted as stated, ordering survives).
