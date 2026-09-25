# 156 — The incumbent org register

Type: task (AFK)
Status: open
Blocked by: none

## Question

Build the archive half of [ADR-0036](../../../docs/adr/0036-the-incumbent-org-ends-app-repos-transfer-and-the-rest-are-archived.md) and the check that grades it.

1. **The register.** `verify/incumbent-org/register.yaml` holds one row per incumbent repo: its disposition (lifted, dropped, superseded or transferred), its reason, and the check whose PASS allows the action, or "none: the owner's authorisation alone".

   | repo | disposition | action allowed when |
   |---|---|---|
   | readiness-collector | dropped: readiness is answered by price, and the collector's counts are not lifted (ticket 13) | none. It is archived first, as the GHCR probe |
   | pr-gate-action | dropped: each adopter's `shift-left.yml` verifies the pin's trust chain, and no unit names the action | none |
   | renovate-config | dropped: it configures Renovate only inside the incumbent org | none |
   | handbook-generator | lifted as a compose-time render (ticket 34) | `verify/handbook` passes |
   | ledger, storefront, reports, api | transferred by ticket 154 | none: the owner's authorisation (ticket 35 round 2 Q9). The check confirms the new owner |
   | c2p-collector | dropped: platform owns the `result2oscal` glue (ADR-0009) | ticket 155's OSCAL check passes |
   | datastore, cloud | lifted (ticket 151) | ticket 151's check passes |
   | governance-agent | superseded by platform's wargamer | with fleet |
   | policy, fleet | superseded by platform and the adopter lanes | one adopter's `verify-reconcile.sh` passes, after ticket 152 |

2. **The check.** `verify/incumbent-org/verify-incumbent-org.sh` reads the register. The archived flags, the transferred repos' new owners and an anonymous GHCR pull of each served incumbent image are read in `truth.yml`'s `clocks` job with `github.token` and passed in, as `CLOCK_VERDICT` is. The unauthenticated API limit is 60 requests an hour per address, and hosted runners share addresses. It FAILs on a repo archived or transferred before its row passes. A row that passes and is not acted on yet is a counted LIMIT. A transferred repo passes when the API names its new owner as the adopter org.
3. **The archives.** Archive each repo with the owner's `gh` login when its row passes, as the owner authorised on 2026-09-25 (ticket 35 round 1 Q6). Record each archive in this ticket. After readiness-collector is archived, pull its image anonymously again. If that pull fails, no repo whose image is still served is archived until the image is built elsewhere.
4. **The records.** Give the notification spine's drop its corrections. In `docs/`: `PRD.md:110`, `:149`, `:188` and `:212`, `adr/0001-transport-signed-git-tags-gitsign.md:44` and `modern-reference-transport.md:73`. `references.md:48` keeps its link with a dated "not used" note. Give a dated note to the talk-spec's `spec.md`, `the-whole-model.md`, `issues/02-architecture-and-flux-role.md`, `issues/08-research-enforcement-engines.md` and `research/08-enforcement-engines.md`, and to hub research notes 20, 21 and 22. Correct `docs/shift-left-dev-workflow.md:11` and `docs/SHOW-AND-TELL.md:131`, which present pr-gate-action as live.

## Notes

Graduated 2026-09-25 from ticket 35, round 1 Q2, Q5 and Q6 with amendments A2 and A5. Definition of done includes wiring its check into `talk/verify-all.sh`.

Facts on 2026-09-25: the incumbent org held 16 repos, only `apps` archived. Eight repos held 42 open Renovate pull requests. fleet's `sunset escalator` ran daily and runs governance-agent's script. An unauthenticated `GET /repos/policy-as-versioned-flux/apps` returned `archived: true`. The GitHub documentation does not say whether a package stays pullable after its repo is archived. That is why the first archive is a probe.

**Condition sharpened, 2026-09-25.** The fleet, policy and governance-agent row needs a `verify-reconcile.sh` PASS on a sample taken under the re-registered fact 7 question. The grader skips facts 6 and 7 on a sample older than the current registration, so a pre-registration sample can print PASS on five facts with the cage not scored (reported by the session that grills ticket 152). Such a PASS does not meet the row.
