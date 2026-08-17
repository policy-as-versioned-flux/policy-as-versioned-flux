# 74 — Netflix: run the whole engine

**What to build:** The whole-engine beat — fear **and** seize on dated evidence, carrying versioned enactment and
setting up the concluding cross-domain comparison.

**Blocked by:** 73, 46

**Status:** done — 2026-08-16, adversarially reviewed and revised the same day. `twin/beat-netflix.sh`,
ten ordinary CLI verbs across nine steps (0-8): `fixture`, `backtest`, `rewind`, `gameplay-sweep`,
`options`, `price`, `trade-off`, `propose`, `substrate`, `grade` (twice), no beat-specific code
path. **No capability grade moves**, and that is the honest reading rather than a shortfall hidden:
the two criteria this ticket genuinely advances (decision ticket 13 AC 7 and decision ticket 08
AC 5) each ask for **both** co-flagships, and Intel is build ticket 75. Each capability file now
names which half is done, so 75 does not have to rediscover it.

A six-agent adversarial review found and this ticket then closed: **`twin propose` bypassed the
constraint pre-filter** (a proposal existed for a response the choice set had already refused,
security HIGH — see "What this ticket found and did not close" below); **the beat proposed the
wrong response**, the code control through the not-code channel, printing a contradiction to its
own audience (code-quality HIGH); **the harness guard's limitation-pairing leg walked 3 of the
beat's 8 artefacts** while its own docstring claimed all of them, confirmed independently by three
reviewers and proved live by adding `synthetic-substrate` to a capability the walk never touched
(docs CRITICAL, architecture and testing MEDIUM); **the ensemble-diversity check asserted only a
count**, so three identical forecasts passed both the guard and the pytest suite (testing HIGH);
**the grade-2 mitigation basis cited an instance absent from any committed signal** — real, and
now in the spine, but not yet written down (docs HIGH); **the "probed rather than reasoned about"
claim pointed at nothing committed** (docs HIGH); and the guard itself drove verb functions
directly rather than the CLI, a seam-2 call sequence the constitution scopes away from
(architecture HIGH). The guard is rewritten below to drive `cli.main`, matching
`a_scored_forecast_is_never_silently_dropped`'s own precedent, with one seam-2 exception named and
defended in its own docstring.

**Reading list:** Decision ticket 22. Spec stories 91, 93.

