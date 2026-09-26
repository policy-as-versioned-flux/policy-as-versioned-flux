# 146 — One grader run grades every engine a line names

Type: task
Status: resolved
Blocked by: none

## Question

Graduated 2026-09-25 from grilling ticket 71, decisions 7, 8, 16 and 19 (delegated), and ADR-0033
points 1, 4 and 5.

A line supports exactly the engines in its `tested_engines`. On each of them, every body that the
line serves compiles and its fixtures pass (ADR-0033 point 1). Today the grader cannot grade that:

- `computed-semver/engine_compatibility.py` `check()` requires `tested_engines.kyverno == [running
  version]`, so a list with a second engine reads could-not-look.
- It grades two families only, cage-tier and cage-netpol (`FAMILIES`, `:26`).
- It grades tagged lines only. An uncut element reads could-not-look.
- `verify-cage-engine.sh` is a `self-proof` row in `talk/verify-manifest.txt`, so could-not-look
  turns the gate red.

Build the following:

1. **The engine table.** The platform keeps one file that lists each Kyverno version the estate
   may run. For each version it holds a pinned sha256 for the CLI tarball of each platform the
   estate uses, for `install.yaml`, and the Helm chart version where the platform installs with
   Helm. The 1.18.2 checksums already pinned in the workflows are the first row. Take every new
   checksum from the upstream release's own checksum file, and record the source.
2. **One run grades every cell.** A cell is one line on one engine. `check()` takes one binary for
   each engine. For each line, it grades each engine in the line's `tested_engines`. A listed cell
   with no binary reads could-not-look. A binary for an engine that no line lists is reported as
   extra, and it is never read as support. The report shows the whole matrix.
3. **Every body the line serves.** The grade covers each body in the line's tree: it compiles on
   the engine, and its fixtures pass. `require-nonroot`, `stamp-posture` and
   `posture-trust-boundary` join cage-tier and cage-netpol. Where a body has no fixture, write one.
   The `scope` value of `tested_engines` changes, so that an old declaration cannot pass under the
   wider meaning.
4. **The machinery has its own `tested_engines`.** The machinery bodies that the composer renders
   are graded the same way, against the platform tools release that ships them. Two of them,
   `orphan-cage` and `governed-namespace-guard`, build the same `posture.acme.io/tier` label map as
   cage-tier, but their `variables.tier` is the string literal `'isolated'`. A review run on
   2026-09-26 compiled both on 1.19.1 under the offline CLI. That run is not captured. The other
   machinery bodies have not run on 1.19.1.
5. **A candidate grade before the cut** (decision 19). An uncut element that carries
   `tested_engines` is graded on the tree of the commit that declares it. After the cut, the grade
   reads the tag. So the gate is not red for the time between a declaration and its cut, and the
   cut is signed only after every cell passes.
6. **The gate installs every engine in the table.** `truth.yml` and `verify-cage-engine.sh` pass
   one binary for each engine to the grader. The table has one row until ticket 148 or ticket 149
   needs 1.19.1. Whichever of the two lands first adds the 1.19.1 row.
7. **A gate check on the estate's own pins** (ADR-0033 point 5). Each of these must name a version
   in the table and a supported engine of every served line:
   - the hub `truth.yml` CLI;
   - the platform `release.yml` and `cut-release.yml` CLI;
   - the platform reference install, `engine/kyverno/helmrelease.yaml` (through the table's chart
     column);
   - the hub test constant `PINNED_KYVERNO` in `tests/test_cage_ladder_holes.py`, or the test reads
     the table instead.

   An adopter's pins are out of scope, because ticket 147 makes them the adopter's declared engine.
8. **`cut-release-update-array-commit.sh` keeps `tested_engines`.** It rebuilds only quoted scalar
   keys with `[^}]*`. An element that carries `tested_engines` before its cut loses the field and
   gains a stray `}`. Under item 5 every new element carries the field before its cut. Write the
   red test first.
