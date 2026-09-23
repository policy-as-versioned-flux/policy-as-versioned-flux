# 121 — Implementing a control moves no price and no tier

Type: task
Status: open
Blocked by: none

## Question

Graduated 2026-09-23 from eco-system ticket
[120](120-the-eighteen-unchecked-candidates-against-adr-0026.md). It is one of three survivors
of the eighteen loophole candidates against ADR-0026. Round 1's `overreach-6` pointed at it.
Reproduced by `tests/test_loophole_adr_0026.py`, leg
`test_implementing_every_weighted_control_moves_no_regime_price_and_no_tier`, against platform
origin/main `b2820d8`.

The candidate said an adopter that widens its baseline to controls no regulator weight names
earns no credit, because the widening delta carries no amount. That is true, and ADR-0026 point 3
says it on purpose. The place it pointed at is wider than that.

1. **No hole status reaches the price.** `_regime_holes` in `compose/composition.py` splits the
   regime entry's amount across every control the pinned weights name, whether or not the
   adopter selected it or claims it. The split sums to the entry. The entry does not depend on
   which lines are holes. Its own docstring says so: "pricing a hole by its status (so
   implementing pl-2 actually shrinks the regime entry) needs the adopter's open hole ids ...
   that is ticket 15's build, not this schema pass." Ticket 38 D1 then kept the partition
   untouched, so that build never happened.
2. **Measured.** tuppence composed against its real parents (ico `penalty-schema` v3), then again
   with its own claim on all four controls the uk-gdpr lower-tier weights name (`pl-2`, `ra-3`,
   `ca-2`, `ir-8`, weights summing to 1.0). All four lines turn `covered`. The regime entry stays
   at 9,039,791.02 GBP, the header's exposure total does not move, and every `proposed_tier` stays
   `isolated`. The whole partition implemented, and nothing moves.
3. **The same holds for the other priced lines.** A bespoke hole priced by its own scenario and
   an ungoverned Namespace priced by its workload share each print an amount and move no tier and
   no exposure total (`test_a_bespoke_hole_is_priced_on_its_own_line_and_moves_no_tier`,
   `test_an_ungoverned_namespace_is_a_workload_share_while_it_exists_and_moves_no_tier`). Ticket
   38 D5 named the bespoke case as a limit. Nobody named the other two.

The record says the opposite. ADR-0026 point 2: "so implementing a control reduces the regime's
price". CONTEXT.md **Hole**: "the regime's price is the sum of its holes and implementing a
control reduces it". Ticket 15 item 2 gave the reason the price must reach the tier: "a price
that cannot move the tier is a report, not a cage." Today every hole price is that report.

A related fact, measured by `test_a_mistranscribed_weight_moves_no_regime_price`: a wrong weight
in the regulator's feed moves no regime price today either, because a weight only splits a fixed
amount. Repair this ticket and a wrong weight starts to matter. The recourse is the adopter's own
pin and a pull request to the publisher, and the repair should say so.

What this ticket owes:

1. Decide, as delegated under ADR-0025, what an implemented control does to the pound. Two
   shapes are known. **Price the open holes**: the regime entry becomes the sum of its open
   holes, so the partition stays a graded fact on its own line and the entry shrinks when a
   hole closes. **Record the limit**: keep the fixed partition and correct ADR-0026 point 2 and
   CONTEXT.md to say a hole is priced and reported, and moves no tier. The first keeps ticket
   15's reason. The second admits the price is a report.
2. Say what `verify/pound-seam/` grades after the choice. Its check 4 requires the hole amounts to
   sum to the entry and prints "implementing one reduces it" as its reason.
3. Say whether the bespoke and ungoverned prices enter the same sum, or stay reported.

## Done

`test_implementing_every_weighted_control_moves_no_regime_price_and_no_tier` flips to a
regression test of the repair, or ADR-0026 point 2 and CONTEXT.md **Hole** stop claiming what the
code does not do, with the decision recorded here and its reason.
