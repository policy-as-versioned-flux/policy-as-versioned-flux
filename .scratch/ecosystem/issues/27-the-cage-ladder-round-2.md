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


**2026-09-10, publication approved and completed.** The owner explicitly approved publishing
software v3.1.0 from reviewed main 332ab19. Signed cut run 34512212053 and identity-pinned release
run 34512281836 both passed. [Platform v3.1.0](https://github.com/policy-as-versioned-platform/platform/releases/tag/v3.1.0)
was published at 18:06:47Z from `332ab192e75cbeedbc072aba6a07726c070a5a61`.
No policy definition or monetary threshold changed; publication does not close the other
portions of this ticket or imply adoption by a compiler pin still naming v3.0.0.


## Partial decision — drop the warn rung, 2026-10-18

Under ADR-0025's delegated architecture authority, choose the original Question's **drop the
word** alternative: Audit is a reported observation that moves no tier, not a selectable cage
rung. The priced runtime choices remain baseline, restricted, quarantine and isolated; infra
remains a platform role outside priced selection. An unpriced or no-cage warn rung would
contradict the existing everything-is-caged model without adding a distinct enforcement
envelope. The four priced rungs already express the runtime choices.

This matches the published platform source
`a27c83b9773e147feff55312b87da90155b8a268`: `graded/cage.py` blob
`21361d41006b34c45b2a267d21fdaf2f23c1e888` defines `ORDER` as those four priced rungs,
`TIERS` includes infra and `LADDER` is `ORDER + ["infra"]`. This is source inspection, not a new
runtime or test result.
FAIR's separate single-state input named `warn` retains its meaning; it is not a cage rung.

Only this choice is decided. Status stays open for the claim-preserving de-posture tier move,
legacy access retirement and authentic per-organisation break-glass/assurance bands, with the
identity shelf retained. The delivered floor comparison remains counterfactual evidence, not
an enacted Namespace move or completion of this ticket's talk/verify-all.sh criterion. The
currency controller's separately accepted re-cage and retired-claim semantics are unchanged.
No new price, threshold, grade, policy, release or runtime observation follows from this note.
