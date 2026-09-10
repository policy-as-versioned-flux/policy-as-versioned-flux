# 110 — A supersede surcharge cannot be re-derived offline, so a signed artefact stops re-rendering

Type: task
Status: open
Blocked by: none

## Question

Two features this estate built and signed now contradict each other, and the contradiction became
observable on 2026-09-10 the moment `ico v4.0.0` was tagged.

**Ticket 45's claim:** an adopter re-verifying its own signed composed tree OFFLINE gets the same
bytes. `verify()` is a byte comparison over every rendered file, so the vendored payload plus
`PROVENANCE.json` must be sufficient and the publisher's clone must not be needed.
`composition.py --selfcheck` asserts exactly that at the seam:
`assert rendered_absent == rendered_present`.

**Ticket 84's surcharge:** when a publisher supersedes the major an adopter pins, the composed
document carries a `supersede` price row, an EOL ramp of `+1x` per year behind capped at `+4x`,
where `since` is the day the newer major's SIGNING TAG was cut.

The surcharge is computed from the publisher's TAG DATES. A vendored copy of a payload cannot
carry the date of a tag that did not exist when it was vendored. So the row appears when the
publisher's clone is present and vanishes when it is absent, and ticket 45's assertion fails.

Measured first-hand in a private estate clone at platform `5b88f1d`, composing driftwood:

```
--- ico ABSENT
+++ ico PRESENT
 | ico | feed      | penalty-schema | driftwood | GBP | GBP 1,787,177.08 | no | isolated |
+| ico | supersede | penalty-schema | driftwood | GBP | GBP 0.00         | no | —        |
```

and, downstream of the extra row, every later price index shifts (`prices[6]` becomes `prices[7]`)
and the artefact's own footer count moves from 8 prices to 9. So the divergence is not one line: it
renumbers the named absences that cite price indices.

The amount is `GBP 0.00` **because the tag was cut that same day** and the ramp is zero on day zero.
It will not stay zero. Tomorrow it is a real number, and the two renders will differ by a priced
amount rather than by a zero.

## What has to be decided

1. **Which claim wins.** Portability and the surcharge cannot both hold in their current form. If
   portability wins, the surcharge has to be derived from something the adopter's own signed tree
   carries. If the surcharge wins, ticket 45's assertion and its promise have to be narrowed, and
   the deck and record that repeat the promise have to be narrowed with them.
2. **If portability wins, where does `since` come from?** The candidate is the vendored
   `PROVENANCE.json`: record the publisher's newest major and the date its tag was cut AT VENDOR
   TIME, so the ramp is a function of the artefact rather than of the world. That makes the number
   reproducible and stale by construction, which is a different honesty problem, and it needs
   saying out loud on the page.
3. **Whether a zero-valued row should render at all.** Today's difference is a row priced at zero.
   A rule that a zero surcharge is recorded but not rendered would postpone this exact failure
   rather than fix it, and would hide the day the clock starts. Decide deliberately, do not drift
   into it.

Done = `composition.py --selfcheck` passes with a publisher clone present and absent, and the
record states which of the two claims was narrowed and why.

## Notes

Charted 2026-09-10. The tag did not break this; it made it reachable. Ticket 84's own record
already names a related half: the supersede line vanished when a newer major's directory was
absent from the pinned checkout, and no adopter workflow passed `--as-of`, so a served line read
0.00 for a tag cut later. This is the same fault line seen from the portability side.

Two adopter pull requests are HELD on ticket 84 (tuppence 27, ludlow 24). Whatever is decided here
governs them, because both subscribe an adopter to a feed whose publisher can supersede it.

Record: ticket 45's `verify-portability`; ticket 84; `composition.py`'s selfcheck at the
`rendered_absent == rendered_present` assertion; `talk/verify-falls.txt` `run=234`.

## Build decisions, 2026-09-10

Implementation is under review; this ticket remains open until review and validation complete.
All choices below are delegated under ADR-0025 and the owner's instruction to implement the
remaining work with review gates.

