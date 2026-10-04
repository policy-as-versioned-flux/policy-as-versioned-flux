# Handbook unpriced-regime fix — 2026-10-03

The authentic apps3.0.1 Driftwood inventory exposes scanned CVEs outside its pinned KEV feed. Composition correctly records that CVE line with `amount: null`, an absent exposure total, and its pricing reason. The handbook formatted every exposure regime through its strict money formatter, so that legitimate absence crashed the entire composition.

Only `compose/handbook.py` and new `compose/test_handbook_unpriced.py` changed. Null or missing regime amounts now render **unpriced (section 6)** and name `exposure.regimes[i].amount` as absent. Regime identity and control count remain visible. The money formatter stays strict: a measured zero remains monetary zero, and a present nonnumeric amount remains refused. No amount is invented.

TDD: the public render regression went red for explicit-null and missing amounts with the same `_money(None)` exception as the original Driftwood compose call. After the fix, all 3 regression tests / 4 cases and 58 existing handbook selfchecks passed. Focused mypy passed for both files. The original in-memory Driftwood compose now returns composed; its CVE regime remains null/unpriced and its exposure total remains absent.

`platform-handbook-unpriced-only.patch` contains only this fix and its tests. Its forward check passes against the reviewed security6 delivery head, and its reverse check passes against the updated original tree. No patch was applied to `.estate-publish/platform`: that checkout remains clean at signed reviewed head `9ddd6a2d050f421d7121225b4b5c68a8a753d513`. Root coordinates the eventual signed source update and exact-head re-review. No external action occurred.

Evidence: `handbook-unpriced-original-red.log`, `handbook-unpriced-original-green.json`, and `handbook-unpriced-fix-checkpoint.json`. The temporary before-file was removed after patch validation; no diagnostic instrumentation was introduced.
