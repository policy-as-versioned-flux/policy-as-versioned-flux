# H12: ADRs, glossary, north star, README and docs/*.md

FRESH = `scratchpad/fresh/hub` (cloned 2026-11-14). All cites are `hub/<path>:<line>` unless another repo is named.

## Summary (8 lines)

1. 55 files, 7,830 lines (`wc -l`): 37 ADRs 4,646; CONTEXT.md 958; NORTH-STAR.md 143; README.md 44; 15 docs/*.md 2,039. **All of it is records. None of it runs.** Do not sum "kernel lines" from this area. Status is `unknown` throughout unless noted.
2. Only about 6 ADRs carry the loop's core decisions: 0015 (proposer), 0021 (pound seam), 0022 (cage ladder), 0024 (daily clock), 0026 (hole priced) and 0035 (CVE priced from the adopter's own scan). Together they are about 1,390 lines, much of it later amendments. The other 31 are thesis transport, versioning, composition, engine, evidence, governance-of-the-build, or model and agent questions.
3. The June PRD, README and HISTORY contain no money vocabulary at all (`grep -ci '£|appetite|exposure|financial'` = 0). The £ loop enters the record from 2026-07-23 (see maps/A1-owner-words.md:13), and the ADRs record it only from ADR-0020/0021/0022 (2026-08-28).
4. The glossary has 120 term entries plus 10 posture decisions and 5 slide-lint rows. About 24 of the entries are needed to follow the loop. The loop terms are the shortest: Appetite 6 lines, Price 7, Exposure 5, Selection policy 3. The longest entries are all machinery: Currency controller 42, Governed namespace 39, Orphan guard 34, Twin 30.
5. **Compare, ratchet and react have no glossary term.** "Ratchet" appears in the ADRs only as a *rejected option*, twice (ADR-0015:68, ADR-0026:187). No entry or ADR compares aggregate Exposure with Appetite. The comparison the record describes is per price line, followed by a strictest-line fold (ADR-0022:141).
6. Of the 37 ADRs, 26 are recorded as assistant decisions (delegated under ADR-0025 or written as such). 9 June-July ADRs carry no attribution. Only ADR-0025 is owner-instructed ("ask fable to decide then record", ADR-0025:19). Owner reasons appear inside notes on ADR-0008, 0014, 0022 and 0024.
7. I found 18 contradictions between ADRs, the glossary, NORTH-STAR and README (listed below). The ones that matter for the loop: the proposer's direction (0015 against 0022), what is compared (glossary Appetite against 0022), and whether the twin's price reaches the tier at all (0021 against 0031).
8. Deviation from the 30-component cap: the area brief asks for one component per ADR, so there are 37 ADR components plus 9 glossary and 6 docs groups (52 in all). ADR-0034 never existed: no commit in `git log --all` touches `docs/adr/0034*`.

## Components

Lines are from `wc -l`. Born dates are from `git log --diff-filter=A --format=%ad --date=short -- <path> | tail -1`. Every status is `unknown` (these are documents) unless a cite says otherwise. Origin legend: assistant/deleg = the assistant decided it under ADR-0025, or recorded it as its own; unknown = no attribution found.

### ADRs (one per ADR; 4,646 lines)

| # | name | path | lines | born | what it decides | loop role | necessity | still needed if reduced to the loop? | origin | cite |
|---|---|---|---|---|---|---|---|---|---|---|
| 0001 | Signed git tags, gitsign | docs/adr/0001-* | 70 | 2026-06-06 | Policy ships as keyless-signed git tags, pinned by tag and commit; verification in CI | evidence | support | Partly: a pinned version is needed to enact; signing is about trust | unknown (June; PRD header "CNS with Claude", docs/PRD.md:6) | 0001:7-11, 28-33 |
| 0002 | Pin + Renovate PR | 0002-* | 39 | 06-06 | Exact pins everywhere, bumped only by a reviewed Renovate PR | enact | support | Yes in spirit: a reviewed change is how a notch lands | unknown | 0002:7-13 |
| 0003 | Kyverno CEL policies | 0003-* | 67 | 06-06 | Kyverno as engine, CEL policy bodies; amended by 0033 | cage | kernel (some admission engine is needed) | Yes: the cage needs an engine. The specific version mechanics are not needed | unknown; amendment delegated | 0003:5-29, 36-38 |
| 0004 | Cloud plane by harvesting collie | 0004-* | 147 | 06-06 | Crossplane cloud plane governed by the same engine | cage | off_mission | No: the loop needs one cage surface, not two planes | unknown; late note delegated (0004:79) | 0004:7-15 |
| 0005 | Flux Operator + ResourceSet | 0005-* | 45 | 06-06 | Install and fleet templating layer; the thesis must stay vanilla-Flux | enact | off_mission | No: the ADR itself says to strip it (0005:15-18) | unknown | 0005:7-12 |
| 0006 | Deterministic policy | 0006-* | 46 | 06-06 | No time conditions in policy bodies; the price may move with the date, the verdict may not | ratchet | support | Yes: a notch lands only by reviewed change, never on a timer | unknown; note delegated | 0006:5-18, 19-26 |
| 0007 | Agent-assisted editorial governance | 0007-* | 106 | 06-06 | An agent reads signals and opens review PRs; it never edits enforcement | react | duplicate (concrete form is the proposer, ADR-0015) | Its job, yes; the ADR, no | unknown; banner delegated (0007:50) | 0007:7-25 |
| 0008 | Measurable = layered ground truth | 0008-* | 56 | 06-06 | Four measurement signals; the dashboard delivery was retired by the owner | evidence | support | Weakly | owner_words (rejection only): "slideware", 2026-07-20 (0008:5-9) | 0008:5-15 |
| 0009 | OSCAL via C2P | 0009-* | 105 | 07-14 | OSCAL assessment results made from PolicyReports by C2P; Lula dropped | evidence | off_mission (holes are priced from control claims, CONTEXT.md:267, 650, not from assessment results) | No | unknown | 0009:5-12 |
| 0010 | Sunset as scheduled proposal | 0010-* | 114 | 07-16 | A dated sunset opens a retirement PR; consumer `sunset:` superseded by Supersede | react | duplicate (superseded by ADR-0023 / Supersede) | No | unknown; banner delegated (0010:5-22) | 0010:5-22 |
| 0011 | Release gate computes the bump | 0011-* | 212 | 08-22 | Semver derived from measured verdict movement; weaker declaration published degraded | none | off_mission | No: it is about versioning the policy artefact, not about risk | assistant; one owner-instructed enactment (0011:193) | 0011:5-24, 26-38 |
| 0012 | Composed artefact self-signed | 0012-* | 36 | 08-24 | An adopter signs its composition; parents pinned by SHA | evidence | off_mission | No: a reduced loop has no multi-parent composition | assistant | 0012:5-12 |
| 0013 | Regulator baselines, bare control id | 0013-* | 90 | 08-24 | Regulator publishes baselines, adopter selects one; key is the bare id; refusals superseded by 0026 | quantify | support | Yes in reduced form: which controls apply defines the holes | assistant | 0013:5, 15-28 |
| 0014 | Unclaimed is caged | 0014-* | 127 | 08-24 | An unclaimed pod in a governed namespace goes to the bottom rung (CREATE deny removed) | cage | support | Yes: nothing outside the cage | assistant; amendments delegated | 0014:5-9, 15-24 |
| 0015 | Adopter runs the proposer | 0015-* | 101 | 08-24 | The war-gamer is the proposer: it runs in the adopter repo and opens the tier PR. Point 7: proposals go both ways | ratchet | kernel | Yes: this is R | assistant | 0015:29-51, 68 |
| 0016 | Subclass never restates a mutate | 0016-* | 84 | 08-25 | Restatement only on a ValidatingPolicy; the tier is the only knob | none | off_mission | No (composition rule) | assistant | 0016:25-36 |
| 0017 | Control claim belongs to the implementer | 0017-* | 84 | 08-25 | Whoever ships the implementation makes the claim that fills a hole | quantify | support | Weakly: something must say a control is implemented | assistant | 0017:15-24 |
| 0018 | Namespace manifest is the declaration | 0018-* | 79 | 08-25 | `governed: "true"` plus the tier on the Namespace manifest is the declaration | cage | support | Yes: the notch needs one place to be written | assistant; amendments delegated | 0018:23-31 |
| 0019 | One feed envelope | 0019-* | 86 | 08-28 | One signed envelope for every feed; parent kinds closed, names free | react | support | Yes in reduced form: one input format for world changes | delegated (bare agree, 0019:10-13) | 0019:15-30 |
| 0020 | Missing instrument refuses | 0020-* | 100 | 08-28 | A missing price input refuses the number; a missing behaviour is priced | quantify | support | Yes: Q must not invent numbers | delegated; owner reason for the currency default only (0020:9-12) | 0020:14-20 |
| 0021 | Twin emits scenario, estate selects tier | 0021-* | 37 | 08-28 | Twin forward intel goes into `prices[]`; fair.py annualises; the adopter's selection policy turns the curve into a tier | compare | kernel in intent; ADR-0031:32 says it is not wired in code | Yes, the seam: price, then tier | delegated ("Lgtm", 0021:10-12) | 0021:14-27 |
| 0022 | Cage ladder | 0022-* | 241 | 08-28 | Tier per Namespace; tighten-only cage; `isolated` bottom rung; floor; no deny; proposer tightens only; strictest-line fold | cage + ratchet | kernel | Yes: this is C/R/E's object | delegated (0022:31-35); owner reason for no-deny, 2026-09-02 (0022:91-100) | 0022:37-52, 110-168 |
| 0023 | Clock appends observations | 0023-* | 115 | 08-28 | A schedule may append observations, never declarations; one signature verified at the Flux source | react | support | Yes: re-quantify on a clock, enact only by review | delegated ("I agree with you're more advanced reasoning", 0023:9-15) | 0023:5-15 |
| 0024 | Daily clock, observation lane, derived ledger | 0024-* | 533 | 08-28 | A daily clock on every unit; the adopter re-composes at today's date and proposes; lane caging; October delivery amendments | react (points 1-2); ceremony (points 3-6, amendments 430-533) | kernel (points 1-2); ceremony for the rest | Points 1-2 yes; the rest no | delegated; point 6 owner-reasoned, ticket 75 Q10 (0024:96-98) | 0024:20-37, 430-533 |
| 0025 | Assistant decides architecture | 0025-* | 54 | 09-02 | The assistant decides and records; a bare yes is a delegation; "provisional" retired | ceremony | ceremony | No | owner_words: "ask fable to decide then record" (0025:19) | 0025:17-31 |
| 0026 | Hole priced, never refused | 0026-* | 386 | 09-04 | Hole = control weight × sized exposure; implementing a control reduces price and can move the tier; removals and widenings are priced deltas | quantify | kernel | Yes: this is the Q formula | delegated (0026:7) | 0026:94-105, 331-354 |
| 0027 | Verifier chains at later instant | 0027-* | 80 | 09-03 | gitsign verifier trust instant = later of tagger time and certificate issue | evidence | support (detail) | No | delegated (0027:7) | 0027:9-24 |
| 0028 | Cage behaviour graded on the lane | 0028-* | 209 | 09-10 | Two live facts: the bottom-rung pod runs and reaches nothing, bracketed by a control pod | evidence | support | Yes in reduced form: proof that a notch constrains | delegated (0028:7-9) | 0028:56-90 |
| 0029 | Candidate model permission; Laya refused | 0029-* | 262 | 09-22 | Ten-condition permission for a model; 0 of 14 pairs hold one | none | off_mission | No | delegated (0029:7-8) | 0029:72-95 |
| 0030 | loophole external tool | 0030-* | 304 | 09-22 | An adversarial agent attacks ADR prose, in rounds, never vendored | ceremony | off_mission | No | delegated (0030:7-8) | 0030:13-27, 63-160 |
| 0031 | Twin agent caged by dial table | 0031-* | 94 | 09-25 | The build's own twin agent gets a dial table on the one ladder; the platform prices it, the adopter selects | cage (of the build's agent) | off_mission | No for the organisation's loop | delegated ("agree" ×4, 0031:7-9) | 0031:22-66 |
| 0032 | Pricing threshold / synthetic never raises grade | 0032-* | 62 | 09-25 | Price only at evidence grade 2, or 3 if declared; synthetic records never raise a grade | quantify | support | Weakly | delegated (0032:7-10) | 0032:31-40 |
| 0033 | Supported engines exact | 0033-* | 162 | 09-26 | A line supports only the exact engine versions it passed on; another engine is priced as holes | cage | support/ceremony | No | delegated (0033:7-9) | 0033:31-40 |
| 0035 | CVE priced from own scan | 0035-* | 93 | 09-25 | The adopter trivy-scans its served images against a KEV-scoped feed; the inventory is a reviewed declaration | quantify + react | support | Yes: "new vulnerability re-quantifies" is X | delegated ("agree", 0035:7-9) | 0035:23-35 |
| 0036 | Incumbent org shrinks | 0036-* | 91 | 09-25 | App repos transfer, other incumbent repos archived when a register row passes | none | off_mission | No | delegated; owner authorisations by "agree"; owner quote 2026-07-16 on repo split (0036:31-33) | 0036:7-14 |
| 0037 | One pinned delivery controller | 0037-* | 57 | 10-17 | Clock observation commits reach main through a reviewed PR by one shared controller | ceremony | ceremony | No | delegated (0037:7); October epoch, no Codex marker in git | 0037:7-33 |
| 0038 | Consumer retirement | 0038-* | 72 | 10-17 | An adopter may explicitly remove exact versions from its composed window for an engine transition | none | off_mission | No | delegated (0038:7) | 0038:17-33 |

ADR sum: 4,646 (matches `cat docs/adr/*.md | wc -l`).

### Glossary sections (CONTEXT.md, 958 lines; born 2026-06-06, 54 commits)

| name | lines (range) | lines | what it does | loop role | necessity | origin | cite |
|---|---|---|---|---|---|---|---|
| G1 Intro, parties, 2022 thesis terms | 1-74, 102-119, 139-146, 165-178, 189-192, 218-224 | 125 | Party, Role, Institution, org overload, Policy, Exemption, -ables, why, governance layers, version pin, coexistence | none (thesis) | support | inherited_2022 + assistant | CONTEXT.md:20-74 |
| G2 Cage and enforcement | 75-101, 290-417, 517-547 | 186 | Cage, Orphan guard, Governed namespace, Currency controller, De-postured, Tier, Isolated, Reference workload, Floor, Infra tier | cage | kernel (Cage, Tier, Isolated, Floor); support for the rest | assistant; Cage carries an owner quote (CONTEXT.md:85-87) | CONTEXT.md:75-101, 517-541 |
| G3 Proposer and rejection ledger | 120-138, 556-560 | 24 | Who opens the tightening PR, and how declined proposals decay | ratchet | kernel (Proposer) | assistant | CONTEXT.md:120-138 |
| G4 Versioning and composition | 147-164, 179-188, 193-217, 225-247, 502-516, 561-571, 595-617, 713-716, 727-730 | 133 | Policy version, major acceptance, consumer retirement, engines, composed artefact, restatement, bump, supersede, revocation, handbook, platform machinery | none | off_mission (except Supersede/Revocation = react) | assistant | CONTEXT.md:147-164 |
| G5 Controls and holes | 248-289, 650-712 | 100 | Baseline, Control claim, Control id, Hole, Delta, Control weight, Ungoverned namespace, Bespoke control, Register entry | quantify | kernel (Hole, Control weight); support for the rest | assistant | CONTEXT.md:650-662 |
| G6 Pricing, tolerance, insurance | 448-501, 634-649, 717-726, 782-799 | 94 | Feed, Size facts, Pricing threshold, Obligation, Reporting currency, Perspective, Selection policy, Price, Appetite, Instrument fault, Exposure, Quote, Attachment, Premium, Switching cost, Reliability score, fit/widening/per-customer/provisions | quantify + tolerance + compare | kernel (Price, Exposure, Appetite, Selection policy); off_mission (insurance, switching, reliability) | assistant (A1: "appetite band" is the assistant's, maps/A1-owner-words.md:75) | CONTEXT.md:485-497, 634-637 |
| G7 Twin and identity | 418-447, 572-594, 739-781 | 101 | Twin, forward intel, overlay, sensed signal, standing scenario, market/news feeds, skill-eval terms, trust domain, reach demand, actor class | react (Sensed signal); none for the rest | off_mission (mostly) | assistant; owner quote in Twin entry (CONTEXT.md:428-429) | CONTEXT.md:418-444, 752-772 |
| G8 Process terms, slide lint, decision log, mode record | 548-555, 618-633, 731-738, 744-747, 800-833, 951-958 | 78 | Observation, Declaration, Capture, Could-not-look, Observation branch, Lift/Drop/Incumbent, banned slide phrases, development window | ceremony | ceremony (Declaration is support for E) | assistant; mode record built on owner renewals | CONTEXT.md:800-833, 955-958 |
| G9 Project posture, Flux and cloud terms | 834-950 | 117 | Ten resolved June decisions; plain-English Flux, Crossplane, OSCAL, C2P | enact (Flux terms); none (rest) | support | inherited June | CONTEXT.md:834-950 |

Glossary sum: 958. Some range lists are approximate. The per-entry lengths come from an awk pass and sum to 958.

### NORTH-STAR, README, docs/*.md (2,226 lines)

| name | paths | lines | born | what it does | loop role | necessity | origin | status | cite |
|---|---|---|---|---|---|---|---|---|---|
| North star | NORTH-STAR.md | 143 | 2026-08-28 | Purpose chain (talk to reference implementation to adoption to argument), one sentence, 7 principles, build order, truth surface, what is out, 18 later decisions | ceremony | ceremony | owner_words for §0 and principles (dated quotes, NORTH-STAR.md:13, 53-57); §4 the assistant's (NORTH-STAR.md:63) | unknown; a gate fails if §0 goes missing (NORTH-STAR.md:7, verify/record/verify-record-states-the-purpose.sh) | NORTH-STAR.md:9-26, 28-30 |
| README | README.md | 44 | 06-06 | Entry page; lists ADR-0001…0010, "no bespoke tooling", "Audit and Deny are rungs" | presentation | support | unknown | unknown | README.md:24, 31-35 |
| Inherited thesis docs | docs/PRD.md, references.md, modern-reference-transport.md, shift-left-dev-workflow.md | 849 | 06-06 to 08-28 | June PRD (no £), citation registry, OCI/cosign upgrade report, laptop verdict reproduction | none (pre-loop); enact (shift-left) | support | inherited_2022 / unknown | unknown | docs/PRD.md:1-14 |
| History and archive | docs/HISTORY.md, ARCHIVE.md | 303 | 07-16, 08-21 | Newcomer narrative; superseded archive plan | ceremony | ceremony | unknown | unknown | docs/ARCHIVE.md:3-9 |
| Show-and-tell runbook | docs/SHOW-AND-TELL.md | 210 | 07-20 | Live demo runbook for the seven -ables | presentation | ceremony | unknown | unknown | docs/SHOW-AND-TELL.md:1-10 |
| Calibration custody docs | docs/qualification-bindings.md, reference-case-admission.md, source-metadata-migration.md, pdf-output-origin.md, native-pdf-remap-helper.md, pdf-comparison-capture.md, pdf-native-host-bridge.md | 607 | 10-30, 10-31 | Custody and attestation protocol for qualifying a model on PDF-extracted reference cases | none | off_mission | unknown (calibration epoch; no Codex marker in git; maps/A5 rows 15-16 infer codex) | unknown; registry empty per docs/qualification-bindings.md:7-9 | docs/qualification-bindings.md:1-9 |
| Twin release route | docs/twin-release.md | 70 | 10-23 | How `twin/v0.1.0` gets cut as one signed tag | ceremony | ceremony | unknown | unknown | docs/twin-release.md:1-12 |

Docs sum: 143+44+849+303+210+607+70 = 2,226. Area total = 4,646 + 958 + 2,226 = **7,830**.

## (1) ADR one-liners

See the ADR table: each row gives what the ADR decides, its loop role, whether it is still needed after reduction, and who decided. Tally:
- **Still needed in some form if the estate were only the loop (12):** 0002, 0003, 0006, 0013, 0014, 0015, 0018, 0020, 0021, 0022, 0024 (points 1-2), 0026. Partly or weakly needed: 0001, 0017, 0019, 0023, 0028, 0032, 0035.
- **Not needed (18):** 0004, 0005, 0007 (duplicate), 0008, 0009, 0010 (superseded), 0011, 0012, 0016, 0025, 0027, 0029, 0030, 0031, 0033, 0036, 0037, 0038.
- **Who decided:** the owner instructed one (0025). Owner reasons appear inside notes on 0008 (rejected the dashboard), 0014/0022 (no deny, no delete) and 0024 point 6 (a local model clock). 26 ADRs record an assistant decision, delegated under ADR-0025 or written in the assistant's voice. The 9 June-July ADRs (0001-0010 except 0008) carry no attribution.

## (2) Glossary term count

**Counting rule:** a term is a top-level `- **Term**` bullet outside "Project posture". `grep -c '^- \*\*' CONTEXT.md` gives 130. Remove the 10 posture bullets, which are decisions, not terms: **120 terms**, made of 102 core (lines 18-799), 9 Flux, 7 cloud plane and 2 mode-record. Not counted: the Role sub-terms publisher, risk-bearer and adopter (CONTEXT.md:28-34), and the 5 slide-lint rows (CONTEXT.md:826-832).

**A newcomer must learn about 24 terms to follow the loop:** Feed, Size facts, Obligation, Perspective, Reporting currency, Price, Hole, Control weight, Control claim, Baseline, Exposure, Appetite, Selection policy, Tier, Isolated, Cage, Floor, Governed namespace, Proposer, Declaration, Supersede, Revocation, Version pin, Flux (with Kustomization).

**Terms that exist only because of machinery (about 70):** `org`, Major acceptance record, Consumer retirement, Supported engine, Declared engine, Unsupported pairing, Composed artefact, Restatement, Control id, Orphan guard, Currency controller, De-postured, Reference workload, Infra tier, Pricing threshold, Instrument fault, Parent kind, Subscription, Discovery record, Observation, Rejection ledger, Declared bump, Degraded publish, Twin, Forward intel, Twin overlay, Sensed signal, Standing scenario, Trust domain, Reach demand, Actor class, Platform machinery, Handbook, Lift, Incumbent org, Drop, Quote, Attachment and limit, Premium, Delta, Ungoverned namespace, Bespoke control, Register entry, Verified source, Switching cost, Reliability score, Vendored payload, Capture, Could-not-look, Market-moves feed, Observation branch, News feed, Not measurable, Wrong basis, Attributable rate, Headline skill, Claim scope, Relevant revenue, Fit check, Widening target, Per customer, Provisions, Mode record, Development window, Advisory metadata, Multi-version coexistence, Policy version, plus the cloud-plane terms. The rest (Party, Role, Policy, Exemption, the -ables, why, governance layers, last mile, Compliance, Consumer, OCI, cosign and so on) are thesis background.

**Length inversion:** the loop kernel terms average about 5 lines (Appetite 6, Price 7, Exposure 5, Selection policy 3, Tier 7, Floor 5). The four longest entries are machinery and its own correction history (Currency controller 42, Governed namespace 39, Orphan guard 34, Twin 30). Orphan guard records "This entry has been wrong twice" (CONTEXT.md:298).

## (3) Terms the record bans or polices

| term | rule | why | cite |
|---|---|---|---|
| exemption | banned concept, "none, ever"; slide lint refuses it | everything-is-policy doctrine (owner, 2026-08-20 "never an exemption ledger EVER", NORTH-STAR.md:53) | CONTEXT.md:57-65, 828 |
| hourglass | refused on a slide | the drift review removed the "neck" (reversal 1) | CONTEXT.md:829 |
| admission gate / deny gate / "deny is the bottom rung" | refused on a slide | owner: a mutating admission controller, not an approving one (2026-09-02) | CONTEXT.md:830-832 |
| gate (admission sense) | flagged for human review, not refused | the truth surface, release gate and adopter gate keep the word | CONTEXT.md:815-820 |
| "baseline" alone | write "the `baseline` rung" | clashes with the OSCAL Baseline | CONTEXT.md:521-522, 248-249 |
| compatible range, "works on 1.18" | avoid | no inferred engine ranges (ADR-0033) | CONTEXT.md:203-204 |
| exemption / implicit engine filter / publisher retirement (for consumer retirement) | avoid | keep consumer retirement explicit | CONTEXT.md:197 |
| evidence floor | avoid | "floor" is a tier bound | CONTEXT.md:466 |
| control / control workload / control pod | avoid for the reference workload | "control" means a catalogue control | CONTEXT.md:534-535 |
| original org, legacy org | avoid; say "incumbent org" | naming | CONTEXT.md:627 |
| retire (for a mechanism) | avoid; say "drop" | "retire" is kept for a policy version leaving the array | CONTEXT.md:632; NORTH-STAR.md:136 |
| lucky, passed | avoid for "wrong basis" | names a cause nobody measures | CONTEXT.md:767 |
| `AC-6`, `AC-06`, `nist-800-53:AC-6` | never keys | exact-string bare id | CONTEXT.md:274-277 |
| provisional | retired | ADR-0025 point 4 | docs/adr/0025-*:28-29 |
| north star | exactly one referent | NORTH-STAR.md | NORTH-STAR.md:3 |
| Party collective noun | none allowed | the argument needs different kinds of party | CONTEXT.md:20-23 |
| De-postured | superseded by Currency controller | homonym and wrong mechanism | CONTEXT.md:405-417 |
| "every actor is attestable" | narrowed to "artefact" | actor attestation never observed | NORTH-STAR.md:32 |

The slide-lint table is machine-read by `talk/build_deck.py:659-686` (outside this area, pointer only). A document here is therefore an input to a presentation check.

## (4) Contradictions

1. **Ratchet direction.** ADR-0015:50 says "Proposals go both ways", and ADR-0015:68 rejects "a tighten-only proposer… it ratchets the estate toward deny and never recovers". ADR-0022:110-168 (note of 2026-09-04) says "the proposer only tightens… Loosening is not implemented, and that is the decision". ADR-0015's banners (0015:5, 7-15) do not record that point 7 is superseded.
2. **What is compared.** The Appetite entry (CONTEXT.md:492-494) says "the £ selects the first cage tier whose residual sits under it", and NORTH-STAR.md:71 says "The £ crosses a band". The record of the code says per-line selection and then "Strictest line, not summed residual" (ADR-0022:122-143). Bespoke and ungoverned prices "enter no sum and no tier" (ADR-0026:352-354). The Exposure entry (CONTEXT.md:634-637) is the input an insurer quotes against and is never compared with Appetite. No document says the loop stops when exposure falls within appetite.
3. **The twin's price does not reach the tier.** ADR-0021:20-26 says forward intel enters `prices[]` and the selection policy turns its curve into a tier. ADR-0031:32, measured 2026-09-25: "Composition selects a tier from the platform table's residuals and only hashes the twin's curve." The reductions each rung buys are "evidenced by nothing but this comment" (ADR-0031:81; pointer: platform/graded/cage.py:71).
4. **Party count.** CONTEXT.md:20-24 says "six units"; README.md:8-11 says "eight parties"; NORTH-STAR.md:41, 45 say the intelligence publisher and the insurer "do not exist yet". FRESH holds 9 repos including `feeds` and `insurer`, and NORTH-STAR.md:94 names them.
5. **Ladder membership.** The Cage entry lists "baseline, restricted, quarantine, isolated, infra" (CONTEXT.md:78-79), and so does ADR-0022:50. The Tier entry (CONTEXT.md:518-519) and ADR-0022:237-241 say `infra` is not a rung.
6. **Deny.** README.md:32 says "Audit and Deny are rungs on the cage ladder". The slide lint refuses "deny is the bottom rung" (CONTEXT.md:832) and the Cage entry says "nothing is denied" (CONTEXT.md:88). Yet the semver major is still defined by "a new or tightened `Deny`, an `Audit`→`Deny` promotion" (CONTEXT.md:152-154), and Restatement still ranks on the "`Audit < Deny` ladder" (CONTEXT.md:239-241). Pointer outside the area: platform/graded/cage.py:64-65 says "that is what Deny, the bottom rung, does".
7. **"Nothing is ever refused."** CONTEXT.md:84 and :525-526 say this without qualification. Against it: Instrument fault "refuses" (CONTEXT.md:498-500); restating a mutate "is refused" (CONTEXT.md:244); unknown or withdrawn control id "refuses" (CONTEXT.md:281); a disagreeing declaration "still refuses" (ADR-0011:22-24); `apply_tier_declaration()` "refuses" (ADR-0022:162). The doctrine holds only in the admission and behaviour sense, and the glossary never states that scope.
8. **What the proposer edits.** CONTEXT.md:122-123 says "edits the tier declaration in the signed composed artefact". CONTEXT.md:326-328 and ADR-0018 decision 1 say the composed artefact carries no namespace list. ADR-0022:39-41 and :113 put the tier on the Namespace manifest, and that is where `apply_tier_declaration()` writes.
9. **Source verification.** Posture (CONTEXT.md:847-851) and ADR-0001:28-33 say there is no verified-source gate on the cluster, only CI. ADR-0023:5 and :94 and ADR-0027:11-13 describe a gitsign-verifying controller at the Flux source boundary. ADR-0001 has no supersession banner for this.
10. **"No bespoke tooling."** CONTEXT.md:890-892 and README.md:35 say there is none. The ADRs name bespoke tools: wargamer.py and tier_pr.py (ADR-0022:113), tier_binding.py (ADR-0022:127), one shared delivery controller (ADR-0037), and verify-currency.sh (CONTEXT.md:399).
11. **"A glossary, not a spec, no implementation details"** (CONTEXT.md:3-4). The Currency controller entry has an RBAC grant, CronJob cadence and a script path (CONTEXT.md:363-403). Governed namespace has priorityClassName values (CONTEXT.md:345-358).
12. **Policy Reporter.** ADR-0008:13-15 retires it as the Prometheus route. CONTEXT.md:944-945 still calls it "the live measurability layer beneath C2P".
13. **"A human merges."** NORTH-STAR.md:57 (principle 5) and CONTEXT.md:134-135 say it. NORTH-STAR.md:94 (development "theatre"), :141 ("the development guard admits direct enactment") and :143 (renewed to 2027-01-01) contradict it.
14. **Purpose.** NORTH-STAR §0 makes the purpose a touring talk, then a reference implementation, then adoption, then the argument (NORTH-STAR.md:13-18). §1's sentence is about an eco-system of signed artefacts (NORTH-STAR.md:30). Neither names financial tolerance or a stop condition, which is the owner's 2026-11-14 statement of the mission.
15. **ADR index.** README.md:24 and docs/PRD.md:8 say "ADR-0001…0010"; there are 37, up to 0038.
16. **Dangling reference.** CONTEXT.md:31 says "see *reflexive*", and there is no such entry.
17. **Actor attestation.** Principle 6 keeps "Every actor is attestable" while §1 narrows the claim to "artefact" (NORTH-STAR.md:32, 58). The north star acknowledges this itself.
18. **ADR-0016 §3 against ADR-0022.** "The composed artefact carries no tier and no tier floor" (ADR-0016:36). ADR-0022:44-45 puts a floor on the party artefact. This is bannered as superseded at ADR-0016:5, so the record is consistent but the body is stale.

## (5) The loop in glossary terms (114 words)

> Each **Feed** (penalty schema, CVE, EOL, threat register) is applied to the adopter's **Size facts** and declared **Obligations** to give a **Price** for every **Hole**, under one **Perspective** and **Reporting currency**; together they are the adopter's **Exposure**. The adopter's **Appetite** is the annual loss it will carry. Its **Selection policy** turns each Price into a **Tier**; the strictest, clamped to the **Floor**, is the **Cage** its **Governed namespace** should carry. When that Tier is tighter than the declared one, the **Proposer** opens a reviewed **Declaration**; once merged, **Flux** applies it and the cage writes the Tier onto every pod. A new Feed version, a **Revocation** or a **Supersede** re-prices, and the Proposer runs again.

**Loop steps with no term:**
- **C compare:** no entry. The rule is a clause inside Appetite (CONTEXT.md:493-494). "Residual" has no entry. Nothing compares Exposure with Appetite.
- **R ratchet:** no entry. "Tighten-only" is an adjective inside Cage (CONTEXT.md:94-95), and there is no word for a notch.
- **X react:** no entry for the re-price trigger or the schedule. "A re-price is a release" is a phrase inside Policy version (CONTEXT.md:158-159).
- **E enact:** only generic Flux terms plus Declaration. There is no project term for "the cage is now on the running system".
- **The stop condition** ("until within tolerance") has no term, and "tolerance" has no entry (it appears only at CONTEXT.md:645 as Appetite's synonym under insurance). "Risk" and "loss" have no entry either.

## What the loop would lose if this area vanished

Nothing that executes. The loop would lose the written formula for Q: hole = control weight × sized exposure, and implementing a control reduces the price (ADR-0026:94-105, 331-354). It would lose the rung list and the tighten-only and fall-closed rules for the cage (ADR-0022). It would lose the rule that a clock may re-price and propose but only a reviewed PR enacts (ADR-0023/0024 points 1-2, ADR-0006). It would lose the seam where a price becomes a tier (ADR-0021). And it would lose the ~24 terms above. The rest (about 6,400 of 7,830 lines) records decisions about versioning, composition, engines, the build's own agents and governance of the record. Losing it would leave the loop exactly as runnable as it is now.

## The simplest thing that would do this area's loop job

One file, `LOOP.md`, about 150 lines:
1. **A 12-row glossary table** (about 30 lines): Feed, Price, Hole, Control weight, Exposure, Appetite, Residual, Tier, Notch (one step up the ladder), Cage, Proposal, Re-price.
2. **The loop as 6 numbered rules** (about 30 lines). Exposure = Σ open holes × weight × size. If exposure > appetite, propose the next tighter tier for the namespace whose holes cost most. A merged proposal is applied by Flux. Any new feed version re-prices. Stop when exposure ≤ appetite. Never loosen without a reviewed human edit.
3. **A rung table** (about 10 lines): rung, dials, the claimed reduction and its evidence (which is currently "none", per ADR-0031:81).
4. **Five decisions with one-paragraph reasons** (about 60 lines): signed pinned versions (0001/0002), deterministic policy plus clock-proposes/human-enacts (0006/0023), price-don't-refuse (0020/0026), tier on the Namespace (0018/0022), proposer in the adopter repo (0015).
5. **An "out of scope" list** (about 20 lines): composition, computed semver, engines, OSCAL/C2P, the twin agent cage, model qualification, observation delivery.

It would replace about 7,830 lines with about 150, and it would name the compare and stop steps that no document names today.

## Surprises

- **"Ratchet" is a rejected design in the record.** ADR-0015:68 rejected a tighten-only proposer because "it ratchets the estate toward deny and never recovers". ADR-0026:187 rejected a selection ratchet as "a wall in slow motion". ADR-0022:164 later made the proposer tighten-only anyway, without bannering 0015.
- **The stop condition is undefined everywhere.** No ADR, glossary entry or north-star sentence says the loop ends when exposure is within appetite. The comparison is per price line plus a strictest fold (ADR-0022:141), labelled "the interim… pending PE-05 / ticket 75 Q4".
- **The rung reductions are unevidenced.** The reduction each notch "buys" is "evidenced by nothing but this comment" (ADR-0031:81), and an adopter's own curve disagrees materially (pointer: platform/graded/cage.py:71-75).
- **The north-star purpose makes the talk the first link** (NORTH-STAR.md:15). The PRD, README and HISTORY contain no money words at all.
- **Documents are gated by checks.** NORTH-STAR §0 is guarded by verify/record/verify-record-states-the-purpose.sh (NORTH-STAR.md:7). ADR banners are checked by verify/adr-supersession. The slide-lint table in CONTEXT.md is parsed by talk/build_deck.py. These are records of records, graded.
- **ADR-0024 is the largest ADR** (533 lines, 21 commits). About 200 of those lines are October amendments on how an observation commit reaches main (ADR-0024:430-533), a build-plumbing concern.
- **ADR-0029 and 0030 (566 lines) decide that two external tools do not enter.** Both are recorded as permanent ADRs.
- **ADR-0034 never existed** (no commit touches it; a 2026-09-26 review also searched and found none: hub/.scratch/ecosystem/research/ticket-71-record-review/2026-09-26-review-1-conflicts-and-claims.json:213).
- **Seven October docs (607 lines)** describe custody protocols for PDF extraction and model qualification. They name a registry that is "initially empty" (docs/qualification-bindings.md:7).
- **CONTEXT.md has 54 commits.** Several entries carry visible "this entry was wrong" histories (CONTEXT.md:298-317, 330-336), so the glossary doubles as an errata log.
