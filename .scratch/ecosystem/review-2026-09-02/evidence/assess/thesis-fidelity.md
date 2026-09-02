# Assessment — FIDELITY TO THE THESIS

Auditor pass, 2026-09-02. Citable base: `TRUTH 2026-09-02T10:11Z run=21 hub=7b92990 ... pass=57
fail=7 skip=18 excluded=2 total=84`. Every capture quoted below is read from the hub's
`origin/main:talk/captures/<file>` (run 21) unless a different run is named. Unit files are read
from the fresh default-branch clones under `scratchpad/units/`, which match run 21's SHAs.

The standard applied is the owner's own published thesis and its mea culpa
(`research/03-blogs-thesis.md`), read as `docs/PRD.md:31` instructs — the **refined** thesis
"over the original talk" — and cross-read against `NORTH-STAR.md` where the north star
deliberately departs from it.

---

## 0. Method and what I did not check

- I re-derived every claim below from a primary source. Where I rely on a reader's map I say so
  and name the map.
- I did **not** stand up a cluster, run any live script, or write anything outside
  `scratchpad/review/`.
- I did **not** read the whole of `twin/` (34,678 lines of Python); the dilution census in §7 is
  a line count plus a directory-level classification, and I state the classification rule so it
  can be re-derived or disputed.
- I did **not** independently re-verify the 24 gitsign tags; I rely on the `publishers` and
  `github-live` maps, which both report every tag verifying against Rekor, and on my own
  observation that all nine repos are public.
- `git tag -v` cannot verify these tags in this sandbox (gitsign/Sigstore keyless, no ambient
  x509 program configured), so no signature claim below is my own cryptographic observation.

---

## 1. The core claim: policy as a versioned dependency

### 1.1 What is genuinely built and proven on a citable run

The dependency graph is real, declared, pinned by `{tag, commit}`, and **machine-checked against
the real remotes on the citable run**. `talk/captures/verify_feed-contract_verify-feed-contract.out`
(run 21) ends:

```
PASS: driftwood pins platform/implementations@2.0.1: tag v2.0.1 on platform
PASS: driftwood pins nist/controls@1.1.0: tag v1.1.0 on nist
PASS: driftwood pins ico/feed/penalty-schema@v3: tag v3.0.0 on ico
PASS: driftwood pins feeds/feed/threat-register@v2: tag threat-register/v2.0.0 on feeds
PASS: driftwood pins insurer/feed/quote-driftwood@v1: tag v1.0.0 on insurer
...
PASS: every published feed is one envelope, and every subscription names a tag that exists on the
      publisher's real remote (existence, not signature -- step 6 checks the signature)
```

Twenty-four pin assertions across eight repositories, all green. `driftwood/composed/HEADER.yaml`
records each parent by `{party, kind, version, sha}`. This is the thesis's central mechanism,
built, and it is stronger than the 2022 original (which pinned one policy repo, not a five-parent
inheritance graph).

**The estate also exceeds the thesis on semver.** The 2022 post asks publishers to *declare*
major/minor/patch. `platform/computed-semver/` (7,524 lines of .py/.sh, the single largest module
in the platform) *computes* the bump from measured verdict movement over a generated corpus and
**refuses a declaration weaker than the computed one**. `verify-gate` PASSes on run 21; its
capture names, among other cases, "a declared bump weaker than computed publishes DEGRADED …
naming the moved corpus entries and the CEL expression … the declared number is never rewritten."
`platform/distribution/versions.yaml:79` carries `bump: "major"` as a reviewed field on the array
element, and `cut-release-gate.py` refuses if the tag's arithmetic disagrees. Nothing in the
thesis asked for this; it closes a hole the thesis left open.

### 1.2 The dependency loop is not wired for policy versions themselves

`driftwood/renovate.json` declares four `customManagers`. Their `depNameTemplate`s are:

```
https://github.com/policy-as-versioned-nist/nist        (gitops/flux-system/gotk-sync-nist.yaml)
https://github.com/policy-as-versioned-platform/platform (gitops/platform/platform-pin.yaml)
feeds/{{feedName}}                                       (party.yaml)
insurer/{{feedName}}                                     (party.yaml)
```

