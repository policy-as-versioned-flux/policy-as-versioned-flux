---
status: accepted
---

# The incumbent org ends: app repos transfer, and the rest are archived

Decided 2026-09-25. The architecture is the assistant's, under
[ADR-0025](0025-the-assistant-decides-architecture-and-records-it.md), labelled delegated. The two
actions on GitHub are the owner's authorisations, given on 2026-09-25 with the word "agree" to a
stated option: archive each repo when its register row passes (round 1 Q6), and transfer four app
repos and make their new packages public (round 2 Q9). Record:
[eco-system ticket 35](../../.scratch/ecosystem/issues/35-scanner-notification-spine-oscal-cronjob-api-and-datastore.md).
Built by eco-system tickets 154 and 156. It makes eco-system ticket 13 item 2 concrete. It
supersedes nothing.

## Context

The **incumbent org** `policy-as-versioned-flux` holds 16 repos. On 2026-09-25 only `apps` was
archived. Its clocks still ran: fleet's `sunset escalator` every day, and a weekly governance nag in
fleet and in policy. Renovate held 42 open pull requests across eight of its repos. Ticket 13 item 2
decided that each repo is archived after its replacement grades green, with fleet last. Nothing
graded that rule.

Ticket 33 lifted ledger, storefront and reports into their adopters' own repos, under
`apps/<app>/`. The image builds stayed in the incumbent org. So a dependency bump in an adopter
changed no served image and moved no price. On 2026-07-16 the owner wrote: "we should consider
seperating these to one repo/app rather than a monorepo".

## Decision

1. **Each app repo is transferred into its adopter's org.** ledger goes to tuppence, storefront and
   api to driftwood, and reports to ludlow. The history, the open pull requests and `release.yml`
   go with each repo. `release.yml` publishes to `ghcr.io/${{ github.repository }}`, so the next tag
   builds under the adopter org. Each new package is made public after its first publish. The
   adopter repo drops `apps/<app>/` and keeps its served manifest, re-pointed by a reviewed pull
   request. A digest manager is added to the adopter's Renovate config.
2. **Every other repo is archived when its register row passes.** A register in the hub names each
   repo, whether it is lifted, dropped or transferred, and the check whose PASS allows the action.
   `verify/incumbent-org/` grades the register. The archived flags and an anonymous GHCR pull are
   read in `truth.yml`'s `clocks` job and passed in, as `CLOCK_VERDICT` is. A repo archived before
   its row passes is a FAIL. A row that passes and is not acted on yet is a counted LIMIT.
3. **The first archive is a probe.** readiness-collector is archived first. Then its image is pulled
   anonymously again. If the pull fails, no repo whose image is still served is archived until that
   image is built somewhere else.
4. **fleet, policy and governance-agent go last, together.** fleet's escalator runs
   governance-agent's script every day. Their row waits for one adopter's `verify-reconcile.sh` to
   pass. That waits for fact 7 to be re-registered (eco-system ticket 152).
5. **Only the hub stays live.**

## Considered options

- **Keep each app's source in its adopter repo and add a build job there.** This works, because the
  merging app holds `workflows:write` in the adopter orgs. It was not chosen. The adopter repo stays
  a monorepo, and the incumbent history does not move with the code.
- **Create new app repos from the adopter's `apps/<app>/` and archive the incumbent app repos.** Not
  chosen. It gives one repo per app but loses the incumbent history and its open pull requests.
- **Keep the incumbent org live as a fourth adopter.** Rejected by ticket 13 item 2. It is the
  shim for software you do not control (GAPS 3.14), which has no build.

## Consequences

- The four old packages stay in the incumbent org. GitHub keeps a container package with its old
  account when the repo moves. The served manifests point at them until the reviewed re-point.
- The Mend Renovate app is installed on all repos in each adopter org. So a transferred repo keeps
  Renovate with no new setup.
- `verify/lifted-apps` must read the app repo instead of `apps/<app>/`. Its planted failures stay.
- A transferred repo leaves the incumbent org. The glossary's **Incumbent org** entry says so.
