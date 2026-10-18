# 157 — Fact 2 is null on two composed sources

Type: task (AFK)
Status: resolved
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

## Answer

**Local implementation, 2026-10-03.** Diagnosed from actual scheduled run logs and recorded the evidence in [drift-signature-diagnosis.md](../research/resume-2026-10-03/drift-signature-diagnosis.md). Current tuppence and ludlow fact 2 are true on every source. Driftwood sampled its composed source without an annotation soon after verifier rollout; the timeline supports a controller-cycle race, without proving every older null shares that cause. Old FALSEs explicitly named certificate notBefore versus tagger-time rejection. Added a bounded wait for any terminal signature verdict, controller reason logging, read-only publisher checkouts and source-specific CI identities/tags. Fixed unknown being collapsed into a cleared falsifier on tuppence/ludlow. Local selfchecks pass; post-change scheduled proof remains pending.

**Delivery reconciled, 2026-10-18.** The scheduled diagnosis and source repair are delivered. The October 3 Driftwood run [37120458169](https://github.com/policy-as-versioned-driftwood/driftwood/actions/runs/37120458169) sampled 17 seconds after verifier rollout inside its 60-second reconcile interval: that supports a controller-cycle race, without uniquely explaining every historical null. Earlier observed FALSE rows name certificate validity at tagger time; they are not unlooked signatures. The sampler's bounded terminal-verdict wait preserves false/unknown and logs the reason. Each publisher is checked out read-only with its own CI identity and tag; missing CI evidence remains unknown rather than a cleared falsifier. The delivered sources are [Driftwood](https://github.com/policy-as-versioned-driftwood/driftwood/blob/5a1b9a1ae85f88dfe91a71aca8eeb308349097ff/drift/five-facts.py), [Tuppence](https://github.com/policy-as-versioned-tuppence/tuppence/blob/e7e2969cd50ab3e88fa11afe61d5bee5d1db30d4/drift/five-facts.py) and [Ludlow](https://github.com/policy-as-versioned-ludlow/ludlow/blob/e65acc95bd107e0ba2864b2ca2f23b51714dc4c1/drift/five-facts.py).

The original Done predicate has subsequent genuine scheduled evidence: Driftwood [39122015854](https://github.com/policy-as-versioned-driftwood/driftwood/actions/runs/39122015854), Tuppence [39128182725](https://github.com/policy-as-versioned-tuppence/tuppence/actions/runs/39128182725) and Ludlow [39130684337](https://github.com/policy-as-versioned-ludlow/ludlow/actions/runs/39130684337) each record fact 2 true on their composed, platform and nist sources, with falsifier 2 inspected, `fired: false` and `ci_accepts: true`. The immutable original rows are in their [Driftwood](https://github.com/policy-as-versioned-driftwood/driftwood/blob/5a1b9a1ae85f88dfe91a71aca8eeb308349097ff/drift/samples.jsonl), [Tuppence](https://github.com/policy-as-versioned-tuppence/tuppence/blob/e7e2969cd50ab3e88fa11afe61d5bee5d1db30d4/drift/samples.jsonl) and [Ludlow](https://github.com/policy-as-versioned-ludlow/ludlow/blob/e65acc95bd107e0ba2864b2ca2f23b51714dc4c1/drift/samples.jsonl) trees. No ceiling alternative or hand sample is used.

The existing registered readers are `.estate-clone/driftwood/verify-reconcile.sh`, `.estate-clone/tuppence/verify-reconcile.sh` and `.estate-clone/ludlow/verify-reconcile.sh`. Their unchanged [recorded run 432 grade table](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/blob/d096cd2f0515a8aa2f9de1b671f5f227beba5478/talk/captures/_grades.tsv) has respectively PASS, SKIP and PASS; the newer scheduled evidence above does not rewrite that table. Tuppence's later fact 5 FALSE, one of 41 rendered objects missing from Flux inventory, remains a separate observed risk-joins failure. This record supplies no new cluster or whole-estate PASS.
