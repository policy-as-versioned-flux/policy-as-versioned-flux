# STEELMAN — the eco-system as built on 2026-09-02

Citable line: `TRUTH 2026-09-02T10:11Z run=21 hub=7b92990 ... pass=57 fail=7 skip=18 excluded=2 total=84`

Everything below I verified in a primary source. Where I re-derived a fact on this machine
rather than quoting a capture, I say so and give the command.

---

## The ten most impressive things that are real and proven

### 1. A complete keyless signature spine across eight independent GitHub organisations — 24 of 24 tags, no exceptions

I re-derived every one myself, not from a capture:

```
cd scratchpad/units && for u in platform nist ico driftwood tuppence ludlow feeds insurer; do
  for t in $(git -C $u tag -l); do git -C $u -c gpg.format=x509 -c gpg.x509.program=gitsign tag -v "$t"; done; done
=== good=24 bad=0 ===
```

Every tag returns `Good signature from [https://github.com/policy-as-versioned-<org>/<repo>/.github/workflows/cut-release.yml@refs/heads/...]`
and `Validated Rekor entry: true`. Each identity is anchored to *that repo's own* workflow —
platform's tags name platform's cut-release.yml, ico's name ico's. No unsigned tag, no bad
signature, no cross-org identity anywhere in the estate.

Two details that make this better than a checkbox:

- `policy/v2.0.1` is signed from `refs/heads/release/2.0.x`, not main, and its commit
  `ebc4ff5` is **not an ancestor of origin/main** (`git merge-base --is-ancestor` → NO). The
  thesis's "older lines are patchable" was exercised for real, on a maintenance branch, and
  the release identity regexp
  (`units/platform/.github/workflows/release.yml:54`) admits exactly
  `(main|release/[0-9]+\.[0-9]+\.x)` and nothing else.
- The org topology is real, not a directory convention. `gh api orgs/policy-as-versioned-<u>`
  returns `repos=1` for all eight, created 2026-07-23 (six) and 2026-08-28 (feeds, insurer).

### 2. Semver is computed from measured verdict movement, and a real release was cut by that computation

This is the one place the build *exceeds* the 2022 thesis, which only asked that policy carry a
semver number.

`units/platform/computed-semver/evidence/4.0.0.json` records:
`outcome {result: passed}`, `bump {declared: major, computed: major}`,
`counts {old: 153, new: 152, union: 164}`,
`corpus_checksum sha256:ae12308f64efd…`, `wall_clock 88.78s`, 28 named movement entries,
`not_looked_at: []`, and a `limits[]` array naming three open limitations against its own interest.

Run 21's capture `.estate-clone_platform_verify-first-gate-determined-release.out` confirms the
ordering: *gate → commit evidence → correct the array → tag → push*, and that
`policy/v4.0.0 → 1d8cec2…` resolves **one commit ahead** of the commit the array names
(`64635df…`), which is the only shape in which the number can have been determined before the tag.

I ran the gate's own selfcheck on this machine — `python3 computed-semver/gate.py --selfcheck`,
exit 0 — and it asserts, among ~30 properties, that *"a declared bump weaker than computed
publishes DEGRADED (tier quarantine, a prerelease suffix on the untouched base number) … the
declared number is never rewritten"*, that a declared version that already exists refuses, and
that the two historical bumps (1.0.0→2.0.0 major, 2.0.1→2.1.1 minor) re-derive exactly.

### 3. A five-parent, pinned-by-tag-and-commit inheritance graph across five separate orgs, machine-checked against the real remotes

`units/driftwood/composed/HEADER.yaml` records each parent as `{party, kind, version, sha}`:

```
platform  implementations 2.0.1  533dccb0a823001b396fd60ab08014bf75065a37
nist      controls        1.1.0  33a05df1f5241bca6ffbc1c69a70075cdb7a5819
ico       feed penalty-schema v3 e1fb8eb5663e50088b13d872a4e44112476f516e
feeds     feed threat-register v2 50a0b330a730f4f9ee9520561b0c05c8be4c9268
insurer   feed quote-driftwood v1 db767055119292e400edd63ed260785ce605eb4e
```

