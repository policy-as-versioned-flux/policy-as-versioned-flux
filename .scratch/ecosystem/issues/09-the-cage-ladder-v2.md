# 09 — The cage ladder v2

Type: grilling (HITL)
Status: open
Blocked by: 08

## Question

The cage as the only enforcement, in full. The ladder gains a bottom rung below quarantine ('too expensive to run or not functional'). A MutatingPolicy defaults the strictest cage at CREATE to any pod that claims nothing; infrastructure claims an infra cage explicitly; the governed-namespace deny is replaced. The tier is declared in the adopter's signed composed artefact and rendered down to `posture.acme.io/tier`; it has a trust boundary (validating deny of an unentitled tier, mutating clobber from the priced decision, unknown label fails closed to strictest). De-posture is a tier move that keeps the claim and prices the residual. An adopter may set a tighten-only tier floor in its overlay. Loosening short of removal is priced; removal-to-nothing refuses. Warn rung: realise or drop. Access.py retired; break-glass scales by org appetite.

## Notes

Re-grills 15, 16, 23, 28; reversals 5, 11, 12, 13, 17; findings H2-01..H2-16, H8-03, H8-09, H8-12. Blocked by the £ seam because the tier's source is decided there.
