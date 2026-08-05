# 07 — `twin score` — a forecast is scored against a known outcome

**What to build:** The skeleton closes. A forecast is scored against a recorded outcome and a score card comes out.
Crude scoring is fine here; ticket 08 makes it proper. What matters is that the loop is closed
before anything else is deepened, because **scoring dictates what every other component must
record** and retrofitting it means revisiting everything.

**Blocked by:** 06

**Status:** ready-for-agent

**Reading list:** Decision tickets 20 (scoring in the first slice), 11. Spec: Implementation Decisions, 'Scoring, first'.

- [ ] A recorded outcome scores a forecast and emits a score card artefact.
- [ ] The score card names the forecast it scored by pin, not by path.
- [ ] End-to-end demonstration: one command sequence runs sense → run → score from a clean checkout.
- [ ] The walking skeleton is declared complete at **stub** depth against every capability it touched, with the checklist showing exactly what is unchecked.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