- [x] A threat path and an opportunity path both run end to end on dated evidence.
      Both from **one commit**, not from one date string. `twin rewind --at 2011-08-01` resolves
      the date; the threat path projects from it (`twin backtest --regime as-consumed`, three
      rival world models at 0.05, 0.15 and 0.55, nothing merging them) and the opportunity path
      sweeps the very commit that rewind returned (`twin gameplay-sweep --ref`, a `land-grab` on
      `streaming-service` because the org holds the adjacent `personalisation-technology`). The
      pins are what the guard asserts, not the `--at` string: two different answers to "what did
      the model look like on the day" would make fear and seize incomparable, which is the whole
      point of running them at one date — now checked as **two independent CLI resolutions**
      (`twin backtest --at` and `twin rewind --at`, each resolving 2011-08-01 on its own) compared
      against each other, after review found the first draft's version opened one rewound repo
      once and handed it to both paths, so its own pin comparison could only ever agree with
      itself. The sweep reports **1 opportunity pulled beside 3 signals pushed**, and the threat
      path's three forecasts are checked for a **distinct** spread, not merely a count — three
      identical probabilities passed the first draft
      (`::test_both_paths_run_from_the_one_state_the_rewind_resolved`).
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
      shows.** Its mitigation claim rests on two dated price changes in this same business, each
      now reported in this org's own filed signal: the November 2010 change (`q4-2010-letter-
      2011-01-26`, whose statement was silent on it in build ticket 73 and now carries the $7.99
      pure-streaming plan and the raised combination-plan prices that filing genuinely reports —
      verified against the real SEC filing, not authored) and the July 2011 separation
      (`q2-2011-letter-2011-07-25` and `q3-2011-letter-2011-10-24`, before and after). That
      repetition is what the grade rests on, and it now traces to committed content rather than to
      a filing the spine cited without carrying. The control's claim rests on domain theory nobody
      measured here, is graded 3, and is **refused a figure with the reason attached** rather than
      given a zero — a zero would have said "this control removes nothing", which is a different
      and probably false claim. A third option, `rank-domestic-members-by-cancellation-risk`, is
      the cheapest of the three and is removed by the universal floor before anything prices it,
      so "a constraint is not a very large price" is demonstrable here and not only in the toy
      fixture (`::test_a_non_technical_lever_and_a_technical_control_price_in_one_unit`,
      `::test_the_prefilter_removes_an_option_before_any_of_this_prices_it`). Direction-named,
      not merely "some response earned nothing": both the guard and the pytest test assert on the
      two response ids by name, after review found the first draft's guard leg would pass with
      the lever's and the control's evidence grades swapped — inverting the beat's own argument —
      because *some* refusal still existed.
      The two valuations trace to a primary filing exactly: the subject's own Q4 2011 segment
      revenue as reported ($476m domestic streaming, $370m domestic DVD), one quarter, taken as
      reported, with no annualisation on top. The lever's cost range does not — see "What this
      ticket found and did not close" below — but its inputs do: the published $5.99 monthly
      uplift ($9.99 to $15.98, Q2 2011 letter) and the roughly 800,000 domestic members the Q3
      letter reports leaving, held for three months across two, three and five times that figure
      and rounded to the nearest five million. That arithmetic was re-derived independently in
      review and reproduces exactly.
- [x] The trade-off curve is the output, with ensemble disagreement visible.
      Three rival causal accounts read the same two filings and disagree about how much of the
      separation crossed to the streaming side — 0.10, 0.35 and 0.05 on the same grade-1 edge,
      same two components, same evidence grade. Believe `the-shock-crossed-to-the-streaming-side`
      and the price hold is cheapest; believe either of the other two and the billing rebuild is.
      `agreement.unanimous` is `false`, `cheapest_by_account` names which is which, and `twin
      trade-off` prints it **before** the computed default, now anchored on the printed line
      prefixes rather than on the bare words — `agreement.note` itself contains the word "default"
      when the accounts disagree, so the first draft's test would still have passed with the
      default line deleted outright
      (`::test_the_accounts_disagree_about_which_response_is_cheapest`,
      `::test_the_disagreement_reaches_the_surface_before_the_default`).
      **This is the first fixture in the repository where that happens on real content.** Build
      ticket 33 recorded that no real fixture made two accounts disagree about the cheapest
      response and called its unit test the honest substitute until one was authored;
      `twin/tradeoff.py` `_assemble` now says so and points here. **Three accounts, not two** —
      review found the guard's own docstring and the harness's returned summary describing "the
      two accounts" while the code always ran three; both are corrected. The third exists so that
      "dropping any one changes nothing about the rest" has three to drop from, checked both
      through the CLI leg above and directly against `tradeoff.curve()`'s own arithmetic in the
      harness guard (deliberately seam 2 — see the guard's own docstring for why), and the
      refused response's own `net_cost_of_risk.range` is asserted to be exactly `0` across all
      three accounts, not merely inferred from the refusal existing
      (`::test_dropping_any_one_account_changes_nothing_about_the_rest`).
- [x] The shared-prior limitation published with any synthetic-substrate result.
      Asserted as a **pairing with the capability**, not with one artefact. **The first draft's
      walk covered 3 of the beat's 8 artefacts — threat, sweep, substrate report — and only one of
      those three can ever claim `synthetic-substrate`, so its own "second surface" leg was
      unreachable.** Three independent reviewers found this the same way: the docs review by
      reading the criterion's own words against the code, architecture by tracing which of the
      beat's eight commands ever produce a checked artefact, testing by adding
      `synthetic-substrate` to `verbs.CAPS_PRICE` and watching the old walk pass anyway. The guard
      now walks all eight — backtest, rewind, gameplay-sweep, options, price, trade-off, propose,
      substrate — and the same mutation now fails
      (`::test_every_artefact_the_beat_emits_carries_computed_depth_grades` covers the pytest
      half; the harness guard covers its own, larger set including artefacts the pytest suite
      does not build).
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One harness guard, `netflix_runs_both_paths_and_the_curve_keeps_the_disagreement`,
      **rewritten in review from a direct-verb-call implementation to one that drives `cli.main`**
      end to end — backtest, rewind, gameplay-sweep, options, price, trade-off, propose, substrate
      — the same seam `a_scored_forecast_is_never_silently_dropped` (build ticket 72) already
      uses, after architecture review named the original a seam-2 call sequence the constitution
      scopes away from ("numerical and structural properties only, never call sequences or object
      shapes"). One leg stays seam 2 deliberately and says so in its own docstring: dropping any
      one causal account is checked directly against `tradeoff.curve()`'s pure arithmetic on one
      hoisted overlay, because that property is about propagation maths and not about CLI wiring,
      and three extra CLI round-trips would spend ~1.6s re-deriving an overlay that has not
      changed to check it. Legs: two independently-resolved CLI dates agree on one commit; the
      threat path's forecasts are both plural and distinct; the opportunity path pulled something
      from that same commit; `twin options` refuses the perspective at the past commit and the
      rewound state carries zero causal edges; the lever and the control are priced and refused by
      name, not by "some response"; the curve keeps the disagreement and the refused option's own
      figure never moves; dropping any account leaves the rest untouched; enactment is proposed on
      the lever through `record`; and the limitation is paired with the capability across all
      eight emitted artefacts. **Probed, not merely reasoned about**, with the mutations review
      demanded run and recorded: making the accounts agree, back-dating the pricing layer,
      regrading the refused claim so it prices, swapping the lever's and control's grades so the
      argument inverts, and widening a capability list to falsely claim `synthetic-substrate` —
      each fails the rewritten guard, and the unmutated fixture passes. Zero invariants or guards
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

## What this ticket found and closed

**`twin propose` bypassed the constraint pre-filter.** `twin options`/`twin price` remove a
response that crosses the universal floor before anything prices it; `twin propose` read
`overlay.responses` directly and had never been asked whether the pre-filter would have kept the
response it was proposing. Security review found the live consequence: `twin propose --response
rank-domestic-members-by-cancellation-risk --channel record` on this fixture emitted a signed,
derived proposal carrying that response's cost — the same option `no-individual-level-output`
removes from every choice set two verbs over. The defect predates this ticket (the toy fixture's
`instrument-viewers-without-telling-them` proposed just as freely), but this ticket is what raised
the exposure: the excluded option is now a per-member ranking on a real named company, and `twin
propose` is now a CI step. `twin/enact.py` `propose()` now refuses a response whose `crosses`
names a universal floor id, before it reads a channel or builds a body, and states plainly that a
perspective's own declared red lines are not checked — this verb carries no `--perspective` —
because floor ids bind every perspective identically and perspective-declared ones do not.
`tests/test_enact.py::test_a_response_that_crosses_the_universal_floor_is_refused_not_priced`
asserts the message names the crossed constraint.

**Two committed files were byte-for-byte duplicated with a small delta, and could have drifted
silently.** `_NETFLIX_ENSEMBLE` and `_NETFLIX_VALUE_CHAIN` in `twin/fixtures.py` each restated a
file `_NETFLIX_BASE` already defines — the scenario file (23 of 25 lines identical) and the
`streaming-service` component — rather than deriving from it. A later edit to the shared prose (the
affected-parties register, say) would have landed in one copy and silently reverted in the fixture
built from the other. Both are now computed from `_NETFLIX_BASE`'s own string — a plain
concatenation for the component, and a guarded `.replace()` for the scenario file that refuses to
return its input unchanged if the anchor text it targets ever moves, rather than a second `.replace()`
that could silently no-op.

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
--response hold-the-bundled-price-for-one-quarter --channel record`. The **`record` channel and
not `policy`**, because the *lever* — the price hold, not the control — is a lever that is not
code, and that narrowing is the argument rather than a caveat on it. **The first draft proposed the
wrong response**: `ship-one-bill-and-one-sign-in-across-the-two-plans`, the billing/SSO rebuild,
which is code with a real enforcement point — the textbook `policy` case — through the channel
whose own text says "not code", printed directly under a response that is. Code-quality review
caught it by re-deriving which response the beat's own AC 2 names as the non-technical lever and
comparing it to what the script actually proposed. Fixed in the script, the harness guard and the
pytest test, all three now asserting the response id by name rather than only the channel's
constant text.
The proposal's own `narrowed_claim` says so — *policy-as-code is AN enactment arm, not THE
definition of governance; most levers are not code, so if versioned policy were the shape of
governance the cross-domain comparison the £ engine exists for could not exist* — which is the
same sentence criterion 2 above is a worked example of. Asserted rather than only printed
(`::test_enactment_is_proposed_through_the_channel_a_lever_that_is_not_code_uses`). That the twin
proposes and never disposes is `enactment_is_propose_only_at_both_layers`' job at both layers, and
is not restated here.

**The proposal's own dependency block now names whose estate it is reading.** Architecture review
found the beat's own script printing "these pins are the tool's own estate, not the subject's" as
three `echo` lines *after* the artefact was already written — prose that never reaches the
artefact, the seam-1 deliverable that gets read, shared and attested. `_dependency_block` in
`twin/enact.py` now takes the org and appends a sixth `limits` entry naming which repository the
pins belong to, so the caveat travels in the file rather than only in the terminal that produced
it.

## What this beat does not show

**A causal claim from the opportunity side.** The land-grab is proposed with its preconditions
checked and it is never priced: the gameplay lens emits a grade-5 claim by construction, so the
opportunity path stops at a proposal and the £ chain runs only on the threat side. That is the
use-gate working, not a gap in the beat, and it is why the cross-domain comparison sits under the
threat shock rather than between a threat and an opportunity.
