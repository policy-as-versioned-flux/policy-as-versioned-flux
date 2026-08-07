# 36 — The three information regimes, gated by construction

**What to build:** **`as-consumed`** (only what the twin actually ingested by time T), **`as-knowable`** (everything
publicly available by T), **`with-hindsight`** (unrestricted). Only `as-consumed` produces a
scoring-eligible forecast.

The gaps localise failure: as-consumed versus as-knowable is a **sensing** failure; as-knowable
versus with-hindsight is an **interpretation** failure; present in all three, it is the **model**.
That triangulation is the reason for three regimes rather than one honest one.

**Blocked by:** 35

**Status:** done (2026-08-07)

**Reading list:** Decision tickets 11, 13, 19. Spec stories 39, 40.

- [x] Regime is a required execution parameter with no default.
      `verbs.run` takes it positionally with no default value and `regimes.require` refuses an
      absent one; `twin run --regime` is `required=True`. The scenario schema lost its `regime`
      field, because an authored one is a default wearing a different hat — an execution that
      omitted the flag would inherit whatever the file happened to say.
- [x] `as_consumed_admits_no_post_T_fact` goes live, **asserted by construction** — the gate is structural, not a review step.
      The model is *loaded through* the regime: `as-consumed` reopens the repository at the last
      commit on or before T and removes every fact dated after T, so the execution has no post-T
      fact available to reference. The check asserts the construction — no default, no schema
      slot, absence rather than screening — not just the outcome.
- [x] A planted post-T fact causes an as-consumed run to fail rather than to quietly include it.
      `fixtures.build_regime_org(planted=True)` commits a fact dated after T *before* T, which
      is the one shape the rewind cannot remove. Bound by a claim to a component the scenario
      forecasts, it refuses the run; the same plant runs under the two looser regimes, so it is
      the regime refusing and not the repository.
- [x] The three-way gap is computed and reported as the localisation diagnostic, not left for a human to infer.
      `twin regimes` emits a `regime-gap`: as-consumed vs as-knowable localises to **sensing**,
      as-knowable vs with-hindsight to **interpretation**, each naming the facts. The **model**
      residual is reported as *not computed*, with the reason — nothing infers a probability from
      a fact yet, so a computed residual of zero would read as "the model is fine" rather than as
      "nothing consumes a signal".
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One invariant activated, none weakened. The re-blessed hashes cite decision ticket 13.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      `scenario-engine` still stands at 1/7. Decision ticket 13 AC 2 wants fast-forward, rewind
      and play each distinguished; rewind is now whole — the time half at build ticket 35 and the
      information gate here, which is what Q2 actually asks for — and fast-forward is build ticket
      37. Two thirds of a three-verb semantics is not the semantics, so nothing is ticked.

## Comments

**Nothing is ticked, and that is the arithmetic rather than a disappointment.** Decision ticket
11's checklist has no criterion this touches either: AC 4 is observation propagation (build ticket
22's) and AC 5 is weak-signal retention (build ticket 54's). The regime gate is most of decision
ticket 13 Q2 and Q2b, and Q2 is one clause of a three-clause criterion.

**Two limits are named in `twin/regimes.py` rather than papered over.**

1. **The rewind leg needs a repository that existed at T.** The Netflix subject is dated 2011 and
   its model repository was built this year, so there is no commit to read and `as-consumed` there
   rests on fact dates alone. The artefact records `ingestion_history.available: false` with the
   consequence, instead of quietly looking stronger than it was. The regime fixture is the only
   repository here whose commit history straddles T, which is why the sensing gap needs it.
2. **A regrade is not date-gated.** `schema.DATED_FACTS` covers facts about the world — signals
   and outcomes. A regrade is the twin's own record of how strong a claim is, so a regrade dated
   after T still moves a grade under `as-knowable`; only the rewind removes one.

**The answer key is withheld, not refused.** A post-T fact refuses the run only when a claim binds
it to a component the scenario forecasts. Refusing on the mere presence of a post-T fact would
make a backtest impossible in any repository that also holds the key it will later be scored
against — which is every backtest.
