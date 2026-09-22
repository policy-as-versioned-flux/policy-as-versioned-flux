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
