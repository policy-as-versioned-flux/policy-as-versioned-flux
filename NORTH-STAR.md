# North star — proposed re-baseline, for the owner's ratification

> Committed at the repo root 2026-08-28 (eco-system ticket 02). The drift-review original at `.scratch/drift-review-2026-08-27/NORTH-STAR.md` is the record; this copy is the one documents cite. The phrase "north star" has exactly one referent: this file.

Status: RATIFIED by the owner 2026-08-27 ("I agree with the northstar"). Re-grill answers are recorded in [REGRILL-ANSWERS.md](.scratch/drift-review-2026-08-27/REGRILL-ANSWERS.md). Where a sentence rests on something you said, the date is given. Where it rests on my judgement, it says so.

> Amended 2026-09-03 by eco-system ticket 95, from the owner's answers of 2026-09-02 in [ticket 75](.scratch/ecosystem/issues/75-grilling-what-is-this-for-the-twelve-questions.md): §0 added; §4 re-headed as the build order with the definition of done; §3 principle 2, §6 and §8 extended. `verify/record/verify-record-states-the-purpose.sh` fails the gate if any of it goes missing.

## 0. What this is for

Every sentence in this section rests on the owner's words of 2026-09-02, recorded in ticket 75, unless it says otherwise.

**What it is for.** Four purposes, in a chain. (Owner, 2026-09-02, ticket 75 Q1: "all of them a leading to b, making c available because its open source underwritten by d".)

- (a) A **touring talk** that proves the corrected 2022 thesis as running code. It leads to
- (b) a **reference implementation** that ControlPlane lifts into client work. That makes
- (c) **adoption by a fourth organisation** available, because the estate is open source. The whole is
- (d) underwritten by **the argument itself**, as a written, checkable artefact.

**Who receives it.** For (a): the circuit the last talk toured. (Owner, 2026-09-02, ticket 75 Q15: "you can see the sorts of conferences i took the last talk to".) The assistant read that circuit from the owner's talk schedule on 2026-09-02: about twenty conferences and meetups between 2022-06-01 and 2023-09-21 (Cloud Native London and Wales, Open Source Summit Latin America and Europe, SREday, GitOpsCon, Spinnaker Summit, Kubernetes Community Days UK, DevSecCon, WeAreDevelopers, OSCONF, Conf42 and several online meetups). That the people in those rooms are principal engineers and leaders is the assistant's reading (ticket 75 Q1), not the owner's words. For (b): ControlPlane's client work. For (c): any fourth organisation. Availability is the promise, not a demonstrated adoption, so no onboarding is built on this map; that fold is the assistant's call, delegated (ticket 75 Q7, 2026-09-02). For (d): anyone who reads the record and runs the truth surface (§5).

**By when.** No date, no venue, no named recipient: "when we've got something good, we'll tour it". (Owner, 2026-09-02, ticket 75 Q15.) No ticket carries a deadline.

**What is done.** The running estate is the deliverable; the talk markets it. That is the assistant's call, delegated: the owner answered ticket 75 Q16 with a bare "a" on 2026-09-02, and under ADR-0025 a bare letter records the assistant's reason. §4 is the build order, and its preamble carries the definition of done. §6 records what is out.

**Consequences recorded with the purpose** (ticket 75 Q1, 2026-09-02): open source is the mechanism that makes (c) available, so the licence work in ticket 82 is on the route; the truth surface is the instrument of (d).

## 1. The one sentence

**A loosely coupled eco-system in which publishers, regulators and intelligence providers ship signed, versioned artefacts, adopter organisations compose those artefacts into their own policy, a platform enacts that policy as priced cages, and every artefact is attestable. The orgs are example consumers that demonstrate the whole eco-system operating.** (Owner, 2026-08-27, restated.)

The last clause read "every actor is attestable" until 2026-09-04. It was changed to "artefact" by ticket 90, on the owner's decision of 2026-09-02 (ticket 75 Q12), because the sentence must be true of what this build can be observed doing: 24 of 24 signed tags verify against Rekor, and actor attestation has never been observed on a citable run — all six identity-plane scripts could not look for want of a cluster. The actor half is not abandoned; it is the design principle 6 keeps, shelved, and the identity lane is the first thing after this map. Nothing else in this sentence changed.

## 2. What the eco-system is made of

Each participant publishes something, consumes something, or both. Nothing in the eco-system is a tenant of anything else.

