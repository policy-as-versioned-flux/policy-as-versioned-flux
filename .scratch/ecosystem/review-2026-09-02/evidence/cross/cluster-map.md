# Cross-dimension cluster map — 2026-09-02

Input: the thirteen files under `review/assess/` plus the per-dimension digest.
Scope: the **surviving** findings only, except where a refuted finding is the evidence for a
grading disagreement. IDs are written `<dimension>/<id>` because the ids collide across
dimensions (there are three different `P1`s and two different `F1`..`F17` series).

Counts below are counts of *ids*, with the number of *distinct underlying defects* in brackets,
because several clusters are one bug found four times.

---

## Part 1 — Cluster map

### C1. "A green that could not look" — 14 ids [6 defects]

**Root cause.** `talk/verify-all.sh` grades by process exit code, and several checks reach exit 0
(or print `ok`) from a path where the property was never observed. Three mechanisms: exit 0 after
printing your own SKIP; a lookup that misses and reports the miss as an honest absence; a check
that grades presence, or a literal, instead of the property its own header quotes.

| id | what it is called there |
|---|---|
| truth-surface/TS-C1 | seven scripts exit 0 after printing their own could-not-look; `verify/provenance` PASSes with a maximal claim over two unobservable sections |
| engineering-quality/EQ-02 | the same six `computed-semver/verify-*.sh` scripts, `SKIP:` then `exit 0` |
| principles/P6-1 | `five-facts.py:522-528` writes `fired: false` when the falsifier returned `None`; the code's own comment three lines above forbids exactly this |
| principles/P6-2 | step 6 verifies platform's `v2.0.1` instead of `policy/v4.0.0`, and declares feeds unsigned |
| demo-steps/DS-F4 | same |
| operability/O3 | same |
| scope/F5 | same |
| truth-surface/TS-M8 | step 5 PASSes on file presence over an artefact two checks FAIL on in the same run |
| demo-steps/DS-F1 | same, framed as "on its schedule" un-graded |
| twin/TWIN-06 | same, framed as the citable number counting step 5 observed-true |
| twin/TWIN-07 | the only graded twin-quality metric scores a heuristic against its own lookup table — a green that cannot move |
| security/SS-08 | `wargamer.py:200,232` hardcodes `"signed": True` and `:324` asserts the literal |
| principles/P5-3 | same, framed as the proposal commit being unsigned |
| principles/P7-1 | a chained inference (tag verified → composed set built from that sha) printed as three independent per-publisher proofs |

**Four of these are one line of code.** `verify/e2e/verify-e2e-step6-provenance.sh:87` uses
`git tag -l 'v*.*.*'`, which cannot match `threat-register/v2.0.0`. That single glob produces
principles/P6-2, demo-steps/DS-F4, operability/O3 and scope/F5 — four ids, four dimensions, one
`|| fallback`. Three more (TS-M8, DS-F1, TWIN-06) are one missing assertion in
`verify-e2e-step5-twin-forecasts.sh`. Two more (TS-C1, EQ-02) are the same seven `exit 0`s.

**Do not merge two things that share a word.** truth-surface/TS-C1 is about
`verify/provenance/verify-provenance.sh` (SPIRE and rekor-cli sections degrade to a printed note
and it PASSes anyway). The other four are about `verify/e2e/verify-e2e-step6-provenance.sh` (the
tag glob). Different files, different bugs, same noun.

---

### C2. Pins are checked for existence, never for content — and outside the policy artefact the estate mostly does not pin at all — 12 ids [8 defects]

**Root cause.** NORTH-STAR §2's "consumed only through a pinned, signed dependency" is applied to
the policy artefact and to almost nothing else: not to the gate's own inputs, not to adopter CI,
not to publisher release gates, not to the twin, not to two of the toolchain installs. Where a pin
does exist, the check is that the tag *resolves*, never that the pinned *tree contains what the
consumer prices or enforces from it*.

**Sub-family A — no pin at all:**

