# 120 — The eighteen unchecked loophole candidates against ADR-0026

Type: task
Status: resolved
Blocked by: none

## Question

Charted 2026-09-22 by eco-system ticket 115, which ran the procedure in
[`bench/loophole/`](../../../bench/loophole/README.md) against a second document.

Three loophole rounds ran against
[ADR-0026](../../../docs/adr/0026-a-hole-is-priced-never-refused-the-claim-keys-on-source-and-id.md),
"a hole is priced, never refused". All three were clean: 0 parse failures, 0 under-production,
0 judge replies without a verdict. They produced **18 candidates**, 9 loophole and 9 overreach,
in `bench/loophole/rounds/adr-0026/round-{1,2,3}/candidates.json`. **None has been checked
against the code.** Ticket 115 was told not to check them, so the checking is this ticket.

At the survival rate measured on ADR-0022 (2 of 6, ADR-0030), 18 candidates hold about 6 real
defects. That rate rests on six checked candidates from one round and a different document, so
it is a budget, not a forecast.

What ticket 115 saw while recording them, read from the candidate text and not from the code:

- Several candidates point at the same places. The `since` date of an ungoverned namespace
  (round 1 loophole-2, round 2 loophole-3, round 3 loophole-2), a bespoke control priced by the
  adopter's own scenario (round 1 loophole-1 and loophole-3, round 2 loophole-2, round 3
  loophole-1), and a namespace created for a short task and swept into the ungoverned walk
  (round 1 overreach-5, round 2 overreach-5, round 3 overreach-6).
- The judge called 11 of 18 resolvable (3, 3 and 5 by round, from each `summary.json`). ADR-0030
  point 5 says that verdict is not a filter.

The rules this ticket works under, from ADR-0030:

1. **Test the place, never the sentence** (point 3).
2. **Count the survival rate on the candidates as stated** (point 3).
3. **Check every candidate whatever the judge said** (point 5).
4. ADR-0026 names a place where the record leads the code: the platform still refuses
   `removed-control`. A candidate that lands there is already known, and says so.
5. The reachable code for ADR-0026 is on the platform integration branch
   `ecosystem/build-2026-09-03` (`compose/composition.py`) and in
   `verify/priced-holes/`. Confirm which branch is live before checking.

## Done

Each of the 18 candidates has a verdict against the code, with the command that decided it. The
survival rate is stated on the candidates as stated. Each survivor is held by a deterministic
test and charted as its own ticket. The matching across the three rounds (same place, same
reason) is recorded, so ADR-0030 point 2's overlap has a second document behind it.

## Build, 2026-09-22

Hub only. No survivor forced a change in a unit repo: each survivor is recorded and reproduced
here, and its repair is its own ticket.

### How it was measured

- Which branch is live. `git merge-base --is-ancestor origin/ecosystem/build-2026-09-03
  origin/main` in the platform clone exits 0: the integration branch this ticket names is merged,
  so platform main is the reachable code. The removal refusal ADR-0026 names is still in
  `check_selected_set` there.
- Units: a detached worktree of each unit's origin/main, not the shared checkout. platform
  `b2820d8`, driftwood `c96c412`, ludlow `32d5696`, tuppence `7009ea9`, nist `f83126f`, ico
  `abcb3a8`, feeds `ff3ac9a`, insurer `d1c1844`. The hub worktree's `.estate-clone` pointed at a
  private estate of those eight.
- No kyverno engine. Every place ADR-0026 governs is in `compose/composition.py`, so every leg
  drives the platform's own `compose()`, `verify()` and namespace walk, on copies of tuppence
  against its real pinned parents or on the composition selfcheck's own fixture estate.
- Every verdict below is held by a test in `tests/test_loophole_adr_0026.py`. Its `VERDICTS`
  table names the test for each candidate, and its record legs check the table against the
  three `candidates.json` files, count the judge's verdicts, and compute the survival rate and
  the overlap.

### The eighteen verdicts

