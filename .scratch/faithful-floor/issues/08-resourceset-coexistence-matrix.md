# 08 — ResourceSet coexistence matrix on cluster1

**What to build:** The crux (PRD §6.4, ADR-0005): a single `ResourceSet` input carrying one nested `{version, commit}` array, whose templates `range` over it to generate a per-version `GitRepository` + `Kustomization` pair — the array element setting `spec.ref.tag`, `spec.ref.commit`, and (via `postBuild.substitute`) the policy bundle's self-selector label value, so tag and selector cannot drift ("one semver string, three authors"). `cluster1` runs all three versions simultaneously; workloads pinned to different versions are each judged by their own version only.

**Blocked by:** 06 — Single-version consumption, 07 — 2.0.0 + 2.1.1 releases.

**Status:** ready-for-agent

- [x] Three policy versions live side by side on `cluster1`, all objects collision-free via nameSuffix
- [ ] Workloads labelled `1.0.0`, `2.0.0`, `2.1.1` are each judged only by their pinned version (a workload compliant under 1.0.0 but not 2.0.0 admits when pinned to 1.0.0) -- **mechanism fixed and proven for a single version in isolation; full 3-version live proof blocked on new signed tags, see Comments**
- [x] Adding a version to the array is the only change needed to install it; removing it uninstalls (prune)
- [x] Every per-version Kustomization `dependsOn` the engine and gates on `wait`

## Comments

**Major finding, live-reproduced and root-caused 2026-07-14:** the design this ticket (and PRD
§6.4 point 3, and CONTEXT.md's "version self-scoping") specifies -- each `ValidatingPolicy`
self-scopes via `matchConstraints.objectSelector` on the `mycompany.com/policy-version` label --
does not actually work for coexistence. Kyverno's admission-controller flattens EVERY installed
ValidatingPolicy's `objectSelector` into ONE shared Kubernetes `ValidatingWebhookConfiguration`
(confirmed against Kyverno 1.18.2 source, `pkg/controllers/webhook/validating.go`: the loop
*assigns* rather than unions each policy's selector, so the last-reconciled policy silently wins).
With 3 versions installed, only the most-recently-reconciled version's workloads were ever
evaluated by *any* policy at all -- a workload pinned to an older version was admitted
unconditionally, regardless of its content, because the outer webhook-level filter never even
called Kyverno for it. This is invisible with a single version installed (issues 02/03/04/06 never
would have caught it) and only manifests under exactly what this ticket tests.

**Fix:** replace `objectSelector` with a per-policy `matchConditions` CEL expression (evaluated
*inside* Kyverno, not flattened onto the shared webhook). Landed in the policy repo
(`policy-as-versioned-flux/policy@1466fdc`) -- see that commit's message for the full story,
including why the version is now a third hand-synced literal (can't be a kustomize substitution
target inside a CEL string) and two verify scripts that had gone stale (one still asserting the
now-removed `objectSelector`, one hardcoding "1.0.0" as if `require-department-label` were still
always the Audit example -- broken by issue 07's own Audit→Deny promotion). Proven live for a
single version in isolation (`policy/verify-live.sh`, all 3 current-tree policies, green).

**What's blocked:** `v1.0.0`/`v1.0.1`/`v2.0.0`/`v2.0.1`/`v2.1.1` are already tagged and immutable
with the broken `objectSelector` pattern baked in -- Flux's continuous reconciliation actively
*reverts* any live hand-patch back to that broken content within a minute, confirmed live (a
manually-patched `require-known-department-label-2.0.0` silently reverted and
`verify-coexistence.sh`'s differential-admission check started failing again). Full proof of "3
versions coexist correctly" needs 3 new patch tags with zero policy-content change (this fix has
no verdict impact by construction) -- prepared, not yet cut:
- `v1.0.2` (content-identical to `v1.0.0`/`v1.0.1` except the matchConditions fix)
- `v2.0.2` (content-identical to `v2.0.0`/`v2.0.1` except the fix)
- `v2.1.2` (same commit already queued for issue 07's release-notes fix, now also carries this)

Blocked on a fresh gitsign OAuth login (the credential cache from issue 04 expired mid-session;
the user asked to pause rather than retry blind, and is currently AFK). `fleet`'s `ResourceSet`
(`clusters/cluster1/policy-versions.yaml`) is ready to repoint at these tags the moment they exist
-- just new `commit` SHAs in the existing `versions` array, everything else (the ranging template,
`verify-coexistence.sh`) already written and tested against the mechanism.

Also built for this ticket, already working: `app2`/`app3` (pinned 2.0.0/2.1.1) in the `apps`
repo, `fleet/verify-coexistence.sh` (collision-freedom, `dependsOn`/`wait` on every generated
Kustomization, prune-on-removal -- all passing now; the differential cross-version admission check
is the one still blocked).
