# Retained legacy metadata and new extraction

`source_metadata_migration` preserves original receipt artifacts while mapping a frozen
legacy grammar into the existing metadata acquisition shape. It does not establish old
execution lineage, publisher authentication, historical publication or missing authorship.
The stock adapter/checker and their closed schemas remain strict.

The custodian interface is:

- `prepare_extraction_plan`: freeze a TEST_ONLY text/HTML child/process-file closure and
  canonical configuration before executing source bytes.
- `prepare_pdf_extraction_plan`: freeze a supplied native converter/configuration/version
  observation/resource closure without executing that converter. The PDF route uses fixed
  `-cfg`, UTF-8, Unix EOL, no page break and whole-document stdout arguments.
- `execute_new_extraction`: verify exact parent/resources, execute within fixed limits,
  retain observed command/time/exit/stdout/stderr/output, and return archive/receipt artifacts.
  Failure produces evidence and no successful receipt/index. Callers retain failures.
- `describe_legacy_adaptation`: construct a clearly new representation record; it cannot
  replace the original receipt or prove a new HTTP capture.
- `freeze_migration_authority`: bind independent layout and observed-index defaults and
  actual helper modules through `MetadataAuthority.freeze`. No packet chooses these values.

Each extraction plan is closed and contains schema/purpose/profile, exact parent hash and
length, new member ID, predecessor seal reference, retained implementation/configuration
pins and a SHA-256-addressed archive. A result contains status/failure, archive, receipts and
dossier pin; successful results additionally contain the derived member and custody index.
The member's default parent identifier is `original`; if a host uses another identifier it
must conserve the same exact parent hash when assembling the reviewed metadata manifest.

The layout configuration is exactly `{schema, purpose, transport_contract_sha256}` with
schema `twin.source-legacy-layout/v1`. The optional transport pin addresses an independently
reviewed `twin.source-legacy-transport-contract/v1` artifact containing purpose, exact legacy
kind/method literals and standardized acquisition kind. Missing original kind/method or
transport proof holds. HTTP status or a URL alone cannot establish transport. The core aliases
and eight closed entry variants are fixed in source; unknown variants/types hold. Nested old
extraction paths/commands/exits remain preserved metadata, never executable selections.

The execution contract is exactly `{schema, purpose, index_sha256s}`, with schema
`twin.source-migration-execution-contract/v1`. Its indexes must be independently selected
from actually observed/reviewed execution; matching public dictionaries cannot enrol
new indexes. The authority keeps actual helper module/guard references privately, rechecks
live function/default/dispatch identities and full source pins, and verifies before/after
callbacks. Clones use independent deep JSON defaults and the actual protected globals.
Empty helper tuples preserve stock callers. Arbitrary callers choosing unreviewed callbacks
or policy do not establish approved authority. Public exports cannot populate a fresh store.

HTML retains one whole-transform disclosure. A separately pinned generated-syntax artifact
records LF event ranges; bounded validation replay checks the complete output/map and every
publisher observation/statement/excerpt rejects generated-range intersections. Original data
LFs remain distinct. Converted HTML is never falsely labelled raw byte-copy. Native PDF
formatting provenance is unestablished; publisher quotations from native derived output
hold until a reviewed provenance capability exists. Raw/producer witnesses still follow all
stock origin, byte, review and authorship requirements.

Profile limits (MiB = 1,048,576 bytes): text input/stdout 64/64 MiB and 10s; HTML 64/128 MiB
and 30s; PDF 256/128 MiB and 120s. Stderr is 1/1/4 MiB respectively, syntax metadata is capped
at 64 MiB. The total wall budget includes a single two-second cleanup allowance, reserved
from extraction time; TERM grace, final KILL, direct-child reap and group-absence observation
share that allowance. Pipes are streamed. Exit is observed with `waitid(WNOWAIT)` so the
unreaped leader reserves its PID/PGID through the final group signal, even after a zero exit
and closed pipes. Direct-parent exit never proves group completion. No destructive signal
is sent after reaping. Only the direct child is reaped by this process; descendants are not
claimed reaped. Success requires independently observed group absence and workspace removal.
If reaping or group absence is unverified, the result holds and its fresh workspace is
preserved for the custodian; no other workspace or process group is cleaned.
Failure/truncation is explicit. Zero exit with bounded diagnostic stderr is accepted by the
fixed v1 diagnostic policy; nonzero exit, overflow, timeout or cleanup failure is not success.

## Current capability limits

Actual native/OS dependency observation is **not implemented**. Every actual-purpose
extraction plan holds, including a well-shaped forged complete-runtime declaration with
arbitrary retained platform files. The fixed native execution/resource/receipt route exists;
a separately reviewed actual dependency-observation adapter is still required to admit an
actual plan. No caller-provided scope label, file list, version string or hash proves completeness.

TEST_ONLY text/HTML tests really execute the fixed child; the native-route tests execute only
a clearly synthetic fake converter or mock the OS process seam. They do not establish real
PDF conversion, full macOS/dyld closure or actual metadata acquisition readiness. No runtime
or package is installed. The TEST_ONLY closure retains child/interpreter/loaded child process
files plus driver/core/schema sources and driver helper identities; it is explicitly scoped
and is not a claim of complete parent-process or OS dynamic dependency closure.

All original intake order/dispositions, old seals/artifacts, rights/grouping/exposure,
unsupported literals, publication precision/origin and missing provenance facts remain the
later data custodian's responsibility. This module does not issue producer statements,
create population/reference/annual records, infer availability/age, or repair source semantics.
New hashes/version names never fill missing old execution/authorship facts.
