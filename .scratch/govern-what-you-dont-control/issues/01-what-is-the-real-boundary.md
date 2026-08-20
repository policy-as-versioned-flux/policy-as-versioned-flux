# 01 — Is "COTS" the boundary, or is it "can we change the pod spec"?

Type: grilling
Status: open
Blocked by: none

## Question

The population was named as "COTS products", but the estate's mechanism doesn't care about
commercial provenance — it cares whether a `policy-as-versioned.dev/policy-version` label can be put
on a pod. Those are different sets, and the difference decides how big this effort is.

Candidates for the real axis:

- **Commercial provenance** — bought, not built. Narrow, but misses in-house workloads nobody owns
  any more.
- **Can we change the pod spec?** Catches COTS *and* vendored Helm charts, operator-managed
  workloads (the operator rewrites the spec), CRD-driven pods, and anything where a controller owns
  the template. Probably the honest boundary.
- **Who is accountable for its compliance?** A governance axis rather than a technical one — the
  vendor, the adopting team, or the platform.

**Decide the axis**, then enumerate the population against the real estate: which workloads today
are actually in it, and how many. This shapes every other ticket — a shim for "things we bought" is a
procurement integration; a shim for "things whose spec we don't own" is an admission-plane feature.

Note the estate has a concrete example already: `flux-system/git-server`, which the forced-drift
campaign had to target *because* driftwood's own namespace runs no Deployment — an
infrastructure-owned workload nobody's policy version covers.
