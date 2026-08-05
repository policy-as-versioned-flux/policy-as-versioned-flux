# 10 — Pin capture and `twin verify`

**What to build:** Derivation is reconstructable rather than materialised — which works precisely because git is the
source of truth and everything else is derived. `twin verify` takes an artefact, recomputes it from
its pins, and reports whether it reproduces.

This is where determinism-given-pins stops being an aspiration. Includes the **cross-machine**
question: seeded floating-point identity across platform maths libraries and reduction orders is an
architectural constraint, and finding it late forces re-architecting the artefact format under sunk
cost.

**Blocked by:** 03

**Status:** done (2026-08-05)

**Reading list:** Decision ticket 14 (provenance and attestation). Spec stories 61, 64.

- [x] `twin verify <artefact>` recomputes from pins and reports reproduce / diverge with a diff.
- [ ] Verification runs on a different machine from the one that produced the artefact, in CI.
- [x] A deliberately non-deterministic operation is caught by verify rather than passing silently.
- [x] Any tolerance or normalisation needed for cross-platform float identity is a **declared, tested** property of the artefact format, not an implicit one.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.

## Built (2026-08-05)

`twin/reproduce.py`, exposed as `twin verify <artefact> --repo <path>`.

- **The chain, not just the artefact.** Reproducing a score card recomputes the forecast bundle it
  scored — from the pins the card recorded — and checks that bundle's digest against the digest the card
  claimed, before re-scoring. That is decision ticket 14's reconstructable derivation, executed rather
  than described.
- `--repo` is required and the error says why: a pin records *which* model tree was read, not *where*
  that repository lives on this machine. A repository that does not hold the pinned commit and tree is
  refused rather than diffed — that is a wrong repository, not a divergence.
- A repository whose world has moved on still reproduces an artefact pinned to an earlier commit. That
  is the whole point of pinning rather than pointing, and it has a test.
- **Tolerance is zero.** Comparison is byte equality. Where platform maths could differ in the last unit
  in the last place — `log`, in the scoring rules — the **format** declares a 12-significant-digit
  quantisation and the comparison stays exact. Putting the tolerance in the format rather than in the
  comparison is what makes it a stated, tested property instead of a silent one. It is not a proof:
  two values straddling a rounding boundary would still diverge, and the CI matrix is what would catch
  that. The declaration travels in the report.
- A deliberately non-deterministic operation is caught, with a unified diff naming the field that moved.

## Review round (2026-08-06)

- **The chain replayed the bundle at the wrong pin.** It used the *card's* model-repo pin rather than
  the bundle's own, so every card whose answer key was committed after the forecast was made — which is
  the normal case, since a forecast is made before it resolves — reported DIVERGES. The headline claim
  of this ticket was false for the ordinary workflow. Fixed, and the ordinary workflow now has a test.
- **`twin verify` had no invariant coverage at all.** Deleting the digest comparison entirely left the
  suite at 15/15. `identical_pins_identical_bytes` now has an operational leg: emit a card, reproduce
  it, and assert a hand-edited one does not reproduce.
- An unknown verb, a missing flag or a malformed command produced a traceback rather than a refusal.
- `_spill` wrote a temporary file per verification and never removed it; 43 had accumulated from the
  test suite alone.

**Left unchecked, deliberately: cross-machine verification has never run.** The workflow now has a
`reproduce-elsewhere` job — the x86_64 Linux runner emits a score card, macOS arm64 downloads it, builds
the model repository from the same deterministic recipe, and reproduces it from its pins. Declared and
wired; unproven until CI runs it.
