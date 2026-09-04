# 69 — An untagged pin is a priced hole

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

Ticket 58 Q5(b): an adopter's pin on an untagged feed is never refused and never free — it is a hole on the adopter's prices[] per ADR-0020's hole pricing, graded by a named check that reads the pin's signature state. First instance: driftwood's quote-driftwood v1. The hole closes itself when ticket 57 cuts the first signed quote tag. Done = the check is in the gate and driftwood's composed artefact prices the hole today.

## Notes

Graduated from ticket 58 (2026-08-31), decision provisional on a bare "Agree".

Map line: An untagged feed pin composes as a priced hole of its own premium and is graded live against the publisher's real remote — 7 of 7 estate pins signed, so the rule runs on a fixture and a scratch estate, not on a live hole.

## Answer

Built 2026-09-04. Every decision below is **delegated** (ADR-0025): none of them is money, a date,
an identity, an authorisation or a real person.

### What was built

**Hub** (branch `ticket-69-an-untagged-pin-is-a-priced-hole`):

- `verify/feed-contract/untagged_pin.py` — the grader. Walks every adopter's `inherits[]` feed pin
  in the estate, reads the pin's signature state **from the publisher's real remote** (`git
  ls-remote --tags` through `feed_contract.remote_tags`/`match_tag` for existence, then the
  platform's own identity-pinned verifier `identity/gitsign-verifier/verify_gitsign.py verify-tag`
  — the one `verify-source-verification.sh` grades — over the tag ref fetched read-only into a
  throwaway bare repo, under the **publisher's own** `release.yml` `EXPECTED_IDENTITY_REGEXP` and
  `EXPECTED_ISSUER` and the skew the verifier's own `deployment.yaml` declares), and grades it
  against the adopter's `composed/evidence.json`.
- `verify/feed-contract/verify-untagged-pin-is-priced.sh` — the named gate check. Runs the
  selfcheck first, then the live walk. Exit 0 / 3 (`SKIP:` last line) / 1 (`FAIL:` last line),
  discovered by `talk/verify-all.sh`'s `find .estate-clone verify -name 'verify*.sh'`. 10s live.
- `tests/test_untagged_pin.py` — 22 pytest cases at the pure seam (the grade and the state
  reading), plus the module's own `selfcheck` (15 planted grades, a stubbed-remote state walk, and
  a two-adopter synthetic estate where one pin is priced and one is not).
- `docs/adr/0020-*.md` — a dated note, not a new ADR number (below).

**Platform** (`.estate-clone/platform/.work/ticket-69`, branch
`ticket-69-an-untagged-pin-is-a-priced-hole` off `ecosystem/build-2026-09-03`, unpushed):
`compose/composition.py` gains `pin_signature_state()`, `untagged_pin_hole()`,
`untagged_pin_deltas()`, the `PIN_SIGNATURE_STATES` and `UNTAGGED_PIN_HOLE_KIND` constants, and
two new `DELTA_KINDS` (`new-untagged-pin`, `closed-untagged-pin`). The `premium` entry now carries
`pin_signature` and `hole`. Six selfcheck assertions cover the real signed pin, untagged, recorded,
unobserved, closed and the byte-identity of the render across all of them.

### Which checks grade it

| check | what it grades | result today |
| --- | --- | --- |
| `verify/feed-contract/verify-untagged-pin-is-priced.sh` | every adopter feed pin, live, against the publisher's real remote | PASS, 7/7 pins signed and verified, 0 untagged |
| the same script's `selfcheck` leg | all 15 grades, including every FAIL shape | ok |
| `.estate-clone/platform/compose/verify-composition.sh` (runs `composition.py --selfcheck`) | the hole itself: opened, recorded, kept open under a could-not-look, closed | PASS |
| `tests/test_untagged_pin.py` | the pure grade and the state reading | 22 passed |

### Decisions

