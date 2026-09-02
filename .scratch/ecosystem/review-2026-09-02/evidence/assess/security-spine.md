# Assessment — identity, signatures and the threat model

**Dimension key:** `security-spine`
**Auditor pass, 2026-09-02.** Citable line: `TRUTH 2026-09-02T10:11Z run=21 hub=7b92990 … pass=57 fail=7 skip=18 excluded=2 total=84`.
**Method:** read the thirteen maps under `review/understand/` for pointers, then went to primary sources for every load-bearing claim. Where I could re-derive a fact by running something read-only, I did — the commands and their outputs are quoted below so a skeptic can repeat them. Nothing was written, pushed, merged or dispatched.

---

## 0. What the ambition asks of this dimension

- **NORTH-STAR §1** — "every actor is attestable".
- **NORTH-STAR §2** — "each participant … signs its own artefacts, and is consumed only through a **pinned, signed dependency**. No participant reaches into another."
- **NORTH-STAR §3 principle 6** — "Every actor is attestable, and the record is falsifiable. Every artefact carries a signature that says what it does and does not assert. **Agent signatures attest the absence of a human.** … A green that could not look is a red."
- **NORTH-STAR §3 principle 5** — "enactment happens only by reviewed PR. … Nothing timed ever changes a verdict on its own."
- **NORTH-STAR §4 step 3** — "A proposal PR opens, **signed by the proposer's identity**."
- **NORTH-STAR §4 step 6** — "Provenance: every step above is **verifiable in Rekor** and in the artefact sidecars."
- **ADR-0023 D3** — the gitsign tag is the only signature.
- **ADR-0024 D1** — a clock appends observations, never a declaration.
- **Thesis / mea culpa (research/03)** — a catastrophic minority belongs at the gate; the rest is a versioned dependency.

Everything below is graded against those, not against my taste.

---

## 1. Strengths — what is genuinely done and proven

**S1. Twenty-four of twenty-four estate tags are real keyless signatures with real Rekor entries, under per-repo anchored identity pins.** I re-derived this on one:

```
$ cd units/ico && gitsign verify-tag v3.0.0 \
    --certificate-identity-regexp='^https://github\.com/policy-as-versioned-ico/ico/\.github/workflows/cut-release\.yml@refs/heads/(main|release/[0-9]+\.[0-9]+\.x)$' \
    --certificate-oidc-issuer=https://token.actions.githubusercontent.com
tlog index: 2664928228
gitsign: Good signature from [https://github.com/policy-as-versioned-ico/ico/.github/workflows/cut-release.yml@refs/heads/main](https://token.actions.githubusercontent.com)
Validated Git signature: true
Validated Rekor entry: true
Validated Certificate claims: true
```

The `publishers` and `github-live` readers checked the other 23 and found the same. This is the load-bearing thing the thesis asks for and it is real, not a fixture.

**S2. The identity pins are correct, per-repo, and negatively tested — and all six checks are green on the citable run.** All eight `release.yml` files carry the identical shape with only the org/repo substituted:

`units/<u>/.github/workflows/release.yml` → `EXPECTED_IDENTITY_REGEXP: ^https://github\.com/policy-as-versioned-<u>/<u>/\.github/workflows/cut-release\.yml@refs/heads/(main|release/[0-9]+\.[0-9]+\.x)$`, `EXPECTED_ISSUER: https://token.actions.githubusercontent.com`.

Run-21 grades, read from `origin/main:talk/captures/`:

| capture | last line |
|---|---|
| `.estate-clone_driftwood_scripts_verify-identity-regexp.out` | `PASS: EXPECTED_IDENTITY_REGEXP matches main + release/<major>.<minor>.x only, anchored to this repo.` |
| `.estate-clone_ludlow_verify-certificate-identity-regexp.out` | `PASS: … matches only policy-as-versioned-ludlow/ludlow's cut-release.yml …` |
| `.estate-clone_nist_scripts_verify-cert-identity-regexp.out` | `OK: EXPECTED_IDENTITY_REGEXP anchors org/repo/workflow and allows only main + release/…` |
| `.estate-clone_ico_…`, `.estate-clone_platform_…`, `.estate-clone_tuppence_…` | all PASS |

`units/driftwood/scripts/verify-identity-regexp.sh:32-46` does not merely regex-test: it runs **real `gitsign verify-tag` against every real `v*.*.*` tag in the repo** and fails the script if any is rejected. That is an estate observation, not a selfcheck.

**S3. `verify_gitsign.py` is well-built and its trust decisions are principled.** `units/platform/identity/gitsign-verifier/verify_gitsign.py`:
- evaluates the chain at the **tagger timestamp inside the signed payload** (`-attime`), not "now" — the right instinct for a ten-minute Fulcio cert (lines 20-25, 191-196);
- **refuses an unanchored identity regexp before using it** (lines 213-217) — `.*` and `platform` cannot silently "pin" everything;
- carries a genuine **tri-state**: `CouldNotLook` (missing root/intermediate, unreachable remote) is never a rejection and never a pass (lines 88-92, 300-308), and a gate it holds **stays held** while it cannot look (lines 335-341) — the documented fix for a real fail-open;
- never signs. `units/platform/verify-source-verification.sh:57-140` proves that with an **AST walk over the module's own `subprocess.run` argv**, not a grep — added 2026-08-29 after a real `subprocess.run(["git","tag","-s",tag])` walked past the shell-shaped grep. That is a defence that learned from its own failure.

