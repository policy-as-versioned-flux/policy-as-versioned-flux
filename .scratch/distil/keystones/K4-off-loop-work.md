# K4: is the off-loop work really off the loop, and who asked for it?

Refuter's working, 2026-11-14. Read-only. Paths are `repo/path:line` under `fresh/` unless they start with `troy/` (the recovered planning text under `scratchpad/troy/.scratch/`) or `maps/`.

## The claim under test

> The calibration programme (about 49k lines, 2026-10-30/31), the hub twin's forecasting, scoring, skills, substrate, sensor-admission, misuse and ethics machinery, computed semver, and the truth surface do not change any adopter's exposure figure, tolerance, cage tier or enactment, and the loop would run without all of them. No recorded owner instruction asked for the calibration programme in those terms.

## Verdict: partly refuted

Three parts break:

1. **Computed semver.** It is on the loop's running path. The composer that does the quantify step loads a file from `computed-semver/` on every run. If that file is missing, every adopter's composition is refused. The adopter's PR gate also uses computed-semver evidence to refuse platform releases. And on 2026-10-17 its engine rule decided which policy lines Ludlow kept, which changed what Ludlow enforces.
2. **"No recorded owner instruction".** This is wrong as worded. On 2026-10-30 the owner chose option `A`, and the record states that A meant "models that earn measured permission to perform the existing judgement skills". That is the programme's purpose in its own terms. What the owner never saw or chose: the Qwen 4B model, PDF/Xpdf origin tracing, ELF closure (pinning the exact shared libraries a program loads), ptrace file tracing, and the tiny Linux lease. Those make up about 29k of the 49k lines.
3. **Map A5 needs several corrections** (see the last section).

What survives: the calibration programme, and the twin's forecasting, scoring, skills, substrate, sensor-admission, misuse and ethics code, change no adopter's money figure, tolerance, Namespace tier or enactment today. The loop would run without them. The truth surface changes no figure either, and it has no code dependency in quantify, tolerance, compare or ratchet.

## 1. Code: callers and imports, from the loop chain outward

### 1a. The adopters' forward-intel emitters do import the hub twin, but not the listed machinery

- Each adopter's emitter imports `twin.evidence`, `fixtures`, `model`, `repo` and `schema` from the hub (`driftwood/twin/emit-forward-intel.py:98-101`; `tuppence/twin/emit-forward-intel.py:112-115`; `ludlow/twin/emit-forward-intel.py:115-118`). It also imports `twin.valuation` (`driftwood/...:212`).
- I computed the static import closure with `ast` at hub HEAD. It is 16 modules and 11,746 lines: artefact, canon, constraints, corpus_size, corroboration, enforcement, **ethics_gate**, evidence, fixtures, model, repo, schema, sign, **skills**, valuation, wardley.
- `ethics_gate` and `skills` enter only through a function-level import:
  - `hub/twin/corroboration.py:211` imports `ethics_gate` inside `_check_admission`, which only runs when the enactment-channel table is loaded (`corroboration.py:92`, `:153`).
  - `ethics_gate.py:68` imports `skills` only for the `Stated` type.
- The emitter path never loads that table. `model.py:388` and `:402` import only `KIND` from corroboration. `schema.py:1004` calls `refuse_disagreeing_grade` only for claims whose kind is `"enactment"` (`schema.py:44`).
- None of the three adopters' `twin/orgs` trees contains the word `enactment` (grep count: 0 files).
- **Executed overlap with the listed machinery: zero lines. Static overlap: `skills.py` 485 plus `ethics_gate.py` 551, which is 1,036 lines.**
- A second insulation layer: all three adopters pin the twin code to `hub_commit 0e353029`, dated 2026-10-23, through signed tag `twin/v0.1.0` (`*/twin/PIN.yaml`). The calibration commits that edited `twin/skills.py` came later: 39186119 (+11/-) and fb9272be (+5/-), both on 2026-10-30. They cannot reach an adopter without a re-pin.
- What the twin *does* feed: Tuppence's forward-intel line is £84,198,283 of its £102,869,480 total (`tuppence/composed/HEADER.yaml:1399`, `:1335`). Those are hub twin model and overlay modules, which are not on the claim's list. A distiller must not shorten the claim to "the hub twin is off the loop".

### 1b. Nothing in platform or the adopters imports the listed twin modules or the calibration code

