# Scope, coherence, and the ambition itself — assessment 2026-09-02

Auditor dimension: is NORTH-STAR coherent and achievable; is the estate the right size for its
purpose; what is load-bearing and what is ballast; is the destination reachable at current cadence.

Citable base: `TRUTH 2026-09-02T10:11Z run=21 hub=7b92990 ... pass=57 fail=7 skip=18 excluded=2
total=84` (`talk/truth.log`, on `origin/main`). Run-21 grades read from
`scratchpad/review/run21-grades.txt` and cross-checked against `origin/main:talk/captures/*.out`.
Unit trees read at the fresh default-branch clones matching run 21's SHAs. Every arithmetic claim
below is re-derivable from files named with paths.

---

## 1. Is the ambition coherent?

**Mostly yes, and much more so than the map's own vocabulary suggests.** Four of the six
"contradictions" I was asked to probe are not contradictions when tested against code:

| Probe | Verdict |
|---|---|
| ADR-0006 "no time conditions" vs as-of pricing | **Not a contradiction.** `compose/composition.py` is provably clock-free: its own selfcheck asserts the module cannot even *import* `datetime`/`time`/`sched`/`croniter` (composition.py:3566-3571), and every `as_of` comes from the feed envelope, never the wall clock (`_feed_as_of`, line 1412). ADR-0006's line ("a date may nudge a human, never change a verdict") holds in the shipped code. |
| "Nothing is refused" vs instrument faults / the publisher gate | **Not a contradiction — it is a recorded, bounded exception.** REGRILL 11 says "publish at a degraded (quarantined) tier instead of refusing. Instrument faults still refuse", and the degraded path is *built*: `computed-semver/gate.py:82 DEGRADED_TIER = "quarantine"`, `cut-release-gate.py:153 degraded_tag()` emits `policy/v4.0.1-quarantine.1`, and `gate.py:256-264` explicitly records `degraded` rather than refusing when the gate could read everything it needed. |
| "No gate" vs adopter-gate / publisher-gate scripts | **Vocabulary collision, not a rule conflict.** Principle 2's "there is no gate" is about *runtime admission of a workload*; NORTH-STAR §2 itself lists "the composition and release gates" as things the platform publishes. The publisher gate refuses only instrument faults; a weak declaration publishes degraded. The word is overloaded, not the rule. |
| Rejection ledger vs "never an exemption ledger" | **Not an exemption ledger.** `wargamer/rejection_ledger.py` derives suppression from closed-unmerged PRs at run time — there is no committed register — and a different curve hash or £ is a *new question* that is not suppressed. Offline the ledger is empty and the caller is told so. This is well designed. (One real problem with it survives: see F7.) |

Two of the probed tensions are real and are treated below: the retired 2.x/3.x lines against the
thesis's ≥3-coexisting-versions requirement (F9), and sunset-vs-supersede (F3).

**Where NORTH-STAR is genuinely incoherent is not in its rules — it is between its rules and its
arithmetic.** Principle 3 says the £ makes a cage tier, a control purchase and an insurance
transfer comparable, and §4 step 3 makes the £ crossing a band the pivot of the whole
demonstration. On the estate's own real, signed numbers the £ has no bands left to cross: every
adopter is already at the bottom rung, and two of three are past the end of the ladder entirely.
That is F1 and F2, and it is the single most consequential thing in this review.

---

## 2. Findings

### F1 (critical) — The cage ladder is saturated: §4 step 3 cannot occur

Read the three adopters' own signed composed artefacts and the platform's own cage table:

- `platform/graded/cage.py:82-127` — `TIERS` reduce factors: baseline 0.30, restricted 0.70,
  quarantine 0.92, isolated 0.98; `ORDER = ["baseline","restricted","quarantine","isolated"]`;
  `caged_residual = uncaged * (1 - reduce)`; `select_tier` picks the loosest tier whose caged
  residual is `<= tolerance` and falls closed to `isolated`.
- `driftwood/selection-policy/selection_policy.py:11-16,52-97` — the adopter's own signed
  selection package implements the same rule and states the fail-closed default explicitly.

Applying that table to the real `composed/evidence.json` amounts and the real signed
`party.yaml` `appetite.tolerance` (driftwood 40,000 GBP; tuppence 15,000; ludlow 5,000):

| adopter | price line | uncaged GBP | baseline | restricted | quarantine | isolated | fits |
|---|---|---:|---:|---:|---:|---:|---|
| driftwood | penalty-schema | 1,787,177 | 1,251,024 | 536,153 | 142,974 | **35,744** | isolated only |
| driftwood | forward-intel (twin) | 1,897,646 | 1,328,352 | 569,294 | 151,812 | **37,953** | isolated only |
| driftwood | threat-register | 19,559 | 13,691 | 5,868 | 1,565 | 391 | all four |
| tuppence | penalty-schema | 9,039,791 | 6,327,854 | 2,711,937 | 723,183 | 180,796 | **none** |
| tuppence | threat-register | 222,574 | 155,802 | 66,772 | 17,806 | 4,451 | isolated only |
| ludlow | penalty-schema | 9,039,791 | — | — | — | 180,796 | **none** |
| ludlow | threat-register | 318,230 | 222,761 | 95,469 | 25,458 | 6,365 | **none** |

