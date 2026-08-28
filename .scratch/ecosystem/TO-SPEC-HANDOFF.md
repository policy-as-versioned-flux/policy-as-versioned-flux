# Handoff to /to-spec — the eco-system, operating

Written 2026-08-28. This is the state of the map after the 2026-08-28 batch. Read this, then `map.md`, then the `## Answer` of each ticket you spec.

## What is decided

- 22 tickets are resolved (01 to 16, 18 to 20, 22 to 24). Their one-line gists are in `map.md` under Decisions so far. Each ticket's `## Answer` holds the detail. A held round above the Answer is the record of what was recommended; the Answer is what was accepted.
- Ratification status. Tickets 04, 07, 08 and the 2026-08-28 batch are provisional: the owner agreed without a reason. Five conflicts (D1 to D5) are decided with the owner's reason. Under the map's process rule a provisional decision can be reopened with a reason; a spec must say which decisions it rests on.
- ADRs written today: [0022](../../docs/adr/0022-the-cage-ladder-tier-per-namespace-isolated-rung-floor-and-infra.md) (cage ladder) and [0023](../../docs/adr/0023-a-clock-appends-observations-and-one-signature-verified-by-a-controller.md) (clocks, one signature, demo number, supersede price). ADRs 0014, 0015, 0016, 0018 carry banners. Ticket 39 owns the next supersessions (0013, 0017, 0018 §3). Ticket 28 supersedes ADR-0015 point 5.
- CONTEXT.md carries the new vocabulary: tier, isolated, floor, infra tier, observation, declaration, rejection ledger, declared bump, and the rest merged 2026-08-28.

## The thin slice, in build order

NORTH-STAR §4, one regulator, one adopter (driftwood), one feed, one cage move, one twin forecast, all real, graded by `talk/verify-all.sh`.

1. **21** Build the feed contract. Unblocks 22, 23, 25, 26, 28, 29, 36, 38, 43, 45, 49, 50.
2. **25** Build the £ seam. One `prices[]` schema pass (C11) and one forward-intel payload amendment (C10) happen here, once.
3. **26** The cage ladder lands. **28** Daily clocks and the caged observation lane. **32** Identity substrate package. These three can run in parallel after 21.
4. **40** Driftwood proves the composed set in force from signed sources in CI. **41** The gitsign-verifying source controller. Then **42** widens to tuppence and ludlow.
5. **29** Adopter twin overlay, twin tag, twin evals. **49** Market-moves feed. **50** News feed and headline skill.
6. **43** The first gate-determined release. **47** The generated deck. **44** Misuse catalogue graded. **45** Switching cost.
7. Then the remaining tasks: 33, 34, 36, 38.

Open AFK tasks from before the batch: **17** (twin follow-ups) and **21**, **25**. Ticket 17 is unblocked and untouched.

## Grilling still open

Eight grilling tickets graduated today: 27, 30, 31, 35, 37, 46, 48, 51. None blocks the thin slice. Walk them at five decisions a day after the first build lands.

## New tickets

| # | Title | Type | Blocked by | From |
|---|---|---|---|---|
| 26 | The cage ladder lands | task | 09, 21 | 09 |
| 27 | The cage ladder, round 2 | grilling | 09 | 09 |
| 28 | Daily clocks, caged observation lane and derived ledger | task | 09, 21 | 10 |
| 29 | adopter twin overlay, twin release tag and twin evals in the gate | task | 09, 21, 25 | 11 |
| 30 | The twin's cage, spec and price per adopter | grilling | 09, 12 | 11 |
| 31 | Sensor admission for the key-person scenario | grilling | 19 | 11 |
| 32 | Build the identity substrate package | task | 09, 12 | 12 |
| 33 | Lift ledger, storefront and reports into their adopters | task | 09 | 13 |
| 34 | Handbook as a compose-time render | task | 09 | 13 |
| 35 | scanner, notification spine, OSCAL CronJob, api and datastore | grilling | 16, 21, 33 | 13 |
| 36 | the insurer quote slice | task | 10, 21, 25 | 14 |
| 37 | insurance round 2 | grilling | 14 | 14 |
| 38 | Priced holes in composition | task | 09, 21, 25 | 15 |
| 39 | Supersede ADR-0013, ADR-0017 and ADR-0018 point 3 | task | 15 | 15 |
| 40 | Driftwood proves the composed set in force from signed sources in CI | task | 03, 10, 16 | 16 |
| 41 | The gitsign-verifying source controller | task | 16 | 16 |
| 42 | Widen the Flux slice to tuppence and ludlow | task | 40, 41 | 16 |
| 43 | The first gate-determined release (H9-04) | task | 16, 21, 25 | 18 |
| 44 | Eco-system misuse catalogue graded by the gate | task | 19 | 19 |
| 45 | Switching cost computed in composition | task | 15, 21, 25 | 19 |
| 46 | The forecast book and the scorer party | grilling | 04, 19 | 19 |
| 47 | The generated deck | task | 03, 10 | 20 |
| 48 | The demo's remaining beats | grilling | 10, 11, 18, 20 | 20 |
| 49 | Build the market-moves feed | task | 10, 21 | 22 |
| 50 | Build the news feed and the headline skill | task | 10, 21, 25 | 23 |
| 51 | The supply-constraint actor path and the scored headline forecast | grilling | 11, 23 | 23 |

## What a spec must carry

- Every ticket's definition of done wires its check into `talk/verify-all.sh`. The TRUTH line is the only citable number.
- Price and cage. Never count, refuse or file. No gate. No exemption. If a spec needs a refusal it has found a missing instrument (ADR-0020), not a behaviour.
- One signature, the gitsign tag. One render, `cage-tier` from the Namespace. One `prices[]` schema. One rule for publisher PRs. One scenario library per adopter, owned by the twin overlay.
- A clock appends observations and never a declaration. The reviewed PR is the unit of adoption.
- Every price carries perspective and currency. No sum crosses perspectives.

## Known residuals

- Step 4 of the demo reads could-not-look until 40 lands.
- The `isolated` default must not flip before the platform's `infra` declaration lands (ADR-0022), or CoreDNS stops.
- `cage-netpol` per-tier reach with `synchronize` has a delete-then-regenerate gap on a tier move. Named, not hidden.
- The EOL-ramp price for a superseded pin may misprice; the revisit trigger is in ADR-0023.