| Participant | Publishes | Consumes | Example today |
|---|---|---|---|
| **Regulator** | Controls (OSCAL catalogue and baselines) or penalties (machine-readable fine schema), as signed semver tags | Nothing | `nist`, `ico` |
| **Intelligence publisher** | Signed, versioned feeds: threat register, CVE, EOL, market and commoditisation intel, prediction-market moves, news events | Public sources on a clock | *Does not exist yet.* Today the platform publishes four of five feeds to itself |
| **The twin** | Priced forecasts and forward intelligence under a declared perspective, signed by an agent identity, scored against reality | Feeds, the adopter's own overlay, history | `twin/` (subjects are eleven real firms today, not the adopters) |
| **Platform** | Policy implementations, the cage ladder, the £ engine, the composition and release gates, the distribution mechanism (Flux) | Regulators, intelligence, the twin | `policy-as-versioned-platform` |
| **Adopter organisation** | Its own composed artefact: a signed declaration of which parents it inherits, which baseline it selects, its appetite band, its size, its obligations, its overlay | Everything above, pinned by tag and commit, bumped by Renovate PR | `driftwood`, `tuppence`, `ludlow` |
| **Insurer or counterparty** | A signed quote against an adopter's declared attachment, limit and exclusions | The adopter's priced exposure | *Does not exist yet.* (Owner asked for insurance practice folded in, 2026-07-23; I cut it to a 40% load.) |

**Loosely coupled means:** each participant lives in its own GitHub organisation, ships on its own cadence, signs its own artefacts, and is consumed only through a pinned, signed dependency. No participant reaches into another. The only shared things are the artefact contracts and the £.

## 3. The seven principles

Each principle is stated, then sourced.

