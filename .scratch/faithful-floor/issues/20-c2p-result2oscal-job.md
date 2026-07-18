# 20 — C2P result2oscal collection job → schema-valid OSCAL in CI

**What to build:** The **measurable** pillar's formal carrier (ADR-0009): a C2P component-definition mapping harvested-catalogue controls to policy names, and the collection job running `result2oscal` over the PolicyReports both planes emit — with the spike-proven jq shim normalising Kyverno ≥1.18's per-resource report shape and stripping the coexistence nameSuffix so versioned VP names match the component-definition Check_Ids. C2P pinned + vendored (pre-GA, accepted risk PRD §10). No second validation engine.

**Blocked by:** 19 — Cloud plane at admission.

**Status:** done — mechanism + real cloud-plane OSCAL evidence proven in a CI-regenerable spike; live `fleet` wiring still gated on issue 19.

- [x] For one compliant + one non-compliant resource per plane, the job emits an OSCAL assessment-results doc marking the mapped NIST control satisfied/not-satisfied
- [x] The doc passes C2P's built-in OSCAL validation plus an independent schema validator
- [x] Regenerable in CI from a fresh KiND bring-up
- [x] C2P and the shim are version-pinned; the report-API shape dependency (wgpolicyk8s vs openreports) is noted where the pin lives

## Comments

2026-07-15: Built the real collection job at `spikes/c2p-real-job/` (new dir alongside the
untouched mechanism spike `spikes/c2p-validatingpolicy-oscal/`, which it reuses the proven
scaffolding of). Ran end-to-end for real on a throwaway KiND cluster — not a dry description.
Confirmed `helm -n kyverno get metadata` → app **v1.18.2** (matches the fleet pin at
`pavf-fleet/infrastructure/kyverno/helmrelease.yaml`, chart 3.8.2).

Real, load-bearing evidence is the **cloud plane**, using the two real policies from `pavf-policy`
(copied into `spikes/c2p-real-job/policies/`, not edited in the policy repo) and their real NIST
mappings from the rationale docs:
- `require-s3-bucket-encryption` → **sc-28** (Protection of Information at Rest)
- `require-rds-multi-az` → **cp-10** (Information System Recovery and Reconstitution)

Two collection passes over the real `pavf-policy/tests` fixtures gave, verified from the emitted
OSCAL (`.work/out-compliant.json`, `.work/out-violations.json`):
- PASS 1 (only `*-pass` fixtures): `sc-28` satisfied, `cp-10` satisfied (0 findings, 3 subjects).
- PASS 2 (add `*-fail` fixtures): `sc-28_smt` → **not-satisfied**, `cp-10_smt` → **not-satisfied**
  (6 subjects). Report entries carry the real policy names verbatim
  (`policy=require-s3-bucket-encryption result=fail source=KyvernoValidatingPolicy`, etc.).

**Both validations pass** (checklist item 2): (a) C2P's built-in `result2oscal` self-validation
(Go/compliance-trestle), and (b) a genuinely independent `check-jsonschema` (Python `jsonschema`)
run against the **official `usnistgov/OSCAL` v1.1.3 assessment-results JSON Schema** — different
language, codebase, and schema provenance, not "C2P twice". The mechanism spike only did (a); (b)
is the added half. Both OSCAL docs emit `oscal-version 1.1.3`.

**Honest scoping note (matters more than the tests):** the workload plane is demonstrated with the
mechanism spike's **toy** `require-team-label` → **cm-8**, labelled *illustrative* everywhere
(component-definition remarks, policy header, README). The three real workload-plane policies
deliberately carry **no** NIST mapping (internal governance, not security controls) — inventing one
would be a fabrication this project's ethos (ADR-0006, `ADVISORY-METADATA.md`) guards against. So
the illustrative cm-8 proves only that C2P is plane-agnostic; sc-28/cp-10 are the real claims.
Also documented: `require-s3-bucket-encryption` is a **Deny gate** in production (pass-only by
construction — a denied bucket leaves no failure trail), so to exercise the sc-28 not-satisfied
path the spike runs *that one policy* in **Audit**; the C2P mapping is byte-identical either way.
This is exactly the "not-satisfied on the Audit tier" path ADR-0009's acceptance criterion relies on.

