# 121 — Implementing a control moves no price and no tier

Type: task
Status: resolved
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

## Build, 2026-09-22

Built on 2026-09-23 against platform origin/main `7144df4` (tickets 124, 123, 119 and 122 merged)
and hub origin/main `ee2df61`. Platform branch `ticket-121-implementing-a-control-moves-the-price`,
hub branch of the same name.

### What the code does now

- `compose/composition.py` `price_parent` takes `implemented`, the adopter's selected controls a
  claim covers. `compose()` passes `selected_set & covered`, and `compute_prices` hands it on to
  `price_parent`, to `compute_switching`'s counterfactuals and to the floor counterfactual.
- The partition is unchanged. Every line on the regime entry's `holes[]` keeps its weight and
  its amount, and `total` is still their sum.
- The entry's `amount` and `new_price` are the sum of the lines not implemented (`_open_lines`).
  `old_price` is scaled by the same open share.
- `old_tier` and `proposed_tier` come from `cage.select_tier` on the same open share of each
  residual, so the price and the tier cannot disagree.
- With nothing implemented the entry is exactly what it was.

### Decisions (all delegated, ADR-0025)

1. **Price the open holes, not record the limit.** The entry is the sum of its open lines. The
   reason is ticket 15 item 2: "a price that cannot move the tier is a report, not a cage." The
   other shape would have made every hole price a report and rewritten ADR-0026 point 2 to say
   so. This shape keeps the record's claim and keeps the weights graded on their own lines.
2. **"Implemented" means selected and claimed.** A line comes off the price when the adopter
   selects that `(source, id)` and a claim covers it. Those are exactly the lines
   `_decorate_regime_holes` marks `covered` or `closed`. A line the adopter does not select stays
   on the price, because ADR-0026 point 5 says the regulator prices a control whether or not it
   is selected, so a removal must hide nothing. A `withdrawn` line stays on the price, as ticket
   123 recorded. Consequence: removing an open hole moves nothing, and removing an implemented
   control puts its line back.
3. **The tier follows the open share.** Both tiers are picked by the engine's own pure
   `select_tier` on the open share of the uncaged residual, against the same band and floor. No
   second selection rule. `changed` still compares the old feed version with the new one at the
   same open share, so it stays the feed-move flag. The move an implementation makes prints as
   its `closed-hole` delta, which carries the line's amount.
4. **No new field.** `total` keeps its meaning, the partition's sum. `amount` changes meaning
   from "the partition" to "the open lines", and the two agree when nothing is implemented.
   `verify/pound-seam/` check 4 now grades: the lines sum to `total`, the weights sum to 1.0,
   and `amount` and `new_price` equal the sum of the lines whose status is neither `covered` nor
   `closed`. Its reason text, "implementing one reduces it", is now true. Three new selfcheck
   cases plant an implemented line that comes off, an entry that still charges one (fails), and
   an unselected line that stays on.