**S4. A pod cannot pick its own tier, and the estate proved that the hard way.** In `units/driftwood/composed/policies/v4.0.0/cage-tier.yaml:30-37` the tier comes from `namespaceObject`, never the pod, and the mutation **clobbers** the pod's `posture.acme.io/tier`. The fallback is fail-closed:

```
- name: tier
  expression: "variables.nsTier in ['baseline','restricted','quarantine','isolated']
    ? variables.nsTier
    : (variables.nsGoverned ? 'isolated' : 'baseline')"
```

Three mutually reinforcing controls sit on this: `posture-trust-boundary-4-0-0` **Denies** a pod whose `posture.acme.io/version` disagrees with its claim; `governed-namespace-requires-claim` **Denies** a claim-less pod in a governed namespace (`units/platform/distribution/versions.yaml:155-176`); the cage mutation is **tighten-only** by construction (ORed hardening booleans, `min()` on cpu/mem quantities, host namespaces clobbered shut). Every one of those carries a dated "observed live, 2026-08-28" note for the loosening it closes. `units/driftwood/gitops/apps/namespace.yaml:30` declares `posture.acme.io/tier: "isolated"` on the governed namespace and `gitops/apps/pod.yaml:23-24` carries no tier label at all. **H8-03 is genuinely closed.**

**S5. The observation cage is real code that demonstrably bites.** `.github/workflows/truth.yml:108-162`: `git reset -q` first (fixing a reproduced 2026-08-28 defect where staged-and-clean entries rode along), then stage only `OBSERVATION_LANE`, then assert the **staged set** against the same env list rather than a second regex, then assert the tree clean outside the lane. That it bites is not an assertion: `github-live` records hub `truth.yml` failing 17 consecutive runs on `::error::the scheduled truth run left a change outside the observation lane`. A cage that never refuses would be the suspicious one.

**S6. Tool supply chain is pinned by version *and* sha256 nearly everywhere.** gitsign `0.17.1/69213a8a…`, kyverno `1.18.2/cb2feb83…`, cosign `3.1.3/4629c757…` in `truth.yml:38-49`; kind, flux, kyverno, flux-operator all version+digest in `units/driftwood/.github/workflows/drift-sample.yml:47-61`, whose header states the rule outright: *"A `curl | bash` installer would put an unreviewed script inside the identity that signs this repository's observation commits."* Two named exceptions are findings below (SS-06, SS-09); the rule itself is applied, not aspirational.

**S7. No private key material is committed anywhere.** `grep -rln "BEGIN .*PRIVATE KEY"` over all eight unit clones and the hub (excluding `.git`) returns **zero**. `units/ico/schema/keys/` and `units/platform/feeds/keys/` hold only `*.pub.pem`. No `ghp_`, `github_pat_`, or `AKIA…` literal anywhere.

**S8. `enact_guard.py` now fails closed and says why.** `twin/enact_guard.py:94` is `DEFAULT_MODE = "operations"` — the 2026-08-29 flip, made after discovering that thirteen tests asserting guard behaviour passed only because an autouse fixture forced the mode the shipped default did not use. The module names its own ceiling honestly (docstring lines 30-35: "the command patterns are a net over the shapes a merge actually takes here, not a proof … the upgrade is a credential that cannot merge").

**S9. `truth.yml` deliberately withholds the write credential from the untrusted scripts.** `truth.yml:59-66`: `persist-credentials: false` on checkout with a written rationale, and `GH_TOKEN` scoped to the cage step's `env:` only. This is a real, deliberate mitigation and better than the default. Its residual is SS-07.

---

## 2. Findings

### SS-01 (critical) — the estate's only cluster-side signature check systematically rejects genuine tags, and its own fixture cannot expose it

`verify_gitsign.py` evaluates the Fulcio chain at the tag's **tagger second** (`openssl verify -attime <tagger epoch>`, line 194). Git writes the tagger line *before* gitsign obtains the certificate, so the tagger second is `<=` the certificate's `notBefore` second and is frequently **one second earlier**. When it is, `openssl verify` returns "certificate is not yet valid" and the verifier grades the tag **REJECTED**.

Re-derived locally against driftwood's real tag:

```
$ git -C units/driftwood cat-file tag v1.1.0 > dw-v110.tag
$ python3 units/platform/identity/gitsign-verifier/verify_gitsign.py verify-object dw-v110.tag \
    --identity-regexp '^https://github\.com/policy-as-versioned-driftwood/driftwood/\.github/workflows/cut-release\.yml@refs/heads/(main|release/[0-9]+\.[0-9]+\.x)$' \
    --issuer https://token.actions.githubusercontent.com
REJECTED: certificate chain did not verify at tagger time 1787677714: … verification failed

$ # why:
tagger epoch = 1787677714  (2026-08-25T17:08:34Z)
notBefore    = Aug 25 17:08:35 2026 GMT   # ONE SECOND LATER
notAfter     = Aug 25 17:18:35 2026 GMT
```

