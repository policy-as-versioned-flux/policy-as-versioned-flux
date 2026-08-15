# 68 — Multi-channel enactment sensing, with corroboration setting the grade

**What to build:** **Declarations and machine-verified evidence are both sensor inputs, and corroboration between
channels sets the evidence grade.**

The elegant part is what this avoids: the action-state loop closes with **no new machinery** and with
*less* surveillance pressure rather than more — a self-declaration corroborated by reconciliation
state grades higher than either alone, so the incentive is to be verifiable rather than to be
watched.

**Blocked by:** 67, 53

**Status:** done (2026-08-15)

**Reading list:** Decision ticket 18. Spec story 20.

- [x] Declarations and machine evidence ingest through the normal sensing path, with no enactment-specific pipeline.
- [x] Corroboration between channels computes the evidence grade; single-channel claims grade lower.
- [x] An uncorroborated self-declaration cannot reach a price-eligible grade.
- [x] Reconciliation state (if Flux survived ticket 65) is one channel among several, not privileged.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.

## What was built

`twin/enactment-channels.yaml` — a versioned, **closed** table of six channels: `self-declaration`,
`merged-change`, `payroll-record`, `counter-signed-contract`, `pinned-policy-version`,
`reconciliation-state`. Each declares what it observes, whether the subject is the one declaring it,
and the rung it holds **alone**. The closure is what makes "no channel is privileged" structural:
privileging one would need a field, and there is none.

`twin/corroboration.py` — the loader, its refusals, and the computation.

**No new pipeline, and the absence is asserted.** A declaration and a reconciler report are ordinary
`signal` documents bound by ordinary `claim` documents. The `claim` schema gained a fourth kind
rather than a parallel record type (decision ticket 18 Q3 refuses one), `component` moved from
required to optional with the per-kind requirement in `_refine_claim`, and `verbs.sense` walks both
kinds through one loop and emits one `bound-signal` kind. `SIGNAL_BINDING_KINDS` is shared rather
than re-typed, which is the fix for the blind spot the change would otherwise have opened:
`unbound_pool` screened for the literal `"binding"`, so every sensed enactment would have gone into
the decaying pool while `sense()` bound it happily.

**No channel prices alone.** The criterion asks only that an uncorroborated self-declaration cannot
price. Making it a rule about every channel is stronger and simpler, and it removes the argument
about which channel deserves the exemption: each channel observes a *proxy* for "this response was
enacted", and the step from proxy to enactment is unevidenced in any single instance — the evidence
ladder's own grade 3. The loader reads the live ladder and refuses a table that disagrees.

**A subject cannot corroborate itself.** The grade is the strongest single-channel rung, strengthened
one rung per **independent** channel beyond the first, floored at rung 1. Every subject-declared
channel counts as one between them, so a set that is entirely self-declared never strengthens. That
is the third criterion made structural rather than checked at the point of use, and it is what keeps
the incentive pointing at *be verifiable* rather than at *say it again*.

**Reconciliation state is one row of six.** Build ticket 65's verdict on whether continuous proof of
force is required cannot be read until 2026-11-06. Grading this channel up in advance would decide
that question by fiat, and grading it down would be the same act in the other direction. The suite
swaps it for every other machine channel and asserts the grade does not move.

**Decision ticket 18 Q3's surveillance guard is run, not restated.** `payroll-record` is the only
channel observing people at all. It carries a decision ticket 15 admission block, and the table is
refused at load unless `twin/ethics_gate.py` admits it — refused too if a channel that observes
nobody carries one, because a gate applied where it was not needed is how it stops being read where
it is.

Harness guard `enactment_is_sensed_and_corroboration_sets_the_grade`. A guard on the suite rather
than an invariant, for the reason build tickets 66 and 67's are: the constitution names sixteen
invariants and may not grow a seventeenth without the constitution changing first. **No invariant
was changed or weakened**, so no authorising citation was needed. `twin verify` goes 61 to 62
passing checks. The golden digests are re-blessed with the authorising citation, because the
capabilities digest and the fixture's model-repo pin both moved and no derivation did.

