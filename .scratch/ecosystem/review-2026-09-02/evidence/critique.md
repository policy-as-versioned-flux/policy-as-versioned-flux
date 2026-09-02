# completeness

# COMPLETENESS CRITIC — what the review did not examine

Working files: `/private/tmp/claude-501/-Users-cns-httpdocs-controlplane-policy-as-versioned-flux/8c6523c6-66de-4c91-94ed-4ceff16a6a76/scratchpad/review/completeness/` (`lm.py`, `lm2.py`, `sc_published.json`, `sc_A.json`, `sc_B.json`, `deck.md`).

---

## PART A — PROBES, PRIORITISED

### C1 (critical). Nobody fact-checked the external data. Two of the estate's anchor fines are wrong, and I measured the £.

`pound-engine` read the exact two numbers that drive driftwood's largest price (`assess/pound-engine.md:47`, `:497-501`) and reasoned only about the **arithmetic** over them. No dimension asked whether the data were still true. `units/ico/penalty-schema/v3/feed.json` `uk-gdpr/lower-tier.real_examples_gbp` publishes, under a note reading *"grounded in real public enforcement notices"*:

- **Doorstep Dispensaree £275,000** — reduced to **£92,000** by the First-tier Tribunal on 2021-08-09; liability at £92,000 confirmed by the Court of Appeal 2024-12-09. Collected penalty is one third of the published figure.
- **Clearview AI £7,552,800** — set aside in full by the FTT 2023-10-17 (no jurisdiction); ICO's appeal upheld by the Upper Tribunal Oct 2025 and **remitted to the FTT for the substantive appeal**; Clearview granted permission to appeal to the Court of Appeal 2025-12-19. As of today it is **not final and has never been collected**.

The payload schema has no litigation-status field, and `ico/verify-penalty-feed.sh` checks structure, not truth.

I ran the real production path (`ico/schema/to_fair_scenario.py` → `platform/fair/fair.py`), turnover 86,000,000:

| case | lm mode | ALE | driftwood exposure | insurer premium |
|---|---|---|---|---|
| as published | 773,782.53 | **1,787,177.08** | **3,704,381.74** | **113,403.30** |
| A: Doorstep = £92,000 | 755,692.87 | 1,746,535.33 | 3,663,739.99 | 111,625.23 |
| B: + Clearview dropped as not-final | 18,188.51 | **656,931.70** | 2,574,136.37 | **63,955.07** |

The "as published" row reproduces `driftwood/composed/evidence.json` exactly (1787177.0751717847 / premium 113403.3), so this is the live pipeline, not a model of it. **Case B moves the adopter's largest signed line by −63% and a second org's gitsign-signed quote by −44%**, and makes the twin the largest line.

**Probe.** Decide the rule ("a penalty under appeal is not a published fine" / "the final figure, not the notice figure"), add `status` + `final_as_of` to the payload schema, cut `ico` v4.0.0, and let the bump propagate. Re-run: `python3 lm2.py && python3 units/platform/fair/fair.py summary sc_B.json`. Then audit the other regimes' examples the same way (FCA/HHS figures in `v3/feed.json` were never checked either).

### C2 (critical). The digest's 13 verdicts predate the adversarial pass and none was rewritten; ~22 refutations have no artefact; one "refuted" finding is confirmed by the review's own evidence and by an open ticket.

`stat -f "%Sm %N" assess/*.md refute/*.md skeptic/*.md | sort`: every `assess/*.md` was written 14:15–14:42; every `refute/`+`skeptic/` file 14:25–16:52. The verdicts you were handed are pre-refutation text. Load-bearing verdict sentences that their own dimension later withdrew:

- `assess/security-spine.md:388` — "the one control that actually gates enactment is broken… rejects 5 of 24 genuine tags" (SS-01, listed refuted); it is also fix **#1** in that verdict's remediation order.
- `assess/scope-and-coherence.md:597` — "§4 step 3 … is foreclosed" (F1, refuted).
- `assess/operability-adoptability.md:57`, `:489` — "the committed deck reads seven grey" + "undemonstrable by construction" (O2, O1, both refuted).
- `assess/truth-surface.md:406` — remediation items (4) "pin the flux install" and (5) "move the hub cron" are the fixes for TS-M3 and TS-M5, both refuted.
- `thesis-fidelity` verdict (b) "no policy anywhere in the estate governs access control, data protection or key management" — `refute/TF-04.md` shows `verify/proportionality/policies/encrypt-at-rest-ludlow.yaml:27` is a `Deny` with a data-protection body, and notes the assessment's own §3.2 describes that file.
- `engineering-quality` verdict's copy-paste paragraph is EQ-03, refuted.

Only 18 of the ~40 refutations have a file under `review/`. Missing entirely: SS-01, TS-C2, TS-M3, TS-M5, TS-M9, TWIN-08, DS-F5, DS-F7, PE-03, PE-09, EQ-05, O1, O2, O6, F1, F7, F9, L1, P2, P12, P2-1/2-2/2-5. A reader cannot audit why those were withdrawn.

**SS-01 is the sharp one and I think the label is wrong** — see Part B.

**Probe.** Re-derive each verdict from the surviving set only, and require every "refuted" to name its artefact. Cheap: for each dimension, diff the verdict's claims against its own surviving list.

### C3 (critical). "≥3 coexisting versions" — the review's most-repeated critical finding — rests on an unquoted paraphrase nobody checked against the source.

`research/03-blogs-thesis.md:40-41` reads: *"The **runtime must support multiple policy versions simultaneously** — at least three semver versions — to allow "transitionary periods for old policy versions to be retired.""* Only the final clause is marked verbatim; **"at least three" is the transcriber's own words**, and the Medium post's own heading quoted two lines below says only *"Your runtime needs to support multiple policy versions 😱"*. `CONTEXT.md:154` then hardcodes it as **"(≥3)"** and calls it *"the crux of the original implementation"*.

I fetched the two primary sources that are fetchable today:
- `https://talks.cns.me/PolicyAsVersionedCode.html` — no minimum number, no retirement window; the seven "-ables" are confirmed verbatim.
- `https://blog.cns.me/posts/policy-versioned-code-mea-culpa…` — confirms the locked-door list verbatim: *"Access control. Data protection. Cryptographic key management."*
- `https://chrisns.medium.com/what-is-policy-as-versioned-code-306e0341290b` — **HTTP 403, could not look.** This is the one source that might say "three".

This single unverified word drives TF-01, TF-02, L7, F9, TS-M9, P4-1, O1, tickets 58/63, and four separate owner questions.

**Probe.** Open the Medium post in a browser (it 403s automation) and settle whether "three" is in it. If it is not, `CONTEXT.md:154` is stating a requirement the thesis never set, and ticket 63's cost changes accordingly.

### C4 (major). Substrate maturity was never graded. Every shipped policy is an alpha API that the next Kyverno minor already breaks.

`grep -rh "^apiVersion:" units/platform/distribution/policies/v4.0.0/*.yaml` → **10 × `policies.kyverno.io/v1alpha1`** (2 ValidatingPolicy, 2 MutatingPolicy, 1 GeneratingPolicy). 69 files estate-wide carry that API. `.scratch/ecosystem/issues/71-…md` (open, HITL) records: *"the composed v4.0.0 that all three adopters pin does not load on a 1.19 cluster at all"*, with two proven incompatibilities. `KYVERNO_VERSION: 1.18.2` (`driftwood/.github/workflows/drift-sample.yml:56`).

No dimension asked what a policy-as-a-versioned-**dependency** thesis owes its consumers about its own substrate's compatibility window — which is precisely the question the thesis exists to answer. No participant publishes a supported-version matrix.

**Probe.** Grade the estate on: (a) is the enforcement API GA; (b) does any published artefact declare its substrate range; (c) does a Kyverno bump go through the same computed-semver gate a policy bump does. Run `kyverno version` compatibility of `v4.0.0` against 1.18.2/1.19.x/1.20.x offline with the pinned CLI.

### C5 (major). No legal or naming realism was assessed, on nine public repos.

All nine repos are `visibility=public` (`gh api repos/policy-as-versioned-*/…`). There is **no disclaimer anywhere**: `grep -rli "not affiliated|no affiliation|fictional|fictitious|demonstration only" units/*/README.md units/*/party.yaml` → zero. `ico/README.md:4` says "**Role:** regulator — publisher"; the signed payload says `"authority": "ICO (Information Commissioner's Office)"`. The only recorded mitigation is one line in the drift-review evidence — `.scratch/drift-review-2026-08-27/evidence/INVENTORY.json:1842`: *"the prefix is the impersonation guardrail"* — which no check enforces and no dimension tested.

Adjacent, also unexamined: the twin's corpus names eleven real firms (`twin/fixtures.py`: carillion, nmc, wirecard, enron, astrazeneca, sanofi, royal-mail, netflix, intel, kodak, maersk) and **real living individuals** (`CEO Brian Krzanich`, `CEO Pat Gelsinger`, `CEO Michelle Johnston Holthaus`, `CEO Lip-Bu Tan`), publicly, attached to scored fraud/failure probabilities. Three of the eleven are fraud cases with living individuals. `NORTH-STAR.md:66-67` excludes covert sensing and real surveillance data; nobody asked whether a public dossier of named executives' quoted statements sits inside or outside that exclusion.

**Probe.** One page of legal review before the talk: (a) a `DISCLAIMER.md` in each regulator repo and a line in each README/party.yaml; (b) a decision on whether the twin's public corpus keeps named individuals; (c) whether publishing scored probabilities about a listed issuer (Intel) needs a "not investment research" line.

### C6 (major). NORTH-STAR §6's portability clause — ratified, owner-sourced — was assessed by nobody and is built by nobody.

`NORTH-STAR.md:65`: *"each adopter's switching cost is published in the same £, feeds are re-derivable from pins a departing adopter keeps, and exit cost sits on the balance sheet."* (Owner, re-grill 38, 2026-08-28.) `grep -rli "switching cost|exit cost|lock-in|portability" assess/` → **zero hits in all thirteen dimensions**. Estate-wide the only hit is `units/driftwood/twin/orgs/driftwood/scenarios/publisher-withdraws-2026.yaml:14`, which says the switching cost is *not* priced. The review graded §2, §3, §4, §5 and §6's last bullet; it skipped §6's second bullet entirely.

**Probe.** Grade the three sub-claims: is a switching cost published in any `prices[]`? Can a departing adopter re-derive `ico`/`feeds` from pins it keeps? Is exit cost on `evidence.json`? All three are read-only greps.

### C7 (major). The argument's carrier was never read as an argument. The deck contains no money.