Run 21's `verify_feed-contract_verify-feed-contract.out` ends PASS after ~80 assertions
including 24 individual pin resolutions against real remotes via `git ls-remote --tags`
(`verify/feed-contract/feed_contract.py:86`), e.g.
`PASS: driftwood pins feeds/feed/threat-register@v2: tag threat-register/v2.0.0 on feeds`.
Unreachable returns None → SKIP, never a pass.

The composed artefacts are demonstrably *generated*, not copied: diffing
`units/platform/distribution/policies/v4.0.0/*.yaml` against each adopter's
`composed/policies/v4.0.0/*.yaml` shows only YAML re-serialisation plus three added provenance
fields — `composed-for: driftwood`, `inherited-from: platform@2.0.1`,
`source-path: distribution/policies/v4.0.0/<file>` — on every object, in all three adopters.

### 4. Proportionality is a computation, not an opinion — I re-derived it on this machine

The mea culpa's central distinction (lane-keeping assist vs a locked door) is the hardest thing
in the thesis to make mechanical. The estate made it arithmetic:

```
python3 units/platform/risk/enforce.py decide verify/proportionality/scenarios/encrypt-at-rest.json --org <o>
driftwood {'verdict': 'Audit', 'risk_bought': 21107.288354622422, 'tolerance': 40000.0}
ludlow    {'verdict': 'Deny',  'risk_bought': 21107.288354622422, 'tolerance': 5000.0}
tuppence  {'verdict': 'Deny',  'risk_bought': 21107.288354622422, 'tolerance': 15000.0}
```

Same control, same scenario, **byte-identical** risk_bought; the enforcement action flips purely
on each organisation's own signed appetite band. `verify/proportionality/verify-proportionality.sh`
asserts the identity first (`risk_bought differs across orgs — not the same control`) and then
that the committed policies match the £-derived render (`render.py --check`). Nothing in the
2022 material proposed a mechanism for deciding which side of that line a control falls on.

### 5. One signed artefact carrying four independent organisations' priced output, in one currency, under one declared perspective — with a summing helper that refuses to cross either

`units/driftwood/composed/evidence.json`:

```
ico      feed     GBP  1,787,177.08  perspective=driftwood  name=penalty-schema
feeds    feed     GBP     19,558.55  perspective=driftwood  name=threat-register
insurer  premium  GBP    113,403.30  perspective=driftwood  name=quote-driftwood
twin     twin     GBP  1,897,646.11  perspective=driftwood  name=forward-intel
```

Each line carries `per_customer`, an `lef_basis` naming its own editorial content, and (for ico)
a four-way `holes[]` breakdown by real NIST control id summing to the total.

The seam is enforced in code, not by discipline: `units/platform/fair/fair.py:67-95`
(`sum_prices`) raises `refusing to sum across perspectives/currencies` and raises again on any
unlabelled amount. I reproduced the feeds line exactly and showed it deterministic:

```
python3 units/platform/fair/fair.py summary .../driftwood-cart-pii.json   (twice)
DETERMINISTIC: identical across two runs
"ale": 19558.549772440045          ← equals evidence.json's feeds amount exactly
```

Run 21's `verify_pound-seam` PASSes 27 assertions, including that two independent tier-selection
engines (platform's `graded/cage.py` and driftwood's own published selection-policy package)
agree in all 60 constructed cases at every band boundary, and that a date the FX feed does not
publish *refuses as a missing instrument and prices nothing*.

### 6. The dependency loop closed for real once — machine-raised, human-merged — and it is graded from the PR record, with the pin load-bearing inside the check

`gh pr view 20 --repo policy-as-versioned-driftwood/driftwood`:

```
#20 MERGED "Update dependency feeds/threat-register to v2"
head=renovate/feeds-threat-register-2.x
commit ea1c8db5 author=github-actions[bot]
files: composed/HEADER.yaml, composed/evidence.json, party.yaml
merged_by=chrisns at 2026-09-01T08:57:50Z
```

A bot opened it, a human merged it, and the declaration and the composed artefact moved in one
commit. Run 21 grades it from that record, not a simulation
(`verify_renovate_verify-renovate-merged-feed-pr.out` → PASS).

