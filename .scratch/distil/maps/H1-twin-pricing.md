# H1: hub twin pricing and model core

Repo: FRESH/hub (clone taken 2026-11-14). Paths are relative to `hub/twin/` unless a repo is named.

## Summary

- 26 files and 6,087 lines: the 22 named files (5,300 lines), plus 4 arithmetic siblings: `evidence.py` 423, `admission.py` 128, `scoring.py` 167 and `calibration.md` 69. `corroboration.py` (425) and `synthetic.py` (197) are gate dependencies of `pricing.py`. They are listed as uncounted.
- The hub's money formula is `pricing.price()`: declared valuation × propagated influence, behind six refusal gates. **No adopter calls it.** The money that reaches the estate is computed inline in each adopter's `twin/emit-forward-intel.py`. It uses one edge, does no propagation and does no prefilter. From the hub it imports only `Overlay`, `evidence`, `valuation.rederive` and `CAUSAL_EDGE` (driftwood/twin/emit-forward-intel.py:98-101,212).
- **A cage tier is not an input to the hub formula.** In the adopter formula a tier enters only as an authored `response` (`run-the-<svc>-at-<tier>`). All 12 such responses across driftwood, tuppence and ludlow carry `mitigates.evidence_grade: 5`, so the credited reduction is 0. Each published curve therefore rises with every tighter rung: tightening the cage costs money and buys nothing (driftwood/twin/forward-intel/v2/feed.json: 8,183.78 → 95,183.78).
- **No financial tolerance or appetite is read anywhere in this area.** The only "appetite" read is `appetite.pricing_threshold`, which is an evidence-grade threshold of 2 or 3, not money (evidence.py:57-58, pricing.py:35-42). "Appetite band" appears once, as prose (enforcement-grades.yaml:66).
- **No frequency here.** The area produces a per-shock magnitude. Annualising it (`lef`) is borrowed from a subscribed feed and done in platform `fair.py` (driftwood/twin/emit-forward-intel.py:300-305).
- Roughly 2,100 of the 6,087 lines are off the money path: severity/TVaR, positions/scoring, regimes/primitives, affected parties, the constraint ethics floor, the regrade audit, and roles/decay vocabularies.
- Everything has a unit test. `demo.sh` (run in CI by .github/workflows/twin.yml:87) exercises `price`, `propagate`, `options`, `exposure`, `severity` and `regimes` against the synthetic netflix fixture. Only `valuation.py` and `Overlay.load` have a recorded real-org output: the committed adopter feeds.

## The money formula, as implemented

### A. The hub formula: `twin price` (pricing.py:199-407), which no adopter calls

For one shock origin O, one perspective P, and each component C the shock reaches:

```
influence(C)   = PERT triple of the PRIMARY path only (pricing.py:223)
               = (Π elasticity triples along the path, point-wise min/mode/max)   propagate.py:296-298
                 × attenuation factor(depth)  {1.0, 0.8, 0.6, 0.4; none past depth 4}   attenuation.yaml:22-43
price(C)       = P.values[C].amount × influence(C)            point-wise on min/mode/max, pricing.py:155-167
credit(option) = price_attenuated(C_claimed) × mitigates.reduction   point-wise, pricing.py:402-406
net(option)    = cost.mode − credit.mode                       tradeoff.py:67-74
```

Each impact is refused, and becomes a register entry with no figure, when any one of these holds:
- the path is directional-only;
- it rests on a synthetic record;
- the worst hop grade is above the threshold;
- P declares no valuation;
- the valuation grade is above the threshold;
- no graded path reaches one of P's declared cash flows.

These refusals are at pricing.py:228-287. Credit is refused when there is no claim, the claim grade is above the threshold, the claim rests on a synthetic record, there is no corroborated enactment (`corroboration.state`), or nothing was priced at the claimed component (pricing.py:337-390).

Three things in this formula are worth noting:
- The noisy-OR `joint` that propagate.py computes over every path (propagate.py:387-500) is **never read by pricing**. Only the primary path prices.
- The PERT sampled spread is reported but not used in the price.
- The CLI verb `verbs.price` loads the overlay without the party's declared threshold (twin/verbs.py:598). It always prices at the ladder default of 2. Only the signal_inputs/task_inputs paths pass `declared_threshold` (signal_inputs.py:203, task_inputs.py:230).

