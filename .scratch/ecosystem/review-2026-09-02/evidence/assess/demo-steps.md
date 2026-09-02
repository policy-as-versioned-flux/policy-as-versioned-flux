# Assessment — NORTH-STAR §4 steps 1–7 and §5

Auditor pass, 2026-09-02. Read-only. Citable line: `TRUTH 2026-09-02T10:11Z run=21 hub=7b92990 …
pass=57 fail=7 skip=18 excluded=2 total=84` (`origin/main:talk/truth.log` line 18, produced by hub
run `33616685427`).

Everything below is either a file:line, a command with its output, or a GitHub run/PR/tag id.
Where I could not look, I say so.

---

## 0. The ledger, in one table

For each §4 step: what has happened **for real** (a real tag / a real merged PR / a real
proposal / a real lane observation / a real scheduled forecast / a real Rekor verify), what the
e2e script actually proves, and what is simulated.

| # | NORTH-STAR §4 sentence | Real, with a citable id | What the e2e script proves | Simulated / not observed | run-21 grade |
|---|---|---|---|---|---|
| 1 | A regulator publishes a new penalty schema version. Signed and tagged. | **Yes.** `ico` tag `v3.0.0` exists on the real remote (`gh api repos/policy-as-versioned-ico/ico/tags` → `v3.0.0`, `v1.0.0`), cut by `cut-release` run `33406040611` (2026-08-31, `workflow_dispatch`), and verified against Rekor in step 6. | Envelope validates against the feed contract **and** the tag is resolved by a real network call: `git ls-remote --tags https://github.com/policy-as-versioned-ico/ico` (`verify/feed-contract/feed_contract.py:86`). | Nothing material. The tag was hand-dispatched, not clock-cut — consistent with §3.5 ("a human merges"), but not "on a clock". No GitHub *Release* exists for v3.0.0 (`gh release list` shows only v1.0.0). | PASS |
| 2 | Renovate raises the pin in one adopter. The composition re-prices the adopter's exposure. | **Half.** The *pin raise* happened once, for real: driftwood PR **#20**, head `renovate/feeds-threat-register-2.x`, single commit `ea1c8db` authored by `github-actions[bot]`, moving `party.yaml` + `composed/HEADER.yaml` + `composed/evidence.json` together, merged by a human 2026-09-01T08:57:50Z. Graded from the **real PR record** by `verify/renovate/verify-renovate-merged-feed-pr.sh` → PASS on run 21. | That bumping a pinned parent version through composition moves `prices[]` — on a **throwaway copy** of an adopter's tree in a `tempfile.TemporaryDirectory()` that is not a git repo (`step2_reprice.py:145-160`). | **The re-price half.** `git show ea1c8db -- composed/evidence.json` shows `old_price` and `new_price` both `19558.549772440045` — the real merged bump moved **no number**. The e2e PASS is on **tuppence**, which has never merged a Renovate PR (its Renovate PRs #1/#2/#4/#10 are all CLOSED) and still pins `v1` on its real main. | PASS (offline, tuppence) |
| 3 | The £ crosses a band. The tier moves. A proposal PR opens, signed. A human merges. | **No.** No proposal PR has ever opened. `gh api repos/*/branches` on all three adopters lists no `wargamer/*` branch. Today's real scheduled proposer run `33626099181` (driftwood, 2026-09-02T11:43Z, conclusion `success`) printed `[]` — nothing proposed. tuppence/ludlow `propose-tier` scheduled runs all **fail** (`33633036907`, `33515059588`, `33518603510`). | That a residual placed either side of the adopter's own signed band selects a different tier through the adopter's own versioned `selection-policy` package (cross-checked against `platform/graded/cage.py`), and that `tier_pr.py --dry-run` would edit `posture.acme.io/tier` on the governed Namespace and not the pod label. Nothing is opened, nothing written. | **The whole event.** The two residuals are synthetic by construction: `under = band * 0.5`, then `over *= 1.02` in a loop until the tier flips (`step3_band.py:181-190`). | PASS (synthetic, driftwood) |
| 4 | Flux reconciles the new cage spec. The workload keeps running, caged tighter. | **Partly, driftwood only.** Today's *scheduled* lane run `33624104359` (2026-09-02T11:20Z, ephemeral cluster `dsample-33624104359`) records for `driftwood-composed`: facts 1, 3, 4, 5 **true** — Ready at the pinned tag+commit from the real remote, `lastAppliedRevision == eacae33ca3a1`, all 16 rendered objects live and equal to the offline render, all 16 in a Flux inventory. Fact 2 **false**. | On a runner with a cluster: seven hard-asserted facts A–G on the standing KinD cluster. On the citable (cluster-less) runner: it grades the lane's committed five-fact sample through `drift/five-facts.py grade`, which refuses hand-typed/unsigned samples and refuses to PASS with an undeclared falsifier (`five-facts.py:627-654`). | **tuppence and ludlow entirely** (see F6), and driftwood's fact 2 (see F5). | **FAIL** |
| 5 | The twin, on its schedule, plays a dated signal forward, emits a scored forecast, publishes forward intel. | **No, on the schedule.** driftwood `twin-sweep.yml` has fired twice and failed twice: `33627910027` (2026-09-02T12:04Z) and `33508119299` (09-01), both on `FAIL: twin/forward-intel/v1/feed.json is not what the overlay renders`. The **artefacts** are real and driftwood's priced chain does carry a `source: twin` line. | Presence, by path, of five twin artefacts, then it runs `verify/twin-evals/verify-twin-evals.sh`. It never looks at a run, a date, or a schedule. | **"on its schedule".** Also: only driftwood has an overlay (ticket 64). | PASS |
| 6 | Provenance: every step verifiable in Rekor and in the sidecars. | **Yes, and it is the most solidly real of the seven.** run-21 capture: 80 published artefacts resolved to tags on publishers' real remotes; 8 release workflows carry anchored own-repo identity regexps; the **real `gitsign` binary** verified 7 tags against real Fulcio certs with `Validated Rekor entry: true` (driftwood v1.1.0, ico v3.0.0, insurer v1.0.0, ludlow v1.1.0, nist v1.1.0, platform v2.0.1, tuppence v1.1.0). | Three parts, all real: remote tag resolution (network), regexp anchoring incl. five negative-shape attacks per unit, and the live Rekor verify. | One publisher silently skipped — see **F4**. | PASS |
| 7 | Honesty: one command reports every claim above as pass, fail or could-not-look. | **Yes.** `verify-e2e-step7-honesty.sh` runs in the gate, runs its own selfcheck first, and printed the table in run 21 with step 4 red. | *Reporting* honesty only: missing/hung step, exit-code-vs-last-line mismatch, hedged PASS, buried "could not look". It explicitly does not re-grade results. | It cannot catch a step that simply asserts something false — stated in its own header and the README. | PASS |

**Step 4 has never once graded PASS on a citable run.** Verdict history of its capture across every
commit that touched it on `origin/main`:

```
2026-08-31 08:09 b05035e2  SKIP: KinD cluster 'driftwood' absent
2026-09-01 09:41 aae09206  SKIP: no cluster on this runner, and the lane sample cannot stand in…
2026-09-01 21:07 62eddf80  FAIL: the scheduled lane sample observes a step-4 fact false
2026-09-02 10:11 a2094961  FAIL: the scheduled lane sample observes a step-4 fact false
```

All seven of run 21's fails are in this dimension:

```
.estate-clone/driftwood/twin/verify-twin-scenarios.sh    FAIL (exit 1)
.estate-clone/driftwood/verify-reconcile.sh              FAIL (exit 1)
.estate-clone/driftwood/verify-twin-overlay.sh           FAIL (exit 1)
.estate-clone/ludlow/verify-reconcile.sh                 FAIL (exit 1)
.estate-clone/tuppence/verify-reconcile.sh               FAIL (exit 1)
verify/demo/verify-demo.sh                               FAIL (exit 1)
verify/e2e/verify-e2e-step4-flux-reconciles-cage.sh      FAIL (exit 1)
```
(`gh run view 33616685427 --repo policy-as-versioned-flux/policy-as-versioned-flux --log`)

---

## 1. Is a PASS on steps 2 and 3 honest as "step N passes"?

**Step 3: yes, and it is a model of how to do this.** Its PASS line opens with "a **SYNTHETIC**
residual placed either side of driftwood's own signed appetite band … **not driftwood's real
priced position**", and the script carries the dated 2026-08-29 self-correction that replaced the
earlier wording (`step3_band.py:262-269`). The shell wrapper adds "(python half; the tier landing
in force is step 4)". A reader of that line cannot come away believing the event happened.