`git show origin/main:talk/deck.md` — 14 slides, 19 code spans, **0 occurrences of "£"**. And it is not a staleness artefact: `for p in $(git ls-tree -r --name-only origin/main talk/captures | grep e2e); do git show origin/main:$p | grep -c "£"; done` → **0 for all seven beats**. A correct rebuild at run 21 would show exactly one money line, step 3's, which its own capture labels *"a SYNTHETIC residual … not driftwood's real priced position"*. driftwood's four real prices (£1,787,177 / £19,559 / £113,403 / £1,897,646) appear nowhere in `talk/`: `git grep -l "1,897,646" origin/main -- talk/` → none; `113,403` → none; `1,787,177` → only `verify_pound-seam…out`, which is not a beat.

`operability` graded the deck's *mechanism* (grades carried honestly, generated not authored). Nobody asked whether a non-engineer watching it learns the thing NORTH-STAR §3 calls the point — that a control, a cage tier, an insurance transfer and a pay rise are comparable in one currency.

**Probe.** Have someone who cannot read a bash capture read the deck cold and state the claim back. Then decide whether the £ beats (pound-seam, proportionality, fair) become beats.

### C8 (moderate). The estate prices everything except itself.

`tcor.py`'s own formula has the slot — *"TCoR = residual + cost-of-controls (fix spend + dynamic-cage run-cost) + transfer"* (`units/platform/tcor/tcor.py:6-8`) — and `NORTH-STAR.md:32` names *"a pay rise"* as one of the five comparables. No participant publishes a cost of operating the governance, and no dimension asked for one. Measured, 2026-09-01→02 across all nine repos: **72 runs, ~170 minutes wall-clock (~85 min/day)**. Free on public repos; on a private adopter's runners that is ~£190/yr of CI, and says nothing about the human cost, which is the number a prospective adopter asks for first — and which this engine, uniquely, could produce.

**Probe.** Publish one `platform/tcor` scenario whose cost-of-controls is the estate's own measured run cost + an FTE assumption, and put it on driftwood's balance sheet. It converts the strongest sceptic question ("what does this cost to run?") into a number in the estate's own currency.

### C9 (moderate). Three modalities were never run at all.

1. **Nothing was executed on a cluster.** The estate's most distinctive claim — the bottom rung is a running cage that reaches nothing — is second-hand in every dimension (`principles` P2-6 says the only proof is presenter-run evidence its own citation rule forbids). *Probe:* one witnessed run of `platform/graded/verify-graded.sh` on an ephemeral KinD, with the `nc` results captured into a lane sample the gate can cite.
2. **No cold reproduction.** Nobody cloned fresh onto a clean machine and ran `talk/verify-all.sh`. Every "I reproduced it" in the review ran against a working tree with a warm `.venv`. *Probe:* fresh container, `clone-estate.sh`, `verify-all.sh`, record time-to-first-verdict and every missing prerequisite.
3. **No external party's view.** Bus factor 1 is a finding (EQ-08); nobody supplied the missing readers. The four that would change the verdict most: a data-protection lawyer (C1/C5), a Kubernetes platform engineer (C4), an actuary on the 2,179% loss ratio (PE-01), and a non-engineer on the deck (C7).

### C10 (minor). Licensing and IP.

`gh api repos/policy-as-versioned-flux/policy-as-versioned-flux` → `license=none`, `size_kb=261363`. A 255 MB public repo holding the thesis, 24 ADRs, NORTH-STAR, the truth surface and the twin is all-rights-reserved (found as O5). Not found by anyone: `units/nist/` redistributes `NIST_SP-800-53_rev5.2.0_catalog.json` (1,196 controls, a US Government work) under a blanket Apache-2.0 `LICENSE` with **no NOTICE and no attribution line** — a party granting rights it does not hold, in the one repo whose whole value is provenance.

### C11 (minor). The owner-question load was never triaged.

13 dimensions × 6 = **78 questions**, to one person, unranked, with visible duplication. At least five questions are asked two-to-four times each: *is ≥3 coexisting still required* (thesis-fidelity Q1, truth-surface Q3, legacy Q2); *should the clock stand up a cluster* (truth-surface Q2, engineering-quality Q3, operability Q3, scope Q3); *is the insurer real or illustrative* (pound-engine Q1+Q3, participants Q1); *must the proposer's commit be signed* (principles Q5, security-spine Q4); *must the twin have its own org and tag* (participants Q3, twin-validity Q3). `process-and-record`'s own finding is that the panel-verdict shape — five conflicts, one page — is the only format that has ever produced a reasoned reply. Handing over 78 will reproduce the bare-agree pathology the review just diagnosed.

---

## PART B — CONCLUSIONS IN THE DIGEST I THINK ARE WRONG

**B1. "SS-01 refuted" is wrong, and it drops a confirmed, live, red-causing defect.** There is no refutation artefact for SS-01. The only evidence in the review directory is `skeptic/deltas.txt` and `skeptic/verdicts.txt` (written 14:25–14:31, *after* the assessment), and it **confirms** the finding exactly: 24 tags measured, five at `delta=-1` (driftwood v1.1.0, ico v1.0.0, ico v3.0.0, ludlow v1.1.0, nist v1.0.0), and the verifier returns `rc=1 REJECTED: certificate chain did not verify at tagger time …` for precisely those five and rc=0 for the other nineteen. The estate agrees: `.scratch/ecosystem/issues/73-the-verifier-rejects-a-tag-whose-cert-postdates-its-tagger-time.md` is **open**, quotes the same error, and `truth-surface`'s own strengths list attributes run-21 reds to "73 cert-skew". Meanwhile `demo-steps` DS-F5 ("step 4's red is an *instrument* fault") is listed refuted — i.e. it is an estate fault. So the digest simultaneously says the cert-skew defect is refuted (security-spine), that calling it an instrument fault is refuted (demo-steps), and that it owns a red under ticket 73 (truth-surface). A fitness verdict built from the digest cannot state this correctly. **Restore SS-01 as surviving, owned by ticket 73.**

**B2. Two dimensions grade NORTH-STAR §4 step 2 in opposite directions and the digest keeps both.** `thesis-fidelity` strengths: *"The updatable loop completed once for real … driftwood #20: Renovate raised threat-register v1 → v2, Chris Nesbitt-Smith merged it."* `demo-steps` DS-F3 (surviving, major): *"The truth surface … asserts a merged re-price that never happened."* Both cannot stand. My read is that they are about different scripts (`verify-renovate-merged-feed-pr` vs `verify-e2e-step2`) and the digest never says so — so a reader sees a strength and a major defect on the same beat with no reconciliation.

**B3. `scope-and-coherence`'s F1 refutation and `pound-engine`/`demo-steps`' surviving findings contradict each other on the ladder.** F1 ("the cage ladder is saturated; step 3 cannot occur") is refuted, yet `assess/pound-engine.md:470` F18 ("tier selection is saturated, and no real £ has ever crossed a band") and DS-F2 ("no crossed band has ever opened a reviewed proposal PR", critical) survive. If the ladder is not saturated, the estate should be able to name the input that moves a real residual across a band; ticket 74 exists precisely because it cannot. Either the refutation is narrow (it refuted "cannot", not "has not") and should say so, or F18/DS-F2 need re-grading.

**B4. `TWIN-08` refuted contradicts three surviving findings about the same fact.** TWIN-08 ("the twin's price is the only pricing parent with no pin, no version resolution, no signature check, and a silent absence") is refuted, while `principles` P6-3, `twin-validity` TWIN-03 and `participants` P6 all survive saying materially the same thing. One of the four is mis-labelled.

**B5. `truth-surface`'s verdict is internally inconsistent after its own refutations.** Its three stated reasons for unfitness are (1) the fictional denominator = TS-C2, **refuted**; (2) composition; (3) blindness to its own instrument. Two of its six "cheap changes to make it fit" fix TS-M3 and TS-M5, both **refuted**. Reason (2) and the C1 `exit 0` class are what actually survive — the verdict should be rewritten around them, and it is a much narrower verdict than the one in the digest.

**B6. A synthesis nobody performed: the insurer row has three independent critical defects and no dimension owns the question of whether it should exist.** `participants` P1 (signed quote attests an exposure that exists at no signed version, critical), `pound-engine` PE-01 (premium is 1/22 of expected loss on its own layer, 2,179% implied loss ratio) and PE-11 (the quote is stale and its refresh clock has never succeeded). Add C1 above and the same premium moves 44% on one un-fact-checked datum. Each dimension recommends fixing its own defect; none asks whether an illustrative counterparty that is wrong four independent ways belongs in a demonstration whose subject is attestable provenance.

