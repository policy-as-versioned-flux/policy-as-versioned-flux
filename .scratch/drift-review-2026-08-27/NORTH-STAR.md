# North star — proposed re-baseline, for the owner's ratification

Status: RATIFIED by the owner 2026-08-27 ("I agree with the northstar"). Re-grill answers are recorded in REGRILL-ANSWERS.md. Where a sentence rests on something you said, the date is given. Where it rests on my judgement, it says so.

## 1. The one sentence

**A loosely coupled eco-system in which publishers, regulators and intelligence providers ship signed, versioned artefacts, adopter organisations compose those artefacts into their own policy, a platform enacts that policy as priced cages, and every actor is attestable. The orgs are example consumers that demonstrate the whole eco-system operating.** (Owner, 2026-08-27, restated.)

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
2. **Everything is always caged.** A workload, a human, a device, a model action and the twin itself each run inside a cage. The cage spec is the only variable. The £ selects the spec. The bottom rung is "too expensive to run or not functional". There is no gate. (Owner: 2026-08-20, 2026-08-22.) That a refusal is therefore the bottom rung reached by the £, rather than a separate mechanism, is my reading, not your words.
3. **One £ currency, proportionate to the org.** Every impact and every candidate response is priced in one currency so a pay rise, a hardening control, a cage tier, an insurance transfer and a strategic play are comparable. The price is proportionate to the organisation: its turnover, its customers, its regulators, its declared appetite. Regulator penalties enter as published schemas applied to the adopter's own size. (Owner: 2026-07-23; "its proporiate to the org right?... cost per customer... percentage of global revenue", 2026-08-19.)
4. **Policy is a versioned dependency, all the way up and down.** Regulators, intelligence providers and the platform each version and sign what they publish. Adopters pin by tag and commit, compose from several parents like class inheritance, restate only stricter, and bump only by reviewed PR. Semver is computed from measured verdict movement, never declared. Older lines are patchable. COTS is wrapped in a shim so it wears a version too. (Original thesis; owner 2026-08-20 to 22.)
5. **Intelligence re-prices on a clock; enactment happens only by reviewed PR.** Feeds refresh, the twin re-forecasts, cages re-price, and proposals open, all on a schedule. A human merges. Nothing timed ever changes a verdict on its own. (ADR-0010; owner: "continuous refreshing", 2026-08-19. This reverses the "nothing timed, ever" rule I wrote into three repos and CONTEXT.md.)
6. **Every actor is attestable, and the record is falsifiable.** Every artefact carries a signature that says what it does and does not assert. Agent signatures attest the absence of a human. Forecasts are pre-registered and scored against reality under proper scoring rules. A green that could not look is a red. (Owner: 2026-07-23, 2026-08-05; twin decision tickets 14, 21.)
7. **Flux is the distribution arm, held integral unless disproven.** Flux fans the signed policy line out to consumers, prunes on retirement, and heals drift. The falsification test stays open and honest. (Owner: 2026-07-23, 2026-08-05.)

## 4. What the demonstration must show

The orgs are example consumers. The demonstration is the eco-system operating, in this order (my proposal, derived from the twin's demo-slice sequencing and your August 19 words):

1. A regulator publishes a new penalty schema version. The feed is signed and tagged.
2. Renovate raises the pin in one adopter. The composition re-prices the adopter's exposure against its own size.
3. The £ crosses a band. The cage tier moves. A proposal PR opens, signed by the proposer's identity. A human merges.
4. Flux reconciles the new cage spec onto the adopter's cluster. The workload keeps running, caged tighter. The residual is on the balance sheet.
5. The twin, on its schedule, plays a dated external signal forward (the niobium headline) on the value chain, emits a scored forecast, and publishes forward intelligence the platform consumes.
6. Provenance: every step above is verifiable in Rekor and in the artefact sidecars.
7. Honesty: one command reports every claim above as pass, fail or could-not-look.

None of steps 1 to 5 runs end to end today. GAPS.md ranks what each needs.

## 5. The truth surface

One command, on a schedule, in CI, is the only source any document may cite for "what works":

- It discovers every `verify*.sh` by glob and fails if any is neither run nor listed in a committed exclusions file with a reason.
- Every live tail has exactly three outcomes: observed-true, observed-false, could-not-look. Could-not-look prints as SKIP with the reason.
- Every script that asserts a live claim first asserts its substrate (`docker info`, `kind get clusters`, the Flux Ready condition) and fails loudly if absent.
- Ticket `Status:` is derived from a named check, in the way `twin grade` already derives depth from `twin/capabilities/*.yaml`.
- The number and its date are recorded on every run. A fall is a blocking event.

## 6. What is explicitly out

- **The talk and the videos** are reads of the truth surface, never the definition of done, never the clock. (Twin map, 2026-08-12, kept.)
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

The 41 re-grills were answered on 2026-08-28. The record is REGRILL-ANSWERS.md. Six of the answers overrode the assistant's recommendation and three reframed the question; all are binding on any future build. The 22 reversals in Appendix C still await the owner's yes or no.
