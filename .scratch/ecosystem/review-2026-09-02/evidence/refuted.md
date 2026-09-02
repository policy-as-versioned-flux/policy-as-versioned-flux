## thesis-fidelity TF-04 — No policy in the estate governs access control, data protection or cryptographic key management
## What I confirmed (the auditor's inventory is accurate)

`platform/distribution/policies/v4.0.0/` contains exactly the six files claimed. Reading each: `require-nonroot.yaml:24` = `validationActions: [Audit]`; `posture-trust-boundary.yaml:15` = Deny with `:38` `expression: variables.posture == variables.claimed`; `cage-tier.yaml:6` MutatingPolicy; `cage-netpol.yaml:6` GeneratingPolicy; `stamp-posture.yaml:6` MutatingPolicy; `priorityclasses.yaml` = 4 PriorityClass objects.

`versions.yaml:117` renders `policy-version-orphan-guard` (Deny) and `:157` renders `governed-namespace-requires-claim`

## thesis-fidelity TF-06 — The human-governance layer's carrier does not exist: nothing is dated, reviewed on a cadence, or removed if undefended
I re-derived every leg from primary sources.

WHAT HOLDS (auditor's quotes are accurate):
- `sed -n '20,32p' docs/adr/0007-...md` -> line 25-26 verbatim: "Each policy version carries `created`, `lastReviewed`, rationale/`why`, and risk/ethos — as annotations + a versioned `rationale.md`". ADR-0006:19 and ADR-0001:59-60 and CONTEXT.md:127-129 match as quoted; docs/PRD.md:332 says the same.
- `grep -l -i superseded docs/adr/*.md` -> 0013,0014,0015,0016,0018,0024 only. Every ADR header is `status: accepted`. ADR-0007 carries two 2026-07-18 corrections, neither touching the metadata paragraph.
- A

## thesis-fidelity TF-08 — The dependency loop is not wired for policy versions themselves — no Renovate manager watches policy/v*
Full write-up: /private/tmp/claude-501/-Users-cns-httpdocs-controlplane-policy-as-versioned-flux/8c6523c6-66de-4c91-94ed-4ceff16a6a76/scratchpad/review/refute/TF-08.md

WHAT HELD (I re-read every file myself):
(1) No adopter renovate.json declares a manager over policy/v*. driftwood/renovate.json:13-69 has four customManagers with depNameTemplates .../nist (:24), .../platform (:37), feeds/{{feedName}} (:49), insurer/{{feedName}} (:64); both git-refs managers match "tag: (?<currentValue>v[0-9.]+)\s*\n\s*commit:" (:21,:34) with versioningTemplate semver. tuppence/ and ludlow/renovate.json are by

## participants P8 — The intelligence publisher has ingested no external datum, and three of the four provenance URLs in the one feed whose rule demands provenance do not resolve
Worked from the fresh feeds clone at /private/tmp/.../scratchpad/units/feeds, HEAD 69c89b0, which matches the TRUTH run=21 line (feeds=69c89b0).

THE HEADLINE CLAIM IS FALSE. All four provenance URLs resolve:

  for u in <the four URLs from news/v1/feed.json>; do curl -s -o /dev/null -w '%{http_code}' "$u"; curl -sL "$u" | grep -o '<title>[^<]*</title>'; done
  200 | <title>Release v1.0.0 · policy-as-versioned-ico/ico · GitHub</title>
  200 | <title>Release policy/v3.0.0 · policy-as-versioned-platform/platform · GitHub</title>
  200 | <title>Release v1.1.0 · policy-as-versioned-nist/nist · Git

## principles P2-5 — No governed workload is reconciled by Flux anywhere in the estate
The auditor's file-level quotes are mostly accurate, but the inference from them is wrong, and the headline claim is directly contradicted by a live read-only observation.

## 1. A governed workload IS reconciled by Flux, and IS caged — right now

`kind get clusters` -> `c2p-spike / driftwood / ludlow / tuppence` (three named clusters are up; docker running).

```
kubectl --context kind-driftwood -n flux-system get gitrepositories,kustomizations -o wide
gitrepository/driftwood   http://git-server.flux-system.svc.cluster.local/cgi-bin/git/driftwood.git  32d  True  stored artifact for revision '

## principles P2-1 — Human and device access is a gate with a DENY, not a priced cage
Every file quote in the finding is real; I confirmed each one. What does not hold is the claim built on top of them: its subject ("the human/device access plane"), its fit impact ("governed by"), and its closing assertion ("no reconciliation") are all contradicted by primary sources.

WHAT I CONFIRMED (all quotes accurate)

1. access.py is a static, £-free table. Full read of /private/tmp/.../scratchpad/units/platform/access/access.py: imports are only `argparse` and `sys` (:28-29) — no fair.py, no cage.py. :36-44 OP_TIER hardcoded (read/list 1, write/exec 2, delete/break-glass/cluster-admin 3

## principles P2-2 — The twin has no cage spec, no tier and no price; what it has is a refusal boundary
## What I confirmed (the auditor's factual spine holds)

1. **Principle 2 names the twin.** `NORTH-STAR.md:31`: "A workload, a human, a device, a model action and **the twin itself** each run inside a cage. The cage spec is the only variable. The £ selects the spec... There is no gate."

2. **The grep result reproduces exactly.** `grep -rln cage twin/` → `twin/enforcement-grades.yaml`, `twin/README.md` — two files, and both hits are the twin *modelling the estate's* cage, not declaring its own: `twin/enforcement-grades.yaml:57` "estate/platform/graded — Kyverno mutate + generate cages a behind

## demo-steps DS-F5 — Step 4 has never passed on a citable run, and its one remaining red is an instrument fault
I re-derived every quoted artefact from primary sources. The factual spine holds; the classification in the title and the Fit-impact paragraph does not, and the map claim is false.

WHAT HOLDS (all independently confirmed)

1. Capture verdict history. `git log --format='%H %ad %s' --date=iso-strict origin/main -- talk/captures/verify_e2e_verify-e2e-step4-flux-reconciles-cage.out` returns exactly four commits: a2094961 2026-09-02T10:11:05Z (run 21), 62eddf80 2026-09-01T21:07:14Z (run 20), aae09206 2026-09-01T09:41:09Z (run 18), b05035e2 2026-08-31T08:09:23Z (run 9). `git show <sha>:<path>` give

## demo-steps DS-F7 — ludlow's observation lane has never fired successfully on a clock
I re-ran the auditor's own command and got a different answer: there are FOUR ludlow drift-sample runs, not three, and the newest is a SUCCESSFUL scheduled one.

1) The run list (primary):
`gh run list --repo policy-as-versioned-ludlow/ludlow --workflow drift-sample.yml --limit 20 --json databaseId,createdAt,event,conclusion`
→ 33636830681 2026-09-02T13:37:12Z **schedule success**
→ 33558858820 2026-09-01T21:02:59Z workflow_dispatch success
→ 33556801679 2026-09-01T20:41:35Z workflow_dispatch success
→ 33517601520 2026-09-01T14:07:55Z schedule failure
`gh api .../actions/workflows/346774311/ru

## truth-surface TS-C2 — The pass ceiling is 70 (65 today), not 84, and nothing states or checks it
I re-derived every number from primary sources. The arithmetic survives; the framing that makes it "critical" does not.

WHAT HOLDS (re-derived, not taken from the auditor):
1. The clock provisions no cluster. `grep -n "kind create\|kind get clusters\|docker\|kind " .github/workflows/truth.yml` → no match (rc=1). GH_TOKEN appears only at truth.yml:110 (the cage step) and :162 (the push); the gate step is truth.yml:92-98 with `env: {VERIFY_TIMEOUT: '900'}` only (the auditor's "121-123" for the cage is wrong; it is 108-110).
2. Run 21's skip set, from the run's own log (`gh run view 33616685427 

## truth-surface TS-M3 — The flux CLI is installed by `curl -s ... | sudo bash`, fifteen lines below a comment claiming every tool is pinned by version and checksum
The artifact half of TS-M3 holds; the causal half — its headline and the reason it is graded major — is wrong, and was already correctly diagnosed and owned by the estate before the auditor looked.

WHAT HOLDS (re-derived from primary sources)

1. The line exists. `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.github/workflows/truth.yml:91` reads exactly `          curl -s https://fluxcd.io/install.sh | sudo bash`. The pinning comment is at :79-81 (auditor cited :77-80), inside the step named at :78 "kyverno, cosign, flux CLIs the offline proofs call": "Every tool the gate observe

## truth-surface TS-M5 — The truth surface is one day behind the estate by declared cron, permanently and deterministically
I confirmed the auditor's raw cron facts but refuted the mechanism, the determinism, the "for ever", the impact, and the ownership claim. Four independent lines.

**1. The declared crons are as quoted (this part holds).**
`.github/workflows/truth.yml:19-20` → `schedule: - cron: '47 5 * * *'`. Adopter `drift-sample.yml:33` in the fresh clones: driftwood `"20 6 * * *"`, tuppence `"22 8 * * *"`, ludlow `"16 9 * * *"`. So 05:47 does precede 06:20 / 08:22 / 09:16.

**2. "can only ever grade yesterday's five-fact sample" is refuted by a direct counterexample the auditor did not look for.** TRUTH run

## truth-surface TS-M7 — The denominator moves silently and no two TRUTH lines are comparable
I opened every file and ran every command myself. Four of the finding's six load-bearing assertions fail; one is true but by ratified design; one narrow gap survives.

**1. The arithmetic in a finding about counting is wrong.** `cat /Users/cns/httpdocs/controlplane/policy-as-versioned-flux/talk/truth.log` (17 lines) plus `git show origin/main:talk/truth.log` (18 lines, run 21) gives totals: 56 (run=local,4,5,6,7,8), 68 (9), 73 (10,11), 83 (12,13,15,16), 84 (17,18,19,20,21). That is five distinct values and **four** changes, not "changed five times".

**2. Wrong line citation.** `cat -n talk/ve

## truth-surface TS-M9 — Five checks are dark because the estate declares one policy version, so the thesis's central claim is currently unobservable
The quoted SKIP strings are all verbatim-accurate and the versions.yaml premise is real, but four load-bearing parts of the claim do not survive re-derivation.

PREMISE CONFIRMED. `git show origin/main:talk/captures/...` reproduces all five SKIP strings verbatim. `gh run view 33616685427 --log | grep -E "SKIP|FAIL|TRUTH "` confirms run 21 grades all five SKIP and emits the cited TRUTH line (pass=57 fail=7 skip=18). `units/platform/distribution/versions.yaml:77` is the sole array element `{ version: "4.0.0", ... }`; `git log --oneline -- distribution/versions.yaml` shows one commit, `3dab34d "e

## pound-engine PE-03 — The exposure total sums lines annualised at different frequencies for the same event, and the twin declares the same regime the ico line prices
I re-derived every quoted artefact and re-ran the estate's own engine. The finding's *numbers* all check out; its *charge* does not.

WHAT HOLDS (re-derived, not taken from the auditor)

1. The total and its three lines. `units/driftwood/composed/HEADER.yaml:609-646` — total `3704381.737952101`, lines uk-gdpr `1787177.0751717847` (source ico, feed penalty-schema v3, with nist pl-2/ra-3/ca-2/ir-8 holes), threat-register `19558.549772440045` (source feeds), forward-intel `1897646.1130078766` (source twin). `python3 -c "print(1787177.0751717847+19558.549772440045+1897646.1130078766)"` → `3704381.

## pound-engine PE-04 — appetite.tolerance is one signed number used as three different economic quantities
I re-derived all four cited sites and then tested the finding's two load-bearing assertions.

CODE FACTS — CONFIRMED (with two citation slips):
- units/driftwood/party.yaml:43-44 — `appetite:` / `tolerance: { amount: 40000, currency: GBP }`. One declaration. Confirmed.
- Reading (1), enforce.py:98-100 exact: `cv = fair.control_value(...)`; `risk_bought = cv["risk_bought"]  # ALE_warn - ALE_deny`; `verdict = "Deny" if risk_bought > tolerance else "Audit"`. Ran it offline: `python3 units/platform/risk/enforce.py decide scenarios/driftwood-cart-pii-tightened.json --org driftwood` -> `residual_war

## pound-engine PE-09 — The falsification instrument runs, disagrees with the model, grades a different number, and is wired to nothing
I re-ran everything offline from the fresh unit clones and the hub, and read origin/main captures. Three of the finding's load-bearing evidential claims do not survive, including the headline one.

WHAT CONFIRMS (I reproduced these exactly):
- `python3 /private/.../scratchpad/units/platform/honesty/calibration.py backtest` → driftwood: model_ale 19558.549772440045, observed_ale 35000.0, var95 30947.91098602646, exceedances 2, exceedance_rate 0.4, verdict "under-prices (too many VaR95 breaches) — recalibrate up". ludlow: model_ale 1025511.0646480098, observed_ale 130000.0, ale_ratio 0.126766062

## twin-validity TWIN-08 — The twin's price is the only pricing parent with no pin, no version resolution, no signature check, and a silent absence
## What holds (I re-opened every file the auditor cited)

**The quoted code is accurate.** `platform/compose/composition.py:1617-1631` (clone at `.../scratchpad/units/platform`, HEAD `46cd775`, which matches the TRUTH line's `platform=46cd775`):

```
1620:    wins. No feed at all is simply no twin entry -- never a refusal."""
1621:    root = Path(adopter_dir).joinpath(*FORWARD_INTEL_DIR)
1622:    majors = sorted((d for d in root.glob("v*") if (d / "feed.json").exists()), ...
1624:    if not majors:
1625:        return None
```
`FORWARD_INTEL_DIR = ("twin", "forward-intel")` (line 308). The nei

## security-spine SS-01 — The only cluster-side signature check systematically rejects genuine tags on a one-second timestamp race, and its own fixture cannot expose it
I re-derived every number from primary sources. The mechanism is real; three load-bearing claims around it are not.

## CONFIRMED (I reproduced all of it)

**The code does evaluate at tagger time.** `verify_gitsign.py` (units/platform/identity/gitsign-verifier/verify_gitsign.py) line 174 `at = tagger_epoch(payload)`, lines 200-202 `openssl verify -CAfile roots -untrusted intermediates -purpose any -attime str(at) leaf.pem`. (Auditor cited :191-196 and :181-206; actual is :200-202 and :188-213 — off by ~9-12 throughout, including "reconcile_one lines 344-349" for the suspend patch, which is act

## engineering-quality EQ-03 — The three adopters are copy-pasted, have genuinely diverged, and fixes do not cross between copies
I re-ran the comparison with my own script (/private/tmp/.../review/skeptic_eq03_norm.py) rather than trusting the auditor's.

WHAT REPRODUCES EXACTLY
- "files present in >=2 adopters: 39 / identical after normalising: 15 / drifted: 24" — exact match.
- wc -l: driftwood/.github/scripts/adopter-gate.py 1087, tuppence/.github/scripts/adopter-gate.py 661, ludlow/.github/scripts/adopter_gate.py 1213. Filename drift to underscore confirmed.
- grep -c '^\s*- name:' shift-left.yml: driftwood 16, tuppence 12, ludlow 15. tuppence's "version cross-check gate" is at :236, after the adopter gate at :152; 

## engineering-quality EQ-05 — 30 of 82 captures end with no verdict line, and the check that enforces the convention covers six scripts
I re-derived every number and re-read every file rather than trusting the quotes.

WHAT HOLDS

1. The arithmetic. `git -C <hub> ls-tree --name-only origin/main talk/captures/ | wc -l` = 82. A python pass over `git show origin/main:talk/captures/<f>` computing the last line (both `tail -1` semantics and last-non-blank; identical result) gives exactly 30 whose last line does not begin PASS:/FAIL:/SKIP: after stripping ANSI. So 30-of-82 is right.

2. verify-all.sh:60 is verbatim `last="$(tail -1 "$cap" | cut -c1-160)"` (grep -n 'tail -1' talk/verify-all.sh -> "60:").

3. The scope of the honesty 

## operability-adoptability O1 — The thesis's headline runtime claim cannot be demonstrated at all today
The one-version fact is real, and two of the three properties do hold up. The headline framing ("undemonstrable with or without a cluster", applied to all three, coexistence first) does not, and it is contradicted by a PASS-graded check inside the very run the finding cites. Four supporting assertions are also wrong.

## 1. The one-version fact: CONFIRMED

`cat -n /private/tmp/.../units/platform/distribution/versions.yaml` (platform @ 46cd775, the run-21 SHA):
- line 77 is the only array element: `- { version: "4.0.0", tag: "policy/v4.0.0", commit: "64635df...", bump: "major" }`
- lines 31-60 

## operability-adoptability O2 — The committed deck shows seven grey slides while five of its checks pass
Re-derived from primary sources; three of the finding's four limbs do not hold as stated.

1. THE COUNT IS WRONG, AND THE LOAD-BEARING EVIDENCE QUOTE IS FALSE.
`git show origin/main:talk/deck.md | grep -n "status="` returns seven beat comments:
  line 63: beat step=1 status=SKIP
  line 80: beat step=2 status=SKIP
  line 104: beat step=3 status=SKIP
  line 121: beat step=4 status=SKIP
  line 150: beat step=5 status=SKIP
  line 167: beat step=6 status=SKIP
  line 184: beat step=7 status=PASS
Six SKIP, one PASS. The finding's title ("seven grey slides"), its claim ("grades all seven NORTH-STAR se

## operability-adoptability O6 — The estate's signature linchpin is bespoke, unversioned, root-running tooling in an estate that claims 'no bespoke tooling'
HOLDS (re-derived, not taken from the auditor):

1. 417 lines. `wc -l .../units/platform/identity/gitsign-verifier/verify_gitsign.py` -> 417.
2. ConfigMap-mounted stock image. deployment.yaml:60 `image: python:3.13-alpine@sha256:540c7d91f98ff6880174c40e99067bf5941eb54d818a7a5e094d188b196a934d`; :63-66 `apk add --no-cache git openssl >/dev/null` then `exec python3 /app/verify_gitsign.py controller`; :83-84 `configMap: { name: gitsign-verifier }` generated by kustomization.yaml configMapGenerator.
3. No securityContext at all. `python3 -c` yaml parse of deployment.yaml prints `pod securityContex

## operability-adoptability O8 — The KiND proof is never exercised by the truth surface
Full write-up: /private/tmp/claude-501/-Users-cns-httpdocs-controlplane-policy-as-versioned-flux/8c6523c6-66de-4c91-94ed-4ceff16a6a76/scratchpad/review/skeptic/O8.md

CONFIRMED PARTS. `grep -i -n kind /Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.github/workflows/truth.yml` -> exit 1, no output; `grep -rln "kind create cluster" .github/workflows/` -> nothing. The clock installs only gitsign/kyverno/cosign/flux (truth.yml:70-91). Run 21 has exactly 18 SKIPs: I tallied the final verdict line of all 82 captures on origin/main and got PASS=43, pass-shaped-other=14, FAIL=7, SKIP=18, i.

## process-and-record P2 — ~84 provisional architectural items are Status: resolved against the record's own rule, with no route, ticket or check that ever ratifies one
I re-derived every number and quote from the files. The arithmetic mostly holds; the interpretation does not.

WHAT I CONFIRMED (auditor's counts are largely right)

1. map.md:16 verbatim — `grep -n "stays open" .scratch/ecosystem/map.md` → "16:- Process rules (from the drift review): at most five decisions put to the owner per day... a bare \"agree\" or letter does not ratify architecture, so a decision is recorded with the owner's reason or it stays open;..."

2. Item count. My own script over `## Answer` sections of `.scratch/ecosystem/issues/*.md` (counting `^\d+\.\s` items, stopping at th

## process-and-record P12 — Ticket 29's false three-adopter claim is still uncorrected four days after it was found, while ticket 40's equivalent was corrected
I opened every source rather than trusting the quotes. The finding's substantive observations hold, but two of its three load-bearing framings — the ownership claim and the elapsed-time claim — are false against primary sources, and those are exactly what carry it to "major".

WHAT HOLDS (verified):

1. Ticket 29's Answer says what the auditor quotes. `cat -n /Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.scratch/ecosystem/issues/29-adopter-twin-overlay-twin-release-tag-and-twin-evals-in-the-.md` line 17: "Built 2026-08-29 ... The twin overlay lives in the adopter repo with the wor

## scope-and-coherence F1 — The cage ladder is saturated: §4 step 3 cannot occur from any clock-driven mover
I re-derived every number and read every cited file and log myself.

WHAT HOLDS (all confirmed):
- `platform/graded/cage.py:82-127`: TIERS reduce = baseline 0.30 / restricted 0.70 / quarantine 0.92 / isolated 0.98; `caged_residual` = ale*(1-reduce) (line 152-154); `select_tier` walks ORDER, breaks on first `<= tolerance`, `else: tier = ORDER[-1]` (lines 182-187). `isolated` dials are reach "none", evictFirst True (cage.py:106-111, auditor said 105-111 — 105 is a comment).
- driftwood's own package agrees: `driftwood/selection-policy/selection_policy.py:32-33` LADDER/FAIL_CLOSED, `:90-97` `unde

## scope-and-coherence F4 — The estate's central runtime claim is structurally outside the only instrument any document may cite
Re-derived from primary sources; full note at /private/tmp/claude-501/-Users-cns-httpdocs-controlplane-policy-as-versioned-flux/8c6523c6-66de-4c91-94ed-4ceff16a6a76/scratchpad/review/refute/F4-scope-and-coherence.md

1) The quoted evidence does not exist. `grep -n "kind\|cluster" .github/workflows/truth.yml` returns NOTHING (exit 1), locally and on origin/main (`git show origin/main:.github/workflows/truth.yml | grep -n -i "kind\|cluster"` -> exit 1). truth.yml:78-91 installs kyverno/cosign/flux and contains neither word. The underlying fact (truth.yml creates no cluster) is true; the auditor'

## scope-and-coherence F6 — Two tag-naming schemes coexist, one contradicts its own repo's declared scheme, and the tooling models one
Full working: /private/tmp/claude-501/-Users-cns-httpdocs-controlplane-policy-as-versioned-flux/8c6523c6-66de-4c91-94ed-4ceff16a6a76/scratchpad/review/refute/F6-tag-naming.md

WHAT HELD. `git -C <clone> tag -l` in the eight fresh clones: feeds = threat-register/v1.0.0, threat-register/v2.0.0; platform = policy/v2.0.0..policy/v4.0.0 plus bare v0.1.0..v2.0.1; insurer = v1.0.0 only; ico v1.0.0/v3.0.0; nist v1.0.0/v1.1.0; adopters v1.0.0/v1.1.0. insurer/quote/{driftwood,tuppence,ludlow}/bump.yaml:4 each say "cut-release.yml signs the tag quote-<adopter>/vX.Y.Z". insurer/party.yaml:60-77 publishes 

## scope-and-coherence F7 — A platform-held, untuned knob suppresses an adopter's own priced tier proposal for up to eight weeks
I re-derived every leg from the fresh default-branch clones (platform=46cd775, driftwood/tuppence/ludlow at run-21 SHAs) and live gh. Three of the finding's four load-bearing legs fail; two facts survive.

WHAT HOLDS
1. The file is where the auditor says. `units/platform/wargamer/rejection-decay.yaml` lines 20-23: `version: 1.0.0`, `half_life_days: 30`, `reject_suppress: 0.5`, `tuned_against: "not yet tuned against real closes -- 30 days is one review cycle..."`. `rejection_ledger.py:45 CALIBRATION = HERE / "rejection-decay.yaml"`.
2. The eight-week arithmetic in the comment (lines 12-13) is c

## scope-and-coherence F9 — The thesis's own unrevised runtime requirement (>=3 coexisting versions) is at one, and the estate has recorded a structural reason it may never be met
The finding splits into a factual half (holds, and is largely a restatement of the previous review's M11) and a structural half ("an old line can never be patched", "unreachable by construction"), which primary evidence contradicts. I mark it refuted because the load-bearing new claim is the structural one, and it does not survive.

WHAT HOLDS (re-derived, not taken from the auditor)

1. The thesis's ≥3 requirement, verbatim, at the cited lines:
   research/03-blogs-thesis.md:40-41 — "The **runtime must support multiple policy versions simultaneously** — at least three semver / versions — to a

## scope-and-coherence F11 — The instrument's attention and the codebase's mass both sit where the ambition does not
I re-derived every number from primary sources rather than trusting run21-grades.txt, then checked the file against the citable TRUTH line.

DISCOVERY (independent of the auditor). talk/verify-all.sh:45 is `mapfile -t SCRIPTS < <(find .estate-clone verify -name 'verify*.sh' -not -path '*/.work/*' -not -path '*/.git/*' | sort)`. Running that glob over the fresh default-branch clones: `for u in platform nist ico driftwood tuppence ludlow feeds insurer; do find $S/$u -name 'verify*.sh' -not -path '*/.git/*' | wc -l; done` -> platform 45, nist 3, ico 4, driftwood 4, tuppence 4, ludlow 3, feeds 3, 

## legacy-and-lift L1 — The decided lift, as scoped, cannot make a feed re-price anything real
Every literal quote in L1 checks out; the claim built on them does not.

WHAT HOLDS (I re-derived each):
- `grep -n "FEED_CONVERTERS" /private/tmp/.../units/platform/compose/composition.py` → 271, 546, 547, 1540. Lines 271-274 are exactly `{"threat-register": ("feeds","to_fair_scenario.py"), "penalty-schema": ("schema","to_fair_scenario.py")}`. Line 1540 `if name not in FEED_CONVERTERS:` → 1543 `raise Refused(f"missing instrument: feed {name!r} declared by {adopter_party} has no converter this composition can price through")`. Confirmed verbatim.
- `grep -niE "deploy/pod|image|inventory|sbom|S

## legacy-and-lift L8 — Two orgs make overlapping present-tense claims with no signpost anywhere a reader lands
Re-derived every component from primary sources. Record at /private/tmp/claude-501/-Users-cns-httpdocs-controlplane-policy-as-versioned-flux/8c6523c6-66de-4c91-94ed-4ceff16a6a76/scratchpad/review/refute/L8.md

HELD (re-derived independently):
- `gh api orgs/policy-as-versioned-flux` -> {"login":"policy-as-versioned-flux","name":null,"description":null,"blog":null,"public_repos":16}. No description. Confirmed.
- `gh api repos/policy-as-versioned-flux/.github` -> 404. The .github repo does not exist at all, so no profile README. Confirmed (stronger than the auditor's contents-path 404).
- 16 rep

