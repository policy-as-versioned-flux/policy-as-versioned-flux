# The twelve questions the review must put to the owner

Ordered by how much each changes the fitness verdict. Each: why the review cannot proceed
without it; the verdict under each plausible answer; the review's own recommended answer, placed
last so it can be ignored (GAPS.md:93 rule 1).

De-duplicated from the 72 `owner_questions` raised across the eleven review dimensions; the
absorption map is at the end.

---

## Q1. What is this for, who receives it, and by when?

**Why the review cannot proceed without it.** Every dimension returned a split verdict of the
form "fit as X, not fit as Y". The analysts do not disagree about facts — they disagree about the
yardstick. Today's ask names no purpose; "fit for purpose" appears nowhere in the repository; and
the record has held no date, venue or recipient since 2026-07-23.

**Verdict under each answer.**
- (a) *A touring conference talk for principal engineers and leaders* (2026-07-23T15:08; "Agree.
  It'll tour", 19:17) → **NEARLY FIT.** You have far more than a 20-minute talk needs. The binding
  defects shrink to three: the committed deck is stale against its own run, three of seven beats
  have never fired, and the RUNBOOK tells the presenter to narrate a signed-GitHub reconcile the
  script does not perform. Most of the review's 38+ shortfalls become irrelevant.
- (b) *A reference implementation ControlPlane lifts into client work* → **NOT FIT**, and the
  cheapest blocker is legal: the hub carries no licence at all (404, verified) while every
  artefact a consumer pins is Apache-2.0. Add zero onboarding docs and three divergent adopter
  forks.
- (c) *A system a fourth organisation could actually adopt* → **NOT FIT and not close.** Nine
  orgs, 37 workflows, 84 verify scripts, no onboarding page, no stated time-to-first-cage.
- (d) *The argument itself — a written artefact proving the corrected thesis is buildable* →
  **MOSTLY FIT**; the gaps that matter shrink to the thesis's own non-negotiables (Q3, Q5).

**Recommended (the review's call).** (a) primary, (d) secondary, (b) as a downstream option that
costs one `LICENSE` file. Reason: it is the only purpose every dated instruction supports without
contradiction — the talk is the artefact you have asked for six times and the only one you have
ever rejected on quality — and it is the only purpose under which the estate is already close.

---

## Q2. Is NORTH-STAR §4 — the seven-step demonstration — your definition of done, or mine?

**Why the review cannot proceed without it.** `NORTH-STAR.md:40` says of the seven steps:
"(my proposal, derived from the twin's demo-slice sequencing and your August 19 words)". §5 (the
truth surface) and §7 carry no owner attribution at all. Your ratification is one line — "I agree
witht he northstar" (2026-08-27T16:19:55Z) — given in the same turn as a request to walk the 41
re-grills one at a time. Every ticket, the map's Destination, the 84-script denominator and every
"not fit" verdict in this review descend from §4 and §5. If §4 is mine, then "not fit for
purpose" is a statement about compliance with a yardstick you did not write.

**Verdict under each answer.**
- (a) *§4 is my definition of done* → **NOT FIT.** Three of seven steps have never run end to end
  (step 3 never once; step 5's clock has failed both firings; step 4 on one adopter of three), and
  the map's destination sentence fails on three independent counts.
- (b) *§4 is a build order I accept, not a definition of done* → **FIT AS WORK IN PROGRESS.** The
  review's job changes from grading to sequencing, and roughly twenty of the thirty-eight
  shortfalls become schedule items rather than defects.
- (c) *§4 is the wrong demonstration* → the review should stop and re-derive it before anything
  else is built.

**Recommended.** (b). Reason: your 2026-08-04 words ("the ambition and scale should be everything,
so that everything is modelled. We don't need to necessarily build everything to demo that")
describe exactly a modelled ambition with a chosen slice; your 2026-07-23 words ("no cuts will be
tolerated") describe the opposite; the two have never been reconciled and this settles them.
Sub-question folded in: does step 2 count as done when driftwood #20 raised the pin but the price
did not move?

---

## Q3. Does the thesis's "≥3 coexisting versions with a retirement window" still bind?

**Why the review cannot proceed without it.** It is the one requirement your own 2022 post calls
what the runtime *must* support (`research/03:40-42`) and the PRD synthesis calls "non-negotiable"
(`:207-208`). `distribution/versions.yaml:77` declares exactly one element (verified). Coexistence,
retirement and shift-left all SKIP from that single root cause; the gate's own bar is two; ticket
58 Q1's remedy reaches two; and the retirement *window* has no mechanism at all — the decided
replacement (ticket 13 D5: price a stale pin by the EOL ramp, adopter's proposer opens a
retirement PR) is unbuilt in both halves. The only retirement the eco-system ever performed was a
flag day. The only machine-opened, human-merged retirement PR in either org is `fleet#69`
(2026-08-15) — in the org NORTH-STAR §6 supersedes.

**Verdict under each answer.**
- (a) *Still binds* → **NOT FIT, critical**, and ticket 63's two-version remedy is insufficient.
- (b) *Superseded by cages* → the review's sharpest criticism dissolves, but the estate then has
  no promise at all to an adopter who is behind, and that hole needs its own answer.
- (c) *Binds, and the legacy org already demonstrated it* → the successor is worse than the thing
  it supersedes on the thesis's own headline claim, and the review must say so.

**Recommended.** (a), in a scoped form: three declared lines and a priced supersede, not three
fully-featured product lines. Reason: it is the one claim your 2022 talk made that no other system
makes; it is what the deck's crux beat exists for; ticket 58 Q1 already started it. Sub-question:
do the 14 legacy repos get a dated "superseded reference implementation" banner now?

---

## Q4. Is the £ a decision instrument or a balance-sheet quantity?

**Why the review cannot proceed without it.** Your words were "my underlying philisophy that i'd
like to find a way to **hint at** is that it might enable one to actually put technological risk on
the balanace sheet" and "go deep on the balance sheet, **we can always cut it out**" (both
2026-07-23T15:50, source-verified). But reversal 20 ordered a real insurance structure built, and
a second signed party now writes a layer against driftwood's signed exposure. The estate publishes
these figures with no qualifier.

**Verdict under each answer.**
- (a) *An ordinal, auditable comparison instrument — rank a control against a cage tier against a
  transfer* → **FIT.** The pound engine is the greenest surface in the estate; the 2,179% implied
  loss ratio becomes a labelling defect fixed by one sentence on the artefact.
- (b) *A quantity a CFO books and a carrier cedes against* → **NOT FIT, major.** The frequency is
  an editorial constant, the magnitudes rest on n=2 published fines, one loss table is a
  platform-held fixture about an adopter, and the insurer's quote and the adopter's exposure
  cannot both be believed.

**Recommended.** (a), stated on the artefact. Reason: your own verb was "hint at", and "we can
always cut it out" is not the language of a booked quantity. Sub-questions folded in: is
`appetite.tolerance` one economic quantity or three? Is the insurer a real second opinion whose
quote must be defensible, or an illustrative counterparty demonstrating the shape of a signed
cross-org transfer — and must an adopter cut a tag whose tree actually carries the `exposure`
section before the insurer row counts as built?

---

## Q5. "There is no gate" — your words, or my reading?

**Why the review cannot proceed without it.** `NORTH-STAR.md:31` states principle 2 and then
concedes: "That a refusal is therefore the bottom rung reached by the £, rather than a separate
mechanism, is my reading, not your words." Your own words are about cages. Your own *blog post*
names three things that belong behind a locked door — access control, data protection,
cryptographic key management (`research/03:124`). The estate ships no policy in any of the three;
encrypt-at-rest exists only in the hub's verification harness, under no tag, pinned by nobody.
Meanwhile two live `Deny` policies do ship, and CONTEXT.md, ADR-0022 and NORTH-STAR give three
different answers about whether they may.

**Verdict under each answer.**
- (a) *Cages all the way down; the mea culpa's locked-door half is superseded* → the estate is
  internally coherent but publishes a doctrine contradicting your own post, and the two shipped
  Denys must become the bottom rung before the demo can claim "there is no gate".
- (b) *The locked door survives for those three* → **NOT FIT** on the thesis's own refined split;
  encrypt-at-rest (or equivalent) must ship as a versioned member of platform's line.

**Recommended.** (b), narrowly. Reason: the locked-door paragraph is the part of your argument
that the 2022 talk got wrong and the blog corrected; erasing it repeats the over-correction in the
opposite direction. The machinery already exists — `verify/proportionality` derives Audit-vs-Deny
from each party's own signed £ band and is the best single piece of thesis fidelity in the estate.
It has no shipped subject, which is a one-ticket fix. Sub-question: does "everything is always
caged" bind the permanently unversioned population (kube-system, Kyverno's own pods, Flux,
cert-manager, COTS), or only workloads that claim a policy version?

---

## Q6. Does "a human merges" still bind?

**Why the review cannot proceed without it.** `NORTH-STAR.md:34` principle 5 ends "A human
merges." On 2026-08-25T13:31 you wrote (source-verified): "i merged them all, read and reviewed
nothing, do you see the value of wasting my time to do that now? change the rule, that is my
instruction and it is specific and authoritive." The rule was changed: `twin/ENACT_MODE` is a
checked-in one-word file, currently `operations`, and your instruction is recorded verbatim in
`twin/enact_guard.py`. Re-grill 29 reads "this is a stepping stone for allows the ai to do it
all". Step 3 — the demonstration's pivot beat, ticket 74 — has never fired, and its definition of
done cannot be written until this is settled.

**Verdict under each answer.**
- (a) *A human merges and it means something* → **NOT FIT** on principle 5 as demonstrated: the
  proposer, reviewer, merger and signer are one identity in all nine repos, zero rulesets and zero
  branch protection exist, and the proposer's commit is unsigned while its own record asserts it
  is signed. Fixing it means a second reviewer or a credential that cannot merge, and the proposer
  commit gitsign-signed before step 3 fires.
- (b) *It is a stepping stone; the end state is AI disposal inside a priced cage* → then the
  estate's most distinctive claim is untested on itself: the AI's only restraint today is a mode
  file the AI writes.

**Recommended.** (a) for the demonstration, (b) recorded as the end state, with the seam named.
Reason: a proposal PR merged by the identity that opened it proves nothing about principle 5, and
step 3 is the moment an audience decides whether this is governance or automation.

---

## Q7. Are driftwood, tuppence and ludlow props, or plausible firms?

**Why the review cannot proceed without it.** Your instruction (2026-07-23T15:50, source-verified)
was "we're only building a ficticious organisation, cluster, applications, its not applying to a
real legit business. no cuts will be tolerated" — fictitious *and* uncut. Today, on the analysts'
arithmetic using platform's own reduce table against the adopters' own signed evidence, all three
sit at the ladder's bottom rung and two are past the end of it; tuppence and ludlow publish no
`size` at all, so principle 3's proportionality operates for one adopter of three; and the pivot
beat (a £ crossing a band) is arithmetically foreclosed by their own numbers.

**Verdict under each answer.**
- (a) *Props whose numbers exist so the ladder visibly moves* → tune the fixtures and the
  criticism dissolves; the £'s claim to be "grounded rather than emotional" weakens slightly and
  should be stated.
- (b) *Plausible firms whose numbers land where they land* → step 3 can never fire from a clock,
  and the demonstration needs a different pivot.

**Recommended.** (a), said out loud on the artefact. Reason: "we're only building a ficticious
organisation... its not applying to a real legit business" is your own framing and the honest one;
the fix is to give tuppence and ludlow a `size` and place one residual so it really crosses a
band, not to defend the current numbers as findings. Sub-question: is a fourth adopter — one you
did not author — a goal? Three copy-pasted adopters with 24 diverged shared files is one answer;
three instances of a pinned shared package is another.

---

## Q8. What is the truth surface for, and what would "green" mean?

**Why the review cannot proceed without it.** Your own dated answer exists and no document cites
it: 2026-08-28T15:22 (source-verified) — "Pre existing is not acceptable. Fix them. **It's not
good till it's green** even if you need to scope slip to back fix stuff." Against that: 21 TRUTH
lines, none with `fail=0`; run 21 is `pass=57 fail=7 skip=18` of 84; and 12 of the 84 scripts can
never exit 0 on the scheduled runner because `truth.yml` creates no cluster, so the real ceiling
is 70 (65 reachable today) and nothing states it.

**Verdict under each answer.**
- (a) *Green = fail 0 and every skip owned* → **NOT FIT today**, and the fastest route is a cluster
  on the clock.
- (b) *Green = the offline half plus the adopters' sampled facts, with the ceiling published* →
  **CLOSE TO FIT**; the denominator must be relabelled and seven scripts must exit 3 instead of 0.
- (c) *It is your private daily regression alarm, not the citable evidence an audience is shown* →
  the deck must stop quoting it as the latter, and the two want opposite denominators.

**Recommended.** (b), plus publish the ceiling beside the number. Reason: you have already
accepted the ephemeral-KinD sample lane as the live surface (re-grill 1, and the adopters'
drift-sample workflows), so a persistent cluster on the hub clock would duplicate it. But the
number must stop being reported against 84 when 70 is the structural ceiling. Sub-questions:
should the hub clock fire *after* the adopters' sample lanes? Should `clone-estate.sh` grade each
unit at its signed tag rather than its default branch, as its own comment promises?

---

## Q9. Is the talk the driver or the byproduct?

**Why the review cannot proceed without it.** Your instruction, twice on the day you set the
direction: "I need a spec for the talk first, and from that falls out the technical spec for
delivery" and "work backwards from the talk spec" (2026-07-23T15:18, 15:22). Against it,
`.scratch/twin/spec.md:421` and `map.md:43,158`: "The conference talk is a byproduct of the real
system, never its driver" — carried into `NORTH-STAR.md:64` and attributed there to "(Twin map,
2026-08-12, kept.)", i.e. my document, not you. `appendices/G-drift-findings.md:1498` records the
pair as never reconciled.

**Verdict under each answer.**
- (a) *Driver* → the deck's staleness, its three unfired beats and the RUNBOOK's untrue narration
  line become the top-priority defects and almost everything else waits.
- (b) *Byproduct* → those drop below a dozen other things and the current build order stands.

**Recommended.** (a). Reason: it is your instruction in your own words, twice, and the reversal is
sourced to a document I wrote. Under Q1(a) it is the same answer. Sub-question: the RUNBOOK says
driftwood's bring-up reconciles the real signed GitHub remote; the script reconciles a git server
it builds on the laptop seconds earlier. Which of those is the demo you want to give?

---

## Q10. Must the twin forecast, or is scoring a recorded belief the thing you want?

**Why the review cannot proceed without it.** NORTH-STAR §2 names the twin as publishing "priced
forecasts... scored against reality", and the twin plus its tests are 54% of the estate's
executable code. `twin/verbs.py:932-956` emits `float(beliefs[proposition_id])` — the probability
is a hand-typed constant, nothing infers one from a signal, and the package prints that fact in
its own output at run time. Your own words are about gameplay and honest scoring: "giving gameplay
opportunities To answer the what if fast forward rewind Play" (2026-08-04T13:02); "Not everything
we predict will happen. It's a weather forecast" (21:27); "if We don't know where we've been. We
can't possibly know where we're going" (14:03).

**Verdict under each answer.**
- (a) *It must derive a probability* → **NOT FIT at its own headline**; 53,000 lines are apparatus
  around a missing engine.
- (b) *"A recorded belief, scored honestly against reality" is the thing* → **FIT**, and NORTH-STAR
  §2's twin row and §4 step 5 must be restated, because they describe something the build
  deliberately reversed (driftwood's `signals.yaml` declares niobium unbound precisely so the twin
  cannot decide on the clock).

**Recommended.** (b), with the row restated. Reason: everything you actually said is about
gameplay, hindsight and honest scoring, not inference; the build's reversal was considered, not an
omission. But the ratified document must stop claiming otherwise. Sub-questions: should a world
model's beliefs carry a required evidence grade and basis, as a valuation already must? Is it
acceptable for the twin's forward-intel feed — driftwood's largest price line — to stay outside
every signed tag and outside `inherits[]`, so its absence is silent and its bytes carry no
signature?

---

## Q11. How do you want to be asked — and is a bare "Agree" a ratification?

**Why the review cannot proceed without it.** Roughly 84 architectural items are recorded
PROVISIONAL, many on tickets marked `Status: resolved`, which the map's own rule (`map.md:16`)
says should stay open. Your own words of 2026-08-27: "i probably did say 'agree' because i got
tired/overhelmed with questions". The corrective written that day — GAPS.md:93 rule 1, "No
recommendation attached to an architectural question" — was dropped when the rules were copied
into `map.md:16` (five of six carried, rule 1 absent). But the batch shape that followed was your
own instruction: 2026-08-28T08:24 (source-verified), "Process all grillings to generate the
recommended options and then I can walk them... Do as much as you can without stopping to wait on
me to answer anything", answered at 10:43 with "ive already read the recommendations and I can't
find fault with a single one. Well done. Get everything ready for me to then to-spec."

**Verdict under each answer.**
- (a) *A bare agree does not ratify (today's rule)* → the review's honest verdict is "the
  architecture is unratified", 84 items need a route to ratification that does not exist, and
  fifteen `Status: resolved` tickets are misstated.
- (b) *The recommendations are the architecture; decide and record it as your own* → the
  provisional vocabulary retires, `Status: resolved` becomes honest, and the review stops
  reporting a debt you never incurred.

**Recommended.** (b), explicitly recorded, with a short exception list (the items in this
question set). Reason: the evidence is that the panel-verdict shape — five conflicts, three lenses,
one page — is the only format that has ever drawn a reasoned reply out of you, and the honest
reading of "Do as much as you can without stopping to wait on me" is that you want the assistant
to decide. Keeping a vocabulary that says otherwise makes the record false about itself.
Sub-questions: do you want the fifteen assistant-resolved cross-ticket conflicts put to you as one
round? When the build discovers a fact mid-run that forces an architectural decision — as on
2026-08-28 at 22:15, promoting the governed-namespace guard from Audit to Deny — do you want to be
interrupted, or do you accept the build deciding and recording it as its own?

---

## Q12. Is the identity and attestation substrate spine, or shelf?

**Why the review cannot proceed without it.** NORTH-STAR §1's final clause is "every actor is
attestable". The *artefact* half is real and excellent: 24 of 24 tags verify against Rekor under
per-repo anchored identities. The *actor* half — SPIRE, mTLS, SPIFFE authz, OpenBao, device SVIDs,
human login — has never been observed on any citable run; all six scripts SKIP because no cluster
exists. Federation is one trust domain with no peer, and the peers' anchors are literals in the
platform's own tree, which is the tenancy shape §2 forbids. Ticket 12 recorded "spine, not cut" on
a bare agree.

**Verdict under each answer.**
- (a) *Spine* → **NOT FIT** on the sentence that defines the eco-system, and six permanent SKIPs
  are the largest unowned hole in the surface.
- (b) *Designed and shelved for this build* → §1's clause reads "every artefact is attestable",
  §2's identity rows come out, six scripts move to the exclusions file with a reason, the number
  improves and the claim becomes true.

**Recommended.** (b) for this build, (a) recorded as the next thing. Reason: the artefact spine is
what the talk needs and it is genuinely strong; the workload/human/device layer needs a persistent
cluster the clock does not have, and claiming a thing while never observing it is exactly the
failure the 2026-08-25 Docker post-mortem exists to prevent. Sub-questions: should `main` and
`release/*.x` be protected with a required review across all nine repos, given you are the only
human in the estate? Is the hub's truth workflow allowed to run 84 unpinned scripts from eight
other orgs in the same job that holds a `contents:write` token?

---

## De-duplication map (72 dimension questions → 12)

| Q | Absorbs |
|---|---|
| Q1 | operability a/d; scope "when is this due"; engineering "operated by someone other than you", "could a second engineer pick this up"; truth-surface "what is it FOR" (part); process "is there a date or event" |
| Q2 | demo-steps "what does end to end mean"; principles "must a demo include a running workload"; demo-steps "does step 2 count as done"; scope "living document or frozen" |
| Q3 | thesis-fidelity ≥3-versions and ticket-13-D5; truth-surface "is ≥3 still required"; legacy "which org demonstrates it", "is running fleet#69 part of end-to-end", "banners on the 14 repos", "ADR-0004 two planes"; operability "ticket 58 decision (1)" |
| Q4 | pound-engine all six; principles "whose numbers price the twin residual"; participants "must the adopter tag carry exposure" |
| Q5 | thesis-fidelity locked-door and ADR-0007 metadata; principles "does caged bind the unversioned population", "is the orphan-guard Deny the second refusal"; thesis-fidelity "should cage behaviour join the sample lane" |
| Q6 | scope "is AI disposal the purpose"; demo-steps "who reviews and merges"; principles + security "must the proposal commit be signed"; twin "what cage does the twin run inside"; security "protect main across nine repos" |
| Q7 | scope "props or plausible firms"; operability "fourth adopter"; engineering "three independent orgs or three instances"; pound-engine "size on tuppence and ludlow"; participants "separation of artefacts or authority"; scope "own forgetting curve" |
| Q8 | truth-surface all six; engineering "ephemeral cluster or offline-only"; operability "real cluster"; scope "allowed to bring up a cluster"; participants "grade at tag or branch", "red or priced hole"; demo-steps "prove the absence" |
| Q9 | operability "RUNBOOK vs up.sh"; demo-steps "push round 3 / ticket for work blocked on your push" |
| Q10 | twin-validity all six; thesis-fidelity "is the thesis still the subject"; participants "twin its own org", "must the publisher consume public sources on a clock"; demo-steps "step 5 fix or out of scope" |
| Q11 | process-and-record all six; demo-steps "cut a ticket for work blocked on your push" |
| Q12 | security-spine "identity substrate in scope", "unpinned scripts with a write token", "delete the ed25519 paths"; security "gitsign trust instant" (part) |

**Deliberately not promoted** (mechanism decisions the assistant should take and record as its
own, per Q11(b)): the gitsign tagger/notBefore trust instant (ticket 73 owns the fix; the correct
instant is the Rekor signed-entry timestamp); re-grill 6's full-combination coverage (already
answered and binding); the twin CI colour question; the selfcheck-vs-pytest test strategy; the
currency-controller retirement (withdraw it, the reason was a word collision).