The same tag verifies perfectly with the real tool (S1's method). So this is unambiguously an **instrument fault**, not a bad signature.

I measured it across every tag in the estate (script: extract tagger epoch from the signed payload, extract `notBefore` from the signer cert, compare):

| unit | tag | delta (tagger − notBefore) | verifier verdict |
|---|---|---|---|
| nist | v1.0.0 | **−1** | REJECT |
| ico | v1.0.0 | **−1** | REJECT |
| ico | **v3.0.0** | **−1** | REJECT |
| driftwood | **v1.1.0** | **−1** | REJECT |
| ludlow | **v1.1.0** | **−1** | REJECT |
| the other 19 tags | | 0 | accept |

**5 of 24 (21%) of the estate's genuine tags are rejected by its own cluster-side verifier.** The three in bold are live pins: ico v3.0.0 is the penalty schema all three adopters pin, driftwood v1.1.0 is the tag driftwood's own composed ResourceSet installs from, ludlow v1.1.0 likewise.

This is visible on the citable run and is the direct cause of at least four of run-21's seven fails. From `origin/main:talk/captures/.estate-clone_driftwood_verify-reconcile.out`:

```
driftwood-composed FALSE fact_2_tag_signature_verified_at_the_source_boundary:
  the controller's verdict is 'false': v1.1.0: signature or certificate chain did not verify
  at tagger time 1787677714: … Verify error: certificate is not yet valid
driftwood-composed true  fact_1 … true fact_3 … true fact_4 … true fact_5
platform           true  fact_2 … verified at the source boundary  (platform v2.0.1, delta 0)
nist               true  fact_2 … verified at the source boundary  (nist v1.1.0, delta 0)
```

Note the pattern precisely matches my table: the delta-0 tags pass, the delta-−1 tag fails.

**Why the estate's own proof cannot catch it.** `units/platform/verify-source-verification.sh` check 4 asserts "it ACCEPTS that real signed tag", using the fixture `platform/distribution/verify/testdata/policy-v3.0.0.tag`. That fixture's tagger epoch is `1787475175` and its `notBefore` is `Aug 23 08:52:55 2026 GMT` = `1787475175` — **delta 0**, so it passes by one second of luck. And every one of platform's own eleven tags is delta 0, so a platform-only corpus never exhibits the failure. The script graded `SKIP: offline proof holds` in run 21 while the property it certifies is false for 21% of the estate.

**Relation to prior work.** REVIEW-2026-08-31 M2 named the same *symptom* with a different *cause* ("unable to get local issuer certificate" — OpenSSL 3.0 chain building). Ticket 55 fixed that (the two-step `openssl verify` / `openssl cms -noverify` split, `verify_gitsign.py:181-206`). This is a **second, distinct cause of the same symptom** that the ticket-55 fix did not touch and could not have found with a delta-0 fixture. It is not a re-raise.

**Fail direction.** This fails *closed* (`reconcile_one` → `ok=False` → `spec.suspend: true` on the gated Kustomization, lines 344-349), so it is a denial of service against a correct release, not an admission of a bad one. That is the right direction — but it makes the gitsign verifier unusable as a gate as shipped, and today it is the only thing standing at the Flux source boundary.

**Remedy.** Either evaluate at `max(tagger, notBefore)` when the gap is inside a bounded skew (with the bound named and tested), or evaluate at the **Rekor signed entry timestamp** — which is also the fix for SS-12 and is already named as this module's ponytail. Either way the fixture corpus must gain a delta-−1 tag so the property is actually tested. This is a decision for the owner: the current behaviour is *defensible* as strict, but it is currently silently wrong about a fifth of the estate.

---

### SS-02 (major) — the whole identity substrate is asserted structurally and has never been observed running on any citable run

Every script in this dimension graded SKIP in run 21, all for the same reason. Last lines from `origin/main:talk/captures/`:

```
platform_identity_verify-identity.out        SKIP: offline proof holds; live tail could not look: kind cluster 'driftwood' is not listed by kind get clusters — SPIRE is Istio's CA, mTLS STRICT, authz by SPIFFE principal …
platform_identity_verify-federation.out      SKIP: … — each cluster-running party has its own trust domain and the four domains federate pairwise
platform_verify-source-verification.out      SKIP: … — the gitsign verifier accepts this repo's own signed tag under release.yml's pins and rejects a tampered payload …
platform_access_verify-access.out            SKIP: … — the access plane wiring holds (Pomerium+Dex+WebAuthn device on the one SPIFFE root)
platform_eud_verify-eud.out                  SKIP: … — EUD vTPM specs and tpm-devid entries sit on the one estate root; WHfB alone is refused
platform_break-glass_verify-break-glass.out  verify-break-glass: done (offline; rides on the access plane …)
```

So on the only citable surface: **no SVID has been observed, no mTLS handshake, no SPIFFE-principal authorization, no OpenBao JWT auth, no Pomerium/Dex login, no device SVID, and no gitsign-verifier controller pod.** The offline halves are genuine structural proofs (YAML shape, cross-file consistency, negative cases) and the SKIP is honest per NORTH-STAR §5's three-outcome rule — this is not dishonesty. But it means the entire "every actor is attestable" leg of principle 6, for *workloads, humans and devices*, is **built and locally reasoned, never proven on the clock**. The only leg proven on the clock is artefact signing (S1, S2).

Note also a wording issue: each SKIP line ends with a declarative sentence ("SPIRE is Istio's CA, mTLS STRICT, authz by SPIFFE principal…") that reads as an assertion of fact. It is prefixed `SKIP:` so a careful reader is not misled, but a capture grepped for its tail reads as a claim. Minor sub-point of the same finding.

**Owned by:** partially — the `kind` substrate absence on the CI runner is a known structural fact of the truth surface; I found no ticket that owns *"the identity substrate has never been observed live on a citable run."*

---

### SS-03 (major) — federation is aspirational, and the peers' trust anchors are held by the platform, which is the tenant shape §2 forbids

`units/platform/identity/README.md:74-86` and `units/platform/identity/federation/driftwood.yaml:12-31` state three real blockers, honestly, and `verify-federation.sh` exits 3 rather than passing:

1. driftwood's live SPIRE still runs the single estate-wide trust domain `acme.internal`, not `driftwood.acme.internal`;
2. tuppence and ludlow run KinD with **no SPIRE at all**;
3. `spire-server.federation.enabled` is off, so no bundle endpoint is served on any side.

Confirmed in code: `units/platform/identity/verify-identity.sh:50` asserts `td == "acme.internal"` — the *single* domain — while `verify-federation.sh:86-97` asserts twelve objects across four `<party>.acme.internal` domains. The two live checks in the same package assert mutually exclusive worlds; one is what runs, the other is what is declared.

The sharper point for §2 ("Nothing in the eco-system is a tenant of anything else"): `trust_domain`, `bundle_endpoint` and `federates_with[]` are **decided** to belong on each party's own signed `party.yaml` (ticket 12 answer 1), but `party/schema.json` is `additionalProperties: false` and `party_artefact.py` reads its allowed keys straight from it, so adding them today REFUSES every existing party artefact. So today driftwood's, tuppence's and ludlow's trust domains and bundle endpoints are **literals in platform's tree**, authored by the platform. `units/platform/identity/README.md:90-99` names this as "exactly the 'demand from a literal' shape H8-05 already names as a defect". Independently confirmed: `grep -rn trust_domain` across all three adopter clones returns **nothing**; the only trust-domain-like constant is `TRUST_DOMAIN = "acme.internal"` hardcoded in `units/tuppence/reset/reach.py:16`.

Answer to the brief's question: **the SPIRE/federation story is aspirational, and the estate says so in the right places and grades it 3 rather than passing.** The residual defect is not the honesty; it is that the schema patch that would make it a party-owned fact is small, named, unowned, and blocking.

**Owned by:** REVIEW-2026-08-31 M11(3) → ticket 58 (grilling, resolved on a bare "Agree") then "builds". No build ticket found that owns the `party/schema.json` patch specifically.

---

### SS-04 (major) — the signature attests a workflow path, not a review; and there is no branch protection anywhere in the estate

The whole spine reduces to one question: *what does `cut-release.yml@refs/heads/main` actually prove?* GitHub's OIDC subject is the workflow **file path at a ref**, not the workflow's content. So the certificate attests: "a GitHub Actions run in this repo executed the file at `.github/workflows/cut-release.yml` on `main`". It attests nothing about what that file contained, and nothing about whether the commit it tagged was reviewed.

I verified the surrounding controls live, read-only, on all nine repos:

```
$ gh api repos/policy-as-versioned-<u>/<u>/rulesets           → []            (all 9, incl. hub)
$ gh api repos/policy-as-versioned-<u>/<u>/branches/main/protection
                                                              → 404 "Branch not protected"  (all 9)
```

Combined with `github-live`'s finding (which I did not re-derive) that all 46 closed non-Renovate PRs were authored **and** merged by the same identity, the honest grade is: **anyone with push access to a unit repo can rewrite `cut-release.yml`, push it to `main` unreviewed, dispatch it, and produce a tag that every consumer's identity pin accepts.** The pin is doing real work against a *foreign* signer; it does nothing against the repo's own writer.

This is not a defect in the pinning design — it is the correct design, and it is what Sigstore's model gives you. It is a shortfall against NORTH-STAR §3 principle 4 ("bump only by reviewed PR") and principle 5 ("A human merges"), both of which are today **conventions with no enforcement point**. The estate already records the adjacent half of this (the observation-lane ruleset cannot be applied to public repos, `units/driftwood/.github/rulesets/README.md`, "Amended 2026-08-28"), but that README is about the *clock* identity; nothing records that the *human* identity is equally unconstrained.

---

### SS-05 (major) — `release/<M>.<m>.x` is an accepted signing branch and one exists, giving a signing path that never touches `main`

Every `EXPECTED_IDENTITY_REGEXP` accepts `@refs/heads/release/[0-9]+\.[0-9]+\.x` as well as `@refs/heads/main`. Live check:

```
$ gh api repos/policy-as-versioned-platform/platform/branches --jq '[.[].name]|join(",")'
ecosystem/thin-slice,main,observations,policy-composition/tickets-09-16-wip,release/2.0.x,renovate/configure,repair/…
```

`release/2.0.x` exists on platform today. A `workflow_dispatch` of `cut-release.yml` on that branch produces a tag whose certificate matches every consumer's pin — with no change to `main` at all. Even if SS-04 were fixed by protecting `main`, this branch pattern would remain an unprotected signing path unless it is protected too. Nothing in the estate protects it (SS-04's ruleset query returns `[]` for every ref).

