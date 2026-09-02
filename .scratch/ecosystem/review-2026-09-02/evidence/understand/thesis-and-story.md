# Thesis and story — reading map

Scope covered exactly as assigned: `research/01,02,03,20,22`, `docs/PRD.md`, `docs/HISTORY.md`,
`docs/SHOW-AND-TELL.md`, `docs/ARCHIVE.md`, `README.md`, `.scratch/talk-spec/the-whole-model.md`,
`.scratch/talk-spec/pitch-v6/plan.md`, `.scratch/demo-feedback/NOTES.md` (+ its sibling
`CONCLUSIONS.md`, read for extra context on how NOTES.md items were resolved). I additionally
opened `.scratch/talk-spec/pitch/script.md`, `pitch-v2/script.md`, `pitch-v4/plan.md` and
`.scratch/talk-spec/spec.md` because they are the only place in this scope where the owner's own
purpose/audience words are quoted (task item 4) — flagged inline, not silently substituted for the
assigned set. I did **not** read NORTH-STAR.md, the ADRs beyond titles/greps, or the drift-review
folder — out of the assigned scope; §5 (open questions) names what that leaves unverified.

All evidence below is `path:line` or an exact quoted string from the file named. Nothing here is
inferred beyond what the cited line says.

---

## 1. The thesis, itemised as testable claims

### 1a. As stated in 2022 (the talk + the original Medium post)

Source: `research/03-blogs-thesis.md` (dossier built from three primary sources: the 2022 Medium
post, the talk at talks.cns.me, and the later "mea culpa" blog — see file header, lines 1–18).

1. **Policy is a versioned software dependency, not a gate.** "Treat policy as a versioned
   software dependency, not as a gate." (`research/03-blogs-thesis.md:23`, framing the thesis;
   the actual "not a gate" formulation is the *later*, mea-culpa-era framing — see 1b).
2. **Policies fail silently in production without the dependency model** — a violating deploy
   breaks main/master without the developer knowing unless they watch event logs
   (`research/03-blogs-thesis.md:30-31`).
3. **Policies get semver numbers** — major/minor/patch, with the explicit caveat "Don't be fooled
   by the decimal points, they're not real (1.20.0 is greater than 1.3.0)"
   (`research/03-blogs-thesis.md:34-39`).
4. **The runtime must support ≥3 semver policy versions simultaneously**, to allow "transitionary
   periods for old policy versions to be retired" (`research/03-blogs-thesis.md:40-41`) — this is
   the literal source of the "≥3 coexisting versions" claim named in the task.
5. **The seven "-able" properties**, verbatim from the talk's "(easily:)" slide
   (`research/03-blogs-thesis.md:53-70`): **visible**, **communicable**, **consumable**,
   **testable**, **usable**, **updatable**, **measurable**. Each is testable independently (see
   the table at that citation for what each means).
6. **The central one-liner**: "Purposeless policy is potentially practically pointless policy."
   (`research/03-blogs-thesis.md:75`) — policy must carry its risk/rationale so debate happens in
   PRs rather than exemption requests (`research/03-blogs-thesis.md:79-88`).
7. **Measurable, concretely, in 2022 terms**: "Renovate … has generated over 1,222 automated pull
   requests" and "When the CIO wants to know how many teams are compliant, the answer is a GitHub
   PR search away." (`research/03-blogs-thesis.md:161-163`) — this is the exact source of the
   "measurable-by-PR-search" claim named in the task. Note precisely what it measures: PR
   *acceptance*, not workload compliance (made explicit later — see §3).

### 1b. The mea-culpa revision (later, refined position) — what changed and what stayed

Source: `research/03-blogs-thesis.md §4` (lines 92–164).

1. **Attribution, not technical, first-order confession**: the idea traces to Michael
   Brunton-Spall's 2016 GOTO Amsterdam talk; CNS "forgot it was his" after six years and 21
   conferences without citing it (`research/03-blogs-thesis.md:99-107`).
