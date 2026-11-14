# H13: the eco-system tickets, map, spec, reviews and handoffs

Area: `FRESH/hub/.scratch/ecosystem/`, meaning its 12 top-level files and the 169 files in `issues/`. The `research/`, `patches/` and `review-2026-09-02/` attachments are excluded. Measured 2026-11-14 with `wc -l` and `git log --diff-filter=A`. Paths starting `issues/` are relative to the area. `_grades.tsv` and `verify-manifest.txt` are `FRESH/hub/talk/`. Other paths are relative to FRESH.

## Summary

- 181 files and 35,554 lines: 32,865 in tickets, 2,689 at the top level. The tickets were born between 2026-08-28 and 2026-10-27. Status lines: 164 resolved, 2 open, 2 claimed, 1 closed. The count at `map.md:370` ("162 total", written in the 2026-10-23 reconciliation) predates tickets 163 to 169.
- Tickets by loop role: ceremony 45, none 30, quantify 27, evidence 21, react 19, cage 12, presentation 5, enact 4, ratchet 3, compare 2, tolerance 1. By necessity: support 61, off_mission 50, ceremony 45, kernel 13.
- 80 of the 169 tickets (47%) exist only to repair, record or verify what an earlier ticket produced. From ticket 98 on, 56 of 72 do.
- Every loop step has tickets, but the ratchet has never moved. Each adopter's app Namespace has been declared `isolated`, the bottom rung, since ticket 26 on 2026-08-28: `driftwood/gitops/apps/namespace.yaml:30` (blame `348b97c4`), and the same commit on tuppence and ludlow at `:28`. Ticket 74, the first real band crossing, has been open since 2026-09-01. The step-3 PASS uses a SYNTHETIC residual (`verify-manifest.txt`, class `simulation`).
- The compare step does run each exposure line through the ladder (`floor_change.lines`: `driftwood/composed/evidence.json:6204`, `tuppence/...:3761`, `ludlow/...:4210`). At `isolated`, the ICO residuals are:
  - driftwood: £35,744 against a tolerance of £40,000, so within;
  - tuppence: £358,159 against £15,000 (its twin line is £1.68M);
  - ludlow: £61.4M against £5,000.

  Two of the three adopters are still above tolerance on the bottom rung, with no notch left. Driftwood is within only because of rung reductions the record calls "self-declared calibration, not measured effectiveness" (`driftwood/composed/evidence.json:6272`).
- After the 2026-09-02 review, most work went to the gate and its records, the Kyverno engine matrix, twin governance and pricing repairs, not to the loop.

## Components (ticket groups by job)

