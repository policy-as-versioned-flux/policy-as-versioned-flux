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
