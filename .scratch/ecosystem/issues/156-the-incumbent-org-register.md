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
