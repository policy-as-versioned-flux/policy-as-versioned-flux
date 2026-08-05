# 11 — Signing: accountability, origin, and the derived-artefact anomaly

**What to build:** **Human signatures assert accountability for a judgement. Agent signatures assert reproducible
origin only** — runtime, model version, config — so agent output never inherits human authority.

The consequence is the interesting part: signatures attest the *absence* of human involvement,
CI-style, which makes the authored/derived split cryptographically enforceable. A derived artefact
carrying human fingerprints becomes a **detectable anomaly** rather than a convention breach.

Role-not-person signatures land here: accountability attaches without creating a personal target.

**Blocked by:** 10

**Status:** ready-for-agent

**Reading list:** Decision tickets 14, 15. Spec stories 62, 63, 73.

- [ ] Human and agent signature types are distinct and non-interchangeable.
- [ ] `derived_never_human_signed` goes live; a planted human-signed derived artefact fails the check.
- [ ] An agent signature carries runtime, model version and config, and asserts nothing about correctness.
- [ ] Signatures bind to roles, not named individuals, and the role register is versioned.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
