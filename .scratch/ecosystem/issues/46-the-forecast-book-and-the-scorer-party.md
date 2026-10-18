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

## Delegated monetary source implementation, 2026-10-18

Under the same delegated build authority, the next software slice uses NIST's
separate namespaced `publisher-reliability/v2` report family for annual aggregate
monetary forecasts. Its registered `money-empirical-crps/v1` criterion scores the
full empirical distribution, with an exact negative mean loss so higher is
better. Each cohort fixes its unit, UTC annual horizon, target feed, served
generator, independent resolver and precommitted case inventory. Different
cohorts are not pooled. Binary v1 keeps its original bytes and claim boundary.

Each adopter may declare an explicit per-target `appetite.publisher_reliability`
policy: signed report/profile/widening references, a nonpositive numeric bar and
a positive minimum eligible sample. Equality meets the bar. No default bar,
minimum, monetary unit or production cohort is supplied. The platform consumes
the publisher-owned full wider target before the existing cage and price
calculation, preserving its frequency and authoritative payload. An authenticated
degraded native release is a separate cause for that same widening, including
when no monetary case has resolved. A missing or unauthenticated instrument
refuses; a genuine empty population stays unmeasured and supplies no score cause.
The evidence-grade pricing threshold is unchanged.

The software path includes public forecast/resolution SDKs, exact signed source
and immutable registration checks, whole-report reconstruction, publisher
conversion and native release proofs, composition, handbook evidence and saved
offline replay from captured Git objects. New diagnostic report publication and
subscription dates cannot advance the financial date. Historical comparisons
retain their captured contexts and distinguish a publisher version change from
the present reliability effect.

`verify/publisher-reliability/verify-publisher-price-vertical.sh` is registered in
the truth manifest as a source self-proof. It executes the actual producer,
independent resolver, scorer, publisher converter and composition using labelled
synthetic histories, monetary declarations and external signature responses.
It exercises the price/tier consequence, equality, insufficient samples,
degraded releases without resolutions, predecessor authentication and portable
replay/tamper refusal. This PASS is not a genuine signed monetary observation or
financial credit. The estate reader separately authenticates the report and
runs its native checker; monetary cohorts remain separate and empty results are
declared waits rather than successes.

Ticket46 remains open. Production currently declares no monetary cohorts and no
adopter has supplied this monetary policy. A genuine independent registration
and resolution population, each publisher's declared target and each adopter's
signed bar remain necessary for an observed price-quality result. Building and
publishing the software does not manufacture those inputs or change historical
grades.
