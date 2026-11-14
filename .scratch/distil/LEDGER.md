# LEDGER: every tracked path, what was proposed, what the blind check found, and the call

Written 2026-11-14, beside `DISTILLATION.md`. Read-only review. Nothing has been removed and nothing here authorises removal.

**What this is.** Every tracked path on the default branch of the nine repositories falls in exactly one of rows L01 to L25. Row L26 is material that is in no remote repository. Row L27 is four repositories outside the nine, which build the served images; they were not cloned, read or counted. For each of L01 to L26 an integrator proposed a disposition. A second reader, who had not been given the reasoning, then tried two things: to show the loop runs without the row, and to show the loop breaks or loses something without it. That is the "blind check". Three readers (L01, L17, L20) opened `TARGET.md`, saw the proposal before judging, and said so (`verdicts/L01.md:6`, `L17.md:5`, `L20.md:5`). L01 still disagreed. Where proposal and check disagree, section 2 shows the disagreement and my call.

**Not covered.** Remote branches other than the default are out of scope and left untouched. The hub has 314 and driftwood 113, among them `wargamer/retune-driftwood-served-images`, dated 2026-11-13. Parking `main` does not remove them.

**Dispositions.**
- **Keep**: stays in the working tree as it is.
- **Shrink**: a named small part stays; the rest leaves the working tree.
- **Merge**: named lines are lifted into the new loop; the rest leaves.
- **Park**: leaves the working tree and the scheduled jobs; stays in git history and on an archive branch.
- **Cut**: leaves the tree with no archive branch of its own; git history still holds it.

**Counting.** Lines are tracked text lines on 2026-11-14, counted by the integrator (`TARGET.md`, section 13). Binary files count as nought. L01 to L25 sum to 2,095,084. With L26 the total is 2,207,933.

**Citations.** `repo/path:line` is a path in the clones of 2026-11-14. `verdicts/Lnn` is the blind check's working for that row. K1 to K4 are the keystone checks. AT:n, T75:n and RA:n are lines of the files that record the owner's dated words (see `DISTILLATION.md`, top). Ids such as B4 or D16 point into section 3.

---

## 1. The ledger

