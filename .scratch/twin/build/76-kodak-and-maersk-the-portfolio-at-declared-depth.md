# 76 — Kodak and Maersk: the portfolio at declared depth

**What to build:** The portfolio subjects, each carrying a depth grade and upgradable on its own independent track.

They are a ticket rather than an assumption because an earlier draft had them in the spec's Subjects
section and in no ticket at all — which is how a subject silently vanishes. If they are not built,
they go in the does-not-do register **by decision**, not by omission.

**Blocked by:** 70

**Status:** ready-for-agent

**Reading list:** Decision tickets 01, 06. Spec: Implementation Decisions, Subjects.

- [ ] Both subjects present at a declared, computed depth grade — `stub` is an acceptable outcome, silence is not.
- [ ] Each is on an independent upgrade track, not gated on the flagships.
- [ ] Anything not built is entered in the does-not-do register with its reason.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
