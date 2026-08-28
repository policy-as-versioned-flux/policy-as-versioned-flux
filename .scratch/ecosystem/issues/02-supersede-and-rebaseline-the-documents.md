# 02 — Supersede and rebaseline the documents

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

Make the documents of record agree with the ratified north star. Commit NORTH-STAR.md at the repo root. Add dated superseded-in-part banners to `.scratch/twin/map.md`, `.scratch/twin/spec.md` and `docs/ARCHIVE.md`. Rename `docs/north-star-modern-reference.md` to `docs/modern-reference-transport.md`. Rewrite CONTEXT.md's Gate, Policy version, Orphan guard and proposer entries in cage and schedule vocabulary, and delete 'Nothing starts a run on a clock'. Redraw `.scratch/talk-spec/the-whole-model.md` with no neck and no exemptions ledger, pins as crossing edges, two institutions exploded asymmetrically. Give the twin an entry in CONTEXT.md and README.md.

## Notes

Reversals 1, 2, 21 and re-grill 9 (composition is the eco-system) are the inputs. No history rewrite: banners, not edits to old decisions.

## Answer

Done 2026-08-28. Every item in the question landed, in one commit on `main`.

- `NORTH-STAR.md` is at the repo root. It is a copy of the drift-review original with its relative links fixed and two notes: where it came from, and that all 22 reversals are now confirmed. The phrase "north star" has one referent.
- Dated superseded-in-part banners: `.scratch/twin/map.md`, `.scratch/twin/spec.md` (governance is not one enactment arm; the estate is not a prior to test; the clusters are not binned; the twin's subjects are the adopter orgs), and `docs/ARCHIVE.md` (the hub is not research-only; the archive checklist is not to be executed). No old text was edited.
- `docs/north-star-modern-reference.md` is renamed to `docs/modern-reference-transport.md`, retitled, with a rename banner. Its body no longer calls itself the north star. `README.md` and `docs/PRD.md` point at the new name.
- `CONTEXT.md`: **Lane-keeping vs. gate** is replaced by a **Cage** entry (no gate; four rungs; bottom rung is "too expensive to run or not functional"; unknown tier fails closed; tier declared in the composed artefact; twin computes, proposer enacts). **Policy version** now versions per package like ESLint configs, is computed not declared, defines major by cage-tier movement, and reads "compliant means caged at a tier the £ accepts"; a re-price is a release. **Orphan guard** cages to the strictest tier instead of denying, with the strictest-cage `MutatingPolicy` as its sibling. **Proposer** starts on a schedule, edits the tier declaration, signs with the Actions identity, has a flood guard with a half life; "Nothing starts a run on a clock" is deleted. One-sentence fixes to **Exemption**, **Governed namespace** and **De-postured** so no entry still says "refuse" or "deny is the bottom rung". A **Twin** entry is added. The intro and the posture section point at `NORTH-STAR.md`.
- `README.md`: rows for the north star and the twin; "Deny = gate" becomes "rungs on the cage ladder; there is no gate".
- `.scratch/talk-spec/the-whole-model.md`: both diagrams redrawn and rendered with `mmdc` to confirm they parse. Diagram 1 has no neck and no ledger: intelligence on a clock, one composed artefact with a declared tier, a four-rung cage ladder, Flux as the distribution arm, evidence to residual £ to balance sheet, proposer to human to signed release. Diagram 2 draws every pin as a labelled crossing edge (`tag+sha`), explodes tuppence (party, composed artefact, twin, proposer, cluster with identity plane) and driftwood (thinner), collapses ludlow, and adds the feeds org, the insurer and the hub. The prose below the diagrams is the July record and is not rewritten; the banner says how to read it.

What this ticket did not do, on purpose: it did not rewrite ADR-0006, ADR-0010, ADR-0014 or ADR-0015. Their superseded clauses are named from the CONTEXT.md entries that cite them. A superseding ADR is ticket 09's (cage ladder v2) and ticket 10's (schedules) to write.
