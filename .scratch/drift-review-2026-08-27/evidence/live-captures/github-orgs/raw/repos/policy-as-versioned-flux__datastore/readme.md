# datastore

The datastore team's repo. Real-estate epic, ticket 08 — this team requests cloud infrastructure
by committing Crossplane claims here, under its own policy version (`2.2.0`), instead of the
platform planting exemplar resources on its behalf (the pattern `fleet`'s
`infrastructure/c2p/cloud-exemplars.yaml` used before this ticket).

`claims.yaml` carries an S3 bucket encryption claim (compliant by construction — sc-28 is a Deny
gate, a non-compliant one can never exist on-cluster) and two RDS instance claims, one
Multi-AZ-compliant and one not (cp-10 is Audit, both states legitimately coexist) — giving the
OSCAL panel a real, attributable finding.

No container image — this team's "workload" is its cloud claims, reconciled straight from this
repo via Flux, same as every other team's own reconcile cadence.
