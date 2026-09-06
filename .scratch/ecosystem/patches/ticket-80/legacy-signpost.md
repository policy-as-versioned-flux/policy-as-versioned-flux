# The signpost for the legacy org (eco-system ticket 80 item 9) — NOT APPLIED

Written 2026-09-06. **Nothing in this file has been applied to any repository.** It is the
material for an enactment the build brief does not authorise, held here so applying it is one
pass rather than a re-derivation. See ticket 80's `## Waits on the owner`.

## Why it was not applied

- The build brief of 2026-09-03 (amended 2026-09-05) authorises pushes to the hub and to the
  eight enactment repos of the eco-system. The `policy-as-versioned-flux` organisation's other
  repositories are not among them, and "development mode" is a statement about the eco-system's
  own units, not a licence to write to fifteen repositories nobody named.
- The org description needs `admin:org`. Measured 2026-09-06: `gh auth status` reports scopes
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

> The first Policy as Versioned Code reference implementation (to 2026-07-20, research-only). The
> current one is an eco-system of nine orgs; start at policy-as-versioned-flux/policy-as-versioned-flux.

240 characters. GitHub's org description limit is generous; if it refuses, cut the parenthesis.