| Id | What | Paths | Lines | Proposed | Reason for the proposal | Blind check | Agree | Final call | What the loop must take from it |
|---|---|---|---|---|---|---|---|---|---|
| L01 | Hub: the owner's dated words | `hub/.scratch/drift-review-2026-08-27/` (AT, the decision ledger, appendices, RA, REPORT.md); ticket 75; PURPOSE.md | 18,772 | keep | The only tracked copy of the owner's dated words. Move it beside `LOOP.md` | shrink | **no** | **Shrink.** Keep 12,103 lines where they are, byte for byte. Park 6,669 lines of the assistant's August analysis | The owner's rules and the index: A2, A8, I1, I2, I11 |
| L02 | Hub: thesis and lineage | `hub/research/0[1-3]-*.md`; `docs/PRD.md`, `HISTORY.md`, `ARCHIVE.md`; `docs/agents/`; `CLAUDE.md`; `LICENSE`; `.gitignore` | 2,531 | keep | The 2022 thesis and the June design are the lineage of enact and react | shrink | **no** | **Shrink.** Keep about 580 lines. Park the June design, the history and two research notes. Cut `ARCHIVE.md` | Two lessons and the lineage: I3, I4, I8, F9, A11 |
| L03 | Hub: NORTH-STAR.md | `hub/NORTH-STAR.md` | 143 | park | Its one sentence states an eco-system and a talk. `LOOP.md` replaces it | park | yes | **Park**, with a banner naming `LOOP.md` | Five rules: I1, I2, I5, I14, B9 |
| L04 | Hub: glossary and front page | `hub/CONTEXT.md`; `hub/README.md` | 1,002 | shrink | About 24 of 120 glossary entries serve the loop | shrink | yes | **Shrink** to about 90 lines | Terms and four rules: I6, I7, I13, C5, B7 |
| L05 | Hub: decision records | `hub/docs/adr/` (37 files) | 4,646 | shrink | Keep two, add ADR-0039, the other 35 leave as history | "park", by which it means leave in place | **no** | **Keep in place.** Add ADR-0039 first, then dated banners that name points | Eleven measured rules: I5, C1, C2, C13, D10, D15, D19, D20, B11, C15, E13 |
| L06 | Hub: planning text, notes and spikes | the rest of `hub/.scratch/`, `hub/docs/`, `hub/research/`; `hub/spikes/`; `hub/explorations/` | 187,123 (and 401 binary media files) | park | Specs, tickets, reviews and research for parked features. None of it runs | shrink | **no** | **Shrink.** Carry five named things, push an archive ref, then the rest leaves | The reference-pod design, Kyverno findings, fine sources: A1, C5, C14, D1, D5, D16, G1, I1, I4, I8, E7, A11 |
| L07 | Hub: twin, calibration programme, tests, benches | `hub/twin/`; `tests/`; `bench/`; `conftest.py`; `pytest.ini`; `bin/` | 143,516 | park | No forecast, score or skill moves driftwood's figure. The calibration programme has no caller (K4) | park | yes | **Park.** Keep tag `twin/v0.1.0` fetchable. Move one helper first | About eight lessons: A5, A6, D10, D16, B4, B11, B16, E3, E13, I9 |
| L08 | Hub: truth surface and CI | `hub/verify/`; `talk/`; `.github/`; `tts.py`; `clone-estate.sh` | 69,717 | park | It grades the build, not exposure: 61 of 117 passes are self-proof | park | yes | **Park.** Switch off its two schedules. Leave history untouched | Ledger and probe rules: A5, A6, A9, B16, B20, C10, D16, D19, E4, E5 |
| L09 | Hub: agent settings and skills | `hub/.claude/` | 2,438 | park | The skills and the guard serve the assistant's build, not the loop | shrink | **no** | **Shrink.** Park four skills. Keep the owner's permission list. The owner makes the commit | Four rules: A5, B9, B17, E14, I12 |
| L10 | Hub: October copies, run records and strays | `hub/.scratch/ecosystem/patches/`; `research/resume-*/`; `t/`; `forged.yaml`; `fleet`; `policy`; `.scratch/0001-*.patch` | 1,337,342 | cut | Copies of other repositories' diffs and session logs. Git history keeps them | park | **no** | **Park**, after an index of the owner's October approvals is written | The index and two rules: A3, A5, A11, B5, C11 |
| L11 | Platform: sources of the new loop | `platform/fair/`; `risk/`; `wargamer/`; `feeds/` | 6,548 | merge | The only working formula for the mean, tolerance reader, one-line rung edit and exploited-flaw match | merge | yes | **Merge** about 380 lines: about 190 into `loop.py` and 190 into `inventory.py`. Write the veto anew, with a half-life | The lifts and their lessons: B1 to B4, B8, B9, B12 to B14, C15, A9 |
| L12 | Platform: the cage | `platform/graded/`; `platform/distribution/` | 10,680 | shrink | One cage tree, `rungs.yaml` and a consumer test replace two authoring copies and the typed table | shrink | yes | **Shrink** to about 240 lines. Tags stay | About fifteen lessons found live: D1 to D15, D21, C2, C7, C13, C14, A10 |
| L13 | Platform: the old chain | `platform/compose/`; `party/`; `shift-left/`; `honesty/`; `tcor/`; `engine/`; `party.yaml` | 25,033 | park | `loop.py` replaces its pricing and compare paths | park | yes (medium confidence) | **Park**, only at the cut-over | About a dozen rules: A7, B2, B6, B8, B10, B19, D2, D6, D10, D16, E2 |
| L14 | Platform: computed semver | `platform/computed-semver/` | 14,507 | park | The composer loads its engine rule on every run (K4). With the composer parked it has no caller | park | yes | **Park**, in the same change as the composer. Lift about 120 lines of test rules first | Test rules: A7, D16 to D18, F3, F6 |
| L15 | Platform: off the loop | `platform/implementations/`; `identity/`; `access/`; `posture/`; `eud/`; `currency-controller/`; `recovery-expense/`; `wardley/`; `break-glass/`; `oscal/`; `policy/`; `docs/`; root `verify-*`, `lib*.sh` | 17,664 | park | Shelved by the owner or wired to no loop step | shrink | **no** | **Shrink.** Keep about 280 lines of release guards. Two parts the owner chose to keep go to decision 7 | Signing rules: F2, F4, F8, E1, B20, D6, C17, D22, A7, A12 |
| L16 | Platform: CI and front page | `platform/.github/`; `README.md`; `CONTEXT.md`; `LICENSE`; `.gitignore` | 1,933 | shrink | Three workflows remain: loop, proof, signed release | shrink | yes | **Shrink in place.** The signing workflow keeps the file name `cut-release.yml` | Release rules: F1 to F7, A9 |
| L17 | Driftwood: the declaration | `driftwood/party.yaml`; `gitops/`; `deploy/`; `renovate.json`; `README.md`; `LICENSE`; `.gitignore` | 1,428 | shrink | Size, tolerance with a basis, one rung line, three Deployments, pins | shrink | yes | **Shrink** to about 315 lines. Removing the floor needs decision 8 | Thirteen lessons: H1 to H9, H11, H12, D15, D22, E7, A10 |
| L18 | Driftwood: sampler and bring-up | `driftwood/drift/`; `git-server/`; `kind/`; `scripts/` | 7,074 | merge | The only probe and reference-bracket code seen running, and the only past observations | merge | yes | **Merge.** Copy the sample logs to the ledger. The rest leaves only after the old workflows retire | The measuring rules: C1 to C9, C12, C16, D13, D17, H10 |
| L19 | Driftwood: generated tree and duplicate selector | `driftwood/composed/`; `selection-policy/` | 26,437 | cut | Generated output with copies of publisher feeds, and a second copy of the selector | cut | yes (medium confidence) | **Cut**, in the change that removes the check that regenerates it | Six small rules: B2, B6, B7, B8, B15, G7, D22, A10 |
| L20 | Driftwood: CI | `driftwood/.github/` | 6,718 | shrink | Nine workflows and the gate scripts become one caller | shrink | yes (medium confidence) | **Shrink** to about 65 lines: a caller and a cut-down Renovate runner | Sixteen encoded fixes: E1, E2, E4 to E12, C9, C10, D13, A10, H12 |
| L21 | Driftwood: off the loop | `driftwood/twin/`; `inventory/`; `observations/`; `scenarios/`; `accepted-majors/`; `tests/`; root `verify-*.sh` | 9,019 | park | The twin line is GBP 758 of GBP 1,807,494 | park | yes (medium confidence) | **Park** at the cut-over | Cage-test lessons and one fixture: D2, D16, D17, C5, C15, B13, B16, G8, H11 |
| L22 | Tuppence and ludlow | both repositories, whole | 92,082 | park | Near-clones. The new loop cannot price either without parked parts | park | yes | **Park.** Copy four fixtures out first | B2, B18, B20, C8, C15, D16, A9 |
| L23 | Ico | the repository, whole | 6,497 | shrink | The owner's first example and the only published fine sizes | shrink | yes | **Shrink** to about 400 lines. All tags stay | Penalty rules: B11, B12, B19, G1, F1, F4 |
| L24 | Feeds | the repository, whole | 85,412 | shrink | The `needs` lists decide what the cage earns. The exploited-flaw list is the only disturbance nobody in the estate writes | shrink | yes | **Shrink** to about 390 lines. All tags stay. The parked feeds include `eol` and `news`, both ideas of the owner's (AT:485, AT:2312): decision 7 | Feed rules: G2 to G6, B11, F2 |
| L25 | Nist and insurer | both repositories, whole | 16,822 | park | The new loop reads no control catalogue, and the premium sits outside the compare | park | yes | **Park**, tags and remotes intact. Stop their schedules | B19, G1, A9 |
| L26 | Local-only and recovered material | the owner's working copy and backup disk | 112,849 | park | Unpushed work and the only record of how the calibration programme was commissioned | shrink | **no** | **By part**: see section 2 | A1, A4, A12, C15, E5, I10, I11 |
| L27 | Outside the nine: the repositories that build the served images | `driftwood/api`, `driftwood/storefront`, `tuppence/ledger`, `ludlow/reports` (`driftwood/gitops/apps/api.yaml:19`, `storefront.yaml:69`; `tuppence/gitops/apps/ledger.yaml:78`; `ludlow/gitops/apps/reports.yaml:66`) | not counted | none made | Not in the first ledger. The critic found it | none run | n/a | **Keep** `driftwood/api` and `driftwood/storefront` live: step 7's patch is a tag there. **Park** `tuppence/ledger` and `ludlow/reports` with their adopters, tags and packages intact | The first tag in each transferred repository is an owner authorisation recorded as not yet given (`hub/docs/adr/0036-*.md:43-44`): decision 10(iv). Whether it was given later: could not determine |

