# 147 — The adopter declares its engine where it installs it

Type: task
Status: claimed
Blocked by: 146 (the engine table)

## Question

Graduated 2026-09-25 from grilling ticket 71, decisions 2, 5 and 17 (delegated), and ADR-0033
point 2. Decision 17 replaced decision 11 on 2026-09-26.

The adopter owns its engine version, and its engine install file is its declaration. Today:

- No adopter's Flux reconciles a platform path. On the named clusters Flux reconciles
  `./gitops/apps` only. `gitops/composed/` reaches only the drift lane, and
  `gitops/platform/platform-distribution.yaml` is opt-in and not applied there.
- The named demo cluster `kind-driftwood` gets the platform's Kyverno from hub `talk/up.sh`, which
  runs platform `engine/up.sh`. tuppence's workload flagship also runs on that cluster, and
  tuppence's `reset/README.md` names platform `engine/up.sh` as its prerequisite.
- `kind-tuppence` and `kind-ludlow` run no Kyverno. Their `scripts/up.sh` install Flux only, and
  their `drift-sample.yml` says that the engine exists only on the lane.
- Each adopter's `drift-sample.yml` installs the raw `install.yaml` from its own `KYVERNO_VERSION`
  env, and each `shift-left.yml` pins its own CLI.
- No adopter declares its engine anywhere, and `party/schema.json` does not allow a field for it.

Build the following in driftwood, tuppence and ludlow, and in the hub:

1. **The declaration is one file: `gitops/engine/kyverno.yaml`.** The path is decided here
   (delegated), because ticket 161 reads it. The file:
   - states the Kyverno version, for example `1.18.2`;
   - names the raw `install.yaml` URL for that version and its sha256, in a form the lane can apply
     server-side (two Kyverno CRDs are larger than 256KB, so the lane applies them server-side);
   - puts every namespaced object it installs in the `kyverno` namespace, which the platform
     declares as substrate (`engine/namespaces.yaml`), so composition prices none of them.
2. **A recompose in the same adopter PR.** The comparison identity hashes every non-hidden source
   file outside `composed/` and the observation lanes (ticket 134). A new file makes
   `composed/HEADER.yaml` stale, so `compose-check` and the pre-tag check refuse until the adopter
   recomposes.
3. **Every cluster of the adopter that runs an engine installs from that file.** This adds no
   engine to a cluster that has none (decision 17, clarified 2026-09-26, delegated).
   - The drift lane: `drift-sample.yml` stops using its own `KYVERNO_VERSION` and checksum, and
     reads both from the file.
   - The named demo clusters: hub `talk/up.sh` installs each named cluster's Kyverno from the file
     of the adopter that owns the cluster, not from platform `engine/up.sh`. The platform's
     `engine/kyverno` stays as the platform's reference install only.
4. **One engine per shared cluster.** A hub check asserts that the adopters who use one cluster
   declare the same engine. Today that is driftwood and tuppence on `kind-driftwood`.
5. **A static check on the file.** A hub check asserts that each adopter's stated version, install
   URL and checksum agree with the platform engine table's row for that version (ticket 146). This
   replaces the drift fact of decision 11. That fact could only read true, because the lane
   installs from the same file that it would compare against.
6. **`shift-left.yml` uses the declared engine.** The adopter's offline CLI version equals its
   declared engine, read from the same file, with the CLI checksum from the engine table.
7. **Tell the session that owns ticket 161.** Its `verify-cage-probe.sh` compares the CLI version
   with the adopter's engine, and must read that version from `gitops/engine/kyverno.yaml`. This
   ticket does not edit `drift/five-facts.py` or `drift/window.yaml`.

Every adopter declares 1.18.2 here. Ticket 150 is the only ticket that moves an adopter to
another engine.

## Done

On each adopter's `origin/main`, `gitops/engine/kyverno.yaml` exists, the composed header is
current, and a scheduled drift sample installed Kyverno from that file. A dispatched run does not
count. `talk/up.sh` installs `kind-driftwood`'s engine from driftwood's file, and it installs no
engine on `kind-tuppence` or `kind-ludlow`. The shared-cluster check and the static check pass on
the hub, and each fails on a planted disagreement.

## Notes

- Ticket 148 must not land before this ticket lands on all three adopters. If composition prices
  before an adopter declares its engine, that adopter gets the `undeclared-engine` price.
