# C2P `result2oscal` collection job — real cloud-plane NIST evidence (ticket 20)

The **real** Compliance-to-Policy (C2P) collection job for ADR-0009's "measurable /
controls-satisfied" pillar. Its sibling `../c2p-validatingpolicy-oscal/` was the *mechanism*
spike (toy policies, proved C2P consumes CEL `ValidatingPolicy` reports at all — risk-retired).
**This** directory runs the job over the project's **real** policy content and adds the
independent schema validation the mechanism spike skipped.

> One-line thesis check: the same versioned Kyverno engine that judges both planes at admission
> emits PolicyReports; C2P `result2oscal` turns those into an OSCAL assessment-results document.
> **No second validation engine.**

## Run it

```sh
./run.sh          # ~5-8 min cold: KiND up, Kyverno, policies, C2P build, 2 collection passes, teardown
KEEP=1 ./run.sh   # leave the cluster up for inspection
```

Prereqs: `docker, kind, kubectl, helm, go (>=1.24), jq, git, python3`. Regenerable from nothing —
every run does `kind create cluster` from scratch and depends on no pre-existing state (ticket 20
checklist item 3). Outputs land in `.work/out-compliant.json` and `.work/out-violations.json`.

## What it proves (ticket 20 checklist)

For **one compliant + one non-compliant resource per plane**, two collection passes show each
mapped control flipping state:

| Pass | Fixtures on-cluster | sc-28 (S3 enc.) | cp-10 (RDS multi-AZ) | cm-8 (team label, *illustrative*) |
|---|---|---|---|---|
| **1 — compliant** | `*-pass` only | satisfied | satisfied | satisfied |
| **2 — violations** | `*-pass` + `*-fail` | **not-satisfied** | **not-satisfied** | **not-satisfied** |

Each output is validated **two independent ways** (checklist item 2):

1. **C2P built-in** — `result2oscal` self-validates the OSCAL (compliance-trestle, Go) before it
   writes the file.
2. **Independent** — `check-jsonschema` (Python, `jsonschema` library) against the **official
   `usnistgov/OSCAL` v1.1.3 assessment-results JSON Schema** fetched from the OSCAL release assets.
   Different language, different codebase, different schema provenance — not "run C2P twice". This
   is the half the mechanism spike did not do.

## HONEST SCOPING — which controls are real, which is illustrative

This matters more than the tests passing (project ethos: ADR-0006, `pavf-policy/ADVISORY-METADATA.md`
— never fabricate, document the real boundary).

- **`sc-28` and `cp-10` are the REAL, load-bearing compliance evidence.** They come from the two
  real cloud-plane policies and their rationale docs:
  - `require-s3-bucket-encryption` → **sc-28** (Protection of Information at Rest) — from
    `pavf-policy/rationale/require-s3-bucket-encryption/rationale.md`.
  - `require-rds-multi-az` → **cp-10** (Information System Recovery and Reconstitution) — from
    `pavf-policy/rationale/require-rds-multi-az/rationale.md`.
- **`cm-8` (workload `require-team-label`) is ILLUSTRATIVE ONLY.** It exists purely to prove the C2P
  mechanism is **plane-agnostic** (a Pod-scoped VP flows into OSCAL exactly like a CR-scoped one).
  The **three real workload-plane policies deliberately carry no NIST mapping** — they are internal
  governance / cost-attribution concerns, not formally-mapped security controls. Attaching a NIST
  control to real workload content would be a fabrication this project explicitly guards against, so
  the workload demonstration uses the mechanism spike's **toy** policy, and its cm-8 mapping is
  labelled illustrative everywhere (component-definition remarks, policy header, this table).

## The Deny-gate → Audit demonstration choice (sc-28)

In production `require-s3-bucket-encryption` is a **Deny gate**. A Deny gate is **pass-only by
construction** for OSCAL evidence: a non-compliant bucket is *rejected at admission*, never
persists, never produces a failing report — so sc-28 could only ever read `satisfied`. ADR-0009
states exactly this and says "the not-satisfied path is always demonstrated on the Audit tier."

