# Structural PDF output origin verification

`twin.pdf_output_origin` implements the raw `pdf-text-xpdf-origin/2` wire replay
and conservative witness checks. It never reads a PDF, starts a converter, performs
native observation or grants acquisition authority. Existing `pdf-text-xpdf/1`
publisher witnesses remain held. The new profile is deliberately absent from the
migration executor's supported profile table.

The fixed protocol is `twin.pdf-output-origin-events/v1`, emitter version1.
The independently supplied protocol document SHA256 is
`ce22a762c8e900c331a4d0c9ef87a402f5e7b8527050a20f04d55d1656bcb664`;
its event schema SHA256 is
`b945d708e188a272d93edf438f605fc06333e9b20e1894aaedb82c3f222b5491`.
These pins identify reviewed grammar, not an executable or an observed run.
The two retained `TEST_ONLY-pdf-output-origin` fixtures are constructed protocol
examples. They are not converter output or native execution evidence.

## Interface

`check_pdf_origin_events(output, raw_events)` accepts exact bytes and returns a
passive frozen `PdfOriginMap`. Its canonical `description` binds the raw/output
hashes and lengths, protocol/schema pins, derived runs, scalar boundaries and
barriers. Its scope is explicitly `structural-only-no-native-authority`.
There is no public map-adoption, observation acquisition or index-enrollment API.

`check_pdf_witness(origin_map, start, end)` accepts only that verifier result. It
requires a nonempty UTF-8 scalar-aligned interval within a single eligible chain.
Generated/modified bytes, remapping, ActualText, copies and crossed barriers hold.
An endpoint may touch a barrier while staying entirely on its supported side.

`check_pdf_publisher_witnesses(origin_map, manifest, member_id)` is a structural
source-integration seam for one independently selected member. It binds the exact
member/output and checks every date observation, publisher statement and publisher
excerpt targeting that member. A descendant alias cannot strip its required map.
It does not validate the full metadata schema or admit a map to an authority.
Unrelated members still require their own stock semantic/provenance checks.

The migration authority protects this module alongside its existing helper through
the core live function/code/default/config/source inventory. Its existing stock
checker, execution-contract/index selection, nine-key transform receipt and public
schemas remain unchanged. No callback default carries a private map or authority.

## Replay and bounds

The parser requires canonical ASCII JSON with sorted keys, integer protocol fields,
no duplicate/unknown keys, one LF per record, consecutive event sequence and exactly
one terminal footer. It checks the exact prefix hash/count, complete stdout hash
and partition, code-byte coverage/hash and scalar emit/omit accounting. Fragment0
is replacement-only ActualText; ordinary code intervals are positive and adjacent.
Missing discontinuity barriers refuse rather than being silently repaired into
eligibility. Extra barriers only restrict witnesses. Duplicate emissions retain
their source scalar identity and are always modified/ineligible.

Fixed caps: wire64MiB, record64KiB, events1,000,000, output128MiB, source code256MiB,
decoder code slice64bytes and scalar arrays4096. Invalid UTF-8, truncation, incomplete
coverage or excess holds. Pure replay has no retry, launch or deadline-extension API.

## Integration still held

Structural replay cannot determine actual wait status, EOF, cleanup, native file
closure, plan/run/config/executable/pipe identity or independent custodian approval.
The raw footer declares intended exit only. Even a valid map is never an actual
observation, publisher authentication, raw-PDF equivalence or a custody-index pin.

The future bridge must revise the native observer for the exact third owned pipe;
drain all three streams under the original deadline; preserve actual private pending
run custody; bind the complete streams and actual wait/EOF/reap/cleanup to the held
plan; construct and cross-check the acyclic host observation envelope; link it through
a newly versioned richer dossier; and retain independent review/index selection and
the mandatory unchanged stock checker. A public envelope cannot self-enroll. No
successful actual handle may escape before the completed origin/dossier/index tuple.

Pure rows P01–P15 and P17 are implemented structurally; P16 covers only raw/output
pins. P18 covers wire/count/record/scalar limits, with native timeout/EOF held. P19–P20
have negative no-authority/no-adoption controls, not actual custody implementation.
P21 checks all three publisher paths structurally; P22 refuses descendant aliases,
while full independently acquired alias custody remains held. P23–P25 preserve the
old profile, strict receipt and protected helper rules. P26 has no authority path
to bypass other evidence gates. P27–P29 reject host/future-binding fields in the raw
grammar, but actual envelope/wait/binding checks are unimplemented. P30 checks exact
captured stdout relation only; actual EOF/nonzero/signal/cleanup gates remain held.
All eight native acceptance rows remain unrun. Pure tests do not complete all30 rows.
