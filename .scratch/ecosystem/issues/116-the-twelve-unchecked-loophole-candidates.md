# 116 — The twelve unchecked loophole candidates

Type: task
Status: open
Blocked by: none

## Question

Graduated 2026-09-22 from [the Laya and loophole map](../../laya-loophole/map.md), ticket 09.
It was fog on that map until
[ADR-0030](../../../docs/adr/0030-loophole-runs-as-an-external-tool-in-rounds-and-the-estate-keeps-the-pointer.md)
decided that the unit of adoption is **three rounds**, which turns 12 unread candidates from a
curiosity into a gap.

Three loophole rounds ran against
[ADR-0022](../../../docs/adr/0022-the-cage-ladder-tier-per-namespace-isolated-rung-floor-and-infra.md)
and produced 18 candidates. Map ticket 08 checked round one's 6 against the code: **2 survived, a
survival rate of 33%**, and both are now eco-system tickets
[113](113-the-infra-declaration-is-read-by-no-served-policy.md) and
[114](114-an-unobserved-party-does-not-leave-the-walk-green.md), held by
`tests/test_cage_ladder_holes.py`. Rounds two and three produced 12 more and **none has been
checked against the code**. Four restate a reason round one already gave; eight are new.

At the measured survival rate the eight new candidates hold about **two or three real defects in
this estate's cage ladder**, and nobody has looked.

The rules this ticket works under, all from ADR-0030 and the map's calls:

1. **Test the place, never the sentence** (ADR-0030 point 3). Both of round one's survivors lost
   the mechanism the model named and kept only the place it pointed at. Neither would have graded
   as real against "is this scenario true as written", and neither would have been found if the
   pointer had been thrown away for being wrong.
2. **Count the survival rate on the candidates as stated**, so the tool is not flattered by the
   checking's own work.
3. **The judge's verdict is not a filter** (ADR-0030 point 5). It called 17 of 18 resolvable, and
   ticket 08 then found 3 of round one's 5 resolvable candidates false against the code, and the
   single unresolvable one false too. Check all twelve whatever it said.
4. **Measure under the pinned kyverno 1.18.2.** 1.19.1 cannot compile the served `cage-tier` body
   (`expected type 'string' but found 'dyn'`). Any new test skips by name on another engine, as
   `tests/test_cage_ladder_holes.py` already does.
5. Round three's `loophole-1` is already disposed of: false as written, and the place it points
   at is ticket 113. It needs no second reading.

The candidates are in `.scratch/laya-loophole/research/11-loophole-round-two/` and
`.scratch/laya-loophole/research/11-loophole-round-three/`.

Cost, from ticket 08's own: six candidates was one ticket's work, so twelve is roughly two.

## Done

Every one of the twelve carries a verdict derived from a deterministic check against the served
code, a survivor is reproduced by a test and enters `twin/ecosystem-misuse-catalogue.yaml` with
its own ticket, and a discard says which fact makes it false. The survival rate over 18 checked
candidates is recorded, and ADR-0030's "about a third" is either confirmed or corrected.

## Build, 2026-09-22

Hub only. No survivor forced a change in a unit repo: the survivor is recorded and reproduced
here, and its repair is ticket 119's.

### How it was measured

- Engine: kyverno 1.18.2, the pinned version. Every engine leg skips by name on another CLI,
  through the same `_kyverno()` that `tests/test_cage_ladder_holes.py` uses.
- Units: a detached worktree of each unit's origin/main, not the shared checkout, which was
  behind. platform `3d7f098`, driftwood `c96c412`, ludlow `32d5696`, tuppence `7009ea9`. The
  hub worktree's `.estate-clone` pointed at a private estate of those four worktrees plus the
  shared nist, ico, feeds and insurer clones.
- Every verdict below is held by a test in `tests/test_loophole_rounds_two_and_three.py`, or for
  round three's `loophole-1` in `tests/test_cage_ladder_holes.py`. The file's `VERDICTS` table
  names each test, and two record legs check the table against both `candidates.json` files and
  compute the survival rate from it.
- Each served policy document is applied alone, so a mutation or a failed validation is
  attributed to the policy that made it. A generating policy is read statically: every served
  one needs a pod the cage already caged.

### The twelve verdicts

