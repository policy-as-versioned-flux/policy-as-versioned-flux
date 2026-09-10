# Ticket 87 prerequisite: separate source and observation refs

Delegated architecture, 2026-09-10, under ADR-0025. This is a staged migration plan and a first
reader implementation, not a declaration that the clocks or forge protections have migrated.
No remote ref, setting, identity, credential, release, policy acceptance or observation is changed
by this slice. The existing production workflow remains active on its existing path.

## Why this can change, and what must survive

ADR-0023 permits observations on main and rejects a no-main alternative because it would silently
reverse ticket 03's durable citable record. Its banner explicitly records that decision as
**delegated**, not owner-reasoned. Ticket 03 requires a scheduled, recorded TRUTH line; its question
contains no owner-reasoned requirement for a particular Git ref. Ticket 100's default-branch-only
rule was likewise delegated to prevent records stranded on disposable proposal branches. Neither
can simply be ignored: the new permanent ref must preserve the record and replace their
reachability proofs. Principle 5's independent review requirement is owner-reasoned and binds.

Seed each new `refs/heads/observations` at the final main tip containing the complete
pre-cutover record and reviewed source changes. That tip may itself be a clock recording commit. Do not create an orphan containing copied historical files: that would erase
which signed commit actually appended each line and which captures belonged beside it. The
seed creates a ref, not a synthetic observation or a rewritten signature. Keep main's historical
observation files and all old commits reachable. Future observation commits change only their
existing lanes, descend from the selected observation tip, and never merge source into that ref.
The old source files retained in its tree are historical bytes and must never be executed.

Reuse publishers' separation of measurement, temporary result and observation-only commit,
including their existing signing mechanism. Do not copy their orphan-bootstrap mechanism for
already populated hub/adopter histories. No new signing key or broad bypass identity is needed.

## Three distinct commits, never one overloaded SHA

* **Source commit:** the reviewed code and declarations actually executed. `hub=` and each existing
  `units=[unit=sha@ref]` entry keep this meaning. Render manifests, policies, pre-registration,
  ownership attribution and check introductions from source history, never observation HEAD.
* **Input observation tip:** the immutable commit from which this run read prior observations.
  Resolve once before the gate. Proposed additive TRUTH field:
  `observations=[hub=<full-sha>@observations,driftwood=<full-sha>@observations,...]`.
  Its exact parsing and migration boundary still need implementation and tests. It must not be
  silently omitted after cutover or claim the output commit (which does not exist yet).
* **Recording commit:** the commit that actually appends this run's TRUTH line and commits its
  captures together. Resolve it from the selected observation history; do not infer it from
  `hub=`. A deck built through the new explicit reader also names `recording=<full-sha>`.

Historical lines keep their exact bytes and original semantics. A reviewed cutover commit/ref
boundary, not a guessed date, distinguishes legacy records from records requiring the new input
provenance. Missing selected refs, missing source objects and incomplete ancestry are named
could-not-look results, never fallback to stale main files. Structural reachability is not a
cryptographic signature verdict; existing signature and lane checks remain necessary.

## First implemented slice and tests

`talk/build_deck.py --record-ref <local-ref> --run N --out <path>` reads the log and captures
from the explicitly selected ref while keeping the line's measured `hub=`. `--name` and `--check`
accept the same selection. The default remains unchanged until the rest of the estate can read
separate observation histories. An explicit selection is resolved to an immutable commit before
multiple reads. For that path the reader requires a genuine log append with a readable parent,
a capture tree, a reachable measured source commit, and exact agreement between the selected
TRUTH line and the line appended by that recording; an orphan copy or shallow boundary
cannot impersonate a recording. Fetching and signature verification remain callers' duties.

The public recorded-run reader, capture export, deck build and CLI name seams are exercised with
real throwaway Git histories. The fixture retains run 1 on main, advances source independently,
records run 2 on observations, and leaves wrong local rehearsal captures. The reader must select
run 2 and its own captures without changing source HEAD, and still reach run 1's original commit.
Missing refs, missing measured source and shallow history must fail closed. Tests do not create
real observations or claim fixture signatures are production signatures.

