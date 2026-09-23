# 128 — Being behind a major the checkout cannot read costs nothing

Type: task
Status: open
Blocked by: none

## Question

Charted 2026-09-23 by the integrator. No open ticket owns this red. Ticket 84 (resolved) owns
the composer rule, and its dated correction of 2026-09-23 records the defect. Ticket 110 measured
it.

`verify/supersede/verify-supersede.sh` FAILs with four lines on run 296. driftwood, ludlow and
tuppence pin `ico/penalty-schema@v3` behind `v4.0.0`, tagged 2026-09-10. driftwood also pins
`feeds/threat-register@v2` behind `threat-register/v3.0.0`. None of the four carries a supersede
line in its served evidence.

The cause, measured by ticket 110: each feed entry records `superseded.state: unobserved`,
because the publisher checkout at the adopter's pin has no directory for the newer major, so
`newest_published_major()` writes no line. The composer does not read the publisher's tags, so
being behind is free again. Ticket 84's review said being behind must never be free.

What this ticket owes, in platform `compose/composition.py`:

1. A newer major that is tagged on the publisher's real remote prices the pinned line, even when
   the pinned checkout has no directory for it. Ticket 110's portability rule still holds: the
   observation is recorded in the vendored `PROVENANCE.json` and replayed offline.
2. A red-first test at the `compose()` seam, and a selfcheck case.
3. The hub's `verify-supersede.sh` reads the new lines. Ticket 127 must grade the new
   `kind: supersede` ico prices correctly, so land 127 first or together.

## Done

Composing each adopter under the new composer writes a supersede line for each of the four pins,
the offline replay is byte-identical, and the hub check passes once the adopters recompose under
a platform tools release that carries this change.

## Build, 2026-09-22

The heading names the build wave the integrator opened on 2026-09-22. Every measurement below
was taken on 2026-09-23.

### What was built

- **Platform, `compose/composition.py`.** When no signed major ahead has a directory in the
  pinned checkout, `newest_published_major()` now returns `behind`. It no longer returns
  `unobserved`. The target is the newest signed tag ahead, marked `readable: false` with
  `published_at: null`. `since` is still the oldest signed major's cut day (ticket 84 review F3).
  `price_supersede()` prices the line and adds a limit naming the unread tag. The observation is
  recorded in the vendored `PROVENANCE.json` exactly as ticket 110 built it, so the offline replay
  is unchanged. Replay refuses a target that says `readable` but not `false`, or one that carries
  a `published_at`.
- **Platform, `wargamer/wargamer.py`.** A line with an unreadable target is priced and not
  proposed as a retirement.
- **Platform, `compose/handbook.py`.** Several supersede limits are joined with "; ".
- **Hub, `verify/supersede/supersede.py`.** The check now reads the new field. A line with
  `readable: false` must name the newest signed tag on the remote and carry no `published_at`.
  A missing line under a composer that predates ticket 128 is still a FAIL. Its message now says
  so and names what lifts it. The check reads which rule applies from the composer at the
  adopter's compiler pin tag (token `"readable": False`).

### Decisions (delegated, ADR-0025)

1. **Price from the tags, do not fetch the newer directory.** The ramp needs only the tag days
   and the pinned line's own amount. Reading the newer major's content would need a second
   checkout of the publisher at another commit, and nothing in the line uses it. Reason: the
   smallest change that makes being behind cost something, and it keeps ticket 110's replay
   untouched.
2. **The target is the newest signed tag, and it says it was unread.** With no directory to
   prefer, the newest tag is the honest "what the publisher now signs". The `readable: false`
   flag stops any reader from taking `newer.version` as content this checkout read. Readable
   targets carry no flag, so every line that already existed keeps its exact bytes.
3. **No retirement to an unreadable target.** Moving `party.yaml` to `v4` without moving
   `gitops/flux-system/gotk-sync-ico.yaml` would not compose, so the proposal would be red on
   arrival. The pin bump is Renovate's job. After it, the next composition names a readable
   target and the retirement follows.
4. **The hub stays red until the adopters recompose.** A composer that predates this rule is not
   downgraded to a SKIP. Ticket 110 decided that a false SKIP is worse than a true FAIL, and the
   served artefacts still price being behind at nothing. The FAIL message now names the missing
   release and the pin move.
5. **Zero lines stay zero.** The served artefacts' `as_of` is 2026-08-28, before both tag days,
   so the new lines read 0.00 with both dates printed. That is ticket 84 review F2's rule. Only
   the clock's `--as-of` recomposition grows them.

### Tests run

- Platform `compose/test_portable_observations.py` (`python3 -m unittest`, with
  `core.hooksPath=/dev/null` set through `GIT_CONFIG_*` for the fixture repositories): two new
  cases. On main one failed (`'unobserved' != 'behind'`) and one errored (`TypeError`, because
  the target was `None`). On this branch all 8 tests pass.
- Platform `composition.py --selfcheck`, run with `PAVC_ESTATE_CLONE` set to a scratch estate of
  detached worktrees at the adopters' pins, and platform set to this branch: rc 0, 102 `OK`
  lines. The flipped "nothing readable" case is red on main. There, `newest_published_major`
  returned `(None, {'state': 'unobserved', ...})` for the same fixture.
- Platform `wargamer.py selfcheck`: rc 0. With the skip removed, it fails with `AssertionError:
  an unreadable target is priced but not proposed`.
- Platform `compose/verify-composition.sh`: rc 3. The unittest steps ran 8, 9, 13 and 16 tests,
  all OK. Step 2 is the existing SKIP (`platform@2.0.1 (533dccb0) does not contain
  distribution/policies/v5.0.0`), unchanged from ticket 110.
