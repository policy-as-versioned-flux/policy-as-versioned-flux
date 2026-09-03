# Provisional decisions (bare agree / bare letter / deferred; architectural or scope) — 211

> **Annotated 2026-09-03 (eco-system ticket 17).** Entries are never deleted or renumbered, because
> `REVERSALS.json`, `DECISION_AUDIT.json`, appendix C and `REGRILL-ANSWERS.md` cite them by id. A
> duplicate capture carries a `Status` line pointing at its original and counts once. Known
> duplicates: P012 and P034 are second and third captures of P010; P013 and P035 are second and
> third captures of P011. The 211 in the title is captures, not decisions; distinct decisions are
> 207. P010 is marked **rejected** (reversal verdict `reverse`; the owner confirmed full depth in
> `REGRILL-ANSWERS.md` row 3-4 on 2026-08-28).

## P001 [2026-07-23T1958_a3a17a79 2026-07-24T15:13] Where Flux distribution sits in the exploded hourglass
- Q: Assistant placed Flux distribution at the hourglass neck (the single admission decision) with shift-left as a dashed pre-admission catch, and flagged: if the user thinks Flux belongs in the top bulb (authoring/distribution) instead, it's a one-line change.
- Options: Flux at the neck (as drawn) vs. Flux moved to the top bulb
- Recommended then: Flux at the neck, shift-left as dashed pre-admission catch
- Reply: `` (deferred, accepted=False)
- Recorded in: .scratch/talk-spec/the-whole-model.md

## P002 [2026-07-23T1958_a3a17a79 2026-07-24T15:25] Six-org provenance graph representation choices
- Q: Two judgement calls flagged: (a) show each institution's nist+ico version pin inside its risk-skin node vs. as explicit crossing edges; (b) only driftwood drilled to team/workload depth vs. exploding all three institutions symmetrically.
- Options: (a) pin-in-node vs. explicit edges; (b) driftwood-only exploded vs. all three exploded
- Recommended then: Pin-in-node for legibility; driftwood-only exploded to avoid triplicating the diagram
- Reply: `` (deferred, accepted=False)
- Recorded in: .scratch/talk-spec/the-whole-model.md

## P003 [2026-07-23T1958_a3a17a79 2026-07-24T17:22] Pitch angle and closing ask for the CEO pitch video
- Q: AskUserQuestion, two questions: (1) 'What's the emphasis for a CEO who's funding this?' with options Balanced (vision + payoff) / Vision-thought-leadership / Hard business case-ROI. (2) 'How should the pitch close — what am I actually asking you to fund?' with options Full build to flagship / Time-boxed proof first / Approval in principle.
- Options: Q1: Balanced vision+payoff / Vision-thought-leadership / Hard business case-ROI. Q2: Full build to flagship / Time-boxed proof first / Approval in principle.
- Recommended then: No option was marked as the assistant's recommendation — all three choices per question were presented neutrally with equal-weight previews.
- Reply: `[The user's literal answer to this AskUserQuestion is not present as a separate USER turn in this transcript. The very n` (bare_letter, accepted=False)
- Recorded in: .scratch/talk-spec/pitch/script.md

## P004 [2026-08-13T1449_226bb1a6 2026-08-13T14:56] How to get drift evidence without the plain 91-day wait
- Q: Which real alternative do you want to pursue instead of the plain 91-day wait?
- Options: Start the cron now, keep waiting / Add literature evidence in parallel / Find an older real cluster to mine / Just start the cron, ask again later
- Recommended then: None stated explicitly.
- Reply: `(No selection text visible; next USER turn 13 min later is a new question: "why is this not a k8s cron job then?")` (deferred, accepted=False)
- Recorded in: 

## P005 [2026-08-13T1449_226bb1a6 2026-08-13T15:21] Plant policy for the solo demo cluster
- Q: How do you want to handle deliberate edits, given a null result may just mean nobody was around?
- Options: Stay pure observation / Plant labelled test edits separately
- Recommended then: None marked explicitly.
- Reply: `(Selection not shown as text; inferred as 'Stay pure observation' from the assistant's own later reference at 2026-08-14` (bare_letter, accepted=False)
- Recorded in: estate/driftwood/drift/window.yaml (dated addendum)

## P006 [2026-08-13T1449_226bb1a6 2026-08-14T09:36] Grilling round 2, Q3 — is settling ticket 65's claim on this cluster worth it at all
- Q: Should tickets 64–65 possibly be retired/rescoped in favour of literature as primary evidence?
- Options: Keep instrumenting / Retire and rescope to literature
- Recommended then: None — assistant said this was the user's judgement call.
- Reply: `force the situation at a higher resolution on a real cluster and capture the stats then?` (deferred, accepted=False)
- Recorded in: 

## P007 [2026-08-13T1449_226bb1a6 2026-08-14T09:41] Grilling round 3, Q1 — forced action set
- Q: Fixed list of plausible operator actions, or a bounded free agent choice?
- Options: Fixed list / Bounded free choice
- Recommended then: Fixed list.
- Reply: `oh, i agree with your recomendations, confirmed` (bare_agree, accepted=True)
- Recorded in: build ticket 78 (forced-drift-latency-campaign-bounded-real-clust.md)

## P008 [2026-08-13T1449_226bb1a6 2026-08-14T09:41] Grilling round 3, Q4 — where this capability lands
- Q: New standalone build ticket with its own pre-registration file, explicitly not evidence for ticket 65?
- Options: Yes, own ticket / fold into ticket 64
- Recommended then: Yes.
- Reply: `oh, i agree with your recomendations, confirmed` (bare_agree, accepted=True)
- Recorded in: build ticket 78 (forced-drift-latency-campaign-bounded-real-clust.md)

## P009 [2026-08-15T2214_c106de98 2026-08-16T07:03] How to make pushing possible given enact_guard.py denies it
- Q: "The instruction and the guard cannot both stand. One of these has to happen, and both are your call: 1. Narrow twin/enact_guard.py so it permits git push and still denies merge (build tickets 66/67 invariants will fail). 2. Remove the hook from .claude/settings.json (drops decision ticket 18 Q1 entirely). Tell me which, and cite it as the authorising change."
- Options: 1. Narrow the guard to permit push only / 2. Remove the PreToolUse hook entirely
- Recommended then: None explicit — assistant presented both neutrally and said the choice is the user's.
- Reply: `I see. Just push now` (bare_agree, accepted=False)
- Recorded in: decision ticket 18 Q1; build tickets 66 and 67

## P010 [2026-08-18T0216_1fd9c838 2026-08-18T02:20] Scope of "everything remaining" for the twin-project implementation run
- Q: What is the scope of "everything remaining" for this implementation run?
- Options: Demo-slice only (Recommended, one new ticket 79); Demo-slice + carried-forward items (several new tickets); All partial capabilities to full depth (dozen+ new tickets across 13 capabilities); Let me name the tickets
- Recommended then: Demo-slice only — ticket 22's demo-slice capability, the one item ticket 77 explicitly named as the next gap, one new build ticket (79)
- Reply: `[Not captured in the digest as a USER turn — the AskUserQuestion tool result text is absent from this transcript. The as` (bare_letter, accepted=False)
- Recorded in: 
- **Status (2026-09-03, eco-system ticket 17): rejected.** The narrowing was not taken: build tickets 79-91 went to full depth and closed 2026-08-18. Reversal verdict `reverse` (REVERSALS.json, appendix C); the owner confirmed full depth in REGRILL-ANSWERS.md row 3-4 (2026-08-28). Duplicate captures: P012, P034.

## P011 [2026-08-18T0216_1fd9c838 2026-08-19T17:13] What basis to use for the pitch-v4 script, since the estate/policy code itself hadn't changed much since 31 Jul
- Q: What should I treat as the current, accurate basis for this pitch — since the estate/policy code itself hasn't changed much since 31 Jul?
- Options: The subject has shifted to the twin project (73/73 capabilities just finished); Same subject, but story/framing changed through conversation, not code; Build fresh from today's live state, ignore all prior scripts, treat pitch-v3/demo/ as tooling reference only
- Recommended then: No option is marked Recommended in this prompt.
- Reply: `[Not captured in the digest as a USER turn — no reply text visible. The assistant's next turn ('While that reconnaissanc` (bare_letter, accepted=False)
- Recorded in: 
- **De-duplicated 2026-09-03 (eco-system ticket 17):** P013 and P035 are second and third captures of this same AskUserQuestion (2026-08-19T17:13). Counts once, here. Its verdict is untouched by ticket 17.

## P012 [2026-08-19T1916_556d5f44 2026-08-18T02:20] Scope of 'everything remaining' for the twin implementation run
- Q: AskUserQuestion: demo-slice only, demo-slice+carried-forward, all partial capabilities to full depth, or user names tickets
- Options: (1) Demo-slice only [Rec]; (2) +carried-forward; (3) All partial capabilities to full depth; (4) User names tickets
- Recommended then: Option 1, demo-slice only
- Reply: `[not captured in digest; inferred from next assistant turn that option 3 was chosen]` (deferred, accepted=False)
- Recorded in: .scratch/twin/build/ (79-91)
- **Status (2026-09-03, eco-system ticket 17): rejected; duplicate of P010.** Same AskUserQuestion at 2026-08-18T02:20, captured from a second transcript. Kept so the trail shows two captures; it is not a second decision and counts once, under P010.

## P013 [2026-08-19T1916_556d5f44 2026-08-19T17:13] Basis for the pitch video given estate barely changed since 31 Jul
- Q: AskUserQuestion: subject shifted to twin, same subject/story changed, or build fresh from live state
- Options: (1) shifted to twin; (2) same subject, framing changed; (3) build fresh, ignore prior scripts
- Recommended then: none explicitly marked
- Reply: `[not captured in digest; inferred option 3 chosen from subsequent research fork]` (deferred, accepted=False)
- Recorded in: 
- **Duplicate of P011 (2026-09-03, eco-system ticket 17):** same AskUserQuestion at 2026-08-19T17:13, second transcript. Counts once, under P011.

## P014 [2026-08-19T1916_556d5f44 2026-08-19T22:00] Destination for multi-org/demo wayfinder map (Q1)
- Q: (a) demo defensible; (b) estate actually complete; (c) decision record only
- Options: (a)/(b)/(c)
- Recommended then: (a) demo defensible
- Reply: `1 b` (bare_letter, accepted=False)
- Recorded in: .scratch/multi-org-estate/map.md

## P015 [2026-08-19T1916_556d5f44 2026-08-19T22:14] estate/ in hub after split (Q7)
- Q: delete; keep as working tree; submodules
- Options: (i)/(ii)/(iii)
- Recommended then: (i) delete
- Reply: `7 i` (bare_letter, accepted=True)
- Recorded in: .scratch/multi-org-estate/map.md

## P016 [2026-08-19T1916_556d5f44 2026-08-20T07:14] How to express composable roles (Q4)
- Q: prose only; prose+machine field; or prose per README
- Options: (i)/(ii)/(iii)
- Recommended then: (i), with (ii) as follow-on
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: CONTEXT.md

## P017 [2026-08-19T1916_556d5f44 2026-08-20T07:14] Should platform's appetite band consolidate into appetite.json (Q5)
- Q: merge and drop override; leave separate; or merge but marked distinctly
- Options: (i)/(ii)/(iii)
- Recommended then: (iii)
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: CONTEXT.md / appetite.json

## P018 [2026-08-19T1916_556d5f44 2026-08-20T07:30] Destination for computed-semver effort (Q1)
- Q: decision record only; ship inheritance; ship computed semver; or both
- Options: (a)/(b)/(c)/(d)
- Recommended then: (c), inheritance only if it earns its place
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/

## P019 [2026-08-19T1916_556d5f44 2026-08-20T07:30] Which estate to build computed semver against (Q2)
- Q: new six-org estate vs old faithful-floor estate
- Options: new/old
- Recommended then: new estate, mining old for test material
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/

## P020 [2026-08-19T1916_556d5f44 2026-08-20T07:30] Does computed-semver rule apply to platform's own version (Q3)
- Q: same rule; policy-body only; or platform's own rule
- Options: (i)/(ii)/(iii)
- Recommended then: (i) same rule
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/

## P021 [2026-08-19T1916_556d5f44 2026-08-20T07:37] Is admitted-but-reported compliant for semver purposes (Q1)
- Q: compliant=admitted vs reported=non-compliant
- Options: two readings
- Recommended then: compliant means admitted
- Reply: `[no direct reply this round; implied accepted via later recording]` (deferred, accepted=True)
- Recorded in: .scratch/computed-semver/

## P022 [2026-08-19T1916_556d5f44 2026-08-20T07:43] Is a computed bump institution-relative (Q4)
- Q: strictest band; declared reference band; matrix; or rule-changes-only
- Options: (i)/(ii)/(iii)/(iv)
- Recommended then: (i), with (iii) as evidence
- Reply: `[not directly answered this round; recorded per recommendation]` (deferred, accepted=True)
- Recorded in: .scratch/computed-semver/

## P023 [2026-08-19T1916_556d5f44 2026-08-20T07:53] Does platform's own infra fall inside this effort (Q2)
- Q: in scope leading case; out of scope; or in scope sequenced last
- Options: (i)/(ii)/(iii)
- Recommended then: (i)
- Reply: `2 agree` (bare_agree, accepted=True)
- Recorded in: .scratch/govern-what-you-dont-control/

## P024 [2026-08-19T1916_556d5f44 2026-08-20T07:53] Whose problem is COTS compliance post-split (Q3)
- Q: institution's; platform's; or split
- Options: (i)/(ii)/(iii)
- Recommended then: (iii) split
- Reply: `3 agree` (bare_agree, accepted=True)
- Recorded in: .scratch/govern-what-you-dont-control/

## P025 [2026-08-19T1916_556d5f44 2026-08-20T08:36] Vendor recourse: fifth move, modifier, or counterparty on transfer (Q1)
- Q: fifth move; modifier; or transfer gains a counterparty
- Options: (i)/(ii)/(iii)
- Recommended then: (iii)
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/govern-what-you-dont-control/

## P026 [2026-08-19T1916_556d5f44 2026-08-20T08:36] Evidence gating for vendor-recourse credit (Q2)
- Q: evidence-graded fail-closed; binary; or face value
- Options: (i)/(ii)/(iii)
- Recommended then: (i) fail closed
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/govern-what-you-dont-control/

## P027 [2026-08-19T1916_556d5f44 2026-08-20T08:44] Remove or reframe the existing exemption ledger (Q1)
- Q: removed; reframed as codified conditional policy; or kept
- Options: (i)/(ii)/(iii)
- Recommended then: (i) removed
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/govern-what-you-dont-control/

## P028 [2026-08-19T1916_556d5f44 2026-08-20T08:44] Accept some workloads then cannot run at all (Q2)
- Q: yes refusal is the point; no always runnable; or procurement-stage decision
- Options: (i)/(ii)/(iii)
- Recommended then: (i), with (iii) as humane path
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/govern-what-you-dont-control/

## P029 [2026-08-19T1916_556d5f44 2026-08-20T08:44] What replaces ledger's OSCAL risk-object output (Q3)
- Q: cage produces it; procurement record; or both
- Options: (i)/(ii)/(iii)
- Recommended then: (i) cage produces it
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/govern-what-you-dont-control/

## P030 [2026-08-19T1916_556d5f44 2026-08-20T09:38] How verify works across six checkouts post-split (Q1)
- Q: hub aggregates; each repo self-verifies; or platform ships harness as dependency
- Options: (i)/(ii)/(iii)
- Recommended then: (iii), fallback (i) for cross-cutting
- Reply: `1 accept` (bare_agree, accepted=True)
- Recorded in: .scratch/multi-org-estate/map.md

## P031 [2026-08-19T1916_556d5f44 2026-08-20T10:28] Do prediction markets belong in £ pricing path (Q1)
- Q: feed; benchmark only; or neither
- Options: (i)/(ii)/(iii)
- Recommended then: (ii) benchmark only
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/multi-org-estate/map.md

## P032 [2026-08-19T1916_556d5f44 2026-08-20T10:28] Should commoditising defence lower the bill (Q2)
- Q: no; yes via cost-of-controls; yes via LEF; or yes gated on corroboration
- Options: (i)/(ii)/(iii)/(iv)
- Recommended then: (iv) applied to (ii)
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/multi-org-estate/map.md

## P033 [2026-08-19T1916_556d5f44 2026-08-20T10:36] Final close-out of prediction-market/commoditising-defence questions
- Q: repeat of earlier Q1/Q2 left unanswered in prior round
- Options: same as prior
- Recommended then: same as prior
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/multi-org-estate/map.md

