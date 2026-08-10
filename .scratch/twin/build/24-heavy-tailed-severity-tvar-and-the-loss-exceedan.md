# 24 — Heavy-tailed severity, TVaR, and the loss-exceedance curve

**What to build:** Lognormal body with a Pareto/GPD tail, **TVaR rather than VaR**, and loss-exceedance curves as the
output shape.

TVaR not VaR is load-bearing: VaR tells you the threshold and says nothing about what lies beyond
it, which is the entire region a risk engine exists to reason about. This is also one of the two
hardest tickets in the plan and gets a window to itself for that reason.

**Blocked by:** 23

**Status:** done (2026-08-10)

**Reading list:** Decision ticket 09; research 02 (risk and threat SOTA). Spec: Out of Scope (why TabFM was rejected — a single-scalar regression head cannot express this, and ±4σ clipping amputates exactly this tail).

- [x] Lognormal body + GPD tail composition with the threshold-selection method declared.
      `twin/severity.py` splices a lognormal body to a GPD tail at an authored peaks-over-threshold
      cut `u`; `tail_probability` (the mass beyond `u`) is *derived* from the body at `u` rather
      than authored a second time, so the splice is continuous by construction. The
      threshold-selection method is declared in the module docstring: `u` is authored directly,
      not fit by a mean-residual-life plot or a Hill estimator — that empirical work is build
      ticket 25's, not this one's.
- [x] TVaR implemented with property tests, including behaviour at the shape-parameter boundary where the mean stops existing.
      `Severity.tvar()` (McNeil & Frey closed form), refusing at `xi >= 1` where a GPD's mean does
      not exist, and refusing below the declared tail (out of scope — see the `ponytail:` note).
      `tests/test_severity.py` covers both boundaries plus a sampler-converges-on-the-closed-form
      property test.
- [x] Loss-exceedance curve as an artefact type.
      `twin severity` emits `loss-exceedance-curve` (`verbs.severity_curve`), standalone like
      `twin reliability` — no organisation, no component, no severity slot on the schema.
- [x] A test demonstrating that a VaR-shaped summary would have hidden a tail this correctly surfaces.
      `test_a_var_shaped_summary_hides_what_tvar_surfaces`: two severities sharing a body,
      threshold and GPD scale but differing tail shape carry an identical VaR at the threshold's
      own exceedance probability, and a materially different TVaR.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      New harness guard `a_var_shaped_summary_hides_what_tvar_surfaces` (not a 17th named
      invariant — the constitution's sixteen are fixed; this is the same shape as build ticket
      16's and 31's guards). No existing invariant body changed.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      `CAPS_SEVERITY = ["currency-regimes"]` (decision ticket 09); the artefact's depth block
      reports the capability's real, computed grade (`partial`, 3/6) rather than anything this
      ticket asserts about itself. `twin/capabilities/currency-regimes.yaml` AC 4's comment is
      updated to record that existential/tail risk now has a treatment; AC 4 itself stays
      unchecked because ethical harms still wait on build ticket 61.
