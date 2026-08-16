# 74 — Netflix: run the whole engine

**What to build:** The whole-engine beat — fear **and** seize on dated evidence, carrying versioned enactment and
setting up the concluding cross-domain comparison.

**Blocked by:** 73, 46

**Status:** done — 2026-08-16. `twin/beat-netflix.sh`, ten ordinary CLI verbs across eight steps
(`fixture`, `backtest`, `rewind`, `gameplay-sweep`, `options`, `price`, `trade-off`, `propose`,
`substrate`, `grade`), no beat-specific code path. **No capability grade moves**, and that is the honest reading rather than
a shortfall hidden: the two criteria this ticket genuinely advances (decision ticket 13 AC 7 and
decision ticket 08 AC 5) each ask for **both** co-flagships, and Intel is build ticket 75. Each
capability file now names which half is done, so 75 does not have to rediscover it.

**Reading list:** Decision ticket 22. Spec stories 91, 93.

- [x] A threat path and an opportunity path both run end to end on dated evidence.
      Both from **one commit**, not from one date string. `twin rewind --at 2011-08-01` resolves
      the date; the threat path projects from it (`twin backtest --regime as-consumed`, three
      rival world models at 0.05, 0.15 and 0.55, nothing merging them) and the opportunity path
      sweeps the very commit that rewind returned (`twin gameplay-sweep --ref`, a `land-grab` on
      `streaming-service` because the org holds the adjacent `personalisation-technology`). The
      pins are what the guard asserts, not the `--at` string: two different answers to "what did
      the model look like on the day" would make fear and seize incomparable, which is the whole
      point of running them at one date. The sweep reports **1 opportunity pulled beside 3 signals
      pushed**, so decision ticket 13 Q3's negativity counterweight is a measured ratio on a real
      subject rather than a claim.
      The date is chosen so the rewind has something to cut: after the Q2 letter called the price
      changes a strength, six weeks before the guidance cut. **The cut is mechanical.**
      `fixtures.build_netflix_org` now commits each layer on the date its own evidence lands — the
      value chain on 2011-04-26, the rival world models on 2011-07-26, the causal and pricing
      layer on 2012-01-26 — so at 2011-08-01 the overlay carries no causal edge and no
      perspective, and back-dating that commit fails
      (`tests/test_netflix_beat.py::test_the_dated_state_carries_no_layer_that_postdates_it`).
      **No score, deliberately.** This org has no answer key, and the beat asserts that absence
      rather than working round it: the overlay carries no outcome and `twin score` refuses and
      names what exists
      (`::test_this_subject_carries_no_answer_key_and_the_engine_says_so`). Falsifiability is
      Royal Mail's beat, build ticket 72, and it lands red.
- [x] Cross-domain comparison demonstrated: a non-technical lever priced against a technical control.
      One shock at `dvd-by-mail` under `the-operator` puts
      `hold-the-bundled-price-for-one-quarter` — a price held and a letter, no engineering — beside
      `ship-one-bill-and-one-sign-in-across-the-two-plans`, both costed in the same unit. **The
      lever is the one with the evidence, which is the opposite of what a governance tool usually
      shows.** Its mitigation claim rests on two dated price changes in this same business (the
      November 2010 change the Q2 2011 letter reports the impact of, and the July 2011 separation)
      and it prices. The control's rests on domain theory nobody measured here, is graded 3, and is
      **refused a figure with the reason attached** rather than given a zero — a zero would have
      said "this control removes nothing", which is a different and probably false claim. A third
      option, `rank-domestic-members-by-cancellation-risk`, is the cheapest of the three and is
      removed by the universal floor before anything prices it, so "a constraint is not a very
      large price" is demonstrable here and not only in the toy fixture
      (`::test_a_non_technical_lever_and_a_technical_control_price_in_one_unit`,
      `::test_the_prefilter_removes_an_option_before_any_of_this_prices_it`).
      Every figure traces to a primary filing. The valuations are the subject's own Q4 2011
      segment revenue as reported ($476m domestic streaming, $370m domestic DVD) — one quarter,
      taken as reported, with no annualisation on top. The lever's cost range is written out from
      the published $5.99 monthly uplift ($9.99 to $15.98, Q2 2011 letter) held for three months
      across two, three and five times the roughly 800,000 domestic members the Q3 letter reports
      leaving.