This slice alone is NOT enough to switch the writer. No production reader silently opts in.

## Hub dependency inventory

| Surface | Current dependency | Required migration |
| --- | --- | --- |
| `.github/workflows/truth.yml` | Measures source checkout, appends `talk/truth.log` and captures, signs and rebases/pushes main; guard and fall step assume main's log | Keep source checkout immutable; select/fetch observation inputs first; measure there; stage result in a separate observation worktree; sign only after parent and lane checks; push observations without rebase/force; record before preserving failure |
| `talk/verify-all.sh`, `clone-estate.sh` | Unit SHA/tag means checked-out source; writes `talk/captures/*` including `_grades.tsv` | Keep source meaning; resolve explicit per-unit observation tips and report them; pass observations separately, without overlaying tracked files in source trees |
| `talk/build_deck.py`, `talk/verify-demo.sh` | Log on disk and recording lookup from HEAD; captures from recording commit | Explicit record-ref reader is first slice; wire verify-demo and shell callers after provenance adapter is complete |
| `talk/fall_check.py`, `verify/a-fall-blocks/*` | Reads local log; compares declarations/manifest meaning at measured hub commits | Supply selected log; retain source-to-source comparisons; compare the just-recorded line after push using its explicit recording snapshot; retain ticket 108 deferral semantics |
| `verify/can-record/*` | Blame/adding commits, main-only guard, branch-stranding reproducers | Replace with durable-record-ref proof, preserving author/run checks, append history and historical stranded-line detection; cannot grade copied files against source HEAD |
| `verify/schedules/{schedules.py,lost_recordings.py}` | Local hub log reconciles scheduled runs and lost recordings | Read the selected observation snapshot; source workflow SHA stays source; no stale-main success if fetch fails |
| `verify/schedules/{lane.py,verify-lane.sh}` | Already fetches/scans main and observations; decides whether missing observation ref is expected from workflow | Preserve historical main scans; grade new ref ancestry and current source workflow identities; reject source merges/declarations in post-cutover observation commits |
| `verify/derived-status/*` | Local log and `_grades.tsv` must agree; check ownership reads source Git history | Load both from the same recording snapshot; keep ownership from reviewed source history, never the historical source tree inside observations |
| `verify/{cited-truth,map-surface,truth-line}/*` | Local log plus cited hub tree/check ownership and current declarations | Selected immutable log; cited source resolution unchanged; tests must cross divergent source/observation histories |
| `verify/local-clock/local_clock.py` | Rejects new local TRUTH lines by reading local hub log | Inspect selected permanent observation history; local model clock remains proposal-only and writes no citable TRUTH line |
| `verify/e2e/verify-e2e-step4-flux-reconciles-cage.sh` | Calls adopter sample/reconcile evidence readers | Consume adopters' explicit observation tips without changing their source/pin provenance |
| `verify/e2e/verify-e2e-step5-twin-forecasts.sh`, `verify/twin-evals/*` | Read adopter swept-at/moved evidence and declared forecast/scoring files | Separate clock-ledger evidence from source declarations and signed feed tags; absence remains non-green |
| `twin/drift.py`, its CLI/invariants, adopter organic/forced probes | Filesystem sample logs include distinct organic, five-fact and forced-campaign instruments | Migrate only scheduled committed lane reads; preserve row-type separation and forced-campaign exclusion; local scratch is not promoted to scheduled evidence |

`talk/local-clock.sh` and its run directory are an additional local observation writer, but not
a direct-main clock: it keeps local execution records and opens proposals. Its existing no-citable-
write rule stays. Publisher fetch clocks already use observations refs; no publisher migration
or new publishing contract is necessary for this prerequisite.

## Exact adopter migration dependencies

Inspected fresh main snapshots in isolated audit repositories:

* Driftwood `c6d3bb0612b9e511c083ee41da2e6106bf74e1fc`.
* Tuppence `7a8c4cf5ec50697e7a6e1a41e4f40444f3a6339d`.
* Ludlow `6fdff4ac1d1d8df613f276fcb60e907d98cfce4e`.

