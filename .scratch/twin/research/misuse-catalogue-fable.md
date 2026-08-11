# The Misuses You Haven't Catalogued

*An adversarial read of the organisational-twin misuse catalogue. Written by someone who has not seen your code and does not want to.*

---

## Intro

Your eight entries share a shape. Each is a **bad actor** doing a **named bad thing** to an **employee** using a **forbidden datum**, and each is blocked by a constraint on *representation* — what can be stored, what can be inferred, what can be produced, what leaves the tenant. That is a coherent theory. It is also a very particular one, and it has a footprint you can see from orbit.

The misuses below are the ones that fit *outside* that shape: harms that need no forbidden data, harms to people who don't work for you, harms produced by the transparency machinery itself, harms with no actor at all, and harms produced by the constraint mechanism working exactly as specified. Several are not blocked at all. Two of them, I think, are load-bearing enough that the design would change if you took them seriously.

I mark confidence per finding: **high** (I'd defend this in a room), **medium** (plausible mechanism, contested severity), **speculative** (worth a paragraph in the catalogue, not a redesign).

---

## Theme A — Harms that need no forbidden data

### A1. Exit-cost asymmetry: the twin knows exactly who cannot afford to leave
**(a)** *Price each person's ability to quit — from visa dependence, mortgage-stage compensation history, caring-shaped working patterns, location, and single-employer skill specificity — and extract accordingly from the ones who are trapped.*

**(b)** Nothing here is Article 9. Compensation, working patterns, location and knowledge-specificity are all first-class permitted fields; the ladder waves them through because each feeds a named retention scenario someone will act on. Crucially, this **defeats your headline block on pay suppression**. The grievance→insider-risk path prices suppression back into the firm's ledger *only for people who have the option to become a problem*. The twin's entire competence is telling you which people those are. For the rest, the counter-price is near zero and the model will say so, in £, with provenance. You have built the discovery mechanism for the exact population where your safeguard does not apply.

**(c)** Proposed: forbid modelled exit-cost/mobility from entering any compensation, workload or assignment scenario as an input — it may only appear as a *risk to the person*, never a *lever on them*. Honest caveat: this is hard to enforce because attrition probability is the same quantity wearing a different hat, and attrition probability is legitimately central. You may only be able to make it visible: publish, per scenario, the correlation between recommended treatment and modelled mobility. If the twin is systematically recommending less for those who can leave least, that should be a first-class red flag on the output, not something a researcher discovers in 2031. **Confidence: high.** This is the strongest genuinely-unblocked employee harm I found.

### A2. Deliberate bus-factor cultivation — the twin makes golden handcuffs computable
**(b)** You model key-person concentration to *reduce* it. The same model, read backwards, tells you how to *create* it: route critical knowledge toward the person you want locked in, decline to cross-train them, and their leverage-to-leave collapses while their cost-to-replace rises. No individual-level output is required — the component-level concentration figure is enough. Advisory-only is no help; a human reads it and assigns work.

**(c)** No constraint exists and I can't design a good one, because "who should own this component" is the twin's core legitimate use. Best available: make concentration *changes* attributable to a decision and reviewable — a rising bus-factor should generate a challenge-register entry, not a silent metric drift. **Confidence: high** on the mechanism, **medium** on how often anyone is cynical enough to do it deliberately. The accidental version is more common and equally harmful.

### A3. "De-risking key-person concentration" is a fully sanctioned name for removing an inconvenient expert
**(b)** Document them, cross-train around them, then they are — by the model's own numbers — cheap to lose. The £ engine will price this play favourably and the record will show a prudent resilience investment. Entry 2 blocks *justifying* layoffs; it does not block *manufacturing the conditions* under which a layoff needs no justification. The record will look better than the truth, which is worse than no record.

**(c)** None available. Honest admission: the twin cannot distinguish resilience engineering from targeted de-skilling, because they are the same actions in a different order with a different intent, and intent is not in your schema. **Confidence: high.**

### A4. Whistleblower and leak attribution
**(b)** Entry 5 bars knowledge edges from *retrospective individual attribution* — scoped, I'd bet, to operational incidents. A leak is a who-knew-what problem, and your graph is a who-knew-what index with timestamps and versioning. Intersect "who had the knowledge edge" with "when the version changed" and your suspect set is small. This is a forensic capability you did not intend to build and it is the single most chilling thing in the system for anyone considering a protected disclosure.

**(c)** Widen entry 5: knowledge edges inadmissible to *any* scenario whose output is a set of named individuals smaller than the whole cohort, for *any* retrospective purpose, including confidentiality, leak, IP and conduct. And say so publicly, because the deterrent effect depends entirely on people believing it. **Confidence: high.** Cheap to fix; expensive to leave.

### A5. Cohort-of-one — "aggregate over individual" is structurally impossible for your best data
**(b)** The necessity rung says prefer cohort over person. But the Wardley backbone's most valuable edges are *person↔component*, and a component's maintainer set is frequently one. Genesis-stage components in particular are near-definitionally one person. "Cohort" and "the individual" collapse for exactly the parts of the graph the twin exists to reason about. This isn't an implementation slip; it's a contradiction between the necessity principle and the value proposition.

**(c)** Enforce a k-threshold on every person-derived output and *refuse to render* below it — with the refusal itself logged, so the org can see how much of its graph is unrenderable. That number is the honest measure of how personal this system actually is. Expect it to be uncomfortable. **Confidence: high.**

### A6. Health and disability inference from permitted working-pattern sensors
**(b)** Absence shape, hours drift, handover frequency. No Article 9 field required; the inference lives in the behavioural overlay, which is gated but not absent, and the gate protects against *access*, not against the gatekeeper. **Confidence: medium** — partially blocked by the overlay gating, fully unblocked for whoever holds the key.

---

## Theme B — The outsiders (your catalogue's largest blank)

Seven of eight entries concern employees. The twin senses supply chain, sanctions, geopolitics and competitors. Nobody outside the payroll appears in your harms list at all.

### B1. Supplier squeeze — pricing exactly how much a small counterparty depends on you
**(a)** *Compute each supplier's revenue concentration, switching cost and cash-cycle fragility, then extract the maximum margin and payment terms they cannot refuse.*

**(b)** Nothing blocks it. Nothing addresses it. The perspectival-£ doctrine actively **legitimises** it: the supplier's harm is definitionally not in your currency, and the offered remedy — "they can instantiate their own twin" — is a joke when applied to a six-person subcontractor. This is not a fringe case; it is the highest-ROI use of the supply-chain sensing you have already built, and it is what a competent CFO will do with it in week two.

**(c)** Proposed: a counterparty-dependency red line in the universal floor — recommendations may not use a counterparty's dependence *on you* as an input to price or terms toward them. Honest assessment: no commercial deployer will accept this, and if the floor is optional it isn't a floor. The realistic outcome is that you name it in the catalogue and admit it's unblocked. **Confidence: high, and I think this is the entry you'd least like to write.**

### B2. Perspectivalism as an externality laundromat
**(b)** Every cost borne by a non-owner is, by construction, outside the currency. "Instantiate your own twin" converts an ethical problem into a capital requirement: modelling capability accrues to whoever can already afford it, so the design is *regressively* distributive. The union, the subcontractor, the affected community and the applicant all lack the data access, the expertise and the money. Perspectivalism doesn't solve the asymmetry; it renames it "pluralism" and stops looking.

**(c)** None that preserves the design. The honest move is to say in the catalogue: *perspectival £ is not a neutrality guarantee, it is a statement that this instrument serves its purchaser, and its harms to non-purchasers are unpriced by design.* Optionally: require every scenario to render an unpriced-externalities panel — named parties bearing cost outside the currency, unquantified. Not a fix, but it stops the number looking complete. **Confidence: high.**

### B3. Acquisition-target hollowing / acqui-poaching
**(b)** Build an external twin of a target from public signals and structural inference, identify the four people who *are* the company, hire them, don't buy it. Entry 8's tenancy boundary protects *overlay data*, not *inference from outside*. Structural topology of a target is substantially reconstructable from public artefacts, and your method is fully published. **Confidence: medium-high.**

### B4. Job applicants and the pre-hire structural read
**(b)** No employment relationship, so no HR safeguard applies, and the applicant has no standing in the challenge register. Two flavours: inferring what a candidate knows from their current employer's topology, and — nastier — selecting *for* candidates who will become bus-factor-1 in a component you want locked down. **Confidence: medium.**

### B5. Procurement-mandated twins — surveillance conscripted down the supply chain
**(a)** *"Onboarding to our twin is a condition of contract" — and each tier passes it to the next.*

**(b)** Nothing in the design prevents the twin becoming a contractual requirement imposed on parties with zero negotiating power, who then must expose their own person↔component topology to a customer. Every consent argument in your DPIA evaporates when the data subject's employer had to agree to keep the contract. This is precisely how SBOM mandates, ESG questionnaires and Cyber Essentials propagated, so the base rate is ~1.

**(c)** Licence-level term: the twin may not be made a condition of commercial engagement, and tenants may not require counterparty instantiation. Enforceability: poor, but a licence term at least makes it a breach rather than a business model. **Confidence: high on the mechanism, and this one is a *distribution* problem, not a *feature* problem, which is why it isn't in your catalogue.**

### B6. Dual-use chokepoint mapping
**(b)** A model that senses supply chain, sanctions and geopolitics, and identifies where a value chain is most fragile, is a targeting package for anyone who wants the chain to break. Full method transparency lowers the bar for reproduction. **Confidence: speculative on likelihood, high on severity.** Worth one paragraph and an export-control question.

---

## Theme C — Weaponising contestability and transparency

### C1. Human signatures create a named-target list
**(a)** *Every judgement carries an accountable human name, so every judgement carries a person to harass, sue, subpoena, brief against or discipline.*

**(b)** This is a direct, designed-in consequence of your accountability model. Signature-as-accountability was chosen to prevent laundering; its side effect is a doxxing surface with provenance. Combined with an open challenge register, it enables targeted campaigns against named analysts, and internally it enables punishment of whoever signed the claim a director disliked.

**(c)** Signatures should bind to a *role and an organisation* by default, with individual identity resolvable only through a named process with a threshold and a log of who resolved it. You lose nothing in accountability — the org is accountable — and you remove the target. **Confidence: high. This is a clean, cheap design fix and I'd take it today.**

### C2. Signature chilling — the record drifts toward the anodyne
**(b)** No bad actor required. If signing an unpopular-but-true claim is career-costly, the population of signed claims selects for the uncontroversial. The twin's evidence base degrades in exactly the direction that makes it useless: high confidence about things nobody disputes. **Confidence: high**, and it compounds C1 — the fix for C1 is also the fix for this.

### C3. Contestation flooding
**(b)** "Anyone can dispute an edge" plus a world in which generating ten thousand plausible disputes costs one afternoon and an API key. Two failure modes: the register drowns, or the org quietly introduces standing requirements and contestability becomes theatre with a nicer UI. Bad-faith challenge is also a harassment vector against a specific signatory (see C1).

**(c)** Rate-limits and staking are the obvious answers and both are regressive — they price out exactly the low-resource challengers contestability exists for. Least-bad: unlimited *filing*, triaged by a published rule, with the triage decisions themselves contestable one level up and no further. Admit the recursion terminates arbitrarily. **Confidence: high on the attack, medium on the mitigation.**

### C4. Contestation as free discovery
**(b)** A litigant, journalist or competitor files challenges not to correct the model but to compel the organisation to *articulate on the record* what it believes, knew and when. Every response is an admission with a signature and a timestamp. You have built an out-of-court deposition service and made it self-serve. **Confidence: high.**

### C5. The published constraint set is an intelligence product
**(b)** Declaring your red lines publicly declares what you will not do — which is a bargaining disclosure, not just a moral one. A counterparty who knows you have red-lined a given escalation negotiates against a known bound. Against a union this may be fine and even good; against a hostile counterparty it is unilateral. **Confidence: medium.** Note the tension honestly rather than pretending publication is costless.

### C6. Insurance and the foreseeability trap, from the insurer's side
**(b)** An insurer who reads your model prices you on your worst modelled scenario and denies claims on anything you modelled and didn't mitigate. **Modelling a risk becomes the act that voids cover for it.** No constraint touches this because it's an external party's rational response to your transparency. See D2 for where this leads. **Confidence: high.**

### C7. The regulatory ratchet
**(b)** Once one firm in a sector runs a twin, "reasonably foreseeable" ratchets upward for the whole sector. Modelling capability becomes a compliance floor set by whoever can afford it — an anti-competitive effect achieved without anyone intending it, and a moat for large deployers. **Confidence: medium-high.**

---

## Theme D — Legal and evidentiary

### D1. A versioned, signed, £-ranked register of known risks is the plaintiff's dream document
**(b)** "You priced this at £X, you knew on this date, you signed it, and you chose the £Y-cheaper branch." That is the Ford Pinto memo, generated automatically, cryptographically attested, and preserved forever by design. Nothing blocks it because it is the design working. **Confidence: high**, and it is the reason a general counsel kills this project.

### D2. The perverse consequence: strategic non-modelling — and your ladder helps
**(a)** *The rational owner scopes the twin to exclude exactly the scenarios most likely to generate liability, so the system models the commercially interesting and is structurally silent on the morally serious.*

**(b)** This is D1's inevitable corollary, and here is the sharp part: **the sensor admission ladder provides the principled-sounding vocabulary for it.** Rung one says a sensor must feed a named scenario someone will act on. If you decline in advance to act on safety, discrimination or environmental harm, you may — correctly, by your own rule — refuse to sense them. A constraint designed to prevent surveillance overreach becomes the certified mechanism of deliberate ignorance. The twin then confers *documented diligence* on precisely the domains where it looked hardest at nothing.

**(c)** Two partial moves. First, a mandatory scenario floor: a declared minimum set of scenario classes (harm-to-persons, discrimination, environmental, safety) that a conforming deployment *must* run, with the **scope declaration itself published and versioned** so the omissions are visible in git rather than absent from it. Second, invert the ladder for harm-detecting sensors: purpose limitation restricts *behavioural* sensing of people, it should not be usable to refuse *aggregate* sensing of harm to people. Honest caveat: neither survives contact with a legal team that treats non-adoption as an option — the deployer just doesn't conform, and no one can tell from outside. **Confidence: high. I'd rank this the single most important missing entry.**

### D3. Privilege laundering
**(b)** Run the uncomfortable scenarios under legal advice and the whole apparatus becomes privileged and undiscoverable. Contestability dies at the privilege boundary, silently, and the public-facing twin is the sanitised remainder. This is the standard corporate manoeuvre and the design has no answer. **Confidence: high.**

### D4. Agent signatures as a liability firewall
**(b)** You designed "agent signature attests the absence of human involvement" as an honesty mechanism. Read by a defence lawyer, it is an attestation that *no human is accountable for this artefact*. Article 22 and advisory-only address the *decision*; they do not address the *analysis* that made the decision inevitable and that no one signed. Deniability, cryptographically attested. **Confidence: medium-high.** Mitigation: every agent-signed artefact must have a human-signed *commissioning* record — someone owns the question even if nobody owns the answer.

### D5. Retention and erasure — an immutable versioned graph versus Article 17
**(b)** Git forgets nothing. A person's 2026 bus-factor score, modelled grievance and attrition probability persist through re-orgs, TUPE transfers and acquisitions, queryable in 2036. And the twin is an **asset that transfers on sale** — consent given to employer A is now held by acquirer B for purposes the subject never saw. "Everything versioned in git" is a commitment made without costing its data-protection obligations, and the legal-hold mirror image is equally unfunded: an org under investigation must now preserve every scenario execution, and a deleted branch becomes spoliation. **Confidence: high, and this is the most concretely legally exposed item in the whole list.**

**(c)** Person-linked overlay data cannot live in the immutable substrate — it needs a separate, erasable store with the graph holding only tombstoned references, which does mean historical scenario executions become non-reconstructable and *that is the correct trade*. Say so out loud; reconstructability of person-level analysis is not a virtue.

---

## Theme E — The symmetry you designed in

### E1. The union twin is a strike-optimisation engine
**(b)** Perspectivalism explicitly permits it. In the union's £, the recommendation is: withdraw labour at the maximum-leverage node, at the moment of peak supply-chain fragility. That is *the same computation* the firm's twin performs on suppliers, and by your own doctrine it is equally legitimate. I think it largely is. But the symmetry is not symmetric in consequences: the same engine, in an activist's hands, selects the node whose failure causes maximum *third-party* harm — the hospital supply, the water treatment dependency — and there is no reason the maximum-leverage node and the maximum-public-harm node should differ. Your universal floor would need to bind the union's twin too, which means someone must enforce a floor on parties who did not buy the product.

**(c)** Honest admission: the floor is unenforceable on instantiations you don't operate, and the design's answer to legitimacy ("everyone can have one") is also its answer to why it can't govern them. **Confidence: high on the mechanism, and the project should state its position rather than let the symmetry stand as an unexamined virtue.**

### E2. The union twin makes the union a surveillance operator of its own members
**(b)** To model its own perspective the union needs person-level data the employer holds and it doesn't — so it collects it from members. You have exported the surveillance problem to the party the Article 9 constraint was protecting, and the union has no DPIA capability, no sensor ladder and no gating overlay. **Confidence: medium-high. This one genuinely surprised me and I think it's the sharpest thing in this theme.**

### E3. Individual twins teach everyone that irreplaceability is the winning move
**(b)** An employee who models their own indispensability learns exactly when to make a demand and what it's worth. Entirely rational, individually. Collectively it means both sides of the employment relationship are now optimising the bus factor in opposite directions with the same tool, and the twin has converted a latent tension into an explicit, quantified contest. **Confidence: medium**, but it's the most interesting second-order effect on the list.

---

## Theme F — Second-order and political

### F1. Ensemble stuffing — pluralism as an attack surface
**(a)** *You no longer need to win the argument; you need to get your world-model into the ensemble, and the trade-off curve widens toward your preference.*

**(b)** The rival-world-model ensemble is presented as epistemic humility. It is also a **voting system**, and voting systems are gameable. Whoever curates the ensemble sets the curve's width; whoever adds a model shifts the default. Internal factional conflict migrates from "which strategy" to "which world-model gets admitted" — a fight conducted in technical vocabulary, in a forum with no politics in it, which is the ideal terrain for whoever is most fluent. Same attack on the graph itself: **the edge nobody adds is the risk that doesn't exist.**

**(c)** Publish ensemble membership with its sponsor, and require that admitting a model is itself a contestable, signed act with a stated rationale. Doesn't stop it, makes it legible. **Confidence: high. This is the most novel technical finding here and I don't think it's in your model at all.**

### F2. Non-verdictive output launders authority rather than reducing it
**(b)** You believe a trade-off curve with a marked default is safer than a single answer. For automation bias it is *worse*. Taking the default is unfalsifiable prudence ("we followed the recommendation"); departing from it is documented courage ("we exercised judgement against the model"). Both are alibis. The curve supplies the appearance of choice and the default supplies the authority, and the decision-maker gets to keep whichever they need afterwards. **Confidence: high**, and entry-level "responsibility laundering" as usually written doesn't capture this — the laundering is *enabled by the safeguard*, not despite it.

### F3. The £ common currency is a selection pressure on what kinds of value survive
**(b)** Once everything competes in one currency, functions whose value is legible in £ (efficiency, loss-avoided security) systematically defeat functions whose value isn't (care, accessibility, culture, long-horizon research, anything with a twenty-year payoff). No bad actor; this is what a common currency *does*. The design's proudest feature is a quiet ideological commitment about which goods are real. **Confidence: high.**

### F4. Compliance theatre
**(b)** "Reuse re-passes the ladder plus a fresh DPIA" — self-assessed, self-approved, by the party that wants the reuse. Nothing external audits a DPIA. **Confidence: high**, low novelty, one line in the catalogue.

### F5. The twin is the highest-value exfiltration target in the organisation
**(b)** It is the org's own kill-chain map, dependency graph, key-person list and unmitigated-risk register in one signed artefact. Who models the twin's bus factor? **Confidence: high**, and it's mildly embarrassing that a resilience tool doesn't appear in its own graph.

---

## Theme G — Harms with no bad actor

### G1. Bus-factor-1 as a documented career prison
**(b)** The system produces a defensible, provenanced reason not to move someone. Under full transparency they can *read it*. And the remedy — cross-training — is the removal of their only leverage, so their resistance to the fix is rational and will be read as obstruction. There is no consenting way through this. **Confidence: high.**

### G2. The twin makes knowledge hoarding rational and measures the destruction it causes
**(b)** If knowledge edges are recorded and concentration is valuable, helping a colleague reduces your differentiation. Your Goodhart doctrine — prefer sensors where gaming *is* the desired behaviour — fails here: gaming a knowledge-spread sensor means *appearing* to spread knowledge (documents nobody reads, pairing sessions nobody learns in). The observable and the good come apart cleanly, and the observable is cheaper. **Confidence: high.**

### G3. Labels that cause the thing they name
**(b)** Flight risk produces flight; modelled grievance, read by the subject, becomes grievance. Under full transparency the subject sees their own scores. Self-fulfilment is not a bug in the sensing, it's a property of telling people what you predict about them. **Confidence: medium-high.**

---

## Theme H — The absence of data as an alibi

### H1. No protected-characteristic data means no disparate-impact audit
**(a)** *Structural unrepresentability of Article 9 data doesn't prevent discrimination — it prevents you from detecting it.*

**(b)** Disparate impact requires no protected field to *occur* and requires one to be *measured*. By making special-category data structurally unrepresentable you have made your own fairness auditing impossible, while acquiring the strongest-sounding and most misleading defence available: "we cannot discriminate on X, we have no field for X." That sentence will be said to a tribunal and it is false. This is a well-known fairness/privacy tension and the design has picked one horn without noting the other exists.

**(c)** A sealed, separately-governed audit channel: protected attributes held by an independent party, joined only for aggregate impact testing, never returned to the graph, results published as pass/fail with effect sizes. This is genuinely hard and genuinely necessary, and "we can't so we won't" is not an answer you can give twice. **Confidence: high. Top-five material.**

### H2. "Structurally unrepresentable" is a claim about the schema, not the system
**(b)** Free-text evidence, attached provenance documents, challenge-register prose and rationale fields will contain Article 9 data within a fortnight of real use, because humans type. Anyone who has operated a "do not put PII in this field" field knows the outcome. **Confidence: high**, mitigation weak (egress scanning catches the careless, not the determined, and generates its own surveillance).

---

## Theme I — Attacks on the constraint mechanism itself

### I1. Removing forbidden options *before* optimisation makes the constraint set unauditable
**(a)** *The system cannot show you what it refused to consider, so you cannot tell a correct exclusion from a convenient one.*

**(b)** Pre-optimisation removal is the wrong sequencing. An operator can exclude a commercially inconvenient option under cover of the ethical floor and the record shows only an absence. Worse, you lose the most valuable audit signal in the whole system: **how attractive the forbidden option was.** A constraint that never binds is decoration; a constraint that binds hard and often is doing real work and its holder deserves to know. Right now you can't tell which you have.

**(c)** Price the forbidden options, mark them `FORBIDDEN`, exclude them from selection but retain them in the record with their £ and their excluding constraint. The register then shows the temptation and its magnitude. Cost: you have now written down, in a discoverable artefact, exactly how much money you left on the table by not doing the unconscionable thing — which is D1 again, sharpened. **That trade-off is real and you should make it deliberately rather than by default.** **Confidence: high. Concrete, fixable, and I think currently invisible to you.**

### I2. Constraint-adjacent optimisation — deleting the option displaces the paperclip, it doesn't remove it
**(b)** Forbid dismissal, the optimiser finds constructive dismissal. Forbid redundancy, it finds reorganisation. Forbid the surveillance sensor, it finds the structural proxy (see all of Theme A). Hard constraints create a boundary and optimisers are boundary-seeking; the nearest permitted point to a forbidden optimum is *usually still the harm*, minus the name. **Confidence: high.**

**(c)** Constraints must be stated over *outcomes for people*, not over *option labels*. Much harder to specify, and I don't have a clean formulation — but a catalogue that doesn't note this is claiming a safety property it doesn't have.

### I3. Who audits "universal"? Jurisdiction shopping and floor capture
**(b)** "A universal legal/ethical floor" — universal per whom, ratified by whom, revised by whom? If the vendor writes it, the vendor is a private legislature. If a standards body writes it, the largest deployers capture it, as they always do. If the customer writes it, it isn't a floor. And a multinational instantiates the tenancy in the jurisdiction with the most convenient legal minimum, which is not a hypothetical, it is Tuesday. **Confidence: high.**

### I4. Constraint erosion by ratchet
**(b)** Every individual relaxation is defensible in its scenario; the ratchet turns one way; the version history records it faithfully and nobody reads version history. **Confidence: high**, and the mitigation is cheap: a periodic mandatory diff-review of the constraint set as a standalone artefact, not as a scenario byproduct.

### I5. Minimal declaration
**(b)** Nothing described audits whether a deployer's declared red lines are meaningful. A perspective may declare exactly one, satisfy the schema, and pass. **Confidence: high**, trivially fixable by conformance levels, and conformance levels are then gamed, so: partially fixable.

---

## Theme J — Attacks on the twin as an instrument

### J1. Scenario multiplicity defeats the decision-laundering block
**(b)** Scheduled execution stops you re-running until it agrees. It does not stop you *specifying forty scenarios up front* and citing the one that agreed. This is p-hacking with pre-registration, which is to say it's p-hacking. **Confidence: high.**

**(c)** Every scenario in a declared family must be published together with its result, and citing one requires exhibiting the family. Straightforward, and it's a real hole in an entry you currently consider closed.

### J2. Evidence-grade gaming
**(b)** Grades are gradeable and challengeable, therefore movable. An insider who wants a decision made feeds one more piece of corroborating evidence to nudge a grade past a threshold. Cheap, deniable, and indistinguishable from diligence. **Confidence: medium-high.**

---

## The five you most need to add

Ranked by severity × genuinely-unblocked × invisibility-to-you.

1. **Strategic non-modelling (D2).** Documented foreseeability creates liability, so the rational deployer scopes the twin to exclude the scenarios most likely to produce it — and the sensor admission ladder supplies the principled language for doing so. Your safeguard against surveillance is also a certified mechanism for deliberate ignorance about harm to people, and the resulting twin confers documented diligence on the domains where it looked hardest at nothing. Nothing blocks this. Partial fix: a published, versioned scope declaration plus a mandatory scenario floor.

2. **The outsiders (B1, B2, B5).** The catalogue is almost entirely about employees; the twin's sharpest commercial edge is aimed at suppliers, contractors, applicants and acquisition targets, and perspectival £ *legitimises* that by placing their harms outside the currency by construction. "They can run their own twin" is an answer only to parties with capital. Add the counterparty-extraction entry, the externality-laundromat entry, and the procurement-mandate entry, and if you can't block them, say so.

3. **Exit-cost asymmetry (A1).** The grievance→insider-risk counter-price — your headline block on pay suppression — only bites for people who can credibly leave. The twin's core competence is identifying who can't. You have built a precision instrument for finding the population your main safeguard does not protect, and every input is a permitted structural field.

4. **Absence-as-alibi (H1).** Structural unrepresentability of Article 9 data prevents discrimination *detection*, not discrimination. It also hands you the most misleading defence in employment law. Needs a sealed audit channel or an explicit admission that this system cannot be checked for disparate impact.

5. **Unauditable constraint removal (I1) plus constraint-adjacent optimisation (I2).** Removing forbidden options before optimisation means the record cannot distinguish an ethical exclusion from a convenient one, and destroys the most informative signal available — how attractive the forbidden thing was. Meanwhile the optimiser walks to the nearest permitted point, which is usually the same harm without the name. Together these mean your safety property is asserted rather than demonstrated.

*Narrowly missed, and I'd take them next:* immutable-graph versus right-to-erasure with twin-transfers-on-acquisition (D5) — the most concretely legally exposed item; role-not-person signatures (C1/C2) — cheapest real fix on the list; ensemble stuffing (F1) — the most novel attack; the union as surveillance operator of its own members (E2) — the most uncomfortable.

---

## The structural blind spot

Every constraint in this design is **epistemic**. What may be represented, what may be inferred, what may be produced, what may be traced, what may leave the tenant. Not one is a constraint on **power** — on who may act, upon whom, with what asymmetry, and with what recourse for the person acted upon. That is why the catalogue is full of forbidden *data* and empty of protected *parties*, why every safeguard fails the moment a harm can be assembled from permitted inputs, and why the largest gap is the entire outside of the organisation, where the twin's value lives and where the designers therefore did not go looking for harm.

Perspectival £ is the tell. Confronted with an irreducible conflict of interest, the design converts a power asymmetry into a *plurality of viewpoints*, declares each internally coherent, and treats the symmetry as a virtue — when the actual asymmetry is that only one of those viewpoints can afford to be instantiated, and it is the one holding the data, writing the constraint set, curating the ensemble, and paying for the twin. This is a team that believes an argument you can have on equal terms is an argument between equals. It usually isn't, and a system whose central safeguard is "the map is a thing to argue with" needs to say, out loud and in the catalogue, who can afford to show up to the argument.
