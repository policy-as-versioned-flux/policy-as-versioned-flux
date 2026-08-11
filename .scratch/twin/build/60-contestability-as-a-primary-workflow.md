# 60 — Contestability as a primary workflow

**What to build:** **Arguing with the artefact is the supported workflow, not a complaints box.** Challenges are
versioned objects against specific artefacts, and there is **no hiding behind aggregation** — a
challenge to a constituent cannot be deflected to the roll-up.

Pulled early: an earlier draft parked this at position 61 of 72, which is a strange place for
something the spec calls a primary feature. It needs artefacts and signatures, and nothing else.

**Blocked by:** 11, 12

**Status:** done (2026-08-10)

**Reading list:** Decision tickets 07, 15. Spec story 77.

- [x] A challenge is a versioned, signed object attached to a specific artefact and claim.
      `twin/challenges.py` — a challenge names exactly one dotted claim-path (the same format
      `canon.walk_values` produces) in exactly one artefact, and freezes the value it disputed at
      the moment raised. `tests/test_challenges.py::test_raising_a_challenge_captures_the_claimed_value`,
      `test_cli_raises_and_signs_a_challenge`.
- [x] A challenge against a constituent cannot be answered by pointing at an aggregate.
      `challenges.resolve()` takes no `claim_path` parameter — the path a resolution addresses is
      read out of the challenge it resolves, structurally rather than by review
      (`tests/test_challenges.py::test_resolve_inherits_the_challenges_own_claim_path`,
      `test_a_challenge_to_a_constituent_is_not_closed_by_a_resolution_to_an_aggregate`,
      `test_a_resolution_naming_a_different_claim_is_refused`). Harness guard
      `a_challenge_to_a_constituent_survives_an_unrelated_resolution` demonstrates the failure mode
      directly.
- [x] Challenges are visible wherever the challenged artefact is visible.
      `twin verify <artefact> --challenge C1 --challenge C2` prints every open and resolved
      challenge before reproducing it; `challenges.for_artefact()` is the one function that decides
      what counts as open (`tests/test_challenges.py::test_cli_resolve_then_verify_shows_the_status`,
      `test_for_artefact_partitions_open_and_resolved`).
- [x] An unresolved challenge is a displayed state of the artefact, not a hidden queue.
      Same mechanism as above — `twin verify` shows open/resolved state inline rather than in a
      separate report a reader has to know to look for
      (`tests/test_challenges.py::test_cli_resolve_then_verify_shows_the_status`, which shows an
      unresolved challenge printed as `"OPEN"` at the verify call site itself).
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One harness guard added (`a_challenge_to_a_constituent_survives_an_unrelated_resolution`),
      zero weakened. Cites decision tickets 07 and 15.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      No capability file ticks against this ticket: it is a cross-cutting workflow over signed
      artefacts, not a criterion of any of the seven tracked capabilities. Landed and ticked
      nothing.

**Retroactive closure note (build ticket 34).** Built and committed at `ace64f8` ("Build tickets
25, 32, 37, 38, 42, 60 and 62"), but this file's own `Status:` line and checklist were never
updated at the time. Found and closed during the build ticket 34 coherence audit; see ticket 25's
identical note for how.