**Step 2: no, not as written.** Its PASS line opens "**a merged pin bump** (threat-register v1 ->
v2) **re-prices tuppence's prices[]** …". No such bump has been merged in tuppence: all four of
tuppence's Renovate PRs are closed unmerged and tuppence's real `party.yaml` still pins `v1`. The
line does say "offline, with no repo touched", which is the confession — but it is at the end,
after the assertion, and "merged" is doing false work at the front. Step 3 got the treatment step
2 has not had. See **F3**.

**Both are honest as *mechanism* proofs and dishonest as *event* proofs, and only step 3 says
which one it is.** That distinction is the whole difference between the map's destination and
where the estate stands.

---

## 2. The destination sentence

> "…and the eco-system has run end to end once, on a clock, with driftwood, tuppence and ludlow
> consuming." (`.scratch/ecosystem/map.md:7`)

**No. Not once, not on a clock, and not with three adopters consuming.** Three independent
reasons, each with a citable id:

1. **Step 3 has never fired.** No `wargamer/*` branch on any adopter; today's real proposer run
   returned `[]` (`33626099181`).
2. **Two of the three adopters have never had their composed set in force.** Every five-fact
   sample tuppence and ludlow have *ever* appended has `fact_4` and `fact_5` false. Today's
   tuppence *scheduled* sample `33632084845`: "12 of 16 rendered objects are absent from the
   cluster"; "16 of 16 rendered objects are in no Flux inventory".
