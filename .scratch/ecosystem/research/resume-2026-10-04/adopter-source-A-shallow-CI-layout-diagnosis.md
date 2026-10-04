# Source A remote CI checkout diagnosis

Read-only diagnosis of Driftwood run 37194894879 and Ludlow run 37194894912 at reviewed source heads eac40457 and 926d6b38. Publication remains held pending the narrow checkout correction and actual CI success.

Both adopters' `shift-left.yml` compose-check own-repository checkouts omit `fetch-depth: 0`. GitHub therefore supplies a depth-one checkout without the historical apps tag. Tuppence already fetches full history. `RealCompilerLayout` uses the real adopter checkout selected by `PAVF_REAL_ESTATE`; it does not copy a fixture. The previous relocated replay retained a complete `.git`, so it did not test this checkout boundary.

The immediate refusal is native CVE inventory provenance: authentic tools 5 `wargamer/inventory.py:56` requires `refs/tags/v3.0.1^{commit}` to resolve to the declared apps commit. That tag is absent in the shallow source checkout. `compose/composition.py:3694` preserves the missing-instrument refusal. The test at `tests/test_platform_tools.py:147` displays only stderr, although the compiler emits its refusal document on stdout, explaining the empty remote assertion detail.

Disposable local shallow/no-tag and full-history clones of each identical reviewed source head reproduce the distinction with the independently authenticated 703eff6 composer: shallow exits 1 with the missing apps-tag refusal; full exits 0 without refusals. Evidence is `adopter-source-A-shallow-CI-layout-diagnosis.json`. The normal wrapper encountered a local Sigstore cache-lock denial; that separate limitation is preserved in `adopter-source-A-shallow-CI-layout-wrapper-cache-limit.json` and is not described as a verified wrapper pass.

Correct both own-adopter job checkouts in Driftwood and Ludlow to `fetch-depth: 0`, add the existing Tuppence workflow-contract regression pattern, and include stdout in failed subprocess diagnostics. Preserve inventory/tag verification and all production refusal guards. Root additionally confirmed the main shift-left job has the same shallow own-checkout defect and should receive the same correction. No product source changes or external actions were made by this reviewer.
