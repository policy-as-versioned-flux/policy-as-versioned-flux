# 25 — Build the £ seam

Type: task (AFK)
Status: resolved
Blocked by: 08, 21

## Question

Make ticket 08 real. Add the `forward-intel` payload schema to `platform/feeds/`. Make the twin emit one signed forward-intel feed for one adopter from that adopter's repo. Add a `source: twin` pricing parent edge in `composition.py`, so `prices[]` gains a twin entry with `perspective` and `currency`. Move `appetite` onto each adopter's `party.yaml` and retire `platform/risk/appetite.json`. Publish `selection-policy` v1 in one adopter and pin it. Add `tail` to `fair.summarize()` and dispatch a lognormal-GPD `lm` to `twin/severity.py`. Definition of done: a `verify-pound-seam.sh` that the gate discovers, which checks the twin entry, the labels, the policy pin and the tail field, and fails if any sum crosses perspectives.

## Notes

ADR-0021. Findings H3-01, H1-13, H3-10, H1-10. GAPS 0.3, 0.4, 1.13, 3.16.

## Answer

Built 2026-08-29 by the /implement run of 2026-08-28 to 29. The pound seam is real. One prices[] schema pass: perspective, currency, source, kind and a per-customer restatement on every entry, the regime entry partitioned into per-hole amounts from ico v3 weights. The twin emits forward-intel from the adopter repo and composition consumes it as a source: twin edge. fair.py reports its tail and dispatches a lognormal-GPD severity spec. Appetite is a signed fact on each party.yaml; platform/risk/appetite.json is retired. FX is a signed feed and a missing rate refuses as a missing instrument. verify/pound-seam/ grades it and fails any sum that crosses perspectives.

Definition of done: its check is in `talk/verify-all.sh`. The run that recorded it is the TRUTH line of 2026-08-29.
