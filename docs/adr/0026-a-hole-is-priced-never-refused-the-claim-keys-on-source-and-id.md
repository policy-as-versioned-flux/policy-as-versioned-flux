---
status: accepted
---

# A hole is priced, never refused: the claim keys on (source, id), and a widening, a removal and an ungoverned namespace print as priced deltas

Decided 2026-09-04 by the assistant under ADR-0025, labelled delegated. Ticket 39. Supersedes in
part [ADR-0013](0013-regulator-publishes-baselines-adopter-selects.md),
[ADR-0017](0017-a-control-claim-belongs-to-whoever-ships-the-implementation.md) and
[ADR-0018](0018-the-namespace-manifest-is-the-governed-declaration.md) point 3.

## Context

Three accepted ADRs carried refusals from the time when a hole was a count and a refusal was the
only signal the composition had:

- **ADR-0013** keyed a control claim on the bare catalogue id against one catalogue, refused the
  composition on a **new hole**, refused a **baseline widening** (MODERATE to HIGH) with no
  override, and said an adopter may add a control and **never remove** one, "because a removal is
  an exemption by another name".
- **ADR-0017** made an adopter's own addition an ordinary new hole: "Refuse, same as any new hole
  (chosen)", the **self-created hole refusal**; and, under its heading "Removing a self-added
  control", chose "Never (chosen)": "Adding was a claim. Withdrawing it is an exemption by another
  name."
- **ADR-0018 point 3**: "Composition refuses an ungoverned adopter namespace, and only a new
  one", the **new-ungoverned refusal**.

One standing line in the ticket record carries the removal rule too, and this ADR retires it:
ticket 15's "Already decided, not re-asked" paragraph (2026-08-28, line 38) says "an adopter may
add a control and never remove one, a claim belongs to whoever ships the implementation (ADR-0013,
ADR-0017)". That line restates the two ADRs; it quotes no owner's words on removal, and no owner
answer on removal exists anywhere in the record, so under ADR-0025 the rule is the assistant's to
decide and record (ADR-0025 point 1; point 2 would bind only if the owner had answered). Ticket
38 then handed exactly this question to this ADR (below). Retiring the line is consistent with
NORTH-STAR §3 principle 1, "everything is policy": a removal is a signed, party-wide change of a
declared selection that anyone can make and the cage prices, which is "a conditional rule anyone
can meet, or a cage with a price", not a carve-out for a named workload.

The decisions that reversed them came in order. Ticket 15 (resolved 2026-08-28, re-grills 19, 20,
25, 27, reversals 9, 10, 18) decided, in its Answer items 1 to 3 and 5: regulator-published
weights price each hole as a partition of the regime exposure; the hole price lands on the regime
`prices[]` entry and all three refusals go, with a new hole, a widening and a new ungoverned
namespace printing as priced deltas; an ungoverned namespace prices as a ramped workload share of
the uncaged residual from the first signed artefact naming it; a bespoke control is a small OSCAL
catalogue the adopter publishes as a `controls` parent of itself, so claims resolve on
`(source, id)` across every controls parent, and a bespoke control with no signed scenario is an
instrument fault. [ADR-0020](0020-a-missing-instrument-refuses-a-missing-behaviour-is-priced.md)
(2026-08-28) drew the line the whole estate now runs on: a missing **behaviour** is priced, a
missing **instrument** refuses.
[ADR-0022](0022-the-cage-ladder-tier-per-namespace-isolated-rung-floor-and-infra.md) made the
cage tighten-only and said "lowering the floor is priced, never refused", and its 2026-09-02 note
carries the owner's reason in the owner's words: proportionality is run with a better cage;
something can find itself unable to run only because it does not fit the cage, never because it
is deliberately denied; a mutating admission controller, not a validating one (NORTH-STAR §3
principle 2, ticket 75 Q5). The 2026-09-03 build brief restates it: the only refusal is a
missing instrument.

Ticket 38 built it (hub PR #16, merged 2026-09-04; platform `compose/composition.py` on
`ecosystem/build-2026-09-03`, unpushed): its D1 to D12 delete the new-hole, widening and
new-ungoverned refusals, key every claim and hole on `(source, id)`, print five kinds of delta,
ramp `tuppence-reset` from its 2026-08-25 signed tag, and keep exactly one hole-shaped refusal, a
bespoke control with no signed scenario. Ticket 38 left dated notes on the three ADRs pointing at
the ADR ticket 39 would write, and left one question to it (its Answer, 2026-09-04): D6 kept the
**removed-control** refusal on ADR-0013's rule, and a removed control is not a missing
instrument, so either this ADR retires that refusal or it records the reason it stands as the one
behaviour-shaped refusal.

