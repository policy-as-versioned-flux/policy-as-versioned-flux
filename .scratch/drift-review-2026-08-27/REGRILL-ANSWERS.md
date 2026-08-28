# Re-grill answers (owner, 2026-08-27)

North star: ratified ("I agree with the northstar").

| # | Id | Question | Owner answer |
|---|---|---|---|
| 1 | P006 | The Flux falsification test | Re-scope: can a publisher's signed policy be proven in force inside a consumer org, continuously, across an org boundary. Drop the drift-floor test. |
| 2 | P022 | Whose bump: global or per-org | "copy the behaviour of how say eslint linting packs are versioned, and how you can supersede, mashup, join them, republish, inner source etc". Reading: every package (publisher policy, adopter composed set) carries its own semver; a composed set that extends others is a new package with its own version; republish and inner-source are normal. |
| 3 | P029 | What emits the OSCAL risk object | Cage and procurement record, same schema. |
| 4 | P030 | Who runs verification across six orgs | Both: each org pins the platform harness and self-verifies; the hub also aggregates a full run. |
| 5 | P049 | Can adopters re-derive the publisher version | Yes: publish the tool and the corpus so any org can re-run it against its own workloads. |
| 6 | P050 | Pairwise vs full combination coverage | Run the full set. Accept the runtime cost. |
| 7 | P057 | Shape definition for witness coverage | Add the cage tier to the shape. |
| 8 | P060 | Does a re-price bump the version | Yes: a re-price is a policy release. Appetite bands and tier mapping enter the versioned subject; a feed that moves cages yields a computed bump, a signed tag, a Renovate PR. |
| 9 | P066 | Which way up: composition or the gate | Composition is the eco-system; the version gate is one consumer of it. Re-parent the maps. |
| 10 | P069 | Is the coverage exclusion file a banned ledger | No: it is disclosure, not an exemption. Keep it. |
| 11 | P070 | Does no-gate-just-cages apply to the publisher release | Yes: publish at a degraded (quarantined) tier instead of refusing. Instrument faults still refuse. |
| 12 | P072 | Is cage-spec comparison enough for the dial | No: enumerate the dial value space too. |
| 13 | P079 | Where the declared bump lives | In a versioned file in the repo, reviewed in the PR; the workflow reads it. |
| 14 | P085 | Adopter gate on a Renovate pin bump | Grade by priced impact on that org; the incoming version lands in a cage; the letter is evidence not trigger. |
| 15 | P096 | What makes a change major under cages | Keep the movement rule; attach the £ cost of every computed move to the signed evidence. |
| 16 | P106 | Removal vs loosening of an enforcement surface | Refuse total removal; loosening short of removal produces a priced delta on the balance sheet. |
| 17 | P113 | Where a human disposes | At the adopter org merge of a publisher/regulator policy PR; enforce it there; development stays permissive; price whether review happened. |
| 18 | P118 | Where composed-artefact signatures are verified | Scope cluster-side verification as real work (controller or the mo-07 OpenPGP bridge so Flux spec.verify bites). |
| 19 | P121 | Control id key | Key on (source, id); wire value stays the bare catalogue id. |
| 20 | P123 | Unimplemented baseline controls (holes) | Price the holes: each carries a £ exposure; the composed artefact carries priced holes and a total; refusal is a £ threshold against appetite. |
| 21 | P133 | Who decides a cage tier | The twin computes the tier under the org perspective; the estate war-gamer enacts it as a PR. This is the seam. |
| 22 | P141 | Rejection ledger | "Flood guard with a half life. Point in time rejection does not mean never." A declined proposal decays and re-raises; it is not a register of accepted risk. |
| 23 | P144 | Can an adopter be stricter on its own authority | Yes: the overlay carries a tier floor the adopter sets, tighten-only. |
| 24 | P145 | Mutate-before-mutate ordering | Declare intra-set ordering in the composed artefact, or write members so order cannot matter. Mutate-before-validate stays out of scope with a citation. |
| 25 | P149 | Bespoke control ids | Allow bespoke ids in a namespaced form; they count as holes and get priced. |
| 26 | P152 | Publisher discovery | Add a discovery record beside the party artefact; a party may declare itself a publisher. |
| 27 | P157 | Pre-existing ungoverned namespaces | Price every recorded one: a priced hole in the evidence, proportionate to the workloads inside, growing over time. |
| 28 | P174 | Unlabelled pods | Default the strictest cage to any pod that claims nothing (MutatingPolicy at CREATE); infrastructure claims an infra cage explicitly. |
| 29 | P175 | What stops a machine change reaching main unreviewed | "Assume a sig check that ids a different entity but this is a stepping stone for allows the ai to do it all." Reading: author and merger must be different identities for now; the end state is an AI allowed to dispose inside a priced cage (see 37). |
| 30 | P179 | Test seams | Re-open: one seam per eco-system joint (composition, publisher release, adopter gate, cage tier move, feed fetch, twin-to-estate tier handoff). Python stays. |
| 31 | P182 | Twin subjects | Adopter orgs (driftwood, tuppence, ludlow) become the primary subjects; the real firms stay as the backtest corpus. |
| 32 | P191 | Unpriced structural blast radius | Keep two outputs; an unpriced hit still gets a cage consequence defaulted from appetite. |
| 33 | P192 | Whose £ | One currency, many perspectives: one unit; each party prices under its declared perspective; no perspective privileged. |
| 34 | P193 | Who picks the point on the trade-off curve | Policy selects the point; the twin keeps emitting the curve; the pick is codified and provenanced. |
| 35 | P194 | The unpriced register | Keep the derived boundary; every register entry carries a cage consequence from appetite. Unpriceable never means unenforced. |
| 36 | P201 | Misuse catalogue | Re-open against the eco-system: publisher gaming its feed price; adopter buying intel on a rival; regulator fine data mispriced downstream with no recourse; the twin valuation used against an org in negotiation. |
| 37 | P202 | Does the twin act or only propose | The twin acts inside a priced cage; propose-only is the outermost setting; Article 22 floor for significant decisions about people. |
| 38 | P204 | Power layer | Make portability a priced cage: publish switching cost in £; feeds re-derivable from pins a departing adopter keeps; exit cost on the balance sheet. |
| 39 | P208 | Demo subjects | "Demos stay as model and tooling Evals. Our demo orgs get a digital twin each." Reading: the real-firm beats (Netflix, Royal Mail, Intel) are kept as evals of the model and tooling, not as the demo; each of driftwood, tuppence, ludlow gets its own twin. |
| 40 | P209 | The Aug 5 scope cut | Yes, itemise it beside the north star; anything the eco-system needs goes back in. (Action for the assistant.) |
| 41 | P211 | The Aug 10 bundle | Keep Cedar (promote to a live policy-composition question) and the tool-call boundary guard, re-expressed as a cage on the twin with a spec and a price. Item 1 moot per answer 1. |