**Pins (checklist item 4):** all at the top of `run.sh` — Kyverno chart 3.8.2/app 1.18.2, C2P
`v2.0.0-rc.1` built from source, OSCAL schema v1.1.3, check-jsonschema 0.37.4. The report-API-shape
dependency is a comment right next to the `REPORT_GROUP` pin and the single `kubectl get
policyreports.wgpolicyk8s.io` line in `collect()`: the pinned Kyverno emits **only**
`wgpolicyk8s.io` (confirmed empirically — `kubectl api-resources` showed no `openreports.io` group),
which is what C2P's kyverno-plugin reads. The scope→resources + version-suffix-strip shim lives in
`collect()` too (the suffix strip is a no-op for this spike's unsuffixed names but is the strip the
production job carries).

**Still gated on issue 19 (not attempted here, correctly):** wiring these real cloud policies into
the live, Flux-GitOps-reconciled `fleet` cluster as first-class versioned entries — which must only
ever run signed, tagged content (ADR-0001) and needs a new gitsign-signed policy release. No git
tag signing, gitsign, or pushes to policy/fleet/apps/cloud were touched. The CRDs in `crds/` are
minimal schema-permissive **stand-ins**, not the real Upbound provider-family packages (those are
issue 18's Flux-installed packages). The C2P artifacts (component-definition, collection shim,
independent schema validation) this ticket owns are done and ready for issue 19 to wire in once its
signing blocker clears — same "real progress, downstream still blocked" state as issue 18.

## Follow-up (2026-07-18): the spike's own cluster isolation was silently broken, twice

A wave-1 audit found `spikes/c2p-real-job/run.sh` had leaked real writes onto the shared
`kind-cluster1` live cluster -- 3 unversioned duplicate ValidatingPolicies (one in weaker `Audit`
mode, materially different from the real `-2.2.0` Deny gate) plus 2 fixture Crossplane CRs, all
outside GitOps control, contaminating ticket 08's live OSCAL-attribution proof (the exact class of
bug that ticket's own c2p-collector fix had just closed, recurring via a different fixture). Root
cause: the script's `kubectl`/`helm` calls relied entirely on `kind create cluster` having switched
the ambient current-context, with no check that it actually had -- when that assumption broke
(however it broke), every apply landed on whatever cluster the ambient context happened to point
at instead, silently.

**Cleaned up and fixed for real.** Deleted the 5 stray live artifacts. Hardened `run.sh`: every
`kubectl`/`helm` call is now pinned via a shell-function override to this job's own
`kind-$CLUSTER` context explicitly, with a hard `exit 1` guard if that context doesn't exist after
cluster creation -- structurally impossible to touch any other cluster regardless of ambient state.
Live-verified end-to-end: ran the full spike from `kind-cluster1`'s own context, confirmed
`kubectl config current-context` was `kind-c2p-real-job` throughout, both OSCAL passes produced the
expected satisfied/not-satisfied verdicts and validated against the independent schema, the
throwaway cluster self-tore-down on exit, and `cluster1`'s own `ValidatingPolicy` set was
byte-for-byte unchanged before and after the run.

**Considered and deliberately deferred**: the same skeptic pass suggested c2p-collector's own
aggregation (real-estate ticket 08's `run.sh`) is still architecturally permissive -- it filters
`skip` results but folds in *any* resource carrying a matching `mycompany.com/policy-version`
label regardless of whether Flux actually manages it (checkable via the
`kustomize.toolkit.fluxcd.io/name` label every Flux-applied resource carries, confirmed present on
all real `datastore` exemplars and absent on every stray artifact seen so far). That's a real,
generalizable hardening -- but it requires an extra per-resource `kubectl get` lookup for every
scoped resource in the collection pipeline (the `PolicyReport.scope` field doesn't carry labels),
meaningful added complexity for a demo project where both *observed* root causes (the skip-result
gap, this spike's context leak) are now independently closed at their actual source. Left as a
known, considered opportunity for a future session rather than added speculatively for a
contamination class that no longer has a live path to occur.
