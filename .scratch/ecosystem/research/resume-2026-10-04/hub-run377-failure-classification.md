Run377 contains real source/checker regressions as well as older observations. Its 25 FAIL grades cannot be explained as live limits. This assessment reads the grade table and captures from immutable hub commit `48324860b8b9f7dc4762e9c9f841206881a28705`; the executing source was `14ec4902bcbd4be58ac43e0ab47d0ea1f4c8250d`. The original received GitHub CLI downloads and their hashes remain in `hub-run377-capture-reads.json` and `hub-run377-captures/`. Independent review found that seven downloads and the downloaded grade table rendered ESC bytes as literal `^[`; their received bytes remain unchanged, but those downloads are not exact Git blobs.

Exact binary Git blobs for all 25 failures and the grade table are now retained separately in `hub-run377-git-raw-captures/`. `hub-run377-git-raw-provenance.json` binds each immutable source blob ID, exact SHA256 and received-download comparison. Eighteen downloads match Git byte-for-byte; the other seven differ only in that ESC rendering. Existing preservation receipts refer to the original received download bytes; the new raw-Git receipt establishes source-byte identity. The exact grade table still records 88 PASS, 25 FAIL, 22 SKIP and 8 EXCLUDED. No check was rerun, dispatched or regraded by this recovery.

| Actual FAIL check | Primary cause and proper closure |
|---|---|
| DW twin-sweep moved-path | Stale-feed fixture changes immutable v1 while the current emitter renders v2; its false result propagates to step5. Cloud owns a current-major regression repair after delivery. Live moved=true is separately absent. |
| Insurer quote | Authentic unpriced exposure has `total: null`; published `pricing/quote.py:257` calls `float(None)`. Add a typed missing-instrument `Refused` path and regression; retain unknown total, never zero. |
| LU standing scenarios | Grader demands a literal claim that the consequence is unpriced, but authentic source now explicitly prices the native grade3 consequence at threshold3; only grade5 mitigation is unpriced. Preserve that genuine price and repair the stale distinction, rather than adding a false absence. |
| Platform composition | Eleven portable-observation fixtures now refuse their CVE subscriptions without committed inventory. Repair fixture Git/apps/inventory closure; retain the production refusal. |
| Platform feeds | Legacy feed smoke test invokes CVE pricing without a committed inventory. Supply a valid test instrument, preserving all signed old bodies. |
| Platform OSCAL claims | Resolver hardcodes only two machinery identities and misses three actually shipped members. Read the genuine machinery catalogue; preserve the zero-dangling guard. |
| TU standing scenarios | Same stale unpriced-consequence assertion as LU. Genuine grade3 pricing and unpriced grade5 mitigation must remain distinct. |
| CVE inventory | Capture itself passes. Missing manifest row converts genuine PASS to FAIL in the summary; Spec's reproduction confirms this, rather than a converter failure. |
| Demo | Aside capture says SKIP while its grade row says FAIL. Repair upstream classification/runtime causes before refreshing any demonstration. |
| Derived status | Four resolved ticket records lack dated acknowledgements of owned red checks. Keep the red and record genuine ownership; do not relabel checks green. |
| E2E step2 | Temporary copied adopter lacks a real Git/apps binding; the strict CVE inventory reader cannot resolve it. Preserve committed object closure in the test clone. |
| E2E step5 | Propagates DW moved-path fixture failure. Offline fix cannot establish a future live firing. |
| E2E step6 | Propagates insurer's invalid legacy cloud-implementation pin, below. |
| Engine pairing | Three forward temporary adopters lack Git/apps closure; planted control also fails. Served engine sections themselves pass at 1.18.2. Repair clone fixture context. |
| Feed contract | Insurer pins platform implementations3.3.0, whose tree has no claimed `implementations/cloud`. This is a real declaration mismatch, requiring a truthful pin/contract fix. |
| Forge review | Five real main branches lack required pull-request protection. This audit changes no forge protection. Keep this governance finding explicit. |
| Lifted apps | Snapshot DW/LU claim7 while their served composed ref still v3/policy5. Atomic delivery addresses the real coupling; a future clock must observe the updated source. |
| Map surface | New workload/OSCAL lane declarations are absent from the hub's ownership map. Add the actual owned paths with negative tests, without broadening clocks arbitrarily. |
| OSCAL lane | Wrapper demands a missing hub-local `.venv`, despite installed runner Python. Runtime discovery repair; no validation deletion. |
| Pound seam | Current table picks isolated while LU/TU evidence attributes baseline. This is a concrete table/evidence mismatch; Spec is diagnosing the exact reduction-set context before any change. |
| Refusal register | Accepted row explicitly names only cage-tier5 while the served surface has5/6/7. Review and record the exact new identities and retained hazard; no blanket acceptance. |
| Schedules | Last actual feeds/insurer and LU/TU twin-sweep scheduled runs are red. Their new-source fixes need an actual subsequent successful tick; no synthetic clock or claimed success. |
| Served workloads | Same missing hub interpreter as OSCAL lane. |
| Truth line | Three newly discovered checks have no manifest classification. Add truthful classes and declared live-wait limits; verify complete discovery coverage. |
| Twin cage | Configured local-clock sandbox has no measured live resistance to a rebuilt child environment. Preserve that limit; missing manifest coverage currently makes its LIMIT grade FAIL. |

Root owns isolated platform repairs; Spec owns isolated hub runtime/fixture/manifest causes; Cloud owns DW's moved-path fixture after its final pointer; Standards owns separate LU/TU scenario-contract and insurer missing-total maintenance after LU final delivery. The scenario wording pre-read corrected the initial assumption that its consequence was still unpriced: the existing notes explicitly declare priced grade3 valuation/loss and unpriced grade5 mitigation, so documentation must not fabricate a missing consequence price to satisfy the old substring assertion. Exact original red evidence remains unchanged. Current scheduled adopter drift samples are still Oct3 composedv3/policy5, and run377 step4 is SKIP; no qualified new-source PolicyReport baseline was established.
