# 31 — The credibility prior: blending world layer and sparse overlay

**What to build:** **Bühlmann–Straub credibility theory**: the industry prior lives in the world layer, sparse
own-data lives in the overlay, and the blend gives a thinly-evidenced org a defensible prior rather
than either a fabricated number or nothing.

This is the capability the world/overlay split exists to enable, and an earlier draft delivered the
split without ever delivering the blend.

**Blocked by:** 4, 23

**Status:** done (2026-08-10)

**Reading list:** Decision tickets 07, 09; research 02. Spec story 5.

- [x] Credibility weighting implemented with property tests: weight on own-data rises with own-data volume and falls with own-data variance.
      `twin/credibility.py::credibility_z()` implements `Z = n / (n + K)`,
      `K = own_variance / world_variance`. `tests/test_credibility.py` parametrises both
      directions — `test_z_rises_with_own_data_volume` and `test_z_falls_as_own_variance_rises` —
      over a grid rather than one hand-picked pair, plus the third property the formula also
      guarantees: `test_z_rises_as_world_variance_rises` (a wider, less certain industry prior is
      overridden faster by the same own evidence).
- [x] An org with no own-data prices from the world prior alone, and says so.
      `blend()` returns the industry triple **exactly** when `n == 0`; `Blend.as_dict()`'s
      `own_data` carries `"n": 0, "note": "no own-data observations; pricing from the world-layer
      prior alone"`. `tests/test_credibility.py::test_no_own_data_prices_from_the_world_prior_alone`
      proves the property against a synthetic triple; the real pocket-org fixture subject
      `payment-fraud-loss` — which deliberately carries a world-layer prior and no `own_data`
      file — is exercised by harness guard `credibility_blend_falls_back_to_the_world_prior_alone`
      and by `tests/test_seam1_cli.py::test_credibility_with_no_own_data_returns_the_world_prior_exactly`,
      not by the unit test above (a review pass caught this citation naming the wrong test for the
      fixture-level leg, and it is corrected here).
- [x] The blend is visible in the artefact — which component of the estimate came from where.
      `Blend.as_dict()`'s `credibility` block carries `own_component` and `world_component`
      (which sum to the blended mode), plus `z`, `k`, `own_data` and `world_prior` in full —
      never just the resulting number. `twin credibility --subject S --out F` emits it as an
      artefact; `twin/pocket-org-worksheet.md` lines 77-82 hand-check every figure for
      `identity-store-incident-cost`.
- [x] Re-estimating as own-data accumulates is a normal operation, not a re-authoring.
      `blend()` is a pure function of an industry triple and an observation list — no regrade
      record, no ceremony. `tests/test_credibility.py::test_re_estimating_as_own_data_accumulates_is_a_normal_read`
      re-runs it with more observations at the same spread and shows `z` simply rises.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      A new harness guard, `credibility_blend_falls_back_to_the_world_prior_alone`, registered in
      `twin/invariants/harness.py` — the same shape as `worksheet_matches_the_pocket_org`. No
      existing invariant's pinned body or `refuses_keys` changed, so no authorising citation was
      needed.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      `twin verbs.py::credibility()` calls `caps.depth_block(CAPS_CREDIBILITY)` against the
      existing `currency-regimes`, `domain-model` and `provenance` checklists. No new capability
      file was added and no existing checklist item was ticked — decision ticket 09's remaining
      criteria (the objective function, rival-model spread, each named incommensurable) are each
      about a different thing than *how* a prior is estimated, so ticking one would overclaim;
      the artefact's depth stays `partial` at the same denominators as before.