9. **The platform records state what is true.** In `computed-semver/README.md`:
   - "not a runtime support range" is now false (ADR-0033);
   - "The two current rows (policy 4.0.0 and 5.0.0)" is stale, because 4.0.0 is retired;
   - "including a generation difference" (`:67-69`) was not reproduced on 1.19.1 by the diagnosis;
   - the "Contract and release boundary" paragraph, and the sentence that the gate is "deliberately
     **not** wired as a new-policy pre-cut gate", are reversed by item 5.

   The comment in `engine/kyverno/helmrelease.yaml` cites "ADR-0003's '>=1.18' floor", which
   ADR-0033 supersedes.
10. **`graded/verify-graded.sh` states the engine it measured with.** It calls a bare `kyverno`
    and asserts no version (laya-loophole ticket 08, side finding 1).

## Done

On `origin/main`, the hub gate's cage-engine check grades 5.0.0 on 1.18.2 from the engine table,
over every body in the line, and it passes. A test with a second listed engine and no binary reads
could-not-look. A test with an uncut element graded on its candidate tree passes, and one whose
candidate fails a cell reads FAIL. The pins check passes on main and fails on a planted pin that no
line supports. The cut script keeps a `tested_engines` that it finds before a cut.

## Notes

- The pins as read on 2026-09-25: hub `.github/workflows/truth.yml:58-59`; platform
  `.github/workflows/release.yml:52-53` and `cut-release.yml:92-93`; platform
  `engine/kyverno/helmrelease.yaml:36`, chart 3.8.2, app version 1.18.2; hub
  `tests/test_cage_ladder_holes.py:61`.
- The grade widens under item 3, so the 5.0.0 element's `tested_engines` must be graded again under
  the new scope before the new scope value is written on it.
- No platform tools tag is needed for items 1 to 3 and 5 to 10. The hub gate grades platform
  `main`. Item 4 grades the machinery on platform `main` too. The machinery reaches adopters only
  with ticket 148's tools tag.

## Comments

**2026-09-26, owner-instructed: built as two pull requests.** On 2026-09-26 the owner answered
"Authorised" to a list that began "build eco-system tickets 146 to 150". This ticket is built as a
platform pull request (policy-as-versioned-platform/platform#47, branch `ticket-146-engine-cells`)
and this hub pull request. Nothing here reaches an adopter, and no tag is cut. The platform pull
request must merge first. Until it does, the hub gate's `verify/estate-engines/` check reads no
engine table on platform `main` and fails by name.

What the two pull requests build, item by item:

1. **The engine table** is platform `engine/kyverno/engine-table.yaml`, read by
   `engine/engine_table.py`, which refuses a malformed row. It has one row, 1.18.2. The CLI
   checksums (darwin_arm64 `cc69bc66...`, linux_x86_64 `cb2feb83...`) are from
   `https://github.com/kyverno/kyverno/releases/download/v1.18.2/checksums.txt`. The linux_x86_64
   value equals the pin in hub `truth.yml` and platform `release.yml` and `cut-release.yml`.
   `install.yaml` is not listed in that checksums file. Its sha256 (`3dcd43ea...`) is the GitHub
   release API's asset digest, the sha256 of the file downloaded on 2026-09-26, and the pin in all
   three adopters' `drift-sample.yml`. All three agree. The chart row (3.8.2, appVersion v1.18.2,
   digest `f4fc787c...`) is from `https://kyverno.github.io/kyverno/index.yaml`.
   `engine/install-kyverno-engines.sh` installs every row by checksum.
2. **One run grades every cell.** `computed-semver/engine_compatibility.py` `check()` takes one
   binary per engine and identifies each by running it. A listed cell with no binary reads
   could-not-look. A binary no subject lists is reported as extra and never read as support. The
   report prints the whole matrix.
3. **Every body the line serves.** The new scope is `every-served-body-v1`. The grader refuses
   `published-cage-fixtures-v1` by name. Fixtures for `require-nonroot`, `stamp-posture` and
   `posture-trust-boundary` at 5.0.0 are new, in `computed-semver/engine-fixtures/v5.0.0/`,
   written against the tagged bytes. 5.0.0 was graded under the new scope on a throwaway commit
   before the scope was written on its element.