The patchable-older-lines requirement (thesis; NORTH-STAR §3 principle 4, "Older lines are patchable") is the reason the pattern exists, so the pattern is right. The gap is that the branch class it opens is not covered by any control, and no check names it.

**Not previously raised** in REVIEW-2026-08-31.

---

### SS-06 (major) — `truth.yml` pipes an unpinned remote script to `sudo bash`, in the one job that later signs and pushes to the hub's `main`

`.github/workflows/truth.yml:80-92`, immediately under a comment that states the rule it breaks:

```yaml
      - name: kyverno, cosign, flux CLIs the offline proofs call
        # Every tool the gate observes with is pinned by version AND checksum, like gitsign
        # above. An unpinned tool makes the number unreproducible …
        run: |
          …
          echo "${KYVERNO_SHA256}  kyverno.tgz" | sha256sum -c -
          echo "${COSIGN_SHA256}  cosign" | sha256sum -c -
          curl -s https://fluxcd.io/install.sh | sudo bash          # <-- unpinned, root
```

`drift-sample.yml:48-50` states the estate's own reasoning for why this is not allowed: *"A `curl | bash` installer would put an unreviewed script inside the identity that signs this repository's observation commits."* That is exactly what `truth.yml` does — and `truth.yml`'s identity is the one that gitsign-signs and pushes `talk/truth.log`, the estate's single citable artefact. Two concrete consequences: (a) the TRUTH number is not reproducible with respect to the Flux CLI version, contradicting the comment three lines above it; (b) a compromise of `fluxcd.io/install.sh` reaches root on the runner before the cage step's `GH_TOKEN` is used.

