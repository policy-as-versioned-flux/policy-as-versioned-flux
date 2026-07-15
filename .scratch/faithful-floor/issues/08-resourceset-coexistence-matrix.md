# 08 — ResourceSet coexistence matrix on cluster1

**What to build:** The crux (PRD §6.4, ADR-0005): a single `ResourceSet` input carrying one nested `{version, commit}` array, whose templates `range` over it to generate a per-version `GitRepository` + `Kustomization` pair — the array element setting `spec.ref.tag`, `spec.ref.commit`, and (via `postBuild.substitute`) the policy bundle's self-selector label value, so tag and selector cannot drift ("one semver string, three authors"). `cluster1` runs all three versions simultaneously; workloads pinned to different versions are each judged by their own version only.

**Blocked by:** 06 — Single-version consumption, 07 — 2.0.0 + 2.1.1 releases.

**Status:** done -- full 3-version live proof completed 2026-07-15, see Comments

- [x] Three policy versions live side by side on `cluster1`, all objects collision-free via nameSuffix
- [x] Workloads labelled `1.0.0`, `2.0.0`, `2.2.0` are each judged only by their pinned version (a workload compliant under 1.0.0 but not 2.0.0 admits when pinned to 1.0.0)
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

**2026-07-15: full proof completed, live.** With the user back at a keyboard for the gitsign
OAuth step, cut the three tags this ticket had prepared for: `v1.0.3`/`v2.0.3` (patch, zero
verdict impact, matchConditions fix only, content otherwise identical to the `1.0.x`/`2.0.x`
lines) and `v2.2.0` (real content release: the same fix plus issue 17's cloud policies, retiring
the `v2.1.1` line). (`v1.0.2`/`v2.0.2` exist too but are skipped in the fleet array -- their
commits, built via `git worktree` from a detached HEAD, were never reachable from any branch,
which Flux's go-git fetch-by-tag requires; root-caused live by deleting/restoring a fix branch and
watching resolution break/recover identically each time -- a documented Flux/go-git limitation
(`fluxcd/source-controller#1166`), not a broken tag. `v1.0.3`/`v2.0.3`'s commits keep a permanent
`release-pins/vX` branch ref in the policy repo for this reason -- load-bearing, not cleanup
candidates.)

`fleet/clusters/cluster1/policy-versions.yaml` repointed at the three fixed tags (PR #7, merged).
Discovered live that `policy-versions.yaml`/`bootstrap.yaml` are one-shot `kubectl apply`d by
`up.sh`, not continuously Flux-reconciled -- re-applied both directly (the same command `up.sh`
itself uses) to actually push the change to the live cluster, not just merge it to git.

`./verify-coexistence.sh` (updated for `2.2.0`, was hardcoded to the retired `2.1.1`) now passes
fully and lives: all 7 ValidatingPolicies present and collision-free, every generated Kustomization
`dependsOn: kyverno` + `wait: true`, and the differential proof -- the identical missing-department
Pod shape pinned to `1.0.0` (still Audit there) admits, the same shape pinned to `2.0.0` (promoted
to Deny) is refused, live and simultaneous on the same cluster. Prune-on-array-removal and
reinstall-on-re-add also proven live in the same run.

Also built for this ticket, already working: `app2`/`app3` (pinned 2.0.0/2.2.0) in the `apps`
repo, `fleet/verify-coexistence.sh` (collision-freedom, `dependsOn`/`wait` on every generated
Kustomization, prune-on-removal -- all passing now; the differential cross-version admission check
is the one still blocked).
