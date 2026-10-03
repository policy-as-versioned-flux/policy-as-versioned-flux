# Platform security6, compatibility7 and tools5 — 2026-10-03

Cut `policy/v6.0.0` from its matching security authoring intermediate, then cut `policy/v7.0.0` together with tools `v5.0.0` from restored compatibility authoring. Retain supported5.0.0 and6.0.0. The unserved6.0.1 candidate was superseded by7.0.0; exact delegated7 acceptances are present for driftwood, tuppence and ludlow, each retaining the owner's original quote. Earlier6.0.1 measurements are unchanged, and its generated corpus is archived in `historical-generated-corpus6.0.1/`.

## Proven local results

- Security6 publisher dry run: declaredmajor, computedmajor, passed. Its exact intermediate engine matrix passed5/6 on1.18.2 and machinery on1.18.2+1.19.1.
- Final7 **actual publisher gate**, retaining the full5/6 window: declaredmajor, computedmajor, passed, exit0. `platform-policy-7.0.0-full-window-dry-run.json` and its log retain the verdict.
- Final7 engine matrix: all6 declared cells passed (5/6 on1.18.2,7 and machinery on1.18.2+1.19.1), recorded in `engine-cells-policy7-final.json`.
- Renderer selfcheck, exact7 render and the three-version coexistence fixture passed. Frozen5/6 policy bytes are unchanged; hashes are in `platform-7.0.0-candidate-checkpoint.json`.
- The five-file preparation patch applies to final7 authoring. Reversal after a populated6.0.0 commit field preserves that field and restores exact final7 authoring. Both directions were checked in the isolated clone.

The clean6.0.1 proposal was not accepted: its full gate computed **major** over5.0.0+6.0.0 and would publish only `6.0.1-quarantine.1` (degraded, exit0), not clean6.0.1. That result is retained in `platform-policy-6.0.1-full-window-dry-run.json`. Comparing only6→6.0.1 had hidden the older supported line. Honest7 is the chosen clean route; retiring5 is a separate future decision after every adopter accepts and moves.

## Candidate commit requirements

First commit the reviewed final7 platform implementation, including candidate6/7 trees and fixtures, the version array, renderer, engine declarations/grader, coexistence fixture, current7 corpus and other approved tools changes. The engine grader reads a committed ref, not dirty files. Do not dispatch a release from final authoring before security6 has been cut.

Apply the patch and commit its five-path delta to form the security intermediate. It touches only `graded/policies/cage-tier.yaml`, `graded/policies/cage-netpol.yaml`, `posture/policies/stamp-posture.yaml`, `distribution/render-version-tree.py` and `distribution/versions.yaml`; other approved edits remain present. It restores alpha/untyped security authoring and the historical posture member in the renderer, and removes only the uncut7 array entry. Frozen5/6 policy trees and the7 candidate tree are unchanged.

The rehearsal commits are unsigned temporary fixtures, not release commits: security intermediate `2b877a18b7933353755f5d9ce893492e2146fc35`, final7 `a41db69b51ae32137009226a78f2a1a528bd2dd2`. Commit the real reviewed state and re-run its declared cells; do not reuse fixture commits or the synthetic6 tag as publication material.

## Exact sequence

These commands are for the parent publishing agent; this review performed no external mutation. Set `platform_release_branch` to the approved branch containing the workflow. The workflow requires a branch checkout and atomically pushes evidence commits, array metadata and tags back to that branch.

```bash
cd /Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone/platform
platform_python=/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.venv/bin/python
platform_release_files=/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.scratch/ecosystem/patches/resume-2026-10-03
platform_release_patch="$platform_release_files/platform-prepare-policy-6.0.0.patch"
platform_release_branch=main

# After the reviewed final implementation is committed:
git apply --check "$platform_release_patch"
git apply "$platform_release_patch"
git add graded/policies/cage-tier.yaml graded/policies/cage-netpol.yaml posture/policies/stamp-posture.yaml distribution/render-version-tree.py distribution/versions.yaml
git commit -m 'Prepare security policy6 from its exact intermediate authoring'
"$platform_python" .github/scripts/cut-release-gate.py --dry-run "$platform_release_files/platform-cut-policy6.tags.json"
"$platform_python" computed-semver/engine_compatibility.py --ref HEAD --engine /private/tmp/pavf-kyverno-engines/1.18.2/kyverno --engine /private/tmp/pavf-kyverno-engines/1.19.1/kyverno
git push origin "HEAD:$platform_release_branch"
gh workflow run cut-release.yml --ref "$platform_release_branch" -F "tags=@$platform_release_files/platform-cut-policy6.tags.json"

# Wait for successful cut and verify the signed policy6 tag/evidence before continuing.
git fetch origin --tags
git pull --ff-only origin "$platform_release_branch"
git apply --check -R "$platform_release_patch"
git apply -R "$platform_release_patch"
git add graded/policies/cage-tier.yaml graded/policies/cage-netpol.yaml posture/policies/stamp-posture.yaml distribution/render-version-tree.py distribution/versions.yaml
git commit -m 'Restore compatibility policy7 after the security6 cut'
"$platform_python" .github/scripts/cut-release-gate.py --dry-run "$platform_release_files/platform-cut-policy7-tools5.tags.json"
"$platform_python" computed-semver/engine_compatibility.py --ref HEAD --engine /private/tmp/pavf-kyverno-engines/1.18.2/kyverno --engine /private/tmp/pavf-kyverno-engines/1.19.1/kyverno
git push origin "HEAD:$platform_release_branch"
gh workflow run cut-release.yml --ref "$platform_release_branch" -F "tags=@$platform_release_files/platform-cut-policy7-tools5.tags.json"
```

For each Actions run, the workflow signs real publisher evidence, grades every declared engine cell, creates evidence commitA, creates array-metadata commitB pointing atA, then signs tags onB and pushes branch/tags atomically. The tag being one commit ahead of its array SHA is intentional; their policy trees must match. Confirm clean `passed` rather than `degraded`, verify signatures/provenance, then perform authorized adopter moves/recompositions. No acceptance record or offline CLI result is a live admission or rollout observation.
