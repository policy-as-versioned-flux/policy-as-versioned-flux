# CONTRACT: the simplified estate

Written 2026-11-14 by the architect stage, revised the same day after three reviews, and amended by the orchestrator after the owner's reply "I'm afk. Jfdi" (`DECISIONS.md`, "Later the same day"): leave to cut tags is given, and the red exit moves to a job of its own (5.3). The builders share this file and nothing else. `DECISIONS.md` and `FORGE.md` outrank it. It outranks `TARGET.md`.

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
| K5 | The cluster is built by `kubectl apply -k` from pinned checkouts. Flux is not installed. | On a cluster made after the merge, Flux proves nothing a checkout does not. It returns with the cluster that stays up, which waits for the owner (decision 9, section 8). | delegated |
| K6 | Pins are followed by `loop.py bump-pins` with plain git. Renovate is not run. | Following a branch by commit could not be checked offline in Renovate. One function handles branch pins now and tag pins later. | delegated |
| K7 | No reusable workflow. Driftwood's workflow checks platform out at the commit in `party.json` and runs its scripts. | Every pin then lives in one file, on one line each. | delegated |
| K8 | No exploited-flaw list, image inventory, scanner or fetch. They are parked, not dropped. `LOOP.md` says where each is kept and what brings it back. | The first loop runs end to end without them. They need about 500 lines and a scanner in CI. | delegated |
| K9 | Ico and feeds have no scheduled job and no landing job. Their one unattended act is to cut a tag when a merge changes the feed's version. A repository variable switches it on (5.2). | With K8 there is nothing to fetch. A tag needs no key: the default token can create one, and driftwood finds it with `git ls-remote`. | delegated, applying decision 2 |
| K10 | Network tests run from the probe pod, not inside every workload container. | Whether the workload images carry a shell is not known. The settle check proves every pod carries the stamp the network rule selects on. | delegated |
| K11 | A loss the cage cannot touch is a priced row with no `needs`, on the publisher's editorial band. | The exposure compared is the whole organisation's. A register without the row could read `within` by leaving the loss out. An unsourced number can only raise the figure. | delegated, applying decision 5 |
| K12 | No veto on a refused release. | No person is on the merge path (decision 2), so nobody refuses. | owner-instructed |
| K13 | `pins.sh` verifies a tag's signature when a pin names a tag. | So that moving to tags is a change to pin lines only. It cannot be proven until a tag exists. | delegated |
| K14 | Driftwood's workloads stay bare Pods, with no rollout stamp. | Every cycle builds a new cluster, so every pod is admitted at the current rung. | delegated |
| K15 | The party file and the ladder file are JSON, not YAML. | The standard library reads JSON and refuses a duplicate key in three lines. YAML needed a dependency, a second action and a hash pin in five jobs. | delegated |
| K16 | A notch is judged by the goal it leads to, not by its own gain. | Decision 6 says cost always counts. Judged alone, the first notch would never be taken, and the loop would sit at `baseline`, against decision 5. | delegated reading of decision 6 |

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
| `twin/` (3 files) | keep | 0 | The guard on agent writes and its mode file. They leave only with the hook, in the owner's own commit (section 8) |
| `docs/adr/` (37 files), `docs/agents/` (2 files) | keep | 0 | The decision records, with no banner edits. ADR-0039 names what it supersedes |
| `.scratch/distil/` (73 files), `.scratch/drift-review-2026-08-27/` (5 files), `.scratch/ecosystem/` (12 files) | keep | 0 | The review and the owner's dated words, byte for byte, but for the two files in the next row |
| `.scratch/distil/ARCHIVE.md`, `.scratch/distil/evidence/archive-refs.tsv` | rewrite | 0 | Appended to by the orchestrator, not by the builder: the branches archived at step 0 of section 8 |
| `.scratch/distil/CONTRACT.md` | new | 0 | This file, copied byte for byte, as a record |
| `LOOP.md` | new | 120 | The owner's sentence. Section 1 of this contract. Where each number comes from and its state today. The worked figures of 6.1, dated "on the inputs of 2026-11-14", with a pointer to the ledger for today's. **What is parked**, where it is kept and what brings it back: the exploited-flaw list (feeds tag `cve/v3.0.0`), the image inventory and scanner (platform tag `v6.3.0`), the fetch clocks and all else (`refs/archive/main/2026-11-14-before-simplify`); a returning fetch adds rows and would need the key in that publisher. Nothing is called a by-product. **What waits for the owner** (section 8). **Four notes.** The loop's machine merges rest on decision 2 ("All AI machine driven"), not on `twin/ENACT_MODE`, which still governs agent sessions in the hub until the owner removes the hook. The CI proof is not yet decision 9's proof. While a release waits for its dwell the lines can read `saturated` and red, and with one cycle a day a dwell is usually met a day late. GitHub disables `loop.yml`'s schedule after 60 days without repository activity; it is switched back on from the Actions tab |
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