4. **The machinery** declares `tested_engines` in platform `distribution/machinery.yaml`. The
   grader renders it through a new public `machinery_members()` in `compose/composition.py`, the
   same call composition makes, and grades each member against
   `computed-semver/engine-fixtures/machinery/<member>/`.
5. **The candidate grade.** An uncut element with `tested_engines` is graded on the commit being
   graded, which is the commit that declares it. `cut-release.yml` now installs every engine in
   the table and runs the grader after the publisher gate and before the evidence commit, so no
   tag is signed until every cell passes. `verify-first-gate-determined-release.sh` asserts that
   step's place.
6. **The gate installs every engine.** Hub `truth.yml` assembles the estate, fetches the platform
   tags, installs every row's linux_x86_64 CLI by the table's checksum into `RUNNER_TEMP`, and
   names the directory in `KYVERNO_ENGINE_DIR`. `verify-cage-engine.sh` hands that directory to
   the grader.
7. **The pins check** is `verify/estate-engines/`. It is not called `engine-pins`, because a file
   hook refuses that word in a file name. It reads the five pins and fails on a planted pin that no
   served line supports.
8. **The cut script** keeps a nested `tested_engines`. The red test is case 9 of platform
   `verify-cut-release-tags.sh`, committed before the fix.
9. **The records.** The computed-semver README section is rewritten, and the four statements are
   gone. The `helmrelease.yaml` comment cites ADR-0033 and the table.
10. **`graded/verify-graded.sh`** prints the engine it measured with, and fails by name if the
    engine is not a row of the table.

**2026-09-26, delegated decisions made during the build (ADR-0025).**

- The table lives beside the reference install whose chart column it constrains, and is named
  for what ADR-0033 calls it. Checksums are quoted strings, because YAML reads an all-digit value
  as an integer, and the macOS `sha256sum` passed a malformed line when one was tried.
- A body with no fixture FAILS its cell rather than reading could-not-look. Support means its
  fixtures pass, and the remedy is the estate's own: write one.
- The grader reads one commit (HEAD by default) for the array, the machinery and the line
  fixtures, never the working tree. Line fixtures are read from that commit, not from the tag,
  because they can be written after the cut. The row records both identities. For cage-tier and
  cage-netpol the tag's own `graded/tests` fixture always runs as well, and a later fixture runs
  beside it, never instead of it (added by the fixer, below).
- The machinery declaration is its own file, not a key in `versions.yaml`. That file is a
  ResourceSet clusters apply, and several readers parse its array.
- The grader gains the generated-documents comparison that ticket 149 item 4 describes, as a
  `generates.yaml` in a fixture folder. Reason, measured: on 1.18.2 `kyverno test` reads a
  generator trigger that the body excludes as Pass / Excluded, even on a row that expects a
  generated resource. So a `kyverno test` fixture for the bottom-rung generator passed with a
  gate planted to exclude one trigger. The `generates.yaml` fixture fails on that plant. Ticket
  149 can reuse the format for cage-netpol.
- The two UPDATE-only holds are graded on compiling only. Measured: `kyverno test` never matches
  an UPDATE-only body, and the rows read Pass / Excluded with the oldObject gate removed too. A
  planted compile error fails the run.
- Corrected by the fixer. The builder wrote here that `kyverno test` does not evaluate
  `namespaceSelector`. That was wrong. `kyverno test` evaluates it only against a Namespace that a
  `cli.kyverno.io/v1alpha1` Values file declares. The builder's two governed-namespace fixtures
  declared none. So the CLI applied those bodies to no pod, and every row read Pass / Excluded
  whatever it asserted. The fixer's paragraph below says what changed.
- `PINNED_KYVERNO` stays a constant, and the pins check reads it with `ast`. Making the test read
  the table would tie the hub pytest suite to the platform clone's table.