- Platform `handbook.py --selfcheck`: 47 checks PASS. `tier_pr.py selfcheck`: rc 0.
- Hub `supersede.py selfcheck`: red first (`TypeError: grade_behind() got an unexpected keyword
  argument 'unreadable_rule'`), then `OK 30 planted grades bite` (25 before).
- Hub `verify/supersede/verify-supersede.sh` against `.estate-clone`: rc 1, 4 FAIL, 3 PASS. They
  are the same four pins as before. Each FAIL now says the pinned composer (v3.0.0) predates
  ticket 128.
- Hub mypy (`twin tests conftest.py`): `Success: no issues found in 199 source files`. mypy on
  `verify/supersede/supersede.py`: no issues.

### Recompose, measured

Each adopter came from a detached `origin/main` worktree: driftwood `01210a7`, ludlow `f299fd1`,
tuppence `79603fd`. The parents came from detached worktrees at the commits their pins name:
platform `533dccb`, nist `33a05df`, ico `9d09222`, feeds `69c89b0`, insurer `632db22`. Each
adopter was composed twice, once with platform main `13f6b22` and once with this branch. The
two `composed/` trees were compared file by file and price by price.

| adopter | new `supersede` price | target | since | as_of | amount |
| --- | --- | --- | --- | --- | --- |
| driftwood | `ico/penalty-schema@v3` | `v4.0.0` (unread) | 2026-09-10 | 2026-08-28 | 0.00 GBP |
| driftwood | `feeds/threat-register@v2` | `threat-register/v3.0.0` (unread) | 2026-09-10 | 2026-08-28 | 0.00 GBP |
| ludlow | `ico/penalty-schema@v3` | `v4.0.0` (unread) | 2026-09-10 | 2026-08-28 | 0.00 GBP |
| tuppence | `ico/penalty-schema@v3` | `v4.0.0` (unread) | 2026-09-10 | 2026-08-28 | 0.00 GBP |

- No other price changes and no delta changes. The deltas are identical to main's. tuppence
  carries one delta that its served evidence does not, the ungoverned `openbao` ramp. Main's
  composer writes it too, so it comes from tickets 119 to 126 and not from this one.
- Price counts go from 7 to 9 (driftwood) and from 5 to 6 (ludlow, tuppence). Each new line sits
  after its feed line, so later indices shift. Ticket 127 names four prices by index. After
  recompose, driftwood's `prices[4]` and `prices[5]` become `prices[6]` and `prices[7]`, and
  ludlow's and tuppence's `prices[3]` becomes `prices[4]`.
- The files that change are `evidence.json`, `HANDBOOK.md`, `HEADER.yaml` (the
  `comparison-inputs.after` digest) and each affected `PROVENANCE.json`. The observation moves
  from `unobserved` with `newer: null` to `behind` with the unread target.
- **Offline replay.** With ico absent, and again with feeds absent, every rendered file is
  byte-identical to the composition with every clone present. Only `evidence.json` differs, and
  as data only in `limits`: the `publisher-clone-absent` limit opens. That is ticket 110's
  recorded disclosure. `prices` are equal as data. `composition.py verify` exits 0 for all three
  with every clone present, with ico absent and with feeds absent.
- **As the clock will see it.** Composed with `--as-of 2026-09-23`: driftwood ico 63,652.88 GBP
  and threat-register 696.61 GBP (ramp 1.035616), ludlow ico 321,965.16 GBP, tuppence ico
  321,965.16 GBP.
- **The hub check on the recomposed evidence.** I loaded `supersede.py`, pointed
  `served_json` at the recomposed files and set both composer-rule reads to true. `check()`
  then graded 7 PASS and 0 FAIL on the branch's own output, and 7 PASS and 0 FAIL on the
  `--as-of 2026-09-23` output. Tags were read from the real remotes.

### What remains, and who does it

- **Owner:** cut a platform tools release carrying platform PR 37. Its version is the owner's
  call. No release workflow was dispatched here.
- **Then, per adopter (an ordinary reviewed PR):** move `.github/platform-tools-pin.yaml` to that
  release, recompose with the publishers present, and merge. The hub check then passes, as
  measured above against scratch recompositions. No adopter PR is opened here, because no
  release exists to pin.
- **Ticket 127 first.** After recompose, each adopter's evidence carries an ico
  `kind: supersede` price. Ticket 127 must land first, so `pound_seam.py` grades that price by
  kind and not as a regime entry. `pound_seam.py` was not touched here.
- **Noticed, not fixed.** `composition.py --selfcheck` fails its path-leak assertion when the
  estate directory holds symlinks to the unit trees. `_portable_reason` resolves the tree paths,
  and the refusal text carries the unresolved path. The selfcheck passed with real
  directories. Real estates use real directories, so this is recorded and not built.

### PRs

- platform: `ticket-128-behind-a-major-unreadable`,
  https://github.com/policy-as-versioned-platform/platform/pull/37
- hub: `ticket-128-behind-a-major-unreadable`, this record and the supersede check.

Merge order: platform first, then the hub. The hub change is safe either way. It grades today's
served evidence as it did before, with a sharper FAIL message. Merging platform first keeps the
record true: the token the hub looks for exists in platform main before the hub names it.

Map line: `- [128 — Being behind a major the checkout cannot read costs nothing](issues/128-being-behind-a-major-the-checkout-cannot-read-costs-nothing.md) — open, built 2026-09-23 in platform PR 37 and a hub PR. The composer prices a pin behind a signed major its pinned checkout cannot read, from the tags alone, marked readable: false; the offline replay is byte-identical. Recomposed in scratch, all four pins carry a line (0.00 GBP at as_of 2026-08-28) and the hub check grades 7 PASS. Waits on the owner's platform tools release, then each adopter's compiler pin move and recompose, with ticket 127 landed first.`
