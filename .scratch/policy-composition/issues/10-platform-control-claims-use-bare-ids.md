# 10 — `platform`'s control claims use bare ids and name the catalogue by href

Type: task
Status: resolved
Blocked by: none

Source: [`spec.md`](../spec.md), *Baselines, control ids and holes* and *Changes in other repos*.
Decisions: [ADR-0013](../../../docs/adr/0013-regulator-publishes-baselines-adopter-selects.md),
[ADR-0017](../../../docs/adr/0017-a-control-claim-belongs-to-whoever-ships-the-implementation.md).

## What to build

A composition can read the platform's control claims without guessing. The platform's OSCAL
component-definition writes `ac-6` and `cm-6`, never `nist-800-53:AC-6`. Its `source` href names the
`nist` party and a path into it, not a local path with no version.

The two dangling claims stay as they are. `cm-6` claims `require-policy-version` and `ac-6` claims
`may-run-root-if-attested`. Neither policy exists. Fixing them is a separate `platform` defect.
This ticket adds the lint that finds them, so the defect has a red check. The lint resolves every
claimed policy name against the version trees the platform ships and prints each miss. Mark the beat
as expected-red until that defect is fixed, and say so in its output. Do not skip it.

The existing up-flow verify beat still passes on the fixture `PolicyReport`. Update the fixture's ids
to the bare form.

## Acceptance criteria

- [ ] The component-definition carries bare control ids only.
- [ ] Its `source` href names the `nist` party and a catalogue path.
- [ ] The up-flow verify beat still passes with the bare ids.
- [ ] A new lint resolves every claimed policy name against the shipped version trees and names each miss.
- [ ] The lint names the two dangling claims today and is marked expected-red in its own output.
- [ ] The lint resolves each claimed control id against the pinned `nist` catalogue, exact-string, and fails on an unknown id.

## Answer

**Built**, in the `platform` repo (`.estate-clone/platform` locally; `policy-as-versioned-platform/platform`
upstream):

- `oscal/component-definition.json` — both `control-id`s are now bare (`ac-6`, `cm-6`); the
  `control-implementations[].source` now reads
  `https://github.com/policy-as-versioned-nist/nist/blob/v1.0.0/catalog/NIST_SP-800-53_rev5.2.0_catalog.json`
  instead of a bare local path with no version.
- `oscal/result2oscal.py` and `oscal/verify-upflow.sh` — the fixture `PolicyReport` and every
  assert now key on the bare ids (`ac-6` / `cm-6`, not `nist-800-53:AC-6` / `nist-800-53:CM-6`). The
  up-flow beat still passes end to end: `PolicyReport -> observation -> finding -> risk ->
  related-observation resolves`.
- `oscal/lint_claims.py` (new) — resolves every claim two ways: the claimed policy name (`Check_Id`)
  against the identity `distribution/policies/v*/*.yaml` actually ships (suffix-stripped, same
  identity `result2oscal.py` keys on), and the claimed control id against the pinned `nist` catalogue,
  exact-string, walking nested (enhancement) controls. `--selfcheck` runs its own asserts plus a fixture
  (`oscal/fixtures/component-definition-unknown-control.json`, control id `zz-999`) proving an unknown
  id is a hard failure, not a hole.
  - Names both known-dangling claims today — `cm-6` claims `require-policy-version`, `ac-6` claims
    `may-run-root-if-attested`, neither policy is shipped — tags them `EXPECTED-RED`, and exits 1.
    It does not fix them: that is a separate `platform` defect (the same one map.md's *Out of scope*
    already named from the hub side). It gives that defect a red check instead of silence, and goes
    green on its own once the defect is fixed.
- `oscal/verify-claims.sh` (new) — the runnable beat: selfcheck, then the real check, printing
  `EXPECTED-RED` and still exiting non-zero while the two known claims dangle.
- `oscal/README.md` — documents the bare-id/href convention and the new beat, `EXPECTED-RED` called
  out plainly.

Verified locally: `verify-upflow.sh` passes (`3 observations, 2 findings; AC-6 not-satisfied, CM-6
satisfied`); `verify-claims.sh` exits 1, printing both known-dangling claims as `EXPECTED-RED` and
nothing else; `lint_claims.py --selfcheck` passes, including the unknown-control-id fixture.

**Outstanding.** As with ticket 09, the `platform` repo's changes above are verified locally only —
not committed there. This task's scope was the hub repo; landing the fix for real needs someone with
push access to `policy-as-versioned-platform/platform` to commit there and merge it, same open
question ticket 09 already recorded for `nist`.

No new ADR — this implements ADR-0013 (bare ids) and ADR-0017 (a claim belongs to whoever ships the
implementation) already recorded; nothing new to decide.