All three governed Namespaces already declare the floor:
`driftwood/gitops/apps/namespace.yaml:30`, `tuppence/gitops/apps/namespace.yaml:28`,
`ludlow/gitops/apps/namespace.yaml:28` — all `posture.acme.io/tier: "isolated"`.

Consequences, each falsifiable:

1. **§4 step 3 ("the £ crosses a band, the cage tier moves") has no reachable move.** To lift
   driftwood off `isolated` its largest uncaged line must fall below `40,000 / 0.08 = 500,000`
   GBP — a 74% fall. Ticket 74 names three movers: a feed bump (which raises the number — the
   real ticket-61 bump moved tuppence 222,574 → 326,139 and the capture itself records
   "tier isolated -> isolated, changed=False", `talk/captures/verify_e2e_verify-e2e-step2-*.out`),
   the EOL ramp (which does not exist as a path — F3), and a hand edit to `party.yaml` (which
   ticket 74 itself forbids: "Do not manufacture a crossing"). No clock-driven mover can fire
   step 3.
2. **For tuppence and ludlow the selection is not a selection.** No rung of the four brings the
   penalty line under tolerance, so `select` returns the fail-closed default. A four-rung ladder
   with one reachable rung and, for two parties, zero, is not a graded response — it is a
   constant.
3. **§4 step 4's own sentence is contradicted by the state.** Step 4 reads "the workload keeps
   running, caged tighter." `isolated` is defined (`graded/cage.py:105-111`) as quarantine's dials
   plus **no ingress, no egress, first eviction** — the estate's own words for "too expensive to
   run or not functional". Every adopter's workload is already there.
4. **Driftwood's margins are 12% and 5%.** 35,744 and 37,953 against a 40,000 band. Any further
   price movement pushes driftwood off the end too, and the only mechanical movement the estate
   has is upward.

**Ownership: none.** Ticket 74 assumes the crossing will arrive; nothing owns the calibration.
REVIEW-2026-08-31 did not find this (its M9 says step 3's *mechanism* is red, not that the
*arithmetic* forecloses it).

### F2 (critical) — "Proportionate to the org" does not operate for two of three adopters

`grep -c '^size:'` over the three `party.yaml` files returns 1, 0, 0. Only driftwood declares
`size` (`driftwood/party.yaml:33-38`: turnover 86,000,000 GBP, 240,000 customers, as_of
2026-06-30). Ticket 07's decision, recorded in map.md:32, is "stale size widens to the cap, never
refuses" — and the cap is what tuppence and ludlow get: an identical **9,039,791 GBP** each,
41 times driftwood's own priced 1,787,177 for the same regime at the same pinned ico v3.

