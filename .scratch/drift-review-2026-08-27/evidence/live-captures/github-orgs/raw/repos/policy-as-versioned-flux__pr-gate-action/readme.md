# pr-gate-action

Composite GitHub Action: verifies a policy-version bump PR before merge. Extracted from the
`fleet` repo (ticket 03 of the real-estate epic,
`policy-as-versioned-flux/policy-as-versioned-flux` hub, `.scratch/real-estate/issues/03-extract-pr-gate-action.md`)
so the gate that verifies pins is itself a pinned, versioned dependency — the extraction pattern's
first instance, and philosophically on-thesis.

For every `{version, tag, commit}` entry in the incoming `clusters/cluster1/policy-versions.yaml`:

1. `gitsign verify-tag`, identity-pinned, offline Rekor bundle.
2. The tag still resolves to the claimed commit (catches a force-moved tag).
3. `kyverno test` runs green against that commit's own fixtures.
4. `flux build --dry-run` renders the incoming manifests, diffed against the base ref's pin.
5. The rendered content's own `mycompany.com/policy-version` label equals the array's declared
   `version` — rendered content, not the tag string, so CI-only-fix patches (version != tag by
   design) stay valid.

## Usage

```yaml
- uses: policy-as-versioned-flux/pr-gate-action@<sha> # vX.Y.Z
  with:
    base-ref: origin/${{ github.base_ref }}
    head-ref: ${{ github.event.pull_request.head.sha }}
```

Requires the calling workflow to have checked out the repo (`fetch-depth: 0`) before this step —
the action reads `clusters/cluster1/policy-versions.yaml` out of the caller's own checkout, not
its own.

## Self-check

`./verify.sh` — proves the extracted logic still works standalone: a clean pass against a real
signed tag from the real policy repo, and rejection of a synthetic declared-version mismatch (the
same proof pattern the original fleet-local gate established). Requires the pinned toolchain
(`gitsign`, `kyverno`, `flux`, `jq`, `yq`) on `PATH` — see `action.yml`'s install step for exact
pinned versions; skips (not fails) if `gitsign` isn't present, so it degrades gracefully outside CI.
