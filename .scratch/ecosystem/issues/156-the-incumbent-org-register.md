# 156 — The incumbent org register

Type: task (AFK)
Status: claimed
Blocked by: none

## Question

Build the archive half of [ADR-0036](../../../docs/adr/0036-the-incumbent-org-shrinks-to-the-hub-app-repos-transfer-and-the-rest-are-archived.md) and the check that grades it.

1. **The register.** `verify/incumbent-org/register.yaml` holds one row per incumbent repo: its disposition (lifted, dropped or transferred), its reason, and the check whose PASS allows the action, or "none: the owner's authorisation alone".

   | repo | disposition | action allowed when |
   |---|---|---|
   | readiness-collector | dropped: readiness is answered by price, and the collector's counts are not lifted (ticket 13) | none. It is archived first, and its image is pulled again afterwards to record what GitHub does |
   | pr-gate-action | dropped: each adopter's `shift-left.yml` verifies the pin's trust chain, and no unit names the action | none |
   | renovate-config | dropped: it configures Renovate only inside the incumbent org | none |
   | handbook-generator | lifted as a compose-time render (ticket 34) | `verify/handbook` passes |
   | ledger, storefront, reports, api | transferred by ticket 154 | none: the owner's authorisation (ticket 35 round 2 Q9). The check confirms the new owner |
   | c2p-collector | dropped: platform owns the `result2oscal` glue (ADR-0009) | ticket 155's OSCAL check passes |
   | datastore, cloud | lifted (ticket 151) | ticket 151's check passes |
   | governance-agent | dropped: platform's wargamer replaces it | with fleet |
   | policy, fleet | dropped: platform and the adopters' lanes replace them | one adopter's `verify-reconcile.sh` passes, after ticket 161 |

