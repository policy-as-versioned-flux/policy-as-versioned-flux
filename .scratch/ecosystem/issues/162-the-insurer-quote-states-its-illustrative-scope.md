# 162 — The insurer quote states its illustrative scope

Type: task (AFK)
Status: claimed
Blocked by: 37, 75

## Question

Deliver the disclosure that [ticket 75 Answer 4](75-grilling-what-is-this-for-the-twelve-questions.md) requires **on the quote**: the insurer is an illustrative counterparty under an ordinal, auditable comparison model. The quote must state plainly that it is a demonstration/model artefact and supplies no real insurance cover, payable-claim determination or independent actuarial second opinion. This implements the existing accepted scope; it does not upgrade formula 1, invent a carrier, change a price or backdate a declaration.

The statement is currently **MISSING** from all three quote-1 JSONs under the genuine insurer `v1.0.0` carrier and from their current JSON counterparts. The party and README demonstration qualifier is outside those quote artefacts. Ticket 37's four original decisions are separate and now recorded; this is a concrete later disclosure defect, not an additional original-37 completion bar.

## Required delivery

1. **The actual public emitter and closed contract.** Repair insurer `pricing/quote.py`'s real `show` and `render` routes so their emitted quote payload carries a plain truthful illustrative/ordinal/no-real-cover statement. Extend the actual closed quote payload schema for that supported version and validate the produced artefact. A README-only sentence, an unconsumed helper result or prose added only to a PR body is insufficient. Choose the exact field/schema migration and normal computed release version only after inspecting and recording the concrete implementation plan; no future `v2` tag or target is assumed here.
2. **Public CLI evidence and conservation.** Preserve a real public-CLI RED for the missing disclosure, then GREEN through the same `show`/`render` seams. Use isolated, genuinely bound financial source inputs and compare their exact outputs: existing amounts, currencies, formula/rates/load, attachment/limit, exclusions, conditions, validity and `priced_against` remain unchanged apart from the explicitly reviewed disclosure/schema/release metadata. Missing totals, stale bases, refusal/unknown paths and deferred actuarial scope retain their meanings. Do not fabricate a financial input, normalize away a difference or use a new observation as billing/transfer credit.
3. **Normal versioned delivery.** Obtain independent source/title/full-body reviews and actual configured CI, publish through the ordinary signed release workflows and verify the genuine resulting artefacts. Deliver any necessary compatible schema/consumer changes and ordinary adopter pin/re-render changes through their normal review and release paths. All three published quote artefacts must carry the disclosure in the supported new contract. Availability of three quote feeds is not three current cover adoptions; do not add a new subscription merely to claim that. Preserve the legacy `v1` payloads, raw tags, signatures and historical replay unchanged. No release/tag/SHA may be filled in before it exists.
4. **Truthful completion record.** Wire or update the relevant registered quote check to read the public artefact's disclosure, with a meaningful missing-statement negative control. Record the genuine source/release/adopter outcomes and their limits. Existing repricing PRs and their original signed sources/failures remain intact; inspect each on its own exact head rather than merging old proposals blindly. A current unknown, expired quote or missing-instrument refusal stays visible. No new premium, validity extension, insurer financial authority, payable claim, actual transferred loss or actuarial upgrade follows from adding this disclosure.

## Notes

Opened 2026-10-21 under ADR-0025 delegation after independent Standards and Spec scope audits of ticket 37. The disclosure requirement originates in ticket 75 Answer 4. Both audits found the four bounded ticket-37 choices resolvable while identifying this separate missing on-quote statement. Implementation, CI, signed publication and any required adopter delivery remain outstanding; the label is MISSING until that evidence is actually delivered.
