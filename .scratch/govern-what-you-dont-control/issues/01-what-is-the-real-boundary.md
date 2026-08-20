# 01 — Is "COTS" the boundary, or is it "can we change the pod spec"?

Type: grilling
Status: resolved
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

## Answer

Resolved by grilling, 2026-08-20.

**1. The axis is "can we change the pod spec" — and it is defined by its remedy.** Owner: *"wrap it
or shim"*. The population is not "things we bought"; it is everything whose pod template we cannot
edit without forking upstream, and what identifies it is that the answer for all of it is the same:
**wrap it or shim it**.

That phrasing forecloses two options this ticket had left open, and the closure matters:
- **not exemption** — a COTS workload is not a thing to carve out of policy;
- **not denial** — it is not a thing to refuse for failing to be first-party.

Practical test for the boundary: *can we add a label and a securityContext to this pod template
without forking the upstream?* If no, it is in the population.

**2. The population, enumerated against the real estate — and it is mostly us.** The estate runs five
third-party Helm charts it does not author, and **none carries a `policy-as-versioned.dev/policy-version`
label**:

| chart | namespace |
|---|---|
| `spiffe` (SPIRE) | `spire-system` |
| `istio` | `istio-system` |
| `openbao` | `openbao` |
| `pomerium` | `access` |
| `dex` | `access` |

Plus `flux-system/git-server`, applied by `scripts/up.sh` outside GitOps — already found once by the
twin's forced-drift campaign, which had to target it precisely because no policy-versioned Deployment
existed to target.

So the largest population of ungovernable-by-default workloads in this estate **is the governance
apparatus itself**.

**3. The platform's own infrastructure is in scope, and is the leading case.** It meets the
definition exactly, it is already running, and it is an exemption nobody declared. It also closes a
real hole in the reflexive story: `honesty/reflexive.py` prices the apparatus's own risk and reports
that it "passes its own test" — but it passes on **£**, while its actual pods (istiod, spire-server,
openbao, pomerium, dex) are matched by no policy and admitted by default. Solving the hardest case
first also proves the mechanism: if the shim can govern istiod, it can govern anything.

**4. Accountability splits along the existing dependency direction.** The **institution** owns the
risk and the £ — it chose the product, it carries the residual in its own appetite band. The
**platform** owns the mechanism — it must publish a wrap or shim that makes the product governable.
Predicted failure mode worth designing against: an institution adopts something ungovernable and
finds the platform has no mechanism for it. That is a request *for a policy version*, not an
exemption request.

**Constraint carried forward to the remaining tickets:** the escape hatch already exists but is
unreachable. `may-run-root-if-attested` implements exactly the right shape —
`nonroot || (attested && hardened)` — but its `matchConditions` require `policy-version == '1.0.0'`,
so it is gated behind the very label this population cannot wear. Whatever the wrap or shim does, it
must get these workloads *to* that mechanism rather than around it.
