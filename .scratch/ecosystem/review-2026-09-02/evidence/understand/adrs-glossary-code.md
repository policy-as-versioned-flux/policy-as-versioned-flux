# ADRs × CONTEXT.md × code — cross-check

Scope checked: `docs/adr/0001`–`0024`, `CONTEXT.md` (both at
`/Users/cns/httpdocs/controlplane/policy-as-versioned-flux`), against the eight fresh unit
clones at `.../scratchpad/units/{platform,nist,ico,driftwood,tuppence,ludlow,feeds,insurer}`
(HEADs match the TRUTH run=21 line given in the brief). The original 2022-thesis reference
org repos (fleet, policy, ledger, storefront, reports, etc.) were **not** cloned or read — any
ADR whose only implementation would live there is marked **could not look**. No cluster was
used; findings are from static reading of policy YAML, Python and shell only, plus each repo's
own `git log`/`git tag`. `talk/` (the hub's dashboard/deck) was not read, so ADR-0008's actual
Grafana dashboard was not inspected — noted as could-not-look there too.

Read as a companion to `.scratch/ecosystem/map.md`, `REVIEW-2026-08-31.md`, and the
drift-review documents — this file does not repeat their findings and does not re-litigate
which side (ADR/CONTEXT.md vs. code) is "right"; it only states what each side currently says
and quotes the evidence.

---

## 1. ADR-by-ADR

Legend: **Status** is the ADR's own frontmatter/banner. **Superseded by** is what the ADR file
itself or CONTEXT.md says supersedes it. **Code** is what was actually found in the unit repos.

### ADR-0001 — Signed git tags, gitsign, tag+commit pin
Status: accepted, no banner. Not superseded.
Code matches. `platform/distribution/versions.yaml:77` carries `tag:`/`commit:` pair per
element; `driftwood/renovate.json`, `tuppence/renovate.json`, `ludlow/renovate.json` all carry
`customManagers`/`git-refs`-shaped config; `gitsign verify` is invoked in
`platform/.github/workflows/release.yml`, `driftwood/.github/workflows/release.yml`, and
checked offline by `driftwood/scripts/verify-identity-regexp.sh` and
`platform/verify-source-verification.sh`. `driftwood/gitops/composed/composed-set.yaml`
records `spec.ref.tag: v1.1.0` + `spec.ref.commit: eacae33ca3a1662819651d56cdb54a4771fe13f1`
and documents (in its own comments) that Flux `spec.verify` is deliberately absent because it
cannot verify gitsign — matching ADR-0001's known-limitation clause verbatim.

### ADR-0002 — Pinned + Renovate PR everywhere
Status: accepted. Not superseded.
Code matches: `driftwood/renovate.json:8`, `tuppence/renovate.json:6`, `ludlow/renovate.json:6`
all set `"automerge": false`.

### ADR-0003 — Kyverno `ValidatingPolicy`/CEL, not `ClusterPolicy`
Status: accepted. Not superseded.
Code matches: `grep -rl "kind: ClusterPolicy"` across all eight units returns nothing; every
policy object found (`platform/distribution/policies/*/*.yaml`, `platform/graded/policies/*`,
`*/composed/policies/*`) is `policies.kyverno.io/v1alpha1` `ValidatingPolicy`/`MutatingPolicy`/
`GeneratingPolicy`. Self-scoping is via `matchConditions` on the version label (e.g.
`platform/distribution/policies/v4.0.0/cage-tier.yaml:24-26`), not `matchConstraints.objectSelector`,
exactly as the ADR's corrected consequence says.

### ADR-0004 — Cloud plane / harvest collie, not Checkov
Status: accepted. Not superseded in text, but **the ecosystem map defers it**:
`.scratch/ecosystem/map.md:40` — "the cloud plane lands in tuppence after the Pod slice runs" —
i.e. future work, not current.
Code: **zero implementation found.** No Crossplane CRD (`*.aws.crossplane.io`), no RDS/S3
`ValidatingPolicy`, no `collie` reference anywhere in the eight units
(`grep -rli "crossplane"` hits only an unrelated OSCAL fixture filename path string; `grep -rli
"lula"` and `"collie"` return nothing at all). This is an honest, self-acknowledged gap (the map
says so) rather than a hidden one, but a reader of ADR-0004 alone, with "accepted" and no
banner, would not know the cloud plane doesn't exist yet in these repos.

### ADR-0005 — Flux Operator, `ResourceSet`
Status: accepted. Not superseded.
Code matches: `platform/distribution/versions.yaml` is a `fluxcd.controlplane.io/v1`
`ResourceSet` whose single `inputs[0].versions[]` array is ranged with `<< range $v := ... >>`
into per-version `GitRepository`+`Kustomization` pairs plus the orphan-guard, exactly as
described.

### ADR-0006 — Deterministic policy, no time-conditions
Status: accepted. Not superseded (ADR-0010 and ADR-0023 both explicitly say they *extend*, not
violate, this one).
Code: no time-based CEL (`request.time`/date literals) found in any `ValidatingPolicy`/
`MutatingPolicy` body under `platform/{distribution,graded}/policies/` or `*/composed/policies/`.
Consistent.

### ADR-0007 — Agent-assisted editorial governance
Status: accepted. Carries two inline "Correction" paragraphs already (2026-07-18) narrowing its
own original overclaim.
Could not look: the governance-agent demonstrator this ADR describes (`governance-agent/SPEC.md`)
lives in the original reference org, not in any of the eight cloned units, and was not cloned.
Nothing in the eight units contradicts it directly, but nothing confirms it either.

### ADR-0008 — Measurable = layered ground truth (four-panel dashboard)
Status: accepted. Not superseded.
Could not look: no Grafana dashboard JSON exists anywhere in the eight units (`find . -iname
"*.json" -path "*grafana*"` empty); the dashboard, if built, lives under the hub's `talk/`,
which was out of scope for this pass. `platform/oscal/result2oscal.py` (see ADR-0009) is present
and produces the OSCAL panel's input.

### ADR-0009 — OSCAL via C2P, not Lula
Status: accepted. Not superseded.
Code matches the "no Lula" half completely (`grep -rli lula` across all units: zero hits). The
"uses C2P" half is realized as **a hand-written offline reimplementation**, not the real
`compliance-to-policy-go` binary: `platform/oscal/result2oscal.py:8` describes itself as "the
offline, dependency-free twin of C2P `result2oscal`". This mirrors the estate's general
pattern of shipping offline twins of things that would otherwise need a cluster/network
(orphan-guard, governed-namespace-guard, etc.), so it is likely intentional and not a hidden
defect, but it means "C2P is used" should be read as "an offline reimplementation of C2P's one
mapping is used" for anyone auditing the actual dependency graph — the ADR's "we pin the v2 rc
and vendor the kyverno-plugin binary" line was not verified to be true of any CI workflow in
these units (no `kyverno-plugin` binary or C2P Go module reference found).

### ADR-0010 — Sunset: scheduled proposal, never scheduled application
Status: accepted, **no superseded banner**, unlike ADR-0014/15/16/18.
**Contradicted by CONTEXT.md itself**, not just by code — see §2.1 below. The `sunset:` field
this ADR defines does not exist anywhere in code (`grep -rn "sunset" .` across all eight units:
one unrelated code-comment hit, `platform/feeds/to_fair_scenario.py:17`). ADR-0024 replaces the
whole mechanism with unconditional EOL-ramp pricing and says so in its own title/decision, but
never states "this supersedes ADR-0010," and ADR-0010's file carries no banner.

### ADR-0011 — Release gate computes the bump; degraded publish
Status: accepted, with an inline "Superseding note, 2026-08-29" already folded into the same
file (not a separate banner) narrowing "refuse a weaker declaration" to "publish it degraded."
Code matches the superseding note: `platform/computed-semver/comparison_window.py:80-110`
implements `4.0.1-quarantine.1`-style prerelease suffixing, a dedicated
`is_degraded_publish()`-style reader, and a function that strips the suffix to recover "the
declared BASE number, which a degraded publish never rewrites."

### ADR-0012 — Composed artefact self-signed, pinned parent SHA
Status: accepted. Not superseded.
Code matches: `driftwood/gitops/composed/composed-set.yaml` pins `driftwood`'s own tag+commit,
`driftwood/composed/policies/` carries the rendered per-version members, and
`platform/compose/composition.py`'s `compose()` records `parents` (party+SHA) in its output
`header`/document (see line ~2247 `header = {..."parents": parents...}`).

### ADR-0013 — Regulator publishes baselines, adopter selects, bare catalogue id
Status: accepted, **no superseded banner**, despite CONTEXT.md explicitly saying "ticket 39
supersedes ADR-0013 ... on this point" (CONTEXT.md:199).
Code is **split**: the id-resolution and baseline-selection half is built and matches
(`nist/catalog/NIST_SP-800-53_rev5.2.0_{LOW,MODERATE,HIGH}-baseline_profile.json`,
`nist/catalog/CATALOG_VERSION.json`; `platform/compose/composition.py` resolves bare ids and
walks nested `controls` for `ac-6.10`-style enhancements). The **refusal** half that this ADR's
own text prescribes ("The composition refuses on a new hole") is **still live in code**,
contradicting the "never refuses, only prices" rewrite CONTEXT.md and ADR-0013's own successor
claim describe — see §2.2, the largest single finding in this pass.

### ADR-0014 — Unclaimed pod is caged not denied; governed namespace requires claim at CREATE
Status: **superseded in part**, banner present, pointing at ADR-0022 for "the CREATE deny on a
governed namespace."
Code: the CREATE-deny policy this ADR designed (`governed-namespace-requires-claim`,
`CREATE`-only, `Deny`) is still exactly what ships
(`platform/distribution/versions.yaml:150-176`) — ADR-0022 later **reinstated** the same Deny
under its own "review" addendum (see §2.1), so the code is simultaneously "what ADR-0014
designed" and "what ADR-0022, after a detour, put back." The orphan-guard half of this ADR (a
claim not in the array is denied) is unchanged in code and is the subject of §2.1/§2.3's larger
finding: CONTEXT.md says this is superseded to a cage; the shipped policy is still `Deny`.

