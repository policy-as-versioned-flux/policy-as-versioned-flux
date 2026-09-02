# Map: the three adopter repos (driftwood, tuppence, ludlow)

Scope note up front: this map covers driftwood, tuppence, ludlow only, cloned fresh at
`.../scratchpad/units/{driftwood,tuppence,ludlow}`. Everything below is read from those
checkouts (git log/tag) plus file contents; no cluster was touched, no script that writes
was run. Paths below are relative to each repo root unless a full path is given.

Base facts, all three (checked 2026-09-02):
- `driftwood` HEAD `67bfc7a9a281959f9e9785d88b091279aa49154a`, `tuppence` HEAD `19cd50878c78e82547a707206a31f8a1156f89f6`, `ludlow` HEAD `ede531ab6ed65c032948eea05f99342cdb5252c2`. tuppence's and ludlow's HEAD match the TRUTH-run-21 line's `units=[...tuppence=19cd508... ludlow=ede531a...]` exactly; driftwood's HEAD is one `drift sample` commit ahead of the TRUTH-cited `6cf0671` (`git -C driftwood log --oneline -2`: `67bfc7a`, then `6cf0671 drift sample: five facts on an ephemeral cluster [skip ci]`) — consistent with "one commit behind" framing, not a discrepancy.
- Each repo carries exactly two tags: `v1.0.0` and `v1.1.0`, `v1.1.0` an ancestor of HEAD in all three (`git merge-base --is-ancestor v1.1.0 HEAD` → true for all three).
  - driftwood: v1.0.0→`92034b0927eb0c15aa9760deddbe6da2960038f0`, v1.1.0→`eacae33ca3a1662819651d56cdb54a4771fe13f1`
  - tuppence: v1.0.0→`9862d846332031d7cb5cf38894d3b0ed321928df`, v1.1.0→`751522b3bca98c40373c9bcb8b72ab376ab3be5b`
  - ludlow: v1.0.0→`7bd9973be43de0b5d1d13b7eb46a1a60b01516ec`, v1.1.0→`a800a58e2547b41f8c9b77a91b93eb9d820e8569`