- Quoted-glob grep over `platform/{compose,wargamer,graded,risk,fair,shift-left,party,feeds,honesty}`: no import of `twin`, `qualification`, `signal_classify`, `causal_claims`, `ethics_gate`, `sensor_admission` or `forecast_book`. The only hit is a docstring at `platform/fair/severity.py:10`.
- Across driftwood, tuppence, ludlow, platform, feeds, ico, nist and insurer, the only hits are:
  - `feeds/verify-news-headline-skill.sh:118`, a verify script that release workflows skip (`feeds/.github/workflows/release.yml:94`);
  - nist metadata naming `twin/scoring.py` as the source of a byte-identical copy (`nist/publisher-reliability/UPSTREAM.json:11-13`).
- **The one wired score-to-money path is dormant.** `platform/compose/publisher_reliability.py` can widen a priced scenario, but only if an adopter declares `appetite.publisher_reliability`. None does: grep of the three `party.yaml` files returns nothing. The NIST report it reads has 0 targets (map H2, path D). The path exists in code and is off today.

### 1c. The misuse catalogue and the truth surface: the nearest misses, not breaks

- **What the code says.** `platform/graded/cage.py:183-206` names four misuse paths by hub catalogue row (`catalogue_row: adopter-twin-...`). `cage.py:211-221` sets `DETECTION_WINDOW = 1.0 day`, "the hub's .github/workflows/truth.yml schedule". The composer uses that window to annualise the twin-agent line (`composition.py:4610`, `:4667`).
- **What this touches.**
  - Both values are hard-coded constants. The composer does not read the hub catalogue or `truth.yml`, so removing them would move no number.
  - The twin-agent line is £0.00017 for Driftwood, £18.70 for Tuppence and £2.98 for Ludlow (`*/composed/evidence.json` `prices[]`, `kind: agent-cage`).
  - It is outside the headline total. Tuppence's four headline lines sum to £102,869,480.26, which is the `total`, without the £18.70.
  - It never folds into the Namespace tier: "a rung for another actor (the twin agent, ticket 145) never folds into the Namespace" (`platform/wargamer/wargamer.py:291-292`).
- **What it does enact.** The twin-agent rung `isolated` switches off the adopters' twin-sweep write job (`driftwood/.github/workflows/twin-sweep.yml:322`, per map A4). That changes what the *assistant's* job may write. It does not cage an adopter workload.
- **Observation delivery.** Each adopter downloads the hub's `talk/observation-delivery.pyz`, pinned to hub commit f546d2d9 (`driftwood/.github/workflows/observation-delivery.yml:45`, `:62`). It delivers only the drift-sample and twin-sweep observations (`:6-8`). No quantify, tolerance, compare, ratchet or enact step reads those.

### 1d. Computed semver: a break

1. **The composer depends on it at run time.**
   - `platform/compose/composition.py:3195` sets `ENGINE_GRADER = PLATFORM_DIR / "computed-semver" / "engine_compatibility.py"`.
   - `:3237-3239` loads `declared_engines` from that file, a 23-line function at `engine_compatibility.py:156`.
   - `:5912` calls it for every implementation parent on every compose.
   - If the file is absent, `_engine_module` raises `Refused("missing instrument ...")` (`:3208-3210`). `:5916` appends a `missing-instrument` refusal, and `:6395` then sets `outcome: refused`.
   - So without computed semver there is no composition, no prices and no tier selection for any adopter. That holds in the daily re-compose in `propose-tier.yml` and on PRs (`shift-left.yml:480`).
   - This is present at Driftwood's pinned tools tag `v6.3.0` (`git show v6.3.0:compose/composition.py` has 2 `ENGINE_GRADER` hits).
   - `platform/shift-left/ci-check.py:28`, `:78` loads the same function in the adopter PR check.
2. **Its rule decides whether a priced line appears.**
   - When a served policy line does not list the adopter's engine under that rule, `engine_deltas` prices an `unsupported-engine` or `undeclared-engine` delta (`composition.py:3339-3380`).
   - Today every pairing is `supported` for all three adopters, and no engine delta exists (`*/composed/evidence.json` `engine.pairings`, `deltas`). So it adds no money today, but the path to money is live.