1. **An untagged pin is a missing *behaviour*, so it is priced and never refused.** *delegated.*
   The instrument is present — the feed envelope is on the parent's disk and prices fine. What is
   absent is the publisher's signature over the pinned version, which is a behaviour the publisher
   has not performed yet. ADR-0020's line therefore prices it. This is ticket 58 Q5(b) decided, not
   recommended: under ADR-0025 the bare "Agree" of 2026-08-31 neither ratifies nor blocks, and
   "provisional" is retired.

2. **The premium edge prices the hole at the premium itself**, under the adopter's own perspective
   and currency, with a `priced_by` naming the pin. *delegated.* Three candidates were open. The
   covered exposure left uncovered is wrong: nothing about the *cover* is unproven — the quote's
   own numbers are on disk and price identically — the *purchase* is. A zero-amount recorded hole
   is wrong: it moves nothing and reads as free, which is the one thing the rule exists to prevent.
   The premium is the honest quantity: money the adopter has committed against a quote no signature
   carries. It is booked under the adopter's own perspective and reporting currency because a
   premium already is (ticket 36, ADR-0021), so the hole needs no conversion of its own.

3. **The hole is a singular `hole` object on the `premium` entry, never a `holes[]` member.**
   *delegated.* `holes[]` means "these partition their entry" — `pound_seam.py` check 4 grades that
   the regime entry's holes sum to its total. This hole is the *whole* edge, not a partition of it,
   so putting it in `holes[]` would break an invariant that is currently true. A different key
   keeps both readings honest.

4. **Signature state is read twice, at two seams, and the two claims differ.** *delegated.* The
   third open decision asked whether composition reads the remote or takes signature state as an
   input file. Neither: composition runs offline in the adopter's CI, so it reads the pinned
   parent's **checkout** tags and says only `signed` / `untagged` / `unobserved` — presence of a
   signature block, the same reading `_signed_tags` already makes of the adopter's own tags. It
   never claims a signature *verifies*. The hub check does the network and the identity-pinned
   verification. An input file was rejected: it would be an unsigned fact produced by an
   unnamed step, and the adopter's own CI has no way to grade it. Reading the remote from
   composition was rejected: it puts a network dependency inside the offline composer and makes an
   adopter's evidence unreproducible.

5. **A tag that exists but does not verify under its publisher's own pins is `untagged`.**
   *delegated.* An unverifiable signature signs nothing, so treating it as signed would let a
   forged or misattributed tag close a hole. The verifier's own three outcomes map straight onto
   the grade: `VERIFIED` → signed, `REJECTED` → untagged, `COULD-NOT-LOOK` → SKIP.

6. **Could-not-look is neither a signature nor an absence.** *delegated.* An unreachable remote, an
   absent verifier, absent identity pins or absent trust material exits **3** with `SKIP` and never
   PASSes; composition's `unobserved` keeps a recorded hole open and opens none. ADR-0020's
   refusal is for a *missing* instrument; not being able to look at one is a different fact, and
   the brief's rule ("a check that cannot look exits 3") already names it.

7. **Scope: every adopter `inherits[]` feed pin in the estate, not driftwood's quote alone.**
   *delegated.* The ticket's named first instance healed on 2026-09-01 when insurer v1.0.0 was cut
   and signed, so a driftwood-only check would grade nothing forever. `feed_contract.py` already
   iterates every pin; the general rule is the thing worth having. Seven pins are graded today
   (driftwood ×3, ludlow ×2, tuppence ×2).

8. **A separate named script, not a new branch inside `verify-feed-contract.sh`.** *delegated.* The
   ticket says "a named check", and the gate's TRUTH line counts scripts: a second grade folded
   into an existing script would be invisible in the count and would inherit that script's exit
   code. `verify-feed-contract.sh` is untouched — its "waiting for tag" SKIP still means what it
   meant, and this check now grades the same fact for money rather than skipping it.