The part I found most convincing is what the PR's *checks* did. All three
(`compose-check`, `shift-left`, `propose-tier`) went green, and the compose-check log shows it
reading driftwood's PR-head pin and then:

```
git checkout --progress --force refs/tags/v2.0.1   (platform)
git checkout --progress --force refs/tags/v1.1.0   (nist)
```

The pin is not decoration on a Renovate PR: the check tests the version being proposed, at the
signed tag, in another organisation. `driftwood/.github/workflows/shift-left.yml:26-36` records
that this was a *fixed defect* — the job used to check out platform's default branch, so a bump
PR never tested what it proposed.

### 7. Live cross-organisation distribution fidelity, observed on a fresh ephemeral cluster, on the adopter's own cron, with the falsifiers pre-registered

`gh run view 33624104359 --repo …/driftwood` → `name=drift-sample, event=schedule,
conclusion=success, createdAt=2026-09-02T11:20:42Z`. A real cron firing today.

`drift-sample.yml` brings up `kind create cluster` with a fresh name, installs kind 0.32.0,
flux 2.9.3, kyverno 1.18.2 and flux-operator 0.58.1 each pinned by **version and SHA256**, and
reconciles from the real github.com remotes — with the reason written down: *"A `curl | bash`
installer would put an unreviewed script inside the identity that signs this repository's
observation commits."* The newest three lines of `drift/samples.jsonl` (cluster
`dsample-33624104359`) record, for driftwood-composed, nist and platform:

- fact 1 Ready at the pinned tag **and** commit, url = the publisher's real remote;
- fact 3 last-applied revision equals the pinned commit;
- fact 4 all 16 rendered objects live and equal to an offline render taken *at the pinned ref*;
- fact 5 all 16 objects present in a Flux inventory — the fact that separates "Flux put it
  there" from "someone ran kubectl apply".

For nist and platform, fact 2 (in-cluster gitsign verification at the source boundary) is also
true, against each publisher's own anchored identity regexp. The facts, three falsifiers and a
0.9 coverage floor were declared in `drift/window.yaml` on 2026-08-28, before sample one, and
`drift/five-facts.py` refuses to grade a sample whose run id is not a real Actions run or whose
appending commit is not signed by the lane's own identity — closing a documented incident where
three hand-typed lines graded PASS.

What is in force there is a genuine cage, not a label. `composed/policies/v4.0.0/cage-tier.yaml`
takes the tier from `namespaceObject` and **clobbers** the pod's own label; the fallback is
fail-closed to `isolated`; hardening booleans are ORed with what the container declared; cpu and
memory ceilings are a minimum via `quantity().isLessThan()`; `hostNetwork/hostPID/hostIPC` are
written false at every rung; and a WAF sidecar is injected at the tighter rungs. Tighten-only, in
CEL, in the copy each adopter actually composes.

### 8. A falsifiability instrument whose headline result is its own worst score — and it still exits 0

I ran it myself, offline, into a scratch directory:

```
bash twin/beat-royal-mail.sh <tmp>        EXIT=0
  market-consensus-2013  p=0.05  brier=0.9025  log-loss=2.9957  [as-consumed]  adjusted brier 0.8641
  contamination discount: -0.0384 on brier (enron-vs-obscure -0.0384)
  the headline: market-consensus-2013 said 0.05, it happened, brier 0.9025 — worse than a coin
  flip, and step 3 printed it above the rest
```

