# Normal dispatch commands for root — 2026-10-04

These are instructions only; this reviewer did not dispatch any workflow. Repository: `policy-as-versioned-platform/platform`. Every cut is from the reviewed main source, never a resume branch.

```bash
gh workflow run cut-release.yml -R policy-as-versioned-platform/platform --ref main -F tags=@/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.scratch/ecosystem/patches/resume-2026-10-03/platform-cut-policy6.tags.json
```

This security6 cut is already running as reported by root (`37173718506`); do not duplicate it. After a successful clean cut and actual tag inspection, inspect whether a release verification run already exists. The normal dispatch fallback selects exact tag source:

```bash
gh workflow run release.yml -R policy-as-versioned-platform/platform --ref policy/v6.0.0 -f tag=policy/v6.0.0
```

Before reversing the preparation patch, root fetches real main/tags, verifies real6 tag/evidence/array ancestry and all frozen hashes. The reviewer's simulation is not a substitute. Reverse-check and apply only the existing five-file patch; leave authentic6 evidence and metadata in place. Deliver reviewed final7 restoration normally. Re-run publisher and engine checks against its actual committed source.

```bash
gh workflow run cut-release.yml -R policy-as-versioned-platform/platform --ref main -F tags=@/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.scratch/ecosystem/patches/resume-2026-10-03/platform-cut-policy7-tools5.tags.json
```

After that atomic cut succeeds cleanly, individually verify both signed tags and, if no verification run exists, dispatch:

```bash
gh workflow run release.yml -R policy-as-versioned-platform/platform --ref policy/v7.0.0 -f tag=policy/v7.0.0
gh workflow run release.yml -R policy-as-versioned-platform/platform --ref v5.0.0 -f tag=v5.0.0
```

Check run conclusion and actual evidence outcome independently; `passed` is required. Require correct identity/issuer, genuine annotated tags, immutable tag object hashes, same peeled commit for final7/tools5, policy7 evidence signature and version,6 metadata retention,5/6 frozen bytes and exact public release tag names/target SHAs. Do not use backfill, test mode, alternate identities, protection edits or tag replacement. CLI `gh workflow run --help` confirms `--ref` accepts a branch or tag and `-F` reads `@file` values.