So principle 3 ("The price is proportionate to the organisation: its turnover, its customers, its
regulators, its declared appetite") is inert for two of the three parties whose whole purpose per
§1 is "to demonstrate the whole eco-system operating"; and the widen-to-cap fallback is precisely
what pushes both off the end of the ladder in F1. Every `per_customer` field in their
`prices[]` is `null` for the same reason.

Nothing refuses, nothing warns, and no check grades the absence: the estate treats a missing size
as a priced widening, which is architecturally right and operationally fatal to the demonstration.
No ticket owns adding `size` to tuppence and ludlow.

### F3 (major) — The decided supersede mechanism (the EOL ramp) has no consumer path

Ticket 13 D5 (`map.md:40`) and ticket 19 D5 (`map.md:45`) both decide that supersede is
publisher-side only and **priced by the EOL ramp**, replacing ADR-0010's sunset cron. Ticket 74
names the ramp as one of the three movers that could fire step 3.

The ramp exists (`platform/feeds/to_fair_scenario.py:74-101`, `eol_ramp(eol_date, as_of)`, +1x per
year past EOL) and it is unreachable:

- `platform/compose/composition.py:272-275` — `FEED_CONVERTERS` has exactly two rows
  (`threat-register`, `penalty-schema`) plus the `quote-` prefix at line 300. There is no `eol` row.
- `composition.py:3560-3561` states it plainly: "an 'eol' parent kind does not exist in the party
  artefact schema at all."
- No adopter subscribes: `grep -n 'eol' {driftwood,tuppence,ludlow}/party.yaml` returns nothing,
  though `feeds/party.yaml:23-27` really does publish an `eol` feed.
- The ramp only moves when a caller passes `--as-of`; nothing on any clock calls it.

So ADR-0010's sunset mechanism is superseded on paper by a mechanism with no wiring, ADR-0010
still carries no superseded banner, and ticket 74's plan rests partly on it. Every ticket naming
the ramp is resolved. **Orphan.**

### F4 (major) — The estate's central runtime claim is outside the only instrument it may cite

NORTH-STAR §5: "One command, on a schedule, in CI, is the **only** source any document may cite for
'what works'." The 2026-08-29 build decision (map.md:78-79) adds: "A hand-taken sample is a
rehearsal and is never cited."

`.github/workflows/truth.yml` installs kyverno, cosign, gitsign and flux CLIs (lines 78-91) and
**never creates a cluster** — `grep -n "kind\|cluster" .github/workflows/truth.yml` returns only
those two CLI lines. Consequently 11 of the 84 checks SKIP every run on "kind cluster 'driftwood'
is not listed by kind get clusters": `access`, `currency-controller`,
`distribution/declared-versions-admit`, `engine`, `eud`, `graded`, `identity/federation`,
`identity/identity`, `posture/posture-projection`, `verify-source-verification`, and
`tuppence/reset/verify-reach-secrets`.

Those eleven are exactly the checks that would observe principle 2 (a workload, a human, a device
each in a cage) and §4 step 4 in force. The estate's design answer for step 4 — ticket 16 D1's
adopter-side ephemeral-KinD sample lane — genuinely works and is now graded (the three
`verify-reconcile.sh` FAILs in run 21 are real observations). But no sample lane exists for the
eleven platform live tails.

Net: **no document may honestly cite that the cages work at runtime**, because the only permitted
instrument structurally cannot look, and the rule forbids citing the local runs that can. Every
ticket that named the live-tail problem (03, 16, 20, 52) is resolved. **Orphan.**

### F5 (major) — The provenance check reports two real signed tags as "no signed tag yet"

`verify/e2e/verify-e2e-step6-provenance.sh:87` selects a publisher's tag with

```
tag="$(git -C "$ESTATE/$u" tag -l 'v*.*.*' 2>/dev/null | sort -V | tail -1)"
[ -n "$tag" ] || { queued+=("$u"); continue; }
```

`feeds`'s real tags are `threat-register/v1.0.0` and `threat-register/v2.0.0`
(`git tag -l` in the fresh clone at 69c89b0; both verify with gitsign against Rekor per the
publishers map). The glob `v*.*.*` does not match them, so feeds is put in `queued` and printed
as a green note:

```
ok   no signed tag yet, honestly queued for cut-release.yml: feeds
PASS: ... and feeds have no signed tag yet
```
(`origin/main:talk/captures/verify_e2e_verify-e2e-step6-provenance.out`)

This is a false negative dressed as honesty, and the deck narrates it. It is *new since* ticket 57
cut those tags on 2026-09-01 — REVIEW-2026-08-31's M1 correctly said feeds had zero tags at the
time. Nothing owns it: ticket 57 is about registration and dispatch, not the provenance check.

### F6 (major) — Two tag-naming schemes coexist and the estate models one

- `feeds` uses per-feed tags (`threat-register/v1.0.0`), and must: it publishes six feeds
  (`feeds/party.yaml:12-27` plus fx/market-moves/news).
- `insurer` *declares* per-feed tags — `insurer/quote/driftwood/bump.yaml` says "cut-release.yml
  signs the tag `quote-driftwood/vX.Y.Z`" — but its one real tag is repo-level `v1.0.0`, and
  ticket 57's own checklist step 4 records the divergence as deliberate ("insurer (version HAS a
  leading v — the two workflows differ)").
- `platform` runs two lines at once (`policy/vX.Y.Z` and bare `vX.Y.Z`), handled specially by
  `cut-release-gate.py:16-23`.
- The cross-cutting checks assume one scheme (F5).

REGRILL 2 / ticket 06 chose the ESLint model: "every package carries its own semver; a composed
set that extends others is a new package." insurer holds three packages
(`quote-driftwood|tuppence|ludlow`) with three separate `bump.yaml` files under **one** repo tag,
so a re-quote for driftwood renumbers the artefact that tuppence and ludlow pin. That is the
opposite of the decided model, and it will bite the first time the insurer re-quotes — which its
daily clock is already trying to do and failing (publishers map, insurer requote runs
33496526156 and 33615860064, all three jobs failing both days).

### F7 (major) — A platform-held knob silences an adopter's own priced proposal

`platform/wargamer/rejection-decay.yaml` (`version: 1.0.0`, `half_life_days: 30`,
`reject_suppress: 0.5`, `tuned_against: "not yet tuned against real closes"`), loaded by
`rejection_ledger.py:45 CALIBRATION = HERE / "rejection-decay.yaml"` with no per-party override
path anywhere in the module.

Its own comment states the effect: "two closes a week apart hold the key quiet for about eight
weeks." Since the estate proposes-never-disposes and a human merges, suppressing the proposal
means the cage does not tighten. So an untuned fixture held in *another party's repository*
decides, for up to two months, whether an adopter's priced move reaches a human.

