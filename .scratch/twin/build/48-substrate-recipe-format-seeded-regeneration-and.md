# 48 — Substrate recipe format, seeded regeneration, and the authored-or-derived spike

**What to build:** The substrate is **regenerable, not merely stored**: a versioned recipe plus a seed reproduces it.

This ticket also runs a **cheap spike on a structural tension that would otherwise surface at ticket
52 or the final coherence audit**. `substrate-generator` is a skill — grade-5, non-deterministic —
yet regeneration demands determinism-given-pins for anything derived, and regenerated substrate is
not byte-reproducible across model versions. So: is regenerated substrate **authored** (content-
hashed, outside attestation) or **derived** (attested)? Answer it here with a toy substrate and a
`twin verify` attempt, for pennies, rather than architecturally later.

**Blocked by:** 42, 10

**Status:** ready-for-agent

**Reading list:** Decision tickets 12, 14. Spec stories 3, 55, 64.

- [ ] Recipe format is versioned; recipe + seed regenerates a toy substrate.
- [ ] **Spike answered and recorded**: regenerated substrate is classified authored or derived, with the reasoning and its consequences for pin capture and anomaly detection written down.
- [ ] The content-hash exception from ticket 01 is exercised for real.
- [ ] If the answer is 'authored', the boundary is explicit and `derived_never_human_signed` is checked against it.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