**Totals by final call.** Keep in place: 4,646 (L05). Shrink: 455,047 (13 rows). Merge: 13,622 (2 rows). Park: 1,708,181 (9 rows). Cut: 26,437 (1 row). Total 2,207,933. L27 is not in these totals.

**Totals as first proposed.** Keep 21,303; shrink 118,316; merge 13,622; park 690,913; cut 1,363,779. The largest shift is L10: 1.3M lines move from cut to park.

**Does the loop run without the row?** The blind check answered yes for 17 rows, partly for 6 and no for 3. The three are the cage (L12), driftwood's declaration (L17) and ico (L23). The six "partly" rows are L11, L14, L16, L18, L20 and L24: each holds lines the new loop is made from, or a path it must keep.

---

## 2. The eight disagreements

In all eight my call sides with the blind check. Each has its own reason. Where a call turns on one fact, I say whether I opened the source.

### L01. The owner's dated words: keep, or shrink

- **Proposed:** keep all 18,772 lines and move them beside `LOOP.md` as `docs/provenance/`.
- **Check says:** shrink. Keep the record of the owner's words in place, byte for byte. Park the assistant's August analysis.
- **The facts it turns on.** The row is two things. 12,103 lines are the record of the owner's words and its readable rendering: AT 3,391, the decision ledger 6,455, RA 91, ticket 75 200, PURPOSE.md 187, appendices A and B 1,779. 6,669 lines are the assistant's analysis: appendices C to G and REPORT.md. I counted the files and the split is right. Citations into these files are by line number, and ticket 75 holds six relative links that a move would break (verdicts/L01, relayed).
- **Call: shrink, and do not move.** Keep the 12,103 lines where they are. Add an index file beside them, never an edit inside them. The index records the 2026-11-14 sentence, which no repository holds: I searched the hub clone for "financial tolerance" and found nothing.
- **A caution on the parked part.** The check could not rule out that appendices D and G hold a sentence of the owner's found nowhere else. So that part is parked on an archive ref, not cut.

### L02. Thesis and lineage: keep, or shrink

- **Proposed:** keep all 2,531 lines as the lineage of enact and react.
- **Check says:** shrink. Nothing on the loop's chain reads any of it.
- **The facts it turns on.** `hub/docs/ARCHIVE.md:3-8` says of itself that it is superseded and "not to be executed" (I read it). The June design has no money, tolerance or compare step, and its surviving decisions are in ADR-0001 and ADR-0002 (verdicts/L02, relayed).
- **Call: shrink.** Keep `LICENSE`, `CLAUDE.md`, `docs/agents/` trimmed, a short `.gitignore`, and `research/03-blogs-thesis.md`, which is the owner's own 2022 text. Copy two lessons into `LOOP.md` first (I3, F9). Park the June design, `HISTORY.md` and research notes 01 and 02. Cut `ARCHIVE.md`: it misleads, and the archive ref taken before anything leaves will still hold it.

### L05. Decision records: shrink, or leave in place