Two facts about the live composition decide that question. First, the regulator's weighted
partition on the regime entry does not depend on the adopter's selection: a weighted control the
adopter has not selected carries status `unselected` and keeps its amount, because the weights
must still sum to one and the amounts to the entry (ticket 25; `verify/pound-seam/pound_seam.py`
check 4 grades the partition, and `_decorate_regime_holes` in `composition.py` sets the status).
So a removal cannot lower the pound the regulator prices. Second, the only price a removal can withdraw
is a bespoke control's own scenario, which the adopter itself declared, signed and priced against
its own band (ticket 38 D5).

## Decision

1. **A claim and a hole key on `(source, id)`.** This refines ADR-0013's rule rather than
   replacing it. The wire value stays the **bare catalogue id** exactly as the catalogue writes
   it (`ac-6`), and the catalogue is still named once, by the `source` or `href` on the enclosing
   block; that source is the first half of the key. ADR-0013 already carried the source
   implicitly and assumed one catalogue; the key names it so that a second `controls` parent, an
   adopter's own catalogue under ticket 15 item 5, cannot collide with the regulator's ids. On
   the wire a bare id belongs to the baseline's catalogue and `source:id` names any other
   controls parent (ticket 38, Answer item 2; its D11 makes the baseline's catalogue the first
   `controls` parent that is not the adopter), so the three real adopters' headers are
   byte-stable. The exact-string rule stands: no case-folding, no prefix-stripping. The hard
   failure on an id no pinned catalogue carries stands and is classified: it is a **missing
   instrument** in ADR-0020's sense, because nothing pinned defines the id and so nothing can
   price it; it is not a judgement on behaviour. The code emits it under its own kind,
   `unknown-control-id`, not `missing-instrument`; the classification is this record's, and the
   code keeps its name.
2. **A hole is priced, never refused.** Each hole prices as the regulator's published control
   weight for that `(source, id)` times the adopter's sized triple for the regime, a partition of
   the regime exposure, so implementing a control reduces the regime's price (ticket 15 item 1).
   A hole no pinned weight names carries `amount: null` and `priced_by: null`, a named absence
   rather than a zero. A new hole prints as a `new-hole` delta and a filled one as `closed-hole`,
   each under the adopter's own perspective and currency; the price moves the cage tier through
   the selection policy that already reads the regime entry (ticket 15 item 2). ADR-0013's
   new-hole refusal and ADR-0017's self-created hole refusal are gone; an adopter's own addition
   is a priced new hole like any other.
3. **A widened baseline is a priced delta.** A named-baseline change that only adds controls
   prints one `baseline-widening` delta (how many controls it adds, how many a pinned weight
   prices, the sum) beside the `new-hole` deltas it opens. There is no override flag because
   there is nothing to override (ticket 15 item 2, reversals 9 and 10). Where no pinned weight
   names any added control the delta carries no amount, which is the honest statement that the
   pound does not move until a regulator prices those controls (ticket 38 D1).
4. **A new ungoverned namespace is a priced delta.** Every ungoverned namespace in the adopter's
   repo prices as its workload share of the adopter's uncaged priced residual, ramped from
   `since`, the creator date of the first signed tag whose composed header names it, bounded at
   the whole residual; a new one prints as a `new-ungoverned` delta and a governed one as
   `closed-ungoverned` (ticket 15 item 3, ticket 38 D2 to D4). The rest of ADR-0018 point 3
   stands: the walk is repo-only, and cluster drift on the label is Flux drift owned by the
   estate's drift tooling.
5. **A removal is priced, never refused.** ADR-0013's "never remove", ADR-0017's "Never
   (chosen)" under "Removing a self-added control", ticket 15's standing line and ticket 38's D6
   are superseded. A control that leaves the adopter's selected set
   prints as a `removed-control` delta carrying the amount the hole
   carried (the regulator's weight times the triple, a bespoke scenario's residual, or a named
   absence), and its line on the regime partition takes status `unselected` with its amount
   unchanged. A named-baseline change that drops controls prints one `baseline-narrowing`
   summary delta beside them, mirroring point 3. Reasons, in order of weight: (a) the doctrine,
   in the owner's words, admits one refusal and it is a missing instrument; a removed control is
   a missing behaviour. (b) ADR-0013's reason for the rule, "an exemption by another name",
   described a count a removal could hide a hole from; under pricing the regulator's weight prices
   the control whether or not the adopter selected it, so a removal hides nothing from the pound.
   (c) ADR-0022 already settled the same shape one layer down: lowering the floor is priced,
   never refused; a narrower selection is the same loosening at the selection layer, and the
   cage's answer to a loosening is to price it, not to wall it. (d) The one pound a removal does
   withdraw is a bespoke control's own scenario, an obligation the adopter invented; the
   withdrawal is a signed, party-wide, printed change of the adopter's risk-bearing selection,
   which ADR-0013 makes the adopter's act, and where it matters to another party it is the
   insurer's quote `conditions`, keyed on `(source, id)` with a `consequence` of void or uplift
   (ticket 14, Answer 3), that carry the consequence, not a composition wall.
   The word **exemption** does not apply: CONTEXT.md defines it as a carve-out for a named
   workload, and a selection change names no workload and hides no price.