| round | candidate | verdict | the fact |
|---|---|---|---|
| 1 | `loophole-1` | discard | The removal it needs still refuses (the known lag). A bespoke hole is priced on its own line and moves no tier and no exposure total. Ticket 38 D5 already named that limit ("priced but not yet tiered"). |
| 1 | `loophole-2` | **survivor** | The delay is impossible: the cluster runs only a signed tag, and `verify` fails before the tag on a Namespace the header does not name. The place is real: `since` is looked up by name, so a rename restarts the ramp. Ticket 122. |
| 1 | `loophole-3` | discard | A bespoke `pl-2`, claimed, covers `tuppence:pl-2` only. The regulator's `pl-2` stays a hole, its weighted line stays `recorded`, and the header lists both keys. |
| 1 | `overreach-4` | discard | True as written: the live code refuses a removal. ADR-0026 names the lag itself, so the place is known (this ticket's rule 4). No ticket held the build; ticket 124 now does. |
| 1 | `overreach-5` | discard | An ungoverned Namespace is priced by its workload share only while it is in the repo. With no workload it prices at 0.0. Deleted, it closes with no price. Its price moves no tier. |
| 1 | `overreach-6` | **survivor** | True that an unweighted widening earns nothing. The place is wider: claiming all four weighted uk-gdpr lower-tier controls moves no regime price, no exposure total and no tier. Ticket 121. |
| 2 | `loophole-1` | discard | A narrowing still refuses, so the composition never emits `composed` for it. The known lag. |
| 2 | `loophole-2` | discard | A bespoke control never covers a regulator key, and the regulator control's removal still refuses. |
| 2 | `loophole-3` | discard | True, and the place is round 1 `loophole-2`'s. An echo of that survivor. |
| 2 | `overreach-4` | discard | The removal still refuses. And no hole moves a tier, so the "tier side effects" cannot happen. |
| 2 | `overreach-5` | discard | Governing a Namespace needs one label and no baseline. A governed Namespace with no tier binds as `isolated`. |
| 2 | `overreach-6` | discard | A wrong weight moves no regime price today: in an ico clone with 0.7 on `pl-2`, tuppence's regime entry, exposure and tiers are unchanged. The recourse is the adopter's own pin and a pull request to the publisher. |
| 3 | `loophole-1` | discard | Same facts as round 1 `loophole-1`. |
| 3 | `loophole-2` | discard | The delay is impossible (above). A Namespace made in the cluster outside the repo is Flux drift, which ADR-0026 point 4 leaves to the estate's drift tooling. An echo of round 1 `loophole-2`'s place. |
| 3 | `loophole-3` | **survivor** | The withdrawn hole does not vanish: the adopter, having changed nothing, is refused `removed-control` for it. ADR-0026 says a withdrawal is not an adopter removal. Ticket 123. |
| 3 | `overreach-4` | discard | `no-controls-parent` fires only when no controls parent is declared. A parent tree that cannot be read is a missing-parent refusal, ADR-0020's decided line. The recourse is a re-pin by pull request. |
| 3 | `overreach-5` | discard | `(source, id)` keeps one id from two sources as two selected controls. Nothing de-duplicates them. |
| 3 | `overreach-6` | discard | A directory of manifests is not a Namespace: the walk reads `kind: Namespace` only. The rest is round 1 `overreach-5`. |

### The survival rate

**3 of 18 survived: 17%, by round 2, 0 and 1.** ADR-0022 gave 3 of 18 too, so two documents give
6 of 36. `test_the_survival_rate_is_derived_from_the_verdicts` computes it and requires ADR-0030's
new dated note to say it.

The judge called 11 of 18 resolvable, as `summary.json` said. It called round 1 `loophole-2`, a
survivor, unresolvable. `test_the_judge_verdicts_are_counted_and_not_used` holds both counts.

### The matching across the three rounds

`MATCHING` in the test file gives each candidate the code place its check tested and the reason
it gives, both read by this ticket. `test_the_overlap_between_rounds_is_counted_by_place_and_by_reason`
computes, as a one-to-one matching per pair:

| pair | by place | by reason |
|---|---|---|
| rounds 1 and 2 | 5 of 6 | 0 of 6 |
| rounds 1 and 3 | 4 of 6 | 3 of 6 |
| rounds 2 and 3 | 4 of 6 | 0 of 6 |

All three rounds share four places (the bespoke scenario, the ramp's `since`, the removal, the
ungoverned walk) and no reason. The 18 candidates give 15 distinct reasons at 8 places. On
ADR-0022 ADR-0030 measured a reason overlap of 2, 1 and 3. On ADR-0026 it is 0, 3 and 0.

### Corrections to this ticket's own premises

- **Round 1 `loophole-3` points at the key, not the bespoke scenario.** Ticket 115 grouped it with
  the bespoke-price candidates. Its check is the `(source, id)` key: it prices nothing.
- **The reachable code is platform main**, not only the integration branch. The branch is an
  ancestor of main.
- **The budget line.** "At the survival rate measured on ADR-0022 (2 of 6)" predates ticket 116,
  which corrected the rate to 3 of 18. The README's budget sentence said 2 in 6 too and now says
  3 of 18 on each document.
- **Rule 4's known place had no ticket.** Ticket 39's D9 left the removal build's number to the
  integrator, and none was opened.

### Decisions

- **Delegated: the counting rule is ticket 116's, and echoes credit the earliest candidate.** Where
  several candidates point at one place, the earliest by (round, key) is the survivor and the rest
  are discards that name it. Reason: the count is the same whichever candidate is credited, and a
  fixed rule means nobody picks the candidate whose sentence reads best. So round 1 `loophole-2`
  survives with a false mechanism, and round 2 `loophole-3`, whose mechanism is exactly right, is
  its echo.
- **Delegated: a place a named limit or the ADR already holds is not a survivor.** Round 1 and
  round 3 `loophole-1` land on a bespoke price that moves no tier, which ticket 38 D5 named. Three
  candidates land on the removal lag, which ADR-0026 names. Reason: the rate budgets defects
  nobody knew.
- **Delegated: the withdrawal is a survivor, not the removal lag.** Both are refused by
  `check_selected_set`. But ADR-0026's list for the removal build does not include telling a
  withdrawal apart, and after that build a withdrawal would still print in the adopter's name.
  Reason: the repair is different, so the defect is.
- **Delegated: chart the removal build as ticket 124.** It is not a survivor and does not count.
  Reason: three candidates landed on a known place that no ticket held, and D9 said the
  integrator would open it.
- **Delegated: survivor legs assert today's behaviour.** Each survivor leg passes now and names
  the ticket that flips it, the shape ticket 116 used. Reason: a failing test on main would read
  as a regression, not a charted defect.
- **Delegated: the matching table lives in the test file, not a `targets.json` beside the
  rounds.** Reason: one table read by the test that computes from it, and nothing new under
  `bench/loophole/rounds/` for the leak check to cover.
- **Delegated: no misuse-catalogue rows here.** Ticket 116 added one because its Done asked. This
  Done asks for a test and a ticket per survivor. Each new ticket can add its row when it decides
  its repair. Reason: the catalogue's graded tests would move in a file another builder may be
  editing today.
- **Delegated: dated notes on ADR-0026 and ADR-0030, no rewrite.** ADR-0026 point 2, point 4 and
  the withdrawal sentence say things the code does not do. The note names the three tickets and
  changes no decision. Reason: which side moves, record or code, is each survivor ticket's
  decision.

### What changed

- `tests/test_loophole_adr_0026.py`: new, 15 legs.
- `.scratch/ecosystem/issues/121-implementing-a-control-moves-no-price-and-no-tier.md`: new.
- `.scratch/ecosystem/issues/122-the-ungoverned-ramp-keys-on-a-name-the-adopter-chooses.md`: new.
- `.scratch/ecosystem/issues/123-a-regulator-withdrawal-refuses-the-adopter-as-a-removal.md`: new.
- `.scratch/ecosystem/issues/124-the-removal-adr-0026-prices-has-no-build.md`: new.
- `docs/adr/0026-...`: dated note naming tickets 121 to 124.
- `docs/adr/0030-...`: dated note, 3 of 18 on ADR-0026, 6 of 36 on two documents, the overlap.
- `bench/loophole/README.md`: the budget sentence and the "attacked so far" line.
- `.scratch/ecosystem/map.md`: lines for tickets 120 to 124.

### What remains

Nothing waits on the owner. The repairs are tickets 121 to 124.

## Answer

Resolved 2026-09-23 by hub PR 93. All 18 loophole candidates against ADR-0026 carry a verdict
from a deterministic check against the served code, each held by a leg of
`tests/test_loophole_adr_0026.py`.

1. **Three survivors, 3 of 18.** Each is its own ticket: 121 (implementing a control moves no
   price and no tier), 122 (the ungoverned ramp keys on a Namespace name the adopter chooses) and
   123 (a regulator's withdrawal refuses the adopter as a removal).
2. **One more ticket that is not a survivor.** Ticket 124 is the platform build that ADR-0026
   names to price removals and that nobody opened. Ticket 123 lands with 124 or after it.
3. **The rate holds across documents.** ADR-0022 and ADR-0026 each gave 3 of 18, so the two give
   6 of 36. ADR-0026 and ADR-0030 carry dated notes.

Review: one round, pass. The reviewer found four minor points. This Answer and a missing unit in
the ADR-0030 note are fixed. A counting-rule wording point and a bare `python3` call that copies its
neighbour's idiom are left as they are.
