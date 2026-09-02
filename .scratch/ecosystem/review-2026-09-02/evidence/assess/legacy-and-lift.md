# Assessment — the original org and the lift

Dimension key: `legacy-and-lift`. Auditor pass, 2026-09-02, read-only.
Newest citable line: `TRUTH 2026-09-02T10:11Z run=21 hub=7b92990 ... pass=57 fail=7 skip=18 excluded=2 total=84`.

Ambition being graded against: NORTH-STAR §6 last bullet ("The original org as the system…
Its working parts (fan-out, notifications, OSCAL CronJob, dashboards, real apps, sunset cron)
are to be lifted into the eco-system or explicitly retired, one by one, with a decision each"),
NORTH-STAR §4 steps 2–4, principles 3, 4 and 5, and the 2022 thesis's ≥3-coexisting-versions
requirement (`research/03-blogs-thesis.md:12-18`, attributed to the talk).

Every fact below was re-derived at a primary source. Where I could not look, it says so.

---

## 1. What state the original org is in

`gh repo list policy-as-versioned-flux --limit 50 --json name,isArchived,pushedAt` (2026-09-02):
**16 repos, 1 archived (`apps`, 2026-07-16), 15 live** — the hub plus the 14 reference repos.
This matches ticket 13's own 2026-08-28 count exactly; nothing has been archived in the five days
since ticket 13 resolved.

CI, from `gh run list --repo policy-as-versioned-flux/<r> --limit 5` on all 14 non-hub repos:

| repo | last run | state |
|---|---|---|
| fleet | 2026-09-02T12:33:55Z `sunset escalator` (schedule) | **success**, daily, green every day back through 2026-08-30 |
| policy | 2026-08-31T16:28:37Z `weekly governance nag` (schedule) | **success**, weekly, green back through 2026-08-03 |
| ledger, storefront, reports, api, readiness-collector | tag `release` runs, 2026-07-16/17 | success (one historical failure on ledger's first `v1.0.0` push, then success) |
| c2p-collector | 2026-08-23 `verify` on a Renovate PR | success |
| datastore, cloud, governance-agent, handbook-generator, pr-gate-action, renovate-config | none | no workflows registered |

**There is no red CI anywhere in the original org.** That is the opposite of the current
eco-system's hub, where `gh run list --repo policy-as-versioned-flux/policy-as-versioned-flux
--limit 12` shows 12 consecutive `truth`/`twin` failures, the most recent at 2026-09-02T09:54:45Z,
i.e. after the run-21 TRUTH capture. The superseded implementation is greener than the successor.

Two clocks are genuinely live:

- **fleet's sunset escalator** (`cron: "0 8 * * *"`). It has one real, dated outcome:
  `gh pr view 69 --repo policy-as-versioned-flux/fleet` →
  `#69 Sunset: retire policy 1.0.0 (scheduled 2026-08-15) | author=app/github-actions
  mergedBy=chrisns at 2026-08-15T17:20:11Z state=MERGED`. A machine opened a retirement PR on a
  clock; a different, human identity merged it.
- **the weekly governance nag** (fleet and policy). Green, currently nagging nothing.

Nothing is rotting *red*. What is rotting is *unowned*: ~44 Renovate PRs open across the org
since 2026-07, none merged, and 5 `agent-governance-review` issues on `policy` opened 2026-07-15
with no comments. That is the expected state of a frozen reference, not a fault.

Two smaller live-org observations:

- `fleet/.github/workflows/sunset-escalator.yml` checks out `policy-as-versioned-flux/governance-agent`
  with **no `ref:`** — an unpinned cross-repo runtime dependency inside the org whose whole
  argument is "pin everything, bump by PR".
- The apps are real, not fixtures. Re-verified by reading the manifests over the API:
  `ledger/pom.xml` declares `log4j-core` **2.14.1**; `storefront/package.json` declares
  `@angular/* ~9.1.0`, `rxjs ~6.5.3`; `reports/requirements.txt` declares `Flask==1.1.4`,
  `Jinja2==2.11.3`, `Werkzeug==1.0.1`. Real, resolvable, genuinely stale dependency trees.

**Coupling: zero.** I re-derived the isolation claim rather than trusting the map. For each of
the 13 non-hub legacy repos, `grep -rl "policy-as-versioned-flux/<repo>"` over all eight fresh
unit clones returned **0 files**, and the same grep over the hub's `talk/` and `verify/`
returned 0. Nothing in the eco-system reads, clones, pins or images anything from the original org.

---

## 2. What NORTH-STAR §6 demanded vs what tickets 13/33/35 decided and built

NORTH-STAR §6 names six working parts; ticket 13's Question names nine. Ticket 13
(`Status: resolved`, 2026-08-28) recorded five answers. Here is each against today's tree.

| mechanism | ticket 13 disposition | state today (verified) |
|---|---|---|
| 5 real apps | **lift** ledger→tuppence, storefront→driftwood, reports→ludlow (provisional); api + datastore wait | **not started.** No `pom.xml`, `package.json`, `requirements.txt`, `go.mod` or non-fixture `Dockerfile` in any adopter (`find` over all three clones returns only `<adopter>/git-server/Dockerfile`). Ticket 33 open, unblocked (blocker 09 is resolved), and **not on the map's own order of attack** (map.md:100-104 lists 54→55→57→61→60→56→58→62,63→59,64,65,66,67 — no 33) |
| sunset cron | **retire consumer-side; D5 DECIDED**: publisher-side supersede, EOL-ramp priced, adopter's scheduled proposer opens a retirement PR | **half-built at best.** ADR-0010 still `status: accepted` with the consumer-side `sunset:` field and **no supersession banner** (`head -8 docs/adr/0010-*.md`); `git log --since=2026-08-27 -- docs/adr/0010-*` is empty. No ticket anywhere owns the retirement-PR proposer: `grep -rn "retirement PR" .scratch/ecosystem/issues/ map.md` hits **only** tickets 13 and 10. `driftwood/.github/workflows/propose-tier.yml` proposes a `posture.acme.io/tier` edit and nothing else |
| Crossplane cloud plane | **lift to tuppence** after the Pod slice runs once; ADR-0004 gains a dated sequencing note | **not started, and the note was never written.** `grep -ril crossplane` over all eight units hits exactly two files, both prose: `platform/oscal/README.md` and `platform/oscal/fixtures/policyreports.yaml`. `docs/adr/0004-cloud-plane-fork-collie.md` still reads `status: accepted`, "an **integral second plane of the floor** (not deferred)… proven at the admission level on KiND", with no dated note; `git log --since=2026-08-27` on the file is empty |
| handbook | **lift as a compose-time render**; ADR-0007's last-mile section confirmed by this | **not started.** `grep -ril handbook` over all eight units hits one file, `nist/catalog/NIST_SP-800-53_rev5.2.0_catalog.json` (a coincidental word inside the OSCAL catalogue). Ticket 34 open, unblocked, off the route. ADR-0007's section still reads "## Last-mile to non-technical consumers (proposed — confirm)" |
| readiness collector | **retire with reason** (priced adopter gate replaces the counts) | honest retirement, no action needed |
| Grafana / CIO dashboards | **retire**, owner rejected 2026-07-20 | honest retirement, held |
| vulnerability scanner | **round 2**, undecided → ticket 35 | ticket 35 `Status: open`, `Blocked by: 16, 21, 33`. 16 and 21 are resolved; **33 is the live blocker** |
| Flux notification spine | **round 2**, undecided → ticket 35 | same. `grep -rln "kind: Alert\|kind: Provider\|kind: Receiver"` over the units → nothing |
| OSCAL CronJob | shape decided, **placement/cadence round 2** → ticket 35 | same. `grep -rln "kind: CronJob"` over all eight units returns exactly one file, `platform/currency-controller/manifests/cronjob.yaml`. The OSCAL up-flow is still offline over `platform/oscal/fixtures/` |
| currency controller (C15) | **"retired… it 404s and ticket 07's fx feed replaces it"** | **not retired, and the reason is wrong** — see finding L5 |
| per-repo archiving | archive each on GitHub once graded green, fleet last | nothing archived; correct under the rule, because nothing has been lifted |

**Net: of the nine-plus mechanisms, three are honestly retired (readiness counts, dashboards,
consumer-side sunset-in-principle), three are decided-but-unstarted (apps, cloud plane, handbook),
three remain undecided behind a blocked round 2 (scanner, notification spine, OSCAL CronJob),
and one (currency controller) was retired on a false premise and is still running.** Ticket 13's
own text says "ticket 13 does not close before round 2" (lines 62 and 90) while its header reads
`Status: resolved`; `map.md:40` records this correctly as "round 2 pending".

---

## 3. Do the adopters have any real application workload?

**No.** Complete inventory of every container image declared in the three adopter clones
(`grep -rn "image:" driftwood tuppence ludlow`, excluding `.git`):

- `driftwood/deploy/pod.yaml` and `driftwood/gitops/apps/pod.yaml`: `image: nginx` — unpinned,
  no tag, no digest. One Pod, `checkout-svc`, label
  `policy-as-versioned.dev/policy-version: "4.0.0"`. This is the only Flux-wired workload in the
  eco-system.
- `tuppence/deploy/pod.yaml`, `ludlow/deploy/pod.yaml`: `image: nginx`, one-line inline Pod,
  **not** referenced from `gitops/apps/kustomization.yaml` in either repo.
- `<adopter>/git-server/deployment.yaml`: `<adopter>-git:local` — the local fixture git server.
- `tuppence/reset/{workloads,openbao-role}.yaml`: `curlimages/curl:latest`,
  `hashicorp/http-echo:latest`, `openbao/openbao:latest` — the tuppence-only reset tour, all
  `:latest`, in a namespace the composed artefact itself records as `ungoverned`.
- One `ghcr.io/acme/coraza-waf:cage` string inside the `cage-tier` CEL body — an invented
  registry path in a mutation expression, not a deployed image.

So: nginx and fixtures. That is the state ticket 13's Q1 recorded on 2026-08-28 and it is
unchanged.

The deeper point, which no map or ticket states, is that **the £ does not depend on a workload at
all**. `driftwood/composed/evidence.json` `prices[]` has exactly four entries, all from signed
parents and the party's own declared size:

```
{source: ico,     kind: feed,    name: penalty-schema,  amount: 1,787,177.08}
{source: feeds,   kind: feed,    name: threat-register, amount:    19,558.55}
{source: insurer, kind: premium, name: quote-driftwood, amount:   113,403.30}
{source: twin,    kind: twin,    name: forward-intel,   amount: 1,897,646.11}
```

`grep -n "deploy/pod\|image\b\|inventory\|sbom\|SBOM" platform/compose/composition.py` returns
**nothing**. Composition never reads a workload. Deleting `deploy/pod.yaml` would change no
number in the composed artefact. NORTH-STAR §4 step 3's "the workload keeps running, caged
tighter. The residual is on the balance sheet" is therefore, today, two independent claims that
do not touch: the cage moves the pod, and the £ moves from feeds, and neither is a function of
the other.

---

## 4. Did the cloud plane survive?

No. ADR-0004's runtime proof lives **only** in the original org and is verifiably still there:
`fleet/clusters/cluster1/policy-versions.yaml` ships `require-s3-bucket-encryption` and
`require-rds-multi-az` as `plane: cloud` policies under version `2.2.0`, with
`dependsOn: crossplane-providers`, and fleet's rendered orphan guard covers
`s3.aws.m.upbound.io/bucketserversideencryptionconfigurations` and
`rds.aws.m.upbound.io/instances` explicitly. `datastore/claims.yaml` is the workload.

In the eco-system: zero Crossplane manifests, zero CRDs, zero cloud policies, zero references
outside two prose files. ADR-0004 still asserts the plane is "integral… not deferred" and
"proven at the admission level on KiND" with no dated note distinguishing where that proof lives.

---

## 5. Does the two-org overlap confuse a reader?

Yes, and the confusion is concentrated at the GitHub front door, not in the deck.

- `gh api orgs/policy-as-versioned-flux` returns `{"name":null,"description":null,"blog":null}`
  and `repos/policy-as-versioned-flux/.github/contents/profile/README.md` is a 404 — **no org
  description, no profile README**. A reader lands on 16 repos with no signpost.
- I read the first 12 lines of all 14 legacy READMEs over the API. **None carries a superseded /
  reference-only banner.** All read in the present tense as the live system: fleet's says "The
  config repo Flux reconciles… **three policy versions coexisting side by side**"; `policy`'s says
  "Tagged semver releases of this repo **are** the dependency consumers pin — see the hub repo's
  CONTEXT.md and ADR-0001/ADR-0002." Following that link now lands on documents describing a
  *different* system, with a different label family (`policy-as-versioned.dev/policy-version` vs
  `mycompany.com/policy-version`) and a different publisher (`policy-as-versioned-platform/platform`).
- The hub's own `README.md` is 38 lines. It describes the system as "governed by one Kyverno
  engine across a Kubernetes workload plane and **a Crossplane cloud plane**", lists "cloud plane
  by harvesting ControlPlane **collie**" under "The decisions, in one breath", points at
  "docs/adr/ — The **decisions** and why (ADR-0001…0010)" when there are 24 ADRs, and carries a
  "Project actions queued" list whose item 2 ("Harvest collie") is already done in the `cloud`
  repo. It **never names the eight eco-system orgs** and never says the 14 sibling repos are the
  superseded reference.
- The only document that addresses the two-implementation question at all is `docs/ARCHIVE.md`,
  whose 2026-08-28 banner is accurate and clear — but it is titled "Archiving
  policy-as-versioned-flux" and buried under `docs/`.
- `talk/deck.md` and `talk/narration.json` on `origin/main` contain zero references to any legacy
  repo. The deck is clean; the org is not.

Related, and this is the sharpest single fact in the dimension: **the thesis's own
≥3-coexisting-versions crux is unproven in both orgs today.** `fleet`'s live array declares two
versions (`2.0.0`/tag `2.0.3`, and `2.2.0`) — it was three until the sunset cron retired `1.0.0`
on 2026-08-15. `platform/distribution/versions.yaml` declares **one** (`4.0.0`), with a dated
2026-08-29 comment retiring 2.0.0/2.0.1/3.0.0 for two independently-observed live defects. Whatever
the right disposition of the original org is, it cannot be "the eco-system already shows what fleet
showed" — on this specific requirement neither does.

---

## 6. Findings

### L1 — critical — The decided lift, as scoped, cannot make a feed re-price anything real

Ticket 13 Q1's recorded rationale is explicit: "(a). NORTH-STAR §4 step 3 … is only honest with a
real dependency a feed can move." Ticket 33's entire scope is "Re-label each app… re-pin to the
adopter's composed artefact, add a renovate.json enabling the stack's manager and dependency
dashboard, and grade each in the truth surface." None of those three acts connects an
application's dependencies to the £.

The missing link is a converter. `platform/compose/composition.py:271-274`:

```python
FEED_CONVERTERS: dict[str, tuple[str, ...]] = {
    "threat-register": ("feeds", "to_fair_scenario.py"),
    "penalty-schema": ("schema", "to_fair_scenario.py"),
}
```

Exactly two feed names can be priced. `composition.py:1540-1543` refuses anything else:
`raise Refused(f"missing instrument: feed {name!r} declared by {adopter_party} has no converter
this composition can price through")`. So if `ledger` (log4j 2.14.1) were lifted into tuppence
today and tuppence pinned the CVE feed, composition would **refuse the whole artefact**, not price
the CVE. The converter work sits inside ticket 35 (the scanner), which is `Blocked by: … 33`.

Ticket 33 is therefore a ticket whose stated definition of done ("grade each in the truth surface")
has nothing priced to grade, and whose owner-recorded reason for existing is delivered by a
different, blocked ticket.

- **Evidence:** `platform/compose/composition.py:271-274,1540-1543` (read); `grep -n
  "deploy/pod\|image\b\|inventory\|sbom" platform/compose/composition.py` → no matches;
  `.scratch/ecosystem/issues/33-*.md` (whole file, 14 lines);
  `.scratch/ecosystem/issues/35-*.md:5` (`Blocked by: 16, 21, 33`);
  `.scratch/ecosystem/issues/13-*.md:44` (the rationale).
- **Already owned by:** partly — ticket 33 owns the lift, ticket 35 owns the scanner. **The
  ordering defect (33 must run first but 35 carries the only thing that makes 33 mean anything) is
  owned by nothing.**
- **Remedy:** either invert the dependency (make the CVE/EOL converter a prerequisite of 33, not
  a consequence of it), or restate ticket 33's definition of done honestly as "a real app runs
  caged, priced at zero, until ticket 35 lands its converter" — and say so in the ticket so the
  gate check it wires in is not mistaken for step-3 evidence.

### L2 — major — The `cve` and `eol` feeds are published and discoverable but unconsumable

`feeds/party.yaml:12-35` advertises `cve` and `eol` in `publishes[]` with payload schemas, which
under ADR-0019 is the whole discovery contract ("the set of signed publisher artefacts IS the
catalogue"). `feeds/cve/` and `feeds/eol/` each hold `v1`, `v2`, `payload.schema.json`,
`rule.yaml`, `bump.yaml`. But no adopter pins either (`driftwood/composed/HEADER.yaml` parents are
platform, nist, ico/penalty-schema, feeds/threat-register, insurer/quote-driftwood; tuppence and
ludlow have four), and any adopter that did would hit the `missing instrument` refusal above.

This is the specific mechanism both remaining lifts need: the scanner (ticket 35) is defined as
"an image inventory priced against the feeds org's CVE feed", and D5's supersede is defined as
"priced by the existing EOL ramp". Neither can be built without it.

- **Evidence:** `feeds/party.yaml:12-35`; `ls feeds/cve feeds/eol`; `ls feeds/converters/` → only
  `fx.py` and `README.md`; `platform/compose/composition.py:271-274,1540-1543`;
  `driftwood/composed/HEADER.yaml:6-27`.
- **Already owned by:** none found. `grep -rn "FEED_CONVERTERS\|converter for\|cve feed\|eol feed"`
  over `.scratch/ecosystem/` returns only fact-finding lines in tickets 10, 13, 15, 22 and 24 —
  ticket 22:31 records the behaviour ("any other edge kind is skipped silently… composition wiring
  only the `threat` subcommand"), no ticket owns fixing it.
- **Remedy:** one ticket: "a published feed with no converter is a priced hole, and cve/eol get
  theirs" — either add `cve`/`eol` to `FEED_CONVERTERS` (the converter already exists at
  `platform/feeds/to_fair_scenario.py`, whose `cve_scenario` and `eol_scenario` functions are
  written and selfchecked), or make an unconverted pin a priced hole under ADR-0020 rather than a
  refusal, on ticket 69's pattern.

### L3 — major — D5, a DECIDED item, has no build ticket anywhere

Ticket 13's item 5 is one of only five items in the whole ticket set recorded `Decided` on a
reasoned owner line ("I agree with you're more advanced reasoning"). It says: "The adopter's
scheduled proposer reads pins against the feed and opens a retirement PR (D1: a proposal, never a
declaration). Retirement PRs use ticket 10's dedupe ledger, keyed `<org>/<kind>/<slug>`."

`grep -rn "retirement PR\|retirement pull" .scratch/ecosystem/issues/ map.md` returns hits in
**ticket 13 and ticket 10 only**. Ticket 10 is `Status: resolved` and its Graduated line reads
"Daily clocks, caged observation lane and derived ledger" — the retirement-PR proposal type is not
in it. Ticket 10's own cross-ticket note C15/C16 flags the hole in advance ("A retirement proposal
has no dedupe key or half-life under Q5(a)"), and it was never resolved.

Meanwhile the mechanism this replaced is still running, once weekly-successfully, in the org it was
retired from.

- **Evidence:** `.scratch/ecosystem/issues/13-*.md:83`; `.scratch/ecosystem/issues/10-*.md:4,75,94`;
  `grep -rn "retirement PR" .scratch/ecosystem/`; `driftwood/.github/workflows/propose-tier.yml`
  (whole file — the only proposal it can emit is a tier edit on the governed Namespace).
- **Already owned by:** none found.
- **Remedy:** a build ticket carrying D5's second half, blocked on L2's converter, with its dedupe
  key defined.

### L4 — major — All three ADR consequences ticket 13 recorded are unwritten

Ticket 13's Consequences (lines 86): "ADR-0010:5-9 (consumer-side `sunset:`) is superseded by the
ADR ticket 10 writes. ADR-0004 gains a dated sequencing note. ADR-0007's last-mile section is
confirmed by item 4."

`git log --oneline --since=2026-08-27 -- docs/adr/0004-cloud-plane-fork-collie.md
docs/adr/0007-agent-assisted-editorial-governance.md docs/adr/0010-sunset-scheduled-proposals.md`
returns **nothing**. All three files are unchanged since before ticket 13 resolved:

- ADR-0010: `status: accepted`, no banner. The only mention of it in a later ADR is
  `docs/adr/0023-*.md:70`, which sharpens the *timing* clause and says nothing about the
  consumer-side `sunset:` placement D5 superseded. Six ADRs carry a superseded marker
  (0013, 0014, 0015, 0016, 0018, 0024's own note); 0010 does not.
- ADR-0004: `status: accepted`, still asserting an integral, non-deferred, KiND-proven second
  plane that does not exist in the eco-system.
- ADR-0007: still "## Last-mile to non-technical consumers (proposed — confirm)".

- **Already owned by:** ticket 67 ("the record matches the surface", open) is adjacent but its text
  does not name these three ADRs.
- **Remedy:** three dated banners, ~10 lines total. Cheapest correction in the estate.

### L5 — major — The currency controller is recorded as retired, on a wrong reason, and is not retired

Ticket 13 answer item 2 and `map.md:113` both record: "The currency controller is retired
(ticket 13)" / "it 404s and ticket 07's fx feed replaces it."

Three separate problems:

1. **The replacement claim is a category error.** `platform/currency-controller/README.md:1-8`:
   "posture re-evaluated after admission… when a running workload's admitted version is retired
   from the platform array, a bounded reconcile pass re-patches its posture (default) or evicts
   it, and the SVID follows." That is *currency of posture*. Ticket 07 (`map.md`, ticket 07 line)
   is about money — "FX is a signed `fx` feed". An FX feed cannot replace a post-admission posture
   reconciler.
2. **It is not retired.** `platform/currency-controller/` is present at run-21's platform SHA
   (`46cd775`) with `currency.py`, `manifests/cronjob.yaml` (`schedule: "* * * * *"`), `up.sh`,
   `README.md` and `verify-currency.sh`. It is the only `kind: CronJob` in the entire eco-system.
   The gate grades it every run: `git show origin/main:talk/captures/.estate-clone_platform_currency-controller_verify-currency.out`
   ends `SKIP: offline proof holds; live tail could not look: kind cluster 'driftwood' is not
   listed by kind get clusters — stale posture is re-evaluated post-admission`.
3. **Another resolved ticket contradicts it.** Ticket 32 (`Status: resolved`) scopes "make the
   currency controller fail loudly on a missing ResourceSet". A resolved ticket repaired a
   mechanism another resolved ticket retired.

The "404s" premise is itself indirect: ticket 12:24 records the 404 as `HTTP Error 404` from
`GET .../resourcesets/policy-versions` on a cluster where no ResourceSet exists — a substrate
absence, not a dead mechanism. `grep -rn 404 platform/currency-controller/` returns nothing.

- **Remedy:** withdraw the retirement, or re-retire it with a reason that survives reading the
  README. Correct `map.md:113`. If it stays, it needs an owner: it is the eco-system's only
  CronJob and its live tail has never been observed.

### L6 — major — Two live clocks run outside the truth surface, in the project's own org

NORTH-STAR §5: "One command, on a schedule, in CI, is the only source any document may cite for
'what works'." `clone-estate.sh:23` sets `UNITS=(platform driftwood tuppence ludlow nist ico feeds
insurer)`; `verify/schedules/schedules.py:85-86` builds remotes from
`policy-as-versioned-{unit}/{unit}` plus the hub. Neither reaches the legacy org.

So fleet's daily sunset escalator and the weekly governance nag — the only clock in either org
that has ever produced a merged retirement PR — are ungraded. If either broke tomorrow, no TRUTH
line would move, and the estate would learn about it only if a human looked at GitHub.

This is not an argument to grade them. It is an argument that the disposition decision is now
overdue in a specific way: while a mechanism is neither lifted nor archived, it is running
unobserved inside the boundary NORTH-STAR §5 claims to cover.

- **Already owned by:** ticket 56 ("the citable run can see whether the clocks ran", open) covers
  the eco-system's own clocks, not the legacy ones.
- **Remedy:** either archive fleet's workflows (deferred to fleet-last under 13 item 2, so: not
  yet), or add a one-line honest note to the TRUTH-line documentation that two clocks in the
  reference org are deliberately outside the surface.

### L7 — major — Neither implementation demonstrates the ≥3-coexisting-versions requirement today

The talk's stated requirement is ≥3 policy versions coexisting at runtime
(`research/03-blogs-thesis.md:12-18`). Today:

- `fleet/clusters/cluster1/policy-versions.yaml` declares **two** array elements: `version: "2.0.0"`
  (tag 2.0.3) and `version: "2.2.0"`. It declared three until the sunset cron retired 1.0.0 on
  2026-08-15 (fleet#69).
- `platform/distribution/versions.yaml` declares **one**: `4.0.0`, with a dated 2026-08-29 comment
  retiring 2.0.0/2.0.1/3.0.0 and the two backports for two independently-observed live defects
  (Priority-admission triple mismatch; pod-forged tier label reaching the API server).

Both retirements are individually defensible and honestly documented. The consequence is not:
the thesis's own crux is currently demonstrated by neither org, and the honest disposition of the
original org can no longer be "we already show that better".

- **Already owned by:** partly. Ticket 71 (open) owns the Kyverno-1.19 question that gates
  re-authoring older lines. Nothing owns "restore a ≥3-version coexistence demonstration".
- **Remedy:** decide explicitly whether the ≥3-version claim is retained, narrowed (the *mechanism*
  supports N, demonstrated at N=1 because the older bodies were unsafe), or retired — and say so
  where a reader meets the claim. `CONTEXT.md:153-155` still calls it "the crux of the original
  implementation".

### L8 — major — Two orgs make overlapping present-tense claims, with no signpost anywhere a reader lands

Detailed in §5 above. In one line: `gh api orgs/policy-as-versioned-flux` returns a null
description, there is no `.github/profile/README.md`, none of the 14 legacy READMEs says it is
superseded, several of them link *into* the hub's current CONTEXT.md and ADRs as authority for
claims those documents no longer make, and the hub's own 38-line README describes the old system
(Crossplane cloud plane, ADR-0001…0010) and never names the eight orgs where the current system
lives.

- **Already owned by:** ticket 02 (resolved) put banners on `.scratch/twin/map.md`,
  `.scratch/twin/spec.md` and `docs/ARCHIVE.md`. It did not reach the legacy repos or the hub README.
  Ticket 67 (open, "the record matches the surface") is the nearest home.
- **Remedy:** three cheap acts, none of which pre-empts an archiving decision: (i) an org
  description and `.github/profile/README.md` naming the two implementations and pointing at the
  eight orgs; (ii) a two-line dated banner at the top of each legacy README ("Reference
  implementation of the July 2026 thesis. The current system is the eco-system — see
  NORTH-STAR.md. This repo is retained as the audit trail; its lift-or-retire decision is
  ecosystem ticket 13."); (iii) fix the hub README's first paragraph and ADR range.

### L9 — minor — Ticket 13's header contradicts its own text

`Status: resolved` at line 4; "ticket 13 does not close before round 2" at lines 62 and 90.
`map.md:40` gets it right ("round 2 pending"). Symptom of the unstandardised status vocabulary
GAPS 2.9 / REVIEW-08-31 M14 named; ticket 59 (open) owns the vocabulary but not this instance.

### L10 — minor — The Renovate dashboard fix was folded into "whichever ticket first touches renovate.json" and that ticket did not do it

Ticket 13's "Already decided" paragraph: "Renovate dependency dashboard: switch it on
(GAPS 3.25), folded into whichever ticket first touches renovate.json." Since 2026-08-28,
`git log --since=2026-08-28 -- renovate.json` shows two commits on driftwood, both ticket 61
(`fc1a252 ticket 61: exactly one Renovate acts on this repo`, `8f7861f ticket 61: Renovate
completes step 2`), and none on tuppence or ludlow. All three still read
`enabledManagers: ["custom.regex"]`, `dependencyDashboard: false`; driftwood additionally reads
`enabled: false`. A decision parked on "the next ticket that touches the file" was not picked up
by the next ticket that touched the file.

### L11 — minor — `fleet`'s sunset escalator fetches its own script unpinned

`fleet/.github/workflows/sunset-escalator.yml`, step "Fetch sunset-escalator.sh from
governance-agent": `actions/checkout@v4` with `repository: policy-as-versioned-flux/governance-agent`
and **no `ref:`**. The clock that enacts the versioning thesis runs whatever is on another repo's
default branch. Worth naming because any lift of this mechanism must not carry the shape across.

### L12 — minor — `clone-estate.sh`'s header is stale in two ways that matter to a reader

`clone-estate.sh:2` "the six real policy-as-versioned-* unit repos" while line 23 lists eight;
lines 37-38 "No signed tag exists yet (ticket 09/12: known, accepted partial state) so this clones
the default branch" while all 24 unit tags verify with gitsign today (per the github-live map;
I did not re-run gitsign myself — `git tag -v` fails in this sandbox with a gpgsm error because
these are keyless Sigstore signatures, so I record this as map-sourced, not re-derived). The
comment reads as a live limitation but is a historical one, and it is the file that defines the
boundary of the truth surface.

### L13 — minor — Hub README's "Project actions queued" item 2 is already done

`README.md:35`: "2. Harvest `controlplaneio/collie` — catalogue + intent as data, toolchain
dropped (ADR-0004)." The `cloud` repo holds the harvested catalogue (README verified over the API,
last push 2026-07-14) and ADR-0004 describes the harvest in the past tense. A queued-actions list
with a completed item on it is a small honesty leak in the estate's front door.

---

## 7. Strengths, honestly

- **The isolation is real and I re-derived it.** Thirteen greps, thirteen zeroes. Nothing in the
  eco-system depends on the original org. Whatever is decided about those 14 repos, no eco-system
  check can break as a result. That is a genuinely good position to make a decision from.
- **The original org is not rotting.** No red CI anywhere, two clocks green, the only merged
  retirement PR in either org (fleet#69, machine-authored, human-merged, 2026-08-15) is a real
  instance of NORTH-STAR §4 step 3's shape.
- **Three retirements are honest and well-reasoned.** The dashboards (owner-rejected, cited
  verbatim), the readiness collector's counts (replaced by priced impact, not silently dropped),
  and consumer-side `sunset:` in principle (D5, the one item in ticket 13 with a real owner
  reason) are decisions a skeptic can read and disagree with, which is the point.
- **Ticket 13's fact-finding is exemplary.** Twenty dated facts with per-clause citations,
  gathered before any question was put, including facts that undercut the recommendation
  (H6-06's refuter noting the "CIO dashboard" framing was the assistant's paraphrase, not the
  owner's words). Two of its facts turned out to be wrong (L5) — but they are wrong in a way a
  reader can catch, because they carry their sources.
- **The archive rule is the right rule.** "Archive each original repo once its lift or retirement
  is recorded and graded green by the truth surface, fleet last" means nothing is destroyed before
  its replacement is proven. Zero repos archived is currently the *correct* state under that rule,
  not a failure of it.
- **The eco-system's clock discipline is materially stronger than the legacy org's.** fleet's
  escalator holds `contents: write`, `pull-requests: write`, `issues: write` and pushes branches;
  driftwood's `propose-tier.yml` declares an `OBSERVATION_LANE`, re-composes into `RUNNER_TEMP`,
  and ends with a cage step that `git reset`s first and fails the run on any staged path outside
  the lane — with an inline note recording the exact 2026-08-28 defect (a `grep -v '^[AMD] '`
  filter) that made the earlier guard blind. Any lift must carry this shape forward, and the
  design to carry it exists.
- **`docs/ARCHIVE.md`'s banner is the model.** Dated, specific, names what reversed it, and
  explicitly says the checklist below is "not to be executed" rather than deleting it. Thirteen
  more of those would close L8.

---

## 8. Fitness verdict

Not fit yet, for one structural reason and one procedural one.

Structurally: NORTH-STAR §6 asks for a lift-or-retire decision per working part, and §4 asks for a
demonstration in which a feed re-prices something real and the workload keeps running caged
tighter. Ticket 13 produced the decisions — genuinely, with evidence — but the three that were
decided *to lift* (apps, cloud plane, handbook) are all unstarted five days on, all off the map's
own route, and the first of them cannot deliver its stated purpose as scoped because the £ engine
can price exactly two feed names and reads no workload at all. The eco-system's only application
is an unpinned `nginx`, and the composed price would be byte-identical if it were deleted.

Procedurally: three ADR consequences the ticket itself recorded were never written, one mechanism
was retired on a reason that does not survive reading its README and is still running and still
graded, and the round-2 decisions (scanner, notification spine, OSCAL CronJob) sit behind a blocker
that nobody is working. Meanwhile the superseded org has greener CI than the successor, runs the
only clock that ever produced a merged retirement PR, and is the only place either the cloud plane
or multi-version coexistence was ever proven at runtime.

What would make it fit, in order: (1) invert 33/35 so the CVE/EOL converter lands before or with
the app lift, and say in ticket 33 what its gate check actually proves; (2) write the three ADR
banners and withdraw the currency-controller retirement; (3) put a dated banner on each legacy
README and an org profile README naming the two implementations — this alone removes most of the
confusion at almost no cost and pre-empts no decision; (4) run ticket 13 round 2 (ticket 35), which
only needs 33 to move; (5) decide explicitly what happens to the ≥3-version claim now that neither
org demonstrates it.

---

## 9. What I could not look at

- **Whether any legacy cluster is running.** The manifests prove intent; nothing here probed a
  cluster. Ticket 13 recorded the same limitation on 2026-08-28 and I did not improve on it — a
  read-only review with no cluster cannot.
- **Signature verification of legacy tags.** `git tag -v` fails in this sandbox (gpgsm, keyless
  Sigstore signatures). Tag existence and content were read over the API; cryptographic validity
  was not re-derived and is taken from the `github-live` and `publishers` maps where cited.
- **Org-level Actions permissions on the legacy org** (`gh api orgs/.../actions/permissions`
  requires `admin:org`; the github-live map records 403 on the two orgs it tried, and I did not
  retry).
- **Whether the four `multi-org-estate` `partial` tickets were later completed.** Flagged by the
  legacy-org map, not chased here — out of this dimension's scope.
- **The 2022 reference orgs `example-policy-org` / `policy-as-versioned-code`** named in
  `CONTEXT.md:9`. I did not check whether they still exist; if they do, they are a third and
  fourth surface with overlapping claims and L8 gets worse.