### ADR-0015 — Adopter runs the proposer, opens the PR
Status: **superseded in part** (two banners: the "proposed Deny opens an issue" line, by
ADR-0022; and three named consequences, by ADR-0024).
Code: `platform/wargamer/wargamer.py`, `platform/honesty/proposer_bounds.py`,
`platform/risk/appetite.json` all exist as described. `propose-policy-pr.sh` /
`tier_pr.py`/`bump-nist-pin.sh` split (stop-at-diff vs. actually-opens-a-PR) matches the ADR's
own description of which rail does what.

### ADR-0016 — A subclass never restates a mutate
Status: **superseded in part** (§3, "carries no tier and no floor," by ADR-0022).
Code: `platform/compose/composition.py`'s `apply_restatements()` (~line 1073) refuses a
restatement of a non-`ValidatingPolicy` member and accepts only a stricter
`Audit`→`Deny` restatement on a `ValidatingPolicy`, matching the ADR. The tier/floor half is
superseded as declared; §3's "no tier, no floor" is now false in the sense that ADR-0022 gives
the adopter exactly one tighten-only `overlay.floor` knob, which `platform/compose/composition.py`
line ~2216 (`floor=(party_doc.get("overlay", {}) or {}).get("floor")`) reads.

### ADR-0017 — Control claim belongs to whoever ships the implementation
Status: accepted, **no superseded banner**, though CONTEXT.md (line 199) names it alongside
ADR-0013 as superseded "on this point" (refuse vs. price) by ticket 39.
Code: `resolve_claims()` (`platform/compose/composition.py:~1271`) reads claims from every party
that ships a member, including the adopter's own, and explicitly refuses a claim made against a
policy another party ships (`"kind": "claim-against-another-partys-policy"`, ADR-0017 cited in
the message). The "never refuses, only prices" successor claim is not reflected here either —
same finding as ADR-0013 (§2.2).

