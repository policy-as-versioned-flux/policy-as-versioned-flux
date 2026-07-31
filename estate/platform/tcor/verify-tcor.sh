#!/usr/bin/env bash
# Beat: "The board line is Total Cost of Risk — residual + cost-of-controls (incl.
# dynamic cages) + transfer premiums — and it MOVES: accept a condition -> it rises,
# tighten a control -> it falls, a cage kicks in -> control-spend rises, a new
# threat/EOL -> it jumps. For each risk the war-gamer computes the fix/cage/transfer/
# deny crossover and books the cheapest." Exits non-zero if the beat would fail on stage.
#
# OFFLINE only (this beat needs no cluster — it is pure £ maths over versioned inputs):
#   1. tcor.py selfcheck: every move books residual+controls+premium; the crossover is
#      computed (cheapest wins, and a cost change flips it); the balance sheet sums the
#      three lines over the book; and the four living-£ levers each move the number the
#      predicted way (accept up, tighten down, cage raises control-spend, threat/EOL jumps).
#   2. The demo book prices out to all THREE moves in play (fix + cage + transfer) so the
#      premium line is real, and the aggregate = residual + controls + premium exactly.
#   3. Proportionality: the SAME book under a stricter appetite band cages harder / costs
#      more (driftwood £40k vs ludlow £5k) — the £ picks a different move-mix per org.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
say()  { printf '\033[1;36m==>\033[0m %s\n' "$*"; }
fail() { echo "FAIL: $*" >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || fail "python3 required"

say "1. offline: the balance sheet is TCoR, the crossover is computed, the £ moves"
python3 "$HERE/tcor.py" selfcheck || fail "tcor.py selfcheck failed"

say "2. offline: the demo book prices out to fix + cage + transfer (all three lines real)"
python3 - "$HERE" <<'PY'
import sys, os, json
here = sys.argv[1]; sys.path.insert(0, here)
import tcor, enforce, fair
pf = fair.load(os.path.join(here, "scenarios", "driftwood-portfolio.json"))
bs = tcor.balance_sheet(pf, enforce.tolerance_for("driftwood"))
chosen = {r["chosen"] for r in bs["rows"]}
assert {"fix", "cage", "transfer"} <= chosen, f"expected all three moves in play, got {chosen}"
assert bs["residual"] > 0 and bs["cost_of_controls"] > 0 and bs["transfer_premium"] > 0, bs
assert abs(bs["tcor"] - (bs["residual"] + bs["cost_of_controls"] + bs["transfer_premium"])) < 1e-6, bs
print(f"  ok   TCoR £{bs['tcor']:,.0f} = residual £{bs['residual']:,.0f} + controls "
      f"£{bs['cost_of_controls']:,.0f} + premium £{bs['transfer_premium']:,.0f}  moves={sorted(chosen)}")
PY

say "3. offline: proportionality — the same book cages harder under a stricter band"
python3 - "$HERE" <<'PY'
import sys, os, json
here = sys.argv[1]; sys.path.insert(0, here)
import tcor, enforce, fair
pf = fair.load(os.path.join(here, "scenarios", "driftwood-portfolio.json"))
dw  = tcor.balance_sheet(pf, enforce.tolerance_for("driftwood"))  # loose £40k
lud = tcor.balance_sheet(pf, enforce.tolerance_for("ludlow"))     # strict £5k
def controls(bs): return next(r for r in bs["rows"] if r["chosen"] == "cage")["cost_of_controls"]
assert controls(lud) > controls(dw), (controls(dw), controls(lud))  # stricter band -> tighter/costlier cage
print(f"  ok   caged row control-spend: driftwood £{controls(dw):,.0f} -> ludlow £{controls(lud):,.0f} (stricter band cages harder)")
PY

echo "PASS: the board line is TCoR, it moves as the levers predict, and the four-move crossover is computed."