3. **ludlow's lane has never succeeded on a clock at all.** Its only scheduled `drift-sample` run
   `33517601520` failed at "install the pinned tools (binary + checksum, no marketplace action)";
   its only two green samples are `workflow_dispatch` (`33556801679`, `33558858820`).

And a fourth, structural: **the truth surface cannot see whether any clock ran.** Every "did this
clock run inside its period" question in `verify/schedules/verify-schedules.sh` SKIPs on the hub
runner with `GitHub unreachable (Command '['gh', 'auth', 'status']' returned non-zero exit status
1.)` — twelve such lines in the run-21 capture. The gate's only real windows onto the clocks are
indirect: a GitHub run id embedded in a lane sample, and merge-commit archaeology in
`verify-renovate-merged-feed-pr.sh`. Both are genuine, but "on a clock" is not, today, a
gradeable proposition. Ticket 56 owns this and is open.

### The shortest real path to the destination

Ordered by dependency; each item names its blocker and its evidence.

1. **Push round 3 of the sampler wait-order fix to tuppence and ludlow.** Ticket 60's own closing
   note says round 3 is "committed and patched" on branch `ticket-60-wait-order`; that branch
   exists on **no** adopter remote, and today's post-round-2 scheduled tuppence sample still reads
   12/16 absent. Blocked by: the owner's push (enact_guard refuses adopter pushes). **No open
   ticket owns this** — see F6.
2. **Fix ludlow's tool-install step** so its lane fires on the clock at all (`33517601520`).
3. **Fix the verifier's cert-vs-tagger-time skew** (ticket 73, open). This is an *instrument*
   fault, not an estate fault: the same driftwood `v1.1.0` tag that the in-cluster controller
   rejects as "certificate is not yet valid" is verified by the real `gitsign` binary in step 6
   with `Validated Rekor entry: true`. Fixing it turns driftwood's step 4 from 4/5 to 5/5.
4. **Make a residual really cross a band** (ticket 74, open). Today driftwood sits at `baseline`
   with a £40,000 band; the step-3 probe shows the flip happens somewhere between £20,000 and
   £58,269 of caged residual. The natural trigger is the next real feed bump that moves a price,
   arriving by Renovate as step 2 already can. Then a human merges the proposal PR.