### ADR-0018 — Namespace manifest is the governed declaration
Status: **superseded in part** (§4, the narrowed CREATE claim rule, by ADR-0022).
Code: `driftwood/gitops/apps/namespace.yaml`-equivalent (governed label) pattern exists and is
read by `governed_namespaces()`/`ungoverned_namespaces()` in `platform/compose/composition.py`.
The composed artefact carries no namespace list, as designed — `header` in `composition.py`
carries `governed-namespaces` as advisory metadata only, matching "no namespace list… advisory
metadata."

### ADR-0019 — One feed envelope signed by the tag
Status: accepted. Not superseded.
Code matches exactly: `feeds/cve/v2/feed.json` (and every other feed file checked) has the keys
`kind, name, version, published_by, published_at, payload_schema, payload` verbatim. `ico`'s
`penalty-schema` migrated into this shape at `ico/penalty-schema/v3/feed.json` (present at tag
`v3.0.0`).

### ADR-0020 — Missing instrument refuses; missing behaviour is priced
Status: accepted. Not superseded.
Code matches: `platform/compose/composition.py:~2214-2223` wraps `compute_prices()` in a
`try/except Refused`, appends a `"kind": "missing-instrument"` refusal on catch, and the
in-file selfcheck at line ~2821 asserts `doc_no_band["refusals"]` contains a `missing-instrument`
kind. This is the one refusal path that is **not** contradicted by any later ticket.