2. **Not everything is a dependency — the lane-keeping vs. locked-door split** (the task's
   "lane-keeping vs. locked-door split" claim, verbatim sourced): quoting Gregor Hohpe, "A
   guardrail stops you at the point of failure. Lane keeping assist nudges you continuously…"
   (`research/03-blogs-thesis.md:113-120`). The concession: "Some policies belong at the gate.
   Access control. Data protection. Cryptographic key management" — "I want a locked door."
   (`research/03-blogs-thesis.md:122-129`). The refined split: ~80% of the enterprise policy
   surface (labelling, tagging, config standards, operational metadata) should be
   dependency/lane-keeping; a catastrophic minority (access control, data classification, crypto)
   is gate/locked-door (`research/03-blogs-thesis.md:130-139`). This is a testable claim: **a
   system that is gate-only is explicitly named as "exactly the mistake v1 over-corrected"**
   (`research/03-blogs-thesis.md:206`, and repeated verbatim in `docs/PRD.md:37-38`).
3. **The human governance layer** — "the thing I missed was the human part." Versioning solves
   distribution for engineers, not governance. GDS-Way-style review: "Every accepted practice
   carries a date. Every practice must be regularly reviewed… it gets removed. Not archived. Not
   deprecated. Removed." (`research/03-blogs-thesis.md:141-150`).
4. **The last mile** — versioning bridges engineers, not non-technical consumers (the talk's "the
   Cleaner"): "the last mile to non-technical consumers … is a different problem that the
   versioning alone does not solve." (`research/03-blogs-thesis.md:153-158`).
5. **What stayed unchanged**: semver mechanics, the seven "-ables", the ≥3-version runtime
   requirement, the "purposeless policy" one-liner — none of these are revised by the mea culpa;
   only the *scope* of what should be a dependency versus a gate, plus the two additions (human
   governance, last mile), are new (`research/03-blogs-thesis.md §7`, lines 201–216, "Design
   implications" — explicit that the mea culpa *adds* constraints rather than replacing the
   original seven).

### 1c. How the PRD claims to honour both

`docs/PRD.md:31-49` states explicitly: "The refined thesis (the 'mea culpa'), which this PRD
honours over the original talk" — followed by the same four bullets (lane-keeping/gate, carry the
why, human-governance layer, last mile) verbatim-paraphrased from `research/03`. `docs/PRD.md:96`
carries the constraint into a binding principle table row: "Proportionality — lane-keeping for the
~80%, a hard gate only for catastrophic boundaries | thesis". `docs/PRD.md:103-115` reproduces the
seven "-ables" as a literal acceptance-criteria table with named mechanisms and demonstrable
evidence per row — i.e. the PRD treats §1a/1b's claims as machine-checkable acceptance criteria,
not just narrative framing.

---

## 2. Dated timeline: what each epic promised, and what it declared done

Built from `docs/HISTORY.md` (the only file in scope with an explicit epic-by-epic narrative) and
cross-referenced against `docs/PRD.md`, `docs/ARCHIVE.md`, `README.md`, and
`.scratch/talk-spec/pitch-v6/plan.md`. Where HISTORY.md gives a date I quote it; where it doesn't,
I say so rather than guess.

