# 32 — Build the identity substrate package

Type: task (AFK)
Status: open
Blocked by: 09, 12

## Question

Publish SPIRE, Istio, OpenBao, Pomerium (pinned 34.0.1) and the two ClusterSPIFFEIDs as one self-versioned gitsign-tagged implementations package with control claims; change the posture SVID template to `/posture/<version>/cage/<tier>/ns/<ns>/sa/<sa>` reading the 09-rendered tier label; fix the spire-agent trust-bundle CrashLoop (confirm root cause first) and make the currency controller fail loudly on a missing ResourceSet; wire verifiers into verify-all.sh.

## Notes

Graduated 2026-08-28 from ticket 12's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.
