# Process and the record — assessment, 2026-09-02

Auditor dimension: **PROCESS AND THE RECORD**.
Baseline: `TRUTH 2026-09-02T10:11Z run=21 hub=7b92990 … pass=57 fail=7 skip=18 excluded=2 total=84`.
Everything below is re-derivable from the hub at `7b92990` / `origin/main`, the fresh unit clones,
and read-only `gh`. Where I could not look, I say so.

Maps read first: `understand/tickets.md`, `understand/drift-review-followthrough.md`, and (for
cross-checks) `understand/adrs-glossary-code.md`, `understand/github-live.md`,
`understand/truth-series.md`, `understand/verify-scripts-platform.md`. Every fact I rely on below I
re-derived at the primary source; where a map's fact turned out imprecise I say so explicitly
(see P5, and "map corrections" at the end).

---

## 1. What the record is supposed to be

The process rules were written by the 2026-08-27 drift review, at
`.scratch/drift-review-2026-08-27/GAPS.md:93-98`, verbatim:

```
1. No recommendation attached to an architectural question. State the trade, or make the call and record it as the assistant's.
2. At most five decisions put to the owner per day. None inside an implementation run.
3. A spec cannot advance to tickets without a recorded owner confirmation. Silence is not consent.
4. Done is defined by the truth surface, never by the demo.
5. Every ticket's definition of done includes wiring its check into the gate.
6. One north-star document; one status vocabulary; one truth number with a date.
```

They exist because `REPORT.md:26` diagnosed the pathology in the owner's own estate:

> "**The architecture is largely mine, ratified by your fatigue.** 482 decisions were put to you.
> Every one carried my recommendation. 306 (63%) got a bare 'agree' or a bare letter. Of the 254
> architectural decisions, 157 were bare, and 147 of those took my recommendation."

`REPORT.md:249` names the remedy: "no recommendation attached to architectural questions (state the
trade, or make the call and record it as mine); a hard cap on decisions per day and none inside an
implementation run".

The live rendition the estate actually operates by is `.scratch/ecosystem/map.md:16`:

> "Process rules (from the drift review): at most five decisions put to the owner per day, none
> inside an implementation run; a bare 'agree' or letter does not ratify architecture, so a
> decision is recorded with the owner's reason or it stays open; a spec does not advance to tickets
> without a recorded owner confirmation; done is defined by the truth surface, never by the demo;
> every ticket's definition of done includes wiring its check into the gate."

Rule 1 is **absent** from that list. Rule 6's "one status vocabulary" clause is absent too. In its
place the map invented a new rule (the bare-agree/provisional convention) which is a *bookkeeping*
remedy, not a *behavioural* one. That substitution is the root of most of what follows.

---

## 2. The bare-agree tally since 2026-08-28

Counted directly from the `## Answer` sections of the ticket files
(`python3` over `.scratch/ecosystem/issues/*.md`, numbered top-level items):

| Ticket | Items | Owner's recorded words | ADR produced |
|---|---|---|---|
| 04 feed contract | 5 | "Agree", then "These are all sound" | ADR-0019 |
| 07 size/obligations/currency | 3 | agreed without a reason; **item 3 has a real owner reason** ("USD is probably the default but we'll mostly use GBP") | ADR-0020 |
| 08 the £ seam | 7 | "Lgtm" | ADR-0021 |
| 09 cage ladder v2 | 5 | "ive already read the recommendations and I can't find fault with a single one" | ADR-0022 |
| 10 schedules and skills | 5 | same line | (ADR-0024, written later by ticket 28) |
| 11 an org twin each | 5 | same line | — |
| 12 identity as spine | 5 | same line | two ADRs |
| 13 lift or retire | 5 | same line (Q5 = D5, decided) | — |
| 14 insurance | 5 | same line | extends 0019/0021 |
| 15 price everything counted | 5 | same line | — |
| 16 Flux rescoped | 5 | same line (Q4 = D3, decided) | — |
| 18 publisher release under cages | 5 | same line (D3 applies) | narrows ADR-0011 |
| 19 misuse and portability | 5 | same line (D5 applies) | — |
| 20 one demo | 5 | same line (Q2 = D4, decided) | — |
| 22 prediction-market feed | 5 | same line (D2 applies) | — |
| 23 news feed / headline skill | 5 | same line | — |
| 24 size beyond turnover | 5 | same line (D2 applies) | — |
| **subtotal 2026-08-28** | **85** | one line covering fourteen held rounds | 6 ADRs touched |
| 58 four architectural gaps | 5 | "Agree" — verbatim, no reason (2026-08-31) | amends ADR-0023 (planned) |
| **total** | **90** | | |

