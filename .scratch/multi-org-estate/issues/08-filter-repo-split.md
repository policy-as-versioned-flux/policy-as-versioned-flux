# 08 — Split the six units into their own GitHub org repos, history preserved

Type: task
Status: open
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
