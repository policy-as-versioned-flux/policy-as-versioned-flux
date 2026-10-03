# Feed source merge and release effects — 2026-10-03

Read-only independent audit of PR10 head `37dfe4a2de50f1a1fd7aeb6348d819373188e0e6`, against `ff3ac9ab00bdc73e1bbf83cabf91c767d35b8e88`. No merge, tag cut or workflow dispatch was performed.

The 19-path commit changes public feed payloads, offline replay corpora, schemas, bump declarations, primary-source readers and defensive validators. No workflow changes. An independent exact-blob scan found no high-confidence secrets. The CVE capture holds 1,733 public KEV/NVD/EPSS records; projected NVD fields are only `id`, `metrics`, `published`. Provenance names constant official CISA/NVD/FIRST endpoints. NVD credentials are environment-only request headers, absent from captures. FX is the authentic **August 2026** HMRC table (141 rates), not an October observation. Threat v4 carries dated, cited frequency estimates and their limitations; subscriber magnitude remains required. Nine prior payloads remain byte-identical. This is public vulnerability metadata and defensive conversion/validation code; no exploit or private customer data was identified.

| Action | Effect |
| --- | --- |
| Merge PR10 to `main` at that exact reviewed head | Makes the source and candidate payloads the public default branch. No workflow has a branch-push or pull-request trigger. Future existing daily `fetch.yml` runs use the new readers; they may append signed observations or propose PRs, and never merge or cut releases. No feed tag, GitHub Release or adopter pin follows from the merge. |
| Explicit `cut-release.yml` dispatch on `main` | Checks the declared version and gates, then creates and pushes an immutable Actions-keyless signed tag. Separate cuts: `cve/v3.0.0`, `fx/v1.1.0`, `threat-register/v4.0.0`. |
| Explicit `release.yml` dispatch per tag | Verifies the signed tag identity and offline Rekor bundle, runs gates, then publishes its GitHub Release. The cut's default Actions credential does not automatically trigger this tag-push workflow. |

PR10 is ready, and `pavc-other-hand[bot]` approved this exact head. Automatic approval review rejected **the source merge**, before execution, because trusted user content did not specifically authorize default-branch publication. The concrete unresolved scope is authorization to merge PR10 into public `policy-as-versioned-feeds/feeds:main` through the reviewed App path. The three signed cuts and three release-verification/publication dispatches are separately identifiable subsequent actions. No alternate identity or execution path was attempted.
