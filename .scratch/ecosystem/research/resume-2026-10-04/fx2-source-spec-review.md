# FX2 exact-source Spec review — 2026-10-04

**PASS: no actionable finding** at SSH-verified clean head `d62f74e52ed992798a75cf3f4f138ec9c83db80a`, against authentic published feeds commit `974e73514e0d8d4cad2e6906acf51d1cc27028b3`. The seven-path diff adds the dated instrument and provenance; it changes no parser, converter, schema, catalogue, fetch default or workflow.

Independently replayed both complete retained HMRC CSVs through the actual unchanged publisher parser. Every resulting payload field equals its envelope and recorded hash. December has164 rows,142 currency codes, validity1–31 December2025 and USD1.3126 units per GBP1; August retains163 rows,141 codes and USD1.3367. No currency alias, projected rate or synthetic money appears.

The actual unchanged rule computes **major**, because VES is withdrawn while BGN/VED are added. The normal ladder yields2.0.0; the new envelope names `fx`, publisher `feeds`, version2.0.0 and the existing payload schema, while `bump.yaml` declares major. The catalogue already publishes the FX namespace. All12 older major bodies and the default August replay are independently byte identical to974.

The unchanged converter selects each actual month across retained major directories: Dec31 conversion passes, August remains available, and missing November2025/January2026 dates refuse. The dated offline replay is explicit and equivalent to the December payload. Dry-run output claims no new upstream clock observation.

Unmodified publisher gates are recorded PASS in `fx2-source-checks.json`; targeted independent replay, version, refusal, frozen-byte, signature and source-hash checks are in `fx2-source-spec-checks.json`. Seven changed public-data files contain no high-confidence credential/private-key matches.

This approves the exact source for the ordinary reviewed PR/release path. Authentic FX2 cut and immutable release verification remain required before consumers pin it. It approves no future tag, served adopter price or activation; corrected published hub pinning and actual producer replay remain separate prerequisites.
