# 146 — One grader run grades every engine a line names

Type: task
Status: open
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
   (the governed-namespace guard, the orphan cage and the others) are graded the same way, against
   the platform tools release that ships them. Some of them build the same `variables.tier` label
   map that does not compile on 1.19.1.
5. **A candidate grade before the cut** (decision 19). An uncut element that carries
   `tested_engines` is graded on the tree of the commit that declares it. After the cut, the grade
   reads the tag. So the gate is not red for the time between a declaration and its cut, and the
   cut is signed only after every cell passes.
6. **The gate installs every engine in the table.** `truth.yml` and `verify-cage-engine.sh` pass
   one binary for each engine to the grader. Until ticket 149 adds a second engine, the table has
   one row.
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
   - "including a generation difference" (`:67-69`) is refuted by the diagnosis;
   - the "Contract and release boundary" paragraph and "deliberately not a pre-cut gate" are
     reversed by item 5.

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