- The pins check binds the pins to the cut lines and to the machinery. An uncut candidate serves
  nothing, and the grader grades its cut. The check reads each subject's `kyverno` list, and
  leaves the scope to the grader.
- Hub `truth.yml` installs the engines inline from the table, rather than by running the
  platform's installer script, so a platform script change cannot change how the hub installs.

**2026-09-26, what was measured on the branches.** Local runs on the owner's Mac, pinned CLI
1.18.2 (darwin_arm64, checksum verified), on a scratch estate of every repository's `origin/main`
with platform at the builder's head `ea027f9`. Two sentences below are corrected by the fixer.

- Grader tests: 19 pass (`python3 -m unittest test_engine_compatibility`). They include a second
  listed engine with no binary (could-not-look), a candidate graded on its declaring commit
  (pass), a candidate that fails a cell (FAIL, exit 1), and a named engine directory with no
  binary (could-not-look, never the CLI on PATH).
- The real grade before the scope moved: 5.0.0 reads could-not-look, naming the retired scope.
  Under the new scope, on 1.18.2: cage-tier 13, cage-netpol 11, require-nonroot 6, stamp-posture 5
  and posture-trust-boundary 5 assertions pass, and all seven machinery bodies pass. Two of those
  seven passed on rows that all read Excluded, so they graded nothing (corrected by the fixer).
  `verify-cage-engine.sh` ends `PASS: engine cells -- passed; 2 cell(s): 2 passed`.
- With 1.19.1 listed on a throwaway commit and both binaries handed in, the 5.0.0 cell on 1.19.1
  reads FAIL: cage-tier does not compile, and cage-netpol reads 9/2, as the diagnosis found. The
  other three 5.0.0 bodies and all seven machinery bodies pass on 1.19.1 under these fixtures.
  That is an offline measurement, not a support claim. Only tickets 148 and 149 list 1.19.1.
- Each new fixture fails when its body is planted broken, except the two governed-namespace
  fixtures. The reviewer planted a wrong bottom rung, and `governed-namespace-requires-claim` still
  passed (corrected by the fixer).
- `verify-cut-release-tags.sh` case 9 fails on the old script, with the field dropped and a stray
  brace. It passes after the fix. A degraded cut still writes `tier: "quarantine"`.
- `verify/estate-engines/` passes with platform at the branch, fails on platform `main` (no
  table), and fails with 1.19.1 planted in a copy of `truth.yml`. Its selfcheck grades twelve
  planted estates as planted.
- `graded/verify-graded.sh` on 1.18.2: the offline proofs hold and the live tail skips. On
  1.19.1 it fails, naming the engine.

**2026-09-26, owner-instructed: the review's findings, fixed on the same two branches.** On
2026-09-26 the owner answered "Authorised" to a list that began "build eco-system tickets 146 to
150". A reviewer read both pull requests and returned one blocking finding and four minor ones.
The fixer pushed to the same branches, platform#47 and this pull request. Nothing was merged or
tagged.

- **Blocking: two machinery fixtures graded nothing.** The reviewer measured it on 1.18.2. Every
  row of `governed-namespace-requires-claim` and `governed-namespace-unclaimed-report` read
  Pass / Excluded, and a wrong `patched.yaml` still passed. The bodies match on
  `namespaceSelector`, and `kyverno test` evaluates that only against a Namespace a Values file
  declares. Each governed-namespace folder now carries a `values.yaml` that declares `governed-ns`
  (`policy-as-versioned.dev/governed: "true"`) and `app-ns` (`"false"`). A new skip row puts the
  unclaimed pod in `app-ns`, so the fixtures now grade the namespace scope too. The instrument
  catches this class itself now. The grader runs `kyverno test -o json` and reads each row's
  reason, and a pass or fail row that reads Excluded fails its body. The false sentences above
  are corrected in place, and both platform READMEs say what is true.
- **Minor: a later fixture could replace the tag-bound cage grade.** Accepted. For cage-tier and
  cage-netpol the tag's `graded/tests` fixture now always runs. An `engine-fixtures` folder for
  the same body runs beside it and never instead of it.
