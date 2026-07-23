# The fictitious organisation & its risk appetite

Type: grilling
Status: resolved
Blocked by: —

## Question

Who is the fictitious company the whole demo is grounded in, precisely enough that every
downstream number and control is *proportionate to something real about it*? Grill out and pin:

- **Sector & regulator** — what regulatory regime sets the fines (e.g. finance/FCA, health/HIPAA,
  payments/PCI-DSS, data/GDPR)? This fixes the £ magnitude of a breach.
- **Size & shape** — revenue, headcount, number of teams/services, cloud footprint — enough to
  make "a breach = £N fine + M days downtime" defensible, not plucked.
- **Risk appetite** — what is the business *willing* to expose itself to, stated as a number/band?
  This is the dial the whole hourglass is tuned against.
- **The threat/risk register (starter set)** — the handful of concrete threats the controls exist
  to answer (e.g. data-at-rest exposure, unpatched CVE like Log4Shell, RDS single-AZ outage,
  unattributed workload), each with a rough impact/likelihood so controls can be sized against them.
- **The teams & apps** — do we keep/rename the current roster (ledger/reports/api/storefront/
  datastore) or redraw it to fit the org? What makes one team the deliberate laggard.

Output: a short "org brief" the risk model (04), balance-sheet (06), and deck (fog) all cite.

## Answer

**Not one org — a six-org topology, all live, all under the `policy-as-versioned-*` family**
(created by the human 2026-07-23). The point demonstrated is *portability of the discipline across
institutions*, plus the regulator sitting at the top of the dependency graph.

| Org | Role | Content honesty |
|---|---|---|
| `policy-as-versioned-platform` | the **shared discipline** all institutions inherit — Flux distribution mechanism, FAIR engine, exemptions-ledger pattern, shift-left harness, OSCAL plumbing (dogfoods the thesis on the tooling itself) | real |
| `policy-as-versioned-driftwood` | institution — **e-commerce** (the teaching default; PCI + GDPR) | fictitious business |
| `policy-as-versioned-tuppence` | institution — **fintech/payments** (FCA + PCI + GDPR; scary £) | fictitious business |
| `policy-as-versioned-caldera` | institution — **US health** (HIPAA) | fictitious business |
| `policy-as-versioned-nist` | regulator — **controls** | **real** 800-53 OSCAL catalog |
| `policy-as-versioned-ico` | regulator — **penalties** (`penalties@vYYYY.N`, machine-readable) | **real public** fine data, repackaged |

**Decisions locked:**
- **All three institutions fully live** (not 1-full-2-repo) — the contrivance is the repo *count*
  per org, not liveness, so faking two buys no honesty.
- **The `policy-as-versioned-` prefix is the impersonation guardrail** — `…-ico`/`…-nist` bear real
  regulator names but are unmistakably this demo's namespace, and their *content* stays honest
  (NIST = the genuine OSCAL catalog; ICO = real public GDPR/HIPAA fine magnitudes made
  machine-readable, never fabricated rulings).
- **The existing `policy-as-versioned-flux` org → archive** — but *at the end of the migration*, not
  now: it's the migration source and the currently-live demo, so archiving it early would break the
  running estate we're refactoring from. Tracked in the multi-org-topology ticket.
- **Portability + proportionality is proven by comparison** — the identical "encrypt at rest"
  control is `Audit` in `driftwood` and `Deny` in `caldera` because a HIPAA breach costs ~8× a
  retail one: same engine, same catalog dependency, different regulator skin, different £.

**Hand-off:** the per-institution **risk skins** (appetite band, fine magnitudes, threat register
numbers) are pinned in the *Risk → proportionality model* ticket (04), applied once per org — that
ticket already consumes this org brief.

**Graduated tickets:** *Regulator-as-upstream-dependency* (10), *Multi-org topology & shared-tooling
inheritance* (11, incl. the archive-flux migration), *Onboard Renovate across the six orgs* (12, task).