| round | candidate | verdict | the fact |
|---|---|---|---|
| two | `loophole-1` | discard | The `platform` role is read from `platform/party.yaml` alone, by the tripwire's `platform_role_ok`. No served body reads a role or a party artefact. An adopter that writes `platform` into its own party.yaml and declares `infra` is bound as the `isolated` it renders. |
| two | `loophole-2` | **survivor** | No discovery list exists, so the mechanism is false. The place is real: a pod that claims nothing in a Namespace with no label is touched by no served policy, and the composition prices that Namespace only if it carries the institution label. Ticket 119. |
| two | `loophole-3` | discard | The binding check compares the declaration with the party's strictest priced line, not with an earlier label. `payments-v48` declared `baseline` against an `isolated` price exits 1, "LOOSER". Declared with no tier it is bound as `isolated`, and every delivered body cages a claiming pod there at `isolated`. |
| two | `overreach-4` | discard | False as written. An ad hoc Namespace carries no label, so an unclaimed debug pod there is not caged at all, let alone at `isolated`. It points at the survivor's place. It restates round one's reason (no break-glass path). |
| two | `overreach-5` | discard | True that no fast loosening exists. ADR-0022 records it: "Loosening is not implemented, and that is the decision, not an omission." The binding check holds it: `baseline` against a `restricted` price exits 1. |
| two | `overreach-6` | discard | Not silent. Each adopter's served `governed-namespace-requires-claim` is a Deny whose message names the missing claim. The platform's next machinery cages the pod and `governed-namespace-unclaimed-report` names the claim and the bottom rung. It restates round one's reason (innocent omission). |
| three | `loophole-1` | discard | Not re-read, as this ticket says. False as written; the place is ticket 113's, held by `test_the_tripwire_names_exactly_the_bodies_the_engine_cages_loosely`. |
| three | `loophole-2` | discard | No served body reads `infra`. A claiming pod gets the same rung with the label as without it, governed or not, under every delivered body. |
| three | `loophole-3` | discard | Same fact as round two's `loophole-3`. |
| three | `overreach-4` | discard | The claim is a pod label. `tier_binding.py` never reads it. A pod that claims again gets its Namespace's declared tier (`baseline` measured) from the newest line and every adopter's served body, with no Namespace edited. |
| three | `overreach-5` | discard | False as written: an unclaimed pod in an unlabelled sandbox Namespace is not caged at all. It points at the survivor's place. It restates round one's reason (innocent omission). |
| three | `overreach-6` | discard | No unit's workflow calls `verify-infra-declaration.sh`. It runs in the hub's gate, classed `estate-observation` in `talk/verify-manifest.txt`, and a red there stops no unit's merge. |

### The survival rate

**1 of 12 survived. Across three rounds 3 of 18 candidates survived: 17%.** By round: 2 of 6,
1 of 6, 0 of 6. ADR-0030's "about a third" is **corrected** to about one in six, in a dated note
on ADR-0030. `test_the_survival_rate_is_derived_from_the_verdicts` computes 3 of 18 from the
verdict table and requires the ADR to say it.

The survivor followed ADR-0030 point 3 again: its mechanism is false and its place is real. The
judge called all twelve resolvable.

### Corrections to this ticket's own premises

- **Three candidates restate a round-one reason, not four.** Measured from ticket 11's
  `11-targets.json`: round two's `overreach-4` and `overreach-6`, round three's `overreach-5`.
  `test_three_of_the_twelve_restate_a_reason_round_one_gave` holds it.
- The shared `.estate-clone` checkouts of platform, driftwood, ludlow and tuppence were all behind
  origin/main when this ticket started.

### Side findings

- The standing red recorded by the Laya map's ticket 08,
  `tests/test_misuse.py::test_the_four_rows_grade_against_this_checkout`, passed against platform
  origin/main `3d7f098`. `price_supersede` is in `composition.py` there. The shared checkout
  predates it.
- The adopters still serve the `governed-namespace-requires-claim` Deny that ADR-0022 names,
  composed under platform `2.0.1`. Their `composed/policies/` trees are at `v4.0.0`.

### Decisions

- **Delegated: the counting rule.** A candidate survives when the place it points at holds a real
  defect that no earlier survivor or ticket already holds. Ticket 08 applied it to round one's
  `overreach-5`, and this ticket's own rule 5 applies it to round three's `loophole-1`. Reason:
  the survival rate budgets real defects per candidate (ADR-0030 point 2). Counting echoes of one
  defect would inflate it. With echoes counted the twelve would give 4, and the ADR note says so.
- **Delegated: the survivor is recorded, not repaired, here.** The repair needs a choice between
  a price and a cage, and a cage shape must not strand CoreDNS (ticket 113). That choice is a
  ticket's worth of work and belongs with its own tests, so it is ticket 119.
- **Delegated: one new test file, importing ticket 08's helpers.** The engine and binding helpers
  in `tests/test_cage_ladder_holes.py` are reused, not copied, so the two files cannot drift on
  how a pod is rendered.
- **Delegated: the verdict table lives in the test file.** A verdict that names no test fails a
  leg, so a later reader cannot remove a check and keep the verdict.

### What changed

- `tests/test_loophole_rounds_two_and_three.py`: new, 13 legs.
- `tests/test_misuse.py`: the eco-system catalogue holds 7 rows and names the new one.
- `twin/ecosystem-misuse-catalogue.yaml`: version 6 to 7, row
  `adopter-runs-uncaged-and-unpriced-in-an-unlabelled-namespace`, waiting on ticket 119.
- `.scratch/ecosystem/issues/119-an-unlabelled-namespace-is-outside-the-cage-and-the-price.md`: new.
- `docs/adr/0030-...`: dated note, 3 of 18.
- `.scratch/ecosystem/map.md`: a line for ticket 119.

### What remains

Nothing waits on the owner. The survivor's repair is ticket 119.