## Where the owner overrode the recommendation

- 6 (P050): run the full combination set, not a sample.
- 12 (P072): enumerate the cage dial value space too, not only cage-spec comparison.
- 2 (P022): version like ESLint shareable configs. Every package versions itself; composed sets are new packages.
- 22 (P141): the rejection ledger is a flood guard with a half life. Rejections decay and re-raise.
- 29 (P175): author and merger must be different identities for now; the end state allows the AI to dispose inside a priced cage (37).
- 39 (P208): the real-firm beats become model and tooling evals; each demo org gets its own twin.

## Actions the assistant owes from these answers

- 40: itemise the 2026-08-05 scope cut and put it back in front of the owner.
- 1: write the re-scoped Flux test as a ticket.
- 9: re-parent the maps so composition is the eco-system.
- 41: raise Cedar as a live policy-composition question.

# Reversal answers (owner, 2026-08-28)

| # | Id | Reversal | Owner answer |
|---|---|---|---|
| 1 | P001 | Hourglass neck | Reverse: redraw with no neck; Flux is the distribution arm; exemptions ledger node removed. |
| 2 | P002 | Six-org graph | Reverse: pins as explicit crossing edges; explode at least two institutions asymmetrically. |
| 3-4 | P010, P012 | Twin scope: demo slice vs full depth | Confirm full depth; mark the narrowing rejected; de-duplicate the record. |
| 5 | P028 | Can some workloads not run at all | Reverse: no refusal; the cage tightens until untenable; procurement is the primary path and emits the risk object before deployment. |
| 6 | P031 | Prediction markets | Reverse the no-estate-work half: ship market price moves as a sixth signed feed; markets still never price a control. |
| 7, 14, 15 | P086, P135, P140 | Schedules | "schedule the data gathering that can run without an LLM, and then give me claude-code skills that can be run to complete any necessary reasoning over the results of data". Reading: deterministic fetch/re-price/proposal steps run on a schedule (no LLM); judgement steps are packaged as Claude Code skills a human runs over the gathered results. PR stays the unit of adoption. |
| 8 | P112 | Where ticket code lands | Reverse: code lands in the real repo the ticket names, pushed; local-only tickets are reopened. |
| 9-10 | P124, P128 | Baseline selection and widening | Confirm both: per-adopter selection driven by its regulators, visibly priced; widening is priced not refused; no override flag. |
| 11-12 | P129, P132 | Unlabelled pods | Confirm: a MutatingPolicy defaults the strictest cage at CREATE; replaces the governed-namespace deny gate. |
| 13 | P134 | What the proposer PR edits | Reverse: the tier is declared in the signed composed artefact and rendered down to the label; the proposer edits the declaration. |
| 16 | P142 | Proposer commit signing | Reverse: sign the proposal commit with the workflow Actions identity; add it to the expected-identity regexp. |
| 17 | P143 | Price selects Deny | Reverse both: add the bottom rung below quarantine; an unknown tier label fails closed to the strictest cage. |
| 18 | P158 | Who may add a governed namespace | Reverse: the proposer may open a PR adding governed:true; a human merges. |
| 19 | P165 | Unsigned commits to unblock | Reverse the precedent: never trade a signature to unblock; record in ADR-0001; the two tags stay as the honest record. |
| 20 | P177 | Insurance and risk transfer | Reverse: build the policy structure (attachment, limit, exclusions; transfer priced off TVaR; a seventh party publishing a signed quote). |
| 21 | P203 | Policy-as-versioned-dependency narrowed | Reverse the narrowing: versioned policy is the spine; non-machine-enforceable levers become priced cages. |
| 22 | P207 | Forecast book | Reverse: build it out as the marketplace credibility instrument (continuous scoring, reliability diagrams per publisher, wider claim scope). |

All 22 reversals confirmed on 2026-08-28. One nuance: reversals 7, 14 and 15 are confirmed in the owner's own shape (schedule the LLM-free data gathering; package reasoning as Claude Code skills).

## Correction to the report (from the itemisation the owner asked for in re-grill 40)

`AUG-05-CUT.md` found that the "20-from-16 scope cut" of 2026-08-05 was not a scope cut. `20 <- 16` was a blocking-edge change in the breakdown's own notation. The republish went 72 to 77 tickets (six merges, five splits, six additions, six edge changes), cites 92 of 93 user stories, and narrowed nothing except by relocation. REPORT.md §6.10 and §8 are corrected accordingly. Two real follow-ups survive: split published ticket 66 and relax `66 <- 65` (the propose-only PR channel is gated behind the unmeasured Flux verdict), and give spec story 2 (git-is-truth) an owning ticket. Publishers, a feeds marketplace and adopter orgs appear nowhere in the twin spec or its 92 tickets; that is a north-star gap, not a cut.
