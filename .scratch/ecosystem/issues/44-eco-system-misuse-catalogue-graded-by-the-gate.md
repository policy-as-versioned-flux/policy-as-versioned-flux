# 44 — Eco-system misuse catalogue graded by the gate

Type: task (AFK)
Status: open
Blocked by: 19

## Question

Add `twin/ecosystem-misuse-catalogue.yaml` (schema `twin.misuse-catalogue/v1`) with the four rows and the mechanism strings from ticket 19, a harness check that loads all three catalogues and refuses a row without a mechanism, and `verify/verify-misuse.sh` so `verify-all.sh` grades it.

## Notes

Graduated 2026-08-28 from ticket 19's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.
