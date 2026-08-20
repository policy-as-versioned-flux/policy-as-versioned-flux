# 08 — Split the six units into their own GitHub org repos, history preserved

Type: task
Status: done
Blocked by: 07

## Question

Execute the split. `git filter-repo` per directory so history and attribution survive, into the six
orgs that already exist and are empty (`policy-as-versioned-{platform,driftwood,tuppence,ludlow,nist,ico}`,
created 2026-07-23, 0 repos each).

Note the history is shallow — `estate/` was largely built in one commit (`26770f8`, "Estate build: 27
tickets implemented via dependency-wave workflow") plus a handful of fixes — so this is cheap, but
preserving it matters for a project whose thesis is provenance.

Per repo: correct README (the current `estate/README.md` describes a monorepo working tree and must
not be copied verbatim into six repos), licence, and the vocabulary settled in ticket 03.

**Do not delete `estate/` from the hub in this ticket** — ticket 12 does that, after the Flux sources
are repointed and proven, so there is a working tree to fall back to if the split needs redoing.

## Comments

Done 2026-08-20. All six directories are now public repos in their matching orgs, history and
attribution preserved, `estate/` untouched in the hub.

For each of `platform`, `driftwood`, `tuppence`, `ludlow`, `nist`, `ico`: cloned the hub locally,
ran `git-filter-repo --path estate/<unit>/ --path-rename estate/<unit>/:` on the clone (never on the
hub itself), confirmed the resulting file tree matches `estate/<unit>/` 1:1 and every commit is still
attributed to `chris@cns.me.uk`, then pushed `main` to a freshly created, confirmed-empty repo named
`<unit>` in the matching `policy-as-versioned-<unit>` org (the name the org's own Flux `GitRepository`
manifests already declare, e.g. `gotk-sync.yaml`'s
`url: https://github.com/policy-as-versioned-driftwood/driftwood`). No tags existed on `estate/` yet,
so only `main` moved — dual-signing (ticket 07) is for the first real release, not this ticket.

Per repo, on top of the preserved history: a `README.md` update (each unit already had its own
non-monorepo README; added a header stating the GitHub org, the ticket-03 **Role**
(`platform` = publisher + risk-bearer — the reflexive £10k band in `risk/appetite.json`, org
`platform`, `root_of_trust: true`; the three institutions = risk-bearer + adopter; `nist`/`ico` =
regulator/publisher), and a link back to the hub for the full thesis; fixed the one cross-repo
relative link that broke — `driftwood/README.md`'s pointer into `platform/distribution/`); and a
`LICENSE` (Apache-2.0, matching the licence the estate already cites for harvested/adjacent work —
`collie`, `oscal-compass/compliance-to-policy-go`).

Every repo independently verified live from the GitHub API (not from the local scratch clones, which
are ephemeral) — public, `main` default, README present without the old monorepo framing and with a
Role line, LICENSE present, file tree matching `estate/<unit>/` 1:1 modulo the added README/LICENSE,
and commit authorship intact on both the oldest and newest commit. Script:
[`verify-08-filter-repo-split.sh`](../verify-08-filter-repo-split.sh).

**Not done, and correctly so per this ticket's own text:** `estate/` still exists in the hub (ticket
12's job); no tags/releases were cut (no dual-signing yet — first real release is a later ticket);
`verify/` and `talk/` were not split out (ticket 07 placed those in the hub org, not one of the six —
out of scope for "the six `estate/` directories" this ticket names); Flux `GitRepository` URLs were
not touched (ticket 09's job — they already declare the real org/repo names used here, which is why
no guessing was needed).
