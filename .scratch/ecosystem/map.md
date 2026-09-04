# Map — the eco-system, operating

Label: `wayfinder:map`. Charted 2026-08-28. Supersedes the nine earlier efforts under `.scratch/` as the single map for what comes next. Their maps and tickets stay as the record.

## Destination

Every joint in [NORTH-STAR.md](../drift-review-2026-08-27/NORTH-STAR.md) §4 (regulator publishes; Renovate pins; the £ crosses a band and a proposal PR opens; Flux reconciles the cage; the twin plays a signal forward; provenance; honesty) has an owning ticket the truth surface can grade, and the eco-system has run end to end once, on a clock, with driftwood, tuppence and ludlow consuming. Then hand off to `/to-spec`. This map carries execution: tickets build, not only decide.

## Notes

- The north star is ratified. The owner's answers to 41 re-grills and 22 reversals are binding: [REGRILL-ANSWERS.md](../drift-review-2026-08-27/REGRILL-ANSWERS.md). The ranked gaps are [GAPS.md](../drift-review-2026-08-27/GAPS.md).
- Build order: the seven steps in NORTH-STAR §4, thinnest slice end to end first (one regulator, one adopter, one feed, one cage move, one twin forecast, all real), before widening. The truth surface is built in parallel because it grades the slice.
- Purpose (ticket 75, 2026-09-02, the owner's chain): a touring talk that proves the corrected thesis as running code, leading to a reference implementation ControlPlane lifts into client work, which makes adoption by a fourth organisation available because the estate is open source, underwritten by the written, checkable argument. No date: "when we've got something good, we'll tour it". The talk is a byproduct and a marketing tool; the running estate is the deliverable. NORTH-STAR §4 is the assistant's build order; done is fitness for the talk as the truth surface defines green (ticket 75 Q8).
- Vocabulary: there is no gate, in the owner's words (ticket 75 Q5): a mutating admission controller more than a validating one; a workload can be unable to run only because it does not fit the cage, never because it is deliberately denied. Everything is caged; the spec of the cage is the only variable; the £ picks the spec; the bottom rung is "too expensive to run or not functional". Never an exemption, never an exemption ledger. Price and cage; never count, refuse, deny or file.
- Versioning follows ESLint shareable configs: every package its own semver; a composed set is a new package; republish and inner-source are normal.
- Schedules run the LLM-free data gathering. Reasoning is packaged as Claude Code skills a human runs over the gathered results. The reviewed PR is the unit of adoption.
- Process rules (from the drift review, amended by ticket 75 Q11 and ADR-0025 on 2026-09-02): the assistant decides architecture and records each decision with its reason; the owner's reasoned answer overrides; a bare letter or "yes" from the owner is a delegation and is recorded as the assistant's decision, labelled delegated; the word "provisional" retires; mid-run, the assistant decides, records and continues. Only purpose, dates, identities, money, authorisations and anything naming a real person go to the owner, at most five per day, none inside an implementation run. Done is defined by the truth surface, never by the demo; every ticket's definition of done includes wiring its check into the gate.
- Skills to consult: `/mattpocock-skills:grilling` and `domain-modeling` for every grilling ticket; `/mattpocock-skills:research` for research tickets; `/arckit:wardley` and `/arckit:impact` for the twin; CONTEXT.md and docs/adr/ before any work.
- Batch record, 2026-08-28: the owner read all 14 held rounds and wrote "ive already read the recommendations and I can't find fault with a single one". Every accepted recommendation is recorded as provisional with that line. Five cross-ticket conflicts went to the owner with a three-lens panel verdict; the owner wrote "I agree with you're more advanced reasoning"; those five are decided (D1 to D5 in each ticket's Answer, ADR-0023). The five-per-day rule was overridden by the owner's instruction for this batch. Held rounds stay in each ticket above the Answer as the record of what was recommended.
- A `Status: prepared` ticket holds a drafted HITL round the owner has not answered. See `docs/agents/issue-tracker.md`.
- Identity is designed and shelved for this build (ticket 75 Q12 amends charting Q2): every artefact is attestable; the actor half waits for an identity lane after this map. The feeds and insurer parties are real orgs the owner creates (charting Q4).
- Merging, development window (ticket 75 Q6, Q14): the owner authors and pushes; the assistant reviews and merges as a second machine identity once ticket 88 creates it; the guard's `operations` mode stands until then. The narrative says a human merges; AI disposal is the recorded end state.
- The twin's model call runs inside Claude Code on the owner's machine, on a local clock (ticket 92), because no tokens exist elsewhere (ticket 75 Q10).

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
- [75 — Grilling: what is this for, the twelve questions](issues/75-grilling-what-is-this-for-the-twelve-questions.md) — sixteen decisions, each labelled owner-reasoned, owner-instructed or delegated: the purpose is a chain (talk → reference implementation → adoption available because open source, underwritten by the written argument), no date; §4 is the assistant's build order; at least three coexisting versions binds in the owner's 2022 words; the £ is an ordinal instrument, said on the artefact; there is no gate, in the owner's words (mutating, never a deliberate deny); a human merges binds, with a second identity as development-window theatre; the adopters are plausible firms, based on studied real firms where needed; green is the offline half plus the lane facts with the ceiling published; the talk is a byproduct and marketing tool; the twin derives a probability with a model run locally; the assistant decides and records (ADR-0025); identity is shelved for this build; the currency controller is un-retired. Graduated 88 to 95; ticket 68 ruled out of scope.
- [88 — The second identity](issues/88-the-second-identity.md) — the GitHub App `pavc-other-hand` (App ID 4819564, owner-named) is installed on all nine estate orgs; `twin/other_hand.py` mints its tokens from a key outside every repo; the guard gains a third mode `other-hand`, now checked in, that keeps every refusal and admits one shape, a merge whose disposing shell segment mints the app's token inline; PR #2, authored by the owner, was approved and merged by `pavc-other-hand[bot]` (c1c87fd). Tickets 87 and 74 are unblocked.
- [94 — Research: the studied firms behind the adopters](issues/94-research-the-studied-firms-behind-the-adopters.md) — one candidate per adopter from primary sources: driftwood → DSG Retail (ICO £500,000 notice of 2020, still in litigation after the Court of Appeal 2026-02-19, no collected figure); tuppence → Starling Bank (FCA Final Notice £28,959,426, 2024-09-27, final and collected, with a board-approved risk appetite); ludlow → Anthem (three final settlements on the 2015 breach of 78.8m people). No bare turnover swap makes a priced rung reachable; the regulator record as a share of turnover spans three orders of magnitude across the three, which ticket 79 must weigh. Findings: [research/94-studied-firms.md](research/94-studied-firms.md). Ticket 79 chooses.
- [95 — The record states the purpose](issues/95-the-record-states-the-purpose.md) — NORTH-STAR gains §0 (the owner's purpose chain, the toured circuit as the audience, no date, done defined by §4's preamble, the licence and the truth surface as consequences); §4 is re-headed as the assistant's build order with the definition of done under Q8 (b) and a dated standing line for the steps; principle 2 carries the owner's Q5 words verbatim; §6 records the talk as byproduct and marketing tool (2026-07-23 superseded, line re-attributed), the development-window theatre with `pavc-other-hand` and AI disposal as the end state, and identity shelved; §8 lists the sixteen decisions by number with status and date. CONTEXT.md's Cage and Multi-version entries already agree. `verify/record/verify-record-states-the-purpose.sh` greps all of it, requires a date on every owner attribution, and self-checks.
- [60 — The scheduled observations land in the citable number, and steps 3–4 happen once for real](issues/60-the-scheduled-observations-land-in-the-citable-number-a.md) — the gate converts: step 4 and the three verify-reconcile checks grade from real, signed lane samples on TRUTH run 20 (2026-09-01T21:07Z, 57/7/18 of 84); first-ever all-five-facts-true observation (nist and platform on driftwood's sample); all ten first clock firings watched (~5.5h cron delay); reds owned by tickets 72 (twin re-render), 73 (verifier cert skew) and 62 (deleted thin-slice refs); step 3's first real merge graduates to ticket 74; ticket 40 corrected. M7 closed; M9 moves to 74.
- [57 — feeds and insurer become runnable: workflows registered, first signed tags cut](issues/57-feeds-and-insurer-become-runnable-workflows-registered.md) — feeds and insurer runnable: default branches `main`, six workflows active, signed tags feeds threat-register/v1.0.0 (and v2.0.0 via 61) and insurer v1.0.0 verified by identity-pinned gitsign, daily fetch crons firing since 2026-09-01, three adopter feed-contract SKIPs converted to PASS on TRUTH runs 21 and 22; clock reds owned by 85 (feeds `__pycache__` in cage) and 77 (insurer pin lacks exposure); other five feeds untagged until an adopter pins one (delegated).
- [55 — Every red on the clock is real, explained, and finishable](issues/55-every-red-on-the-clock-is-real-explained-and-finishable.md) — PR #8 merged as platform 46cd775 on 2026-09-01; run 22 grades corpus-generator PASS, render-version-tree PASS, publisher-gate and source-verification SKIP with the reason named; the patch file is deleted.
- [66 — The deck check grades the run its own TRUTH line names](issues/66-the-deck-check-grades-the-run-its-own-truth-line-names.md) — the deck names the recorded run it describes and verify-demo grades it against that run's committed captures, everywhere; the lane is unchanged, lag is a note, the widened-lane alternative is the owner's to reopen (ADR-0024 note).
- [81 — Round 3 of the sampler wait-order lands on tuppence and ludlow](issues/81-round-3-of-the-sampler-wait-order-lands.md) — round 3 of the sampler wait order cherry-picked onto today's main in all three adopters, patches regenerated, the order graded by verify-sampler-wait-order.sh (red until merged), push and merge held for the owner.
- [73 — The verifier rejects a tag whose certificate postdates its tagger time](issues/73-the-verifier-rejects-a-tag-whose-cert-postdates-its-tagger-time.md) — the source verifier chains at max(tagger time, notBefore) within a declared 60s
- [17 — Twin follow ups from the aug 05 itemisation](issues/17-twin-follow-ups-from-the-aug-05-itemisation.md) — the 66/65 split is overtaken and closed with a dated note (Flux verdict settled unmeasured from 2026-08-16); twin build 65 reads `CLOSED UNMEASURED`, 66 reads `Blocked by: none` and `PR CHANNEL IS THE ESTATE'S`, the constitution carries a dated correction; spec story 2 is owned by twin build ticket 01 (`store_rebuildable_from_git` is its test, run green); P010 marked rejected and P012/P034 (and P013/P035 of P011, P042 of P037) annotated as duplicate captures, nothing deleted, 206 distinct of 211 by a stated method; no verify script, record-keeping only.
- [53 — cut-release.yml pushes the tag but never the branch, so signed evidence never reaches main](issues/53-the-release-pushes-tags-but-not-the-branch.md) — owner-instructed 2026-08-31 (platform `b83eba1`): the branch goes in the same atomic push as the tags, never by PR; orphaned signed commits stay unreachable, the release bot re-committed the evidence (`533dccb`), `v2.0.1` carries every bundle and all three adopters pin it; graded by the hub's `verify-release-evidence-reaches-main.sh` (outcome, green now) and platform `verify-cut-release-tags.sh` case 8 (mechanism, waits on the owner's push); ADR-0011 dated note; ticket 54 owns the CEL/toolchain reds.
- [82 — Licence, attribution and disclaimers](issues/82-licence-attribution-and-disclaimers.md) — built: hub LICENSE Apache-2.0, nist NOTICE from its manifests, one demonstration line on all 8 party.yaml (comment) and READMEs, DISCLAIMER.md on ico and nist, verify/disclaimer/ grades it; named-individuals ruling drafted, waits on the owner.
- [44 — Eco-system misuse catalogue graded by the gate](issues/44-eco-system-misuse-catalogue-graded-by-the-gate.md) — third misuse catalogue (four eco-system rows, ticket 19's mechanisms, anchored by path or by the open ticket building the price) loaded by the one loader, harness check `misuse_catalogues_load_and_every_row_names_a_mechanism`, `verify/misuse/verify-misuse.sh` in the gate: PASS, 2 rows resolve, 2 could-not-look by name (45/46, 84/46); the affected-parties re-cut (open item above) can start.
- [72 — A feed bump re-renders the twin's derived artefacts](issues/72-a-feed-bump-re-renders-the-twin-s-derived-artefacts.md) — built 2026-09-03 — a feed bump re-derives feed.json and signals.yaml in the bump commit (completer + widened fileFilters); twin-sweep's moved branch, dead under bash -e since written, now runs, proposes both files and appends moved=true observations; verify-twin-sweep-moved.sh could-not-look until it fires live; driftwood branch waits on the owner's push, the bump-commit TRUTH run on the next feed tag.
- [70 — The observation lane is detectively enforced and honestly recorded](issues/70-the-observation-lane-is-detectively-enforced-and-honest.md) — the lane is detective -- `verify-lane.sh` walks every observation ref's first-parent history and reds a scheduled-identity commit outside the lane or a clock's merge; ADR-0023 amended (no push ruleset on a public repository, revisit on going private); ticket 28's "caged" claim corrected.
- [65 — enact_guard closes the --git-dir family](issues/65-enact-guard-closes-the-git-dir-family.md) — enact_guard closes the `--git-dir`/`GIT_DIR` family (M17): every pushing segment
- [38 — Priced holes in composition](issues/38-priced-holes-in-composition.md) — the three refusals (new hole, baseline widening, new ungoverned namespace) become priced `deltas[]` of five kinds keyed `(source, id)` under the adopter's perspective and currency; an ungoverned namespace is a ramped workload share of the residual, bounded; a bespoke control prices by its own scenario or refuses as a missing instrument; `verify/priced-holes` grades it (SKIP on the real estate until the owner re-composes the adopters); removed-control stays a refusal for ticket 39's ADR to settle. D1 to D12 delegated.
- [92 — The local clock](issues/92-the-local-clock.md) — the local clock: `talk/local-clock.sh` runs the model steps from the owner's machine as `claude -p "/<skill> <adopter>"` under the guard, lands a branch + PR body (owner pushes), `--inject` rehearsals are marked `injected: true` and refused everywhere citable; `verify-local-clock.sh` grades the marker; headless runs write no override; ADR-0024 point 6.
- [39 — Supersede ADR-0013, ADR-0017 and ADR-0018 point 3](issues/39-supersede-adr-0013-adr-0017-and-adr-0018-point-3.md) — ADR-0026 records that a hole is priced, never refused, and the claim keys on (source, id); dated banners on ADR-0013, ADR-0017 and ADR-0018 point 3; CONTEXT.md agrees; removal is priced as a removed-control delta (the platform build named in Consequences); every refusal kind composition emits is classified; verify/adr-supersession grades the record offline
- [69 — An untagged pin is a priced hole](issues/69-an-untagged-pin-is-a-priced-hole.md) — An untagged feed pin composes as a priced hole of its own premium and is graded live against the publisher's real remote — 7 of 7 estate pins signed, so the rule runs on a fixture and a scratch estate, not on a live hole.
- [76 — Every green rests on an observation](issues/76-every-green-rests-on-an-observation.md) — every green rests on an observation — a missing instrument now exits 3 in fourteen
- [78 — The proposer can only tighten, the enacted tier is bound to the priced tier, and the proposal is signed](issues/78-the-proposer-can-only-tighten.md) — the proposer folds the whole party to its strictest priced line, clamps to overlay.floor, reads the declaration off the governed Namespace and lands nothing looser; two governed Namespace documents is an ambiguity it refuses; the proposal is gitsign-signed; a binding check in each adopter's shift-left and a hub estate walk grade the enacted tier against the priced one (ADR-0022 note)
- [83 — The TRUTH line says what it measured](issues/83-the-truth-line-says-what-it-measured.md) — The TRUTH line carries the split by class and the ceiling; an undeclared could-not-look
- [90 — Identity is shelved for this build](issues/90-identity-is-shelved-for-this-build.md) — Identity is shelved and the record says so — §1 claims the artefact half, principle 6
- [63 — The unlabelled default flips to isolated](issues/63-the-unlabelled-default-flips-to-isolated.md) — the unlabelled default is `isolated` in graded and in the new 5.0.0 line; the check that
- [56 — The citable run can see whether the clocks ran](issues/56-the-citable-run-can-see-whether-the-clocks-ran.md) — truth.yml's `clocks` job holds `actions: read` and hands the gate a facts-only clock verdict file, so "did each clock run inside its period" grades on the citable run with no credential in the job that runs eight orgs' scripts; a cancelled run is no longer excused, and the three D2 SKIPs become PASSes with a named limit.
- [85 — Every clock is green, or red for an estate reason](issues/85-every-clock-is-green-or-red-for-an-estate-reason.md) — the two unowned red clocks are fixed at the source (feeds' cage read the `__pycache__` its own python wrote; nist's reader globbed a feed envelope at a controls catalogue and wrote null every day), the fix is shared verbatim with insurer and nist, and every red clock now names the open ticket that owns it in the gate's own output.

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

**Worked 2026-09-02, ticket 75.** The owner answered all thirteen questions and three follow-ups
in two rounds, in chat. The Medium post was read through the owner's browser and "at least three"
is the owner's phrase. Tickets 88 to 95 are graduated: 88 (the second identity, HITL, blocks 87
and 74), 89 (Deny is not a rung), 90 (identity shelved), 91 (currency controller un-retired), 92
(the local clock), 93 (the twin derives a probability, blocked by 92), 94 (research: the studied
firms), 95 (the record states the purpose). Ticket 68 is closed out of scope. Order of attack now:
95 → 76 → 78 → 81 → 85 → 89 → 77 (with 62) → 79 (after 94) → 80 (with 67) → 90 → 91 → 83 → 84 →
86 → 92 → 93 → 82. Ticket 88 waits on the owner and gates 87 and 74.

**Worked 2026-09-03, ticket 88.** The owner registered nothing by hand: the app was created,
keyed and installed through the owner's browser with the owner confirming sudo mode, the name and
the one download in chat. The guard's mode is `other-hand`, not `development`. Ticket 87 (the
ruleset) and ticket 74 (step 3 for real) are unblocked.

## Not yet specified

- After ticket 75 (2026-09-02):
- The identity lane that grades the actor half of attestation, and a federation peer with it. First thing after this map (ticket 75 Q12).
- A shared, pinned adopter package instead of three forks, once a real divergence shows what the package must hold (ticket 75 Q7).
- The eleven real firms' and four named executives' place in a public corpus, once ticket 94 shows which studied firms the adopters rest on and ticket 82 rules on named individuals.
- £ beats on the deck, so a non-engineer learns that a control, a cage tier and an insurance transfer are comparable; the estate's own running cost on driftwood's balance sheet. Rebuilt from the truth surface when the estate is fit (Q9, Q16).
- Which ordinal-arithmetic and grade-5 rulings ticket 93's derivation must reopen.
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
- A fourth adopter, and onboarding for one. Purpose (c) is "available because open source", not a demonstrated adoption (ticket 75 Q1, Q7).
- [68 — Federation gets its peer](issues/68-federation-gets-its-peer.md): closed 2026-09-02. Identity is shelved for this build (ticket 75 Q12); a peer returns with the identity lane as a fresh effort.
- A date or venue for the talk. None exists; none is invented (ticket 75 Q15).