| Epic | What it promised (stated goal) | What it declared done | Source |
|---|---|---|---|
| **Faithful floor** (Episode 1) | "proved the mechanism itself: one Kyverno-engine cluster, multiple policy versions coexisting side by side, adopted via a reviewed Renovate PR, retired without a flag day." 26 tickets. | "By the end of this epic: three policy versions live simultaneously on one cluster, an orphan guard making the gate tier a locked door … a real Renovate customManager … a CIO dashboard reading live PolicyReport + OSCAL data — proof the mechanism itself works." | `docs/HISTORY.md:21-63` |
| **Show+tell / "cardboard cutout"** (Episode 2) | A narrated demo walkthrough surfaced that "the *estate* around the mechanism was a cardboard cutout" — 3 identical nginx pods in one monorepo, no real dependency trees/teams/cadences; "the trust chain had one confirmed hole." | 16 pieces of raw feedback captured (`.scratch/demo-feedback/NOTES.md`), then grilled into `spec.md` for the next epic. No "done" claim here — this episode is explicitly the *problem-finding* one. | `docs/HISTORY.md:65-75` |
| **Real estate** (Episode 3) | "making the estate real" — turn 3 identical nginx pods into 5 real teams/repos with real dependency staleness; componentise pr-gate/c2p-collector/handbook-generator/readiness-collector into their own pinned repos. 15 tickets, 5 passes. | First pass: "all fifteen tickets marked done." **Second wave ("turning 'done' into 'provably done'")**: an adversarial multi-agent audit found 5 real gaps behind "done" status; a follow-up audit found more. The most significant: `clusters/cluster1/policy-versions.yaml`/`apps.yaml` were never wired into continuous Flux reconciliation — one-shot `kubectl apply`'d by `up.sh` and never touched again. Fixed via `fleet#55` (cluster-state Kustomization) and re-proven via `fleet#56`/`#57`. Four other real gaps (Renovate manager enablement, 3 more repos missing renovate.json, "skip already-actioned" checkbox with no code behind it, 8/9 repos missing forge tag-immutability) — all fixed with linked PRs. | `docs/HISTORY.md:76-185` |
| **Sunset governance addendum** (still Episode 3, later pass) | ADR-0010's "on the date itself, a machine opens a retirement PR" was claimed as built. | A later adversarial pass found `sunset-escalator.sh`'s logic was real and hand-demonstrated, but **nothing in the estate ever invoked it** — "aspirational, not automated." Fixed with a real daily cron GH Actions workflow (`fleet#58`). | `docs/HISTORY.md:172-184` |
| **Estate/eco-system re-split** (dated in ARCHIVE.md) | The monorepo hub (`policy/`, `fleet/`, `docs/`, `research/`, `spikes/`) was to become "research-only," superseded by a six-org estate. Checklist item: "New estate proven … pre-split: `estate/talk/verify-all.sh` 25/25 offline beats PASS, 0 fail (3 expected live-cluster skips), commit `ef84d1636647a...`, **2026-07-31**." | Two of four checklist boxes unchecked as of the file's own text: GitHub-repo archiving ("human/GitHub-admin step, cannot be done unattended") and the README banner — both still `[ ]`. **Superseded 2026-08-28** (see next row) before those two boxes were ever closed. | `docs/ARCHIVE.md:29-64` |
| **North-star reversal of "research-only"** | N/A (a correction, not a new promise) | `docs/ARCHIVE.md:3-8` (banner, undated internally but says "Superseded in part, 2026-08-28"): "The ratified north star §7 reverses the 'research-only' framing below. This hub is not archived and is not research-only. It is the eco-system's own repository." I.e. the archive-the-hub plan documented above was itself reversed five weeks after the 2026-07-31 proof date, before its own checklist finished. | `docs/ARCHIVE.md:3-8` |
| **Multi-org split (mo-12)** | N/A — an infrastructure move noted retroactively. | "Moved, mo-12 (2026-08-21): this file used to live at `estate/ARCHIVE.md`… That shape is gone: the six units … are now real, separate `policy-as-versioned-*` GitHub repos … the cross-cutting `verify/` + `talk/` moved to this hub repo's own root." | `docs/ARCHIVE.md:16-22` |
| **Policy-composition** (named in task, not detailed in scope) | Not covered by any file in this agent's assigned scope — `docs/HISTORY.md` (as read) stops before it. The user's own memory file (system reminder, not a project doc) names "Policy-composition ticket 18 done" and "Truth surface ticket 03" as later work; I did not verify these against primary sources — out of scope. | — flagged as **not covered**, see §5. |
| **Talk-spec / pitch epic** | `.scratch/talk-spec/pitch-v6/plan.md:1-15`: "Charted 2026-08-25. Cold start. Every number, capture and screenshot in this deck comes from a command run on 2026-08-25… Subject: both north stars — the six-org governance estate *and* the organisational digital twin." Explicit honesty commitment: "Three verify beats are red on the day of recording and the deck says so… A demo that only shows green has demonstrated nothing." (`pitch-v6/plan.md:22-26`) | Declared delivered at the foot of the same file: "**81 segments · 3,872 spoken words · 14 acts · 19 minutes 58 seconds of audio**… Video: `pitch-v6.mp4`, 20 minutes 8 seconds… Spot check: six frames… each compared against its rendered slide by structural similarity. All six match at 0.99 or better. No drift." (`pitch-v6/plan.md:150-158`). But the same file's "What is red on the day of recording" table (below) lists **8 real, reproducible reds** it ships rather than hides — so "done" here explicitly includes shipping known-red state, not claiming all-green. | `.scratch/talk-spec/pitch-v6/plan.md:1-26, 111-158` |
| **"Ecosystem" epic / current state** | Not directly detailed by any file in my assigned scope (`.scratch/ecosystem/` was named in the task's system prompt as a key document but is outside my reading list). | Not verified by me — flagged in §5. | — |

**Cross-cutting note on "declared done" language.** `docs/HISTORY.md` itself narrates a repeated
pattern across at least two epics — a first "done" claim, followed by a dedicated adversarial-audit
pass that finds real gaps behind it, followed by fixes recorded with PR links. This pattern is
explicit at `docs/HISTORY.md:118-119` ("A second wave: turning 'done' into 'provably done.'") and
recurs for the sunset-escalator gap (`docs/HISTORY.md:177-184`). The same document also records the
project **catching itself mid-narrative**: a draft of HISTORY.md itself over-corrected one claim
into a new, broader false one, caught by a *second* adversarial pass (`docs/HISTORY.md:172-176`).

---

## 3. Every place a later document says an earlier claim was wrong

This section is the task's item 3. I list each correction with the earlier claim, what said it was
wrong, and the fix, all with citations. I did not include corrections that are internal to a single
document's own narration of "we found X and fixed it live" unless a *later*, separate document
revises what an *earlier* document had asserted as settled.

1. **The Kyverno version-selector mechanism itself (webhook flattening).**
   Earlier design (implicit in `research/01`/`02`'s dossier of the 2022 orgs, and carried forward
   into `research/20`'s "faithful mapping" §1.6, which explicitly recommends keeping the
   `match.selector`/`objectSelector` self-scoping "verbatim," e.g.
   `research/20-synthesis-faithful-flux-mapping.md:97`) assumed a per-policy `objectSelector` would
   scope each version independently, same as the 2022 Kyverno `ClusterPolicy` behaviour.
   `docs/HISTORY.md:27-34` states this "looked right in isolation and was wrong in production:
   Kyverno flattens every installed `ValidatingPolicy`'s `objectSelector` onto one shared
   Kubernetes `ValidatingWebhookConfiguration` — only the most-recently-reconciled version's
   selector survived, silently." Fixed by moving version-scoping into a `matchConditions` CEL
   expression evaluated inside Kyverno instead (commit `policy@1466fdc`, cited at
   `docs/HISTORY.md:33-34`). `docs/PRD.md:257-261` records the corrected design as the shipped
   mechanism and explicitly names the discovery: "found live in issue 08."

2. **Two "correct" signed tags that Flux could not resolve — and a wrong first diagnosis of why.**
   `docs/HISTORY.md:36-57`: tags `v1.0.2`/`v2.0.2` were "cut, signed, and correct" yet Flux's
   `source-controller` (go-git) refused to resolve them. **The first fix attempt's own commit
   message misdiagnosed the cause as SSH-signed commits** — a real but secondary difference.
   Root cause (confirmed live, not from docs) was that the commits were unreachable from any
   branch (a `git worktree` artefact) — a documented go-git shallow-fetch-by-tag limitation
   (`fluxcd/source-controller#1166`). The wrong diagnosis was corrected **in the open**, in a
   follow-up PR (`fleet#11`, "Correct root-cause comment: branch reachability, not (only) SSH
   signing") rather than rewritten quietly — `docs/HISTORY.md:49-57` is explicit that the PR's own
   title concedes SSH signing was "a real, secondary factor," not fabricating a single clean cause.

3. **"Never actually merged" claim about a retirement PR — overcorrected, then re-corrected.**
   `docs/HISTORY.md:132-138`: ticket 09's claim that "merging a retirement PR retires the version"
   had never been tested against a continuously-reconciling cluster, because
   `clusters/cluster1/*.yaml` wasn't wired into Flux at the time `fleet#7` merged. The document
   then flags its **own drafting error**: "A second adversarial pass caught an earlier draft of
   this very paragraph repeating the wrong, broader claim — 'never actually merged' — even after
   ticket 09's own file had already corrected it; fixed here to match." This is a documented
   instance of a correction itself needing correction, recorded rather than silently fixed.

4. **A checkbox-wording claim in a prior "fix" was itself wrong.**
   `docs/HISTORY.md:162-166`: "A prior fix's own 'correction' claiming two governance-issue
   checkbox templates use identical wording was itself wrong — re-checked directly against both
   scripts, only one of the three lines actually matches, and the other two don't just differ in
   wording, they swap which answer means what." This is a correction of a correction, both
   documented.

5. **"`ledger` will be worst-in-class on both staleness axes" — half right, half wrong once
   measured.**
   `docs/HISTORY.md:166-171`: ticket 12's headline claim about the deliberately-old-log4j app
   `ledger` "turned out, once its real vulnerability scan finally landed, to be true on the
   policy-version axis and **false** on the vulnerability axis — `ledger` has fewer live CVEs (22)
   than either `reports` (188) or `storefront` (146). Left as the genuinely interesting, slightly
   inconvenient finding it is, not reshaped to fit the original thesis." This exact reversal is
   re-confirmed independently in `docs/SHOW-AND-TELL.md:147-149`: "the live trivy scan shows the
   real CVE counts (honestly: `ledger` is *not* worst on CVEs — `reports`/`storefront` are higher;
   kept as the genuinely-interesting finding it is)."

6. **HISTORY.md's own date-range claim over-corrected into a broader false claim.**
   `docs/HISTORY.md:172-176`: a "day-old, not year-old" correction about `policy#7`'s onboarding PR
   (opened 2026-07-16, merged 2026-07-17, "genuinely a day old, not the 'year-old' an earlier draft
   of this line claimed") itself "over-corrected into a broader false claim — this document briefly
   asserted the *entire project's* history spans 2026-07-14 to 2026-07-18, when only the real-estate
   epic does; the hub repo's actual first commit is 2026-06-06, five weeks earlier." Also in the same
   passage: "Ticket 16's ADR-0005 citation for `flux-operator`'s chart version pin was wrong — the
   pin lives in `fleet`'s own `up.sh`, not the ADR, which never mentions a version number."

7. **The "3-KinD-clusters-under-load" explanation for the pitch-v6 reds was withdrawn.**
   `.scratch/talk-spec/pitch-v6/plan.md:119-124`: eight reds are listed as "real, reproducible"
   (coexistence/graded/posture layers, identity/reach, access plane). The closing line: "The
   original attribution ('three KinD clusters did not finish converging on a machine already
   running someone else's scan at load two hundred') was written on 2026-08-25 without a second
   run and is withdrawn (GAPS 2.11)." `docs/HISTORY.md:219-221` corroborates from the other side of
   the same event: "The pitch-v6 reds that were attributed to 'load two hundred' are
   re-attributed in `.scratch/talk-spec/pitch-v6/plan.md` to what the 2026-08-27 review actually
   observed."

8. **The Docker-not-running post-mortem — an entire period of "working" claims retracted.**
   `docs/HISTORY.md:204-230` ("Post-mortem: 2026-08-25, Docker was not running") records that on
   2026-08-25 the owner discovered Docker was not running on the machine that had, for days, been
   reporting live deployments as working, quoting the owner verbatim: *"just occured to me docker
   isn't running so you've presumably not been deploying anything you've been doing?! how on earth
   are you saying its working!?!!"* The document states plainly: "No KinD cluster can exist without
   Docker, so every 'reconciled', 'installed live' and 'pruned live' claim in that period was a
   claim nobody had observed." Root cause named: verify scripts converted absence into a false
   positive (`verify-retirement.sh` printed "retirement pruned it live" for a Kustomization it had
   never seen; `talk/verify-all.sh` reported live-reconcile beats as SKIP on *any* non-zero exit,
   making a dead substrate indistinguishable from a real regression). Fixed by "eco-system ticket
   03, 2026-08-28": every live-claiming script now asserts its substrate first and has exactly
   three outcomes (observed-true / observed-false / could-not-look = SKIP with a reason and exit
   3); `talk/verify-all.sh` discovers scripts by glob and fails on any unaccounted-for script.

9. **`docs/ARCHIVE.md`'s own plan superseded by the north star.**
   Already covered in §2's timeline row, repeated here because it is a direct "an earlier document's
   plan was wrong (or overtaken)" case: `docs/ARCHIVE.md:3-8` states the ratified north star (dated
   2026-08-27 per the banner's "Superseded in part, 2026-08-28") "reverses the 'research-only'
   framing below," i.e. the entire premise of the archive plan documented in the rest of that file.

10. **Pitch-v6's own adversarial-review table — eleven factual claims corrected before publication.**
    `.scratch/talk-spec/pitch-v6/plan.md:64-88` is itself an in-document ledger of eleven specific
    factual overclaims caught by a same-day adversarial review and fixed before the deck shipped —
    e.g. "'fifty-one verify scripts, twenty-five wired' had no capture" → corrected to "fifty-six
    and twenty-eight" (with a capture cited); "'three policy versions, live at once' — the capture
    is an offline render proof, and the live beat is red" → retitled to what the capture actually
    proves; "'every artefact carries a signed sidecar' — every twin capture reads `unsigned`" →
    narration changed to say so. I list this as one item rather than eleven because they are all
    one review pass in one document, but flag that each row is independently a "claim → shown wrong
    → fixed" instance, all in scope of the task's item 3.

---

## 4. The owner's own words about purpose and audience, dated

The nine files in my primary assigned scope contain almost no first-person owner quotes about
*purpose/audience* (as opposed to thesis content) — the one exception is the Docker post-mortem
quote in item 8 above, which is about honesty/observability, not purpose/audience. To answer this
task item I opened four adjacent files under `.scratch/talk-spec/` that are the only place *in the
whole talk-spec tree* where the owner's purpose/audience is stated directly, and I'm flagging that
extension explicitly rather than passing it off as in-scope-by-default.

1. **Thesis-defence framing, 2022, talk vs. blog** — not a direct owner quote about audience, but
   `research/03-blogs-thesis.md:12-18` documents the sourcing split itself: the talk
   (`talks.cns.me/PolicyAsVersionedCode.html`) is aimed at a live conference audience (the
   seven "-ables" and the "purposeless policy" line live only there), while the Medium post is "the
   technical how-to" for engineers reading async, and the mea-culpa blog is explicitly a *public
   correction* of the talk's own overreach — i.e. three different audiences (conference,
   engineering blog, public accountability) by design, stated by the dossier's own framing note.

2. **Internal funding pitch to ControlPlane — audience is explicit and dated.**
   `.scratch/talk-spec/pitch/script.md:1-4`: header states **"To: the funder (ControlPlane)"**,
   angle "vision hook → ControlPlane payoff → the ask," close "fund the full build to a flagship
   talk." Quoted lines (owner's own scripted words, meant to be spoken in first person):
   - S18: *"So what do you actually get for the spend? A flagship conference talk that tours the
     circuit. A reusable demonstration estate our teams can put in front of literally any
     prospect. And clear ownership of a narrative that nobody else in this entire market is
     telling yet."* (`.scratch/talk-spec/pitch/script.md:64`, mirrored in
     `pitch/generate.py:34` and `pitch/slides.py:373`)
   - S19: *"Here is my commitment. Nothing is a nice-to-have. Six orgs, built fresh, fully live…
     I build the whole thing."* (`.scratch/talk-spec/pitch/script.md:66` region — S19 in the same
     file)
   - S20 (the ask): *"So here's the ask. Fund it. End to end, through to the flagship talk. Give
     me the runway, and I'll hand you the estate that proves governance can finally be
     proportionate, honest, and alive."*
   Dating: this file itself carries no date, but it precedes pitch-v2, whose header says "Revised
   per adversarial review (**2026-07-31**)" (`.scratch/talk-spec/pitch-v2/script.md:4`) — so pitch
   v1 is dated no later than 2026-07-31, likely the same window as the `1718b6a` commit
   (`git log` shows `1718b6a … 2026-07-31 Add pitch v2 — 6:40 + tight 4:50 Pecha Kucha pitch to the
   ControlPlane CEO`, confirmed by `git log --format='%H %ad %s' --date=short -1 1718b6a`).