Of those 90, **at most five carry a reasoned owner line** — D1 to D5, the one cross-ticket panel
round the owner answered with "I agree with you're more advanced reasoning" — plus ticket 07 item
3's partial currency reason. **~84 architectural decision items rest on a bare agree.**

**Which are architectural?** Six ADRs (0019, 0020, 0021, 0022, plus ticket 12's two and ticket 28's
0024) were written directly out of this batch, and ADR-0011 was narrowed by ticket 18 Answer 1.
That is the whole feed contract, the instrument-fault/priced-behaviour doctrine, the £ seam, the
cage ladder, the identity spine and the clock — i.e. essentially all of the eco-system's
architecture as it exists today. This is not a set of small choices.

The record's own honesty here is real and worth stating plainly: **every one of those seventeen
tickets quotes the owner's exact words and states in its own text that a bare agree does not
ratify.** The record never claims a ratification it does not have. Ticket 08 even self-reports its
own breach on the day: "The daily budget of five decisions was already spent by tickets 04 and 07
before this round; the owner answered on the day anyway, and that is recorded here."

---

## 3. The five-per-day rule and "none inside an implementation run"

Ticket creation dates (`git log --diff-filter=A` over `.scratch/ecosystem/issues/`):
**52 tickets added 2026-08-28, 19 on 2026-08-31, 3 on 2026-09-01.**

The intraday sequence on 2026-08-28 (hub `git log`, times BST):

| Time | Commit | Event |
|---|---|---|
| 03:22 | `ea86428` | drift review committed (contains the five-per-day rule) |
| 03:31 | `8a14528` | **map charted, carrying the process rules** |
| 06:26 | `6ee916a` | ticket 04 resolved — 5 decisions |
| 06:38 | `32894fb` | ticket 07 resolved — 3 decisions (cap now exceeded: 8) |
| 08:14 | `c57a887` | ticket 08 resolved — 7 decisions (15) |
| 12:32 | `20568bc` | **14 grilling tickets resolved in one commit** (~70 more) + ADR-0022 + ADR-0023 + CONTEXT.md rewrite |
| 12:41 | `faad634` | spec written, ready-for-agent |
| 16:22 | `3e83a16` | **implementation run begins** (ticket 21 verify) |
| 22:15 | `318052d` | **ADR-0022 amended inside the run** — Audit→Deny promotion |
| 2026-08-29 02:19 | `f19876f` | ADR-0023 amended inside the run |
| 2026-08-29 06:25 | `a766346` | ADR-0011 superseding note inside the run |
| 2026-08-29 06:40 | `6058943` | run ends; fifteen tickets resolved |

**Verdict on "at most five per day":** broken within three hours of being written, breached again
knowingly, then formally waived. `map.md:18` records the waiver: "The five-per-day rule was
overridden by the owner's instruction for this batch." Since 2026-08-28 the cap has been kept
exactly once: ticket 58 put five questions on 2026-08-31. So the rule is honestly recorded as
broken, but it is not a live constraint.

