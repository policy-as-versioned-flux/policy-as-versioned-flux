# 16 — Flux rescoped and verified at the cluster

Type: grilling (HITL)
Status: open
Blocked by: none

## Question

Two linked questions. The Flux test, re-scoped: can a publisher's signed, pinned policy be proven in force inside a consumer org, continuously, across an org boundary? Design the measurement and its pre-registration. Cluster-side verification: a verifying step at the cluster boundary, either a controller or the mo-07 OpenPGP dual-signing bridge so `GitRepository.spec.verify` bites, time-boxed until Flux ships gitsign. Also: wire `gitops/platform` into each adopter's reconcile so the ResourceSet fan-out reconciles for the first time, and make the composed set the thing it installs.

## Notes

Re-grills 1, 18; findings H6-01, H6-02, H9-01, H9-09, H9-10.