- `git tag -v v1.1.0` on all three fails locally with `gpgsm: can't open '-': No such file or directory` before printing the tag object — expected, since these tags are gitsign/keyless-signed (Sigstore/Rekor), not classic-GPG, and no GPG key/gpgsm is configured in this sandbox. **I could not cryptographically verify any tag signature from this environment.** The tag objects themselves are real (`git tag -v` still prints the tagger line: e.g. driftwood's v1.1.0 tagger is `policy-as-versioned release bot <releases@policy-as-versioned-driftwood.invalid>` at unix time `1787677714`, message `policy-composition ticket 18: driftwood's first signed composed artefact. MODERATE baseline, 285 recorded holes, 0 refusals, 0 ungoverned namespaces.`). tuppence's v1.1.0 message names the same ticket and adds `1 recorded ungoverned namespace (tuppence-reset)`; ludlow's matches driftwood's shape (0 ungoverned).
- The repos' own most recent drift-sample runs independently attempted gitsign verification of these same v1.1.0 tags and **failed** fact 2 for driftwood and ludlow with `certificate is not yet valid` at the tagger's own timestamp (see the Drift section below) — i.e. the estate's own tooling also could not verify these tags at sample time, for a clock/cert-validity reason, not a "signature absent" reason.

Byte-identical across all three, confirmed by diff (only the party name/label differs, templated):
- `composed/policies/v4.0.0/{cage-netpol,cage-tier,posture-trust-boundary,require-nonroot,stamp-posture}.yaml` — identical except the `policy-as-versioned.dev/composed-for:` label value.
- `composed/governed-namespace-guard.yaml`, `composed/orphan-guard.yaml` — same, label-only diff.
- `.github/scripts/read-two-pins.py`, `.github/rulesets/observation-lane.json`, `.github/rulesets/README.md` — byte-identical.
- `gitops/composed/kustomization.yaml`, `gitops/platform/kustomization.yaml` — byte-identical.
- `kind/<name>.yaml`, `scripts/lib.sh`, `scripts/render_composed.py`, `scripts/reset.sh`, `scripts/up.sh` — identical templates, only the party/cluster name substituted.
- `git-server/Dockerfile`, `git-server/deployment.yaml`, `git-server/lighttpd.conf` — identical templates, only the name substituted (`<name>-git:local`, `/cgi-bin/git/<name>.git`).
- `gitops/platform/platform-pin.yaml`, `gitops/platform/platform-distribution.yaml` — same platform pin (`tag: v2.0.1`, `commit: 533dccb0a823001b396fd60ab08014bf75065a37`) in all three; wording differs slightly (driftwood's is the original, tuppence/ludlow's comment attributes the split to "ecosystem ticket 42, widening ticket 40" while driftwood's says only "ecosystem ticket 40" — driftwood's comment predates ticket 42 and was not updated).
- `gitops/flux-system/gotk-sync-nist.yaml` — identical `nist` pin (`tag: v1.1.0`, `commit: 33a05df1f5241bca6ffbc1c69a70075cdb7a5819`) in all three, same identity-regexp annotation.
- `.github/workflows/cut-release.yml` — same trigger shape (`workflow_dispatch`), same checkout-of-parents pattern (platform/nist checked out at their pinned tag via `steps.pins.outputs.*_tag`, ico/feeds/insurer checked out with `fetch-depth: 0` and no ref) in all three (spot-checked driftwood vs tuppence; ludlow's opening matches).

---

## 1. party.yaml

driftwood (`units/driftwood/party.yaml`) is the fullest and the odd one out:
- Only driftwood declares a `size:` block: `turnover: {amount: 86000000, currency: GBP}`, `customers: 240000`, `data_subjects: 240000`, `headcount: 410`, `as_of: '2026-06-30'`. **tuppence and ludlow have no `size:` key at all** (confirmed: `grep -l '^size:'` over all three only matches driftwood).
- `appetite.tolerance`: driftwood £40,000; tuppence £15,000; ludlow £5,000 (ludlow's comment: "near-zero: the same control that Audits in driftwood Denies here").
- `baseline: MODERATE` for all three (identical wording/comment).
- `roles: [risk-bearer, adopter, publisher]` — identical for all three (tuppence/ludlow's party.yaml comment explicitly reasons about why `publisher` belongs given their own `publishes[]` exposure record).
- `inherits[]`:
  - platform `implementations` v2.0.1, nist `controls` v1.1.0, ico `feed/penalty-schema` v3 — identical across all three, same `since: '2026-08-28'`.
  - `feeds` `feed/threat-register`: **driftwood pins v2; tuppence and ludlow both pin v1.** This is a real, load-bearing version skew between driftwood and the other two (see evidence.json and renovate.json sections below for why).
  - **Only driftwood inherits a fifth parent**: `{party: insurer, kind: feed, name: quote-driftwood, version: "v1", since: '2026-08-28'}` — an insurer quote line. tuppence and ludlow have no insurer parent at all — no `quote-tuppence`/`quote-ludlow` line exists in their `inherits[]`, their `.github/rulesets`/scripts, or anywhere else searched.
- `publishes[]`: all three publish `{kind: feed, name: exposure, path: composed, payload_schema: null}`. **Only driftwood additionally publishes** `{kind: feed, name: forward-intel, path: twin/forward-intel, payload_schema: twin/forward-intel/payload.schema.json}` — tied to driftwood's unique `twin/` tree (§7).
- `overlay: {add: [], restate: []}` — empty and identical in all three.
- `reporting_currency: GBP` — identical in all three.
- No `trust_domain` field exists anywhere in party.yaml (or anywhere else) in any of the three repos — `grep -rn trust_domain` across all three trees returns nothing. The nearest concept found is a hardcoded SPIFFE trust-domain string `TRUST_DOMAIN = "acme.internal"` in `units/tuppence/reset/reach.py:16` — a Python constant local to tuppence's `reset/` subsystem (§8), not a party.yaml field, and absent from driftwood and ludlow entirely.

## 2. composed/ tree

Tree contents, identical shape in all three: `composed/HEADER.yaml`, `composed/evidence.json`, `composed/governed-namespace-guard.yaml`, `composed/orphan-guard.yaml`, `composed/policies/v4.0.0/{cage-netpol,cage-tier,posture-trust-boundary,require-nonroot,stamp-posture}.yaml`.

`composed/evidence.json` (`outcome: "composed"`, `party_artefact_errors: []` in all three):

| | driftwood | tuppence | ludlow |
|---|---|---|---|
| `parents[]` count | 5 | 4 | 4 |
| `members[]` | 7 (identical set/order) | 7 | 7 |
| `holes[]` | 285, all `status: recorded` | 285, same set | 285, same set |
| `refusals` / `cages` | `[]` / `[]` | `[]` / `[]` | `[]` / `[]` |
| `ungoverned` | `[]` | **`[{"namespace": "tuppence-reset", "status": "recorded"}]`** | `[]` |
| `prices[]` count | **4** | **2** | **2** |

- driftwood's 4 `prices[]` entries: `ico/penalty-schema` (amount 1,787,177.08 GBP, `per_customer.amount` 7.45 GBP, tier `isolated`, unchanged), `feeds/threat-register` (amount 19,558.55 GBP, per_customer 0.081 GBP, tier `baseline`), `insurer/quote-driftwood` (`kind: premium`, amount 113,403.30 GBP, per_customer 0.47 GBP, attachment £40,000, limit £3,000,000, one exclusion on pl-2/ra-3, conditions void-on-ac-6-lapse and £25,000 uplift-on-cm-6-lapse, `priced_against` platform 1.1.1 + driftwood's own exposure v1.1.0), and `twin/forward-intel` (`kind: twin`, amount 1,897,646.11 GBP, per_customer 7.91 GBP, residuals ladder baseline/restricted/quarantine/isolated, policy_basis "loosest tier whose caged residual (37952.92 GBP) is within the tolerance (40000.00 GBP)").
- tuppence's 2 entries: `ico/penalty-schema` amount **9,039,791.02 GBP** (`per_customer: null`), tier `isolated`; `feeds/threat-register` amount 222,574.31 GBP (`per_customer: null`), tier `isolated`.
- ludlow's 2 entries: `ico/penalty-schema` amount **9,039,791.02 GBP** (`per_customer: null`, identical to tuppence's), tier `isolated`; `feeds/threat-register` amount **318,229.78 GBP** (`per_customer: null`), tier `isolated`.
- **`per_customer` is `null` for every price line in tuppence and ludlow, and populated for every price line in driftwood** — directly downstream of §1's finding that only driftwood declares `size.customers` in party.yaml (composition can't divide by a customer count that isn't declared).
- Open question worth flagging to auditors: tuppence's and ludlow's `ico/penalty-schema` amounts are bit-for-bit identical (9039791.01976426) despite different appetites (£15,000 vs £5,000) and no declared `size`/turnover for either — I could not find, in the time available, what input produces that specific number for both (no shared turnover fixture was located in either repo; `platform/risk/appetite.json` lives in the `platform` unit, out of this task's scope, and was not read). Their `feeds/threat-register` amounts differ (222,574.31 vs 318,229.78) despite pinning the identical `feeds` parent SHA (`50a0b330a730f4f9ee9520561b0c05c8be4c9268`) and both being tier `isolated` — so whatever drives that number is party-specific and not simply a function of the shared feed/tier. This wasn't resolved from the adopter repos alone.
- `limits[]` — identical two entries in all three: `two-publisher-conflict` (`status: open`, count 1) and `pinned-parent-lacks-rendered-versions` (`status: closed`, count 0, checked 1).

`composed/HEADER.yaml` diffs (driftwood vs tuppence vs ludlow) are exactly what evidence.json implies: parent list, party name, `ungoverned-namespaces`, `selection-policy: 1.0.0` line (present only for driftwood — HEADER only records a selection-policy version where one exists), and the mirrored price totals. tuppence's `total: 9262365.331667097`; ludlow's `total: 9358020.798349269`; driftwood's `total: 3704381.737952101` (lower than tuppence/ludlow despite driftwood's much larger declared turnover — because driftwood's `ico` line alone (1.79M) plus feeds (19.6K) plus premium (113K) is far below tuppence/ludlow's undivided ico line of 9.04M each).

## 3. gitops/

Directory shape identical: `gitops/apps/{kustomization.yaml,namespace.yaml,nist-pin-configmap.yaml,version-configmap.yaml,+pod.yaml|risk-appetite-configmap.yaml}`, `gitops/composed/{composed-set.yaml,kustomization.yaml}`, `gitops/flux-system/{gotk-sync.yaml,gotk-sync-nist.yaml}`, `gitops/platform/{kustomization.yaml,platform-pin.yaml,platform-distribution.yaml}`.

**Flux sources and pins** (`gitops/flux-system/gotk-sync.yaml`, the repo's own canonical GitRepository+Kustomization):
- driftwood: `url: https://github.com/policy-as-versioned-driftwood/driftwood`, `ref.tag: v1.0.0`, `ref.commit: 92034b0927eb0c15aa9760deddbe6da2960038f0`, Kustomization `path: ./apps`.
- tuppence: same shape, `ref.tag: v1.0.0`/`9862d846332031d7cb5cf38894d3b0ed321928df`, Kustomization `path: ./gitops/apps`.
- ludlow: same shape, `ref.tag: v1.0.0`/`7bd9973be43de0b5d1d13b7eb46a1a60b01516ec`, Kustomization `path: ./gitops/apps`.
- **None of the three point at their own newest published tag** (`v1.1.0` exists in all three, per §above) — all three self-pins sit one tag behind.
- **driftwood's Kustomization path (`./apps`) is stale relative to tuppence's and ludlow's (`./gitops/apps`).** tuppence's file carries an explicit comment naming the reason: "`./gitops/apps`, NOT `./apps` (ecosystem ticket 42, found by running driftwood's ticket-40 dry run against the real remote). This object's source is the github.com remote above, whose tree root holds `gitops/`, so `./apps` resolves to nothing there and the Kustomization never becomes Ready." Ludlow's file carries the identical comment. **driftwood's own `gotk-sync.yaml` still says `path: ./apps`** and carries none of this explanatory comment — i.e. the bug ticket 42 found and fixed in tuppence and ludlow was never back-ported to driftwood, the repo where it was first found. Against driftwood's own real GitHub remote (`https://github.com/policy-as-versioned-driftwood/driftwood`) this Kustomization would, by the tuppence/ludlow comment's own logic, never reconcile.
- `gitops/composed/composed-set.yaml` (the ResourceSet installing each repo's own composed policy set) pins each repo's **own** tag+commit at **v1.1.0**, not v1.0.0 — i.e. this file and `gotk-sync.yaml` disagree on which of the repo's own two tags is current, identically in all three repos (driftwood: `eacae33ca3a1662819651d56cdb54a4771fe13f1`; tuppence: `751522b3bca98c40373c9bcb8b72ab376ab3be5b`; ludlow: `a800a58e2547b41f8c9b77a91b93eb9d820e8569` — each matching that repo's real v1.1.0 tag exactly).
- `composed-set.yaml`'s own commentary differs meaningfully: driftwood's copy says wiring the composed set into `gitops/apps` (so it reconciles unattended) is "ticket 42's widening, **once tuppence and ludlow carry flux-operator too**" — future tense, framed as pending. tuppence's and ludlow's copies say the opposite has already been decided: "still opt-in after ticket 42's widening, **and deliberately**. kind-tuppence/kind-ludlow carries neither Kyverno nor flux-operator, and `gitops/apps` health-gates with `wait: true`, so listing this there would break the offline touring demo" — i.e. driftwood's comment is stale documentation describing a decision (permanent opt-in for tuppence/ludlow) that tuppence's and ludlow's own files say has already been made and is final, not pending.
- Platform pin (`gitops/platform/platform-pin.yaml`): identical `tag: v2.0.1` / `commit: 533dccb0a823001b396fd60ab08014bf75065a37` in all three.

**Namespace / tiers** (`gitops/apps/namespace.yaml`):
- driftwood: `name: driftwood`, `policy-as-versioned.dev/institution: driftwood` (comment: "e-comm / PCI+GDPR institution (Audit-heavy risk skin)"), `posture.acme.io/tier: "isolated"`.
- tuppence: `name: tuppence`, institution comment "fintech / FCA+PCI+GDPR institution (toward-strict risk skin)", tier `"isolated"`.
- ludlow: `name: ludlow`, institution comment "US health / HIPAA institution (Deny-heavy, strictest risk skin)", tier `"isolated"`.
- All three land on the same tier label (`isolated`) — the strictest rung — despite different appetites and different regimes; each namespace's comment explains this is because each party's strictest `proposed_tier` across its own `prices[]` is `isolated` (tighten-only rule, ADR-0022).
- Only tuppence and ludlow carry `gitops/apps/risk-appetite-configmap.yaml` (`tuppence-risk-appetite`/`ludlow-risk-appetite`, `data.toleranceGBP: "15000"`/`"5000"`, `data.skin`), explicitly documented as "a human/audit-readable mirror of `../../platform/risk/appetite.json`'s tolerance ... `platform/risk/appetite.json` remains the single source of truth." **driftwood has no such configmap** — consistent with driftwood's party.yaml comment that its appetite fixture in `platform/risk/appetite.json` "is retired, because whose money is at risk is this party's own declaration and nobody else's" (ADR-0021). So driftwood has migrated off the platform-fixture-mirror pattern that tuppence and ludlow still use.

**The live workload pod — a real, asymmetric fix**:
- All three have a top-level `deploy/pod.yaml` ("A real `<name>` workload manifest, pinned to policy-version 4.0.0"): driftwood names Pod `checkout-svc`, tuppence `payments-svc`, ludlow `patient-records-svc`.
- **Only driftwood also has `gitops/apps/pod.yaml`** (referenced in `gitops/apps/kustomization.yaml`'s `resources:` list) — a maintained mirror of `deploy/pod.yaml`, explicitly namespaced (`namespace: driftwood`) so Flux actually applies it into the governed namespace. Its header comment ("WIRED LIVE 2026-08-31, ticket 40 answer item 2") records that this pod was declared but never reconciled onto any cluster until that date, and that doing so surfaced a real defect: `securityContext.runAsNonRoot: true` on the plain `nginx` image (whose entrypoint runs as root) makes the kubelet refuse to start the container at all, with no writable path for a non-root user even if it could start. The fix, present in driftwood's `deploy/pod.yaml` **and** `gitops/apps/pod.yaml`: `runAsUser: 101` (nginx's own built-in account) plus two `emptyDir` volumes (`/var/cache/nginx`, `/run`).
- **tuppence's and ludlow's `deploy/pod.yaml` still carry the pre-fix shape**: `securityContext: { runAsNonRoot: true }` with no `runAsUser` and no volumes, containers as a one-line list with no volume mounts. Neither has a `gitops/apps/pod.yaml` at all, and neither's `gitops/apps/kustomization.yaml` lists any pod resource (tuppence's and ludlow's `resources:` list `risk-appetite-configmap.yaml` where driftwood's lists `pod.yaml`). So for tuppence and ludlow: (a) the workload pod is never wired into Flux/the governed namespace at all, unlike driftwood, and (b) even if it were applied as-is, it carries the same crash-on-start defect driftwood's own comment says was found and fixed on driftwood's copy — this fix was not carried over. This is a concrete, evidenced asymmetry, not a naming-only difference.

## 4. .github/workflows

Same eight-workflow shape is NOT uniform: **driftwood has two extra workflows tuppence and ludlow lack**: `twin-sweep.yml` and `verify-identity-regexp.yml`. Common to all three: `shift-left.yml`, `release.yml`, `renovate-run.yml`, `propose-tier.yml`, `drift-sample.yml`, `cut-release.yml`.

Triggers/cron (`grep cron:`):
| workflow | driftwood | tuppence | ludlow |
|---|---|---|---|
| `renovate-run.yml` | `11 6 * * *` | `13 8 * * *` | `07 9 * * *` |
| `propose-tier.yml` | `47 6 * * *` | `49 8 * * *` | `43 9 * * *` |
| `drift-sample.yml` | `20 6 * * *` | `22 8 * * *` | `16 9 * * *` |
| `twin-sweep.yml` | `5 7 * * *` | — (no file) | — (no file) |

(all three also fire `propose-tier.yml` on `pull_request: {types: [closed], paths: [party.yaml]}`, and `shift-left.yml`/`verify-identity-regexp.yml` on PR/push events, not cron.) Each unit's daily crons are offset ~2 hours later than the previous (driftwood ~06:xx UTC, tuppence ~08:xx UTC, ludlow ~09:xx UTC) — consistent with staggered onboarding order, not a fixed shared schedule.

**Commits / signing, per workflow (spot-checked driftwood in full, diffed against tuppence/ludlow):**
- `cut-release.yml` (`workflow_dispatch` only): installs a pinned gitsign binary by checksum (`GITSIGN_VERSION`/`GITSIGN_SHA256`, no marketplace action), creates a gitsign-signed annotated tag. Same in all three.
- `release.yml` (`on: push: tags: [v*.*.*]`, plus `workflow_dispatch`): verifies the pushed tag's gitsign signature; checks out with `fetch-depth: 0, fetch-tags: true`. Same shape in all three (spot-checked driftwood/tuppence headers).
- `renovate-run.yml` (cron + `workflow_dispatch`, `permissions: contents: write`): runs self-hosted Renovate (`actions/setup-node`), no gitsign/cosign step of its own (the commit it produces is a normal git commit; the tag/signature step is `cut-release.yml`'s job, separately triggered).
- `drift-sample.yml` (cron + `workflow_dispatch`, `permissions: contents: write`): reads the platform pin, checks out `platform` at that pinned tag into `.platform-src` (`ref: ${{ steps.platform.outputs.tag }}`), installs pinned gitsign to run `gitsign verify-tag`, appends a signed sample commit (`[skip ci]`) — this is what populates `drift/samples.jsonl` (§6).
- `twin-sweep.yml` (driftwood only, cron `5 7 * * *`, `permissions: contents: write`): checks out `hub` at `ref: main` plus `hub/.estate-clone/driftwood` with `fetch-depth: 0`; installs pinned gitsign to sign its own observation commit. No equivalent exists for tuppence/ludlow.
- `verify-identity-regexp.yml` (driftwood only, triggered on PRs touching `release.yml`/`scripts/verify-identity-regexp.sh`, or push to `main`): checks out `fetch-depth: 0, fetch-tags: true`, installs pinned gitsign, runs `scripts/verify-identity-regexp.sh` (also driftwood-only, §5) against real tags plus negative shapes. Not present for tuppence/ludlow — **tuppence and ludlow have no equivalent self-check of their own `EXPECTED_IDENTITY_REGEXP` constant**, though both `release.yml` and `shift-left.yml` still define and use such a regexp.
- `propose-tier.yml`: driftwood checks out `ico`/`feeds`/`insurer` at `ref: main`, with a comment "ticket 57 renamed the default branch; ticket 62 owns the real pin" on the feeds/insurer lines. tuppence checks out `ico` at `ref: main` but `feeds`/`insurer` at **`ref: ecosystem/thin-slice`** — a non-default branch, not `main`. (ludlow's equivalent lines were not individually re-checked line-by-line in this pass; flagged as an open item below.)

**`shift-left.yml` — the biggest real divergence found, checkout-ref handling for the PR's own repo checkout:**
- driftwood: `- uses: actions/checkout@v4` / `with: { path: driftwood }` — no `fetch-depth`, no explicit `ref` (relies on the default `pull_request` checkout, which is the ephemeral merge commit).
- tuppence: `with: { path: tuppence, fetch-depth: 0 }` — full history, still the default (merge-commit) ref, no explicit pin.
- ludlow: `with: { path: ludlow, ref: ${{ github.event.pull_request.head.sha }} }` — **explicitly pins to the PR head SHA**, not the default merge commit, and adds a second step immediately after: `fetch this PR's base commit too (ticket cs-28 needs the OLD platform pin, not just the new one)` → `git -C ludlow fetch --depth=1 origin ${{ github.event.pull_request.base.sha }}`. Only ludlow does this explicit head/base pinning; driftwood and tuppence do not.
- Adopter-gate env var naming also differs: driftwood uses `EVIDENCE_EXPECTED_IDENTITY_REGEXP` / `EXPECTED_ISSUER`; ludlow uses `ADOPTER_GATE_IDENTITY_REGEXP` / `ADOPTER_GATE_ISSUER` for the equivalent constant (tuppence's naming was not individually confirmed in this pass — the driftwood-vs-tuppence diff output was large and I did not re-isolate that one line for tuppence; flagged as open below).
- The `.github/scripts/adopter-gate.py` (`adopter_gate.py` in ludlow — **note the filename itself differs: hyphen in driftwood/tuppence, underscore in ludlow**) is not shared code: line counts are 1087 (driftwood), 661 (tuppence), 1213 (ludlow) — `shift-left.yml`'s own comment in tuppence confirms this is intentional: "each adopter's own adopter-gate.py CLI has evolved independently."
- Only tuppence has `.github/scripts/render-evidence-comment.py` (driftwood and ludlow do not; both apparently render the PR-body evidence comment a different way — not independently confirmed by reading driftwood's/ludlow's equivalent step in this pass).
- Only ludlow has `.github/scripts/trusted_root.json` (driftwood and tuppence do not) — not opened in this pass; flagged as open below.

## 5. renovate.json customManagers

tuppence's and ludlow's `renovate.json` are **byte-for-byte identical** to each other. Both differ from driftwood's in three ways:
1. driftwood's has `"enabled": false` plus a `description` explaining a real incident: "two Renovates fought over one branch on 2026-09-01 — the hosted app rebased `renovate/feeds-threat-register-2.x`, consumed the retry checkbox, and cannot run `postUpgradeTasks`... The self-hosted runner (`renovate-run.yml`) overrides this with `RENOVATE_FORCE={"enabled":true}`." tuppence/ludlow have no `enabled` key and no such description — i.e. **this collision fix was applied only to driftwood's config**; tuppence/ludlow have not (yet, or ever) needed/received it.
2. driftwood declares **4** `customManagers`; tuppence and ludlow declare **2**. driftwood's extra two: (#3) a regex manager over `party.yaml` that bumps the `feeds`/`<feedName>` per-feed tag pin (`party: feeds, kind: feed, name: ..., version: "vN"`), and (#4) an equivalent manager for the `insurer`/`<feedName>` quote pin. **tuppence and ludlow have neither** — matching §1's finding that neither has an insurer parent at all, and directly explaining why their `feeds/threat-register` pin is stuck at `v1` while driftwood's has moved to `v2`: only driftwood's Renovate config can ever propose that bump.
3. driftwood's has a `"postUpgradeTasks"` block (`bash .github/scripts/complete-feed-bump.sh`, `fileFilters: ["composed/**"]`, `executionMode: branch`) that tuppence/ludlow entirely lack — so a Renovate-driven bump PR in tuppence/ludlow (of `nist` or `platform`, the only two things their config can bump) has no automated step re-rendering `composed/`; whether/how that re-render happens for them was not confirmed in this pass.
4. `packageRules[0].matchDatasources` is `["git-refs", "git-tags"]` in driftwood (both datasources used by its 4 managers) vs `["git-refs"]` only in tuppence/ludlow (matching that they have no `git-tags`-datasource manager).
`.github/scripts/complete-feed-bump.sh` exists only in driftwood's `.github/scripts/` — not present in tuppence or ludlow.

## 6. drift/samples.jsonl

| | driftwood | tuppence | ludlow |
|---|---|---|---|
| total lines | 12 | 6 | 6 |
| "legacy" pre-ticket-60 lines (schema: `ts/reachable/revision/ready/subjects`, no `run`/`facts`/`verdict`) | 3 (2026-08-10, -11, -13) | 0 | 0 |
| "real" five-fact runs (`kind: flux.five-facts/v1`, 3 lines each = 3 subjects sampled per run) | 3 runs: `33556795181` (2026-09-01T20:46Z), `33558850420` (2026-09-01T21:07Z), `33624104359` (2026-09-02T11:25Z) | 2 runs: `33556798230` (2026-09-01T20:43Z), `33558854558` (2026-09-01T21:04Z) | 2 runs: `33556801679` (2026-09-01T20:43Z), `33558858820` (2026-09-01T21:04Z) |

**driftwood's most recent run (`33624104359`) is materially better than tuppence's/ludlow's most recent runs**, and it is a run neither of the other two has a counterpart for (it ran ~14–15 hours after their latest):
- driftwood run `33624104359`: subject `driftwood` itself → **verdict FAIL**, but only because `fact_2_tag_signature_verified_at_the_source_boundary` observed `False` ("`v1.1.0: signature or certificate chain did not verify at tagger time 1787677714 ... certificate is not yet valid`"); facts 1, 3, 4, 5 all `observed: true` (16/16 rendered objects present, byte-equal to the offline render, and in the Flux inventory). Subjects `platform` and `nist` in the same run both → **verdict PASS**, all 5 facts true.
- tuppence run `33558854558` and ludlow run `33558858820` (their latest): **every one of the 3 subjects in each run is verdict FAIL**, and not just on fact 2 — facts 3, 4 and 5 are `observed: false` across the board: `objects_declared: 16`, `objects_absent: [all 16 policy object names]`, `inventory_entries: 4`, `"16 of 16 rendered objects are absent from the cluster"` / `"...are in no Flux inventory"`. I.e. on these samples, tuppence's and ludlow's composed policy sets were not actually applied to (or not reconciled onto) their sample clusters at all, whereas driftwood's was fully applied and only failed the certificate-timing check.
- Own-tag fact 2 specifically: driftwood's and ludlow's own-repo subject both failed with the identical `certificate is not yet valid` error (driftwood tagger-time `1787677714`, ludlow tagger-time `1787677815` — ~101s apart); tuppence's own-repo subject in its equivalent run actually shows `fact_2 ... controller_verdict: 'true', observed: True` (tuppence's own tag verified) but still fails overall on facts 3/4/5 (0/16 objects present). So the two failure modes (cert-not-yet-valid vs whole-composed-set-absent) are independent and both real, and tuppence exhibits only the second.
- I did not go further back through driftwood's earlier two real runs or the 3 legacy-schema lines in detail beyond confirming their schema/timestamps above — flagged as not fully covered.

## 7. selection-policy/ and twin/ (driftwood only)

Neither `selection-policy/` nor `twin/` exists in tuppence or ludlow (confirmed both by directory listing and by `grep -rl "selection-policy\|selection_policy"` over tuppence/ludlow, which returns only their unrelated `.github/rulesets/` files that happen to contain the substring in prose).

- `selection-policy/`: `PIN.yaml` (`policy_version: 1.0.0`), `VERSION` (`1.0.0`), `README.md`, `selection_policy.py`. `PIN.yaml`'s own comment explains why this pin lives here rather than on `party.yaml` or via a Renovate `git-refs` manager: the party schema forbids unknown keys, and there's no second repo to track since the package is in-repo; `composed/HEADER.yaml` records the selected version (`selection-policy: 1.0.0`, confirmed present only in driftwood's HEADER, §2).
- `twin/`: `currency.yaml` (`perspectives: {driftwood: GBP}`), `PIN.yaml` (`twin_version: 0.1.0`, `twin_tag: twin/v0.1.0`, `tag_cut: false` — the tag doesn't exist yet), `signals.yaml` (a hand-maintained pin→dated-signal lookup table, `version: 2`, feeding driftwood's twin-sweep), `emit-forward-intel.py`, `verify-twin-scenarios.sh`, `verify-twin-overlay.sh` (top-level, also driftwood-only), `forward-intel/{bump.yaml,payload.schema.json,rule.yaml,v1/}`, `orgs/driftwood/`, `world/{components,meta.yaml,propositions,world_models}`, `VENDORED.md`.
- This is the concrete substrate behind driftwood's unique `publishes[].forward-intel` record (§1) and its unique `twin`-kind price line in `composed/evidence.json` (§2), and the reason driftwood alone has `twin-sweep.yml` (§4).

## 8. reset/ (tuppence only)

`reset/` exists only in tuppence: `authorizationpolicy.yaml`, `destinationrule.yaml`, `openbao-role.yaml`, `reach.py`, `README.md`, `up.sh`, `verify-reach-secrets.sh`, `workloads.yaml`. Not present in driftwood or ludlow.
- `reach.py` implements "the posture gate as pure, offline-testable logic (ticket 17)": an Istio `AuthorizationPolicy` (`source.principals`) and an OpenBao JWT role (`bound_claims["sub"]`) both matching a `spiffe://…/posture/<vN>/*` glob, parsed directly out of the two real manifests. `TRUST_DOMAIN = "acme.internal"` is defined at `units/tuppence/reset/reach.py:16` — the one place anything resembling a "trust domain" appears in any of the three repos (see §1 note on the absent `trust_domain` field).
- This whole subsystem is what produces the `ungoverned: [{"namespace": "tuppence-reset", "status": "recorded"}]` entry unique to tuppence's `composed/evidence.json` (§2) — `tuppence-reset` is a namespace this reset subsystem stands up outside the governed-namespace guard, and composition records it as an explicitly-known ungoverned namespace rather than silently ignoring it.
- Not independently verified against a cluster (would require `kind create`/`up.sh`, out of scope for a read-only pass); reported as static file content only.

## What I did not get to (explicit gaps)

- Did not fully line-by-line diff `propose-tier.yml`, `release.yml`, or `cut-release.yml` for ludlow (only driftwood-vs-tuppence was diffed in full for these three; ludlow's opening steps were spot-checked and matched driftwood/tuppence's shape, but its `ico`/`feeds`/`insurer` checkout `ref:` values were not individually re-confirmed the way tuppence's were).
- Did not open `.github/scripts/render-evidence-comment.py` (tuppence-only) or `.github/scripts/trusted_root.json` (ludlow-only) — flagged as present/unique but not read.
- Did not confirm tuppence's exact `EVIDENCE_EXPECTED_IDENTITY_REGEXP`-vs-`ADOPTER_GATE_IDENTITY_REGEXP` env-var naming (confirmed for driftwood vs ludlow only); the driftwood-vs-tuppence `shift-left.yml` diff was very large and I read it only in summary, not to that specific line.
- Did not trace what produces the identical tuppence/ludlow `ico` price (9,039,791.02 GBP) or the differing `feeds` prices, despite identical parent pins and appetite differences — the pricing logic itself lives in the `platform` unit (out of this task's three-repo scope) and was not read.
- Did not attempt any cluster-based verification (no `up.sh`, no `kind create`, per the read-only constraint) — everything in §6 (drift samples) is the repos' own historical recorded output, not independently reproduced here.
- Did not read the 3 legacy-schema `drift/samples.jsonl` lines in driftwood beyond their schema/timestamps, and did not diff driftwood's two earlier real runs (`33556795181`, `33558850420`) against its latest in detail.
- `git tag -v` could not verify any tag (see top of file) — no attempt was made to reach Rekor or otherwise verify the gitsign/Sigstore signatures out-of-band; only the tag object's plaintext (tagger, message) was read.