- The engine versions as read on 2026-09-25: `drift-sample.yml` driftwood `:56-57`, ludlow and
  tuppence `:59-60`; `shift-left.yml` driftwood `:117-118`, ludlow `:140-141`, tuppence
  `:138-139`. The lane applies Kyverno server-side at `drift-sample.yml` driftwood `:162-167`,
  ludlow and tuppence `:165-170`.

## Comments

**2026-09-26, owner-instructed: built as four pull requests.** On 2026-09-26 the owner answered
"Authorised" to this list: "build eco-system tickets 146 to 150; the signed policy tag for ticket
149; the tools and adopter tags for ticket 148; the adopter-gate retirement and adopter tag for
ticket 150; an upstream Kyverno report." This ticket is built as three adopter pull requests
(policy-as-versioned-driftwood/driftwood#51, policy-as-versioned-tuppence/tuppence#49 and
policy-as-versioned-ludlow/ludlow#46, each on branch `ticket-147-declared-engine`) and this hub
pull request. No adopter moves engine: each declares 1.18.2. No tag is cut. The adopter pull
requests merge first, because the hub check reads each adopter's `origin/main`.

What the four pull requests build, item by item:

1. **The declaration** is `gitops/engine/kyverno.yaml` in each adopter. It states the version, the
   `install.yaml` URL and sha256, and the linux_x86_64 CLI archive and sha256. Each figure was
   written from the 1.18.2 row of platform `engine/kyverno/engine-table.yaml` on platform
   `origin/main` (`cb680f2`), not typed. On 2026-09-26 the figures were checked again: the
   `install.yaml` sha256 `3dcd43ea...` is the GitHub release API's asset digest and the sha256 of
   the downloaded file, and the CLI sha256 `cb2feb83...` is the line in
   `https://github.com/kyverno/kyverno/releases/download/v1.18.2/checksums.txt`. The downloaded
   `install.yaml` holds 70 objects. All 24 namespaced ones (4 Deployments, 6 Services, 4
   ServiceAccounts, 4 Roles, 4 RoleBindings and 2 ConfigMaps) sit in `kyverno`, which the platform
   declares `infra` in `engine/namespaces.yaml`. The other 46 are cluster-scoped. The file header
   records this measurement, which holds for as long as the sha256 does. Each adopter's
   `.github/scripts/engine_declaration.py` is the one reader there, and it refuses a file that is
   not an exact version with that release's URL and a sha256 for each artefact.
2. **The recompose** is in each adopter pull request, made with the tools each adopter pins,
   platform `v4.0.0`, and parents at their pinned tags. In each adopter it changes one line,
   `comparison-inputs.after` in `composed/HEADER.yaml`. `composed/evidence.json` is byte-identical,
   and the document the composition prints is byte-identical to the one it prints on
   `origin/main`. No price moves. The composition walk skips the file, because it declares no
   object. `platform-tools.py verify` passes on each head. On a throwaway driftwood commit that
   carries the new file and `origin/main`'s header, it refuses with "comparison history does not
   match current source inputs", which is the refusal the recompose removes.
3. **Every cluster that runs an engine installs from the file.**
   - The drift lane: each `drift-sample.yml` no longer carries `KYVERNO_VERSION` or
     `KYVERNO_SHA256`. A new step, `read the engine this repository declares`, reads the file
     through the reader, and the install step downloads the declared URL and checks the declared
     sha256. The engine is still applied once, server-side.
   - The named demo cluster: hub `talk/up.sh` no longer runs platform `engine/up.sh`. It runs a
     new hub script, `talk/engine-up.sh driftwood`. That script applies platform
     `engine/namespaces.yaml`, installs Kyverno from driftwood's own file (refused unless the
     download hashes to the declared sha256, applied server-side, and refused unless the admission
     controller then runs the declared version), and applies platform
     `engine/flux-operator/helmrelease.yaml`, as `engine/up.sh` did. `kind-tuppence` and
     `kind-ludlow` get no engine. The platform's `engine/kyverno/helmrelease.yaml` stays its
     reference install only.
