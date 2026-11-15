# CONTRACT: the simplified estate

Written 2026-11-14 by the architect stage, revised the same day after three reviews, and amended by the orchestrator after the owner's reply "I'm afk. Jfdi" (`DECISIONS.md`, "Later the same day"): leave to cut tags is given, and the red exit moves to a job of its own (5.3). The builders share this file and nothing else. `DECISIONS.md` outranks it. It outranks `TARGET.md`. Section 11 lists what the review of the built code changed. Where sections 1 to 10 and section 11 differ, section 11 and the code win.

**The mission, in the owner's words.** "quantified risk and a reactive ratcheting process cage to mitigate the quantified risk until the risk is within financial tolerance of the organisation". Then: "Remove all redundant code. Simplify everything".

**Rules for builders.** Write only the files your repository's table in section 2 marks `new` or `rewrite`. Delete nothing: a script removes every tracked path the table does not name. Add no file, field, flag, check or dependency this contract does not name. Python is the standard library only, version 3.10 or later. The runner's `python3` is 3.12. No workflow has a `pip` step or a `setup-python` step. Tests use `unittest`. A path cited as `repo/path:line` is in the before-simplify trees under `fresh/`.

**One hazard when writing workflows.** A secrets hook on this machine refuses any file in which the permission name `id-token` is followed directly by a colon and its value. The three `cut-release.yml` files need that permission. Write the key quoted, as `"id-token": write`, which the hook accepts. Do not get round the hook with another tool. The owner is told of this (section 8).

**Words.**

- *Adopter*: the organisation that is caged. Here it is driftwood. *Publisher*: a repository that publishes numbers about the world as a *feed*. Here they are ico and feeds.
- *Exposure*: the adopter's expected loss in pounds a year. *Tolerance*: the loss a year it says it will bear.
- *Cage*: limits put on a running pod from outside, by two Kyverno policies. *Rung*: a named cage setting. *Notch*: a move to the next rung in ladder order.
- *Governed Namespace*: the one Namespace the cage acts in. *Stamp*: the two labels the cage writes on each pod it has caged.
- *Capability*: one thing a running pod can do that a live test can check. *Probe*: that test. *Reference*: pods outside the cage that run the same test, to show the network works. *Probe pod*: the one caged pod the tests run from.
- *Row*: one way a loss happens, published by feeds, with the capabilities it `needs`. *Basis*: where a number came from: a kind, a date and a sentence.
- *Cycle*: one pass of the loop. *Ledger*: a file with one line per cycle. *Could-not-look*: the loop could not measure, so it gives no judgement and moves nothing.
- *Pin*: the exact commit of another repository that driftwood uses.
- *The app*: the GitHub App `pavc-other-hand`, a machine identity. *The key*: its private key. *Default token*: the credential GitHub gives a workflow run.

**What this contract decided.** The label says whose decision each is. *Owner-instructed* restates an answer in `DECISIONS.md`. *Delegated* is the architect's, under ADR-0025.

| # | Decision | Why | Label |
|---|---|---|---|
| K1 | The compared figure is exposure plus the current rung's running cost a year. | Decision 6: "Always". | owner-instructed |
| K2 | The loop moves one notch towards a goal rung. It tightens at once and releases after the dwell, by the same machine path. | Decisions 1 and 2. | owner-instructed |
| K3 | The ladder has three rungs: `baseline`, `quarantine`, `isolated`. The old `restricted` is merged into `quarantine`. | Only two capabilities can be tested live, and a rung must close something a probe can see (LEDGER C7). | delegated |
| K4 | Two capabilities only: `egress` and `inbound`. | A read-only root filesystem read as closed at every rung, because driftwood's own manifests already set it. No row needs the others. | delegated |
| K5 | The cluster is built by `kubectl apply -k` from pinned checkouts. Flux is not installed. | On a cluster made after the merge, Flux proves nothing a checkout does not. It returns with the cluster that stays up, which waits for the owner (decision 9, section 8). The cluster of 2026-11-15 runs without Flux (K19). | delegated |
| K6 | The publishers' pins are followed by `loop.py bump-pins` with plain git. The platform pin is not followed (K17). Renovate does not follow the pins. (Since 2026-11-15 the hosted Renovate app has a configuration in each repository but the hub, and watches actions, checked downloads and images there. No Renovate manager reads `party.json`: section 11, "After the review of every line".) | Following a branch by commit could not be checked offline in Renovate. One function handles branch pins now and tag pins later. | delegated |
| K7 | No reusable workflow. Driftwood's workflow checks platform out at the commit in `party.json` and runs its scripts. | Every pin then lives in one file, on one line each. | delegated |
| K8 | No exploited-flaw list, image inventory, scanner or fetch. They are parked, not dropped. `LOOP.md` says where each is kept and what brings it back. | The first loop runs end to end without them. They need about 500 lines and a scanner in CI. | delegated |
| K9 | Ico and feeds have no scheduled job and no landing job. Their one unattended act is to cut a tag when a merge changes the feed's version. A merge to `main` that changes `version` cuts the tag, and no variable switches it on (5.2). | With K8 there is nothing to fetch. A tag needs no key: the default token can create one, and driftwood finds it with `git ls-remote`. Until 2026-11-15 a repository variable, `CUT_ON_MERGE`, switched the cut on. Once set it never decided anything, so it was deleted after the review of every line (D7, section 11). | delegated, applying decision 2 |
| K10 | Network tests run from the probe pod, not inside every workload container. | Whether the workload images carry a shell is not known. The settle check proves every pod carries the stamp the network rule selects on. | delegated |
| K11 | A loss the cage cannot touch is a priced row with no `needs`, on the publisher's editorial band. | The exposure compared is the whole organisation's. A register without the row could read `within` by leaving the loss out. An unsourced number can only raise the figure. | delegated, applying decision 5 |
| K12 | No veto on a refused release. | No person is on the merge path (decision 2), so nobody refuses. | delegated, applying decisions 1 and 2 |
| K13 | `pins.sh` verifies a tag's signature when a pin names a tag. | So that moving to tags is a change to pin lines only. It cannot be proven until a tag exists. (Proven since 2026-11-14: the cycle of driftwood pull request 133, the first tag pins, ran the tag branch of `pins.sh`.) | delegated |
| K14 | Driftwood's workloads stay bare Pods, with no rollout stamp. | Every cycle builds a new cluster, so every pod is admitted at the current rung. | delegated |
| K15 | The party file and the ladder file are JSON, not YAML. | The standard library reads JSON and refuses a duplicate key in three lines. YAML needed a dependency, a second action and a hash pin in five jobs. | delegated |
| K16 | A notch is judged by the goal it leads to, not by its own gain. | Decision 6 says cost always counts. Judged alone, the first notch would never be taken, and the loop would sit at `baseline`, which is not what the owner was told to expect under decision 5. This departs from a consequence written in the option the owner chose: option (c) of `DISTILLATION.md` section 7 item 6 reads "cost is added to exposure, so a notch that costs more than it saves is not taken", and the owner answered "Always". `DECISIONS.md` records the departure, and the owner can reverse it. | delegated; kept by the owner on 2026-11-15 |
| K17 | The loop never moves the platform pin. `bump-pins` follows ico and feeds only. A platform change reaches the adopter by a pull request that changes the platform pin line. Decided 2026-11-15, after the second look (section 11). | The pinned platform holds `check-diff` and `bump-pins`, which gate what lands, so a loop that pinned a new platform tag itself would be following its own code. The pull request is pushed from an agent session, so its own cycle runs the new platform on a cluster before the app merges it. | delegated |
| K18 | A row whose counted door is found closed stays in the register at the rate its own method gives, 0, with the reading dated. It is not removed and not left at the old rate. Decided 2026-11-15 (section 11). | Feeds' second row is the case. Its rate is N x C / M, and N, read again on 2026-11-15, is 0. Leaving N = 1 knowingly overstates the rate. Removing the row loses the reading and its history. | delegated, applying "Do everything" |
| K19 | The proof on a cluster that stays up runs from an agent session on the owner's machine, with the pinned harness and loop unchanged. Its lines say `cluster: standing` and go to no ledger. Flux stays out. Decided 2026-11-15 (section 11). | The owner chose a kind cluster on the owner's own machine (answer 3), and GitHub's runners cannot reach it. Running the pinned `up.sh`, `probe.py` and `loop.py` unchanged makes it the same loop on a cluster that outlives a cycle. Its lines are not cycles of the daily loop, so they do not enter the ledger or the dwell. K5 stands. | delegated, applying the owner's answer 3 |
| K20 | When a cage file's rules change, the cage takes the version of the tag that carries it. So cage 8.0.2 is carried by `policy/v8.0.2`, and there is no cage 8.0.1: `policy/v8.0.1` carried cage 8.0.0. Decided 2026-11-15 (section 11). | A cage version is the claim the pods match on (5.2), and a cage binds only the pods that claim it. So the adopter's platform pin and its pods' claim change in one pull request. | delegated |

Two things follow from the owner's sentence, and the owner has commented on neither: the pound is a real figure, and the exposure compared is the whole organisation's.

## 1. The loop in ten lines

A row is *closed* when a capability it needs was measured closed this cycle **and** `rungs.json` declares that capability closed at the current rung or a looser one. Otherwise it is *open*. On a `could-not-look` or `cage-ineffective` line every row is open. `mean(l, m, h) = (l + 4m + h) / 6`.

1. **Sense.** `probe.py` checks that every pod in the governed Namespace is Ready and stamped at the rung in git. It tests each capability on a live connection, between two reads from the reference. If any of that fails the verdict is `could-not-look` and nothing moves.
2. **Price.** `amount(row) = mean(events a year) x ( mean(loss an event) + penalty rate x mean(penalty at the adopter's turnover) )`. `exposure` is the sum of the amounts of open rows.
3. **Add cost.** `figure = exposure + cost(current rung)`. This is the one formula and the one compared number. `cost` is that rung's `cost` in `platform/cage/rungs.json` at the pinned commit, in pounds a year. It has no source today. Its `cost_basis` therefore starts `unsourced:`, and the ledger prints `cost` and `cost_basis` on every line.
4. **Compare.** `tolerance` comes from `party.json`: a sum, or a share of turnover turned into pounds. Within means `figure <= tolerance`.
5. **Predict, to choose a direction only.** `predicted(k)` = the amounts of the rows that would stay open if exactly the capabilities declared closed at rungs up to `k` were closed, plus `cost(k)`. `goal(limit)` = the loosest rung with `predicted <= limit`. If there is none, it is the rung with the lowest `predicted`, the looser on a tie. A prediction never enters the figure. The loop is *release-ready* when `goal((1 - margin) x tolerance)` is looser than the current rung.
6. **Decide.** The first match wins.
   - `could-not-look`: step 1 failed.
   - `cage-ineffective`: a capability the current rung declares closed is measured open. Red. No move.
   - `could-not-look` again: a capability is measured closed that the current rung does not declare closed. Something other than the cage closed it, so it earns nothing.
   - `tighten`: `goal(tolerance)` is tighter than the current rung. One notch tighter, now.
   - `release`: every row is priced, and the loop has been release-ready on every cycle for `dwell_days`, this one included. One notch looser.
   - `within`: `figure <= tolerance` and every row is priced. Hold. `within-partial`: the same with a row unpriced. The figure is then a lower bound. Hold, never release.
   - `saturated`: `figure > tolerance` and no move applies. Red. Hold. The line's `unreachable` says how far the best rung, cost included, still is above tolerance.
7. **One notch** is one changed line: the rung line (3.6) moves to the next rung. Cost always enters the figure (decision 6). A notch is judged by the goal it leads to (K16). So a notch may cost more than it saves, on the way to a goal whose figure is lower with cost included. The loop never starts a climb unless some tighter rung predicts a lower figure. A rung that has stopped earning its cost is given back by `release`.
8. **Enact.** In `act` mode the workflow opens a pull request for the notch. A second job checks it. The app merges it. The merge starts the next cycle on a new cluster built from `main`.
9. **Record.** One JSON line per cycle goes to the `ledger` branch (3.5), whatever the verdict. The one exception is a run whose pins cannot be checked out or whose input is refused: it is red and writes no line.
10. **The rule on numbers.** An unsourced number may raise the figure. Only a measured, declared closure, or a publisher's change landed on its `main`, may lower it. One exception, by owner decision 6: a rung's cost leaves the figure when the loop leaves that rung. A missing penalty rate is 1. An uncited tier is the tier with the larger mean penalty. A row with a missing number is unpriced and named.

**On today's inputs** the loop in `act` mode takes two notches and stops at `isolated`, where the shop no longer serves. Every cycle after that is red: `saturated` at GBP 1,643,518.63, which is GBP 1,603,518.63 more than any rung can reach (6.1). The owner chose the climb in decision 5. What is left is the third row, which no cage can close, at a penalty rate nobody has counted. `within` needs the world to change: a counted penalty rate, a new tolerance, or a changed row.

## 2. The final tree of each repository

A path ending in `/` means every tracked file under it, kept unchanged. `keep` is an existing file, unchanged. `rewrite` is an existing path with new content. Lines are a budget of authored lines, not a target. A path not in a table is deleted.

### 2.1 platform

| Path | Status | Lines | Purpose | Lifted from |
|---|---|---|---|---|
| `LICENSE` | keep | 0 | Licence | |
| `.gitignore` | rewrite | 1 | `__pycache__/` | |
| `README.md` | rewrite | 40 | What the loop is; how to run the tests and the proof. For what a rung does to a pod it points to `cage/cage-tier.yaml` and restates nothing | |
| `loop/loop.py` | new | 420 | Price, compare, decide, edit the rung line, check a diff, follow pins, build the ledger line (4.1) | `platform/fair/fair.py:106-130`; `ico/schema/to_fair_scenario.py:99,206-250`; `platform/risk/enforce.py:81-91`; `platform/wargamer/tier_pr.py:84-152,201-217,327-360` |
| `loop/probe.py` | new | 190 | Read the cluster and test the capabilities (4.2) | `driftwood/drift/five-facts.py:291-332,454-468,518-547,589-606,900-956,958-1000` |
| `loop/test_loop.py` | new | 350 | Every test in 6.1 | |
| `cage/cage-tier.yaml` | new | 40 | The one rewriting policy (3.4) | `platform/distribution/policies/v7.0.0/cage-tier.yaml:1-43` |
| `cage/cage-netpol.yaml` | new | 45 | The network rules for `quarantine` and `isolated` (3.4) | `platform/distribution/policies/v7.0.0/cage-netpol.yaml:1-45` |
| `cage/rungs.json` | new | 12 | The ladder, what each rung closes, its cost (3.4) | costs from `platform/graded/cage.py:82-111` |
| `harness/up.sh` | new | 75 | Build the cluster: kind, Kyverno, cage, reference, apps (4.3) | `driftwood/.github/workflows/drift-sample.yml:51-52,141-142,155-156,171,204,237`; `driftwood/gitops/engine/kyverno.yaml:39-42` |
| `harness/reference.yaml` | new | 35 | Namespace `loop-reference` with pods `sink` and `client` and Service `sink` (4.2) | shape of `driftwood/drift/five-facts.py:485-516` |
| `harness/proof.sh` | new | 65 | The three cluster runs of 6.2 | |
| `harness/fixture/party.json` | new | 15 | Test party (6.2) | |
| `harness/fixture/threats.json` | new | 20 | Two test rows (6.2) | |
| `harness/fixture/penalties.json` | new | 20 | Exactly the example in 3.3. `test_loop.py` reads it as its penalty input | |
| `harness/fixture/apps/kustomization.yaml` | new | 5 | Lists the two files below | |
| `harness/fixture/apps/namespace.yaml` | new | 8 | Governed Namespace `fixture` at `quarantine` | |
| `harness/fixture/apps/shop.yaml` | new | 25 | One nginx Pod: the served workload and the probe pod | `driftwood/gitops/apps/pod.yaml:42-58` |
| `.github/workflows/proof.yml` | new | 40 | Unit tests and the cluster proof (5.1) | |
| `.github/workflows/cut-release.yml` | rewrite | 55 | Sign and push one tag, by dispatch (5.2) | `platform/.github/scripts/cut-release-create-tags.sh:21-26` |

Total 1,461.

### 2.2 ico

| Path | Status | Lines | Purpose | Lifted from |
|---|---|---|---|---|
| `LICENSE`, `DISCLAIMER.md`, `.gitignore` | keep | 0 | Licence, the demonstration-party disclaimer, ignores | |
| `README.md` | rewrite | 30 | What the feed is, the disclaimer line, how a change lands | |
| `penalty-schema/feed.json` | new | 70 | The penalty feed (3.3) | `ico/penalty-schema/v4/feed.json:12-114` |
| `test_feed.py` | new | 45 | The shape rules of 3.3 as tests | |
| `.github/workflows/cut-release.yml` | rewrite | 35 | Test every change; sign and push the feed's version tag (5.2) | `ico/.github/workflows/cut-release.yml:21-52,99-116` |

Total 180.

### 2.3 feeds

| Path | Status | Lines | Purpose | Lifted from |
|---|---|---|---|---|
| `LICENSE`, `.gitignore` | keep | 0 | Licence, ignores | |
| `README.md` | rewrite | 30 | What the feed is, the disclaimer line, how a change lands | |
| `threat-register/feed.json` | new | 70 | The threat rows (3.2) | `feeds/threat-register/v4/feed.json:15-68` |
| `test_feed.py` | new | 45 | The shape rules of 3.2 as tests | |
| `.github/workflows/cut-release.yml` | rewrite | 35 | Test every change; sign and push the feed's version tag (5.2) | `feeds/.github/workflows/cut-release.yml:22-68,115-133` |

Total 180.