9. **Absence is not a pass.** *delegated.* An estate walk that observes **zero** adopter feed pins
   emits `FAIL`, not a silent 0. A check that grades nothing and exits green is the failure mode
   the gate exists to catch.

10. **Done, restated.** *delegated.* The ticket's literal done clause — "driftwood's composed
    artefact prices the hole today" — became unobservable on 2026-09-01, before this build started,
    because the tag it waited for landed. Done is now: the rule exists in composition, the named
    check is in the gate, both legs of the grade are proven on real files (a fixture in the
    composer, a scratch estate end to end), and the live estate reports zero untagged pins. That
    is a self-healing rule doing exactly what it promised, not an unbuilt one.

11. **The hole's own lifecycle mirrors a control hole's.** *delegated.* `new` on first sight,
    `recorded` once a signed artefact carried it, `closed` when a signed tag now carries the pin,
    absent thereafter — with a `new-untagged-pin` / `closed-untagged-pin` delta on the moves and
    silence in between. It is the shape ticket 38 gave every other hole, so nothing new has to be
    learned to read it, and re-composition alone closes it with no edit.

### Proven, not asserted

The live estate has no untagged pin, so both non-trivial legs were proven against real files
rather than claimed:

- **In the composer** (`composition.py --selfcheck`): the real insurer tree, copied to a scratch
  directory with `git init` and **no tag**, is the untagged case. Nothing in the fixture claims a
  signature; the only signed tag ever read is the insurer's real one. The rendered artefact is
  byte-identical across untagged, recorded and closed — signature state lives in the evidence,
  never in the render.
- **End to end in a scratch estate** (`PAVC_ESTATE_CLONE`, a copy — the real clones' `composed/`
  trees were not regenerated and driftwood's was not touched): the insurer gains a
  `quote/driftwood/v2/feed.json` and driftwood pins `@v2`, a version no tag on the **real** insurer
  remote carries. The check FAILs (`the premium entry carries no open hole`); composing driftwood
  with the ticket-69 composer prices the hole; the check then PASSes with `1 untagged pin(s)
  priced`. Moving the platform's verifier aside makes every signed pin `SKIP` and the script exit
  3. Red, green and could-not-look, all observed.

### Recorded where

`docs/adr/0020-*.md` carries a dated note (2026-09-04, ticket 69, delegated under ADR-0025) rather
than a new ADR number: the rule is a *consequence* of ADR-0020's own missing-behaviour line applied
to one more kind of absence, exactly as ADR-0026 applied it to the hole-shaped refusals. A new
number would imply a new principle where there is none.

### For the integrator

The platform branch `ticket-69-an-untagged-pin-is-a-priced-hole` merges into
`ecosystem/build-2026-09-03` **before or with** the hub pull request: the hub check's untagged leg
grades a `hole` object that only the ticket-69 composer writes. The signed leg — the one the live
estate exercises today — passes either way, so the hub PR is not wedged if the order slips.

Contained for tickets 62 and 77: `feed_contract.py` is unmodified (imported, not edited), and the
composition.py change is additive — three new functions, two new delta kinds, two new keys on the
`premium` entry, one new argument on `price_quote`. No existing branch was rewritten.

## Waits on the owner

1. **Push of `compose/composition.py` to `policy-as-versioned-platform`.** Enactment repo; the
   guard refuses agent pushes. Committed locally on the branch above.
2. **Re-composition and push of the adopters' `composed/` trees.** Until the owner pushes a
   platform tag carrying this composer and the adopters re-compose against it, no live
   `evidence.json` carries `pin_signature`. Nothing fails meanwhile: every live pin is signed, and
   the check's signed leg needs no field from the evidence.
3. **Any signed tag** on insurer, platform or driftwood — cut only by `cut-release.yml` dispatched
   by the owner. No agent fakes one, including in a fixture.
4. Optional: **a reason on ticket 58 Q5(b)**, if the owner wants the rule ratified in their own
   words rather than recorded as delegated. It changes nothing built.
