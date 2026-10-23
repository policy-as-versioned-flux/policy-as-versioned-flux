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

## Signed publisher adapter releases, 2026-10-23 UTC

The generic publisher conversion capability is now available in signed release artifacts. Feeds [PR 15](https://github.com/policy-as-versioned-feeds/feeds/pull/15) normally merged as `0a1f27277a6d8f2db5fdd7983df0357b6834a858`; signed [threat-register/v4.1.0](https://github.com/policy-as-versioned-feeds/feeds/releases/tag/threat-register/v4.1.0), tag object `c860a2251d5f2ee77af0eab47dac4be0a2620270`, is Release 421397920. ICO [PR 10](https://github.com/policy-as-versioned-ico/ico/pull/10) normally merged as `8e53a5998571f7f4366c56ce338cc19d6ea589d8`, preserving reviewed source `f4ae1f9c6ec8326a9dafe56a2d3c1374733652bc` and tree `28322bc11e4f82a8e4681ab83f855f39001462a6`; signed [v4.0.1](https://github.com/policy-as-versioned-ico/ico/releases/tag/v4.0.1), tag object `552491455b74752e30327e65308575f777fa2faf`, is Release 421410540. Both artifacts carry the reviewed standalone `forecast-base` and `widen-to` modes and optional publisher native release-proof helper. Source delivery, signed publication and monetary enrollment remain distinct.

Original feeds [cut 39890888600/1](https://github.com/policy-as-versioned-feeds/feeds/actions/runs/39890888600) and [release 39891086344/1](https://github.com/policy-as-versioned-feeds/feeds/actions/runs/39891086344), and ICO [cut 39893295164/1](https://github.com/policy-as-versioned-ico/ico/actions/runs/39893295164) and [release 39893348575/1](https://github.com/policy-as-versioned-ico/ico/actions/runs/39893348575), all completed successfully. Each hosted identity-pinned verification records Git signature, Rekor entry and certificate claims TRUE for its own cut workflow. The retained original log ZIPs pass CRC and bind their actual source checkouts and tag targets. The private frozen publication proofs are `.scratch/ecosystem/research/resume-active-20261022T2203/feeds-adapter-capability-release-publication/PROOF.json` and `ico-adapter-capability-release-publication/PROOF.json` under the same research root.

ICO's actual registered envelope verifier initially rejected a valid same-major patch because it required exact x.0.0 versions. The fix checks canonical ASCII semver against each directory major while retaining identity, schema, migration and financial-formula invariants. Meaningful RED/GREEN/restored-RED/final-GREEN evidence includes the two Unicode-digit rejection cases. The complete genuine wrapper passed on the exact corrected tree with original OpenSSL signatures, release-pinned platform 2.0.1 FAIR source and a real NIST tag read; the actual hosted release also ran the 8 envelope, 10 ABI and 11 native-proof fixture tests successfully. These historical computations verify source behavior, not a new financial observation.

**Still open.** Neither release adopts a monetary model, cohort, publisher widening target, adopter bar/minimum, forecast registration, independent outcome or adopter pin change; neither enrolls a release cage or supplies new price-quality/cage credit. The three pending owner choices remain assurance cutoffs, workload baseline versus explicit isolated floor versus revised model, and calibration target/population/outcome scope. The prospective institutional direct-recovery model must match its chosen accounting outcome; overlapping workload planning contingencies do not supply that model by relabeling or summation. Genuine pre-horizon signed registrations, independently sourced final/complete outcomes, publisher-owned widening targets and each adopter's signed policy remain necessary. Primary TRUTH 450 remains historical **115 PASS / 3 FAIL / 23 SKIP / 8 EXCLUDED**. Ticket 46 stays open; tickets 27, 74, 155 and 156 and counts **156 resolved / 2 claimed / 3 open / 1 closed** are unchanged. Post-release queue maintenance is separate and no queue-reset completion is claimed here.

## Compatible feeds ABI adopter delivery, 2026-10-23 UTC

Following the signed publisher-adapter publication recorded above, the compatible feeds 4.1 converter interface has completed ordinary source, signed-composition and final-pointer delivery in Driftwood and Ludlow. Driftwood source [PR97](https://github.com/policy-as-versioned-driftwood/driftwood/pull/97) merged at `138ddd652aa23f940cab378f7f8fb7d88eb7ba97`; signed [v5.1.0](https://github.com/policy-as-versioned-driftwood/driftwood/releases/tag/v5.1.0), tag `9ce5e3c3e484f9e6c2fc263cb039a392a5a2249d`, is Release 421449689. Final [PR98](https://github.com/policy-as-versioned-driftwood/driftwood/pull/98) merged at `5120aa52322615e59b970c75bfa9e610d09101c9` and selects that source. Ludlow source [PR99](https://github.com/policy-as-versioned-ludlow/ludlow/pull/99) merged at `17bc9dbd176b97b1e3d551aa9ebf79c0b89df216`; signed [v5.2.0](https://github.com/policy-as-versioned-ludlow/ludlow/releases/tag/v5.2.0), tag `3a6281b704930f9fd902b34b00d073e9714ba84f`, is Release 421460754. Final [PR100](https://github.com/policy-as-versioned-ludlow/ludlow/pull/100) merged at `2eb62516695deab9567d5338bf81842b8302839e` and selects that source. The original final-pointer CI runs, 39902803551/1 and 39904424877/1, completed with both jobs successful; independent final canonical conservation audits bind the complete source/body, old signed objects, full observation blames and unchanged financial outputs.

Tuppence source [PR 107](https://github.com/policy-as-versioned-tuppence/tuppence/pull/107) merged at `c7eb0973c32d687feb8ef5e8891a2e261fe44acc`; signed [v4.2.0](https://github.com/policy-as-versioned-tuppence/tuppence/releases/tag/v4.2.0), tag `e373f80f469517c33cc27139a3fa09104d1c8626`, is Release 421464135. Final [PR 108](https://github.com/policy-as-versioned-tuppence/tuppence/pull/108) normally merged at `92affc93499e9bb05af2e5009e3d7c1df839d389` and selects that source. Original final-pointer CI [39905361260/1](https://github.com/policy-as-versioned-tuppence/tuppence/actions/runs/39905361260) completed with both jobs successful and 66 hosted tests. Each composition tag remains at source A; final repository source B selects it, without an additional B tag.

This is FE-only compatible ABI delivery: authoritative financial payloads, numeric types, each financial as-of, prices/tiers and five legacy pricing-function ASTs are conserved. ICO 3 and all other publisher/tools pins, apps/native inventory, policy declarations and historical OBS/captures remain unchanged. The signed generic ICO 4.0.1 capability remains unadopted here; ICO 3→4 changes financial schema/model semantics and is outside this route. Repository pointer delivery is not cluster activation or a new runtime grade.

Ticket 46 remains open. No monetary model, cohort, widening target, signed adopter bar/minimum, assurance choice, forecast registration, independent outcome or financial/cage credit is adopted. The three pending owner choices and matching institutional recovery model, genuine pre-horizon registrations and independent complete outcomes remain necessary. Historical TRUTH 450 remains 115 PASS / 3 FAIL / 23 SKIP / 8 EXCLUDED; active tickets 27/46/74/155/156 and 156 resolved / 2 claimed / 3 open / 1 closed (162 total) remain unchanged. Earlier progress rollups remain history.