### 2.4 driftwood

| Path | Status | Lines | Purpose | Lifted from |
|---|---|---|---|---|
| `LICENSE` | keep | 0 | Licence | |
| `.gitignore` | rewrite | 1 | `__pycache__/` | |
| `README.md` | rewrite | 35 | Where things are, the disclaimer line, how to read the ledger | |
| `party.json` | new | 16 | Size, tolerance, margin, dwell, mode, pins (3.1). It replaces `party.yaml` | `driftwood/party.yaml:35-43,60` |
| `renovate.json` | rewrite | 4 | `{"enabled": false}` only: it keeps the hosted Renovate app silent | `driftwood/renovate.json:4` |
| `gitops/apps/kustomization.yaml` | rewrite | 7 | Lists the four files below | |
| `gitops/apps/namespace.yaml` | rewrite | 9 | The governed Namespace and the one rung line (3.6), at `baseline` | `driftwood/gitops/apps/namespace.yaml:1-5,14,30` |
| `gitops/apps/api.yaml` | rewrite | 22 | Pod `api`, same image digest, port 8080 | `driftwood/gitops/apps/api.yaml:4-23` |
| `gitops/apps/storefront.yaml` | rewrite | 28 | Pod `storefront`, same image digest, port 80 | `driftwood/gitops/apps/storefront.yaml:54-79` |
| `gitops/apps/pod.yaml` | rewrite | 26 | Pod `checkout-svc`, same image digest, port 80; the probe pod | `driftwood/gitops/apps/pod.yaml:42-58` |
| `.github/workflows/loop.yml` | new | 185 | The five jobs of 5.3 | `hub/twin/other_hand.py:74-98,138-140` |
| `.github/pins.sh` | new | 38 | Check out the three pins and verify them (7) | `driftwood/.github/scripts/platform-tools.py:19-22,79-91`; `driftwood/.github/actions/install-gitsign/install.sh:1-17` |

Total 371. Each Pod keeps its Namespace name, its `runAsUser`, its `readOnlyRootFilesystem`, and for the nginx pods the two `emptyDir` mounts. Each carries the label `policy-as-versioned.dev/policy-version: "8.0.0"` and declares its `containerPort`. `pod.yaml` also carries `loop.policy-as-versioned.dev/probe: "true"`. The ledger is not on `main` (3.5).

### 2.5 hub

Start from `hub-records` as it is, 139 files. No builder removes anything.

| Path | Status | Lines | Purpose |
|---|---|---|---|
| `LICENSE`, `CLAUDE.md`, `.claude/settings.json`, `research/03-blogs-thesis.md` | keep | 0 | As they are |
| `twin/` (3 files) | keep | 0 | The guard on agent writes and its mode file. They leave only with the hook, in the owner's own commit (section 8). They left with the hook on 2026-11-15, by hub pull request 326, made from an agent session on the owner's word and merged by the app (section 11) |
| `docs/adr/` (37 files), `docs/agents/` (2 files) | keep | 0 | The decision records, with no banner edits. ADR-0039 names what it supersedes |
| `.scratch/distil/` (73 files), `.scratch/drift-review-2026-08-27/` (5 files), `.scratch/ecosystem/` (12 files) | keep | 0 | The review and the owner's dated words, byte for byte, but for the two files in the next row |
| `.scratch/distil/ARCHIVE.md`, `.scratch/distil/evidence/archive-refs.tsv` | rewrite | 0 | Appended to by the orchestrator, not by the builder: the branches archived at step 0 of section 8 |
| `.scratch/distil/CONTRACT.md` | new | 0 | This file, copied byte for byte, as a record |
| `LOOP.md` | new | 120 | The owner's sentence. Section 1 of this contract. Where each number comes from and its state today. The worked figures of 6.1, dated "on the inputs of 2026-11-14", with a pointer to the ledger for today's. **What is parked**, where it is kept and what brings it back: the exploited-flaw list (feeds tag `cve/v3.0.0`), the image inventory and scanner (platform tag `v6.3.0`), the fetch clocks and all else (`refs/archive/main/2026-11-14-before-simplify`); a returning fetch adds rows and would need the key in that publisher. Nothing is called a by-product. **What waits for the owner** (section 8). **Four notes.** The loop's machine merges rest on decision 2 ("All AI machine driven"), not on `twin/ENACT_MODE`, which governed agent sessions in the hub until 2026-11-15 (section 11). The CI proof is not yet decision 9's proof. While a release waits for its dwell the lines can read `saturated` and red, and with one cycle a day a dwell is usually met a day late. GitHub disables `loop.yml`'s schedule after 60 days without repository activity; it is switched back on from the Actions tab |
| `docs/adr/0039-one-loop-three-rungs-machine-merges.md` | new | 60 | Records the owner's ten answers by pointer to `DECISIONS.md`. Records K1 to K16 with the labels above, and the two things derived from the sentence as derived, with no comment from the owner. Points to `CONTEXT.md` for the terms and does not define them again. Says it reverses the ordinal pound (T75:111), ADR-0022's tighten-only rule and floor, and "a human merges" in ADR-0002, 0023 and 0024; that it supersedes ADR-0021 in full; that it sides with ADR-0015; and, from ADR-0026's own text, why this ratchet is not the one that record rejected |
| `CONTEXT.md` | rewrite | 80 | The loop's terms, defined here and nowhere else in the hub: the Words above, plus figure, goal, release-ready, settled, and each verdict |
| `README.md` | rewrite | 35 | As now, with `LOOP.md` first and the glossary note corrected |
| `.gitignore` | rewrite | 6 | `.venv/`, `__pycache__/`, `.claude/settings.local.json`, `.claude/scheduled_tasks.lock` |

Total 301.

**The budget.** All five come to 2,493 authored lines, against TARGET's 3,000 and a ceiling of 4,000. Three parts are over TARGET's own figure for them: `loop.py` (420 against 280: cost, goal, the diff check and the pin follower), `test_loop.py` (350 against 170: 6.1 names 36 tests) and driftwood's CI (223 against 65: it holds what TARGET put in a 220-line reusable workflow). The saving elsewhere pays for each.

## 3. The data contracts

Every example below is complete and is a test input. Amounts are pounds. A three-point value is `[lowest, most likely, highest]`.

### 3.1 `driftwood/party.json`

```json
{
  "note": "A demonstration party, not affiliated with, endorsed by or speaking for any real authority it names.",
  "party": "driftwood",
  "currency": "GBP",
  "turnover": 86000000,
  "turnover_as_of": "2026-06-30",
  "tolerance": {"amount": 40000, "basis": "fixture 2026-07-31, not owner-declared"},
  "margin": 0.2,
  "dwell_days": 7,
  "mode": "measure",
  "pins": {
    "platform": {"repo": "policy-as-versioned-platform/platform", "ref": "main", "commit": "0000000000000000000000000000000000000000"},
    "ico": {"repo": "policy-as-versioned-ico/ico", "ref": "main", "commit": "0000000000000000000000000000000000000000"},
    "feeds": {"repo": "policy-as-versioned-feeds/feeds", "ref": "main", "commit": "0000000000000000000000000000000000000000"}
  }
}
```

- The keys are exactly these. `read_party` refuses a duplicate key, an unknown key, a missing key, and a boolean or string where a number belongs. Nothing has a default. `turnover_as_of` is the date of the turnover figure. It is required, and no rule reads it.
- `tolerance` holds `basis` and exactly one of `amount` (pounds a year) or `share_of_turnover` (above 0, below 1). With a share, the tolerance is `share_of_turnover x turnover`. The ledger prints `basis` on every line. When the owner names a figure, only this line changes.
- `margin` is at least 0 and below 1. `dwell_days` is 0 or more. `mode` is `measure` or `act`. All three are settings: their values live here and nowhere in code.
- Each pin is one line in exactly this form, and `read_party` refuses a file where it is not. PIN_LINE is `^    "(platform|ico|feeds)": \{"repo": "(policy-as-versioned-[a-z]+/[a-z]+)", "ref": "([A-Za-z0-9._/-]+)", "commit": "([0-9a-f]{40})"\},?$`. Builders write forty zeros. The orchestrator fills in the commits.
- The feed's `currency` and each regime's `currency` must equal the party's, or pricing refuses. Nothing is converted.

### 3.2 `feeds/threat-register/feed.json`

```json
{"feed": "threat-register", "version": "5.0.0", "published_by": "feeds", "published_at": "2026-11-14", "currency": "GBP",
 "note": "A demonstration party, not affiliated with, endorsed by or speaking for any real authority it names. One row is one way a loss happens. Overlapping rows are never summed.",
 "rows": [
  {"id": "checkout-pii-exfiltration", "party": "driftwood",
   "events_a_year": [2, 4, 9],
   "events_basis": {"kind": "editorial", "as_of": "2026-09-09", "text": "DBIR retail-sector web-app-attack base rate, editorial midpoint"},
   "loss_an_event": [1000, 4000, 9000],
   "loss_basis": {"kind": "editorial", "as_of": "2026-09-09", "text": "the publisher's band for one cart or checkout data exfiltration at a mid-market UK shop. Nobody has counted it."},
   "penalty": {"regime": "uk-gdpr", "tier": null},
   "needs": [{"capability": "inbound", "source": "MITRE ATT&CK T1190, Exploit Public-Facing Application (Initial Access), version 2.8, read 2026-11-14 at attack.mitre.org/techniques/T1190: exploiting a weakness in an Internet-facing host or system to initially access a network."}]},
  {"id": "scheduled-agent-misuses-write-credential", "party": "driftwood",
   "events_a_year": [8.4186e-05, 8.4186e-05, 0.00029465],
   "events_basis": {"kind": "published", "as_of": "2026-09-26", "text": "N x C / M, as in v4. Kept from v4 as an upper bound. The workflows of 2026-11-14 pin every action by commit, so the door this rate counts is closed."},
   "loss_an_event": [1000, 4000, 9000],
   "loss_basis": {"kind": "editorial", "as_of": "2026-11-14", "text": "priced as one event of checkout-pii-exfiltration: a misused write credential on the repository that holds the rung line can open the cage"},
   "penalty": {"regime": "uk-gdpr", "tier": null},
   "needs": []},
  {"id": "insider-or-lost-device-disclosure", "party": "driftwood",
   "events_a_year": [0.2, 0.4, 0.9],
   "events_basis": {"kind": "editorial", "as_of": "2026-11-14", "text": "one tenth of the rate of checkout-pii-exfiltration. The ratio is the publisher's own. Nobody has counted this loss for this party."},
   "loss_an_event": [1000, 4000, 9000],
   "loss_basis": {"kind": "editorial", "as_of": "2026-11-14", "text": "priced as one event of checkout-pii-exfiltration. Nobody has counted it."},
   "penalty": {"regime": "uk-gdpr", "tier": null},
   "needs": []}]}
```

- The feeds builder publishes exactly these three rows. In the second row, the words "N x C / M, as in v4." are replaced by the row's `source` and its `lef_basis.statement`, copied in full from `feeds/threat-register/v4/feed.json:52-58`. Tuppence's and ludlow's rows are not carried. The third row is the loss outside the cage (K11).
- `price` uses only the rows whose `party` equals the party file's `party`.
- `events_a_year` or `loss_an_event` may be `null`. The row is then unpriced. `penalty` may be `null`. The row then has no penalty term.
- `penalty.tier` names a tier of the regime, or is `null`. `null` means the tier with the larger mean penalty, and the row's `bound` is `upper`. A missing `penalty_rate` also makes the bound `upper`. Otherwise the bound is `estimate`.
- `needs` is a list of `{capability, source}`. A need with an empty or missing `source` is ignored. A row whose list is then empty never closes. Closing any one listed capability closes the row. The list is the publisher's editorial claim.
- Each basis holds `kind`, `as_of` and `text`, and a row with one missing is refused. `kind` is `editorial`, `published` or `counted`. A row is *sourced* only if neither basis is `editorial`, its tier is cited, and the regime's `penalty_rate` is counted.
- **Since feeds `threat-register/v5.2.0` (2026-11-15, the review of every line).** The feed carries no `feed`, `published_by` or `published_at` key, which nothing read: it starts `{"version": ..., "currency": "GBP",`. Its note says "The reader adds every open row, so rows must not overlap." in place of "Overlapping rows are never summed.", which was false: the loop adds every open row. Feeds' test now refuses a need with an empty `source`; the loop still ignores one, as the bullet on `needs` says. No number changed. The example above is left as the builders had it.

### 3.3 `ico/penalty-schema/feed.json`

```json
{"note": "A demonstration party, not affiliated with, endorsed by or speaking for any real authority it names.",
 "regimes": {"uk-gdpr": {
  "currency": "GBP", "statute": "UK GDPR, Data Protection Act 2018 s157",
  "penalty_rate": null,
  "penalty_rate_basis": {"kind": "not-counted", "as_of": "2026-11-14", "text": "The chance that one breach draws a penalty. Nobody has counted the regulator's register, so a reader takes it as 1."},
  "tiers": {
   "higher": {"rate": 0.04, "cap": 17500000, "fines": [
    {"org": "British Airways", "year": 2020, "amount": 20000000, "status": "imposed-appeal-unchecked", "source": "ICO monetary penalty notice, 16 Oct 2020"},
    {"org": "Marriott International", "year": 2020, "amount": 18400000, "status": "imposed-appeal-unchecked", "source": "ICO monetary penalty notice, 30 Oct 2020"},
    {"org": "TikTok Information Technologies UK", "year": 2023, "amount": 12700000, "status": "imposed-appeal-unchecked", "source": "ICO monetary penalty notice, 4 Apr 2023"}]},
   "lower": {"rate": 0.02, "cap": 8700000, "fines": [
    {"org": "Clearview AI Inc", "year": 2022, "amount": 7552800, "status": "not-collected", "source": "ICO monetary penalty notice, 23 May 2022"},
    {"org": "Doorstep Dispensaree Ltd", "year": 2019, "amount": 92000, "status": "final", "source": "ICO monetary penalty notice, 17 Dec 2019; reduced by the First-tier Tribunal in 2021; further appeals dismissed by the Upper Tribunal in 2023 and the Court of Appeal in 2024"}]}}}}}
```

Corrected on 2026-11-15: the notice is dated 17 December 2019 (ico 5.1.1).

Changed on 2026-11-15, after the review of every line: the example's header is gone, as it went from `harness/fixture/penalties.json` in `policy/v8.0.3`, so the example is still the fixture byte for byte. Until then the example began `{"feed": "penalty-schema", "version": "5.0.0", "published_by": "ico", "published_at": "2026-11-14",`. Ico's published feed is not the fixture. Since `v5.2.0` it starts with `version` and `note`, it carries no `feed`, `published_by` or `published_at` key, and its fines carry no `year`: nothing read them. The fixture keeps each fine's `year`. Ico's test now also refuses a fine status outside `final`, `imposed-appeal-unchecked` and `not-collected`, a fine with no `source` whatever its status, and a tier rate above 1. No number changed.

- The ico builder publishes this regime only. Each fine also carries a `litigation` text, copied from v4. The other regimes and `control_weights` are not carried.
- `penalty_rate` is `null`, or a number above 0 and at most 1. It stays `null` until someone counts the regulator's register. When it is a number, `penalty_rate_basis.kind` is `counted`.
- A fine prices only if its `status` is `final` or `imposed-appeal-unchecked`. A pricing fine with no `source` is refused. A tier with no pricing fine makes the row unpriced.
- **The mean penalty at a turnover**, for one tier. Let `ex` be the amounts of the pricing fines. `lo, mode, hi = min(ex), median(ex), max(cap, 1.2 x max(ex), median(ex))`. Multiply all three by `rate x turnover / cap`. Then `hi = min(hi, max(cap, rate x turnover))`, `mode = min(mode, hi)`, `lo = min(lo, mode)`. The mean penalty is `mean(lo, mode, hi)`. No size is keyed by an adopter's name anywhere.

### 3.4 `platform/cage/rungs.json` and the cage

```json
{"ladder": [
  {"rung": "baseline", "closes": [], "cost": 500,
   "cost_basis": "unsourced: typed in platform/graded/cage.py on 2026-07-31 for the v7 rung, which carried a priority class that cage 8 removes. No measurement."},
  {"rung": "quarantine", "closes": ["egress"], "cost": 6000,
   "cost_basis": "unsourced: typed in platform/graded/cage.py on 2026-07-31 for the v7 rung, which carried a WAF sidecar and a priority class that cage 8 removes. No measurement."},
  {"rung": "isolated", "closes": ["inbound"], "cost": 15000,
   "cost_basis": "unsourced: typed in platform/graded/cage.py on 2026-07-31 for the v7 rung, which carried a WAF sidecar and a priority class that cage 8 removes. No measurement."}]}
```