- **Minor: the green path has run only locally.** Accepted. The fixer cannot dispatch a
  workflow. The integrator's merge order names the dispatch and what it must show.
- **Minor: a failed engine download stopped the whole gate.** Accepted. The `truth.yml` step now
  prints `::error::` naming the row, installs nothing for it, and goes on.
  `KYVERNO_ENGINE_DIR` is set before any download. The grader then reads that engine's cells as
  could-not-look, and its verdict line names them.
- **Minor: the PASS line named no served artefact.** Accepted. The verdict line now names the
  graded platform commit, each cut line's tag and the commit it points at, and every cell that
  did not pass, with its reason.

**2026-09-26, delegated decisions made by the fixer (ADR-0025).**

- The grader reads rows from `kyverno test -o json`, not from the printed table. Reason, measured:
  1.18.2 and 1.19.1 print the same JSON fields (`POLICY`, `RESOURCE`, `RESULT`, `REASON`), with no
  colour codes and no column widths to parse.
- A skip row may read Excluded. Reason, measured: Excluded means the engine did not apply the
  policy, which is what a skip row asserts. If the body does act, the row reads "Want skip, got
  pass" and fails. The two holds and two cage-netpol rows rely on this.
- A run whose rows cannot be read, or whose row count differs from its summary, fails its body
  and names why. It does not read could-not-look, because the engine ran and the grade cannot be
  shown to hold.
- `governed-namespace-cage-holds` also carries the `values.yaml`. Reason: its rows now read
  Excluded because it is UPDATE-only, not because its Namespace is unknown. Measured: with the
  Namespace declared and the gate removed it still reads Excluded, and with CREATE added it reads
  "Want skip, got pass".
- `verify/estate-engines/` is not extended to check the installed engine directory. Reason: the
  grader's verdict line already names a row that did not install, inside the record (measured
  below), and `estate-engines` stays a check of files that runs the same locally and on CI.

**2026-09-26, what the fixer measured.** Local runs on the owner's Mac. The pinned CLI 1.18.2
and, offline only, 1.19.1 were used. Both darwin_arm64 archives were checked against
`https://github.com/kyverno/kyverno/releases/download/v1.18.2/checksums.txt` and
`https://github.com/kyverno/kyverno/releases/download/v1.19.1/checksums.txt`. The platform
branch head sits directly on platform `origin/main` `541d2aa`.

- Grader tests: 23 pass. On the builder's grader (`ea027f9`) the final test file gives six failures
  and one error (corrected by the integrator from the review's measurement: this line first said
  four). Among them are an excluded pass row, rows that cannot be read, the tag-bound cage grade and
  the verdict line.
- `verify-cage-engine.sh` at the platform head with `KYVERNO_ENGINE_DIR` holding 1.18.2 exits 0
  and ends `PASS: engine cells -- passed; 2 cell(s): 2 passed; graded platform commit
  1dba561...: policy 5.0.0 from refs/tags/policy/v5.0.0 at 5b88f1d...`.
- Row reasons on 1.18.2. Policy 5.0.0: cage-tier 13 Ok; cage-netpol 9 Ok and 2 skip rows
  Excluded; require-nonroot 6 Ok; stamp-posture 5 Ok; posture-trust-boundary 5 Ok. Machinery: the
  orphan guard 3 Ok and the orphan cage 3 Ok. Each governed-namespace body reads 2 Ok and 1 skip
  row Excluded. The holds read skip rows Excluded only. The bottom-rung generator passes on five
  triggers.
- The builder's fixtures under the new grader: FAIL, naming each Excluded pass or fail row of
  both governed-namespace bodies.
