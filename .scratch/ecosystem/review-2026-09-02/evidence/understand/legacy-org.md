# Legacy org survey — `policy-as-versioned-flux` on GitHub

Read-only survey, 2026-09-02. Evidence is `gh api`/`gh pr|issue|run list` output (commands shown),
fresh clone contents under `scratchpad/legacy/` and `scratchpad/units/`, and files under the hub
checkout at the paths given. Where I could not look, it is said explicitly.

## 1. Per-repo table

15 live repos + `apps` (archived). `pushed_at` and CI/PR/tag facts are `gh api`/`gh pr|run list`
output, 2026-09-02.

| repo | purpose (README, 1 line) | last push | CI (default branch/tags, last runs) | open PRs | tags |
|---|---|---|---|---|---|
| **fleet** | Flux config repo: KiND floor, 3-way policy coexistence (ResourceSet matrix), orphan guard, notifications, C2P/OSCAL CronJob, readiness CronJob, trivy-operator, Crossplane, sunset cron | 2026-08-15T17:21Z | `main` has no build workflow; two cron workflows run on `main`: **sunset escalator** (daily 08:00 UTC) succeeded every run through **2026-09-02T12:34Z (today)**; **weekly governance nag** (Mon 09:00 UTC) succeeded 2026-08-31; **governance checkbox follow-through** (issue-comment triggered) shows `skipped` when no matching checkbox edit fired — not a fault, just no matching event | 4 (all Renovate, opened 2026-07-16, unmerged since) | none (no semver-tagged releases; it's the config repo) |
| **policy** | Versioned Kyverno CEL policy source, semver-tagged, gitsign-signed releases | 2026-07-25T07:56Z | `main`: **weekly governance nag** green weekly through 2026-08-31; **governance checkbox follow-through** `skipped` (no event) | 3 (Renovate, opened 2026-07-17/18) | v1.0.0…v2.2.1 (11 tags) |
| **ledger** | Java/JDK HttpServer app, deliberately old `log4j-core:2.14.1` (Log4Shell CVE-2021-44228), policy 1.0.0 ("the laggard") | 2026-07-25T03:58Z | 2 `release` runs on tag `v1.0.0` (2026-07-16): 1 failure then 1 success | 5 (Renovate) | v1.0.0 |
| **storefront** | Old Angular 9 static build behind nginx, policy 2.2.0 ("tracer bullet" for consumer story) | 2026-08-01T11:46Z | 3 `release` runs on `v1.0.0`, all success | 11 (Renovate — largest backlog of any repo) | v1.0.0 |
| **reports** | Python/Flask, Flask 1.1.4-era deps, policy 2.0.0 ("the middle case") | 2026-08-29T04:46Z | 1 `release` run on `v1.0.0`, success | 10 (Renovate) | v1.0.0 |
| **api** | Go, `go-chi/chi`, current deps, policy 2.2.0 ("the good citizen") | 2026-08-22T12:06Z | 1 `release` run on `v1.0.0`, success | 4 (Renovate) | v1.0.0 |
| **datastore** | Crossplane v2 claims (S3 encryption, RDS Multi-AZ x2), policy 2.2.0, no container image | 2026-07-16T13:32Z | none observed (`gh run list` empty) | 0 | none |
| **cloud** | Harvested NIST 800-53r5 OSCAL catalogue + Crossplane v2 setup (ADR-0004); harvests `controlplaneio/collie`'s IP, not its toolchain | 2026-07-14T18:18Z | none observed | 0 | none |
| **governance-agent** | Agent governance layer spec + thin demonstrator (ADR-0007); hosts `sunset-escalator.sh`, fetched live by fleet's workflow | 2026-07-20T16:09Z | none observed | 0 | none |
| **handbook-generator** | Renders the policy handbook from any policy checkout+tag via git plumbing; `--with-summaries` calls `claude -p` per policy, cached by rationale-hash | 2026-07-18T14:14Z | none observed | 0 | v1.0.0 |
| **pr-gate-action** | Composite Action verifying a policy-version-bump PR (gitsign verify-tag, tag-resolves-to-commit, `kyverno test`, `flux build --dry-run`, label cross-check) | 2026-07-16T12:35Z | none observed | 0 | v1.0.0 |
| **c2p-collector** | Pinned, digest-addressable image baking `c2pcli`+`kyverno-plugin` (compliance-to-policy-go v2.0.0-rc.1) for the OSCAL `result2oscal` collection CronJob | 2026-08-23T00:06Z | `verify` workflow green on every Renovate/feature branch through 2026-08-23; 2 `release` runs (v1.0.0, v1.0.1) both success | 4 (Renovate) | v1.0.0, v1.0.1 |
| **readiness-collector** | Offline `kyverno apply` of a candidate tag's policies against a dump of live workloads → per-team pass/fail + `ready` boolean ConfigMap; never touches admission | 2026-07-25T07:15Z | 3 `release` runs on `v1.0.0`, all success | 3 (Renovate) | v1.0.0 |
| **renovate-config** | Org-level Renovate preset (`config:recommended`, `onboarding:false`, `automerge:false`) every repo extends | 2026-07-16T12:27Z | none observed | 0 | none |
| **apps** (archived) | Superseded consumer-workload monorepo; archived 2026-07-16 ticket 08, replaced by the 5 real team repos; fleet no longer references it | 2026-07-16T13:42Z | n/a (archived) | 0 | none |

All Renovate PRs across all repos are unmerged since their creation date (some since 2026-07-16),
i.e. the reference org's dependency-bump backlog is not being worked — expected, since this org is
explicitly the frozen reference implementation, not a maintained line.

## 2. The two live crons, checked today (2026-09-02)

- `fleet`'s **sunset escalator** ran at 2026-09-02T12:34Z (`gh run view 33630627591 --log`,
  fleet repo). Output: `== signal: sunset: dates in ...clusters/cluster1/policy-versions.yaml
  (today: 2026-09-02) ==` / `2.0.0: no sunset date, skipped` / `2.2.0: no sunset date, skipped`.
  The one version that ever had a `sunset:` date, `1.0.0` (retiring 2026-08-15), was actually
  retired: fleet PR #69 "Sunset: retire policy 1.0.0 (scheduled 2026-08-15)" opened by
  `github-actions[bot]` 2026-08-15T17:16Z, human-merged 2026-08-15T17:20Z. Fleet issue #30
  ("Sunset approaching: policy 1.0.0 retires 2026-08-15 (30 days)") is still open with no
  comments and no checkbox ticked — this is not rot, it's the escalation issue for an
  already-completed retirement, left open as the audit record (the escalator's own dedup logic
  only reopens/re-escalates if the version is still present and still due).