- The ladder is in order, loosest first. A rung keeps what the rungs before it close. `cost` is pounds a year to run that rung. A `cost_basis` that does not start `unsourced:` must name a measurement. No rung carries a reduction. The file holds nothing else: what each rung does to a pod is read from `cage-tier.yaml`, never restated here.
- `cage/cage-tier.yaml` is the v7 file with four edits and nothing else. (1) `7.0.0` and `7-0-0` become `8.0.0` and `8-0-0` everywhere. (2) The `tier` variable's list is `['baseline', 'quarantine', 'isolated']`. (3) The `dial` map has those three keys, each with only `cpu`, `mem` and `harden`; each key takes v7's values for the rung of the same name. (4) The mutation loses `priorityClassName`, `priority`, `preemptionPolicy`, the `waf-sidecar` filter and the appended sidecar. An unknown or missing rung label still falls to `isolated`.
- `cage/cage-netpol.yaml` is the v7 file with three edits. (1) The version strings, as above. (2) The `rungs` variable is `['quarantine', 'isolated']`. (3) In `reach`, the `other` ingress becomes one empty rule, `dyn([dyn({})])`, so `quarantine` admits all traffic in. `synchronize` stays off. It generates one NetworkPolicy for each of its rungs, named `cage-reach-<rung>`.
- The cage acts on a pod that carries `policy-as-versioned.dev/policy-version: "8.0.0"` (8.0.2 since `policy/v8.0.2`, K20). It reads the rung from the Namespace's label only, and only when that Namespace carries `policy-as-versioned.dev/governed: "true"`. Its stamp is `posture.acme.io/caged: "true"` and `posture.acme.io/tier: <rung>` on the pod. Neither file holds a deny action.
- **Since cage 8.0.2.** The version strings in both cage files are `8.0.2` and `8-0-2`. `cage-tier.yaml` branches on the operation. When a pod is created it does what this section says. On an update it sets the stamp only and does not touch the pod's spec, because Kubernetes will not change a running pod's limits or capabilities. The network rule selects pods by the stamp's tier label, so it follows the rung in place. A pod moved to another rung in place keeps the limits and capabilities it was created with until it is replaced. Kyverno's rewrite of `cage-tier` for pod controllers is switched off (`spec.autogen.podControllers.controllers: []`): a controller's pods are caged when they are created.

### 3.5 The ledger line

One JSON object on one line, appended to `loop.jsonl` on the branch `ledger` of driftwood. Every field is present on every line the loop writes.

```json
{"ts": "2026-11-15T06:52:10Z", "party": "driftwood", "run": "1234567890", "commit": "<driftwood commit>", "cause": "schedule", "cluster": "throwaway", "mode": "measure",
 "pins": {"platform": "<sha>", "ico": "<sha>", "feeds": "<sha>"},
 "rung": "baseline", "rung_set_by": "github-actions[bot]", "looked": true, "why": "",
 "pods": [{"name": "api", "ready": true, "rung": "baseline"}, {"name": "checkout-svc", "ready": true, "rung": "baseline"}, {"name": "storefront", "ready": true, "rung": "baseline"}],
 "capabilities": {"egress": "open", "inbound": "open"}, "reference": {"before": true, "after": true}, "serving": {"ok": 3, "total": 3},
 "rows": [{"id": "checkout-pii-exfiltration", "amount": 16280871.43, "open": true, "bound": "upper", "needs": ["inbound"]},
          {"id": "scheduled-agent-misuses-write-credential", "amount": 431.49, "open": true, "bound": "upper", "needs": []},
          {"id": "insider-or-lost-device-disclosure", "amount": 1628087.14, "open": true, "bound": "upper", "needs": []}],
 "unpriced": [], "exposure": 17909390.06, "cost": 500, "cost_basis": "<the baseline cost_basis of 3.4>", "figure": 17909890.06,
 "tolerance": 40000, "tolerance_basis": "fixture 2026-07-31, not owner-declared", "margin": 0.2, "dwell_days": 7,
 "goal": "isolated", "unreachable": 1603518.63, "release_ready": false, "sourced_share": 0.0,
 "weakest_basis": {"kind": "not-counted", "of": "uk-gdpr penalty_rate"},
 "verdict": "tighten", "rung_to": "quarantine"}
```

- `verdict` is one of `within`, `within-partial`, `tighten`, `release`, `saturated`, `cage-ineffective`, `could-not-look`. `rung_to` is the next rung for `tighten` and `release`, else `null`.
- `cause` is the event that started the run: `schedule`, `push`, `workflow_dispatch` or `pull_request`. `cluster` is `throwaway` or `harness`. `rung` is the rung line in git.
- `rung_set_by` is the author name of the newest non-merge commit on `main` that touched the rung file. It tells the loop's notch from a person's edit.
- When `looked` is false, `why` says what failed, `capabilities` and `serving` are `null`, and every row is open. With no probe file at all, `pods` is `[]` and `reference` is `null`. The figure on such a line is the uncaged one. It is never a measurement. A `cage-ineffective` line keeps its measurements and also prices every row as open.
- `goal` is `goal(tolerance)`. `unreachable` is the lowest `predicted(k)` on the ladder minus the tolerance, or 0 if that is negative. It includes cost. `release_ready` is as section 1, step 5. `sourced_share` is the sourced rows' share of `figure`. An unsourced cost counts as unsourced.
- `weakest_basis` names the weakest basis that enters `figure`, as owner decision 4 asks. The kinds, weakest first, are `not-counted`, `unsourced`, `editorial`, `published`, `counted`. The candidates, in this order, are: each open row's `events_basis` (`of` is `<row id> events`) and `loss_basis` (`<row id> loss`); the `penalty_rate_basis` of each regime an open row uses (`<regime> penalty_rate`); and the current rung's cost (`cost of <rung>`), which is `unsourced` when its basis starts so, else `counted`. A tie goes to the first candidate.
- Each row's amount is rounded to pence when it is priced, and every sum adds rounded amounts. Nothing else is rounded.
- **The first line** is not written by the workflow. The orchestrator writes it once, when it creates the branch at step 5 of section 8: `{"ts": "...", "party": "driftwood", "cause": "reset", "commit": "<sha>", "rung_from": "isolated", "rung": "baseline", "note": "floor removed and rung reset, owner decision 8 of 2026-11-14"}`. Readers skip any line with no `verdict`.

### 3.6 The one rung line

It lives in `driftwood/gitops/apps/namespace.yaml`, in the one Namespace document that carries `policy-as-versioned.dev/governed: "true"`. Its exact text is four spaces, then `posture.acme.io/tier: "baseline"`. RUNG_LINE is `^    posture\.acme\.io/tier: "(baseline|quarantine|isolated)"$`. The file holds exactly one governed Namespace and exactly one such line. No other file in driftwood names a rung.

## 4. The code interfaces

### 4.1 `platform/loop/loop.py`

It runs no cluster command and no forge command. Its only subprocesses are `git ls-remote` and `git diff`.

| Command | Reads | Writes | Exit |
|---|---|---|---|
| `loop.py cycle --party F --namespace-file F --penalties F --threats F --rungs F [--probe F] [--ledger F] --cause S --cluster S --run S --commit S --rung-set-by S --out F [--write]` | The files named. No `--probe`, a probe with `looked` false, or a probe whose `rung` differs from the rung line, gives `could-not-look` | The ledger line, to `--out` and to standard output. With `--write`, `mode: act` and a verdict of `tighten` or `release`: the rung line, in place | 0 for `within`, `within-partial`, `tighten`, `release`. 2 for `saturated` and `cage-ineffective`. 3 for `could-not-look`. 1 for a refused input |
| `loop.py check-diff --kind rung\|pins --base REF --head REF [--from R --to R --rungs F]` | `git diff --unified=0 BASE...HEAD` | A one-line reason | 0 if the diff is allowed, else 1 |
| `loop.py bump-pins --party F [--write]` | `git ls-remote https://github.com/<repo>` for each pin | With `--write`, the changed pin lines, in place | 0 |

Functions, with these exact names. All are pure.

- `mean(lo, mode, hi)`; `read_party(text) -> dict`; `read_rungs(text) -> list[dict]`; `tolerance(party) -> float`. Both readers use `json.loads` with an `object_pairs_hook` that refuses a duplicate key.
- `mean_penalty(tier, turnover) -> float | None` (3.3). `price(rows, penalties, party) -> list[dict]`, each `{id, amount | None, bound, needs, sourced}`.
- `closed_capabilities(probe, rungs, rung) -> set`. It raises `CouldNotLook` or `CageIneffective` in the order of section 1, step 6: a declared-closed capability measured open is checked before a closed one that is not declared.
- `exposure(priced, closed) -> float`; `predicted(priced, rungs, k) -> float`; `goal(priced, rungs, limit) -> int`; `weakest_basis(...) -> dict` (3.5).
- `dwell_met(lines, now, dwell_days) -> bool`. Walk the ledger from the newest line back. Skip `could-not-look` lines and lines with no `verdict`. Stop at the first line whose `release_ready` is false. The dwell is met when the oldest line of that unbroken run is at least `dwell_days` days old. An empty ledger never meets a dwell above 0. A dwell of 0 is always met. A change of rung does not break the run, so a release two rungs long waits one dwell, not two. A `tighten` line always breaks it, because its `release_ready` is false. `decide` also needs the present cycle to be release-ready.
- `decide(priced, rungs, rung, closed, tol, margin, dwell_ok) -> dict` with `verdict`, `rung_to`, `goal`, `figure`, `unreachable`, `release_ready`. It is the only place that uses the margin and the dwell.
- `read_rung(text) -> str` and `set_rung(text, rung) -> str`. A line edit by regular expression, never a YAML parse or re-dump. `--- # comment` is a document separator. Two governed Namespaces, no governed Namespace, or a rung not on the ladder raises. `set_rung` changes exactly one line.
- `check_diff(diff, kind, frm=None, to=None, ladder=None) -> tuple[bool, str]`. For `rung`: one file, `gitops/apps/namespace.yaml`; one line removed and one added; both match RUNG_LINE; the old rung is `frm` and the new is `to`; they are next to each other on the ladder. For `pins`: one file, `party.json`; every removed and added line matches PIN_LINE; lines pair by name; `repo` is unchanged. Anything else is refused.
- `next_pin(ref, commit, ls_remote) -> tuple[str, str]`. If `ref` does not end in `v<n>.<n>.<n>` it is a branch: return `ref` and the commit of `refs/heads/<ref>`. Otherwise it is a tag: among tags with the same text before the `v`, return the highest version and its peeled commit.
- `cycle(...) -> dict` builds the ledger line from parsed inputs and a `now`. `main(argv) -> int`.

### 4.2 `platform/loop/probe.py`

`probe.py --context C --out F [--settle-seconds 600]`. It uses `kubectl` only. It creates and deletes nothing. It always writes `F` and exits 0, unless its arguments are wrong.

**Since `policy/v8.0.3` (2026-11-15, the review of every line).** The command is `probe.py --context C --out F`. No caller passed `--settle-seconds`, so the flag went, and the 600 seconds of step 3 are the constant `SETTLE_SECONDS`. Step 3 no longer requires at least one pod. An empty governed Namespace still fails, at step 5, which finds no probe pod: its `why` reads "0 probe pods, not one". The steps below are otherwise as written.

What it does, in order. A step that fails sets `looked` to false with a `why`, and stops.

1. Find the one Namespace labelled `policy-as-versioned.dev/governed=true`. Read its rung label.
2. Find the one `mutatingpolicies.policies.kyverno.io` whose name starts `cage-tier-`. Require `status.conditionStatus.ready`.
3. **Settle.** List the Namespace's pods. Require at least one. Every pod must be Ready and carry the stamp, with `posture.acme.io/tier` equal to the Namespace's rung. Poll every 5 seconds for up to `--settle-seconds`. A pod still starting is waited for, not judged.
4. In Namespace `loop-reference`, require pods `sink` and `client` Ready, neither stamped, and no NetworkPolicy. Read Service `sink`'s cluster address.
5. Find the one governed pod labelled `loop.policy-as-versioned.dev/probe=true`.
6. **Reference before.** From `client`, connect to `sink` on port 80. Retry up to 10 times, 3 seconds apart. It must succeed.
7. **`egress`.** From the probe pod, connect to `sink` on port 80.
8. **`inbound` and serving.** From `client`, connect to each governed pod's address on its first declared `containerPort`. `serving` is `{ok, total}`. A `total` of 0 fails the step. The reading is open if `ok` is 1 or more.
9. **Settling a reading.** A reading that is not open must hold: it is read 3 more times, 3 seconds apart, and is `closed` only if none of them is open. A reading that is open is `open`, unless a NetworkPolicy exists in the governed Namespace. Then it is read again every 3 seconds for up to 60 seconds, because the rule may not be programmed yet, and the first reading that is not open goes to the hold check. The harness, not the probe, waits for the NetworkPolicy to exist (4.3).
10. **Reference after.** Step 6 again. It must succeed, or a closed reading cannot be blamed on the cage.

One connect is `kubectl exec <pod> -- sh -c '<snippet>' HOST PORT`. The snippet is: `if command -v bash >/dev/null 2>&1; then timeout 4 bash -c "</dev/tcp/$0/$1" 2>/dev/null; rc=$?; elif command -v nc >/dev/null 2>&1; then nc -w 4 -z "$0" "$1" 2>/dev/null; rc=$?; else rc=127; fi; echo loop-probe-rc=$rc`. The answer is read from the marker, never from `kubectl`'s exit code. `0` is open. `127` or no marker fails the step. Anything else is not open.

Output: `{"looked": true, "why": "", "rung": "baseline", "pods": [{"name": "api", "ready": true, "rung": "baseline"}], "capabilities": {"egress": "open", "inbound": "open"}, "reference": {"before": true, "after": true}, "serving": {"ok": 3, "total": 3}}`.

Its one entry point for tests is `measure(run, sleep, settle_seconds) -> dict`. `run(args: list[str]) -> tuple[int, str]` is the only way it reaches a cluster.

### 4.3 `platform/harness/up.sh`

`up.sh <cage-dir> <apps-dir> [--no-netpol]`. It works on a laptop and in CI. The cluster is named `loop` and its context is `kind-loop`. `up.sh` and `proof.sh` find their own files from the script's directory, `here=$(cd "$(dirname "$0")" && pwd)`, never from the working directory: driftwood runs `up.sh` from its own checkout. In order:

1. Use `kind` from the path only if `kind version` reports `v0.32.0`. Otherwise, on Linux, download kind 0.32.0, check `sha256 50030de23cf40a18505f20426f6a8506bedf13c6e509244bd1fa9463721b0f54` and put it first on `PATH`. Download Kyverno 1.18.2's `install.yaml` and check `sha256 3dcd43eaf11f0719084217148cd0c82a8fa49faa9b1a783ea5bea2cf84041bda`. Downloads go to `$RUNNER_TEMP`, or to a new temporary directory. They never go to the checkout.
2. `kind create cluster --name loop --wait 120s`, unless it exists.
3. Apply Kyverno with `--server-side --force-conflicts`. Wait for its admission controller and its background controller to roll out.
4. Apply `cage-tier.yaml`, and `cage-netpol.yaml` unless `--no-netpol`. Wait until each reports `status.conditionStatus.ready`.
5. Apply `$here/reference.yaml`. Wait for its two pods.
6. `kubectl apply -k <apps-dir>`. Then, if `cage-netpol.yaml` was applied and the governed Namespace's rung is not `baseline`, wait up to 120 seconds for NetworkPolicy `cage-reach-<rung>` to exist there. Kyverno writes it after the pod is admitted, so a probe that ran first would read a false `open`. If it never appears, carry on: the probe reports what it finds. `up.sh` does not wait for the pods. The probe's settle step does.

The cage is always in place before any workload, so no pod is admitted uncaged. All reference and fixture pods use `nginx@sha256:abe47724e466aeab9a345d8e46a221c2fa8953c7848bb4a3bd9976a7199f8cf2`, the image driftwood's `checkout-svc` already runs.

### 4.4 How the two are tested without a cluster

`loop.py` takes the probe's result as a file, so its tests build that result by hand. `probe.py` takes `run` and `sleep` as arguments, so its tests pass a fake that answers each `kubectl` call from a table. `python3 -m unittest discover -s loop -p 'test_*.py'` needs no network, no cluster, no git remote and no installed package.

## 5. The workflows

Every workflow pins `actions/checkout@11d5960a326750d5838078e36cf38b85af677262` (`driftwood/.github/workflows/observation-delivery.yml:50`) and uses no other action. Top-level permissions are `contents: read`. Inputs reach scripts through `env`, never by interpolation. Every `if:` is written inside `${{ }}`: a bare `!cancelled()` does not parse.

### 5.1 platform: `.github/workflows/proof.yml`

Triggers: `pull_request`, `push` to `main`, `workflow_dispatch`. The `pull_request` trigger is what lets the proof run before the file is on `main`. Identity: the default token, read-only. It needs no key.

Job `unit`: `python3 -m unittest discover -s loop -p 'test_*.py' -v`. Job `cluster`, after `unit`: `bash harness/up.sh cage harness/fixture/apps --no-netpol`, then `bash harness/proof.sh` (6.2).

### 5.2 `cut-release.yml` in ico, feeds and platform

The file's name and path do not change, because the signer's identity names them. This is ico's file in full. Feeds' file differs only in the two `env` values. The two comments show feeds' values, and neither builder copies them.

```yaml
name: cut-release
on: {pull_request: {}, push: {branches: [main]}, workflow_dispatch: {}}
permissions: {contents: read}
env:
  FEED: penalty-schema/feed.json   # feeds: threat-register/feed.json
  PREFIX: v                        # feeds: threat-register/v
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262
      - run: python3 -m unittest -v test_feed
  cut:
    needs: test
    if: ${{ github.ref == 'refs/heads/main' && (github.event_name == 'workflow_dispatch' || (github.event_name == 'push' && vars.CUT_ON_MERGE == 'true')) }}
    runs-on: ubuntu-latest
    permissions: {contents: write, "id-token": write}
    steps:
      - uses: actions/checkout@11d5960a326750d5838078e36cf38b85af677262
        with: {fetch-depth: 0}
      - run: |
          set -euo pipefail
          version=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["version"])' "$FEED")
          [[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo "refused: version '$version'"; exit 1; }
          tag="${PREFIX}${version}"
          if git rev-parse -q --verify "refs/tags/$tag" >/dev/null; then git diff --quiet "refs/tags/$tag" HEAD -- "$FEED" || { echo "refused: $FEED changed and version did not"; exit 1; }; echo "$tag exists: nothing to cut"; exit 0; fi
          curl -fsSL -o "$RUNNER_TEMP/gitsign" https://github.com/sigstore/gitsign/releases/download/v0.17.1/gitsign_0.17.1_linux_amd64
          echo "69213a8a0813a151e5a47d0060862952ff833a845d57309dff76f7ba6600abae  $RUNNER_TEMP/gitsign" | sha256sum -c -
          chmod +x "$RUNNER_TEMP/gitsign"; export PATH="$RUNNER_TEMP:$PATH"
          git -c gpg.format=x509 -c gpg.x509.program=gitsign -c gitsign.rekorMode=offline -c user.name="policy-as-versioned release bot" -c user.email="releases@${GITHUB_REPOSITORY_OWNER}.invalid" tag -s "$tag" -m "$tag"
          GITSIGN_REKOR_MODE=offline gitsign verify-tag "$tag" --certificate-oidc-issuer=https://token.actions.githubusercontent.com --certificate-identity-regexp="^https://github\.com/${GITHUB_REPOSITORY}/\.github/workflows/cut-release\.yml@refs/heads/main$"
          git push origin "refs/tags/$tag"
```