1. **Portability wins.** A supersede surcharge describes the publisher tag state observed when
   this artefact was composed. It does not establish the publisher's current newest major. The
   handbook prints that limitation on each affected feed, including when the observation is
   current or unobserved, rather than hiding the qualification in a provenance file.
2. **Record the complete observation.** Each vendored `PROVENANCE.json` carries a versioned
   `publisher_observation`: feed identity, pinned version, resolved parent SHA, pin-signature
   observation, supersede observation, newest readable signed target, and oldest signed major's
   tag/date. Recording only `since` would still change the target, the observation and signature
   holes offline. The adopter's existing signature covers this record; it is an observation of
   the publisher's tags, not another publisher declaration or a claim of signature verification.
3. **Fresh composition and verification have different jobs.** Ordinary `compose` reads
   available publisher tags and records a new observation; with a publisher absent it reuses the
   vendored observation. `verify` explicitly replays the adopter's recorded observations even
   when a live publisher has acquired newer tags. The scheduled proposer's existing `compose
   --as-of` remains a fresh observation, so it can discover supersedes and grow the ramp. An
   explicit pricing date is also recorded in `HEADER.yaml` and replayed during verification.
4. **Zero rows remain.** They disclose the day the ramp starts; removing them would merely
   defer the discrepancy. The handbook prints the start and pricing dates beside the row,
   including the existing qualification when pricing precedes the signing date.
5. **Legacy behavior is explicit.** Provenance lacking the new observation cannot prove which
   tags were seen. Verification and offline composition refuse it as a named missing instrument;
   they do not backfill signed history from today's tags. Old signed artefacts remain verifiable
   with their pinned composer. Adopting this composer requires fresh composition with publisher
   clones present, followed by the ordinary reviewed release. Invalid observations, or those
   naming another feed/version/SHA, also refuse. Tuppence 27 and ludlow 24 retain ticket 84's
   release/pin/re-composition prerequisites.
6. **Preserve converter attribution offline.** The fixture exposed another byte difference:
   a converter originally copied from platform was re-labelled as publisher-owned on the next
   offline vendor pass. Re-vendoring preserves `converter_from` from the existing provenance.

### Validation, 2026-09-10

Red first at the `compose()`/`verify()` seam using a synthetic adopter, synthetic publisher git
repository, and the actual shipped converter: the signed newer major produced a different
render with the publisher absent. No fixture tag is placed on a real publisher. Five focused
cases now pass: byte-identical online/offline replay; nonzero pricing and later tags without
rewriting verification history; current/unobserved replay; legacy refresh; invalid identity and
tag dates. The handbook's 47 selfchecks pass. The full `composition.py --selfcheck` passes against an isolated estate assembled from cached
upstream refs: driftwood `a1817254`, nist `f83126f5`, ico `9653fd9f`, feeds `ca403965`, insurer
`61fba9db`, tuppence `bd15aaeb`, ludlow `2c2d740d`; platform is this implementation based on
`5b88f1d`. Its portability leg re-derives all 31 rendered files byte-identically with ico absent.
`pin_content.py --selfcheck`, Python compilation and shell syntax checks also pass.

The selfcheck needed `core.hooksPath=/dev/null` in its process environment because a pre-existing
fixture commit invokes the owner's global network hook otherwise. No persistent config changed.
The pre-existing installed-object invariance assertion excluded the header and handbook but
included provenance; it now excludes `PROVENANCE.json` too, because tag observations intentionally
change that record and no engine installs it.

Mypy reports the same 84 existing diagnostics on the base `5b88f1d` and this implementation;
comparing their messages and multiplicities finds no added or removed diagnostics. This is not a
claim of a clean typecheck. These are local validations, not a recorded TRUTH run, and at this validation checkpoint independent review and release were still pending. The gate wrapper now runs the
five fixture tests before the existing estate selfcheck.

### Independent review, 2026-09-10

Standards: no findings. Spec: one blocking finding was fixed red-first: a signed observation
without its tag and a supersede target tag naming another feed were accepted. Replay now checks
signature-tag presence by state, feed identity and pinned/target major, and start-major ordering.
The sixth focused test plants six malformed observations; all are refused. The reviewer reran
that regression test and confirmed the finding closed. Six focused tests now pass; the earlier
five-test count records validation before this review. Publication and rollout remain pending.


### Publication, 2026-09-10

Both review axes passed after the correction above. The signed implementation commit
`41761fa9747b63d73f52bbc8d9ac40bf3b28faf8` was merged through platform PR24 as
`3602142e5adb26945705c3dc3f86c1ab4ad66721` (the merge tree is identical to the reviewed tree).
The local secret scan reported zero secrets; the owner authorized a per-commit bypass of the
quota-exhausted network hook, with signing retained.

The proposed software release is **v3.0.0**, because the new composer requires a fresh
provenance observation when upgrading legacy compositions. The previous v2.0.1 is 82 commits
behind the implementation. In addition to the composition tests above, the Kyverno 1.18.2
shift-left proof and all eight release-tag fixture scenarios passed. The fixture scenarios
used process-scoped unsigned synthetic tags, not real publisher tags.

Publication is prepared but has not run: automatic approval review rejected the release
workflow dispatch because the authorization to implement, push and merge did not explicitly
name immutable software publication. Owner approval has been requested. After approval: cut
v3.0.0 from the reviewed main, run release.yml at ref v3.0.0 with tag input v3.0.0, verify the
release, then upgrade adopter pins and freshly compose before merging the held subscriptions.
No policy tag is re-cut and no adopter pin is advanced ahead of the software release.


**2026-09-10, publication authorized.** The owner explicitly approved publishing v3.0.0 through
the signed release workflows. The cut workflow is now running as
[34504582573](https://github.com/policy-as-versioned-platform/platform/actions/runs/34504582573).
The earlier automatic-approval block is cleared; signature verification and GitHub Release
publication remain gates before adopter upgrades.


**2026-09-10, published and verified.** The cut run 34504582573 and identity-pinned release run
34504674000 both succeeded. [Platform v3.0.0](https://github.com/policy-as-versioned-platform/platform/releases/tag/v3.0.0)
was published at 16:52:01Z and resolves to reviewed main
`3602142e5adb26945705c3dc3f86c1ab4ad66721`. Release verification checked the Actions signer
identity and issuer, the offline Rekor bundle, and the shift-left proof. Adopter migration is
now unblocked, but no adoption or recorded rollout result is implied by publication.

### Superseded map entry retained as history

- [110 — A supersede surcharge cannot be re-derived offline](issues/110-a-supersede-surcharge-cannot-be-re-derived-offline.md) — CHARTED, not built. Ticket 45 promises a signed composed tree re-renders byte-identically with the publisher's clone ABSENT; ticket 84's supersede surcharge is computed from the publisher's TAG DATES, which a vendored copy cannot carry. Cutting ico v4.0.0 made the contradiction observable: composing driftwood with ico present renders a `supersede` row priced GBP 0.00 that composing it with ico absent does not, which renumbers every later price index and moves the artefact's own footer count. `composition.py --selfcheck` fails on it today. The amount is zero only because the tag was cut that day; tomorrow the two renders differ by a priced amount. One of the two claims has to be narrowed, and the record has to say which.

Map line: `- [110 — A supersede surcharge cannot be re-derived offline](issues/110-a-supersede-surcharge-cannot-be-re-derived-offline.md) — open, implementation reviewed and merged in platform PR24; signed software v3.0.0 published and verified at 3602142. Composition now vendors identity-bound publisher observations and replays them offline; fresh composition observes current tags. Legacy provenance requires fresh composition when upgrading. Adopter pin upgrades, recomposition and recorded rollout proof remain outstanding.`