One failure remains and predates this ticket: `drift_window_is_actually_being_sampled`, because
build ticket 64's probe has written no sample since 2026-08-13. Build ticket 67 reported the same
one.

## What a two-axis review changed

**The channel is declared, not verified — so it is now attributable.** The review's sharpest finding:
`channel` is a free identifier and `claimed_by` was free text, so the cheap route past "a subject
cannot corroborate itself" was to declare, then file your own `merged-change` claim and reach grade
2. Nothing here can check that the merged change or the payroll run exists, so what it does instead
is refuse an anonymous label: an enactment claim is attributable to a **registered role**, the same
discipline `_refine_claim` already applies to an `override`. The residual limit is real and is now
stated in the capability's own checklist rather than left to be discovered.

**The shared-kind sweep had stopped one caller short, and the fix is not the one it looked like.**
`twin/regimes.py` read `claim["component"]` directly, so a post-T enactment would have been covered
by accident. Extending it to resolve through the response's `addresses` made the as-consumed
refusal fire — correctly by that reading, and wrongly in fact: an execution reads components, world
models and propositions and **never reads a response**, so a dated enactment cannot change what it
answers, and refusing a run over one refuses a fact nothing could have consumed. So the decision is
taken in one place, `Overlay.forecast_subject`, which returns `None` for an enactment and records
what would change it — decision ticket 18's AC 5, when a forecast becomes conditional on whether a
response was enacted. The silent literal is gone; the over-refusal was not introduced.

`twin/signal_classify.py`'s labelled corpus read `claim["component"]` across every claim in an
overlay. It is filtered to binding claims now — it measures a component binding, so no other kind
is a labelled item, and reading `component` off one that has none would raise rather than skip.

**Declined, with the reason.** The review reads "self-declaration (alone 4) plus one machine
channel gives grade 2, so the subject's own word tips it into pricing" as a defect. It is the
specified behaviour: decision ticket 18 Q3's own worked example is "a self-declaration corroborated
by reconciliation state grades higher than either alone". The rule counts independent channels and
does not weight them by rung, and that is what "corroboration sets the grade" means here.

Smaller review fixes: the `"enactment"` literal is spelled once (`schema.ENACTMENT`, re-exported as
`corroboration.KIND`); `table()` carries the cache ceiling its sibling `evidence.ladder()` does;
`alone()` reads as `alone_grade()`; `refuse_disagreeing_grade` names the limit that it always
grades against the shipped table; and the yaml comment claiming "a test reads the number back out
of this text" was wrong — the code reads the `step_rungs` **field**, which is why the two cannot
disagree, and it now says that.

## What this does not close

**Decision ticket 18's criterion 5 stays unchecked, deliberately.** This ticket built the *read*
side of the action-state path: `corroboration.state(overlay, response)` answers "was the
recommendation acted upon, and how well is that evidenced" from the ordinary model. What closes
ticket 08's conditional-forecast loop is a **consumer** — mitigation credit that requires an
evidenced enactment, so that "the incident did not happen because of our control" needs both a
graded reduction claim and a graded observation that the control was ever put in place.
`twin/pricing.py` gates only the first today, and wiring the second changes every fixture's credit
and the pocket-org worksheet with it. Ticking criterion 5 on the read side alone would be the
constitution's own premature-done failure mode.

The enactment capability moves to **4 of 5**, and the table to 39 of 69.

`ponytail:` the grade counts **which** channels observed, never how many observations each made.
Ten reconciler reports are one channel on purpose. If recency or per-channel volume ever needs to
count, it belongs in the table as a declared property of a channel, not as a second knob in the rule.

`ponytail:` moving a claim between channels changes its recorded grade, and `evidence.history_violations`
would report that as an unrecorded regrade. That reading is defensible — the claim did get stronger
or weaker — but the event is a channel move rather than a regrade, and nothing distinguishes them
yet. No fixture exercises it. The upgrade is the shape build ticket 67 already built for enforcement
rungs: a separate move record, kept apart from a regrade.