1. **Everything is policy.** There are no exemptions, no exemption ledger, no carve-outs for a named workload, at any scope, under any name. An allowance is either a conditional rule anyone can meet, or a cage with a price. (Owner: "all of this is 'the policy'", 2026-07-31; "never an exemption ledger EVER", 2026-08-20.)
2. **Everything is always caged.** A workload, a human, a device, a model action and the twin itself each run inside a cage. The cage spec is the only variable. The £ selects the spec. The bottom rung is "too expensive to run or not functional". There is no gate. (Owner: 2026-08-20, 2026-08-22.) In the owner's words (2026-09-02, ticket 75 Q5): "The evolution that we've come to whilst building this implementation and more modern technologies is that proportionality can be managed and run with a better cage and better protections and mitigations. Fundamentally, something could find itself unable to run, but that's only because it doesn't fit the cage, not because we deliberately deny it. So, in Kubernetes Parlance, we've built a Mutating admission controller more than a Approving admission and control". A refusal is therefore never a separate mechanism: a workload that does not fit its cage does not run. Ticket 89 makes the shipped policy say so.
3. **One £ currency, proportionate to the org.** Every impact and every candidate response is priced in one currency so a pay rise, a hardening control, a cage tier, an insurance transfer and a strategic play are comparable. The price is proportionate to the organisation: its turnover, its customers, its regulators, its declared appetite. Regulator penalties enter as published schemas applied to the adopter's own size. (Owner: 2026-07-23; "its proporiate to the org right?... cost per customer... percentage of global revenue", 2026-08-19.)
4. **Policy is a versioned dependency, all the way up and down.** Regulators, intelligence providers and the platform each version and sign what they publish. Adopters pin by tag and commit, compose from several parents like class inheritance, restate only stricter, and bump only by reviewed PR. Semver is computed from measured verdict movement, never declared. Older lines are patchable. COTS is wrapped in a shim so it wears a version too. (Original thesis; owner 2026-08-20 to 22.)
5. **Intelligence re-prices on a clock; enactment happens only by reviewed PR.** Feeds refresh, the twin re-forecasts, cages re-price, and proposals open, all on a schedule. A human merges. Nothing timed ever changes a verdict on its own. (ADR-0010; owner: "continuous refreshing", 2026-08-19. This reverses the "nothing timed, ever" rule I wrote into three repos and CONTEXT.md.)
6. **Every actor is attestable, and the record is falsifiable.** Every artefact carries a signature that says what it does and does not assert. Agent signatures attest the absence of a human. Forecasts are pre-registered and scored against reality under proper scoring rules. A green that could not look is a red. (Owner: 2026-07-23, 2026-08-05; twin decision tickets 14, 21.) **The actor half of this principle is SHELVED for this build** (owner, ticket 75 Q12, 2026-09-02; recorded here by ticket 90, 2026-09-04): the design stands and the sentence stays, but nothing in this build observes it. Of the two halves, the artefact half is real and graded on every run — signed tags verified against Rekor, certificate identity regexps, the gitsign source verifier — and §1 claims only that. The actor half (SPIRE as Istio's CA, federation across trust domains, EUD device identity, access-plane authz, posture in the SVID path, secret reach) has never been observed on a citable run: its six scripts skip for want of a persistent cluster and no ticket on this map clears them, so they are excluded from the gate with that reason in `talk/verify-exclusions.txt` rather than printed as six could-not-looks forever. The falsifiability half is not shelved and binds today. The identity lane returns first after this map; ticket 68 (federation gets its peer) is closed out of scope until it does.
7. **Flux is the distribution arm, held integral unless disproven.** Flux fans the signed policy line out to consumers, prunes on retirement, and heals drift. The falsification test stays open and honest. (Owner: 2026-07-23, 2026-08-05.)

## 4. The build order: what the demonstration must show

This section is the assistant's build order, not the owner's definition of done. (Owner, 2026-09-02, ticket 75 Q2: "not mine".) The seven steps are the assistant's proposal, derived from the twin's demo-slice sequencing and the owner's words of 2026-08-19. The order of the steps is the order of attack.

**The definition of done** (ticket 75 Q2 and Q8, 2026-09-02): the estate is done when it is fit for purpose (a) in §0 as the truth surface (§5) defines green, and (d) holds on every citable run. Green, under ticket 75 Q8 (b): the offline half passes and every adopter's sampled lane facts are true, with the ceiling published on the TRUTH line beside the number (ticket 83), and the cage graded through two more lane facts (ticket 86). A lane fact is one of the facts an adopter's scheduled sample records about its own cluster, today five (Flux Ready at the pinned pair, signature verified, applied revision equal, rendered objects byte-equal and Flux-owned; ticket 16); ticket 86 adds two about the cage. The ceiling is the count of scripts that can never look on the runner. Q8 was delegated: the owner answered "yes" and the assistant's reason is recorded in ticket 75.

The orgs are example consumers. The demonstration is the eco-system operating, in this order:

1. A regulator publishes a new penalty schema version. The feed is signed and tagged.
2. Renovate raises the pin in one adopter. The composition re-prices the adopter's exposure against its own size.
3. The £ crosses a band. The cage tier moves. A proposal PR opens, signed by the proposer's identity. A human merges.
4. Flux reconciles the new cage spec onto the adopter's cluster. The workload keeps running, caged tighter. The residual is on the balance sheet.
5. The twin, on its schedule, plays a dated external signal forward (the niobium headline) on the value chain, emits a scored forecast, and publishes forward intelligence the platform consumes.
6. Provenance: every step above is verifiable in Rekor and in the artefact sidecars.
7. Honesty: one command reports every claim above as pass, fail or could-not-look.

None of steps 1 to 5 ran end to end on 2026-08-27. [GAPS.md](.scratch/drift-review-2026-08-27/GAPS.md) ranks what each needed then.

Standing on 2026-09-02 (ticket 75 Q2): step 2 has fired once for real, because Renovate raised driftwood's pin and a human merged it (ticket 61). That the price did not move is a £-inputs defect owned by tickets 77 and 79, not a step-2 failure; that reading is the assistant's, delegated. Step 3 has never fired. Step 5's clock failed both of its firings. Step 4 holds for one adopter of three.

## 5. The truth surface

One command, on a schedule, in CI, is the only source any document may cite for "what works":

- It discovers every `verify*.sh` by glob and fails if any is neither run nor listed in a committed exclusions file with a reason.
- Every live tail has exactly three outcomes: observed-true, observed-false, could-not-look. Could-not-look prints as SKIP with the reason.
- Every script that asserts a live claim first asserts its substrate (`docker info`, `kind get clusters`, the Flux Ready condition) and fails loudly if absent.
- Ticket `Status:` is derived from a named check, in the way `twin grade` already derives depth from `twin/capabilities/*.yaml`.
- The number and its date are recorded on every run. A fall is a blocking event.

## 6. What is explicitly out

- **The talk and the videos** are a byproduct and a marketing tool. The running estate is the deliverable; the talk markets it, and the deck is rebuilt from the truth surface when the estate is fit. (Owner, 2026-09-02, ticket 75 Q9 and Q16: "by product / marketting tools".) This supersedes the owner's instruction of 2026-07-23 to work backwards from the talk. The byproduct line first stood here attributed to the twin map of 2026-08-12, the assistant's document; from 2026-09-02 it is the owner's. The talk and the videos stay reads of the truth surface, never the definition of done, never the clock.
- **The development-window theatre.** Principle 5 says a human merges, and it binds for the demonstration: ticket 87 protects `main` and `release/*.x` with a required review from a different identity. For the development window the assistant reviews and merges as a second identity, while the narrative says a human merges. (Owner, 2026-09-02, ticket 75 Q6: "I agree, though, for you to develop and build this. It's going to be a bit of theatre because I'm going to be making you approve and merge everything. But the narrative and talk should be that it's a human doing it, but that doesn't really work in development.") The second identity is the GitHub App `pavc-other-hand`, created by the owner on 2026-09-03 (ticket 88). The owner authors and pushes; the assistant reviews and merges as the app; the guard admits no other merge shape. The recorded end state is AI disposal: the assistant disposes of a proposal itself, inside a priced cage, and the human merge is this build's narrative, not the design's last word. (Owner, re-grill 29, 2026-08-28: "this is a stepping stone for allows the ai to do it all"; restated in ticket 75 Q6, 2026-09-02.)
- **The identity substrate** is designed and shelved for this build. (Ticket 75 Q12, 2026-09-02, delegated; ticket 90.) Artefact attestation is real: 24 of 24 signed tags verified against Rekor on 2026-09-02. Actor attestation had never been observed on a citable run by that date. So the claim this build makes is that every artefact is attestable; principle 6 keeps "every actor is attestable" as the shelved design. Ticket 90 edits §1 and principle 6 to say so and excludes the six identity scripts from the gate with a reason. The identity lane is the first thing after this map.
- **A power layer, except portability.** The eco-system constrains knowledge and prices consequences. Lock-in is treated as a priced cage: each adopter's switching cost is published in the same £, feeds are re-derivable from pins a departing adopter keeps, and exit cost sits on the balance sheet. (Owner, re-grill 38, 2026-08-28.)
- **Covert sensing.** Permanently excluded. (Twin ticket 15.)
- **Real surveillance data.** Substrates are synthetic with planted ground truth. (Twin ticket 12.)
- **The original org as the system.** `policy-as-versioned-flux` is the reference implementation of the July thesis and the audit trail. Its working parts (fan-out, notifications, OSCAL CronJob, dashboards, real apps, sunset cron) are to be lifted into the eco-system or explicitly retired, one by one, with a decision each.

## 7. Documents this supersedes, in part

Add a dated banner to each. Do not rewrite history.

- `.scratch/twin/map.md` and `.scratch/twin/spec.md`: governance is not "one enactment arm"; the estate is not "a prior to test"; the clusters are not "binned".
- `docs/ARCHIVE.md`: the hub is not research-only. It is the eco-system's own repository.
- `CONTEXT.md`: the Gate entry, "Compliant means admitted", the semver definition, and "Nothing starts a run on a clock" are rewritten in cage and schedule vocabulary.
- `.scratch/talk-spec/the-whole-model.md`: the neck and the exemptions ledger are redrawn out.
- `docs/north-star-modern-reference.md`: renamed to `docs/modern-reference-transport.md`.

## 8. Decisions made after ratification

The 41 re-grills were answered on 2026-08-28. The record is [REGRILL-ANSWERS.md](.scratch/drift-review-2026-08-27/REGRILL-ANSWERS.md). Six of the answers overrode the assistant's recommendation and three reframed the question; all are binding on any future build. The 22 reversals in Appendix C still await the owner's yes or no.

> Update 2026-08-28: all 22 reversals are confirmed. The record is the same REGRILL-ANSWERS.md.

> Update 2026-09-02: [ticket 75](.scratch/ecosystem/issues/75-grilling-what-is-this-for-the-twelve-questions.md) put the twelve questions about purpose to the owner and resolved sixteen decisions. Each carries its status, owner-reasoned, owner-instructed or delegated, under ADR-0025, which retired the word "provisional". By number:

1. Purpose is the four-purpose chain in §0 (owner-reasoned, 2026-09-02).
2. §4 is the assistant's build order; done is defined in §4's preamble (owner-instructed, 2026-09-02).
3. At least three coexisting versions bind, as three declared lines and a priced supersede, in the owner's words of 2022-03-11 (owner-reasoned, 2026-09-02; tickets 63, 84).
4. The £ is an ordinal, auditable comparison instrument, said so on every artefact; the two stale fines are corrected (delegated, 2026-09-02; ticket 79).
5. There is no gate: cages all the way down, a mutating admission controller (owner-reasoned, 2026-09-02; ticket 89).
6. A human merges binds for the demonstration; the development window is theatre with a second identity (owner-reasoned, mechanics delegated, 2026-09-02; tickets 87, 88).
7. The adopters are plausible firms, nicknames for studied real firms where needed (owner-instructed, 2026-09-02; tickets 94, 79).
8. Green is the offline half plus the adopters' lane facts, with the ceiling published (delegated, 2026-09-02; tickets 83, 86).
9. The talk is a byproduct and a marketing tool (owner-reasoned, 2026-09-02).
10. The twin may derive a probability with a model call, run inside Claude Code on the owner's machine on a local clock (owner-reasoned, 2026-09-02; tickets 92, 93).
11. The assistant decides architecture and records it; "provisional" retires (owner-instructed, 2026-09-02; ADR-0025, ticket 80).
12. Identity is designed and shelved for this build (delegated, 2026-09-02; ticket 90).
13. The currency controller is un-retired and owned (delegated, 2026-09-02; ticket 91).
14. The second identity is a machine identity for the assistant (delegated, 2026-09-02; ticket 88).
15. No date, venue or recipient for the talk (owner-reasoned, 2026-09-02).
16. The estate is the deliverable and the talk markets it (delegated, 2026-09-02).