3. **Pitch v2, dated 2026-07-31, addressed to "the CEO of ControlPlane (the funder)."**
   `.scratch/talk-spec/pitch-v2/script.md:1-8`: explicit self-correction note in the header —
   *"Revised per adversarial review (2026-07-31): … removed a fabricated '8×' statistic; recast the
   six-orgs slide from *already built* to *what the funding builds* (no overclaim — demonstrable-
   core is live, breach-cost + balance-sheet are narrated)…"* — the owner's own account of
   tightening an audience-facing claim to stop overclaiming, addressed to a named internal
   stakeholder (ControlPlane's CEO), dated. Quoted purpose line: S18 (paralleling pitch v1) *"For
   the spend, you get three things that compound. A flagship talk that tours every conference. A
   demo estate our teams put in front of any prospect. And ownership of a story no competitor in
   this market is telling yet."* (`.scratch/talk-spec/pitch-v2/slides.py:384` and
   `pitch-v2/script.md:66` region).

4. **Pitch v4, dated 2026-08-19, same audience, restated verification discipline.**
   `.scratch/talk-spec/pitch-v4/plan.md:1-7`: **"To: Andy, CEO of Control Plane, the funder. Ask:
   back the next stretch of runway."** Every fact in that script is stated as "verified live today
   (2026-08-19), not carried forward from any prior draft" — an explicit, dated commitment to
   re-verification rather than reuse of prior claims, addressed to a named person by role.

