# Source-A cut/release interface and feed closure — 2026-10-04

Read-only exact-head audit: Driftwood eac40457, Tuppence d1dbe766, Ludlow926d6b38. The fresh full-window major gates independently join all three exact source heads, declare major, admit6/7 and retire none. Root's timestamped remote preflight observes each real apps3.0.1 baseline and unused v4.0.0; recheck immediately before cutting.

All three normal `cut-release.yml` interfaces remain valid: `version` and `message` are required workflow_dispatch inputs. The source checkout follows the dispatch ref. The pinned local platform-tools composite action checks out independent tools, verifies HEAD/tag/703, clean bytes and exact publisher identity before execution. Parent checkouts remain beside the adopter; `verify-pinned-checkouts` checks each actual HEAD before the authentic tools5 byte-replay gate, which runs before any signed tag is created. Existing-tag rejection and normal gitsign/git-push signing remain intact.

The feeds checkout uses the authentic threat4 tag and `fetch-depth: 0`. Full-history [checkout](https://github.com/actions/checkout/blob/11d5960a326750d5838078e36cf38b85af677262/src/git-source-provider.ts#L158) fetches all branches/tags before checkout, so genuine FX2 tag/object8c84 is available without moving genericHEAD974. Composition reads its own declared generic parent; Ludlow's producer separately verifies FX2 and git-shows8c84. The later object-store availability neither relabels threat4 nor adds an unsupported FX parent edge. Postcommit genuine local closure and relocated byte replay already pass.

All `release.yml` interfaces require `tag` for workflow_dispatch, verify the exact adopter cut-release identity (main or an ordinary release branch) and Actions issuer using normal offline Rekor trust, then publish the resolved commit. The dispatcher must choose the immutable tag as its workflow **ref** too: supplying only the tag input while dispatching main would build main, because checkout does not read the input and the GITHUB_SHA equality guard runs only for push events. This existing interface has a safe normal route; no source change is needed.

After root verifies the merged main tree equals the reviewed candidate tree, normal commands per adopter are:

```sh
gh workflow run cut-release.yml --repo policy-as-versioned-ORG/ORG --ref main -f version=v4.0.0 -f message='Reviewed Stage 2 source; delivery pins remain held'
# Only after genuine cut success and independently verified tag target:
gh workflow run release.yml --repo policy-as-versioned-ORG/ORG --ref v4.0.0 -f tag=v4.0.0
```

These commands were not executed by this reviewer. Source-A release does not move served self-pins or prove live activation; review later composition-B and delivery heads separately.
