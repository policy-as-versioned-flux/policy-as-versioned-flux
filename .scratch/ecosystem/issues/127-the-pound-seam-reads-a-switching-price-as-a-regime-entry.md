# 127 — The pound seam reads a switching price as a regime entry

Type: task
Status: resolved
Blocked by: none

## Question

Charted 2026-09-23 by the integrator from a read-only map of the gate's reds. No ticket owns
this red. Ticket 79 built the check, and ticket 121 measured the same four FAILs and said "not
this ticket's".

`verify/pound-seam/verify-pound-seam.sh` FAILs with "4 £-seam check(s) observed false" on run
296. Measured on main:

1. `verify/pound-seam/pound_seam.py:210` treats every price with `source: ico` as a regime entry,
   and lines 227-230 demand `holes[]` from it. Each adopter's `composed/evidence.json` carries two
   ico prices: `kind: feed`, which has `holes[]`, and `kind: switching`, which has none. Three of
   the four FAILs are the switching entries (driftwood `prices[4]`, ludlow and tuppence
   `prices[3]`).
2. The fourth is driftwood `prices[5]`, feeds/threat-register `kind: switching`, with
   `amount: None` and a named `could_not_look`: its forward-intel feed supplies no lef.

Ticket 128 adds `kind: supersede` prices from ico too, so the misreading will grow.

What this ticket owes:

1. Check 4 selects regime entries by kind, not by source alone.
2. A price that carries a non-empty `could_not_look` grades as a named could-not-look, declared in
   `talk/verify-manifest.txt`, not as a FAIL. It must not grade PASS either.
3. Selfcheck cases for both, each red on today's code.

## Done

The check grades each ico price by its kind, a named could-not-look is a declared SKIP, and the
selfcheck holds both. Whether driftwood's forward-intel feed can ever supply a lef is a separate
question near grilling ticket 30 and is not this ticket's.

## Build, 2026-09-22

Hub only. Branch `ticket-127-pound-seam-switching-price`. No unit repo changed.

What changed:

1. `verify/pound-seam/pound_seam.py` check 4 now selects the regime entry as `source: ico` and
   `kind: feed`. ico's `switching` and `supersede` prices carry no `holes[]` and are no longer
   asked for them. They are still graded by legs 1, 2 and 5, and supersede arithmetic by
   `verify/supersede/`.
2. Leg 1 grades a price with no amount and a non-empty `could_not_look` as a named SKIP. The
   line names the entry, its source, name and kind, and quotes the reason. It never prints PASS.
3. Leg 1 still FAILs a price with no amount and no reason. It now also FAILs a could-not-look
   that restates an amount per customer, and a price that carries both an amount and a reason.
4. `talk/verify-manifest.txt`: the pound-seam row's `waits:` pattern gains one alternative,
   `switching\) could not be priced, and says why: missing instrument: .* supplies no lef`, and
   the row's note says why.
5. Eight new selfcheck cases (seven graded, one baseline).

Measured, all in the hub worktree against the local `.estate-clone` (driftwood c96c412, ludlow
32d5696, tuppence 7009ea9, platform 13f6b22):

- Red first. The new selfcheck run against origin/main's `check_doc`, with a grader that records
  instead of stopping: 4 cases red (ico switching read as a regime entry, ico supersede read as a
  regime entry, a named could-not-look graded as a SKIP, a price with both an amount and a reason),
  plus the "one SKIP and no PASS" count. The three guard cases (feed entry still owes holes beside
  a switching price, empty reason fails, per-customer on a could-not-look fails) were already
  green on main, as guards should be. Green on this branch: `pound_seam.py selfcheck` exits 0.
- Grade row on the real estate: from FAIL to a declared SKIP. origin/main's `pound_seam.py check`
  exits 1 with 4 FAIL lines. This branch's exits 3 with 30 PASS and 1 SKIP. The SKIP is driftwood
  `prices[5]`, feeds/threat-register `kind: switching`. The wrapper's last line is that SKIP.
- The gate's own judge: `talk/truth_manifest.py judge talk/verify-manifest.txt
  verify/pound-seam/verify-pound-seam.sh "<that last line>"` prints `declared waits`, exit 0.
  The same line against origin/main's manifest prints `undeclared`, exit 1. The same shape with
  another reason (`missing instrument: USD rate not published`) is `undeclared`, exit 1.
- `talk/truth_manifest.py check talk/verify-manifest.txt --exclusions talk/verify-exclusions.txt`
  exits 0. `talk/truth_manifest.py selfcheck` prints `selfcheck ok`.
- `pytest tests/test_truth_manifest.py -n0 -q`: 18 passed. mypy over `twin tests conftest.py`:
  no issues in 199 files. mypy over `pound_seam.py` alone: no issues.

Decisions (delegated, ADR-0025):

1. The regime entry is ico's `kind: feed` price. Reason: that is the only ico kind the composer
   gives `holes[]` and `total`. Selecting by kind grades ticket 128's `kind: supersede` ico
   prices correctly with no further change, and a selfcheck case holds that.
2. The could-not-look SKIP lives in leg 1, not leg 4. Reason: the fourth FAIL was a feeds price,
   not an ico one, and leg 1 is where "carries no numeric amount" was refused. One SKIP line per
   entry. Leg 4 skips an ico feed entry that leg 1 already graded as a could-not-look, so it is
   never also a PASS or a FAIL.
3. A price with both an amount and a reason is a FAIL. Reason: platform
   `compose/composition.py` writes `amount = None if could_not_look else ...`, so the two never
   coexist in a composed document; one that carries both contradicts itself.
4. The manifest declares only today's reason, "supplies no lef", not every could-not-look.
   Reason: a broad pattern would hide a new reason under an old declaration, the known limit the
   manifest's header names for aggregate lines.

Known limit, not this ticket's: the wrapper puts only the FIRST `SKIP:` line on its last line.
If an earlier leg ever SKIPs for a declared reason, a later undeclared SKIP hides behind it. That
is how the row worked before this ticket. Today there is exactly one SKIP, so nothing hides.

Owner items: none. Whether driftwood's forward-intel feed can ever supply a lef stays near
grilling ticket 30, as the ticket says.

## Answer

Resolved 2026-09-23 by hub PR 106. The pound seam grades each ico price by its kind.

1. Check 4 picks the regime entry as the ico price of `kind: feed`. ico's `switching` and
   `supersede` prices are no longer asked for `holes[]`.
2. A price with no amount and a non-empty `could_not_look` is a named SKIP, never a PASS. A price
   with neither still FAILs, and so does a price that carries both.
3. `talk/verify-manifest.txt` declares the one real could-not-look, driftwood's forward-intel
   feed that supplies no lef. The gate's own judge accepts the real line and refuses the same
   shape with another reason.

On the real estate the row moves from FAIL (4 lines) to a declared SKIP (30 PASS, 1 SKIP).

Review: one round, pass, four minor findings, not fixed. One names an edge worth a later ticket:
a document with an ico switching price and no ico feed entry grades a named-absence PASS.
