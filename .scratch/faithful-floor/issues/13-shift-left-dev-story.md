# 13 — Shift-left dev story (usable)

**What to build:** The **usable** "-able" (PRD §6.9), with no bespoke tooling: documented native-CLI flows by which a developer reproduces the cluster's admission verdict on their laptop against the same pinned policy versions the cluster runs — `flux build … --dry-run | kyverno apply`, `kyverno test`, `flux diff` for PR preview, `gitsign verify` for provenance — and the in-cluster SSA dry-run behaviour explained. The 2022 bash/Docker checker stays deleted.

**Blocked by:** 06 — Single-version consumption.

**Status:** done

- [x] Following the doc verbatim on a clean laptop reproduces the same admit/deny verdict the cluster gives for a sample workload
- [x] The flow uses only native CLIs — no wrapper scripts
- [x] CI runs the same commands, so laptop and CI cannot drift

## Comments

Done 2026-07-14. `docs/shift-left-dev-workflow.md`: clone at the pinned tag, `gitsign verify-tag`
(reusing issue 04's tag-flattening fix), `./verify.sh` (`kyverno test` fixtures), `flux build
--dry-run`/`kustomize build` to see the rendered manifest, and the key step -- `kyverno apply
<rendered-policy> --resource=<sample-workload>` to reproduce the admission verdict entirely
offline. `flux diff` documented separately since it's the one step that genuinely needs live
cluster access (it's a diff against what's actually running, not an offline render).

Ran the whole doc verbatim from a clean clone in `/tmp` -- every step worked exactly as written.
Cross-checked the offline `kyverno apply` verdict against the live `cluster1` for both a failing
and a passing sample workload: identical verdict, identical message, both ways.

"CI runs the same commands" isn't just asserted -- the doc explicitly cross-references
`policy/.github/workflows/release.yml` (issue 04) and `fleet/pr-gate-check.sh` (issue 12), which
call the exact same `kyverno test`/`gitsign verify-tag`/`flux build --dry-run` invocations this
doc walks through by hand, not a parallel/divergent implementation.

Named the one thing this flow can't reach: the shared-Kyverno-webhook bug issue 08 found only
manifests with multiple policy versions installed simultaneously, which `kyverno apply`'s offline
single-policy evaluation has no way to reproduce (that's what `fleet/verify-coexistence.sh` is
for).