### 3.3 `ico/penalty-schema/feed.json`

```json
{"feed": "penalty-schema", "version": "5.0.0", "published_by": "ico", "published_at": "2026-11-14",
 "note": "A demonstration party, not affiliated with, endorsed by or speaking for any real authority it names.",
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
    {"org": "Doorstep Dispensaree Ltd", "year": 2019, "amount": 92000, "status": "final", "source": "ICO monetary penalty notice, 12 Dec 2019; reduced by the First-tier Tribunal in 2021; upheld by the Court of Appeal in 2024"}]}}}}}
```

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
- The cage acts on a pod that carries `policy-as-versioned.dev/policy-version: "8.0.0"`. It reads the rung from the Namespace's label only, and only when that Namespace carries `policy-as-versioned.dev/governed: "true"`. Its stamp is `posture.acme.io/caged: "true"` and `posture.acme.io/tier: <rung>` on the pod. Neither file holds a deny action.

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

**How a rung change reaches `main` unattended.** `cycle` decides and makes the patch with a read-only token. `write` opens the pull request as `github-actions[bot]`. `check` refuses anything but one rung line, one notch, in the direction of this run's verdict. `land` approves and merges as the app. The app did not open the pull request, so its approval satisfies the one-review rule. A pull request opened with the default token starts no workflow, which is why the check is a job of the same run. The merge is the app's, so it does start a run: the `push` trigger fires and the next cycle begins.

**A release** takes the same path with no special case. The verdict is `release`, the patch moves the line one rung looser, and `check` is given that direction. The margin and the dwell are values in `party.json`. The rule that uses them is in `loop.py` only.

**A pin change** takes the same path with `--kind pins`. The diff must touch pin lines only. So the tolerance, margin, dwell and mode, which share the file, cannot ride along.

**In `measure` mode** `cycle`, `verdict` and `write` run, `write` only appends the ledger line, pins do not move, and `check` and `land` are skipped.

**A red verdict does not stop the landing path.** `cycle` ends green whenever it wrote a line, and only `verdict` carries the red. So a pin change, which is how a publisher's correction or a platform fix arrives, still lands while the verdict is `saturated`, `cage-ineffective` or `could-not-look`. On today's inputs every run at `isolated` is red at `verdict`, and its line is still written.

**How the ledger is stored.** One file, `loop.jsonl`, on the orphan branch `ledger` of driftwood. The orchestrator creates the branch once (section 8). After that only `write` pushes it, only from runs on `main`, with the default token. No ruleset covers that branch (FORGE). A push with the default token starts no workflow.

## 6. The proof

### 6.1 Unit tests that must exist, in `platform/loop/test_loop.py`

R1, R2 and R3 are the three rows of 3.2, in order. The test builds 3.1 and 3.2 by hand and reads `harness/fixture/penalties.json` for 3.3. The rungs are `cage/rungs.json`. Money is compared to the penny.