To exercise C2P's not-satisfied code path **for sc-28**, this spike runs that one policy in **Audit**
(the change is called out in `policies/cloud-s3-encryption.yaml`). The C2P *mapping* mechanism
(sc-28 ↔ policy name; satisfied when all pass, not-satisfied when any fail) is byte-identical under
Deny or Audit — only whether a failing report ever exists differs. `cp-10` (RDS multi-AZ) is an
Audit lane-keeper in production too, so it needs no change and is the faithful not-satisfied path.

## Version pins & where they live

All pins are at the top of `run.sh` (checklist item 4):

| Thing | Pin | Authority |
|---|---|---|
| Kyverno | chart **3.8.2** == app **1.18.2** | must match `pavf-fleet/infrastructure/kyverno/helmrelease.yaml` |
| C2P | **v2.0.0-rc.1**, built from source | ADR-0009 "pin the v2 rc and vendor the kyverno-plugin binary" |
| OSCAL schema | **v1.1.3** assessment-results | matches the `oscal-version` C2P emits |
| check-jsonschema | **0.37.4** | independent validator |

### Report-API shape dependency (checklist item 4)

Kyverno has shipped its PolicyReport CRD under **`wgpolicyk8s.io`** (long-standing) and the newer
**`openreports.io`**. C2P's kyverno-plugin reads `wgpolicyk8s.io`. The pinned Kyverno (1.18.2)
emits **only** `wgpolicyk8s.io` — confirmed empirically on the running cluster (`kubectl
api-resources` shows the `wgpolicyk8s.io/v1alpha2 PolicyReport` group and **no** `openreports.io`
group). The assumption is documented **as a comment in `run.sh`** right next to the `REPORT_GROUP`
pin and the single `kubectl get` line in `collect()` (not just here in prose). The job is
self-checking — if that group ever stopped carrying results, collect() would capture 0 subjects —
and that `kubectl get` line is the one place to change if a future Kyverno makes `openreports.io`
primary.

## The collection shim (declarative jq, ADR-0009)

`collect()` in `run.sh` carries the two normalizations ADR-0009 specifies:
1. **`.scope` → `results[].resources`** — Kyverno ≥1.18 emits per-resource reports with the subject
   in `.scope` and `results[].resources = null`; C2P reads subjects from `results[].resources`.
   Without this, subjects captured = 0 and every in-scope control false-negatives (the mechanism
   spike proved this precisely).
2. **version-suffix strip on `results[].policy`** — the coexistence build deploys VPs as
   `<policy>-<x.y.z>`; strip the trailing `-SEMVER` so the name equals the component-definition
   `Check_Id`. A **no-op here** (this spike deploys unsuffixed names) but present because it is the
   exact strip the production collection job carries.

## What is NOT here — still gated on ticket 19

This is a **self-contained throwaway KiND spike** (own `kind create cluster`, `kubectl apply` of the
policy YAMLs directly), the same accepted pattern as the sibling mechanism spike. It is **not** the
production path. Wiring the real cloud policies into the live, Flux-GitOps-reconciled `fleet` cluster
as first-class versioned entries — which must only ever run **signed, tagged** content (ADR-0001:
"signed git tags are the transport") — is **ticket 19's** job and remains correctly blocked (it needs
a new gitsign-signed policy release). Likewise the **CRDs here are minimal schema-permissive
stand-ins** (`crds/`), not the real Upbound provider-family packages that ticket 18 installs via Flux.
The C2P collection artifacts (component-definition, collection shim, independent schema validation)
built here are what ticket 20 owns; they are ready for ticket 19 to wire into the real cluster once
its signing blocker clears.

## Files

```
run.sh                       the job (pins at top; shim + report-API comment inside collect())
component-definition.json    controls -> policy names (sc-28, cp-10 real; cm-8 illustrative)
policies/                    the 2 real cloud VPs (S3 Deny->Audit for demo) + toy workload VP
fixtures/pass/               compliant: bucket-pass, instance-pass, pod-good
fixtures/fail/               non-compliant: bucket-fail, instance-fail, pod-bad
crds/                        stand-in Crossplane CRDs + Kyverno cloud-CR RBAC
.work/                       (gitignored) built C2P, venv, schema cache, generated OSCAL
```