6. **Every refusal kind composition emits today, classified.** On the platform integration
   branch `compose/composition.py` emits eleven refusal kinds (each a `"kind"` whose dict carries
   `needs_composition`; `compose/verify-composition.sh` step 1b prints nine of them on
   2026-09-04 because its scan window is 400 characters and `claim-against-another-partys-policy`
   and `rule-conflict` carry a longer `detail`). Each is an **instrument fault**, ADR-0020's
   line, where nothing pinned can resolve or price the thing named, or a **behaviour**, something
   the adopter does or omits, which the doctrine says to price. One line each:
   - `claim-against-another-partys-policy`: instrument fault. A claim is only evidence when the
     claimant ships the policy (ADR-0017, which stands on this); a claim citing another party's
     policy evidences nothing, so the hole it names is simply not closed.
   - `dangling-claim`: instrument fault. The policy the claim cites is in no composed member; the
     claim resolves to nothing.
   - `missing-baseline-file`: instrument fault. The controls parent publishes no baseline of that
     name, so there is no selected set to price.
   - `missing-instrument`: instrument fault by name. No appetite band, no price for a declared
     regime, no FX rate for the date (ADR-0020); a bespoke control with no signed scenario
     (ticket 38 D5); a bespoke band in a currency other than the reporting currency (ticket 38
     D12).
   - `no-controls-parent`: instrument fault. There is no catalogue to resolve the baseline
     against.
   - `removed-control`: behaviour. The one behaviour-shaped refusal in the code; point 5 retires
     it and the platform build named in Consequences must price it.
   - `restatement-of-non-validating`: instrument fault. A restatement compares on the strictness
     ladder only a `ValidatingPolicy` carries (ADR-0016); against any other kind there is nothing
     to compare, so the declaration is unmeasurable, not looser.
   - `rule-conflict`: instrument fault. Two parents supply the same rule at the same version with
     different content; two instruments disagree and nothing pinned says which to read.
   - `split-diamond`: instrument fault. One parent is inherited at two versions through
     different edges; the pin is ambiguous, so there is no single instrument.
   - `unknown-control-id`: instrument fault (point 1). No pinned catalogue defines the id.
   - `unpriceable-inability`: instrument fault, and the kind nearest the line. The inability is a
     declared behaviour; what is missing is its price instrument (no scenario of the adopter's
     own and no threat parent to price from), and ADR-0020 refuses on that. A later build may
     price it from a default the way the twin prices an unpriced register entry (ticket 15,
     re-grills 32 and 35: a cage consequence defaulted from appetite); until one exists it is
     recorded here as the instrument fault it is.
   So the only refusal that judges a behaviour is `removed-control`, and its retirement is
   point 5. `verify-adr-supersession.sh` carries this list of eleven as a fixture and fails if
   this ADR stops naming and classifying any of them; a kind the source gains later is a fact for
   the next ADR, not a silent widening of this one.

## Options considered

**The removal (the question ticket 38 left)**

- **Priced, as a `removed-control` delta (chosen).** The reasons in point 5.
- **Kept as the one behaviour-shaped refusal, with ADR-0013's reason.** Rejected. The reason no
  longer describes the estate: the pound the regulator prices does not move on a removal, so the
  refusal protects a count, not a price, and the doctrine admits no count-shaped wall.