| Test | Expected |
|---|---|
| `test_mean` | `mean(2, 4, 9) = 4.5`. `mean(1000, 4000, 9000) = 4333.33` |
| `test_mean_penalty` | At 86,000,000: higher 3,613,638.10, lower 301,823.75. At 861,741,000: higher 32,893,885.03, where the cap rule bites |
| `test_amounts` | R1 16,280,871.43. R2 431.49. R3 1,628,087.14. All `upper`. R1 with `tier: "lower"` cited: 1,377,706.90. A row of another party is ignored |
| `test_figure_at_baseline` | Exposure 17,909,390.06. Cost 500. Figure 17,909,890.06 |
| `test_predicted_and_goal` | `predicted(quarantine)` 17,915,390.06. `predicted(isolated)` 1,643,518.63. No rung is within 40,000, so `goal(40000)` is the lowest, `isolated`. With R1 and R2 only, `predicted(isolated)` is 15,431.49 |
| `test_walk_on_todays_inputs` | At `baseline`, all open: `tighten` to `quarantine`. At `quarantine`, `egress` closed and `inbound` open: figure 17,915,390.06, `tighten` to `isolated`. At `isolated`, both closed, serving 0 of 3: figure 1,643,518.63, `saturated`, exit 2, `unreachable` 1,603,518.63, `release_ready` false |
| `test_within` | R1 and R2 only, at `isolated`, both closed: figure 15,431.49, `within`, `unreachable` 0 |
| `test_release_after_dwell` | Penalty rate 0.0005, counted, at `isolated`: figure 17,763.80, and `predicted(baseline)` is 30,894.49, which is at or below 32,000. Ledger release-ready for 7 days: `release` to `quarantine`. For 6 days: `within`. The next cycle, at `quarantine` with that release line added: `release` to `baseline`, with no second dwell |
| `test_unreachable_counts_cost` | R1 and R2 only, tolerance 10,000, at `isolated`: `saturated`, `unreachable` 5,431.49 |
| `test_cost_stops_a_notch` | One row needing `egress`, 1 event a year at 3,000; tolerance 1,000; at `baseline`: figure 3,500, `predicted(quarantine)` 6,000, `saturated`, no move, `unreachable` 2,500 |
| `test_cost_gives_a_notch_back` | No rows, at `quarantine`, tolerance 1,000: figure 6,000. Dwell met: `release`. Not met: `saturated` |
| `test_exactly_at_tolerance_is_within` | A figure equal to the tolerance is `within` |
| `test_cage_ineffective` | At `quarantine` with `egress` open: `cage-ineffective`, no move, exit 2, every row priced as open. The same with `inbound` also closed: still `cage-ineffective` |
| `test_closed_but_undeclared_is_could_not_look` | At `baseline` with `inbound` closed: `could-not-look`. R1 is not credited |
| `test_could_not_look` | No probe file; `looked` false; probe rung not the git rung: each gives `could-not-look`, no move, exit 3. At `baseline` the line carries the uncaged figure 17,909,890.06. With no probe file `pods` is `[]` and `reference` is `null` |
| `test_within_partial_never_releases` | A row with `events_a_year: null` is named in `unpriced`. The verdict is `within-partial`. No release, even when release-ready with the dwell met. Above tolerance it still tightens |
| `test_need_without_source_is_ignored` | A need with an empty `source` never closes its row |
| `test_weakest_basis` | On 3.1 to 3.3 at `baseline`: `not-counted`, of `uk-gdpr penalty_rate`. With the rate counted: `unsourced`, of `cost of baseline` |
| `test_tolerance` | `share_of_turnover: 0.005` gives 430,000. A missing tolerance is refused. Both forms together are refused |
| `test_party_is_read_strictly` | A duplicate key, an unknown key, a boolean turnover, a bad `mode`, a pin split over two lines: each is refused |
| `test_currency_is_never_mixed` | A regime in USD with a party in GBP is refused |
| `test_fine_rules` | A `not-collected` fine does not price. A pricing fine with no source is refused. A row basis with no `as_of` is refused |
| `test_set_rung_changes_one_line` | The diff is one line. Comments survive. `--- # comment` separates documents. Two governed Namespaces raise. A rung not on the ladder raises |
| `test_check_diff_rung` | Accepts one notch in the verdict's direction, tighter and looser. Refuses a two-line diff, a two-notch move, the wrong direction, and another file |
| `test_check_diff_pins` | Accepts a changed `commit` and a changed `ref`. Refuses a changed tolerance line, a changed `mode` line and a changed `repo` |
| `test_next_pin` | `main` follows the branch head. `policy/v7.0.0` moves to the highest `policy/v*` and ignores `v6.3.0` and `cloud/v1.0.1` |
| `test_dwell` | Met after an unbroken run. Broken by one false line. Not broken by a change of rung. `could-not-look` lines are skipped. An empty ledger is not met. A dwell of 0 is met |
| `test_monte_carlo_agrees` | 20,000 simulated years of R1 with Poisson counts, seed 20261114: the mean is within 2% of 16,280,871.43 |
| `test_no_deny_and_no_reduction` | No file under `cage/` holds `Deny` or `validationActions`. `rungs.json` holds no `reduce` |
| `test_loop_runs_no_forge_command` | Neither `loop.py` nor `probe.py` runs `gh` as a command word, or holds `api.github.com` or `approve` |
| `test_probe_reads_the_marker` | Exit 1 from `kubectl` with marker 0 is open. No marker gives `looked` false |
| `test_probe_closed_must_hold` | Not open once, then open: `open`. Not open on four reads: `closed`. Open with a NetworkPolicy present, then not open on four reads: `closed` |
| `test_probe_reference_brackets` | The reference fails before, or after: `looked` false |
| `test_probe_settle` | An unstamped pod, a pod at another rung, a pod not Ready at the limit, or no pods: `looked` false |
| `test_probe_policy_not_ready` | `status.conditionStatus.ready` false: `looked` false |
| `test_probe_reference_must_be_uncaged` | A stamp on `client`, or a NetworkPolicy in `loop-reference`: `looked` false |

