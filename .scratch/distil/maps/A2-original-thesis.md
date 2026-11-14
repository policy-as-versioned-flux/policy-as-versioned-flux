# A2: The original thesis and how simple it was

## Summary
1. The 2022 thesis was about delivery: policy is a semver-tagged dependency, pinned, tested and bumped by a reviewed PR. Up to 4 versions coexist on one cluster. It must "carry its why". It had 11 repos per org, 2 label policies (both `enforce`) and a one-line consumer CI step.
2. The June 2026 PRD (21c1da96, 2026-06-06) re-implements that thesis on Flux. Whole-tree grep of 21c1da96 finds no money, tolerance, quantification, ratchet or "financial". "Appetite" appears only twice, both about a Flux maintainer.
3. The PRD covers loop step E (enact) well. It has R seeds (an Audit/Deny ladder, semver major = tightening) and an X seed (an agent reading CVE and regulatory signals). Q is only qualitative risk metadata that the engine never reads. T and C are missing.
4. The loop's vocabulary (appetite in £, quantified risk, "ratchet down") first appears in commit 575d5fae on 2026-07-23. This follows an owner pivot recorded as "policy versioning as the thesis -> quantified risk as the spine".
5. Verdict: historically the loop is a second mission added 47 days later. Structurally, versioned policy is a natural E step, and part of R. The 2022 "grounded in threat modelling, not emotional and anecdotal" is the seed of Q.
6. One real conflict stands between them (my inference). In ADR-0002 the consumer pulls each upgrade through a reviewed PR. A ratchet driven by exposure pushes instead. Under ADR-0002 a consumer can stay on a loose version for ever.
7. In the original, "simple" meant one string doing two jobs, a one-line consumer CI step and one label to onboard. In June the owner asked to "consider where it could be SIMPLIFIED". On the same day the PRD overrode six of the register's recommendations, all toward more scope or more strictness.
8. Area total: 2,906 lines. That is 2,715 lines across the 7 named files at HEAD plus 191 lines of CONTEXT.md@21c1da96 as a snapshot. 200 HEAD lines were inserted after 21c1da96 (188 in the PRD, which grew 366→480). So the HEAD rows reflect June plus later amendments.

## Method notes
- **`status` on documents:** each document gets the status of the mechanism it specifies, but only where this area holds evidence that the mechanism ran. Anything else is `unknown`. The 2022 CI runs appear only second-hand (research/02:132-144).
- **Sources:**
  - research/03 is the assistant's capture of the owner's 2022 blog and talk, and I could not check it offline. Its "-able" glosses are "synthesised" (03:58).
  - PURPOSE.md §0 (hub/.scratch/ecosystem/review-2026-09-02/evidence/purpose/PURPOSE.md:16-19) says no commit message carries owner speech.
  - The PRD is authored "CNS with Claude", and its choices depart from the assistant's own register in six places, so its origin is `unknown`.
- **Line numbers** marked `@21c1da96` come from `git show 21c1da96:<path>`. Unmarked numbers are at FRESH HEAD.

## Components

