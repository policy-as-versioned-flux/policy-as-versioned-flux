# 45 — Switching cost computed in composition

Type: task (AFK)
Status: resolved
Blocked by: none

> **Unblocked 2026-09-06 (record correction).** This line read `Blocked by: 15, 21, 25` until today. Tickets 15, 21, 25 resolved on 2026-08-29; nobody re-read this line, so the ticket sat behind a blocker that no longer existed. A `Blocked by:` line is a claim about another file and rots the same way a cited figure does (ticket 80).

## Question

Compute `kind: switching` in `prices[]` by re-composing with each substitutable publisher's edges dropped, annualised over the pin's life with perspective and currency; vendor priced payloads and converters under `composed/feeds/<party>/<version>/`; ship `verify/verify-portability.sh` that re-derives one adopter's prices with the publisher clone absent.

## Notes

Graduated 2026-08-28 from ticket 19's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.

## Answer

Built 2026-09-06. Branch `ticket-45-switching-cost-computed-in-composition` in the hub and in
platform. Nothing in this ticket was already built; one part of it was already RESERVED, and the
distinction matters, so it is stated first.

### What tickets 15, 21 and 25 already left standing

Read before building, and reused rather than rebuilt:

* **Ticket 21 (the feed contract).** `platform/feeds/schema.json`'s envelope, the closed parent
  kind with a free feed name, and — the load-bearing one here — `publishes[]` as the ONLY
  discovery record there is (ADR-0019 point 5). That is what makes "substitutable" a computable
  property rather than an opinion, and it is what `_feed_publishers()` reads.
* **Ticket 25 (the £ seam).** The ONE `prices[]` schema — perspective, currency, source, kind,
  amount, per-customer restatement — `_price_entry()`, and `fair.sum_prices` as the estate's one
  summing helper that refuses a list crossing a perspective or a currency. Every figure this
  ticket adds goes through both, unchanged.
* **Ticket 15 (price everything that was counted).** The regime entry partitioned into per-hole
  amounts, and the rule that a missing SIZE is a missing behaviour priced at the publisher's
  statutory cap rather than a refusal. This ticket does not revisit that; it says what follows
  from it for a switching cost (below).
* **`switching` itself was RESERVED, schema support only.** `PRICE_KINDS` has carried it since
  ticket 25 with the comment "nothing in this estate constructs an entry of those kinds yet" and
  a producer named as ticket 32 — which ticket 90 then shelved with identity. **This ticket is
  the producer.** Nothing else about it existed: no `composed/feeds/` anywhere in the estate, no
  vendoring, no portability check.