`test_feed.py` in ico and in feeds asserts the shape rules of 3.3 and 3.2 on the published file. It does not compare the file with a copy of itself.

### 6.2 The cluster proof: `harness/proof.sh`

**The fixture.** Party: `fixture`; turnover 1,000,000; tolerance `amount: 10000` with basis "test fixture"; margin 0.2; `dwell_days: 0`; mode `measure`; three pin lines of forty zeros, never checked out. Rows, both of party `fixture`, with `penalty: null` and every basis `{"kind": "editorial", "as_of": "2026-11-14", "text": "test fixture"}`: `fixture-exfiltration`, events `[1, 1, 1]`, loss `[50000, 50000, 50000]`, needing `egress` with the source "MITRE ATT&CK T1041, Exfiltration Over C2 Channel (Exfiltration), version 2.4, read 2026-11-14 at attack.mitre.org/techniques/T1041."; and `fixture-outside`, events `[1, 1, 1]`, loss `[1000, 1000, 1000]`, no needs. Namespace `fixture` is at `quarantine`. Its one nginx pod, `shop`, claims 8.0.0, declares port 80 and is the probe pod.

Each run is `probe.py`, then `loop.py cycle --cluster harness`. Nothing is written to any ledger.

| Run | What is done first | Green means |
|---|---|---|
| 1. The label-only control | `up.sh --no-netpol`: the cage stamps pods and writes no network rule | Pods stamped `quarantine`. `egress` open. Exposure 51,000.00. Verdict `cage-ineffective`. If the exposure is below 51,000.00 the money is following the label, and the job fails |
| 2. The positive run | Apply `cage-netpol.yaml`, wait until it is ready, delete the pod and apply it again, then wait up to 120 seconds for NetworkPolicy `cage-reach-quarantine` to exist | `egress` closed. `inbound` open. Serving 1 of 1. Exposure 1,000.00. Figure 7,000.00. Verdict `within` |
| 3. The break test | `kubectl -n fixture delete networkpolicy cage-reach-quarantine`, then sleep 15 seconds so the node opens the path. Git and the labels still say `quarantine` | `egress` open. Exposure back to 51,000.00. Verdict `cage-ineffective` |

The job is green only if all three hold. Any `could-not-look` is red. Run 2 shows a figure that falls while the workload still serves. Run 3 is the one observation that tells feedback from a lookup.

**This is not yet decision 9's proof.** The owner accepted a cluster that stays up for the proof and the break test. This proof runs on a throwaway kind cluster and says so: `cluster: harness`. The other cluster waits for the owner (section 8).

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
- Once driftwood is in `act` mode it follows platform's `main` by itself. From then on a platform pull request merges only with `unit` and `cluster` both green.
- If the proof stays red, platform is fixed by further pull requests under the gate of step 4, no platform tag is cut, and driftwood stays in `measure` mode on a commit pin for platform.

**What waits for the owner.**

| What | Until then | When it comes |
|---|---|---|
| The tolerance figure | GBP 40,000, labelled a fixture on every line | Change the `tolerance` line of `party.json`: `amount` or `share_of_turnover`, and `basis` |
| A cluster that stays up, for decision 9's proof and break test | The proof runs on a throwaway kind cluster, labelled `harness` | The owner names the machine or the spend |
| The secrets hook and the signing permission | The three `cut-release.yml` files quote the `id-token` key so that the hook passes them. The old files wrote it unquoted | The owner confirms the spelling, or adjusts the hook |
| Removing the guard's hook from the hub | `twin/` and `.claude/settings.json` stay | One commit of the owner's removes the hook and the three `twin/` files together |
| The hosted Renovate app on driftwood | `renovate.json` keeps it silent | Uninstall it, then delete the file |

**Settled on 2026-11-14 by the owner's reply "I'm afk. Jfdi".** Leave to cut tags: given, and used at steps 6 to 8. The key in feeds and ico: granted and not used. Nothing built here would read it, and a secret with no reader is redundant. Only a returning fetch would need it (`LOOP.md`, what is parked).

The numbers nobody has counted are not the owner's to supply: the penalty rate is ico's work, and the third row's band is feeds' work. `LOOP.md` names both.

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
- A landing job, an environment or a key in ico, feeds or platform (the key was granted on 2026-11-14 and is not used). A separate CI workflow in ico or feeds.
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
