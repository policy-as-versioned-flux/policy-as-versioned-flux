# The signpost for the legacy org (eco-system ticket 80 item 9) — NOT APPLIED

Written 2026-09-06. **Nothing in this file has been applied to any repository.** It is the
material for an enactment the build brief does not authorise, held here so applying it is one
pass rather than a re-derivation. See ticket 80's `## Waits on the owner`.

## Why it was not applied

- **The push list.** The build brief of 2026-09-03 (amended 2026-09-05) names what may be
  pushed: the hub, and the eight enactment repos of the eco-system (`-platform`, `-driftwood`,
  `-tuppence`, `-ludlow`, `-nist`, `-ico`, `-feeds`, `-insurer`). The `policy-as-versioned-flux`
  organisation's other repositories are not on that list. "Development mode" widened who may push
  the eight; it did not widen the eight. Ticket 80 item 9 does name these fourteen, so the ground
  is not that nobody named them -- it is that naming a repository in a ticket is not the same act
  as authorising a write to it, which is exactly what ADR-0025 point 6 reserves to the owner
  (authorisations).
- **The org description needs `admin:org`.** Measured 2026-09-06: `gh auth status` reports scopes
  `delete_repo, gist, read:org, repo, workflow`. There is no scope here that can set it, so this
  half cannot be done by any agent holding this token, whatever the authorisation.
- `gh api orgs/policy-as-versioned-flux` returns `"description": null` on 2026-09-06, so the
  finding is confirmed: the org names neither implementation.

## What is there, measured 2026-09-06

`gh repo list policy-as-versioned-flux` returns **16** repositories. One is the eco-system hub
itself (`policy-as-versioned-flux/policy-as-versioned-flux`), which needs no signpost because it
IS the signpost. That leaves **15**, of which **`apps` is archived** and cannot take a commit
until somebody unarchives it — which is why the ticket says fourteen. The fourteen writable ones:

    api                  fleet                policy               renovate-config
    c2p-collector        governance-agent     pr-gate-action       reports
    cloud                handbook-generator   readiness-collector  storefront
    datastore            ledger

Archived, needs unarchiving first: `apps`.

## The banner, to go at the top of each README, under the title

> **Superseded reference implementation, 2026-09-06.** This repository is part of the *first*
> Policy as Versioned Code reference implementation, built to 2026-07-20 and research-only since.
> It is kept as the record and is not maintained. The current implementation is an eco-system of
> nine independent GitHub organisations exchanging signed, versioned dependencies — a platform,
> two regulators, three regulated institutions, a feeds publisher and an insurer — and its hub,
> thesis, decision record and truth surface are at
> [policy-as-versioned-flux/policy-as-versioned-flux](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux).
> Where the two disagree, the eco-system is the current design; this repository is what was built
> first and what the drift review of 2026-08-27 measured it against.

## The org description

> Superseded: the first Policy as Versioned Code reference implementation (to 2026-07-20). The
> current one is nine orgs; start at policy-as-versioned-flux.

**153 characters**, counted 2026-09-06, against GitHub's 160-character limit on an organisation
description. The first draft of this file offered a 198-character sentence and called it 240; both
numbers were wrong and neither would have been accepted. Corrected under ticket 80's own review.

## The sharper question for the owner: a banner, or a proposal?

Two shapes, and they are not the same ask.

- **Direct commits to fourteen default branches.** One pass, fourteen repositories changed, no
  review anywhere. It is the cheapest and it is the least like anything else this estate does:
  the reviewed PR is the unit of adoption (NORTH-STAR principle 5), and fourteen unreviewed
  pushes to make a point about honesty sits badly.
- **Fourteen pull requests, none merged.** The same material, proposed and not enacted, disposed
  of by the owner one at a time or in a batch. It costs fourteen PRs of noise in an archive-shaped
  organisation, and it leaves the signpost absent until somebody merges them.

Recorded, not decided: this is an authorisation, so it is the owner's under ADR-0025 point 6. The
assistant's view, if it helps: **proposals**, because these repositories are the record of what
was built first and a reviewed change is how this estate touches a record. The `apps` repository
is archived and takes neither shape until it is unarchived.