**Sources:** [Hunton — FTT cuts Doorstep Dispensaree fine by two-thirds](https://huntonak.com/privacy-and-information-security-law/uk-first-tier-tribunal-cuts-icos-doorstep-dispensaree-fine-by-two-thirds) · [dataguidance — Court of Appeal dismisses Doorstep Dispensaree's appeal](https://www.dataguidance.com/news/uk-court-appeal-dismisses-doorstep-dispensarees-appeal) · [Dechert — Tribunal overturns ICO enforcement against Clearview AI](https://www.dechert.com/knowledge/onpoint/2023/11/tribunal-overturns-uk-ico-s-enforcement-against-clearview.html) · [ICO — UK Upper Tribunal hands down judgment on Clearview AI Inc](https://ico.org.uk/about-the-ico/media-centre/news-and-blogs/2025/10/uk-upper-tribunal-hands-down-judgment-on-clearview-ai-inc/) · [The Register — Clearview/ICO Upper Tribunal, Oct 2025](https://www.theregister.com/2025/10/09/ico_clearview_ai_tribunal/) · [talks.cns.me — Policy as [versioned] code](https://talks.cns.me/PolicyAsVersionedCode.html) · [blog.cns.me — mea culpa technical argument](https://blog.cns.me/posts/policy-versioned-code-mea-culpa-technical-argument-nesbitt-smith-pedef/)

# cross_dimension

# Cross-dimension cluster map — 2026-09-02

Written to `/private/tmp/claude-501/-Users-cns-httpdocs-controlplane-policy-as-versioned-flux/8c6523c6-66de-4c91-94ed-4ceff16a6a76/scratchpad/review/cross/cluster-map.md`. Full content below.

IDs are written `<dimension>/<id>` because they collide (three different `P1`s, two `F1..F17` series). Counts are counts of *ids*, with distinct underlying defects in brackets — several clusters are one bug found four times.

---

## Part 1 — Cluster map

### C1. "A green that could not look" — 14 ids [6 defects]

**Root cause.** `talk/verify-all.sh` grades by process exit code, and several checks reach exit 0 (or print `ok`) from a path where the property was never observed. Three mechanisms: exit 0 after printing your own SKIP; a lookup that misses and reports the miss as an honest absence; a check that grades presence, or a literal, instead of the property its own header quotes.

| id | what it is called there |
|---|---|
| truth-surface/TS-C1 | seven scripts exit 0 after printing their own could-not-look; `verify/provenance` PASSes with a maximal claim over two unobservable sections |
| engineering-quality/EQ-02 | the same six `computed-semver/verify-*.sh` scripts, `SKIP:` then `exit 0` |
| principles/P6-1 | `five-facts.py:522-528` writes `fired: false` when the falsifier returned `None`; the code's own comment three lines above forbids exactly this |
| principles/P6-2 | step 6 verifies platform's `v2.0.1` instead of `policy/v4.0.0`, and declares feeds unsigned |
| demo-steps/DS-F4 | same |
| operability/O3 | same |
| scope/F5 | same |
| truth-surface/TS-M8 | step 5 PASSes on file presence over an artefact two checks FAIL on in the same run |
| demo-steps/DS-F1 | same, framed as "on its schedule" un-graded |
| twin/TWIN-06 | same, framed as the citable number counting step 5 observed-true |
| twin/TWIN-07 | the only graded twin-quality metric scores a heuristic against its own lookup table — a green that cannot move |
| security/SS-08 | `wargamer.py:200,232` hardcodes `"signed": True` and `:324` asserts the literal |
| principles/P5-3 | same, framed as the proposal commit being unsigned |
| principles/P7-1 | a chained inference (tag verified → composed set built from that sha) printed as three independent per-publisher proofs |

**Four of these are one line of code.** `verify/e2e/verify-e2e-step6-provenance.sh:87` uses `git tag -l 'v*.*.*'`, which cannot match `threat-register/v2.0.0`. That single glob produces principles/P6-2, demo-steps/DS-F4, operability/O3 and scope/F5 — four ids, four dimensions, one fallback. Three more (TS-M8, DS-F1, TWIN-06) are one missing assertion in `verify-e2e-step5-twin-forecasts.sh`. Two more (TS-C1, EQ-02) are the same seven `exit 0`s.

**Do not merge two things that share a word.** truth-surface/TS-C1 is about `verify/provenance/verify-provenance.sh` (SPIRE and rekor-cli sections degrade to a printed note and it PASSes anyway). The other four are about `verify/e2e/verify-e2e-step6-provenance.sh` (the tag glob). Different files, different bugs, same noun.

### C2. Pins are checked for existence, never for content — and outside the policy artefact the estate mostly does not pin at all — 12 ids [8 defects]

**Root cause.** NORTH-STAR §2's "consumed only through a pinned, signed dependency" is applied to the policy artefact and to almost nothing else: not to the gate's own inputs, not to adopter CI, not to publisher release gates, not to the twin, not to two of the toolchain installs. Where a pin does exist, the check is that the tag *resolves*, never that the pinned *tree contains what the consumer prices or enforces from it*.

**Sub-family A — no pin at all:**

| id | called there |
|---|---|
| participants/P5 | the truth surface clones every unit's default branch; `clone-estate.sh:37-39`'s own precondition ("once a signed v1.0.0 lands, pin it here") fired on all eight and was not acted on |
| participants/P3 | ico, feeds and insurer consumed at moving `main`, no Flux source object, no commit |
| participants/P2 | twelve checkouts naming the deleted branch `ecosystem/thin-slice` (ticket 62) |
| participants/P4 | ico, insurer and feeds release gates check out platform with no `ref:` — the gate's instrument is platform's default branch |
| security/SS-06 | `curl -s https://fluxcd.io/install.sh \| sudo bash`, fifteen lines under a comment stating the pinning rule, inside the identity that signs the only citable artefact |
| security/SS-03 | the adopters' trust domains and bundle endpoints are literals in platform's tree |

**Sub-family B — a pin whose tree does not contain the thing (the sharpest shape in the review):**

| id | called there |
|---|---|
| participants/P1 | the insurer's gitsign-verified quote attests `driftwood exposure v1.1.0`; no adopter's v1.1.0 tree has an `exposure` section |
| pound-engine/PE-11 | **the same bug**, seen from the clock: every requote leg REFUSES `missing instrument: … carries no exposure section`, on both runs the insurer has ever had |
| principles/P4-2 | **the same shape, at the cage**: adopters' `composed-set.yaml` is reconciled from tag `v1.1.0`, whose tree carries 2.0.0/2.0.1/3.0.0 — three *retired* lines — so what Flux installs is a policy set the platform withdrew |
| participants/P6 | the twin has no org, no tag, no signature; driftwood runs the sweep inside `hub/.estate-clone/driftwood` |
| principles/P6-3 | same, framed as the largest £ line entering signed evidence as a local file read |
| twin/TWIN-03 | same, framed as "the one participant whose output nobody can verify" |

Sub-family B is the same failure that `insurer/party.yaml` already records happening once before (the fabricated `v1.2.0`, found 2026-08-29). The fix then substituted a real version string without checking the tree. It is now on its third artefact.

### C3. The citable clock stands up no substrate — 4 ids [1 defect]

`.github/workflows/truth.yml` installs gitsign/kyverno/cosign/flux and never creates a cluster, so every live tail is structurally could-not-look on the only surface any document may cite. `thesis/TF-05` (critical), `principles/P2-6`, `security/SS-02`, `engineering-quality/EQ-06`. Refuted on the same fact: `truth-surface/TS-C2`, `operability/O8`, `scope/F4` — see Part 2 §6.

### C4. One declared policy version — 4 ids [1 decision]

The 2026-08-29 retirement left `distribution/versions.yaml` with one element, removing the subject of four gate checks in one commit. `thesis/TF-01` (critical), `principles/P4-1`, `principles/P1-1` (the conditional-rule branch lived only in the retired `require-nonroot-2-0-1`), `legacy/L7`. Refuted on the same fact: `scope/F9`, `operability/O1`, `truth-surface/TS-M9` — see Part 2 §7.

### C5. Nothing prices or proposes being behind — 5 ids [2 defects]

The DECIDED replacement for ADR-0010's `sunset:` — price a stale pin by the EOL ramp, have the adopter's proposer open a retirement PR — is unbuilt on both halves. `composition.py:271-274` `FEED_CONVERTERS` has two rows and no `eol`/`cve` kind; `tier_pr.py` builds only `cage-tier` proposals. `thesis/TF-02` (critical), `scope/F3`, `legacy/L3`, `legacy/L2` (the publisher advertises cve and eol; composition refuses any adopter who pins them — the same missing converter), `legacy/L4` (the record half).

### C6. The £ is an ordinal index published as a balance-sheet quantity — 9 ids [8 defects]

Every input that turns a severity into money is an editorial constant, a platform-held fixture, or absent; nothing aggregates the retained lines against the one band; `size` exists on one adopter of three. `pound/PE-02`, `PE-06`, `PE-07`, `PE-10`, `PE-05`, `PE-08` + `scope/F2`, `PE-01`, `PE-12`.

### C7. The £ never reaches an enactment — 5 ids [3 defects]

Nothing binds the composed `proposed_tier` to the enacted `posture.acme.io/tier`; the residual that would move is computed from the platform's table rather than the adopter's own published curve; no residual has ever crossed a band. `demo-steps/DS-F2` (critical), `principles/P5-2`, `thesis/TF-03`, `twin/TWIN-09`, `principles/P3-1`. Downstream of C6.

### C8. The clocks are half-dead and the gate is blind to them — 7 ids [5 defects]

`participants/P9` (feeds and insurer failed every scheduled run ever; nist green and writing null because its reader looks at `catalog/v<N>/feed.json` and the catalogue is at `catalog/`), `participants/P7` + `twin/TWIN-04` (twin-sweep runs under `bash -e`, so the python line aborts before `rc=$?`; the `moved=true` branch is unreachable), `truth-surface/TS-M2` + `principles/P5-1` (no cross-org credential; twelve SKIPs), `demo-steps/DS-F6` (round 3 committed and unpushed), `security/SS-07` (half).

### C9. One identity is every role and nothing on the forge enforces any of it — 4 ids (+1 shared)

`security/SS-04`, `security/SS-05`, `engineering-quality/EQ-08`, `scope/F8`; shared with C1: `security/SS-08` — the proposer's identity cannot be forged because it does not exist.

### C10. The durable record is derived from nothing, so it drifts from the code — 10 ids

`process/P4`, `process/P5` + `principles/P2-4`, `process/P8` + `legacy/L4`, `legacy/L5` + `scope/F10`, `truth-surface/TS-M4`, `operability/O7`, `process/P7`.

### C11. ~84 architectural items rest on a bare agree, and nothing converts them — 3 ids

`process/P1` (GAPS rule 1 dropped when the rules were copied into `map.md:16`), `process/P7` (shared with C10), `principles/P4-3` (re-grill 6's recorded override, disclosed as unbuilt in the shipped 4.0.0 evidence). C11 is the upstream of C10, not a peer.

### C12. The twin scores beliefs; it does not form them — 4 ids (1 shared)

`twin/TWIN-01` (critical), `twin/TWIN-02`, `twin/TWIN-05`, and shared with C1, `twin/TWIN-07`.

### C13. The engineering apparatus is applied to the twin only — 3 ids

`engineering-quality/EQ-01`, `EQ-04`, `EQ-07`.

### Singletons

`operability/O4`, `operability/O5`, `truth-surface/TS-M1`, `truth-surface/TS-M6`, `principles/P3-2`, `legacy/L6`.

---

## Part 2 — Contradictions, and the same fact graded differently

**Direct contradictions — two findings that cannot both stand**

1. **The currency controller. `legacy/L5` vs `scope/F10`.** L5: the retirement was a *category error* (posture currency vs money FX), it is the only post-admission re-caging mechanism, withdraw the retirement. F10: the retirement was *decided and never executed*, 416 lines of ballast still graded every run, delete it. Same file, opposite remedies, neither auditor saw the other.
2. **Whether the twin's price has a pin. `twin/TWIN-08` (refuted) vs `principles/P6-3` + `participants/P6` + `twin/TWIN-03` (all surviving).** Either the refutation is wrong or three surviving findings overstate the same fact.
3. **Whether "there is no gate" is a contradiction. `scope/§1` probe table ("vocabulary collision, not a rule conflict") vs `principles/P2-4` + `process/P5`.** Scope is right about the *release* gate; the other two find a live second `Deny` at *admission*, a glossary that denies it, and an ADR that blesses only one refusal. Read literally, the scope verdict refutes two surviving findings.
4. **Cert-skew: estate fault or instrument fault. `demo-steps/DS-F5` (refuted) + `security/SS-01` (refuted) vs `truth-surface/§3 row 1` + `principles/P7-4`.** Two auditors called the cause of four of run 21's seven reds an *instrument* fault and both were refuted; two called it an *estate* fault (ticket 73) and were not challenged. The cause of the largest red group is unsettled inside this review.
5. **Whether step 2 is done. `thesis/strengths` vs `demo-steps/DS-F3`.** Thesis: the updatable loop completed for real (PR #20). Demo-steps: the same PR moved `old_price == new_price == 19558.549772440045`, and the PASS line's word "merged" describes tuppence, which merged nothing.

**Same fact, different grade**

6. **`truth.yml` creates no cluster — seven findings, four gradings.** Survives as `thesis/TF-05` (**critical**), `principles/P2-6`, `security/SS-02`, `engineering-quality/EQ-06` (major); refuted as `truth-surface/TS-C2`, `operability/O8`, `scope/F4`. Identical evidence graded critical, major, and not-a-finding.
7. **"≥3 coexisting versions" is at one — six findings, two gradings.** Survives as `thesis/TF-01` (**critical**), `principles/P4-1`, `legacy/L7`; refuted as `scope/F9`, `operability/O1`, `truth-surface/TS-M9`. This is the thesis's own non-negotiable, and the review has it both ways.
8. **Proportionality. `thesis/TF-03` (surviving) vs `principles/§3`** ("the strongest-built principle"). Same `verify_proportionality` PASS; one reads it as proof, the other as a hub bench rig whose control appears in zero unit repos.
9. **The deck. `truth-surface/TS-M1` (surviving) vs `operability/O2` (refuted).** Same artefact, opposite survival.
10. **The three adopter forks. `engineering-quality/EQ-03` (refuted, graded critical) vs `operability/O7` (surviving, major).** Same measurement.
11. **Insurer severity. `participants/P1` (critical, "second shipment of the same laundering class") vs `pound/PE-11` (major, calls the SKIP "honest").**
12. **nist's clock, inside one dimension.** `participants` lists the null-observation line in its **strengths** (refusal over guessing) and in surviving `P9` as "a dated falsehood about its own signed catalogue".
13. **The five-fact sample. `principles/P7-1` (surviving: fact 3 is a chain printed as three proofs) vs `thesis/§3.5` and `demo-steps/§5` (praised as a real cross-org observation).**
14. **Ownership disagreements.** `demo-steps/DS-F6` says the tuppence/ludlow reconcile fix has no open owning ticket; `truth-surface/§3` assigns those reds to 62/74. `participants/P9` assigns the feeds/insurer clocks to ticket 57; `truth-surface/M2` to ticket 56.
15. **`TS-C1` vs `EQ-02`.** Identical evidence, identical remedy, graded critical and major.

---

## Part 3 — Root-cause ranking

| # | root cause | ids closed | cost shape |
|---|---|---|---|
| **1** | **C1 — a green that could not look** | **14** | mechanical: 7 `exit 0`→`exit 3`; one tag glob; one step-5 assertion; one deleted `"signed": True`; one falsifier tri-state; one honest sentence on P7-1 |
| **2** | **C2 — pins checked for existence, never content; not applied to the estate's own instruments** | **12** | mostly mechanical + two real pieces of work (cut an adopter tag carrying `exposure`; bump the composed set off the retired lines) + one owner decision (tags or branches?) |
| **3** | **C10 — the record is derived from nothing** | **10** | cheap: two ADR banners, a dated note on fourteen tickets, one glossary entry, ticket-67's check widened from `map.md` to `issues/*.md` |
| 4 | C6 — the £ is an ordinal index published as a balance-sheet quantity | 9 | owner decisions |
| 5 | C8 — clocks half-dead, gate blind to them | 7 | mechanical + one push |
| 6= | C5 / C7 | 5 each | build / one binding check |
| 8= | C3 / C4 / C9 | 4 each | one decision each |
| 11 | C13 / C12 / C11 | 3 each | — |

**Top three, as the fix:**

1. **C1 — make every green rest on an observation (14 ids):** `truth-surface/TS-C1`, `engineering-quality/EQ-02`, `principles/P6-1`, `principles/P6-2`, `demo-steps/DS-F4`, `operability/O3`, `scope/F5`, `truth-surface/TS-M8`, `demo-steps/DS-F1`, `twin/TWIN-06`, `twin/TWIN-07`, `security/SS-08`, `principles/P5-3`, `principles/P7-1`.
2. **C2 — consume the estate the way the estate tells adopters to consume (12 ids):** `participants/P1`, `/P2`, `/P3`, `/P4`, `/P5`, `/P6`, `pound/PE-11`, `principles/P6-3`, `principles/P4-2`, `twin/TWIN-03`, `security/SS-06`, `security/SS-03`. The load-bearing half is one assertion — *verify that a pinned tree contains what the pin claims* — which closes three otherwise unrelated findings at once (`participants/P1` + `pound/PE-11` + `principles/P4-2`).
3. **C10 — derive the record from something (10 ids):** `process/P4`, `/P5`, `/P7`, `/P8`, `principles/P2-4`, `legacy/L4`, `legacy/L5`, `scope/F10`, `truth-surface/TS-M4`, `operability/O7`. Cheapest of the three and lowest fitness weight — nothing in it changes what the estate does, only what it says it does. Its ten are the symptom; **C11 is the cause**, and C11 is the one root cause here whose remedy is an owner decision about how decisions get made.

**If ranked by consequence rather than count, C6 replaces C10 in third place.** C6's nine ids are the only cluster whose fix also unblocks C7's five (including `demo-steps/DS-F2`, critical) and one of the two things the destination sentence fails on. C10's ten cost the estate credibility; C6's nine cost it the demonstration.

**Two clusters carry a critical each and are deliberately absent from the top three.** C3 (4 ids, incl. `thesis/TF-05`) and C4 (4 ids, incl. `thesis/TF-01`) are small by count and large by weight — between them they are why the estate cannot cite its own cage and cannot show the thesis's own non-negotiable. Both are single decisions, not programmes of work. A count-based ranking under-serves them, and inherits the review's own inconsistency on exactly those two facts (§6 and §7 above).

# steelman

Written to `/private/tmp/claude-501/-Users-cns-httpdocs-controlplane-policy-as-versioned-flux/8c6523c6-66de-4c91-94ed-4ceff16a6a76/scratchpad/review/STEELMAN.md`. Full content follows.

# STEELMAN — the eco-system as built on 2026-09-02

Citable line: `TRUTH 2026-09-02T10:11Z run=21 hub=7b92990 ... pass=57 fail=7 skip=18 excluded=2 total=84`

Everything below I verified in a primary source. Where I re-derived a fact on this machine rather than quoting a capture, I say so and give the command.

## The ten most impressive things that are real and proven

### 1. A complete keyless signature spine across eight independent GitHub organisations — 24 of 24 tags, no exceptions

I re-derived every one myself, not from a capture:

```
cd scratchpad/units && for u in platform nist ico driftwood tuppence ludlow feeds insurer; do
  for t in $(git -C $u tag -l); do git -C $u -c gpg.format=x509 -c gpg.x509.program=gitsign tag -v "$t"; done; done
=== good=24 bad=0 ===
```

Every tag returns `Good signature from [https://github.com/policy-as-versioned-<org>/<repo>/.github/workflows/cut-release.yml@refs/heads/...]` and `Validated Rekor entry: true`. Each identity is anchored to *that repo's own* workflow — platform's tags name platform's cut-release.yml, ico's name ico's. No unsigned tag, no bad signature, no cross-org identity anywhere in the estate.

Two details that make this better than a checkbox:

- `policy/v2.0.1` is signed from `refs/heads/release/2.0.x`, not main, and its commit `ebc4ff5` is **not an ancestor of origin/main** (`git merge-base --is-ancestor` → NO). The thesis's "older lines are patchable" was exercised for real, on a maintenance branch, and the release identity regexp (`units/platform/.github/workflows/release.yml:54`) admits exactly `(main|release/[0-9]+\.[0-9]+\.x)` and nothing else.
- The org topology is real, not a directory convention. `gh api orgs/policy-as-versioned-<u>` returns `repos=1` for all eight, created 2026-07-23 (six) and 2026-08-28 (feeds, insurer).

### 2. Semver is computed from measured verdict movement, and a real release was cut by that computation

This is the one place the build *exceeds* the 2022 thesis, which only asked that policy carry a semver number.

`units/platform/computed-semver/evidence/4.0.0.json` records: `outcome {result: passed}`, `bump {declared: major, computed: major}`, `counts {old: 153, new: 152, union: 164}`, `corpus_checksum sha256:ae12308f64efd…`, `wall_clock 88.78s`, 28 named movement entries, `not_looked_at: []`, and a `limits[]` array naming three open limitations against its own interest.

Run 21's capture `.estate-clone_platform_verify-first-gate-determined-release.out` confirms the ordering: *gate → commit evidence → correct the array → tag → push*, and that `policy/v4.0.0 → 1d8cec2…` resolves **one commit ahead** of the commit the array names (`64635df…`), which is the only shape in which the number can have been determined before the tag.

I ran the gate's own selfcheck on this machine — `python3 computed-semver/gate.py --selfcheck`, exit 0 — and it asserts, among ~30 properties, that *"a declared bump weaker than computed publishes DEGRADED (tier quarantine, a prerelease suffix on the untouched base number) … the declared number is never rewritten"*, that a declared version that already exists refuses, and that the two historical bumps (1.0.0→2.0.0 major, 2.0.1→2.1.1 minor) re-derive exactly.

### 3. A five-parent, pinned-by-tag-and-commit inheritance graph across five separate orgs, machine-checked against the real remotes

`units/driftwood/composed/HEADER.yaml` records each parent as `{party, kind, version, sha}`:

```
platform  implementations 2.0.1  533dccb0a823001b396fd60ab08014bf75065a37
nist      controls        1.1.0  33a05df1f5241bca6ffbc1c69a70075cdb7a5819
ico       feed penalty-schema v3 e1fb8eb5663e50088b13d872a4e44112476f516e
feeds     feed threat-register v2 50a0b330a730f4f9ee9520561b0c05c8be4c9268
insurer   feed quote-driftwood v1 db767055119292e400edd63ed260785ce605eb4e
```

Run 21's `verify_feed-contract_verify-feed-contract.out` ends PASS after ~80 assertions including 24 individual pin resolutions against real remotes via `git ls-remote --tags` (`verify/feed-contract/feed_contract.py:86`), e.g. `PASS: driftwood pins feeds/feed/threat-register@v2: tag threat-register/v2.0.0 on feeds`. Unreachable returns None → SKIP, never a pass.

The composed artefacts are demonstrably *generated*, not copied: diffing `units/platform/distribution/policies/v4.0.0/*.yaml` against each adopter's `composed/policies/v4.0.0/*.yaml` shows only YAML re-serialisation plus three added provenance fields — `composed-for: driftwood`, `inherited-from: platform@2.0.1`, `source-path: distribution/policies/v4.0.0/<file>` — on every object, in all three adopters.

### 4. Proportionality is a computation, not an opinion — I re-derived it on this machine

The mea culpa's central distinction (lane-keeping assist vs a locked door) is the hardest thing in the thesis to make mechanical. The estate made it arithmetic:

```
python3 units/platform/risk/enforce.py decide verify/proportionality/scenarios/encrypt-at-rest.json --org <o>
driftwood {'verdict': 'Audit', 'risk_bought': 21107.288354622422, 'tolerance': 40000.0}
ludlow    {'verdict': 'Deny',  'risk_bought': 21107.288354622422, 'tolerance': 5000.0}
tuppence  {'verdict': 'Deny',  'risk_bought': 21107.288354622422, 'tolerance': 15000.0}
```

Same control, same scenario, **byte-identical** risk_bought; the enforcement action flips purely on each organisation's own signed appetite band. `verify/proportionality/verify-proportionality.sh` asserts the identity first (`risk_bought differs across orgs — not the same control`) and then that the committed policies match the £-derived render (`render.py --check`). Nothing in the 2022 material proposed a mechanism for deciding which side of that line a control falls on.

### 5. One signed artefact carrying four independent organisations' priced output, in one currency, under one declared perspective — with a summing helper that refuses to cross either

`units/driftwood/composed/evidence.json`:

```
ico      feed     GBP  1,787,177.08  perspective=driftwood  name=penalty-schema
feeds    feed     GBP     19,558.55  perspective=driftwood  name=threat-register
insurer  premium  GBP    113,403.30  perspective=driftwood  name=quote-driftwood
twin     twin     GBP  1,897,646.11  perspective=driftwood  name=forward-intel
```

Each line carries `per_customer`, an `lef_basis` naming its own editorial content, and (for ico) a four-way `holes[]` breakdown by real NIST control id summing to the total.

The seam is enforced in code, not by discipline: `units/platform/fair/fair.py:67-95` (`sum_prices`) raises `refusing to sum across perspectives/currencies` and raises again on any unlabelled amount. I reproduced the feeds line exactly and showed it deterministic:

```
python3 units/platform/fair/fair.py summary .../driftwood-cart-pii.json   (twice)
DETERMINISTIC: identical across two runs
"ale": 19558.549772440045          ← equals evidence.json's feeds amount exactly
```

Run 21's `verify_pound-seam` PASSes 27 assertions, including that two independent tier-selection engines (platform's `graded/cage.py` and driftwood's own published selection-policy package) agree in all 60 constructed cases at every band boundary, and that a date the FX feed does not publish *refuses as a missing instrument and prices nothing*.

### 6. The dependency loop closed for real once — machine-raised, human-merged — and it is graded from the PR record, with the pin load-bearing inside the check

`gh pr view 20 --repo policy-as-versioned-driftwood/driftwood`:

```
#20 MERGED "Update dependency feeds/threat-register to v2"
head=renovate/feeds-threat-register-2.x
commit ea1c8db5 author=github-actions[bot]
files: composed/HEADER.yaml, composed/evidence.json, party.yaml
merged_by=chrisns at 2026-09-01T08:57:50Z
```

A bot opened it, a human merged it, and the declaration and the composed artefact moved in one commit. Run 21 grades it from that record, not a simulation (`verify_renovate_verify-renovate-merged-feed-pr.out` → PASS).

The part I found most convincing is what the PR's *checks* did. All three (`compose-check`, `shift-left`, `propose-tier`) went green, and the compose-check log shows it reading driftwood's PR-head pin and then:

```
git checkout --progress --force refs/tags/v2.0.1   (platform)
git checkout --progress --force refs/tags/v1.1.0   (nist)
```

The pin is not decoration on a Renovate PR: the check tests the version being proposed, at the signed tag, in another organisation. `driftwood/.github/workflows/shift-left.yml:26-36` records that this was a *fixed defect* — the job used to check out platform's default branch, so a bump PR never tested what it proposed.

### 7. Live cross-organisation distribution fidelity, observed on a fresh ephemeral cluster, on the adopter's own cron, with the falsifiers pre-registered

`gh run view 33624104359 --repo …/driftwood` → `name=drift-sample, event=schedule, conclusion=success, createdAt=2026-09-02T11:20:42Z`. A real cron firing today.

`drift-sample.yml` brings up `kind create cluster` with a fresh name, installs kind 0.32.0, flux 2.9.3, kyverno 1.18.2 and flux-operator 0.58.1 each pinned by **version and SHA256**, and reconciles from the real github.com remotes — with the reason written down: *"A `curl | bash` installer would put an unreviewed script inside the identity that signs this repository's observation commits."* The newest three lines of `drift/samples.jsonl` (cluster `dsample-33624104359`) record, for driftwood-composed, nist and platform:

- fact 1 Ready at the pinned tag **and** commit, url = the publisher's real remote;
- fact 3 last-applied revision equals the pinned commit;
- fact 4 all 16 rendered objects live and equal to an offline render taken *at the pinned ref*;
- fact 5 all 16 objects present in a Flux inventory — the fact that separates "Flux put it there" from "someone ran kubectl apply".

For nist and platform, fact 2 (in-cluster gitsign verification at the source boundary) is also true, against each publisher's own anchored identity regexp. The facts, three falsifiers and a 0.9 coverage floor were declared in `drift/window.yaml` on 2026-08-28, before sample one, and `drift/five-facts.py` refuses to grade a sample whose run id is not a real Actions run or whose appending commit is not signed by the lane's own identity — closing a documented incident where three hand-typed lines graded PASS.

What is in force there is a genuine cage, not a label. `composed/policies/v4.0.0/cage-tier.yaml` takes the tier from `namespaceObject` and **clobbers** the pod's own label; the fallback is fail-closed to `isolated`; hardening booleans are ORed with what the container declared; cpu and memory ceilings are a minimum via `quantity().isLessThan()`; `hostNetwork/hostPID/hostIPC` are written false at every rung; and a WAF sidecar is injected at the tighter rungs. Tighten-only, in CEL, in the copy each adopter actually composes.

### 8. A falsifiability instrument whose headline result is its own worst score — and it still exits 0

I ran it myself, offline, into a scratch directory:

```
bash twin/beat-royal-mail.sh <tmp>        EXIT=0
  market-consensus-2013  p=0.05  brier=0.9025  log-loss=2.9957  [as-consumed]  adjusted brier 0.8641
  contamination discount: -0.0384 on brier (enron-vs-obscure -0.0384)
  the headline: market-consensus-2013 said 0.05, it happened, brier 0.9025 — worse than a coin
  flip, and step 3 printed it above the rest
```

The rewind is real, not a filter: the fixture's dated git history runs 2013-08-01 → 2019-05-23, the run is cut at T=2018-06-01, and both the profit warning (2018-10-01) and the answer key (2019-05-23, citing Royal Mail's real £1.8bn investment concession) are *absent by construction*. The fixture repos are deterministic — "same content, same commit sha, on every machine". The contamination discount is measured from two other subjects (Enron as the notoriety control, Carillion as the low-notoriety leg), never hardcoded. The forecast bundle reproduces byte-identically from its own pins (`forecast-bundle a03e55a0e10a54e1 (recorded a03e55a0e10a54e1)`, `tolerance: none — byte identity`).

And the machine says out loud what it cannot do, in its own output: *"A forecast here reads a world model's declared belief and nothing infers it from a signal, so the three probabilities are identical by construction and a computed residual of zero would read as 'the model is fine' rather than as 'nothing consumes a signal'."*

The same discipline holds in CI: `gh run view 33615039125` (twin.yml, event=schedule, today) shows `70 passed, 1 failed, 3 skipped` invariants and `1 failed, 1550 passed`, with the one failure being a pre-registered guard whose own message says *"This guard staying red is the finding, not a defect in it"* — while `determinism (x86_64-linux)`, `(aarch64-linux)`, `(arm64-darwin)` and `reproduce-elsewhere` all pass in the same run.

### 9. Three policy lines were retired because the estate's own engine refused to let them be patched — after a live-observed escape

`units/platform/distribution/versions.yaml:29-59` is the best single page in the estate. 2.0.0, 2.0.1, 3.0.0 and two backports were retired on 2026-08-29 for two independently *observed* reasons:

1. Not deployable — every 2.x/3.x cage-tier wrote `priorityClassName` without the `priority` and `preemptionPolicy` the Priority admission plugin re-derives, so the plugin refused the pod.
2. Not safe, and unfixable as a patch — every pre-ADR-0022 body read the tier from the **pod's own label**. Observed live on kind-driftwood: in a Namespace declaring `posture.acme.io/tier=isolated`, a pod claiming 2.0.2 and forging `tier=baseline` was admitted as baseline with `hostNetwork=true` and **reached the API server**; the identical pod claiming 4.0.0 was clobbered to isolated, hostNetwork=false, and reached nothing.

Teaching an old body to read `namespaceObject` *is* ADR-0022, which the engine classifies major — "so it cannot be a patch on those lines, and ADR-0011 refuses a declaration weaker than the computed one. The honest repair is retirement, not a number." The released trees stay on disk behind their signed tags, unedited. This is the estate's own computed-semver machinery over-ruling its author's convenience, and the record saying so.

Related and verified: **there is no exemption mechanism anywhere.** A case-insensitive grep for `PolicyException|exemption` across all eight unit clones (excluding .git, `__pycache__`, and markdown) returns 23 hits, and every one is a negation, a fail-closed default, or a reference to the deleted `render-exemption.py` — e.g. `composition.py:36` *"not an exemption: it is a DECLARED INABILITY, priced"*, `render-governed-namespace-guard.py:87` *"Silence is not an exemption"*, `identity/component-definition.json:59` *"A pod with no tier is named `isolated`, the strictest running cage: silence is not an exemption."*

### 10. One command, on a clock, in CI, writing one dated, signed, committed number — that records itself when it is red

Run 21 is GitHub Actions run `33616685427`, `event=schedule`, `conclusion=failure`. Its steps:

```
7  the gate                                                        success
8  record the TRUTH line                                           success
9  the observation cage -- a clock appends observations, never a declaration   success
10 fail if the gate failed                                         failure
```

The number was written and pushed **before** the run went red, and the red is the honest signal. I verified the commit's signature:

```
git -c gpg.format=x509 -c gpg.x509.program=gitsign log -1 --show-signature a209496
tlog index: 2685003932
Good signature from […/policy-as-versioned-flux/.github/workflows/truth.yml@refs/heads/main]
Validated Rekor entry: true
```

The instrument is honest about itself in four ways I checked:

- **Discovery, not a list.** `talk/verify-all.sh:45` globs 84 `verify*.sh`; I counted 84 on disk. A script neither run nor listed with a reason is itself a FAIL, and a listed exclusion that no longer exists is a FAIL too, so the list cannot rot.
- **A cage that bites.** `truth.yml:108-162` does `git reset -q` **first** (fixing a reproduced 2026-08-28 defect where staged-and-clean entries rode along), stages only `OBSERVATION_LANE`, then asserts the *staged set* against the same list rather than a second regex, then asserts the tree clean outside the lane.
- **Reporting graded separately from results.** Run 21's step-7 capture shows `PASS: steps 1-6 each report one honest verdict (verdicts: PASS PASS PASS FAIL PASS PASS PASS)`. A red step 4 and a green step 7 in one tally is correct, and its script says why in its header. I ran its selfcheck: `bash verify/e2e/verify-e2e-step7-honesty.sh selfcheck` → *"a hedged PASS, an exit/last-line mismatch, a non-conforming step and a green whose own transcript confesses mid-run are each caught; an honest SKIP and an honest FAIL are not."*
- **It refuses to fake a subject it no longer has, at its own cost.** `distribution/verify-coexistence.sh:35-45` declines to loop a one-element array — *"looping a one-element array to claim coexistence would be the false pass this project forbids. Do not invent a second version to keep the beat alive"* — and SKIPs with a stated reason. `verify-shift-left.sh` does the same for the ±1 window. The insurer's own quote check SKIPs because *"the insured re-signed its exposure and a re-quote PR is due."* And when ticket 60 reordered three checks to grade the real lane sample *before* looking for a cluster, the published number got **worse** — run 19→20, `skip 22→18, fail 3→7` in `talk/truth.log` — because four could-not-looks became honest observed-falses. A project that made its own headline metric worse in order to be true has earned the metric.

Even the deck obeys it: `talk/deck.md`'s header says it was built at a superseded commit and therefore *"records no run of the truth surface at this commit, so this deck quotes no headline number"*, and `verify-demo.sh` FAILs run 21 for exactly that staleness rather than shipping a green lie.

## Which purposes these ten already serve, and the honest claim for each

### (a) A conference talk — serves it well today, with one rebuild

The seven-beat, generated-not-authored deck is the estate's best single idea: `build_deck.py` writes every slide from one capture per check, and `verify-demo.sh` refuses the deck if a figure is not in the capture behind it, if a beat status disagrees with the run, or if a TRUTH line is quoted from another commit. It caught its own staleness on run 21. Beats 1, 2, 6 and 7 are green on the citable run; 3 is green on a labelled synthetic; 4 has a fully-diagnosed red; 5 is green. Nine of the ten items above are demonstrable live, from a laptop, in seconds — the gitsign verification loop, `enforce.py decide` across three orgs, `fair.py summary`, `gate.py --selfcheck`, the Royal Mail beat.

> **Honest claim:** *"Here is a nine-organisation eco-system where policy is a signed, semver, pinned dependency; where the release number is computed from measured verdict movement rather than declared; where the same control resolves to Audit in one firm and Deny in another purely from each firm's own signed appetite; and where one command, on a clock, publishes a signed number that today reads 57 pass, 7 fail, 18 could-not-look. I will show you the reds and tell you which are the estate's fault and which are the instrument's."*

### (b) A reference architecture — serves it now, for the publish/consume half

The artefact contracts are the reusable part and they are small and closed: a 7-field feed envelope with `additionalProperties: false` and a written argument for why there is no in-band signature field; a party schema all eight parties validate against; an inheritance header with `{party, kind, version, sha}` per parent; per-object `inherited-from` / `source-path` provenance; a ResourceSet whose single `versions[]` array is simultaneously the install list, the prune list and the orphan-guard allow-list. All eight unit repos are Apache-2.0. A regulator or intelligence publisher can adopt the contract in an afternoon — `bash units/ico/verify-penalty-feed.sh` passes offline on a stock laptop in seconds, including a real `git ls-remote` against nist.

> **Honest claim:** *"This is a worked reference for treating policy as a versioned dependency across organisational boundaries: the envelope, the pin shape, the composition header, the release gate, and the identity regexp are all here, Apache-2.0, exercised against real remotes. It is not yet a product an unfamiliar platform team can operate unaided — there is no onboarding path and no measured time-to-first-cage."*

### (c) A research artefact — serves it strongly, and this is its best fit

Determinism is proven across three architectures in the same CI run where other jobs fail; every stochastic path is explicitly seeded; a fixture corpus produces the same commit sha on every machine; the twin's forecast bundle reproduces byte-identically from its own pins; 1,550 tests and 73 computed capability grades that refuse a hand-typed value. The falsification tests are pre-registered before first observation and name their own falsifiers. Negative results survive to the surface — a Brier of 0.9025 is the headline, not a footnote. And the record documents its own limits against interest: `not_looked_at: []` beside a `limits[]` array, a coverage figure expressed as cells and pairs and *never* a percentage, `anchored: false` on the GPD parameters that feed the largest number on the balance sheet.

> **Honest claim:** *"An artefact built to be checked rather than believed: pre-registered falsifiers, seeded determinism verified on three architectures, byte-identical reproduction from declared pins, scored forecasts under proper scoring rules where the worst score is the headline, and an instrument that made its own published number worse in order to stop reporting a could-not-look as a pass."*

### (d) A consultancy asset — serves it as an argument and a capability demonstration, not yet as a liftable package

What a client conversation can use today: a live, verifiable cross-org signature spine; a compose-check that tests a Renovate bump at the signed tag in another organisation before a human merges it; a release gate that computes the number and refuses the author's declaration; a cage that tightens and never widens, with the escape it was built to close recorded as an observed incident; and a £ engine that makes a control, a cage tier and an insurance transfer comparable in one currency under one perspective. The one blocker to *lifting* it is administrative, not architectural: the hub carries no licence (`gh api …/license` → 404) while all eight units are Apache-2.0.

> **Honest claim:** *"This is what a governance eco-system looks like when every participant is a separate organisation signing its own artefacts and consuming everyone else's by pinned tag and commit. It demonstrates capability and taste. It is a private demonstration and a set of reusable contracts, not a productised platform — and the hub needs a licence before any of it travels."*

### (e) A thesis defence — serves the mechanism half convincingly and the doctrinal half partly, and knows which is which

The mechanism the 2022 posts describe is built and machine-checked: semver, signed tags, pinned consumption, Renovate bumps, reviewed merges, Flux distribution, coexistence-by-matchCondition, maintenance-branch patching. On two points the build *goes past* the original — semver is computed from measured verdict movement and a weaker declaration cannot be published clean; and "exemptions dissolve into conditional policy" is not a slogan but a verified absence, with zero exemption mechanisms in 28,490 lines of unit Python and 11,246 of shell. The mea culpa's locked-door distinction is turned into arithmetic that I re-derived. And the honest weak point is honestly recorded: with one declared version, the coexistence, retirement and shift-left beats SKIP rather than fake a subject, which is itself the thesis's own standard being kept under pressure.

> **Honest claim:** *"The mechanism half of the thesis is built, signed and machine-checked on a clock — and in two respects it is stronger than what I wrote in 2022, because the version number is now computed from measured behaviour rather than declared, and the lane-keeping/locked-door split is a computation over each firm's own signed appetite rather than a judgement call. The doctrinal half is where I owe the most: the estate runs one policy line today, so three coexisting versions with a retirement window is unproven at runtime, and my own checks say so by refusing to pass rather than by inventing a second version."*

## What I could not look at

- `verify-graded.sh`'s live cage proof (the `nc` reach test from an isolated pod, the refused orphan pod) requires a persistent kind cluster named `driftwood`. I read the code (`units/platform/graded/verify-graded.sh:470-535`) and it is a real TCP connection test with a polled 60-second window and a written reason for the poll, but I did not run it — creating a cluster is out of scope for this review.
- Run 21's step-4 red: driftwood's fact 2 is observed false with `certificate is not yet valid` at tagger time 1787677714. I confirmed separately that `driftwood v1.1.0` verifies *cleanly* under gitsign with `Validated Rekor entry: true` on this machine. Both facts are mine; I did not attempt to adjudicate which side is at fault.
- I did not re-derive the ico £1,787,177.08 line from first principles; I verified its four `holes[]` sum to it and that all four control ids resolve in nist's catalogue, which I did re-derive (sha256 `d820835a…` recomputed, 20 groups, 1,196 controls, verbatim NIST SP 800-53 rev 5.2.0 OSCAL).

# purpose

# PURPOSE ANALYSIS

Files: `/private/tmp/claude-501/-Users-cns-httpdocs-controlplane-policy-as-versioned-flux/8c6523c6-66de-4c91-94ed-4ceff16a6a76/scratchpad/review/purpose/PURPOSE.md` and `.../QUESTIONS.md`

## 0. Method, and what I could not look at

Owner's words only. Quotes marked **(SV)** were re-read at source in the raw session transcripts (`~/.claude/projects/-Users-cns-httpdocs-controlplane-policy-as-versioned-flux/*.jsonl`, 95 files), not just in the drift review's derived appendices. Others are quoted at one remove from `evidence/AMBITION_TIMELINE.json` and appendices C/G — documents the owner engaged with (he answered the 41 re-grills they produced), but which I did not independently verify line by line.

Three things I checked and could not find:

- **Git commit messages are not a source of owner speech.** All 404 hub commits under `chris@cns.me.uk` (`git log --format='%an|%ae' | sort | uniq -c`) are in the assistant's documentary voice. I found no owner utterance in any of them.
- **"Fit for purpose" appears nowhere in the repository.** `grep -rn "fit for purpose\|fit-for-purpose" --include="*.md"` → 0 hits. No document states a threshold at which the owner would say it does what he wanted.
- **No date, venue, deadline or named recipient exists anywhere since 2026-07-23.** A keyword sweep of the full ambition timeline for deadline/venue/conference terms returns one unrelated hit (LTS patch dates). `map.md`'s Destination is undated.

## 1. Today's ask, verbatim (SV)

`2026-09-02T12:33:43.667Z`, invoked as `/mattpocock-skills:wayfinder`:

> "review everything that has been done, new version of fable just landed with greater reasoning abilities, so you can better understand everything that has been build and **assess if its in anyway fit for purpose**, where the gaps are, ultracode use a range of models for all your research, **any questions about the underlying goals let me know**. no rush, take your time, depth and accuracy over speed and cheap. be exhaustive..."

He names no purpose. He explicitly invites the question. He invoked a *charting* skill, so he expects a route out, not only a grade.

## 2. The eight purposes the record supports

**P1 — A touring conference talk superseding the 2022 one.** `2026-07-23T15:08` (SV): *"principal engineers and leaders, they know their shit, go as long as you need to explain a narative like the original policy as verionned code talk"*; `15:18`: *"I need a spec for the talk first, and from that falls out the technical spec for delivery"*; `15:22`: *"work backwards from the talk spec... the talk itself, lets plan for that as a first class citizen"*; `19:17`: *"Agree. It'll tour"*; `2026-07-31T18:09`: *"you've produced a pitch deck, not a demo deck"*; `2026-08-25T18:05`: *"Make sure that we're covering all of the features that we built... the whole lot. the talk should fit within 20 minutes"*.

**P2 — A demo of a built system, originally for the sponsor.** `2026-07-23T15:50` (SV): *"a preference to try and demonstrate how flux plays a part in it, since control plane are sponsoring the work"*; `2026-07-24T17:20` and `2026-07-31T12:11`: *"you're pitching to the ceo of control plane who is funding the development"*; then `2026-08-19T17:51` (SV): *"we don't need to ask for funding, we've basically built it right, this is a demo of it all"*. The funding ask is dead by his own words; the sponsor relationship has never been restated since July.

**P3 — Put technological risk on the balance sheet.** `2026-07-23T15:37` (SV): *"my underlying philisophy that i'd like to find a way to **hint at** is that it might enable one to actually put technological risk on the balanace sheet of the business, be that for the biz value, insurance or other reasons"*; same turn (SV): *"go deep on the balance sheet, **we can always cut it out**, but at least then it'll be proved comprehensively"*; `2026-08-19`: *"the financial risk of 21707 doesn't seem sane to the same on every org, its proporiate to the org right? maybe think about describing it as a cost per customer?"*; reversal 20 (2026-08-28) ordered attachment/limit/exclusions/TVaR transfer and a seventh signing party. Note the verb: *hint at*, and *we can always cut it out*.

**P4 — An economic model and a feeds marketplace.** `2026-08-19T19:15`: *"so a gartner or others could publish risk and regulation fine things, and news feeds that can all be then consumed by your organisation's implementation, you can pay for these just like your financial times or bloomberg subscription"*; *"we've developed a reference arch, and a platform but also a whole economic platform and model for risk feeds"*; and the north-star sentence, `2026-08-27T16:19` (SV): *"one loosely coupled 'system' but its a broader whole eco-system, with the orgs as an example consumers to demonstrate the whole eco-system operating"*.

**P5 — Prove the corrected 2022 thesis as running code.** `2026-07-23T15:08` (SV): *"remember the policy is just like a linting pack as a dependency"*; `2026-08-21`: *"the intent was never to inherit from tiself, it was to inherit from others... like an object oriental[ted]"*; re-grill 2: *"copy the behaviour of how say eslint linting packs are versioned, and how you can supersede, mashup, join them, republish, inner source etc"*; reversal 21: *"versioned policy is the spine"*. The in-tree statement (`docs/HISTORY.md:18`, assistant-authored, never contradicted): *"re-implements that corrected thesis faithfully, on Flux CD, as a real, runnable, live-verified system — not a slide deck."*

**P6 — Model everything; build only the demo slice.** `2026-08-04T13:17`: *"the ambition and scale should be everything, so that everything is modelled. **We don't need to necessarily build everything to demo that.** Let's plan out the whole big thing. Then work backwards to what's needed to demo it"*.

**P7 — Build it all; nothing is a nice-to-have.** `2026-07-23T18:07`: *"nothing is a nice to have, you're either building it or your not"*; `15:50` (SV): *"we're not short of time, lets make it real, we're only building a ficticious organisation, cluster, applications, its not applying to a real legit business. **no cuts will be tolerated**"*; `2026-08-27`: *"i'm interested in coverage and depth more, and less in the speed"*; `2026-08-28T15:22` (SV): *"Pre existing is not acceptable. Fix them. **It's not good till it's green** even if you need to scope slip to back fix stuff"*.

**P8 — A stepping stone to an AI that disposes inside a priced cage.** Re-grill 29: *"Assume a sig check that ids a different entity but **this is a stepping stone for allows the ai to do it all**"*; re-grill 37: *"The twin acts inside a priced cage; propose-only is the outermost setting; Article 22 floor"*; `2026-08-25T13:31` (SV): *"i merged them all, read and reviewed nothing... change the rule, that is my instruction and it is specific and authoritive"*; `2026-08-31T13:51` (SV): *"Commit. Sign. Push. Merge  Explicit instruction"*.

## 3. Silences

| # | Silence | Evidence |
|---|---|---|
| S1 | **No purpose has ever been put to the owner as a question.** All 41 re-grills, 22 reversals and 7 GAPS Tier-0 items are mechanism or design questions. Nearest: `P208` (demo *subjects*), `P204` (power layer). None asks what it is for, who receives it, or when. | REGRILL-ANSWERS.md rows 1–41; GAPS.md 0.1–0.7 |
| S2 | No date, venue, recipient or deadline since 2026-07-23 | timeline sweep; map.md Destination undated |
| S3 | No definition of "fit for purpose" or of done-for-the-whole; map stops at "hand off to `/to-spec`" | grep → 0 hits |
| S4 | Whether a real third party is ever meant to occupy the adopter role | NORTH-STAR:21; no owner words either way |
| S5 | Whether any of it is reusable. **The hub carries no licence at all** — `gh api repos/policy-as-versioned-flux/policy-as-versioned-flux/license` → HTTP 404, no `LICENSE*` on disk — while all eight unit repos are Apache-2.0 | verified live |
| S6 | Whether the successor must beat the reference implementation it supersedes | NORTH-STAR:68 |

## 4. Contradictions

**C1 — The yardstick is mine, not his (the sharpest).** `NORTH-STAR.md:40` says of the seven-step demonstration: *"(my proposal, derived from the twin's demo-slice sequencing and your August 19 words)"*. §5 (the truth surface) and §7 carry no owner attribution at all. §3 principle 2 concedes: *"That a refusal is therefore the bottom rung reached by the £, rather than a separate mechanism, is my reading, not your words."* The ratification is one line — *"I agree witht he northstar"* (`2026-08-27T16:19:55Z`, SV) — in the same turn as *"walk me through the 41 re-grills, one at a time, plain simple short english"*. Every ticket, the map's Destination, the 84-script denominator and every "not fit" verdict in this review descend from §4 and §5.

**C2 — Build everything vs model everything.** P7 (2026-07-23) vs P6 (2026-08-04). Never reconciled in any document.

**C3 — The talk: driver or byproduct.** *"work backwards from the talk spec"* (2026-07-23) vs `.scratch/twin/spec.md:421` and `map.md:43,158` *"The conference talk is a byproduct of the real system, never its driver"*, carried into `NORTH-STAR.md:64` and attributed there to *"(Twin map, 2026-08-12, kept.)"* — my document, not his. `appendices/G-drift-findings.md:1498` records the pair as never reconciled.

**C4 — "A human merges."** `NORTH-STAR.md:34` vs `2026-08-25T13:31` (SV), implemented as `twin/ENACT_MODE` (checked-in, currently `operations`) with the instruction recorded verbatim in `twin/enact_guard.py`'s docstring, plus re-grill 29's stepping-stone answer.

**C5 — The locked door.** The mea culpa names access control, data protection and cryptographic key management as needing *"a locked door"* (`research/03:124-128`) vs NORTH-STAR §3.2 *"There is no gate"* — bridged by a sentence the north star itself flags as my reading. The estate ships no policy in any of the three.

**C6 — Three coexisting versions.** `research/03:40-42, :207-208` (the runtime *must* support ≥3, *"non-negotiable"*) vs `distribution/versions.yaml:77`, which declares exactly one element (`4.0.0`) — verified. The only machine-opened, human-merged retirement PR in either org is `fleet#69` (2026-08-15), in the org NORTH-STAR §6 supersedes. He has never been asked directly whether the ≥3 rule still stands.

**C7 — Fictitious by instruction, priced as if real.** *"we're only building a ficticious organisation... its not applying to a real legit business"* (SV) vs a signed insurer quote written against driftwood's signed exposure.

**C8 — The bare-agree corrective did not take, and the batch shape was his own instruction.** Owner 2026-08-27: *"i probably did say 'agree' because i got tired/overhelmed with questions"*. The corrective — `GAPS.md:93` rule 1, *"No recommendation attached to an architectural question"* — was **dropped** when the rules were copied into `map.md:16` (five of six carried; rule 1 absent). But then `2026-08-28T08:24` (SV): *"Process all grillings to generate the recommended options and then I can walk them... Do as much as you can without stopping to wait on me to answer anything"*, answered at `10:43` (SV) with *"ive already read the recommendations and I can't find fault with a single one. Well done. Get everything ready for me to then to-spec"*.

**C9 — Funder audience retired, never replaced.** P2's two halves.

## 5. The twelve questions

Recommendations are the review's own calls, placed **after** the trade so they can be ignored — `GAPS.md:93` rule 1 forbids attaching one, and this brief required one; this is the honest way to satisfy both.

**Q1. What is this for, who receives it, and by when?**
*Can't proceed:* every dimension returned "fit as X, not fit as Y". The analysts agree on facts and disagree on the yardstick. Today's ask names no purpose; the phrase appears nowhere in the repo; no date/venue/recipient since 2026-07-23.
*Verdicts:* (a) touring talk for principal engineers and leaders → **NEARLY FIT**; binding defects shrink to three (stale deck, three unfired beats, the RUNBOOK's untrue reconcile line). (b) reference implementation ControlPlane lifts into client work → **NOT FIT**, cheapest blocker legal (no hub licence). (c) a system a fourth org could adopt → **NOT FIT, not close**. (d) the argument itself, as a written artefact → **MOSTLY FIT**.
*Recommend:* (a) primary, (d) secondary, (b) downstream at the cost of one `LICENSE`. It is the only purpose every dated instruction supports without contradiction, and the only one under which the estate is already close.

**Q2. Is NORTH-STAR §4 your definition of done, or mine?**
*Can't proceed:* §4 says "my proposal"; §5 and §7 have no owner attribution; the ratification is one line. If §4 is mine, "not fit" is a compliance statement about a yardstick he did not write.
*Verdicts:* (a) it is his definition of done → **NOT FIT** (step 3 never once; step 5's clock failed both firings; step 4 on one adopter of three). (b) a build order, not a definition of done → **FIT AS WORK IN PROGRESS**; ~20 of 38 shortfalls become schedule items. (c) wrong demonstration → stop and re-derive.
*Recommend:* (b). His 2026-08-04 words describe exactly a modelled ambition with a chosen slice; his 2026-07-23 words describe the opposite; this settles C2. Folded in: does step 2 count as done when driftwood #20 raised the pin but the price did not move?

**Q3. Does "≥3 coexisting versions with a retirement window" still bind?**
*Can't proceed:* it is the one thing his own post calls what the runtime *must* support and the synthesis calls non-negotiable; the estate declares one; the gate's bar is two; ticket 58 Q1's remedy reaches two; the retirement *window* has no mechanism at all and the decided replacement (ticket 13 D5) is unbuilt.
*Verdicts:* (a) still binds → **NOT FIT, critical**; ticket 63 insufficient. (b) superseded by cages → the sharpest criticism dissolves, but the estate then has no promise to an adopter who is behind. (c) binds and the legacy org already did it → the successor is worse than what it supersedes on the thesis's headline claim.
*Recommend:* (a), scoped — three declared lines and a priced supersede, not three product lines. Folded in: do the 14 legacy repos get a dated "superseded reference implementation" banner now?

**Q4. Is the £ a decision instrument or a balance-sheet quantity?**
*Can't proceed:* his verb was *"hint at"* and *"we can always cut it out"*; reversal 20 then ordered a real insurance structure, and a second signed party now writes a layer against driftwood's exposure. The estate publishes the figures with no qualifier.
*Verdicts:* (a) ordinal comparison instrument → **FIT**; the 2,179% implied loss ratio becomes a labelling defect fixed by one sentence. (b) a quantity a CFO books and a carrier cedes against → **NOT FIT, major** (editorial frequency constant, n=2 magnitudes, platform-held loss fixture, quote and exposure cannot both be believed).
*Recommend:* (a), stated on the artefact. Folded in: is `appetite.tolerance` one quantity or three? Is the insurer a real second opinion or an illustrative counterparty — and must an adopter cut a tag whose tree actually carries `exposure` before that row counts?

**Q5. "There is no gate" — your words, or my reading?**
*Can't proceed:* NORTH-STAR:31 says the bridge is my reading. His own blog names three things needing a locked door; the estate ships policy in none of them; encrypt-at-rest lives only in the hub harness; two `Deny` policies ship anyway and three documents disagree about whether they may.
*Verdicts:* (a) cages all the way down → internally coherent, but publishes a doctrine contradicting his own post, and the two Denys must become the bottom rung. (b) the locked door survives for those three → **NOT FIT** on the thesis's refined split.
*Recommend:* (b), narrowly. `verify/proportionality` already derives Audit-vs-Deny from each party's signed £ band — the best single piece of thesis fidelity in the estate — and simply has no shipped subject. Folded in: does "everything is always caged" bind kube-system, Kyverno, Flux, cert-manager and COTS, or only workloads that claim a version?

**Q6. Does "a human merges" still bind?**
*Can't proceed:* principle 5 says it; his 2026-08-25 instruction changed the rule and is recorded verbatim in code; re-grill 29 names AI disposal as the end state. Ticket 74's definition of done cannot be written until this is settled.
*Verdicts:* (a) it binds and means something → **NOT FIT**: proposer, reviewer, merger and signer are one identity in all nine repos, zero rulesets, and the proposer's own record asserts a signature it does not have. (b) stepping stone → the most distinctive claim is untested on itself: the AI's only restraint is a mode file the AI writes.
*Recommend:* (a) for the demonstration, (b) recorded as the end state. Step 3 is where an audience decides whether this is governance or automation.

**Q7. Are driftwood, tuppence and ludlow props, or plausible firms?**
*Can't proceed:* his instruction was fictitious *and* uncut. Today all three sit at the ladder's bottom rung on their own signed numbers, two past its end; tuppence and ludlow publish no `size`; the pivot beat is arithmetically foreclosed.
*Verdicts:* (a) props → tune the fixtures, criticism dissolves, the "grounded not emotional" claim weakens slightly and should be stated. (b) plausible firms → step 3 can never fire from a clock and the demonstration needs a different pivot.
*Recommend:* (a), said out loud. Folded in: is a fourth adopter — one he did not author — a goal? Three copy-pasted adopters is one answer; three instances of a pinned shared package another.

**Q8. What is the truth surface for, and what would "green" mean?**
*Can't proceed:* his own dated answer exists and no document cites it — `2026-08-28T15:22` (SV) *"It's not good till it's green"*. Against it: 21 TRUTH lines, none `fail=0`; run 21 `57/7/18` of 84; 12 scripts can never exit 0 on the runner because the clock creates no cluster, so the real ceiling is 70 (65 today) and nothing states it.
*Verdicts:* (a) green = fail 0, every skip owned → **NOT FIT today**. (b) green = offline half plus adopters' sampled facts, ceiling published → **CLOSE TO FIT**. (c) private regression alarm, not citable evidence → the deck must stop quoting it as the latter.
*Recommend:* (b) plus publish the ceiling. He has already accepted the ephemeral-KinD lane (re-grill 1). Folded in: should the hub clock fire *after* the adopters' lanes? Should `clone-estate.sh` grade at signed tags, as its own comment promises?

**Q9. Is the talk the driver or the byproduct?**
*Can't proceed:* his instruction twice on the day he set direction, vs my framing carried into the ratified document and attributed to my own twin map. Recorded as never reconciled.
*Verdicts:* (a) driver → the deck's staleness, three unfired beats and the RUNBOOK's untrue narration line become top priority. (b) byproduct → they drop below a dozen other things.
*Recommend:* (a). It is his instruction; the reversal is mine. Folded in: the RUNBOOK says driftwood reconciles the real signed GitHub remote; the script reconciles a git server built on the laptop seconds earlier. Which demo does he want to give?

**Q10. Must the twin forecast, or is scoring a recorded belief the thing?**
*Can't proceed:* NORTH-STAR §2 says "priced forecasts... scored against reality"; `twin/verbs.py:932-956` emits a hand-typed constant and says so at run time; the twin is 54% of executable code. His own words are gameplay and honest scoring — *"It's a weather forecast"*, *"if We don't know where we've been. We can't possibly know where we're going"*.
*Verdicts:* (a) must derive → **NOT FIT at its own headline**. (b) recorded belief, honestly scored → **FIT**, and §2's twin row and §4 step 5 must be restated, because the build deliberately reversed them.
*Recommend:* (b), with the row restated. Folded in: should a world model's beliefs carry a required evidence grade and basis? Is it acceptable for the forward-intel feed — driftwood's largest price line — to stay outside every signed tag and outside `inherits[]`?

**Q11. How do you want to be asked — and is a bare "Agree" a ratification?**
*Can't proceed:* ~84 architectural items are PROVISIONAL on tickets marked `resolved`, which the map's own rule says should stay open. The corrective he prompted (`GAPS.md:93` rule 1) was dropped from `map.md:16`. But the batch shape was his own instruction (`2026-08-28T08:24`, SV).
*Verdicts:* (a) bare agree does not ratify → the honest verdict is "the architecture is unratified", and fifteen resolved tickets are misstated. (b) the recommendations are the architecture, decided and recorded as the assistant's → the vocabulary retires and `Status: resolved` becomes honest.
*Recommend:* (b), explicitly recorded, with this question set as the exception list. The panel-verdict shape (five conflicts, three lenses, one page) is the only format that has ever drawn a reasoned reply. Folded in: put the fifteen assistant-resolved cross-ticket conflicts as one round? Interrupt on a mid-run architectural discovery, or accept the build deciding?

**Q12. Is the identity and attestation substrate spine, or shelf?**
*Can't proceed:* §1's closing clause is "every actor is attestable". The artefact half is real (24/24 tags Rekor-verified). The actor half — SPIRE, mTLS, SPIFFE authz, OpenBao, device SVIDs, human login — has never been observed on any citable run; all six scripts SKIP. Federation is one trust domain with no peer, anchors held as literals in the platform's tree, the tenancy shape §2 forbids. Ticket 12 recorded "spine, not cut" on a bare agree.
*Verdicts:* (a) spine → **NOT FIT** on the sentence that defines the eco-system. (b) designed and shelved → §1 reads "every artefact is attestable", six scripts move to the exclusions file with a reason, and the claim becomes true.
*Recommend:* (b) for this build, (a) as the next thing. Claiming a thing while never observing it is exactly the failure the 2026-08-25 Docker post-mortem exists to prevent. Folded in: protect `main` and `release/*.x` across all nine repos? May the truth workflow run 84 unpinned scripts in the same job that holds a `contents:write` token?

## 6. De-duplication

The 72 dimension `owner_questions` map onto the twelve as: Q1←operability a/d + scope-due-date + engineering-operated-by-others + process-ratification-date; Q2←demo-steps end-to-end + principles-running-workload + step-2-done + living-document; Q3←thesis ≥3-versions + ticket-13-D5 + truth-surface ≥3 + legacy ×4 + operability ticket-58; Q4←all six pound-engine + principles-whose-numbers + participants-exposure-tag; Q5←thesis locked-door + ADR-0007 metadata + principles unversioned-population + orphan-guard-Deny + cage-in-sample-lane; Q6←scope AI-disposal + demo-steps who-merges + proposer-signing (×2) + twin's-own-cage + protect-main; Q7←scope props-or-firms + fourth-adopter + three-orgs-or-instances + size + separation-of-authority + forgetting-curve; Q8←all six truth-surface + engineering-cluster + operability-cluster + scope-cluster + participants tag-vs-branch and red-vs-hole + prove-the-absence; Q9←RUNBOOK-vs-up.sh + push-round-3; Q10←all six twin-validity + thesis-is-the-subject + participants twin-org and publisher-clock + step-5-scope; Q11←all six process-and-record; Q12←security identity-substrate + write-token + ed25519 + trust-instant.

**Deliberately not promoted** (mechanism calls the assistant should take and record as its own, under Q11(b)): the gitsign tagger/notBefore trust instant (ticket 73 owns it; the correct instant is the Rekor signed-entry timestamp); re-grill 6's full-combination coverage (already answered, binding); the twin CI colour; selfcheck-vs-pytest; the currency-controller retirement (withdraw it — the recorded reason was a collision between two senses of "currency").