3. **It shaped Ludlow's enactment.**
   - ADR-0038 (delegated, 2026-10-17) requires "Every retained line and the machinery must declare support for both engines under `every-served-body-v1`" (`hub/docs/adr/0038-...md`). That scope is the engine-compatibility rule's.
   - Ludlow then retired policy windows 5.0.0 and 6.0.0, deleting `composed/policies/v5.0.0/*` and `v6.0.0/*` (ludlow ce5213f, 2026-10-17, "Retire measured Ludlow policy lines before its engine transition"). It moved to Kyverno 1.19.1 (2115b34).
   - Ludlow's evidence now pairs only policy 7.0.0 with 1.19.1.
   - That is a change to what Ludlow enforces, and it was gated by computed semver. It was an engine upgrade, not a ratchet notch, but it is enactment.
4. **It gates the adopter's pick-up of a new cage release.**
   - `driftwood/.github/scripts/adopter-gate.py` is in map A4's kernel at hop 2. It refuses a platform bump whose added versions lack signed computed-semver evidence (`:394-399`). It refuses a computed major with no owner acceptance record (`:1041-1048`).
   - `shift-left.yml` runs on every pull request (`on: [pull_request]`) and calls the gate (`:198-232`). It also imports the computed-semver package in the matrix-row step (`:243-247`; `adopter-gate.py:855-857`).
   - Driftwood holds records for platform 5.0.0, 6.0.0 and 7.0.0 under `accepted-majors/`. The 7.0.0 record cites the owner's 2026-10-03 delegation "you tell me, you control them all, you don't need me to answer".
   - Platform's own policy tag cut runs the computed-semver gate before `git tag` (`platform/.github/scripts/cut-release-gate.py`; `cut-release.yml:162`, `:176`).
   - Whether shift-left is a required status check on adopter `main`: could not determine (needs the GitHub API).
5. **Conclusion.** Computed semver does not change exposure, tolerance or Namespace tier today. It does gate enactment and has changed it once. As wired, the loop does not run without it: its 23-line engine rule is a hard dependency of quantify.
6. **Map corrections.** Map P1 gave the engine grader "loop role: none" (`maps/P1-...md:23`), and FACTS says computed semver "feeds none of the loop steps". Both need correcting.

### 1e. The calibration programme, checked directly

- 184 hub files were born between 2026-10-30 and 2026-10-31, holding 49,343 lines at HEAD (`git log --diff-filter=A`, then `wc`). That matches "about 49k".
- No adopter or platform file imports any of it (1b). Adopter twin pins predate it (1a).
- The confirmed spec forbids it reaching money: user story 29, "model qualification never grants merge rights, human overrides or price eligibility" (`troy/calibration-programme/spec.md:47`).
- `twin/qualification-registry.json` is `{"entries":[]}` (map H2, row 20).
- **Verdict for this part: holds.**

## 2. Who asked for the calibration programme, in what words

Dated trail from the recovered text. Quotation marks mark the owner's own words only where the record says they are verbatim.

| Date | Owner's words (as recorded) | What the words were answering | Source |
|---|---|---|---|
| 2026-09-21 | "A model may judge on a GitHub clock, within thresholds." | Laya/loophole map; amended ticket 75 Q10 | `fresh/hub/.scratch/ecosystem/issues/75-...md:165-172` |
| 2026-10-03 | "you tell me, you control them all, you don't need me to answer" | Codex resuming September's work | `driftwood/accepted-majors/platform-7.0.0.yaml:3-6` |
| Standing, 2026-10 | Goal objective: "new session quota, resume do not stop implementation phase until the whole thing is built" | Codex goal | `troy/calibration-programme/WORK-STATE-BEFORE-PLAN.json:3` |
| 2026-10-22 | "1. agree to renew this until the end of the year / 2. resume this / 3. delegate / 4. delegate" | Item (4) was "investigating calibration target, population and outcome sources". Here "calibration" meant ticket 46's *monetary* calibration, a quantify-side target. The recommended target was the 2027 direct-recovery-expense pilot | `troy/ecosystem/research/resume-user-decisions-20261022/OWNER-INSTRUCTION.md:3-12`; `.../resume-active-20261022T2203/NEXT-OWNER-DECISIONS.md:7` |
| 2026-10-23 | Accepted all three recommendations, including "Calibration policy: implement the prospective 2027 institutional direct-recovery-expense pilot". The exact reply sits in `OWNER-DECISION.json`, which was **not recovered** | Proposal list | `troy/ecosystem/research/adopt-three-owner-policies-20261023/ADOPTION.md:1-5` |
| About 2026-10-26/27 | "Your two instructions": a labelled challenge corpus, and a dedicated pilot evidence custodian. Exact words **not recovered**: `resume-20261027-delegated-evidence/OWNER-DECISION.json` is absent | Unknown | `troy/ecosystem/research/resume-20261027-delegated-evidence/REPORT.md:3`; `fresh/hub/.scratch/ecosystem/issues/168-...md:9` |
| 2026-10-28 | None. The Codex goal tool returned "blocked" after three no-progress turns. One of the five open requirements was `authentic_independent_semantic_skill_labels_and_sufficient_population` | The assistant's own reading of NORTH-STAR | `troy/ecosystem/research/resume-20261028-post-dataset-audit-003/REPORT.md:1-7`; `WORK-STATE-BEFORE-PLAN.json` `pending_requirement_ids` |
| 2026-10-30 | `A` | "the two-option outcome question". Recorded meaning: "models that earn measured permission to perform the existing judgement skills". "No additional owner reason was supplied" | `troy/calibration-programme/interview.md:11` |
| 2026-10-30 | `2 A` | Population: this estate, its three adopters and existing domains | `interview.md:19` |
| 2026-10-30 | `3 existing resources` | No new spending | `interview.md:23` |
| 2026-10-30 | `4 yes` | Take the whole proposal into a spec and tickets | `interview.md:35`; `design-proposal.md:5` |
| 2026-10-30 | "Approve stronger plant checks" | One substrate scorer exception | `spec.md:110` |

