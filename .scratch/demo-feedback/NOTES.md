# Demo feedback — raw notes (show+tell, 2026-07-16)

Captured verbatim-in-substance from the narrated walkthrough. Numbering matches the order given.

1. **[org]** Consider splitting the `apps` monorepo into one repo per app (app1/app2/app3) instead of bundling all three consumer apps in one repo.
2. **[release]** The gitsign signed-message block in release notes renders as raw text — should be fenced (or otherwise handled) for readability (`release.yml`'s notes generation).
3. **[release]** Should releases carry actual build artifacts/assets (rendered bundle, checksums, SBOM?) rather than only GitHub's auto-generated source tarball?
4. **[fleet history]** Consider deleting/recreating repo(s) with clean history, squashing out the thrashing bug-fix commits now that the working config is known. *(Destructive — needs its own explicit confirmation, never bundled into other work.)*
5. **[gate]** CONFIRMED GAP: `pr-gate-check.sh` never cross-checks the fleet array's declared `version:` against what's actually baked into the fetched tag's rendered content. A PR could declare `version: "2.0.0"` pointing at content that internally says `2.2.0` and CI would pass.
6. **[gate]** Consider extracting `pr-gate-check.sh` + workflow into a separate reusable repo/GitHub Action — "too much in this repo".
7. **[governance agent]** The issue checkboxes (Yes/No/Not sure) do nothing programmatically (by design, ADR-0006), but nothing tracks/reminds follow-through either. Wants something GitHub-Action-shaped reacting to the checkboxes.
8. **[grafana]** Disable Grafana auth for demos (`auth.anonymous`).
9. **[dashboard]** Add an explicit "which policy versions does this cluster support" panel/stat, not just the implicit revision table.
10. **[dashboard]** Add an "update readiness" view: how ready is the estate to adopt a newer policy version (who's still on old versions, who would fail if bumped).
11. **[semantics]** Policies are admission-time only — retiring/updating a version never auto-stops running workloads. True and proven, but should be stated prominently; it's a natural point of confusion.
12. **[architecture]** Policy versions should have a **sunset time**. *(Tension: ADR-0006 deliberately rejects all timed/automatic policy changes.)*
13. **[renovate]** Renovate confusion resolved live (it had never actually run; only fixture dry-runs). User then **installed the Renovate GitHub App on the org during the demo** — settings at https://developer.mend.io/github/policy-as-versioned-flux/-/settings?tab=renovate. Dependency-dashboard-style visibility wanted.
14. **[apps]** Give demo apps REAL software dependencies (old Angular, log4j, etc.) so dependency scanning has real staleness signal — and build an aggregate dashboard of app-dependency staleness AND policy-version staleness together.
15. **[apps]** Replace/augment placeholder `nginx:latest` containers with real (minimal) apps on deliberately old, unpatched versions. Keep nginx as one example.
16. **[renovate vs flux]** Answered live: Flux's image-automation (auto-apply within ranges) is the opposite of this project's reviewed-PR principle; Renovate's git-refs customManager is the right tool. Now moot — app installed (see 13).

Session workflow preferences also given: background `say` calls, use `kubectx` for context switching, Grafana shouldn't need login in demos.
