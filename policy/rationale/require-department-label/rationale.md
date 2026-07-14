# require-department-label

**Risk mitigated:** cost and ownership are unattributable — a workload with no
owning department cannot be charged back, contacted at incident time, or
included in a decommission sweep.

**Intent:** consistency-enforcing, not security-enforcing. This is lane-keeping
(`validationActions: Audit`), not a gate — most of the estate should adopt this
gradually via the versioned dependency, never blocked at admission.

**Why Audit, not Deny:** an unlabelled workload is an operational nuisance, not
"whether the workload may exist at all" (the mea-culpa's gate criterion). A hard
Deny here would repeat the opaque-gate mistake the thesis explicitly walks back.

**Disagreement:** raise a pull request against this policy (e.g. to exempt a
resource kind, or promote to Deny) — not an out-of-band exemption request.

Dated: 2026-07-14. Reviewed: 2026-07-14.