### ADR-0021 — Twin emits scenario, estate selects tier
Status: accepted. Not superseded.
Code: `driftwood/twin/emit-forward-intel.py` and `driftwood/twin/forward-intel/v1/` exist;
`driftwood/twin/orgs/driftwood/` holds an overlay directory tree
(`components/`, `responses/`, etc.) per the ADR's per-adopter-twin description.
Not independently verified for tuppence/ludlow twin overlays in this pass (their `twin/`
directories were not opened) — noted as partial coverage, not a contradiction.

### ADR-0022 — Cage ladder: tier per namespace, isolated rung, floor, infra
Status: accepted. Marked "Provisional: the owner agreed without a reason." **This is the ADR
most in tension with the shipped code** — see §2.1 and §2.3.
Code: the ladder itself (`baseline, restricted, quarantine, isolated`), the
`namespaceObject`-sourced tier read, tighten-only mutation, and fail-closed-to-`isolated`
default all match precisely in `platform/graded/policies/cage-tier.yaml` and
`platform/graded/cage.py`, and are rendered per-version into
`platform/distribution/policies/v4.0.0/cage-tier.yaml`. The two "Added 2026-08-28 (review)"
bullets (ungoverned-namespace-still-baseline; no-claim-in-governed-namespace-is-Deny) are also
both implemented and live-tested (`platform/graded/verify-graded.sh:514-530`,
`platform/graded/tests/cage-tier/`). What is **not** reconciled is the orphan-guard's own
`Deny` (§2.1/§2.3) and the version-array retirement down to one version (§2.4), both of which
this ADR's own doctrine bears on but does not resolve in the shipped `distribution/` tree.

### ADR-0023 — Clock appends observations; one signature verified by a controller
Status: accepted, with an inline "Amendment, 2026-08-29" section (not a banner) naming three
live-but-scheduled-for-retirement signature mechanisms.
Code: all three named mechanisms are present and match the amendment's description —
`platform/computed-semver/evidence/*.json.bundle` (cosign evidence bundle),
`platform/feeds/keys/feeds-signing-key.pub.pem` + `.sig` files, `ico/schema/keys/ico-signing-key.pub.pem`
+ `ico/schema/sign.sh` + `.sig` files. **The stated retirement triggers have already fired but
the cleanup has not happened** — see §2.5, a second significant finding.

### ADR-0024 — Daily clock, caged observation lane, derived rejection ledger
Status: accepted. Not superseded.
Code: `platform/wargamer/rejection_ledger.py` and `platform/wargamer/rejection-decay.yaml`
exist (derived-ledger design); `platform/honesty/rejections.json` and
`DEFAULT_REJECTIONS` were checked for absence — **could not fully verify their deletion in this
pass** (not exhaustively searched for the exact constant name); `platform/honesty/proposer_bounds.py`
was read only for ADR-0015 purposes, not re-read for this specific removal. Flagged as an open
question rather than a finding either way (§3).

---

## 2. CONTEXT.md ↔ code contradictions (file:line both sides)

### 2.1 Orphan guard and governed-namespace-requires-claim: "cages to isolated" / "no CREATE
deny any more" vs. the shipped `Deny`

**CONTEXT.md says no refusal:**
- `CONTEXT.md:218-224` (Orphan guard) — "A deterministic catch-all that cages to **`isolated`**
  any workload whose `policy-version` label is not in the cluster's currently-installed version
  set... **the workload is not denied**... A pod carrying no claim at all is handled by the cage
  mutation itself, which renders the governed namespace's declared tier onto every pod at
  admission."
