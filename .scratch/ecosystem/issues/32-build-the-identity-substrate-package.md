# 32 — Build the identity substrate package

Type: task (AFK)
Status: resolved
Blocked by: 09, 12

## Question

Publish SPIRE, Istio, OpenBao, Pomerium (pinned 34.0.1) and the two ClusterSPIFFEIDs as one self-versioned gitsign-tagged implementations package with control claims; change the posture SVID template to `/posture/<version>/cage/<tier>/ns/<ns>/sa/<sa>` reading the 09-rendered tier label; fix the spire-agent trust-bundle CrashLoop (confirm root cause first) and make the currency controller fail loudly on a missing ResourceSet; wire verifiers into verify-all.sh.

## Notes

Graduated 2026-08-28 from ticket 12's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.

## Answer

Built 2026-08-29 by the /implement run of 2026-08-28 to 29. The identity substrate ships as a self-versioned implementations package. One trust domain per party that runs a cluster, federated pairwise and declared on the party artefact. The SVID path carries the cage tier from the one rendered label. The OpenBao JWKS claim was false for 27 days (a Job pointed at an http URL on a 443-only Service, and separately passed bound_claims as a string); it is now true and asserted.

Definition of done: its check is in `talk/verify-all.sh`. The run that recorded it is the TRUTH line of 2026-08-29.

> **Correction, 2026-09-06 (eco-system ticket 80 item 1).** The done-line above cites "the TRUTH
> line of 2026-08-29" as proof this ticket's check is in the gate. That citation is withdrawn.
> The line is run 7, `hub=918022b`, recorded at 2026-08-29T12:03Z, and `git ls-tree -r 918022b`
> carries three verify directories -- `verify/party/`, `verify/proportionality/` and
> `verify/provenance/` -- and none of the checks this ticket names. It was graded BEFORE the
> build it is offered as proof of, so it recorded nothing at all about this check. What this
> check actually rests on is whichever later run first discovered it, which the gate names for
> itself on every run. `verify/cited-truth/` grades this rule from today and refuses the next
> citation of a measurement that did not measure the thing.