What the record says the programme was for:
- Its problem statement: "The owner wants models to perform this estate's existing judgement skills only after earning measured permission" (`spec.md:7`).
- Its operative trigger was the blocked goal's fourth requirement. Its design keeps the other open requirements separate: "real band-crossing ... remain separate requirements. This programme neither manufactures those events nor changes their acceptance criteria" (`design-proposal.md:34`).
- It does not claim to change money, tolerance or tier anywhere.

Split by who decided:
- **Purpose: owner-instructed, by bare letter.** The option text was written by the assistant. The text of option B was not recorded.
  - `fact-audit.md:47` sets "a human-led workflow already has an existing authorisation contract" against "earning model permission". That *suggests* B was the existing human-run path. This is inference, not record.
  - Who opened the grilling session: could not determine.
- **Delegated under ADR-0025, never put to the owner:**
  - the Qwen3-4B candidate (`design-proposal.md:18`);
  - the 15-ticket breakdown (`tickets.md:5`).
- **Not in the owner-confirmed spec, design or tickets at all:**
  - **What the grep shows.** A word-bounded grep for pdf, xpdf, `\belf\b`, soname, ptrace, lease and cgroup across `spec.md`, `interview.md`, `design-proposal.md`, `tickets.md` and `issues/*.md` finds only "native verification lease is spent" (`source-guide.md:52`), which is unrelated. The earlier count of 4 hits in `spec.md` came from `elf\b` matching "itself" and is withdrawn.
  - **Where the work did come from.** The PDF host bridge, Xpdf instrumentation, ELF-needed diagnostics and the tiny Linux harness appear only as implementation sub-workstreams in `implementation-20261030/CURRENT-IMPLEMENTATION-STATE.json` (keys `PDF_host_bridge_contract`, `tiny_CI_ELF_needed_diagnostic`, `tiny_linux_harness` and others). That file records `"owner_decision_pending": false`, and its `next` field reads "... No owner decision pending."
  - **The nearest ticket wording.** Ticket 06 asks to demonstrate "the exact actor in the actual intended execution environment ... Linux/runtime readiness" (`issues/06-...md:20`). Ticket 02's acceptance records "real kernel network denial" (`issues/02-...md:37`).
  - **Size.** Map A5 rows 18-21: 2,044 + 9,798 + 2,438 + 14,834 = 29,114 lines.

The word "calibration" drifted:
- On 2026-10-22 and 10-23 it meant calibrating the money figure against real 2027 recovery costs. That is a quantify-side aim, and the owner delegated it and then accepted it.
- By 2026-10-30 the "calibration programme" meant qualifying a language model on the twin's six judgement skills.
- The second inherited the name of the first. Map H2 found three meanings of the word (`maps/H2-twin-forecasting.md`, Surprises 2).

## 3. Corrections to map A5 (written without this material)