| name | paths | lines | born | what it does | loop role | necessity | origin | status | cite |
|---|---|---|---|---|---|---|---|---|---|
| T1 Risk quantification decisions | issues 07, 08, 15, 24 | 280 | 2026-08-28 | Grilling tickets that decided how exposure becomes money: signed size and obligations per adopter, per-regime scaling, appetite on party.yaml, a versioned selection policy, every hole priced | quantify | kernel | delegated | tested_offline | issues/07, 08 Answers; issues/24 owner 2026-08-19 "cost per customer" |
| T2 Pricing built into composition | issues 25, 38, 119, 121, 124 | 702 | 2026-08-28 | Builds the pound seam and priced holes in composition.py, so each adopter's composed/evidence.json carries prices[] and a cage decision (residual vs band) | compare | kernel | delegated | observed_running | driftwood/composed/evidence.json:363-368 (cage: residual vs band); _grades.tsv verify-priced-holes PASS (estate-observation) |
| T3 Pricing defect repairs | issues 106, 110, 122, 123, 126, 127, 128, 133, 136, 137, 138, 139, 165 | 2438 | 2026-09-08 | Fixes defects in the pricing build found by checks, loophole rounds and rollouts (offline re-derivation, as-of dates, ramps, withdrawn controls) | quantify | support | assistant | tested_offline | issues/133, 136, 139 Answers cite platform PRs 39-43 |
| T4 Exposure inputs, staleness, provenance | issues 69, 79, 84, 94 | 1437 | 2026-08-31 | Makes the pound inputs sourced and current: legal status of ICO fines, studied real firms for sizes, untagged and superseded pins priced | quantify | support | assistant | observed_running | driftwood/composed/evidence.json prices[] supersede line; _grades.tsv verify-supersede PASS (estate-observation) |
| T5 Cage ladder design and build | issues 09, 26, 27, 63, 89 | 1863 | 2026-08-28 | Defines and serves the cage: ladder baseline/restricted/quarantine/isolated/infra, tier on the governed Namespace, tighten-only mutation, unlabelled default to isolated, nothing denied | cage | kernel | delegated | tested_offline | 4 of 5 delegated; exception 89 from the owner's issues/75 Round 1 Q5 quote 2026-09-02; driftwood/gitops/apps/namespace.yaml:30; _grades.tsv verify-graded SKIP (class never) |
| T6 Cage defect repairs | issues 98, 111, 113, 130, 158, 159 | 1519 | 2026-09-05 | Repairs cage bodies and delivery: undelivered PriorityClasses, unread infra role, a rung that loosened runAsNonRoot, a tier label honoured on ungoverned Namespaces | cage | support | assistant | tested_offline | issues/158 (baseline rung wrote runAsNonRoot false), 159; fixed in platform policy/v7.0.0 |
| T7 Clocks and the ratchet (proposer) | issues 10, 28, 74, 78 | 599 | 2026-08-28 | Daily clocks re-compose at today's date and propose a tier PR; the proposer is clamped tighten-only and signed; ticket 74 waits for the first real crossing | ratchet | kernel | assistant | written_never_run | the ratchet EVENT never ran; ticket 74's text says the proposer clock fires daily and proposed `[]` (not verified: verify-schedules is SKIP); issues/74 Status: open; _grades.tsv verify-e2e-step3 PASS on a SYNTHETIC residual (manifest class simulation); tier unchanged since 2026-08-28 (blame 348b97c4) |
| T8 Enact via Flux and post-admission re-caging | issues 16, 41, 42, 91 | 419 | 2026-08-28 | Flux reconciles the adopter's signed composed tag behind a gitsign-verifying source controller; the currency controller re-cages after retirement | enact | support | delegated | observed_running | _grades.tsv verify-e2e-step4 PASS from scheduled lane sample; issues/41 |
| T9 Runtime cage evidence lane (facts 1-8) | issues 40, 81, 86, 107, 135, 140, 152, 155, 157, 160, 161 | 2518 | 2026-08-28 | Scheduled ephemeral-KinD samples grade whether the composed cage is in force (facts 1-5), the bottom rung runs and reaches nothing (6, 7), and served workloads run in cage (8) | evidence | support | assistant | observed_running | _grades.tsv verify-reconcile PASS x3 (class self-proof, grades committed lane samples); issues/160, 161 |
| T10 Feed contract and real feed bumps | issues 01, 04, 21, 57, 61, 62, 72 | 964 | 2026-08-28 | One signed feed envelope, publisher orgs, workflows that actually register, pinned and signed consumption, and the one real Renovate feed bump (step 2) | react | support | delegated | observed_running | driftwood merge 27f1cf2 2026-09-01 "Merge pull request #20 ... renovate/feeds-threat-register-2.x"; _grades.tsv verify-feed-contract PASS |
| T11 Speculative signal feeds (markets, news, headline) | issues 22, 23, 49, 50, 51 | 614 | 2026-08-28 | Prediction-market and news feeds plus a human-run headline skill that feed the twin | react | off_mission | delegated | tested_offline | _grades.tsv verify-news-headline-skill PASS (human-run skill); issues/22 "Markets never price a control" |
| T12 CVE scan as reaction input | issues 35, 153 | 278 | 2026-08-28 | Places the vulnerability scanner and prices a CVE from the adopter's own image scan against a KEV-scoped feed | react | support | delegated | observed_running | _grades.tsv verify-cve-inventory PASS; driftwood/composed/evidence.json cve price could_not_look (no KEV match) |
| T13 Twin forecasting and probability | issues 11, 29, 64, 92, 93, 141, 144 | 1835 | 2026-08-28 | Per-adopter twin overlays, scenario libraries, a local Claude clock and a derived probability, feeding a source:twin price | quantify | support | delegated | tested_offline | twin price lines exist in served evidence (tuppence forward-intel 84.2M GBP), but the derive step never ran: _grades.tsv verify-derived-forecast SKIP (no forecast reached main), verify-e2e-step5 SKIP, verify-local-clock SKIP |
| T14 Twin skill-evaluation hygiene | issues 112, 118, 164, 168, 169 | 657 | 2026-09-22 | Grades the twin's six skills: corpus sizes, right answer for the wrong reason, stated basis, causal evidence, decay dates | ceremony | off_mission | codex | tested_offline | hub merges PR 272, 282, 283 (codex/ branches); issues/112, 118 |
| T15 Twin agent cage and twin sensing ethics | issues 30, 31, 142, 143, 145 | 2291 | 2026-08-28 | Cages and prices the twin AI agent itself, and decides what a twin may sense about a key person | none | off_mission | delegated | tested_offline | _grades.tsv verify-twin-cage "LIMIT: ... no fresh live test was run"; issues/31 is 1,109 lines |
| T16 Insurance and the insurer party | issues 14, 36, 37, 162 | 206 | 2026-08-28 | An insurer party publishes signed quotes; the premium enters prices[]; a disclosure says the quote is illustrative | none | off_mission | delegated | observed_running | driftwood/composed/evidence.json premium 113,403.30 GBP; tolerance 40,000 GBP (driftwood/party.yaml:60) |
| T17 Forecast reliability pilot | issues 46 | 150 | 2026-08-28 | A publisher-reliability scorer and a prospective 2027 recovery-expense pilot | evidence | off_mission | delegated | written_never_run | issues/46 Status: open; "final annual outcomes unavailable before 2028-01-01" |
| T18 Versioning, computed semver, release machinery | issues 05, 06, 18, 43, 53, 99, 103, 129, 131, 132, 134 | 1739 | 2026-08-28 | Computed semver of policy releases, declared-vs-computed bump gates, adopter gates over majors, release tag mechanics, ESLint and Cedar research | none | off_mission | delegated | tested_offline | _grades.tsv verify-gate and verify-comparison-window PASS (selfcheck) |
| T19 Signature and trust-root verification | issues 73, 77, 101, 105 | 1394 | 2026-09-01 | Adopter gates verify real published signatures offline; pins are checked for content; a tag-certificate timing fix | evidence | support | assistant | observed_running | _grades.tsv verify-untagged-pin-is-priced PASS; issues/101, 105 |
| T20 Kyverno multi-engine support | issues 54, 71, 146, 147, 148, 149, 150 | 1306 | 2026-08-31 | Which Kyverno versions a policy line supports, per-adopter engine declaration, pricing of unsupported pairings, one adopter on 1.19.1 | none | off_mission | delegated | tested_offline | _grades.tsv ludlow verify-cage-probe PASS on kyverno 1.19.1, offline |
| T21 Identity substrate (shelved) | issues 12, 32, 68, 90 | 312 | 2026-08-28 | SPIRE/Istio/OpenBao/Pomerium identity spine, built and then shelved; federation peer closed | none | off_mission | delegated | written_never_run | issues/90 (shelved 2026-09-04); issues/68 Status: closed |
| T22 Truth surface and gate machinery | issues 03, 52, 55, 56, 59, 60, 70, 76, 83, 85, 100, 104, 108, 114, 125, 163, 166, 167 | 3266 | 2026-08-28 | verify-all.sh, the TRUTH line, falls that block, derived Status, recording mechanics, fixes to checks of checks | evidence | ceremony | assistant | observed_running | hub/talk/truth.log run=491 2026-11-12 pass=117 [observed=42 self=61 simulated=4 meta=10] |
| T23 Agent enactment governance | issues 65, 87, 88, 96, 97 | 1080 | 2026-08-31 | Guards on what the assistant may push or merge: enact_guard, a second GitHub identity, forge rulesets, ENACT_MODE recorded and checked | ceremony | ceremony | assistant | tested_offline | issues/97 owner 2026-10-22 "agree to renew this until the end of the year" |
| T24 Misuse, portability, loophole rounds | issues 19, 44, 45, 115, 116, 120 | 1281 | 2026-08-28 | Misuse catalogue, switching cost, and adversarial loophole rounds against ADRs with deterministic verdicts | ceremony | off_mission | assistant | tested_offline | issues/115, 116, 120 (bench/loophole) |
| T25 Demo, deck, handbook | issues 20, 34, 47, 48, 66 | 959 | 2026-08-28 | Deck generated from gate captures, demo beats, handbook render | presentation | off_mission | delegated | unknown | issues/47, 48, 66 |
| T26 Incumbent org, apps, cloud plane | issues 13, 33, 151, 154, 156 | 745 | 2026-08-28 | Lift or retire 2022-era mechanisms and repos, transfer apps, archive the incumbent org, Crossplane cloud plane in tuppence | none | off_mission | delegated | unknown | issues/156 Status: claimed; issues/151 |
| T27 Purpose, records, legal ceremony | issues 02, 17, 39, 58, 67, 75, 80, 82, 95, 102, 109, 117 | 2013 | 2026-08-28 | Purpose (ticket 75), north-star rebaseline, ADR supersessions, record hygiene, licence, the duplicate-number fix | ceremony | ceremony | assistant | observed_running | majority assistant; exceptions 75, 95 (owner words, issues/75 Round 1 answers 2026-09-02); _grades.tsv verify-derived-status PASS |
| P1 Planning, specs and agent briefs | map.md, spec.md, TO-SPEC-HANDOFF.md, GRILL-WALK.md, HANDOFF-2026-08-31.md, BUILD-BRIEF.md, BUILD-BRIEF-2026-09-03.md, EXECUTION-2026-09-10.md | 1217 | 2026-08-28 | The map (decision log: 370 lines, 143 KB), the thin-slice spec of NORTH-STAR §4, and run briefs for agent waves | ceremony | ceremony | assistant | unknown | spec.md:25-32 (the seven joints); map.md:370 count "162 total", dated 2026-10-23, before tickets 163-169 |
| P2 Whole-estate reviews | REVIEW-2026-08-31.md, REVIEW-2026-09-02.md | 381 | 2026-08-31 | Two agent-swarm audits (55 and 407 agents) that charted tickets 53-67 and 76-87 | ceremony | support | assistant | unknown | REVIEW-2026-09-02.md:52 "All three adopters sit on the bottom rung" |
| P3 Repair and ops records, pin-bump helper | REPAIR-2026-09-04.md, CI-2026-09-04.md, TICKET-87-OBSERVATION-MIGRATION.md, bump-adopter-pins.sh | 1091 | 2026-08-31 | Diagnoses of regressions the agent waves caused, a CI repair, an observation-ref migration plan, and a script that bumps adopter platform pins | ceremony | ceremony | assistant | unknown | REPAIR-2026-09-04.md:1-10 "the eight regressions the 2026-09-03 build caused" |

