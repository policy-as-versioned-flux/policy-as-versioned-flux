# Assessment — Operability and Adoptability

Dimension: fit for purpose for four real audiences.
Date: 2026-09-02. Citable line: `TRUTH 2026-09-02T10:11Z run=21 hub=7b92990 ... pass=57 fail=7 skip=18 excluded=2 total=84`.
Method: read the thirteen maps under `review/understand/`, then re-derived every claim below from primary sources
(the hub working tree at `7b92990`, `git show origin/main:…` for run-21 captures, the eight fresh unit clones under
`scratchpad/units/`, and read-only `gh`).

---

## 0. Moving parts, counted

Every figure here is from a command a skeptic can re-run.

| Thing | Count | Command |
|---|---|---|
| GitHub repos in the eco-system | 9 (hub + 8 units) | `clone-estate.sh:23` `UNITS=(platform driftwood tuppence ludlow nist ico feeds insurer)` + hub |
| GitHub organisations | 9 (one per repo) | `talk/README.md:11-30`, `github-live` map |
| `verify*.sh` the gate discovers | 84 (16 under `verify/`, 68 across the units), 2 excluded | `find verify -name 'verify*.sh' \| wc -l` = 16; per-unit find = 45+3+4+4+4+3+3+2 = 68; matches `total=84` in the TRUTH line |
| GitHub Actions workflows | 37 | `ls .github/workflows/*.yml units/*/.github/workflows/*.yml \| wc -l` |
| Python, units | 28,490 lines | `find units -name '*.py' -not -path '*/.git/*' -exec cat {} + \| wc -l` |
| Python, hub (`twin/` 33,872 + `tests/` 18,623 + `verify/`+`talk/` 3,738) | 56,233 lines | same method per directory |
| Shell, units | 11,246 lines | `find units -name '*.sh' … \| wc -l` |
| Distinct Kubernetes CRD kinds in `platform/` YAML | 5 projects' CRDs: Flux (`GitRepository`, `Kustomization`, `HelmRelease`, `HelmRepository`, `OCIRepository`), flux-operator (`ResourceSet`, `Instance`), Kyverno (`ValidatingPolicy`, `MutatingPolicy`, `GeneratingPolicy`, `PolicyReport`), SPIRE (`ClusterSPIFFEID`, `ClusterFederatedTrustDomain`, `ClusterStaticEntry`), Istio (`PeerAuthentication`, `AuthorizationPolicy`) | `grep -rhno '^\s*kind: [A-Za-z]*' platform --include='*.yaml' \| sort \| uniq -c` |
| Controllers the live demo stands up on one KinD cluster | Flux (4 controllers) + SPIRE + Istio + OpenBao + Kyverno + flux-operator + Dex + Pomerium + a bespoke `gitsign-verifier` + a `git-server` pod + a WAF placeholder image | `talk/up.sh:60-70`, `platform/{identity,engine,access}/up.sh` |
| Per-adopter code an org must carry | ~2,300 lines of its own Python, 6–8 workflows, 31–94 YAML files | `find <adopter> -name '*.py' … \| wc -l` → driftwood 2,321 / tuppence 2,422 / ludlow 2,270 |

**Total: ≈ 85,000 lines of Python and 11,000 lines of shell across 9 repos, 37 workflows and 84 verify scripts,
to demonstrate a thesis about not writing bespoke tooling.** That is the headline operability fact.

---

## 1. Audience (a) — a conference audience watching a 20-minute talk

### Verdict: **partly fit** for a narrated talk; **not fit** for the live demo the RUNBOOK describes.

**What is genuinely good.** The seven-beat structure (NORTH-STAR §4) is the clearest thing in the estate: seven
numbered steps, each with one check, each slide carrying that check's own grade in the check's own words. The
"three outcomes, never two" discipline and the generated-not-authored deck (`talk/build_deck.py` writes it,
`talk/verify-demo.sh` refuses it if a figure is not in the capture behind it) are a real, defensible innovation —
this is the part of the estate most likely to survive contact with a hostile audience. 15 slides / 7 beats is
correct pacing for 20 minutes (`grep -c '^---$' talk/deck.md` = 14 separators).

Beat 1 works instantly on any laptop with nothing installed:
```
$ python3 platform/fair/fair.py summary platform/fair/scenarios/driftwood-cart-pii.json
{... "ale": 19558.5, "var95": 30947.9, "tvar": 34086.7, "carried": 34958.4 ...}   # 0.155s total
```

