# 86 — Enactment: gate mitigation credit on verified enactment, not just claimed evidence grade

**What to build:** The last AC on `enactment` (4/5). Build ticket 68 built the read side —
`corroboration.state(overlay, response)` answers whether a recommendation was actually acted upon,
and how well evidenced that is. Nothing consumes it: `twin/pricing.py`'s `_credit(entry, claim,
priced)` (~line 230) computes mitigation credit purely from the response's own `mitigates` claim and
its `evidence_grade`, never calling `corroboration.state()` — confirmed by grep, zero hits. This is
decision ticket 08's conditional-forecast loop left open at exactly the join point.

**Blocked by:** 85 (both tickets touch `twin/pricing.py`'s credit/refusal machinery; sequencing
after 85 avoids two tickets editing the same function region out of order)

**Status:** done (2026-08-18)

**Reading list:** Decision ticket 18 (`.scratch/twin/issues/18-enactment-arm.md`), and its link back
to decision ticket 08's conditional-forecast loop. `twin/capabilities/enactment.yaml` for exact AC
text. `twin/pricing.py` (`_credit`), `twin/corroboration.py`.

- [x] AC 5 — "The action-state feedback path that closes ticket 08's conditional-forecast loop."
      `_credit()` gains an enactment-state lookup via `corroboration.state()`: a response claiming
      mitigation credit is refused — with a named reason, mirroring the existing refusal-reason
      constants — if the option it credits has no corroborated enactment, even when the claim's own
      evidence grade would otherwise pass. Add a harness guard mirroring the shape of
      `enforcement_is_a_spectrum_and_never_prices_a_rung`, and a worked-example test: identical
      claims, one corroborated as enacted and one not, scoring differently.
      Closed exactly as scoped: `twin/pricing.py`'s `_credit()` now takes a required `overlay`
      parameter and, once a claim's own grade clears the pricing threshold, calls
      `corroboration.state(overlay, option["option"])` — a claim on an uncorroborated option is
      refused with the new reason `pricing.NOT_ENACTED`, distinct from `pricing.CLAIM_TOO_WEAK`.
      `overlay` is required rather than defaulted, on purpose: an omittable parameter would be a
      silent way to skip the gate, which this codebase never does elsewhere (`CLAIMS_NONE` is
      structural, not a default either). Threaded through both call sites that reach `_credit()`:
      `twin/verbs.py`'s `price()` and `twin/tradeoff.py`'s `curve()`. Worked-example test:
      `tests/test_pricing.py::test_identical_claims_score_differently_by_corroborated_enactment`
      — the identical claim, against the identical priced impact, credited for
      `pin-the-tooling-image-set` (build ticket 68's corroborated fixture case) and refused as
      `NOT_ENACTED` for `report-node-schedule-variance` (build ticket 68's self-declared-only
      case) — plus `test_a_claim_against_an_option_with_no_enactment_claims_at_all_is_also_refused`
      (the gate fails closed on an option nobody ever declared anything about). Harness guard
      `mitigation_credit_is_gated_on_corroborated_enactment_not_just_claimed_evidence`
      (`twin/invariants/harness.py`) mirrors `enforcement_is_a_spectrum_and_never_prices_a_rung`'s
      shape: the same unit-level differential, plus the live `verbs.price()` artefact path on a
      fresh pocket-org fixture, crediting `retrain-the-on-call-rota` against its own corroborating
      enactment claims and then refusing the identical claim the moment those two claims are
      stripped from an otherwise-identical fixture.

## Also found and fixed

- **A universal gate collides with fixtures that were never enacted, and the pocket/netflix/intel
  orgs are not interchangeable about how much room they leave to fix that.** Making mitigation
  credit require corroborated enactment means every EXISTING credited response in every fixture
  needed its own corroborating enactment claim, or it would now be silently refused — the pocket
  org's `retrain-the-on-call-rota` (the hand-checked worksheet's own credit figure,
  `twin/pocket-org-worksheet.md` line 73) and the netflix org's `expand-the-delivery-network`
  (`tests/test_tradeoff.py`) and `hold-the-bundled-price-for-one-quarter`
  (`tests/test_netflix_beat.py`), each caught only by running the full suite rather than assumed
  from the unit tests alone. Adding a plain `mitigates`-shaped signal+claim pair worked cleanly for
  `pocket` (no other invariant reads its signal collection at all) and for the netflix walking-
  skeleton (`OVERLAY_FILES`) once the two new signals were dated **before** `dvd-decline-2011`'s
  own T (2011-07-12) — a later date would have grown `test_a_post_T_fact_bound_to_nothing_the_
  scenario_forecasts_does_not_refuse`'s exact withheld-fact list. The netflix **beat** org
  (`build_netflix_org()`, decision ticket 12's co-flagship real subject) is different in kind, not
  degree: `tests/test_netflix.py::test_the_spine_is_six_dated_checkpoints` asserts its spine is
  EXACTLY the subject's six real, dated SEC filings, and `Spine.from_overlay()` reads every signal
  in the overlay with no filter — so any new signal breaks that guarantee regardless of its date or
  content, because the guarantee is about count and realness, not about any one date. Fixed by
  keeping the two enactment records **out of `build_netflix_org()`** entirely: a new function,
  `fixtures.corroborate_the_price_hold_as_enacted()`, dated after `tests/test_netflix_beat.py`'s
  own rewind point (2011-08-01) so `test_opportunities_are_pulled_and_signals_are_pushed_side_by_
  side`'s `counts["signals"] == 3` (read from git history at the rewound commit, not from the
  schema's `date` field) is untouched too. `tests/test_netflix.py`'s own `netflix_repo_dir`
  fixture never calls it, so the six-filing spine stays exactly what it always was — see the next
  finding for where this function ended up being called from once a second, independent call site
  turned up needing the identical fix.
- **`tests/test_enact.py` and `tests/test_grades.py`'s two capability-set guards hardcode the
  shipped-`full` set by name** — the same maintenance every prior ticket that reached `full` for
  the first time (79, 84, 87, 82, 85) already did to this exact pair. `enactment` reaching `full`
  changed all three, and all three refused with a clear diff (an assertion mismatch, not a crash),
  which is what these guards are for. Updated to name `enactment` alongside the rest.
- **A second, independent netflix-beat call site had the identical uncorroborated-lever gap, and
  `pytest -q`'s own failure count did not surface it.** The harness guard
  `netflix_runs_both_paths_and_the_curve_keeps_the_disagreement` builds its own netflix-beat repo
  via `fixtures.build_netflix_org()` directly, and — before this finding — `twin/beat-netflix.sh`
  (via `twin fixture --name netflix`, `fixtures.BUILDERS["netflix"]`) would have built the
  identical uncorroborated repo for real. Both were caught only by reading `twin verify`'s own
  `RESULT` line, never by the `pytest -q` failure count: this harness check runs inside
  `test_invariant_suite.py`'s single aggregate assertion, which was *already* red for the two
  pre-existing, unrelated reasons (drift/flux-floor), so one more failing reason changed that
  assertion's message without changing its pass/fail outcome or the suite's failure count. Fixed
  by promoting the fixture-plus-corroboration pairing to one function,
  `fixtures.build_and_corroborate_netflix_org()`, registered as `BUILDERS["netflix"]` itself — so
  `beat-netflix.sh`, the harness guard and `tests/test_netflix_beat.py` now share one call site
  rather than three copies of the same two-line pairing, and a fourth consumer added later gets it
  for free. `tests/test_netflix.py` still calls `build_netflix_org()` directly, unaffected. The
  general lesson, named rather than only fixed: a suite-level aggregate that is already red can
  hide a genuinely new failure inside its own detail text, so a harness-touching change needs its
  own `twin verify` read, not just a green-enough `pytest -q` failure count.
- **The fix above still failed on the first full `twin verify` run, and the reason was a shared
  cache key, not a missed call site.** `netflix_runs_both_paths_and_the_curve_keeps_the_disagreement`
  (line ~1743) and build ticket 73's own sibling guard,
  `netflix_substrate_is_free_running_and_every_plant_carries_a_horizon` (line ~1589), both cache
  their netflix-beat repository at the identical path, `ctx.tmp / "netflix-repo"` — harmless while
  both wanted the same plain org, and every check in one `twin verify` run shares one `ctx.tmp`.
  Ticket 73's guard runs first (lower line number), builds the PLAIN org there deliberately — it
  asserts spine fidelity, which build ticket 86's two extra signals would have thrown off — and
  this ticket's own guard then found the directory already `.exists()` and skipped rebuilding it,
  silently inheriting the uncorroborated repository. Running the new guard alone
  (`invariants.run(only=[...])`) passed every time, because a solo run gets a fresh `ctx.tmp` and
  builds its own copy — which is exactly why this stayed invisible until a **full** `twin verify`
  run, not a targeted one, was read. Fixed by giving the new guard its own cache key,
  `netflix-repo-corroborated`, rather than trying to make the two guards agree on one shared
  build. Ticket 73's guard is untouched. The lesson this adds to the one above: two harness guards
  that happen to reuse the same scratch path were never a problem until one of them started
  needing a DIFFERENT fixture at that path — a full run is what a change like that has to be
  checked against, not a single named check.
- **Golden digests needed re-blessing**, the same mechanism ticket 85 used: `enactment` reaching
  `full` changes `Capabilities.digest`, which every emitted artefact's `depth` block carries, so
  the twelve committed golden digests in `twin/invariants/golden-digests.json` went stale the
  moment AC 5 ticked. Re-blessed via `twin verify --bless-goldens --authorise "decision ticket 18
  — enactment reaches full, AC 5 closed (build ticket 86)"`.

