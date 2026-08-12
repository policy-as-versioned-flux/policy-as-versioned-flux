# 15 — The pocket-org golden fixture

**What to build:** **The continuous coherence mechanism, and the answer to the class of failure refusal tests cannot
catch.** A refusal test catches a reintroduced absence. It is satisfied by a degenerate system: a
PERT triple that is present but garbage, a score tagged with the *wrong* regime, a contamination
discount hardcoded rather than measured, an elasticity that stops being recalibrated three tickets
later. All of those stay green.

So: a tiny hand-computable organisation — roughly five components, six edges, known elasticities —
with its expected numbers **worked out by hand in a committed worksheet**. Every ticket touching the
derivation path must keep the pocket-org artefact matching the worksheet.

This also decouples two tracks. The £ chain takes a distribution as input; it does not care whether
that distribution came from Monte-Carlo propagation or from this fixture. Committing it here is what
lets pricing run parallel to propagation instead of behind it.

**Blocked by:** 12

**Status:** done (2026-08-06)

**Reading list:** Decision tickets 07, 08, 09. Spec: Testing Decisions.

- [x] A ≈5-component, 6-edge org with named elasticities, committed as a fixture.
- [x] A worksheet computing the expected propagated influence and expected price **by hand**, with the arithmetic shown so a reviewer can check it without running the code.
- [x] A CLI-level test asserting the artefact matches the worksheet.
- [x] Every subsequent derivation-path ticket adds its own line to the worksheet — stated here as the contract those tickets inherit.
- [x] The worksheet is human-authored and signed as such; it is the one place a human number is the authority.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.

## Built (2026-08-06)

`fixtures.build_pocket_org`, `twin/pocket-org-worksheet.md`, `twin/worksheet.py`, `twin worksheet`,
and the `worksheet_matches_the_pocket_org` guard.

- **Five components, six edges, every number hand-computable.** Four structural edges and two causal
  ones, one of the two with a real range and one degenerate, so both paths are exercised. The world
  layer holds no components and names no tenant, so `world_never_references_overlay` holds here too.
- **The worksheet is the yardstick and the code has to match it.** Twenty-nine lines, each with the
  arithmetic shown, so a reviewer can check it without running anything. Twenty-three are computable
  today and match; six carry their arithmetic already and name the build ticket that must make them
  computable — three for propagation (20) and three for price (30).
- **A pending line is not a passing line.** A line whose build ticket has already closed fails, the
  same shape as `no_invariant_pending_past_its_ticket`. That is what stops the worksheet quietly
  becoming a list of things nobody ever wired up.
- **Compared at six decimal places, declared in the worksheet** rather than hidden in the comparison,
  because the expected column is decimal and the computed one is binary floating point.
- **Authored, and signed as such.** `twin worksheet --emit` writes it as an `authored` artefact and
  signs it as the `worksheet-author` role from the register. Everywhere else in this system a
  hand-typed number is refused; this is the one place a human number is the authority, and the
  authored/derived mark is what says so.
- The guard is a harness check rather than a seventeenth invariant: the worksheet is a **second
  yardstick** alongside the constitution, and the constitution's sixteen may not grow without it
  changing first.

This is what closes the gap a refusal test structurally cannot: a triple that is present but garbage,
an elasticity nobody recalibrated three tickets later, a propagation that changed unnoticed. All three
keep every refusal test green. Two tests plant exactly those and both fail the worksheet.

Not built: the £ line is authored from a **severity with no empirical anchor** — a fixture number,
stated as such, which build ticket 25 replaces. The constraint pre-filter that must run before any of
it is build ticket 28 and gets its own line when it lands.