4. **One engine per shared cluster** and 5. **the static check** are one new hub check,
   `verify/adopter-engines/verify-adopter-engines.sh`, with its manifest row
   (`estate-observation`, no could-not-look declared). It asserts (a) each adopter's figures equal
   the table's row for its version, (b) adopters that share a named cluster declare the same
   engine, and (c) `talk/up.sh` installs an engine from the owner's file on each cluster a platform
   layer targets, on no other cluster, and never through platform `engine/up.sh`. The adopters are
   the units whose `party.yaml` claims the adopter role. The sharing is derived from the scripts
   `talk/up.sh` runs: a `CTX="${CTX:-kind-...}"` default, or the `CLUSTER=` of the `lib.sh` a
   script sources. Today that puts driftwood (`scripts/up.sh`) and tuppence (`reset/up.sh`) on
   `kind-driftwood`. No list of adopters or clusters is written in the check.
6. **`shift-left.yml`** in each adopter reads the file through the same reader, installs the
   declared CLI by its sha256, and fails when `kyverno version` reports another version.
7. **Ticket 161** is told by the integrator, not by this builder. The file's form: top-level
   `schema: 1`, `engine: kyverno`, `version: "1.18.2"`, `install.url`, `install.sha256`,
   `cli.linux_x86_64.file` and `cli.linux_x86_64.sha256`. No key other than these five top-level
   ones is accepted. This ticket does not edit `drift/five-facts.py` or `drift/window.yaml`.

**The decisions made during the build, each delegated under ADR-0025.**

- *The file is a plain declaration, not a Kubernetes manifest.* No Flux Kustomization reconciles
  `gitops/engine/`, so a manifest would be applied by nothing. The `install.yaml` is 5.7 MB, and
  vendoring it would put its 70 objects, four of them Deployments, into the tree that composition
  walks. A manifest cannot carry a checksum of a remote file that `kubectl` checks. Every reader
  (the lane, shift-left, `talk/engine-up.sh`, ticket 161 and, later, ticket 148's composition)
  reads a few named fields.
- *The CLI checksum is carried in the adopter's own file.* Item 6 asks for "the CLI checksum from
  the engine table". The adopters pin platform tools `v4.0.0`, which has no engine table, so no
  adopter workflow reads the table. The file carries the table's figure, and the hub check holds
  it to the table on platform `origin/main`. Only the linux_x86_64 CLI is declared, because both
  adopter workflows run on `ubuntu-latest`.
- *The file carries no `namespace` or `apply` field.* Nothing would read either. The lane and
  `talk/engine-up.sh` apply server-side in code, and the namespace measurement is bound to the
  sha256 and recorded in the file's header.
- *A new check, not an extension of `verify/estate-engines/`.* That check requires each estate
  pin to be a supported engine of every served line. An adopter's declared engine may be any
  version, because ticket 148 prices an unsupported pairing (ADR-0033 point 3). One PASS line
  cannot carry both rules.
- *A missing or malformed declaration is a FAIL, not a could-not-look.* After this ticket, a
  missing file is the regression this check exists to catch. So until the adopter pull requests
  merge, the check fails by name on the hub.
- *An engine goes where the platform's layers run, and nowhere else.* Assertion (c) derives the
  clusters that need an engine from the platform steps in `talk/up.sh`. Today that is
  `kind-driftwood` only, which is decision 17's "adds no engine to a cluster that has none".
- *`talk/engine-up.sh` refuses a cluster whose Kyverno came from the platform's HelmRelease.* A
  `kind-driftwood` brought up before this ticket runs Kyverno from `kyverno/kyverno`. Applying the
  declared engine over it gives one engine two owners, and deleting that HelmRelease uninstalls
  Kyverno's CRDs and every policy with them. The script names both ways out and changes nothing.
- *Stale instructions were corrected in the adopters.* Each `verify-reconcile.sh` skip text told a
  reader to run platform `engine/up.sh` on the adopter's cluster, and tuppence's
  `reset/README.md` named it as a prerequisite. Both now name the declared engine.

**What was measured, on 2026-09-26, on the owner's Mac.**

- The hub check's selfcheck plants 17 estates and each grades as planted. Among them: tuppence on
  another row of the table while it shares `kind-driftwood` (FAIL), ludlow on another row while it
  shares nothing (PASS), a ludlow script moved onto `kind-tuppence` with the two disagreeing
  (FAIL), `talk/up.sh` still running platform `engine/up.sh` (FAIL) and an engine added to
  `kind-ludlow` (FAIL), and tuppence on another row when `talk/up.sh` does not run driftwood's
  own bring-up (FAIL, because the engine's owner counts as a user of its cluster). Six mutations
  of the check (no shared-cluster comparison, no field comparison, the reference install allowed,
  an engine allowed anywhere, the sharing hard-coded, and the owner not counted as a user) each
  make the selfcheck fail.
- The check over an estate of platform `origin/main` (`cb680f2`) and the three adopters'
  `origin/main` (driftwood `5d0f467`, tuppence `0be3665`, ludlow `2eca9d0`): exit 1, five FAIL
  lines, each naming a missing declaration. Over the same platform and the three adopter branch
  heads: exit 0, "all 5 assertions hold".
- The check over copies of the real files, each with one plant: tuppence's install sha256 changed
  in its last character (FAIL, naming both values, and FAIL on `kind-driftwood`); ludlow's file
  removed (FAIL); `origin/main`'s `talk/up.sh` (FAIL twice: the reference install, and no engine
  where the platform layers run); tuppence's `reset/up.sh` moved to `kind-tuppence` (PASS, "no
  named cluster is used by more than one adopter").
- `talk/up.sh` was run in all four modes with `kind`, `kubectl`, `flux` and `timeout` stubbed, over
  the branch estate. In each mode the only engine install is `talk/engine-up.sh driftwood`: one
  server-side apply on `kind-driftwood` of a file whose sha256 is `3dcd43ea...`, then the
  flux-operator HelmRelease. No engine call names `kind-tuppence` or `kind-ludlow`, and platform
  `engine/up.sh` is never run. `talk/engine-up.sh` alone refused before any apply on a stubbed
  HelmRelease `kyverno/kyverno`. On a declaration whose sha256 does not match the download it
  refused before the engine apply, after applying only the substrate Namespaces. It refused after
  the apply when the stubbed admission controller reported `v1.19.1`.
- Each adopter's `.github/tests` passes (8 tests). The new workflow test fails against
  `origin/main`'s `drift-sample.yml` and `shift-left.yml`, on a `KYVERNO_VERSION` typed back into
  the lane's env, and on a second, client-side apply of the engine.
- `verify/sampler-wait-order/`, which reads each adopter's `drift-sample.yml`, passes over the
  `origin/main` estate and over the branch estate. `verify/fold-agreement/` and
  `verify/real-signature/` read the `adopter gate` step and the job-level identity env of each
  `shift-left.yml`. Neither changed. They were read, not run.

**What CI measured, on 2026-09-26.**

- Each adopter pull request's `shift-left` and `compose-check` jobs pass (Actions ids: driftwood
  36242241671, tuppence 36242243112, ludlow 36242244410). The logs show the declared CLI's
  `kyverno.tar.gz: OK`, "kyverno CLI 1.18.2: the engine gitops/engine/kyverno.yaml declares", the
  8 `.github/tests` passing and "composed artefact matches the committed copy -- no drift". The
  latest `shift-left` runs of ticket 143a's pull requests in the same repositories also pass.
