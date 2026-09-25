# 157 — Fact 2 is null on two composed sources

Type: task (AFK)
Status: open
Blocked by: none

## Question

Find why fact 2 (`fact_2_tag_signature_verified_at_the_source_boundary`) reads null on the driftwood and tuppence composed sources on 2026-09-25, why it reads null or observed FALSE on most days on all three composed sources, and why no sample looks at falsifier 2 on driftwood's `platform` and `nist` sources. Then fix the cause, or record it as a declared ceiling of the instrument.

Facts on 2026-09-25, from `drift/samples.jsonl` at driftwood `155db9e`, tuppence `5deffe6` and ludlow `b8e14f7`, one sample a day from 2026-09-11:

- `driftwood-composed`: fact 2 is null on most days and observed FALSE on 2026-09-15, 09-18, 09-20 and 09-21. It is never true.
- `tuppence-composed`: fact 2 changes between null and true. It is true on 2026-09-11, 09-12, 09-14, 09-16, 09-22 and 09-24.
- `ludlow-composed`: fact 2 is null on most days, observed FALSE on 2026-09-17, 09-21 and 09-22, and true once, on 09-25.
- driftwood: falsifier 2 has `fired: null` on `platform` and `nist`, where fact 2 is true. `grade` turns that into a SKIP ("FALSIFIER NOT LOOKED AT", ludlow `drift/five-facts.py:1484-1488`).

So there are two symptoms. A null says the signature was not looked at. An observed FALSE says a signature was not verified at the source boundary, which is a different cause. The diagnosis must explain both. Fact 7 is also null on every source, which ticket 161 fixes.

Diagnose on a lane run, not by reading the code only. A sample taken by hand is a rehearsal and is never cited (ADR-0023, D4).

## Notes

Graduated 2026-09-25 from ticket 152, Q3 and Q11. Definition of done: a scheduled sample on each adopter reads fact 2 true on each source, or observed false with its cause named, and looks at falsifier 2 wherever fact 2 is true. Or a dated paragraph in each adopter's `drift/window.yaml` records the cause as a ceiling. Wire any new check into `talk/verify-all.sh`.

Step 4 grades driftwood (`verify/e2e/verify-e2e-step4-flux-reconciles-cage.sh:46`). So ticket 152 alone cannot give step 4 a PASS. This ticket blocks ticket 151.
