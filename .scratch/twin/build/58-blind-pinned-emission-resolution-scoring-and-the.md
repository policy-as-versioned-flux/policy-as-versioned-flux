# 58 — Blind pinned emission, resolution scoring, and the narrow claim

**What to build:** Forecasts emitted, **pinned and signed before the resolution window opens**, on the same questions
and timestamps as liquid prediction markets. Forward-dated questions cannot be in any training
corpus, so this is the one external gate contamination cannot reach.

**Observe only, never place** — no UK gambling exposure, and play money tracks real money to within
1–5 percentage points anyway, so money-backing buys nothing.

The claim scope is stated **narrowly on purpose**: evidence of non-overconfidence in general
world-forecasting, and **nothing** about Wardley propagation, elasticities, £ pricing or the org
overlay. A real external gate oversold becomes a fake one.

**Blocked by:** 57, 11

**Status:** done (2026-08-13)

**Reading list:** Decision ticket 21; research 17 (prediction markets). Spec stories 48, 51, 52.

- [x] Emission is signed and pinned before the resolution window, verifiably.
- [x] Resolutions score against the same questions and timestamps, co-registered.
- [x] No code path places a position; observe-only is structural.
- [x] The narrow claim scope is published **with** every result, stating what the gate does not evidence.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.

## Built (2026-08-13)

`twin/forecast_book.py`, `twin/capabilities/forecast-book.yaml` (three more of decision ticket
21's six acceptance criteria ticked), one harness guard
(`forecast_book_is_blind_by_construction_and_observe_only`), `tests/test_forecast_book.py`.

- **Blind emission is refused structurally, not reviewed.** `emit()` refuses to build a
  `forecast-emission` artefact timed at or after its question's own declared
  `resolution_window_opens_at` — checked at the boundary itself and past it, not only on obviously
  late input (`tests/test_forecast_book.py::test_emit_refuses_at_the_resolution_window_boundary_and_past_it`).
  `is_blind()` is the *same* function the refusal calls internally, so an auditor holding nothing
  but the emitted artefact's own recorded body can recompute the identical check later, rather
  than trust that the refusal fired at build time.
- **Signed and pinned via the existing machinery, reused rather than reinvented.** `emit()`
  returns a `derived` `Artefact` — the exact shape `twin/attest.py`'s `build()` already agent-signs
  and refuses a human signature on (`derived_never_human_signed`, unchanged, reused rather than
  re-implemented). `tests/test_forecast_book.py` exercises this directly against the real
  `twin/sign.py`/`twin/attest.py` machinery: a genuine agent-signed sidecar round-trips clean
  through `attest.check()`, and a hand-built human signature on an emission is refused.
- **Resolution scoring is co-registered, not merely same-named.** `score_resolution()` accepts no
  question id or timestamp as a fresh parameter — both travel from the pinned emission's own pins
  and body, so a resolution can only ever be scored against the exact question and the exact
  emission it was pinned to. A doctored emission whose body no longer attests blindness against
  its own recorded timestamps is refused rather than scored
  (`test_score_resolution_refuses_a_doctored_emission_that_no_longer_attests_blindness`) — a
  defence against a forged or hand-edited artefact, not only against the honest path `emit()`
  already gates.
- **Scoring reuses `twin/scoring.py`, never a second implementation.** `score_resolution()` calls
  `scoring.score()` directly; `tests/test_forecast_book.py` and the harness guard both assert its
  output reproduces `scoring.brier()`/`scoring.log_loss()` bit for bit, and the harness guard
  additionally asserts the call is actually present in `score_resolution`'s own source.
- **Observe-only is structural, not a convention (decision ticket 21 Q4).** `twin/forecast_book.py`
  exposes exactly three functions — `emit`, `score_resolution`, `is_blind` — asserted as an
  **allow-list** by both the unit test and the harness guard, the same discipline
  `prefilter_precedes_pricing` uses on `twin/options.py`: a differently-named position-placing
  function would still be caught, not only one matching an obvious keyword. Every emission's body
  also records `observe_only: true, position_placed: false` directly.
- **The narrow claim scope travels with every result, not stated once in prose (decision ticket 21
  Q5).** `CLAIM_SCOPE` is carried in the body of both the `forecast-emission` and the
  `resolution-score` artefacts: `evidences` names non-overconfidence in general world-forecasting
  on a pre-registered, blind, co-registered question set; `does_not_evidence` names Wardley
  propagation, the causal elasticities, £ pricing and the org-specific overlay explicitly, checked
  against the emitted body in both suites rather than asserted only here; `residual_limit` restates
  decision ticket 21 Q1's own honesty condition — the quarantine (build ticket 57) proves no
  *direct* ingestion, never that the twin's priors were unshaped by market-adjacent information
  arriving some other way.
- **Three more of decision ticket 21's six acceptance criteria are honestly ticked** (venue +
  observe-vs-participate, the blind-emission protocol, the claim-scope statement) — bringing
  `forecast-book` from build ticket 57's 1/6 to **4/6**, still `partial`. The remaining two —
  circularity (the ingestion-side quarantine enforcement on a *live* signal path is build ticket
  59's) and the proportionality verdict (a judgement already recorded in decision ticket 21's own
  resolution text, not a code artefact this or any build ticket computes) — stay honestly unticked.
- Extends the invariant suite with one harness guard — no manifest or golden-digest change to the
  constitution's fixed sixteen, the same shape
  `benchmark_selection_is_mechanical_and_quarantine_catches_a_planted_breach` (build ticket 57) is:
  a property of this module's own contract, not one of the sixteen fixed names. Ticking three more
  criteria on `twin/capabilities/forecast-book.yaml` does move `Capabilities.digest`, and every
  artefact's pins with it, so `twin/invariants/golden-digests.json` was re-blessed via
  `bin/twin verify --bless-goldens --authorise "decision ticket 21 — build ticket 58 (blind pinned
  emission and resolution scoring) changes computed artefact bytes"` in the same change.
- `ponytail:` no `twin` CLI verb, the identical call build ticket 57's own notes make and for the
  identical reason: `emit`/`score_resolution` are typed functions exercised at seam 2, and a real
  venue adapter (build ticket 59) is what would give a CLI invocation a live question to point at.
  Add `twin forecast-emit`/`twin forecast-score` once one exists.
- `ponytail:` timestamps are validated by a fixed-width `YYYY-MM-DDTHH:MM:SSZ` regex and compared
  as plain strings, the identical discipline `twin/regimes.py`'s `cutoff()` already uses for its
  own dated cutoff, rather than reaching for `datetime.fromisoformat` and its looser,
  offset-carrying acceptance — one stdlib type doing less is exactly the shape that keeps "before"
  a fact a string comparison can decide rather than a parser someone has to trust.

**A pre-existing, unrelated failure found while verifying, not introduced here:**
`drift_window_is_actually_being_sampled` fails because the live `estate/driftwood/` cluster probe
(build ticket 64, a different subsystem entirely) has not sampled within its freshness window —
confirmed by `git stash`-ing every change from this ticket back to the exact base commit (c9babc9)
and re-running the check in isolation: it fails identically there, before any of this ticket's
code existed. Not this ticket's to fix — a live-infrastructure probe issue, unrelated to
`twin/forecast_book.py` and outside decision ticket 21's scope. `bin/twin verify` is green on
every other check, including the newly re-blessed `identical_pins_identical_bytes`. This ticket's
own tests (`tests/test_forecast_book.py`, 20/20, plus the new harness guard) and every
previously-green check still pass. `mypy twin tests conftest.py` passes with no issues.