- `CONTEXT.md:228` — "The shipped `Deny` form is the July record, superseded by ADR-0022."
- `CONTEXT.md:234-243` (Governed namespace) — "There is no `CREATE` deny any more: a pod that
  claims nothing gets the namespace's tier, and a namespace that declares no tier renders to
  `isolated`."

**ADR-0022 itself, later in the same file, says the opposite for the no-claim case** (and this
text postdates the CONTEXT.md rewrite — see commit evidence below):
- `docs/adr/0022-...md:37-43` — "a pod created in a governed Namespace with NO
  `policy-as-versioned.dev/policy-version` claim is REFUSED by
  `governed-namespace-requires-claim`, promoted that day from `Audit` to `Deny`... **This is the
  one refusal the doctrine allows**."

**Code ships `Deny` for both the orphan guard and governed-namespace-requires-claim, and tests
assert the refusal, not a cage:**
- `platform/distribution/versions.yaml:117` — orphan guard, `validationActions: [Deny]`.
- `platform/distribution/versions.yaml:155-157` — `governed-namespace-requires-claim`,
  `validationActions: [Deny]`, `operations: ["CREATE"]`.
- `platform/distribution/render-orphan-guard.py` and `platform/distribution/verify-orphan-guard.sh`
  are the offline twin/beat for the same Deny form; `verify-orphan-guard.sh:49-50` fails the run
  if the orphan pod is **not** denied ("orphan pod (9.9.9) was NOT denied — a version outside the
  array could run").
- `platform/graded/verify-graded.sh:519-530` (the newest, ADR-0022-wave test, same 2026-08-28
  date as ADR-0022's own review addendum) live-asserts both: "a pod claiming an undeclared
  version is refused live by the orphan guard" and "a pod with no claim at all is refused live in
  a governed Namespace — silence is not an exemption."
- `platform/currency-controller/currency.py:26-27` (docstring, last touched 2026-08-23) — the
  `--action evict` re-admission path "hits the orphan-guard (version retired ∉ array) → **DENIED**".

**Root cause, dated:** `CONTEXT.md`'s Orphan-guard/Governed-namespace entries were written in
commit `20568bc` (2026-08-31 08:55:42 +0100, same commit that first added ADR-0022). ADR-0022's
"review" addendum reinstating the Deny was added three days *before* that, in commit `318052d`
(2026-08-28 22:15:08 +0100), but that commit touched **only** the ADR file (`git show --stat
318052d`: 1 file changed, the ADR). So CONTEXT.md's glossary was written after the Deny-reinstating
decision existed, yet still describes the pre-reinstatement position for governed-namespace, and
still describes the orphan guard's own Deny as superseded when nothing in the codebase or in
ADR-0022 actually retracts the orphan-guard's own `Deny` — only the CONTEXT.md prose claims it
is retracted.

**Net:** for a no-claim pod in a governed namespace, ADR-0022 and the code agree (refused); only
CONTEXT.md disagrees with both. For a pod claiming an out-of-array version (the orphan guard's
own subject), CONTEXT.md and ADR-0022's headline both claim it now cages to `isolated`; the code
and its own newest test suite (`verify-graded.sh`, same wave) still refuse it. Two different
mismatches, same two entries.

### 2.2 "Never refused, never counted" (holes, baseline widening) vs. `compute_holes` /
`check_baseline_widening` still refusing, citing ADR-0013

**CONTEXT.md:**
- `CONTEXT.md:196-200` (Baseline) — "A baseline control that nothing implements is a **hole**; a
  composition **prices** every hole, new or pre-existing, and **a new hole moves the tier, never
  refuses** (rewritten 2026-08-28, ticket 15; **ticket 39 supersedes ADR-0013 and ADR-0017 on
  this point**)."
- `CONTEXT.md:432-435` (Hole) — "Priced as the regulator's control weight... **Never refused,
  never counted; the earlier new-hole and widening refusals are gone.**"

**Code, unchanged, still refusing and citing the very ADR CONTEXT.md says is superseded:**
- `platform/compose/composition.py:1301-1323` — `compute_holes()`: "a new hole refuses
  (ADR-0013)"; appends `{"kind": "new-hole", ..., "needs_composition": True}`.
- `platform/compose/composition.py:1345-1361` — `check_baseline_widening()`: "a baseline widening
  is a reviewed decision and has no override (ADR-0013)"; appends `{"kind":
  "baseline-widening", ...}`.
- `platform/compose/composition.py:2189-2192` — both are called from the main `compose()` path
  and their output is concatenated into the top-level `refusals` list.
- `platform/compose/composition.py:2290` — `"outcome": "refused" if refusals else "composed"` —
  a non-empty `refusals` list (hole or widening included) sets the **whole composition's**
  outcome to `refused`, not merely a priced entry.
- `platform/compose/composition.py:3236-3247` — the module's own `selfcheck` asserts this live:
  a second composition that adds an unfilled control (`aa-3`) produces
  `doc2["outcome"] == "refused"` with a `new-hole` refusal naming `aa-3` — this is an executable
  test, not dead/vestigial code.

**Net:** the compose engine that ships in `platform/compose/composition.py` still implements
exactly the ADR-0013/0017 refuse-on-new-hole and refuse-on-widening design that CONTEXT.md
(citing "ticket 39") says has been replaced by pure pricing. `_regime_holes()`/`compute_prices()`
(the pricing path CONTEXT.md's rewrite describes) exists **alongside** the refusal path, not
instead of it — both run in the same `compose()` call.

### 2.3 Multi-version coexistence "≥3" vs. one declared version

- `CONTEXT.md:153-155` (Multi-version coexistence) — "A single runtime (cluster) must accept and
  evaluate **multiple policy versions simultaneously** (≥3), so old versions can be retired over a
  transition window... *The crux of the original implementation.*"
- `platform/distribution/versions.yaml:29-77` — the live `ResourceSet` array (the thing that
  actually installs `GitRepository`+`Kustomization` pairs on a cluster) has been reduced, by a
  dated, well-reasoned comment block, to **exactly one element**:
  `{ version: "4.0.0", tag: "policy/v4.0.0", commit: "64635d...", bump: "major" }`. The comment
  explains 2.0.0/2.0.1/3.0.0 and two never-cut backports were all retired 2026-08-29 because
  every pre-ADR-0022 body read the tier from the **pod's own forgeable label**, and a live probe
  showed a pod on 2.0.2 forging `posture.acme.io/tier=baseline` was admitted with `hostNetwork:
  true` and reached the API server, while an identical 4.0.0 pod was correctly clobbered to
  `isolated`.
- `driftwood/gitops/composed/composed-set.yaml:36-46` (driftwood's own composed-set
  `ResourceSet`) **does** currently declare three versions — `2.0.0, 2.0.1, 3.0.0` — pinned at
  driftwood's own historical tag `v1.1.0` (`composed-set.yaml`'s `GitRepository.spec.ref`), with
  a comment noting `4.0.0` is deliberately not yet added pending a follow-up PR. `git -C
  driftwood ls-tree v1.1.0 composed/policies` confirms `v1.1.0`'s tree does carry
  `composed/policies/v2.0.0` and `v3.0.0`; current driftwood `main` HEAD (`67bfc7a`) carries only
  `composed/policies/v4.0.0` on disk. This file is opt-in (`kubectl apply -k gitops/composed/`,
  not wired into `gitops/apps/kustomization.yaml`), so it is not part of the default reconcile —
  but if applied as documented, it would install the same three pre-ADR-0022 versions platform's
  own comment calls "Not safe, and unfixable as a patch," with the same forgeable-tier defect,
  because `driftwood/composed/policies/` for v2.0.0/v3.0.0 no longer exists on disk to have been
  patched.

**Net:** the thesis's own "crux" claim (≥3 versions coexisting) is not true of the platform's
currently-declared version set (exactly one, by deliberate, documented retirement for a real
safety defect). A three-version coexistence example does exist (driftwood's opt-in composed set,
pinned to a year-old tag) but it is the specific set platform's own comment says is unsafe to run.

### 2.4 "No consumer-side sunset field exists" (CONTEXT.md, ticket 13) vs. CONTEXT.md's own
unrevised "Project posture" section, and ADR-0010 carrying no banner

- `CONTEXT.md:404-406` (Supersede, added 2026-08-28 ticket 13) — "A publisher retires a version
  by publishing a newer one. A pin behind a newer published version is priced by the EOL ramp...
  **No consumer-side sunset field exists.**"
- `CONTEXT.md:561-564` ("Project posture" section, not touched by the ticket-13 rewrite) —
  "**Sunset = scheduled proposal, never scheduled application.** A fleet's array entry **may
  carry a `sunset:` date**; on that date a machine opens a retirement PR..." — cites ADR-0010
  directly.
- `docs/adr/0010-sunset-scheduled-proposals-not-application.md` carries **no superseded banner**
  (unlike 0014/0015/0016/0018), so a reader following ADR-0010 alone has no signal that its
  central `sunset:` field mechanism has been dropped.
- Code: `grep -rn "sunset" <all eight units>` returns exactly one hit, an unrelated code comment
  (`platform/feeds/to_fair_scenario.py:17`, "not a one-off sunset event"). No `sunset:` field,
  key, or reader exists anywhere. Code agrees with the ticket-13 rewrite (§404-406), not with the
  unrevised "Project posture" section or with ADR-0010's own text.

### 2.5 ADR-0023's stated key-retirement triggers have fired, but the retirement has not
happened

`docs/adr/0023-...md` (Amendment, 2026-08-29) names two key-based signers as "past the trigger
their own migration set and… waiting only on tags `cut-release.yml` cuts after a merge":

- **ico's schema key** — "Retires when ico has cut the `v3.0.0` tag those pins wait for: delete
  `schema/keys/`, `schema/sign.sh`, the `.sig` files and `verify-penalty-feed.sh`'s openssl
  block." `ico` **has already cut `v3.0.0`** (`git -C ico tag` → `v1.0.0`, `v3.0.0`; `git -C ico
  log -1 v3.0.0` → 2026-08-31, the same commit as `ico`'s current HEAD `9d09222`), and all three
  adopters pin it (`driftwood/party.yaml:53`, `tuppence/party.yaml:28`, `ludlow/party.yaml:29`
  all read `{ party: ico, kind: feed, name: penalty-schema, version: "v3" }`). Yet
  `ico/schema/keys/ico-signing-key.pub.pem`, `ico/schema/sign.sh`,
  `ico/schema/v1/penalty-schema.json.sig`, `ico/schema/v2/penalty-schema.json.sig`, and the
  `openssl pkeyutl -verify` block at `ico/verify-penalty-feed.sh:46` are **all still present** at
  that same `v3.0.0` tag/HEAD.
- **platform's feed key** — "Retires when the `feeds` party has cut the tags those pins wait
  for: delete `feeds/keys/`, the `.sig` files..." `feeds` has cut
  `threat-register/v1.0.0`/`v2.0.0` (`git -C feeds tag`), and all three adopters now pin `party:
  feeds` for `threat-register` (`ludlow/party.yaml:30`, `tuppence/party.yaml:29`,
  `driftwood/party.yaml:54`). Yet `platform/feeds/keys/feeds-signing-key.pub.pem`,
  `platform/feeds/verify-feeds.sh`, and six `.sig` files under `platform/feeds/{cve,eol,threat-register}`
  are all still present.

**Net:** this is not a contradiction between an ADR and CONTEXT.md, but between ADR-0023's own
stated condition and the state of the two repos it names — the trigger condition it describes
has been met, and the promised deletions have not happened.

---

## 3. Vocabulary: banned / undefined terms found in code

**Banned:** CONTEXT.md bans exactly one term outright — "Exemption" (`CONTEXT.md:57-65`, "a
banned concept... none, ever"). All 20 occurrences of "exemption" across the eight units were
read (`platform/posture/spire/clusterspiffeid-posture.yaml:22`,
`platform/distribution/render-governed-namespace-guard.py:18,87`,
`platform/compose/composition.py:36,1119-1120`, `platform/distribution/versions.yaml:173`,
`platform/graded/{verify-graded.sh:530, cage.py:33,196,225,374, policies/cage-tier.yaml:17,149,
tests/cage-tier/{resources.yaml:9,kyverno-test.yaml:16}}`, `platform/policy/verify-conditional.sh:2`,
and the three adopters' `composed/governed-namespace-guard.yaml:29`) — every one is a negation
("not an exemption," "never an exemption") or a reference to the deleted `render-exemption.py`.
**No live exemption mechanism was found; the ban holds in code**, which is itself worth recording
since the estate's own history (`.scratch/govern-what-you-dont-control/issues/05-...`) shows it
shipped one once.

**Heavily used, not banned, but overloaded without CONTEXT.md flagging the overload the way it
flags `org`:** "gate" (988 occurrences, 164 files) and "refuse"/"refusal" (757 occurrences, 136
files). CONTEXT.md's Cage entry says "**There is no gate**" (`CONTEXT.md:76`, about workload
admission specifically) while using "gate" 13 more times elsewhere in the same file for a
different mechanism (the release/adopter gate, the instrument-fault gate, the truth-surface gate)
that genuinely does refuse. This is internally reconcilable on a careful read (workload admission
vs. release/composition-time checks are different mechanisms) but, unlike `org`, CONTEXT.md never
states the overload explicitly, and §2.2 above shows the composition-time "gate" still literally
refuses whole compositions on a new hole — which is exactly the behaviour the Baseline/Hole
entries say is gone. A reader relying only on "there is no gate" would not expect
`compose()`'s `outcome: "refused"` path to exist at all.

**Used pervasively, never defined in CONTEXT.md or any ADR:** `ponytail:` — an inline
code-comment marker (69 occurrences across the units) that always introduces a named, deliberate
small gap or upgrade path (e.g. `platform/graded/policies/cage-tier.yaml:31-33`,
`platform/graded/cage.py` several places). It is used once, in passing, inside ADR-0015's prose
("The `ponytail:` upgrade path in `proposer_bounds.py` stays unbuilt") but never defined as a
term anywhere. Not a contradiction, but a load-bearing house convention with no glossary entry —
an auditor grepping for open gaps should know to grep `ponytail:` specifically.

**Referenced as an authority but not present in the repo it's cited from:** `spec.md`, cited
~15 times in `platform/compose/composition.py` (e.g. "see spec.md, 'Testing Decisions', 'One
seam'", "(spec.md, Resolution)") as the design authority for the composition seam. No file named
`spec.md` exists anywhere in the `platform` repo (`find . -iname spec.md` empty). It almost
certainly refers to a hub-side `.scratch/ecosystem/issues/<N>/spec.md` ticket document not
carried into the unit repo — plausible given the multi-repo estate, but not verified in this
pass, so recorded as **could not confirm** what `spec.md` actually is or whether its claims still
match `composition.py`.

**Tier names:** the ladder `baseline, restricted, quarantine, isolated, infra` is used
consistently everywhere it appears (`CONTEXT.md:78`, `docs/adr/0022`,
`platform/graded/{cage.py,policies/cage-tier.yaml}`, all four adopters' `composed/policies/*/cage-tier.yaml`)
— no drift found in the tier-name vocabulary itself, only in *who currently gets refused vs.
caged* at the boundary (§2.1).

---

## 4. What this pass did not cover

- The original 2022-thesis reference-org repos (`fleet`, `policy`, `ledger`, `storefront`,
  `reports`, `api`, `datastore`, `cloud`, `governance-agent`, `handbook-generator`,
  `pr-gate-action`, `c2p-collector`, `readiness-collector`, `renovate-config`) — not cloned, so
  ADR-0007's demonstrator and ADR-0004's "harvest" source were not directly inspected, only
  their described outcome in the units repos.
- `talk/` (the hub's gate/deck) — ADR-0008's actual Grafana dashboard, and the `TRUTH`
  line/capture files it's built from, were not opened.
- `tuppence/twin/` and `ludlow/twin/` overlay contents — only `driftwood/twin/` was opened for
  ADR-0021.
- `platform/honesty/proposer_bounds.py`'s current `DEFAULT_REJECTIONS` state (ADR-0024's claim
  that the fixture ledger is deleted) — not directly re-verified in this pass; flagged as open in
  §1's ADR-0024 entry rather than asserted either way.
- No ADR/CONTEXT.md cross-check was done against `insurer`'s or `feeds`' own code beyond what's
  quoted above (their repos were opened only for the specific greps shown); a full pass over
  `insurer/` and `nist/scripts/` was not performed.
- All findings are static-read only; nothing was run against a live or KiND cluster, so any claim
  above about live/admission behaviour is inferred from the policy YAML and the (also static)
  verify-script source, not from re-executing those scripts.