| id | called there |
|---|---|
| participants/P5 | the truth surface clones every unit's default branch; `clone-estate.sh:37-39`'s own precondition ("once a signed v1.0.0 lands, pin it here") fired on all eight and was not acted on |
| participants/P3 | ico, feeds and insurer consumed at moving `main`, no Flux source object, no commit |
| participants/P2 | twelve checkouts naming the deleted branch `ecosystem/thin-slice` (ticket 62) |
| participants/P4 | ico, insurer and feeds release gates check out platform with no `ref:` — the gate's instrument is platform's default branch |
| security/SS-06 | `curl -s https://fluxcd.io/install.sh \| sudo bash`, fifteen lines under a comment stating the pinning rule, inside the identity that signs the only citable artefact |
| security/SS-03 | the adopters' trust domains and bundle endpoints are literals in platform's tree |

**Sub-family B — a pin whose tree does not contain the thing (the sharpest shape in the review):**

| id | called there |
|---|---|
| participants/P1 | the insurer's gitsign-verified quote attests `driftwood exposure v1.1.0`; no adopter's v1.1.0 tree has an `exposure` section |
| pound-engine/PE-11 | **the same bug**, seen from the clock: every requote leg REFUSES `missing instrument: … carries no exposure section`, on both runs the insurer has ever had |
| principles/P4-2 | **the same shape, at the cage**: adopters' `composed-set.yaml` is reconciled from tag `v1.1.0`, whose tree carries 2.0.0/2.0.1/3.0.0 — three *retired* lines — so what Flux installs is a policy set the platform withdrew |
| participants/P6 | the twin has no org, no tag, no signature; driftwood runs the sweep inside `hub/.estate-clone/driftwood` |
| principles/P6-3 | same, framed as the largest £ line entering signed evidence as a local file read |
| twin/TWIN-03 | same, framed as "the one participant whose output nobody can verify" |

Sub-family B is the same failure that `insurer/party.yaml` already records happening once before
(the fabricated `v1.2.0`, found 2026-08-29). The fix then substituted a real version string without
checking the tree. It is now on its third artefact.

---

### C3. The citable clock stands up no substrate — 4 ids [1 defect]

**Root cause.** `.github/workflows/truth.yml` installs gitsign/kyverno/cosign/flux and never
creates a cluster, so every live tail in the estate is structurally could-not-look on the only
surface any document is permitted to cite.

`thesis/TF-05` (critical), `principles/P2-6`, `security/SS-02`, `engineering-quality/EQ-06`.

Refuted on the same fact: `truth-surface/TS-C2`, `operability/O8`, `scope/F4`. See Part 2 §6.

---

### C4. One declared policy version — 4 ids [1 decision]

**Root cause.** The 2026-08-29 retirement of 2.0.0 / 2.0.1 / 3.0.0 left
`distribution/versions.yaml` with one element, removing the subject of four gate checks in one
commit.

`thesis/TF-01` (critical), `principles/P4-1`, `principles/P1-1` (the conditional-rule branch lived
only in the retired `require-nonroot-2-0-1`), `legacy/L7`.

Refuted on the same fact: `scope/F9`, `operability/O1`, `truth-surface/TS-M9`. See Part 2 §7.

---

### C5. Nothing prices or proposes being behind — 5 ids [2 defects]

**Root cause.** The DECIDED replacement for ADR-0010's consumer-side `sunset:` — price a stale pin
by the EOL ramp, and have the adopter's proposer open a retirement PR — is unbuilt on both halves.
`composition.py:271-274` `FEED_CONVERTERS` has exactly two rows and no `eol`/`cve` kind, and
`tier_pr.py` builds only `cage-tier` proposals.

`thesis/TF-02` (critical), `scope/F3`, `legacy/L3`, `legacy/L2` (the publisher advertises cve and
eol; composition refuses any adopter who pins them — the same missing converter),
`legacy/L4` (ADR-0010 still teaches the field that was voted out — the record half).

---

### C6. The £ is an ordinal index published as a balance-sheet quantity — 9 ids [8 defects]

**Root cause.** Every input that turns a severity into money is an editorial constant, a
platform-held fixture, or absent; nothing aggregates the retained lines against the one band; and
`size` exists on one adopter of three.