| # | name | paths | lines | born | what it does | loop role | necessity | origin | status | cite |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2022 example-policy-org dissection | hub/research/01-original-example-policy-org.md | 810 | 2026-06-06 | Records the inherited 2022 delivery machinery: a `policy` repo with 3 tags, policy-checker, policy-action, 6 consumers, e2e, Renovate regexManagers. "One label string, two jobs" is the trick | enact | support | assistant | unknown | hub/research/01-original-example-policy-org.md:32-46, 780-799 |
| 2 | 2022 coexistence crux | hub/research/02-original-cns-org.md | 363 | 2026-06-06 | Shows how N versions coexist: `nameSuffix` plus the version label plus a self-selector inside the policy. A cluster narrows its set by installing fewer versions. Records the orphaned-label gap | enact | support | assistant | unknown | hub/research/02-original-cns-org.md:31-95, 146-157 |
| 3 | Thesis core: dependency, seven -ables, carry the why | hub/research/03-blogs-thesis.md:1-91 | 91 | 2026-06-06 | Semver policy, a runtime serving 3 or more versions, the seven -ables, "Purposeless policy...", "grounded in informed threat modelling" (a qualitative seed of Q) | enact | support | inherited_2022 | unknown | hub/research/03-blogs-thesis.md:23-26, 40-41, 58-66, 75, 80-88 |
| 4 | Mea-culpa refinement | hub/research/03-blogs-thesis.md:92-166 | 75 | 2026-06-06 | Lane-keeping for about 80% of policy, a "locked door" gate for access, data and crypto, dated/reviewed/removed governance (a manual react cycle), and the open last mile | cage | support | inherited_2022 | unknown | hub/research/03-blogs-thesis.md:111-151 |
| 5 | Design implications and quote bank | hub/research/03-blogs-thesis.md:167-216 | 50 | 2026-06-06 | Restates sections 1-4 as six design rules (duplicates PRD §1-3) | ceremony | duplicate | assistant | unknown | hub/research/03-blogs-thesis.md:201-216 |
| 6 | Faithful Flux mapping | hub/research/20-synthesis-faithful-flux-mapping.md:1-315 | 315 | 2026-06-06 | Maps each 2022 mechanism to a Flux primitive, plus 10 open questions (duplicates PRD §5-6 and research/22) | enact | duplicate | assistant | unknown | hub/research/20-synthesis-faithful-flux-mapping.md:17-31, 239-256 |
| 7 | Simplify/modernise synthesis | hub/research/21-synthesis-simplify-modernise.md:1-262 | 262 | 2026-06-06 | The only document whose job is deletion. MVP floor: "No image-automation, no Terraform, no flux-operator, no ResourceSet". The owner's ask is at 21:4-5 | enact | support | owner_words | unknown | hub/research/21-synthesis-simplify-modernise.md:4-5, 173-182, 192-207 |
| 8 | PRD decision register | hub/research/22-prd-decision-register.md:1-257 | 257 | 2026-06-06 | Options and recommendations for the grilling (duplicates ADR-0001..0008). Six of its recommendations were overridden by the same-day ADRs (see Surprises) | ceremony | duplicate | assistant | unknown | hub/research/22-prd-decision-register.md:35, 52, 148, 162, 200, 227 |
| 9 | PRD §1-4: thesis, goals, non-goals, principles, -ables | hub/docs/PRD.md:1-118 | 118 | 2026-06-06 | Mission statement. Holds June's only react-flavoured line ("let the risk mitigations move as fast as the risk") and the proportionality principle (a cage seed) | cage | support | unknown | unknown | hub/docs/PRD.md@21c1da96:26-29, 64-83, 99 |
| 10 | PRD §5-6.4, 6.9-6.10: distribution, adoption, engine, coexistence, shift-left | hub/docs/PRD.md:119-292, 346-361 | 190 | 2026-06-06 (amended 07-14 to 09-26) | gitsign tags and commit pin, reviewed Renovate PR, Kyverno CEL Audit/Deny, ResourceSet matrix, orphan guard, native CLIs instead of the checker | enact | kernel | unknown | unknown | hub/docs/PRD.md@21c1da96:189-229 |
| 11 | PRD §6.5-6.6: cloud plane and layered compliance | hub/docs/PRD.md:293-324 | 32 | 2026-06-06 | Crossplane CRs judged by the same engine (widens what is caged); dashboard of revision, PolicyReports, OSCAL and PR-state | evidence | support | unknown | unknown | hub/docs/PRD.md:293-324 |
| 12 | PRD §6.7-6.8: agent governance and last mile | hub/docs/PRD.md:325-345 | 21 | 2026-06-06 | The agent reads rationale plus CVE, regulatory and Wardley signals and opens review PRs; it "never edits enforcement". Plus a generated handbook | react | support | unknown | unknown | hub/docs/PRD.md@21c1da96:246-265 |
| 13 | PRD §7-12 and refs | hub/docs/PRD.md:362-477 | 116 | 2026-06-06 | KiND proof, P1/P2/P3 phases, four CIO questions, risks, out-of-scope list | evidence | support | unknown | unknown | hub/docs/PRD.md@21c1da96:283-347 |
| 14 | October correction stamps | hub/docs/PRD.md:478-480; last 4 lines each of research/20, 21, 22 | 15 | 2026-10-03 | Appends "ADR-0036 drops the incumbent notification spine" to four June documents | ceremony | ceremony | unknown | unknown | hub/research/22-prd-decision-register.md:259-261; commit 6ed89616 |
| 15 | CONTEXT@21c1da96 core thesis terms | CONTEXT.md@21c1da96:1-90 | 90 | 2026-06-06 | Glossary. "Policy — A set of rules that mitigates a risk"; the why; lane vs gate; version pin; orphan guard | cage | support | unknown | unknown | hub/CONTEXT.md@21c1da96:16-19, 29-44, 75-89 |
| 16 | CONTEXT@21c1da96 posture and Flux/cloud glossary | CONTEXT.md@21c1da96:91-191 | 101 | 2026-06-06 | Restates the ADR decisions and defines terms (duplicates PRD/ADRs) | enact | duplicate | unknown | unknown | hub/CONTEXT.md@21c1da96:93-142 |

