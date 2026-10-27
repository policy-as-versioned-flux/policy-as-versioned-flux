# 168 — Causal evidence needs affirmative support

Type: task
Status: resolved
Blocked by: none

## Question

The user resumed implementation after delegating a labelled evaluation corpus and a dedicated pilot custodian. The new agent-authored synthetic challenge exposed poor causal reasoning. Its broad accuracy is not a previously claimed independent-quality result: build45 explicitly declares the fixed-magnitude heuristic stand-in. A separate, minimized public-API failure violates the existing evidence ladder: `expert judgement`, including an explicitly calibration-untrained opinion, receives grade4. The ladder requires calibration-trained judgement; unsupported opinion belongs at grade5.

Decision08 Q2, build45 and the existing asymmetric grade scorer require this distinction. Thirteen paired probes confirm that an unqualified alias, substring matching inside `uncalibrated` and ignored negation cause over-grading. The internal selected marker, public answer and Stated trace agree; scoring is not the defect. Independent valid calibration evidence is a positive control and must remain usable. A subsequent public-API control exposes the same defect for stronger grades: explicitly denying a dated natural experiment, repeated historical co-movement or published work produces grades1,2,3 rather than5. These grades may reach price eligibility, so the same bounded correction covers the existing marker vocabulary across grades1–4.

## Done

- Ordinary, explicitly uncalibrated and negated calibration opinions remain grade5 without stronger independent support. Affirmative calibrated-judgement vocabulary remains grade4.
- Explicitly denied grade1–3 evidence does not manufacture that grade; remaining affirmative evidence determines the result or defaults to5. Whole-phrase boundaries and local claim scope prevent negative language from manufacturing positive support across grades1–4. A separate valid source or a distinct affirmative claim is not vetoed by an unrelated unsupported opinion.
- `propose` and `propose_stated` share the same actual decision and expose the selected marker/default/source reasoning. The remaining keyword heuristic and source-authentication limits stay explicit.
- The existing `causal_claims_over_grading_is_penalised_and_alternatives_are_mandatory` check is strengthened, preserving its original legs and registered name. Public-interface regressions and that check cover both calibration and the denied stronger-grade cases, and are red before the fix and green after it, with a restoration control.
- Sign/lag/fixed-magnitude logic, confounders/alternatives, four fitted raw answers, actual scorers, asymmetric penalty, original corpora, thresholds/minima, party grade3 pricing opt-in, permissions and score/history bytes remain conserved. A corrected unsupported grade may change its grade-derived width.
- Independently reviewed source is delivered through ordinary signed publication, original CI classification and matching-head App review/normal merge. Later original measurement remains a separate source-bound fact.

## Scope and authority

The assistant makes this architecture/implementation decision under ADR0025 and the user's standing implementation and ordinary reviewed delivery authority. It strengthens the named existing check; it authorizes no weaker invariant, threshold, evidence ladder, permission, fabricated source or prototype-quality claim. No new model/provider, generic natural-language parser, fitted numerical rule, corpus relabelling, workflow retry or local cluster is required. Re-runs of the examined challenge are explicitly regression re-evaluations.

The diagnostic's original full grade reproduction returned grade4 instead of5 in0.00460seconds at the public API; its minimal two-token statement reproduced on three repeats, and deleting either token restored grade5. Actual current source base `2fc2fddd039dc649c130f5cdbc5469930b41e62e` has the same causal module bytes as the diagnosed delivered source.

## Answer — 2026-10-27, source capability verified privately

The owning registered check remains `causal_claims_over_grading_is_penalised_and_alternatives_are_mandatory` in `twin/invariants/harness.py`. Its original three legs still test the asymmetric over-grading penalty, mandatory alternatives and actual shared graph ancestors. An additional evidence-authority leg exercises the actual public raw/Stated interfaces, unsupported calibration, denied grade1–3 cues and affirmative controls. No new check name, TRUTH row, threshold or permission was added.

The shared grade selector removes the unqualified expert-opinion alias and checks the existing grade1–4 phrases at word boundaries within separately supplied statements and simple sentence/semicolon/contrast clauses. Prefix denials and bounded immediate denial predicates after a marker prevent the reproduced promotions. Calibration contradiction terms remain conservative refusals. A separate affirmative source or distinct supported clause still supplies its rung; denied stronger evidence yields to valid weaker support rather than winning the ordering. Raw and Stated outputs share the same actual decision, marker/default and source evidence.

Actual diagnosis ruled out answer assembly and scoring: internal selected markers, public grades and Stated traces agreed on the wrong promotions. The original calibration regressions produced12FAIL/12PASS before its correction. The expanded stronger-rung regressions produced19FAIL/4PASS before that correction. The strengthened guard failed on the old selectors. The final product passes149focused causal/basis/harness tests in11.88seconds,72evidence-ladder/pricing tests in62.26seconds, the real owning CLI check with1PASS/0FAIL/0SKIP, three-file mypy and diff whitespace validation. These are local machinery controls, not empirical observations.

The original full and minimal calibration reproductions and the three original denied stronger-grade cases now return the expected grade5. Restoring the old calibration selector recovers its original failure; restoring the pre-extension selector recovers the stronger-rung failures and guard RED. Restoring the final bytes clears those failures again. All four historical fitted raw answers and their input/expected labels remain exact, raw/Stated answers agree, and281other tracked twin/test paths are byte-identical. The only additional changed protected source path is the authorized existing harness guard. Sign, lag, fixed mode, confounders/alternatives, both scorers, asymmetric penalty, ladder, thresholds/minima, party-specific grade3 opt-in, corpora, score history and model permissions remain conserved. A corrected grade legitimately changes its derived width.

## Recorded-check qualification and limits

Resolution records the privately verified source capability at base `2fc2fddd039dc649c130f5cdbc5469930b41e62e`. Existing recorded checks predate this source and do not exercise the strengthened leg. Ordinary independent review, signed publication, original configured CI classification, matching-head App approval/normal merge and later source-bound measurement remain distinct delivery facts. This ticket does not pre-assign a future gate grade or erase the historical `flux_coverage_floor_is_still_reachable` shortfall.

This is a bounded lexical reference heuristic. Recognized affirmative wording does not authenticate a source, prove estimator calibration or establish causal identification. Quotation, nested negation and grammar outside the stated direct forms remain limitations. The fixed-magnitude numerical prototype and broader challenge-quality findings remain disclosed. The108-case agent-authored challenge, all labels and prior results stay frozen; observed cases are regression material rather than a fresh unseen holdout. No provider/model call, local cluster, financial observation or workflow retry occurred.