The rewind is real, not a filter: the fixture's dated git history runs 2013-08-01 → 2019-05-23,
the run is cut at T=2018-06-01, and both the profit warning (2018-10-01) and the answer key
(2019-05-23, citing Royal Mail's real £1.8bn investment concession) are *absent by construction*.
The fixture repos are deterministic — "same content, same commit sha, on every machine". The
contamination discount is measured from two other subjects (Enron as the notoriety control,
Carillion as the low-notoriety leg), never hardcoded. The forecast bundle reproduces
byte-identically from its own pins (`forecast-bundle a03e55a0e10a54e1 (recorded a03e55a0e10a54e1)`,
`tolerance: none — byte identity`).

And the machine says out loud what it cannot do, in its own output: *"A forecast here reads a
world model's declared belief and nothing infers it from a signal, so the three probabilities are
identical by construction and a computed residual of zero would read as 'the model is fine' rather
than as 'nothing consumes a signal'."*

The same discipline holds in CI: `gh run view 33615039125` (twin.yml, event=schedule, today)
shows `70 passed, 1 failed, 3 skipped` invariants and `1 failed, 1550 passed`, with the one
failure being a pre-registered guard whose own message says *"This guard staying red is the
finding, not a defect in it"* — while `determinism (x86_64-linux)`, `(aarch64-linux)`,
`(arm64-darwin)` and `reproduce-elsewhere` all pass in the same run.

### 9. Three policy lines were retired because the estate's own engine refused to let them be patched — after a live-observed escape

`units/platform/distribution/versions.yaml:29-59` is the best single page in the estate. 2.0.0,
2.0.1, 3.0.0 and two backports were retired on 2026-08-29 for two independently *observed*
reasons:

1. Not deployable — every 2.x/3.x cage-tier wrote `priorityClassName` without the `priority` and
   `preemptionPolicy` the Priority admission plugin re-derives, so the plugin refused the pod.
2. Not safe, and unfixable as a patch — every pre-ADR-0022 body read the tier from the **pod's
   own label**. Observed live on kind-driftwood: in a Namespace declaring
   `posture.acme.io/tier=isolated`, a pod claiming 2.0.2 and forging `tier=baseline` was admitted
   as baseline with `hostNetwork=true` and **reached the API server**; the identical pod claiming
   4.0.0 was clobbered to isolated, hostNetwork=false, and reached nothing.

Teaching an old body to read `namespaceObject` *is* ADR-0022, which the engine classifies major —
"so it cannot be a patch on those lines, and ADR-0011 refuses a declaration weaker than the
computed one. The honest repair is retirement, not a number." The released trees stay on disk
behind their signed tags, unedited. This is the estate's own computed-semver machinery over-ruling
its author's convenience, and the record saying so.

Related and verified: **there is no exemption mechanism anywhere.** A case-insensitive grep for
`PolicyException|exemption` across all eight unit clones (excluding .git, `__pycache__`, and
markdown) returns 23 hits, and every one is a negation, a fail-closed default, or a reference to
the deleted `render-exemption.py` — e.g. `composition.py:36` *"not an exemption: it is a DECLARED
INABILITY, priced"*, `render-governed-namespace-guard.py:87` *"Silence is not an exemption"*,
`identity/component-definition.json:59` *"A pod with no tier is named `isolated`, the strictest
running cage: silence is not an exemption."*

### 10. One command, on a clock, in CI, writing one dated, signed, committed number — that records itself when it is red

Run 21 is GitHub Actions run `33616685427`, `event=schedule`, `conclusion=failure`. Its steps:

```
7  the gate                                                        success
8  record the TRUTH line                                           success
9  the observation cage -- a clock appends observations, never a declaration   success
10 fail if the gate failed                                         failure
```

The number was written and pushed **before** the run went red, and the red is the honest signal.
I verified the commit's signature:

```
git -c gpg.format=x509 -c gpg.x509.program=gitsign log -1 --show-signature a209496
tlog index: 2685003932
Good signature from […/policy-as-versioned-flux/.github/workflows/truth.yml@refs/heads/main]
Validated Rekor entry: true
```

The instrument is honest about itself in four ways I checked:

- **Discovery, not a list.** `talk/verify-all.sh:45` globs 84 `verify*.sh`; I counted 84 on disk.
  A script neither run nor listed with a reason is itself a FAIL, and a listed exclusion that no
  longer exists is a FAIL too, so the list cannot rot.
- **A cage that bites.** `truth.yml:108-162` does `git reset -q` **first** (fixing a reproduced
  2026-08-28 defect where staged-and-clean entries rode along), stages only `OBSERVATION_LANE`,
  then asserts the *staged set* against the same list rather than a second regex, then asserts the
  tree clean outside the lane.
- **Reporting graded separately from results.** Run 21's step-7 capture shows
  `PASS: steps 1-6 each report one honest verdict (verdicts: PASS PASS PASS FAIL PASS PASS PASS)`.
  A red step 4 and a green step 7 in one tally is correct, and its script says why in its header.
  I ran its selfcheck: `bash verify/e2e/verify-e2e-step7-honesty.sh selfcheck` →
  *"a hedged PASS, an exit/last-line mismatch, a non-conforming step and a green whose own
  transcript confesses mid-run are each caught; an honest SKIP and an honest FAIL are not."*
- **It refuses to fake a subject it no longer has, at its own cost.**
  `distribution/verify-coexistence.sh:35-45` declines to loop a one-element array —
  *"looping a one-element array to claim coexistence would be the false pass this project forbids.
  Do not invent a second version to keep the beat alive"* — and SKIPs with a stated reason.
  `verify-shift-left.sh` does the same for the ±1 window. The insurer's own quote check SKIPs
  because *"the insured re-signed its exposure and a re-quote PR is due."* And when ticket 60
  reordered three checks to grade the real lane sample *before* looking for a cluster, the
  published number got **worse** — run 19→20, `skip 22→18, fail 3→7` in `talk/truth.log` — because
  four could-not-looks became honest observed-falses. A project that made its own headline metric
  worse in order to be true has earned the metric.

Even the deck obeys it: `talk/deck.md`'s header says it was built at a superseded commit and
therefore *"records no run of the truth surface at this commit, so this deck quotes no headline
number"*, and `verify-demo.sh` FAILs run 21 for exactly that staleness rather than shipping a
green lie.

---

## Which purposes these ten already serve, and the honest claim for each

### (a) A conference talk — **serves it well today, with one rebuild**

The seven-beat, generated-not-authored deck is the estate's best single idea: `build_deck.py`
writes every slide from one capture per check, and `verify-demo.sh` refuses the deck if a figure
is not in the capture behind it, if a beat status disagrees with the run, or if a TRUTH line is
quoted from another commit. It caught its own staleness on run 21. Beats 1, 2, 6 and 7 are green
on the citable run; 3 is green on a labelled synthetic; 4 has a fully-diagnosed red; 5 is green.
Nine of the ten items above are demonstrable live, from a laptop, in seconds — the gitsign
verification loop, `enforce.py decide` across three orgs, `fair.py summary`, `gate.py --selfcheck`,
the Royal Mail beat.

> **Honest claim:** *"Here is a nine-organisation eco-system where policy is a signed, semver,
> pinned dependency; where the release number is computed from measured verdict movement rather
> than declared; where the same control resolves to Audit in one firm and Deny in another purely
> from each firm's own signed appetite; and where one command, on a clock, publishes a signed
> number that today reads 57 pass, 7 fail, 18 could-not-look. I will show you the reds and tell
> you which are the estate's fault and which are the instrument's."*

### (b) A reference architecture — **serves it now, for the publish/consume half**

The artefact contracts are the reusable part and they are small and closed: a 7-field feed
envelope with `additionalProperties: false` and a written argument for why there is no in-band
signature field; a party schema all eight parties validate against; an inheritance header with
`{party, kind, version, sha}` per parent; per-object `inherited-from` / `source-path` provenance;
a ResourceSet whose single `versions[]` array is simultaneously the install list, the prune list
and the orphan-guard allow-list. All eight unit repos are Apache-2.0. A regulator or intelligence
publisher can adopt the contract in an afternoon — `bash units/ico/verify-penalty-feed.sh` passes
offline on a stock laptop in seconds, including a real `git ls-remote` against nist.

> **Honest claim:** *"This is a worked reference for treating policy as a versioned dependency
> across organisational boundaries: the envelope, the pin shape, the composition header, the
> release gate, and the identity regexp are all here, Apache-2.0, exercised against real remotes.
> It is not yet a product an unfamiliar platform team can operate unaided — there is no onboarding
> path and no measured time-to-first-cage."*

### (c) A research artefact — **serves it strongly, and this is its best fit**

Determinism is proven across three architectures in the same CI run where other jobs fail; every
stochastic path is explicitly seeded; a fixture corpus produces the same commit sha on every
machine; the twin's forecast bundle reproduces byte-identically from its own pins; 1,550 tests
and 73 computed capability grades that refuse a hand-typed value. The falsification tests are
pre-registered before first observation and name their own falsifiers. Negative results survive
to the surface — a Brier of 0.9025 is the headline, not a footnote. And the record documents its
own limits against interest: `not_looked_at: []` beside a `limits[]` array, a coverage figure
expressed as cells and pairs and *never* a percentage, `anchored: false` on the GPD parameters
that feed the largest number on the balance sheet.

> **Honest claim:** *"An artefact built to be checked rather than believed: pre-registered
> falsifiers, seeded determinism verified on three architectures, byte-identical reproduction from
> declared pins, scored forecasts under proper scoring rules where the worst score is the headline,
> and an instrument that made its own published number worse in order to stop reporting a
> could-not-look as a pass."*

### (d) A consultancy asset — **serves it as an argument and a capability demonstration, not yet as a liftable package**

What a client conversation can use today: a live, verifiable cross-org signature spine; a
compose-check that tests a Renovate bump at the signed tag in another organisation before a human
merges it; a release gate that computes the number and refuses the author's declaration; a cage
that tightens and never widens, with the escape it was built to close recorded as an observed
incident; and a £ engine that makes a control, a cage tier and an insurance transfer comparable in
one currency under one perspective. The one blocker to *lifting* it is administrative, not
architectural: the hub carries no licence (`gh api …/license` → 404) while all eight units are
Apache-2.0.

> **Honest claim:** *"This is what a governance eco-system looks like when every participant is a
> separate organisation signing its own artefacts and consuming everyone else's by pinned tag and
> commit. It demonstrates capability and taste. It is a private demonstration and a set of
> reusable contracts, not a productised platform — and the hub needs a licence before any of it
> travels."*

### (e) A thesis defence — **serves the mechanism half convincingly and the doctrinal half partly, and knows which is which**

The mechanism the 2022 posts describe is built and machine-checked: semver, signed tags, pinned
consumption, Renovate bumps, reviewed merges, Flux distribution, coexistence-by-matchCondition,
maintenance-branch patching. On two points the build *goes past* the original — semver is computed
from measured verdict movement and a weaker declaration cannot be published clean; and "exemptions
dissolve into conditional policy" is not a slogan but a verified absence, with zero exemption
mechanisms in 28,490 lines of unit Python and 11,246 of shell. The mea culpa's locked-door
distinction is turned into arithmetic that I re-derived. And the honest weak point is honestly
recorded: with one declared version, the coexistence, retirement and shift-left beats SKIP rather
than fake a subject, which is itself the thesis's own standard being kept under pressure.

> **Honest claim:** *"The mechanism half of the thesis is built, signed and machine-checked on a
> clock — and in two respects it is stronger than what I wrote in 2022, because the version number
> is now computed from measured behaviour rather than declared, and the lane-keeping/locked-door
> split is a computation over each firm's own signed appetite rather than a judgement call. The
> doctrinal half is where I owe the most: the estate runs one policy line today, so three
> coexisting versions with a retirement window is unproven at runtime, and my own checks say so by
> refusing to pass rather than by inventing a second version."*

---

## What I could not look at

- `verify-graded.sh`'s live cage proof (the `nc` reach test from an isolated pod, the refused
  orphan pod) requires a persistent kind cluster named `driftwood`. I read the code
  (`units/platform/graded/verify-graded.sh:470-535`) and it is a real TCP connection test with a
  polled 60-second window and a written reason for the poll, but I did not run it — creating a
  cluster is out of scope for this review.
- Run 21's step-4 red: driftwood's fact 2 is observed false with
  `certificate is not yet valid` at tagger time 1787677714. I confirmed separately that
  `driftwood v1.1.0` verifies *cleanly* under gitsign with `Validated Rekor entry: true` on this
  machine. Both facts are mine; I did not attempt to adjudicate which side is at fault.
- I did not re-derive the ico £1,787,177.08 line from first principles; I verified its four
  `holes[]` sum to it and that all four control ids resolve in nist's catalogue, which I did
  re-derive (sha256 `d820835a…` recomputed, 20 groups, 1,196 controls, verbatim NIST SP 800-53
  rev 5.2.0 OSCAL).