5. **Fix the twin's overlay re-render** (ticket 72, open) so `twin-sweep` succeeds on its clock,
   and **harden step 5 to assert a dated scheduled sweep** (ticket 64, open).
6. **Give the citable run sight of the clocks** (ticket 56, open) so "on a clock" can be graded
   rather than asserted.
7. **Rebuild the deck** (ticket 66, open) so the artefact a reader opens matches the surface.

Items 1, 4 and the merge in 4 need the owner. Everything else is AFK work with an owning ticket
except item 1.

---

## 3. §5, the truth surface, bullet by bullet

| §5 bullet | State | Evidence |
|---|---|---|
| Discovers every `verify*.sh` by glob; fails if any is neither run nor excluded with a reason | **Almost.** `find .estate-clone verify -name 'verify*.sh'` (`talk/verify-all.sh:45`) globs two directories, not the tree. `.scratch/multi-org-estate/verify-08-filter-repo-split.sh` and `verify-09-repoint-flux-sources.sh` are neither run nor in `talk/verify-exclusions.txt` (2 entries, both `.estate-clone`). `talk/verify-demo.sh` **is** covered, via the symlink `verify/demo/verify-demo.sh`, and says so in its own header. | F8 |
| Three outcomes; could-not-look prints as SKIP with a reason | **Built and holding** for the seven steps: `lib.sh`'s `pass/fail/skip` → exit 0/1/3, verdict flattened to one line. | `verify/e2e/lib.sh:11-15` |
| Every live claim asserts its substrate first | **Holds for the e2e family.** Step 4 checks kubectl/kind/docker/cluster/CRD before any live read and falls to the lane sample, never to a pass. | `verify-e2e-step4…sh:63-73` |
| Ticket `Status:` derived from a named check | **Not built.** Ticket 59, open. | `.scratch/ecosystem/issues/59-*.md:4` |
| The number and its date recorded every run; a fall is a blocking event | **Recorded, yes** (18 TRUTH lines in `talk/truth.log`). **"Blocking", by convention only** — ticket 59 owns the mechanism. The falls were in fact acted on: run 17 (pass=59 fail=1) → run 18 (fail=3) produced ticket 72; run 19 → 20 (fail=7) produced 72/73/62. | `origin/main:talk/truth.log`; ticket 59 |

**Correction to a reader's map (`github-live`):** hub `truth.yml`'s failures are **not**
observation-lane failures. On run `33616685427` (the run that produced TRUTH 21), the step
"the observation cage — a clock appends observations, never a declaration" concluded `success`
and the only failed step is `fail if the gate failed`. Same for `33497493135` and `33557360933`.
The truth clock is healthy; its red is the honest red of a 7-fail estate.

**Correction to a reader's map (`verify-scripts-hub`):** the run-21 `verify-schedules` capture is
not missing a wrapper verdict. Its last line (line 50) *is* the wrapper's composed verdict — it is
byte-identical to line 8 because `verify-schedules.sh` composes it as
`echo "SKIP: $(grep '^SKIP:' "$log" | head -1 | cut -c7-)"`, and line 8 is the first raw SKIP.

---

## 4. Findings

### F1 (major) — Step 5 reads PASS on the citable run while the twin's only clock has failed on both firings

`verify-e2e-step5-twin-forecasts.sh` checks the presence of five paths and then runs
`verify/twin-evals/verify-twin-evals.sh`. It never looks at a run, a date or a schedule, yet
NORTH-STAR §4.5's operative words are "**on its schedule**". driftwood's `twin-sweep.yml` has
fired twice and failed twice — `33627910027` (2026-09-02T12:04Z) and `33508119299` (2026-09-01) —
both on `FAIL: twin/forward-intel/v1/feed.json is not what the overlay renders`. The estate's gate
*does* catch the underlying red, via `driftwood/verify-twin-overlay.sh` (FAIL in run 21) — but the
beat labelled "5 · The twin plays a dated signal forward" would render green.
**Owned**, not orphan: ticket 64 says in terms "harden step 5 to assert a dated scheduled sweep
observation once twin-sweep first fires"; ticket 72 owns the re-render; REVIEW-2026-08-31 already
listed "step 5 grades file presence not the scheduled forecast" among its minors (line 87). New
here: both clock firings have now happened and both failed, so this is no longer a latent gap.
**Remedy:** the smallest honest fix is a two-line change to step 5 — after the artefact checks,
require the newest `forward-intel` render to be reproducible *and* a dated sweep observation to
exist; until then exit 3 naming ticket 72 rather than 0.

