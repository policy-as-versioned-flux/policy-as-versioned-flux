# 152 — Fact 7 cannot pass as registered

Type: grilling (HITL)
Status: resolved
Blocked by: none

## Question

Fact 7 of the drift lane asks whether the bottom rung reaches nothing while the control reaches. Ticket 86's resolution (2026-09-24) says it cannot pass as registered: under policy 5.0.0 the cage puts the fall-closed pod and the control on the same rung, `isolated`. So there is no bottom rung distinct from the loosest one, and every sample records fact 7 as `null`.

A `null` fact, with no fact observed false, makes the sample COULD-NOT-LOOK. On 2026-09-25 every line in all three adopters read that verdict. So each adopter's `verify-reconcile.sh` and `verify-e2e-step4` SKIP with "the lane sample cannot stand in". Fact 7 is not the only null: fact 2 is `null` on driftwood's and tuppence's own composed source.

Decide how fact 7 is re-registered: which pod is the control, on which rung, and what the pre-registered question becomes. Re-registering the section restarts the scores taken against the old wording (ticket 86's rule).

## Notes

Graduated 2026-09-25 from ticket 35, round 2 Q8. Definition of done includes wiring its check into `talk/verify-all.sh`.

This ticket blocks ticket 151, and the fleet, policy and governance-agent row of ticket 156's register. It relates to ticket 27, the cage ladder round 2, which owns the meaning of the rungs but whose question does not cover fact 7. The rung order, the `baseline` rung loosest and the `isolated` rung bottom, is ADR-0022's. Ticket 30 does not own fact 7.

## Facts found (2026-09-25)

Read at ludlow `b8e14f7`, driftwood `155db9e`, tuppence `5deffe6` and platform `557c153`, all `origin/main`.

- **Why the control lands on `isolated`.** The sampler gives both pods the version claim. The control's Namespace carries no governed label and no tier. Under 4.0.0 that fell to the `baseline` rung. Platform commit `60c02f8` (ticket 63, 2026-09-04) made 5.0.0 fall every Namespace without a tier to `isolated` (`composed/policies/v5.0.0/cage-tier.yaml:31-34`). No adopter serves 4.0.0 now.
- **What the served cage does to four candidate pods.** An offline proof with kyverno 1.18.2, on all three adopters, is in [research/ticket-152-fact-7-reference/](../research/ticket-152-fact-7-reference/README.md). A claiming pod in a Namespace that declares the `baseline` rung lands on `baseline` and no NetworkPolicy selects it. An unclaimed pod in a Namespace that declares nothing is not caged and no NetworkPolicy selects it. The `governed` label does not change the rung.
- **Reach by rung.** The served `cage-netpol` gives the `baseline` rung no NetworkPolicy. `restricted` and `quarantine` get DNS-only egress. `isolated` gets no ingress and no egress. So `restricted` and `quarantine` also reach neither of fact 7's two targets. Session 30 reported this.
- **Fact 7 is not the only null.** On the 2026-09-25 samples, fact 2 is null on the driftwood and tuppence composed sources. On driftwood, falsifier 2 is not looked at on `platform` and `nist`. Only ludlow fails on fact 7 alone. Step 4 grades driftwood (`verify/e2e/verify-e2e-step4-flux-reconciles-cage.sh:46`).
- **A five-fact PASS window.** `grade` does not score facts 6 and 7 on a sample older than the current registration (ludlow `drift/five-facts.py:1432`, `:1447`), and then it can print PASS (`:1490`). A fact finder simulated a re-registration on ludlow's real samples and got `rc 0` with the cage not scored.
- **The gate hid the null.** The four `talk/verify-manifest.txt` rows for `verify-reconcile.sh` and step 4 match "the lane sample cannot stand in" anywhere in the line (`talk/truth_manifest.py:133`). `truth_manifest.py judge` on the 2026-09-25 captures returned "declared waits".
- **Nothing runs `five-facts.py selfcheck`.** The workflows run `sample` and `grade` only. The hub truth runner installs the kyverno CLI 1.18.2 (`.github/workflows/truth.yml:58-59`). The adopters install the CLI only in `shift-left.yml`.
- **Doctrine.** Each adopter's signed governed Namespace declares `isolated` (`gitops/apps/namespace.yaml:28` in ludlow and tuppence, `:30` in driftwood). ADR-0022 says that a declaration cannot be looser than the party's worst-priced regime (`:123`), and calls a looser one "an exemption bought by choosing a Namespace" (`:222`). Ticket 119 decision 2 keeps an unclaimed pod in an unlabelled Namespace outside the cage, and a regression test holds it.
- **Two defects outside this ticket.** At the `baseline` rung the cage writes container `runAsNonRoot: false` over a pod that declared `true` (`cage-tier.yaml:40`, ADR-0022 `:47`). A tier label on an ungoverned Namespace steers the cage exactly as on a governed one.
- **A correction to the Notes above.** The text of ticket 27 covers the warn rung, de-posture, break-glass bands and the price of a tier move. It does not cover reach, `isolated` or fact 7.

Sessions 30, 35 and 71 answered questions from what they already knew. Two fact finders, then a workflow of two provers and two adversarial reviewers, found the rest. The reviewers refuted the first draft of Q6. The assistant checked each claim that changed a recommendation before it used it.

## Grilling rounds (put and answered 2026-09-25)

The owner answered each round with "agree". A bare reply is a delegation (ADR-0025). So each decision below is **delegated**, 2026-09-25, and its reason is the assistant's.

1. **Q1: fact 7 keeps its claim.** Only the comparison pod changes. A reach matrix over all rungs is a new claim about rung meaning, and a host-network probe does not use the pod network.
2. **Q2: the comparison pod is the "reference workload".** In this estate a **control** is a catalogue control. Write "the `baseline` rung", never "baseline" alone, because **Baseline** is also an OSCAL profile. The new name was free only in this re-registration. CONTEXT.md carries both entries.
3. **Q3: fact 2 gets its own ticket, 157.** It is a different fact with an unknown cause. Pointing step 4 at ludlow would hide the driftwood fault.
4. **Q4: a sample older than the newest registration reads could-not-look on facts 6 and 7.** A question not yet asked is not a pass. The old rule protected samples from before ticket 86, and all of those are older than the 48-hour bound.
5. **Q5: an unstamped fall-closed pod keeps reading null for fact 6.** A null cannot become a false pass. No adopter moves to kyverno 1.19.1 while the served cage does not compile there. Session 71 was told, and it carries the condition. No ticket for that move is written yet.
6. **Q6: the reference workload is an unclaimed pod in a Namespace that declares nothing.** The cage does not select it, by ticket 119 decision 2. The first draft put it in a runtime governed Namespace that declares the `baseline` rung. That buys a looser cage by choosing a Namespace, where the binding check cannot see it, which ADR-0022 calls an exemption. The Q1 wording said "change only where the pod runs". This option also removes the pod's version claim, and the round said so before the owner answered. ADR-0028 decision 2 ("the rung is derived, never asserted") stands.
7. **Q7: the instrument checks that the fall-closed rung is the ladder's bottom.** The pod's priority must equal the lowest `cage-` PriorityClass on the cluster, and the NetworkPolicy that selects it must have no rules and declare both policy types. Two connects alone cannot tell `quarantine` from `isolated`.
8. **Q8: the new registration text** is [research/ticket-152-fact-7-reference/cage-behaviour-sample.draft.yaml](../research/ticket-152-fact-7-reference/cage-behaviour-sample.draft.yaml). Fact 6's text is byte-identical. Fact 7 has a new id, `fact_7_the_bottom_rung_reaches_nothing_while_the_reference_reaches`. The four falsifiers become six. Falsifier 3 gets the new name. Falsifier 4, "the cage puts the control and the fall-closed workload on the same rung", is replaced by Q6's `the_cage_selects_the_reference_workload`: a reference that the cage does not select carries no rung, so it can share a rung with the fall-closed pod only if the cage stamps it. Q7 and Q10 add one falsifier each. Q4 adds a `scoring` key. The three adopters get the same section, except `declared_on`.
9. **Q9: a new `verify-cage-probe.sh` in each adopter.** It runs `five-facts.py selfcheck` and checks the CLI version against the adopter's engine pin. It proves that the CLI reads Namespace labels. It then runs the sampler's own probe objects against the served set at the pinned tag and at HEAD. It fails when the fall-closed pod is not on the bottom, when anything selects the reference, or when a named PriorityClass is not served. It gets one `talk/verify-manifest.txt` row per adopter and a step in each `shift-left.yml`. A hub script was rejected as a second ruler (ticket 86 decision 7).
10. **Q10: a cage fact that is null on 3 samples in a row reads FAIL,** and `grade` names each null fact on its SKIP line. A null that clears stays a could-not-look. Ticket 160 applies the same rule to the five facts.
11. **Q11: four defects get tickets 157 to 160.** Session 30 assigned numbers from 157.
12. **Q12: this ticket resolves as a grilling ticket.** The build is ticket 161.

These follow from the decisions and needed no question:

- Facts 6 and 7 share one section, so the new registration restarts fact 6 too. The cost is one sample interval.
- The Q4 grade change lands before the new window text, or in the same commit, on each adopter. Never after it.
- ADR-0028 gets a dated correction. Its decision 2 said that the ungoverned control lands on the loosest rung, and that was already false for 5.0.0.
- The Q2 rename reaches `talk/deck.md:270` (in ticket 161) and ticket 155 (in this change). Ticket 86, `map.md` history and `samples.jsonl` stay as written.

## Decided while recording (2026-09-25)

Two adversarial reviewers read this record before it was committed. They found gaps that the rounds did not settle. Each gap is decided here by the assistant under ADR-0025, labelled **delegated**, with its reason. None changes an answer above.

- **The bottom check also covers fact 6.** If the fall-closed rung is not the bottom, facts 6 and 7 both read could-not-look. Fact 6's claim names "its own bottom rung", and a TRUE on a rung that is not the bottom would assert a rung the instrument did not derive.
- **Which samples count for Q10.** The three newest samples in `drift/samples.jsonl` that were taken at or after the newest registration of the section. A lane run started by hand from the Actions tab counts, because its record is not told apart from a scheduled one. It is not citable as a pass (ADR-0028, Consequences), but here it can only bring a fall sooner, never make a pass. A rehearsal is never appended (ADR-0023, D4). Samples from before the registration do not count, or the rule would fire on the first new sample.
- **`declared_on` may differ.** The three sections are identical except `declared_on`. Each adopter's registration is read from its own git history.
- **Items 2 and 3 of ticket 161 land in one commit.** `grade` fails when the section and the code disagree on an id.

## Answer

**Resolved 2026-09-25. Every decision is delegated (ADR-0025).**

The reference workload is an unclaimed pod in a Namespace that declares nothing, so the cage does not select it. The fall-closed pod stays as ticket 86 built it. The instrument checks that its rung is the ladder's bottom by priority and by a reach policy with no rules and both policy types. Fact 7 is renamed. One falsifier is renamed, one is replaced and two are added. A sample from before the new registration reads could-not-look, never PASS on five facts. A cage fact that is null on three samples in a row is a fall. The full section is [cage-behaviour-sample.draft.yaml](../research/ticket-152-fact-7-reference/cage-behaviour-sample.draft.yaml).

This ticket does not build. The Definition of done in the Notes above moves to ticket 161, which holds the build and the check for `talk/verify-all.sh`.

Graduated 2026-09-25:

- [157 — Fact 2 is null on two composed sources](157-fact-2-is-null-on-two-composed-sources.md)
- [158 — The baseline rung writes runAsNonRoot false](158-the-baseline-rung-writes-runasnonroot-false.md)
- [159 — A tier label on an ungoverned namespace steers the cage](159-a-tier-label-on-an-ungoverned-namespace-steers-the-cage.md)
- [160 — A fact that is never looked at is a fall](160-a-fact-that-is-never-looked-at-is-a-fall.md)
- [161 — Fact 7 is registered again with a reference workload](161-fact-7-is-registered-again-with-a-reference-workload.md)

Ticket 151 is now blocked by 157 and 161. Ticket 156's fleet, policy and governance-agent row waits on 161.
