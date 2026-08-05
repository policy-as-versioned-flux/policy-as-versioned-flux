# 30 — Response pricing and evidence-graded mitigation credit

**What to build:** Candidate **responses** priced in the same unit as impacts, so an HR lever, a security control and
a strategic play are directly comparable and the cheapest proportionate one can be identified.

**Mitigation credit is itself evidence-graded**, which closes the classic unfalsifiability loophole:
"the incident didn't happen *because* of our control" is a causal claim like any other and must
carry its grade.

**Blocked by:** 29

**Status:** ready-for-agent

**Reading list:** Decision ticket 09. Spec stories 26, 28.

- [ ] Responses are priced on the same scale as impacts, from any domain.
- [ ] Mitigation credit carries an evidence grade and is use-gated on the same rule as any other claim.
- [ ] An ungraded mitigation claim yields no credit rather than default credit.
- [ ] A worked comparison in which a non-technical lever prices below a technical control, demonstrating the cross-domain claim.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