- Six plants, each on a throwaway commit, each FAIL: the selector matching `governed: "yes"`
  (Excluded refused); a selector matching every Namespace ("Want skip, got pass" and "Want skip,
  got fail"); a `patched.yaml` on `baseline` ("Resource diff"); the report's fail row flipped to
  pass ("Want pass, got fail"); `BOTTOM_RUNG = 'baseline'`, the reviewer's plant, which now fails
  `governed-namespace-requires-claim` as well as the orphan cage and the bottom rung; and the
  `values.yaml` removed (Excluded refused).
- The machinery listed on 1.19.1 on a throwaway commit, with both binaries handed in: 3 cells
  pass, with the same row reasons. That is an offline measurement, not a support claim.
- The new `truth.yml` engine step, lifted verbatim and run under `bash -e` with the darwin column
  swapped in, exits 0 in all seven cases. A good row installs. A wrong checksum, a release that
  does not exist, a checksum YAML reads as a number, a wrong archive name and an unreadable table
  each print `::error::` naming the row, and the good rows beside them still install. The branch
  for a binary that reports another version was not exercised.
- The grader handed the directory from the wrong-checksum case, with 1.19.1 listed on the
  machinery: exit 3, `SKIP: ... not passed: machinery on 1.19.1 could-not-look (no binary for
  kyverno 1.19.1 was handed to this run)`.
- On a throwaway merge of this branch onto hub `origin/main` `8ee6a97c`, with platform at
  `1dba561`: `verify/estate-engines/` passes 5 of 5, and its selfcheck grades 12 planted estates.
  `verify-can-record`, `verify-a-fall-blocks` and `verify-cited-truth` pass.
  `verify-branch-refs`, `verify-schedules`, `verify-forge-review` and `verify-local-clock` read
  the same as on `origin/main`. `tests/test_can_record.py` (28), `test_fall_check.py` (46),
  `test_schedules_clock.py` (32) and `test_lost_recordings.py` (7) pass.

**2026-09-26, the integrator, before the merge.** Review round 2 approved with three minor
findings. Two are fixed on this branch. First, `truth.yml` now exports `KYVERNO_ENGINE_DIR` before
it reads the engine table, so an absent table leaves the directory empty and every listed cell
reads could-not-look. Before this fix the step exited first, and `verify-cage-engine.sh` then used
the CLI on `PATH`. Second, the test count above is corrected. The third finding is outside this
ticket and is carried here: platform `distribution/render-governed-namespace-guard.py` and
`distribution/verify-governed-namespace-guard.sh` still say that the kyverno CLI cannot evaluate
`namespaceSelector` offline. The review measured on 1.18.2 that `kyverno test` and `kyverno apply`
evaluate it against a Namespace that a Values file declares.

## Answer

Resolved 2026-09-26 by the integrator. Platform PR 47 merged as cb680f22 and hub PR 146 as
ef0edb98, both as `pavc-other-hand`, after review round 2 approved. The owner authorised the
delivery on 2026-09-26: "Authorised" (owner-instructed).

Truth run 358 on hub `main` (`talk/truth.log`, 2026-09-26T12:32Z, hub ef0edb9, platform
cb680f2@main) records pass=88 and no fall. It measured each Done clause as follows:

- `.estate-clone/platform/computed-semver/verify-cage-engine.sh` PASS. Its recorded capture grades
  two cells, policy 5.0.0 and the machinery, on 1.18.2 from the engine table, and both pass. Each
  body is read by `git archive` at `refs/tags/policy/v5.0.0` or at the graded platform commit.
- `verify/estate-engines/verify-estate-engines.sh` PASS: "all 5 of the estate's own engine pins
  name a row of the platform engine table and a supported engine of every served line and of the
  machinery". Its selfcheck fails on each planted unsupported pin.
- `.estate-clone/platform/verify-cut-release-tags.sh` PASS, with case 9: "the array rewrite keeps
  a nested tested_engines it finds before the cut".
- The platform unit tests in `computed-semver/test_engine_compatibility.py` cover a second listed
  engine with no binary (could-not-look), and a candidate that passes or fails a cell (PASS or
  FAIL). They ran on the fixer's head, 1dba561, which platform `main` carries.

What stays open elsewhere: the table has one row, 1.18.2, until ticket 148 or ticket 149 adds
1.19.1. The two UPDATE-only holds are graded on compiling only, because the offline CLI evaluates
every resource as a CREATE.