The fix is mechanical (the same pinned-tarball pattern the file already uses three times, and which `drift-sample.yml:53-56` already applies to Flux specifically with `FLUX_VERSION: 2.9.3 / FLUX_SHA256: eae4e860…`). The digest is literally already known elsewhere in the estate.

---

### SS-07 (major) — the hub's write credential is separated from the untrusted scripts by process convention, and the comment claims more than that

`truth.yml:59-66` sets `persist-credentials: false` with a good written rationale, and the cage step's comment says:

> `# The credential is handed to THIS command only; nothing the gate ran could reach it (see persist-credentials above).`

That claim is too strong. The gate step runs **84 `verify*.sh` scripts cloned unpinned off eight other orgs' default branches** (`clone-estate.sh`), as the runner user, with passwordless `sudo` available (SS-06 uses it), in the **same job** that afterwards runs `git -c http.extraheader="AUTHORIZATION: basic <token>" push`. Any of those scripts could write a `git` shim onto `PATH`, or edit `~/.gitconfig`, and intercept the push. `persist-credentials: false` removes the token from `.git/config`; it does not create a boundary.

I am not claiming an exploit exists — every one of those repos is owned by the same person, and I read no malicious script. I am claiming the property asserted in the comment is not the property the design has. The estate half-knows this: **ticket 56** (open) is written in exactly these terms — *"an equivalent design that keeps the token out of the eight orgs' unpinned scripts"* — but it is scoped to the *read* credential verify-schedules needs, not to the *write* credential the cage step already holds.

Related and confirmed: `verify/schedules/verify-schedules.sh`'s live half is structurally blind. From `origin/main:talk/captures/verify_schedules_verify-schedules.out`, every clock in the run:

```
SKIP: hub/truth.yml: GitHub unreachable (Command '['gh','auth','status']' returned non-zero exit status 1.) -- cannot look at whether this clock ran inside its period
```

So "did the clocks run" is a permanent could-not-look on the citable surface. That half is REVIEW-2026-08-31 M6, correctly owned by open ticket 56, and I confirm it is still true today.

---

### SS-08 (major) — the proposer's commit is unsigned, while its own record claims a gitsign/Rekor identity

NORTH-STAR §4 step 3: "A proposal PR opens, **signed by the proposer's identity**." What is actually configured, `units/driftwood/.github/workflows/propose-tier.yml:184-185` (the only git config in the whole file):

```
git -C driftwood config user.email "wargamer-proposer@policy-as-versioned-driftwood.invalid"
git -C driftwood config user.name  "wargamer proposer"
```

No `gpg.format x509`, no `gpg.x509.program gitsign`, no `commit.gpgsign true` — unlike `truth.yml:145-149`, `drift-sample.yml`'s cage step and `twin-sweep.yml`, which all three set exactly those three lines with a written explanation of why they must be in local config rather than on the commit command. `units/platform/wargamer/tier_pr.py:350-351` then does a plain `git commit` and `git push --force`.

