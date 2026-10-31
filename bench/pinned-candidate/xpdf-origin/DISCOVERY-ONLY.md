# Separate Linux discovery DATA capability

`discover_linux_tools.py` implements the separately reviewed DISCOVERY_ONLY
operation. Its two interfaces are `discover_linux_tools(selection, owned_parent)`
and pure `check_discovery_bundle(bundle, expected_selection_sha256)`. The latter
takes retained relative-path/bytes pairs and never reads the host. There is no
public appointment setter, execution callback, command option or CLI mode.

The private discovery appointment defaults to absent. Public selection JSON,
review hashes and successful checking cannot populate it. The accepted full-build
appointment and nonnullable review gate are separate and unchanged. Actual parent
bootstrap provenance, trusted query selection, source/workflow/run association,
capacity, appointment delivery and activation remain unconfigured prerequisites.
The source and TEST_ONLY models establish no actual Linux discovery or permission
to run a tool, prepare source, build, invoke a converter or acquire metadata.

The checked-in `discovery-contract/` files retain the exact accepted query profile,
closed records and binding projection. The private parent binds the exact driver,
build supervisor, source preparer, build/discovery contracts and workflow bytes.
Those files are read stably as DATA before setup, retained, and rechecked before
complete export. Independent bootstrap and query writer-control references are
required; root ownership/mode and inventory hashes alone do not establish them.

The fixed operation inventories eleven selectors, then runs fifteen serial fixed
version/target/specs/program-name queries. `/bin/sh` is DATA only. No query output
selects an executable. CMake must report canonical major/minor >=3.24; only
`/usr/share/cmake-M.m/Modules` is considered. Every regular module is retained;
symlink/special entries, changes and unsupported layouts stop collection. GCC
internal replies are retained canonical DATA under the sole selected GCC version
directory and are never executed. Already-loaded bootstrap candidates under
independently selected roots are DATA, without runtime-closure inference.

Version DATA uses finite per-selector syntax: GNU Make/patch, the precise Binutils
tool name, or gcc/g++ with GCC, GNU or an explicitly shaped Ubuntu package heading,
followed by a canonical dotted numeric version. No new minimum is imposed. Only
the selected notice-line grammar may follow the unique heading; wrong tools,
duplicate headings, unknown tails and unsupported variants hold with raw bytes
preserved. A substring `GNU` is insufficient, and Ubuntu compiler headings need
not contain it. This syntax is prospective: actual output compatibility remains
unproved until separately appointed observation. Banner matching is not trust.

The nine-integer stat vector is, in order:
`dev, ino, mode, uid, gid, size, mtime_ns, ctime_ns, nlink`. Candidate routes include
ordered raw symlink targets and link vectors. Stable no-follow descriptor reads,
pre/post vectors, path readback, hashes and lengths bind candidate bytes. Directory
names are bounded while enumerated, sorted, retained and compared before/after.
The pure checker reconstructs the rooted module-directory child-name graph,
including empty leaves/nested directories. Each module file must appear in its
observed parent's list. Missing/unrooted paths, traversal/cycles, conflicting
file/directory roles and unsafe identities cannot form complete DATA.

Parent T0 precedes startup. D is exactly `min(T0+60, original A deadline)` and
includes setup, reads, queries, custody and export. Each query has its original
five-second allowance inclusive of shared two-second cleanup; ten seconds must
remain after that allowance. The accepted supervisor has one private keyword,
`terminal_reserve=0`, restricted to strict integer 0 or 10. Discovery passes literal
10 at its internal pre-Popen admission. Existing build callers retain default 0.
This check is not an atomic real-time or blocking-call guarantee. Late/unknown
observations hold and never receive fresh time.
Time before immutable T0 is refused before workspace acquisition. Its exact
invalid observation is retained in the first fault, without substituting the
later terminal observation or resetting the parent clock.

Actual supervisor command ids, phase, clocks, nullable bindings and raw wait
facts are conserved. The pure checker reconstructs the normative projection;
unknown binding/deadline observations stay null. Consuming-wait cutoff, equal-tick
ordinals, shared cleanup grace, direct reap and group absence use the unchanged
accepted custody checker. Unsettled custody stops further queries and preserves
the workspace; it is never converted into successful cleanup or deletion.

Discovery records use sorted compact UTF-8 JSON, `ensure_ascii=false`, no NaN and
no trailing newline. The accepted environment artifact uses ASCII canonical JSON
**with** its terminating newline. The custody binding hashes ASCII canonical JSON
**without** that newline. `FILES.json` lists exactly payload files, excluding itself
and `RESULT.json`; the result references the prior file manifest. No future
transport envelope or self hash is invented.

Bounds are 256 MiB retained logical DATA, 8192 regular files, 1 MiB per metadata
record, 16 MiB per query stream, 4096-byte paths and sixteen bounded faults with
the original first. Sixteen MiB remains reserved inside the total for failure
evidence; two further metadata records are reserved before normal payload growth.
Thirty-two regular-file slots are also reserved for all thirty possible query
stream prefixes, the sole partial-file prefix and first-failure metadata. Normal
payload is therefore at most 8158 files; even an interrupted export retaining both
terminal files can retain every failure file within the original 8192-file cap.
Before a query the collector conservatively reserves 32 MiB for its two streams.
These checks are not a live disk quota or a measured fit claim. Fifteen worst-case
queries cannot fit sixty seconds. Slow inventory stops with its actual prefix.

Known-terminal partial inventory may export its already captured immutable DATA
within the same original deadline. Unknown/late custody or failed export instead
retains a finite diagnostic prefix and first-failure record without pretending to
be a checker-approved complete bundle. Failed export invalidates complete state;
actual late/null clocks remain unchanged. Cancellation is retained/re-raised after
best-effort finite retention. No workspace is swept or deleted.
Owned descriptor cleanup attempts each known descriptor once. Secondary close
failure preserves/re-raises the first actual exception, including cancellation,
and retains a bounded secondary Fault with unknown time/close outcome. With no
earlier failure, close failure itself fails the operation. Failed close is never
claimed successful; no close retry or process-cleanup authority is introduced.

Every result, including COMPLETE_DATA, has
`build_hold=H_PROBE_EXECUTION_UNESTABLISHED`, `build_complete=false` and
`native_execution=false`. COMPLETE_DATA means captured candidate DATA only.
Later independent review and a separately appointed full build must reacquire
the selected tuple. There is no archive GET, preparation, configure, compile,
generated probe, converter, network, receipt, native qualification or workflow
activation in this capability. The existing tiny900 and A1800/transport300
contracts are unchanged. Actual discovery, Linux bootstrap/tools/modules,
capacity, timing, native access and build outcomes remain UNRUN/UNPROVED.