`pound/PE-02` (frequency is a converter constant; cannot draw a loss-free year),
`pound/PE-06` (sizing rule diverges from ticket 07's decided `min()` *and* from Art 83(4)),
`pound/PE-07` (`THREAT_LM_GBP` — a per-adopter fixture in the platform's repo, the exact class
ADR-0021 retired), `pound/PE-10` (control weights uncited, and they drive a 60% insurance
carve-out), `pound/PE-05` (no aggregation: 2.18× the band retained with every line green),
`pound/PE-08` + `scope/F2` (no `size` on tuppence or ludlow → identical £9,039,791, `per_customer`
null), `pound/PE-01` (the one insurance transfer is priced at 1/22 of the loss on its own layer),
`pound/PE-12` (tcor's transfer move double counts the deductible and charges the full ALE).

---

### C7. The £ never reaches an enactment — 5 ids [3 defects]

**Root cause.** Nothing binds the composed `proposed_tier` to the enacted
`posture.acme.io/tier`; the residual that would move is computed from the platform's table rather
than the adopter's own published curve; and no residual has ever crossed a band, so no proposal has
ever opened.

`demo-steps/DS-F2` (critical), `principles/P5-2`, `thesis/TF-03`, `twin/TWIN-09`,
`principles/P3-1`.

Downstream of C6: the calibration decision is what makes a crossing possible at all.

---

### C8. The clocks are half-dead and the gate is blind to them — 7 ids [5 defects]

`participants/P9` (feeds and insurer have failed every scheduled run they have ever had; nist is
green and writes null because its reader looks at `catalog/v<N>/feed.json` and the catalogue is at
`catalog/`), `participants/P7` + `twin/TWIN-04` (twin-sweep's step runs under `bash -e`, so the
python line aborts the step before `rc=$?`; the `moved=true` branch is unreachable and no
observation has ever been written), `truth-surface/TS-M2` + `principles/P5-1` (`verify-schedules`
has no cross-org credential; twelve SKIPs every run; principle 5 recorded as one SKIP),
`demo-steps/DS-F6` (tuppence and ludlow have never had their composed set in force; round 3 of the
fix is committed and unpushed), `security/SS-07` (half — the read credential the schedules check
needs, and the write credential it shares a job with).

---

### C9. One identity is every role and nothing on the forge enforces any of it — 4 ids (+1 shared)

`security/SS-04` (zero rulesets and zero branch protection on all nine repos, verified live),
`security/SS-05` (`release/<M>.<m>.x` is an accepted signing path that never touches `main`),
`engineering-quality/EQ-08` (proposer = reviewer = merger = signer, 408 commits, one human),
`scope/F8` (the AI's only restraint is a mode file the AI rewrites; the interim author≠merger rule
is unbuilt). Shared with C1: `security/SS-08` — the proposer's identity cannot be forged because it
does not exist.

---

### C10. The durable record is derived from nothing, so it drifts from the code — 10 ids

`process/P4` (fifteen resolved tickets cite the TRUTH line of 2026-08-29, whose hub tree contains
none of their checks; fourteen uncorrected), `process/P5` + `principles/P2-4` (Audit→Deny promoted
inside an implementation run; CONTEXT.md still says the opposite; a green gate check certifies a
fix that never shipped), `process/P8` + `legacy/L4` (ADR-0008 and ADR-0010 read as live
architecture), `legacy/L5` + `scope/F10` (the currency controller is retired in the map, present in
the tree, and graded by the gate every run), `truth-surface/TS-M4` (Status is not derived from a
check; the tracker has gone false), `operability/O7` (README's config-base claim vs three divergent
adopter forks), `process/P7` (four of the six ADRs from the bare-agree batch do not record their
own provisionality).

---

### C11. ~84 architectural items rest on a bare agree, and nothing converts them — 3 ids

`process/P1` (GAPS rule 1 — "no recommendation attached to an architectural question" — was dropped
when the rules were copied into `map.md:16`), `process/P7` (shared with C10 — the provisionality
lives only in `.scratch/`), `principles/P4-3` (re-grill 6's recorded owner override, "run the full
combination set", disclosed as unbuilt in the shipped 4.0.0 evidence). C11 is the upstream of C10,
not a peer of it.

---

### C12. The twin scores beliefs; it does not form them — 4 ids (1 shared)

`twin/TWIN-01` (critical — `verbs.py:932-956` reads a YAML number; nothing infers a probability),
`twin/TWIN-02` (the flagship red scores a belief attributed to "market consensus" with no record of
how it was established), `twin/TWIN-05` (the twin's own participant definition is true for no
adopter), and shared with C1, `twin/TWIN-07`.

---

### C13. The engineering apparatus is applied to the twin only — 3 ids

`engineering-quality/EQ-01` (zero tests, types or lint across 28,490 lines of unit Python and the
gate's own 3,738), `EQ-04` (the one pytest/mypy gate is permanently red, and a real typecheck
regression arrived inside that red unnoticed), `EQ-07` (7,000 lines of monolithic `selfcheck()`
that no runner can address).

---

### Singletons (no cluster)

`operability/O4` (the RUNBOOK narrates a signed-GitHub reconcile that `up.sh` never performs),
`operability/O5` (the hub carries no licence), `truth-surface/TS-M1` (the deck is built from a
local run at a superseded commit — adjacent to C1 and C10 but its own mechanism),
`truth-surface/TS-M6` (20 of 57 passes cross a party boundary and the composition is nowhere
labelled), `principles/P3-2` (two severity engines, no equality check — the estate built exactly
this guard for the two *selection* engines), `legacy/L6` (the superseded org's clock still runs).

---

## Part 2 — Contradictions, and the same fact graded differently

### Direct contradictions — two surviving findings that cannot both stand

**1. The currency controller. `legacy/L5` vs `scope/F10`.**
L5: the retirement was a **category error** (posture currency vs money FX), it is the estate's only
post-admission re-caging mechanism, and the retirement should be withdrawn. F10: the retirement was
**decided and never executed**, the module is 416 lines of ballast still graded every run, and it
should go. Same file, same decision, opposite remedies, and neither auditor saw the other.

**2. Whether the twin's price has a pin. `twin/TWIN-08` (refuted) vs `principles/P6-3` +
`participants/P6` + `twin/TWIN-03` (all surviving).**
TWIN-08 — "the twin's price is the only pricing parent with no pin, no version resolution, no
signature check, and a silent absence" — was refuted. Three near-identical claims survive under
different names. Either the refutation is wrong or three surviving findings overstate the same
fact; the review does not currently say which.

**3. Whether "there is no gate" is a contradiction. `scope/§1` probe table vs `principles/P2-4` +
`process/P5`.**
The scope auditor grades it "vocabulary collision, not a rule conflict" — correctly, for the
*release* gate. The other two find a live second `Deny` at *admission* (`policy-version-orphan-
guard`), a glossary that denies it exists, and an ADR that blesses only one refusal. Read
literally, the scope verdict refutes two surviving findings; read carefully, they are answering
different senses of the word. Someone has to say which sense NORTH-STAR principle 2 means.

**4. Whether the cert-skew red is an estate fault or an instrument fault. `demo-steps/DS-F5`
(refuted) + `security/SS-01` (refuted) vs `truth-surface/§3 row 1` + `principles/P7-4`.**
Two auditors classed the cause of four of run 21's seven reds as an *instrument* fault
(`verify_gitsign.py` evaluating the chain at the tagger second, which is one second before
`notBefore` on 5 of 24 tags) and both were refuted. Two classed the same red as an *estate* fault
owned by ticket 73 and were not challenged. The cause of the largest red group on the citable run
is unsettled inside this review.

**5. Whether step 2 is done. `thesis/strengths` vs `demo-steps/DS-F3`.**
Thesis: "the updatable loop completed once for real and is graded from the PR record rather than
simulated" (driftwood #20). Demo-steps: the same PR moved `old_price == new_price ==
19558.549772440045`, so step 2's second clause ("the composition re-prices") is unmet, and the
PASS line's word "merged" describes tuppence, which has merged nothing. Same PR, opposite verdict.

### Same fact, different grade

**6. `truth.yml` creates no cluster — seven findings, four gradings.**
Survives as `thesis/TF-05` (**critical**: "a platform enacts priced cages" is unciteable),
`principles/P2-6` (major), `security/SS-02` (major), `engineering-quality/EQ-06` (major).
Refuted as `truth-surface/TS-C2` (the ceiling claim), `operability/O8`, `scope/F4`. The identical
evidence — `grep "kind create" .github/workflows/truth.yml` returns nothing — is graded critical,
major, and not-a-finding in the same review.

**7. "≥3 coexisting versions" is at one — six findings, two gradings.**
Survives as `thesis/TF-01` (**critical**), `principles/P4-1` (major), `legacy/L7` (major).
Refuted as `scope/F9`, `operability/O1`, `truth-surface/TS-M9`. This is the requirement the 2022
thesis calls non-negotiable and `CONTEXT.md:153-155` calls "the crux"; the review has it both ways.

**8. Proportionality. `thesis/TF-03` (surviving, major) vs `principles/§3` verdict.**
Principles reads `verify_proportionality`'s PASS as making principle 3 "the strongest-built
principle". Thesis reads the same capture as a hub bench rig whose control (`encrypt-at-rest`)
appears in zero unit repos, under no tag, pinned by nobody. Same PASS line, opposite weight.

**9. The deck. `truth-surface/TS-M1` (surviving) vs `operability/O2` (refuted).** Same artefact,
same staleness, opposite survival.

**10. The three adopter forks. `engineering-quality/EQ-03` (refuted, graded critical) vs
`operability/O7` (surviving, major).** Same measurement — adopter gates at 1,087 / 661 / 1,213
lines, `five-facts.py` diverged in both directions — refuted in one dimension and surviving in
another.

**11. Insurer severity. `participants/P1` (critical, "the second shipment of the same laundering
class") vs `pound/PE-11` (major, and its text calls the SKIP "honest").** Same artefact, same
missing section, two severities and two framings.

**12. nist's clock, inside one dimension.** `participants` lists
`"it looked and found none, which is a fact with a date on it, not a silence"` in its **strengths**
(refusal over guessing) and the same JSONL line in surviving `P9` as "the regulator's green clock
writes a dated falsehood about its own signed catalogue". Both are true; the dimension does not
reconcile them.

**13. The five-fact sample. `principles/P7-1` (surviving: fact 3 for the two publishers is a
chain, not a reconciliation observation, and the capture prints it as three independent proofs) vs
`thesis/§3.5` and `demo-steps/§5` (praised as a real, live, cross-org observation).** Same sample,
same run id.

**14. Ownership disagreements on the same reds.** `demo-steps/DS-F6` says the tuppence/ludlow
reconcile fix has **no** open owning ticket (round 3 committed and unpushed, ticket 60 resolved);
`truth-surface/§3` assigns those two reds to tickets 62/74. `participants/P9` assigns the
feeds/insurer clock failures to ticket 57; `truth-surface/M2` assigns them to ticket 56.

**15. TS-C1 vs EQ-02 severity.** Identical evidence (`verify-cage-engine.sh:12-15` and five
siblings), identical remedy (`exit 0` → `exit 3`), graded **critical** by truth-surface and
**major** by engineering-quality.

---

## Part 3 — Root-cause ranking

Ranked by the number of surviving finding ids each would close. Overlaps are marked; shared members
are counted once in the total.

| # | root cause | ids closed | cost shape |
|---|---|---|---|
| **1** | **C1 — a green that could not look** | **14** | mechanical: 7 `exit 0`→`exit 3`; one tag glob; one step-5 assertion; one deleted `"signed": True`; one falsifier tri-state; one honest sentence on P7-1 |
| **2** | **C2 — pins checked for existence, never content; and not applied to the estate's own instruments** | **12** | mostly mechanical (pin `clone-estate.sh` to tags, fix the twelve dead refs, `ref:` the publisher gates, pin the flux install) + two real pieces of work: cut an adopter tag that carries `exposure`, and bump the adopters' composed set off the retired lines; + one owner decision (does the gate grade tags or branches?) |
| **3** | **C10 — the record is derived from nothing** | **10** | cheap: banners on two ADRs, a dated note on fourteen tickets, one glossary entry, one ticket-67 check widened from `map.md` to `issues/*.md` |
| 4 | C6 — the £ is an ordinal index published as a balance-sheet quantity | 9 | owner decisions (calibration, `size` on two adopters, what the £ is *for*) |
| 5 | C8 — the clocks are half-dead and the gate is blind to them | 7 | mechanical (`bash -e`, nist's path, a cross-org read token) + one push the owner must make |
| 6 | C5 — nothing prices or proposes being behind | 5 | build: an `eol` converter row and a retirement proposal shape |
| 6= | C7 — the £ never reaches an enactment | 5 | one binding check + whatever C6 decides |
| 8 | C3 — the clock stands up no substrate | 4 | one job in `truth.yml`, or a declared scope in NORTH-STAR §5 |
| 8= | C4 — one declared policy version | 4 | one owner decision (ticket 58 (1) / 63) |
| 8= | C9 — one identity is every role | 4 | one owner decision (protect `main` and `release/*.x` on nine repos) |
| 11 | C13 / C12 / C11 | 3 each | — |

**Top three, stated as the fix.**

1. **C1 — make every green rest on an observation (14 ids).** Seven scripts exit 3 instead of 0;
   `verify-e2e-step6-provenance.sh:87` reads each unit's own tag shape instead of `v*.*.*`;
   step 5 asserts a reproducible render and a dated sweep observation instead of file presence;
   `wargamer.py`'s `"signed": True` is derived or deleted; `five-facts.py` propagates `None` as
   could-not-look; P7-1's PASS line says "chain", not "three proofs". Closes
   `truth-surface/TS-C1`, `engineering-quality/EQ-02`, `principles/P6-1`, `principles/P6-2`,
   `demo-steps/DS-F4`, `operability/O3`, `scope/F5`, `truth-surface/TS-M8`, `demo-steps/DS-F1`,
   `twin/TWIN-06`, `twin/TWIN-07`, `security/SS-08`, `principles/P5-3`, `principles/P7-1`.

2. **C2 — consume the estate the way the estate tells adopters to consume (12 ids).** Pin the
   gate's clones to signed tags; give ico/feeds/insurer real tag+commit pins and Flux sources;
   replace the twelve `ecosystem/thin-slice` refs; pin the publisher release gates' platform
   checkout; pin the flux install; tag the twin; and — the load-bearing half — **verify that a
   pinned tree contains the thing the pin claims**, which is one assertion and closes three
   otherwise unrelated findings at once (`participants/P1` + `pound/PE-11` + `principles/P4-2`).
   Closes `participants/P1`, `/P2`, `/P3`, `/P4`, `/P5`, `/P6`, `pound/PE-11`, `principles/P6-3`,
   `principles/P4-2`, `twin/TWIN-03`, `security/SS-06`, `security/SS-03`.

3. **C10 — derive the record from something (10 ids).** Closes `process/P4`, `/P5`, `/P7`, `/P8`,
   `principles/P2-4`, `legacy/L4`, `legacy/L5`, `scope/F10`, `truth-surface/TS-M4`,
   `operability/O7`. It is the cheapest of the three and the lowest fitness weight: nothing in it
   changes what the estate *does*, only what it *says it does*. Note also that C10's ten findings
   are the symptom; **C11 is their cause**, and C11 cannot be fixed by an agent — it is the one
   root cause on this list whose remedy is an owner decision about how decisions get made.

**If the ranking is by consequence rather than by count, C6 replaces C10 in third place.**
C6's nine ids are the only cluster whose fix also unblocks C7's five (including
`demo-steps/DS-F2`, critical) and one of the two things the map's destination sentence fails on.
C10's ten cost the estate credibility; C6's nine cost it the demonstration.

**Two clusters carry a critical each and appear nowhere in the top three, deliberately.**
C3 (4 ids, incl. `thesis/TF-05` critical) and C4 (4 ids, incl. `thesis/TF-01` critical) are small by
count and large by weight: between them they are the reason the estate cannot cite its own cage and
cannot show the thesis's own non-negotiable requirement. Both are single decisions, not programmes
of work. Ranking by id count under-serves them, which is why §6 and §7 above matter: the review
graded both of those facts inconsistently, and a count-based ranking inherits that inconsistency.
