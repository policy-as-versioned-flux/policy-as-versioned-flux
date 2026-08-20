# 01 — Sweep every verify script for checks that pass by not looking

Type: task
Status: open
Blocked by: none

## Question

Two gates have been found that report green without verifying anything. Are there more, and what
does the honest pass count become once they are fixed?

**Confirmed instances:**

1. `estate/tuppence/reset/verify-reach-secrets.sh:50` — enters its live tail if the namespace and
   deployment merely *exist*, never checking its actual prerequisite (the posture layer). Result:
   **PASS when the cluster is absent**, FAIL when the cluster is present-but-incomplete. Green when
   it can see least. Contrast `estate/platform/posture/verify-posture-projection.sh:71`, which
   correctly gates on `kubectl get mutatingpolicy stamp-posture`.
2. `estate/platform/identity/verify-identity.sh:56` — asserts
   `global.caName == "SPIRE"`. In Istio 1.24 `caName` is only ever tested against
   `GkeWorkloadCertificate`; "SPIRE" is a no-op. The check has been green while verifying nothing.

3. `estate/platform/wardley/wardley.py`'s `selfcheck()` asserts `credential-stuffing-aas` "must not
   signal (no movement)" — but that component has `base_risk: null`, and `forward_signal()` skips any
   component without a `base_risk` *before* it ever considers movement. The assertion would pass even
   if the component did move. It cannot fail for the reason it claims to test. (Found by the
   scenario-slate research, which supplies a replacement control case carrying a real `base_risk`.)

**The job:** audit all 29 `verify-*.sh` for this bug class and fix them —
- a live section whose guard doesn't test its own prerequisite (should SKIP, not silently pass);
- an assertion on a value that cannot fail, or that the target system ignores;
- anything where "cluster unreachable" and "check passed" are indistinguishable in the output.

Re-derive the true baseline pass/fail count afterwards and record it. This runs **first** because it
changes what "green" means for every other ticket on this map.

This is the most on-thesis bug class in the estate: it argues governance tools lie by showing green
ticks, and then shipped two of them.
