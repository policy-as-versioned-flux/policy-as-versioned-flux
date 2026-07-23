# Architecture skeleton & Flux's load-bearing role

Type: grilling
Status: resolved
Blocked by: 08

## Question

With **Flux fixed as the central, load-bearing anchor** and everything else open, decide the
architecture skeleton the rest of the build hangs off. Concretely:

- **Enforcement engine** — stay on Kyverno (CEL ValidatingPolicy), or reselect? Judge on: can it
  express risk-tuned proportionality, feed the exemptions ledger and residual-risk maths cleanly,
  and support the shift-left check offline? (Research 08 surveys the options incl. Kyverno
  `PolicyException` and Crossplane's possible role.)
- **Where Flux is genuinely load-bearing** — not decoration for the sponsor. Name the jobs only
  Flux does well here (versioned distribution via `ResourceSet`, drift-heal, prune-on-retire,
  per-team reconcile cadence) and make sure the redesign leans on them rather than working around
  them.
- **The subsystem map** — one diagram: distribution (Flux), enforcement, shift-left discovery/check,
  exemptions ledger, evidence/up-flow (OSCAL), quantification. Which existing pieces survive, which
  are rebuilt, which are new.
- **Crossplane** — the human flagged the existing cloud-plane work as possibly supporting this;
  decide if/where it earns a place (research 08 informs this).

Output: the architecture decision + a subsystem diagram the shift-left (03), exemptions (05), and
refactor (fog) tickets build against.

## Answer

**Architecture skeleton confirmed** (research 08 drew it; human confirmed 2026-07-23). Flux central
and load-bearing; nothing is a "nice-to-have" — every component is built or cut, and none are cut.

- **Enforcement: Kyverno** `ValidatingPolicy` (CEL) — keep. Wins on all three criteria; switching
  buys nothing under a Flux anchor.
- **Flux load-bearing in six jobs:** `ResourceSet` version fan-out, signed `GitRepository`
  provenance, `prune`-on-retire, reconcile drift-heal, `dependsOn`/health ordering, notification
  event spine.
- **Exemptions = git ledger entry → rendered Kyverno `PolicyException`**, Flux `prune` (+
  `cleanup.kyverno.io/ttl` backstop) so it lives only while a live ledger row backs it.
- **Shift-left = ±1 version-skew** off the `ResourceSet` array; `kyverno apply` runs the target
  version's real action offline (Audit→Deny caught in CI).
- **Crossplane stays the cloud plane** (a policy target); the `ResourceSet` array is the version
  contract, not Crossplane.
- **Everything built, no cuts:** `trivy` (CVE→risk £), `c2p-collector`/OSCAL (evidence up-flow),
  `governance-agent` (now generalised — see below), `handbook-generator`, `policy-reporter`.

**Sunset dissolved into lifecycle/EOL risk (routed to the Risk model, 04, and upstream feeds, 10):**
the "sunset escalator" is not bespoke — a policy version going unmaintained is the same shape as
RHEL/Windows/Node/library EOL. It becomes a **time-varying intelligence thread** that ramps the
risk £ as EOL nears/passes (unpatched → CVEs accumulate), consumed from a real feed
(`endoflife.date`) exactly like the regulator artifacts. The policy version's own lifecycle is one
row in that same feed.

**Deferred to ticket 11 (topology):** the subsystem diagram and the cluster shape (1 vs 3 clusters).