The component lines sum to 35,554, the area total.

## Every ticket

`R` marks a ticket that exists only to repair, record or verify what an earlier ticket produced. The rule: the ticket's Question rests on a defect, a stale record or an ungraded claim in something an earlier ticket built or decided. A grilling ticket that graduates into its build is not `R`.

Origin rules: `owner_words` needs a dated owner quote in the ticket. A bare "agree" counts as `delegated`, which is how the record treats it (ADR-0025, `issues/75`). `codex` needs a merge from a `codex/` branch or an explicit "Codex" line.

| # | gist | group | loop role | necessity | origin | R | status | lines | born |
|---|---|---|---|---|---|---|---|---|---|
| 01 | create feeds and insurer orgs | T10 | react | support | delegated | - | resolved | 23 | 2026-08-28 |
| 02 | rebaseline documents to north star | T27 | ceremony | ceremony | delegated | - | resolved | 26 | 2026-08-28 |
| 03 | one gate, honest TRUTH line | T22 | evidence | support | delegated | - | resolved | 50 | 2026-08-28 |
| 04 | signed feed envelope contract decided | T10 | react | support | delegated | - | resolved | 25 | 2026-08-28 |
| 05 | Cedar research: composition strictness no-go | T18 | none | off_mission | assistant | - | resolved | 62 | 2026-08-28 |
| 06 | ESLint versioning semantics research | T18 | none | off_mission | unknown | - | resolved | 77 | 2026-08-28 |
| 07 | org size, obligations, currency | T1 | quantify | kernel | delegated | - | resolved | 23 | 2026-08-28 |
| 08 | pound seam: appetite, selection policy | T1 | compare | kernel | delegated | - | resolved | 31 | 2026-08-28 |
| 09 | cage ladder v2 decided | T5 | cage | kernel | delegated | - | resolved | 164 | 2026-08-28 |
| 10 | which steps run on clocks | T7 | react | support | delegated | - | resolved | 94 | 2026-08-28 |
| 11 | an org twin each, decided | T13 | react | support | delegated | - | resolved | 91 | 2026-08-28 |
| 12 | identity as spine, decided | T21 | none | off_mission | delegated | - | resolved | 106 | 2026-08-28 |
| 13 | lift or retire old mechanisms | T26 | none | off_mission | delegated | - | resolved | 120 | 2026-08-28 |
| 14 | insurance and insurer party decided | T16 | none | off_mission | delegated | - | resolved | 99 | 2026-08-28 |
| 15 | price every counted hole | T1 | quantify | kernel | delegated | - | resolved | 92 | 2026-08-28 |
| 16 | Flux verified at cluster boundary | T8 | enact | support | delegated | - | resolved | 84 | 2026-08-28 |
| 17 | twin follow-up record keeping | T27 | ceremony | ceremony | assistant | R | resolved | 115 | 2026-08-28 |
| 18 | publisher release under cages | T18 | none | off_mission | delegated | - | resolved | 105 | 2026-08-28 |
| 19 | misuse catalogue and portability | T24 | none | off_mission | delegated | - | resolved | 99 | 2026-08-28 |
| 20 | one demo of the ecosystem | T25 | presentation | off_mission | delegated | - | resolved | 100 | 2026-08-28 |
| 21 | build the feed contract | T10 | react | support | delegated | - | resolved | 41 | 2026-08-28 |
| 22 | prediction-market feed decided | T11 | react | off_mission | delegated | - | resolved | 102 | 2026-08-28 |
| 23 | news feed, headline skill decided | T11 | react | off_mission | delegated | - | resolved | 152 | 2026-08-28 |
| 24 | size beyond turnover per regime | T1 | quantify | support | owner_words | - | resolved | 134 | 2026-08-28 |
| 25 | build the pound seam | T2 | compare | kernel | delegated | - | resolved | 29 | 2026-08-28 |
| 26 | cage ladder lands, isolated rung | T5 | cage | kernel | delegated | - | resolved | 56 | 2026-08-28 |
| 27 | warn rung, bands per appetite | T5 | tolerance | support | delegated | - | resolved | 221 | 2026-08-28 |
| 28 | daily clocks, proposer, observation lane | T7 | react | kernel | delegated | - | resolved | 23 | 2026-08-28 |
| 29 | adopter twin overlay and evals | T13 | react | support | delegated | - | resolved | 46 | 2026-08-28 |
| 30 | twin agent's own cage decided | T15 | none | off_mission | delegated | - | resolved | 317 | 2026-08-28 |
| 31 | key-person sensor admission ethics | T15 | none | off_mission | delegated | - | resolved | 1109 | 2026-08-28 |
| 32 | identity substrate package built | T21 | none | off_mission | delegated | - | resolved | 29 | 2026-08-28 |
| 33 | lift three apps into adopters | T26 | cage | support | delegated | - | resolved | 260 | 2026-08-28 |
| 34 | handbook as compose-time render | T25 | presentation | off_mission | delegated | - | resolved | 324 | 2026-08-28 |
| 35 | scanner, spine, OSCAL placement decided | T12 | react | support | delegated | - | resolved | 147 | 2026-08-28 |
| 36 | insurer quote slice built | T16 | none | off_mission | delegated | - | resolved | 29 | 2026-08-28 |
| 37 | insurance round two decisions | T16 | none | off_mission | delegated | - | resolved | 41 | 2026-08-28 |
| 38 | priced holes in composition built | T2 | quantify | kernel | delegated | - | resolved | 88 | 2026-08-28 |
| 39 | supersede three refusal ADRs | T27 | ceremony | ceremony | delegated | R | resolved | 59 | 2026-08-28 |
| 40 | five-fact sample proves cage | T9 | evidence | support | delegated | - | resolved | 29 | 2026-08-28 |
| 41 | gitsign-verifying source controller | T8 | evidence | support | delegated | - | resolved | 29 | 2026-08-28 |
| 42 | widen Flux to tuppence, ludlow | T8 | enact | support | delegated | - | resolved | 29 | 2026-08-28 |
| 43 | first gate-determined policy release | T18 | none | off_mission | delegated | - | resolved | 47 | 2026-08-28 |
| 44 | ecosystem misuse catalogue graded | T24 | ceremony | off_mission | delegated | - | resolved | 70 | 2026-08-28 |
| 45 | switching cost by recomposition | T24 | quantify | off_mission | delegated | - | resolved | 562 | 2026-08-28 |
| 46 | forecast book, scorer, 2027 pilot | T17 | evidence | off_mission | delegated | - | open | 150 | 2026-08-28 |
| 47 | deck generated from captures | T25 | presentation | off_mission | delegated | - | resolved | 29 | 2026-08-28 |
| 48 | demo's remaining beats decided | T25 | presentation | off_mission | delegated | - | resolved | 407 | 2026-08-28 |
| 49 | build market-moves feed | T11 | react | off_mission | delegated | - | resolved | 29 | 2026-08-28 |
| 50 | build news feed, headline skill | T11 | react | off_mission | delegated | - | resolved | 29 | 2026-08-28 |
| 51 | supply-constraint path, scored headline | T11 | react | off_mission | delegated | - | resolved | 302 | 2026-08-28 |
| 52 | end-to-end seven-step harness | T22 | evidence | support | delegated | - | resolved | 29 | 2026-08-28 |
| 53 | release pushes tags not branch | T18 | ceremony | ceremony | assistant | R | resolved | 167 | 2026-08-31 |
| 54 | gate pins kyverno 1.18.2 | T20 | ceremony | ceremony | assistant | R | resolved | 55 | 2026-08-31 |
| 55 | clock reds are instrument faults | T22 | ceremony | ceremony | assistant | R | resolved | 129 | 2026-08-31 |
| 56 | truth run sees clock health | T22 | ceremony | ceremony | assistant | R | resolved | 208 | 2026-08-31 |
| 57 | feeds, insurer workflows register | T10 | react | support | assistant | R | resolved | 267 | 2026-08-31 |
| 58 | grill four gaps, untagged pin | T27 | ceremony | ceremony | delegated | - | resolved | 35 | 2026-08-31 |
| 59 | fall blocks; status derived | T22 | ceremony | ceremony | assistant | - | resolved | 441 | 2026-08-31 |
| 60 | lane samples land in number | T22 | evidence | support | assistant | R | resolved | 212 | 2026-08-31 |
| 61 | Renovate completes step two once | T10 | react | support | assistant | - | resolved | 131 | 2026-08-31 |
| 62 | feed parents pinned and signed | T10 | evidence | support | assistant | R | resolved | 315 | 2026-08-31 |
| 63 | unlabelled default flips isolated | T5 | cage | kernel | delegated | - | resolved | 769 | 2026-08-31 |
| 64 | twin for all three adopters | T13 | react | support | assistant | R | resolved | 337 | 2026-08-31 |
| 65 | enact guard closes git-dir | T23 | ceremony | ceremony | assistant | - | resolved | 208 | 2026-08-31 |
| 66 | deck grades its named run | T25 | presentation | ceremony | assistant | R | resolved | 99 | 2026-08-31 |
| 67 | record matches the surface | T27 | ceremony | ceremony | assistant | R | resolved | 452 | 2026-08-31 |
| 68 | federation peer (closed) | T21 | none | off_mission | delegated | - | closed | 23 | 2026-08-31 |
| 69 | untagged pin priced as hole | T4 | quantify | support | delegated | - | resolved | 300 | 2026-08-31 |
| 70 | observation lane detectively enforced | T22 | ceremony | ceremony | delegated | - | resolved | 51 | 2026-08-31 |
| 71 | which kyverno versions supported | T20 | none | off_mission | delegated | - | resolved | 271 | 2026-08-31 |
| 72 | feed bump re-renders twin artefacts | T10 | react | support | assistant | R | resolved | 162 | 2026-09-01 |
| 73 | verifier trust instant fix | T19 | evidence | support | assistant | R | resolved | 117 | 2026-09-01 |
| 74 | step 3 happens once, real | T7 | ratchet | kernel | assistant | - | open | 30 | 2026-09-01 |
| 75 | what is this for: purpose | T27 | ceremony | ceremony | owner_words | - | resolved | 200 | 2026-09-02 |
| 76 | every green rests on observation | T22 | ceremony | ceremony | assistant | R | resolved | 305 | 2026-09-02 |
| 77 | every pin checked for content | T19 | evidence | support | assistant | R | resolved | 295 | 2026-09-02 |
| 78 | proposer only tightens, signed | T7 | ratchet | kernel | assistant | R | resolved | 452 | 2026-09-02 |
| 79 | pound inputs published and current | T4 | quantify | support | assistant | - | resolved | 657 | 2026-09-02 |
| 80 | record matches code round two | T27 | ceremony | ceremony | assistant | R | resolved | 269 | 2026-09-02 |
| 81 | sampler wait-order round three | T9 | evidence | support | assistant | R | resolved | 297 | 2026-09-02 |
| 82 | licence, attribution, disclaimers | T27 | none | ceremony | assistant | - | resolved | 165 | 2026-09-02 |
| 83 | TRUTH line classifies measurement | T22 | ceremony | ceremony | assistant | R | resolved | 279 | 2026-09-02 |
| 84 | being behind costs: supersede pricing | T4 | quantify | support | assistant | - | resolved | 423 | 2026-09-02 |
| 85 | every clock green or explained | T22 | ceremony | ceremony | assistant | R | resolved | 155 | 2026-09-02 |
| 86 | cage enters the citable number | T9 | evidence | support | assistant | R | resolved | 665 | 2026-09-02 |
| 87 | forge enforces review rulesets | T23 | ceremony | ceremony | assistant | - | resolved | 358 | 2026-09-02 |
| 88 | second identity pavc-other-hand | T23 | ceremony | ceremony | owner_words | - | resolved | 49 | 2026-09-02 |
| 89 | deny is not a rung | T5 | cage | kernel | owner_words | - | resolved | 653 | 2026-09-02 |
| 90 | identity shelved for build | T21 | ceremony | ceremony | delegated | - | resolved | 154 | 2026-09-02 |
| 91 | currency controller un-retired | T8 | enact | support | delegated | - | resolved | 277 | 2026-09-02 |
| 92 | local clock runs Claude skills | T13 | react | support | owner_words | - | resolved | 418 | 2026-09-02 |
| 93 | twin derives a probability | T13 | quantify | support | delegated | - | resolved | 475 | 2026-09-02 |
| 94 | studied real firms behind adopters | T4 | quantify | support | owner_words | - | resolved | 57 | 2026-09-02 |
| 95 | record states the purpose | T27 | ceremony | ceremony | owner_words | - | resolved | 38 | 2026-09-02 |
| 96 | TRUTH line carries enact mode | T23 | ceremony | ceremony | assistant | R | resolved | 243 | 2026-09-04 |
| 97 | unrecorded mode flip goes red | T23 | ceremony | ceremony | assistant | R | resolved | 222 | 2026-09-04 |
| 98 | mutation-made refusal graded | T6 | cage | support | assistant | R | resolved | 462 | 2026-09-05 |
| 99 | adopter gate grades the change | T18 | none | off_mission | assistant | R | resolved | 311 | 2026-09-05 |
| 100 | branch runs record nothing | T22 | ceremony | ceremony | assistant | R | resolved | 388 | 2026-09-05 |
| 101 | adopter gate verifies real signature | T19 | evidence | support | assistant | R | resolved | 452 | 2026-09-05 |
| 102 | cited tree names check author | T27 | ceremony | ceremony | assistant | R | resolved | 344 | 2026-09-06 |
| 103 | ico gate computes bump cut | T18 | none | off_mission | assistant | R | resolved | 200 | 2026-09-06 |
| 104 | branch push cancels main run | T22 | ceremony | ceremony | assistant | R | resolved | 165 | 2026-09-06 |
| 105 | trust root verified offline | T19 | evidence | support | assistant | R | resolved | 530 | 2026-09-06 |
| 106 | composition selfcheck red fixed | T3 | quantify | support | assistant | R | resolved | 301 | 2026-09-08 |
| 107 | sampler waits for Kustomizations | T9 | evidence | support | assistant | R | resolved | 827 | 2026-09-08 |
| 108 | recording commit reds two checks | T22 | ceremony | ceremony | assistant | R | resolved | 348 | 2026-09-09 |
| 109 | map line checked against map | T27 | ceremony | ceremony | assistant | R | resolved | 146 | 2026-09-10 |
| 110 | supersede surcharge re-derives offline | T3 | quantify | support | assistant | R | resolved | 397 | 2026-09-10 |
| 111 | cage priority classes undelivered | T6 | cage | support | assistant | R | resolved | 317 | 2026-09-21 |
| 112 | threshold states its corpus | T14 | ceremony | off_mission | assistant | R | resolved | 292 | 2026-09-22 |
| 113 | infra declaration read nowhere | T6 | cage | support | assistant | R | resolved | 320 | 2026-09-22 |
| 114 | unobserved party not green | T22 | ceremony | ceremony | assistant | R | resolved | 181 | 2026-09-22 |
| 115 | loophole round is re-runnable | T24 | ceremony | ceremony | assistant | - | resolved | 182 | 2026-09-22 |
| 116 | twelve loophole candidates checked | T24 | ceremony | ceremony | assistant | R | resolved | 168 | 2026-09-22 |
| 117 | two tickets numbered 111 | T27 | ceremony | ceremony | assistant | R | resolved | 164 | 2026-09-22 |
| 118 | lucky green may not promote | T14 | ceremony | off_mission | assistant | R | resolved | 227 | 2026-09-22 |
| 119 | unlabelled namespace priced | T2 | quantify | support | assistant | R | resolved | 233 | 2026-09-23 |
| 120 | eighteen ADR-0026 candidates checked | T24 | ceremony | ceremony | assistant | R | resolved | 200 | 2026-09-23 |
| 121 | implemented control moves price, tier | T2 | ratchet | kernel | assistant | R | resolved | 186 | 2026-09-23 |
| 122 | ramp survives namespace rename | T3 | quantify | support | assistant | R | resolved | 237 | 2026-09-23 |
| 123 | regulator withdrawal not adopter's | T3 | quantify | support | assistant | R | resolved | 229 | 2026-09-23 |
| 124 | priced removal finally built | T2 | quantify | support | assistant | R | resolved | 166 | 2026-09-23 |
| 125 | test sees leaked signing key | T22 | ceremony | ceremony | assistant | R | resolved | 138 | 2026-09-23 |
| 126 | withdrawn control not selectable | T3 | quantify | support | assistant | R | resolved | 179 | 2026-09-23 |
| 127 | seam reads switching as regime | T3 | quantify | ceremony | assistant | R | resolved | 117 | 2026-09-23 |
| 128 | unreadable major ahead priced | T3 | quantify | support | assistant | R | resolved | 230 | 2026-09-23 |
| 129 | owner-accepted major record | T18 | none | off_mission | assistant | R | resolved | 140 | 2026-09-23 |
| 130 | composed root machinery delivered | T6 | enact | support | assistant | R | resolved | 337 | 2026-09-23 |
| 131 | adopter tag cut unblocked | T18 | ceremony | ceremony | assistant | R | resolved | 182 | 2026-09-24 |
| 132 | adopter gate reads acceptance | T18 | none | off_mission | assistant | R | resolved | 177 | 2026-09-24 |
| 133 | first recompose is fixed point | T3 | quantify | support | assistant | R | resolved | 98 | 2026-09-24 |
| 134 | clock data excluded from comparison | T18 | none | off_mission | assistant | R | resolved | 271 | 2026-09-24 |
| 135 | lifted app check was stale | T9 | evidence | ceremony | assistant | R | resolved | 199 | 2026-09-24 |
| 136 | two feeds one publisher vendored | T3 | quantify | support | assistant | R | resolved | 134 | 2026-09-24 |
| 137 | second feed verifies offline | T3 | quantify | support | assistant | R | resolved | 145 | 2026-09-24 |
| 138 | grader and composer as-of | T3 | quantify | ceremony | assistant | R | resolved | 134 | 2026-09-24 |
| 139 | priced before it existed | T3 | quantify | support | assistant | R | resolved | 147 | 2026-09-24 |
| 140 | fact 4 defaulted false | T9 | evidence | support | assistant | R | resolved | 145 | 2026-09-24 |
| 141 | adopter declares pricing grade | T13 | quantify | off_mission | delegated | - | resolved | 361 | 2026-09-25 |
| 142 | twin cage check, schedule gaps | T15 | none | off_mission | delegated | - | resolved | 208 | 2026-09-25 |
| 143 | twin sweep read-only split | T15 | none | off_mission | delegated | - | resolved | 193 | 2026-09-25 |
| 144 | twins price on comparable evidence | T13 | quantify | support | delegated | - | resolved | 107 | 2026-09-25 |
| 145 | platform prices twin agent cage | T15 | none | off_mission | delegated | - | resolved | 464 | 2026-09-25 |
| 146 | grader grades every engine | T20 | none | off_mission | delegated | - | resolved | 350 | 2026-09-26 |
| 147 | adopter declares its engine | T20 | none | off_mission | delegated | - | resolved | 285 | 2026-09-26 |
| 148 | unsupported engine pairing priced | T20 | none | off_mission | delegated | - | resolved | 82 | 2026-09-26 |
| 149 | policy line on two kyvernos | T20 | cage | off_mission | delegated | - | resolved | 134 | 2026-09-26 |
| 150 | ludlow runs kyverno 1.19.1 | T20 | none | off_mission | delegated | - | resolved | 129 | 2026-09-26 |
| 151 | cloud plane lands in tuppence | T26 | cage | off_mission | delegated | - | resolved | 146 | 2026-09-25 |
| 152 | fact 7 cannot pass, regrill | T9 | evidence | support | delegated | R | resolved | 87 | 2026-09-25 |
| 153 | CVE priced from own scan | T12 | react | support | delegated | - | resolved | 131 | 2026-09-25 |
| 154 | one repo per app transferred | T26 | none | off_mission | delegated | - | resolved | 113 | 2026-09-25 |
| 155 | lane runs served workloads (fact 8) | T9 | evidence | support | delegated | - | claimed | 105 | 2026-09-25 |
| 156 | incumbent org archive register | T26 | none | off_mission | delegated | - | claimed | 106 | 2026-09-25 |
| 157 | fact 2 null diagnosed | T9 | evidence | support | delegated | R | resolved | 36 | 2026-09-25 |
| 158 | baseline rung loosened runAsNonRoot | T6 | cage | support | delegated | R | resolved | 39 | 2026-09-25 |
| 159 | ungoverned tier label steers cage | T6 | cage | support | delegated | R | resolved | 44 | 2026-09-25 |
| 160 | never-looked fact is a fall | T9 | evidence | ceremony | delegated | R | resolved | 47 | 2026-09-25 |
| 161 | fact 7 re-registered with reference | T9 | evidence | support | delegated | R | resolved | 81 | 2026-09-25 |
| 162 | quote states illustrative scope | T16 | ceremony | off_mission | unknown | R | resolved | 37 | 2026-10-21 |
| 163 | pound wrapper judges every skip | T22 | ceremony | ceremony | codex | R | resolved | 30 | 2026-10-26 |
| 164 | six skills state their basis | T14 | ceremony | off_mission | codex | R | resolved | 44 | 2026-10-26 |
| 165 | declared ICO feed needs price | T3 | quantify | ceremony | codex | R | resolved | 90 | 2026-10-26 |
| 166 | orphan check reads default record | T22 | ceremony | ceremony | codex | R | resolved | 64 | 2026-10-26 |
| 167 | default record named by event | T22 | ceremony | ceremony | codex | R | resolved | 93 | 2026-10-26 |
| 168 | causal grade needs affirmative support | T14 | ceremony | off_mission | codex | R | resolved | 58 | 2026-10-27 |
| 169 | decay date boundary fix | T14 | ceremony | off_mission | codex | R | resolved | 36 | 2026-10-27 |