- `policy` and `fleet`'s **weekly governance nag** ran green through 2026-08-31 but currently has
  nothing to nag: no open issue in `fleet`, `policy`, or any other repo currently carries
  `awaiting-defence-pr` or `awaiting-change-pr` (checked via `gh issue list --json labels`
  across all 8 repos with issues). `policy`'s 5 open `agent-governance-review` issues
  (CVE-2026-54523 rationale reviews, opened 2026-07-15) carry no such label and have not been
  commented on since opening — again explicit: the nag only fires on the two specific labels, and
  these issues never reached that state (no defend/change decision was recorded on them).

## 3. Eco-system cross-references (units/*, hub talk/, hub verify/)

`grep -rl "policy-as-versioned-flux/<repo>"` across `scratchpad/units/{driftwood,feeds,ico,
insurer,ludlow,nist,platform,tuppence}`, `hub/talk`, `hub/verify`:

- **fleet, ledger, storefront, reports, api, datastore, cloud, governance-agent,
  handbook-generator, pr-gate-action, c2p-collector, readiness-collector, renovate-config: zero
  hits.** None of the twin/eco-system code references any of these 13 repos by name, path, or
  image. They are not wired into the current build in any way — confirmed by direct grep, not
  inference.
- **policy: 24 hits**, but every one is either (a) `policy-as-versioned-flux/policy-as-versioned-flux`
  — the **hub**, self-referenced in READMEs/workflows/ADR links, not the `policy` repo, or (b) a
  historical citation of the original tagged corpus as fixture provenance (e.g.
  `units/platform/computed-semver/corpus/*.yaml` headers: `# source: policy-as-versioned-flux/policy
  @ v2.0.0`) used as frozen input data for the semver-derivation gate, not a live dependency. No
  eco-system code clones, pulls, or pins the `policy` repo at runtime.