### B. The formula that reaches the estate: adopter emitter (driftwood/twin/emit-forward-intel.py:181-206, 257-266)

```
base   = party.size.turnover.amount × share_of_turnover / periods_per_year   (valuation.py:33; FX via a signed feed when currencies differ, valuation.py:42-62)
lm     = base × elasticity[min, mode, max] of the ONE causal edge into the cash flow   (emit-forward-intel.py:266)
impact = base × elasticity.mode
curve[tier] = impact × (1 − reduction_mode_if_grade≤threshold_else_0) + cost_mode(tier response)   (emit-forward-intel.py:200-205)
lef    = null   (frequency borrowed from the subscribed `threat-register` feed, annualised in platform fair.py)
```

Worked driftwood example (v2 feed): 86,000,000 GBP × 0.14884 / 4 = 3,200,000. Then 3,200,000 × 5.743e-5 = 183.78 per shock. Reduction is 0 at grade 5, so curve = 183.78 + {8,000; 20,000; 42,000; 95,000}.

| input | unit | source | measured or assumed |
|---|---|---|---|
| turnover | GBP/yr | driftwood/party.yaml `size.turnover`, signed | declared filing figure (the adopter is fictional; `valuation.py` checks that the derivation matches to within 1) |
| share_of_turnover, periods_per_year | ratio, count | perspective `values` (driftwood/twin/orgs/driftwood/perspectives/driftwood.yaml) | authored; the basis says "management-accounts split", grade 2, with no audit record |
| elasticity triple | fraction of the cash flow lost per shock | driftwood/twin/orgs/driftwood/edges/cart-pii-loss-cuts-checkout-revenue.yaml | **assumed**: grade 3, a "published comparable anchor, not an observed revenue suppression" (an ICO/DSG penalty divided by Currys group revenue) |
| reduction per tier | fraction | responses/run-the-checkout-at-*.yaml `mitigates` | **assumed and withdrawn**: grade 5, "Unmeasured calibration … withdrawn by ticket144", so it prices as 0 |
| cost per tier | GBP | the same response files, `cost` triple | **assumed**: no evidence_grade field and no basis on cost |
| currency | ISO code | adopter `twin/currency.yaml` (not in the twin schema; perspectives/driftwood.yaml note) | declared |
| FX rate | ratio | signed `feeds` fx release (valuation.py:42-65) | measured if a non-illustrative release is pinned; the emitter refuses illustrative rates (emit-forward-intel.py:236-237) |
| frequency (lef) | events/yr | not here; the subscribed feed | out of area |

**Is a cage tier an input?** In formula A, no: `enforcement-grades.yaml:9-15` explicitly refuses a number per rung, and tiers appear nowhere in pricing.py. In formula B, yes, but only as a lookup key for an authored response with a cost and an ungraded reduction. **Is tolerance read?** No, in either formula.

## Components

