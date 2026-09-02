# Map — the eco-system, operating

Label: `wayfinder:map`. Charted 2026-08-28. Supersedes the nine earlier efforts under `.scratch/` as the single map for what comes next. Their maps and tickets stay as the record.

## Destination

Every joint in [NORTH-STAR.md](../drift-review-2026-08-27/NORTH-STAR.md) §4 (regulator publishes; Renovate pins; the £ crosses a band and a proposal PR opens; Flux reconciles the cage; the twin plays a signal forward; provenance; honesty) has an owning ticket the truth surface can grade, and the eco-system has run end to end once, on a clock, with driftwood, tuppence and ludlow consuming. Then hand off to `/to-spec`. This map carries execution: tickets build, not only decide.

## Notes

- The north star is ratified. The owner's answers to 41 re-grills and 22 reversals are binding: [REGRILL-ANSWERS.md](../drift-review-2026-08-27/REGRILL-ANSWERS.md). The ranked gaps are [GAPS.md](../drift-review-2026-08-27/GAPS.md).
- Build order: the seven steps in NORTH-STAR §4, thinnest slice end to end first (one regulator, one adopter, one feed, one cage move, one twin forecast, all real), before widening. The truth surface is built in parallel because it grades the slice.
- Vocabulary: there is no gate. Everything is caged; the spec of the cage is the only variable; the £ picks the spec; the bottom rung is "too expensive to run or not functional". Never an exemption, never an exemption ledger. Price and cage; never count, refuse or file.
- Versioning follows ESLint shareable configs: every package its own semver; a composed set is a new package; republish and inner-source are normal.
- Schedules run the LLM-free data gathering. Reasoning is packaged as Claude Code skills a human runs over the gathered results. The reviewed PR is the unit of adoption.
- Process rules (from the drift review): at most five decisions put to the owner per day, none inside an implementation run; a bare "agree" or letter does not ratify architecture, so a decision is recorded with the owner's reason or it stays open; a spec does not advance to tickets without a recorded owner confirmation; done is defined by the truth surface, never by the demo; every ticket's definition of done includes wiring its check into the gate.
- Skills to consult: `/mattpocock-skills:grilling` and `domain-modeling` for every grilling ticket; `/mattpocock-skills:research` for research tickets; `/arckit:wardley` and `/arckit:impact` for the twin; CONTEXT.md and docs/adr/ before any work.
- Batch record, 2026-08-28: the owner read all 14 held rounds and wrote "ive already read the recommendations and I can't find fault with a single one". Every accepted recommendation is recorded as provisional with that line. Five cross-ticket conflicts went to the owner with a three-lens panel verdict; the owner wrote "I agree with you're more advanced reasoning"; those five are decided (D1 to D5 in each ticket's Answer, ADR-0023). The five-per-day rule was overridden by the owner's instruction for this batch. Held rounds stay in each ticket above the Answer as the record of what was recommended.
- A `Status: prepared` ticket holds a drafted HITL round the owner has not answered. See `docs/agents/issue-tracker.md`.
- Identity is spine, not cut (charting Q2). The feeds and insurer parties are real orgs the owner creates (charting Q4).

## Decisions so far

<!-- one line per closed ticket -->
- [04 — The feed contract](issues/04-the-feed-contract.md) — one envelope (`kind`, `name`, `version`, `published_by`, `published_at`, `payload_schema`, `payload`), signed by the gitsign tag and nothing else; parent kind closed to `controls | implementations | feed` with a free `name`; subscription is `inherits[]` plus `since`; discovery is `publishes[]` on the publisher's `party.yaml`, no central catalogue; revocation is a new version plus `revoked[]`, a revoked pin is a priced hole. Owner agreed twice without a reason; recorded as such. ADR-0019.
- [03 — The truth surface](issues/03-the-truth-surface.md) — `talk/verify-all.sh` discovers all 56 scripts by glob, grades PASS/FAIL/SKIP by exit code, ends with one dated TRUTH line that `truth.yml` writes daily to `talk/truth.log`; first number 40/16/0 of 56; `twin.yml` split and scheduled; invariants 42 and 45 green, 43 and 44 red by decision; five unit-repo PRs (platform 3 and 4, driftwood 11, tuppence 8, ludlow 7) carry three-outcome live tails, substrate-first, the semver-distance window and pin-reading verifiers, unmerged; post-mortem in HISTORY.md; pitch-v6 reds re-attributed; tuppence scenario E, the six live-object reds and the 12 enact tests stay red and named.
- [02 — Supersede and rebaseline the documents](issues/02-supersede-and-rebaseline-the-documents.md) — NORTH-STAR.md is at the root and is the one referent; twin map, twin spec and ARCHIVE.md carry dated banners; the transport doc is renamed; CONTEXT.md's Cage, Policy version, Orphan guard and Proposer entries speak cage and schedule, and a Twin entry exists; the-whole-model.md is redrawn with no neck, no ledger, pins as crossing edges, tuppence and driftwood exploded. ADRs 0006, 0010, 0014, 0015 are not rewritten; tickets 09 and 10 own the superseding ADRs.
- [01 — Create feeds and insurer orgs](issues/01-create-feeds-and-insurer-orgs.md) — both orgs and both empty repos exist; Renovate installed on all repos in both (verified); Mend non-silent settings set by the owner, unverified.
- [05 — Research: Cedar for composition](issues/05-research-cedar-for-composition.md) — No-go: `symcc implies` really does decide strictly-stricter, but over 2 of the composed set's 6 members, and on the cage spec it only reproduces `cage_engine.py` Track 2. Its one real edge — catching a *conditional* widening Track 2 is blind to — is unreachable unless ticket 09 lets the tier floor be scoped; that is the trigger to revisit.
- [06 — Research: ESLint versioning semantics](issues/06-research-eslint-versioning-semantics.md) — copy ESLint's packaging model (every pack self-versions, a mashup is a new package, a severity-only override never touches the rule body, republish and inner-source are ordinary) but not its bump table, because ESLint's minor may break your build and answers that with `~` while ADR-0002 already pins everywhere; supersede, inner source and publisher-declared compatibility have no estate form at all, a regulator's baseline addition is a major nobody classifies, and the tier floor is the one thing ESLint never had to build.

- [07 — Org size obligations and currency](issues/07-org-size-obligations-and-currency.md) — the adopter signs `size` (turnover, customers, data subjects, headcount, `as_of`) and `obligations` (regime names) in its party artefact; `pct_of_global_turnover` gives `hi = min(rate × turnover, cap)` with the examples scaled by `hi / cap`; stale size widens to the cap, never refuses; every amount carries a currency, `reporting_currency` defaults to USD and the adopters declare GBP; FX is a signed `fx` feed; a missing regime price or FX rate is an instrument fault and refuses. Owner agreed; reason given only for the currency default. ADR-0020.

- [08 — The pound seam](issues/08-the-pound-seam.md) — the twin emits a forward-intel feed (a scenario under a perspective, no recommended action) from the adopter's repo; `fair.py` annualises it as a `source: twin` entry in `prices[]`; a versioned, signed `selection-policy` package picks the tier; appetite moves onto `party.yaml`; every price carries `perspective` and `currency`; `fair.py` reports `tail` and accepts a lognormal-GPD spec. Owner answered "Lgtm" with no reason; recorded as such; daily budget exceeded. ADR-0021.

- [09 — The cage ladder v2](issues/09-the-cage-ladder-v2.md) — the tier attaches to the governed Namespace manifest and `cage-tier` clobbers the pod label from `namespaceObject` (label is output only, H8-03 closes); the cage mutation is tighten-only in all served copies; the bottom rung is `isolated` (quarantine dials, no ingress, no egress, first eviction) and replaces Deny-to-issue; `overlay.floor` on `party.yaml` clamps selection and lowering is priced, never refused; only a `platform`-role party may declare `infra`, on its own Namespace manifests, landing before the unlabelled default flips to `isolated`. Ladder: baseline, restricted, quarantine, isolated, infra. Owner agreed without a reason; recorded as provisional. ADR-0022.
- [10 — Schedules and skills](issues/10-schedules-and-skills.md) — a clock consumes only reviewed grade-5 claim files; one daily `schedule:` floor on every unit, each org picks its time; the adopter's clock re-composes at today's date and proposes without committing; a clock may append observations to main but never a declaration, caged by ruleset and signed bot commits; a publisher fetch opens a PR only when the computed bump is not `none`, per-feed rule file; the rejection ledger is derived from closed PRs with a half-life. Owner agreed without a reason (provisional); D1, D2, D5 decided.
- [11 — An org twin each](issues/11-an-org-twin-each.md) — the twin overlay lives in the adopter's own repo with the world layer vendored and `twin` self-versioned by a signed tag; the floor is authored (workload, policy line, data as components, roles only, one priced edge, an `employer` perspective whose `currency` must equal `reporting_currency`); a subscribed feed becomes a signal by lookup on the clock; six standing scenarios per adopter with two new classes; one `verify-twin-evals.sh` in the gate, `truth.log` the record. Owner agreed without a reason; provisional. C4, C5, C13, C14, C19 applied.
- [12 — Identity as spine](issues/12-identity-as-spine.md) — one trust domain per cluster-running party, federated pairwise, `trust_domain`/`bundle_endpoint`/`federates_with[]` signed on `party.yaml`; SVID path carries platform version plus cage tier, rendered by 09's `cage-tier`; a serving org declares its caller demand in its own composed artefact against a pinned `party` feed, failed reach priced as a twin entry; five actor classes, two issuers (SPIRE, GitHub Actions OIDC), twin agent is the twin schedule's workflow subject, Dex retired; substrate ships as one platform `implementations` package. Owner: "can't find fault with a single one"; provisional. Two ADRs.
- [13 — Lift or retire the original mechanisms](issues/13-lift-or-retire-the-original-mechanisms.md) — ledger, storefront and reports lift into tuppence, driftwood and ludlow by re-label, re-pin and renovate.json; original repos are archived one by one after their replacement grades green, fleet last, hub stays live; the cloud plane lands in tuppence after the Pod slice runs; the handbook is a compose-time render under the artefact's tag; supersede is publisher-side only, priced by the EOL ramp (D5, decided); currency-controller retired. Q1-Q4 provisional on a bare agree; round 2 pending.
- [14 — Insurance and the insurer party](issues/14-insurance-and-the-insurer-party.md) — `appetite` gains annual-aggregate `attachment`, `limit` and `exclusions` keyed on regimes and `(source, id)`; the adopter's composed artefact publishes an `exposure` aggregate; the quote is a per-adopter feed (`quote-<adopter>`) with `priced_against`, validity and `conditions`; the premium is a cost line under the adopter's perspective; the insurer repo pins platform and the exposure and prices on a clock, human tags. Owner agreed without a reason; provisional. Extends ADR-0019/0021.
- [15 — Price everything that was counted](issues/15-price-everything-that-was-counted.md) — regulator-published weights keyed `(source, id)` price each hole as a partition of the regime exposure; the price lands on the `prices[]` entry so holes move the tier and the three refusals go; an ungoverned namespace is a ramped workload share of the residual; an unpriced register entry takes its scenario's selected tier; a bespoke control is an adopter-published `controls` catalogue priced by its own scenario. Owner agreed without fault-finding; provisional. D5 and C1, C9-C11, C17, C18 applied.
- [16 — Flux rescoped and verified at the cluster](issues/16-flux-rescoped-and-verified-at-the-cluster.md) — one sample records five facts (Ready at the pinned pair from the real remote, signature verified, `lastAppliedRevision` equal, rendered objects byte-equal and Flux-owned); three falsifiers pre-registered; a scheduled workflow in the adopter's repo samples an ephemeral KinD and appends an observation under a caged lane (D1); cluster-side verification is an identity-pinned gitsign-verifying controller, the SSH bridge rejected (D3); the ResourceSet ranges the adopter's composed tag with platform and nist kept as verified sources; ticket 20 step 4 cites only the CI number (D4). Q1, Q2, Q3, Q5 provisional on a bare agree; Q4 decided.
- [18 — The publisher release under cages](issues/18-the-publisher-release-under-cages.md) — a degraded publish is a prerelease suffix on the declared number with `tier: quarantine` on the array element (narrow note on ADR-0011); the adopter prices it as a hole and compose skips it unless pinned; platform gets a signed `party.yaml` and prices moves under its own perspective, evidence only; the adopter fills the matrix with the published `computed-semver` package; the bump is a field on the array element, `bump.yaml` for ico and nist. Owner: "can't find fault", provisional; D3, C1, C8 decided.
- [19 — Misuse and portability](issues/19-misuse-and-portability.md) — publisher reliability is a feed from a scorer party and a low score widens the adopter's triple to the publisher's `widen_to`; a mispriced regulator is disclosed and a stale pin is priced by the EOL ramp (D5); exposure is public by design and "a rival reads my holes" is a priced twin scenario; switching cost is computed by dropping each publisher's edges, annualised as `kind: switching`; the composed tree vendors every priced payload and converter, re-derived by blob id. Owner agreed without a reason; D5 decided.
- [20 — One demo of the eco system](issues/20-one-demo-of-the-eco-system.md) — a generator in `talk/` emits `talk/deck.md` as Marp from per-script captures the gate writes under `talk/captures/` as caged observations; the deck is built only from the scheduled offline CI run, step 4 could-not-look until 16 Q3; all seven steps rendered from day one with a distinct "no check yet" status; `verify-demo.sh` checks captures, grades, figures, order and four phrases; mp4 becomes a release asset, audio dropped; niobium never narrated as feed content. Q2 decided (D4); rest provisional on a bare agree.
- [22 — The prediction-market feed](issues/22-the-prediction-market-feed.md) — `kind: feed`, `name: market-moves`: universe is a versioned, signed, mechanical rule file (benchmark-rule shape) in the feeds repo; Polymarket only in v1 with `venue` on every observation; payload is dated series only (`market_id`, `venue`, `question`, `resolution_source`, `observations[{date, price_level}]`), no moves, no probability field; the skill is the twin's `signal-classify` body; daily LLM-free fetch appends to an observation branch and opens the publisher PR under ticket 10's one rule (D2). Owner agreed without a reason except D2; recorded as such.
- [23 — The news feed and the headline skill](issues/23-the-news-feed-and-the-headline-skill.md) — the news feed carries observed entries only (`id, date, source, statement, provenance{url}`, no STEEP); niobium lives in the twin's scenario library, never in the feed; the headline skill is signal-classify plus evolution-judge run by a human, landing a grade-5 binding and an attributable override as one PR on the adopter's overlay; only the override or a regrade is price-eligible; forward-intel gains `claim_scope` and `derived_from`. Owner agreed without fault found; recorded provisional. Ticket 25 amends ADR-0021.
- [24 — Size beyond turnover](issues/24-size-beyond-turnover.md) — HIPAA prices per individual per provision (`provisions` publisher-shipped, default 1); FCA prices `rate × relevant_revenue` (optional fact, defaults to turnover) with a publisher-shipped `widen_to` for stale size; PCI stays size-blind; every `prices[]` entry gains `per_customer`; each publisher ships its own converter and composition passes `size`; fx is HMRC monthly under ticket 10's one fetch rule (D2). Owner agreed without a reason; recorded provisional except D2.
- [61 — Renovate completes step 2 once, for real](issues/61-renovate-completes-step-2-once-for-real.md) — the inherits[] customManagers and a postUpgradeTasks completer land on driftwood; feeds cuts threat-register/v2.0.0; Renovate raises the bump with party.yaml and composed/ in one bot commit and the owner merges it (PR #20, 27f1cf2), firing propose-tier for real; exactly one Renovate acts per repo now (hosted Mend app disabled, self-hosted force-enabled); graded by verify-renovate-merged-feed-pr, citable on the next TRUTH run.
- [58 — Grilling: the four architectural gaps and the untagged pin](issues/58-grilling-the-four-architectural-gaps-and-the-untagged-p.md) — five decisions, all provisional on a bare "Agree": the isolated flip is the second declared line (5.0.0) and re-carries root-if-attested; driftwood becomes the federation peer; the lane stays public and is enforced detectively with ADR-0023 amended; an untagged pin is a priced hole. Graduated: 63 updated, 68, 69, 70.
- [60 — The scheduled observations land in the citable number, and steps 3–4 happen once for real](issues/60-the-scheduled-observations-land-in-the-citable-number-a.md) — the gate converts: step 4 and the three verify-reconcile checks grade from real, signed lane samples on TRUTH run 20 (2026-09-01T21:07Z, 57/7/18 of 84); first-ever all-five-facts-true observation (nist and platform on driftwood's sample); all ten first clock firings watched (~5.5h cron delay); reds owned by tickets 72 (twin re-render), 73 (verifier cert skew) and 62 (deleted thin-slice refs); step 3's first real merge graduates to ticket 74; ticket 40 corrected. M7 closed; M9 moves to 74.

### Built 2026-08-29 — the thin slice runs, and the gate is green

The `/implement` run of 2026-08-28 to 29 built the slice in five phases, each phase a workflow of
builders, one integrator, adversarial reviewers, a fixer and a committer. Fifteen tickets resolved:
21, 25, 26, 28, 29, 32, 36, 40, 41, 42, 43, 47, 49, 50 and 52. Each ticket's `## Answer` records
what was built and which check in the gate proves it.

The truth surface went from 40 pass, 16 fail of 56 to 65 pass, 0 fail, 16 could-not-look of 83.
Every could-not-look names what it waits for. Nothing is red.

> **Correction, 2026-08-31 (ambition review).** The 65/0/16 figure was a local rehearsal. No TRUTH
> line records it, and the paragraph above broke the never-cite-a-rehearsal rule below it. The
> newest citable line is `TRUTH 2026-08-31T17:22Z run=13 hub=eba3569 pass=53 fail=7 skip=21
> excluded=2 total=83`. Seven checks are red and the review found five of them are unowned
> instrument faults. See [REVIEW-2026-08-31.md](REVIEW-2026-08-31.md).

Decisions the build had to take, each recorded in its ticket:

- **Policy versions 2.0.0, 2.0.1 and 3.0.0 are retired, not patched.** They could never admit a
  pod. A backport was built and then withdrawn: teaching an old line to read the Namespace tier is
  ADR-0022, which the engine computes as major, so it cannot ride on a patch, and the patched lines
  let a pod pick its own cage. Retirement is the estate's own mechanism and the only honest repair.
- **The cage writes three priority fields, not one.** The Priority admission plugin re-derives
  `priority` and `preemptionPolicy` from the mutated class and refuses if either disagrees.
- **A hand-taken sample is a rehearsal and is never cited.** The five-fact grader refuses any
  sample whose run id, committing identity or signature does not come from the observation lane.

What the owner must do before more can be true: merge the branches and let each `cut-release.yml`
cut its signed tags. Several checks read could-not-look by name until those tags exist. A signature
cannot be made on this machine, and no build faked one.

### Reviewed 2026-08-31 — everything graded against the ambition

An ultracode review (six auditors, one adversarial skeptic per finding, 55 agents) graded the
estate against NORTH-STAR §2 to §7: 38 shortfalls confirmed, 10 claims refuted. Full record:
[REVIEW-2026-08-31.md](REVIEW-2026-08-31.md). The one critical: the gate's kyverno 1.19.0 pin was a URL
fix, not a version decision; under it the cage-tier CEL does not compile, three of run 13's seven
reds follow from it, and the citable gate has never once been green. The honest headline stands
beside it: the signature spine, the £ seam, the hub clock and the honesty machinery are real and
proven.

**Worked 2026-08-31.** Ticket 54 is resolved: the gate's kyverno pin was an accident, and the
estate is authored against 1.18.2, so the gate now pins 1.18.2 and cosign by version and checksum,
installs jsonschema, and allows 900s. Ticket 55's four repairs are built and proved against the CI
runner's own OpenSSL 3.0.13 but sit on a local branch: `enact_guard` refused the push to platform,
correctly, and the owner pushes. Ticket 71 graduates the real kyverno question (the composed 4.0.0
does not load on a 1.19 cluster). Ticket 58 is resolved provisional; tickets 68, 69, 70 graduated.

Tickets [54](issues/54-the-gate-observes-with-the-estate-s-own-toolchain.md) to
[67](issues/67-the-record-matches-the-surface.md) chart the remediation. Order of attack:
54 (the gate can go green) → 55 (every red real or explained) → 57 (feeds/insurer runnable) →
61 (step 2 by Renovate once) → 60 (steps 3–4 observed on the clock) → 56 (the surface sees its
clocks) → 58 (owner decides the four architectural gaps and the untagged pin) → 62, 63 →
59, 64, 65, 66, 67. Dated update comments were appended to tickets 53, 17, 38, 48, 20 and 37;
53 is repaired in code and ready to close, 38 and 48 are unblocked and ready to run.

### Reviewed 2026-09-02 — fit for which purpose

A second ultracode review (407 agents: 13 readers, 13 auditors, three skeptics per finding, four
critics) graded everything against the thesis and NORTH-STAR §2 to §7. Record:
[REVIEW-2026-09-02.md](REVIEW-2026-09-02.md); evidence under `review-2026-09-02/evidence/`.
88 findings survived adversarial verification, 35 were refuted, and they cluster into twelve root
causes. The verdict: nearly fit as a touring talk and fit as a research artefact; not fit against
§4 as a definition of done; not close for adoption by a fourth organisation. The record never
states which purpose counts.

The three findings the 2026-08-31 review missed and that decide the demonstration:

- **The £ inputs are editorial and two anchor fines are legally stale.** Frequency, the reduction
  table, the threat magnitudes and the control weights are authored constants. Doorstep
  Dispensaree is £92,000 (not £275,000) and Clearview AI has never been collected. Corrected,
  driftwood's largest line falls 63 percent and the insurer's premium 44 percent. All three
  adopters sit at `isolated` on their own signed numbers; two fit no rung at all.
- **Step 3 has never fired, and when it fires it will loosen the cage.** The proposer has no
  tighten-only clamp and fires per price line. Ticket 74 is blocked by ticket 78.
- **The cage has never been graded on a citable run.** The clock creates no cluster; twelve of
  eighteen skips name a cluster the runner never has.

Charted: [75](issues/75-grilling-what-is-this-for-the-twelve-questions.md) (prepared, the twelve
questions about the underlying goals; tickets 79, 84, 86, 87 and part of 63 wait on it), 76 to 87.
Order of attack for work that needs no decision: 76 → 78 → 81 → 85 → 77 (with 62) → 80 (with 67)
→ 82 → 83. Dated comments were appended to 74, 73, 62, 64, 63, 67, 13, 66, 59, 56, 57, 72, 71
and 35. Ticket 57 is ready to close on its registration and tags.

Process note. GAPS rule 1, "no recommendation attached to an architectural question", was
dropped when the rules were copied into this map. Ticket 75 states each trade first and the
assistant's call after it, labelled as such. Ticket 80 restores or retires the rule with a reason.

## Not yet specified

- After the 2026-09-02 review, the fog that waits on ticket 75:
- A shared, pinned adopter package instead of three divergent forks (Q7); a fourth adopter.
- A twin that derives a probability from a signal, if Q10 says it must; the eleven real firms' and four named executives' place in a public corpus.
- £ beats on the deck, so a non-engineer learns that a control, a cage tier and an insurance transfer are comparable; the estate's own running cost on driftwood's balance sheet.
- A supported-engine-version matrix per published policy line (ticket 71's widening).
- The thin slice is built (2026-08-29 section above). What remains dim:
- Placement of the scanner, notification spine and OSCAL CronJob after ticket 35 decides lift-or-retire for them. The currency controller is retired (ticket 13).
- The eco-system re-cut of the affected-parties register and DPIA, once ticket 44 grades the misuse catalogue.
- Per-workload de-posture inside a Namespace tier, if an adopter ever needs it (ticket 27 decides the de-posture move first).
- A `v1beta1` move for the 72 Kyverno `v1alpha1` policies. Housekeeping, not on the route, until a Kyverno upgrade forces it.

## Out of scope

- The video as the deliverable or the clock. The demo is a read of the truth surface (NORTH-STAR §6).
- A power layer beyond portability-as-a-priced-cage.
- Covert sensing; real surveillance data (permanently excluded).
- Rewriting history in place. Superseded documents get banners.
- Reopening the 114 re-ratified decisions.