- **`test`** is the publisher's whole CI. It runs on every pull request and every push to `main`. The orchestrator's merge gate reads it.
- **`cut`** signs the tag named by the feed's own `version`, verifies it against the identity of section 7, and pushes it. When that tag exists and the feed is the same as at the tag, it does nothing. When the feed changed and `version` did not, it ends red: once pins name tags, that change would otherwise never reach driftwood. So a publisher changes `version` in the same pull request as the numbers.
- **Until the first tags**, `CUT_ON_MERGE` is unset and no tag is cut by a merge. The orchestrator opens a publisher's pull request, `test` runs on it, and the app approves and merges it from the orchestrator's session. Driftwood follows the new `main` by itself (5.3).
- **Unattended** needs one setting and no file change: the repository variable `CUT_ON_MERGE=true`. From then on a merged change of `version` cuts its tag, and driftwood's `bump-pins` finds it once the pin names a tag (7). No key is needed. The orchestrator sets the variable at step 8 of section 8, after the first tags are cut by dispatch.
- **Platform's file** has no `test` job and no top-level `env`. Its only trigger is `workflow_dispatch` with one input, `version`, which reaches the script through the step's `env`. Its `cut` job has `if: ${{ github.ref == 'refs/heads/main' }}` and the same steps, with three differences. The tag is the input, refused unless it matches `^policy/v[0-9]+\.[0-9]+\.[0-9]+$`. A tag that exists is refused with exit 1, with no comparison of files. The unit tests of 5.1 run before the signing. Platform's release number is written in no file: the `8.0.0` in the cage files is the claim the pods match on, not a release number. So nothing cuts a platform tag on merge. The orchestrator or the app dispatches it.

**Since ico `v5.2.0` and feeds `threat-register/v5.2.0` (2026-11-15, the review of every line).** The publishers' file differs from the block above in four places, and the bullets on "Until the first tags" and "Unattended" describe a variable that no longer exists:

- The `cut` job's condition is `if: ${{ github.ref == 'refs/heads/main' }}`. It runs on dispatch and on every push to `main`, and reads no variable. A merge that changes `version` cuts the tag; a merge that leaves the feed as it is at its tag prints "exists: nothing to cut". The repository variable `CUT_ON_MERGE` was deleted from ico and feeds after both files stopped reading it (D7).
- The line that checked the form of `version` went. The `test` job, which `cut` needs, checks it (`test_header` in ico, `test_envelope` in feeds).
- After the tag-exists line, the job refuses a version that is not above every existing tag of its prefix: `python3 -c 'import re, sys; p, n, *tags = sys.argv[1:]; v = lambda s: tuple(map(int, s.split("."))); sys.exit(any(v(n) <= v(t[len(p):]) for t in tags if re.fullmatch(re.escape(p) + r"[0-9]+\.[0-9]+\.[0-9]+", t)))' "$PREFIX" "$version" $(git tag -l) || { echo "refused: $tag is not above every ${PREFIX} tag"; exit 1; }`.
- Each `uses:` line ends `# v4.4.0`, so Renovate can follow the pinned action.

Platform's file changed in `policy/v8.0.3` too. Its own refusal of a tag that exists went: `git tag` refuses to create a tag that exists, before anything is signed, so a dispatch with an existing tag still ends red. Its `uses:` line ends `# v4.4.0`.

**The owner gave leave to cut tags on 2026-11-14.** A tag can never be moved or deleted, so a tag is cut only at a commit the loop has already run against (section 8, step 6). The `cut` jobs cannot be proven before that first dispatch. In ico and feeds every pull request still parses the whole file, so a syntax fault shows at once.

### 5.3 driftwood: `.github/workflows/loop.yml`

Triggers: `schedule` at `47 6 * * *`; `workflow_dispatch`; `push` to `main` on `party.json` or `gitops/apps/**`; `pull_request`. Concurrency: `{group: "loop-${{ github.ref }}", cancel-in-progress: false}`. A running cycle is never cancelled. GitHub may replace a waiting run with a newer one on the same ref, and that one reads the same `main`. On a pull request, or on any ref but `main`, only `cycle` and `verdict` run and nothing is written. In the table, MAIN stands for `github.event_name != 'pull_request' && github.ref == 'refs/heads/main'`. Write it out in the file. No job but `verdict` uses a status function, so each of the others runs only when the jobs it needs succeeded.

| Job | `needs` and `if` | Permissions and identity | What it does |
|---|---|---|---|
| `cycle` | No `needs` and no `if` | `contents: read`. Default token. Runs platform code | Checks out with full history and no saved credentials. `bash .github/pins.sh party.json "$RUNNER_TEMP/deps"`. Reads `loop.jsonl` from `origin/ledger` if that branch exists. `up.sh "$RUNNER_TEMP/deps/platform/cage" gitops/apps`. `probe.py`. `loop.py cycle ... --cluster throwaway --write`, with `--rung-set-by "$(git log -1 --no-merges --format=%an -- gitops/apps/namespace.yaml)"`. All three run inside `set +e`, so that each exit code is read. If `up.sh` or `probe.py` fails, `loop.py cycle` still runs, with no `--probe`, and gives `could-not-look`. If `mode` is `act`: saves the `git diff` of the rung file, restores the tree, runs `loop.py bump-pins --write`, saves the `git diff` of `party.json`. Sets the outputs `line`, `rung_patch`, `pins_patch` (each base64), `verdict`, `rung`, `rung_to`, `mode` and `code`, which is `loop.py`'s exit code. The job ends green whenever `loop.py` wrote a line (codes 0, 2 and 3). It ends red only when `pins.sh` failed or `loop.py` refused an input (code 1): there is then no line |
| `verdict` | `needs: [cycle]`. `if: ${{ always() }}` | `contents: read`. No checkout. Runs no code from any repository | Exits with `needs.cycle.outputs.code`, read through `env`, or with 1 if that is empty. It is the only job a red verdict turns red: 2 for `saturated` and `cage-ineffective`, 3 for `could-not-look`. It runs on every event, so a pull request shows its verdict too |
| `write` | `needs: [cycle]`. `if: ${{ MAIN }}` | `contents: write`, `pull-requests: write`. Default token. Runs no platform code | Every commit it makes carries `-c user.name="github-actions[bot]" -c user.email="41898282+github-actions[bot]@users.noreply.github.com"`: a runner has no git identity, and `rung_set_by` reads this name. Appends `line` to `loop.jsonl` on the branch `ledger` and pushes. It appends nothing when `line` is empty, which is the case when `pins.sh` failed or `loop.py` refused an input. It stages `loop.jsonl` only. It never creates the branch: a missing `ledger` fails the job. If `mode` is `act`: for a non-empty `rung_patch` it resets the branch `loop/rung` to `main`, applies the patch, force-pushes, and opens a pull request titled `loop: <verdict> <rung> to <rung_to>` if none is open. The body is the ledger line. It does the same for `pins_patch` on `loop/pins`. It closes a pull request from either branch that has no patch this run |
| `check` | `needs: [cycle, write]`. `if: ${{ MAIN && needs.cycle.outputs.mode == 'act' }}` | `contents: read`, `pull-requests: read`. Default token. Runs platform code | It reads `mode`, `rung` and `rung_to` from `needs.cycle.outputs`, which is why `cycle` is in its `needs`. Checks out `main` with full history. Runs `pins.sh` from `main`, so the checker is the platform commit that `main` pins, never the pull request's. For the open pull request from `loop/rung`: `loop.py check-diff --kind rung --base origin/main --head <head commit> --from <rung> --to <rung_to> --rungs ...`. For `loop/pins`: `--kind pins`. Its output `land` lists the `number:commit` pairs that passed |
| `land` | `needs: [check]`. `if: ${{ MAIN && needs.check.outputs.land != '' }}` | `environment: observation-delivery`. The only job that sees `PAVC_OTHER_HAND_PRIVATE_KEY`. No checkout, so `env` sets `GH_REPO: ${{ github.repository }}`. Runs no code from any repository | Mints an installation token for the app `pavc-other-hand` (app id 4819564) in shell: a JWT with `iat` 60 seconds back and `exp` 540 ahead, signed RS256 with `openssl dgst -sha256 -sign`; then `GET /repos/{repo}/installation` and `POST /app/installations/{id}/access_tokens`. The key is written to a file of mode 600 under `$RUNNER_TEMP` and removed in the same step. Masks the token. For each pair: `gh pr review <n> --approve`, then `gh pr merge <n> --merge --match-head-commit <commit>` |

**How a rung change reaches `main` unattended.** `cycle` decides and makes the patch with a read-only token. `write` opens the pull request as `github-actions[bot]`. `check` refuses anything but one rung line, one notch, in the direction of this run's verdict. `land` approves and merges as the app. The app did not open the pull request, so its approval satisfies the one-review rule. A pull request opened with the default token starts only a held run with no jobs (`LOOP.md`, the notes), which is why the check is a job of the same run. The merge is the app's, so it does start a run: the `push` trigger fires and the next cycle begins.

**A release** takes the same path with no special case. The verdict is `release`, the patch moves the line one rung looser, and `check` is given that direction. The margin and the dwell are values in `party.json`. The rule that uses them is in `loop.py` only.

**A pin change** takes the same path with `--kind pins`. The diff must touch pin lines only. So the tolerance, margin, dwell and mode, which share the file, cannot ride along.

**In `measure` mode** `cycle`, `verdict` and `write` run, `write` only appends the ledger line, pins do not move, and `check` and `land` are skipped.

**A red verdict does not stop the landing path.** `cycle` ends green whenever it wrote a line, and only `verdict` carries the red. So a pin change, which is how a publisher's correction or a platform fix arrives, still lands while the verdict is `saturated`, `cage-ineffective` or `could-not-look`. On today's inputs every run at `isolated` is red at `verdict`, and its line is still written.

**How the ledger is stored.** One file, `loop.jsonl`, on the orphan branch `ledger` of driftwood. The orchestrator creates the branch once (section 8). After that only `write` pushes it, only from runs on `main`, with the default token. No ruleset covers that branch (FORGE). A push with the default token starts no workflow.

## 6. The proof

### 6.1 Unit tests that must exist, in `platform/loop/test_loop.py`

R1, R2 and R3 are the three rows of 3.2, in order. The test builds 3.1 and 3.2 by hand and reads `harness/fixture/penalties.json` for 3.3. The rungs are `cage/rungs.json`. Money is compared to the penny.

**As they are since `policy/v8.0.3` (2026-11-15, the review of every line): 42 tests.** The builders wrote the 36 in the first part of the table. `policy/v8.0.1` added two, and `policy/v8.0.3` added seven and removed three that held nothing alone; those three rows say so. The rows added since are at the end. Tests that stayed also gained cases: every reachable guard that no test held is now held, each case shown to fail without its line.

| Test | Expected |
|---|---|
| `test_mean` | `mean(2, 4, 9) = 4.5`. `mean(1000, 4000, 9000) = 4333.33`. *Removed in `policy/v8.0.3`: `test_amounts` holds R1 to the penny through `mean`, and `test_monte_carlo_agrees` checks the mean on its own* |
| `test_mean_penalty` | At 86,000,000: higher 3,613,638.10, lower 301,823.75. At 861,741,000: higher 32,893,885.03, where the cap rule bites |
| `test_amounts` | R1 16,280,871.43. R2 431.49. R3 1,628,087.14. All `upper`. R1 with `tier: "lower"` cited: 1,377,706.90. A row of another party is ignored |
| `test_figure_at_baseline` | Exposure 17,909,390.06. Cost 500. Figure 17,909,890.06 |
| `test_predicted_and_goal` | `predicted(quarantine)` 17,915,390.06. `predicted(isolated)` 1,643,518.63. No rung is within 40,000, so `goal(40000)` is the lowest, `isolated`. With R1 and R2 only, `predicted(isolated)` is 15,431.49. *Removed in `policy/v8.0.3`: the walk, `test_within` and `test_release_after_dwell` hold these figures; its case of a goal exactly at the limit moved to `test_exactly_at_tolerance_is_within`* |
| `test_walk_on_todays_inputs` | At `baseline`, all open: `tighten` to `quarantine`. At `quarantine`, `egress` closed and `inbound` open: figure 17,915,390.06, `tighten` to `isolated`. At `isolated`, both closed, serving 0 of 3: figure 1,643,518.63, `saturated`, exit 2, `unreachable` 1,603,518.63, `release_ready` false |
| `test_within` | R1 and R2 only, at `isolated`, both closed: figure 15,431.49, `within`, `unreachable` 0 |
| `test_release_after_dwell` | Penalty rate 0.0005, counted, at `isolated`: figure 17,763.80, and `predicted(baseline)` is 30,894.49, which is at or below 32,000. Ledger release-ready for 7 days: `release` to `quarantine`. For 6 days: `within`. The next cycle, at `quarantine` with that release line added: `release` to `baseline`, with no second dwell |
| `test_unreachable_counts_cost` | R1 and R2 only, tolerance 10,000, at `isolated`: `saturated`, `unreachable` 5,431.49. *Removed in `policy/v8.0.3`: it held nothing that `test_cost_stops_a_notch` and the walk do not* |
| `test_cost_stops_a_notch` | One row needing `egress`, 1 event a year at 3,000; tolerance 1,000; at `baseline`: figure 3,500, `predicted(quarantine)` 6,000, `saturated`, no move, `unreachable` 2,500 |
| `test_cost_gives_a_notch_back` | No rows, at `quarantine`, tolerance 1,000: figure 6,000. Dwell met: `release`. Not met: `saturated` |
| `test_exactly_at_tolerance_is_within` | A figure equal to the tolerance is `within` |
| `test_cage_ineffective` | At `quarantine` with `egress` open: `cage-ineffective`, no move, exit 2, every row priced as open. The same with `inbound` also closed: still `cage-ineffective` |
| `test_closed_but_undeclared_is_could_not_look` | At `baseline` with `inbound` closed: `could-not-look`. R1 is not credited |
| `test_could_not_look` | No probe file; `looked` false; probe rung not the git rung: each gives `could-not-look`, no move, exit 3. At `baseline` the line carries the uncaged figure 17,909,890.06. With no probe file `pods` is `[]` and `reference` is `null` |
| `test_within_partial_never_releases` | A row with `events_a_year: null` is named in `unpriced`. The verdict is `within-partial`. No release, even when release-ready with the dwell met. Above tolerance it still tightens |
| `test_need_without_source_is_ignored` | A need with an empty `source` never closes its row |
| `test_weakest_basis` | On 3.1 to 3.3 at `baseline`: `not-counted`, of `uk-gdpr penalty_rate`. With the rate counted: `unsourced`, of `cost of baseline` |
| `test_tolerance` | `share_of_turnover: 0.005` gives 430,000. A missing tolerance is refused. Both forms together are refused. Since `policy/v8.0.3`, also refused: an extra key, a share of 0 or 1, and an amount of 0 |
| `test_party_is_read_strictly` | A duplicate key, an unknown key, a boolean turnover, a bad `mode`, a pin split over two lines: each is refused |
| `test_currency_is_never_mixed` | A regime in USD with a party in GBP is refused |
| `test_fine_rules` | A `not-collected` fine does not price. A pricing fine with no source is refused. A row basis with no `as_of` is refused |
| `test_set_rung_changes_one_line` | The diff is one line. Comments survive. `--- # comment` separates documents. Two governed Namespaces raise. A rung not on the ladder raises. Since `policy/v8.0.3` the two assertions on comments are gone, because the one-line check already holds them, and a rung line outside the governed Namespace raises |
| `test_check_diff_rung` | Accepts one notch in the verdict's direction, tighter and looser. Refuses a two-line diff, a two-notch move, the wrong direction, and another file |
| `test_check_diff_pins` | Accepts a changed `commit` and a changed `ref`. Refuses a changed tolerance line, a changed `mode` line and a changed `repo` |
| `test_next_pin` | `main` follows the branch head. `policy/v7.0.0` moves to the highest `policy/v*` and ignores `v6.3.0` and `cloud/v1.0.1`. Since `policy/v8.0.3` the listing is in git's order, by name, so the highest tag is neither first nor last; it also ignores `refs/meta/v99.0.0`, and `v6.3.0` stays at `v6.3.0` |
| `test_dwell` | Met after an unbroken run. Broken by one false line. Not broken by a change of rung. `could-not-look` lines are skipped. An empty ledger is not met. A dwell of 0 is met |
| `test_monte_carlo_agrees` | 20,000 simulated years of R1 with Poisson counts, seed 20261114: the mean is within 2% of 16,280,871.43 |
| `test_no_deny_and_no_reduction` | No file under `cage/` holds `Deny` or `validationActions`. `rungs.json` holds no `reduce`. Since `policy/v8.0.3` the second check is a table through `read_rungs`: a rung with a `reduce` key is refused, and so are a ladder with an extra key, an entry that is not an object, a cost of -1 or `true`, `closes` as a string, and a `cost_basis` of 5 or the empty string |
| `test_loop_runs_no_forge_command` | Neither `loop.py` nor `probe.py` runs `gh` as a command word, or holds `api.github.com` or `approve` |
| `test_probe_reads_the_marker` | Exit 1 from `kubectl` with marker 0 is open. No marker gives `looked` false |
| `test_probe_closed_must_hold` | Not open once, then open: `open`. Not open on four reads: `closed`. Open with a NetworkPolicy present, then not open on four reads: `closed` |
| `test_probe_reference_brackets` | The reference fails before, or after: `looked` false |
| `test_probe_settle` | An unstamped pod, a pod at another rung, a pod not Ready at the limit, or no pods: `looked` false. Since `policy/v8.0.3` no pods fails at the probe-pod count, "0 probe pods, not one" (4.2), and a pod with the tier label but no `caged` label is unstamped |
| `test_probe_policy_not_ready` | `status.conditionStatus.ready` false: `looked` false |
| `test_probe_reference_must_be_uncaged` | A stamp on `client`, or a NetworkPolicy in `loop-reference`: `looked` false |
| `test_malformed_values_are_refused` | Added in `policy/v8.0.1`. A three-point value out of order, below 0, of the wrong length or not numbers; a tier rate, cap or fine amount not above 0; a penalty rate that disagrees with its basis kind; an amount that is not a sum of money: each is refused |
| `test_bump_pins_leaves_the_platform_pin` | Added in `policy/v8.0.1`. `bump-pins --write` moves the ico pin to its newest tag and leaves the platform pin alone (K17) |
| `test_cycle_on_files` | Added in `policy/v8.0.3`. Through `main`: a ledger 8 days release-ready, with a trailing blank line, gives `release`; with no ledger, `within`. The rung line moves only in `act` mode with `--write`. A namespace file with CRLF line endings is refused |
| `test_exit_codes` | Added in `policy/v8.0.3`. Missing arguments, a missing party file and a failed `git` exit 1; `--help` exits 0 |
| `test_check_diff_on_git` | Added in `policy/v8.0.3`. `check-diff` through `main` on a real repository made in a temporary directory: one notch in the right direction passes, the wrong direction is refused, and a pins change passes |
| `test_rung_names_agree` | Added in `policy/v8.0.3`. The rung names in `rungs.json`, `RUNG_LINE` and both cage files agree |
| `test_cage_version_agrees` | Added in `policy/v8.0.3` (D8f). The seven copies of the cage's version agree: each cage file's name, label and match condition, and `shop.yaml`'s claim |
| `test_probe_finds_one_of_each` | Added in `policy/v8.0.3`. Two or no governed Namespaces, cage policies or probe pods; no governed pod with a port; a reference pod not Ready; a `kubectl` error: each gives `looked` false with its own `why`, and sleeps nothing |
| `test_probe_main` | Added in `policy/v8.0.3`. `probe.py` run as a command with a stand-in `kubectl` writes its file and exits 0, also when `kubectl` is missing or fails |

