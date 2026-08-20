# 13 — Balance-sheet → Total Cost of Risk

**What to build:** Residual £ framed as economic/risk-based capital, extended to **TCoR = residual + cost-of-controls (incl. dynamic cages) + transfer (premiums)**. The moving-£ loop is demonstrated live; the fix/cage/transfer/deny crossover is computed.

**Blocked by:** 06, 10, 11

**Status:** done (2026-08-20) — `estate/platform/tcor/verify-tcor.sh` PASSes offline

- [x] Balance-sheet number = TCoR (residual + control spend incl. cages + transfer premiums) — `bash estate/platform/tcor/verify-tcor.sh` → `TCoR £47,921 = residual £27,271 + controls £3,500 + premium £17,150`
- [x] £ moves as expected: accept a condition → rises; tighten a control → falls; a cage kicks in → control-spend rises; new threat/EOL → jumps — same run: `levers: accept->£72127  tighten->£27771  threat/EOL->£76801`; step 3: caged control-spend `driftwood £500 -> ludlow £6,000` under a stricter band
- [x] The fix/cage/transfer/deny crossover is computed — `crossover: cheap-fix->fix, ruinous-fix->cage`; step 2 confirms all three book lines are real: `moves=['cage', 'fix', 'transfer']`

## Comments

- 2026-08-20 (audit mo-02): `verify-tcor.sh` PASSes offline; all 3 ACs directly evidenced. The prose's "demonstrated live" is realized as a pure offline computation over the same `fair.py`/`cage.py` engines, not an actual cluster demo — no cluster is needed for this ticket's own ACs. Status corrected from `ready-for-agent` to `done`.
