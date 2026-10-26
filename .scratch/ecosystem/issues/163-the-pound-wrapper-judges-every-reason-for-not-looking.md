# 163 — The pound wrapper judges every reason for not looking

Type: task (AFK)
Status: resolved

## Question

Can a declared £-seam wait hide a later undeclared missing instrument because the wrapper reports only its first SKIP line?

## Required delivery

When the money grader exits 3, `verify/pound-seam/verify-pound-seam.sh` must pass every individual SKIP line to the existing `talk/truth_manifest.py judge` CLI and unchanged manifest. Only if all reasons are declared may its final summary retain the first accepted wait and exit 3. An unknown reason in either order, a missing reason, or an unavailable judge must fail. Genuine backend failures stay failures. Preserve child output and existing declaration patterns, financial logic and observation history.

Use explicit money-child fixtures through the actual wrapper and actual manifest/CLI, including independent single/mixed/order/backend-failure controls. This implements the existing declared-wait contract; it does not register a new wait, turn an unpriced amount into zero, reprice an estate or change a recorded TRUTH grade.

## Notes

Claimed 2026-10-26 in an isolated canonical-origin clone at public base f0efb127. Root's actual wrapper/manifest reproduction is red for allowed-then-unknown and green for the reversed unknown-first order. The original RED captures and the earlier reproduction-helper typo STOP remain immutable. Source publication, configured CI, a later genuine primary and future natural observations are separate evidence.

## Answer — source fix verified in isolation, 2026-10-26

The wrapper's exit-3 branch now submits every SKIP line to the existing manifest judge CLI, including an unterminated final line. It retains its first wait as the final summary only after all reasons were accepted. Missing reasons, a missing judge/manifest, any rejected reason in either order, and a child FAIL despite exit 3 produce a final FAIL. A genuine backend exit 1 remains exit 1; all declared waits remain exit 3. The complete child output is still printed.

The new `tests/test_pound_seam_wrapper.py` invokes the real shell wrapper and unchanged complete manifest/judge CLI in disposable filesystem roots. Only the money child is a fixture, including its selfcheck; no financial engine, estate grading, native execution or cryptographic verdict is claimed. Before the fix its twelve cases produced eight failures and four passes; after the fix those cases and the unchanged manifest suite produced 39 passes. Restoring the original wrapper makes the declared-then-undeclared regression fail again. Root's original four-case wrapper-plus-judge reproduction also becomes green: only the declared-only case is accepted as a wait. Bash syntax, shellcheck and the existing manifest selfcheck pass.

The backend-failure control passed before the fix, disproving the pipeline-status hypothesis. The measured cause was the wrapper's first-SKIP-only summary hiding a later undeclared missing instrument. No manifest pattern, money grader, price, policy, observation or recorded grade changes. The first test command stopped before collection because this interpreter has no coverage plugin and cannot accept `--no-cov`; the corrected serial test command runs with coverage absent, without installing or changing the environment.

### Delivery qualification — 2026-10-26

This Answer records the bounded source fix and explicit fixture verification of `verify/pound-seam/verify-pound-seam.sh`. It is not a new current-estate PASS or a new primary grade. Independent review, ordinary public source delivery and configured CI remain separate publication steps. Existing undeclared real missing instruments remain failures; future annual outcomes, natural observations and live moved witnesses remain separate evidence requirements. Earlier primary records and the original reproduction-helper STOPs are retained unchanged.
