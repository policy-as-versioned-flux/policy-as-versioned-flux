# 30 — Response pricing and evidence-graded mitigation credit

**What to build:** Candidate **responses** priced in the same unit as impacts, so an HR lever, a security control and
a strategic play are directly comparable and the cheapest proportionate one can be identified.

**Mitigation credit is itself evidence-graded**, which closes the classic unfalsifiability loophole:
"the incident didn't happen *because* of our control" is a causal claim like any other and must
carry its grade.

**Blocked by:** 29

**Status:** done (2026-08-07)

**Reading list:** Decision ticket 09. Spec stories 26, 28.

- [x] Responses are priced on the same scale as impacts, from any domain.
      `twin price` emits the impact, the response costs and the mitigation credits in one unit.
      The impact is the perspective's declared valuation scaled by the propagated influence, and
      the response cost is the same triple `twin options` already produced.
- [x] Mitigation credit carries an evidence grade and is use-gated on the same rule as any other claim.
      `schema.mitigation` requires `component`, `reduction`, `evidence_grade` and `basis`, and a
      claim outside the published threshold earns nothing. "The incident did not happen *because*
      of our control" is a causal claim, and it now has to carry its evidence like one.
- [x] An ungraded mitigation claim yields no credit rather than default credit.
      Two shapes, both in the fixture. A response with no `mitigates` block claims nothing and
      earns nothing, because silence is not an average reduction. A claim graded outside the
      threshold earns nothing rather than a discount. Neither comes back with a figure.
- [x] A worked comparison in which a non-technical lever prices below a technical control, demonstrating the cross-domain claim.
      `retrain-the-on-call-rota` costs a mean of 6000 and earns 40000 of credit at grade 2.
      `add-a-read-replica` costs 30000, claims a **larger** reduction, and earns nothing because
      it claims it at grade 3. The cheaper lever is the non-technical one, and the more confident
      claim is the one the gate refuses.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      Two extended, none weakened, both citing decision ticket 09.
      `grade_5_only_path_never_prices` gains a priced-impact leg, because the largest figures in
      the system now appear there and a gate asserted only on the exposure would be asserted only
      where the smaller numbers are. `prefilter_precedes_pricing` extends its allow-list to
      `twin/pricing.py` and asserts that `price` reaches the choice set only through
      `options.prefilter`, because a lock on one module while a sibling prices freely is not a lock.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      `currency-regimes` stays at **3/6**, and nothing else moves either. That is the honest
      arithmetic. Decision ticket 09 AC 4 wants a treatment of *each* named incommensurable
      including where we refuse to price, and this ticket adds five distinct refusal reasons to
      the register — but existential and tail risk are build ticket 24 and ethical harms and the
      affected-parties register are 61, so "each" is still not true. ACs 5 and 6 need the
      trade-off curve across the ensemble, which is build ticket 33.

## Comments

**The worksheet's price lines were wrong, and correcting them was the first half of this ticket.**
Lines 27-29 asked for `1000000 x [0.12, 0.20, 0.28]` — an authored severity scaled by the
propagation out of `shared-database`. Both halves failed:

1. Every route out of `shared-database` crosses `database-slows-orders` at grade 3, and the
   published threshold is 2. Line 34 of the same worksheet already said so:
   `blast.shared-database.admitted_to_pricing = 0`. The lines asked for a number the rest of the
   table said could not exist. They were authored at build ticket 15; the use-gate landed at 19
   and causally-gated admission at 29.
2. The `1000000` lived in the prose and nowhere in the model.

The correction was put to the human who owns the worksheet and authorised on 2026-08-07. The
priced shock moved to `order-service`, whose edge to the portal is the only one in this
organisation graded well enough to price, and the refused shock stays in the table as lines 70-71
so the gate is asserted in both directions rather than only where it passes.

**There is no severity slot, and that is a decision rather than an omission.** A separate authored
severity would put two magnitudes on one component under one eye — a severity and that
perspective's declared valuation — with nothing reconciling them and an author free to move the
price through whichever is watched less. The declared valuation *is* the magnitude. One authored
figure, already evidence-graded, and the £ stays perspectival right down into the price: the
operator prices the same shock at 160000 and the staff council at 20000.

**The pocket org's only legal price is a point, and that is a finding.** `orders-slow-the-portal`
is degenerate on purpose, and it is also the only edge the gate admits. The edge that carries a
real range is graded 3 and may not price. Worksheet lines 68-69 pin both ends at 160000 and say
why, rather than quietly reporting a range that is not there.

**Build ticket 25's subject changed with this decision.** It anchors *valuations* now, not a
severity, and should be read that way when it opens.
