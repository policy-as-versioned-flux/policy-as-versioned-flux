# 67 — Graded enforcement and posture-as-identity, narrowed

**What to build:** Consequence as a **spectrum rather than a cliff edge**, and posture-as-identity retained only where
the evidence supports it.

**Blocked by:** 66

**Status:** done (2026-08-15)

**Reading list:** Decision ticket 18. Spec stories 83, 84.

- [x] Enforcement grades are implemented and a control can occupy any of them.
- [x] Posture-as-identity is scoped to the cases the evidence supports, with the unsupported cases named as excluded.
- [x] Moving a control between grades is a versioned, signed change. **Signed is qualified** — see
      "What this does not do": it attaches to the authored posture artefact and to each move's
      registered role binding, never to the git commit that carried the move.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.

## What was built

`twin/enforcement-grades.yaml` is a versioned four-rung ladder — `observe`, `warn`, `constrain`,
`block` — with `block` the bottom rung of a spectrum rather than the mechanism. Two rungs change
the outcome and two do not, and that property is what everything else is scoped by. Data rather
than code for the reason the evidence ladder is: changing a rung is a diff against a version
number. Each rung states what it admits, what it does not, and what realises it in the estate —
including `warn`, which nothing here realises and says so.

**The load-bearing half is that a rung carries no number, and the assertion is sharper than the
refusal.** Decision ticket 18 Q4 admitted graded enforcement precisely because it needs *no special
status*: the £ engine already prices partial mitigation through a control's own evidence-graded
`mitigates` claim. A reduction per rung would turn that into a free multiplier — tighten the rung,
earn more credit, evidence nothing — which is the unfalsifiable claim build ticket 30 closed. So
the ladder loader refuses a number on a rung, the response schema refuses one inside an
`enforcement` block, and the harness guard asserts that **the same control produces an identical
`Option` at every rung**. `Option` is the only thing the pre-filter accepts and therefore the only
thing that can reach a price, so the rung is structurally invisible to the £.

**Posture-as-identity is computed from two declared facts and cannot be declared.** A control
qualifies only if its rung changes the outcome and its posture is stamped by something that is not
the subject; `posture_as_identity` is refused as an unknown field, the same move that makes a depth
grade derived rather than typed. Five cases are named as excluded and published in the artefact: a
lever that is not code, a rung that changes nothing, a posture the subject can write,
posture-as-identity as a governance philosophy, and proof that a control is in force *now*.
Declaring a trusted stamper at a rung that changes nothing is refused at load rather than computed
to `false` — the field would otherwise sit in the model looking like the claim while meaning
nothing, and a claim reading bigger than it is was the original defect.

`enforcement_moves` is a new overlay collection, versioned exactly like the evidence regrade and
deliberately separate from it: a regrade moves what we *believe*, a move changes what a control
*does*, so neither can be offered in place of the other (asserted). The chain must be contiguous
and end where the control now stands, and `twin validate` reads the response file's **git history**
— the half that catches the first unrecorded move, before any chain exists to be inconsistent with.
The history walk itself was extracted to `evidence.unrecorded_changes` and is now shared by both
records rather than copied, because a second copy of a check like this is how one of them quietly
stops biting.

**Deleting a control's `enforcement` block counts as a move; adding one does not.** The asymmetry
was found reviewing this ticket's own first draft, which read a missing block as nothing and so let
a control be silently un-enforced — the exact absence-shaped weakening the constitution says a diff
never shows. A missing block now reads as `(no rung)`, which is not a valid rung, so no move record
can cover the removal and it is always reported; arriving at a rung stays uncounted, because a
control that gains consequence has none to have moved from.

`twin enforcement --org <org>` emits the posture: the ladder in force, where every control sits,
what its identity proves, the levers that occupy no rung at all, and every recorded move with its
direction derived. **Authored** and signed as `model-steward`, like the constraint set — which rung
a control occupies is a declaration, and criterion 3's point is that somebody stands behind the
consequence a control carries. The netflix overlay's three responses occupy no rung, which is the
majority case rather than an omission: the £ engine's cross-domain comparison exists because most
levers are not code.

`twin/capabilities/enactment.yaml` criterion 4 now ticks, taking decision ticket 18 to 3 of 5. The
capabilities digest moved with it, so the golden digests were re-blessed with the authorising
citation, as build ticket 66 did for the same reason.

## What this does not do

- **Nothing checks that a rung is in force.** A control declaring `constrain` says where it is
  enforced; no cluster is asked whether it is. The same limit build ticket 66 reported on the
  dependency pins, and it is why posture-as-identity's fifth exclusion exists — the identity
  attests the posture at issue, never since. Whether continuous proof of force is required at all
  is build ticket 65's pre-registered question and is open.
- **`signed` is narrower than the criterion reads.** The published posture is authored and carries
  a human signature bound to a registered role, and every move names one. The **git commit** that
  carried the move is not keyless-signed —
  `estate/verify/provenance/verify-provenance.sh` records that this repository's commits are not —
  so the word attaches to the artefact and the role binding, not to the commit. Stated in the
  artefact's own `signed.not_covered` field rather than left to read bigger than it is.
- **`warn` is a rung with no realisation.** Named because the ladder is the vocabulary and a silent
  absence is worse than a stated one, but nothing in this estate implements it.
- **The rung ladder is not wired to the estate's cage tiers.** `estate/platform/graded` expands
  `baseline`/`restricted`/`quarantine` into dials and prices them; this ladder names `constrain`
  as the class those three belong to and does not read them. Wiring them would make the twin's
  rung and the cluster's tier one fact rather than two, and is not built.
- **No control moves rung through the enactment channel yet.** A move is authored in the model and
  published; `twin propose --channel policy` is what would carry it to a repository, and build
  ticket 66's PR channel is still unwired.