- Conclusion: the legacy org is a dead-end for the current build — cited as history/provenance in
  a handful of fixture-header comments, otherwise completely unreferenced.

## 4. North-star mechanisms — lifted / retired-with-decision / rotting undecided

Source: `.scratch/ecosystem/issues/13-*.md` (resolved, round 1, 2026-08-28), `33-*.md` and
`35-*.md` (both graduated from 13, both still `Status: open` as of the current map — checked
`.scratch/ecosystem/map.md:112-115`, which still lists "Placement of the scanner, notification
spine and OSCAL CronJob after ticket 35 decides lift-or-retire for them" as dim), and
NORTH-STAR.md §6 last bullet (fan-out, notifications, OSCAL CronJob, dashboards, real apps,
sunset cron — the shorter list; ticket 13's own question names 9: those 6 plus handbook,
readiness collector, and Crossplane cloud plane).

| mechanism | disposition | evidence |
|---|---|---|
| **Sunset cron** | **DECIDED** (publisher-side supersede, D5, item 5) — the fleet-side `sunset:`/escalator pattern is *not* carried forward; retirement becomes a publisher-declared EOL read by the adopter's scheduled proposer, which opens the retirement PR itself. ADR-0010's consumer-side placement is superseded by an ADR ticket 10 will write. | ticket 13 Answer item 5, "Decided" (not provisional) |
| **5 real apps (ledger, storefront, reports; api, datastore held back)** | **DECIDED to lift** (item 1, provisional) but **not yet done** — ticket 33 ("Lift ledger, storefront and reports into their adopters") graduated 2026-08-28, `Status: open`, blocked by ticket 09. Checked the 3 target adopter clones directly: no ledger/storefront/reports artefacts, no `log4j`/Angular/Flask fixtures found in `units/{tuppence,driftwood,ludlow}`. | ticket 33 file; `find units/{tuppence,driftwood,ludlow} -iname '*ledger*' -o -iname '*storefront*' -o -iname '*reports*'` → empty |
| **api, datastore** | **Placement decided, not built** — held to a "later round" per ticket 13 Q1/Q3; folded into ticket 35 (open). | ticket 13 item 1 last line; ticket 35 |
| **Crossplane cloud plane** | **DECIDED** (item 3, provisional): lands in tuppence beside ledger, RDS/S3 policies become ADR-0017 published members, graded at admission in KiND, built after the Pod slice runs once. **Not yet built** — sequencing note says "after the Pod slice of §4 runs once," and the Pod slice's own ledger/storefront/reports lift (ticket 33) is still open. | ticket 13 item 3 |
| **Handbook generator** | **DECIDED** (item 4, provisional): lifted as a *compose-time render*, not a scheduled job — a platform-published tool run in each adopter's compose step, output landing under the same signed tag; `verify-fresh.sh` becomes the truth-surface check; `verify.sh` retired; `claude -p` summaries become a Claude Code skill. **Not yet built** — I found no compose-time handbook render script in `units/*`; the only per-adopter render artefacts I located were `driftwood/composed/{evidence.json,composed-set.yaml}` from the *policy-composition* effort, which is a different mechanism (composed-artefact evidence, not a human-readable handbook). Could not confirm absence with full certainty — a targeted grep for "handbook" across `units/*` was not run; flagged as an open question below. | ticket 13 item 4 |
| **Readiness collector** | **DECIDED not to lift as-is** (ticket 13 round-1 preamble, "Already decided, not re-asked"): "the collector's counts are not lifted as counts" — the readiness question is instead answered by the adopter gate's priced-impact grading on a Renovate pin bump (re-grill 14 lineage). This is a retirement-with-reason of the specific mechanism, not an open question. | ticket 13 lines 36 |
| **Grafana/CIO/estate dashboards** | **RETIRED with decision**, and decisively: "the owner rejected them on 2026-07-20 ... and NORTH-STAR §5 makes the truth surface the only citable read; no dashboard of any kind is re-asked." | ticket 13 lines 25, 36 |
| **Vulnerability scanner (trivy-operator)** | **ROTTING UNDECIDED** — explicitly named as a later-round item in ticket 13's own text ("Later rounds, blocked on the above: round 2 ... decides the vulnerability scanner") and re-listed as open work inside ticket 35 (`Status: open`, blocked by 16, 21, 33). No lift-or-retire decision recorded anywhere I found. | ticket 13 "Later rounds" paragraph; ticket 35 |
| **Flux notification spine (Alert/Provider/Receiver)** | **ROTTING UNDECIDED** — same round-2 deferral as the scanner; folded into ticket 35, still open. Ticket 13 itself raises the fallback ("or drop the 'six jobs' claim from spec.md and research/08") as unresolved. | ticket 13 "Later rounds" paragraph; ticket 35 |
| **OSCAL CronJob (on the adopter cluster)** | **ROTTING UNDECIDED for placement/cadence** — the *shape* is decided (item under "Already decided": "collection runs as a CronJob / Flux Kustomization ... each org self-verifies and the hub aggregates"), but "placement and cadence stay open (later)" is explicit in the same paragraph, and ticket 35 (open) is where that lands. Today's OSCAL up-flow in the eco-system is fully offline against hand-written fixtures (`platform/oscal/fixtures/policyreports.yaml`, graded by `verify-upflow.sh`) — no CronJob exists anywhere in `units/*`. | ticket 13 lines 36, "Later rounds" paragraph; ticket 35 |
| **fan-out** (the version-coexistence/ResourceSet mechanism itself) | Not itself one of ticket 13's 9 items (it's fleet's core reconciliation pattern, not an add-on); NORTH-STAR §6's "fan-out" bullet is answered by ticket 16 ("owns the Flux measurement and the fan-out reaching a cluster"), which is a separate, not-yet-read ticket. **Not covered by this survey** — flagged as an open question. | NORTH-STAR §6; ticket 13 line 62 ("ticket 16 owns the Flux measurement and the fan-out reaching a cluster") |

Per-repo archive sequencing (ticket 13 item 2, provisional): each original repo is archived on
GitHub once its lift/retirement is graded green on the truth surface; `fleet` goes last. **None
have been archived yet** except the pre-existing `apps` (archived 2026-07-16, predates ticket 13).
Checked `gh repo list --json isArchived`: only `apps` shows `isArchived: true`.

The currency-controller CronJob (raised as a cross-ticket note, C15) is folded into ticket 13's
answer and retired outright ("it 404s and ticket 07's fx feed replaces it") — decided, not rotting.

## 5. Earlier `.scratch/` efforts — open tickets found

Nine pre-eco-system effort directories exist: `computed-semver`, `demo-feedback` (no issues/
subdir), `drift-review-2026-08-27` (no issues/ subdir, narrative reports only), `faithful-floor`,
`govern-what-you-dont-control` (no issues/ subdir), `multi-org-estate`, `policy-composition`,
`real-estate`, `talk-spec`, `twin` — ten counting `demo-feedback`/`govern-what-you-dont-control`
as effort dirs without a ticket tracker.

Checked every `Status:`/`**Status:**` line in every `issues/*.md` file. `faithful-floor` and
`real-estate` use `**Status:**` inline in the "What to build" section rather than a `Status:`
header line; spot-checked several (09-orphan-guard, 09-sunset-implementation) and both read
"done" / "done, fully" — no open tickets found in either directory by this check, though I did
not open all 16 real-estate and 26 faithful-floor files individually (see open questions).

Genuinely-worded non-terminal statuses found:
- **`policy-composition/issues/09-nist-publishes-named-baselines.md`**: header says `Status:
  blocked (implementation done locally, needs a human with push+signing access to
  policy-as-versioned-nist/nist ...)`. **This is stale** — I checked the actual `nist` repo clone
  and found tag `v1.1.0` already cut (2026-08-25, commit `33a05df`) carrying exactly the baseline
  files the ticket describes (`NIST_SP-800-53_rev5.2.0_{LOW,MODERATE,HIGH}-baseline_profile.json`,
  `BASELINE_VERSIONS.json`). The blocker recorded in the ticket file was cleared after the file was
  last edited; the file itself was never updated to reflect it. I could not verify the tag's
  gitsign signature from this machine (`git tag -v` failed locally with `gpgsm: can't open '-'` —
  a local tooling gap, not evidence the tag is unsigned).
- **`policy-composition/issues/18-wire-composition-into-adopter-ci-and-sign.md`**: header says
  `Status: ready-for-agent`, all 8 acceptance-criteria checkboxes unchecked, no `## Answer`
  section. **Also stale** — matches user memory note `project_policy_composition_ticket18_done.md`
  ("compose-check, evidence backfill, adopter-gate rewire, first tags, all real, all 3 adopters").
  I found the real artefacts directly: `units/driftwood/composed/{evidence.json,composed-set.yaml}`,
  `units/driftwood/scripts/render_composed.py`, and a real `git tag` list on the driftwood clone
  (`v1.0.0`, `v1.1.0`). The ticket file was left unmarked after the work landed under a different
  (ecosystem) tracker; treat the file's own status as unreliable for this ticket, not as an open
  gap.
- **`multi-org-estate`**: 4 tickets marked `partial` (04-istiod-ca-bootstrap, 09-repoint-flux-sources,
  10-per-org-release-and-renovate, 11-prove-28-of-28-live), each with a named specific gap in its
  own status line (e.g. 09: "repointed and proven live, but no signed tag exists yet"). This effort
  predates the eco-system re-baseline (2026-08-27) by about a week; I did not check whether these
  specific partial items were later completed or superseded — **flagged as an open question**,
  since `multi-org-estate` is not named in NORTH-STAR §7's supersession list and its live status is
  unclear from documents alone.
- **`twin`**: several tickets carry "2 ACs partial, carried forward" language (e.g. 06, 08, 13) —
  these are pre-2026-08-27 research/design tickets for the twin, and the twin has since been
  re-scoped per memory (`project_twin_rescope.md`, ".scratch/twin/ supersedes 'estate epic done'
  as north star" — itself now further superseded by the 2026-08-28 eco-system map). Did not
  chase whether each partial AC was later resolved under an ecosystem ticket; **flagged as an open
  question**.

No open ticket in `computed-semver` (all `done`/`resolved`/`split`), `talk-spec` (all
`resolved` except one `claimed` — `12-onboard-renovate.md`, not re-checked in depth here).

## What I did not cover

- Did not open all 16 `real-estate` and 26 `faithful-floor` ticket files individually — spot-checked
  two of each and both were `done`; full sweep not done given scope.
- Did not chase whether `multi-org-estate`'s 4 `partial` items or `twin`'s several
  "carried forward" ACs were later resolved by an eco-system ticket — flagged above.
- Did not confirm/deny a compose-time handbook render exists in `units/*` beyond the
  policy-composition evidence artefacts (which are a different mechanism); a targeted grep for
  "handbook" across all unit repos was not run.
- Did not read ticket 16 (fan-out/Flux measurement) — NORTH-STAR §6's "fan-out" bullet's
  disposition is therefore not independently assessed here beyond the one cross-reference found.
- Did not clone or read the 4 non-"units" cross-org repos in the current eco-system
  (`policy-as-versioned-nist/nist`'s upstream, etc.) beyond the local fresh clones already
  provided under `scratchpad/units/`; treated those as ground truth for "what's built."
- Could not verify gitsign signatures on any legacy-org or nist tag from this machine (`gpgsm`
  invocation fails locally) — tag existence and content were verified; cryptographic signature
  validity was not.
- Did not check `talk-spec/issues/12-onboard-renovate.md` (`Status: claimed`) in depth.