2. **The check.** `verify/incumbent-org/verify-incumbent-org.sh` reads the register. The archived flags, the transferred repos' new owners and an anonymous GHCR pull of each served incumbent image are read in `truth.yml`'s `clocks` job with `github.token` and passed in, as `CLOCK_VERDICT` is. The unauthenticated API limit is 60 requests an hour per address, and hosted runners share addresses. It FAILs on a repo archived or transferred before its row passes. A row that passes and is not acted on yet is a counted LIMIT. A transferred repo passes when the API names its new owner as the adopter org.
3. **The archives.** Archive each repo with the owner's `gh` login when its row passes, as the owner authorised on 2026-09-25 (ticket 35 round 1 Q6). Record each archive in this ticket. This ticket is the archive log that ticket 35 round 1 Q6 refers to. After readiness-collector is archived, pull its image anonymously again and record the result. After ticket 154, no archived repo has an image the estate serves (ADR-0036 decision 3).
4. **The records.** Give the notification spine's drop its corrections. In `docs/`: `PRD.md:110`, `:149`, `:188` and `:212`, and `modern-reference-transport.md:73`. ADR-0001 is accepted, so line 44 gets a dated note, not an edit. `references.md:48` keeps its link with a dated "not used" note. Give a dated note to the talk-spec's `spec.md`, `the-whole-model.md`, `issues/02-architecture-and-flux-role.md`, `issues/08-research-enforcement-engines.md` and `research/08-enforcement-engines.md`, and to hub research notes 15, 20, 21 and 22 (15:129 and :311 call commit status the compliance pillar's killer feature). Correct `docs/shift-left-dev-workflow.md:11` and `docs/SHOW-AND-TELL.md:131`, which present pr-gate-action as live.

## Notes

Graduated 2026-09-25 from ticket 35, round 1 Q2, Q5 and Q6 with amendments A2 and A5. Definition of done includes wiring its check into `talk/verify-all.sh`.

Facts on 2026-09-25: the incumbent org held 16 repos, only `apps` archived. Eight repos held 42 open Renovate pull requests. fleet's `sunset escalator` ran daily and runs governance-agent's script. An unauthenticated `GET /repos/policy-as-versioned-flux/apps` returned `archived: true`. The GitHub documentation does not say whether a package stays pullable after its repo is archived. That is why the first archive is a probe.

**Condition sharpened, 2026-09-25.** The fleet, policy and governance-agent row needs a `verify-reconcile.sh` PASS on a sample taken under the re-registered fact 7 question. The grader skips facts 6 and 7 on a sample older than the current registration, so a pre-registration sample can print PASS on five facts with the cage not scored (reported by the session that grills ticket 152). Such a PASS does not meet the row.

## Implementation, 2026-10-03

Claimed by Codex while resuming Claude's handoff. The sixteen-row register and named check are implemented. The credentialled clocks job collects forge ownership and archive flags, and anonymous OCI manifest observations for the images at each adopter's apps-source tag plus the permanent readiness-collector probe. The grading job receives that file without a credential. Missing or duplicate image observations cannot establish a pass; an unacted eligible row is a LIMIT. The final three archives require a reconcile PASS under the reference-workload registration, not a pre-registration five-fact PASS.

The collected pre-action facts are recorded in `research/resume-2026-10-03/incumbent-facts.json`: all four app repositories have the adopter owners; the three unconditional drops are eligible and still live; all served incumbent image manifests and the readiness-collector probe were readable anonymously. The selfcheck plants premature archives, wrong owners, an archived hub, failed and missing anonymous pulls. It passes; the typecheck passes. No archive is claimed here until its action and post-action observation are recorded below.

The notification spine and pr-gate corrections are in the named current documents, with dated notes in the accepted ADR and historical research and talk records. Resolution still requires the archive log and a citable truth run.

## Archive log, 2026-10-04

The owner explicitly approved the three named unconditional drops after automatic approval review required specific authorization. `readiness-collector` was archived first at 09:36 UTC. Its permanent `v1.0.0` image was read anonymously immediately afterward: HTTP 200, digest `sha256:8c5d78146351822a31935cf5e7cfc54bb855d7a1300bdb56ff0311b9d84786cd`, unchanged from the pre-action observation. `pr-gate-action` and `renovate-config` were then archived. The actual forge responses confirm all three flags. No other repository was archived in this action.

The dated receipts, explicit approval scope, original automatic-review rejection, and pre/post probe are in `research/resume-2026-10-04/incumbent-unconditional-archives-complete.json` and its linked files. The current forge check also confirms all four application repositories have their adopter owners and the hub remains live. Conditional rows still require their own genuine current passing checks; the final fleet/policy/governance-agent group still requires the re-registered cage sample. This entry does not claim those archives or resolve the whole ticket.

## Archive log — handbook-generator, 2026-10-17; recorded 2026-10-21

[`policy-as-versioned-flux/handbook-generator`](https://github.com/policy-as-versioned-flux/handbook-generator) was archived after its genuine fresh handbook/register prerequisite passed over six served refs across three adopters. The saved post-action forge response reports `archived: true`, `updated_at: 2026-10-17T00:35:15Z`; the actual verification receipt is dated `2026-10-17T00:35:16.829394+00:00`. It confirms no estate image is served by that archived repository and its source is unchanged. Retained receipt paths, relative to the workspace root, are `.scratch/ecosystem/research/resume-2026-10-17/handbook-archive/verified-outcome.json`, `.scratch/ecosystem/research/resume-2026-10-17/handbook-archive/repository-after.json` and `.scratch/ecosystem/research/resume-2026-10-17/handbook-archive/register-after.log`. The anonymous OCI read in that shared receipt is the separate readiness-collector `v1.0.0` permanent probe. This entry records the saved October 17 action and prerequisite results; it performs no new archive or measurement.

Recorded TRUTH 438's existing incumbent-register capture also reports handbook-generator archived/PASS. Ticket 156 remains claimed: c2p-collector still waits for the OSCAL check and datastore/cloud for cloud admission; fleet, policy and governance-agent are eligible but unacted LIMITs and remain last, together, under ADR-0036 decision 4 and their recorded prerequisites. All existing archive history and pending rows remain. This append supplies no new current renderer-health, forge/runtime result or whole-ticket completion claim.

**2026-10-22: grade observable contradictions in the archive sequence.** The register grader now enforces ADR-0036 decisions 3 and 4 across rows: an observed live readiness-collector alongside a newly archived dropped/lifted repository fails “readiness first”; an observed archived fleet, policy or governance-agent member alongside an observed live member fails “together”; any observed archived final member while an earlier dropped/lifted repository remains live fails “last”. The already archived pre-migration `apps` repository is excluded from “readiness first”; the retained hub and transferred applications are not archive requirements. Missing or failed forge observations retain their unknown/SKIP behavior, and eligible but unacted rows retain their LIMITs. Current flags cannot prove the historical order of completed actions or make three archive writes atomic; the operator still owns the ordered, grouped procedure.

The first, last and partial-final contradictions returned success before their respective guards were added. Permanent offline tests failed before each repair; all 39 focused tests, the named offline selfcheck and targeted two-file type checking pass locally. The original and corrected graders produce byte-identical output and status for the unchanged saved run 441 forge facts and grade table with each cage-prerequisite value. This is a saved-input source comparison, not a new cage proof or recorded TRUTH result. No repository was archived, no prerequisite was granted, and ticket 156 remains claimed with its existing pending archives and completion conditions.


**Archive log, 2026-10-22: datastore and cloud.** Citable TRUTH450's native cloud-admission
PASS satisfies ticket151's prerequisite, and its original incumbent-register capture reports
both rows as eligible unacted LIMITs. The unchanged signed original
`cdf629a9ddbb0ec6f785c5b5b13547bcd9b61962` was normally recorded by PR246 as hub main
`70431b9059bfc411fff8a1f0dc6edb3ca088068c` before either archive. The owner authorised eligible
archives under ADR-0036; the authenticated owner login was `chrisns`. Immediately before each
write, the operator checked the citable prerequisite, current public refs and full source tree,
fresh complete forge facts and the applicable anonymous image pull. Each API write set only
`archived: true`; it did not edit source, refs, branches or workflows.

| repository | actual archive request started (UTC) | post-action verification completed (UTC) | unchanged main |
|---|---|---|---|
| `policy-as-versioned-flux/datastore` | 2026-10-22T23:31:09.855415Z | 2026-10-22T23:31:23.565372Z | `988e414eb01c7f768bdd9fc75a0d7e068745a9b3` |
| `policy-as-versioned-flux/cloud` | 2026-10-22T23:31:25.807923Z | 2026-10-22T23:31:39.523086Z | `30060d27a56e659fc0568734ff9a63ba5c211188` |

Both immediate post-action GETs report archived, both registered rows pass, and all public refs
and complete source trees match the pre-action snapshots. The subsequent independent canonical
clone/API audit, observed at 2026-10-22T23:35:16.656658Z, additionally conserves both complete raw
commit histories: two refs, two commits and all ten source blobs, 7,217,462 bytes. All other
14 forge records are unchanged. Its fresh registered check exits0, with13PASS/4LIMIT, using the
same citable prerequisite grades. No applicable incumbent estate image is served from either
newly archived repository. The permanent readiness probe remains anonymous HTTP200, digest
`sha256:8c5d78146351822a31935cf5e7cfc54bb855d7a1300bdb56ff0311b9d84786cd`.

Retained receipts, relative to the workspace root:
`.scratch/ecosystem/research/resume-active-20261022T2203/datastore-cloud-actual-archives/COMPLETE.json`
and `.scratch/ecosystem/research/resume-active-20261022T2203/datastore-cloud-public-conservation/PROOF.json`,
each with its adjacent manifest. An earlier read-only preflight stopped on differing ref-listing
formats before any archive write; its original packet and exact-format correction are retained.
The corrected complete ref maps match before and after the actual actions.

These are bounded post-action forge/registry measurements, **not a new TRUTH run**. Original450
and its115PASS/3FAIL/23SKIP/8EXCLUDED vector and eligible-LIMIT capture remain unchanged. Ticket156
stays claimed: c2p-collector still needs its workload-OSCAL prerequisite; governance-agent, policy
and fleet remain live and must be archived last, together, after the earlier rows and their
recorded prerequisites pass. No remaining archive or whole-ticket completion is claimed.


**2026-10-25: final four eligible archives performed and post-verified.** Original scheduled TRUTH 461 (`40183546501`, attempt 1), normally recorded by [PR 267](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/pull/267) at `646416d3f336c167c9c8c166bccf14c08f52aa3f`, explicitly passes the OSCAL prerequisite and all three reconcile checks. Those reconcile captures score facts 6 and 7 under the current reference registration; this is not the earlier five-fact shortcut. The overall primary remains failed on its other recorded rows.

Under the owner's standing authorization, `c2p-collector` was archived first at 19:44 UTC and its postchecks passed. The final logical group followed at 19:45 UTC in the order `fleet`, `policy`, `governance-agent`, stopping the daily caller first. The three archive requests are separate, non-atomic GitHub writes; their retained responses span approximately three seconds. No intermediate partial group is claimed as a register pass.

All four post-action forge flags are archived. The operational register reports 17 PASS, zero LIMIT/FAIL/SKIP over all 16 registered repository rows and the permanent readiness probe. All four source trees, complete public ref maps and 965 reachable commit/tag/tree/blob contents are unchanged. Current served tags name no incumbent target image; five anonymous OCI manifest reads retain HTTP 200 and their exact digests, including the readiness probe `sha256:8c5d78146351822a31935cf5e7cfc54bb855d7a1300bdb56ff0311b9d84786cd`. These are manifest observations, not downloaded-layer or new runtime proofs.

The exact per-action times, unchanged main/tree identities and receipt-manifest digest are in [`incumbent-final-archives.json`](../research/resume-20261025/incumbent-final-archives.json). All archive actions are now performed and operationally verified. The next unforced primary must record the completed flags before the ticket claims a new signed TRUTH result; the existing 461 grades and all original failures remain unchanged. No whole-ecosystem completion is claimed here.
