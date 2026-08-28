# 08 — The pound seam

Type: grilling (HITL)
Status: resolved
Blocked by: none

## Question

The seam between intelligence and enactment. The twin computes a cage tier under the org's declared perspective; the estate enacts it. Settle: which engine is the eco-system's £ (twin prices a shock under a perspective; estate prices annualised residual against appetite; one converts into the other, how); how the twin's trade-off curve terminates in a cage spec via a versioned, published selection policy; what the twin emits (a signed forward-intel artefact) and what `evidence.json prices[]` consumes; one currency, many perspectives, labelled; how `fair.py` gains the twin's heavy tail or states its bound.

## Notes

Re-grills 21, 33, 34; findings H3-01, H1-13, H3-10; GAPS 0.3, 0.4.

## Answer

Resolved 2026-08-28. Grilled in one round of seven questions. The owner answered "Lgtm". No reason was stated. Under the map's process rule the seven decisions are recorded with the owner's word verbatim and the recommendation's reasoning as the recorded rationale. The daily budget of five decisions was already spent by tickets 04 and 07 before this round; the owner answered on the day anyway, and that is recorded here.

Facts found first: two engines, no import between them; `graded/cage.py` selects the first tier under a scalar `tolerance` from unsigned `risk/appetite.json`; every `prices[]` entry is `changed: false` and `cages[]` is empty on all three adopters; the phrase "forward intel" appears in no twin code; `fair.py` is bounded beta-PERT (H3-10); the PR edits the pod label, not the composed declaration (ticket 09's ground).

1. **Which engine is the £.** The twin emits a scenario under a perspective. `fair.py` annualises it against appetite and selects. The twin has no frequency, so it cannot annualise; `fair.py` is wired to `prices[]` and the proposer. GAPS 0.4's wording ("the twin's Monte Carlo produces the tier number") is corrected: the twin produces the scenario, the estate produces the tier.
2. **What the twin emits.** A forward-intel artefact is an ADR-0019 feed: `kind: feed`, `name: forward-intel`, published into the adopter's own repo, signed by the adopter's twin agent identity. Payload: `{perspective, shock, horizon, lef: triple | null, lm: triple | severity spec, currency, curve: [{account, net_cost_of_risk}]}`. A null `lef` means the subscribed pricing feed supplies frequency. No `recommended action` field, ever.
3. **How `prices[]` consumes it.** A new pricing parent edge, `source: twin`, gives its own `prices[]` entry. One entry per source keeps provenance readable.
4. **The selection policy.** The curve never picks. The adopter publishes `selection-policy` as its own semver package in its own repo. Version 1 is the existing rule (first tier whose caged residual is under tolerance) plus the name of the account it selects under. Renovate pins it. The proposal PR carries the policy version and the curve hash.
5. **Appetite is a signed fact.** `appetite: {tolerance: {amount, currency}}` moves onto each adopter's `party.yaml`, signed by the adopter alone, next to `size`. `platform/risk/appetite.json` is retired.
6. **Labelling.** Every `prices[]` entry and every twin payload carries `perspective` and `currency`. The estate's own regime prices carry `perspective: <adopter>`. No sum crosses perspectives.
7. **The tail.** `summarize()` output gains `tail`, `bounded-pert` today. When a payload supplies `lm` as `{model: lognormal-gpd, mu, sigma, u, xi, beta}`, `fair.py` dispatches to `twin/severity.py` and `tail` names it.

Defaults set without a decision, open to challenge: `horizon` is one year and is stated in the payload; the twin re-emits on its schedule (NORTH-STAR principle 5) and on a new signed feed version.

Graduated: ticket 25 (build the £ seam). ADR-0021 records engine and seam. CONTEXT.md gains Perspective, Forward intel, Selection policy, Price, Appetite. Unblocked: tickets 09 and 11.