- **A ratchet: the selected set is the union with the last signed selected set, so a removal has
  no effect and prints.** Rejected. It composes against a set the party artefact does not
  declare, which is the duplicated state ADR-0018 §2 rejected ("a mirror of one into the other
  is duplicated state"), and it makes a hole that can never close, a count that never falls,
  which is a wall in slow motion.

**The key**

- **`(source, id)`, bare catalogue id on the wire (chosen).** One authority for the id, one place
  naming the catalogue, and room for a second controls parent.
- **Replace the bare id with a prefixed id (`nist:ac-6`) everywhere.** Rejected for ADR-0013's
  own reason: the prefix names the catalogue a second time, and the three real adopters' signed
  headers would change shape for no new fact.
- **Keep one catalogue.** Rejected: ticket 15 item 5 makes an adopter's bespoke control a
  catalogue the adopter publishes, so a single-root resolver cannot price it.

**What prices a hole** (ticket 15 Q1)

- **Regulator-published weights, a partition of the regime exposure (chosen).** The only option
  under which the widening beat and NORTH-STAR step 2 both happen, and the join sits where the
  eco-system says it belongs: the regulator, as a signed feed version.
- **A uniform share, exposure times holes over selected.** Rejected: a count wearing a price.
- **An adopter-declared scenario per hole.** Rejected: 285 declarations nobody will sign.

**Where the price lands and whether the refusals go** (ticket 15 Q2)

- **On the regime `prices[]` entry, moving the tier; all three refusals deleted (chosen).** A
  price that cannot move the tier is a report, not a cage.
- **On the balance sheet line only.** Rejected for the same reason.

**How an ungoverned namespace grows** (ticket 15 Q3)

- **A ramped share of the uncaged residual from the first signed tag naming it (chosen).** Both
  factors and the ramp already exist; no invented formula, no knob.
- **A flat share with the date printed beside it.** Rejected: the grandfather clause re-grill 27
  rejected.

**What this ADR's check grades**

- **The record only (chosen).** `verify/adr-supersession/verify-adr-supersession.sh` reads
  `docs/adr/` and `CONTEXT.md`, selfcheck first, never SKIP. The code is graded by
  `verify/priced-holes/verify-priced-holes.sh` (ticket 38); a second grader over the same source
  would drift from the first.
- **The record and the code.** Rejected: duplicated grading, and red on the removal leg until its
  build lands, which would make this ADR's check report a fact ticket 38's check already reports.

## Consequences

- **Banners.** ADR-0013, ADR-0017 and ADR-0018 carry a dated "Superseded in part" banner naming
  this ADR, in the blockquote style ADR-0014, 0015, 0016 and 0018 already use for ADR-0022.
  ADR-0018's ADR-0022 banner for §4 stands beside it; this ADR's banner is confined to point 3,
  and ticket 89 adds its own note to ADR-0018 later. ADR-0015's deny-to-issue is already
  superseded by ADR-0022 (ticket 09) and carries its banner; nothing here touches it.
- **CONTEXT.md.** The **Baseline**, **Control id**, **Hole** and **Delta** entries cite this ADR
  and no longer say a removal refuses or that an adopter may never remove a control.
- **What the code does today, stated honestly.** On the platform integration branch
  `ecosystem/build-2026-09-03`, `compose/composition.py` no longer refuses a new hole, a widening
  or a new ungoverned namespace (ticket 38). Its `check_selected_set` still refuses
  `removed-control`; `composition.py --selfcheck` asserts that refusal in its `run2-removed` case
  (SMALL to TINY, `outcome: refused` naming `aa-1.1` and `aa-2`), which
  `compose/verify-composition.sh` runs as its step 1 while its step 1b lists `removed-control`
  among the refusal kinds still emitted; the party schema's `overlay.controls` description still
  says "May only grow: a composition still refuses on any id that leaves the last signed composed
  artefact's selected set, because a removal is an exemption by another name"; and
  `verify/priced-holes/priced_holes.py`'s `check_source` does not grade its absence, its own
  selfcheck planting `removed-control` in the source it must pass. The unknown-id refusal of
  point 1 is emitted under the code kind `unknown-control-id`, not `missing-instrument`; this ADR
  classifies it as an instrument fault and renames nothing. A platform build ticket deletes
  the refusal, adds the `removed-control` and `baseline-narrowing` delta kinds to
  `compute_deltas`, rewrites the `run2-removed` case to expect `outcome: composed` with two
  `removed-control` deltas and one `baseline-narrowing` delta, rewrites the schema sentence, and
  adds `removed-control` to `check_source`'s gone set with its selfcheck fixture flipped. Until it
  lands the record leads the code, as ADR-0013 led the estate on its 285 holes; this ADR's check
  grades the record only and says so in its header.
- **Ticket 38's D6 is superseded** by point 5. Its D1 to D5 and D7 to D12 stand and are cited
  here as the reasons they are.
- **The three adopters' evidence** (`composed/evidence.json`) still carries the refusal-era shape
  until the owner re-composes and pushes driftwood, tuppence and ludlow; that wait is ticket 38's
  and is unchanged by this ADR.
- **A control the regulator withdraws from its catalogue** is not an adopter removal: it leaves
  the selected set with the catalogue bump; a weights feed that still names it is that feed's own
  fact to fix in its next version (ticket 15 item 1 puts the weights under a `payload_schema`
  major, and ticket 04's Answer item 3 rules that "a `payload_schema` change is always major";
  ADR-0019 records the envelope and the signed tag, not that rule); and an adopter still naming
  it in `overlay.controls` meets the unknown-id instrument fault of point 1, code kind
  `unknown-control-id`. Revisit trigger: the first such bump.
- **Terms.** `CONTEXT.md`'s **Exemption** entry is unchanged; a priced, signed, party-wide
  selection change is not one.
