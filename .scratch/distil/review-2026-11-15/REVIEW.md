# The review of every line, 2026-11-15

All times are UTC on 2026-11-15 unless a date is given. This file is for a reader who has only the hub. It says what the owner asked, how the review was done, what it found, what landed, what was refuted, how the design questions were ruled, and where the rest is.

The release has not happened. The loop's first release of a notch is due from 10:55 on 2026-11-22, and that direction has never run live. Nothing listed below as "after the release" has landed.

## The owner's words

- "Adversely review. Every LOC must be justified and earn its keep (not literally, don't condense lines for the sake of it)".
- On Renovate, earlier the same day (already recorded in hub pull request 327): "It should be everywhere but configured correctly".

Read as, by the assistant: every block of code must have a reason that holds, and what holds nothing goes; lines are not squeezed together to lower a count. How the review was run, and the rule for what landed before the release, are the assistant's choices, delegated (ADR-0025). `../DECISIONS.md`, "15 November: the review of every line", records the reading.

## How it was done

1. **Evidence first.** One statement or condition at a time was removed from `loop.py` and `probe.py`, and the 38 unit tests were run each time: 884 changes, 209 that no test noticed.
2. **Twelve reviewers**, one for each part, gave a verdict on every block: keep, remove, merge, untested or defect. The parts were `loop.py` in two halves, `probe.py`, the tests, the harness, the cage, driftwood's workflow, the adopter and the READMEs, the publishers, duplication across repositories, who reads each value, and the delegated decisions.
3. **A second model, codex**, reviewed the same code on its own: 54 items. Four of them, a missing licence file, were wrong, because its copy of the code left the licence files out.
4. **Ten verifiers** then tried to refute every finding of both, running each removal, test and fix in a private copy.
5. **The design questions** went into 17 decision memos, D1 to D17, some in parts (D2a, D2b and so on). The assistant ruled on each (delegated).
6. **The rule for what landed now.** Only rulings off the release path that do not change the cage's rules. Everything else waits until after the release, and `LATER.md` lists it with its exact change.

| Count | |
|---|---|
| Statement removals on `loop.py` and `probe.py` | 884, of which 209 no test noticed |
| Blocks judged by the twelve reviewers | 1,399 |
| Blocks kept, each with a stated reason | 1,143 |
| Findings raised by the reviewers | 254 |
| Items raised by codex | 54, four of them wrong |
| Rulings after the verifiers | 164: 120 confirmed, 18 refuted, 26 design questions |
| Decision memos | 17 (D1 to D17) |

The full block-by-block reports, the verifiers' adjudications, their private copies and rehearsal scripts were working files of the session. They were not kept. `LATER.md` carries every change still owed, with its exact text.

## What landed

Each merge was the app's.