## P034 [2026-08-19T2155_deefb3b4 2026-08-18T02:20] Scope of "everything remaining" for the twin-project implementation run
- Q: What is the scope of "everything remaining" for this implementation run?
- Options: Demo-slice only (Recommended, one new ticket 79); Demo-slice + carried-forward items (several new tickets); All partial capabilities to full depth (dozen+ new tickets, 34 unchecked ACs across 13 capabilities); Let me name the tickets
- Recommended then: Demo-slice only — build ticket 22's demo-slice capability (0/4, graded stub), the one item ticket 77 explicitly names as the next honest gap.
- Reply: `[Not present as a distinct USER turn in this digest — AskUserQuestion tool-result content is not captured as user text h` (bare_letter, accepted=False)
- Recorded in: no single ticket cites this decision text; it produced build tickets 79-91 under .scratch/twin/build/
- **Status (2026-09-03, eco-system ticket 17): rejected; duplicate of P010.** Same AskUserQuestion at 2026-08-18T02:20, captured from a third transcript. Counts once, under P010.

## P035 [2026-08-19T2155_deefb3b4 2026-08-19T17:13] Accurate basis for the pitch-v4 script, given the estate/policy code itself barely changed since 31 Jul
- Q: What should I treat as the current, accurate basis for this pitch — since the estate/policy code itself hasn't changed much since 31 Jul?
- Options: The subject has shifted to the twin project; Same subject but the story/framing changed through conversation, not code; Build fresh from today's live state, ignore all prior scripts (pitch-v3/demo/ as tooling reference only)
- Recommended then: None of the three options was tagged Recommended; presented as a neutral three-way choice.
- Reply: `[Not present as a distinct USER turn in this digest. The assistant's subsequent actions — launching a live-state reconna` (bare_letter, accepted=False)
- Recorded in: 
- **Duplicate of P011 (2026-09-03, eco-system ticket 17):** same AskUserQuestion at 2026-08-19T17:13, third transcript. Counts once, under P011.

## P036 [2026-08-19T2155_deefb3b4 2026-08-19T20:17] Whether to chart a Wayfinder map for the six-empty-GitHub-orgs split, or just correct the demo's claim about it
- Q: Do you want me to chart a wayfinder map for the split specifically, or would you rather I just make the demo's claim honest (restate segment 23) and keep the split as recorded fog? (asked again, near-verbatim, at 21:54:21.752Z: "Do you want that charted as a wayfinder map, or shall I just make the demo's claim honest and record the split as fog?")
- Options: Chart a Wayfinder map for the org split specifically — real multi-session work (713 files across six orgs, signed releases, Renovate, Flux sources, verify-all.sh kept green); Just make the demo's claim honest (fix the narration) and record the split as fog
- Recommended then: No option explicitly tagged Recommended; the assistant flagged the claim as needing fixing 'one way or the other' but did not pick between the two paths.
- Reply: `How's it going?` (deferred, accepted=False)
- Recorded in: 

## P037 [2026-08-20T1046_68fb0689 2026-08-20T10:50] Which risk tier(s) of open tickets to implement now
- Q: The open task-type tickets split into three risk tiers (local-only, needs-live-infra, creates-real-GitHub-orgs). Which tier(s) should I implement now?
- Options: Tier 1: safe/self-contained (8 tickets); Tier 2: needs live infra (5 tickets); Tier 3: creates real GitHub orgs and repoints live Flux (4 tickets)
- Recommended then: No option explicitly labeled recommended; framed by ascending risk/reversibility.
- Reply: `[no free-text reply captured; answered via AskUserQuestion UI. Subsequent narrative implies Tier 1 approved immediately,` (bare_letter, accepted=True)
- Recorded in: .scratch/multi-org-estate/, .scratch/computed-semver/, .scratch/govern-what-you-dont-control/

## P038 [2026-08-20T1046_68fb0689 2026-08-20T17:32] Visibility of the six new GitHub org repos created for mo-08
- Q: mo-08 creates real repos in six existing empty GitHub orgs and pushes filtered history. What visibility should those repos have?
- Options: Private (recommended); Public
- Recommended then: Private (recommended)
- Reply: `[no free-text reply captured; UI selection only. Outcome per mo-08 workflow result at 19:29:51.556Z: 'all six repos exis` (bare_letter, accepted=False)
- Recorded in: .scratch/multi-org-estate/08-*.md

## P039 [2026-08-20T1046_68fb0689 2026-08-20T17:32] Pacing of the Tier 3 chain (mo-08 -> mo-09 -> mo-10 -> mo-12)
- Q: mo-09 retires the in-cluster git-server and mo-12 deletes estate/ from the hub. Run the full chain now, or stop after mo-08 for review?
- Options: Stop after mo-08 (recommended); Run the full chain
- Recommended then: Stop after mo-08 (recommended)
- Reply: `[no free-text reply captured; UI selection only. Outcome per 17:35:09.775Z: 'Tier 3 is running now: mo-08 -> mo-09 -> mo` (bare_letter, accepted=False)
- Recorded in: .scratch/multi-org-estate/

## P040 [2026-08-20T1046_68fb0689 2026-08-20T19:30] Whether to retry mo-09 immediately or pause Tier 3 for review
- Q: Given mo-09 hit a real governance-bypass bug, should I retry it now (loophole closed) or pause Tier 3 for you to review mo-08's public repos first?
- Options: Pause here (recommended); Retry mo-09 now
- Recommended then: Pause here (recommended)
- Reply: `[no free-text reply captured; UI selection only. Outcome per 19:44:43.841Z: 'Cleaned up... and relaunched mo-09 -> mo-10` (bare_letter, accepted=False)
- Recorded in: .scratch/multi-org-estate/09-*.md

## P041 [2026-08-20T1046_68fb0689 2026-08-21T12:00] Fixed point for the follow-up /code-review diff
- Q: What should the review compare against — the fixed point for the diff?
- Options: Whole session (72c6a90..HEAD), broad Spec axis; Just the attestation follow-up
- Recommended then: No option explicitly labeled recommended.
- Reply: `[no reply captured before the transcript excerpt ends; next assistant turn (12:04:24.633Z) says the review is already ru` (deferred, accepted=False)
- Recorded in: 

## P042 [2026-08-21T1210_08208ccc 2026-08-20T10:50] Implementation scope: which risk tier(s) to run
- Q: Which risk tier(s) (Tier1 safe/local, Tier2 live infra, Tier3 real GitHub orgs) should be implemented now?
- Options: Tier1 (8 tickets) / Tier2 (5 tickets) / Tier3 (4 tickets), multiSelect
- Recommended then: No option marked recommended; presented neutrally
- Reply: `[not captured as text in digest; inferred all three tiers approved from subsequent sequential execution]` (bare_letter, accepted=False)
- Recorded in: .scratch/multi-org-estate/ and .scratch/computed-semver/ maps

## P043 [2026-08-21T1210_08208ccc 2026-08-20T10:50] Include grilling/prototype tickets in this pass?
- Q: computed-semver/03,04,05 are grilling tickets, 06 a prototype ticket. Include them?
- Options: Skip them (recommended) / Include anyway
- Recommended then: Skip them
- Reply: `[not captured; inferred skip chosen since cs-07 stayed out of scope]` (bare_letter, accepted=True)
- Recorded in: .scratch/computed-semver/issues/03,04,05,06

## P044 [2026-08-21T1210_08208ccc 2026-08-20T19:30] Handling four unsigned tags pushed via unguarded REST path
- Q: How should I handle the four unsigned tags?
- Options: Delete them, redo properly / Leave them, note the gap
- Recommended then: Neither marked
- Reply: `[not captured; inferred 'Delete them, redo properly' since assistant confirmed deletion next]` (bare_letter, accepted=False)
- Recorded in: .scratch/multi-org-estate/issues/09

## P045 [2026-08-21T1210_08208ccc 2026-08-21T10:26] Implement keyless attestation gate for Renovate trust
- Q: Want me to implement that now — extend shift-left.yml, deploy to all three institution repos, and correct mo-10's ticket text?
- Options: Implement now / decline or defer
- Recommended then: Implement now
- Reply: `yes do all the work` (bare_agree, accepted=True)
- Recorded in: .scratch/multi-org-estate/issues/10