5. **The bespoke price stays reported.** A bespoke hole is priced by the adopter's own scenario
   against its own band. It is not a share of the regulator's regime, so adding it to the regime
   entry would mix two instruments on one line. Giving it its own tier needs a `prices[]` kind
   of its own, which is the `PRICE_KINDS` major the platform README already names ("priced but
   not yet tiered"). That limit stands and is recorded here for the next loophole round.
6. **The ungoverned price stays reported.** Its base is the exposure total. Summing it into that
   total would price the total against itself. The brief also keeps the ramp out of scope. It
   now takes its share of a smaller total where the adopter implements a weighted control; the
   code that prices it did not change.
7. **A wrong weight now matters, and the recourse is the pin.** Once a control is implemented,
   its weight decides how much comes off. The adopter's own pin holds the version it priced
   against, and a correction is a pull request to the publisher's repo. Pound-seam check 4
   already fails a partition whose weights do not sum to 1.0. The leg
   `test_a_mistranscribed_weight_moves_the_price_of_what_is_implemented` holds both halves.

### Tests, run in this task

- Red first. The new leg `test_implementing_a_weighted_control_moves_the_regime_price_and_the_tier`
  failed against platform origin/main: claiming `pl-2` left the entry at 9,039,791.02 where it
  expected 6,327,853.71.
- Green. `tests/test_loophole_adr_0026.py`, 23 passed, with the hub worktree's `.estate-clone`
  pointing platform at the ticket-121 platform worktree. The flipped leg measures: claiming
  `pl-2` takes exactly its line off the entry and off the exposure total; claiming all four
  weighted controls takes the entry to 0.0 and its tier from `isolated` to the rung
  `select_tier(0.0, ...)` picks under tuppence's floor; every other entry keeps its tier. The new
  leg `test_removing_an_implemented_control_puts_its_line_back_on_the_price` holds decision 2.
- `tests/test_priced_holes.py`, 28 passed.
- `verify/pound-seam/pound_seam.py selfcheck` passes. `verify-pound-seam.sh` exits 1 with the
  same 4 FAIL lines as origin/main's grader on the same estate (diffed). They are the
  `supersede` entries (`source: ico`, no `holes[]`) and one numberless price. Not this ticket's.
- `verify/adr-supersession/verify-adr-supersession.sh`: PASS.
- mypy on `twin tests conftest.py`: no issues in 199 files.
- Platform `composition.py --selfcheck`: exit 0, 97 OK lines, run from a plain-directory copy of
  the estate with platform at this branch. A symlinked estate fails its "no absolute path"
  assert at the same place on origin/main too, so the copy is needed. The new case prints, on
  driftwood pinned to ico v3 with a claim on `pl-2`: "takes its 536153.12 line off the regime
  entry, 1787177.08 -> 1251023.95; the partition still sums to 1787177.08".
- Platform `compose/verify-composition.sh` on the same copy: exit 3. Step 1 passes. Step 2 SKIPs
  because driftwood's platform pin (2.0.1) does not contain `distribution/policies/v5.0.0`; that
  waits on a cut release and a pin move, not on this build.

### Adopter prices, measured

Recomposed driftwood `c96c412`, tuppence `7009ea9` and ludlow `32d5696` (detached origin/main
worktrees) with platform origin/main and with this branch, against the same parent trees. The
whole evidence document hashes the same under both for all three. No adopter claims a weighted
uk-gdpr lower-tier control today (every line reads `recorded`), so no committed price moves.

### What remains

- **Owner:** a signed platform tools release carrying this build, then each adopter's pin move.
  Until then the adopters' composed evidence is the old composer's, which prices the same.
- **Integrator:** merge platform first, then hub. The hub leg reads `.estate-clone/platform`, so
  it passes only once platform main carries the build.
- **Next loophole round:** the bespoke price reaches no tier (decision 5).

## Answer

Resolved 2026-09-23 by platform PR 35 and hub PR 101. Implementing a weighted control now takes
its line off the regime price and can move the tier, as ADR-0026 point 2 says.

1. `price_parent` takes the adopter's implemented set: its selected controls that a claim covers.
   The regulator's partition does not change. Every line on `holes[]` keeps its weight and
   amount, and `total` is still their sum.
2. The regime entry's `amount` and `new_price` are now the sum of the lines not implemented. Both
   tiers come from `cage.select_tier` on the open share, so there is no second selection rule.
3. `test_implementing_a_weighted_control_moves_the_regime_price_and_the_tier` is the regression
   test. For tuppence, claiming pl-2 takes exactly its line off. Claiming all four weighted
   controls takes the entry to 0.0 and moves its tier off `isolated`.
4. `verify/pound-seam` check 4 also grades that `amount` equals the sum of the open lines.

No adopter's committed price moves today, measured by recomposing all three adopters under the
old and the new composer: none claims a weighted uk-gdpr lower-tier control.

Review: one round, pass, three minor findings, not fixed. One names a real edge for the next
loophole round: when the previous pin published no weights, `old_price` is scaled by the new
pin's weights.