| name | paths | lines | born | what it does | loop role | necessity | origin | status | cite |
|---|---|---|---|---|---|---|---|---|---|
| Price join and mitigation credit | pricing.py | 514 | 2026-08-07 | Multiplies a perspective's declared valuation by the primary path's influence triple, behind six refusal gates, and credits responses by graded, enactment-corroborated reduction claims | quantify | duplicate (the live £ is computed inline in the 3 adopter emitters, driftwood/twin/emit-forward-intel.py:181-266) | owner_words for perspectival £ (.scratch/twin/issues/09-currency-regimes.md:36-37, 2026-08-05); gates and credit are assistant | tested_offline | pricing.py:199-324, 327-407; demo.sh:182 |
| Valuation re-derivation and FX | valuation.py | 66 | 2026-10-03 | Re-derives a valuation from the signed party turnover × share ÷ periods; converts currency only through a pinned FX envelope | quantify | kernel (the only hub arithmetic on the live £ path) | unknown (born in commit 6ed89616 "Resume Claude ecosystem handoff", 611 files; October epoch) | observed_running | valuation.py:19-66; called at driftwood/twin/emit-forward-intel.py:212-246; output in driftwood/twin/forward-intel/v2/feed.json `valuation` |
| Causal propagation and attenuation | propagate.py, attenuation.yaml | 724 | 2026-08-06 | Enumerates simple causal paths (depth ≤5, ≤32 per target); composes elasticity triples, attenuates by depth, Monte-Carlo samples, and noisy-OR joins paths with inclusion-exclusion | quantify | support (the live path uses one edge at depth 1, factor 1.0; the joint is never read by pricing) | assistant (decision ticket 08) | tested_offline | propagate.py:503-633; joint 387-500; pricing.py:223 reads the primary path only |
| Blast radius | blast.py | 213 | 2026-08-06 | Reverse-dependency traversal splitting reached components into priceable-causal vs unpriced-structural | quantify | support (feeds admission.py:100; shown in the demo) | assistant ("inherited from /arckit:impact", blast.py:3) | tested_offline | blast.py:1-19; demo.sh:83 |
| Cash-flow admission gate | admission.py | 128 | 2026-08-06 | Admits an impact to the £ only if a graded causal path reaches a declared cash flow | quantify | support | assistant (09 Q4 option "(c)" chosen in grilling, no verbatim quote) | tested_offline | admission.py:1-25, 65 |
| Evidence ladder and thresholds | evidence.py:1-302, evidence-ladder.yaml | 406 | 2026-08-06 | Five evidence grades; pricing threshold 2 (party may declare 3); `may_price`, `weakest` order statistic | quantify | support (this gate is what the adopter emitter keeps: emit-forward-intel.py:167,201) | assistant | tested_offline | evidence-ladder.yaml:35,52; evidence.py:57-58,148,231 |
| Regrade chain audit | evidence.py:303-423 | 121 | 2026-08-06 | Checks that every grade change in git history has a recorded regrade | ceremony | ceremony | assistant | tested_offline | evidence.py:332-423 |
| PERT triples and calibration procedure | pert.py, calibration.md | 339 | 2026-08-06 | min/mode/max triple with Beta moments, raw moments, seeded sampling; requires calibration.md's steps by name | quantify | support (used by price; the adopter uses only `.mode`) | assistant (decision ticket 08 Q1, "Hubbard calibration") | tested_offline | pert.py:99-226 |
| Response costing and constraint prefilter | options.py | 310 | 2026-08-06 | Removes responses that cross a constraint before costing; samples each survivor's cost triple | ratchet (costs candidate responses) | support (no adopter calls it) | owner_words for constraints-before-prices (09:58-59 "(human, 2026-08-05)", paraphrase in bold, not verbatim) | tested_offline | options.py:157-262; demo.sh:161 |
| Constraint set (ethics floor, exclusions, positions) | constraints.py, constraints.yaml | 463 | 2026-08-06 | Publishes a universal floor (no special-category data, no covert sensing, no individual attribution, **no automatic enactment**, no ruin option), scope exclusions and positions | none | off_mission (governs the twin's ethics towards people, not the cage loop) | owner_words (09:58-79, human 2026-08-05) | tested_offline | constraints.yaml:22-88; no-automatic-enactment at :62-69 |
| Trade-off curve across rival accounts | tradeoff.py | 251 | 2026-08-10 | Runs pricing once per rival causal account; net = cost − credit per response; marks a mean-lowest default and flags disagreement | ratchet (chooses among responses) | duplicate (the adopter `curve()` plus selection_policy does the live tier choice, driftwood/twin/emit-forward-intel.py:181-206) | assistant (09 Q3 option "(c)", no quote) | tested_offline | tradeoff.py:59-130; beat-netflix.sh:145 |
| Heavy-tailed severity, TVaR, anchoring | severity.py, anchoring.py, severity-anchors.yaml | 561 | 2026-08-10 | Lognormal body spliced to a GPD tail, closed-form TVaR, loss-exceedance curve; two-point fit from Cyentia IRIS quantiles (xi and beta unanchored) | quantify | duplicate (the estate uses platform/fair/severity.py, 80 lines); unwired here: "no severity slot" (pricing.py:12) | assistant (research 02 / decision ticket 09) | tested_offline | verbs.py:1469-1545; demo.sh:266; severity-anchors.yaml:52-80 |
| World/overlay model loader | model.py | 844 | 2026-08-05 | Loads world + org overlay at pinned commits, validates 14 collections, builds the typed graph, holds the party threshold, enforces the world→overlay direction rule | quantify (supplies every input) | kernel (adopters call `Overlay.load`) | assistant (decision ticket 07) | observed_running (via the adopter emitters) | model.py:131-200, 495-545; driftwood/twin/emit-forward-intel.py:343 |
| Rival world-model positions and forecast scoring | positions.py, scoring.py | 312 | 2026-08-10 / 2026-08-06 | Deltas between believed, rival and revealed positions; Brier and log-loss scoring; reliability diagram | evidence (model skill) | off_mission (nothing on the money path reads it) | assistant (decision tickets 07, 11) | tested_offline | positions.py:1-23; scoring.py:47-129 |
| Time and intervention primitives, information regimes | primitives.py, regimes.py | 617 | 2026-08-07 | Rewind to a commit, do() vs observe(); as-consumed / as-knowable / with-hindsight backtest gating | none (backtest research) | off_mission | owner_words for layered hindsight (.scratch/twin/issues/13-scenario-gameplay-engine.md:74, 2026-08-05) | tested_offline | regimes.py:1-41; primitives.py:1-33; demo.sh:45 |
| Affected-parties register | affected_parties.py | 79 | 2026-08-12 | Aggregates the outsiders each scenario names; prices nothing | none | off_mission | assistant (decision ticket 15) | tested_offline | affected_parties.py:1-30 |
| Cage rung vocabulary | enforcement-grades.yaml | 70 | 2026-08-15 | observe/warn/constrain/block rungs with Kyverno realisations; explicitly prices nothing | cage | support (read by enforcement.py; a different vocabulary from the adopters' baseline/restricted/quarantine/isolated LADDER) | assistant (decision ticket 18 Q4) | unknown | enforcement-grades.yaml:9-15, 22-70; driftwood/selection-policy/selection_policy.py:43 |
| Unbound-signal decay | decay.yaml | 31 | 2026-08-12 | 180-day half-life for signals not yet bound to the graph | react | support | owner_words (.scratch/twin/issues/11-sense-move-loop.md:77, "(human," 2026-08) | unknown (reader unbound_pool.py is out of area) | decay.yaml:21-31 |
| Signing role register | roles.yaml | 38 | 2026-08-11 | Six roles a signature binds to (model-steward, worksheet-author, challenger …) | ceremony | ceremony | assistant (decision ticket 15) | unknown (reader sign.py is out of area) | roles.yaml:10-38 |

Line check: 514+66+724+213+128+406+121+339+310+463+251+561+844+312+617+79+70+31+38 = 6,087.

## What the loop would lose if this area vanished

- **Q (quantify):** `valuation.rederive` and `Overlay.load` (with `evidence.may_price`), which the three adopter emitters import. Without them each emitter would need about 40 lines of its own: read the YAML, multiply turnover × share ÷ periods, check the grade, convert FX. Nothing else in the area is on the path that produces the published £.
- **T (tolerance):** nothing. No money tolerance is read here.
- **C (compare):** nothing. No exposure is compared with anything here.
- **R (ratchet) and E (enact):** nothing live. `options.py` and `tradeoff.py` model choosing among responses, but the live tier choice is the adopter selection policy. `constraints.yaml` actually forbids automatic enactment (constraints.yaml:62-69).
- **X (react):** a decay half-life (decay.yaml), read elsewhere.
- About 2,100 lines could vanish with no effect on any published figure: severity/anchoring 561, positions/scoring 312, primitives/regimes 617, affected parties 79, constraints 463, regrade audit 121. The hub `pricing.py`, `propagate.py`, `blast.py`, `admission.py` and `tradeoff.py` (2,030 lines) are a more rigorous version of a calculation the estate does not run. Losing them would remove the multi-hop, multi-path, enactment-gated pricing that was designed but never connected to the estate.

## The simplest thing that would do this area's loop job

One file, `exposure.py`, about 60 lines, plus one YAML table per org:

```yaml
# exposure.yaml (per org)
cash_flow: {amount_from: party.size.turnover, share: 0.1488, periods: 4, grade: 2}
threats:   # one row per loss path
  - id: cart-pii-exfil
    loss_fraction: {min: 2.87e-5, mode: 5.74e-5, max: 5.74e-5, grade: 3, source: <url>}
    frequency_from: feeds/threat-register@vN
tiers:     # one row per cage notch, loosest first
  - {tier: baseline,   cost: 8000,  reduction: 0.0, grade: 5}
  - {tier: restricted, cost: 20000, reduction: 0.3, grade: 5}
```

```
def exposure(org) -> money: base × loss_fraction × frequency, one line per threat, summed
def residual(org, tier) -> money: exposure × (1 − reduction if grade ≤ threshold else 0) + cost
```

The table covers turnover, loss fraction, frequency, per-tier cost and reduction, and a grade per number. The two functions take about 25 lines, plus about 15 for the grade gate and 20 for FX. This is what the three emitters already do inline, made explicit. Tolerance and compare belong next to this file (`if residual > appetite: ratchet`), not in the twin.

## Surprises

1. **The hub's pricing engine is not on the live path.** `pricing.price`, `propagate`, `options.prefilter` and `tradeoff` are imported by no adopter (driftwood/twin/emit-forward-intel.py:98-101). The published £ is about 25 lines of inline arithmetic per adopter, which keeps only the grade gate. The enactment-corroboration and synthetic-record gates that pricing.py:362-385 makes so much of are not applied to any published figure.
2. **Tightening the cage never pays.** All 12 tier responses are grade 5, so every published curve is impact + rung cost, rising monotonically: driftwood 8,183.78 → 95,183.78; ludlow 4,907,554.7 → 4,922,054.7; tuppence 7,955,955 → 7,970,455 (`*/twin/forward-intel/v*/feed.json`). driftwood v1 had falling curves (372,800 → 133,400) before ticket 144 withdrew the reduction evidence. The ratchet currently has no money justification anywhere.
3. **Driftwood's impact fell by about 2,000×** between feed v1 (lm mode 384,000) and v2 (lm mode 183.78) when the elasticity was re-anchored to one ICO penalty divided by Currys group revenue (edges/cart-pii-loss-cuts-checkout-revenue.yaml note).
4. **Two cage vocabularies.** enforcement-grades.yaml has observe/warn/constrain/block; the adopters' selection policy has baseline/restricted/quarantine/isolated (driftwood/selection-policy/selection_policy.py:43). Nothing here maps one onto the other.
5. **"Accounts" means two different things.** In tradeoff.py an account is a rival causal account. In the adopter `curve()` it is a cage tier (`{"account": tier, …}`, emit-forward-intel.py:205).
6. **Severity is built twice and wired once.** Hub severity.py, anchoring.py and severity-anchors.yaml (561 lines) are a standalone verb that pricing deliberately refuses (pricing.py:12-18). The estate's copy is platform/fair/severity.py (80 lines), and the adopter emitter emits a bounded triple, not a GPD spec (emit-forward-intel.py:262-265).
7. **The CLI `twin price` ignores the party's declared threshold** (verbs.py:598 calls `Overlay.load(repo, org)` with no `pricing_threshold`). The adopters' grade-3 edges would be refused by the hub verb and are priced by the emitters.
8. **The universal floor forbids automatic enactment** (constraints.yaml:62-69, "the twin proposes only"). That sits in tension with a reactive cage that tightens itself. The tension is resolved by keeping enactment outside the twin.
9. pricing.py is 38% docstring and comment lines (193 of 514, measured with ast), before counting its long refusal strings. These carry ticket and ADR numbers, and the body-key allow-list (pricing.py:131-147) means any new field requires "an authorising decision ticket".