### F2 (major) — Step 3 has never happened; the PASS is a synthetic probe by construction

No `wargamer/*` branch exists on driftwood, tuppence or ludlow (`gh api repos/…/branches` on all
three). Today's real scheduled proposer on driftwood (`33626099181`, conclusion `success`) printed
`[]` after `note: ledger derived from 0 closed-unmerged proposal PR(s)`. tuppence and ludlow
`propose-tier` scheduled runs fail outright (`33633036907`, `33515059588`, `33518603510`).
`step3_band.py:181-190` constructs the crossing (`under = band * 0.5`, `over *= 1.02` until the
tier flips).
**Owned:** ticket 74 (open), which states the position accurately. **Not a defect in the script —
the script says what it is.** It is a shortfall against the destination sentence.
**Remedy:** ticket 74 as written; the residual has to move for real, or the band has to move.

### F3 (major) — Step 2's PASS line calls a synthetic bump "merged", and the one real bump moved no money

Two separable facts.

(a) The **real** event happened once and is well graded: driftwood PR #20, commit `ea1c8db`
authored by `github-actions[bot]`, `party.yaml` + `composed/` in one commit, human-merged;
`verify/renovate/verify-renovate-merged-feed-pr.sh` PASSes on run 21 reading the real merge
record. That is a genuine strength.

