# 25 — Empirical severity anchoring

**What to build:** Anchor the severity distributions to real evidence — Cyentia IRIS, Verizon DBIR-class sources —
so the parameters are defensible rather than illustrative. Separated from ticket 24 because the
implementation and the empirical work are different jobs and each needs its window.

**Blocked by:** 24

**Status:** done (2026-08-10)

**Reading list:** Decision ticket 09; research 02. Spec story 28.

- [x] Named public sources with dated citations for each anchored parameter.
      `twin/severity-anchors.yaml`'s `data-breach-loss` subject cites Cyentia Institute, IRIS 2025
      by URL, with a `dated`/`accessed` pair per quantile; `mu`, `sigma` and `threshold` are each
      anchored from those two cited quantiles (`twin/anchoring.py fit_lognormal`/`anchored`).
- [x] Anchoring is a versioned artefact, so a re-anchoring is a visible change.
      `anchoring.pin()` reports the file's `version` and digest, and every artefact `twin severity
      --anchor` emits carries the pin — the same discipline the evidence ladder and the constraint
      set already apply. `tests/test_anchoring.py::test_a_bad_anchor_file_is_refused_not_silently_loaded`
      asserts the loader, not just the intent.
- [x] Where no defensible anchor exists, the parameter is marked as unanchored rather than quietly assumed.
      `xi` and `beta` carry `anchored: false` and a stated `reason` in the data file; the loader
      refuses a parameter typed `anchored: false` with no reason, and a parameter typed
      `anchored: true` with no method (`tests/test_anchoring.py::test_an_unanchored_parameter_with_no_reason_is_refused`).
      Harness guard `unanchored_severity_parameters_are_marked_not_assumed` checks both legs
      against the committed subject directly.
- [x] Sensitivity of the headline outputs to each anchor is reported.
      `twin/anchoring.py sensitivity()` sweeps the unanchored `xi` alone, holding every anchored
      parameter and `beta` fixed, and reports the min/max TVaR across the grid
      (`tests/test_anchoring.py::test_sensitivity_varies_only_the_unanchored_xi`).
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One harness guard added (`unanchored_severity_parameters_are_marked_not_assumed`), zero
      weakened; the constitution's fixed sixteen are untouched. Cites decision ticket 09.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      No capability file ticks against this ticket. `currency-regimes` AC 4 ("treatment of each
      named incommensurable, incl. where we refuse to price") is the criterion this work speaks to
      closest, and it stays unchecked: `twin/README.md`'s honest-build narrative already states
      five of six named incommensurables is not each of them, and anchoring existential/tail risk's
      *parameters* is not the same claim as treating incommensurability itself. Landed and ticked
      nothing, which is the honest number rather than a disappointing one (the same shape build
      tickets 16 and 31 landed in).

**Retroactive closure note (build ticket 34).** This ticket's code, tests and harness guard were
built and committed at `ace64f8` ("Build tickets 25, 32, 37, 38, 42, 60 and 62"), but this file's
own `Status:` line and checklist were never updated at the time. Found during the build ticket 34
coherence audit while reconciling `twin/README.md`'s stale "30 of 77 build tickets closed" banner
against what is actually built; recorded and closed here
rather than left silent.