| Repository | Pull request | Merged as | Tag | What it carried |
|---|---|---|---|---|
| platform, ico, feeds, driftwood, api, storefront | platform 80, ico 16, feeds 24, driftwood 143, api 7, storefront 23 | | none | A `renovate.json` for each repository (below) |
| platform | 83 | `1b7fcf9` | `policy/v8.0.3`, cut by dispatch (run 43750343790) | The loop's and the proof's changes (below). `unit` and `cluster` green on the pull request and on `main` |
| ico | 19 | `ab91903` | `v5.2.0`, cut by the merge (run 43749613233) | Keys nothing reads went; the test holds the fine statuses |
| feeds | 25 | `992d860` | `threat-register/v5.2.0`, cut by the merge (run 43749627685) | The false note corrected; keys nothing reads went |
| driftwood | 144 | `9ff3a9b` | none | The platform pin to `policy/v8.0.3`; README made true |
| driftwood | 145 (`loop/pins`, the loop's own) | `e548c96` | none | The pins to ico `v5.2.0` and feeds `threat-register/v5.2.0` |

**Renovate.** Each repository has its own `renovate.json`, as the owner answered:

- Actions stay pinned by commit, with a `# v4.4.0` comment Renovate can follow.
- Downloads checked by a sha256 (kind, Kyverno, gitsign) are listed on the dependency dashboard, and get a pull request only when ticked. The pull request says to replace the sha256 by hand.
- The `nginx` image is pinned by digest with no tag, so Renovate could only move it to `latest`. That too is held on the dashboard.
- Nothing merges by itself.
- Driftwood's `party.json` pins stay the loop's. No Renovate manager reads that file.

Every configuration passed `renovate-config-validator --strict` (Renovate 44.239.1), and a second agent checked it key by key against Renovate's documentation. The hub has no `renovate.json`: its organisation's archived `renovate-config` repository sets `onboarding: false`, and the hub, which has nothing to update, has never had a Renovate pull request. One thing is held until after the release: the `# v4.4.0` comments on the three checkout lines of driftwood's `loop.yml`, so that Renovate opens nothing against `loop.yml` before then (`LATER.md` item 5.4). Renovate has since opened `actions/checkout` v7 pull requests in platform (81) and ico (17), which the app merged after their checks passed (`02374c5`, `0f7d247`), and dependency dashboards in platform (82), ico (18), driftwood (33), api (3) and storefront (3).

**Platform pull request 83.** Nothing under `cage/` changed: the cage is still version 8.0.2.

- A tolerance amount of 0 or below is refused, as a share of 0 or below already was.
- The proof's check that Kyverno has not rewritten the cage for pod controllers is red when its query fails. It had read a failed query as green.
- Removals, each shown unneeded: the two shebangs; the probe's no-pods guard, which the probe-pod count already makes (an empty Namespace now reads "0 probe pods, not one"); the unused `--settle-seconds` flag, with 600 seconds now a named constant; an argparse `prog`; `next_pin`'s fallback for a tag family with no tags, which cannot happen because tags are never deleted; a filter on `git ls-remote` output; an unused `read_party` call; a duplicated tag-exists refusal in `cut-release.yml` (`git tag` refuses an existing tag itself); an unread port on the reference sink; the fixture's untrue header; and three tests that held nothing alone (`test_mean`, `test_predicted_and_goal`, `test_unreachable_counts_cost`), with a fourth command-line run folded into `test_could_not_look`.
- Tests for every reachable guard that no test held, each shown to fail without its line. The tests went from 38 to 42. The statement-removal run on the new code made 877 changes and the tests caught 832. Each of the 45 left has a reason: it is removed later, it is a design decision, or it cannot be reached.
- `harness/diagnose.sh`, one script that `up.sh` and `proof.sh` both call when a run is red.
- README sentences made true.
- New proof checks that the cage, as it is, strips host access, privilege and capabilities from a pod that asks for them; falls to `isolated` outside a governed Namespace; writes no rule for a pod that claims no cage version; writes both restricting rules; and writes none for a pod created at `baseline`. The first two are server-side dry runs through Kyverno's admission, which start nothing.

**Ico pull request 19.** The feed lost keys nothing reads (`feed`, `published_by`, `published_at`, and each fine's `year`), and the note on the change of date at the end of Doorstep Dispensaree's litigation text. No number, status or source changed. The test now holds the closed set of fine statuses. Before, a misspelt status passed the test and silently stopped that fine from pricing: in the verification, a typo in British Airways' status lowered driftwood's figure with no warning. It also holds a source for every fine, and a tier rate of at most 1. The `cut` job refuses a version that is not above every existing tag, no longer reads `CUT_ON_MERGE`, and leaves the version's form to the `test` job it needs.

**Feeds pull request 25.** The note said "Overlapping rows are never summed", which was false: the loop adds every open row. It now says "The reader adds every open row, so rows must not overlap." The unread envelope keys went. A need's source must say something: an empty source passed the test, and the loop then ignored that need. The `cut` job changed as ico's did.

**The repository variable `CUT_ON_MERGE`** was deleted from ico and feeds after both workflows stopped reading it (D7). A merge that changes a feed's `version` cuts its tag.

**Driftwood pull request 144.** The platform pin moved to `policy/v8.0.3` at `1b7fcf9`. The README's row on triggers now says what runs a cycle: once a day, on dispatch, on each pull request but the loop's own, and after a push to `main` that changes `party.json` or `gitops/apps/`. Its guide to the ledger, and the line on `looked` and `why`, were made true. The tolerance basis lost the hand-typed "GBP 430,000 at this turnover", since the loop computes the figure from the share. `.gitignore` went. The pull request's own cycle (run 43750427912) ran the new platform: `within` at GBP 17,290.68, release-ready. The merge started run 43750805019, which wrote ledger line 15 and opened pull request 145 for ico `v5.2.0` and feeds `threat-register/v5.2.0`. The checker passed it, and the app merged it as `e548c96`. Run 43751179363 then wrote ledger line 16 on the new pins: `within`, GBP 17,290.68, release-ready.

**Where driftwood stands.** It pins platform `policy/v8.0.3` (`1b7fcf9`), ico `v5.2.0` (`ab91903`) and feeds `threat-register/v5.2.0` (`992d860`). The ledger has 16 lines. Lines 11 to 16 are all release-ready, so the dwell that started at 10:55:04 is unbroken. The loop is still waiting it out.

## What was refuted, and why it matters

18 findings did not survive. These are the ones worth naming:

- **Removing `test_monte_carlo_agrees`.** It is the only expected value in the tests that is not typed from the formula itself.
- **Removing the check of the written line's key order, and the "moved" case of the dwell test.** Each is the only check of its behaviour.
- **"The probe tests only the first declared port", as a defect.** It is true, but it is what contract 4.2 step 8 chose, and it cannot move money on today's cage (D17).
- **Codex's missing licence files.** The files exist; codex's copy left them out.

## The design rulings

The assistant's, delegated.

| When | Rulings |
|---|---|
| Landed now | D7 (`CUT_ON_MERGE` goes); D8c and D8d (keep the cage's guards, and the proof now checks them); D8f (a unit test that the copies of the cage's version agree, and a README line that the tie to the tag is kept by hand); D9 (keep `measure` mode, and test its write gate); D10 (keep `turnover_as_of` and keys like it, and complete driftwood's guide to the ledger); D11 (the envelope keys and each fine's `year` go, in ico `v5.2.0` and feeds `threat-register/v5.2.0`, and the fixture's untrue header goes); D12 (tests for the lines the release is the first to use); D13 (one copy of each hand-copied README fact); D16 (ico's test holds the set of fine statuses) |
| No change | D1 (keep the margin, but correct its stated reason: see below); D14 (no gate on a platform tag from the cluster proof); D15 (the pin repositories stay unfixed in `pins.sh`); D17 (the probe tests the first declared port) |
| After the release | D2a and D2b (the dwell counts a `could-not-look` line by its own `release_ready`, and no longer passes over a line with no verdict); D3a and D3b (`within-partial` exits 2, and release-ready needs every row priced); D4a and D4d (the ledger fields `bound`, `looked`, `reference` and `unpriced` go); the code parts of D4b and D4c (a `cost_basis` must start `unsourced:` or `measured:`, a dead clause goes, and a penalty rate whose basis kind does not match is refused); D5 (the proof's first run and `--no-netpol` go); D6 (no branch pins); D8a, D8b and D8e (the cage's limits and read-only root filesystem go, and quarantine's DNS allowance after a cluster run). The cage changes come in one new cage version, with the pods' claims moved together |

**D1, the margin.** The records said the margin is there "so one release does not cause the next tightening". That is wrong. On the same inputs a release never causes the next tightening, margin or not: none of 59,022 random releases did. What the margin does is hold the cage tight against a later rise in a publisher's number. On today's inputs it decides nothing: `baseline` is predicted at GBP 25,697.44, and the margin bites only between GBP 344,000 and GBP 430,000. Removing it would move the published thresholds, so it stays. The records now give the corrected reason (`../DECISIONS.md` row 1, `../../../LOOP.md`).

## Where the rest is

- `LATER.md`, beside this file: every change that waits until after the release, with its exact text, its tests, what it proves and what it does not, and the order it lands in. Its line numbers are those of platform `policy/v8.0.2`, so each item quotes the old text.
- `../CONTRACT.md` section 11, "After the review of every line": the contract's own account, and which of its sections changed.
- `../../../LOOP.md`: where the loop stands.
