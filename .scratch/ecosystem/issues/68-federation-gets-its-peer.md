# 68 — Federation gets its peer

Type: task (AFK)
Status: open
Blocked by: none

## Question

Ticket 58 Q3(a): driftwood becomes the second SPIRE trust domain, federated pairwise with the platform domain. Add `trust_domain`, `bundle_endpoint` and `federates_with[]` to party/schema.json (a schema change, so the engine computes the bump and the release machinery cuts it), declare both domains on the two signed party.yaml files, stand up the second trust domain on driftwood's cluster, and add a verify script that grades the live bundle exchange with three outcomes, substrate-first. Done = the gate grades federation for real, or names the absent cluster as a could-not-look.

## Notes

Graduated from ticket 58 (2026-08-31), decision provisional on a bare "Agree".
