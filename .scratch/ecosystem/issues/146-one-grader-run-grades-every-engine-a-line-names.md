# 146 — One grader run grades every engine a line names

Type: task
Status: open
Blocked by: none

## Question

Graduated 2026-09-25 from grilling ticket 71, decisions 7 and 8 (delegated), and ADR-0033.

A line supports exactly the engines in its `tested_engines` (ADR-0033 point 1). Today the grader
cannot grade more than one engine. `computed-semver/engine_compatibility.py` `check()` requires
`tested_engines.kyverno == [running version]`, so a list with a second engine reads
could-not-look, and `verify-cage-engine.sh` is a `self-proof` row in `talk/verify-manifest.txt`,
where could-not-look turns the gate red. Build the following:

1. **The engine table.** The platform keeps one file that lists each Kyverno version the estate
   may run. For each version it holds a pinned sha256 for the CLI tarball of each platform the
   estate uses, and for `install.yaml`. The 1.18.2 checksums already pinned in the workflows are
   the first row. Take every new checksum from the upstream release's own checksum file, and
   record the source.
2. **One run grades every cell.** A cell is one line on one engine. `check()` takes one binary
   for each engine. For each cut line, it grades each engine in the line's `tested_engines`. A
   listed cell with no binary reads could-not-look. A binary for an engine that no line lists is
   reported as extra, and it is never read as support. The report shows the whole matrix.
3. **The gate installs every engine in the table.** `truth.yml` and `verify-cage-engine.sh` pass
   one binary for each engine to the grader. Until ticket 149 adds a second engine, the table has
   one row.
4. **A gate check on the estate's own pins** (ADR-0033 point 5). Each of these must name a version
   in the table and a supported engine of every served line: the hub `truth.yml` CLI, the platform
   `release.yml` and `cut-release.yml` CLI, and the platform `engine/kyverno/helmrelease.yaml`
   engine. The in-cluster engine must equal the release CLI. An adopter's pins are out of scope,
   because ticket 147 makes them the adopter's declared engine.
5. **`cut-release-update-array-commit.sh` keeps `tested_engines`.** It rebuilds only quoted
   scalar keys with `[^}]*`. An element that carries `tested_engines` before its cut loses the
   field and gains a stray `}`. Write the red test first.
6. **The platform README states what is true.** `computed-semver/README.md` says that
   `tested_engines` is "not a runtime support range", and ADR-0033 now makes it one. It also says
   "The two current rows (policy 4.0.0 and 5.0.0)", but 4.0.0 is retired.
7. **`graded/verify-graded.sh` states the engine it measured with.** It calls a bare `kyverno`
   and asserts no version (laya-loophole ticket 08, side finding 1).

## Done

On `origin/main`, the hub gate's cage-engine check grades 5.0.0 on 1.18.2 from the engine table,
and it passes. A test with a second listed engine and no binary reads could-not-look. The pins
check passes on main and fails on a planted pin that no line supports. The cut script keeps a
`tested_engines` that it finds before a cut.

## Notes

- Evidence for the current grader: platform `computed-semver/engine_compatibility.py:163-170`,
  and `test_engine_compatibility.py:136-138`.
- The pins as read on 2026-09-25: hub `.github/workflows/truth.yml:58-59`; platform
  `.github/workflows/release.yml:52-53` and `cut-release.yml:92-93`; platform
  `engine/kyverno/helmrelease.yaml:36`, chart 3.8.2, app version 1.18.2.
- No platform tools tag is needed. The hub gate grades platform `main`.