- The hub branch's `truth` workflow on `4fc814b` (Actions id 36242579517) printed a TRUTH line.
  A branch run records nothing, so its figures are not citable: pass=88 fail=3 total=131 ceiling=112.
  The newest recorded line on `main`, run 358 on `ef0edb9`, carries pass=88 fail=2 total=130 ceiling=111.
  The two fails on both are `verify/forge-review/` and
  `verify/schedules/`. The one more fail on the branch is the new row: it reads the adopters'
  `origin/main`, where no declaration exists yet. Its selfcheck passed on the Linux runner. The
  hub pull request's own truth run cannot pass that row before the three adopter pull requests
  merge.

**Not run live.** No KinD cluster ran. The Docker daemon on the owner's Mac was not running, and
this builder did not start it, because other sessions share the machine and a Docker start can
bring the named clusters back. So `talk/engine-up.sh` has not installed Kyverno on a real cluster.
The live proof is the first `talk/up.sh` on a fresh `kind-driftwood`.

**Done, clause by clause.** On the branches: the file exists in each adopter, the composed header
is current, `talk/up.sh` installs `kind-driftwood`'s engine from driftwood's file and none on
`kind-tuppence` or `kind-ludlow`, and both checks fail on planted disagreements. After the merges:
the file and the header on each adopter's `origin/main`, and the hub check passing on the hub.
After the merges and a scheduled run: a scheduled drift sample on each adopter that installed
Kyverno from the file. A dispatched run does not count. This ticket is not resolved until then.