5. **Pitch v6, dated 2026-08-25, subject widened by the owner's own confirmed decision.**
   `.scratch/talk-spec/pitch-v6/plan.md:10-11`: **"Subject: both north stars — the six-org
   governance estate *and* the organisational digital twin. Confirmed by the owner, 2026-08-25."**
   This is the only place in the assigned+adjacent scope where a scope decision is attributed
   directly to "the owner" with a date, rather than narrated as an agent's own choice. The same
   file's honesty commitment (`pitch-v6/plan.md:22-26`) is presented as a house rule rather than a
   quote, but reads as owner-endorsed given it governs what a funder-facing deck is allowed to
   claim: *"The estate's own standing preference is honesty over green… A demo that only shows
   green has demonstrated nothing."*

6. **"Talk audience" as stated in the spec that the current build serves.**
   `.scratch/talk-spec/spec.md:11-13`: **"A principal engineer or a security/risk leader watching a
   governance talk is shown GitOps plumbing and told to trust that it makes them 'compliant'…"** —
   the explicit target audience for the live conference talk (principal engineers, security/risk
   leaders), as opposed to the ControlPlane-internal funder audience of the pitch decks above.
   Corroborated by `.scratch/talk-spec/the-whole-model.md:258-260`: **"Locked (2026-07-23): a
   ~35–40 min conference talk that tours — principal-engineers + leaders."**

