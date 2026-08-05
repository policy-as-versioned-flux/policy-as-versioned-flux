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

**Status:** ready-for-agent

**Reading list:** Decision tickets 07, 08, 09. Spec: Testing Decisions.

- [ ] A ≈5-component, 6-edge org with named elasticities, committed as a fixture.
- [ ] A worksheet computing the expected propagated influence and expected price **by hand**, with the arithmetic shown so a reviewer can check it without running the code.
- [ ] A CLI-level test asserting the artefact matches the worksheet.
- [ ] Every subsequent derivation-path ticket adds its own line to the worksheet — stated here as the contract those tickets inherit.
- [ ] The worksheet is human-authored and signed as such; it is the one place a human number is the authority.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
