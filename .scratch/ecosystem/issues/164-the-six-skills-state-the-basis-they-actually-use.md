# 164 — The six skills state the basis they actually use

Type: task (AFK)
Status: resolved

## Question

Can the six actual skills expose their own decision basis to the existing seam-3 evaluator without changing their raw answers or turning fitted examples into independent evidence?

## Required delivery

Complete ticket 118’s remaining software capability: evaluation-facing `Stated(answer, basis)` entrypoints for signal-classify, evolution-judge, causal-claims (both metrics), gameplay-lens, substrate-generator and ethics-gate. Each must share the real decision computation with its existing raw function and cite the actual rules/source witnesses used. Do not copy expected labels or an input-provided basis. Preserve raw APIs/results, seven scorers, fitted corpora/digests, CORPUS_KIND, thresholds/minima, model permission and score history. Keep recorder evaluation and raw baseline functions explicit. Use the generic evaluator with explicitly supplied test-only bases for mechanical RED/GREEN and negative controls. Real sufficient independent labels remain separate, and no empirical pass or permission follows.

## Notes

Claimed 2026-10-26 before source/test changes in an independent canonical HTTPS clone at f0efb12775b06dbf2d555d92b76f27edaeb2f4ef, branch codex/actual-skill-bases-20261026. Root accepted source plan 7d4d36a5fd501446549cf19a0ceb739048883e01c4384e85e6cb0f7c2e8a060c. Ticket 163 is separately claimed by the pound-seam author. No owner decision blocks this software capability. No signing/publication/native/crypto/model-call or committed score-log write is authorised in this private author phase.

## Answer — software capability verified privately, 2026-10-26

The six actual skills now have explicit evaluation entrypoints: `classify_stated`, `judge_stated`, both modules’ `propose_stated`, `generate_from_recipe_yaml_stated` and `admit_stated`. Every raw and stated entrypoint shares one internal decision computation. Its basis names actual keyword/default decisions, token-overlap candidates, cited evidence fields, graph precondition witnesses, recipe/seed/channel generation, or the walked sensor-ladder readings and current table/rules. No entrypoint reads an expected answer or caller-provided basis. Fixed causal magnitude, unchecked gameplay incumbency and synthetic generation remain disclosed limits.

**Delegated:** keep the existing raw APIs and add separate `raw_skill(metric)` and `evaluation_skill(metric)` registry selection. The recorder evaluates stated functions; `corpus_facts` still sends raw answers into baselines, variance and reference scoring. The generic evaluator and its corpus/basis-scorer interface are unchanged: a caller can explicitly supply a separately sourced corpus through that existing seam, without a new data-loader or model API.

Each skill’s first actual evaluator test was RED (correct answer, absent stated basis, UNSCOREABLE) before its entrypoint was implemented, then GREEN. The registry integration was separately RED before being changed. The causal test initially used the wrong expected-field shape; that STOP is retained, the fixture was corrected to the unchanged scorer contract, and actual base source was restored to demonstrate the correct attribution RED before the fixed implementation passed. A later test found trace capture reading an out-of-scope gameplay position that the raw API did not read; that genuine KeyError RED is retained and trace capture now preserves the original boundary.

Actual verification: the ten focused compatibility modules passed 274 tests serially in 184.24s. After the final signal trace-sharing and gameplay unread-field correction, the two affected raw suites plus the final boundary suite passed 67 tests in 38.25s. Final targeted mypy passed all eight changed Python files. The final 29 boundary tests cover all seven metrics, correct/wrong/absent/foreign bases, hidden labels, changed source witnesses, raw-answer compatibility and below-minimum NOT MEASURABLE outcomes. These are explicitly TEST_ONLY worked examples, never a new independent population.

A separate pure comparison used the original f0ef Git package and final source. All 46 raw answers across seven metric rows, every fitted corpus digest, full baseline/variance/reference facts and fitted-model declarations are byte-identical: both 43,414-byte reports hash to 74436184f7b5fef3228485d6ac076e92e24ebbff40d7fa60ae651dd7835ffa93. All seven scorers and six corpus builders retain identical ASTs; the generic evaluator, permission implementation, thresholds/minima, score history, corpus-size rules, sensor table and fixtures are byte-identical to base.

### Delivery qualification

This resolves only ticket 118’s remaining software capability. Source authenticity, independent semantic labels, holdout provenance and adequate measured populations remain separate work. Existing fitted corpora gain no basis or independent status; CORPUS_KIND stays harness-mechanism, all seven existing metrics remain not measurable, and no model permission is granted. No score/model log was written outside test temporary directories. No real model call, compiler/financial/native engine, cryptographic execution, Docker, workflow dispatch, signature, public push or merge was performed in this author phase. Independent review, configured CI and ordinary public delivery remain pending. No real-world skill accuracy, annual outcome or live estate observation is established.

Map line: [164 — The six skills state the basis they actually use](issues/164-the-six-skills-state-the-basis-they-actually-use.md) — privately verified software capability, 2026-10-26: actual decision traces reach the existing evaluator for all six skills/seven metrics while raw answers, corpus facts, scorers and permission boundaries are conserved. Fitted corpora remain basis-less and not measurable; authentic independent labels, review and public delivery remain separate.

### Independent review correction — 2026-10-26, version 2

The first independent Spec review requested explicit fallback provenance (P2): an empty signal keyword list did not state the economic fallback or fixed grade5, and null causal markers did not state default grade5, negative direction or180-day lag. Version1 and its CHANGES_REQUIRED review are retained unchanged in the private evidence packet.

The narrow correction takes those values from the same constants used by the actual decision computation, states whether each fallback was used, and identifies signal’s fixed grade as a model assertion. Matched and no-match paths share those rules; raw answers do not change. Three new default-path cases through the actual evaluator were RED on exact version1 source (WRONG_BASIS despite correct answers), then GREEN. Their independent TEST_ONLY basis labels also reject wrong fallback values, wrong fixed grade and a wrong default-use claim while the answer stays right. The duplicated test-local metric-scorer lookup was consolidated; expected bases remain separately authored literals.

Version2’s final boundary suite has32 tests. The two affected raw skill suites plus those boundary tests passed74 tests in15.98s; final targeted mypy passed all8 changed Python files. A fresh actual final-source comparison conserved all46 raw answers, seven corpus digests and full baseline/variance/reference/fitted-model facts against the original43,414-byte report, SHA25674436184f7b5fef3228485d6ac076e92e24ebbff40d7fa60ae651dd7835ffa93. No broader274-test rerun is claimed: the five unaffected skill/registry modules are byte-identical to version1, and its original compatibility receipts remain historical evidence.

This version uses a new canonical HTTPS clone on the normal public Pound merge09a1c9cfc8ddafee169169d7f736cf58288bc26d. The base advance changed only Pound’s four paths; the entire twin subtree is unchanged from f0ef (b683d28f3fa5450e7dccbc8f24a5412050563a66). The public ticket163 map entry and every other base byte remain, with only this ticket164 line added. The old author clone, version1 snapshots and every earlier failure/STOP are preserved. Version2 independent review, signing, public CI and delivery remain pending. Authentic corpus labels, empirical measurability, permission and all other evidence limits above are unchanged.
