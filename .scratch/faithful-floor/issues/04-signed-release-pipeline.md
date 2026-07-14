# 04 — Signed release pipeline: gitsign tags + identity-pinned CI verify

**What to build:** Releasing the policy becomes a signed, verifiable act (ADR-0001): cutting a semver tag produces a keyless gitsign signature (Fulcio via OIDC, logged to Rekor), and CI verifies it identity-pinned (expected OIDC issuer + subject, not just "a valid signature exists") against a persisted offline Rekor bundle (`GITSIGN_REKOR_MODE=offline`, gitsign version pinned), plus asserts the tag still resolves to the pinned SHA. Ends with `v1.0.0` cut for real.

**Blocked by:** 03 — Gate VP + rationale layout.

**Status:** ready-for-agent

- [x] Tagging a release produces a gitsign-signed tag; `gitsign verify` succeeds in CI with issuer+subject pinned
- [x] Verification runs offline against a persisted Rekor bundle; gitsign is version-pinned
- [x] CI fails if a tag no longer resolves to its recorded commit SHA
- [x] `v1.0.0` exists as a signed tag containing the lane-keeper + gate + rationale + fixtures
- [x] Release tags are forge-protected/immutable

## Comments

Done 2026-07-14. Also did the repo-topology split this ticket needed (PRD §5.1): created the
public `policy-as-versioned-flux` GitHub org, extracted `policy/` and `fleet/` into their own
repos with history preserved (`git subtree split`), hub repo pushed to
`policy-as-versioned-flux/policy-as-versioned-flux`.

`policy-as-versioned-flux/policy` `.github/workflows/release.yml`: on every `v*.*.*` tag push,
installs pinned gitsign/kyverno/kustomize (binary+checksum, no marketplace actions), runs the
`kyverno test` fixtures as a release gate, `gitsign verify-tag` identity-pinned
(`--certificate-identity`/`--certificate-oidc-issuer`, not just "a valid signature exists")
against `GITSIGN_REKOR_MODE=offline`, asserts the tag resolves to the commit the run was
triggered from, and publishes a GitHub Release recording that resolved SHA. A repository ruleset
blocks deletion/force-update of `v*` tags (immutability) — confirmed live by the ruleset
rejecting my own attempted force-push.

`v1.0.0` was cut first and its own CI run genuinely failed: `actions/checkout`'s second internal
fetch (it resolves the trigger ref to a SHA for checkout) force-overwrites the local
`refs/tags/<name>` to point straight at the commit, flattening the annotated tag object gitsign
needs — confirmed from the failure log ("error reading tag object: object not found"). Since the
tag-protection ruleset (deliberately) blocks even the owner from moving a pushed tag, and nothing
external depends on `v1.0.0` yet, I left it in place as an honest record of the bug and fixed the
workflow (re-fetch the real tag ref immediately before verifying) on `main`. `v1.0.1` (patch —
CI-only fix, no policy content change, so no verdict impact) is the first release whose pipeline
ran green end-to-end: https://github.com/policy-as-versioned-flux/policy/releases/tag/v1.0.1

Scoping note on "CI fails if a tag no longer resolves to its recorded commit SHA": ticket 04's
own release workflow can only check same-run consistency (the tag's dereferenced commit vs. the
SHA that triggered this run) — it has no earlier "recorded" value of its own to compare against.
The cross-time drift check ADR-0001 describes (a Renovate-authored consumer pin's `{tag, commit}`
pair vs. what the tag currently resolves to) is consumer-side and lands with issue 12's PR CI
gate.
