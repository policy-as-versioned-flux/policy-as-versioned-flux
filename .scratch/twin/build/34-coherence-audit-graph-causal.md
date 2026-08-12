# 34 — Coherence audit: graph → causal → £

**What to build:** A shrunken audit, not a discovery exercise. The pocket-org worksheet has been carrying continuous
coherence since ticket 15, so this ticket confirms rather than explores. **If integration problems
are found here rather than confirmed absent, the plan has failed its own early-detection brief** —
record that as a finding.

**Blocked by:** 33, 21, 22

**Status:** done (2026-08-10)

**Reading list:** The pocket-org worksheet; the invariant manifest. Constitution.

- [x] Full pocket-org run end to end, every worksheet line checked.
      `.venv/bin/python -m pytest tests/test_pocket_org.py` — 8 passed. All 82 worksheet lines
      match the emitted artefacts to 6 decimal places
      (`test_the_artefact_matches_the_worksheet`), and
      `test_every_line_is_either_matched_or_pending_on_an_open_ticket` confirms every line is
      either matched or pending against a ticket still open — none is. Confirmed absent, not
      discovered: the pocket-org worksheet has been carrying continuous coherence since ticket 15
      and this audit found nothing it had missed.
- [x] Units audited across every boundary — the classic silent failure is a units mismatch that no invariant catches.
      Read the £ chain end to end at its module boundaries: `twin/wardley.py` (D/K/R, dimensionless,
      matches the worksheet's hand arithmetic exactly) → `twin/propagate.py` (an elasticity triple
      is a dimensionless share of a shock in the unit interval; `_path_entry` raises if a composed
      influence ever exceeds `1.0`, because above one noisy-OR silently reverses) →
      `twin/pricing.py` (`price = perspective's declared £ valuation × propagated influence`, the
      only multiplication where £ is created, with a closed body so no stray field can carry a
      figure the £ chain didn't derive) → `twin/credibility.py` (own- and world-variance are both
      £², so `Z = n/(n+K)` is dimensionless and the blend stays in £) → `twin/tradeoff.py`
      (`net_cost_of_risk = cost.mode − credit.mode`, both £ from the same `pricing.price()` call).
      `twin/severity.py`'s TVaR is deliberately **not** joined to this chain — its own docstring
      states why (a second authored magnitude per component would let a price be laundered through
      whichever number is watched less) — so it carries no shared-unit obligation with pricing.
      `twin/evidence.py`'s grade ladder is the one scale everything gates on
      (`pricing_threshold`/`path_admission_threshold`), and the loader itself cross-checks every
      rung's `may_price` bit against the threshold on read, so a grade-scale mismatch fails at load
      rather than surfacing as a silently wrong price. No mismatch found.
- [x] No invariant is still pending past its activating ticket.
      `twin/invariants/manifest.yaml`: the only two `state: pending` invariants are
      `price_levels_never_probabilities` (activates at build ticket 59) and
      `standing_library_covers_committed_classes` (activates at build ticket 69) — both still
      ahead of this ticket in the build order. `./bin/twin verify`: 36 passed, 0 failed, 3 skipped
      (the two pending invariants, correctly not yet due, plus one cross-architecture leg that
      skips outside the CI matrix rather than faking a result).
- [x] Any problem found here is recorded with the ticket that should have caught it, and that ticket's ACs are amended.
      One integration problem found, off the graph→causal→£ derivation path itself:
      seven build tickets (25, 32, 37, 38, 42, 60, 62) had real, tested, committed code from
      `ace64f8` and no closed ticket file — `Status:` still read `ready-for-agent` and every
      checkbox was unticked, months of `.scratch/twin/build/` bookkeeping silently behind what
      `twin/`, `tests/` and `twin/README.md` already proved was built. `twin/README.md`'s own
      opening banner was stale for the identical reason, missing those nine tickets entirely and
      separately undercounting ticket 23 (its own checklist was already closed; the banner still
      carved it out as "at `partial`"). Both are amended: the seven ticket files now carry
      `Status: done` and their acceptance criteria checked against the evidence that already
      existed for them (none tick a new capability criterion — `./bin/twin grade`'s arithmetic is
      unchanged, 14/41), and `twin/README.md`'s banner and honest-build narrative now read 41 of
      77 with the finding named in place rather than silently corrected. This is exactly the
      plan-failed-its-brief case
      the ticket anticipates — a bookkeeping gap, not a units or derivation defect, but a real one.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      No invariant or harness guard changed. Nothing here needed one: the audit confirmed the
      existing suite already catches what it claims to, rather than finding a gap the suite itself
      should close.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      This ticket adds no derivation code and ticks no capability criterion — `./bin/twin grade`'s
      arithmetic is unchanged before and after (14/41; every capability's own numbers verified
      unmoved, above). An audit ticket that confirms coherence rather than building a capability
      has no owning decision ticket to grade against; the six-fold `twin verify` / `twin grade` /
      `pytest tests/test_pocket_org.py` run above **is** this ticket's own evidence, computed
      rather than typed, in the same spirit the checklist asks of every other ticket.