**Verdict on "none inside an implementation run":** kept in letter — no decision was *put to the
owner* between 16:22 on 08-28 and 06:40 on 08-29. Broken in substance: three ADRs were amended
inside that window, and ticket 21 records seven build-taken decisions
(`21-build-the-feed-contract.md:15-25`, "Decisions taken while applying the review of the first
build. Each is provisional; reopen with a reason"). The rule has no lane for "the build discovered
a fact that forces an architectural call", so those calls were made and recorded without a round.
See P5.

---

## 4. Findings

### P1 (critical) — The corrective rule was dropped, and the pathology it was written to stop recurred at higher intensity

**Claim.** GAPS.md's rule 1 — "No recommendation attached to an architectural question" — is not in
`map.md:16` and appears nowhere in `.scratch/ecosystem/`. Every grilling round then attached a
recommendation (the `➡️` pattern; e.g. `13-lift-or-retire-the-original-mechanisms.md:60` "➡️ (a).
It adds no mechanism beyond what ticket 10 must build…"), and 85 items were accepted on one line.

**Evidence.**
- `.scratch/drift-review-2026-08-27/GAPS.md:93` (rule exists), `.scratch/ecosystem/map.md:16`
  (rule absent). `grep -rn "recommendation attached" .scratch/ecosystem/` → no hits.
- `.scratch/drift-review-2026-08-27/REPORT.md:26` (the diagnosis: 482 decisions, all with a
  recommendation, 157 architectural ones bare).
- `git log`: map charted `8a14528` 2026-08-28 03:31; batch resolved `20568bc` 2026-08-28 12:32.

**Why it is critical, not tidy-up.** The prior estate's failure mode was 157 bare architectural
decisions accumulated over months. The current estate produced ~85 in a single reply. Per-reply
density went *up*, not down. The provisional convention the map substituted records the debt but
does not slow its accrual, and nothing converts it (P2).

**Remedy.** Restore rule 1 to `map.md:16`, or delete it from GAPS.md with a dated reason. A rule the
owner never rescinded and the operating document silently omits is worse than either.

---

### P2 (critical) — ~84 provisional architectural items are `Status: resolved`, against the record's own rule, with no route to ratification

**Claim.** `map.md:16` says "a decision is recorded with the owner's reason **or it stays open**."
Seventeen tickets carrying ~84 unratified items are `Status: resolved`. No ticket, check or
document owns converting a provisional to a decided.

**Evidence.**
- Counts and per-ticket ratification wording: §2 above, each line re-derived from the ticket's own
  Answer paragraph (e.g. `09-the-cage-ladder-v2.md:141`, `15-price-everything-that-was-counted.md:78`,
  `58-…:29-30`).
- `Status:` values across all 74 tickets: resolved 41, open 31, prepared 1, claimed 1.
- `grep -rln "ratif\|convert.*provisional"` across `issues/*.md`, `map.md`, `spec.md`,
  `TO-SPEC-HANDOFF.md`, `BUILD-BRIEF.md`: every hit is a ticket *recording* provisionality; none
  owns *removing* it.
- The only conversion mechanism that ever worked is the panel-verdict round (D1–D5, 2026-08-28).
  The identical shape was tried again on 2026-08-31 (ticket 58) and produced another bare "Agree",
  so all five stayed provisional. Success rate to date: 1 of 2.

**Fit impact.** The estate's contract with itself (NORTH-STAR §2's cross-org shapes, ADR-0019's feed
envelope, ADR-0022's ladder) is architecture the owner is recorded as never having reasoned about.
If the owner later disagrees with any one of the 84, the record supplies no defence — and the build
has already shipped code, tags and signed artefacts on top of them.

**Remedy.** Either (a) make `Status: resolved` illegal while any item is PROVISIONAL — which turns
17 tickets back to open and makes the debt visible on the tracker — or (b) record the owner's
explicit acceptance that the assistant's recommendations *are* the architecture, and retire the
provisional vocabulary as a false comfort. Both are honest; the current state is neither.

---

### P3 (major) — REVIEW-2026-08-31's refutation of the bare-agree finding is unsound

**Claim.** `REVIEW-2026-08-31.md:99` refutes "17 of 22 decisions rest on a bare agree with no route
to ratification" with: "the provisional convention is a recorded process rule with an explicit
reopen-with-a-reason path; no ambition document requires conversion." Both halves fail.

**Evidence.**
- The reopen path is circular: every ticket's wording is "Anyone who wants them reopened needs a
  reason the owner did not give" (`04-the-feed-contract.md:17`). The condition for reopening is the
  very thing whose absence made the item provisional.
- "No ambition document requires conversion" is contradicted by the map itself: `map.md:16` says an
  unratified decision "stays open", and seventeen such tickets are `resolved`. The map *is* the
  operating document the review cites elsewhere.

**Note on the other nine refutations.** I re-derived two directly and found them sound: "All five §7
supersessions carry dated banners" (`REVIEW…:34`) — ADRs 0011, 0014, 0015, 0016, 0018 all carry
dated banners, confirmed by `grep` on the file heads; and "no scheduled clock has ever fired" was
correct on 2026-08-31 and has since been overtaken by real firings. I did not re-derive the
remaining seven and do not endorse or dispute them.

**Also, on the review's findings:** of the eighteen M-findings I could test, none was wrong. M13,
M14 (run 12→13 fell 54→53, confirmed in `talk/truth.log`), M15 (confirmed still true today — see
P12) and M18 all check out. One prediction mis-fired harmlessly: M18 said the deck check "will red
again on run 14"; run 14 exists on GitHub (`33435351306`, 2026-08-31T20:18:51Z, conclusion
`failure`) but produced **no TRUTH line at all** — `talk/truth.log` jumps 13 → 15. See P16.

---

### P4 (major) — Fifteen resolved tickets cite as proof a TRUTH line that exists and contradicts them, and only one has been corrected

**Claim.** Each of tickets 21, 25, 26, 28, 29, 32, 36, 40, 41, 42, 43, 47, 49, 50, 52 ends: "The run
that recorded it is the TRUTH line of 2026-08-29." The only TRUTH line dated 2026-08-29 is:

```
TRUTH 2026-08-29T12:03Z run=7 hub=918022b units=[driftwood=eacae33 ico=8902b66 ludlow=a800a58
nist=33a05df platform=58ef9c5 tuppence=751522b] pass=43 fail=11 skip=0 excluded=2 total=56
```

That line graded hub tree `918022b`. `git ls-tree --name-only 918022b:verify/` returns exactly
`_estate.py party proportionality provenance` — **none** of `feed-contract`, `pound-seam`,
`twin-evals`, `schedules`, `e2e`, `demo`, `renovate` existed. Its unit SHAs (`driftwood=eacae33`
etc.) are identical to runs 4, 5 and 6, i.e. the pre-build estate. `total=56`, versus 83 once the
build's scripts were discovered (run 12).

So the fifteen tickets' shared sentence "Definition of done: its check is in `talk/verify-all.sh`.
The run that recorded it is the TRUTH line of 2026-08-29" names a run in which **none of those
checks existed**. This is a sharper defect than the map's own correction, which says only that the
65/0/16 figure "was a local rehearsal. No TRUTH line records it" (`map.md:64-68`) — a reader
chasing the citation finds a real line that says the opposite.

**Ownership.** Ticket 40 alone carries a dated in-place retraction (added by ticket 60, 2026-09-01).
Ticket 67 ("The record matches the surface", open) explicitly scopes itself: "The map's false
65/0/16 citation and the stale fog list were corrected at charting time on 2026-08-31; **this
ticket owns the rest**" and then enumerates (a)–(d), none of which is the fourteen uncorrected
Answers. Its check (d) — "any pass/fail figure that map.md quotes must exist as a line in
talk/truth.log" — is scoped to `map.md` only. **The fourteen are an orphan.**

**Remedy.** Append the same dated note ticket 40 carries to the other fourteen, and widen ticket
67(d)'s check to `.scratch/ecosystem/issues/*.md`.

---

### P5 (major) — An architectural decision the owner never saw was written into an ADR inside an implementation run, and the glossary still contradicts it

**Claim.** `git show 318052d` (2026-08-28 22:15, i.e. inside the 16:22 → 06:40 implementation run)
adds two addenda to ADR-0022, the second of which promotes `governed-namespace-requires-claim` from
`Audit` to `Deny` — "This is the one refusal the doctrine allows". No owner round preceded it, and
the addendum is not marked PROVISIONAL (unlike the ADR's own body, which is).

**Evidence.**
- Commit message and diff quoted in full from `git show 318052d -- docs/adr/`.
- The reversal is substantive: `map.md:13` states the estate's vocabulary rule as "Price and cage;
  never count, refuse or file."
- `CONTEXT.md:240-241` still reads "There is no `CREATE` deny any more: a pod that claims nothing
  gets the namespace's tier". `git log -S "deny any more" -- CONTEXT.md` returns exactly one commit,
  `20568bc` (2026-08-28 **12:32**) — nine hours *before* the ADR addendum — and the line has never
  been touched since.
- The shipped code follows the ADR, not the glossary (per `understand/adrs-glossary-code.md`:
  `platform/distribution/versions.yaml:155-157` Deny/CREATE, live-asserted at
  `platform/graded/verify-graded.sh:526-530`). I did not re-open those two files myself.

**Map correction.** `understand/adrs-glossary-code.md` states the ADR addendum "predates CONTEXT.md's
rewrite commit (20568bc, 2026-08-31)". `git log -1 20568bc` dates that commit **2026-08-28 12:32**.
Same conclusion (the glossary is wrong), different mechanism: CONTEXT.md was not rewritten after the
ADR and ignored it — it was written *before* and never revisited.

**Fit impact.** The estate's own glossary and its ADR disagree on whether the one permitted refusal
exists. A newcomer reading CONTEXT.md would build the wrong thing. And the decision that created the
disagreement is the clearest instance of a call that was the owner's to take.

**Remedy.** Either fix CONTEXT.md's Governed-namespace entry to match ADR-0022's addendum, or put
the Audit→Deny promotion to the owner as a real decision. It is the one refusal in a doctrine whose
headline is "never refuse"; it deserves a round.

---

### P6 (major) — Fifteen of the twenty recorded cross-ticket conflicts were resolved by the assistant

**Claim.** `GRILL-WALK.md:47-67` lists twenty cross-ticket conflicts, C1 to C20. `map.md:18` records
that **five** went to the owner with a three-lens panel verdict (becoming D1–D5). The other fifteen
were resolved by the assistant and applied as "amendments" inside the tickets, under the same bare
agree.

**Evidence.** The conflict list itself (quoted verbatim from GRILL-WALK.md:47-67). Some are honest
derivations and say so — `18-the-publisher-release-under-cages.md:82`: "C1 and C8 are not decisions
of their own: C1 rests on ticket 09's accepted round … and C8 on ticket 04 A4 and ADR-0018 §1
(settled)". Others are genuine choices between two positions the owner separately agreed to:
- **C9** — "09 Q4 wants an adopter-declared floor tier; 15 Q4 rejects one."
- **C11** — "`prices[]` reshaped by 14, 15, 19, 24 independently."
- **C15** — "10 and 12 hand the currency controller to 13; 13 omits it" (resolved by *retiring* the
  currency controller — a live component).
- **C13** — "20 calls niobium the first news entry; 23 Q1 says never."

**Fit impact.** A conflict between two owner-agreed positions is by construction a place the owner's
own words do not settle. Resolving fifteen of them without a round is exactly the class of decision
GAPS rule 1 was written about.

**Remedy.** Publish a one-page list of the fifteen with the assistant's call and one line of reason
each, and put it to the owner as a single round — the panel-verdict shape that worked once.

---

### P7 (major) — Four of the six ADRs born of the bare-agree batch do not record that they are provisional

**Claim.** ADR-0022 and ADR-0024 disclose their own provisionality; ADR-0019, 0020, 0021 and 0023 do
not.

**Evidence.**
- `grep -c -i provisional docs/adr/0019*.md 0020*.md 0021*.md 0023*.md` → `0` for all four.
- `docs/adr/0022-…:10-11`: "Decided 2026-08-28 in `.scratch/ecosystem/issues/09`. **Provisional: the
  owner agreed without a reason.**"
- `docs/adr/0024-…:81-85`: "…are PROVISIONAL on a bare agree
  (`.scratch/ecosystem/issues/10-schedules-and-skills.md:80`) … Corrected 2026-08-28 so the
  decided/provisional line stays…"

**Fit impact.** ADR-0019 is the feed envelope every publisher and every adopter implements; ADR-0020
is the refuse-vs-price doctrine the whole composition engine turns on. A reader of the ADRs — the
canonical decision record, and the artefact a newcomer or an external reviewer actually reads —
cannot learn that either rests on an unratified line. The bare-agree convention is recorded in the
*ticket tracker*, which is `.scratch/` scratch material, and not in the durable record.

**Remedy.** Copy ADR-0022's one-sentence provisionality line into 0019, 0020, 0021 and 0023.

---

### P8 (major) — Two ADRs are superseded by *decided* owner positions and carry no banner

**ADR-0010 (consumer-side `sunset:`).** Ticket 13's Q5 is **D5 — DECIDED**, the strongest
ratification class in the entire record ("I agree with you're more advanced reasoning"). Ticket
13:86 states: "ADR-0010:5-9 (consumer-side `sunset:`) is superseded by the ADR ticket 10 writes."
ADR-0024 was written; `grep "ADR-0010\|supersede" docs/adr/0024*.md` shows it supersedes **ADR-0015
point 5** and nothing else. ADR-0010's head shows `status: accepted` and no banner. Ticket 02's own
Answer flagged the debt on 2026-08-28: "it did not rewrite ADR-0006, ADR-0010, ADR-0014 or
ADR-0015". 0014 and 0015 have since gained banners; 0010 has not. **No open ticket names ADR-0010**
(ticket 39 names 0013, 0017 and 0018 pt.3 only).

**ADR-0008 (four-panel Grafana dashboard).** `grep -c "superseded\|retired\|2026-08"
docs/adr/0008-measurable-layered-ground-truth.md` → `0`; `status: accepted`. Its entire mechanism —
"the dashboard is four panels over four datasources" — was rejected by the owner in his own words
on 2026-07-20 and formally retired by ticket 13:36: "Grafana dashboards are retired: the owner
rejected them on 2026-07-20 … and NORTH-STAR §5 makes the truth surface the only citable read; **no
dashboard of any kind is re-asked**."

**Fit impact.** Both ADRs read as live architecture to anyone who opens `docs/adr/`. One of them
(0010) describes a mechanism the estate has replaced; the other (0008) describes one the owner
explicitly rejected. Contrast with ADRs 0011/0014/0015/0016/0018, all five of which do carry dated
banners — so the convention exists and works; these two were missed.

**Remedy.** Add dated superseded-in-part banners to 0010 and 0008 naming ticket 13 / D5 and the
2026-07-20 rejection respectively. One commit; no code change.

---

### P9 (minor) — A promise inside a decided ticket never landed and nobody owns it

`13-lift-or-retire-the-original-mechanisms.md:86` says "**ADR-0004 gains a dated sequencing note.**"
I read `docs/adr/0004-cloud-plane-fork-collie.md` in full: no dated note, no sequencing note,
`status: accepted`, and `grep "2026-0" 0004*.md` returns nothing. Ticket 13 is `resolved`; no open
ticket names ADR-0004. Orphan.

---

### P10 (minor) — CONTEXT.md carries two contradictory sunset entries

- `CONTEXT.md:~404` (added 2026-08-28, ticket 13): "**No consumer-side sunset field exists.**"
- `CONTEXT.md:~559`: "A fleet's array entry may carry a `sunset:` date; on that date a machine opens
  a retirement PR… See ADR-0010."

`git log -S "A fleet's array entry may carry a" -- CONTEXT.md` → `8b4010a`, **2026-07-16**, never
revised. The two entries live in one glossary. This is downstream of P8's missing ADR-0010 banner:
nothing swept the glossary when the mechanism was superseded. Owned in spirit by ticket 67 ("a
reader following the map meets no claim the truth surface contradicts") but not named in its (a)–(d)
list.

---

### P11 (minor) — HISTORY.md's post-mortem states a universal rule that is false today

`docs/HISTORY.md:219-222`: "Every live tail now has exactly three outcomes: observed-true,
observed-false, and could-not-look, which is `SKIP` with a reason and exit 3. Every live-claiming
script asserts its substrate first, in order: `docker info`, `kind get clusters`…"

Counter-example, read directly from the fresh platform clone,
`platform/computed-semver/verify-gate.sh:11-14`:

```sh
if ! command -v kyverno >/dev/null; then
  echo "SKIP: kyverno CLI not found -- the gate's seam needs it for ticket 19+'s movement checks"
  exit 0
fi
```

`exit 0` is graded **PASS** by `talk/verify-all.sh`. Its sibling
`platform/distribution/verify-render-version-tree.sh:23-29` was fixed, and its comment names the
class exactly: "exit 3, not 0. verify-all.sh grades 0 as PASS, so exiting 0 here reported 'the
coexistence proof holds' on any runner without the CLI — a check that passes on absence, **the exact
class the 2026-08-25 incident came from**." Per `understand/verify-scripts-platform.md` six
computed-semver scripts share the unfixed convention; I verified one. Run 21's runner had kyverno,
so no live false PASS today — the record's claim, not the gate, is what is wrong.

Separately, "asserts its substrate first" is no longer the rule either: ticket 60 deliberately
reordered the three `verify-reconcile.sh` scripts to grade the sample *before* the substrate check
(correctly, to fix REVIEW M7). HISTORY.md has not been updated.

---

### P12 (major) — Ticket 29's false claim is uncorrected four days after it was found, while ticket 40's was corrected

Ticket 29's Answer (`29-…:17`) reads: "the six standing scenarios **exist per adopter**". Direct
check on the fresh clones at the run-21 SHAs:

```
$ find units/{driftwood,tuppence,ludlow} -path '*twin*' -not -path '*/.git/*'
units/driftwood/verify-twin-overlay.sh
units/driftwood/twin
units/driftwood/twin/verify-twin-scenarios.sh
units/driftwood/twin/world
units/driftwood/twin/currency.yaml
(tuppence: nothing; ludlow: nothing)
```

REVIEW M15 confirmed this on 2026-08-31; ticket 64 (open) exists to record it. Ticket 29's Answer is
unchanged. The record's stated convention is "no history rewrite in place, ever" plus dated
in-place corrections — applied to ticket 40 on 2026-09-01, not applied to ticket 29. Inconsistent
application of the estate's own honesty convention is itself the finding; the underlying gap is
owned.

---

### P13 (minor) — Fourteen of 41 resolved tickets name no gate check, against process rule 5

By direct scan of each resolved ticket's `## Answer…` section for any `verify` reference: **01, 02,
04, 05, 06, 07, 08, 09, 12, 15, 22, 23, 24, 58** name none. Ten of those are grilling/research
tickets where rule 5 arguably has no subject (a decision is not a check). Two are assertions of
real-world fact with no check at all: ticket 01 self-discloses that the Mend dashboard settings were
"set by the owner… **Not verified by the assistant**"; ticket 02 asserts a documents rewrite. This is
honest but it means the tracker records fourteen `resolved` states no scheduled run can ever
contradict.

---

### P14 (minor) — Status vocabulary and even the Answer heading are still free text

Four free-typed `Status:` values in use (resolved 41, open 31, prepared 1, claimed 1) with no enum
and no derivation — GAPS 2.9 / REVIEW M14 / ticket 59, all open. The `## Answer` heading is also
unstandardised: `## Answer`, `## Answer (2026-08-31)` (ticket 54), `## Answer — 2026-09-01, step 2
happened for real` (ticket 61). My own first scripted pass mis-scored tickets 54 and 61 as
"no check named" purely because of the heading variance — a live demonstration that the record is
not machine-readable, which is exactly what ticket 59(b) proposes to fix.

---

### P15 (minor) — The map's section heading still asserts a green gate

`map.md:54`: "### Built 2026-08-29 — the thin slice runs, **and the gate is green**", above
`map.md:62` "Nothing is red." The dated correction at `map.md:64-68` retracts "the paragraph above"
— which covers line 62 but not the heading. Ticket 67's own text declares this already handled ("The
map's false 65/0/16 citation and the stale fog list were corrected at charting time"). The gate has
never been green: fail counts across the whole eighteen-line `talk/truth.log` series are
16, 11, 11, 11, 11, 11, 14, 16, 16, 6, 7, 3, 1, 1, 3, 3, 7, 7 — **fail=0 has never occurred**.

---

### P16 (minor) — The citable series has an undetected hole at run 14

`gh run list --repo policy-as-versioned-flux/policy-as-versioned-flux --workflow truth.yml` shows
run 14 (`33435351306`, 2026-08-31T20:18:51Z, `push`, conclusion `failure`), 99 seconds before run 15.
`talk/truth.log` jumps from `run=13` to `run=15`. Nothing in the gate detects a run number that
produced no line, so a run that dies before printing its TRUTH line is invisible to the record. This
is the mirror of ticket 59(a)'s "a fall is a blocking event": a *missing* line is not a fall either.

---

### P17 (minor) — Every truth.yml run concludes `failure`, so the workflow signal carries no information

Of 21 runs pulled, 20 concluded `failure`; the single success is a `workflow_dispatch` on
2026-08-28T04:34. Run 21 — the run that produced today's citable line — concluded `failure`
("the scheduled truth run left a change outside the observation lane", per
`understand/github-live.md`, which I did not re-derive from the log myself). The TRUTH line is
genuinely committed and genuinely citable; but REVIEW M14's "the permanently red workflow saturates
the only signal" is still exactly true, and ticket 59 is open. Also worth noting for the record's
honesty: run 20, the line ticket 60 cites as its proof, was `workflow_dispatch`, not the cron —
and **ticket 60 says so itself** (`60-…:186`, "Honesty note: today's graded samples came from
workflow_dispatch firings of the lane workflow (owner-triggered after the merges), not from the
cron event"). That disclosure is a credit, not a fault.

---

### P18 (minor) — The enact guard was disabled fifteen times in twenty-six hours, every time on the record

`git log --grep="twin: .*mode\|back to operations"` shows fifteen disable/re-enable pairs between
2026-08-31 14:51 and 2026-09-01 09:59, each a separate dated commit on `main` with a stated reason
("development mode to land the release repair" → "back to operations, the repair is proposed and
waits on review"). `twin/ENACT_MODE` currently reads `operations`. The bookkeeping here is
exemplary — the mode is a checked-in file, visible in `git blame`, never an environment variable
nobody would find. The *process* observation is that a guard routed around fifteen times in a day is
functioning as a speed bump, not a control; two of the fifteen record the guard doing its job
("back to operations, the merges are not mine to make", `fdfc2cf`).

---

## 5. Strengths — recorded honestly

1. **The record never claims a ratification it does not have.** All seventeen bare-agree tickets
   quote the owner verbatim and state in their own text that a bare agree does not ratify
   (`04:17`, `09:141`, `15:78`, `58:29-30`, …). This is rarer and harder than it sounds.
2. **Self-reported breaches on the day they happen.** `08-the-pound-seam.md:17` records its own
   budget overrun; `map.md:18` records the five-per-day waiver as an owner instruction rather than
   silently ignoring the rule; ticket 54 records the assistant's own self-introduced SIGPIPE bug.
3. **Every one of the 24 ADRs carries reconstructible rationale.** Section inventory across
   `docs/adr/*.md`: each has an `## Alternatives` / `## Considered options` / `## Why` block plus
   `## Consequences`. A newcomer can reconstruct why any ADR exists from the ADR alone. Five
   supersessions carry dated banners (0011, 0014, 0015, 0016, 0018).
4. **Ticket 61's promise was kept and is now citable.**
   `talk/captures/verify_renovate_verify-renovate-merged-feed-pr.out` reads
   `SKIP: no merged Renovate feed-pin PR exists yet…` at run 17 (`93c2d79`) and
   `PASS: driftwood #20: Renovate raised threat-register v1 -> v2, Chris Nesbitt-Smith merged it…`
   from run 18 onward, unchanged through run 21. That closes REVIEW M8 on a numbered line and
   settles the open question `understand/tickets.md` left unresolved.
5. **Ticket 60 is a model of the standard the rest should meet:** a genuinely numbered TRUTH line
   (run 20, verifiable in `talk/truth.log`), *plus* a self-disclosed caveat that limits it, *plus* a
   successor ticket (74) for the part that did not happen.
6. **Ticket 40 carries a dated in-place retraction** rather than a silent edit, and the map carries
   its own dated correction block. The convention exists and works when applied.
7. **The truth number has never been gamed.** Eighteen recorded lines, none with `fail=0`, and every
   one of run 21's seven reds maps onto a named open ticket (72, 73, 62, 66, 74). Process rule 4
   ("done is the truth surface, never the demo") is the one rule that is operationally intact.
8. **The provisional/decided distinction is applied with real discipline.** The same "five questions
   in one batch" shape produced DECIDED once (D1–D5, reasoned reply) and PROVISIONAL the second time
   (ticket 58, bare "Agree"). The record graded the owner's two replies differently on their actual
   wording. That is not bookkeeping theatre.

---

## 6. Sustainability of the owner's decision load

The load is **not sustainable in its current shape, and the record proves it twice over.** The
drift review measured the failure directly: 482 decisions, 63% bare. The remedy — a cap plus "no
recommendation attached" — was applied for about three hours, then the cap was waived and the
"no recommendation" rule was dropped from the operating document. On the first day under the new
rules, ~85 architectural items went to the owner in one batch and came back on one line.

But the diagnosis "the owner cannot absorb this" is only half right. The evidence says the owner
*can* decide well when the question is shaped for deciding: the one panel-verdict round (five
conflicts, three lenses each, one page) got a reasoned reply — "I agree with you're more advanced
reasoning" — and produced the only five ratified decisions in the estate. The same owner, given
fourteen held rounds at once, produced "I can't find fault with a single one". The variable is not
the owner's capacity; it is the batch size and the presence of a recommendation.

**Is the provisional debt a fitness risk or bookkeeping?** Both, and the split matters:

- **Bookkeeping, not risk, for most of it.** ~84 items, mostly internally consistent, mostly built,
  mostly working. If the owner reads them and agrees, nothing changes. The debt is honestly
  labelled everywhere in `.scratch/`.
- **Real fitness risk in three specific places.** (a) The provisionality is *not* labelled in
  `docs/adr/` (P7), which is the durable, externally-visible record — so the honesty is confined to
  scratch material. (b) The estate has already cut signed tags, published feeds and re-priced three
  adopters on top of ADR-0019/0020/0021; a reversal now is not a document edit, it is a re-release
  across eight repos. (c) One decision reversing the estate's headline doctrine (the Audit→Deny
  promotion, P5) was taken with no round at all and the glossary still contradicts it.

The debt is therefore compounding faster than it is being serviced: 90 items put in six days,
5 ratified, 0 mechanism to ratify the rest, and the one rule that would have prevented it deleted
from the operating document.

---

## 7. Map corrections (things I checked that the readers' maps got slightly wrong)

- `understand/adrs-glossary-code.md` dates CONTEXT.md's rewrite commit `20568bc` to 2026-08-31.
  `git log -1 20568bc` → **2026-08-28 12:32**. The conclusion (glossary contradicts ADR-0022) stands;
  the mechanism is "never revisited", not "revisited and ignored".
- `understand/tickets.md` left open whether ticket 61's promised SKIP→PASS flip happened. It did, at
  run 18, and holds at run 21 (capture quoted in §5.4).
- `understand/tickets.md` counts "22 resolved tickets name no gate check". By direct scan of the
  `## Answer…` sections the number is **14**; the difference is tickets 10, 11, 13, 14, 16, 18, 19,
  20 which do name a script, and tickets 54/61 whose non-standard Answer headings defeat naive
  parsing.
- `understand/drift-review-followthrough.md` reports "15 files contain the phrase 'bare agree'" as a
  raw count. The load-bearing number is the *item* count, which is ~90 across 18 tickets (§2).

## 8. What I could not look at

- I did not re-derive the seven of REVIEW-2026-08-31's ten refutations that I do not name in P3.
- I did not read the run-21 workflow log to confirm the cause of `truth.yml`'s failure conclusion
  (P17); I take that from `understand/github-live.md`.
- I did not open the five remaining computed-semver `exit 0` scripts named in
  `understand/verify-scripts-platform.md`; I verified one (`verify-gate.sh`).
- I did not audit the 41 REGRILL answers or GAPS.md's 66 rows individually; that is
  `drift-review-followthrough`'s scope and it flags its own coverage gaps.