## P046 [2026-08-21T1415_d69fbfea 2026-08-21T14:27] What the corpus is made of (Round 1 Q1)
- Q: Given clusters have almost no workloads to harvest and the policy surface is small enough to generate cheaply, but ticket 01's validation set was five hand-authored fixtures, what should the corpus be made of?
- Options: Not explicitly enumerated as discrete options; framed as a synthesis decision (generated vs hand-picked vs hybrid).
- Recommended then: Two named populations: a generated spine enumerated over the policy surface decides bumps, and a witness set (ticket 01's five fixtures plus six real infra workloads) proves the generator didn't miss a real shape. Hand-selection never decides a bump.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: issues/03-what-is-the-corpus.md

## P047 [2026-08-21T1415_d69fbfea 2026-08-21T14:27] What one corpus entry is (Round 1 Q2)
- Q: Is a corpus entry (a) a pod spec alone with the harness supplying the band matrix, or (b) a pod spec plus its band so the corpus carries institution context?
- Options: (a) pod spec + version pin, harness crosses with every institution band; (b) pod spec + band baked in
- Recommended then: (a). Keeps the corpus institution-free, letting platform own it and publish the per-institution matrix ticket 02 asked for.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: issues/03-what-is-the-corpus.md

## P048 [2026-08-21T1415_d69fbfea 2026-08-21T14:27] Whether unlabelled and wrapped workloads enter the corpus (Round 1 Q4)
- Q: Now that the COTS effort's blocker is resolved, should unlabelled/wrapped workloads (post-wrap composites) enter the corpus?
- Options: Include composites vs. exclude them
- Recommended then: Yes, they are the leading case. The entry is the post-wrap composite pod spec (what admission sees), tagged with claim source (procured, wrapped, identified).
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: issues/03-what-is-the-corpus.md

## P049 [2026-08-21T1415_d69fbfea 2026-08-21T14:32] Who owns the corpus (Round 2 Q1)
- Q: Does platform own the one corpus/generator, or does each institution own its own corpus for its own adoption decision?
- Options: platform owns one corpus vs. per-institution corpora
- Recommended then: platform owns one corpus and the generator, beside computed-semver/. No institution owns a corpus, since semver is a property of the artefact, not the consumer; per-institution pre-adoption checks belong to ticket 05, not a second corpus.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: issues/03-what-is-the-corpus.md

## P050 [2026-08-21T1415_d69fbfea 2026-08-21T14:32] What the generator enumerates and where it stops (Round 2 Q2)
- Q: Given an infinite field space, what stopping rule should the generator use?
- Options: Enumerate per field (unbounded) vs. enumerate per CEL expression with a bounded case set
- Recommended then: Enumerate per CEL expression: satisfied, violated, absent. Add a version-pin axis (in/out of array). Combine pairwise, not fully.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: issues/03-what-is-the-corpus.md

## P051 [2026-08-21T1415_d69fbfea 2026-08-21T14:32] Whether the corpus is versioned and signed (Round 2 Q4)
- Q: Should the corpus itself be signed given the estate signs evidence everywhere else?
- Options: Sign the corpus vs. don't sign it, regenerate in CI and diff-check instead
- Recommended then: Do not sign the corpus; CI regenerates and fails on any diff, which proves the same property more cheaply. Sign the gate's evidence output instead with the existing platform key.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: issues/03-what-is-the-corpus.md

## P052 [2026-08-21T1415_d69fbfea 2026-08-21T14:32] What weight a weak claim source carries (Round 2 Q5)
- Q: Does a bump observed on a composite with a weaker claim source (e.g. SPIFFE identity only) count for less than one with a procurement record?
- Options: Down-weight weak-claim composites vs. count all claim sources equally and just print the grade
- Recommended then: No, it counts the same; the evidence output states its claim grade. Down-weighting would be an exemption wearing a different name, which CONTEXT.md bans.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: issues/03-what-is-the-corpus.md

## P053 [2026-08-21T1415_d69fbfea 2026-08-21T14:41] How a generated workload gets a residual (Round 3 Q1)
- Q: Three ways for a generated pod to acquire a residual: (a) residual as a third generated axis at rung boundaries, (b) drop cage-spec comparison and compare admission outcome only, (c) build a scenario catalogue and bind scenarios to pods by label/namespace.
- Options: (a) generated residual axis at rung boundaries; (b) drop cage-spec comparison; (c) scenario catalogue binding
- Recommended then: (a). Generate residuals at each rung boundary and just either side of it, the only values that can change an answer. Stays institution-free. Reject (b) as abandoning the ticket-02 model; reject (c) as a separate effort with insufficient seed data.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: issues/03-what-is-the-corpus.md

## P054 [2026-08-21T1415_d69fbfea 2026-08-21T14:41] Whether the version array is part of the subject (Round 3 Q2)
- Q: Should distribution/versions.yaml (the version array) be included in the subject the generator reads, so a version retirement is visible?
- Options: Subject = policy bodies only vs. subject = policy bodies + version array
- Recommended then: Yes, include it. Anything less cannot see a retirement, forcing ticket 07 to invent a second mechanism.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: issues/03-what-is-the-corpus.md

## P055 [2026-08-21T1415_d69fbfea 2026-08-21T14:41] Whether changing the generator moves the version (Round 3 Q3)
- Q: Since editing the generator changes the corpus and thus observed movement, can generator changes bump the policy version themselves?
- Options: Generator changes can move the version vs. generator is excluded from the subject but held to a standard
- Recommended then: No, the generator is not part of the subject and cannot bump the version. But it must be visible: evidence names the generator version and corpus checksum, and a generator change must re-derive ticket 01's three known-good bumps or be refused.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: issues/03-what-is-the-corpus.md

## P056 [2026-08-21T1415_d69fbfea 2026-08-21T14:45] Which bands the rung boundaries come from, and whether platform is a row (Round 4 Q1)
- Q: Should the band matrix be built from platform/risk/appetite.json's four rows, and should platform (a risk-bearer, not an institution) be included as a row?
- Options: Exclude platform row vs. include it
- Recommended then: Read all four rows including platform, because ticket 07 binds platform's own version to this rule and honesty/reflexive.py exists to refuse self-exemption. Tag stays computed against ludlow at £5k regardless, so including platform costs nothing.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: issues/03-what-is-the-corpus.md

## P057 [2026-08-21T1415_d69fbfea 2026-08-21T14:45] What "the same shape" means, for the witness-miss check (Round 4 Q3)
- Q: Round 2 said a witness workload whose shape is missing from the spine fails the build — what precisely defines 'shape'?
- Options: Not enumerated as alternatives; a definition proposal.
- Recommended then: A shape is the tuple of outcomes each subject CEL expression gives on that pod, plus whether its pin is inside the version array. A witness is covered when its tuple already appears in the spine, ignoring cosmetic differences.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: issues/03-what-is-the-corpus.md

## P058 [2026-08-21T1415_d69fbfea 2026-08-21T14:47] Whether the corpus is generated once or twice per comparison (Round 5 Q2)
- Q: The gate compares two policy versions (two subjects) — should the corpus be generated from one subject or both?
- Options: Generate once from the new subject vs. generate from both old and new subjects and union
- Recommended then: Generate from both subjects and take the union. A retired rule is exactly the case a release must be able to see; generating from the new subject alone would hide it.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: issues/03-what-is-the-corpus.md

## P059 [2026-08-21T1415_d69fbfea 2026-08-21T14:47] Whether an entry is a pod, or a pod in a cluster state (Round 5 Q3)
- Q: Given multi-version coexistence and the pooled-exit-code trap ticket 01 found, is a corpus entry evaluated against one version's directory or the whole installed policy set?
- Options: Entry evaluated against a single version directory vs. entry stays a plain pod evaluated against the whole installed set with per-policy outcomes
- Recommended then: An entry stays a plain pod. The gate evaluates it against the whole installed policy set for a subject, reading per-policy outcomes rather than a pooled exit code, matching what rederive_bumps.py already does.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: issues/03-what-is-the-corpus.md

## P060 [2026-08-21T1415_d69fbfea 2026-08-21T15:15] Replace the residual axis with a tier-label axis (Round 6 Q1) — reverses Round 3 Q1
- Q: Given cage-tier.yaml is a MutatingPolicy that reads a tier label rather than a priced residual, and the £ engine never enters admission, should the residual axis be replaced with a tier-label axis?
- Options: Keep the residual axis from Round 3 vs. replace it with a generated tier-label axis (absent/baseline/restricted/quarantine)
- Recommended then: Generate the tier label instead: absent, baseline, restricted, quarantine. No invented money; matches what a pod actually carries. Absent is an important case since the policy defaults it to baseline. Drops the residual axis entirely.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: issues/03-what-is-the-corpus.md

## P061 [2026-08-21T1415_d69fbfea 2026-08-21T15:15] Where the bands go if the corpus is band-free (Round 6 Q2)
- Q: Round 4 crossed the corpus with four bands, but under the new tier-label axis the corpus no longer needs bands — where does band handling go?
- Options: Keep the band cross-product in the corpus vs. split into two separate evidence checks
- Recommended then: Split the evidence in two: the corpus proves what each tier does to a pod at admission; a separate cheap check runs select_tier as a pure function over each band in appetite.json and prints the per-institution matrix. Both land in the same evidence output.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: issues/03-what-is-the-corpus.md

## P062 [2026-08-21T1415_d69fbfea 2026-08-21T15:20] Which policies the subject contains (Round 7 Q1) — widens Round 3/5 scope
- Q: Only 3 of 8 live Kyverno policies carry a version; should the subject be (a) versioned bodies only, or (b) every Kyverno policy that can reach a pod?
- Options: (a) versioned policies only; (b) every Kyverno policy that can reach a pod
- Recommended then: (b) for observation, (a) for the tag. The gate evaluates against the whole installed set (matches admission), but an unversioned policy can't be described by a version number it lacks — so when observed movement traces to an unversioned policy, the gate fails and names the file. Repair is ticket 07's job.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: issues/03-what-is-the-corpus.md

## P063 [2026-08-21T1415_d69fbfea 2026-08-21T15:20] Whether the dials table is a policy body (Round 7 Q2)
- Q: The cage-tier CEL dials map (cpu limits per tier) exists in both cage.py and cage-tier.yaml — is it a policy body subject to the versioning rule?
- Options: Treat the dials table as out of scope vs. treat it as a policy body, with the CEL map in cage-tier.yaml as the authoritative copy
- Recommended then: Yes, and the CEL map in cage-tier.yaml is the copy that counts, since admission reads it. Consequence: tightening baseline's cpu limit is a major bump by CONTEXT.md's rule, yet today carries no version at all — so under Q1 it fails the gate.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: issues/03-what-is-the-corpus.md

## P064 [2026-08-21T1533_4ea03a72 2026-08-21T16:05] Override semantics: may a subclass weaken an inherited rule?
- Q: When an adopter inherits a rule from a publisher, may the adopter make that rule weaker?
- Options: No — strictest wins (composition is monotonic, stricter parent wins); Yes — most-derived wins (classical OO override, lets adopter weaken an upstream control); Only by conditional policy (child may only add a condition the parent's rule already admits, no override)
- Recommended then: No explicit single recommendation stated; the assistant flagged that 'strictest wins' is closest to what CONTEXT.md's exemption ban implies, while 'most-derived wins' is the literal OO model the user had named but would need reconciling with the exemption ban.
- Reply: `prototype what we now understand is needed` (deferred, accepted=False)
- Recorded in: .scratch/computed-semver/map.md (ticket 06); later .scratch/policy-composition/

## P065 [2026-08-21T1533_4ea03a72 2026-08-21T16:05] Where the composition question should live
- Q: Where should the composition question live?
- Options: Its own map (new policy-composition map, re-scope ticket 06 to note the dependency); Re-scope ticket 06 here (rewrite ticket 06 to the cross-party question and prototype on the same map); Record the correction only (fix ticket/map to state the real question, build nothing further until the model is decided)
- Recommended then: No explicit single recommendation stated; assistant presented all three neutrally, noting 'Re-scope ticket 06 here' risked the map's own warning against letting a refactor take the release gate hostage.
- Reply: `prototype what we now understand is needed` (deferred, accepted=False)
- Recorded in: .scratch/computed-semver/map.md (ticket 06); later .scratch/policy-composition/

## P066 [2026-08-21T1533_4ea03a72 2026-08-21T16:08] Four open uncertainties about what 'mash up' composition means
- Q: What would you like to clarify? (1) direction of inheritance — is the child the adopter, or can a publisher also compose; (2) what gets inherited — a policy's rules, the whole policy set, or the control catalogue/rationale; (3) whether 'mash up' implies override at all, or composition only with no override; (4) whether the bump is even the point, or composition is a bigger idea the gate only consumes
- Options: Say which of the four is off, or name something else
- Recommended then: None given — open clarifying question, no recommendation offered
- Reply: `prototype what we now understand is needed` (deferred, accepted=False)
- Recorded in: .scratch/computed-semver/map.md (ticket 06); later .scratch/policy-composition/

## P067 [2026-08-21T1958_e07c76bf 2026-08-21T20:01] Coverage figure: number or list
- Q: Bullet 1 of the ticket asks for a coverage figure over the CEL expressions. A percentage invites a threshold, which invites tuning the corpus until it passes.
- Options: (a) a percentage, (b) a list of what the run did not look at plus raw counts, (c) both
- Recommended then: (b). Publish counts and an explicit 'not looked at' list. Publish no percentage.
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/04-coverage-stated-not-implied.md

## P068 [2026-08-21T1958_e07c76bf 2026-08-21T20:01] Unit of measurement for coverage
- Q: Two candidates measure different things: cells (each subject CEL expression against satisfied/violated/absent) vs full shapes (ticket 03's pairwise combinations, most of which are never built).
- Options: Cells only; full shapes only; both
- Recommended then: Report both, with different jobs: cells as a completeness self-check, the pairwise gap stated as 'we built N of M combinations, pairwise by design'.
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/04-coverage-stated-not-implied.md

## P069 [2026-08-21T1958_e07c76bf 2026-08-21T20:01] Handling an expression no pod reached
- Q: Under ticket 03's generator an unreached expression is normally a generator defect, but some expressions cannot be satisfied at all (contradiction, unpopulated field).
- Options: Fail hard and name it vs. allow silent exclusion vs. declared exclusion file
- Recommended then: Fail hard and name the expression. Add a declared exclusion file for unsatisfiable ones, each entry with a reason, printed in the evidence. Silence is never allowed.
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/04-coverage-stated-not-implied.md

## P070 [2026-08-21T1958_e07c76bf 2026-08-21T20:01] What can fail the build
- Q: Bullet 3 asks whether low coverage blocks a release.
- Options: Percentage threshold vs. binary gates
- Recommended then: No percentage threshold. Three binary gates: unreached expression fails; witness shape missing from generated spine fails (per ticket 03); movement traced to an unversioned policy fails (per ticket 03). The pairwise gap never blocks, only stated.
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/04-coverage-stated-not-implied.md

## P071 [2026-08-21T1958_e07c76bf 2026-08-21T20:01] Artefact and its readers
- Q: Bullet 4 lists three places evidence could live; how many artefacts and views should there be.
- Options: Separate artefacts per reader vs. one signed source with multiple views
- Recommended then: One source, three views. CI writes one signed evidence JSON, renders it to markdown in the Renovate PR body, and release notes link the signed file. The PR body gets the design effort.
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/04-coverage-stated-not-implied.md

## P072 [2026-08-21T1958_e07c76bf 2026-08-22T06:45] Predicates vs variables in coverage model
- Q: Ticket 03's model of 'satisfied/violated/absent' per CEL expression only fits predicate expressions; several live expressions (e.g. cage-tier's rawTier, dial) are variables returning strings/objects, for which 'satisfied' is meaningless.
- Options: Extend the model to variables somehow vs. restrict coverage definition to predicates only
- Recommended then: Define coverage over predicate expressions only (matchConditions and validations). A variable is covered when an enumerated axis spans its value space; uncovered variables (dial, container rewrite) are named in the not-looked-at list. This is a correction to ticket 03's wording, not a new axis.
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/04-coverage-stated-not-implied.md

## P073 [2026-08-21T1958_e07c76bf 2026-08-22T06:45] Who may add an exclusion entry
- Q: Q3 created an exclusion file for unreachable expressions; an exclusion file is an escape hatch that risks bringing curation back.
- Options: Single-tier exclusion list vs. two-tier (proved vs. declared) with different authority
- Recommended then: Two tiers, gate decides which one an entry gets. Gate-proved entries become proved exclusions; entries the gate cannot prove stay declared holes and print in the not-looked-at list every release. A human may declare a hole but may not promote it to proved.
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/04-coverage-stated-not-implied.md

## P074 [2026-08-21T1958_e07c76bf 2026-08-22T06:45] Evidence field set
- Q: Q5 settled one signed JSON with three views; this fixes what fields it carries.
- Options: Open-ended/optional fields vs. a fixed nine-field set
- Recommended then: Nine fixed fields: declared bump, computed bump, per-policy verdict movement, three entry counts (old/new/union), generator version, corpus checksum, wall-clock, not-looked-at list, derived limits with counts, per-institution matrix from ticket 03. Nothing else, no field optional.
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/04-coverage-stated-not-implied.md

## P075 [2026-08-21T1958_e07c76bf 2026-08-22T06:45] Whether a hole has a stable identity
- Q: A reviewer reading the PR body needs to know not just 'are there holes' but 'is this a new hole'.
- Options: No identity tracking vs. stable id per not-looked-at entry
- Recommended then: Give each not-looked-at entry a stable id derived from the expression identity, not its position, so the PR body shows holes as carried over, new, or closed since the last release.
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/04-coverage-stated-not-implied.md

## P076 [2026-08-21T1958_e07c76bf 2026-08-22T06:51] What the stable id is derived from
- Q: Q11's id must survive a version bump or every hole reads as new at exactly the release that matters. Message text is unusable (embeds version literals); list index is unusable (reorder invents holes).
- Options: Message text; list index; hash of normalised expression text
- Recommended then: The id is a hash of the normalised expression text, scoped by identity family and policy name with version stripped, per ticket 06's normalisation rule.
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/04-coverage-stated-not-implied.md

## P077 [2026-08-21T1958_e07c76bf 2026-08-22T06:51] Whether the gate emits evidence when it refuses
- Q: Three conditions fail the build under Q4; should the gate emit anything when it refuses.
- Options: Emit nothing on failure vs. always emit and sign evidence, even on refusal
- Recommended then: Always emit the evidence and always sign it. The outcome field carries 'refused' and names the reason; every other field is still populated as far as the run got. A refusal is the most valuable evidence the gate produces.
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/04-coverage-stated-not-implied.md

## P078 [2026-08-22T0817_01e7460c 2026-08-22T08:25] Refuse, warn, or correct a weaker-than-computed declared bump
- Q: A release declares 2.1.0 but the evidence computes major. Does the gate fail the release, warn and proceed, or rewrite the tag to 3.0.0?
- Options: fail/refuse; warn and proceed; rewrite the tag
- Recommended then: Refuse and never rewrite; permit a stronger declared bump with the discrepancy printed in evidence; split the rule on the under/over-declare asymmetry.
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/05-the-gate-and-disagreement.md

## P079 [2026-08-22T0817_01e7460c 2026-08-22T08:25] Where the declared bump is read from
- Q: Read the declared bump from the tag, versions.yaml, or the PR title?
- Options: tag; versions.yaml; PR title
- Recommended then: Read from cut-release.yml's version input, gate before git tag; keep a second cheaper check in release.yml verifying signed evidence matches the tag.
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/05-the-gate-and-disagreement.md

## P080 [2026-08-22T0817_01e7460c 2026-08-22T08:25] One gate or two, and what the adopter's gate asks
- Q: Should there be one gate or two (publisher vs adopter), and what does the adopter's gate compute?
- Options: single shared gate; two gates asking different questions
- Recommended then: Two gates: publisher computes/signs one bump at the strictest band; adopter verifies signature identity-pinned then computes its own composed bump.
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/05-the-gate-and-disagreement.md

## P081 [2026-08-22T0817_01e7460c 2026-08-22T08:25] Five unversioned policies blocking every release from day one
- Q: Should the gate ship hard (blocking every release until the five unversioned Kyverno policies get versions) or ship with a grace mode?
- Options: ship hard; ship with a grace mode/threshold
- Recommended then: Ship it hard, version the five first as a prerequisite task under ticket 07; a grace mode is a threshold that never gets removed.
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/05-the-gate-and-disagreement.md

## P082 [2026-08-22T0817_01e7460c 2026-08-22T08:29] The override path for a human who wants a weaker bump
- Q: Should there be a legitimate override path when the human believes the gate's computed bump is wrong and wants a weaker bump than computed?
- Options: allow an override with evidence/signature/expiry; no override
- Recommended then: No override at all. An override is what exemptions.yaml carried, and that argument lost on 2026-08-20. Make the refusal actionable via a reviewed PR to the generator or policy instead.
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/05-the-gate-and-disagreement.md

## P083 [2026-08-22T0817_01e7460c 2026-08-22T08:29] Which predecessor the gate compares against
- Q: Compare against the immediately preceding tag only, every version in the supported window (strictest wins), or every tag ever cut?
- Options: N-1 only; every version in supported window, strictest wins; every tag ever cut
- Recommended then: Every version in the supported window, strictest result wins; comparing only N-1 hides breaks for clusters on N-2.
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/05-the-gate-and-disagreement.md

## P084 [2026-08-22T0817_01e7460c 2026-08-22T08:29] How evidence is signed, transported and verified
- Q: Use the existing feeds/sign.sh repo-local PEM key shape, or a different signing/transport mechanism, given the evidence must now reach an adopter in another org before the tag exists?
- Options: feeds/sign.sh PEM key; cosign sign-blob keyless with committed bundle
- Recommended then: Drop feeds/sign.sh; sign with cosign sign-blob keyless using OIDC identity for both outcomes; commit evidence JSON and bundle at a fixed path on success; run artifact + job summary on refusal.
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/05-the-gate-and-disagreement.md

## P085 [2026-08-22T0817_01e7460c 2026-08-22T08:29] When the adopter's composed bump disagrees with the publisher's tag
- Q: Does the adopter's check fail the Renovate PR when its composed bump differs from the publisher's tag, or only report?
- Options: fail the PR; only report
- Recommended then: Fail the PR when the composed bump is major; only report otherwise. Print both bumps side by side in the PR body.
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/05-the-gate-and-disagreement.md

## P086 [2026-08-22T0817_01e7460c 2026-08-22T08:35] What triggers the adopter's gate and where composition inputs come from
- Q: Does the adopter's gate run on a schedule or only on pull requests, and where do its composition inputs come from?
- Options: scheduled check; PR-only trigger
- Recommended then: Only on pull requests, never on a schedule, because ADR-0002 makes the reviewed PR the unit of adoption; composition inputs are the pinned versions in the institution's own repo at PR head.
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/05-the-gate-and-disagreement.md

## P087 [2026-08-22T0817_01e7460c 2026-08-22T08:35] A platform release that only edits the version array (retirement)
- Q: Does an array-only release (no policy body change) trigger the gate, and does retiring an old version count as a major break, given ticket 07 owns the platform's own versioning?
- Options: wait for ticket 07 to define this; gate it now and treat retirement as major
- Recommended then: The gate runs on an array-only release, and a retired element computes major; don't wait for ticket 07, which only gets the numbering mechanics.
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/05-the-gate-and-disagreement.md

## P088 [2026-08-22T0817_01e7460c 2026-08-22T08:40] The adopter checks out platform's default branch instead of the pinned tag (live bug)
- Q: Which ref should the cross-org adopter gate check out, given shift-left.yml today checks out platform with no ref (default branch), not the institution's pinned tag?
- Options: leave as default-branch checkout; check out the pinned tag from gitops/platform/platform-pin.yaml
- Recommended then: Check out the tag under review, read from gitops/platform/platform-pin.yaml at PR head; verify resolved commit matches the pinned commit and refuse otherwise. Fix as part of this ticket, not logged as future work.
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/05-the-gate-and-disagreement.md

## P089 [2026-08-22T0817_01e7460c 2026-08-22T08:40] Where the adopter's expected-identity constant lives
- Q: Should the expected-identity constant used to verify the publisher's signature be fetched from platform, or held locally by each institution?
- Options: fetch from platform; each institution holds its own pinned copy
- Recommended then: Each institution holds its own copy as a pinned constant, changed only by a reviewed PR; never fetch a trust identity from the party being checked.
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/05-the-gate-and-disagreement.md

## P090 [2026-08-22T0817_01e7460c 2026-08-22T08:40] Where the cosign bundle lives
- Q: Should the cosign verification bundle stay as a PR comment, or be committed alongside the evidence for future re-verification?
- Options: PR-comment only; commit bundle next to evidence JSON in the release commit
- Recommended then: Commit the bundle next to the evidence JSON in the release commit so verification is offline by construction; keep PR-comment rendering as a convenience view.
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/05-the-gate-and-disagreement.md

## P091 [2026-08-22T0817_01e7460c 2026-08-22T08:50] Which window a retiring release compares against
- Q: Does a retiring release compare against the window as it stood before or after the retirement, given the retirement shrinks the window?
- Options: compare against window after retirement; compare against window as it stood before this release
- Recommended then: Compare against the window as it stood before this release, so the retirement's major impact falls out of the comparison naturally.
- Reply: `20 just like with normal software, it may be desirable to patch a previous old version of the policy whilst still suppor` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/05-the-gate-and-disagreement.md

## P092 [2026-08-22T0817_01e7460c 2026-08-22T08:54] What a backport compares against
- Q: Given the window comparison from Q7/Q19, what should a backport release compare against, since comparing against a higher unrelated line measures nothing?
- Options: compare against the whole supported window; compare against every supported version lower than the declared version, strictest wins
- Recommended then: Compare against every supported version lower than the declared version, strictest result wins; for a head release this is unchanged, for a backport it narrows to the line below.
- Reply: `22 whatever the best practice for implementing semvers says
Otherwise, I agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/05-the-gate-and-disagreement.md

## P093 [2026-08-22T0817_01e7460c 2026-08-22T08:54] Maintenance branches break the identity pin
- Q: A backport dispatched from a maintenance branch produces a gitsign identity ending in that branch ref, which every release.yml's hardcoded main-only identity pin would reject. How should this be resolved?
- Options: keep main-only pin (backports stay unreleasable); adopt release/<major>.<minor>.x branches with an anchored regexp allowing both main and that branch shape
- Recommended then: Adopt release/<major>.<minor>.x branches and pin with an anchored --certificate-identity-regexp allowing refs/heads/main and that branch shape; treat as part of this ticket since backports are unreleasable without it.
- Reply: `22 whatever the best practice for implementing semvers says
Otherwise, I agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/05-the-gate-and-disagreement.md

## P094 [2026-08-22T0817_01e7460c 2026-08-22T09:40] Final confirmation of the full 24-decision shared understanding
- Q: The assistant summarized all 24 settled decisions across 6 rounds (what the gate decides, where it runs, what it compares against, what it publishes, what changes in the estate) and asked the user to confirm before writing the ticket answer, resolving it, and updating the map.
- Options: confirm; request changes
- Recommended then: (no separate recommendation; this was a request to confirm the accumulated summary)
- Reply: `Confirm` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/05-the-gate-and-disagreement.md

## P095 [2026-08-22T1006_af93f742 2026-08-22T10:23] Q0 - naming the problem: is 'unversioned' the right frame
- Q: Do four of the five policies (plus the second v1.0.0 tree) share a deeper trait -- delivered outside the pinned path -- so this ticket should own delivery as well as numbering, or is that a separate ticket, or is graded/posture scaffolding that should be dropped from scope?
- Options: (a) this ticket owns delivery and numbering together; (b) delivery is a separate ticket, this one decides numbering only; (c) graded/posture are demo scaffolding never meant to ship, shrink the claim
- Recommended then: (a), and raise the installed-set assumption back to cs-05 as a finding
- Reply: `0 agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/07-platform-version-under-the-same-rule.md

## P096 [2026-08-22T1006_af93f742 2026-08-22T10:28] Q4 - what makes a change major when the cage is the only enforcement
- Q: With no content gate, what should 'major' mean: a viability estimate of whether a workload can still run under the new dial, any downward move of any dial regardless of who it affects, or keep admission as the definition and treat cage tightening as minor?
- Options: (a) viability rule, estimate whether workload can still run; (b) movement rule, any downward dial move is major, no estimate of impact; (c) keep admission as the definition, cage tightening is minor
- Recommended then: (b)
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/07-platform-version-under-the-same-rule.md

## P097 [2026-08-22T1006_af93f742 2026-08-22T10:28] Q5 - how the anti-forgery pair survives one mechanism
- Q: Under one mechanism, stamp-posture/posture-trust-boundary risk a silent hole if a version tree ships without its copy. Should the release gate refuse a version tree missing a mandatory member, should a renderer generate the pair into every tree automatically, or accept the hole and rely on review?
- Options: (a) release gate refuses a tree missing a mandatory member; (b) renderer generates the pair into every version tree automatically; (c) accept the hole, rely on review
- Recommended then: (b)
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/07-platform-version-under-the-same-rule.md

## P098 [2026-08-22T1006_af93f742 2026-08-22T10:28] Q6 - do the cage's non-Kyverno dials (PriorityClasses) enter the version trees
- Q: Should the three PriorityClasses get versioned copies with distinct names, stay single-instance and shared with edits reaching every version at once, or should the eviction dial be deleted from the cage entirely?
- Options: (a) yes, versioned copies with versioned names; (b) stay single-instance/shared, gate prints it as unmeasured; (c) delete the eviction dial from the cage
- Recommended then: (a), reluctantly, as the price of the Q1 answer
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/07-platform-version-under-the-same-rule.md

## P099 [2026-08-22T1006_af93f742 2026-08-22T10:31] Q7 - what the platform's own number covers, and what computes it
- Q: Should the platform tag use one rule/one gate/one corpus covering everything Q0 pulls into the pinned path, two separate rules for policy tags vs platform tag, or should the two tag namespaces collapse into one number?
- Options: (a) one rule, one gate, one corpus; (b) two rules, verdict movement for policy/vN, machinery rule for platform tag; (c) collapse the two namespaces into one number
- Recommended then: (a)
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/07-platform-version-under-the-same-rule.md

## P100 [2026-08-22T1006_af93f742 2026-08-22T10:31] Q8 - does the platform number cover the orphan guard's own CEL
- Q: Should the platform number cover the versions.yaml template (classified by the same verdict rule), should the orphan guard get its own third version line, or should only the generated allow-list be measured while the template is machinery?
- Options: (a) platform number covers the template, classified by the same verdict rule; (b) the guard gets a third version line of its own; (c) template is machinery, only the generated allow-list is measured
- Recommended then: (a)
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/07-platform-version-under-the-same-rule.md

## P101 [2026-08-22T1006_af93f742 2026-08-22T10:31] Q9 - what happens to the orphaned policy/policies/v1.0.0 tree
- Q: The uninstalled policy/policies/v1.0.0/ tree contradicts distribution's 1.0.0. Should it become a second policy family with its own array element, fold into the single distribution line at its correct (wider) number, or be deleted as demo material?
- Options: (a) second policy family, own array element and claim; (b) fold into the distribution line at its correct number; (c) delete it as demo material
- Recommended then: (b), at 1.0.1, as a backport
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/07-platform-version-under-the-same-rule.md

## P102 [2026-08-22T1006_af93f742 2026-08-22T10:31] Q10 - does the platform leave 0.x
- Q: At v0.1.1 the gate has no teeth under semver's 0.x rule. Should the repair release cut platform 1.0.0, should the gate apply >=1.0.0 rules anyway by local dialect, or should the gap be accepted until a natural 1.0.0?
- Options: (a) cut 1.0.0 as part of this ticket's repair release; (b) stay at 0.x, apply the rules by local rule; (c) accept the gap until a natural 1.0.0
- Recommended then: (a)
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/07-platform-version-under-the-same-rule.md

## P103 [2026-08-22T1006_af93f742 2026-08-22T10:38] Q12 - where the source of truth lives, and what git holds
- Q: Given per-version trees need per-version copies of claim-wide policies with no omissions, should every version tree be hand-authored, should one authoring copy under graded/posture be rendered into committed per-version copies, or should a ResourceSet template render copies only at reconcile time (git holds only a template)?
- Options: (1) hand-authored copies, N copies written by hand, renderer only checks; (2) one authoring copy, renderer emits per-version copies, emitted copies committed; (3) template renders copies at reconcile time, git holds only a template
- Recommended then: (2)
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/07-platform-version-under-the-same-rule.md

## P104 [2026-08-22T1006_af93f742 2026-08-22T10:41] Q15 - which trees CI re-renders, and what the gate reads for an older version
- Q: Should CI re-render only the tree being cut and read prior versions from their tag with a frozen-tree check, re-render everything and fail on any diff, or version the authoring copy itself with a directory per version?
- Options: (a) re-render only the cut tree, gate reads prior versions from their tag, frozen-tree check; (b) re-render everything, fail on any diff; (c) version the authoring copy too
- Recommended then: (a)
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/07-platform-version-under-the-same-rule.md

## P105 [2026-08-22T1006_af93f742 2026-08-22T10:41] Q16 - how the repair avoids uncaging every pod on an already-released version
- Q: Since cut tags cannot gain files, deleting the shared cage-tier would strip enforcement from every pod pinned to an existing version. Should both supported versions be re-cut with the full set and swapped in one release, should shared and per-version copies run side by side through a transition window, or should the old versions simply be retired?
- Options: (a) re-cut both supported versions as new patch releases with the full set, swap the array in one release; (b) run shared and per-version copies side by side through a transition window; (c) retire the old versions and publish only the new pair
- Recommended then: (a)
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/07-platform-version-under-the-same-rule.md

## P106 [2026-08-22T1006_af93f742 2026-08-22T10:44] Q17 - does enforcement removal get its own axis, or only a note
- Q: Since removing a cage scores as a patch under the workload-side rule, should this be recorded only as a named limit, should the gate gain a second structural axis that refuses a release removing an enforcement surface regardless of computed bump, or should 'major' itself be redefined to include enforcement removal?
- Options: (a) record as a named limit, leave the rule alone; (b) gate refuses a release that removes an enforcement surface, as a refusal not a bump class; (c) redefine major to include enforcement removal
- Recommended then: (b)
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/07-platform-version-under-the-same-rule.md

## P107 [2026-08-22T1006_af93f742 2026-08-22T10:45] Q20 - restating the major-bump rule at spec level for cage-tier's full mutation set
- Q: cage-tier changes more than dials (sidecar injection, priorityClassName, hardening flags, capability drops). Should the rule compare rendered cage specs and call it major when the new spec isn't at least as permissive as the old, enumerate the specific surfaces that count, or treat any spec difference at all as major?
- Options: (a) spec-level comparison, major when the new spec is not at least as permissive as the old; (b) enumerate the counted surfaces (dials, sidecars, capabilities, priority class); (c) any spec difference at all is major
- Recommended then: (a)
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/07-platform-version-under-the-same-rule.md

## P108 [2026-08-22T1006_af93f742 2026-08-22T10:45] Closing confirmation of the full 21-decision shared understanding
- Q: The assistant summarized all 21 decisions (D1-D4, the repair release shape, four new gate rules, two named limits, and the three-child-ticket output shape) and asked the user to confirm before writing the answer into ticket 07, opening child tickets, and filing the cs-05 finding.
- Options: confirm the summarized design as written, or send back corrections
- Recommended then: confirm
- Reply: `Confirm` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/07-platform-version-under-the-same-rule.md

## P109 [2026-08-22T1053_e99f72e6 2026-08-22T10:55] Spec scope for computed-semver
- Q: What should the spec cover?
- Options: (1) The whole release gate [Recommended] - one spec for the gate computing major/minor/patch from verdict movement, refusing weaker declared bumps, signing evidence; tickets 09/10/11 become the implementation path, the 7 resolved tickets become Implementation Decisions. (2) Only the three open tickets - narrower spec covering renderer(10), repair release(09), four gate rules(11), assumes gate design already settled. (3) The policy-composition map instead - write spec for cross-party composition, the other open map.
- Recommended then: The whole release gate
- Reply: `[No user reply text appears in the digest for this AskUserQuestion tool call — it was presumably answered via UI option ` (bare_letter, accepted=True)
- Recorded in: .scratch/computed-semver/spec.md

## P110 [2026-08-22T1053_e99f72e6 2026-08-22T10:55] Test seam for computed-semver gate
- Q: Where do the tests attach?
- Options: (1) One seam: the evidence document [Recommended] - single entry point in platform/computed-semver/ returns evidence dict; computed bump, per-institution matrix, coverage counts, not-looked-at list, derived limits, refusal reasons all report through it; renderer surfaces via gate rule 2. (2) Two seams: renderer and gate - renderer(ticket 10) gets its own seam/tests following render-orphan-guard.py's --selfcheck pattern, gate gets a second seam. (3) Bash beats only - no new Python test seam, extend estate's existing verify-*.sh convention (SKIPs when kyverno CLI absent).
- Recommended then: One seam: the evidence document
- Reply: `[No user reply text appears in the digest for this AskUserQuestion tool call — same as above, answered via UI selection ` (bare_letter, accepted=True)
- Recorded in: .scratch/computed-semver/spec.md

## P111 [2026-08-22T1106_eab00d9c 2026-08-22T12:10] Ticket breakdown approval (granularity, blocking edges, split candidates, numbering)
- Q: Four-part quiz on the proposed 19-ticket breakdown of computed-semver: (1) Does the granularity feel right? (2) Are the blocking edges correct, given Lane B has no dependency on Lane A? (3) Should A4/ticket 15 split further, or should B2 and B3 merge into one corpus ticket? (4) Number new tickets from 12 onward, or replace tickets 09/10/11 in place?
- Options: (1) too coarse / too fine / right as proposed; (2) edges correct / edges wrong; (3) split A4 further / merge B2+B3 / leave as proposed; (4) number from 12 (keep 09-11 as split markers) / renumber in place over 09-11
- Recommended then: Assistant recommended: keep A4 whole because the publish and array swap must land in one commit; give Lane B no dependency on Lane A since the gate engine validates against the read-only faithful-floor line; number new tickets from 12, leaving 09-11 as pointers to their replacement slices.
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/computed-semver/issues/12-*.md through 30-*.md; tickets 09, 10, 11 marked Status: split; map.md and spec.md updated

## P112 [2026-08-22T1526_6b3745ad 2026-08-22T15:32] How to handle the 18 tickets whose code lives in repos the assistant cannot push to (enact_guard.py blocks it)
- Q: How should I handle the 18 tickets whose code lives in the platform/enactment repos, which I cannot push to?
- Options: (1) Implement + commit locally in .estate-clone/* [labeled Recommended]; (2) Hub-only: ticket 30 plus a design doc, no code in .estate-clone/; (3) Full scope including live pushes and real release tags, would need the guard disabled
- Recommended then: Option 1: implement and commit locally in .estate-clone/*, push only ticket 30 to the hub, leave the rest for the user's own PR channel
- Reply: `[Not captured in transcript text — this was an AskUserQuestion tool call; the digest contains no USER turn with the sele` (bare_letter, accepted=True)
- Recorded in: .scratch/computed-semver/ (session scope, not a single ticket)

## P113 [2026-08-22T1526_6b3745ad 2026-08-22T16:07] Final confirmation before touching the guard at all, given new evidence this repo has never crossed this EU AI Act Article 22-grounded boundary
- Q: Given this is a deliberate, EU AI Act Article 22-grounded rule that nothing in this codebase has ever crossed, do you still want me to be the first thing that does — disabling the guard myself and pushing the code and the real signed release tags end to end?
- Options: (1) Yes, proceed exactly as I said, disable guard + push code + dispatch releases myself end to end [assistant explicitly noted 'Recommended is not implied' for this option]; (2) No — implement and push code myself (reversible), but the user triggers the release; (3) No — keep the guard on, prepare everything as unpushed local branches, user pushes/opens PRs themselves
- Recommended then: None marked recommended — assistant deliberately declined to recommend on this irreversible question
- Reply: `[Not captured in transcript text. Inferred from subsequent behavior, which matches option 2: the assistant pushed code/w` (bare_letter, accepted=False)
- Recorded in: .scratch/computed-semver/

## P114 [2026-08-22T1526_6b3745ad 2026-08-22T22:39] How to number the repair release after the gate itself computed the planned 1.0.2/2.0.1 numbers as under-declaring a real major break
- Q: The prepared repair release computes as a real major break (cage-tier resource clamping) but the plan names it 1.0.2/2.0.1. How should I resolve the numbering before this becomes a real signed release?
- Options: (1) Renumber to a major bump (e.g. 2.0.0/3.0.0-shaped); (2) Ship 1.0.2/2.0.1 with a documented exception explaining the newly-live cage-tier enforcement; (3) Split the release: ship require-nonroot/posture now, phase cage-tier in separately as its own later major release
- Recommended then: None of the three options was marked Recommended
- Reply: `[Not captured in transcript text. Inferred from the assistant's next move: it investigated whether option 1's premise (a` (bare_letter, accepted=False)
- Recorded in: .scratch/computed-semver/issues/15-*.md

## P115 [2026-08-24T1430_9966d8b3 2026-08-24T14:32] Composed artefact: published vs ephemeral
- Q: Is a composed artefact itself a new thing a party publishes and signs (its own asset, checked into the estate), or is it purely ephemeral — computed at reconcile time from parents' signed artefacts and never itself signed or stored?
- Options: Published and signed (Recommended) | Ephemeral, never signed
- Recommended then: Published and signed — the composed set becomes a real artefact of its own, committed, versioned, and signed, so a verifier can trust it directly without re-deriving it every time.
- Reply: `[No free-text reply is present in the digest between this AskUserQuestion block and the next assistant turn. The choice ` (bare_letter, accepted=True)
- Recorded in: .scratch/policy-composition/issues/02-what-gets-signed.md

## P116 [2026-08-24T1430_9966d8b3 2026-08-24T14:32] Signer identity for a composed artefact
- Q: Who or what would hold the signing identity for a composed artefact, if it is signed at all?
- Options: The adopter (subclass) signs its own composed set (Recommended) | A shared composition service signs every composed set | Not applicable — composed sets aren't signed
- Recommended then: The adopter (the subclass) — driftwood, tuppence, ludlow etc. each sign their own composed effective policy set, the way they already own their own artefact today.
- Reply: `[No free-text reply present in digest; UI option-select not captured as quoted text.]` (bare_letter, accepted=True)
- Recorded in: .scratch/policy-composition/issues/02-what-gets-signed.md

## P117 [2026-08-24T1430_9966d8b3 2026-08-24T14:32] Reproducibility bar for verifying a composed set
- Q: How strict does 'reproducible from signed parent digests' need to be, for a verifier to trust a composed set?
- Options: Byte-for-byte deterministic re-render (Recommended) | Semantically equivalent, not byte-identical
- Recommended then: Byte-for-byte deterministic re-render — given the same parent digests and composition logic, output must be byte-identical every time, the bar ticket 01's prototype already met.
- Reply: `[No free-text reply present in digest; UI option-select not captured as quoted text.]` (bare_letter, accepted=True)
- Recorded in: .scratch/policy-composition/issues/02-what-gets-signed.md

## P118 [2026-08-24T1430_9966d8b3 2026-08-24T14:51] Where composed-artefact verification happens
- Q: Facts found: Flux cannot verify gitsign at admission (a known, still-open upstream gap — ADR-0001's own noted consequence). Every signature check today happens in CI/at merge, never at the cluster boundary. Does composing multiple parties' artefacts raise the bar past that floor?
- Options: CI/merge-time only, same floor as today (Recommended) | Composition needs admission-time verification
- Recommended then: CI/merge-time only, same floor as today — admission-time verification stays the separate, already-flagged Flux/gitsign gap, not something this ticket takes on.
- Reply: `[No free-text reply present in digest; UI option-select not captured as quoted text.]` (bare_letter, accepted=True)
- Recorded in: .scratch/policy-composition/issues/02-what-gets-signed.md

## P119 [2026-08-24T1430_9966d8b3 2026-08-24T14:51] Explicit marker distinguishing composed from leaf artefacts
- Q: The adopter signs its own composed artefact, the same way it signs its own artefacts today. Does a verifier need a way to tell, from the artefact alone, that this one is composed — declares external parents — rather than a leaf artefact with no parents?
- Options: Yes — mark it explicitly (Recommended) | No — same shape either way
- Recommended then: Yes — mark it explicitly; a verifier checking a composed artefact also has parent SHAs to check, so it needs to know which case it's in.
- Reply: `[No free-text reply present in digest; UI option-select not captured as quoted text.]` (bare_letter, accepted=True)
- Recorded in: .scratch/policy-composition/issues/02-what-gets-signed.md

## P120 [2026-08-24T1651_864040ab 2026-08-24T16:55] Who declares the compliance baseline
- Q: Who declares the baseline: the regulator (knows the catalogue, not the system), the publisher (coverage would be tautological), or the adopter (bears the cost of a missing control)?
- Options: regulator declares; publisher declares; adopter declares
- Recommended then: Split it: the regulator publishes named baselines as versioned, signed OSCAL profiles; the adopter selects one by name, since selection is the risk-bearing act.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/03-baseline-and-catalogue-ids.md

## P121 [2026-08-24T1651_864040ab 2026-08-24T16:55] Canonical control id form
- Q: What is the canonical form for a control id, given the catalogue uses bare lowercase ('ac-6'), display labels use 'AC-6'/'AC-06', the estate mapping uses 'nist-800-53:AC-6', and the prototype invented 'nist-800-53:ac-6'?
- Options: bare catalogue id (ac-6); prefixed id (nist-800-53:ac-6); display label (AC-6)
- Recommended then: Bare catalogue id exactly as the catalogue writes it, 'ac-6'. The prefix is duplicated state since the catalogue is already named by the enclosing source/href. Display labels never become keys.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/03-baseline-and-catalogue-ids.md

## P122 [2026-08-24T1651_864040ab 2026-08-24T16:55] Resolver behavior on an unresolvable id
- Q: What should the resolver do with an id it cannot find in the catalogue -- be forgiving (case-fold, strip prefixes) or fail hard?
- Options: forgiving resolution (case-fold/strip); exact-string match with hard failure
- Recommended then: Resolve by exact string against the catalogue, never case-fold or strip; an unmatched id is a hard failure with the id printed. Also require the resolver to walk nested controls so enhancements like ac-6.10 aren't missed by a group-level scan.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/03-baseline-and-catalogue-ids.md

## P123 [2026-08-24T1651_864040ab 2026-08-24T16:55] Handling a baseline control nothing implements
- Q: What happens to a baseline control that nothing implements, given MODERATE has 287 controls and the estate implements only 2 -- refuse composition on the absolute hole count, or something else?
- Options: refuse on absolute hole count; refuse only on a new hole vs. prior composition
- Recommended then: Do not refuse on absolute hole count. Refuse only on a new hole relative to the previously composed set; print the count and list of hole ids so an old hole is tracked debt and a new hole is a refusal.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/03-baseline-and-catalogue-ids.md

## P124 [2026-08-24T1651_864040ab 2026-08-24T17:00] Which named baseline the estate selects
- Q: Which named baseline does this estate select -- LOW (149 controls, excludes ac-6), MODERATE (287, includes both implemented controls plus ac-6.10), or a bespoke regulator-published estate-specific baseline?
- Options: LOW; MODERATE; bespoke estate-sized baseline
- Recommended then: MODERATE. LOW is factually wrong since ac-6 falls outside it; a bespoke baseline sized to what's implemented is the tautology Q1 rejected. MODERATE means 285 recorded holes on day one, which the new-hole-only refusal rule (Q4) makes shippable.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/03-baseline-and-catalogue-ids.md

## P125 [2026-08-24T1651_864040ab 2026-08-24T17:00] Where the adopter's baseline selection is recorded
- Q: Which document holds the adopter's baseline selection -- the existing nist-pin-configmap.yaml (currently documented as a mirror), a new adopter-side OSCAL profile, or the composed artefact from ADR-0012?
- Options: nist-pin-configmap.yaml as authoritative; new OSCAL profile; ADR-0012 composed artefact
- Recommended then: The adopter's own party artefact, the input it gitsign-signs under ADR-0012. nist-pin-configmap.yaml gains a baselineName key and stays a mirror; no new file is created.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/03-baseline-and-catalogue-ids.md

## P126 [2026-08-24T1651_864040ab 2026-08-24T17:00] Whether the adopter may tailor the selected baseline
- Q: May the adopter tailor the selected baseline by removing controls, since OSCAL tailoring profiles support both addition and removal?
- Options: allow add and remove; add only
- Recommended then: Add only. Removal is an exemption by another name, and the map's standing preference forbids exemptions -- a control the adopter can't meet goes to the cage and is priced, never removed from the baseline.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/03-baseline-and-catalogue-ids.md

## P127 [2026-08-24T1651_864040ab 2026-08-24T17:00] Comparison point for the new-hole test
- Q: What does the new-hole test (Q4) compare the current composition against -- a separate state file, git history of the composed file, or the adopter's last signed composed artefact?
- Options: separate state file; git history; last signed composed artefact
- Recommended then: The adopter's last signed composed artefact, since ADR-0012 already makes it published, versioned and signed -- adds no new store and makes the hole list signed evidence for an auditor.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/03-baseline-and-catalogue-ids.md

## P128 [2026-08-24T1651_864040ab 2026-08-24T17:03] Behavior when the adopter deliberately widens its own baseline
- Q: When the adopter moves from MODERATE to HIGH, adding 83 controls at once, should the composition refuse (since nearly all become new holes), even though the adopter did this deliberately?
- Options: refuse anyway with no override; add an override/exemption flag for a deliberate widening
- Recommended then: Refuse anyway, and do not add an override. The refusal is the point -- it tells the adopter the exact price of widening before the claim lands; it clears the same way any refusal clears, via a reviewed PR, never an 'I meant it' flag, since that would be an exemption branch the map forbids.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/03-baseline-and-catalogue-ids.md

## P129 [2026-08-24T1724_f36d4c59 2026-08-24T17:30] How many things does 'no label' mean on a pod (infra vs. de-postured vs. evader)
- Q: Absence of the claim label currently covers three different situations (infra that never claims, a deliberately de-postured workload, and an evader). The guard cannot tell them apart. Should the estate name these apart, or treat 'no label' as one thing?
- Options: Treat all 'no label' cases as one thing vs. name the three cases apart and use a different signal for the deny-worthy case
- Recommended then: Name them apart. Absence alone cannot distinguish infrastructure from an evader, so absence alone must never be the deny trigger; only the evader case deserves a deny, via a different signal.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/04-unlabelled-pod-denial.md

## P130 [2026-08-24T1724_f36d4c59 2026-08-24T17:30] Is a de-postured pod a deliberate cage or an accident the guard should override
- Q: currency.py de-postures a stale pod by design (docstring: 'Keep running but caged'). Is that the intended settlement for a retired version, or a workaround a stricter guard should override?
- Options: Intended settlement (guard must keep skipping it) vs. workaround a stricter guard should override (i.e. deny it)
- Recommended then: It is the intended settlement and the map's standing preference in action. Deny is the bottom rung; a de-postured pod is caged, not denied, so the guard must keep skipping it.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/04-unlabelled-pod-denial.md

## P131 [2026-08-24T1724_f36d4c59 2026-08-24T18:11] Which side wins (code vs. CONTEXT.md), and what happens to the 'locked door' sentence
- Q: Under the committed behaviour, CONTEXT.md:161's claim that the orphan guard 'makes the gate tier a locked door rather than an opt-in door' is false, not merely narrow (silence bypasses it). (a) Delete the claim, or (b) narrow the claim to what is true and name the residual hole in the same entry.
- Options: (a) Delete the claim / (b) Narrow the claim and name the residual hole
- Recommended then: Option (b). The true statement is narrow: the guard locks the door against a claim, not against silence. Deleting would erase a real requirement from the record; the map prefers honesty over green, so the entry should carry the hole.
- Reply: `aggree` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/04-unlabelled-pod-denial.md

## P132 [2026-08-24T1724_f36d4c59 2026-08-24T18:11] How much of the fix mechanism to settle in this ticket vs. hand to platform
- Q: Ticket 03 sends the code to platform, but the residual hole still needs a shape or platform gets a complaint with no design. (a) Name the hole only, or (b) settle the mechanism here in one paragraph and hand the build over. The assistant proposed adding a sibling ValidatingPolicy scoped by a namespace label, matching CREATE only (never UPDATE), and flagged the namespace-label key itself as unset convention needing the user's decision.
- Options: (a) Name the hole only / (b) Settle the mechanism here (sibling ValidatingPolicy, namespace-scoped, CREATE-only)
- Recommended then: Option (b), with the described mechanism: a sibling ValidatingPolicy beside the guard, scoped by a namespace label, matching CREATE only so de-posture (an UPDATE) still passes.
- Reply: `aggree` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/04-unlabelled-pod-denial.md

## P133 [2026-08-24T1926_50fff040 2026-08-24T19:35] Which proposer raises the cage-tier drift
- Q: Do you extend the existing war-gamer with a tier-drift row, or build a separate composition proposer?
- Options: Extend the war-gamer / build a separate proposer
- Recommended then: Extend the war-gamer — the map's standing preference is to reuse the estate's engines, and a second proposer means a second thing proposer_bounds.py must bound.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/05-the-proposer.md

## P134 [2026-08-24T1926_50fff040 2026-08-24T19:35] What line the PR changes
- Q: Nothing today carries a tier on any adopter workload. Three options for what the proposer's PR edits: (a) posture.acme.io/tier on the adopter's workload manifest, (b) the adopter's composed artefact declares the tier as a signed risk declaration, (c) no diff — the proposer opens an issue instead.
- Options: (a) edit workload label / (b) composed-artefact tier declaration / (c) open an issue, no diff
- Recommended then: (a) — smallest change that works and edits what the engine actually reads; (b) is the better story but a larger build; (c) proposes nothing actionable.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/05-the-proposer.md

## P135 [2026-08-24T1926_50fff040 2026-08-24T19:35] What notices an EOL re-price with no commit
- Q: An EOL feed re-price moves price with no commit, so a push-triggered proposer would never see it. Does the proposer run on a clock, or wait for a human to dispatch a run?
- Options: Add a recurring schedule / workflow_dispatch plus push trigger on feed paths, and name the gap
- Recommended then: Ship workflow_dispatch plus a push trigger on the feed paths; name the EOL blind spot rather than close it — a live recurring schedule is a standing decision out of scope for this ticket.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/05-the-proposer.md

## P136 [2026-08-24T1926_50fff040 2026-08-24T19:37] Which repo runs the proposer
- Q: The war-gamer lives in platform, but the PR must edit a label in an adopter's repo, and platform's GITHUB_TOKEN can't open a cross-org PR, and no scoped credential exists. (a) run in platform on a credential that doesn't exist yet, or (b) invert it — the adopter runs the war-gamer against its own composition, in its own repo, on its own token.
- Options: (a) platform runs it, needs new cross-org credential / (b) adopter runs it against itself
- Recommended then: (b) — matches ADR-0013, avoids inventing the credential the estate has twice refused to invent; selection is the risk-bearing act so the risk-bearer proposes against itself.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/05-the-proposer.md

## P137 [2026-08-24T1926_50fff040 2026-08-24T19:37] Which subjects the proposer scans
- Q: Something must produce the list of workloads to price a tier for. (a) the composed artefact lists the adopter's caged subjects, (b) the proposer scans the adopter's committed workload manifests, (c) keep it org-level, one tier for the whole adopter.
- Options: (a) composed-artefact list / (b) scan committed manifests / (c) org-level only
- Recommended then: (b) — the PR edits a manifest so the proposer must read manifests anyway; also sharpens the map's open fog item about governed namespaces.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/05-the-proposer.md

## P138 [2026-08-24T1926_50fff040 2026-08-24T19:37] Whether a proposal may loosen a tier
- Q: cage.select returns the loosest tier that fits, so a falling residual could return a looser tier. Does the proposer emit loosening proposals, or tightening only?
- Options: Emit both directions / tightening only
- Recommended then: Emit both — tighten-only ratchets the estate to deny and never recovers; a human merges either direction so safety is unchanged, but a loosening proposal is the one a reviewer must read hardest.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/05-the-proposer.md

## P139 [2026-08-24T1926_50fff040 2026-08-24T19:39] Whether the proposer crosses the diff-only line
- Q: Both existing rail scripts deliberately stop at the diff. Does the tier proposer also stop there (leaving nothing to raise the PR), or does it commit, push, and run gh pr create?
- Options: Stop at diff (keep the rail) / cross it and open the PR
- Recommended then: Cross it — ADR-0010 already sanctions a machine opening a PR given allow_auto_merge:false and the require-pr-gate ruleset; the proposer still exposes no merge()/approve(). Note the estate then has two rails, not one.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/05-the-proposer.md

## P140 [2026-08-24T1926_50fff040 2026-08-24T19:39] What starts a run in the adopter's repo
- Q: (a) a Renovate pin bump merge in the adopter's repo starts the proposer, (b) platform fires repository_dispatch at each adopter on a feed change, (c) workflow_dispatch only, human-started.
- Options: (a) Renovate pin-bump merge as trigger / (b) repository_dispatch / (c) manual dispatch only
- Recommended then: (a) plus workflow_dispatch — the pin bump merge is already the adopter's notice a parent changed and is a reviewed PR under ADR-0002; needs no new mechanism or cross-org credential, unlike (b).
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/05-the-proposer.md

## P141 [2026-08-24T1926_50fff040 2026-08-24T19:39] Where the rejection ledger lives
- Q: Each adopter now runs its own proposer. Does each adopter keep its own rejection ledger, or do they all write the shared platform/honesty/rejections.json?
- Options: Per-adopter ledger / shared platform ledger
- Recommended then: Each adopter keeps its own — a rejection is that adopter's editorial history and platform must not hold per-adopter state it can't verify; costs adopters cross-learning from each other's rejections, which nothing did anyway.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/05-the-proposer.md

## P142 [2026-08-24T1926_50fff040 2026-08-24T19:40] Whether the proposer signs its commit
- Q: wargamer.py's docstring claims every proposal carries the war-gamer's gitsign identity 'stamped at commit time', but no code ever committed until now. (a) sign with the proposer workflow's own Actions identity plus a second identity regexp, or (b) leave the proposal commit unsigned.
- Options: (a) sign with new Actions identity / (b) leave unsigned
- Recommended then: (b) — a proposal is not an artefact; it becomes one when a human merges and cut-release.yml cuts a signed tag against the existing regexp. Correct the overclaiming docstring in the same change.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/05-the-proposer.md

## P143 [2026-08-24T1926_50fff040 2026-08-24T19:40] What the proposer does with a proposed Deny
- Q: select_tier can return 'deny', but the cage-tier MutatingPolicy coerces any unknown label value to 'baseline' — so a merged tier:deny PR would silently make the workload the loosest it can be. (a) write the tightest real tier, quarantine, and say 'the price says deny' in the PR body, (b) refuse to open a tier PR for a Deny and open an issue instead, (c) write deny anyway and have the estate fix the coercion first.
- Options: (a) write quarantine + note the real verdict / (b) open an issue instead of a tier PR / (c) write deny and require a platform fix first
- Recommended then: (b) — Deny is not a tier change; a tier PR is the wrong instrument since reaching deny means the workload shouldn't admit at all, a ValidatingPolicy decision in a different repo. Record the coercion as the map's sixth named gap. (a) understates the price in what the engine reads; (c) makes the ticket wait on an out-of-scope platform fix.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/05-the-proposer.md

## P144 [2026-08-25T0802_a3f815d3 2026-08-25T08:09] Mutate path: legal route for an adopter wanting a stricter cage, given a mutate/generate carries no action to tighten
- Q: Finding 1: a subclass cannot tighten a mutate or a generate, because they carry no action. What is the legal path for an adopter that wants a stricter cage?
- Options: Only the proposer (Recommended) — overlay restatement stays ValidatingPolicy-only; a cage change is a tier label set upstream via ticket 05's proposer as a reviewed PR | Overlay may set a tier — faster but puts a verdict-moving value in the overlay | Refuse the case entirely — strictest, leaves the adopter no route
- Recommended then: Only the proposer: keep restatement ValidatingPolicy-only; a stricter cage goes through ADR-0015's proposer as a reviewed PR.
- Reply: `[Not present as a USER text turn in this digest — the AskUserQuestion tool result is not rendered as visible user text. ` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/06-*.md (ticket 06); docs/adr/0016-a-subclass-never-restates-a-mutate.md; CONTEXT.md; map Decisions-so-far entry

## P145 [2026-08-25T0802_a3f815d3 2026-08-25T08:09] Ordering: whose problem is undeclared mutate-before-validate ordering between composed members
- Q: Finding 3: composition renders flat per version, so it does not state that stamp-posture must run before posture-trust-boundary, or cage-tier before cage-netpol. Whose problem is that?
- Options: Platform machinery, out of scope (Recommended) — Kyverno's webhook ordering guarantees mutate-before-validate; record as a named residual risk, rule out of scope | Composition must declare it — composed artefact records intra-set dependencies, adds a second ordering axis | Fog, not yet sharp — write into Not yet specified for a later ticket
- Recommended then: Platform machinery, out of scope: rely on Kyverno's webhook ordering guarantee and record the residual risk.
- Reply: `[Not present as a USER text turn in this digest — same AskUserQuestion call as the Mutate-path decision, answer not rend` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/06-*.md (ticket 06); map Out-of-scope entry

## P146 [2026-08-25T0816_2a8c3f0a 2026-08-25T08:19] What may fill an adopter-added control
- Q: Q1 - What may fill an adopter-added control?
- Options: (a) Only an implementations parent — adopter waits for platform to ship a rule, control stays a hole until then. (b) The adopter's own implementation, carried in its overlay — coverage reads a per-party mapping, not just the parent's. (c) Nothing ever — an added control is a permanent hole, caged and priced.
- Recommended then: (b) — the domain already allows it: roles compose, and platform both adopts nist and publishes implementations. (a) makes the adopter ask a favour of its parent (an exemption request in a new coat); (c) prices a gap the adopter could close, which is dishonest.
- Reply: `` (deferred, accepted=False)
- Recorded in: .scratch/policy-composition/issues/07-adopter-added-controls.md

## P147 [2026-08-25T0816_2a8c3f0a 2026-08-25T08:19] Whether an adopter-added hole refuses like an inherited one
- Q: Q2 - Does an adopter-added hole refuse like an inherited one?
- Options: (a) Treats it identically to any new hole and refuses. (b) Records it instead of refusing, because the adopter chose it knowingly.
- Recommended then: (a), no difference — ADR-0013 already refuses a MODERATE to HIGH widening (83 controls at once); an added control is the same act at size one. Deliberate intent buys no discount; the refusal clears in a reviewed PR, the estate's only override shape.
- Reply: `` (deferred, accepted=False)
- Recorded in: .scratch/policy-composition/issues/07-adopter-added-controls.md

## P148 [2026-08-25T0816_2a8c3f0a 2026-08-25T08:19] Where the adopter declares the added control
- Q: Q3 - Where does the adopter declare the added control?
- Options: (a) A plain list in the signed party artefact, next to the selected baseline name (the prototype's dead 'requires' field is this shape). (b) An adopter-authored OSCAL profile that imports the regulator's named baseline and adds controls (the native OSCAL move).
- Recommended then: (a), the list in the party artefact — ADR-0013 already put the selection there; one file then answers 'what applies to me'. (b) makes the adopter an author of profiles, blurring the split ADR-0013 just drew.
- Reply: `` (deferred, accepted=False)
- Recorded in: .scratch/policy-composition/issues/07-adopter-added-controls.md

## P149 [2026-08-25T0816_2a8c3f0a 2026-08-25T08:19] Which control ids an adopter may add
- Q: Q4 - Which control ids may an adopter add?
- Options: (a) Only ids that resolve in a catalogue the adopter already inherits. (b) Also an id the adopter invents for a rule of its own.
- Recommended then: (a) — ADR-0013 makes an id absent from the catalogue a hard failure. A company-specific rule is a policy, not a control; it composes through the overlay and needs no catalogue id.
- Reply: `` (deferred, accepted=False)
- Recorded in: .scratch/policy-composition/issues/07-adopter-added-controls.md

## P150 [2026-08-25T0831_85a1d089 2026-08-25T08:32] What may fill an adopter-added control
- Q: Three candidates for what fills a control an adopter adds itself.
- Options: (a) an inherited publisher's implementation, when that publisher's component-definition already claims the control; (b) the adopter's own implementation, shipped as an overlay member with the adopter's own OSCAL claim; (c) a third publisher the adopter pins as a new implementations parent
- Recommended then: All three, with one rule: a control is filled by a signed OSCAL claim from whoever ships the implementation. The composition does not care which party; compose.py already does this for parents and only needs to also read the adopter's claim.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/07-adopter-added-controls.md

## P151 [2026-08-25T0831_85a1d089 2026-08-25T08:32] Adopter-added hole under the new-hole rule
- Q: Does an adopter-added hole (created in the same commit that adds the control) get special treatment under ticket 03's new-hole rule, since it compares against the last signed composed artefact and would otherwise just look like a new refusal?
- Options: special-case an intentional adopter-added hole with an override flag, or apply the existing new-hole refusal rule with no exception
- Recommended then: No special case. It refuses, exactly as ticket 03 edge 2 already specifies at size one. The adopter clears it by supplying the implementation in the same reviewed PR or accepting the hole onto the recorded list in that PR. An 'I added it on purpose' override flag is forbidden by the map.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/07-adopter-added-controls.md

## P152 [2026-08-25T0831_85a1d089 2026-08-25T08:32] Whether shipping an implementation makes the adopter an implementations publisher
- Q: Does shipping an implementation make the adopter an implementations publisher, with the versioning and signing obligations that role carries?
- Options: not enumerated as discrete alternatives; yes/no framing with a proposed answer
- Recommended then: It adds no obligation the adopter does not already carry. ADR-0012 already makes the adopter sign its composed artefact with the same gitsign tag; the adopter's own policy is an overlay member versioned with it, gains no separate semver axis or pin. The adopter becomes an implementations publisher only when another party pins its composed artefact as a parent — a fact about the pinner, not a new role to declare.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/07-adopter-added-controls.md

## P153 [2026-08-25T0831_85a1d089 2026-08-25T08:32] Adopter claiming a control against an inherited (parent) policy
- Q: May the adopter claim a control against an inherited policy, e.g. asserting platform's cage-netpol also evidences sc-7 when platform never said so?
- Options: not enumerated as discrete alternatives; yes/no framing with a proposed answer
- Recommended then: No. A claim belongs to whoever ships the implementation; a claim on another party's artefact is unsigned by the owning party and breaks the moment that party changes the policy. The adopter must ask platform to claim it upstream, or ship its own member.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/07-adopter-added-controls.md

## P154 [2026-08-25T0831_85a1d089 2026-08-25T08:32] Adopter withdrawing a control it added itself
- Q: May the adopter later remove a control it added itself, given ADR-0013 says an adopter never removes a control (written for inherited controls)?
- Options: allow removal of self-added controls as an exception, or apply the no-removal rule uniformly
- Recommended then: No, same rule. Adding was a claim; withdrawing the claim is an exemption by another name. The control stays, the hole is recorded, and the cage prices it.
- Reply: `agree` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/07-adopter-added-controls.md

## P155 [2026-08-25T0851_e7ce8c96 2026-08-25T08:53] Declared or derived: where the governed-namespace set is recorded
- Q: Should the governed namespace set be declared via a label on the adopter's own signed Namespace manifest, restated as a list inside the composed artefact, or derived from the live cluster?
- Options: (a) governed:"true" label on the Namespace manifest is the declaration and the composed artefact carries no namespace list; (b) the composed artefact lists namespaces and the label is rendered from it; (c) derive from the cluster
- Recommended then: (a) — the declaration is already signed in the adopter's repo; the composed artefact only carries it as advisory metadata, the same way it records parent SHAs, so a verifier can re-derive it from the adopter's own manifests.
- Reply: `accept` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/08-*.md; docs/adr/0018-the-namespace-manifest-is-the-governed-declaration.md; CONTEXT.md; .scratch/policy-composition/map.md

## P156 [2026-08-25T0851_e7ce8c96 2026-08-25T08:53] Where the risk-bearing act lands: party artefact vs. Kubernetes manifest
- Q: Given Q1's answer (a), the namespace set lives in a Kubernetes manifest rather than the party artefact where ticket 03 put the baseline name. Is that split acceptable, or must the party artefact also name each governed namespace so the two risk-bearing selections sit together?
- Options: Accept the split (manifest is authoritative, party artefact does not restate it) vs. require the party artefact to name each governed namespace
- Recommended then: Accept the split. The manifest is what the cluster reads and is in the same signed tag; mirroring it in the party artefact would be duplicated state again.
- Reply: `accept` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/08-*.md; docs/adr/0018-the-namespace-manifest-is-the-governed-declaration.md; CONTEXT.md; .scratch/policy-composition/map.md

## P157 [2026-08-25T0851_e7ce8c96 2026-08-25T08:53] What refuses at composition time for namespace declarations
- Q: What should cause a composition-time refusal: an adopter namespace with the institution label but no governed:"true" label, a composed artefact naming a namespace with no manifest, both, or neither (treating label drift as ordinary Flux drift)?
- Options: (a) a namespace with institution but not governed refuses (ADR-0014's 'hole moved up'); (b) a composed artefact naming a namespace with no manifest refuses; (c) both; (d) neither — label drift is Flux drift already owned by drift tooling
- Recommended then: (a) at merge time, using the same new-versus-recorded rule as ticket 03, so a brownfield estate records an existing ungoverned namespace but refuses a new one; (b) has nothing to refuse if Q1 is (a); out-of-band cluster drift is (d) and unobservable at merge time.
- Reply: `accept` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/08-*.md; docs/adr/0018-the-namespace-manifest-is-the-governed-declaration.md; CONTEXT.md; .scratch/policy-composition/map.md

## P158 [2026-08-25T0851_e7ce8c96 2026-08-25T08:53] Who may add a governed namespace, and by what rail
- Q: Adding a governed namespace is the adopter's PR to its own repo, human-merged. May the proposer (automated) ever propose one?
- Options: Only the adopter, by hand vs. the proposer may also propose a new namespace
- Recommended then: Only the adopter, by hand. The proposer edits one label on one workload; a new namespace is a scope change, not a priced verdict, and ADR-0015 gives the proposer nothing to price it with.
- Reply: `accept` (bare_agree, accepted=True)
- Recorded in: .scratch/policy-composition/issues/08-*.md; docs/adr/0018-the-namespace-manifest-is-the-governed-declaration.md; CONTEXT.md; .scratch/policy-composition/map.md

## P159 [2026-08-25T0923_9622c563 2026-08-25T09:27] Testing seam for policy-composition spec
- Q: The to-spec skill instructs checking the seam matches user expectations before publishing. Assistant chose a single seam and asked whether to keep it as one seam or split it.
- Options: Keep the single seam as chosen; or split into multiple seams (e.g. composition vs pricing)
- Recommended then: Keep the one-seam design; assistant proceeded without waiting, noting "I proceeded without asking, because you are not watching."
- Reply: `` (deferred, accepted=False)
- Recorded in: .scratch/policy-composition/spec.md

## P160 [2026-08-25T0923_9622c563 2026-08-25T09:27] Reminder to confirm the one-seam choice before cutting tickets
- Q: "Confirm the one-seam choice before /to-tickets. A seam change after tickets are cut means editing every ticket."
- Options: Confirm one seam is correct, or request a split before tickets are cut
- Recommended then: Confirm now, before ticket-cutting locks the seam in
- Reply: `` (deferred, accepted=False)
- Recorded in: .scratch/policy-composition/spec.md

## P161 [2026-08-25T0923_9622c563 2026-08-25T09:30] Ticket 12 granularity
- Q: "Ticket 12 is the largest. It holds the seam, the loader rewrite and the render. Split it if it does not fit one context window."
- Options: Keep ticket 12 as one combined ticket, or split it
- Recommended then: No explicit recommendation; framed as user's call
- Reply: `` (deferred, accepted=False)
- Recorded in: .scratch/policy-composition/issues/12-*.md

## P162 [2026-08-25T0923_9622c563 2026-08-25T09:30] Ticket 17 scope (proposer's tier-PR step)
- Q: "The map calls gap fixes platform's job, but ADR-0015 is a decision and not a gap. I kept it in. Drop it if you want the proposer built elsewhere."
- Options: Keep ticket 17 here, or drop it (build proposer in platform repo)
- Recommended then: Keep it in, as the assistant already did
- Reply: `` (deferred, accepted=False)
- Recorded in: .scratch/policy-composition/issues/17-*.md

## P163 [2026-08-25T0934_3c3e8238 2026-08-25T13:05] What to do next given tickets 09 and 17 were mismarked resolved
- Q: Tell me which of these you want next: fix the ticket 17 bug and get it to a real clean review, push the WIP branches so you can look at them on GitHub, open draft PRs for review, or stop here.
- Options: fix ticket 17 bug to clean review / push WIP branches to GitHub / open draft PRs / stop here
- Recommended then: No single option pushed — presented as an open menu of four.
- Reply: `fix all the things` (bare_agree, accepted=False)
- Recorded in: .scratch/policy-composition/issues/ (tickets 09, 17)

## P164 [2026-08-25T0934_3c3e8238 2026-08-25T13:16] Whether the now-fixed work on the five WIP branches should go into the five external repos at all, and how
- Q: That decision — whether any of this goes to those five repos — is still yours. (implicit: push/PR now, or continue holding it locally)
- Options: push/open PR to the five real repos now; keep holding on local branches only
- Recommended then: None given — explicitly deferred entirely to the user.
- Reply: `goes in all the repos its supposed to go in you fuck` (bare_agree, accepted=False)
- Recorded in: 

## P165 [dc4083c1_2026-07-15 2026-07-15T10:35] Rebuild the two patch tags (v1.0.2/v2.0.2 -> v1.0.3/v2.0.3) with unsigned underlying git commits to fix a Flux go-git resolution bug, while keeping the tag itself gitsign-signed
- Q: Root cause found: v1.0.2/v2.0.2's underlying commits were SSH-signed (shell default), and Flux's go-git library chokes on SSH-format commit signatures during shallow-fetch-by-tag (plain git handles it fine). Fix: cut v1.0.3/v2.0.3 with identical content but an unsigned underlying commit — tag still fully gitsign-signed via real OAuth. Auto-mode flagged this twice as resembling the fake-signing workaround the user had banned earlier; assistant wanted explicit go-ahead since it was blocked twice.
- Options: A) Yes, cut v1.0.3/v2.0.3 this way (Recommended) — unsigned commit avoids the go-git bug, tag still real and gitsign-signed via OAuth. B) No — let's find a different fix (don't touch commit signing; investigate go-git further or another workaround).
- Recommended then: A) Yes, cut v1.0.3/v2.0.3 this way
- Reply: `[not captured as free text — AskUserQuestion selection; assistant's next turn 'Explicit go-ahead received. Proceeding.' ` (bare_agree, accepted=True)
- Recorded in: 

## P166 [dc4083c1_2026-07-15 2026-07-15T12:35] Grant Kyverno a read-only ClusterRole to see Crossplane CRDs (S3, RDS resource types) so the two new cloud ValidatingPolicies can leave NotReady
- Q: The two new cloud ValidatingPolicies (S3, RDS) were created but stuck NotReady: Kyverno's background/reports controllers had zero RBAC access to the Crossplane CRDs (a documented Kyverno gap, not a bug in the policies — the earlier spike hit and solved the identical issue). Fix is a read-only (get/list/watch) ClusterRole scoped to exactly the 2 Crossplane resource types this project targets. Auto-mode wanted explicit sign-off since it's an RBAC grant.
- Options: A) Yes, add the read-only ClusterRole (Recommended) — get/list/watch only, scoped to exactly s3.aws.m.upbound.io/bucketserversideencryptionconfigurations and rds.aws.m.upbound.io/instances, no write access, no other resource types. B) No — leave cloud policies NotReady for now (skip; policies stay created but non-functional until reviewed separately).
- Recommended then: A) Yes, add the read-only ClusterRole
- Reply: `[not captured as free text — AskUserQuestion selection; assistant's next turn 'Now applying it live directly to unblock ` (bare_agree, accepted=True)
- Recorded in: 

## P167 [dc4083c1_2026-07-15 2026-07-15T13:19] How to handle ticket 21 (CIO dashboard) — build a real, continuously-running CronJob (new infrastructure) or skip it and go to the final demo
- Q: Every ticket except 21 (CIO dashboard) and 27 (final demo) was done and live-verified. Ticket 21's last panel (OSCAL assessment-results) needs a real, continuously-running job against the live fleet publishing somewhere Grafana can query — today's OSCAL evidence only exists from a throwaway spike run. That means building and running a real container image (a C2P CronJob), which is new infrastructure, not a bug fix. Asked how to handle it.
- Options: A) Build the real CronJob (Recommended) — design and build a Flux-native CronJob that runs C2P against the live fleet's PolicyReports and publishes OSCAL for Grafana's infinity datasource, likely via a ConfigMap, no bespoke exporter; new infra, needs a container image and probably another PR cycle. B) Skip 21 for now, go straight to the final demo — leave ticket 21 open/deferred, move to ticket 27 covering everything that IS done.
- Recommended then: A) Build the real CronJob
- Reply: `[not captured as free text — AskUserQuestion selection; assistant's next turn 'Building this in stages: first the C2P Cr` (bare_agree, accepted=True)
- Recorded in: 

## P168 [dc4083c1_2026-07-16 2026-07-16T09:17] Grilling: history rewrite (item 4)
- Q: User wanted thrashing bug-fix commits gone; assistant recommended against any rewrite -- messy history is evidence, rewriting breaks dashboard/tracker references, curated HISTORY.md serves the real need instead.
- Options: Keep history + HISTORY.md (Recommended) / Rewrite fleet only / Park it
- Recommended then: Keep history + HISTORY.md, no rewrite.
- Reply: `[Not captured verbatim; recap at 11:06:34 records '(1) history -- no rewrite, endgame is a fresh-org redeploy' matching ` (bare_agree, accepted=True)
- Recorded in: real-estate/issues/15, real-estate/spec.md

## P169 [dc4083c1_2026-07-16 2026-07-16T10:37] Grilling: app roster (item 1, part 2)
- Q: Proposed five-app roster spanning ecosystems/staleness/policy-version/both planes, including a genuinely vulnerable live log4j 2.14 app. Good roster?
- Options: Yes, all five as proposed (Recommended) / Yes but no live log4j / Different roster
- Recommended then: Yes, all five, including running log4j live.
- Reply: `[Not captured verbatim; recap matches roster exactly, and ledger later runs genuinely vulnerable log4j-core 2.14.1.]` (bare_agree, accepted=True)
- Recorded in: real-estate/issues/07, real-estate/issues/08

## P170 [dc4083c1_2026-07-16 2026-07-16T10:41] Grilling: sunset vs ADR-0006 (item 12)
- Q: Reconcile sunset with ADR-0006: scheduled proposals, never scheduled application -- sunset field, escalating issues, machine-opened retirement PR, human merge required, new ADR first.
- Options: Accept: scheduled proposals (Recommended) / Softer: countdown only / Harder: true expiry
- Recommended then: Accept scheduled proposals.
- Reply: `[Not captured verbatim; recap records '(4) sunset -- scheduled proposals never scheduled application' matching exactly, ` (bare_agree, accepted=True)
- Recorded in: real-estate/issues/02, real-estate/issues/09

## P171 [dc4083c1_2026-07-16 2026-07-16T11:00] Grilling: estate staleness dashboard placement (item 14)
- Q: New second dashboard for estate staleness rather than extending the existing CIO dashboard, keeping each one-question-shaped. Agree?
- Options: New dashboard (Recommended) / Extend existing
- Recommended then: New, separate dashboard.
- Reply: `[Not captured verbatim; recap and ticket 12 confirm a new dashboard was built.]` (bare_agree, accepted=True)
- Recorded in: real-estate/issues/12

## P172 [dc4083c1_2026-07-18 2026-07-18T09:15] Add unattended sunset-escalator.yml CI workflow to fleet repo
- Q: Create the sunset-escalator.yml GitHub Actions workflow in the fleet repo (daily cron, contents:write + pull-requests:write + issues:write, no new secrets)?
- Options: Yes, create it (Recommended) — closes the gap where ticket 09's retirement PR never actually fires unattended / No, leave it documented only — honestly document that a human must manually run the script on the date
- Recommended then: Yes, create the workflow, using only the default GITHUB_TOKEN scoped to fleet's own repo.
- Reply: `[AskUserQuestion tool response not rendered as chat text in this digest — the assistant's next turn (09:35:12Z, 'Confirm` (bare_agree, accepted=True)
- Recorded in: .scratch/real-estate/issues/09 (sunset ticket), shipped as fleet PR #58

## P173 [dc4083c1_2026-07-18 2026-07-18T10:40] Whether to expand the adversarial verification marathon beyond the 16-ticket real-estate epic
- Q: Should the adversarial verification marathon expand to cover faithful-floor's 26 tickets too (42 total), or stay scoped to real-estate's 16?
- Options: Expand to all 42 (Recommended) — matches the goal's literal 'all tickets' wording, run verify+skeptic against faithful-floor too / Keep it scoped to real-estate's 16 — faithful-floor is a separate earlier epic not what the goal was about
- Recommended then: Expand to all 42 tickets.
- Reply: `[Not rendered as chat text in this digest — the assistant's next turn (10:40:35Z, 'Expanding the marathon to all 42 tick` (bare_agree, accepted=True)
- Recorded in: session /goal scope (no single ticket file); preceded by the user's own questions at 10:38:51Z and 10:39:51Z that surfaced the scoping gap

## P174 [dc4083c1_2026-07-18 2026-07-18T11:10] Widen orphan-guard's Deny-mode admission gate to cover Crossplane CRD types
- Q: Extend orphan-guard's Deny-mode admission gate to also cover the two Crossplane CRD types (S3 encryption config, RDS instance), closing a real gap where unlabeled cloud resources currently bypass all enforcement?
- Options: Yes, extend it (Recommended) — matches the guard's own documented design intent ('locked door, not opt-in door') / No, just document the gap — leave orphan-guard Pods-only and document as a known limitation instead
- Recommended then: Yes, extend the guard's scope.
- Reply: `[Not rendered as chat text — the assistant's next turn (11:13:18Z, 'Confirmed — continuing the fix.') indicates the reco` (bare_agree, accepted=True)
- Recorded in: .scratch/faithful-floor/issues/19-cloud-plane-at-admission.md, shipped as fleet PR #61

## P175 [dc4083c1_2026-07-20 2026-07-20T15:54] Enable org/repo GitHub Actions setting to let Actions open PRs, closing ticket 09's automation gap
- Q: The sunset-escalator's retirement-PR path works end-to-end except for one repo setting: 'Allow GitHub Actions to create and approve pull requests' is OFF on the fleet repo, so gh pr create 403s. Enable it so the 2026-08-15 retirement PR fires fully unattended?
- Options: Enable it on fleet (Recommended) -- run gh api to set can_approve_pull_request_reviews=true on fleet only, closes the gap, mildly loosens posture (any fleet workflow could open PRs). | Leave it off, document as manual step -- keep as-is, document in ticket 09 that opening the retirement PR needs a one-time toggle or PAT secret.
- Recommended then: Enable it on fleet (labeled 'Recommended' in the AskUserQuestion option).
- Reply: `[reply not captured as a USER turn in this session digest; the next ASSISTANT turn at 2026-07-20T16:03:26.833Z opens wit` (bare_agree, accepted=True)
- Recorded in: ticket 09 (sunset-escalator retirement-PR path)

## P176 [dc4083c1_2026-07-23 2026-07-23T15:16] Wayfinding destination (first AskUserQuestion, interrupted)
- Q: What's the destination of this wayfinding effort - what does 'done' look like?
- Options: Decide + spec the hourglass (plan only) / Just enrich the talk (framing+diagram only) / Build a thin slice now (implement one vertical slice live)
- Recommended then: Decide + spec the hourglass - produce a spec to build from later, not built this session (wayfinder default).
- Reply: `[Request interrupted by user]` (deferred, accepted=False)
- Recorded in: 

## P177 [dc4083c1_2026-07-23 2026-07-23T18:56] Fold actuarial/insurance practices into the model
- Q: Two moves: 1) fold risk-transfer (avoid/reduce/transfer/retain) + TVaR/loading into the model (recommended), and/or 2) spawn a research ticket on deeper actuarial methods; should that research also pin cyber-policy structure (limits, retentions, exclusions)?
- Options: Fold-in only (recommended) / fold-in and spawn research ticket / fold-in and research also covers policy structure
- Recommended then: Fold-in - it's the completing piece and not much build; consider also spawning the deeper research ticket.
- Reply: `Fold in` (bare_agree, accepted=True)
- Recorded in: Risk model / balance-sheet / war-gamer tickets

## P178 [dc4083c1_2026-07-23 2026-07-23T19:22] Closing grill Q3 - appetite framing / proportionality ordering (ticket 04)
- Q: Q3 - Is caldera strictest (Deny-heavy), driftwood loosest (Audit-heavy), tuppence in between-toward-strict the right shape? Or should a different institution be the strict one?
- Options: caldera strictest / driftwood loosest / tuppence toward-strict (recommended) / different institution as strictest
- Recommended then: caldera strictest, driftwood loosest, tuppence toward-strict, driven by HIPAA long-lived confidentiality vs short-lived cart data.
- Reply: `Yes` (bare_letter, accepted=True)
- Recorded in: Risk model ticket (04)

## P179 [dc4083c1_2026-07-31 2026-07-31T08:56] Test seams for the spec (/to-spec)
- Q: Do the proposed four test seams (fair.py CLI, Kyverno test fixtures, verify-*.sh scripts, war-gamer feed->PR seam) match how you'd want this tested?
- Options: Approve the 4 seams as proposed, or request changes
- Recommended then: Approve as-is; assistant argued these are the fewest possible seams (one per subsystem) and seam 1 (fair.py CLI) is load-bearing
- Reply: `should we do python would a rust binary be more fashionable?` (deferred, accepted=True)
- Recorded in: .scratch/talk-spec/spec.md

## P180 [dc4083c1_2026-07-31 2026-07-31T09:40] Runtime identity carrier for posture-as-identity
- Q: Carry posture on SPIFFE/SPIRE SVID, a lighter projected ServiceAccount-token claim, or Istio's built-in mTLS identity without SPIRE?
- Options: SPIFFE/SPIRE (attestation-native) / projected SA-token (lighter, weaker) / Istio-mTLS-only (middle ground)
- Recommended then: SPIFFE/SPIRE
- Reply: `SPIFFE/SPIRE` (bare_letter, accepted=True)
- Recorded in: .scratch/talk-spec/issues/16-enforcement-response-gradient.md

## P181 [dc4083c1_2026-08-04 2026-08-04T12:49] Wayfinder map destination
- Q: What is the destination for the re-scoped effort: (a) the rigorous real system, talk as byproduct; (b) the talk, bar raised; (c) the methodology/skills as the deliverable?
- Options: (a) rigorous real system; (b) talk, bar raised; (c) methodology itself
- Recommended then: (a) The rigorous real system — talk becomes a byproduct, attacks the root cause of the prior demo-first shortcuts.
- Reply: `a` (bare_letter, accepted=True)
- Recorded in: .scratch/twin/map.md

## P182 [dc4083c1_2026-08-04 2026-08-04T14:05] Flagship as real-history-spine + synthetic-substrate hybrid
- Q: Accept the flagship as a real org's real documented history (backtest ground truth) wearing a synthetic behavioural substrate, or keep the flagship fully fictitious and run the history-backtest against a separate real org?
- Options: hybrid (real spine + synthetic substrate); fully fictitious flagship + separate real backtest proxy
- Recommended then: The hybrid — backtest is only as honest as the history is real, running it against the actual subject is stronger than a proxy.
- Reply: `yes
i agree with your recomendation` (bare_agree, accepted=True)
- Recorded in: .scratch/twin/issues/01-subject-and-purpose.md

## P183 [dc4083c1_2026-08-04 2026-08-04T14:42] AskUserQuestion — flagship-selection direction after wave-1 contrarian challenge
- Q: How to proceed toward committing the flagship after Fable's contrarian exposed a criteria flaw: (1) run a targeted second wave sampling the collapsed-firm-with-answer-key class and re-score; (2) commit now to living flagship (Ferrari) + Carillion added as dedicated backtest; (3) make a collapsed firm (Carillion) the flagship itself; (4) accept the Opus pick (LEGO) as-is with caveats.
- Options: (1) Second wave first; (2) Living flagship + collapsed backtest org; (3) Bold: collapsed firm as flagship; (4) Accept Opus pick as-is
- Recommended then: No explicit single recommendation stated before the ask; assistant endorsed option (1) after the fact as 'the right call'.
- Reply: `[AskUserQuestion tool selection — verbatim user text not captured in digest; assistant's next turn confirms 'Second wave` (bare_letter, accepted=True)
- Recorded in: .scratch/twin/issues/06-flagship-osint-scoping.md

## P184 [dc4083c1_2026-08-04 2026-08-04T20:33] Ticket 07 Q2 — is there a privileged 'actual' world map
- Q: (a) A privileged consensus world-map; (b) no privileged map, only a distribution of weighted models; or (c) a hybrid — the twin's own 'best current estimate' map, explicitly just its own scored belief?
- Options: (a) privileged consensus map; (b) pure distribution, no truth; (c) twin's own belief as scored default reference
- Recommended then: (c) — tractable like (a) without (a)'s epistemic dishonesty; makes the twin's own model a scored participant.
- Reply: `C` (bare_letter, accepted=True)
- Recorded in: .scratch/twin/issues/07-twin-domain-model.md

## P185 [dc4083c1_2026-08-04 2026-08-04T20:41] Ticket 07 Q3 — causal vs structural-only edges
- Q: (a) Structural edges only; (b) a distinct causal/influence edge type layered on the structural graph, with evidence backing each claim; or (c) a full causal DAG/SCM as the primary model?
- Options: (a) structural only; (b) typed causal layer with evidence; (c) full SCM
- Recommended then: (b) — avoids correlational cosplay of (a) without the full-SCM data/assumption burden of (c).
- Reply: `B` (bare_letter, accepted=True)
- Recorded in: .scratch/twin/issues/07-twin-domain-model.md

## P186 [dc4083c1_2026-08-04 2026-08-04T20:47] Ticket 07 Q4 — source of truth: git vs graph database
- Q: (a) Git-versioned text is the source of truth; (b) a graph database is the source of truth; or (c) a hybrid split by data kind?
- Options: (a) git-native; (b) graph DB primary; (c) split by kind
- Recommended then: (a) as the rule with (c) as a pragmatic exception for bulk observational data.
- Reply: `A` (bare_letter, accepted=True)
- Recorded in: .scratch/twin/issues/07-twin-domain-model.md

## P187 [dc4083c1_2026-08-04 2026-08-04T20:52] Ticket 07 Q5 — where risk/£ attaches
- Q: (a) Node attributes; (b) first-class versioned scenario objects that reference graph nodes; or (c) both, with roll-ups denormalised onto nodes?
- Options: (a) node attributes; (b) scenario objects; (c) both with roll-ups
- Recommended then: (b) with (c)'s roll-ups as a derived view only.
- Reply: `Agree b with roll ups` (bare_agree, accepted=True)
- Recorded in: .scratch/twin/issues/07-twin-domain-model.md

## P188 [dc4083c1_2026-08-04 2026-08-04T20:56] Ticket 07 Q6 — how people attach and where the ethics gate lives in the schema
- Q: (a) Individuals as first-class nodes with behavioural attributes on the person node; (b) roles only, no individuals; or (c) individuals as nodes but sensitivity-split, special-category attributes not representable at all?
- Options: (a) full individual nodes; (b) roles only; (c) sensitivity-split schema
- Recommended then: (c) — keeps both committed capabilities while making Art. 9 compliance structural rather than procedural.
- Reply: `C` (bare_letter, accepted=True)
- Recorded in: .scratch/twin/issues/07-twin-domain-model.md

## P189 [dc4083c1_2026-08-04 2026-08-04T21:06] Ticket 08 Q1 — what a causal edge asserts
- Q: (a) Qualitative direction+strength; (b) semi-quantitative sign+lag+elasticity as a calibrated PERT-style range; or (c) full functional forms per edge?
- Options: (a) qualitative; (b) calibrated range; (c) full functional forms
- Recommended then: (b), with (a) a legal degraded state and (c) reachable per-edge.
- Reply: `B` (bare_letter, accepted=True)
- Recorded in: .scratch/twin/issues/08-causal-layer.md

## P190 [dc4083c1_2026-08-04 2026-08-04T21:10] Ticket 08 Q2 — grading evidence behind a causal claim
- Q: (a) A single confidence scalar; (b) a typed evidence ladder (GRADE-style) with use-gating by grade; or (c) full Bayesian priors updated per edge?
- Options: (a) confidence scalar; (b) typed evidence ladder + use-gating; (c) full Bayesian
- Recommended then: (b) — separates 'how we know' from 'how sure'; only grades 1-2 may carry a scored £ delta.
- Reply: `Agree` (bare_agree, accepted=True)
- Recorded in: .scratch/twin/issues/08-causal-layer.md

## P191 [dc4083c1_2026-08-04 2026-08-04T21:12] Ticket 08 Q3 — how interventions propagate on structural-only paths
- Q: (a) Causal edges only; (b) structural edges get a default weak causal interpretation; or (c) two distinct outputs — priced causal £ delta on causal paths, unpriced flagged blast-radius on structural-only paths?
- Options: (a) causal-only; (b) structural-as-weakly-causal; (c) two separate outputs
- Recommended then: (c) — keeps both capabilities and makes the priced/unpriced boundary visible.
- Reply: `C` (bare_letter, accepted=True)
- Recorded in: .scratch/twin/issues/08-causal-layer.md

## P192 [dc4083c1_2026-08-04 2026-08-04T21:35] Ticket 09 Q1 — whose £ is the currency denominated in
- Q: (a) The firm's £, explicitly; (b) multi-stakeholder books, each separate, no single 'cheapest' answer; or (c) the firm's £ as primary ledger with named stakeholder impacts carried alongside as non-nettable entries?
- Options: (a) firm's £ only; (b) multi-stakeholder books, no single answer; (c) firm's ledger primary + non-nettable stakeholder entries
- Recommended then: (c) — keeps the engine decidable while making externalised costs impossible to hide.
- Reply: `` (deferred, accepted=False)
- Recorded in: .scratch/twin/issues/09-currency-regimes.md

## P193 [dc4083c1_2026-08-05 2026-08-05T06:29] Ticket 09 Q3 - what does the engine optimise within allowed options
- Q: Within the allowed options, what does the engine actually optimise, or does it refuse to pick?
- Options: (a) minimise total cost of risk; (b) rank by efficiency (risk reduction per £); (c) show the trade-off curve, don't pick
- Recommended then: (c), with (a) shown as a default marker on the curve - advisory-by-design (Art. 22), don't collapse plurality into a false single answer
- Reply: `c` (bare_letter, accepted=True)
- Recorded in: .scratch/twin/issues/09-currency.md

## P194 [dc4083c1_2026-08-05 2026-08-05T06:32] Ticket 09 Q4 - what's allowed into the £ currency
- Q: What is actually allowed into the £, and what stays outside it?
- Options: (a) shadow prices for everything; (b) separate never-converted registers; (c) price only where an evidence-graded causal path to cash flow exists, else register entry
- Recommended then: (c) - the boundary is derived rather than declared, using ticket 08's use-gating rule for a third job
- Reply: `c` (bare_letter, accepted=True)
- Recorded in: .scratch/twin/issues/09-currency.md

## P195 [dc4083c1_2026-08-05 2026-08-05T07:37] Ticket 12 Q2 - who plants ground truth and prevents planter/detector collusion
- Q: Who plants the ground truth, and how do we stop the detector simply thinking like the planter?
- Options: (a) same process, time/context separated; (b) enforced adversarial split (sealed planter, blind detector, separate scorer); (c) skip planting, rely only on the real backtest
- Recommended then: (b) alongside (c) doing a different job - the synthetic substrate measures detection mechanics, the real backtest is genuinely external
- Reply: `b` (bare_letter, accepted=True)
- Recorded in: .scratch/twin/issues/12-synthetic-substrate.md

## P196 [dc4083c1_2026-08-05 2026-08-05T08:29] Ticket 11 Q4 - how movement propagates (observation vs intervention)
- Q: When an inferred position moves, how does that travel the graph - is it the same as ticket 08's intervention?
- Options: (a) same machinery as do(x); (b) distinct semantics - observation updates bidirectionally, intervention downstream-only; (c) no propagation
- Recommended then: (b) - textbook Pearl; conflating the two would quietly corrupt everything
- Reply: `b` (bare_letter, accepted=True)
- Recorded in: .scratch/twin/issues/11-sense-move-loop.md

## P197 [dc4083c1_2026-08-05 2026-08-05T08:35] Ticket 12 Q1 - what is the synthetic substrate for
- Q: What is the substrate actually for?
- Options: (a) a test harness, optimise for measurability; (b) a believable world, optimise for verisimilitude; (c) both, layered, one wins ties
- Recommended then: (c), with measurability winning ties - believability-first substrates produce low-n dramatic storylines that break calibration
- Reply: `c` (bare_letter, accepted=True)
- Recorded in: .scratch/twin/issues/12-synthetic-substrate.md

## P198 [dc4083c1_2026-08-05 2026-08-05T09:24] Ticket 14 Q1 - attest artefacts or the reasoning chain
- Q: Do we attest the artefact, or the reasoning that produced it?
- Options: (a) artefacts only; (b) materialised reasoning chains; (c) signed artefacts with reconstructable derivation from pinned inputs
- Recommended then: (c) - gets (b)'s epistemic property from (a)'s cost, works specifically because source of truth is git-versioned
- Reply: `c` (bare_letter, accepted=True)
- Recorded in: .scratch/twin/issues/14-provenance.md

## P199 [dc4083c1_2026-08-05 2026-08-05T09:32] Ticket 15 Q1 - test that admits a behavioural sensor
- Q: What test admits a behavioural sensor at all?
- Options: (a) purpose-limitation test; (b) proportionality test; (c) necessity test
- Recommended then: all three as a ladder in that order, plus 'model the mechanism universally, sense sparingly' as the reconciling move
- Reply: `agree 3 as a ladder` (bare_agree, accepted=True)
- Recorded in: .scratch/twin/issues/15-ethics-sensing.md

## P200 [dc4083c1_2026-08-05 2026-08-05T09:35] Ticket 15 Q2 - Goodhart's law, sensors are disclosed so gaming is guaranteed
- Q: Sensors are disclosed, so gaming is guaranteed - what does the twin do about it?
- Options: (a) accept and disclose; (b) prefer gaming-proof sensors, mark gameability; (c) actively watch for suspicious improvement
- Recommended then: (b) as the design rule, (c) as the backstop - prefer sensors where gaming the metric is the desired behaviour
- Reply: `b+c` (bare_letter, accepted=True)
- Recorded in: .scratch/twin/issues/15-ethics-sensing.md

## P201 [dc4083c1_2026-08-05 2026-08-05T09:39] Ticket 15 Q3 - what's missing from the misuse catalogue
- Q: What's missing from the proposed misuse catalogue table, and does the blame-attribution constraint work?
- Options: open-ended review of an 8-row table
- Recommended then: n/a (asking user to spot gaps)
- Reply: `i don't see anything missing from q3 table, ask a fable sub agent for suggestions` (deferred, accepted=True)
- Recorded in: .scratch/twin/issues/15-ethics-sensing.md

## P202 [dc4083c1_2026-08-05 2026-08-05T10:00] Ticket 18 Q1 - does the twin act or only propose
- Q: Does the twin act, or only propose?
- Options: (a) propose only; (b) graduated autonomy priced by stakes; (c) act with human veto
- Recommended then: (a), now derived (not just inherited) from Art.22, the trade-off curve having nothing to auto-execute, and agent signatures asserting origin not endorsement; carve-out: the twin acts freely on its own model
- Reply: `a` (bare_letter, accepted=True)
- Recorded in: .scratch/twin/issues/18-enactment-arm.md

## P203 [dc4083c1_2026-08-05 2026-08-05T10:00] Ticket 18 Q2 - does policy-as-versioned-dependency survive the risk basis
- Q: Does policy-as-versioned-dependency actually survive the risk basis?
- Options: (a) survives as-is; (b) survives narrowed to machine-enforceable controls plus a verification substrate for the rest; (c) rejected
- Recommended then: (b), because ticket 09 broke the broad version - most levers aren't code, so versioned policy can't be the shape of governance itself
- Reply: `b` (bare_letter, accepted=True)
- Recorded in: .scratch/twin/issues/18-enactment-arm.md

## P204 [dc4083c1_2026-08-05 2026-08-05T10:08] Ticket 15 (power layer) - fable's misuse review found the design constrains knowledge, not power
- Q: Do we add a power layer to the design, or accept the limit honestly and say so? (plus: how to handle exit-cost asymmetry, where the assistant has no good answer)
- Options: (a) add power constraints; (b) accept the limit, scope it explicitly; (c) specific fixes without a general power layer
- Recommended then: (b) as the honest framing, delivered through (c)'s mechanisms - a system can't constrain power it doesn't hold, but can refuse to be the alibi
- Reply: `b` (bare_letter, accepted=True)
- Recorded in: .scratch/twin/issues/15-ethics-sensing.md

## P205 [dc4083c1_2026-08-05 2026-08-05T17:10] Ticket 20 Q1 - what is a 'skill' as the build unit
- Q: What is a 'skill' here, actually?
- Options: (a) agent skills throughout; (b) libraries/CLIs throughout; (c) split by determinism - code on the derivation path, skills for irreducible judgement
- Recommended then: (c), forced by ticket 14's determinism-given-pins requirement; skills produce grade-5 claims that code then validates/prices/scores
- Reply: `c` (bare_letter, accepted=True)
- Recorded in: .scratch/twin/issues/20-skill-inventory.md

## P206 [dc4083c1_2026-08-05 2026-08-05T17:16] Ticket 21 Q1 - is co-registered market forecasting circular
- Q: The same markets feed the twin and score it - is that circular?
- Options: (a) accept and disclose; (b) strict separation - disjoint quarantined benchmark set; (c) temporal separation - forecast before consuming price
- Recommended then: (b) and (c) together - they defend against different failures (direct copying vs indirect inheritance)
- Reply: `b+C` (bare_letter, accepted=True)
- Recorded in: .scratch/twin/issues/21-forecast-book.md

## P207 [dc4083c1_2026-08-05 2026-08-05T17:16] Ticket 21 Q3 - is the forecast book worth building given thin coverage
- Q: Is this worth building, given it touches ~10% of scenario families and 0% of the per-org overlay?
- Options: (a) build fully; (b) build minimally as a floor, not a proof; (c) don't build it
- Recommended then: (b) - marginal cost is small since scoring harness already exists from ticket 20; it's the only mechanism that cannot be contaminated
- Reply: `b` (bare_letter, accepted=True)
- Recorded in: .scratch/twin/issues/21-forecast-book.md

## P208 [dc4083c1_2026-08-05 2026-08-05T17:47] Ticket 22 Q2 - which subjects the minimal demo slice needs
- Q: Which subject(s) does the minimal slice actually need?
- Options: (a) Netflix only; (b) Netflix + one low-contamination backtest case; (c) Netflix + a backtest case + Intel as a live forward beat
- Recommended then: (c) - Netflix cannot carry the falsifiability beat alone (too famous/contaminated); each subject does an irreplaceable job
- Reply: `c` (bare_letter, accepted=True)
- Recorded in: .scratch/twin/issues/22-demo-slice.md

## P209 [dc4083c1_2026-08-05 2026-08-05T18:22] Whether to rebuild the ticket breakdown folding in all of fable's review findings
- Q: Shall I rebuild the breakdown with all of this folded in and publish to .scratch/twin/build/? I'd apply everything above, including my 20<-16 cut, unless you want to argue any of it.
- Options: accept fable's corrections and republish / dispute specific findings
- Recommended then: accept and rebuild
- Reply: `yes` (bare_agree, accepted=True)
- Recorded in: .scratch/twin/build/00-constitution.md

## P210 [dc4083c1_2026-08-10 2026-08-10T09:28] Whether to widen ticket 65 (Flux vs continuous proof-of-force question) to a three-way question immediately, mid-measurement-window
- Q: Item 1 changes a pre-registered measurement, so I will not touch it without your word. Which do you want? (widen ticket 65 to three-way now, or open a second declared window with a written reason)
- Options: (1) widen ticket 65 to three-way now; (2) leave ticket 65 as-is and open a second declared window with a written reason
- Recommended then: Assistant recommended widening ticket 65 to a three-way question now, while the window is young, calling the alternative (a second declared window) less desirable.
- Reply: `(no direct reply to this specific ask — superseded by the next, near-identical ask after the MFOTL agent returned; user'` (deferred, accepted=False)
- Recorded in: .scratch/twin/issues/65.md

## P211 [dc4083c1_2026-08-10 2026-08-10T09:37] Final go-ahead to widen ticket 65 to three-way and make the four supporting amendments (26/64/66/27/63/69), after all research agents returned
- Q: Action 1 changes a pre-registered measurement. I will not touch it without your word. Shall I proceed with 1 [widen ticket 65 to three-way], and with 2 to 5 [shrink the spike, ticket 27 borrows plain Cedar not Dogwood, amend ticket 66 for the layered argument, record the signal in tickets 63/69]?
- Options: proceed with all five actions, or hold
- Recommended then: Assistant recommended proceeding with all five actions (widen ticket 65; shrink spike to an hour; ticket 27 borrows Cedar not Dogwood; amend ticket 66; record signal in 63/69).
- Reply: `yes` (bare_agree, accepted=True)
- Recorded in: .scratch/twin/issues/ (tickets 27, 63, 64, 65, 66, 69), committed as 1c4d20c

