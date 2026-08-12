# 71 — Royal Mail: the answer key

**What to build:** The falsifiability subject, and **Netflix cannot carry this beat**: its story is famous, so a twin
"anticipating" Qwikster or the 2022 crash is indistinguishable from reciting it — the contamination
pillar would undermine the very thesis the demo leads with.

Royal Mail is low-contamination and unusually well-instrumented: the counterfactual sits **inside its
own audited filings** (GLS reported line-by-line in the same segmental accounts), with six-plus dated
checkpoints including a **legally-liable IPO prospectus forecasting the very trend it then
underinvested against**.

**Blocked by:** 41

**Status:** done (2026-08-11)

**Reading list:** Decision tickets 19, 22. Spec story 90.

- [x] Six or more dated checkpoints from the segmental accounts, each cited.
      `fixtures.build_royal_mail_org()`: six signals, each real, dated and cited by URL — the 2013
      IPO prospectus, DPD's Hinckley automated hub (2015), Hermes's Rugby automated hub (2017), the
      CWU "Four Pillars" agreement (Jan 2018), Royal Mail's own FY2017-18 results reporting GLS
      beside UKPIL in the same segmental accounts (May 2018), and the Oct 2018 profit warning —
      plus the outcome itself (the subject's own May 2019 £1.8bn remedial-investment concession),
      seven dated checkpoints in total (`tests/test_royal_mail.py::test_every_signal_carries_a_real_date_and_a_dated_source`,
      `test_the_outcome_conforms_to_the_ticket_08_fixture_format`).
- [x] The IPO prospectus forecast captured with its date and its legal status noted.
      The `ipo-prospectus-2013-09-27` signal's `provenance.legal_status` names the statutory basis
      (FSMA 2000 Part VI / Prospectus Rules, s.90 director liability) distinguishing it from an
      ordinary investor presentation (`test_the_ipo_prospectus_signal_carries_its_date_and_legal_status`).
- [x] Every fact carries a knowability date for regime gating.
      Every signal carries `date`, the outcome carries `resolved_on` — `twin/schema.py`'s own
      `DATED_FACTS` contract — and the `as-consumed` regime gate is exercised for real against this
      fixture's own commit history (`test_every_fact_carries_a_knowability_date_for_regime_gating`,
      `test_a_real_rewind_reads_the_repository_as_it_actually_stood`,
      `test_a_claim_is_bound_in_the_same_commit_as_the_signal_it_evidences`,
      `test_a_backtest_before_the_first_signal_sees_none_of_them`).
- [x] Key conforms to the answer-key fixture format.
      Validates against the closed schema, the world layer names no tenant, the commit history is
      monotonically dated to match the real 2013-2019 timeline (the same discipline build ticket 38
      established for Carillion), and a forecast run through the real CLI scores against the
      resolved outcome and reproduces from its own pins
      (`test_the_fixture_validates_against_its_closed_schema`, `test_the_world_layer_names_no_tenant`,
      `test_the_commit_history_is_monotonically_dated`,
      `test_a_royal_mail_forecast_scores_against_the_resolved_answer_key`,
      `test_a_royal_mail_score_card_reproduces_from_its_own_pins`). Registered as a new row in
      `twin/invariants/harness.py`'s `_FURTHER_ANSWER_KEYS` table — the extension point its own
      comment names for "a new answer-key fixture" — rather than a bespoke guard, so the suite
      checks it to the identical contract Carillion/NMC/Wirecard/Enron hold even though the
      proposition is a missed opportunity, not a collapse.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One row added to the existing `_further_answer_keys_are_dated_and_evidenced` guard's table
      (decision ticket 19's roster gap, resolved by research 19's recommended addition); zero
      invariants or guards weakened; no `checks_module_sha256`/`body_sha256` in
      `twin/invariants/manifest.yaml` moved, since the sixteen constitutional invariants
      (`twin/invariants/checks.py`) are untouched.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      No capability file ticks against this ticket, the same finding tickets 38-41 record: it
      authors one further answer-key fixture and a row in an existing extensible guard table, not a
      criterion of any of the seven tracked capabilities (`twin/capabilities/*.yaml`). Landed and
      ticked nothing.

**Closure note.** This worktree's branch had been created from a point in the shared history that
predated build tickets 01-44/60/62 (a base-ref mismatch in how this session's worktree was cut, not
a defect in the prior tickets themselves). The missing `twin/`, `.scratch/twin/`, `tests/`,
`conftest.py`, `pytest.ini`, `bin/` and `estate/driftwood/drift/` state was restored from the
shared checkout's own `main` (file content only, not a merge/rebase of branch history, per this
session's isolation contract) before this ticket's own work began; the two restoration commits
precede this ticket's own commit and are named as such rather than folded in silently. Restoring
`estate/driftwood/drift/` left its one sample a day stale against build ticket 64's own liveness
guard (`drift_window_is_actually_being_sampled`); rather than fabricate a fresh sample, `probe.sh`
was run for real against the still-live `kind-driftwood` cluster, appending one honest sample.
Neither restoration authors anything this ticket's own acceptance criteria claim credit for.