**What I could not find in scope.** No file I read (assigned or adjacent) quotes the owner
addressing an actual external client or a live thesis-defence audience in first person with a date
— the closest is the internal ControlPlane-funder pitches (items 2–5) and the talk's *stated*
target audience (item 6), not a transcript or quote *from* a client-facing or conference session.
`docs/HISTORY.md`'s Docker post-mortem quote (§3 item 8) is the one verbatim owner quote in the
core-scope files, and it is about observability/honesty, not purpose/audience.

---

## 5. Notable facts a reviewer must not miss (summary pointers, full detail above)

- The seven "-ables," the ≥3-coexisting-version requirement, and the "measurable = PR search away"
  claim are all sourced to **the talk**, not the Medium post — `research/03-blogs-thesis.md:12-18`
  is explicit about this attribution split, and it matters because later documents (e.g.
  `docs/PRD.md`) cite "the talk" and "the blog (mea culpa)" as distinct, separately-dated sources.
- The mea culpa **adds** two claims (human-governance layer, last mile) and **narrows** one (not
  all policy is a dependency — a minority is a gate) but does not revise the seven "-ables" or the
  semver/≥3-version mechanics.
- `docs/PRD.md` explicitly frames itself as honouring the *mea-culpa* thesis "over the original
  talk" (`docs/PRD.md:31`) — i.e. the current build's own stated contract is with the revised
  thesis, not the 2022 one.