This is the exact shape ADR-0021 retired for appetite — `risk/appetite.json` is gone and
`enforce.py`'s selfcheck now asserts the file does not exist, because "whose money is at risk is
the party's own signed fact" (`driftwood/party.yaml:39-42`). The same migration was not applied to
the forgetting curve. It also cuts against §2's "Nothing in the eco-system is a tenant of anything
else" and REGRILL 33's "no perspective privileged". **Orphan.**

(To be fair to it: the price still lands in `evidence.json` and on the balance sheet, so the risk
stays disclosed. This is a tenancy defect, not a hidden exemption.)

### F8 (major) — The one interim rule the owner named for AI disposal is unbuilt and unowned

REGRILL 29 (`REGRILL-ANSWERS.md:35`): "author and merger must be different identities for now; the
end state is an AI allowed to dispose inside a priced cage (see 37)." REGRILL 37: "The twin acts
inside a priced cage; propose-only is the outermost setting."

Verified live, read-only, today:

- `gh api repos/policy-as-versioned-driftwood/driftwood/rulesets` → `0`;
  `.../branches/main/protection` → 404 "Branch not protected" on the hub. Zero rules across all
  nine repos (github-live map; two spot-checked by me).
- `gh pr list --repo policy-as-versioned-driftwood/driftwood --state merged` — PRs 22, 21, 20, 19,
  18, 16, 15, 14, 12, 11 are all `author=chrisns mergedBy=chrisns`.
- Even the flagship step-2 event is not an exception: PR #20's *commit* is
  `github-actions[bot]` on branch `renovate/feeds-threat-register-2.x`, but the PR author and the
  merger are both `chrisns`.
- The propose-only guard is a toggle the agent holds: `twin/ENACT_MODE` was flipped
  `operations`→`development`→`operations` **eight times in two days** by the assistant itself
  (hub commits fd9b779, a79261b, 7ee4f4f, bba9ec5, c40887c, 245e5b4, c82dec1, e7981a5).

The flips are honestly committed and grep-able, which is a real strength — but a guard whose key
is held by the guarded party is disclosure, not a cage. And on the estate's own doctrine a cage has
a **price**; `ENACT_MODE` has none. Nothing in the 74-ticket set builds the priced cage on the
agent that REGRILL 29/37 points at. **Orphan.**

### F9 (major) — The thesis's own runtime requirement is at one version, structurally

`research/03-blogs-thesis.md:40-41`: "The runtime must support multiple policy versions
simultaneously — **at least three semver versions** — to allow transitionary periods for old
policy versions to be retired." The mea culpa revises neither this nor the seven -ables
(research/03 §4, §7). `docs/PRD.md:31` says the build honours the revised thesis.

`platform/distribution/versions.yaml:77` declares exactly one element: `4.0.0`. The reasoning
recorded above it (lines 31-59) is excellent and honest — two independently observed live defects,
and the finding that teaching an old line to read `namespaceObject` *is* ADR-0022, which the engine
classifies major, so it cannot ride on a patch. But that reasoning generalises: **if every
substantive policy change computes major, an old line can never be patched, and "older lines are
patchable" (NORTH-STAR §3 principle 4) is unreachable by construction.** The estate proved this
once and recorded it as a one-off.

