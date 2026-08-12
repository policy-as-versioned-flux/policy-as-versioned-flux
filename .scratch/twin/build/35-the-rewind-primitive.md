# 35 — The rewind primitive

**What to build:** Rewind to a dated past state — Pearl's **abduction**. The first of the two primitives from which
everything else composes.

**Blocked by:** 20

**Status:** done (2026-08-07)

All six criteria are met. Rewind resolves the declared time to the last commit at or before it and
opens the repository there, so what comes back is a model state that every downstream reader treats
as ordinary. The test that matters is the recalibration one: an elasticity widened in a later dated
commit reads at its **old** value after a rewind, which a filtered view could not do — a filter can
hide rows added since and cannot restore a number that was overwritten, so a backtest through one
would score the past with today's figures.

Because the rewound repository is an ordinary repository, `do()` at a past time needed no code at
all; the composition test asserts it rather than the implementation providing for it.

**One bug found and fixed during review, worth recording because it is the same shape as the
criterion above.** `git rev-list --before=not-a-date` exits 0 and returns HEAD. A typo'd timestamp
would therefore have answered a question about the past with today's model, silently, and the
artefact would have recorded the typo as `rewound_to` beside the newest commit. The time is now
parsed before git sees it, an unparseable one is refused, and so is a year outside git's own
1970-2099 window — `datetime.fromisoformat` accepts `1968-06-01` and git reads it as `now`, which
is the same silent wrong answer wearing a valid-looking date. The check also moved: it was only
reachable through the CLI, so `twin/verbs.py` now verifies the pin it was handed against the time
it was told, and every caller inherits the refusal rather than one. A time with no offset is read as UTC
explicitly, so the same command does not rewind to different commits in different timezones.

Decision ticket 13 AC 2 stays unchecked: rewind and play are built and distinguished, fast-forward
is build ticket 37.

**Reading list:** Decision ticket 13. Spec story 38.

- [x] Rewind to a declared timestamp produces a model state, not a filtered view.
- [x] The mapping to abduction is documented and the semantics tested, not asserted as a metaphor.
- [x] Rewind composes with intervention (`do()` at a past time) without special-casing.
- [x] Rewinding to a time before the model existed fails explicitly rather than returning an empty state.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