Meanwhile the proposal record it emits asserts the opposite — `units/platform/wargamer/wargamer.py:199-200` and `:231-232`:

```python
"identity": "gitsign keyless (OIDC -> Fulcio) -> Rekor transparency log",
"signed": True,               # stamped at commit time by propose-policy-pr.sh
```

and `wargamer.py:324` **asserts** it in the module's own selfcheck: `assert p["signed"] is True and "Rekor" in p["identity"], p`. So the selfcheck tests that the hardcoded literal is the hardcoded literal.

Two mitigations I confirmed, which set the severity at major rather than critical: (a) `_pr_body()` (`tier_pr.py:283-309`) does **not** render `signed` or `identity` into the pull request body, so no human reader is shown the false claim; (b) no proposal has ever fired — no `wargamer/*` branch exists on any adopter (`gh api …/branches`), consistent with open ticket 74 ("step 3 happens once for real"). So this is a latent fabricated-provenance field, not one that has laundered into a signed artefact yet. It would become one the first time step 3 runs.

**Owned by:** GAPS 1.9 named it; `drift-review-followthrough` records it as still present. I found no *open* ticket that owns "the proposer signs its commit". Ticket 74 owns the firing, not the signing.

---

### SS-09 (minor) — `npx --yes renovate@44.37.1` is the second exception to the estate's pinning rule, in a job holding three write scopes

`units/driftwood/.github/workflows/renovate-run.yml:28-31, 75` (and byte-similar in tuppence and ludlow):

```yaml
permissions: {contents: write, pull-requests: write, issues: write}
…
        run: npx --yes renovate@44.37.1
```