Real cluster evidence does exist on a clock, in the adopters' own `drift-sample.yml` lanes: `driftwood/drift/samples.jsonl`
run `33624104359` (2026-09-02) records a real ephemeral KinD cluster `kind-dsample-33624104359` in which
`fact_1_ready_at_the_pin_on_the_real_remote` and `fact_2_tag_signature_verified_at_the_source_boundary` were
observed **true** against `https://github.com/policy-as-versioned-nist/nist` at `v1.1.0@33a05df`. That is a
showable, honest fact.

**Why it is not fit today.** Findings O1, O2, O3, O4 below. In short: the headline claim of the 2022 thesis
(≥3 versions coexisting at runtime) is undemonstrable by construction; the committed deck reads seven grey
"could not look" slides when five of the seven checks actually pass; the provenance beat structurally cannot
see one of the estate's four publishers' tags; and the only documented bring-up reconciles a fabricated
in-cluster git server, not the signed GitHub remote the narration claims.

---

## 2. Audience (b) — a real adopter organisation

### Verdict: **not fit**.

Day 1 for an org that wants to pin NIST's controls and the platform's policies:

1. Create a GitHub org (the estate's own convention — `talk/README.md:11-13`, one org per party).
2. Author a `party.yaml` against `platform/party/schema.json` (`additionalProperties: false`).
3. Copy ~2,300 lines of Python, 6–8 workflows and 31–94 YAML files from an existing adopter. There is no
   template repo, no scaffold, no `adopter-quickstart`, and **no onboarding document anywhere**:
   `grep -ril 'onboard|getting started|quick start|how to adopt|day 1' --include='*.md'` across all eight unit
   repos returns **zero hits**.
4. Copy the adopter gate. It is not shared code: `driftwood/.github/scripts/adopter-gate.py` 1,087 lines,
   `tuppence/.github/scripts/adopter-gate.py` 661 lines, `ludlow/.github/scripts/adopter_gate.py` 1,213 lines —
   three divergent forks, documented in-repo as having "evolved independently".
5. Stand up KinD + Flux + SPIRE + Istio + OpenBao + Kyverno + flux-operator + Dex + Pomerium, plus the bespoke
   `gitsign-verifier` controller, before any cage can be shown.

**Time-to-first-cage** is therefore not measurable from any document, because no document states it and no
script measures it. What is measurable: the estate itself has never stood that stack up on a clock (finding O8),
and the last recorded attempt required a human at a laptop.

**Reusability of the "shared discipline" is better than it looks.** I checked whether `platform/` is entangled
with the three demo adopters. 21 of 40 `platform/*.py` files mention `driftwood|tuppence|ludlow`, but inspection
shows the references in the largest (`compose/composition.py`, 77 mentions) are all comments/docstrings or
selfcheck fixtures below `def selfcheck()` at line 2617. Only three hard-coded adopter *sets* exist estate-wide:
`platform/identity/verify-federation.sh:47`, `platform/computed-semver/gate.py:967`,
`platform/computed-semver/comparison_window.py:347` — the last two inside selfchecks. **The engines are
parameterised; the surrounding operational scaffolding is not.**

---

## 3. Audience (c) — a real regulator or intelligence publisher

### Verdict: **partly fit** — the best-designed adopter surface in the estate, undermined by packaging.

**Strengths, verified.** The feed envelope is small, closed and well-argued: seven required fields,
`additionalProperties: false`, and no in-band `signature` field because "a signature cannot cover itself"
(`platform/feeds/schema.json`). The publisher contract is documented in one page (`feeds/README.md:20-70`):
where files live, what `rule.yaml`/`bump.yaml` mean, the bump ladder, the tag convention, and that discovery
is `publishes[]` on `party.yaml` with no central catalogue. `bump.py selfcheck` runs 21 cases. A publisher's
own verify runs offline in seconds on a stock laptop — I ran it:
```
$ bash ico/verify-penalty-feed.sh
PASS: ico penalty schema signed+versioned, fair.py consumes it unmodified, a schema bump moves the £, …
```

**Why only partly fit.** Findings O12 (the envelope contract has no independently fetchable home — a publisher's
own verify SKIPs without a sibling `platform` checkout) and O13 (ico's own README documents the retired
ed25519 `schema/` mechanism, not the `penalty-schema/` envelope adopters actually pin). There is no
publisher SDK or starter repo; a new regulator copies `ico` or `nist` by hand.

---

## 4. Audience (d) — ControlPlane / the owner, as a consultancy asset or reference architecture

### Verdict: **not fit as a reusable asset; partly fit as a demonstration and an argument.**

The single blocking fact is O5: **the hub has no licence.** All eight unit repos carry Apache-2.0
(`ls units/*/LICENSE` = 8). The hub — which holds the thesis, the PRD, all 24 ADRs, `NORTH-STAR.md`,
the truth surface, and 56,233 lines of Python including the entire `twin/` — carries none:
```
$ git ls-files | grep -i license      # (no output)
$ gh api repos/policy-as-versioned-flux/policy-as-versioned-flux/license
{"message":"Not Found", … "status":"404"}
```
A public repo with no licence is "all rights reserved" by default. Nothing in this estate's most valuable
half can be lifted into a client engagement, quoted in a proposal, or forked by a prospect.

What *is* reusable, honestly: the feed envelope and its bump ladder; the three-outcome truth-surface
discipline and the capture/deck-refusal mechanism; `fair.py`; the composition engine's refusal set;
`tier_pr.py`'s propose-never-dispose AST guard. What is bespoke to the demo: every `up.sh`, the `git-server`,
the three adopter gates, the demo party names, and the `gitsign-verifier` (which is explicitly time-boxed
in-repo to "die before it earns a release train of its own").

---

## 5. Documentation, for a newcomer

| Doc | Size | Newcomer verdict |
|---|---|---|
| `README.md` | 342 words | Good. Correct "start here" table, one-breath decision list. Its "**no bespoke tooling**" claim is contradicted by `gitsign-verifier` (O6). |
| `NORTH-STAR.md` | 1,517 words | Excellent structure (one sentence, participants, seven principles, what the demo must show). Two participant rows are now stale (O9). |
| `CONTEXT.md` | 6,623 words, 633 lines, 5 headings | Too long to navigate. One section ("Core thesis terms") runs 502 lines with no index and no anchors. Its very first entry defines "Party" as "any of the **six** units" (O9). The `adrs-glossary-code` map found four separate places where CONTEXT.md contradicts shipped code. |
| `docs/PRD.md` | 4,153 words | Strong and honest (§1.1 names the 2022 shortfalls). Predates the eco-system re-baseline. |
| `docs/HISTORY.md` | 2,353 words | The best newcomer document in the estate. Real commits/PRs/tags, records its own corrections-of-corrections. |
| `talk/RUNBOOK.md` | 1,613 words | Half-superseded (§2's beat table carries a SUPERSEDED banner), and §0's CLI list is incomplete (O11). Its §1 description of `driftwood/scripts/up.sh` is factually wrong (O4). |
| `talk/deck.md` | 15 slides | Currently all-SKIP (O2). |
| Unit READMEs | 15–132 lines | driftwood's is stale (O17); tuppence's (15 lines) and ludlow's (16 lines) are ticket-number stubs; ico's documents a retired mechanism (O13). |

---

## 6. The ~5h cron delay and the KiND-only proof

**Cron delay, measured directly.** `.github/workflows/truth.yml:21` declares `cron: '47 5 * * *'`. Actual
scheduled firings (`gh run list --workflow truth.yml`): 2026-09-02T09:54:45Z (4h 07m late), 2026-09-01T10:27:22Z
(4h 40m late). Every document that says the clock runs at 05:47 is describing an intention, not an observation.
Consequence for operability: the TRUTH line's own timestamp (10:11Z) is ~4.5h after the declared time, so
"yesterday's number" and "today's number" can land within hours of each other, and a presenter cannot plan
around the clock. `verify/schedules/verify-schedules.sh` grades whether each clock ran *inside its period*,
which absorbs the delay honestly — but nothing anywhere states the delay as a known operating characteristic.

**The KiND-only proof is narrower than "KiND-only".** `truth.yml` installs python, gitsign, kyverno, cosign
and flux — `grep -i kind .github/workflows/truth.yml` returns **nothing**. The gate never installs `kind` and
never creates a cluster, so on the citable run every cluster-asserting script is a structural SKIP. Run 21's
18 skips include 12 whose reason is literally `kind cluster 'driftwood' is not listed by kind get clusters`.
The only real-cluster observation on any clock is the three adopters' `drift-sample.yml` lanes
(`driftwood/.github/workflows/drift-sample.yml:127` `kind create cluster --name "${name}"`), which produce the
five-fact samples — 12 samples in driftwood, 6 each in tuppence and ludlow, total.

Nothing in the estate has ever run on a managed cluster, and no document claims otherwise. That is honest, but
it means every "the workload keeps running, caged tighter" claim rests on a single-node KinD node with
`hostNetwork` semantics that differ from any real cluster. For audience (b) this is the difference between a
demonstration and a reference architecture.

---

## 7. Findings

### O1 — The thesis's headline runtime claim cannot be demonstrated at all today (critical)

`platform/distribution/versions.yaml:29-50` declares exactly one version (4.0.0); 2.0.0/2.0.1/3.0.0 and two
patch backports were retired 2026-08-29 for two independently-observed live defects. The consequence is visible
in run 21's grades: three checks SKIP for a reason that is *not* an absent cluster —

- `platform/distribution/verify-coexistence.sh` → `SKIP: … distribution/versions.yaml declares one version (4.0.0); coexistence needs two declared versions to show si…`
- `platform/distribution/verify-retirement.sh` → `SKIP: distribution/versions.yaml declares one version (4.0.0), so a retirement would leave an empty allow-list…`
- `platform/shift-left/verify-shift-left.sh` → `SKIP: distribution/versions.yaml declares one major line (4.0.0), so a target has no ±1 neighbour…`

Multi-version coexistence, prune-on-retire and the ±1 shift-left window are three of the seven "-ables" and
the single most-cited claim of the 2022 talk (`CONTEXT.md:153-155` calls ≥3 coexisting versions "the crux of
the original implementation"). None can be shown on stage, with or without a cluster, until a second line is
declared. This is *owned* — `.scratch/ecosystem/issues/58-…md:9` decision (1) is exactly "declare a second
policy line so coexistence, retirement and shift-left have a subject" — but ticket 58 is `Status: prepared`,
i.e. waiting on the owner, and ticket 63 is blocked behind it.

**Remedy:** the owner answers ticket 58 decision (1). Ticket 63's isolated-default flip forces a major that
can be that line, so the cost is one decision, not one build.

### O2 — The committed deck shows seven grey slides while five of its checks pass (major)

`git show origin/main:talk/deck.md` footer: `run=local · hub=5b1a891 · 2026-08-31T17:04Z`, and every beat
comment reads `status=SKIP`. Run 21's own captures grade those checks PASS, PASS, PASS, FAIL, PASS, PASS, PASS
(`git show origin/main:talk/captures/verify_e2e_verify-e2e-step7-honesty.out`, last line). The gate catches
this — `verify_demo_verify-demo.out` ends `FAIL: talk/deck.md has been hand edited or is stale; run python3 talk/build_deck.py`,
and that is one of run 21's seven fails. `talk/deck.html` (untracked, `git ls-files talk/deck.html` → nothing)
is staler still: `hub=00ecffc · 2026-08-29T01:56Z`.

If the talk were given today from the committed artefacts, the audience would see seven "could not look" slides
for an estate whose checks mostly pass — the opposite of the overclaiming the discipline was built to prevent,
but equally untrue.

**Already owned:** ticket 66 owns the *mechanism* (grade the deck against the run its TRUTH line names).
Nothing owns the *artefact*: no scheduled step rebuilds or commits the deck, and `talk/deck.html` is not
regenerated at all.

**Remedy:** rebuild and commit the deck from run 21's captures as part of landing ticket 66, and either
regenerate `deck.html` in the same step or delete it so it cannot be opened stale.

### O3 — The provenance beat structurally cannot see the `feeds` publisher's signed tags (major)

`verify/e2e/verify-e2e-step6-provenance.sh:88`:
```sh
tag="$(git -C "$ESTATE/$u" tag -l 'v*.*.*' 2>/dev/null | sort -V | tail -1)"
[ -n "$tag" ] || { queued+=("$u"); continue; }
```
`feeds` publishes more than one feed, so by its own documented convention its tags are `<feed>/vX.Y.Z`
(`feeds/README.md:38-41`). `git -C units/feeds tag -l` returns `threat-register/v1.0.0` and
`threat-register/v2.0.0` — both real, both gitsign/Rekor-verifying (per the `publishers` map, re-derived there
with `gitsign verify-tag`). The glob `v*.*.*` cannot match either. Run 21's capture therefore prints
`ok   no signed tag yet, honestly queued for cut-release.yml: feeds` and the beat's PASS line says
`7 of 8 anchored identity regexps matched … and feeds have no signed tag yet`.

This is an instrument fault, not an estate fault, and it is silent-by-construction: no number of feed releases
will ever change the verdict. It understates the estate on the audience-facing provenance slide, and it would
mislead anyone reading beat 6 about how many publishers actually sign.

**Already owned:** none found. `grep -rl 'v\*\.\*\.\*'` across `.scratch/ecosystem/issues/` returns nothing.

**Remedy:** widen the glob to `'*v[0-9]*.[0-9]*.[0-9]*'` (or read the tag from each unit's `party.yaml`
`publishes[]`) and re-grade.

### O4 — The presenter's runbook misdescribes the only live bring-up it documents (major)

`talk/RUNBOOK.md:57-60` states the first bring-up step is "KinD `driftwood` + Flux, **pointed at the real
`policy-as-versioned-driftwood` GitHub repo** (mo-09 retired the in-cluster git-server this used to seed)".

The script at the unit repo's HEAD does the opposite. `driftwood/scripts/up.sh:32-38` `git init`s a fresh
throwaway repo from the local `gitops/` tree and tags it `v1.0.0`; line 74 `docker build`s a `git-server`
image; line 78 applies its Deployment; lines 93-101 apply a `GitRepository` whose `url` is
`${GIT_URL_IN_CLUSTER}` = `http://git-server.flux-system.svc.cluster.local/cgi-bin/git/driftwood.git`
(`driftwood/scripts/lib.sh:11`). `grep -n 'github.com' driftwood/scripts/up.sh` matches only a comment.

So the live estate a presenter brings up reconciles from a git repo created seconds earlier on the same laptop,
carrying an *unsigned* local tag — while the runbook tells the presenter to say it is reconciling the real,
gitsign-signed remote. `driftwood/README.md:26-40` describes the git-server accurately, so the code and the
unit README agree; the hub's presenter-facing runbook is the wrong one.

**Already owned:** none found (no ticket mentions `up.sh`'s source).

**Remedy:** either correct RUNBOOK §1 to say what `up.sh` does, or add a `--remote` mode that points the
`GitRepository` at the real GitHub URL with the real signed tag and lets the `gitsign-verifier` gate it —
which is the beat the talk actually wants.

### O5 — The hub, the most valuable half of the estate, has no licence (major)

`git ls-files | grep -i license` → no output. `gh api repos/policy-as-versioned-flux/policy-as-versioned-flux/license`
→ `404 Not Found`. All eight units carry Apache-2.0 (`ls units/*/LICENSE | wc -l` = 8). The hub is public
(`gh api … --jq .visibility` → `public`) and holds `NORTH-STAR.md`, `docs/PRD.md`, all 24 ADRs, `CONTEXT.md`,
`twin/` (33,872 lines), `verify/`, `talk/` and `tests/` (18,623 lines).

**Already owned:** none. `grep -ril 'licen' .scratch/ecosystem/issues/` → no matches.

**Remedy:** add `LICENSE` (Apache-2.0, matching the units) and a one-line note in README. Ten minutes.

### O6 — The estate's signature linchpin is bespoke, unversioned, root-running tooling (major)

`README.md`'s decisions line claims "**no bespoke tooling**". But the only mechanism that verifies the only
signature the estate has is bespoke: `platform/identity/gitsign-verifier/verify_gitsign.py`, 417 lines, run as
a controller. Its README states the reason honestly — Flux `GitRepository.spec.verify` speaks only OpenPGP and
returns `unsupported signature type: x509` on a real gitsign tag, observed live on source-controller v1.9.3.

The packaging is the finding. `platform/identity/gitsign-verifier/deployment.yaml:58-84`: a stock
`python:3.13-alpine` image, `apk add --no-cache git openssl` **at pod start** (so the pod needs egress to the
Alpine mirrors to become Ready), the program mounted from a ConfigMap, running **as root** with
`readOnlyRootFilesystem: false` — the comment says "true nowhere else in this package". In an estate whose
first principle is "everything is always caged", the component that decides which policy sources are trusted
is the least caged thing in the cluster.

This is disclosed in-repo as a `ponytail` with a named upgrade path (build and gitsign-sign an image, pin by
digest, tighten to `runAsNonRoot`). It is a fitness finding anyway: no adopter security review passes this,
and it is the one component an adopter cannot avoid installing.

**Already owned:** the upgrade path is written in the deployment comment; no ticket carries the packaging.
`grep -rl 'gitsign-verifier' .scratch/ecosystem/issues/` returns exactly one file, ticket 73, which is about
the verifier rejecting a tag whose certificate postdates its tagger time — a correctness question, not the
image/root/egress question raised here.

**Remedy:** either cut and sign an image for it, or say plainly in README that "no bespoke tooling" has one
named exception and why.

### O7 — The adopter surface is copy-paste, contradicting the "config-base" claim (major)

`platform/README.md:11-14` promises "the governance machinery every institution inherits as a *pinned, signed
dependency* (the `config-base` pattern) … so the same apparatus is inherited rather than copy-pasted per
institution."

Measured: `wc -l` on the three adopter gates gives 1,087 (driftwood), 661 (tuppence), 1,213 (ludlow) — three
forks of the same idea, documented in-repo as having "evolved independently". Total adopter-side Python is
2,321 / 2,422 / 2,270 lines. `.github/workflows` counts are 8 / 6 / 6 and the sets differ (only driftwood has
`twin-sweep.yml` and `verify-identity-regexp.yml`). `gitops/flux-system/gotk-sync.yaml` `path:` is `./apps` in
driftwood and `./gitops/apps` in the other two (ticket 42's fix, never back-ported to the repo where the bug
was found). `renovate.json` differs across all three.

What is inherited is the *policy content* (`composed/policies/v4.0.0/*.yaml` are byte-identical templates).
What is copy-pasted is the entire operational apparatus — which is exactly what a real adopter has to own.

**Already owned:** partially — the divergence is acknowledged in-repo; no ticket proposes consolidating.

**Remedy:** decide whether the adopter gate is platform-published code (then publish it as a versioned artefact
the adopters pin, which is the estate's own doctrine) or genuinely per-adopter (then stop calling it
config-base). Either answer is defensible; the current state is neither.

### O8 — The KinD proof is never exercised by the truth surface (major)

`grep -i kind .github/workflows/truth.yml` → no matches. The clock installs python 3.12 + `pyyaml` +
`jsonschema` + gitsign 0.17.1 + kyverno 1.18.2 + cosign 3.1.3 + flux, and runs `talk/verify-all.sh`. It never
installs `kind` and never creates a cluster, so 12 of run 21's 18 skips are the structural
`kind cluster 'driftwood' is not listed by kind get clusters`, and `verify/e2e/lib.sh:23`'s `cluster_up()`
(ephemeral cluster `pav-e2e`) can never fire on the clock.

The number the estate cites as "what works" therefore grades the offline half of the estate plus whatever the
adopters' own lanes wrote into `drift/samples.jsonl`. That is honest — the SKIPs say so — but it means
`pass=57` contains almost no live-cluster observation, and no reader of the TRUTH line is told that.

**Already owned:** the SKIP reasons are honest and ticket 60 deliberately made the reconcile scripts grade the
sample lane *before* the cluster check, which is the right fix in miniature. Nothing owns "the clock should
stand up a cluster".

**Remedy:** either add a `kind`-capable job to `truth.yml` (Actions runners can run KinD), or state in
`talk/RUNBOOK.md §5` and the deck that the citable number is the offline half plus the adopters' sampled
facts — so nobody reads `pass=57` as 57 live observations.

### O9 — The census is wrong in the ratified ambition and in 15 places besides (minor)

NORTH-STAR §2's participant table still records the intelligence publisher as "*Does not exist yet.* Today the
platform publishes four of five feeds to itself" and the insurer as "*Does not exist yet.*" Both are now real
repos with real signed tags: `git -C units/feeds tag -l` → `threat-register/v1.0.0`, `threat-register/v2.0.0`;
`git -C units/insurer tag -l` → `v1.0.0` (all gitsign/Rekor-verifying per the `publishers` map). The document
every other document cites understates the estate by two participants.

`grep -rn 'six units|six real|six-org|the six |six parties'` across `CONTEXT.md`, `talk/README.md`,
`talk/RUNBOOK.md`, `clone-estate.sh`, `talk/up.sh` returns 15 hits. The first glossary entry in `CONTEXT.md:20`
reads "**Party** — Any of the six units of the estate", in a file that opens by saying "When a term here
conflicts with how someone is speaking, the term here wins." `clone-estate.sh:23` already lists eight.

**Already owned:** ticket 67 ("the record matches the surface") is open and is the natural home.

**Remedy:** one pass replacing "six" with "eight" and updating the two NORTH-STAR rows to name `feeds` and
`insurer` with their tags. NORTH-STAR §7 says "add a dated banner, do not rewrite history" — a dated update
line, as §8 already uses, is the in-house form.

### O10 — There is no onboarding document of any kind (minor)

`grep -ril 'onboard|getting started|quick start|quickstart|how to adopt|day 1|day one' --include='*.md'`
across all eight unit clones: **zero hits**. In the hub, two incidental hits (`docs/PRD.md:111`,
`docs/HISTORY.md:152`), neither an onboarding guide. `talk/README.md:120-128` has a four-line "Quick start"
but it is for touring the demo, not for adopting.

For audiences (b) and (c) this is the single cheapest missing artefact: a one-page "you are a regulator, here
is what you publish" and "you are an adopter, here is what you pin" would convert a demonstration into
something a prospect can act on.

**Already owned:** none.

### O11 — The documented prerequisites are incomplete; a newcomer's first run is degraded (minor)

`talk/RUNBOOK.md:70-73`: "Required CLIs: `git`, `kind`, `kubectl`, `flux`, `kyverno`, `python3`, `openssl`, `jq`."
`.github/workflows/truth.yml:65-90` additionally installs **gitsign 0.17.1**, **cosign 3.1.3** and
`pip install 'pyyaml==6.0.3' 'jsonschema==4.23.0'`. None of the three is mentioned in the runbook.

Observed on this machine: `python3 -c "import jsonschema"` → `ModuleNotFoundError: No module named 'jsonschema'`.
The committed deck's own beat 1 records the same symptom as its SKIP reason: "python lacks jsonschema/pyyaml".

**Remedy:** add the three to the RUNBOOK prerequisite list, or ship a `requirements.txt` and a
`talk/preflight.sh`. Given the estate's own doctrine ("a green that could not look is a red"), a missing pip
package silently converting checks to SKIP is worth a preflight.

### O12 — The publisher contract has no home a publisher can fetch (minor)

`feeds/verify-feeds.sh:26-32` searches sibling directories for a `platform` checkout and, failing to find one,
prints `SKIP: cannot look -- the envelope schema lives at platform/feeds/schema.json (ADR-0019) and no platform
checkout was found; set PLATFORM_DIR`. So an independent publisher — the one participant the north star says is
"loosely coupled … no participant reaches into another" — cannot validate its own envelope without cloning the
platform. `feeds/` carries no copy (`find feeds -name schema.json` → nothing).

The schema's `$id` is `https://policy-as-versioned.dev/schema/feed-envelope.json`; I could not check whether
that URL is served (no network fetch in scope), and nothing in the estate publishes to it.

**Remedy:** publish the envelope schema as a versioned, signed artefact in its own right (the estate's own
doctrine would make it `platform`'s `implementations` kind, pinned by publishers like any other parent), or
vendor a pinned copy into each publisher with a check that it matches.

### O13 — The regulator's own README documents the retired mechanism (minor)

`ico/README.md:20-31` describes only `schema/v1`, `schema/v2`, `schema/keys/ico-signing-key.pem` (an ed25519
demo keypair) and `sign.sh`/`verify.sh`. It never mentions `penalty-schema/` — the ADR-0019 envelope at v1/v2/v3
that every adopter actually pins, and whose v3.0.0 tag was cut 2026-08-31. ADR-0023's amendment named the ico
key retirement trigger as exactly that tag being cut; the trigger has fired and the artefacts remain
(per the `adrs-glossary-code` map, re-derived there).

A regulator reading this README to learn how to publish would build the wrong thing.

### O14 — The deck is never proven to render (minor)

`talk/verify-demo.sh:132` gates the marp render on `DECK_RENDER=1`. `grep -rn 'DECK_RENDER'` across the whole
hub returns exactly two hits, both inside that file — nothing ever sets it. So the gate proves the deck's
*content* is honest and never proves it becomes slides. When it does run, it calls
`npx --yes @marp-team/marp-cli@latest` — unpinned, in an estate that pins gitsign, kyverno and cosign by
version *and* SHA256 precisely because "an unpinned tool makes the number unreproducible".

**Remedy:** pin the marp-cli version and run the render on the clock, or drop the block and say the render is a
human step.

### O15 — The gate grades unreleased mainline, not what an adopter would pin (minor)

`clone-estate.sh:56` clones each unit's default branch. Its own comment at lines 36-38 still reads: "No signed
tag exists yet (ticket 09/12: known, accepted partial state) so this clones the default branch. Once a signed
v1.0.0 lands, pin it here." 24 signed tags now exist across the eight units (per the `github-live` map,
verified there with `gitsign tag -v` on every one). The TRUTH line records the unit *commits* it graded, so
this is disclosed, not hidden — but the estate's central claim is that consumption happens through a pinned,
signed dependency, and its own truth surface consumes unpinned HEAD.

**Remedy:** the comment's own instruction — pin the clone to each unit's newest signed tag, or add a second
gate lane that does, so "what the gate graded" and "what an adopter would get" are both on the record.

### O16 — The clock is ~4.5 hours later than every document says (minor)

`.github/workflows/truth.yml:21` → `cron: '47 5 * * *'`. `gh run list --workflow truth.yml`: scheduled runs
started 2026-09-02T09:54:45Z and 2026-09-01T10:27:22Z — 4h07m and 4h40m after the declared slot. The
`github-live` map measured the same 4.5–5.5h spread across 14 workflow/repo pairs fleet-wide. Every document
that states a clock time (`talk/README.md`, `feeds/README.md:60` "daily at 03:17 UTC", the gate-mechanics
per-unit table) is stating an intention.

Second-order: the hub's `truth.yml` concludes **failure** on every scheduled run, by design — the gate step
exits 1 when `fail>0` and a final `run: exit 1` step re-fails the job. That is honest, but it means the hub's
public Actions badge has been red continuously and there is no signal distinguishing "the estate has 7 reds"
from "the clock itself broke".

**Remedy:** state the observed delay once, in RUNBOOK §5, as an operating characteristic. Consider a
job-summary line that separates instrument failure from estate reds.

### O17 — driftwood's README is stale in the direction of over-claiming (minor)

`driftwood/README.md:18` — "Bring-up (idempotent, **offline-safe**, resettable)" and lines 26-40 describe the
in-cluster git server as the mechanism. `talk/RUNBOOK.md:12-25` explicitly retracts the offline-safe guarantee
for the whole estate ("**No venue-Wi-Fi independence — abandoned, mo-12**"). Line 74 still closes with "What's
here now vs later — Phase 0 (this ticket)", listing as future work things that have since shipped (the Kyverno
CEL policy set, the ico pin, the risk skin).

**Remedy:** fold into ticket 67's record-matches-surface pass.

---

## 8. Fixed since REVIEW-2026-08-31

Recording these honestly, since the prior review's findings are load-bearing for the map:

- **C1 (kyverno pin)** is fixed and proven: `truth.yml:46-47` pins `KYVERNO_VERSION: 1.18.2` with SHA256, with
  the incident written into the comment. None of run 21's seven fails is a cage-tier CEL compile error.
- **M1 (feeds and insurer mechanically unrunnable)** is substantially fixed: both repos now have registered
  workflows and real signed tags (`feeds` threat-register/v1.0.0 and v2.0.0, `insurer` v1.0.0).
- **M7 (reconcile SKIPs before reading the sample)** is fixed by ticket 60: the three `verify-reconcile.sh`
  now grade the five-fact sample first, which is why they moved SKIP→FAIL in run 21 — a *better* outcome, not
  a regression: the gate now sees a real red instead of a comfortable grey.

The prior review raised **no** operability, documentation, licence or audience-fitness findings. Every finding
in this assessment is new to the record except O1 (owned by ticket 58) and, in mechanism only, O2 (ticket 66).

---

## 9. Fitness verdict, per audience

| Audience | Verdict | The one sentence |
|---|---|---|
| (a) Conference | **partly fit** | The seven-beat, grade-carrying deck is the estate's best idea and the £ engine opens in 0.15s, but the committed deck reads seven greys, multi-version coexistence — the talk's headline claim — is undemonstrable by construction, and the only documented live bring-up reconciles a fake local git server. |
| (b) Adopter org | **not fit** | Nine orgs, 37 workflows, ~2,300 lines of your own Python, three divergent copies of the adopter gate, nine controllers on one KinD cluster, no onboarding document, and no measured time-to-first-cage. |
| (c) Regulator / publisher | **partly fit** | The envelope is small, closed, well-argued and the publisher's own verify passes offline in seconds — but the contract lives inside `platform`, there is no SDK or starter repo, and ico's own README teaches the retired mechanism. |
| (d) ControlPlane asset | **not fit as reusable; fit as an argument** | The engines are genuinely parameterised and several components are lift-worthy, but the hub carries no licence at all, so the half that matters cannot legally be reused, quoted or forked. |
