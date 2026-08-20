# 07 — Decide the split mechanics and how cross-org verification works

Type: grilling
Status: resolved
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

## Answer

Resolved by grilling, 2026-08-20. The refactor is far smaller than feared, and two README claims
turned out to be false.

**1. Verification: platform ships the harness as a pinned dependency; the hub runs the cross-cutting
beats.** Each repo consumes the verify tooling exactly as it consumes policy — a verify script that
drifts per repo is the same rot the version array exists to prevent. This is cheap: **only 4 scripts**
carry a single-tree assumption, `verify-all.sh` anchors on one line (`ROOT=dirname/../..`), and the
cross-cutting beats are nearly self-contained — `verify/proportionality/` carries its own copies of the
per-institution policies and scenarios and reaches into platform for exactly one path
(`$HERE/../../platform/risk`, the appetite bands), which becomes an ordinary pinned dependency.

**2. `verify/` and `talk/` become their own repos in the hub org** (`policy-as-versioned-flux`), not
directories inside the hub repo. They cannot live in `platform` — platform is a dependency
institutions *consume*, and a beat that reads three institutions' appetite bands would invert the
dependency direction platform is built on. The hub org is the thing that belongs to no single party,
which is what a cross-party comparison needs.

**3. Signing: dual-sign, time-boxed.** `GitRepository.spec.verify` only speaks OpenPGP — stated in
three places in the tree — so Flux **cannot verify** the estate's gitsign (keyless → Rekor)
signatures. Today that is masked because the source is an in-cluster git server seeded from the local
tree; after the split it would be six real remotes whose signatures the cluster never checks. So tags
are **dual-signed**: gitsign for the keyless/Rekor provenance story, OpenPGP so `spec.verify` actually
bites at the cluster. Keys are per-org, held as **GitHub Actions org secrets**, backed up to the
owner's 1Password vault.

**This is a bridge, not a design choice.** It exists only until Flux supports gitsign, which is on
their roadmap. The ticket that implements it must carry a **link to the upstream Flux issue** so
removal is triggerable rather than remembered, and mark the OpenPGP path in-repo as temporary —
otherwise the next reader will assume OpenPGP is the intended trust root.

**4. Regulator pins stay direct — and the README is wrong about this.** `estate/README.md:19` declares
`nist`/`ico` → `platform` → institutions. In fact **all three institutions pin `nist` directly** (each
has its own `gotk-sync-nist.yaml` and `nist-pin-configmap.yaml`), platform pins nist nowhere, and
**nobody pins `ico` as a GitRepository at all** — its penalty schema arrives by another route, with
`feeds/sign.sh` noting *"ico is a separate publishing org"* with its own key.

Direct is the right arrangement and is kept: a regulator's catalog is the *institution's* compliance
obligation, and routing it through platform would make platform a single point of failure for
regulatory currency — and able to withhold it. The cost is N reviewable PRs per regulator bump, which
is accepted. **The README must be corrected** rather than the edges changed; after the split it is a
claim about organisational structure, exactly the kind this effort exists to stop over-claiming.

**5. Surfaced, and beyond this ticket: an institution has *many* obligation sources.** Owner: platform
could publish **meta/curated packages** bundling upstreams and pinning versions; a consuming org may
be subject to **more than one regulator** (ICO/GDPR *and* PCI); and **customer SLAs load in the same
fashion**. The estate models one regulator catalog plus one penalty schema. Raised as its own ticket.
