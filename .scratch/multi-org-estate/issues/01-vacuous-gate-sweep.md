# 01 — Sweep every verify script for checks that pass by not looking

Type: task
Status: done
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
   **This one instance is delegated to the per-org forward-layer ticket**, which is already editing
   `wardley.py` and would otherwise collide with this sweep. Do not touch `wardley.py` or
   `verify-wardley.sh` here.

**The job:** audit the other 28 `verify-*.sh` (all but `verify-wardley.sh` — see above) for this bug class and fix them —
- a live section whose guard doesn't test its own prerequisite (should SKIP, not silently pass);
- an assertion on a value that cannot fail, or that the target system ignores;
- anything where "cluster unreachable" and "check passed" are indistinguishable in the output.

Re-derive the true baseline pass/fail count afterwards and record it. This runs **first** because it
changes what "green" means for every other ticket on this map.

This is the most on-thesis bug class in the estate: it argues governance tools lie by showing green
ticks, and then shipped two of them.

## Comments

Done 2026-08-20. Read all 29 `verify-*.sh` under `estate/` (the ~27 the ticket names, minus
`verify-wardley.sh`, is 29 once you count the two `verify-reconcile.sh`/`verify-catalog.sh`-style
ones the summary undercounted). Four fixes, all the same bug class:

1. **`verify-identity.sh:56`** — the confirmed no-op. `global.caName == "SPIRE"` is never read by
   Istio 1.24 outside `GkeWorkloadCertificate`. Replaced with the two settings that actually make
   SPIRE the mesh CA (both already present in `istio/helmrelease.yaml`, just never asserted):
   `pilot.env.ENABLE_CA_SERVER == "false"` (istiod's own CA off) and the `spire` sidecar-injection
   template mounting `csi.spiffe.io` at Envoy's SDS default path.
2. **`verify-reach-secrets.sh:50`** — the confirmed loose guard. Entered the live tail on ns+deploy
   existing, never checking its real prerequisite (the posture layer). Added a
   `kubectl get mutatingpolicy stamp-posture` check ahead of the ns/deploy checks, same pattern as
   `verify-posture-projection.sh:71`.
3. **`verify-access.sh`** and **`verify-identity.sh`**'s live pod/ping checks — found in the sweep,
   same class as the ticket's #2: `grep -q dex && echo ok || echo "FAIL Dex"` never actually fails,
   it only prints text; a missing pod and a present one both fall through to script exit 0. Both
   files had no `fail()` helper at all. Added one, wired the Dex/Pomerium/SPIRE/istiod/OpenBao/
   ping→pong checks through it.
4. **`verify-retirement.sh`**'s live tail — found in the sweep. The guard tested "any Kustomization
   exists" (not this beat's own retired-version Kustomization), and neither branch of the nested
   `if` ever asserted anything — present or absent, the script exits 0 either way. Rewritten as three
   honestly-labeled outcomes (still-reconciled → SKIP with reason, gone → live confirmation, no
   cluster → SKIP with reason); no branch pretends to gate when it can't.

`estate/platform/wardley/`, `wargamer.py`, `tcor.py`, and the other python `selfcheck()`s were read
where a `.sh` delegated its whole check to one, but not separately audited beyond that — the ticket
scopes this sweep to the shell gates, and ticket 14 already owns the one known python-selfcheck
vacuity (`wardley.py`'s `credential-stuffing-aas` assertion).

True baseline, re-derived: `estate/talk/verify-all.sh` (offline, no live cluster) — **25/25 PASS**,
3/3 live beats **SKIP** (no reachable `kind-*` cluster here) — 25+3 = **28**, unchanged from the
map's destination number; none of the four fixes above flip an offline beat's pass/fail, they make
the ones that were already green, green for the stated reason. Evidence:
`KUBECONFIG=<empty> bash estate/talk/verify-all.sh` → `pass=24 fail=1 skip-live=3` (the one failure,
`verify-currency.sh`'s `kubectl apply --dry-run=client` with zero kubeconfig contexts defined, is a
test-harness artifact of that empty-kubeconfig run, not a repo bug — confirmed by rerunning the same
`kubectl apply --dry-run=client -f estate/platform/currency-controller/manifests/rbac.yaml` under a
kubeconfig with any current-context set: exits 0 instantly, no network dependency for these
core-API-only manifests). All four fixed scripts individually re-run and confirmed `PASS`/SKIP-live
as intended, both under an empty kubeconfig and under one with real (unreachable) `kind-*` contexts.
