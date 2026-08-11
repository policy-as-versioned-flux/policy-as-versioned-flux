# 07 — `twin score` — a forecast is scored against a known outcome

**What to build:** The skeleton closes. A forecast is scored against a recorded outcome and a score card comes out.
Crude scoring is fine here; ticket 08 makes it proper. What matters is that the loop is closed
before anything else is deepened, because **scoring dictates what every other component must
record** and retrofitting it means revisiting everything.

**Blocked by:** 06

**Status:** done (2026-08-05)

**Reading list:** Decision tickets 20 (scoring in the first slice), 11. Spec: Implementation Decisions, 'Scoring, first'.

- [x] A recorded outcome scores a forecast and emits a score card artefact.
- [x] The score card names the forecast it scored by pin, not by path.
- [x] End-to-end demonstration: one command sequence runs sense → run → score from a clean checkout.
- [x] The walking skeleton is declared complete at **stub** depth against every capability it touched, with the checklist showing exactly what is unchecked.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.

## Built (2026-08-05)

`twin/verbs.py` `score()`, `twin/demo.sh`.

- A recorded outcome scores every forecast in a bundle addressing its proposition, Brier for now
  (build ticket 08 makes it proper). The score card names the bundle by **sha256 and pins**; a test
  asserts no filesystem path appears anywhere in it.
- `twin/demo.sh` is the end-to-end: build a clean fixture repository, sense, run, score, rebuild the
  derived index from git alone, prove byte-identity, and prove a dirty tree is refused.
- The fixture carries both co-flagships at toy depth: Netflix retrospective with an answer key, Intel
  live with a forecast and nothing yet to score it against. The Netflix believed map scores worst
  (Brier 0.5625) against the rival-fast model (0.0361) — belief versus revealed, which is the
  anticipation failure the whole engine exists to measure.

**The skeleton is complete and it is a skeleton.** Five capabilities, one `stub` and four `partial`,
**4 of 30** acceptance criteria across five decision tickets ticked, every unticked one named in every
artefact it touches. Because `domain-model` is `stub`, every artefact's overall depth computes to `stub`
— which is what this ticket asks for, reached by the checklist rather than asserted. See
`twin/README.md` for the full honest boundary.

## Review round (2026-08-05)

Four adversarial reviews ran against the first pass — correctness, spec-conformance, mutation-testing
and security. What they found is the reason several things above read differently from how they were
first written:

- **Three guards did not bite.** `no_invariant_pending_past_its_ticket` compared the whole status line
  against a set, so `done (2026-08-05)` — the format this repository writes — never read as closed.
  `hash_changes_are_authorised` compared the working tree against `HEAD`, which in CI are the same
  object. The refusal blocklist was unprotected, and both refusal checks derived their expectations from
  the dict they were policing. All three are fixed and each now has a test that plants the weakening.
- **Three capability ticks were withdrawn**, each having rested on one clause of a multi-clause
  criterion. The count went 7 → 4.
- **Three mutations survived the first test suite**: the grade-5 binding refusal, the worst-grade rule in
  the depth block, and the ambiguous-`--org` refusal. All three now have tests; `tests/test_refusals.py`
  exists because of this round.
- **Determinism had two real holes**: `core.quotePath` silently dropped non-ASCII paths from a listing,
  and `world_ref` accepted a branch name, so identical pins could give different bytes on different
  machines or on different days. Both refused now.
- **Security**: repository-local git config could execute a command, a ref could smuggle a git option
  into `git show --output=`, and a YAML alias bomb expanded 476 bytes into 15 GB at serialisation. All
  three closed; see "What a hostile model repository cannot do" in `twin/README.md`.
