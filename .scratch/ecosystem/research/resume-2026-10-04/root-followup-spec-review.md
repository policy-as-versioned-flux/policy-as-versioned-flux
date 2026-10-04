# Root followup Spec review — 2026-10-04

**PASS: no actionable finding** in `5bc47331a536476f3580542be794908f5053f816`, relative to `6ed89616d7d43dece00b5daa8f0a03c56b53d5e7`. The three source SHA256s match the recorded date-regression evidence; full values are in the companion JSON.

Issue144 requires signed dated FX when USD figures are reported in GBP. The helper now requires a real calendar `party.size.as_of` and an FX period equal to its month. Missing, invalid and mismatched dates raise `MissingInstrument`. Actual adopter wrappers map this to `CannotLook`/exit3. The exact signed tag/commit checks remain in place; no rate, zero or accepted money is invented. Native-currency behavior is retained.

The ADR0026 fixture changes only its copied party when real inventory is absent, removing the unrelated legacy CVE edge. Genuine inventory layouts retain it. Its public-composer negative regression restores that real edge and proves missing inventory still refuses. Production missing-instrument rules are unchanged.

Validation evidence: meaningful valuation red6→green7; root CI-style mypy passes205 files; independently exercised old-isolated and new-native fixture layouts each pass27 cases. Unchanged checks were not repeated.

An independent scan of207 committed source/Oct4 receipt files found no high-confidence token, private-key, credential-URL or JWT matches. Public signatures, author identity and masked Actions values remain provenance. Current claims distinguish completed authentic foundation releases from pending corrected-hub/adopter delivery, preserve the live coverage-floor refusal and explicitly quarantine the invalid Ludlow conversion as negative evidence.

December2025 HMRC evidence requires a separately reviewed genuine FX2 release. Corrected published hub pinning, actual producer replay and fresh exact-head adopter review remain outstanding; this review supplies no overall CI or live-admission claim.
