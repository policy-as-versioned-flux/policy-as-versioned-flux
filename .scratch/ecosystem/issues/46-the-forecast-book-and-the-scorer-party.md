# 46 — The forecast book and the scorer party

Type: grilling (HITL)
Status: open
Blocked by: 04, 19

## Question

Which party runs the publisher-reliability scorer (it must publish no scored feed), from which repo, how the `publisher-reliability` feed is versioned and signed, what the adopter's threshold looks like on `party.yaml`, and how reliability diagrams and claim scope are published.

## Notes

Graduated 2026-08-28 from ticket 19's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.


## Delegated first implementation, 2026-10-17

Under ADR-0025 and the owner's standing build authorization, use the existing NIST
publisher as the independent scorer for the first report-only slice. Its published
discovery currently contains controls and no scored feed. Keep the scorer's own
reliability publication outside the scored set and reject a scorer that publishes
any target feed. This uses the existing party and feed contracts.

Build authenticated input/provenance handling, deterministic binary-forecast
scoring and reliability bins, an explicit unmeasured result for an empty eligible
population, discovery and the ordinary namespaced release route, and a registered
native/estate check. Preserve the scope of the existing Brier/log-loss instrument:
it does not establish publisher-price accuracy. A source-only test is not a
resolved forecast or an observed price.

The later price-affecting slice still needs its registered measure, unit, horizon,
resolution rule, publisher-supplied widening target and each adopter's signed bar.
The evidence-grade pricing threshold is a different quantity. This decision does
not supply those numbers, cut a release, change monetary inputs, or close ticket46.
Keep rejected input, authenticated but unscoreable input, and measured input
distinct. Genuine future registrations and independently sourced resolutions
remain necessary for a nonempty calibration population.