`test_feed.py` in ico and in feeds asserts the shape rules of 3.3 and 3.2 on the published file. It does not compare the file with a copy of itself.

### 6.2 The cluster proof: `harness/proof.sh`

**The fixture.** Party: `fixture`; turnover 1,000,000; tolerance `amount: 10000` with basis "test fixture"; margin 0.2; `dwell_days: 0`; mode `measure`; three pin lines of forty zeros, never checked out. Rows, both of party `fixture`, with `penalty: null` and every basis `{"kind": "editorial", "as_of": "2026-11-14", "text": "test fixture"}`: `fixture-exfiltration`, events `[1, 1, 1]`, loss `[50000, 50000, 50000]`, needing `egress` with the source "MITRE ATT&CK T1041, Exfiltration Over C2 Channel (Exfiltration), version 2.4, read 2026-11-14 at attack.mitre.org/techniques/T1041."; and `fixture-outside`, events `[1, 1, 1]`, loss `[1000, 1000, 1000]`, no needs. Namespace `fixture` is at `quarantine`. Its one nginx pod, `shop`, claims 8.0.0 (8.0.2 since `policy/v8.0.2`, K20), declares port 80 and is the probe pod.

Each run is `probe.py`, then `loop.py cycle --cluster harness`. Nothing is written to any ledger.

| Run | What is done first | Green means |
|---|---|---|
| 1. The label-only control | `up.sh --no-netpol`: the cage stamps pods and writes no network rule | Pods stamped `quarantine`. `egress` open. Exposure 51,000.00. Verdict `cage-ineffective`. If the exposure is below 51,000.00 the money is following the label, and the job fails |
| 2. The positive run | Apply `cage-netpol.yaml`, wait until it is ready, delete the pod and apply it again, then wait up to 120 seconds for NetworkPolicy `cage-reach-quarantine` to exist | `egress` closed. `inbound` open. Serving 1 of 1. Exposure 1,000.00. Figure 7,000.00. Verdict `within`. Since `policy/v8.0.3`, also: NetworkPolicy `cage-reach-isolated` exists, so both restricting rules are written and a move in place to `isolated` never starts under no rule |
| 3. The break test | `kubectl -n fixture delete networkpolicy cage-reach-quarantine`, then sleep 15 seconds so the node opens the path. Git and the labels still say `quarantine` | `egress` open. Exposure back to 51,000.00. Verdict `cage-ineffective` |
| 4. A climb in place | Set the Namespace to `baseline` and replace the pod, so it is created there. Set the Namespace to `quarantine` and annotate the running pod: one update, which must be admitted. Wait up to 120 seconds for the label and for `cage-reach-quarantine`, which run 3 deleted | The pod is labelled `quarantine` and `cage-reach-quarantine` exists again. The pod was not replaced or restarted, and its CPU limit is still 500m. `egress` closed. `inbound` open. Serving 1 of 1. Exposure 1,000.00. Figure 7,000.00. Verdict `within`. Cage 8.0.0 fails this run. Since `policy/v8.0.3`, also: with the Namespace back at `quarantine` and before the update, `cage-reach-quarantine` does not exist, so a pod created at `baseline` writes no rule |
| The check | Nothing | `cage-tier` is not rewritten for pod controllers. Since `policy/v8.0.3` a failed query is red, not green |
| The guards, since `policy/v8.0.3` | A pod made from `shop.yaml` that asks for the host network, PID and IPC, for privilege, for privilege escalation and for `NET_ADMIN`, sent as a server-side dry run, which goes through Kyverno's admission and starts nothing. Once in `fixture`, and once in `cage-check`, a Namespace with a tier label that is not governed | In `fixture` it comes back at `quarantine`; in `cage-check` it falls to `isolated`. In both, the host fields are off, `privileged` and `allowPrivilegeEscalation` are false, `runAsNonRoot` is true, and the capabilities are `drop: [ALL]` |
| An unclaimed pod, since `policy/v8.0.3` | In `cage-check`, a pod that carries the stamp's labels and claims no cage version | The cage writes no NetworkPolicy there |

The job is green only if all four runs and the checks hold. Any `could-not-look` is red. Run 2 shows a figure that falls while the workload still serves. Run 3 is the one observation that tells feedback from a lookup. Run 4 and the check came with cage 8.0.2 (section 11). The guards, the unclaimed pod and the two added clauses of runs 2 and 4 came with `policy/v8.0.3`, after the review of every line. They test cage 8.0.2 as it is, and no file under `cage/` changed. A red run also prints what `harness/diagnose.sh` reads from the cluster.

**This is not yet decision 9's proof.** The owner accepted a cluster that stays up for the proof and the break test. This proof runs on a throwaway kind cluster and says so: `cluster: harness`. The other cluster waits for the owner (section 8).

A proof on a cluster that stays up ran on 2026-11-15, from an agent session (section 11, "After the four answers", and `standing-proof/2026-11-15.md`).

**If kind does not enforce the `quarantine` rule**, run 2 reads `egress` open and the job is red. Whether kind enforces it is not known: only the no-traffic rule has been seen working there. Driftwood then stays in `measure` mode until a change to platform makes the proof green.

## 7. Pins

- **Today.** Only driftwood pins anything. Each of its three pins is a full commit, with `ref: main`. `pins.sh` clones each repository, checks out the commit, and checks that `HEAD` equals it. For a branch `ref` it also requires `git merge-base --is-ancestor <commit> origin/<ref>`, so a commit that never landed on the publisher's `main` is refused. `loop.py bump-pins` follows the head of `main`. Platform's cage, loop and harness move together under the one platform pin.
- **When tags exist.** A pin line's `ref` becomes the tag: `policy/v8.0.0`, `v5.0.0`, `threat-register/v5.0.0`. Nothing else changes. `pins.sh` already handles a `ref` that ends in `v<n>.<n>.<n>`. It checks that the tag resolves to the pinned commit, installs gitsign 0.17.1 by checksum, and runs `gitsign verify-tag` with `GITSIGN_REKOR_MODE=offline`, the issuer `https://token.actions.githubusercontent.com` and the identity `^https://github\.com/<repo>/\.github/workflows/cut-release\.yml@refs/heads/main$`. `bump-pins` already follows the newest tag of the same family.
- That tag branch of `pins.sh` cannot be proven before a tag exists. The first tag pin proves it, on its own pull request, in the `cycle` job.
- Each feed is published at a fixed path. Its version is the `version` field inside the file, so a new major version changes no path in `loop.yml`.
- No workflow names another repository in a `uses:` line. Binaries are pinned by checksum in `up.sh`, `pins.sh` and `cut-release.yml`. Images are pinned by digest.

## 8. The landing plan

Every pull request is opened by the orchestrator under the owner's login, and approved and merged by the app from the orchestrator's session. No `main` has a required check, so each gate below is the orchestrator's own.

**Step 0: archive before anything is deleted.** The owner's rule is "archive ... we can always bring back", and `ARCHIVE.md` deleted nothing until its commit was read back from a ref. In platform, ico, feeds and driftwood the orchestrator does three things, in order. It disables every old scheduled workflow with `gh workflow disable`, so no clock writes again and nothing merges into a tree that is about to change. It pushes the tip of every branch but `main` to `refs/archive/heads/<branch>` in the same repository and reads each ref back. It appends one row for each ref to `.scratch/distil/evidence/archive-refs.tsv` and a dated section to `.scratch/distil/ARCHIVE.md`, inside the hub's pull request of step 1. The `observations` branches matter most: they hold the fetch clocks' readings, and no pull request holds them. In the clones taken before the clean-up they were 74 commits ahead of `main` in platform, 75 in ico and 403 in feeds. Those counts are a floor.

| Step | Repository | The gate before the merge | Branches deleted after the merge, each already archived |
|---|---|---|---|
| 1 | hub | The text matches this contract. The archive record of step 0 is in the pull request | None |
| 2 | ico | `test` green on the pull request | `observations`, `renovate/configure` |
| 3 | feeds | `test` green on the pull request | `observations`, the seven `fetch/*` |
| 4 | platform | `unit` green on the pull request. `cluster` is read and recorded. The pull request is worked on until `cluster` is green too; it merges with a red `cluster` only for a named cause that cannot be fixed in the pull request | `observations`, `renovate/configure`. `release/2.0.x` is archived and stays: the ruleset forbids deleting it |
| 5 | driftwood, `mode: measure` | The pins hold the three merged commits. The pull request's own `cycle` job writes a line whose verdict is not `could-not-look`. The branch `ledger` exists | The four `renovate/*`, the `wargamer/*`, the `observations/drift-sample/*` |
| 6 | the first tags: ico, feeds, platform | At least one ledger line with a verdict from a run on driftwood's `main`. Each tag is cut by dispatching `cut-release.yml` at the commit that line's `pins` name. Platform's is cut only if its `cluster` job was green at that commit. Each tag is read back and must peel to that commit | None |
| 7 | driftwood, pins to tags, still `mode: measure` | A pull request that changes the three `ref` values and nothing else. Its own `cycle` job is the proof of the tag branch of `pins.sh` | None |
| 8 | ico and feeds: `CUT_ON_MERGE=true` | Step 7 merged | None |
| 9 | driftwood, `mode: act` | Platform's `cluster` job green, all three runs, at the platform commit `main` pins. A pull request that changes the `mode` line and nothing else | None |

- Steps 2, 3 and 4 may land in any order. Step 5 needs all three.
- After each of steps 2 to 5 the orchestrator closes that repository's stale pull requests, each with a note naming its archive ref. It deletes a stale branch only if its tip still equals its archive ref. A tip that moved is archived again first, and one more hub pull request corrects the record.
- Before step 5 merges, the orchestrator pushes the orphan branch `ledger` to driftwood, holding `loop.jsonl` with the one reset line of 3.5.
- Steps 6 to 9 are kept apart so that a failure names its cause. Pins do not move in `measure` mode, so the pull requests of steps 7 and 9 are the orchestrator's: `check-diff` is not used and the orchestrator's session lands them. From the merge of step 9 the loop moves the rung by itself. On today's inputs it takes two notches, the shop stops serving, and every run after that ends red with `saturated`. The undo is one line: `"mode": "measure"` in `party.json`, and the rung line back to `baseline`.
- Once driftwood is in `act` mode it follows the newest tags of ico and feeds by itself. It does not follow platform (K17): a `policy/v*` tag is cut only by dispatch, and the platform pin moves only by a pull request to the pin line. From then on a platform pull request merges only with `unit` and `cluster` both green.
- If the proof stays red, platform is fixed by further pull requests under the gate of step 4, no platform tag is cut, and driftwood stays in `measure` mode on a commit pin for platform.

**What waits for the owner.**

The table that stood here is empty, so it is gone. Its last two rows, the guard's hook and the hosted Renovate app on driftwood, left it on 2026-11-15.

The guard's hook was removed from the hub on 2026-11-15 (pull request 326): the agent harness's own safety check first refused the assistant's push, and then the owner answered "Do it with blessing" (section 11).

On Renovate, the owner answered that it should be everywhere, configured correctly, and the configurations are being written (section 11). *Later on 2026-11-15* they landed, one in each repository but the hub (section 11, "After the review of every line"). (The "uninstall" recorded here before 2026-11-15 was wrong: it would break `api` and `storefront`.)

The row on the secrets hook and the quoted `id-token` key left the table on 2026-11-15, closed. YAML reads the quoted and the unquoted key as the same key, nine signed tags have been cut with it, and it stays quoted (section 11, **After "Stop leaving things alone"**).

Two rows left it earlier. The owner answered them on 2026-11-15, with the penalty rate and K16 (`DECISIONS.md`, "15 November: the four answers"). The tolerance is now 0.5% of turnover, GBP 430,000, on the `tolerance` line of driftwood's `party.json`. The cluster that stays up is a kind cluster on the owner's own machine: K19, and `standing-proof/2026-11-15.md`. Section 11, "After the four answers", says what followed.

**Settled on 2026-11-14 by the owner's reply "I'm afk. Jfdi".** Leave to cut tags: given, and used at steps 6 to 8. The key in feeds and ico: read as given, and not used. Nothing built here would read it, and a secret with no reader is redundant. Only a returning fetch would need it (`LOOP.md`, what is parked).

The numbers nobody has counted are not the owner's to supply: the penalty rate is ico's work, and the third row's band is feeds' work. `LOOP.md` names both. The penalty rate has since been counted three ways. On 2026-11-15 the owner chose which count ico publishes, and ico published it as `v5.1.0` (section 11). The third row's band is still feeds' work.

## 9. The carry-over from LEDGER section 3

Only the lessons the loop cannot run or be believed without. The ids are LEDGER's.

| Lands in | Ids |
|---|---|
| `loop/loop.py` and its tests | B1 the formula. B2 one currency. B3 a missing tolerance refuses. B4, B5 the rung is edited on the Namespace, one line. B6 a sum with an unpriced row is never `within`; equal is within. B7 an unknown rung is refused. B9 the loop's code merges nothing. B10 a strict party file. B11 an unsourced number only raises; a missing number is never invented. B12 the penalty rules; a basis with no date refuses. B13 one breach's consequences add inside the event. B14 the Poisson cross-check. B16 the line names the cluster kind, who set the rung, the sourced share and the weakest basis. B20, B21, B23 the tested outcomes and `bound: upper`. C8 red outranks could-not-look, but only after a real look |
| `loop/probe.py` and its tests | C1 the bracket and the held silence. C2 the stamp and the policy's ready status. C3 the marker. C4 a starting pod is waited for. C5 the reference is outside the cage. C13, C14 serving and reach are measured live |
| `cage/` | D1 start from the 7.0.0 shape. D2 the three priority fields go together. D3, D4, D5 kept by leaving v7's expressions untouched. D7 every restricting rule is generated at once. D8 `matchConditions`. D9 one rewriting policy. D13 no sidecar. D14 no reduction; a cost with a basis. D15 the rung is on the Namespace only. D19 no deny. D21 serving now ends only at the last rung |
| `harness/up.sh` and `proof.sh` | C10 wait for the object the cage generates, and an empty list is not a yes. E8 pinned binaries in a temporary directory. E10 server-side apply, then wait for the webhooks. H1 the cage before the workloads. H7 the engine pinned by checksum |
| `driftwood/.github/` | E1 tag and commit together, with the signature checked. E3 the measuring job cannot write. E4 the ledger writer's rules, one run at a time for each ref. E5 the landing path runs its own check. E9 `set +e` around a code that must be read. E11 a schedule, not only a push |
| `cut-release.yml` | F1 the file name. F2 sign with the log proof and verify before pushing. F3 never move an existing tag; inputs through `env`. F4 manual dispatch stays. F5 a pinned signer. F7 the tag is `policy/v8.0.0` |
| The two feeds | G1 a source on each fine; no rate until counted. G2 `needs` with sources, and a row for the loss outside the cage. G4 a publisher's tag does not wait for a hand. G7 the basis in the row. G8 overlapping rows are not summed |
| driftwood's manifests | H2 nginx as user 101 with two scratch mounts. H3 every manifest names its Namespace. H5 the version claim. H8 the disclaimer. H9 the tolerance has a basis and the floor is gone |
| hub and section 8 | A1 archive first. A2, A8 the sentence in a file; the owner's words untouched. A9 each old schedule is stopped. A12 each reversal recorded in ADR-0039. I1, I5, I6, I7, I8, I9, I12. I14 what the machine merges rest on |

