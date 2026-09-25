# 144 — The twins price on published comparable evidence

Type: task
Status: open
Blocked by: 141

## Question

Graduated 2026-09-25 from grilling ticket 30, decisions 4, 6 and 13 (delegated), and ADR-0032.

1. **driftwood.** Its pricing edge `cart-pii-loss-cuts-checkout-revenue` claims grade 2 with no
   record; it drops to grade 3 and gets a comparable-firm anchor, as tuppence's and ludlow's edges
   have. Its rung responses cite "two prior incident post-mortems" and "the platform's own
   break-glass drill", which exist nowhere; they drop to grade 3 or cite a real source. driftwood
   declares grade 3 on `party.yaml` (ticket 141).
2. **tuppence and ludlow.** Each gets a signed `size:` block, a share-of-turnover figure and a
   valuation amount derived from them, and declares grade 3 (ticket 141). **The sizing rule is
   fixed before its effect is computed** (ticket 30 decision 13): copy the comparable firm's
   published figures and their real date from its most recent complete primary filing (Starling
   Bank for tuppence, Elevance Health for ludlow); a stale `as_of` widens to the cap. The figures
   and their sources are appended to this ticket by ticket 30's research pass.
3. **The missing instruments.** tuppence and ludlow ship no `selection-policy/` package and no
   publishing contract (`twin/forward-intel/v1/feed.json`, `rule.yaml`, `bump.yaml`, a
   `publishes[]` record). Both are needed before composition prices a twin line.
4. **One edge reaches the cash flow.** A replacement edge replaces the grade-3 edge; it does not
   sit beside it.

## Notes

`verify/schedules/clock-owners.yaml` maps tuppence's and ludlow's twin sweeps here (moved from
ticket 30 on 2026-09-25). Caution: a size change is one of ticket 74's three movers; the figures
must not be tuned to cause a crossing. Adopter tags wait for the owner's authorisation.

## Comments

**2026-09-25, the sizing research (ticket 30 decision 13).** One finder and one adversarial
checker; the checker confirmed all 18 fields against the primary filings. No price, tier or
residual was computed with these figures before they were fixed.

| Field | tuppence, from Starling Bank Limited | ludlow, from Elevance Health, Inc. |
|---|---|---|
| Filing | Annual Report and Accounts 2026, individual company, year to 2026-03-31; Companies House AA filed 2026-07-12 | Form 10-K, year to 2025-12-31; SEC accession 0001156039-26-000013, filed 2026-02-06 |
| `as_of` | 2026-03-31 | 2025-12-31 |
| `turnover` | 861,741,000 GBP, statutory "Revenue" (p142) | 197,584,000,000 USD, "Total operating revenue" |
| `customers` | 4,900,000, "Total customer accounts" 4.9m (p6, p11); a rounded count of accounts | 45,232,000, "Total Medical Membership 45,232" (thousands); members, not purchasers |
| `data_subjects` | not disclosed | not disclosed |
| `headcount` | 3,902, "Total average number of employees" (note 10, p170); an annual average | 97,100, "approximately 97,100 individuals" at 2025-12-31 |
| share of turnover | 113,975 / 861,741 = 0.13226, "Fee and commission income" (note 7) over "Revenue"; the filing states 13.23% itself (p8) | 8,475 / 197,584 = 0.04289, "Service fees" over "Total operating revenue" |

Sources: Starling, Companies House document `MzUzMDYwOTgwOGFkaXF6a2N4` (a scanned PDF read by
OCR; cross-sums hold). Elevance,
`https://www.sec.gov/Archives/edgar/data/1156039/000115603926000013/elv-20251231.htm` and its
XBRL rendering `R5.htm`. No newer complete filing exists for either firm on 2026-09-25.

Consequences for this ticket, each **delegated** (ADR-0025):

1. **`data_subjects` is not disclosed by either filing**, and the size block is all or nothing
   today. The rule forbids filling a gap. Decided: `data_subjects` becomes optional in ticket
   141's schema change. Nothing in the estate reads it today (only `turnover`, `as_of` and
   `customers` are read); a converter that needs it later refuses by name (ADR-0020).
2. **Turnover is the gross statutory revenue.** Starling's net alternative, "Total income
   £748.0m", includes £114.1m of intercompany income, and the filing's own fee ratio uses the
   gross base.
3. **Neither size is stale.** Both `as_of` dates are within 12 months of the pinned penalty
   schema's `published_at` (2026-08-28), so neither widens to the cap. Round 3 expected the cap
   from the older filings in `94-studied-firms.md`.
4. **The share is annual.** Neither perspective declares `periods_per_year`, so it defaults to 1.
5. **ludlow's figures are USD**; its reporting currency is GBP. The valuation amount converts
   through the signed FX feed at a dated rate. The twin's valuation re-derivation check applies no
   conversion today, so this ticket adds one.
6. The labels differ from driftwood's meaning: Starling's customers are accounts, Elevance's are
   members, and Starling's headcount is an average. Each `size:` block carries a note that says so.
