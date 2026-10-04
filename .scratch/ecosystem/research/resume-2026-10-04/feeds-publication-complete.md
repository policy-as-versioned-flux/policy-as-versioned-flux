Feeds publication is complete. [PR10](https://github.com/policy-as-versioned-feeds/feeds/pull/10) was merged by `pavc-other-hand[bot]` at the independently approved signed source head `37dfe4a2de50f1a1fd7aeb6348d819373188e0e6`. The resulting merge commit is `974e73514e0d8d4cad2e6906acf51d1cc27028b3`, with the exact reviewed tree `e70d9c00caea6313cc0b3c4f65ee0205fc42c709`.

| Published feed | Annotated tag object | Cut run | Verify/publish run |
|---|---|---|---|
| [cve/v3.0.0](https://github.com/policy-as-versioned-feeds/feeds/releases/tag/cve/v3.0.0) | `647f4961eb02d0858092ee6f91a43cb1657bdd97` | [37161227853](https://github.com/policy-as-versioned-feeds/feeds/actions/runs/37161227853) SUCCESS | [37170113406](https://github.com/policy-as-versioned-feeds/feeds/actions/runs/37170113406) SUCCESS |
| [fx/v1.1.0](https://github.com/policy-as-versioned-feeds/feeds/releases/tag/fx/v1.1.0) | `fcd8697eafdd44de5d6748ac50b190c9139c5af0` | [37161252190](https://github.com/policy-as-versioned-feeds/feeds/actions/runs/37161252190) SUCCESS | [37177589644](https://github.com/policy-as-versioned-feeds/feeds/actions/runs/37177589644) SUCCESS |
| [threat-register/v4.0.0](https://github.com/policy-as-versioned-feeds/feeds/releases/tag/threat-register/v4.0.0) | `57cfe4af7aa85301e27dc720f0227834bfd0574f` | [37161274961](https://github.com/policy-as-versioned-feeds/feeds/actions/runs/37161274961) SUCCESS | [37184479972](https://github.com/policy-as-versioned-feeds/feeds/actions/runs/37184479972) SUCCESS |

All three annotated tags peel to the merge commit above. Independent local `gitsign verify-tag` returned zero for each with Git signature, offline Rekor bundle, and certificate claims validated. The exact signer identity is `https://github.com/policy-as-versioned-feeds/feeds/.github/workflows/cut-release.yml@refs/heads/main`; the OIDC issuer is `https://token.actions.githubusercontent.com`. Raw tag objects and signature logs are preserved beside `feeds-tag-signature-proof.json`.

Both release gates and the identity-pinned signature gate passed in every explicit release run. CVE and FX used `main` while its checkout equalled the signed tag commit; threat used its immutable tag ref. The workflow’s tag-push-only trigger comparison step was skipped for manual dispatch; the independent checkout/tag equality check above passed. FX dispatch returned a transport reset, but the accepted real run was located and verified before any retry. No duplicate dispatch occurred.

CVE3 contains 1,733 captured CISA/NVD/FIRST records, with EPSS dated 2026-10-03. FX1.1 uses the authentic HMRC August2026 CSV (141 rates), with that observation month retained. Threat4 adds cited scheduled-agent credential-misuse frequency; subscriber magnitude remains absent until declared. Old frozen feed payloads remain preserved by the reviewed source change. Neither fresh prices nor adoption evidence is inferred from publication.

Only `.estate-publish/feeds` received fetched objects; its source branch remains at the reviewed head. To make the authentic objects available to the shared owner checkout without overwriting its source edits, run this fetch only:

```sh
git -C .estate-clone/feeds fetch origin '+refs/heads/main:refs/remotes/origin/main' \
  refs/tags/cve/v3.0.0:refs/tags/cve/v3.0.0 \
  refs/tags/fx/v1.1.0:refs/tags/fx/v1.1.0 \
  refs/tags/threat-register/v4.0.0:refs/tags/threat-register/v4.0.0
```

Use an isolated tag checkout or `git archive` for released payload inspection. The fetch does not reset, checkout, or pull the owner’s working tree. Oct3 rejection artifacts remain unchanged; the explicit Oct4 user approval authorized this sequence. No feed delivery blocker remains.