The cost is visible in the number: four run-21 SKIPs trace to it —
`verify-coexistence` ("declares one version (4.0.0); coexistence needs two"),
`verify-retirement` ("would leave an empty allow-list"),
`verify-shift-left` ("one major line, so a target has no ±1 neighbour"), and
`policy/verify-conditional` ("the root-attested conditional branch lives only in
require-nonroot-2-0-1, and 2.0.1 is retired").

Partly owned: ticket 58's decision graduates a *second* line (5.0.0) into ticket 63, and ticket 71
owns the kyverno-version question. Unowned: the structural claim that the estate cannot reach
three, and cannot demonstrate an *old* line in transition at all.

### F10 (major) — A retirement decision that changed nothing, asserted as done

Ticket 13 (resolved 2026-08-28) decides "currency-controller retired ... it 404s and ticket 07's
fx feed replaces it" (`map.md:40`), and `map.md:113` states flatly "The currency controller is
retired (ticket 13)."

At run-21's platform SHA (46cd775) the module is entirely present: `currency-controller/currency.py`,
`manifests/`, `up.sh`, `verify-currency.sh`, and a `README.md` whose first lines still claim it
live ("This closes the single biggest gap research 16 flagged"). 416 lines of code plus a CronJob
manifest. `verify-currency.sh` is still discovered by the gate and SKIPs in run 21.

`grep -l currency-controller` over `.scratch/ecosystem/issues/` returns only tickets 10, 12 and 13
— all resolved. **Orphan**, and the map asserts the opposite.

### F11 (major) — The estate's weight is on the platform's internals, not on the eco-system

From `run21-grades.txt` (84 lines):

- 45 of 84 checks (54%) are `platform`'s own.
- The three adopters — the parties §1 says "demonstrate the whole eco-system operating" — carry
  11 between them (driftwood 4, tuppence 4, ludlow 3).
- The four publishers carry 12; the hub's cross-cutting `verify/` + `talk/` carry 16.

Code follows the same shape. Hand-written lines (`.py` + `.sh`, `find … | wc -l`):
platform 25,163; hub `twin/` 33,872 plus `tests/` 18,623; hub `verify/`+`talk/` 5,418;
driftwood 3,905, tuppence 3,682, ludlow 3,136; feeds 1,699, ico 718, insurer 915, nist 518.
Total ≈ 97,600 lines, of which the twin and its tests are **52,495 (54%)** and serve one of seven
§4 steps — step 5, whose gate check
(`verify/e2e/verify-e2e-step5-twin-forecasts.sh:38-43`) grades **file presence** plus the twin's
own evals.

This is not an argument that the twin is worthless — its forward-intel really does reach
driftwood's priced evidence (see Strengths). It is an argument that the instrument's attention and
the codebase's mass both sit where the ambition does not.

### F12 (minor) — NORTH-STAR's own factual rows are stale, and nothing owns them

- §2, "Intelligence publisher … *Does not exist yet.* Today the platform publishes four of five
  feeds to itself" — false since 2026-08-31: the `feeds` org exists, publishes six feeds, and has
  two gitsign-signed tags.
- §2, "Insurer or counterparty … *Does not exist yet.*" — false: `insurer` exists, is tagged
  `v1.0.0`, and its `quote-driftwood` premium (113,403 GBP) is a live line in driftwood's
  `composed/evidence.json`.
- §4:50, "None of steps 1 to 5 runs end to end today" — steps 1 and 2 now do, for real.

NORTH-STAR is the one document everything cites and §7 rightly forbids rewriting history — a dated
update line is the estate's own convention and it has not been added. Ticket 67 ("the record
matches the surface") scopes only the map, the two NORTH-STAR *copies*' disagreement, ico's
bump.yaml, and the lane paths. The stale §2/§4 facts are **unowned**.

### F13 (minor) — "Semver computed, never declared" has a disclosed structural hole

`platform/computed-semver/rederive_bumps.py:281-284`, printed on every run:

> "Minor cannot be rederived from bare admission pass/fail alone: a brand-new Audit policy produces
> ZERO admitted/refused transitions for any fixture by construction (Audit never refuses), so there
> is no verdict movement to observe — it can only be detected by a STRUCTURAL diff."

Principle 4 says semver is "computed from measured verdict movement, never declared". For a whole
class of change the engine cannot measure movement and falls back to a structural diff. The same
file names a second honest gap: the real historical `2.0.1 → 2.1.1` release "does not follow
textbook bump-and-reset semver either way — CONTEXT.md defines per-change classification but is
silent on reset-on-bump". Both are named in the code and owned by nobody.

### F14 (minor) — A resolved joint's module has no caller

Ticket 11 resolution 3 (map.md:38): "a subscribed feed becomes a signal by lookup on the clock."
`twin/feed_signal.py` implements it (247 lines, a fixed `STEEP_BY_FEED` table, a named hole that
raises rather than guesses — good design). `grep -rn "feed_signal"` across the whole hub returns
exactly three call sites: its own `demo()` invoked by `verify-twin-evals.sh:174-177`, and
`verify-e2e-step5-*.sh:43`, which asserts **the file exists**. Nothing on any clock calls
`signal_for`. The joint is graded by presence, not by operation.

### F15 (minor) — Ticket close rate has collapsed; creation has not

Resolution dates, from `git log -S"Status: resolved"` over each issue file (first commit
introducing the line):

| date | resolved |
|---|---|
| 2026-08-28 | 22 (all decision/grilling tickets; no build) |
| 2026-08-29 | 15 (the one `/implement` thin-slice run) |
| 2026-08-31 | 2 (54, 58) |
| 2026-09-01 | 2 (60, 61) |
| 2026-09-02 | 0 |

Creation (`git log --diff-filter=A`): 52 tickets on 2026-08-28, 19 on 08-31, 3 on 09-01. Over the
last three days: **22 created, 4 resolved**. 31 open, of which 15 are the untouched 2026-08-28
cohort (17, 27, 30, 31, 33, 34, 35, 37, 38, 39, 44, 45, 46, 48, 51). The four that did close
(54, 58, 60, 61) were the four cheapest on the review's own ordered route; the remainder include
"lift three real apps" (33), "the twin is three adopters" (64), "federation gets its peer" (68) and
"the misuse catalogue" (44).

At the last-three-days rate the current 31 clear in ~23 days *if* nothing new is charted and *if*
the remaining tickets cost what 54/58/60/61 cost. Neither holds.

### F16 (minor) — The truth number has plateaued, and the last fall is honesty, not decay

`talk/truth.log` on `origin/main`, 18 recorded lines: pass 43 (runs 4-8) → 45 → 47 → 54 → 53 →
57 → 58 → **59 (run 17, peak)** → 57 → 57 → 57 → 57. `fail` has never been 0 in any run; the
minimum is 1 (runs 16 and 17).

Pass has been 57 for four of the last five runs while total grew to 84. The 19→20 rise in fail
(3→7) is **not** decay: `skip` fell 22→18 in the same step, because ticket 60 taught the three
`verify-reconcile.sh` scripts and step 4 to grade the real lane sample instead of exiting SKIP
before reading it. Four could-not-looks became honest observed-falses. Any reader of the series
must be told this, or the number reads backwards.

Separately: `truth.yml`'s workflow conclusion is `failure` on all 15 most recent runs
(`gh run list --workflow truth.yml`), **including run 21's own** (33616685427). This is correct
behaviour — the last step is `fail if the gate failed` (`.github/workflows/truth.yml:163-165`),
firing because `verify-all.sh` exited nonzero with 7 reds. It is *not* the observation-lane error
a reader map attributed it to: the `::error::the scheduled truth run left a change outside the
observation lane` lines in the log are the step's own **source echo**, and the same log shows the
lane commit pushing cleanly (`7b92990..a209496  HEAD -> main`). Recorded so the misreading does
not propagate.

The consequence for §5's "A fall is a blocking event" is still real though narrower than
REVIEW-2026-08-31's M14 stated: the workflow conclusion is a truthful but *binary and permanently
saturated* signal — run 17→20's fall from fail=1 to fail=7 produced no change in it. Ticket 59
(open) owns the comparison half.

### F17 (minor) — The retirement removed the subject of four checks at once

Deleting 2.0.0/2.0.1/3.0.0 (map.md:72-79) was the honest repair, and it cost four gate checks
their subject in one move: coexistence, retirement, shift-left and the conditional-rule beat all
now SKIP naming the one-version array or 2.0.1's retirement (run-21 grades). Three of the four are
the checks that would prove the *thesis's own* headline properties. Owned by ticket 63 (the second
declared line) and ticket 58's D-decision to re-carry `root-if-attested` on 5.0.0 — recorded here
because the cost was paid in one commit and the repayment is still open.