- **Proposed:** shrink. Keep ADR-0001 and ADR-0002 amended, add ADR-0039, and let the other 35 leave as history.
- **Check says:** "park". Its meaning is the opposite of this ledger's: leave all 37 files in the working tree and add dated banners only. I show its label as given and take its substance.
- **The facts it turns on.** No file on the loop reads a decision record. Checks in the parked truth surface do read their exact text, and those checks still run every day (verdicts/L05, relayed; the last hub commit is the app's, 2026-11-12, which I confirmed). The records hold the only written account of eleven measured failures. One is the ratchet contradiction: ADR-0015 rejected a tighten-only proposer (`hub/docs/adr/0015-*.md:68-69`, read) and a note of 2026-09-04 in ADR-0022 adopted one (`0022-*.md:110`, read).
- **Call: keep in place.** 4,646 lines of text cost the loop nothing. ADR-0039 lands first and absorbs the eleven rules (I5). Then banners that name points, never a rewrite: ADR-0021 in full; 0015, 0020, 0022, 0023, 0024 and 0026 in part; 0019 after it is read. Look again at moving the 35 into history once the truth surface's schedule is off.
- **For the owner.** ADR-0025 (the assistant decides architecture) and ADR-0037 (the delivery controller) are authorisations. Whether they stand is decision 7.

### L06. Planning text, notes and spikes: park, or shrink

- **Proposed:** park all 187,123 lines.
- **Check says:** shrink. The destination is the same. The difference is what happens first.
- **The facts it turns on.** No archive branch or tag exists on the hub remote: its only tag is `twin/v0.1.0`, and the three branches with "archive" in their names are record branches (I listed them). Four notes hold things the new loop needs and no other file holds: the reference-pod design (`ticket-152-fact-7-reference/`), the Kyverno findings (`kyverno-1.18-cage-facts.md`, `kyverno-1.19-cage-diagnosis/`), and the sourced fine evidence that the ico feed cites (`research/94-studied-firms.md`) (verdicts/L06, relayed).
- **Call: shrink.** Push an archive ref. Carry the five things (C5, D1, D5, G1, I4). Then the rest leaves in the same change as the truth surface, which is its only real reader. Do not fold all of `talk-spec/the-whole-model.md` into `LOOP.md`: carry its thesis line and "policy carries its why", and nothing else.

### L09. Agent settings and skills: park, or shrink

- **Proposed:** park all 2,438 lines with the twin.
- **Check says:** shrink. Park the four skills. Keep a small settings file.
- **The fact it turns on.** `hub/.claude/settings.json` is 44 lines. It holds the owner's permission list, and a hook that runs `twin/enact_guard.py` before every tool call (`:32-38`, read). If the twin file leaves and the hook stays, every tool call in a hub session is blocked (verdicts/L07, relayed).
- **Call: shrink.** The permission list is the owner's and stays. The hook goes in the same commit that parks the twin. The owner makes that commit, not an agent (decision 10, part iii).

### L10. October copies and run records: cut, or park

- **Proposed:** cut all 1,337,342 lines, on the ground that they hold no owner instruction.
- **Check says:** park. That ground is false.
- **The fact it turns on.** I opened `hub/.scratch/ecosystem/research/resume-2026-10-04/explicit-publication-authorization.json`. It records `user_words: "approve"`, received 2026-10-03T23:14Z, for merging platform PR 49 and feeds PR 10 and cutting six signed tags. One of those tags is `cve/v3.0.0`, the tag the exploited-flaw feed has been frozen at ever since. Thirteen file names in that directory contain "authorization" or "approval". Only the archive approvals are mirrored in a ticket (verdicts/L10, relayed). Separately, `hub/verify/cited-truth/cited_truth.py:955` reads one file inside this row (read), so the daily truth run goes red if the row leaves first.
- **Call: park.** Park differs from cut here by three things: an archive ref, an index written first (A3), and an order (the truth surface leaves first or in the same commit). The removal is an ordinary commit. It does not shrink a clone, because history keeps the lines. The last commit that holds the row is hub `fc37a668`; the tree hashes are in `verdicts/L10.md`.

### L15. Platform, off the loop: park, or shrink

- **Proposed:** park all 17,664 lines.
- **Check says:** shrink. Keep about 280 lines. Name two parts for the owner.
- **The facts it turns on.** `platform/party.yaml:72-88` records that ticket 75 question 13 withdrew the currency controller's retirement, because it is "the estate's only post-admission re-caging mechanism" (read). `platform/recovery-expense/pilot-2027.json` exists and names the three adopters for 2027 (read). Both are choices of the owner's. The guards that protect two signing fixes live only here (verdicts/L15, relayed).
- **Call: shrink.** Keep `verify-release-signing.py` (89 lines), `verify-certificate-identity-regexp.sh` (45), `lib.sh` (102) and `lib-selfcheck.sh` (44), folded into the signed-release proof. Park the rest, and not before the composer, which reads `oscal/` from the pinned tree. The currency controller and the recovery-expense pilot go to decision 7 by name. The in-cluster tag verifier leaves only after the loop's workflow verifies tags in CI.

### L26. Local-only and recovered material: park, or shrink

- **Proposed:** park all of it; push "the 31 tips" first.
- **Check says:** shrink, part by part. The 31 is an undercount.
- **The facts it turns on.** The count of local refs not reachable from the remote is 40 branches, 8 detached checkouts and 1 stash (verdicts/L26, relayed; I did not re-run it. The session that ran the review re-counted it afterwards and got the same three numbers; the branch names are in `evidence/unpushed-local-branches.txt`). The backup disk holds `interview.md`, `ADOPTION.md`, `NEXT-OWNER-DECISIONS.md` and `OWNER-INSTRUCTION.md`; the file said to hold the owner's floor decision, `OWNER-DECISION.json`, is not there (I searched).
- **Call, by part:**

| Part | Size | Call | What must happen first |
|---|---|---|---|
| Local refs in no remote history | 40 branches, 8 detached checkouts, 1 stash | Park | An archive push, or one bundle of every such ref onto the backup disk. Saving only "the 31" loses part of it |
| Empty worktree directories | 215 directories; 334 `.DS_Store` files and 141 symlinks | Cut | The archive above: pruning the worktrees drops the checkouts that keep 8 commits alive |
| Keynote build | 1,463 files, 1.4 GB, untracked | Park on the backup disk, outside the repository tree | It is not ignored by git, so `git add -A` would stage it and `git clean` would delete it |
| Recovered planning text | 311 files, 14,449 lines | Shrink: copy five records, about 95 lines, into the hub beside the owner's words. The rest stays on the backup disk | Mark the five as the assistant's paraphrase of bare replies, not as the owner's sentences |
| A build-contract packet found only in the working copy | 25 files, 4,162 lines | Park | Copy it to the backup disk |

- **Why it matters.** Two of the five records are the only trace of how `floor: isolated` was adopted on 2026-10-23, which the cut-over would reverse. One is the owner's 2026-10-30 choice of the calibration programme's purpose, which parking that programme sets aside. Both go to the owner as reversals (decisions 7 and 8), not as clean-slate design.

---

## 3. What the minimal loop must carry over

Gathered from every row's blind check, with duplicates merged. The row ids in brackets say where each came from. "Could-not-look" means the loop could not take a measurement: it gives no verdict and makes no move.

### A. Before anything leaves a working tree

- **A1. Archive first.** Push an archive ref from hub `main`, and archive or bundle every local ref not in remote history: 40 branches, 8 detached checkouts, 1 stash. Copy the untracked keynote build and the 25-file packet to the backup disk. None of this exists today. [L06, L26]
- **A2. Write the 2026-11-14 sentence into a file.** No repository holds it. [L01]
- **A3. Write a dated index of the owner's October approvals** before the October records leave: date, the owner's exact words, the action, the approved commit, and the path at hub `fc37a668`. [L10]
- **A4. Copy five recovered records into the hub** beside the owner's words: `interview.md`, `OWNER-INSTRUCTION.md`, `ADOPTION.md`, `SPEC.md`, `NEXT-OWNER-DECISIONS.md`. [L26]
- **A5. Park the hub in one order.** Move `twin/other_hand.py` (171 lines) first, to `platform/loop/`: it mints the token of the GitHub App `pavc-other-hand`, the identity the owner's merge rule relies on and the one the merge job of decision 2(b) would use. Park the truth surface with or before the planning text and the October records, because its checks read both. Remove the hook in `.claude/settings.json` in the same commit that parks `twin/enact_guard.py`. [L07, L08, L09, L10, L06]
- **A6. Keep these fetchable for as long as anything pins them.** Tag `twin/v0.1.0` (commit 0e353029). Hub commit f546d2d9, which driftwood's old workflows download from. Platform tools tag v6.3.0. Driftwood tag v5.3.0. Ico tags v3.0.0, v4.0.0, v4.0.1. Every existing feeds tag. The nist tag that ico's release check reads. The four ruleset files. [L07, L08, L13, L19, L23, L24, L25]
- **A7. The composer, `engine/declaration.py` and computed semver park together, at the cut-over.** The composer refuses every run without the other two. The off-loop platform parts do not leave before the composer. [L13, L14, L15]
- **A8. The kept record of the owner's words stays byte-identical and in place.** Citations are by line number. [L01]
- **A9. Stop each schedule in the change that parks its code.** Hub `truth.yml`, `truth-delivery.yml`, `twin.yml`. Platform `fetch.yml`, `recovery-expense.yml`, `cloud-release.yml`. The proposer crons of tuppence and ludlow. Nist and insurer. [L08, L11, L16, L22, L25]
- **A10. Driftwood's cut-over has an order.** Read the branch rules. Stop the old clocks, including the proposer's trigger on closed pull requests. Remove the old gates. Then reset. Moving the platform pin, dropping the old cage bodies and adopting version 8 is one change. [L12, L17, L19, L20]
- **A11. Repair links before their targets leave.** Pin links to a commit where a kept record points into parked text (ADR-0033:151). Repoint the links that `platform/compose/handbook.py:744`, `feeds/README.md:12-13` and `ico/penalty-schema/v4/feed.json:262` make into the hub. Drop the README links to parked documents. [L02, L06, L10]
- **A12. Record each reversal of an earlier choice of the owner's when it is made.** The currency controller (ticket 75 question 13). The recovery-expense pilot for 2027. The calibration programme's purpose ("A", 2026-10-30). The floor (recorded as adopted 2026-10-23). The ordinal pound (T75:78, T75:111, delegated). The owner's own ideas set aside, each named in decision 7: the twin (AT:1215), war-gaming (AT:513, AT:1054), the end-of-life thread (AT:485), paid and news feeds (AT:2305, AT:2312), inheritance (AT:2913) and the no-cuts rule (`PURPOSE.md:137`). [L03, L15, L17, L26]

### B. `loop.py`: price, compare, decide, write

- **B1. Lift the formula for the mean**: `platform/fair/fair.py:106-108` and `:111-130`. Test that it reproduces GBP 1,784,371 for today's fine line and GBP 3,725,501 for driftwood at a penalty rate of 1. [L11]
- **B2. Never add across currencies.** Refuse mixed currencies. A tolerance in another currency is converted through a sourced rate, or there is no verdict. Test with ludlow's US-dollar turnover. [L11, L13, L19, L22]
- **B3. A missing tolerance refuses. It never defaults.** Lift `platform/risk/enforce.py:52-91`. The old shared `appetite.json`, where the three figures came from, stays retired. [L11]
- **B4. Edit the rung on the governed Namespace, never on the pod.** Lift the edit with its helpers, about 100 lines, not 34 (`platform/wargamer/tier_pr.py:84-152, 201-217, 327-360`). `--- # comment` is a document separator. Two governed Namespaces in one file is could-not-look with a non-zero exit, never a silent skip. Read the current rung from the Namespace on the base branch at write time. [L11, L07]
- **B5. The rewrite changes one line only.** Use a line-anchored edit, and test that the diff touches exactly that line. A YAML tool once removed 39 unrelated comment lines. [L10]
- **B6. A partial sum gives no verdict of `within`.** A GBP 10,000 priced line beside an unpriced GBP 50,000,000 line once read "within". Exposure exactly at tolerance counts as within. [L13, L19]
- **B7. Rung names.** Refuse a rung name that is not on the ladder. Decide what an unknown or missing label means: today it falls to `isolated`, so the serving check must catch a corrupted rung line. Do not carry over "fall to isolated when nothing fits": the new loop holds and goes red. [L04, L17, L19]
- **B8. Write the release veto anew.** Derive it from that adopter's own closed, unmerged pull requests, never from a committed file. Find them by a marker in the pull request body. Merged pull requests, pull requests off the branch and other organisations' pull requests do not count. Key it on a hash of every loop input. An unreadable list is could-not-look. Read past the first 100 pull requests. A closed release proposal blocks re-raising for a half-life set in `party.yaml`, or until an input changes, whichever comes first. This is the owner's rule: "Flood guard with a half life. Point in time rejection does not mean never" (RA:28). The old ledger already decays after 30 days (`platform/wargamer/rejection-decay.yaml:21-23`, relayed). Test that it holds inside the half-life, re-raises after it, and lifts when an input changes. [L11, L13, L19, L20]
- **B9. The loop never merges a release.** Keep the scan that finds merge, approve and close verbs in the loop's code. The loop's own workflow token has no merge permission, and a test reads the workflow back to prove it. Until the owner authorises decision 2(b), every notch waits for a person. If the owner does, a separate merge job holds the key of the GitHub App `pavc-other-hand`, already a secret in driftwood (`driftwood/.github/workflows/observation-delivery.yml:75`). It approves and merges only a pull request whose diff is the one rung line moved one notch tighter, or pin lines only. A test shows it refuses a release, a two-line diff and a two-notch move. That test proves the job's code, not the key, which reaches every organisation (`hub/docs/adr/0037-*.md:39-40`). The App merges observation pull requests this way today: all 67 first-parent commits on driftwood's `main` since 2026-10-16 are its merges (for example driftwood 3b561c7). Not established: whether driftwood's rules let the App merge a rung or pin change, which the ruleset file reserves for a person (`driftwood/.github/rulesets/README.md:50-59`). [L03, L09, L11, L13]
- **B10. Read `party.yaml` strictly.** Refuse duplicate keys, a half-declared size, a YAML boolean read as a number, and a declared pin that disagrees with the pinned tag. Read the bytes once and price from that one reading. [L13]
- **B11. The numbers rule, in full.** An unsourced number may raise the figure. A missing instrument refuses a number; it never invents one. A stale size widens to the statutory cap. A sourced correction by a publisher may lower the figure. A zero match from a fetch and a scan that both worked is a measured zero, not a missing number. This replaces the twin's rule that weak evidence is left unpriced, and `LOOP.md` should say so. [L05, L07, L23, L24]
- **B12. Penalty rules move into `loop.py` if pricing moves there.** The cap is the greater of the fixed sum and the rate times turnover. Only final fines price. A frequency with no dated basis refuses. The fine tier is cited or the higher tier is used. One frequency source, never two. No sizes keyed by adopter name in the subscriber's code. [L23, L11]
- **B13. Several consequences of one breach share one frequency and add within the event.** Overlapping contingencies are never summed. [L11, L21, L24]
- **B14. The Monte-Carlo cross-check draws Poisson counts.** Today's simulation rounds, so anything rarer than one year in two simulates to nought (`platform/fair/fair.py:160`). [L11]
- **B15. An input fingerprint**: a hash of the canonical inputs, sorted, on every ledger line. [L19]
- **B16. What every ledger line prints.** Could-not-look, never a missing figure. The cluster kind. The Kyverno and Flux versions. The scanner version and database date. The sourced share and the weakest basis. Who merged. [L07, L08, L21]
- **B17. A model's assertion never lowers a figure.** A model may judge on the clock only within thresholds, which is the owner's instruction (T75:172). The loop as designed uses none, because a count and a probe need none. [L09]
- **B18. Keep tuppence's and ludlow's size and tolerance as two what-if inputs.** They are the only real cases where tolerance cannot be reached. [L22]
- **B19. The saturated message.** Control ids come from the ico feed as plain strings, labelled editorial. The "fix a control" lever is recorded as parked. The levers must never become exemptions. If insurance returns: premium = (1 + load) x E[max(L - D, 0)] and what stays with the firm = E[min(L, D)]. One issue is opened per saturated episode, assigned to the person named in `party.yaml`. The owner foresaw a deadlock and a "reconciler stage" (AT:2857); none is designed. [L04, L13, L23, L25]
- **B20. Could-not-look is a tested third outcome,** never a pass and never a fail. Probe unreachable, reference failed, no pods found, feed unreadable: each has a test that shows no verdict and no move. [L08, L15, L22]
- **B21. `cage-ineffective` is a tested outcome.** A capability `rungs.yaml` declares closed at the commanded rung, measured open on settled pods, gives red, no further notch and the capability named. Without it the loop climbs on declarations alone. [critic]
- **B22. At most one tightening pull request is open.** While it waits, each cycle appends a ledger line marked `waiting_on_merge` and opens nothing. [critic]
- **B23. Print `bound: upper`** on every priced row whose penalty rate or fine tier is unsourced. Driftwood's GBP 16,280,871 is 18.9% of turnover a year in fines: a bound, not an estimate. [critic]

### C. `probe.py`, the inventory and the harness

- **C1. Bracket every network probe.** Reference first, then the caged pod, then the reference again. The caged silence must persist across at least four reads three seconds apart. If the reference fails before or after, the result is could-not-look. What stays unobservable: an outage wholly between two working reference reads. [L05, L18]
- **C2. A rung counts as measured only if the cage acted.** Require the cage's stamp on the running pod and the policy's own ready status. A policy that is installed and ready but has not rewritten the pod is could-not-look. This was measured live. [L05, L12, L18]
- **C3. Read the real exit code from a marker in the pod's output.** `kubectl exec` returns 1 both when the command failed and when it never ran. [L18]
- **C4. Transient pod states, an unscheduled pod and an apply that made no pod are could-not-look,** not verdicts. [L18]
- **C5. The reference sits outside the cage.** Its own Namespace, with no governed label, rung or version claim. The comparison is void if it carries a stamp or any network policy selects it. Run it on the same node as the caged pod. [L04, L06, L18, L21]
- **C6. A network policy the probe cannot evaluate is never treated as match-all.** A silence no policy explains is not credited to the cage. [L18]
- **C7. `rungs.yaml` names only capabilities a probe can tell apart.** Today restricted and quarantine share one network shape. Make them differ or merge them. [L12, L18]
- **C8. A measured FALSE is never downgraded to could-not-look** by aggregation. Red outranks could-not-look. [L18, L22]
- **C9. Clean-up waits until the probe's Namespace is gone.** A failed clean-up is kept as evidence. An unreachable cluster creates nothing. [L18, L20]
- **C10. An empty list is silence, not yes.** Wait for the objects the cage generates, not only the ones applied. This took three failed rounds to learn. [L08, L20]
- **C11. The harness waits in an asserted order**: admission webhook ready, then Flux, then apply, then waits. A test reads the steps back. A pass that only came from an unrelated timeout counts as not looked. Download into a temporary directory, never the checkout. [L10, L20]
- **C12. Restart the in-cluster git server after a reseed.** [L18]
- **C13. Serving is measured on running pods.** A cage bundle that lacks its priority classes is a refusal that looks like a cage, and must read as `serving-lost`. So must a pod that is admitted but never starts. [L05, L12]
- **C14. Reach is measured on a live connection, never predicted from YAML.** Poll through the gap before the network programs the rule. [L06, L12]
- **C15. Inventory.** Digest-pinned images only; an image without a digest is an instrument fault. Pin the scanner by checksum with a timeout. Read the commit Flux applied. An empty scan is still a required instrument. An unlisted flaw is a named absence, never a guess. The editorial frequency multiplier is unsourced, so it may only raise. Open a pull request only when the set of ids changes. Price from digests scanned this cycle and never cite a stored report: driftwood's stored citations already dangle. Refuse Kustomize image transforms. Redact tokens from output. Drop the old headline-only rule, because means add. Fixtures: tuppence's log4j row, and one real scanner report. [L05, L11, L21, L22, L26]
- **C16. Still to be written.** Probing capabilities on the workload's own pods, and counting served requests. Neither exists. Whether the workload images carry a shell: could not determine. [L18]
- **C17. Test that a pod label loosened by hand is corrected at the next admission.** [L15]

### D. Cage version 8 and its consumer test

- **D1. Start from the 7.0.0 shape**: `policies.kyverno.io/v1` and `string(variables.tier)`. [L06, L12]
- **D2. Priority.** A priority class name must come with the matching priority value and `preemptionPolicy: Never`, or the cluster refuses every pod. Ship the classes with the cage, or drop all three fields. [L12, L13, L21]
- **D3. Write `privileged: false` beside `allowPrivilegeEscalation: false`,** or the API server rejects the pod. [L12]
- **D4. Force host network, host process and host IPC off.** A host-network pod once escaped the isolated rung. [L12]
- **D5. Every rewrite only tightens.** Limits are the lower of the pod's and the rung's. A pod's own stricter setting survives. The baseline rung once wrote `runAsNonRoot: false` over a pod that declared `true`: test for it. [L06, L12]
- **D6. Full body when a pod is created, labels only when it is updated.** Never rewrite a container list on update. Never write `validationActions` on a mutating or generating policy. [L12, L13, L15]
- **D7. Network rules.** Generate every restricting rung's rule up front, with one owner per name, or use static rules per governed Namespace. A rung move once opened a window with no rule at all. [L12]
- **D8. Scope with `matchConditions`,** not an object selector, which Kyverno flattens into one shared webhook. [L12]
- **D9. One rewriting policy writes the cage.** Two once produced a pod labelled isolated with baseline's priority. The move from version 7 to 8 is one change. [L12]
- **D10. Substrate Namespaces are never governed.** Test what happens to a pod in `kube-system`, `flux-system` and `kyverno`, and in a Namespace with no rung label. Infrastructure is a role, not a rung. [L05, L07, L12, L13]
- **D11. Cage every pod in a governed Namespace,** claimed or not, and harden init containers too. [L12]
- **D12. Name the known holes in `rungs.yaml`.** A host-path volume cannot be removed by the cage. [L12]
- **D13. Drop the placeholder firewall sidecar and its filter together.** Its image exists in no registry. [L12, L18, L20]
- **D14. No reduction column in `rungs.yaml`.** A cost column only if the owner answers decision 6 that way, and then each cost carries a basis. Today's four costs are typed with no source (`platform/graded/cage.py:82-111`). [L12]
- **D15. The rung lives on the Namespace only,** because a pod label can be forged. The copy stamped on pod templates uses its own key. The settle check reads a mark only the cage writes. [L05, L06, L17]
- **D16. The consumer test runs on a pinned, checksummed Kyverno 1.18.2** and checks the version before it runs. Any other version, or no Kyverno, is could-not-look, never green. Version 1.19.1 does not compile the older body. [L06, L07, L08, L13, L14, L21, L22]
- **D17. The test must not pass on nothing.** Refuse rows that read Excluded. Require one summary, at least one pass, no fail, and every policy named by a row. Assert at least one rule loaded. Judge generated network policies by the documents written, not the result table. Pass Namespace labels through a values file. Stamp the version label each served body scopes itself on. [L13, L14, L18, L21]
- **D18. "Each rung closes at least what it closed last release"** is tested by running old and new bodies over the same pods, not by comparing declarations. [L14]
- **D19. One small test that no cage body carries a deny-shaped action,** and no rung sets replicas to nought. [L05, L08]
- **D20. Policy bodies stay deterministic and date-free.** The price may move with the date. The verdict of a policy may not. [L05]
- **D21. On the cage served today, the measured serving range is baseline.** From restricted upward, traffic is admitted from the same Namespace only. [L12]
- **D22. Name the delivery route for version 8's bodies.** Flux cannot verify this estate's signed tags, so the signature check happens in CI. Say whether the two old guard policies are replaced or dropped. If the bodies come by tag and the in-cluster verifier stays, carry its 60-second clock-skew fix (ADR-0027). [L15, L17, L19]

### E. The loop's workflow, the caller and CI

- **E1. Pin the platform loop as a tag and a commit together.** Verify the tag resolves to the commit, and verify its signature offline against the anchored identity. A `uses:@tag` reference checks no signature. [L15, L20]
- **E2. Fetch full history and tags.** Re-fetch the annotated tag. A missing tag is could-not-look, never "unsigned". Name an explicit ref on every cross-repository checkout. On a pull-request event use `HEAD`, not `head.sha`. [L08, L13, L20]
- **E3. Split the read-only measuring job from the writing job.** Never check out another party's `main` under a write token. Do not persist credentials in the checkout. [L07, L08]
- **E4. Ledger writer rules.** Record only from default-branch runs. One run at a time per ref, never cancelled. Use `!cancelled()`, not `always()`. A clock never grades its own run. Stage only the ledger file and refuse anything else. The loop never pushes `main`. The ledger sits on its own branch, because `main` requires review and the forge refuses the Actions app as a bypass actor. [L08, L20]
- **E5. Checks may not run on the loop's own pull requests.** Work done with the default token starts no workflow. Pull requests opened by the app or Renovate can sit with zero checks until a person approves the runs. Treat a proposal with no check result as could-not-look. So the merge job of decision 2(b) runs the diff check itself and does not wait for a check. Renovate's pull requests are in the same position (`driftwood/.github/workflows/renovate-run.yml:78`). Opening a proposal at all needs the organisation setting that lets Actions create pull requests. [L08, L20, L26]
- **E6. A required check has no path filter.** [L20]
- **E7. Exactly one Renovate.** `enabled: false` in the config plus the force setting in the runner. Node 24. A regex manager that bumps tag and commit together, on adjacent lines. `allowedCommands` is a glob unless wrapped in slashes. [L06, L17, L20]
- **E8. Every binary is pinned by version and checksum** and downloaded into the runner's temporary directory. [L20]
- **E9. Wrap `set +e` around any exit status that must be read.** Could-not-look must be reported, not aborted. [L20]
- **E10. Install Kyverno with server-side apply, and wait for its webhooks before applying policies.** [L20]
- **E11. The loop runs on a schedule, not only on a push,** because the price depends on the date. [L20]
- **E12. An unreadable list of closed proposals is could-not-look,** never an empty list. [L20]
- **E13. A clock may propose and append observations. Only a reviewed change enacts.** Subject to decision 2. [L05, L07]
- **E14. A guard counts only if a test reads its registration back** and asserts the shipped default. [L09]

### F. Signed releases

- **F1. The signing workflow stays at `.github/workflows/cut-release.yml`** in platform and in ico, with the identity pattern unchanged. Otherwise four driftwood files change in the same commit. [L16, L23]
- **F2. Sign with the transparency-log proof embedded,** then verify in the same job, before pushing. [L15, L16, L24]
- **F3. Refuse a malformed tag and an existing tag. Push branch and tags atomically. Pass inputs through the environment.** [L14, L16]
- **F4. Keep the manual-dispatch route.** A tag pushed with the default token triggers no second workflow. [L15, L16, L23]
- **F5. Pin the signing tool by version and checksum.** [L16]
- **F6. Before signing, run the consumer test and the label-only control** in place of the old gates. Cut the workflow down in place, cut the 8.0.x tag from the cut-down file, and see driftwood's tool check pass before the old steps go. [L14, L16]
- **F7. The tag for cage 8 is `policy/v8.0.0`,** following platform's existing tag `policy/v7.0.0`. [L16]
- **F8. Carry the two guard tests, about 130 lines,** and the three-outcome rule in `lib.sh`. Prove the identity pattern against real signed tags, with cases that must fail. [L15, L18]
- **F9. A Flux source that follows a tag needs the tag reachable from a branch.** The target avoids this by following `main`. [L02]

### G. The publishers: ico v5 and feeds v5

- **G1. Ico v5.** Copy the sources and dates for each fine from `94-studied-firms.md` into the feed rows. Drop `control_weights` or carry the ids as plain strings. `penalty_rate` stays absent until a fetch counts the regulator's register. Move driftwood off v3, whose converter has none of the fixes. Rewrite the release check that is pinned to an old platform tag. [L06, L11, L23, L25]
- **G2. Feeds v5.** `needs` on every row. A row is open while every capability in its `needs` list is open; closing any one closes the row. Fewer needs when unsure; empty needs never closes. Each need cites an outside source for the attack technique, and a need without one is ignored. The list is still an editorial claim, and the ledger prints its basis. Rows for losses outside the cage. A basis on every frequency. Signed as a new tag before any ledger line reads it. The second driftwood row, `scheduled-agent-misuses-write-credential`, has no published magnitude (`feeds/threat-register/v4/feed.json:44`, `:64`): v5 publishes one with a basis, or the row stays unpriced and driftwood can reach only `within-partial`. It is not dropped while a scheduled job holds a write credential. [L24]
- **G3. Keep the fetch rules.** Primary sources. A bounded retry. Refuse on an empty page. A checksum of every raw response. [L24]
- **G4. The exploited-flaw list must not ride a hand-merged, hand-cut tag.** No workflow in feeds holds the App's key, so freeing this hop needs that grant from the owner (decision 2). The regulator's path in ico stays with a person: ico has no fetcher of the register today (`ico/.github/workflows/fetch.yml:23-24`). [L24]
- **G5. Trim the feeds release gates in the same change that parks the unused feeds,** or v5 cannot be cut. Move driftwood's pin off the recovery-expense tag family. Carry the feed-envelope check inside feeds, or keep its pin on the old platform tag. [L24]
- **G6. Clean thoroughly before switching to an orphan branch,** and reset the declared bump after each cut. [L24]
- **G7. Move the basis wording into the feed rows,** so the sourced share and weakest basis can print. [L19]
- **G8. Say in the row schema that overlapping contingencies are not summed.** [L21]

### H. Driftwood

- **H1. The workloads depend on the cage,** so a cold cluster never admits uncaged pods. Admission fires once. [L17]
- **H2. The nginx workloads need user 101 and writable scratch directories** to survive a read-only root. [L17]
- **H3. Every manifest names its Namespace,** or Flux puts it in `default`, outside the cage. [L17]
- **H4. The Flux path is `./gitops/apps`.** [L17]
- **H5. Every workload carries the policy-version claim,** and it moves with the cage's major version. [L17]
- **H6. One installer per cluster-wide name.** [L17]
- **H7. The engine is pinned by version and checksum.** [L17]
- **H8. Keep the demonstration-party disclaimer.** The estate names a real regulator. [L04, L17, L23]
- **H9. The tolerance gains a basis line. The floor goes only on a dated decision of the owner's.** [L17]
- **H10. Copy the three sample logs and their pre-registration file to the ledger branch,** byte for byte. [L18]
- **H11. `party.yaml` drops its old blocks only in the change that removes the code that requires them.** [L17, L21]
- **H12. Renovate's post-upgrade task goes in the change that cuts the generated tree.** [L17, L20]

### I. `LOOP.md`, ADR-0039 and the hub's records

- **I1. The owner's rules, each with its date.** Never an exemption ledger (AT:2815). Always caged; only the cage's spec changes (AT:2780). No deliberate deny (T75:79). A workload may degrade until it is too expensive to run or does not work (AT:2962). The fine is "for a breach" (AT:324). Monte-Carlo was asked for by name (AT:2263). A model may judge on a clock "within thresholds" (T75:172). A refused proposal is a "flood guard with a half life" (RA:28). The merge is theatre, but the story is that a person merges (T75:80). [L01, L03, L04, L06]
- **I2. A bare agree is not consent** (AT:3060). Keep the three decision labels. [L01, L03]
- **I3. Where could-not-look came from**: the post-mortem of 2026-08-25. An absence is not a pass. The date is part of the number. [L02]
- **I4. A short lineage paragraph** with the 2022 thesis line and "policy carries its why". [L02, L06]
- **I5. ADR-0039.** It defines notch, tolerance and the stop, which no record defines today. It says it reverses ADR-0022's tighten-only and sides with ADR-0015. It says why this ratchet is not the one ADR-0026 rejected. It reverses the ordinal pound. It lands in the same commit as the first banner that names it. [L03, L04, L05]
- **I6. The glossary.** Tolerance replaces appetite. Exposure is the probe-priced figure. Remove tighten-only, floor, and the wording that contradicts release by proposal. [L04]
- **I7. The README.** Licence, disclaimer, a pointer to `LOOP.md`. Remove "Audit and Deny are rungs". [L04]
- **I8. Keep the agent pointers working**: `CLAUDE.md`, a trimmed `docs/agents/issue-tracker.md`, `domain.md`, the licence. [L02, L06]
- **I9. `LOOP.md` says what is parked and that no live figure reads it**: the twin lines of tuppence and ludlow, the control lever. [L07, L13]
- **I10. One line on checks held for approval** (E5). [L26]
- **I11. The index, the approvals and the five recovered records** (A2, A3, A4). [L01, L10, L26]
- **I12. The permission list in the hub's settings file is the owner's.** [L09]
- **I13. Derive what you assert.** One glossary entry was wrong twice because the record said `isolated` while the shipped body said Deny. A record states only what a test reads back from the thing itself. [L04]
- **I14. Decide where the guard on agent writes lives once the twin is parked,** and say once that a person merges release proposals. Today the guard is a mode file with an end date, inside the twin, and the App merges only while that window is valid (`hub/docs/adr/0037-*.md:42-51`). A standing permission for decision 2(b) would be recorded in `hub/LOOP.md`. [L03, L09]