All three: `.github/workflows/drift-sample.yml` executes `drift/five-facts.py sample`, appends
`drift/samples.jsonl`, then signs/pushes main. `drift/five-facts.py grade` and `sample_provenance`
read the working file and Git attribution at source HEAD; `verify-reconcile.sh` invokes that
reader. Their prerequisite is an explicit sample-record ref/path adapter that reads bytes and
attribution from the SAME observation commit while reading `drift/window.yaml`, manifests and
registration history from the measured source commit. Merely copying the log into the checkout
fails the dirty-file provenance check; merely checking out observations runs old code.

All three: `.github/workflows/propose-tier.yml` and `renovate-run.yml` are scheduled writers of
proposal branches. Their generic lane declarations do not make them observation-log writers.
Keep their reviewed proposal route and existing compiler-tools pins; do not reroute proposals
to observations or grant bypass. Confirm no main push remains in either effective workflow.

Driftwood: `.github/workflows/twin-sweep.yml` measures with the hub twin, may create a reviewed
feed proposal, appends `observations/twin-sweep.jsonl`, and separately commits its observation.
Move only the latter write. `twin/verify-twin-sweep-moved.sh` reads that ledger and must receive
its selected observation ref. The declaration/feed proposal, emitter, pricing and signed release
contract remain unchanged. Its current loose `twin_ref` prose must be replaced for NEW rows by
the actual source SHA used; old rows remain unaltered and retain their disclosed limits.

Tuppence and Ludlow: `.github/workflows/twin-sweep.yml` invokes
`.github/scripts/twin-sweep.py record`, which uses the existing emitter and already records full
`hub_ref` and `adopter_ref`. The helper currently reads/writes/gates the ledger below
`--adopter-dir`, conflating input source and output record location. Add an explicit ledger output
location, preserving source arguments; append exactly the emitted row to the observation worktree.
Gate the same run's row there, after recording/signing, retaining emitter exits 0/1/3. Missing
signed valuations and unsupported causal edges remain owned by ticket 30; no feed, forecast,
monetary value, causal admission or pricing acceptance is created by the migration.

Cross-repository order: adopter reader adapters and tests → hub collector/provenance readers →
adopter clock writers → hub truth writer → real scheduled evidence and negative push tests →
reviewed-source branch rulesets. Moving a writer ahead of its readers strands evidence again.

## Cutover gates, owned by the root integrator

1. Finish and review all reader/provenance adapters and gate integration. Test source A / input
   observation B / new recording C, wrong-local-file rejection, missing history, and old records.
2. Prepare writer patches and execute their real shell/helper paths in disposable repositories.
   Pre-staged declarations, merges, wrong parent, missing ref, broken append prefix, failed
   signatures and denied pushes must record no false success. Preserve signature identity and
   contents/id-token permission boundaries; no new key or GitHub App.
3. Establish a short explicit writer cutover barrier across each repository's clocks. Wait for
   in-flight old writers before choosing the final main tip and seeding observations. Otherwise
   a last old main recording after the seed is lost. Do not fabricate a sample for this interval.
   No barrier, ref creation or workflow dispatch is executed by this slice.
4. Seed the permanent ref at that final tip, merge reviewed writer configuration, then resume
   clocks. Serialize all writers to the same observation ref using a shared non-cancelling group.
   No force push, no source merge, no silent reset; contention must fail or retry the append
   against a newly verified parent, preserving already signed history.
5. Fetch both source and observation refs, prove every old recording SHA is still reachable and
   its bytes unchanged, and observe actual scheduled writes/failures at the new target. Test
   lost-record detection, citable deck, fall comparison, derived statuses, signatures and lanes.
6. Only then enable review-required main/release protection. Confirm source direct pushes fail
   while clocks continue on observations. Restrict observation ref deletion/force updates as
   separately reviewed rules, without pretending those rules provide a path-scoped bypass.

No completion claim is supported until those integration gates pass. A local reader test is not
proof of a live clock, push-time enforcement, signature validity or resolved pricing.