(b) That real bump **did not re-price**. `git show ea1c8db -- composed/evidence.json`:
`"old_price": 19558.549772440045` / `"new_price": 19558.549772440045`. The e2e step-2 PASS is
therefore about **tuppence**, whose Renovate PRs (#1, #2, #4, #10) are all closed unmerged and
whose real `party.yaml` still pins `v1`. The PASS line reads "a **merged** pin bump
(threat-register v1 -> v2) re-prices **tuppence's** prices[]". Nothing was merged in tuppence.

Note the internal inconsistency: `step2_reprice.py:200-204` is scrupulous about the *number* ("what
moved is the recorded pin, not the number — not a re-price, looking on") but not about the word
*merged*. Step 3 received exactly this correction on 2026-08-29; step 2 did not.
**Already owned by:** none for the wording. Ticket 61 is resolved and its DoD (the
`verify-renovate-merged-feed-pr` flip) is genuinely met.
**Remedy:** change step 2's PASS to the step-3 shape — "a SYNTHETIC pin bump (no such PR has been
merged on tuppence) …", and, separately, note in ticket 74 or a successor that the £ has not yet
moved on any real bump.

### F4 (major) — Step 6's Rekor half silently excludes `feeds`, and its PASS line asserts the opposite

`verify-e2e-step6-provenance.sh` part 3 selects a tag with
`git tag -l 'v*.*.*'`. `feeds` tags per feed: `threat-register/v1.0.0`, `threat-register/v2.0.0`
(`gh api repos/policy-as-versioned-feeds/feeds/tags`). That glob cannot match a prefixed tag —
verified: `git -C <fresh feeds clone> tag -l 'v*.*.*' | wc -l` → `0`. So `feeds` falls into the
`queued+=("$u")` branch and run 21's PASS line states:

> `ok   no signed tag yet, honestly queued for cut-release.yml: feeds`
> `PASS: … and feeds have no signed tag yet`

Both statements are false. `feeds` has two real, gitsign-signed tags. The consequence is not
cosmetic: **the one publisher using the per-feed tag scheme has never had a tag Rekor-verified by
step 6**, and the failure mode is a *silent under-count dressed as an honest queue* — the exact
class step 6's own 2026-08-28 comment ("`$verified`, not `$units` … 8 asserted against 6 actually
verified") was written to close, reappearing on the other side.
**Already owned by:** nothing I could find. `grep -rl "v\*\.\*\.\*" .scratch/ecosystem/issues/`
returns nothing; no ticket names it. **Orphan.**
**Remedy:** replace the glob with a per-unit tag-shape read (each unit already declares its tag
form to `feed_contract.py`'s `tag_forms(entry, version)`), or at minimum fall back to
`git tag -l '*/v*.*.*'` and verify the newest of each feed. A one-line fix; the false sentence is
the important part.

### F5 (major) — Step 4's red is an instrument fault, and step 4 has never passed on a citable run

driftwood's fact 2 is false in every sample with the same message: `the controller's verdict is
'false': v1.1.0: signature or certificate chain did not verify at tagger time 1787677714 …
certificate is not yet valid`. Tagger time 1787677714 = 2026-08-25T17:08:34Z. The **same tag**
verifies in step 6 with the real `gitsign` binary: `ok   driftwood v1.1.0: real cert subject
matches the anchored regexp, Rekor entry validated`. So the artefact is genuinely signed and the
in-cluster verifier is wrong about it. This is an **instrument fault**, and it alone is what keeps
driftwood's otherwise-complete step 4 red.
**Owned:** ticket 73 (open), which names the cause correctly.
**Remedy:** ticket 73. Worth recording plainly that when 73 lands, driftwood's step 4 goes green
with all five facts true — the estate fact is already there.

### F6 (major) — tuppence and ludlow have never had their composed set in force, and the fix has no owner

Every five-fact sample either adopter has ever appended has `fact_4` and `fact_5` false. Today's
tuppence **scheduled** sample (`33632084845`, on tuppence `origin/main`, i.e. after the round-2
sampler fix merged as PR #14):

```
fact_4 … False | 12 of 16 rendered objects are absent from the cluster and 0 are live but unequal
fact_5 … False | 16 of 16 rendered objects are in no Flux inventory
```

Ticket 60 (Status: **resolved**) diagnoses this precisely — the round-2 edit's second string
replace hit the wrong occurrence, so the kyverno wait stayed below the composed apply — and states
that "Round 3 (branch `ticket-60-wait-order` …) is committed and patched". **That branch exists on
no adopter remote**: `gh api repos/…/branches` lists `ticket-60-grade-the-lane-sample` and
`ticket-60-sampler-waits` on all three, and no `ticket-60-wait-order`. The hub's own HEAD commit
message (`7b92990`, "ticket 60: round-2 wait fix was mis-ordered; round 3 committed with asserted
order") confirms round 3 was authored but, by enact_guard's design, not pushed.
**Already owned by:** nothing open. `grep -rl "wait-order\|round 3" .scratch/ecosystem/issues/`
returns only ticket 60, which is resolved. **Orphan.**
**Remedy:** open a ticket for round 3 (or reopen 60), and get the three commits pushed and merged.
Until then two of the three adopters cannot satisfy the destination's "consuming".

### F7 (major) — ludlow's observation lane has never fired successfully on a clock

`gh run list --repo policy-as-versioned-ludlow/ludlow --workflow drift-sample.yml` returns exactly
three runs ever: `33558858820` (dispatch, success), `33556801679` (dispatch, success),
`33517601520` (**schedule, failure**, at step "install the pinned tools (binary + checksum, no
marketplace action)"). So every ludlow observation the estate holds was owner-triggered. Ticket
60's own honesty note already concedes this for the 2026-09-01 batch ("today's graded samples came
from workflow_dispatch firings"); what is new is that ludlow's *one* subsequent scheduled attempt
failed and it has produced nothing since.
**Already owned by:** partially — ticket 56 owns "the citable run can see whether the clocks ran";
no ticket owns ludlow's tool-install failure specifically.
**Remedy:** diagnose the pinned-tool install step in ludlow's `drift-sample.yml` (compare against
tuppence's, which succeeded today at 12:49Z), and fold it into ticket 56 or a new one.

### F8 (minor) — §5 bullet 1 is not literally satisfied: two `verify*.sh` are neither run nor excluded

`talk/verify-all.sh:45` globs `.estate-clone` and `verify` only.
`find . -name 'verify*.sh' -not -path './.estate-clone/*' -not -path './.git/*'` also returns
`./.scratch/multi-org-estate/verify-08-filter-repo-split.sh` and
`./.scratch/multi-org-estate/verify-09-repoint-flux-sources.sh`; neither is in
`talk/verify-exclusions.txt` (2 lines, both `.estate-clone` paths). §5 says the gate "fails if any
is neither run nor listed in a committed exclusions file with a reason". These are archival
scratch scripts, so the practical risk is nil — but the invariant as stated is false, and the same
glob would silently miss a *new* hub check written outside `verify/`.
**Already owned by:** none found. **Orphan, minor.**
**Remedy:** either glob the repo root (excluding `.git`/`.estate-clone` dupes) or add the two
paths to the exclusions file with a reason. The second is one line.

### F9 (minor) — Step 7 re-executes steps 1–6 with a 300 s timeout against the gate's 900 s

`verify-e2e-step7-honesty.sh:96` runs `out="$(timeout 300 bash "$s" 2>/dev/null)"`. So the table on
deck beat 7 is a **second, independent execution** of steps 1–6, not a read of the gate's grades:
it can disagree with the TRUTH tally if state changes between the two runs (all six steps run
twice per gate run), and a step whose wall-clock lands between 300 s and 900 s would be graded
`hung: no verdict inside 300s` → `UNGRADED` → step 7 FAILs while the gate PASSes that same step.
Today's headroom is large: run 21's SLOWEST 5 shows `verify-e2e-step7-honesty.sh` at 33 s for all
six, and the slowest script in the whole estate at 358 s. It is latent, not live.
**Already owned by:** none found. **Orphan, minor.**
**Remedy:** raise step 7's per-step timeout to `${VERIFY_TIMEOUT:-300}` so it tracks the gate, and
state in the README that the table is a re-run, not the gate's grades.

### F10 (minor) — Step 7's PASS line lists seven verdicts for six steps

`PASS: steps 1-6 each report one honest verdict (verdicts: PASS PASS PASS FAIL PASS PASS PASS)` —
the seventh is step 7's own. Cosmetic, but a reader counting reds on the deck will mis-attribute
the FAIL's position. **Orphan, minor.** One-word fix in the final `pass` call.

### F11 (minor) — the committed deck is stale by six beats, in the safe direction

`origin/main:talk/deck.md` records `status=SKIP` for beats 1–6 with reasons from a tool-less local
run ("python lacks jsonschema/pyyaml", "KinD cluster 'driftwood' absent"). A rebuild from run-21's
own captures gives `PASS PASS PASS FAIL PASS PASS`. `verify/demo/verify-demo.sh` correctly FAILs on
exactly this. So the estate's one presentation artefact **under-claims** — the failure direction to
prefer, and evidence the check bites. But anyone opening `talk/deck.md` today reads six
could-not-looks that are wrong.
**Owned:** ticket 66 (open). **Remedy:** ticket 66.

### F12 (minor, correction) — the `verify-schedules` capture anomaly is not one

See §3. Line 50 is the wrapper's composed verdict, identical by construction to line 8.

### F13 (minor, correction) — hub `truth.yml`'s failures are the honest red, not a cage violation

See §3. `gh run view 33616685427 --json jobs`: `the observation cage` = `success`;
`fail if the gate failed` = `failure`. Same shape on `33497493135` and `33557360933`.

### F14 (minor) — the citable run cannot see any clock; "on a clock" is asserted, not graded

Twelve `SKIP: …: GitHub unreachable (Command '['gh', 'auth', 'status']' returned non-zero exit
status 1.) -- cannot look at whether this clock ran inside its period` lines in the run-21
`verify-schedules` capture, covering every unit's clock and the hub's own `truth.yml`. This is
structural: the live half needs cross-org read on eight separate single-repo orgs, which a normal
Actions token cannot do.
**Owned:** ticket 56 (open). **Remedy:** ticket 56. Until it lands, no document may cite "on a
clock" as a graded fact — only as an inference from run ids embedded in lane samples.

### F15 (minor) — step 1's tag was cut by hand-dispatch, and has no GitHub Release

`ico` `cut-release` run `33406040611` (2026-08-31) was `workflow_dispatch`; there is no subsequent
`release` run and no GitHub Release for v3.0.0 (`gh release list --repo policy-as-versioned-ico/ico`
shows only v1.0.0, 2026-08-21). NORTH-STAR §4.1 asks only that the feed be "signed and tagged", and
§3.5 requires a human at the enactment step, so the dispatch is *correct*. The missing Release is a
loose end that Renovate's own release-notes link in driftwood PR #17 points at
(`…/feeds/releases/tag/threat-re…`), i.e. adopters' bump PRs link to pages that do not exist.
**Owned:** the publishers reader raised the same for nist v1.1.0. I found no ticket. **Minor.**

---

## 5. Strengths, stated as plainly as the faults

1. **Step 6 is genuinely, cryptographically real.** Seven tags verified in the citable run by the
   real `gitsign` binary against real Fulcio certs with `Validated Rekor entry: true`, each against
   a regexp derived from that unit's *own* git remote (never a list in the script), with five
   negative shapes per unit — foreign org, foreign workflow, scheme prefix, suffix attack, and a
   non-`main` branch ref.
2. **The estate's Renovate step happened, once, for real, and is graded from the real record.**
   `verify-renovate-merged-feed-pr.sh` reads driftwood's actual `main` for a merge from a
   `renovate/` branch with bot-authored commits and a human merger, and PASSes citing PR #20. It
   is a check that cannot be satisfied by a simulation, which is exactly what ticket 61's DoD
   demanded.
3. **The lane-sample grader is built to refuse.** `five-facts.py:627-654` refuses when the three
   falsifiers are not still declared, refuses a stale sample, and (via `sample_provenance`) refuses
   a hand-typed or unsigned one — closing a documented real incident where three typed lines graded
   PASS.
4. **Step 3's PASS line was corrected against its own reader.** The 2026-08-29 note in
   `step3_band.py:262-269` is the estate at its best: it names the wording a deck reader would have
   misread, says what the probe actually is, and keeps the property under test.
5. **The proposer correctly proposes nothing.** Today's real scheduled run returned `[]` because no
   residual crossed a band. A machine that stays quiet when it should is worth as much as one that
   fires.
6. **Step 7's grading bites, and proves it every run.** Its selfcheck plants a hedged PASS, an
   exit/last-line mismatch, a non-conforming step and a mid-transcript confession, requires all four
   caught and an honest SKIP and FAIL through — and the no-argument path runs it first, closing the
   2026-08-28 finding that nothing ever invoked it.
7. **A red step 4 and a green step 7 in the same TRUTH line are both correct.** Step 7 grades
   reporting, not results, and says so in three places. This is a genuinely well-drawn seam.
8. **The deck check caught the deck.** run 21's `verify-demo` FAIL is the mechanism working: the
   committed artefact drifted from the surface and the surface said so.
9. **Nothing in this dimension is fabricated.** I looked for a green that could not look and found
   none; every PASS I traced rests on an observation. The two false sentences I did find (F4's
   "feeds have no signed tag yet"; F3's "merged") both understate or mis-frame rather than invent.

---

## 6. Fitness verdict

Not fit yet for the purpose the map's Destination states, and the gap is honestly visible in the
estate's own number rather than hidden by it. Of the seven §4 steps, **two are real end to end**
(1 and 6), **one is real once but only half** (2: the pin moved, the money did not), **one is real
for one adopter and blocked by an instrument fault** (4), **two have never happened at all** (3,
and 5's "on its schedule"), and **one is a reporting roll-up that correctly refuses to grade the
others' results** (7). The destination's "once, on a clock, with three adopters consuming" fails on
three independent counts and is, today, not even a gradeable proposition, because the gate cannot
see its own clocks. What *is* fit is the instrument: the gate finds these gaps, names them, and has
never — in the seven steps I traced — turned an absence into a pass. Four things would make this
dimension fit: push round 3 so tuppence and ludlow reconcile (F6, no owner); land ticket 73 so
driftwood's fifth fact turns (F5); make one residual really cross a band (ticket 74); and fix the
twin's re-render so its clock succeeds and step 5 asserts it (tickets 72 and 64). Three of the four
are already charted; the first is not, and it is the one nearest to done.