* **This week.** Ticket 89's shape is followed for a wait that is real (an outstanding thing is
  exit 3 naming the tag it waits for, never a pass), and ticket 99's rule is followed for what a
  check may read (the served artefact and the operation that reaches it, named in a table in the
  script's own header). Neither's code needed changing; ticket 99's `shift-left` fix is what makes
  the adopters' own gates green to build against.

### How the cost is computed

**Perspective and currency.** Every entry is `perspective: <the adopter>` and
`currency: <that adopter's own reporting_currency>`, constructed through `_price_entry()`, so a
switching cost is subject to the same one schema and the same one summing helper as every other
price. No sum crosses either.

**Which parents are substitutable.** A `feed`, and only a feed — because a feed is discovered
through the publisher's own `publishes[]` record and any party may publish one. `implementations`
and `controls` resolve through a Flux pin and a catalogue; dropping one is not a switch, it is
leaving the estate, and nothing here prices that. The limit is printed in the module, not implied.

**The instrument.** The whole edge set is RE-PRICED with that publisher's feed edges dropped, and
the two priceable exposures are differenced. Re-composing, not subtracting — and the estate's own
numbers show why that is not pedantry. Dropping ico costs driftwood its whole regime line,
`GBP 1,787,177.08/yr`. Dropping the THREAT publisher is not a number at all: driftwood's own
forward-intel borrows its loss-event frequency from the threat register it subscribes to, so with
that publisher gone `price_twin` refuses for want of a LEF and the composition prices nothing. A
subtraction would have printed a confident `GBP 19,558.55` and been wrong by the rest of the book.

**Annualised over the pin's life.** The amount is an annual rate, because every figure in
`prices[]` is one. `over_pin_life` carries that rate over the window the pin has actually stood —
`amount * pin_life_months / 12` — with `since`, `as_of` and `pin_life_months` printed beside it so
a reader can redo the arithmetic. Both ends are signed facts (the edge's own `since`, and
`_composition_as_of`'s newest pinned `published_at`), so this module still reads no clock (D1).

**Refusals (ADR-0020), each one named:**

1. a feed edge with no `since` — a pin's life is a window between two signed dates, and a window
   with one end is a missing instrument. Refuses, naming the party, the feed and the version;
2. no pinned feed carrying a `published_at` — no as-of to measure the window against. Refuses;
3. a counterfactual that cannot be priced at all — NOT a refusal of the composition, because the
   real composition priced fine. The entry carries no amount, no per-customer restatement, and
   the publisher's own refusal verbatim on `could_not_look`. Never a pass, never a guess. This is
   the threat-register case above, live on driftwood today;
4. two feed edges of one party at one version, which would vendor onto one another — refuses
   rather than silently overwriting a payload;
5. a vendored copy that does not match the digest the adopter's own tag signed — refuses rather
   than pricing from bytes nobody signed.

**A premium is not exposure.** Dropping the insurer moves driftwood's priceable exposure by
nothing (`0.0`), because `EXPOSURE_KINDS` deliberately excludes `premium` — folding cover into the
exposure it was priced from would make the premium an input to its own formula. The premium that
stops being computable is NAMED on `unpriceable[]` beside the figure and never added to it.

**The unsigned-size rule.** tuppence and ludlow publish no `size:` (ticket 64), so ico prices their
regime at its statutory cap. The composition does not refuse — ticket 15 already decided a missing
size is a missing behaviour — but the number it produces is a ceiling every firm in the estate
shares, so it is not a statement about either institution. The check therefore grades those lines
a NAMED could-not-look and never a pass, and it PROVES the reading rather than asserting it:

    SKIP: ludlow and tuppence publish no signed size and both price penalty-schema at exactly
    9039791.02 — the same number to the penny for two different institutions, which is what a
    statutory cap looks like and is why neither line may be read as a switching cost for either

### The tree that makes the cost payable

`composed/feeds/<party>/<version>/` carries the adopter's own copy of every payload it was priced
from, the publisher's party artefact, and the converter that priced it — each at the publisher's
OWN relative path, so `feed_file()`, `_converter()` and `pin_content` read a vendored tree with no
special case anywhere. Every file is digested into `PROVENANCE.json` and the digests ride on
`composed/HEADER.yaml`, so the adopter's own tag signs them. With a publisher's clone absent,
composition prices from that copy and names the substitution on an open `publisher-clone-absent`
limit; it is never a silent substitution.

Two facts the build turned up and wrote down rather than smoothed over:

* the threat register's publisher (`feeds`) ships **no converter of its own**. Composition falls
  back to platform's `feeds/to_fair_scenario.py`, so `feeds`' feed is priced by platform's code.
  `converter_from: platform` records it on every vendored copy.
* the insurer's quote is priced without a converter at all, so none is vendored and
  `converter: null` says so — a named absence, not an empty file pretending to be one.

### The check that grades it

`verify/portability/verify-portability.sh` (+ `portability.py`), discovered by
`talk/verify-all.sh` — 113 scripts on this branch, measured by the gate itself and never typed
into a check — with a manifest row declaring all NINE could-not-looks it can print. Its header
carries the served-artefact/operation table. It reads each adopter's own commit (`git show HEAD:`)
and each publisher's tree AT THE TAG THAT ADOPTER PINS, out of the adopter's own
`gitops/flux-system/gotk-sync-<party>.yaml`: never platform's main, never a working tree, never a
file merely existing.

Its strongest leg is an experiment rather than an assertion: the vendored converter is written into
a temporary directory holding nothing but itself and the vendored payload, with no publisher clone
and no estate reachable, and RUN. A converter that will not run there is a FAIL.

The full re-derivation runs at the seam that owns it, `platform/compose/composition.py
--selfcheck`, and this script does not restate it. That seam proves the stronger claim: with ico's
clone removed, driftwood does not merely get the same PRICES back, it re-renders all 24 files of
its composed artefact BYTE-IDENTICALLY — `composed/HEADER.yaml` and the parent SHAs included — so
an adopter can run `composition.py verify` on its own signed tree with the publisher unreachable.
That is what the provenance record's own `sha` field is for: a vendored tree is not a git
repository, and without it `_resolve_unpinned_sha` would digest the copy and every re-derivation
would disagree with the artefact it was re-deriving.

**What it says today, and why that is a wait and not a pass:** no adopter has vendored anything,
because the composition that vendors is on an unmerged platform branch and each adopter composes
against the platform version it PINS (2.0.1). So the check exits 3 and names, per edge, the amount
that cannot be re-derived and the tag the wait is on. It flips green by itself when a signed
platform tag carrying this composition exists and each adopter's pin moves to it. Committing a
`composed/` tree rendered by an untagged platform branch would be exactly the working-tree proxy the
brief forbids, so **no adopter repository is touched by this ticket**.

The figures that observation produces are new, and they are reported PER ADOPTER and never
totalled: three adopters' exposures are three balance sheets, and a sum that crosses a perspective
is the one thing the £ seam refuses. Seven feed edges, and what each adopter prices today from a
publisher whose clone it would need to re-derive any of it:

| adopter | unre-derivable, under its own perspective |
|---|---|
| driftwood | GBP 1,920,138.92/yr |
| ludlow | GBP 9,358,020.80/yr |
| tuppence | GBP 9,262,365.33/yr |

The estate had those numbers nowhere before today. (An earlier draft of this Answer quoted one
estate-wide total. That would have summed three perspectives into a figure belonging to nobody,
which `fair.sum_prices` exists to refuse; the check now prints the three separately and says why.)

### Red before green

    # platform, composition.py --selfcheck, the new section, before the build
    assert len(switching) == len(feed_edges), (len(switching), len(feed_edges))
    AssertionError: (0, 3)

    # after
    OK prices[]: one `switching` entry per feed edge, each measured by re-composing with that
    publisher's edges dropped -- ico's costs its whole regime line, the threat publisher's is not
    a number at all because driftwood's own twin borrows that feed's LEF and stops pricing
    without it, and the insurer's moves the exposure by nothing and names the premium it would
    lose instead of folding it in
    OK composed/feeds/: every priced payload, the publisher's own party artefact and the
    converter that priced it are vendored under the adopter's own signature, digested into a
    PROVENANCE.json the header names, with the converter's real source party recorded and a quote
    feed's absent converter named rather than faked
    OK portability: with ico's clone ABSENT, driftwood re-derives every price it signed and
    re-renders all 24 files of its composed artefact BYTE-IDENTICALLY -- header, parent SHAs and
    all -- from its own vendored payload and converter, printing the substitution as an open
    limit; a tampered vendored payload refuses against the digest its own tag signed
    OK switching: a feed edge carrying no `since` refuses as a missing instrument naming the edge
    -- a pin's life is a window between two signed dates, never a default

The hub check's plants each bite (`portability.py selfcheck`), including the two that matter
most: a vendored payload that has drifted from the publisher's own bytes at the pinned tag, and a
vendored file that does not match the digest its own header signed.

### Decisions

1. **A substitutable parent is a `feed`, and nothing else** (`delegated`, ADR-0025). `publishes[]`
   is the only discovery record there is, so a feed is the only parent kind whose publisher the
   estate can describe replacing. `implementations` and `controls` resolve through a Flux pin and a
   catalogue and dropping one produces no priceable delta at all, so pricing it would be modelling,
   not measuring. Printed as a limit in the module rather than left as an unstated scope.
2. **The amount is the delta in PRICEABLE EXPOSURE, measured by re-composing** (`delegated`). The
   ticket says re-compose and the estate immediately rewarded it: the threat-register
   counterfactual refuses, which no subtraction could have discovered.
3. **A counterfactual that refuses is a named could-not-look on the entry, not a refusal of the
   composition** (`delegated`, ADR-0020). The composition that really ran priced everything; it is
   the hypothetical one that could not. Refusing the real artefact because a hypothetical failed
   would have reddened three adopters over a question nobody asked them.
4. **`over_pin_life` is the rate times the window, with both ends printed** (`delegated`). "Annualised
   over the pin's life" needs a rate and a window; the amount is the rate (every figure in
   `prices[]` is annual) and `since`→`as_of` is the window, both signed, so no clock is read.
5. **A `premium` is named on `unpriceable[]`, never summed into the amount** (`delegated`). It is a
   cost, not an exposure; one array must not add them.
6. **An unsized adopter's line is priced and graded a could-not-look** (`delegated`). Ticket 15
   already decided a missing size is priced at the cap, not refused, and reversing that here would
   have made two adopters' whole composition refuse. So the composition prices (the cap is the
   publisher's own published number, never an invented one) and carries `sized: false`, and the
   GATE refuses to call the line verified. Both halves are honest and both are recorded.
7. **The vendored tree reproduces the publisher's own relative paths** (`delegated`). The
   alternative — a flat layout — needs a special case in `feed_file`, `_converter` and
   `pin_content`, and three special cases are three places for the vendored and the live read to
   drift apart. The publisher's own `party.yaml` travels with it because that is what says where
   the feed lives; a publisher that ships none is recorded as shipping none.
8. **`PROVENANCE.json`, not `.yaml`** (`delegated`). `composed/**/*.yaml` is swept by
   `composition.verify()` and by driftwood's `render_composed.py`; a `.json` name keeps a data file
   out of two globs that look for objects.
9. **The vendored SHA is the publisher's commit, read back from the provenance** (`delegated`). A
   vendored tree is not a git repository, so `_resolve_unpinned_sha` would digest the copy — and
   every re-derivation would then disagree with the artefact it is re-deriving.
10. **No adopter repository is touched** (`delegated`). Their `composed/` trees are rendered by the
    platform version they pin; regenerating them from an untagged branch is the working-tree proxy
    the brief forbids. The check names the wait by tag and flips green on its own.
11. **One existing promise is narrowed, in writing** (`delegated`). "No rendered file changes on a
    price move" becomes "no rendered POLICY file changes": a bump adds the new version's vendored
    copy and drops the old one's, which is the point of vendoring. Nothing under `composed/feeds/`
    is a Kubernetes object and no Kustomization path reaches it, so the promise that mattered — a
    tier appearing in something Kyverno reads — is untouched. `_assert_only_the_moved_feed_changed()`
    states the narrowing at the assertion rather than quietly widening the comparison.
12. **`_run_converter` gained a content-keyed cache** (`delegated`). Measuring a switching cost
    re-prices the edge set once per feed publisher, which multiplies converter subprocesses. The key
    is the converter's bytes, the payload's bytes and the arguments — never a path or a version — so
    a fixture that rewrites a payload in place under the same version is a different key and is
    really re-run. A cache keyed on the pin would have quietly answered a stale price to the very
    tests that plant a change.

### Verify commands

    # platform (worktree, PAVC_ESTATE_CLONE set to the real clone)
    .venv/bin/python compose/composition.py --selfcheck      # exit 0
    bash compose/verify-composition.sh                       # exit 3 -- and exit 3 on
      origin/main too, measured in a throwaway worktree rather than assumed: its step-2 SKIP
      ("the composed set renders policy versions the pinned parent commit does not contain")
      is the pre-existing pin/version state and nothing this ticket did

    # hub
    bash verify/portability/verify-portability.sh            # exit 3, the named wait
    .venv/bin/python verify/portability/portability.py selfcheck   # exit 0, ten plants
    bash talk/verify-all.sh --selfcheck                      # PASS
    bash verify/truth-line/verify-truth-line.sh              # PASS
    bash verify/every-green/verify-every-green.sh            # PASS, 113 scripts discovered
    .venv/bin/python -m mypy twin tests conftest.py --ignore-missing-imports --warn-unused-ignores
                                                             # Success: no issues in 177 files

**Map line:** `- [45 — Switching cost computed in composition](issues/45-switching-cost-computed-in-composition.md) — `switching` stops being a reserved schema value and becomes a measured one: one entry per feed parent, priced by RE-COMPOSING with that publisher's edges dropped rather than by subtracting the line about to be lost, under the adopter's own perspective and currency, carried over the window between the edge's signed `since` and the composition's own as-of. A counterfactual that cannot be priced is a named could-not-look with no amount — driftwood's twin borrows the threat register's LEF and stops pricing without it, which no subtraction would have found. `composed/feeds/<party>/<version>/` vendors every priced payload, its publisher's party artefact and the converter that priced it, digested onto the header the adopter's own tag signs, so an adopter can re-derive its own signed prices with the publisher's clone absent. `verify/portability/` grades the served half against each publisher's tree at the tag that adopter pins, runs the vendored converter with nothing else on disk, and reports, per adopter and never totalled, what each prices today from a publisher whose clone it would need to re-derive any of it: driftwood GBP 1,920,138.92/yr, ludlow GBP 9,358,020.80/yr, tuppence GBP 9,262,365.33/yr.`

## CI

The `truth` workflow serialises across every branch at once (`concurrency: truth-${{ github.event_name }}`),
and several builders pushed today, so **all three `truth` runs on this branch were CANCELLED, not
green** — 34041169274, 34041955787 and 34042143614, each superseded while pending. That is quoted as
what happened, not worked around: a cancelled run is not a pass and this branch has no citable
observation of its own. The build brief (2026-09-03) already records that a branch TRUTH line is
usually only in the Actions log and is not citable. The gate evidence for this ticket is therefore
the local runs listed above, each with its exit code, and the checks that grade the record
(`verify-map-surface`, `verify-cited-truth`) passing on this tree.

## Waits on the owner

1. **A signed platform release tag carrying this composition.** A signed tag cannot be cut locally
   (hard rule 3); `cut-release.yml` cuts it in Actions. Until it exists and each adopter's
   `platform-pin.yaml` moves to it, no adopter's `composed/feeds/` tree can be rendered by anything
   but a working-tree copy, and `verify/portability/` names that wait per edge, by tag.
2. **Nothing else.** Every decision above is `delegated` under ADR-0025 and recorded here rather
   than held.