**A judgement call, made and not revisited:** the new gate sits between `CLAIM_TOO_WEAK` and
`NOTHING_PRICED_THERE` in `_credit()`'s own ordering — after the claim's own evidence grade is
checked, before whether a priced impact exists to apply the reduction to. The ticket does not
specify an order; this one reads as "check the claim's own defect, then whether the *option* was
enacted, then whether there is anything in this shock for the reduction to be a fraction of" —
each gate narrower than the last. A reader could reasonably put the enactment check last instead;
nothing here depends on this exact ordering, and the three-gate behaviour (each refusal named,
none defaulting to a number) is identical either way.

## Evidence

Baseline note: no full-suite baseline was captured on a completely clean tree before this ticket's
edits began (a process gap against this ticket's own instructions, named rather than hidden). What
was captured — `.venv/bin/python -m pytest -q tests/test_invariant_suite.py` on a `git stash`ed
clean tree — confirms the pre-existing failures independently: `2 failed, 21 passed`
(`test_the_suite_is_green` and `test_every_live_invariant_actually_asserts_something`, the latter
on `identical_pins_identical_bytes`, which is flaky/order-dependent — it passes in isolation and
in most full runs, including the final one below). Build ticket 85's own committed evidence
records the same-day full-suite baseline as `1 failed, 1482 passed`, the identical single
pre-existing failure this ticket's own final run still shows.

`.venv/bin/mypy twin tests conftest.py --ignore-missing-imports --warn-unused-ignores`:
```
Success: no issues found in 151 source files
```

`.venv/bin/python -m pytest -q` (final, after all fixes):
```
FAILED tests/test_invariant_suite.py::test_the_suite_is_green - AssertionErro...
1 failed, 1498 passed in 359.61s (0:05:59)
```
The sole failure is the pre-existing one (`drift_window_is_actually_being_sampled` and
`flux_coverage_floor_is_still_reachable`, both recorded rather than re-probed per the standing
decision — see `feedback_flux_verdict_unmeasured` in project memory). Zero new failures; two new
passing tests (`tests/test_pricing.py`'s worked example and fail-closed test).

`.venv/bin/python -m twin verify` (final, after all fixes):
```
RESULT: 69 passed, 2 failed, 2 skipped (0 pending invariants, 2 skipped and not faked)
  FAIL drift_window_is_actually_being_sampled: the window is open and the newest sample is 5 day(s) old ...
  FAIL flux_coverage_floor_is_still_reachable: the pre-registered coverage floor of 90% can no longer be reached ...
```
Same two pre-existing failures, nothing else — including the new harness check (#57 in the run,
`mitigation_credit_is_gated_on_corroborated_enactment_not_just_claimed_evidence`, PASS) and both
netflix-beat guards (#26 `netflix_substrate_is_free_running_and_every_plant_carries_a_horizon`,
PASS, still seeing exactly the six real spine facts; #27
`netflix_runs_both_paths_and_the_curve_keeps_the_disagreement`, PASS, the lever now priced with
credit). (Up from 68 passed before this ticket, since `identical_pins_identical_bytes` is the
flaky one named above and the golden-digest re-bless cleared what would otherwise have been a
third failure there.)

`twin verify --bless-goldens --authorise "decision ticket 18 — enactment reaches full, AC 5 closed
(build ticket 86)"`:
```
golden digests -> golden-digests.json (12 artefacts)
```

`.venv/bin/python -m twin grade` (relevant lines):
```
==> enactment: full  (5/5 of decision ticket 18)
  [x] 5. The action-state feedback path that closes ticket 08's conditional-forecast loop.
        build ticket 86: ...
==> aggregate: 61 of 73 across 13 capabilities, 9 at `full`
```