## Counts by loop role

| loop role | tickets | lines |
|---|---|---|
| ceremony | 45 | 7775 |
| none | 30 | 5728 |
| quantify | 27 | 6116 |
| evidence | 21 | 4697 |
| react | 19 | 2550 |
| cage | 12 | 3364 |
| presentation | 5 | 959 |
| enact | 4 | 727 |
| ratchet | 3 | 668 |
| compare | 2 | 60 |
| tolerance | 1 | 221 |

| necessity | tickets | lines |
|---|---|---|
| support | 61 | 13253 |
| off_mission | 50 | 9154 |
| ceremony | 45 | 7862 |
| kernel | 13 | 2596 |

## Tickets that exist only to repair, record or verify an earlier ticket

**80 of 169**, holding 17,226 of the 32,865 ticket lines. The tickets: 17, 39, 53, 54, 55, 56, 57, 60, 62, 64, 66, 67, 72, 73, 76, 77, 78, 80, 81, 83, 85, 86, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 152, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169.

From ticket 98 on, 56 of the 72 tickets are `R`. From early September, most of the tracker records the build fixing itself:

- Tickets 119 and 121 to 124 survived loophole rounds against the ticket 38 pricing build.
- Tickets 131 to 140 came out of the tools v3.3.0 rollout.
- Tickets 152 and 157 to 161 repair the five-fact and fact 7 instruments.
- Tickets 163 to 169 are Codex work from 2026-10-26 and 2026-10-27. They fix checks of checks and edge cases in the twin skills.