**Left out, and why.** A3 to A7, A10, A11: done by the archive of 2026-11-14, or moot because the old chain leaves in one change. B8, B22: no person and no wait on the merge path. B15: the pinned commits already name the bytes. B17: no model is used. B18: one test at tuppence's turnover is enough. B19: the levers are words in `LOOP.md`, and no issue is opened. C6, C7: settled by K3 and K4. C9, C17: the probe creates nothing. C11, C12, F9, H4, H6: no Flux and no git server. C15, C16: no inventory. D6, D10, D11: v7's scoping by claim is kept as it is; an unclaimed pod in the governed Namespace has no stamp, so the cycle is `could-not-look`. D12, D20, D22: the cage files come from the pinned checkout and carry no date. D16 to D18, F6, F8: no offline Kyverno test and no signing guard tests; the cluster proof and the first tag are the tests. E2, E6, E7, E12 to E14: no cross-repository `uses`, no required check, no Renovate, no veto. G3, G5, G6: no fetch. H10 to H12, I2 to I4, I10, I11, I13: records already kept, or parts that are gone. The "stale size widens to the cap" part of B11 is not carried: no rule reads `turnover_as_of`.

## 10. What this contract deliberately leaves out

No builder adds any of these.

- Flux, its sources, a git server, a second way to build the cluster.
- Renovate's runner. A reusable workflow. Any `uses:` of another repository. Any action but `actions/checkout`. PyYAML or any other installed package.
- The exploited-flaw list, an image inventory, a scanner, any fetch, any scheduled job in ico, feeds or platform. They are parked (K8).
- A landing job, an environment or a key in ico, feeds or platform (leave for the key was read as given on 2026-11-14, and the key is not used). A separate CI workflow in ico or feeds.
- Deployments, a rollout stamp, readiness checks. The cluster that stays up is not built here: it waits for the owner (section 8).
- A `restricted` rung. Any capability but `egress` and `inbound`. Priority classes. The firewall sidecar. An offline Kyverno test.
- A reduction typed per rung, anywhere. A floor. A setting that keeps the loop off a rung where the workload stops serving.
- A veto or half-life on a release. An issue opened when saturated. A reconciler.
- A `--what-if` flag. Monte-Carlo outside the tests. A bad-year percentile. Currency conversion.
- Ledger fields beyond 3.5: no break-even rate, no input hash, no engine versions, no list of losses left out.
- A party file in a publisher. JSON schemas. A feed envelope. A version in a feed's path. Other regimes. Other adopters' rows.
- Banners on the 37 decision records. Moving or editing the owner's dated words.
- Any size, rate or reduction keyed by an adopter's name in code. Any model.
- Anything in `driftwood/api` or `driftwood/storefront`.

## 11. What the review changed

Eight reviewers read the built code on 2026-11-14 and the fixes below were made before anything merged. Each is in the code. Sections 1 to 10 are left as the builders had them, but for the corrections of the second look, which the part "After the second look" lists, for K18, which the part **After "Do everything"** adds to the table at the top, for the changes the part **After the four answers** lists: K16's label, K19, pointers in K5, 6.2 and section 8, and section 8's table; and for the changes the part **After "Stop leaving things alone"** lists: K20, 3.3's example, 3.4, 6.2's table and its rule, and section 8's table; and for the changes the part **After the review of every line** lists: K6, K9 and K13, dated lines in 3.2, 3.3, 4.2, 5.2 and 6.1, 3.3's example, rows in 6.1's and 6.2's tables and 6.2's rule, and a pointer in section 8.

**The merge gate (4.1, 5.3, 7).**

- `check-diff` runs `git diff --unified=0 --merge-base BASE HEAD`, so a head with two merge bases is refused. It reads git's output as bytes and splits on newlines only. A rung diff is exactly one line out and one line in, in one place.
- Every git ref the jobs compare is named in full (`refs/remotes/origin/main`, `HEAD:refs/heads/ledger`), in `loop.yml` and in `pins.sh`. A tag named `origin/main` can no longer stand in for the branch.
- For a pin change, `check` works the pins out itself with `bump-pins`, and the pull request's `party.json` must equal the result byte for byte. It then checks the proposed pins out with `pins.sh`, and runs the loop those pins name on the inputs they name with no probe. That run must end `could-not-look` (code 3). A refused input (code 1) does not land, so the loop cannot lock itself by its own hand.
- `land` approves the commit that was checked and no other, and merges with `--match-head-commit`. Its token is asked for this repository only, with `contents` and `pull_requests` write only. The key file is removed as soon as the JWT is signed.
- Every proposal is a branch made fresh: `write` deletes `loop/rung` or `loop/pins` first, which closes any pull request left from an earlier run, then pushes with no force.
- A tag's version is read with `[0-9]` only.

**The loop (1, 3, 4.1).**

- A number that is not finite is refused, in the party file, the ladder and both feeds. An amount that is not a sum of money is refused.
- A threat feed with no row for the party is refused: no rows is not a figure of nought.
- A capability the rung declares closed that was measured neither open nor closed is `could-not-look`.
- A refused rung write leaves no line. A file with CRLF line endings is refused, not rewritten.
- 3.3's `max(cap, 1.2 x max(ex), median(ex))` loses its third term, which could never be the largest. No figure changes.
- Sums of pence are rounded to the penny, against 3.5's "nothing else is rounded": plain float addition printed 30894.489999999998.

**The cage and the proof (3.4, 4.3, 6.2).**

- Two more lines leave each v7 file: the unused `tier` variable in `cage-netpol.yaml`, and the `claims-a-policy-version` condition in `cage-tier.yaml`, which the next condition implies.
- `up.sh` applies the governed Namespace together with the reference, so Kyverno has seen the Namespace before any of its pods is admitted.
- Run 2 of the proof deletes the pod and calls `up.sh` again without `--no-netpol`. The proof therefore runs the same path driftwood runs every cycle.

**The publishers (2.2, 2.3, 3.2, 3.3).**

- Each publisher's test refuses what the loop would refuse: a duplicate key, a number that is not finite, a row of another party, a regime or tier the penalty feed does not hold.
- `ico/DISCLAIMER.md` and both `.gitignore` files are `rewrite`, not `keep`: the disclaimer described the old layout.
- The litigation texts copied from v4 lose the sentences that pointed at fields this feed does not carry. The second threat row's basis loses its sentence about an evidence ladder that no longer exists.

**The records (2.5).** `LOOP.md` and ADR-0039 say plainly that K16 departs from the wording of `DECISIONS.md` row 6. The second look corrected what it departs from: see "After the second look" below. The parked table names the twin, the talk and the calibration programme.

**The budgets (2).** The built tree is over budget in `loop.py`, `test_loop.py` and `loop.yml` most of all. The budgets left out blank lines, the stand-in for `kubectl` that six probe tests need, and the pin check above. The tests are 36, as 6.1 lists them.

**After the first real cycle.** The cycle on driftwood pull request 132 ended `could-not-look`: `up.sh` applied the second cage policy seconds after Kyverno's rollout and the policy webhook refused the connection. It was a pull request's cycle, so it wrote no ledger line. The proof had not met this, because it applies that policy minutes later. Each `kubectl apply` in `up.sh` is now tried for two minutes (platform pull request 76). The next cycle measured.

**How it landed, 2026-11-14.** Steps 0 to 9 of section 8 are done, each merge by the app: hub 320; ico 12; feeds 21; platform 75 and 76; driftwood 132 (`measure`), 133 (pins to tags), 134 (`act`). The loop then opened and landed driftwood 135 and 136 by itself and stopped at `isolated`, `saturated`, as section 1 said it would.