- The webhook-flattening bug (§3.1) is the single most architecturally significant "an earlier
  claim was wrong" finding: the faithful-mapping synthesis (`research/20`) recommended keeping the
  2022 selector mechanism "verbatim," and that recommendation itself turned out to be unsafe on
  the actual Kyverno CEL engine — found only by building it, not by the research phase.
  `research/20-synthesis-faithful-flux-mapping.md` predates this discovery and was never itself
  corrected in place (it is dated to the synthesis phase, before the faithful-floor build); the
  correction lives only in `docs/HISTORY.md` and `docs/PRD.md`.
  `docs/PRD.md` §6.4 (lines 249-261) documents the shipped/corrected mechanism.
- The Docker post-mortem (§3 item 8) is the largest single retraction in scope: an unbounded period
  of "reconciled/installed/pruned live" claims across possibly multiple demo sessions was
  invalidated at once, and the fix was a repo-wide rule about what counts as an observation, not a
  patch to one script.
- `docs/ARCHIVE.md` is a live example of a document whose own stated plan was reversed by a later
  ratification (the north star, 2026-08-27/28) before its own checklist was completed — two of four
  checklist items are still unchecked in the file's own text, and the file's banner says not to
  execute the checklist below it.
- The task's "policy-composition" epic and the "ecosystem" epic (both named in the task's own list
  of six epics to timeline) are **not covered** by any file in my assigned reading list — I did not
  fabricate timeline entries for them. `docs/HISTORY.md` as given to me stops at the real-estate
  epic's second wave and the Docker post-mortem; it does not narrate policy-composition or the
  ecosystem epic at all. If those are required for the audit, a separate pass over
  `.scratch/ecosystem/` and any policy-composition-specific docs (not in my scope) is needed.