---

## 3. What is genuinely done and proven

Each with evidence a skeptic can re-derive.

1. **The eco-system's central artefact claim is real.** `driftwood/composed/evidence.json` carries
   four priced lines from four distinct parties — ico 1,787,177; feeds 19,559; insurer premium
   113,403; twin forward-intel 1,897,646 — all GBP, all under `perspective: driftwood`, in one
   artefact signed by driftwood's own tag. Four independent orgs' output, composed and priced by a
   fifth's engine, in the consumer's own currency and perspective. That is the thesis, working.
2. **The signature spine is real and complete.** 24 tags across the 8 unit repos all verify with
   gitsign against Rekor (github-live map; 7 independently re-verified in the publishers map,
   including `feeds` and `insurer`'s first tags cut on 2026-09-01).
3. **"No gate" survives contact with the release path.** The degraded-publish decision (REGRILL 11,
   ticket 18) is *in code*, not just in a ticket: `gate.py:82,256-264` records `degraded` rather
   than refusing, and `cut-release-gate.py:153` emits the prerelease suffix on the untouched base
   number. The gate refuses only instrument faults, and has no override at any scope
   (`cut-release-gate.py:41-54`, the `CUT_RELEASE_TEST_MODE` scoping).
4. **The rejection ledger is not an exemption ledger.** Derived at run time from closed PRs; the
   old committed fixture is deleted and the reason recorded; empty offline with the caller told so;
   a different curve hash or £ is a new question (`wargamer/rejection_ledger.py:1-31`).
5. **Composition cannot read a clock, and proves it.** `composition.py:3566-3571` asserts its own
   source contains no `import datetime`/`time`/`sched`/`croniter`. ADR-0006 is enforced, not
   merely stated.
6. **The retirement used the estate's own mechanism with observed reasons.**
   `distribution/versions.yaml:31-59` records two independently observed live defects (the Priority
   admission triple, and a pod forging its own tier label reaching the API server from an
   `isolated` namespace on 2026-08-28) and the reasoning that a backport is impossible. Nothing was
   quietly deleted.
7. **The number got worse because the instrument got better.** Run 19→20: skip 22→18, fail 3→7.
   Four could-not-looks converted to observed-falses when ticket 60 reordered the graders. This is
   the behaviour NORTH-STAR §6 asks for ("a green that could not look is a red"), demonstrated
   against the project's own headline metric.
8. **Illustrative parameters are disclosed, not laundered.** `twin/severity-anchors.yaml:13,56,67`
   marks the GPD `xi`/`beta` `anchored: false` with the reasoning, rather than assuming them —
   even though the line they feed (forward-intel, 1,897,646 GBP) is the largest number on
   driftwood's balance sheet.
9. **The publishers' bumps are checked, not merely declared.** `ico`/`nist`
   `.github/scripts/declared-bump-gate.py` recomputes the bump from the feed's own `rule.yaml`
   before `cut-release.yml` tags, and refuses on disagreement — it refused for real the first time
   it ran. Principle 4's "never declared" holds where the gate exists.
10. **`truth.yml`'s red is honest.** The workflow fails because the gate has reds, by an explicit
    final step, while still committing and pushing the TRUTH line. A red run records its number.

---

## 4. Is the estate the right size?

**No — and the mismatch is not "too much code" so much as "mass in the wrong place".**

A minimal honest core that demonstrates both the thesis and the eco-system would need:
one regulator publishing signed OSCAL controls (nist, 518 lines) and one publishing a signed
penalty schema (ico, 718); one intelligence publisher with one feed (feeds, ~600 of 1,699); the
platform's compose (3,703) + party (829) + fair (528) + graded (1,176) + distribution (1,569) +
feeds converters (318) + honesty (754) + wargamer (1,576) = 10,453 of platform's 25,163; one
adopter (driftwood, 3,905); the hub's `verify/` + `talk/` (5,418); and the twin's forward-intel
emitter and pricing spine — call it 6,000 of the twin's 52,495.

That is roughly **29,000 lines, or ~30% of the ~97,600 the estate carries.** The other 70% is not
all ballast, and I want to be precise about which is which:

- **On the thesis path but off the §4 demo path (keep, but the demo does not need it):**
  `computed-semver` (7,524 lines — the single largest platform module) is principle 4 itself; it
  works and is fully green. `oscal` (552) is the "measurable" -able. `shift-left` (224) is a talk
  claim. Retiring these would cost thesis coverage, not demo coverage.
- **On a principle but not on any step, and unobservable on the clock:** `identity` (1,047),
  `access` (378), `eud` (218), `break-glass` (295), `posture` (209) — these are principle 2's
  "a human, a device, a model action" arms, and they SKIP every run for want of a cluster (F4).
  Ticket 27 (open) owns the human/device round.
- **Ballast by the estate's own decision, still shipping:** `currency-controller` (416) — F10.
- **Ballast by dilution:** the twin at 52,495 lines against one §4 step graded by file presence.
  REGRILL 39 deliberately keeps the eleven real firms as "evals of the model and tooling", so they
  are not an accident — but the ratio is.

**The truth surface's shape confirms it:** 54% of the graded checks belong to one of the eight
parties, and only 13% belong to the three parties whose consumption is the whole point.

---

## 5. Is the destination reachable?

Map Destination: "Every joint in NORTH-STAR §4 has an owning ticket the truth surface can grade,
**and the eco-system has run end to end once, on a clock, with driftwood, tuppence and ludlow
consuming.**"

The first half is essentially done: all seven steps have a gate check
(`verify/e2e/verify-e2e-step1..7`) and each has an owning ticket. The second half:

| step | real, on a clock? | evidence |
|---|---|---|
| 1 regulator publishes | **yes** | ico v3.0.0 cut, signed, on the remote; step-1 capture PASS |
| 2 Renovate pins, composition re-prices | **yes, once** | driftwood PR #20, bot commit ea1c8db on `renovate/feeds-threat-register-2.x`, merged 2026-09-01 (ticket 61) — though the gate's step-2 check itself grades an offline simulation |
| 3 £ crosses a band, PR opens, human merges | **never, and cannot** | ticket 74 open; F1 shows no clock-driven mover exists |
| 4 Flux reconciles the cage | **no** | step 4 FAILs on a real lane sample (fact 2, gitsign cert not yet valid at tagger time — ticket 73) |
| 5 twin plays a signal forward | **partly** | forward-intel really reaches driftwood's evidence; the gate grades presence; only 1 of 3 adopters has a twin (ticket 64) |
| 6 provenance | **yes, with a hole** | 7 of 8 identity regexps matched real Fulcio certs; F5 is the hole |
| 7 honesty | **yes** | step 7 PASSes correctly while step 4 FAILs — it grades honest reporting, not outcomes |

**Answer: not weeks; not months at this cadence; and step 3 is currently *never* without a
decision the owner has to take.** Three independent gates on the timeline:

1. **F1/F2 is a wall, not a queue.** No amount of ticket-burning fires step 3 while every adopter
   is pinned at the ladder's floor and two are past its end. This needs a calibration decision
   (bigger appetites, smaller exposures, more rungs, or size blocks on tuppence/ludlow), and no
   ticket contains it.
2. **Velocity.** 4 tickets in 3 days against 22 charted, with the expensive ones untouched (F15).
3. **The instrument's ceiling.** 11 of 84 checks can never be green on the clock as `truth.yml` is
   written (F4), so "the eco-system has run end to end" can never be fully evidenced by the only
   citable source until either the clock brings up a cluster or every live claim moves to a sample
   lane.

Against that, the *pace of honest correction* is genuinely fast: five days from a critical review
finding (kyverno pin) to a fixed gate, and the same-week conversion of four SKIPs into real FAILs.
The project is not stalling on competence. It is stalling on scope: 74 tickets and ~97,600 lines
chase seven demonstration steps whose pivot is arithmetically foreclosed.

---

## 6. The AI-disposal end state — is it the real purpose?

REGRILL 29 and 37 are the only place in the whole record where the owner describes an **end state**
rather than a mechanism: "this is a stepping stone for allows the ai to do it all", and "the twin
acts inside a priced cage; propose-only is the outermost setting; Article 22 floor for significant
decisions about people."

Read against that, most of the estate reads as the *substrate* for it rather than the goal: the
priced cage ladder is the vocabulary an agent's actions would be caged in; the identity spine is
how an agent's authorship would be attested; the honesty machinery is how its claims would be
falsified; the rejection ledger with a half-life is how its proposals would be rate-limited. That
is a coherent and unusually well-founded architecture for an agent-disposal control plane.

But almost nothing in the current 74 tickets builds *the agent as the subject*:

- The cage ladder's dials (`cpu`, `mem`, `waf`, `reach`, `evictFirst`) are pod dials. There is no
  dial vocabulary for a model action.
- `twin/enact_guard.py` is the one real constraint on machine disposal, and it is a mode file the
  agent itself rewrites (F8) — no price, no tier, no attestation of who flipped it beyond the
  commit.
- The interim rule the owner *did* name (author ≠ merger) is unbuilt on every repo (F8).
- Ticket 30 ("the twin's cage, spec and price per adopter") is open and is the closest thing;
  it is in the 2026-08-28 untouched cohort.

So: the AI-disposal end state is plausibly the real purpose, it is the most distinctive thing in
this record, and it is the least built. That is the question I most want the owner to answer.

---

## 7. Three candidate purposes — a decision for the owner

### A. "Prove the thesis, on a stage, with one honest worked example."
*Keep:* compose, party, fair, graded, distribution, computed-semver, one regulator (ico) + nist,
one feed publisher, **one** adopter (driftwood), `talk/`, the truth surface, the signature spine.
*Cut or park:* the twin down to the forward-intel emitter (~6k of 52k), insurer, tuppence and
ludlow, eud, break-glass, access, posture, tcor, wardley, oscal upflow, currency-controller.
*Must fix first:* F1 (recalibrate so a band is crossable in a demo), F9 (get to ≥3 lines or
publicly amend the thesis), F5.
*Estate shrinks to roughly 30%.* Destination reachable in weeks.

### B. "A running eco-system of loosely coupled parties."
*Keep:* every party, every artefact contract, the £, the composition, the signature spine, Flux,
all three adopters, the insurer, the feeds marketplace, the twin as a party.
*Cut:* platform-internal engines no *party* consumes — currency-controller, and the live-only
modules until a cluster exists on the clock (`eud`, `access`, `posture`, `break-glass`) — and the
eleven real firms from the critical path.
*Must fix first:* F1/F2 (the ladder must move for three parties, which means size blocks and a
calibration decision), F7 (the last platform-held tenancy), F6 (one tag scheme), F4 (the clock must
be able to see a cluster, or every live claim moves to a sample lane).
*Estate stays roughly this size but re-weights hard away from platform internals.* Destination in
months.

### C. "A control plane for AI disposal, priced and attestable."
*Keep:* the twin, `enact_guard`, the £ engine, the identity spine, the honesty machinery, the
evidence ladder, the forecast book, the rejection ledger, one adopter as a worked substrate.
*Cut or freeze:* the Kubernetes cage ladder to one demonstrated example, the multi-version
distribution question, the publisher marketplace beyond one regulator and one feed, the deck.
*Must build (none of it exists):* a dial vocabulary for model actions; a price on the agent's own
disposal; author ≠ merger enforced; the Article 22 floor; `ENACT_MODE` replaced by a tier the agent
cannot select for itself.
*This is the only one of the three that is not mostly already built, and it is the only one the
owner has described as an end state rather than a mechanism.*

---

## 8. Fitness verdict

The ambition is coherent — more so than the review's own probe list assumed — and the estate has
genuinely built the hard, distinctive parts: a real cross-org signature spine, a real composed and
priced artefact carrying four parties' output in one currency under the consumer's own
perspective, and an honesty machine that has repeatedly made its own headline number worse in
order to be true. Those are not small.

It is **not fit for the purpose NORTH-STAR states**, for one arithmetic reason and one shape
reason. The arithmetic: §4 step 3 — the pivot of the whole demonstration — is foreclosed, because
every adopter is already at the ladder's bottom rung and two of three are past its end, and the
only mechanical mover the estate has pushes the number further up. The shape: 54% of the graded
checks and 54% of the code sit in two components (the platform's internals and the twin) that
between them own one of the seven steps, while the three parties whose consumption is the entire
point carry 13% of the instrument.

What would make it fit, in order: (1) an owner decision on the £ calibration — appetites, sizes,
rungs, or exposures — so a band can actually be crossed; (2) `size` on tuppence and ludlow, so
principle 3 operates for more than one party; (3) a clock that can see a cluster, or every live
claim moved onto a sample lane, so the estate's central runtime claim is citable at all; (4) a
decision between purposes A, B and C, because at 4 tickets closed in 3 days against 31 open the
estate cannot afford all three.
