# 169 — The decay date names the first decayed day

Type: task
Status: resolved
Blocked by: none

## Question

Build54 and decision11 Q3 retain unbound signals with a reported decay date. The public `decayed_on` closed-form estimate can name a day that is still live at the strict threshold, or a day after the first decayed day because logarithmic rounding overshoots. A half-life1/threshold0.5 signal dated2026-01-01 currently reports2026-01-02 while its weight is still0.5. The first decayed calendar day is2026-01-03.

## Required delivery

- Return the first whole calendar day satisfying the unchanged `is_decayed(weight(age,path),path)` predicate; the predecessor must remain live. Correct estimates that are either early or late.
- Keep public interfaces, the versioned decay.yaml bytes, strict predicate, retention/rescue, pin and grade/scorer/history behavior unchanged. Search must be bounded by representable calendar dates and preserve ordinary overflow/error behavior for dates that cannot be represented.
- Exercise public functions and pool integration at exact, fractional, adjacent-float and ordinary boundaries. Strengthen the existing `unbound_pool_retains_a_decayed_signal_rather_than_dropping_it` check without removing any retention/count leg or changing its registered name. Preserve actual RED/GREEN/restoration evidence.
- Local verification, ordinary source delivery and later source-bound TRUTH remain distinct. No future grade, new empirical fact, provider, cluster, workflow dispatch or policy retuning is authorized.

## Notes

Claimed2026-10-27 before source/test changes on02381daa338a9d5061e79deb177ac11289a4228d. Root supplied minimized public RED and one-variable controls before this implementation. Seams are the existing `decayed_on`, `weight`, `is_decayed`, `pool` and registered retention guard; standing authorization explicitly covers them.

## Answer — 2026-10-27, source capability verified privately

The owning registered check remains `unbound_pool_retains_a_decayed_signal_rather_than_dropping_it`. Its original retention and observable live-count legs remain. A new boundary leg uses the existing public functions with half-life 1 and threshold 0.5: a signal dated 2026-01-01 must report 2026-01-03, which is decayed, while its predecessor remains live. No new check name or TRUTH row was added.

`decayed_on` uses its logarithmic result as an estimate and checks the unchanged `is_decayed(weight(age, path), path)` predicate on the reported day and predecessor. When correction is needed, binary search over representable whole calendar days finds the first decayed day. The calendar bounds correction to at most 22 iterations; an accepted half-life with no representable crossing still raises `OverflowError`. This corrects estimates on either side of the boundary, including the reproduced late result and a valid crossing on the final representable date. The published decay parameters, strict predicate, public interfaces, retention/rescue, pinning, grades, scorers and history are unchanged.

The first literal public regression failed before the product edit, then passed. Final focused pool and retrospective-rescue suites pass 47 tests; targeted mypy passes three source files. Public coverage includes exact powers, fractional half-lives, adjacent floating thresholds, an ordinary crossing, the reproduced late estimate, a large accepted half-life, calendar overflow and pool/live-count agreement across the boundary. The existing default-parameter test now checks the reported day itself as well as its predecessor.

Restoring only the original product bytes produces 8 FAIL / 5 PASS in the selected boundary tests and makes the strengthened owning CLI check fail. Restoring the exact fixed bytes gives 13 PASS and the owning CLI check 1 PASS / 0 FAIL / 0 SKIP. Both original early and late public reproductions now satisfy the current-day and predecessor predicates. All original receipts are retained. An earlier attempted suite passed 31 tests but rejected one test YAML scalar: scientific notation without a decimal point parsed as text. The fixture notation was corrected, preserving that refusal and the existing product validation.

## Recorded-check qualification and limits

Resolution records the privately verified source capability at base `02381daa338a9d5061e79deb177ac11289a4228d`. The local passing check is `unbound_pool_retains_a_decayed_signal_rather_than_dropping_it`; existing recorded checks predate this strengthened boundary leg. Ordinary independent review, signed source publication, configured CI, matching-head App review/normal merge and later source-bound TRUTH remain separate delivery facts. No future recorded grade is assigned here, and the historical coverage shortfall remains.

This computes the first whole calendar day using the existing floating-point decay function and accepted parameters; it does not replace that function with exact real-number arithmetic or introduce new parameter policy. Dates outside the representable calendar remain errors. No provider, model, cluster, workflow dispatch, empirical observation, corpus, score or permission change occurred. Actual commands and results are preserved in the sibling `implementation-v1` packet.