## Tickets closest to the loop, and the state of each

| step | tickets | state, with evidence |
|---|---|---|
| Q quantify | 07, 15, 24 (decided), 38 (built), 79, 84 (inputs) | Running. Each adopter serves `composed/evidence.json` with `prices[]`. Driftwood's ICO regime line is 1,787,177 GBP, tuppence's 17.9M, ludlow's 3.07bn (`driftwood/composed/evidence.json` prices[0]). The inputs are editorial: `REVIEW-2026-09-02.md:52` found "Every input that turns severity into money is editorial". Ticket 79 then added legal status per fine. |
| T tolerance | 08 (appetite moved onto party.yaml), 27 (assurance bands) | Running. `driftwood/party.yaml:52-60` holds tolerance 40,000 GBP and bands the owner adopted on 2026-10-23 (`issues/27` Answer; tuppence 15,000, ludlow 5,000). |
| C compare | 08, 25 | Running, at two levels. (1) `cages[]` holds per-workload recovery scenarios: 3 on driftwood, 1 each on tuppence and ludlow. All are far below band (7 to 26 GBP) at `isolated`, each with an owner-adopted "explicit isolated minimum" (`driftwood/composed/evidence.json:363-368`; tuppence `:356-361`; ludlow `:201-206`). (2) `floor_change.lines` runs every exposure line through the ladder (driftwood `:6204`, tuppence `:3761`, ludlow `:4210`). At `isolated` the ICO residual is 35,744 GBP for driftwood (tolerance 40,000), 358,159 for tuppence (15,000) and 61.4M for ludlow (5,000). The rung reductions are "self-declared calibration, not measured effectiveness" (driftwood `:6272`). |
| cage | 09, 26, 63, 89 | Served and tested offline. All three adopters are on policy 7.0.0 after the 158/159 fixes. The live TCP proof of the bottom rung, `platform/graded/verify-graded.sh`, is SKIP with class `never` on the hub clock (`_grades.tsv`, `verify-manifest.txt`). Facts 6 and 7 come only from adopter lane samples (tickets 152, 161). |
| R ratchet | 28, 78, 121, **74** | **Never happened.** The proposer runs daily and is clamped tighten-only (78). Ticket 74, the first real crossing and human merge, has been `open` since 2026-09-01. Every adopter Namespace has been `isolated` since 2026-08-28 (git blame `348b97c4`, driftwood `gitops/apps/namespace.yaml:30`), so no tighter notch exists. Ticket 121 (2026-09-23) made an implemented control move a price, but no tier has moved. The step-3 grade is a SYNTHETIC residual (`verify-manifest.txt`: `verify-e2e-step3 ... | simulation`). |
| E enact | 16, 41, 42, 130 | Observed on ephemeral KinD lanes only. `verify-e2e-step4` and the three `verify-reconcile` PASS lines grade the adopters' committed lane samples, class `self-proof` (`verify-manifest.txt`). No persistent cluster is graded. |
| X react | 21, 57, 61, 72, 153 | One real event. Ticket 61 records a Renovate feed bump (driftwood PR #20, threat-register v1 to v2) merged on 2026-09-01 as driftwood commit `27f1cf2`, after which the twin artefacts broke (ticket 72). The CVE line prices only on tuppence. Driftwood and ludlow read `could_not_look: No scanned CVE is in the pinned KEV feed` (`driftwood/composed/evidence.json`). The twin's derived probability has never reached main (`verify-derived-forecast` SKIP, run 491). |

## Questions still waiting on the owner (as of 2026-11-14)

44 tickets carry a `## Waits on the owner` heading, and most of those waits are spent. Live ones:

1. **Ticket 82: the disclaimer and named individuals.** The owner-reasoned item "[carry / do not carry]" a "not investment research" line is still a blank dated "2026-09-__" (`issues/82` tail). The named-individuals ruling was "still unanswered" in `issues/31` (2026-09-09), and nothing later answers it.
2. **Tickets 92 and 93: the first real runs on the owner's machine.** Both the local-clock run and the derive run are classed identity and money, so they are the owner's. Run 491 still grades `verify-local-clock` and `verify-derived-forecast` SKIP (`_grades.tsv`).
3. **Ticket 74: a real band crossing and a human merge.** It is HITL by type. Nothing in the record says how a crossing can happen while every adopter is on the bottom rung with an owner-adopted isolated minimum.
4. **Ticket 46: the 2027 pilot.** It is open, waiting on institutional model declarations, signed shadow contexts and pre-horizon registrations. Outcomes cannot exist before 2028-01-01 (`issues/46` tail).
5. **Ticket 97: the enactment window.** The `twin/ENACT_MODE` development window lapses on 2027-01-01, and only the owner can renew it (`issues/97`, "Owner renewal, 2026-10-22").
6. **Ticket 48: the hub release asset.** The pitch mp4 is meant to become a hub release asset, and "the hub has no releases". I could not check the current state, because the rules forbid network access.
7. **Ticket 70: going private.** Taking the repos private is a recorded revisit trigger and an authorisation. It is optional.
8. **Fog lines on the map.** `map.md` lists under "Not yet specified": the identity lane, a shared adopter package, named executives in a public corpus, and pound beats on the deck. These are purpose and identity calls.

Verified as spent:
- Ticket 64's signed sizes for tuppence and ludlow now exist (`tuppence/party.yaml:21-22`, `ludlow/party.yaml:22-23`).
- The policy 4.0.0 major acceptance (tickets 99, 101, 105) was overtaken by ticket 129's `accepted-majors/` record and by 4.0.0's retirement in ticket 113.
- The claimed tickets 155 and 156 wait on scheduled observations, not on the owner.

## What the loop would lose if this area vanished

Nothing at run time. This area is records. The code that prices, cages and proposes lives in platform and the adopters. The loop would lose:
- The reasons behind its kernel decisions: appetite as a signed fact on `party.yaml` (08), every hole priced and never refused (15, 38), the ladder with its isolated bottom rung (09, 26), and the owner's "mutating, not denying" rule (89, from `issues/75` Q5).
- The one plain statement that the ratchet has never fired (74), and the review line that every adopter sits on the bottom rung (`REVIEW-2026-09-02.md:52`).

The rest record the gate, its records, the twin's governance, engine compatibility and repairs: the 156 tickets not marked `kernel`, together with the 12 top-level files. Without them the loop runs exactly as it does now.

## The simplest thing that would do this area's loop job

The area's job is to say what the loop is, why, and what state each step is in. One file would do it:

- **`LOOP.md`, about 150 lines**, holding:
  - **A step table** of 6 rows: step, file that does it, check that grades it, last observed date and state. For example, "R | adopter `propose-tier.yml` | verify-e2e-step3 | never (synthetic only)".
  - **A decision table** of about 15 rows: the kernel decisions from 07, 08, 09, 15, 26, 27, 63 and 89, each with date, who decided (owner, or delegated) and one sentence of reason.
  - **An open list** of at most 8 items: the live owner waits above, and "no headroom: all adopters at isolated".

That replaces 169 tickets, 32,865 lines. The repair history lives in git and PR descriptions.

For the loop itself, the matching minimal build would be:
- `loop.py`, about 250 lines. It reads `party.yaml` (size, tolerance), the signed penalty, CVE and KEV feeds, and `ladder.yaml`. It prices exposure at each rung, picks the loosest rung whose residual is within tolerance (or the strictest, flagged "still above tolerance"), and opens a PR changing one Namespace label.
- `ladder.yaml`, about 40 lines: 4 rungs, each with dials and a reduction.
- One Kyverno MutatingPolicy, about 100 lines, that applies the dials by label.
- Flux to reconcile it, plus a 40-line check that the served label equals `loop.py`'s output.

## Surprises

- **The loop has had no headroom since day one.** Ticket 26 declared every adopter `isolated` on 2026-08-28. The 2026-09-02 review saw it (`REVIEW-2026-09-02.md:52`). Ticket 74 still waits for a real crossing 74 days later. The cage decisions now carry an owner-adopted "explicit isolated minimum" (`driftwood/composed/evidence.json:363-368`). The ratchet has no tighter notch to propose. Enact still runs, but it has only ever re-applied the same rung.
- **The loop cannot finish for two of the three adopters.** At the bottom rung, tuppence's ICO residual is 358,159 GBP against a tolerance of 15,000, and ludlow's is 61.4M against 5,000 (`floor_change.lines`, tuppence `evidence.json:3761`, ludlow `:4210`). Under the mission's terms the cage alone cannot bring them within tolerance. Nothing in the tickets says what happens next: transfer, a fifth rung, or accepting the exposure.
- **Large numbers beside the cage.** The twin line on tuppence is 84.2M GBP uncaged and 1.68M at `isolated` (`tuppence/composed/evidence.json` prices[4], floor_change). Driftwood's insurance premium, 113,403 GBP, is almost three times its tolerance.
- **The largest ticket is off-mission.** Ticket 31 (sensor admission for a key-person scenario) runs to 1,109 lines and 7 review rounds. Ticket 107 (sampler wait order) runs to 827.
- **Stale counts.** `map.md:370` says "162 total" (2026-10-23). There are 169 files: 164 resolved, 2 claimed, 2 open, 1 closed.
- **The tracker polices itself.** Two tickets were numbered 111. That produced ticket 117 and a check (`verify-derived-status`) that every number names one file. Tickets 102 and 109 check that tickets cite TRUTH lines and map lines correctly.
- **The ratification vocabulary changed mid-stream.** Tickets 04 to 24 were marked PROVISIONAL on a bare "agree" ("ive already read the recommendations and I can't find fault with a single one", 2026-08-28). ADR-0025 (2026-09-02) then retired "provisional" and relabelled such answers as delegated.
- **The October style is different.** Codex-era Answers ("Delivery reconciled", "privately verified software capability", "genuine", "actual") are long qualification paragraphs. Ticket 155 is still `claimed` after a 2026-10-23 entry that cites "1,160 prior raw objects and 256 full observation byte/blame records" of conservation proof.
- **Gate classes.** In run 491, only 42 of 117 passes are `observed`; 61 are `self` (`hub/talk/truth.log`, last line).

## Could not determine

- **Origin of ticket 06.** The ESLint instruction it quotes is the owner's, but undated.
- **Origin of ticket 162.** It was born 2026-10-21 in the Codex era, but no `codex/` branch is tied to it.
- **Whether the proposer clock really fires daily.** Only ticket 74's text says so, and `verify-schedules` is SKIP in run 491.
- **Current archive and hub-release state** (tickets 48, 156). The rules forbid network access.
- **Status of T25, T26 and P1 to P3.** No check in `_grades.tsv` maps cleanly to them.
- **Whether the code matches each ticket Answer.** This area is tickets only. Code was read only where cited above.