1. **"The calibration trigger cannot be read verbatim anywhere."** Wrong now. It is the 2026-10-30 grilling session (`interview.md`), with the owner's replies `A`, `2 A`, `3 existing resources` and `4 yes`. It sits inside a Codex goal whose objective was "... do not stop implementation phase until the whole thing is built", after the goal blocked on 2026-10-28.
2. **"The only owner words are 'Approve stronger plant checks'."** Wrong. The four interview replies above came the same day, plus the 2026-09-21 "within thresholds" amendment.
3. **"The bar is ADR-0029's ten conditions: about 326 items per skill."** Wrong on the number. The programme keeps the existing measured minima of 16/12/16/16/9/16/16 (`spec.md:71-79`; `fresh/hub/twin/skill-thresholds.yaml:30-31` shows `threshold: 0.8`, `min_items: 16`). 326/3,260 came from a different ten-bin calibration-error question (`troy/ecosystem/research/resume-20261028-candidate-adapter-audit/REPORT.md:71`). The ten conditions themselves are right.
4. **"A single demonstrated developmental reference case" and "the commissioned dataset is unreadable".** Both incomplete.
   - Four publication cases were admitted (0.27, 0.61, 0.34, 0.14) and 42 withheld (`resume-20261028-case-admission/REPORT.md:1`).
   - A 105-input agent-authored dataset (17 development, 88 held out) was consumed by the incumbent heuristics in 104 calls. Supported-correct results: signal 0/16, evolution 0/12, causal 0/16 and grade 0/16; gameplay, substrate and ethics passed mechanics only (`resume-20261028-scoped-diagnostic/REPORT.md:3-13`).
   - The "commissioned dataset" is a 19-case Evidence Inference packet with reported-significance labels and **zero** admitted product-skill cases (`resume-20261028-dataset-commission/REPORT.md:3-7`).
5. **The causal grade fix (ticket 168) "would be lost" from the loop.** Overstated. PR #282 merged on 2026-10-27, but `causal_claims.py` is not in the adopters' twin import closure (1a). Adopters price authored edges with their declared grades. No adopter figure can depend on that fix.
6. **Origin "codex (inferred)" for rows 15-23.** Now better supported. The 2026-10-22 note says "in this Codex session" (`OWNER-INSTRUCTION.md:3`). The same goal-objective string carries through to the 10-30/31 work-state files. The programme records itself as "the assistant's architectural decisions under ADR-0025" (`design-proposal.md:13`).
7. **A5's "loop role: none" for the programme is right**, and its "no change at all from calibration" table is right. Those parts stand.

## 4. The claim, restated precisely

The calibration programme (49,343 hub lines born 2026-10-30/31) changes no adopter's exposure figure, tolerance, Namespace tier or enactment, and the loop would run without it. So would the hub twin's forecasting, scoring, skill, substrate, sensor-admission, misuse-catalogue and ethics code:
- none is imported by platform;
- the adopters' forward-intel emitters import `skills` and `ethics_gate` only statically, behind a lazy import that no adopter overlay triggers (0 enactment claims);
- adopters pin twin code from before the programme (0e353029, 2026-10-23).

The truth surface changes no figure and is no code dependency of quantify, tolerance, compare or ratchet. Its nearest contact is two things:
- a hard-coded one-day detection window in the twin-agent line, which is £0.00017 to £18.70 and outside every headline total;
- the hub-pinned observation-delivery tool, which carries evidence only.

Computed semver is the exception. Its engine rule (`computed-semver/engine_compatibility.py`) is loaded by the composer on every run, and without it every composition is refused. Its evidence and major-acceptance checks gate the adopter's pick-up of new cage releases. It governed Ludlow's 2026-10-17 retirement of policy windows 5.0.0 and 6.0.0. So it is on the enact and quantify path as wired, even though it moved no money figure or Namespace tier.

The calibration programme's purpose was chosen by the owner, by bare letter `A` on 2026-10-30, to an option the assistant wrote: "models that earn measured permission to perform the existing judgement skills". The owner never chose its PDF/Xpdf, ELF, ptrace and Linux-lease machinery (about 29k lines) or its Qwen candidate. No owner sentence links the programme to exposure, tolerance, the cage or the loop.

## Could not determine

- The text of option B on 2026-10-30, and who opened the grilling session.
- The verbatim owner replies of 2026-10-23 and about 2026-10-26/27 (`OWNER-DECISION.json` files not recovered).
- Whether `shift-left` is a required check on adopter `main` branches.
- Whether the owner read the option text before answering `A`. The owner has said bare agrees are often fatigue (FACTS, "Whose idea each part is").