Sum: 810+363+91+75+50+315+262+257+118+190+32+21+116+15+90+101 = **2,906**.

## The six questions

### (1) The 2022 thesis, and its moving parts
Treat policy as a versioned software dependency, not an opaque gate: "It should have a version number. It should follow semantic versioning. It should live in a Git repository" (research/03:25-26). Consumers pin a version, test against it locally and in CI, and adopt new versions through reviewed Renovate PRs. The runtime serves 3 or more versions at once so old ones retire over a window (03:40-41). Policy should be visible, communicable, consumable, testable, usable, updatable and measurable (03:60-66). It carries its purpose and is grounded in threat modelling, not "emotional and anecdotal" reasoning (03:75, 86-88). The mea culpa adds three things. Lane-keeping covers most of the surface and a locked-door gate covers access, data and crypto. Every policy is dated, reviewed and removed if nobody defends it. The last mile stays open (03:111-158).

**Moving parts.** example-policy-org has 11 repos (01:34-46), 3 tags and 2 policies × 2 engines (Kyverno, Checkov). policy-as-versioned-code has 11 repos and 4 tagged versions of the same 2 policies (02:13-25). Recorded file lists:
- `policy` repo: about 33 files (my count of 01:70-84)
- checker: 7 files (01:337-339)
- policy-action: 3 files (01:496-497)
- e2e: 2 files (01:688)
- .github: 2 files (01:745)

run.sh is about 20 lines (02:220-240). The consumer gate is one workflow step (02:313-325). Total lines are **not recorded**.

Both 2022 policies are department-label rules with `validationFailureAction: enforce` (01:160, 196; 02:64). They blocked at admission, so there was no Audit/lane-keeping mode in the 2022 code. The Audit/Deny ladder is a 2026 addition.

### (2) The June 2026 PRD's scope and its non-goals
The PRD re-implements the thesis on Flux (PRD@21c1da96:11-15, 64-75):
- semver git tags signed with gitsign, consumed by a Flux GitRepository
- pinned everywhere and bumped only by a reviewed Renovate PR
- Kyverno CEL ValidatingPolicy, with Audit as lane-keeping and Deny as the gate
- N versions per cluster through `nameSuffix` and a self-selector, generated by a Flux Operator ResourceSet, with an orphan guard
- a cloud plane via a collie fork (Crossplane, OSCAL/Lula)
- a four-question CIO dashboard
- an agent that proposes review PRs and never edits enforcement
- a generated handbook, and proof on KiND in phases P1-P3