The Renovate version is pinned; its **transitive dependency tree is resolved at run time** and is not. Every binary in this estate is otherwise version+digest pinned with a written justification. This is the same class as SS-06 with a smaller blast radius (the job pushes only Renovate's own branches; the cage step at the end asserts the checkout is clean). Worth naming because the estate's own rule is explicit and this is one of exactly two places it does not hold.

---

### SS-10 (minor) — a gate PASS line overclaims against the checker's own documented ceiling

`verify/schedules/schedules.py:558` emits, for every clean scheduled job:

> `PASS: <unit>/<workflow> job <job>: caged -- no shell step in this job stages a declaration or mints a signed artefact, and nothing it runs is opaque to this checker`

But the same file's `cage_faults` docstring (`schedules.py:251`) names the opposite: *"capability is the only thing that catches a job whose writing happens inside an opaque tool (`npx renovate`, a `uses:` action, a called python script)"*, and `:264-271` states the ceiling explicitly: *"everything below reads each step's own inline `run:` string. A push from inside a called program … is invisible to it."* Run 21 duly prints `PASS: driftwood/renovate-run.yml job renovate: caged … nothing it runs is opaque to this checker` for a job whose entire body is `npx renovate`, and `PASS: hub/truth.yml job gate: caged …` for the job that runs `curl | sudo bash` and 84 foreign scripts.

The *grade* is defensible (the cage step exists, which is what the check is for). The *sentence* is not; it says the one thing the function's own docstring says it cannot say. Fixing the sentence is a one-line change and it matters because these lines are what the deck and the tickets quote.

---

### SS-11 (minor) — committed demo credentials, and a live manifest comment the package's own README calls false

`units/platform/access/oidc/dex-helmrelease.yaml:50-62`:

```yaml
        - id: pomerium
          secret: pomerium-oidc-secret          # ponytail: inline demo secret; OpenBao-source at a venue
      staticPasswords:
        - email: operator@acme.internal
          # bcrypt("operator") — demo only; never a real credential.
          hash: "$2a$10$2b2cu2a0Yj1u5b5F8Q0m1uJ9e3v4Xq7Zr6sT8wV0yA2bC4dE6fGh"
```

plus `units/platform/identity/openbao/helmrelease.yaml:34`: `devRootToken: root       # demo only; ephemeral in-memory storage`. All three are labelled, all three would be real credentials the moment this substrate is applied anywhere reachable, and `identity/README.md` states this Dex account is **"the only human root in the estate"** today.

Separately, line 56-57 of the same file narrates that account as *"The SAME subject narrated as the gitsign committer — one human, one root."* `identity/README.md:139-146` says plainly: *"That is false: every signed tag in this estate is cut by a per-org GitHub Actions workflow subject … No human can log in as that subject, and no human should."* The correction lives in the README; the false claim is still in the shipped manifest, where an operator reading the YAML will see it and the README will not be open.

---

### SS-12 (minor, but it is the ceiling of SS-01's fix) — the cluster-side check is strictly weaker than the CI-side check: it does not verify Rekor

`verify_gitsign.py`'s docstring, lines 43-52, states this outright:

> *"ponytail: the ceiling is the transparency log. This does NOT verify the Rekor signed entry timestamp or an inclusion proof, so a signer who obtained a Fulcio certificate for the pinned identity and never logged it would pass here and fail `gitsign verify-tag`."*

The consequence for the ambition is concrete: **NORTH-STAR §4 step 6 requires "every step above is verifiable in Rekor"**, and the one place where verification actually gates enactment — the Flux source boundary — is the one place that does not consult Rekor. CI does (`release.yml` runs real `gitsign verify-tag`; so does `five-facts.py:gitsign_verifies`, and so does `verify-identity-regexp.sh`). The strongest check runs where nothing is enforced; the weakest runs where enforcement happens. The module names the gap and `verify-source-verification.sh` runs a `gitsign verify-tag` differential against the same fixture whenever gitsign is on PATH, which is the right way to watch a gap you have chosen not to close — so this is disclosed, not hidden.

---

### SS-13 (minor) — ADR-0023's two retirement triggers have both fired and the second signer is still in the tree

`docs/adr/0023…:23-33` names two key-based signers and their exact triggers:

> *"**platform's ed25519 feed key** … **Retires when** the `feeds` party has cut the tags those pins wait for: delete `feeds/keys/`, the `.sig` files and the five openssl blocks that read them"*
> *"**ico's ed25519 schema key** … **Retires when** ico has cut the `v3.0.0` tag those pins wait for: delete `schema/keys/`, `schema/sign.sh`, the `.sig` files and `verify-penalty-feed.sh`'s openssl block"*

Both triggers have fired: `git -C units/feeds tag -l` → `threat-register/v1.0.0, threat-register/v2.0.0`; `git -C units/ico tag -l` → `v1.0.0, v3.0.0`. Neither deletion has happened. Still present on the default branches today: `units/ico/schema/keys/ico-signing-key.pub.pem`, `units/ico/schema/sign.sh` (a **signing** script), `units/platform/feeds/keys/feeds-signing-key.pub.pem`, and 10+ `*.sig` files across `ico/schema/v1|v2`, `platform/feeds/{cve,eol,threat-register}`, `platform/wardley`, `platform/wargamer/fixtures`.

The ADR is unusually honest about this — *"Until those tags exist the estate cannot say 'one signature' without this paragraph beside it"* — so this is an owned obligation now past due, not a hidden second signer. It matters because principle 6 says every artefact's signature must say what it does and does not assert, and today two signature schemes are live over overlapping artefacts.

---

### SS-14 (minor) — two stale comments sit on trust-critical files, both now saying the opposite of what is true

1. `units/driftwood/gitops/platform/platform-pin.yaml:33-37` pins `tag: v2.0.1 / commit: 533dccb0…` and the comment beneath says *"the resolved SHA platform **v1.1.0** tag points to"*. I checked: `git -C units/platform rev-parse v2.0.1^{commit}` → `533dccb0a823001b396fd60ab08014bf75065a37`, so the **pin is correct and the comment is wrong**. On the one file that names which platform release governs driftwood, a stale provenance sentence is exactly the wrong thing to leave.

2. `units/driftwood/.github/workflows/drift-sample.yml:151-157` says the gitsign-verifier *"landed in platform AFTER the tag this repo currently pins, so … this apply is a no-op and fact 2 stays could-not-look."* Falsified: `git -C units/platform ls-tree -d v2.0.1 identity/gitsign-verifier` returns the tree, and run 21's capture shows fact 2 producing a real `false` verdict from the controller — so the controller **is** installed and **is** deciding. A reader following that comment would conclude the estate has no cluster-side verification at all, which is the opposite of the truth and the opposite of SS-01's severity.

---

### SS-15 (minor) — "agent signatures attest the absence of a human" has no implementation

NORTH-STAR §3 principle 6 requires it. `grep -rn "absence of a human"` across `twin/`, `verify/`, `docs/` and all eight unit clones returns **zero** outside NORTH-STAR itself. What exists is a workflow-identity signature, which does say "an Actions run made this, not a person's key" — a partial satisfaction. But every `cut-release.yml` is **`workflow_dispatch` only** (`units/platform/.github/workflows/cut-release.yml:60`, and the same in all eight), so every signed tag in the estate was in fact initiated by a human choosing a commit. No artefact anywhere carries a claim distinguishing agent-authored content from human-authored content. The principle as written is not implemented; the closest thing to it asserts something adjacent.

---

## 3. Answers to the brief's threat exercise, stated plainly

| Attempt (by reading, not by attacking) | Verdict |
|---|---|
| **Can an adopter loosen its own cage without a reviewed PR?** | Yes, trivially — and that is by design (self-governance), but nothing enforces the "reviewed" half. The tier lives on the adopter's own governed `Namespace` manifest, delivered by its own Flux `Kustomization` from its own repo. With no branch protection (SS-04) a direct push to `main` moves it. The *proposer* cannot dispose (`tier_pr.py` has no merge path, AST-verified) — but the proposer is not the attacker in this scenario, the repo writer is. |
| **Can a pod pick a lower tier?** | **No.** Tier comes from `namespaceObject` and clobbers the pod label; unknown/absent tier in a governed namespace falls to `isolated`; the mutation is tighten-only; a mismatched `posture.acme.io/version` is Denied; a claim-less pod in a governed namespace is Denied. Three named live defects in this exact area were found and closed on 2026-08-28. (Residual, disclosed in the policy's own comment: a `hostPath` volume cannot be clobbered because SSA merges volumes by name, so an `isolated` pod can still mount the node filesystem; forced `runAsNonRoot` is the only bar.) |
| **Can a publisher ship an unsigned or wrongly-identified tag that a consumer accepts?** | **Wrongly-identified: no** — the identity regexps are anchored, per-repo, per-workflow-path, negatively tested, and enforced in CI (`release.yml`), in the adopter gate, in `five-facts.py`, and at the cluster boundary. **Unsigned: no** — `split_tag_object` rejects a tag with no signature block, and CI runs real `gitsign verify-tag`. **But**: a tag from the same repo's own `release/<M>.<m>.x` branch is accepted with no `main` involvement (SS-05), and a *correctly* signed tag is rejected 21% of the time (SS-01). |
| **Can a scheduled workflow commit a declaration?** | The client-side cage is real, correct and demonstrably biting (S5). The server-side half **cannot be applied** — GitHub allows push rulesets only on private/internal repos and all nine are public (`gh api …/rulesets` → `[]`, verified). This is recorded in `units/*/.github/rulesets/README.md`'s 2026-08-28 amendment. So: no, in practice; yes, if the client-side step is removed, with nothing on the server to stop it. |
| **Can the proposer's identity be forged?** | The proposer has no identity to forge — its commits are unsigned (SS-08). Nothing downstream verifies a proposer signature, so "forged" is not the right frame; the frame is that the claimed identity does not exist. |
| **Can the hub's truth workflow token be abused by a unit's verify script?** | Not by the mechanism the design removed (`persist-credentials: false` is real and correct), but the separation is process-level, not a boundary: 84 unpinned foreign scripts run with `sudo` in the same job that later uses the token (SS-07). The comment claiming otherwise overclaims. |
| **Is the SPIRE/federation story real or aspirational?** | **Aspirational, and the estate says so and grades it 3.** One trust domain (`acme.internal`), no peer, no bundle endpoint, two of four "cluster-running" parties have no SPIRE at all (SS-03). Never observed on a citable run (SS-02). |
| **The unpinned flux install** | Real, in `truth.yml`, contradicting the estate's own written rule and its own file's own comment, with the correct pinned digest already present elsewhere in the estate (SS-06). |
| **Any secrets committed?** | No private keys, no tokens (S7). Three labelled demo credentials in the Dex/OpenBao manifests, plus one false comment beside them (SS-11). |

---

## 4. Fitness verdict

The **artefact-signing spine is genuinely fit and is the strongest thing in the estate**: 24 real keyless tags with Rekor entries, per-repo anchored identity pins that are negatively tested and enforced at four independent places, no key material committed, and a cluster-side verifier whose design decisions (verify at signed tagger time, refuse an unanchored pattern, never turn could-not-look into a verdict, prove by AST that it cannot sign) are better than most production systems I have read. Against NORTH-STAR §2's "consumed only through a pinned, signed dependency", the platform→adopter and nist→adopter legs are proven on the clock.

The **enforcement spine is not fit yet**, for three separate reasons that do not overlap. First, the one control that actually gates enactment is broken in a way its own proof cannot see: `verify_gitsign.py` rejects 5 of 24 genuine tags on a one-second timestamp race, including three live pins, and its fixture is delta-0 so it certifies a property that is false for a fifth of the estate (SS-01). Second, everything about *actor* attestation — SPIRE, mTLS, SPIFFE authz, OpenBao, device SVIDs, human login — has never been observed running on any citable run (SS-02), and federation is a single trust domain with the peers' anchors held as literals in the platform's tree, which is the tenant shape §2 forbids (SS-03). Third, the governance layer that principles 4 and 5 rest on — "bump only by reviewed PR", "a human merges" — has **no enforcement point anywhere**: zero rulesets and zero branch protection on all nine repos, verified live, plus an accepted `release/*.x` signing path nothing covers (SS-04, SS-05).

What would make it fit, in the order I would take it: (1) fix SS-01 and add a delta-−1 tag to the fixture corpus — this is a day's work and unblocks four of run-21's seven reds; (2) protect `main` and `release/*.x` on all nine repos and require a review, which converts principles 4 and 5 from convention to mechanism; (3) pin the Flux install and move the Renovate install to the same pattern (SS-06, SS-09) — hours, not days; (4) sign the proposer's commit and delete the hardcoded `signed: True` (SS-08) *before* step 3 ever fires, so no fabricated provenance can enter a real proposal; (5) either land the `party/schema.json` patch so federation is party-owned, or write down that federation is out of scope for this build (SS-03). Items 2 and 5 are owner decisions, not build tasks. The remainder are mechanical and the estate already knows how to do each of them, because it has done the same thing correctly somewhere else in the same repository.

One thing deserves saying separately, because a review that only lists faults is useless: nearly every finding above was findable *because the estate wrote down its own rules precisely enough to be caught breaking them.* SS-06 is a finding only because `drift-sample.yml` states the rule; SS-10 is a finding only because `schedules.py`'s docstring states its own ceiling; SS-13 is a finding only because ADR-0023 named its own trigger and said the estate could not claim "one signature" until it fired; SS-14(2) is a finding only because the comment was specific enough to falsify. That is a rare and valuable property and it should not be traded away to make the numbers look better.
