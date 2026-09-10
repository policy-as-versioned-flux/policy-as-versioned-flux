# 27 — The cage ladder, round 2

Type: grilling (HITL)
Status: open
Blocked by: 09

## Question

With the grain fixed per Namespace: the warn rung (Audit findings that move nothing, or drop the word); de-posture as a tier move that keeps the claim (H2-12); access.py retirement and break-glass bands per org appetite (H8-09, H8-12); how a tier move prices against the ticket 08 prices[] entry.

## Notes

Graduated 2026-08-28 from ticket 09's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.


## Bounded implementation — floor-change evidence, 2026-09-10

Platform PR25 merged as `332ab192e75cbeedbc072aba6a07726c070a5a61` after both
independent reviews passed. Its reviewed signed commit is `70cf92d6abfa8cbae74101791752f97c42505cf7`;
the merge tree matches. The compiler now emits `composed/floor-change.json` and a handbook
comparison for a floor edit, holding the current publisher, scenario, appetite and calibration
fixed. This makes the floor's selected-tier and retained-residual effects visible without
changing the existing publisher-version price comparison or supplying monetary thresholds.

The HEADER retains the before/after floor history needed for byte-identical offline replay.
Missing historical information stays explicitly unknown; a known absent floor is distinct.
Repeated composition retains the comparison, and a subsequent floor edit starts a new one.
Nine focused public cases, 47 handbook tests and a full 32-file offline replay pass. The scoped
typecheck has the same 87 diagnostic messages and multiplicities as its baseline; it is not clean.
Release checks pass, but proposed software v3.1.0 remains unpublished pending explicit approval.

This addresses only the floor-price evidence portion. The warn rung, de-posture claim semantics,
access.py retirement and owner-sourced per-organisation break-glass bands remain open. It does
not prove a deployed tier move or resolve the whole ticket's talk/verify-all.sh criterion.