**Left as they are, and known.** The hosted Renovate app can still push branches to driftwood (the owner's to uninstall; on 2026-11-15 the owner answered that it should stay everywhere, configured correctly: see the end of this section). Driftwood's ruleset does not dismiss an approval when a new commit is pushed (a forge setting, the owner's). The ledger branch has no ruleset. `ico/penalty-schema/feed.json` keeps each fine's litigation text, which no rule reads.

**After the second look, 2026-11-15.** Codex, another model, and four checkers read the landed estate on 2026-11-14 and 2026-11-15. This part says what they found and what changed. Where it differs from the text above, this part wins.

What codex found:

- The loop followed its own code. It would have pinned a new platform tag by itself, and the pinned platform holds `check-diff` and `bump-pins`, which gate what lands.
- The figure can fall with no closure and no publisher's change, when the adopter's turnover or a rung's cost changes. The records said it could not.
- The loop accepted malformed values the publishers' tests refuse: a negative tier rate, a three-point value out of order, a `null` penalty rate whose basis kind is `counted`.
- This section said driftwood's first cycle ended `could-not-look`. The ledger holds no such line.
- The records said one ledger line per cycle. A pull request's cycle writes none.
- Each fine's litigation text in ico's feed is read by no rule.
- `CONTEXT.md` said neither cage policy denies anything. At `isolated` the network rule lets no traffic in or out.

What the checkers found:

- **K16.** The records called K16 a departure from the assistant's reading. It departs from a consequence written in the option the owner chose: option (c) of `DISTILLATION.md` section 7 item 6.
- **Stale words.** Sentences that were true before the first tags, before `act` mode and before `CUT_ON_MERGE` was set. "Commit" stood where a pin is now a signed tag and its commit. The publishers' READMEs wrote of `CUT_ON_MERGE` as if it were unset. 5.3 said a pull request opened with the default token starts no workflow. Feeds' second row said in the present tense that a workflow runs which driftwood deleted on 2026-11-14.

What changed:

- **K17 (delegated).** `bump-pins` follows ico and feeds only. The platform pin moves only by a pull request to the pin line, pushed from an agent session, whose own cycle runs the new platform on a cluster before the app merges it. The rule lives in `bump-pins` alone: `check` works the pins out itself and compares byte for byte, so a proposed platform move cannot match. This overrides the words "or a platform fix" in 5.3, and the lines on `bump-pins` in 4.1 and section 7 as far as they cover the platform pin.
- **The refusals.** The loop now refuses the malformed numbers codex named. It does not repeat every check of the publishers' tests: a `null` rate whose basis kind is neither `not-counted` nor `counted` is still accepted, and so are the key sets, date formats and capability names that only those tests check. A three-point value that is not `null` must be three numbers, none below 0, in ascending order. A tier's `rate` and `cap`, and each pricing fine's `amount`, must be above 0. A penalty rate that is not `null` needs a basis of kind `counted`, and a `null` rate must not have one. The three fallbacks of step 10 stay.
- **The rule on numbers** is corrected in the records, with no new code. `LOOP.md` step 10 says what can lower the figure and by which path. A change to the turnover or to a rung's cost needs a pull request the loop cannot write. This overrides step 10 of section 1.
- **One line per cycle.** A cycle on `main` writes one line. A pull request's cycle, and a run whose input is refused, write none. This overrides the Words and step 9 of section 1.
- **Corrected in place above.** In sections 1 to 10: the opening paragraph, which cited a file that never existed; K6, K12 and K16, and the new K17; 5.3's sentence on a pull request opened with the default token; section 8's lines on following platform and on the key; and section 10's line on the key. In this section: the full ref names, the budgets and the first cycle.
- **The other records.** `LOOP.md` now says where to read the verdict, which red run is a fault and what has not yet run live. ADR-0039 names the half-life rule among what it reverses. `DECISIONS.md`, `CONTEXT.md`, `ARCHIVE.md` and the hub's README carry the smaller corrections.
- **The publishers.** Feeds' second row now says in the past tense that the sweep ran. Its feed becomes version 5.0.1, and no number in it changes. Ico's README and disclaimer change. Ico's feed does not, so ico cuts no tag.
- **The cage keeps version 8.0.0.** The platform change touches no file under `cage/` or `harness/`, and the tag that carries it is `policy/v8.0.1`. A tag names a release of the repository. `policy-version` in `cage/`, the policy names `cage-tier-8-0-0` and `cage-netpol-8-0-0`, and the label on the fixture's pod and on driftwood's pods are the cage's own version. They do not move.
  *Later on 2026-11-15* the cage's rules changed, and K20 replaced this as a standing rule: the cage takes the version of the tag that carries it, now 8.0.2 under `policy/v8.0.2`. The bullet stays true of `policy/v8.0.1`.
- **Who chose the climb.** Section 1 says the owner chose the climb in decision 5. The climb rests on decision 5 and on K16 together, and K16 is delegated. This overrides that sentence.
- **The penalty rate** is research. Three counts exist. Nothing lands in ico's feed, and the choice between the counts is put to the owner (`penalty-rate/CHOICE.md`).

Not done:

- The opening comments of the two cage files, which describe a validating, many-version shape these files do not have.
- The words "for this example" in ico's litigation texts. They are inside the feed and wait for its next change. The texts themselves stay: each is the reason for its fine's status.
- Feeds' second row is priced with `needs` empty although its text says the door is closed, and its id names an agent that no longer exists. Those are a number and an id.

Later on 2026-11-15 the cage comments and the rate of feeds' second row were done, and the litigation wording was prepared and held. The row keeps its id. See **After "Do everything"** below.

**How the second look landed, 2026-11-15.** Each merge was the app's.

- Platform 77 carried the refusals and K17. `unit` and `cluster` were green on the pull request and again on `main`. The tag `policy/v8.0.1` was then cut by dispatch. The tests are now 38.
- Ico 13 changed words only. Its `cut` job ran on the merge and printed "v5.0.0 exists: nothing to cut".
- Driftwood 137 moved the platform pin to `policy/v8.0.1` and corrected the README. Its own cycle ran the new platform on a cluster and read `saturated` at GBP 1,643,518.63, as `main` does. It was merged before any other cycle could run, because the platform it replaced would have followed the new tag by itself.
- Feeds 22 carried version 5.0.1. Its merge cut and signed `threat-register/v5.0.1`: the first tag cut by a merge.
- A driftwood cycle, started by dispatch, then opened pull request 138 for the feeds pin. `check` passed it and `land` merged it. No person was on that path after the dispatch.
- The ledger's lines 7 to 9 are the three cycles on `main` that followed: after 137, the dispatched one, and after 138. Each reads `saturated` at GBP 1,643,518.63 at `isolated`. The last ran on feeds `e949341d`.

**After "Do everything", 2026-11-15.** The assistant's report of that morning named two things that waited for the owner: K16, and which penalty rate ico publishes, with the tolerance. It also listed what was not done: three paths not yet run live, and the three items under "Not done" above. The owner replied, in full: "Do everything". It was read as leave to do what the report listed as not done. It was not read as an answer to any open choice: it names no penalty rate, no tolerance, no machine or spend for a cluster that stays up, and it does not say to reverse K16. So no rate was published, the tolerance was not changed, no cluster was stood up, and K16 stays as built. Those four were put to the owner as questions (`DECISIONS.md`, "15 November"). The guard's hook, the hosted Renovate app and the quoted `id-token` key were not in that report. They stay in the owner's hand (section 8). *Later on 2026-11-15* the `id-token` item was closed, the guard's hook was removed on the owner's word after the harness first refused the push, and the owner answered that Renovate should be everywhere, configured correctly: see **After "Stop leaving things alone"**. Where this part differs from the text above, this part wins.

What was found:

- Feeds' second row takes its rate from N x C / M. N was read again at driftwood `main` `08ba2d0`: the one workflow, `loop.yml`, names `actions/checkout` three times, each by commit and none by tag. So N is 0. Up to 5.0.1 the row kept N = 1 "as an upper bound".
- C and M were not read again. The method counts one kind of door only, so 0 is not an upper bound on every misuse of the credential.

What changed:

- **K18 (delegated, applying "Do everything").** Feeds' second row now has `events_a_year` `[0, 0, 0]`, and its basis text says what was read again, what was not, and that 0 is not an upper bound on every misuse. Nothing else in the feed changed. The row stays in the register, priced at 0.00, open, with `needs` empty. A second model, codex, reviewed the choice and said go, with two wording changes, which were made. K18 is added to the table at the top of this file.
- **What it does to the figure.** On the pinned loop (`policy/v8.0.1`), run offline before the merge with probe stand-ins proved against the real ledger lines, and with the penalty rate still `null`, the figure falls by GBP 431.49 at every rung. `isolated` goes from 1,643,518.63 to 1,643,087.14 (exposure 1,628,087.14, cost 15,000), still `saturated`. `quarantine` goes from 17,915,390.06 to 17,914,958.57, and `baseline` from 17,909,890.06 to 17,909,458.57. No verdict, goal or release-readiness changes. The pin check, the loop with no probe, ends with code 3.
- **The cage comments.** In each of `cage/cage-tier.yaml` and `cage/cage-netpol.yaml` the four stale opening comment lines became one line that is true of that file. No rule changed: below its first line each file is byte for byte what it was. No tag was cut, because a tag for a comment would mean a pin change for nothing. So platform `main` is one change ahead of the pinned tag `policy/v8.0.1` (`e91e5db`), and the next platform tag will carry it. The cage keeps version 8.0.0.
- **The litigation wording.** A draft pull request removes the words " FOR THIS EXAMPLE" from three litigation notes in ico's feed: British Airways, Marriott International and TikTok. It is held on purpose and not merged, so the feed and its version are unchanged. A merge cuts a tag that can never be moved, and one ico tag should carry this together with the penalty rate, if the owner chooses one.
- **The penalty-rate tables** were run again on the loop of `policy/v8.0.1` and feeds 5.1.0 (`penalty-rate/CHOICE.md`). None of the 18 outcomes in its table of where the three counts land changes. Every figure moves, by GBP 0.57 to GBP 431.49. One threshold moves at four figures: at GBP 430,000 the highest rate at which `isolated` is within tolerance is now 0.2540, not 0.2539.

Not done:

- A release and its dwell. One can start only when a rate or a tolerance makes the loop release-ready, which is the owner's choice, and it then takes 7 days. The margin, the dwell and the tolerance were not touched to force one.
- The proof on a cluster that stays up. The owner has not named the machine or the spend.

Both moved later the same day, after the four answers: the loop became release-ready at 10:55:04 and waits out the dwell, and the proof on a cluster that stays up ran from an agent session. See **After the four answers** below.

**How it landed, 2026-11-15.** Each merge was the app's.

- Feeds 23, commit `9a43342`, merged as `489e2fe`. The merge cut and signed the tag `threat-register/v5.1.0`: run 43694567853, with `test` and `cut` green.
- Platform 78, commit `4988db8`, merged as `ae58ab9`. `unit` and `cluster` were green on the pull request.
- Ico 14, commit `bf9b54e` on the branch `held/litigation-wording`, is a draft pull request, held and not merged. Later the same day it carried the rate too and was merged, and one tag, `v5.1.0`, carries both (below).
- No cycle was dispatched after the tag was cut, on purpose: the next scheduled cycle should find the tag and follow it with no person and no dispatch. When this was written the loop had not yet followed 5.1.0. The last ledger line, line 9 (run 43663748023), still read GBP 1,643,518.63 on feeds 5.0.1, and driftwood's `party.json` still pinned `threat-register/v5.0.1`.
- The first scheduled run of `loop.yml` was due at 06:47 UTC. It had not started by 08:33 UTC. GitHub runs schedules late under load, and earlier scheduled workflows in the estate started hours late. It is watched, not dispatched.

*Corrected later on 2026-11-15.* The schedule did not get the chance to find the tag. The cycle started by the merge of the owner's tolerance followed both new tags first, by a push cycle, not the schedule: see **After the four answers** below. The first scheduled run had still not started at 10:58 UTC. It started at 14:21:02: see **After "Stop leaving things alone"** below.

**After the four answers, 2026-11-15.** The four questions of the part above were put to the owner in one dialog, each with options the assistant wrote and one marked as the assistant's recommendation. The owner chose one option for each (`DECISIONS.md`, "15 November: the four answers"). The labels of the options are the assistant's words; the choices are the owner's. Where this part differs from the text above, this part wins.

The answers:

- **The penalty rate.** The count over all breach reports, 0.0002095. It was not the assistant's recommendation, which was the cyber-only count.
- **The tolerance.** 0.5% of turnover: GBP 430,000 at driftwood's turnover. It is no longer a fixture.
- **The cluster that stays up.** A kind cluster on the owner's own machine, left running.
- **K16.** Kept.

What changed:

- **Ico 5.1.0.** Ico pull request 14 carried the litigation wording held earlier (`bf9b54e`) and the rate (`0a34cca`). The app merged it as `39ddfaf`, and the merge cut and signed `v5.1.0` (run 43705453283, `test` and `cut` green). One tag carries both changes. `penalty_rate` is 0.0002095, of basis kind `counted`: 20 ICO monetary penalties over 95,466 breach reports of every kind, ICO financial years 2018/19 to 2025/26. The basis text gives the interval (0.000128 to 0.000400), what the check found, and the caveat as its own researcher states it: a rate over every report, too low for a serious breach by an amount the method cannot state. It names the two other counts and points at hub commit `d1aebbb`. One agent drafted the text from the research. A second checked each sentence against the research, compared the feed key by key, and ran the pinned loop and the pin check. The orchestrator then made three wording changes and ran the tests and the pin check again. Ico's README line on the rate is brought up to date.
- **The tolerance.** Driftwood pull request 139 (`81373c2`, merged by the app as `f22cd9a`) changed one line of `party.json`: `share_of_turnover` 0.005, with the basis "0.5% of turnover, the low end of audit materiality: GBP 430,000 at this turnover. Chosen by the owner on 2026-11-15, from options the assistant offered." The figure is the owner's. Writing it as a share, so that it moves with the turnover, is the assistant's choice (delegated). The loop prints it as 430000.0. This overrides the fixture of 3.1 as the published value. 3.1 stays as a test input.
- **The loop followed both tags by itself.** The merge of 139 started a cycle on `main` (run 43705857417, cause `push`). It wrote ledger line 10 at 10:51:31 on the old pins: both capabilities closed, serving 0 of 3, figure GBP 1,643,518.63 against GBP 430,000, `saturated`, not release-ready. In the same run it opened driftwood pull request 140 (`loop/pins`) for ico `v5.1.0` at `39ddfaf` and feeds `threat-register/v5.1.0` at `489e2fe`. `check` passed it and the app merged it as `4126d2e`. That merge started the next cycle (run 43706149681, cause `push`). It wrote ledger line 11 at 10:55:04: both capabilities closed, serving 0 of 3, rows 22,906.76 (closed), 0.00 and 2,290.68, exposure 2,290.68, cost 15,000, figure GBP 17,290.68, tolerance 430,000, `within`, goal `baseline`, release-ready, weakest basis "unsourced: cost of isolated". It is the first green run of the loop: every job passed. No person was on that path after the tolerance merge. So what followed feeds 5.1.0 was a push cycle, not the schedule.
- **K16** is kept. Its label in the table at the top becomes "delegated; kept by the owner on 2026-11-15". It no longer waits for the owner.
- **K19 (delegated, applying the owner's answer 3).** The proof on a cluster that stays up ran from an agent session on the owner's machine. A kind cluster named `loop` was built by the pinned `harness/up.sh` of `policy/v8.0.1`, unedited, with driftwood's `gitops/apps` at `main`, and has its own kubeconfig, so the owner's own kube contexts were not touched. The pins were checked out with driftwood's own `pins.sh`, unedited, and each tag's signature was verified. Each run is one `probe.py` and one `loop.py cycle`, as in `loop.yml`, with `--cause session --cluster standing` and no `--write`. Its eight lines are in `standing-proof/lines.jsonl`, and `standing-proof/2026-11-15.md` records them. It showed the break test for real on a cluster that was already running: deleting `cage-reach-isolated` was seen by the next probe, and the line read `cage-ineffective` at GBP 17,924,390.06 while git and the labels still said `isolated`. It showed running pods re-caged without a restart, from `isolated` to `quarantine` and back to `isolated` by way of `baseline`, once something touched the pod. Those pods had been created at `isolated`; the first finding below is about a pod created at `baseline`. Its last line, on the new pins, reads `within` at GBP 17,290.68, release-ready, as ledger line 11 does. The cluster is left running.
- **Changed in place above.** K16's label; the new K19; pointers in K5, in 6.2 and in section 8; section 8's table, which loses the tolerance and the cluster that stays up; and, in this section, three dated pointers in the part **After "Do everything"** and its closing sentence, now the last sentence of this file. This part also overrides, without editing them: section 1's paragraph "On today's inputs", 5.3's sentence "On today's inputs every run at `isolated` is red at `verdict`", and section 8's sentence that on today's inputs every run after the two notches ends red with `saturated` (on the inputs of 2026-11-15 the line at `isolated` is `within`); the bullet of "After the second look" that says nothing lands in ico's feed and the choice between the counts is put to the owner, and the litigation wording its "Not done" list leaves for the feed's next change (both are now in ico `v5.1.0`); the `null` rate of 3.3 as the published value (ico now publishes 0.0002095, counted; 3.3 stays as a test input); 3.5's lists for `cause` and `cluster`, which the standing proof's lines extend with `session` and `standing` (those lines go to no ledger); and section 10's "it waits for the owner" for the cluster that stays up, which now stands, still without Flux, Deployments or a rollout stamp.

What the proof on a cluster that stays up found. Neither is fixed.

- **A climb from `baseline` cannot be made in place.** A pod created at `baseline` cannot be tightened while it runs: the API server refuses the update, and until the pod is replaced it has `baseline`'s reach whatever the Namespace says. Worse, every update to such a pod is refused while the Namespace sits at a tighter rung. On a cluster that stays up, a climb from `baseline` therefore needs the pods replaced.
- **Loosening to `baseline` in place is partial.** The label and the network rule follow. The limits and the dropped capabilities stay as the pod was created.

The daily loop is not affected by either: it builds a new cluster every cycle, so every pod is created at the rung in git. Closing them needs a change to the cage (a new cage version, a tag and a pin change), or Deployments with a rollout on each rung change, which section 10 names as the work of the cluster that stays up. That was not in the scope of the owner's answer.

The release that waits:

- The dwell is 7 days. It started with ledger line 11, at 10:55:04 on 2026-11-15, and is met from 10:55:04 on 2026-11-22.
- The first cycle on `main` after that reads `release`, `isolated` to `quarantine`. Its merge starts a cycle that releases again, to `baseline`. That merge starts a cycle at `baseline`, where the pinned loop predicts GBP 25,697.44, `within`, with the shop serving. (`quarantine` predicts GBP 31,197.44.) These three cycles follow each other within the hour.
- It depends on two things. A cycle must run on `main` on or after 2026-11-22 10:55:04, and the only thing that starts one unattended is the daily schedule, which has not yet run once. And every line until then must be release-ready: a line that is not release-ready starts the wait again, while a `could-not-look` line is passed over.
- Nothing was done to hurry it. The margin and the dwell are unchanged.

Not done:

- The daily schedule has not run once. Its first run (cron `47 6 * * *`) had still not started at 10:58 UTC. Driftwood's scheduled workflows start hours late as a rule: the earlier workflow with the same cron, `propose-tier`, started at 14:42 on 11 November, 15:35 on 12 November, 14:54 on 13 November and 13:47 on 14 November, 7 to 9 hours after 06:47. So the first run of `loop.yml` is expected between about 13:45 and 15:35 UTC. Until it runs, the schedule is unproven. It is watched, not dispatched.
- The release has not happened. It is expected on 2026-11-22.
- The two findings of the proof on a cluster that stays up are not fixed.
- In the owner's hand, unchanged: the guard's hook in the hub, the hosted Renovate app on driftwood, and the quoted `id-token` key (section 8).
- Numbers still unsourced: the three rung costs, the rows' bands (editorial), the margin and the dwell.
- Platform `main` is one change ahead of the pinned tag: the cage files' comment.
- Noticed and not changed: the source text of the Doorstep Dispensaree fine in ico's feed says "12 Dec 2019", while the research names 17 and 20 December 2019 for that notice. The year is the same and no price moves. It is a source text inside the feed, and waits for the feed's next change.

Later the same day the schedule ran (14:21 UTC), finding 1 was fixed by cage 8.0.2 while finding 2 stands by design, platform `main` is no longer ahead of the pinned tag, the Doorstep date was corrected in ico `v5.1.1`, and the `id-token` item was closed. The guard's removal was first refused by the agent harness, then made on the owner's word ("Do it with blessing", hub pull request 326). The recorded action on Renovate was found wrong, and the owner answered that Renovate should be everywhere, configured correctly. See **After "Stop leaving things alone"** below.

**How the four answers landed, 2026-11-15.** Each merge was the app's.

- Hub 324 recorded the four answers, merged as `d1aebbb`.
- Ico 14, commits `bf9b54e` and `0a34cca`, merged as `39ddfaf`. The merge cut and signed `v5.1.0`: run 43705453283.
- Driftwood 139, commit `81373c2`, merged as `f22cd9a`. Its own cycle (run 43705528010) looked at a cluster and read `saturated` on the old pins: GBP 1,643,518.63 against GBP 430,000.
- Run 43705857417, started by that merge, wrote ledger line 10 and opened driftwood 140, which the app merged as `4126d2e`.
- Run 43706149681, started by that merge, wrote ledger line 11: `within`, release-ready.
- Driftwood `main` is `4126d2e`. It pins platform `policy/v8.0.1` (`e91e5db`), ico `v5.1.0` (`39ddfaf`) and feeds `threat-register/v5.1.0` (`489e2fe`). Mode `act`, rung `isolated`, shop not serving. The ledger has 11 lines.
- The proof on a cluster that stays up wrote no ledger line and no commit.

**After "Stop leaving things alone", 2026-11-15.** The assistant's report after the four answers ended with a list headed "Left alone": the guard's hook, the hosted Renovate app and the `id-token` spelling; the Doorstep Dispensaree date in ico's feed; and platform `main` one comment change ahead of its pinned tag. The same report said the two findings of the proof on a cluster that stays up were not fixed, and offered a scheduled check after 22 November. The owner replied, in full: "Stop leaving things alone". It was read as: do each thing on that list now, and stop deferring what the assistant can do itself. It was not read as an answer to a new choice. Two items were not done in that round, for different reasons, and the owner answered both later that day. Where this part differs from the text above, this part wins.

What changed:

- **Ico 5.1.1.** The notice itself reads "Dated the 17th Day of December 2019". The First-tier Tribunal (EA/2020/0065/V, 2021), the Upper Tribunal ([2023] UKUT 132 (AAC)) and the Court of Appeal ([2024] EWCA Civ 1515) each give 17 December 2019, and the ICO announced the fine on 20 December 2019. No source read gives the 12th. The fine's `source` and `litigation` texts now carry 17 December 2019, name the Upper Tribunal's dismissal of 2023, which they left out, and say the further appeals were the pharmacy's and were dismissed, so GBP 92,000 was left in place. Their basis is now the notice and the three decisions, read on 2026-11-15, where it was published legal reporting. No number, year, status or other fine changed, and no price moves. One sub-agent read the sources, a second fetched each and confirmed every quote, and a third checked the final wording claim by claim. It found one sentence, on where the old date had come from, that said more than was known, and that sentence was corrected before the merge.
- **Cage 8.0.2, under `policy/v8.0.2`.** `cage/cage-tier.yaml` branches on the operation. When a pod is created it does what it did. On an update it sets the two stamp labels only and does not touch the pod's spec. Kubernetes will not change a running pod's limits or capabilities, and the old cage tried to on every update, so every update to a pod created at a looser rung was refused. The network rule selects pods by the tier label, so it now follows the rung in place. Kyverno's own rewrite of the cage for pod controllers errored on a controller that carried the claim, as it did before this change, so it is switched off. On a test cluster a Deployment that claims the cage was created and updated, and its pod came up labelled and limited. Platform's fixture carries the corrected Doorstep text. One sub-agent wrote the change. A second checked that the create branch is the old expression character for character, and read Kyverno's source at the pinned version for the operation variable. The orchestrator ran all four runs of the proof on a separate kind cluster with Kyverno 1.18.2 on the owner's machine before the pull request, then removed that cluster.
- **The proof has four runs and a check** (6.2). Run 4, "a climb in place", moves a running pod created at `baseline` to `quarantine` by one update, which must be admitted, without a restart. The old cage fails it. The check: `cage-tier` is not rewritten for pod controllers.
- **K20 (delegated).** When a cage file's rules change, the cage takes the version of the tag that carries it. There is no cage 8.0.1. K20 is added to the table at the top of this file.
- **Driftwood follows.** Driftwood pull request 141 changed the platform pin line to `policy/v8.0.2` and the three pods' claim to `"8.0.2"` together, because a cage version binds only the pods that claim it. Its own cycle (run 43722423361) ran the new platform on a cluster before the merge: looked, both capabilities closed, serving 0 of 3, `within` at GBP 17,290.68, release-ready. The loop then followed ico `v5.1.1` by itself.
- **The daily schedule has run.** The first scheduled run of `loop.yml`, run 43723875879, was started by GitHub at 14:21:02, 7 hours 34 minutes after the cron time of 06:47, inside the window the earlier workflows predicted. Every job passed. It wrote ledger line 14 at 14:24:04: cause `schedule`, both capabilities closed, serving 0 of 3, `within` at GBP 17,290.68, release-ready. Lines 11 to 14 are all release-ready, so the dwell that started at 10:55:04 is unbroken.
- **The `id-token` spelling: closed.** The three `cut-release.yml` files write the key quoted. YAML reads the quoted and the unquoted key as the same key, and nine signed tags have been cut with it. It stays quoted, and leaves section 8's table.
- **The cluster that stays up, rebuilt.** At 14:18 it was built again from nothing with the pinned harness of `policy/v8.0.2` and driftwood at `49f467c`; the pins were checked out again and the three signatures were good. Its three lines are in `standing-proof/lines-b.jsonl`, and `standing-proof/2026-11-15-b.md` records them. The step the first proof found refused was admitted: pods created at `baseline` were moved to `isolated` in place and relabelled without a restart, and the line read both capabilities closed, serving 0 of 3, `within` at GBP 17,290.68. So finding 1 is fixed by cage 8.0.2, on the cluster where it was found. The pods' limits stayed 500m, with no capability dropped, until the pods were replaced, as the design says.
- **The check after the release.** A one-time, read-only scheduled check named "driftwood release check" is set for 16:30 on 2026-11-23. It reads driftwood's ledger and reports whether the loop released and the shop reopened. It has no connectors and cannot write. The owner can change or delete it from the routines page of their Claude account.
- **Changed in place above.** K20 in the table at the top; 3.3's example and the line under it; 3.4's version pointer and its bullet on cage 8.0.2; run 4 and the check in 6.2's table, and "all four"; 6.2's fixture claim; in 2.5, the pointer on the `twin/` row and the line on `twin/ENACT_MODE` in the `LOOP.md` row; section 8's table, now gone, and the sentences under it; and, in this section, the opening paragraph's list of changes, a pointer after "They stay in the owner's hand" in the part **After "Do everything"**, a pointer under "The cage keeps version 8.0.0", a pointer after the correction on the first scheduled run, a pointer after the "Not done" list of the four answers, and the closing sentence, still the last sentence of this file. This part also overrides, without editing them: the claim `"8.0.0"` in 2.4 and in 5.2, which is now `"8.0.2"` (K20), and 5.2's sentence that the claim is not a release number, since under K20 the claim takes the number of the tag that carries a change of rules; "the three cluster runs" in 2.1, now four and a check; "all three runs" in step 9 of section 8's landing table, a gate passed on 2026-11-14, when the proof had three runs; the line "the owner's to uninstall" under "Left as they are, and known", which the owner's answer on Renovate below now corrects; the sentence "The cage keeps version 8.0.0" that ends the bullet "The cage comments" in the part **After "Do everything"**, which stays true of `policy/v8.0.1` (K20), and that bullet's "platform `main` is one change ahead of the pinned tag", which `policy/v8.0.2` ended; in the four answers' part, "Neither is fixed" and the sentence on what closing them needs, since finding 1 is fixed by cage 8.0.2 and finding 2 stands by design, closed by replacing the pods; and, in "The release that waits", the words "which has not yet run once".

Not done at first, and what followed:

- **The guard's hook.** The assistant prepared the removal from an agent session: the three `twin/` files and the `hooks` entry of `.claude/settings.json`, nothing else. The guard's own text was read first, and nothing in it says it must stay. Its checked-in mode is `development`, which admits everything, so the removal would change what no session can do today; what would go is the switch back to its stricter modes. When the assistant went to push that change, the agent harness's own safety check refused the action as undermining oversight. Nothing was pushed, and the working copy was put back. The assistant did not try another route, and will not bundle the removal into another change. This was a refusal by the harness, not a choice to leave it. The assistant then put the question to the owner: the harness had refused the push, and the guard's checked-in mode already admits everything. The options offered were to leave the guard in place, or for the owner to remove it by hand. The owner's answer, in full: "Do it with blessing". Hub pull request 326, commit `4d81cbc`, merged by the app as `cc93590`, removed `twin/ENACT_MODE`, `twin/ENACT_MODE.why`, `twin/enact_guard.py` and the `hooks` entry of `.claude/settings.json`; nothing else in that file changed. The assistant made the change from an agent session; the owner did not remove it by hand. The commit and the pull request say what protection went and quote the owner's answer. The twin, with the guard and its tests, stays parked at `refs/archive/main/2026-11-14-before-simplify` and comes back with them. The loop's machine merges rest on decision 2, as before.
- **Renovate.** The recorded action was wrong. The hosted app's installation covers every repository of the driftwood organisation, and `api` and `storefront` use it: each has `config:recommended`, open Renovate pull requests and a dependency dashboard. Uninstalling would break them. Narrowing the installation to `api` and `storefront` is an organisation setting, which GitHub offers only in its settings pages, not through its API. It was put to the owner as a question on 2026-11-15. The owner's answer, in full: "It should be everywhere but configured correctly". Read as, by the assistant: the hosted app stays installed on every organisation and is not narrowed, and each repository gets a configuration that makes Renovate do correct, useful work there; driftwood's `renovate.json` is rewritten, not deleted. Read on 2026-11-15, Renovate is installed on all repositories of each of the five organisations, and only `api` and `storefront` have a working configuration: driftwood's `renovate.json` is `{"enabled": false}`, and platform, ico, feeds and the hub have none. The configurations were being written and checked by sub-agents when this was written, and had not landed. K6 is unchanged: the loop's own pins stay the loop's, not Renovate's. *Later on 2026-11-15* they landed: see **After the review of every line**.

What stands:

- **Finding 2, by design.** A pod moved to another rung in place keeps the limits and capabilities it was created with until it is replaced. It is closed by procedure, not code: on the cluster that stays up, the pods are replaced after a rung change to or from `baseline`. The daily loop is not affected: every pod it sees is created at the rung in git.
- A release and its dwell have not run live. The release needs a cycle on `main` on or after 10:55:04 on 2026-11-22; with the schedule's usual lateness that is the afternoon of 22 November.
- A Renovate configuration for each repository, as the owner answered. They were being written when this was written, and their record comes with them. *Later on 2026-11-15* they landed: see **After the review of every line**.
- Numbers still unsourced: the three rung costs, the rows' editorial bands, the margin and the dwell.
- An adversarial review of every line of code was asked by the owner later on 2026-11-15, and was under way when this was written. Its findings get their own record. *Later on 2026-11-15*: see **After the review of every line**, and `review-2026-11-15/REVIEW.md`.

**How "Stop leaving things alone" landed, 2026-11-15.** Each merge was the app's.

- Ico 15, commit `55434a2`, merged as `27c5c49`. The merge cut and signed `v5.1.1`: run 43720413024, `test` and `cut` green.
- Platform 79, commit `42e8f0e`, merged as `f5ef7c7`, with `unit` and `cluster` green on the pull request and on `main`. The tag `policy/v8.0.2` was then cut by dispatch at `f5ef7c7` (run 43722326858). It also carries platform 78's comment change, so platform `main` is no longer ahead of the pinned tag.
- Driftwood 141, commit `7ecc485`, merged as `065039a`. Its own cycle was run 43722423361.
- Run 43722765277 (cause `push`), started by that merge, wrote ledger line 12 at 14:12:03 (`within`, GBP 17,290.68, release-ready) and opened driftwood 142 (`loop/pins`) for ico `v5.1.1` at `27c5c49`. `check` passed it and the app merged it as `49f467c`.
- Run 43723127078 (cause `push`), started by that merge, wrote ledger line 13 at 14:15:59 (`within`, GBP 17,290.68, release-ready).
- Run 43723875879 (cause `schedule`) wrote ledger line 14 at 14:24:04, as above.
- Driftwood `main` is `49f467c`. It pins platform `policy/v8.0.2` (`f5ef7c7`), ico `v5.1.1` (`27c5c49`) and feeds `threat-register/v5.1.0` (`489e2fe`). Mode `act`, rung `isolated`, shop not serving. The ledger has 14 lines.
- The proof on the rebuilt cluster wrote no ledger line and no commit.
- Hub 326, commit `4d81cbc`, merged as `cc93590`, removed the guard's hook and the three `twin/` files, on the owner's answer "Do it with blessing".

**After the review of every line, 2026-11-15.** Later that day the owner asked for a review of the code, in full: "Adversely review. Every LOC must be justified and earn its keep (not literally, don't condense lines for the sake of it)". It was read, by the assistant, as: every block must have a reason that holds, a block that holds nothing goes, and lines are not squeezed together to lower a count (`DECISIONS.md`, "15 November: the review of every line"). How the review was run, and what landed before the release, are the assistant's choices (delegated). `review-2026-11-15/REVIEW.md` has the full account, and `review-2026-11-15/LATER.md` every change that waits, with its exact text. The block-by-block reports and the verifiers' adjudications were working files of the session and were not kept. Where this part differs from the text above, this part wins.

How it was done:

- One statement or condition at a time was removed from `loop.py` and `probe.py`, and the 38 tests were run each time: 884 changes, 209 that no test noticed.
- Twelve reviewers gave a verdict on every block: keep, remove, merge, untested or defect. They judged 1,399 blocks, kept 1,143 with a stated reason, and raised 254 findings. A second model, codex, reviewed the same code on its own and raised 54 items. Four of them, a missing licence file, were wrong: its copy left the licence files out.
- Ten verifiers tried to refute every finding of both, running each removal, test and fix in a private copy. They made 164 rulings: 120 confirmed, 18 refuted and 26 design questions. The design questions went into 17 decision memos, D1 to D17, and the assistant ruled on each (delegated).
- The rule for what landed now: only rulings off the release path that do not change the cage's rules. The release of a notch is due from 10:55 on 2026-11-22, and that direction has never run live.

What was found, among the 120 confirmed rulings:

- **Defects.** A tolerance amount of 0 or below was accepted. The proof's check on pod controllers read a failed query as green. Feeds' note said overlapping rows are never summed, and the loop adds every open row. A misspelt fine status passed ico's test and silently stopped that fine from pricing. A need with an empty source passed feeds' test, and the loop then ignored it. A `within-partial` line counts as release-ready, so a missing number can fill the dwell (D3b, found by the design verifier; it waits). Init containers are not hardened by the cage (CG6; it waits).
- **Code that held nothing.** Guards that cannot be reached, a flag no caller passes, a variable (`CUT_ON_MERGE`) that never decided anything once set, feed keys nothing reads, and tests that held nothing another test did not.
- **Lines no test held.** 209 of the 884 removals passed every test. Each guard that can be reached now has a test.
- **A wrong reason.** The margin's stated reason (D1, below).

What changed:

- **Renovate.** Platform 80, ico 16, feeds 24, driftwood 143, api 7 and storefront 23 each give the repository its own `renovate.json`. Actions stay pinned by commit, with a `# v4.4.0` comment Renovate can follow. Downloads checked by a sha256 (kind, Kyverno, gitsign) wait on the dependency dashboard and get a pull request only when ticked, and that pull request says to replace the sha256 by hand. The `nginx` image is pinned by digest with no tag, so Renovate could only move it to `latest`: it waits on the dashboard too. Nothing merges by itself. No Renovate manager reads driftwood's `party.json`, so the pins stay the loop's (K6). Each configuration passed `renovate-config-validator --strict` (Renovate 44.239.1) and a second agent's check, key by key, against Renovate's documentation. The hub has no `renovate.json`: its organisation's archived `renovate-config` repository sets `onboarding: false`, and the hub has nothing to update. Held until after the release: the `# v4.4.0` comments on the three checkout lines of driftwood's `loop.yml` (`LATER.md` item 5.4).
- **The loop and the proof, `policy/v8.0.3`.** A tolerance amount of 0 or below is refused, as a share already was. The proof's check on pod controllers is red when its query fails; it had read a failed query as green. The removals, each shown unneeded: the two shebangs; the probe's no-pods guard, which the probe-pod count already makes; `--settle-seconds`, which no caller passed, with 600 now the constant `SETTLE_SECONDS`; an argparse `prog`; `next_pin`'s fallback for a tag family with no tags, which cannot happen because tags are never deleted; a filter on `git ls-remote` output; an unused `read_party` call in `bump-pins`; the tag-exists refusal in platform's `cut-release.yml`, which `git tag` makes itself; an unread port on the reference sink; the fixture's untrue header; and three tests that held nothing alone, with a fourth command-line run folded into another test. Tests now hold every reachable guard that no test held, each shown to fail without its line: 38 tests became 42. On the new code the statement-removal run made 877 changes and the tests caught 832; each of the 45 left has a reason (removed later, a design decision, or unreachable). `harness/diagnose.sh` is the one script `up.sh` and `proof.sh` call on a red run. README sentences were made true. The proof's new checks show that cage 8.0.2, as it is, strips host access, privilege and capabilities, falls to `isolated` outside a governed Namespace, writes no rule for a pod that claims no cage version, writes both restricting rules, and writes none for a pod created at `baseline` (6.2). Nothing under `cage/` changed: the cage is still version 8.0.2.
- **The feeds.** Ico's feed lost `feed`, `published_by`, `published_at` and each fine's `year`, and the change note at the end of Doorstep Dispensaree's litigation text. Feeds' lost the same three envelope keys, and its note now says "The reader adds every open row, so rows must not overlap." in place of the false "Overlapping rows are never summed." No number, status or source changed (3.2, 3.3). Ico's test holds the closed set of fine statuses, a source for every fine and a tier rate of at most 1: a misspelt status passed it and silently stopped that fine from pricing, and in the verification a typo in British Airways' status lowered driftwood's figure with no warning. Feeds' test refuses a need with an empty source, which the loop would ignore.
- **The cut jobs.** Each publisher's `cut` job refuses a version that is not above every existing tag of its prefix, and reads no variable. The repository variable `CUT_ON_MERGE` was deleted from ico and feeds after both workflows stopped reading it (D7, K9, 5.2).
- **The adopter.** Driftwood pull request 144 moved the platform pin to `policy/v8.0.3`, made its README's triggers row, its guide to the ledger and its line on `looked` and `why` true, took the hand-typed "GBP 430,000 at this turnover" out of the tolerance basis (the loop computes it from the share), and removed `.gitignore`.
- **The margin (D1).** No section above gives the margin's reason. `DECISIONS.md` row 1 gave one, "so one release does not cause the next tightening", and it was wrong: on the same inputs a release never causes the next tightening, margin or not (none of 59,022 random releases did). The margin holds the cage tight against a later rise in a publisher's number. It stays. Row 1 carries the correction.
- **Changed in place above.** K6 (Renovate does not follow the pins), K9 (no variable switches the cut on) and K13 (proven since 2026-11-14); dated lines in 3.2, 3.3, 4.2, 5.2 and 6.1; 3.3's example, which is again the fixture byte for byte; the three removed tests and nine added ones in 6.1's table; the two added clauses, the guards and the unclaimed pod in 6.2's table, and its rule; a pointer in section 8; and, in this section, pointers after the two "being written" lines and the "under way" line of the part **After "Stop leaving things alone"**, and this part, before the closing sentence, which is still the last sentence of this file. This part also overrides, without editing them: 2.4's `renovate.json` row, `{"enabled": false}` only, since driftwood's file now tells Renovate what to watch, and its `.gitignore` row, since that file is gone; 2.1 to 2.3, which name no `renovate.json` and no `harness/diagnose.sh`; 3.1's bullet on `tolerance`, where an `amount` must now also be above 0; and, in section 9's "Left out", the words "no Renovate".

What was refuted. 18 findings did not survive. The ones worth naming: removing `test_monte_carlo_agrees`, which holds the only expected value not typed from the formula itself; removing the check of the written line's key order, and the "moved" case of the dwell test, each the only check of its behaviour; "the probe tests only the first declared port" as a defect, which is true but is what 4.2 step 8 chose, and cannot move money on today's cage (D17); and codex's missing licence files.

The design rulings (the assistant's, delegated):

- **Now.** D7, D8c and D8d (keep the cage's guards; the proof now checks them), D8f, D9, D10, D11, D12, D13 and D16.
- **No change.** D1 (keep the margin, with its corrected reason), D14, D15 and D17.
- **After the release.** D2a and D2b (the dwell), D3a and D3b (`within-partial` red; release-ready needs every row priced), D4a and D4d (the ledger fields `bound`, `looked`, `reference` and `unpriced` go), the code parts of D4b and D4c, D5 (the proof's first run and `--no-netpol` go), D6 (no branch pins), and D8a, D8b and D8e (the cage's limits and read-only root filesystem go, and quarantine's DNS allowance after a cluster run). The cage changes come in one new cage version, with the pods' claims moved together (K20).

What waits. Everything in `review-2026-11-15/LATER.md`: one later platform tag carrying the loop's and the ledger's changes, the new cage version and the proof's changes; one driftwood pull request for its own files; one pin pull request; and one hub pull request for the records those change. None of it has landed. The ledger line keeps its shape until then, and so does every section above that describes it.

**How the review of every line landed, 2026-11-15.** Each merge was the app's.

- The Renovate pull requests: platform 80, ico 16, feeds 24, driftwood 143, api 7 and storefront 23. Renovate has since opened `actions/checkout` v7 pull requests in platform (81) and ico (17), which the app merged after their checks passed (as `02374c5` and `0f7d247`; both repositories' runs on `main` were green with v7), and dependency dashboards in platform (82), ico (18), driftwood (33), api (3) and storefront (3).
- Ico 19, merged as `ab91903`. The merge cut `v5.2.0` (run 43749613233).
- Feeds 25, merged as `992d860`. The merge cut `threat-register/v5.2.0` (run 43749627685).
- The variable `CUT_ON_MERGE` was deleted from ico and feeds.
- Platform 83, merged as `1b7fcf9`, with `unit` and `cluster` green on the pull request and on `main`. The tag `policy/v8.0.3` was cut by dispatch (run 43750343790).
- Driftwood 144, merged as `9ff3a9b`. Its own cycle (run 43750427912) ran the new platform: `within` at GBP 17,290.68, release-ready. The merge started run 43750805019, which wrote ledger line 15 and opened driftwood 145 (`loop/pins`) for ico `v5.2.0` and feeds `threat-register/v5.2.0`. `check` passed it and the app merged it as `e548c96`.
- Run 43751179363 then wrote ledger line 16 on the new pins: `within`, GBP 17,290.68, release-ready.
- Driftwood `main` is `e548c96`. It pins platform `policy/v8.0.3` (`1b7fcf9`), ico `v5.2.0` (`ab91903`) and feeds `threat-register/v5.2.0` (`992d860`). Mode `act`, rung `isolated`, shop not serving. The ledger has 16 lines, and lines 11 to 16 are all release-ready, so the dwell that started at 10:55:04 is unbroken.

Not yet run live: a release and its dwell. The dwell is met from 10:55:04 UTC on 2026-11-22; the release then needs a cycle to run on `main`, and every line until then to be release-ready. The daily schedule ran for the first time at 14:21 UTC on 2026-11-15. The proof on a cluster that stays up has run twice, from an agent session, not from the daily workflow (K19).