**Its own non-goals** (PRD@21c1da96:77-83):
- OCI transport, cosign attestations, SBOM, an enforced "why"
- Flux-native gitsign verification (#1068)
- a UK CAF OSCAL catalogue
- real-cloud fleet e2e at scale
- **"a production-grade risk-intelligence agent"**
- engine-agnosticism

### (3) What in the June PRD points at the loop, and what does not

| Step | Points at it | Does not |
|---|---|---|
| Q quantify | "Policy — A set of rules that mitigates a risk" (CONTEXT@21c1da96:16). Each policy carries "risk/rationale" (PRD@21c1da96:39-41) | No number, no money. Advisory metadata is "never consumed by the engine" (PRD@21c1da96:98, 257-258; ADR-0006@21c1da96:19) |
| T tolerance | nothing | Absent. Whole-tree `git grep` of 21c1da96 for appetite, tolerance, quantif, ratchet, financial and £ returns only docs/upstream/fluxcd-source-controller-1068-gitsign.md:4 and :77 ("maintainer signals appetite") |
| C compare | "Proportionality: lane-keeping for the ~80%, a hard gate only for catastrophic boundaries" (PRD@21c1da96:99) | A judgement by category, never a comparison against a threshold |
| R ratchet | Semver "major = breaking tightening" (PRD@21c1da96:193-195); Audit vs Deny as a two-notch axis (PRD@21c1da96:208-212); orphan guard "(Audit→Deny)" (PRD@21c1da96:227) | No rule decides when to tighten. Adoption is pulled by each consumer through a reviewed PR (ADR-0002@21c1da96:7-14). The "risk-proportional" per-environment split was rejected (ADR-0002@21c1da96:19-21) |
| E enact | Strong: versioned dependency, Flux reconcile, Renovate PR and coexistence put a new version onto running workloads (PRD@21c1da96:189-229) | |
| X react | "let the risk mitigations move as fast as the risk ... Defensive risk should travel at the same speed" (PRD@21c1da96:26-29). The agent reads "CVEs, cloud/regulatory change, Wardley climatic movement" (PRD@21c1da96:251-252) | The agent "never edits enforcement", has "one signal source", and a risk-intelligence agent is a non-goal (PRD@21c1da96:82, 255-256). Policy is deterministic (ADR-0006) |

### (4) What "simplicity" meant in the original: the owner's own phrases
- The talk slide over the seven -ables is headed **"(easily:)"** (research/03:55, verbatim heading). The seven words are verbatim (03:60-66); their glosses are synthesised (03:58).
- "the advantages of exposing policy and communicating that effectively with its developers far outweigh any potential security advantage" (Medium, 03:86-87).
- "When the CIO wants to know how many teams are compliant, the answer is **a GitHub PR search away**" (blog, 03:162-163).
- The 2022 repos: "everything coexisting on a single cluster **for simplicity**" (02:342), and the checker is a "**simple tool** to help our developers test their apps" (02:348).
- June 2026 ask: "research how to modernise (or **better yet consider where it could be SIMPLIFIED**)" (research/21:4-5, in a file born 2026-06-06; the exact date of the ask is not recorded).
- 2026-07-23T15:08, marked source-verified in PURPOSE.md:111-112: "remember the policy is just like a **linting pack as a dependency**, update a eslint rule pack and it could find issues in your code".
- 2026-07-31: "all of this is 'the policy' we're not carving exemptions, **or greater complexity**, we're codifying how the organisation operates" (OWNER_BRIEF.md:94).
- Structurally, simple meant **one string, two jobs** (01:780-782 "That single fact is the entire trick"), a one-step consumer CI (02:325), and onboarding by "setting one `policy-version` label" (PRD@21c1da96:111).

### (5) Is versioned policy the means of E, or a separate mission the loop was bolted onto?

**Case for "the means of E":**
- Owner 2026-07-23T15:29: "change the regulator financial fine we might get for a breach and then make the controls and everything else proportionate and grounded in that rather than making emotional or simply 'best practice' decisions" (PURPOSE.md:87-89; not marked source-verified). This nearly restates 2022's "grounded in informed threat modelling rather than emotional and anecdotal" (03:86-88). So Q is "carry the why" made numeric.
- The map that introduced the loop: "**Versioning is the *mechanism***; ... risk is the *ground and the scoreboard*" (.scratch/talk-spec/map.md@575d5fae:27-28).
- The first "ratchet" is defined as a version bump: "the 'ratchet down' is a version bump tightening the condition" (.scratch/talk-spec/issues/05-exemptions-ledger.md@575d5fae:22; attribution not determined).
- June already wanted mitigations to "move as fast as the risk" (PRD@21c1da96:26-29).
- Semver major = tightening, which is a notch.
- Reversal 21: "versioned policy is the spine; non-machine-enforceable levers become priced cages" (PURPOSE.md:117-118).

**Case for "a separate mission added later":**
- No loop vocabulary exists in 21c1da96.
- The risk-intelligence agent is a June **non-goal** (PRD@21c1da96:82), and risk metadata stays out of the engine (PRD@21c1da96:98).
- The pivot is owner-attributed and dated 2026-07-23: "policy versioning as the thesis -> quantified risk as the spine" (OWNER_BRIEF.md:31).
- The owner's own verb for the balance sheet was "**hint at**" (PURPOSE.md:82-84).
- ADR-0002's adoption is pulled by the consumer, while a ratchet is pushed by exposure (my inference).
- The later cage doctrine dissolved the mea culpa's locked door ("There is no gate", CONTEXT.md:75-76 at HEAD, versus 03:128).

**Evidence favours:** the two ideas came separately in time but join cleanly. History: the loop arrived 47 days after the PRD (2026-06-06 → 2026-07-23) as an owner pivot. Structure: the versioned dependency is the obvious E step and half of R (major = tighter notch), and 2022's "grounded in threat modelling" seeds Q. The one design conflict to resolve is consumer-pulled adoption (ADR-0002) versus an exposure-pushed ratchet.

### (6) The smallest set of original ideas that must survive
1. **Policy is a versioned dependency, with major = tightening**, so one notch is one version (03:23-41; PRD@21c1da96:193-195).
2. **One string, two jobs.** The declared version is both the pin and the engine selector (01:780-782).
3. **A cluster runs several versions at once, with an orphan guard.** Without the guard, retiring a version silently uncages its workloads (02:146-157; PRD@21c1da96:214-229).
4. **Carry the why.** Each rule names the risk it mitigates. In the loop this becomes the exposure reduction its notch buys (03:80-88).
5. **Change goes through a reviewed PR.** The PR is the unit of debate (ADR-0002), but the comparison must be able to open it (push), not only the consumer (pull).
6. **Proportionality.** Not every rule is a locked door (03:130-138). The loop turns the category into a comparison against tolerance.
7. **Native tools, no bespoke checker** (CONTEXT@21c1da96:135-137; research/21:20-34).

## What the loop would lose if this area vanished
- The only statement of **how a tighter cage reaches running workloads**: versioned delivery, pin = selector, coexistence, orphan guard (components 1, 2, 10).
- The human roots of Q and C: **proportionality** and "grounded in threat modelling" (components 3, 4).
- The record that June scope **held no money**. Without it, nobody can tell which loop machinery is original and which came after 2026-07-23.
- Components 5, 6, 8, 14 and 16 are restatement, so losing them costs nothing.

## The simplest thing that would do this area's loop job
One `policy` repo and three small files, assuming about 6 rules over 3 notches:
- **`policy/<rule>/`:** a CEL `ValidatingPolicy` with the version self-selector, a `kyverno test` fixture, and front-matter `risk_id`, `notch`, `exposure_reduction_gbp`. About 40 lines per rule, so about 240 for 6 rules.
- **`ladder.yaml`:** notch → rules, about 30 lines. Each new notch is a semver major tag.
- **`fleet/versions.yaml`:** the installed versions, about 10 lines. The ResourceSet expands it into sources and the orphan-guard allow-list.
- **`ratchet.py`:** reads `exposure_gbp` and `tolerance_gbp`. If exposure is above tolerance, it opens a PR bumping the fleet pin by one notch. About 80 lines; this is the push path ADR-0002 lacks.

Total: about 360 lines. Everything else in the June PRD (OSCAL/C2P, cloud plane, handbook, agent) is optional to the loop.

## Surprises
- **The loop is not in the original.** Whole-tree `git grep` of 21c1da96 finds no tolerance, quantif, ratchet, financial or £. "Appetite" appears only twice, about a Flux maintainer (docs/upstream/...:4, 77). `git log -S` puts "appetite", "£" and "ratchet" first in 575d5fae (2026-07-23), and "cage" and "twin" first in 6ab21fb8 (2026-07-31). Caveat: FRESH/hub is a partial clone and `git log -S` tried to fetch missing blobs, which was refused, so an earlier hit could hide in a missing blob. The direct grep of 21c1da96 is complete.
- **The same-day PRD/ADRs overrode six of the register's own recommendations**, all toward more scope or more strictness:
  - D1.1: OCI recommended (22:35) → gitsign git tags (ADR-0001)
  - D1.2: per-environment split recommended (22:52) → pinned everywhere (ADR-0002)
  - D5.1: MVP first, no operator (22:148) → Flux Operator plus ResourceSet (ADR-0005)
  - D5.2: Checkov in CI for the MVP (22:162) → collie/Crossplane cloud plane (ADR-0004)
  - D7.1: vanilla Flux for the MVP (22:200) → Flux Operator (ADR-0005)
  - D8.2: park governance (22:227) → "full human-governance layer is in scope" (ADR-0007@21c1da96:7)

  Who decided could not be determined from this area. The pattern is consistent with owner answers in a grilling session that I did not read.
- **2022 had no lane-keeping mode.** Both 2022 policies were label rules at `enforce` (01:160; 02:64). The "locked door" was never shown on an access, data or crypto rule, and "Audit = lane" is a 2026 invention.
- **CONTEXT.md grew from 191 to 958 lines and from 39 to 130 bolded terms.** It now says "There is no gate. Everything is always caged" (CONTEXT.md:75-76), against "I want a locked door" (03:128). It was rewritten 2026-08-28 (CONTEXT.md:12-14).
- **One October commit, 6ed89616 (2026-10-03, "Resume Claude ecosystem handoff"), touched 611 files with +366,822 lines.** It stamped "Correction ... ticket 156" onto four June documents.
- **"Three coexisting versions" was "non-negotiable"** (03:207-208). PURPOSE.md C6 records that the built estate later declared one version. That is unverified here and belongs to another area.
- **No owner use of "ratchet" or "reactive" was found** in OWNER_BRIEF.md, PURPOSE.md, REGRILL-ANSWERS.md, appendices/A-ambition-timeline.md or evidence/AMBITION_TIMELINE.json (all under hub/.scratch/drift-review-2026-08-27 or review-2026-09-02). The nearest owner words are "informed caging based on risk appetite/threat intel" (2026-08-21, OWNER_BRIEF.md:180) and "you're always caged even if it's a permissive one. It's the spec of the cage that can change" (2026-08-20, quoted in appendices/C-provisional-decision-audit.md:1159).