- I did not read NORTH-STAR.md itself, despite it being referenced repeatedly by every in-scope
  document (`docs/PRD.md:7`, `README.md:13`, `docs/ARCHIVE.md:3`) as the ratifying document for the
  "research-only" reversal and as "the north star" the PRD's non-goals defer to. Anyone using this
  map to audit the "ratified 2026-08-27" claim should read NORTH-STAR.md directly — it is outside
  my assigned scope.

---

## Open questions

1. Where (which file, if any) does the project ever reconcile the **synthesis-phase recommendation**
   (`research/20`: keep the 2022 selector mechanism "verbatim") with the **build-phase discovery**
   that this was unsafe (`docs/HISTORY.md`, `docs/PRD.md §6.4`)? I found the correction but not a
   place where `research/20` itself is marked superseded/corrected — it reads, as filed, as if still
   current advice.
2. `research/22-prd-decision-register.md` frames several decisions (D1.1 OCI vs git tags, D1.2
   pinned vs range, E1 ClusterPolicy vs ValidatingPolicy) as open "grill hard" questions with
   recommendations. `docs/PRD.md` §6 shows the decisions as settled (signed git tags, pinned
   everywhere, CEL ValidatingPolicy). Is there a document recording the actual grilling session's
   resolution of D1.1–D1.3/E1 with the owner's reasoning, or did the PRD simply adopt the
   register's own "recommended" defaults without a recorded grill? Not answerable from files in my
   scope.
3. The task asks for the ">=3 coexisting versions" claim's history — I traced its 2022 origin
   (`research/03:40-41`) and its faithful-floor delivery claim ("three policy versions live
   simultaneously," `docs/HISTORY.md:61`) and its show-and-tell demo claim (three GitRepository
   objects, `docs/SHOW-AND-TELL.md:26-46`). I did not find, in scope, any later document stating
   this claim was ever *wrong* or *unverified* — unlike most other claims in §3, ≥3-coexisting-
   versions appears to have survived every adversarial pass covered by my reading. Worth an
   auditor double-checking this against `.scratch/ecosystem/` material I did not read, since its
   clean survival record is itself slightly conspicuous next to how much else got walked back.
4. Item 4's coverage of "clients" and "thesis defence" audiences came up empty in my scope. Is there
   a transcript, recording, or notes file (perhaps under a `research/` or `.scratch/` path I wasn't
   pointed to) of an actual external client conversation or a real thesis-defence Q&A, as opposed
   to internal ControlPlane-funder pitches and the talk's *stated* intended audience? If such a
   source exists it should supersede my item-4 answer.