- [x] The trade-off curve is the output, with ensemble disagreement visible.
      Three rival causal accounts read the same two filings and disagree about how much of the
      separation crossed to the streaming side — 0.10, 0.35 and 0.05 on the same grade-1 edge,
      same two components, same evidence grade. Believe `the-shock-crossed-to-the-streaming-side`
      and the price hold is cheapest; believe either of the other two and the billing rebuild is.
      `agreement.unanimous` is `false`, `cheapest_by_account` names which is which, and `twin
      trade-off` prints it **before** the computed default
      (`::test_the_accounts_disagree_about_which_response_is_cheapest`,
      `::test_the_disagreement_reaches_the_surface_before_the_default`).
      **This is the first fixture in the repository where that happens on real content.** Build
      ticket 33 recorded that no real fixture made two accounts disagree about the cheapest
      response and called its unit test the honest substitute until one was authored;
      `twin/tradeoff.py` `_assemble` now says so and points here. The third account exists so that
      "dropping any one changes nothing about the rest" has three to drop from, and that is
      asserted rather than narrated
      (`::test_dropping_any_one_account_changes_nothing_about_the_rest`).
- [x] The shared-prior limitation published with any synthetic-substrate result.
      Asserted as a **pairing with the capability**, not with one artefact. Build ticket 73
      checked that one substrate report carries the limitation; the criterion here says *any*
      result, so the guard walks every artefact the beat emits and requires that any artefact
      whose depth block names `synthetic-substrate` carries `planter.SHARED_PRIOR_LIMITATION`
      verbatim, and fails if none claimed the capability at all. A second surface claiming that
      capability without the limitation fails here rather than shipping quietly.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One new harness guard, `netflix_runs_both_paths_and_the_curve_keeps_the_disagreement`, six
      legs on the **committed** fixture: both paths from the one resolved commit; nothing
      back-dated into that state; a lever and a control in one unit with the refusal surviving; a
      ranking disagreement across the accounts; dropping any account leaving the rest untouched;
      and the limitation paired with the capability. **Probed rather than reasoned about** —
      making the two accounts agree, back-dating the pricing layer, and regrading the refused
      claim so it prices each fail it, and the unmutated fixture passes. Zero invariants or guards
      weakened; no `checks_module_sha256`/`body_sha256` in `twin/invariants/manifest.yaml` moved,
      since the sixteen constitutional invariants are untouched.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      The beat's closing step prints two computed grades and types neither: `demo-slice` stays at
      `stub`, 0/4 of decision ticket 22 — build ticket 77 owns three of those criteria and the
      fourth needs all three subjects — and `scenario-engine` stays at `partial`, 4/7. Every
      artefact the beat presents prints the computed grade of every capability that produced it,
      compared in test against what `Capabilities.load()` computes rather than merely checked for
      shape (`::test_every_artefact_the_beat_emits_carries_computed_depth_grades`).
      **Two criteria are now half done and neither is ticked.** Decision ticket 13 AC 7 wants one
      fear and one opportunity scenario *across the co-flagships*: Netflix has both, Intel has
      neither on a real spine. Decision ticket 08 AC 5 wants a real causal claim from *each*
      co-flagship: `the-separation-reaches-the-streaming-service` is real and graded 1, and
      `euv-delay-slips-the-node` still lives only in the walking-skeleton fixture that cites
      `example.invalid`. Both capability files now carry a note saying exactly that, and
      `::test_the_scenario_engine_criterion_this_beat_touches_needs_the_other_co_flagship` fails
      the day AC 7 ticks, so build ticket 75 has to come back and say which ticket supplied the
      other half.

## What this ticket found and did not close

**A response's `cost` carries no evidence grade, and everything around it does.** A perspective's
valuation is graded and refused an amount outside the threshold; a mitigation claim is graded and
refused credit outside it; a causal edge is graded and refused a price outside it. A `cost` is
none of these — the schema has no slot — so the two levers' ranges here are authored, and the
fixture writes the arithmetic out in each response's own `note` rather than claiming a grade it
cannot carry. Named rather than fixed: widening the schema needs an authorising decision ticket
and this ticket has none.

## Versioned enactment, in the narrowed form that makes the beat's own argument

No criterion asks for it and the ticket's opening line does, so it is here: `twin propose
--response ship-one-bill-and-one-sign-in-across-the-two-plans --channel record`. The **`record`
channel and not `policy`**, because the control is a lever that is not code, and that narrowing is
the argument rather than a caveat on it. The proposal's own `narrowed_claim` says so — *policy-as-
code is AN enactment arm, not THE definition of governance; most levers are not code, so if
versioned policy were the shape of governance the cross-domain comparison the £ engine exists for
could not exist* — which is the same sentence criterion 2 above is a worked example of. Asserted
rather than only printed
(`::test_enactment_is_proposed_through_the_channel_a_lever_that_is_not_code_uses`). That the twin
proposes and never disposes is `enactment_is_propose_only_at_both_layers`' job at both layers, and
is not restated here.

## What this beat does not show

**A causal claim from the opportunity side.** The land-grab is proposed with its preconditions
checked and it is never priced: the gameplay lens emits a grade-5 claim by construction, so the
opportunity path stops at a proposal and the £ chain runs only on the threat side. That is the
use-gate working, not a gap in the beat, and it is why the cross-domain comparison sits under the
threat shock rather than between a threat and an opportunity.