None watches `policy/v*` — the tag namespace the policy *line* is released under
(`platform` carries `policy/v2.0.0 … policy/v4.0.0` alongside its package tags `v0.1.0 … v2.0.1`).
So **a new policy version cannot raise a Renovate PR at any adopter**. It arrives only as a
side-effect of a platform *package* tag bump, which fans the whole `versions.yaml` array in. This
is the same observation ecosystem ticket 18 recorded in its Notes ("Adopters' Renovate never sees
`policy/v*` tags"); it is still true today and no ticket owns fixing it.

The one merged machine-raised bump is a **feed**, not a policy version. `verify-renovate-merged-feed-pr`
PASSes on run 21:

> `PASS: driftwood #20: Renovate raised threat-register v1 -> v2, Chris Nesbitt-Smith merged it,
> and party.yaml and composed/ moved together -- step 2 happened for real`

I confirmed #20 independently: `gh pr view 20 --repo policy-as-versioned-driftwood/driftwood`
returns `mergedAt: 2026-09-01T08:57:50Z`, `author: chrisns`, `mergedBy: chrisns` (the PR was
opened by hand because Renovate's create call errored; the branch commits are the bot's — ticket
61's Answer says so). Filtering all closed PRs in the three adopters by a Renovate author returns
**zero merged**; every bot-authored PR is `CLOSED merged=null`.

So: the thesis's headline loop — *a new policy version becomes an automated dependency PR that a
human reviews and merges* — **has happened exactly once, for a threat feed, and never once for a
policy version.**

### 1.3 ≥3 coexisting versions: at one, and the plan tops out at two

The thesis calls this non-negotiable: "The runtime must support multiple policy versions
simultaneously — at least three semver versions — to allow *transitionary periods for old policy
versions to be retired*" (`research/03-blogs-thesis.md:40-41`). `CONTEXT.md:153-155` restates it
as the estate's own definition, "(≥3) … *The crux of the original implementation.*"

`platform/distribution/versions.yaml` declares **one** element today: `{ version: "4.0.0", tag:
"policy/v4.0.0", commit: 64635df…, bump: "major" }` (line 79). Three versions were retired on
2026-08-29 for two independently observed reasons recorded in the file itself (a Priority
admission-plugin triple mismatch making them undeployable; a forgeable pod-label tier observed
live reaching the API server from an `isolated` namespace).

The consequences are visible on run 21, and the estate reports them honestly rather than faking a
subject:

| script | run-21 verdict (capture tail) |
|---|---|
| `distribution/verify-coexistence.sh` | `SKIP … distribution/versions.yaml declares one version (4.0.0); coexistence needs two declared versions to show side by side, and retirement left one` |
| `distribution/verify-retirement.sh` | `SKIP: distribution/versions.yaml declares one version (4.0.0), so a retirement would leave an empty allow-list` |
| `shift-left/verify-shift-left.sh` | `SKIP: … declares one major line (4.0.0), so a target has no ±1 neighbour … the flip beat has nothing to observe until a second major is declared again` |

Three of the thesis's own demonstrations are dark from one root cause.

Two further facts a skeptic should have:

1. **The gate's own bar is two, not three.** `distribution/verify-coexistence.sh:35` reads
   `if [ "$n_versions" -lt 2 ]; then … live_tail_skip`. A green coexistence beat would therefore
   prove a weaker claim than `CONTEXT.md:153-155` states and than the thesis requires.
2. **The owned remedy also stops at two.** `REVIEW-2026-08-31.md` M11 raised this; it graduated to
   ticket 58 Q1, whose recorded (PROVISIONAL) answer is "(a) the ticket-63 isolated flip is the
   next computed major and becomes the second line", and ticket 63's own text says "coordinate
   with ticket 58's second-declared-version decision, since this cut can be the coexistence
   subject". No ticket in the 74 targets three.
3. The 2022 reference implementation is also at two today: `fleet/clusters/cluster1/policy-versions.yaml`
   (read via `gh api`) declares `2.0.0` and `2.2.0` only. `docs/HISTORY.md:59` records "three policy
   versions live simultaneously on one cluster" for the faithful-floor epic; that claim predates the
   truth surface (which starts 2026-08-28) and appears on no TRUTH line.

### 1.4 The retirement window has no mechanism, and the DECIDED replacement is unbuilt

The thesis's reason for ≥3 is the *transition window*. ADR-0010 (`status: accepted`, no superseded
banner) defines a consumer-side `sunset:` date and a machine-opened retirement PR on that date.
`CONTEXT.md:404-406` retires that: "**Supersede** … A pin behind a newer published version is
priced by the EOL ramp from the newer version's publish date. **No consumer-side sunset field
exists.**" Ticket 13 item 5 is one of only five items in the whole tracker recorded **DECIDED**
(not provisional), and it says the same, adding "The adopter's scheduled proposer reads pins
against the feed and opens a retirement PR".

Neither half exists:

- `grep -rn sunset` across all eight unit repos returns two hits, both prose comments
  (`platform/feeds/to_fair_scenario.py:17`, `platform/feeds/README.md:70`). No field, no code.
- The EOL ramp exists (`platform/feeds/to_fair_scenario.py:74 eol_ramp`) but its feed's
  `components` are `python-3.9`, `ubuntu-20.04`, `istio-1.18`, `kyverno-1.10`
  (`platform/feeds/eol/v2/eol-feed.json`) — **no policy version is an entry**, and
  `compose/composition.py:1952-1967` (`compute_prices`) iterates only edges whose `kind` is in
  `FEED_KINDS`. A stale policy pin is priced at nothing. `driftwood/composed/evidence.json`
  `prices[]` has four entries (ico, feeds, insurer, twin); none is a policy-version staleness line.
- No retirement proposal is ever constructed. The only proposal kind the proposer builds is
  `cage-tier` (`platform/wargamer/tier_pr.py:3,288-291`). `rejection_ledger.py:16-17,82-84` merely
  reserves a *key namespace* for a retirement proposal ("a cage-tier proposal and a retirement
  proposal about the same slug are different questions"); nothing produces one.

So the 2026-08-29 retirement — the only retirement the eco-system has ever performed — was a **flag
day**: three versions deleted from the array in one edit, with no window, no advance signal, and no
price on being behind. That is precisely the failure mode `CONTEXT.md:153-155` says coexistence
exists to avoid. It was the *right* engineering decision (the versions were unsafe and unpatchable),
and the file records why at length — but it means the thesis's transition mechanism has never been
exercised and currently has no implementation.

---

## 2. The seven "-ables", per audience

The PRD turns these into acceptance criteria with named mechanisms (`docs/PRD.md:103-115`). I grade
each against that table, and name for whom it holds.

| "-able" | Adopter engineer | CIO | Regulator | Verdict |
|---|---|---|---|---|
| **visible** | yes | yes | partly | Holds mechanically. All nine repos are public (`gh api repos/…/… .private == false` for all). The artefact a non-engineer would read is `composed/evidence.json` — 250+ machine-keyed `holes` records; see §5. |
| **communicable** | partly | no | no | See §2.1. |
| **consumable** | yes | n/a | n/a | `party.yaml`'s five-line `inherits[]` + one `platform-pin.yaml` is the whole consumption surface; `composed/` is rendered from it. |
| **testable** | yes | n/a | n/a | Real `kyverno test` fixtures in four dirs (`platform/{posture,distribution,graded,policy}/tests`); `verify-composition` PASSes run 21 ("every rendered policy version is present at the pinned parent commit"). |
| **usable** | yes, with a hole | n/a | n/a | `driftwood/.github/workflows/shift-left.yml` checks out platform *at the tag under review*, verifies the commit against the pin, runs the pinned `kyverno` CLI via `platform/shift-left/ci-check.py --resource driftwood/deploy/pod.yaml`, recomposes, and signs a keyless cosign attestation posted to the PR. Exercised green on driftwood #16/#18/#19/#20. The hole: the ±1 flip beat itself SKIPs (one major line). |
| **updatable** | once, for a feed | n/a | n/a | §1.2. |
| **measurable** | yes | different question | partly | §2.2. |

### 2.1 Communicable is half-built

- **Release notes.** Twenty-four tags across the eight units; **ten** GitHub Releases
  (`gh api repos/…/tags` vs `gh release list`, per repo: platform 11/2, nist 2/1, ico 2/1,
  driftwood 2/1, tuppence 2/1, ludlow 2/1, feeds 2/2, insurer 1/1). Platform's newest Release is
  `v0.1.1` (2026-08-21) while its newest tags are `v2.0.1` and `policy/v4.0.0`. So fourteen signed
  releases carry no release page. Mitigating, and real: the annotated tag messages *are* substantive
  release notes — `git tag -l -n20 policy/v4.0.0` returns a full paragraph naming every behavioural
  change in the cage release. A consumer with git has the notes; a CIO with a browser does not.
- **Broadcast.** The PRD's named mechanism is "notification-controller broadcasts version changes;
  Alert fires on new tag". `grep -rln "kind: Alert|kind: Provider|notification.toolkit"` across all
  eight units returns **nothing**. The notification spine is open ticket 35 (a ticket-13 round-2
  item, still unplaced per the `legacy-org` map).

### 2.2 Measurable answers a better question than the thesis's, and a different one

The thesis's metric is adoption-by-PR-acceptance: "When the CIO wants to know how many teams are
compliant, the answer is a GitHub PR search away" (`research/03:161-163`). The PRD replaced it with
"layered ground-truth: Flux revision + PolicyReports + OSCAL via C2P; PR-state = adoption velocity",
and a dashboard answering four CIO questions (`docs/PRD.md:115`). The dashboard was then **retired**
by the owner (NORTH-STAR §5 and `legacy-org` map: "Grafana/CIO dashboards -> RETIRED (owner rejected
2026-07-20 … truth surface only)").

What actually exists is better than a PR search on one axis and worse on another:

- **Better:** `verify-feed-contract` is a real, citable, estate-wide "who is on which version"
  matrix checked against the real remotes (§1.1). It shows driftwood on `threat-register v2` while
  tuppence and ludlow are on `v1` — genuine, visible staleness. A PR search cannot do this.
- **Worse:** it grades *tag existence*, not *distance behind*. Nothing computes or prices "ludlow is
  a major behind" (§1.4). And the TRUTH line itself measures whether the estate's own claims are
  true, not how much of an estate has adopted a policy — those are different questions, and the
  TRUTH number is the only thing any document is allowed to cite (NORTH-STAR §5).
- The PR search still literally works: `gh api search/issues -f q='org:… is:pr is:merged'` returns
  24 merged PRs across the three adopters. Under the thesis's own metric, adoption of a
  machine-raised bump stands at 1 of 3 adopters, once.

---

## 3. The mea culpa's split: lane-keeping vs the locked door

### 3.1 The strongest single piece of thesis fidelity in the estate

`verify/proportionality/verify-proportionality.sh` PASSes on run 21:

```
ok  driftwood(£40000 tol, from its OWN party.yaml): loose buys £19439 -> Audit | tightened buys
    £54520 -> Deny | same loose under ludlow(£5000 tol) -> Deny | a party with no declared appetite
    refuses as a missing instrument
    risk_bought £21,107  |  driftwood band £40,000 -> Audit  |  ludlow band £5,000 -> Deny
ok  committed policies match the £-derived render for driftwood, ludlow
PASS: same control, same £ (risk_bought £21107) — Audit in driftwood, Deny in ludlow.
      Proportionality by comparison.
```

The script's own header calls it "THE MONEY SHOT", and it earns the name: the *same* control body,
the *same* FAIR scenario, the *same* £, and the Audit/Deny divergence falls out of each party's own
signed appetite band. The script asserts `risk_bought` is byte-identical across the two orgs before
comparing, and diffs the two rendered policies to prove they differ in ≤6 lines. This is the mea
culpa's "lane-keeping where appropriate, a locked door where not" turned into a computation instead
of an opinion. Nothing in the 2022 thesis or the mea culpa proposed a mechanism for *deciding*
which side of the line a control falls on; the estate built one.

### 3.2 …and it is the one control that is not a versioned dependency

`encrypt-at-rest` — the control that carries the whole demonstration — exists **only** in the hub's
verification harness:

```
verify/proportionality/control/encrypt-at-rest.tmpl.yaml
verify/proportionality/policies/encrypt-at-rest-{driftwood,ludlow}.yaml
verify/proportionality/scenarios/encrypt-at-rest.json
verify/proportionality/tests/encrypt-at-rest/{kyverno-test.yaml,resources.yaml}
```

`grep -rn "encrypt-at-rest"` across all eight unit repos returns **zero hits**. It is in no party's
`publishes[]`, in no `composed/` tree, under no signed tag, not fanned out by Flux, and pinned by
nobody. Its two rendered policies are committed fixtures in the hub, regenerated by
`verify/proportionality/render.py --check`.

The consequence for this dimension is precise: **the catastrophic-minority half of the mea culpa's
split is demonstrated by a bench rig, not by the mechanism the thesis is about.** The lane-keeping
half (`require-nonroot`, Audit) *is* a real versioned dependency; the locked-door half is not.

### 3.3 No policy in the estate governs the three things the mea culpa names

The mea culpa names the gate's scope three times: "Access control. Data protection. Cryptographic
key management." The complete shipped policy line (`platform/distribution/policies/v4.0.0/`) is:

| object | kind | action | what it governs |
|---|---|---|---|
| `require-nonroot-4-0-0` | ValidatingPolicy | **Audit** | `runAsNonRoot` + `readOnlyRootFilesystem` |
| `posture-trust-boundary-4-0-0` | ValidatingPolicy | **Deny** | that `posture.acme.io/version` equals the claimed policy-version (anti-forgery on the label) |
| `cage-tier-4-0-0` | MutatingPolicy | — | writes the tier + priority triple onto the pod |
| `cage-netpol-4-0-0` | GeneratingPolicy | — | renders per-tier NetworkPolicies; `isolated` gets `ingress: []`, `egress: []` |
| `stamp-posture-4-0-0` | MutatingPolicy | — | stamps posture from the validated version |
| `policy-version-orphan-guard` | ValidatingPolicy | **Deny** | version not in the declared array |
| `governed-namespace-requires-claim` | ValidatingPolicy | **Deny** | a pod in a governed namespace carries no version claim |

Every `Deny` in the estate is a **meta-rule about the policy-version claim or the posture label**.
`grep -rln "encrypt\|Encrypt"` across the eight units returns two files, both twin world-model
propositions. There is no data-classification rule, no key-management rule, no access-control
admission rule anywhere in the 55 policy objects the units ship. The identity/access substrate
(`platform/identity/`, `platform/access/`, `platform/break-glass/`, 3,284 lines) governs *human and
workload reach*, which is adjacent, but it is not a versioned admission policy distributed as a
dependency, and `identity/README.md` states federation is not live.

### 3.4 Is `isolated` an honest equivalent of the locked door, or a redefinition?

NORTH-STAR principle 2 says "There is no gate", and immediately flags its own provenance: "That a
refusal is therefore the bottom rung reached by the £, rather than a separate mechanism, is my
reading, not your words."

**On the merits, the mechanism is a defensible equivalent and in one respect stronger.**
`cage-netpol-4-0-0`'s `reach` variable gives the `isolated` rung `{'ingress': [], 'egress': []}` —
a NetworkPolicy that permits nothing in either direction. A pod that would open an unencrypted
connection to a personal-data database cannot reach the database. That satisfies the *purpose* of
the mea culpa's locked door (the harmful act does not happen) while keeping the workload observable
and priced rather than invisible behind a rejected `kubectl apply`. It is a genuine contribution.

**Three things stop me grading it proven.**

1. **It has never been observed on the citable surface.** `verify-graded`'s capture is
   byte-identical from commit `f3b87c7` (2026-08-31 20:41) through run 21 and reads:
   `SKIP: offline proof holds; live tail could not look: kind cluster 'driftwood' is not listed by
   kind get clusters — the Namespace declares the tier and the pod wears it; the cage only tightens;
   the bottom rung runs and reaches nothing; TCoR booked.` The claim after the em-dash is exactly
   the equivalence claim, and it is on the SKIP line every run.
2. **It can never be observed by the hub gate as currently built.** `.github/workflows/truth.yml`
   runs on `ubuntu-latest` and installs gitsign, kyverno, cosign and flux CLIs; it never creates a
   KinD cluster (`grep -n "kind create" .github/workflows/truth.yml` → nothing). Every live-cluster
   tail in the estate is therefore structurally could-not-look on the citable run, permanently, by
   construction of the instrument. This is an **instrument** limit, not an estate fault — and it is
   partly compensated (see 3.5) — but it means no citable run has ever observed *any* policy denying
   or caging anything.
3. **The estate is on both sides of the doctrine in its own record.** Three `Deny` policies ship in
   every adopter's `composed/` tree (`orphan-guard.yaml:13`, `governed-namespace-guard.yaml:13`,
   `posture-trust-boundary` in `composed/policies/v4.0.0/`), ADR-0022's addendum explicitly
   reinstates one ("the one refusal the doctrine allows"), and `CONTEXT.md:234-243` denies that any
   CREATE deny remains. The `adrs-glossary-code` reader documents this contradiction in detail; I
   confirmed the code side (`platform/distribution/versions.yaml:117,155-157`). For *this*
   dimension the point is narrower: a reader cannot tell from the estate's own documents whether
   "there is no gate" is a description or an aspiration, which makes the thesis's most important
   revision illegible in the result.

### 3.5 What *is* observed live, on a clock, and imported into the number

Credit where due, because it is the estate's best answer to (2) above.
`driftwood/.github/workflows/drift-sample.yml` creates a **real ephemeral KinD cluster** on every
run (`kind create cluster --name "${name}" --wait 120s`, line 127), installs pinned-and-checksummed
kyverno, flux-operator and flux, reconciles from the **real** GitHub remotes, samples five facts,
and deletes the cluster. `drift/five-facts.py:75-79` names them: ready-at-the-pin, tag-signature-at-
the-source-boundary, last-applied-revision-equals-the-pinned-commit, rendered-objects-byte-equal-to-
an-offline-render, every-rendered-object-in-the-Flux-inventory. The hub's three `verify-reconcile.sh`
scripts grade that sample *before* looking for a local cluster (ticket 60's reorder), so live
observation genuinely reaches the citable number.

On driftwood's latest sample (run 33624104359, 2026-09-02T11:25Z, per the `adopters` map) facts
1/3/4/5 are true — 16 of 16 rendered objects present, byte-equal and in the Flux inventory — and
only fact 2 fails, on a gitsign certificate "not yet valid at tagger time" (open ticket 73). That
is a real, live, cross-org observation that a signed, pinned policy artefact is in force on a
cluster. It is exactly the thesis's distribution claim.

But note what the five facts are **not**: they are all about *distribution fidelity*. None of them
observes an admission verdict, a cage, or a denial. So the estate has live proof that the right
bytes arrive, and no citable live proof that they do anything on arrival.

---

## 4. The human governance layer

The mea culpa's second addition: "Every accepted practice carries a date. Every practice must be
regularly reviewed… it gets removed. Not archived. Not deprecated. Removed."

### 4.1 What exists, and it is real

- **Debate by PR, never by exemption.** This is the strongest structural alignment in the estate.
  `grep -rn "exemption"` across the eight units returns 20 hits and **every one is a negation or a
  reference to a deleted mechanism** — e.g. `compose/composition.py:36` ("not an exemption: it is a
  DECLARED INABILITY, priced"), `render-governed-namespace-guard.py:18` ("omitting one label was
  the exemption this project bans"), `versions.yaml:173` ("Silence is not an exemption"). The
  thesis's "informed debate through pull requests rather than exemption requests"
  (`research/03:79-88`) is enforced by construction.
- **A rejection decays.** `platform/wargamer/rejection_ledger.py` derives suppression from *closed,
  unmerged* proposal PRs with a half-life (`suppress while sum(0.5 ** (age_days / h)) >=
  reject_suppress`), keyed `<org>/<kind>/<slug>`, and refuses to count a rejection whose curve hash
  or selection-policy version has moved ("a rejection of GBP2,000 must not silence a proposal of
  GBP20,000"). Offline it returns empty **and says so**, so a clock that cannot see rejections
  neither silently suppresses nor silently re-asks. This is a genuinely thoughtful piece of human
  governance and has no equivalent in the 2022 work.
- **Propose, never dispose.** `tier_pr.py`'s `disposing_calls()` does an AST walk to forbid
  `gh pr merge`, after a real planted regression on 2026-08-29 passed an attribute-name-only check
  (`platform/wargamer/tier_pr.py:82-203`, per the `platform-engines` map, which I did not re-read in
  full). A machine may open a PR; only a human merges.

### 4.2 What is missing: the carrier itself

Three accepted, unsuperseded ADRs and the glossary all require the same artefact:

- `docs/adr/0007-agent-assisted-editorial-governance.md:25-26` — "Each policy version carries
  `created`, `lastReviewed`, rationale/`why`, and risk/ethos — as annotations + a versioned
  `rationale.md`, mappable to OSCAL."
- `docs/adr/0006-…:19` — "Review metadata (`created`, `lastReviewed`, rationale, risk) is advisory
  input for…"
- `docs/adr/0001-…:60` — "annotations + `rationale.md`), travelling with the tag."
- `CONTEXT.md:127-128` — the same list, as a defined term.

None of it exists:

```
find … -name "rationale*"                                      → 0 files
grep -rn "lastReviewed|last_reviewed"  (yaml/py/md/json, 8 units) → 0 hits
grep -rn "annotations:" platform/distribution/policies/         → 0 hits
grep -rin "purposeless"  (8 units)                              → 0 hits
```

The only annotations that reach a policy body are added at compose time and are provenance, not
rationale: `policy-as-versioned.dev/inherited-from: platform@2.0.1` and
`policy-as-versioned.dev/source-path: …` (`driftwood/composed/policies/v4.0.0/require-nonroot.yaml:10-12`).
`composed/evidence.json`'s `members[]` entries carry `family, name, kind, version, source_party,
source_sha, action` — no `why`, no date. `prices[]` has a `why` key and it is `null` on all four
driftwood entries.

Therefore: **no policy in this estate is dated, none has a review cadence, and nothing removes an
undefended one.** The three verbs of the mea culpa's governance clause — dated, reviewed,
removed-if-undefended — have no implementation. ADR-0007's agent demonstrator lives in the legacy
`governance-agent` repo, which the `legacy-org` reader confirmed (by direct grep, zero hits) is
referenced nowhere in the eco-system.

The nearest substitute is the **£**: a policy's justification is now a price rather than a prose
rationale, and a price is re-derived on a clock, which is arguably a *stronger* form of "still
defensible?" than a review date. That is a legitimate design position — but it is a substitution
nobody has written down, and ADR-0007 still stands unamended saying the other thing.

### 4.3 "Other teams review it, challenge it"

`github-live` reports zero branch-protection rules and zero rulesets on `main` in all nine repos,
and that every one of 46 closed non-Renovate PRs was authored **and** merged by `chrisns`. I
re-verified this on the one PR that matters most for the thesis: driftwood #20 has
`author.login: chrisns` and `mergedBy.login: chrisns`. The mea culpa's governance loop —
"Other teams review it, challenge it, adopt it or push back" — has no instance in the record. This
is expected in a one-person demonstration estate and I do not grade it as a defect of the build;
it is a limit on what the estate can be said to have *demonstrated* about the human layer.

---

## 5. The last mile

The mea culpa's third addition, and the thesis's own named open problem. ADR-0007 proposes the
answer: "an always-in-sync, human-readable policy handbook … generated from the versioned source".
Ticket 13 item 4 (PROVISIONAL) confirmed it as "a compose-time render … under the same gitsign tag
as the artefact", and graduated ticket 34.

- `grep -rln "handbook"` across all eight unit repos: **zero hits**.
- Ticket 34 is `Status: open`, `Blocked by: 09`.
- What a non-technical consumer would actually be handed today is
  `driftwood/composed/evidence.json` — whose `holes[]` array is ~250 entries of the shape
  `{"control_id": "ac-17.3", "status": "recorded"}` — and `composed/HEADER.yaml`, whose first line
  is `# advisory header -- policy-as-versioned.dev/composed (ticket 12; ADR-0012)`.

So the last mile is exactly where the thesis left it: named, honest, unsolved. The estate is
faithful in *naming* it (ADR-0007's own section says full adoption "remains partly cultural and is
named as a residual open problem") and has moved no distance on it. Because the legacy org's
`handbook-generator` was not lifted, the eco-system is currently **behind** the 2022 reference
implementation on this plank.

---

## 6. "Measurable, a PR search away" vs the truth surface

Covered in §2.2. In one sentence: the estate replaced an adoption metric with a truthfulness metric,
built a better adoption instrument than the thesis asked for (`verify-feed-contract`), and then
forbade any document from citing anything but the truthfulness metric (NORTH-STAR §5). A CIO asking
the thesis's question — "how many of my teams are compliant?" — gets the right answer from a script
nobody is allowed to quote as the headline, while the headline number (57/7/18 of 84) answers a
question the CIO did not ask.

---

## 7. Dilution: is the thesis still legible?

### 7.1 The census

Executable lines (`.py` + `.sh`, `wc -l`, `.git` excluded):

| body | lines | share |
|---|---|---|
| hub `twin/` | 34,678 | 35% |
| hub `tests/` (the twin's test suite) | 18,623 | 19% |
| `units/platform` | 25,163 | 26% |
| three adopters (driftwood+tuppence+ludlow) | 10,723 | 11% |
| four publishers (nist, ico, feeds, insurer) | 3,850 | 4% |
| hub `verify/` + `talk/` (the truth surface) | 5,271 | 5% |
| **total** | **~98,300** | |

Within `platform`, by module (`.py`+`.sh` only):

- **Dependency thesis**: `computed-semver` 7,524, `compose` 3,703, `distribution` 1,569,
  `party` 829, `oscal` 552, `shift-left` 224, `engine` 108, `policy` 92 → **14,601**
- **Pricing / £ / intelligence / insurance**: `wargamer`, `wardley`, `fair`, `risk`, `tcor`,
  `currency-controller`, `feeds`, `honesty` → ~5,500
- **Identity / access / cage**: `graded`, `identity`, `access`, `posture`, `break-glass`, `eud` → ~5,000

So roughly **15% of the estate's executable code directly implements the versioned-dependency
thesis**; a further ~5% (the truth surface) verifies it; the twin and its tests are **54%**.

### 7.2 The tickets

I classified all 74 files in `.scratch/ecosystem/issues/` by the primary concern in their title and
first paragraph (rule: a ticket counts once, to the concern its "Done =" clause serves):

| concern | tickets | count |
|---|---|---|
| dependency thesis (versioning, composition, distribution, updatable, shift-left, lift) | 4,5,6,13,16,18,33,34,35,39,40,42,43,53,61,62,71 | 17 |
| instrument / truth surface | 3,28,52,54,55,56,59,60,66,70 | 10 |
| pricing / £ | 7,8,15,24,25,30,38,45,69,74 | 10 |
| process / infra / provenance / safety | 1,2,10,19,41,44,57,58,65,67,73 | 11 |
| twin | 11,17,29,31,46,51,64,72 | 8 |
| cage ladder / identity | 9,12,26,27,32,63,68 | 7 |
| feeds / intelligence | 21,22,23,49,50 | 5 |
| insurance | 14,36,37 | 3 |
| demo / deck | 20,47,48 | 3 |

**23% of tickets serve the dependency thesis; 35% serve pricing + twin + insurance + feeds.**

### 7.3 Judgement

The dilution is **sanctioned, not drift**. Every one of these bodies is named in the ratified
NORTH-STAR §2 table (the twin has its own row; the insurer has one; the £ is principle 3). The
owner ratified that on 2026-08-27. So this is not an agent wandering off; it is the owner's own
widening, and grading it as "drift" would be grading against my taste rather than the record.

The fidelity cost is nonetheless real and worth naming plainly:

1. **The thesis is now a minority tenant of its own repository.** A reader arriving at this estate
   to learn "policy as a versioned dependency" meets 53,000 lines of organisational-forecasting
   code first. `docs/PRD.md` still frames the whole build as the thesis; NORTH-STAR §1 does not
   mention semver, coexistence, or Renovate at all. The two north stars are not reconciled in any
   one document.
2. **The twin's subjects are not the adopters.** NORTH-STAR §2 itself says "(subjects are eleven
   real firms today, not the adopters)", and open ticket 64 says only driftwood has an overlay while
   ticket 29's Answer claims all three. So the largest body of code in the estate is, today, mostly
   not about the policy the thesis is about. Its one connection to the priced chain is real and I
   verified the shape of it: `driftwood/composed/evidence.json` `prices[]` carries a `{source:
   twin, kind: twin, name: forward-intel}` entry at £7.91/customer.
3. **The one place the thesis is most legible is the least diluted.** `computed-semver` +
   `compose` + `distribution` is 12,800 lines of tightly-argued, heavily-self-checked code that does
   exactly what the thesis says. It is also, per `truth-series`, the module family with the most
   persistently red checks in the series — which means the clearest expression of the thesis is
   also the part the truth surface most often cannot confirm.

---

## 8. What `REVIEW-2026-08-31` said, and where it stands today

I checked its refuted list and did not re-raise anything on it. Two of its confirmed findings
intersect this dimension:

- **M8** ("step 2 has never happened for real … every Renovate PR closed/autoclosed") is **fixed and
  citable**: `verify-renovate-merged-feed-pr` PASSes on run 21 naming driftwood #20. I re-verified
  the PR via `gh`. Ticket 61 resolved.
- **M11(1)** ("one declared version leaves coexistence, retirement and shift-left without a
  subject") is **still true on run 21**, now with all three captures quoted above, and its owned
  remedy reaches two, not three (§1.3). Ticket 58 resolved on a bare "Agree" (PROVISIONAL); ticket
  63 open.

Nothing in this assessment contradicts a claim that review refuted.

---

## 9. Fitness verdict

See the structured return. In short: the mechanism half of the thesis is built, verified and in
places bettered; the *lane-keeping-vs-locked-door* half is proven only on a bench; the human
governance layer's carrier does not exist; the last mile is behind where the 2022 org left it; and
the one requirement the thesis calls non-negotiable — three coexisting versions with a retirement
window — is at one, with no window mechanism and no ticket aiming at three.
