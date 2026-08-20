# 07 — Decide the split mechanics and how cross-org verification works

Type: grilling
Status: open
Blocked by: 03

## Question

The split is decided in principle: `git filter-repo` per directory preserving history, six real
GitHub orgs, hub **loses** `estate/` (the six repos become the source of truth, not a mirror).
Internet is assumed — the offline guarantee is a declared false constraint and is being removed.

What is **not** decided is how the estate keeps working once it is six checkouts:

- **Cross-org verification.** `estate/talk/verify-all.sh` and the per-area scripts currently assume a
  single tree with relative paths (`$ROOT/estate/platform/...`). Does the hub keep a
  `clone-estate.sh` that assembles a working set? Does verify-all run from the hub against six
  sibling checkouts, or does each repo verify itself and the hub only aggregates? What happens to
  `estate/verify/` (proportionality, provenance) which is inherently cross-institution?
- **Where the cross-cutting dirs go.** `verify/` and `talk/` are explicitly "not repos" today.
- **Dependency direction on the wire.** `nist`/`ico` → `platform` → institutions is currently
  directory references; after the split each hop is a real signed tag + commit pin. Which repo pins
  which, at what granularity.
- **Release identity.** Six orgs, one human owner. Does each org tag its own signed releases, and
  what identity signs them.

Resolve enough to make tickets 08–12 executable without guessing.
