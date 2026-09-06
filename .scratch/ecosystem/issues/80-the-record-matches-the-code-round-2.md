# 80 — The record matches the code, round 2

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

Ticket 67 makes the map match the surface. This ticket makes the ADRs, the tickets and the glossary match the code. Ten cheap corrections:

1. Fifteen resolved build tickets (21, 25, 26, 28, 29, 32, 36, 40, 41, 42, 43, 47, 49, 50, 52) cite "the TRUTH line of 2026-08-29" as proof their check is in the gate. That line is run 7, graded before the build, and its tree contains none of the checks. Append the dated correction ticket 40 already carries to the other fourteen, and widen ticket 67(d)'s check so any TRUTH figure quoted in `issues/*.md` must resolve to a real line whose tree contains the named check.
2. ADR-0010's consumer-side `sunset:` was decided away by ticket 13 D5. ADR-0008's dashboards were rejected on 2026-07-20. Neither carries a banner. Add dated superseded-in-part banners to both.
3. ADR-0019, 0020, 0021 and 0023 say `accepted` and nowhere say the decision rests on a bare agree. Copy ADR-0022's one-sentence provisionality line into each, with the originating ticket path.
4. CONTEXT.md's Governed-namespace entry says there is no CREATE deny. ADR-0022's 2026-08-28 addendum promoted `governed-namespace-requires-claim` to Deny inside an implementation run with no round. Correct CONTEXT.md to match the shipped code, and list the promotion in ticket 75 as an assistant-made call.
5. Restore GAPS rule 1 to `map.md`'s process rules, or delete it from GAPS.md with a dated reason. It was dropped in the copy.
6. ~~The currency controller: correct `map.md:113` with whatever ticket 75 Q13 decides, and delete or own the module in one commit.~~ **Direction settled and item DONE, 2026-09-05 (ticket 91 item 4).** Ticket 75 Q13 decided (a): the retirement is withdrawn. So the disjunction closes on **own**, not delete — "delete or own" is no longer an open choice and no build should read it as one. Ticket 91 executed the un-retirement: the module is a versioned member of platform's published `implementations` package numbered by the platform's own tag, its CronJob may only tighten, `CONTEXT.md` carries a **Currency controller** term, and `verify-currency.sh` grades that term's sentence. The two map sentences this item named — the ticket-13 line's "currency-controller retired" and "The currency controller is retired (ticket 13)" under *Not yet specified* — are corrected in the same change. Ticket 13's Answer carries the dated withdrawal with the reason each retirement clause failed on. **Nothing is left for ticket 80 here.**
7. The three ADR notes ticket 13 assigned itself (0004, 0007, 0010) are unwritten. Write them.
8. `talk/RUNBOOK.md` section 1 says driftwood's bring-up reconciles the real signed GitHub remote. `scripts/up.sh` reconciles an unsigned tag from a git server built on the laptop. Correct the runbook, or give `up.sh` a `--remote` mode.
9. The fourteen legacy repos and the `policy-as-versioned-flux` org carry no signpost to the eco-system. Add a dated "superseded reference implementation" banner to each README and an org description naming both implementations.
10. `platform/README.md` calls the adopter apparatus a shared config base. Three independent gates of 1087, 661 and 1213 lines share 260 lines. Say which it is, per ticket 75 Q7.

Done = a script under `verify/` greps each of the ten facts and passes; no ADR says `accepted` for a decision the tracker records as provisional; no ticket cites a number no TRUTH line records.

## Notes

Charted by [REVIEW-2026-09-02.md](../REVIEW-2026-09-02.md) R10 and R12. Findings: process/P1, P4, P5, P7, P8, principles/P2-4, legacy/L4, L5, scope/F10, operability/O4, O7, truth-surface/TS-M4 (record half). Sibling of ticket 67.

## Answer

Resolved 2026-09-06. Ten items: nine done, one declined with a reason. Every decision below is
labelled. Under [ADR-0025](../../../docs/adr/0025-the-assistant-decides-architecture-and-records-it.md)
the unlabelled default is **delegated** — the assistant decided, recorded the reason, and did not
interrupt the owner.

**The durable half is item 1's check, not item 1's sweep.** Ten corrections were the visible task.
Fifteen tickets citing a measurement that never measured the thing is the estate's central defect,
and a sweep fixes fifteen instances while a check stops the sixteenth. So the shape of this ticket
is `verify/cited-truth/`, and the twelve appended corrections are its first output.

### The check

`verify/cited-truth/verify-cited-truth.sh` (+ the pure `cited_truth.py`), in the gate, discovered
by `talk/verify-all.sh`, manifest row `verify/cited-truth/verify-cited-truth.sh | meta | -`.

**What it grades.** Every `.scratch/ecosystem/issues/*.md`:

1. A paragraph offering a TRUTH line as proof that a check is in the gate must cite a line
   `talk/truth.log` actually recorded, whose `hub=` commit **this checkout can read**, whose
   **tree carries a check the ticket names** — or the ticket must carry a **dated** correction
   that names that citation. An undated correction does not dispose of anything; nor does one
   naming a different run.
2. A TRUTH figure (`pass= fail= skip= excluded= total= ceiling=`) quoted on the same text line as
   a run citation must be that run's figure.
3. Ticket 80's other nine corrections, as a table of 19 literal sentences the record must carry or
   must no longer carry — because a correction appended below a claim it never removed leaves the
   estate saying both things at once, which is the shape this ticket exists to end.

**What it refuses to grade, and says so on every run rather than once.**

- Whether the named check is the **right** check for what the ticket built. No script reads that.
  It grades that the check existed in the tree that was measured: necessary, never sufficient.
- Anything outside `issues/*.md`. A figure in `map.md`, an ADR or the deck is ticket 67(d)'s and
  `verify-demo.sh`'s question.
- A figure with no run citation beside it (21 lines today), and a line that says of itself it is a
  fixture, planted, a rehearsal, hypothetical, from the Actions log or not citable (7 lines
  today). **Both populations are counted and printed on every run**, so the ungraded surface is a
  number that moves, not a sentence somebody wrote once. That is the answer to "a disclosed limit
  goes stale like any other assertion".
- Item 6's module (platform's `verify-currency.sh`) and item 10's README (platform's own gate, on
  platform#15). Reading a working copy of another party's README from the hub would be exactly the
  proxy this ticket is about.

**It declares no could-not-look, and there is none to declare** (delegated, the same call
`verify/can-record/` records). Every state it could shrug in is red with its own line: no python,
no git, a **shallow** checkout (in which every historic hub commit is absent, so nothing can be
proved — `truth.yml`'s gate checkout is `fetch-depth: 0`), a missing `talk/truth.log`, a missing
issues directory, a cited commit this checkout cannot resolve (`unreadable-tree`), a cited line
nobody recorded (`no-such-line`).

**Tests at the seam first**, `tests/test_cited_truth.py`, 25 of them, pure: file texts, log text
and an injected `tree_lookup`, so no git and no estate. Red before green, recorded in the pull
request.

### Item by item

1. **Done.** Run 7 is `TRUTH 2026-08-29T12:03Z run=7 hub=918022b … pass=43 fail=11 skip=0
   excluded=2 total=56`. `git ls-tree -r 918022b -- verify/` returns `verify/party/`,
   `verify/proportionality/`, `verify/provenance/` and nothing else. Twelve of the fifteen gained
   the dated correction (21, 25, 26, 32, 36, 41, 42, 43, 47, 49, 50, 52). **Delegated:** 28, 29 and
   40 already carried a dated correction naming the same citation and were left alone — a second
   correction on top of a good one is noise, and the check confirms theirs disposes. Two further
   findings of the same class fell out and were fixed: tickets 83 and 89 quote five figures from
   branch runs (65, 70, 92, 95) that never reached `talk/truth.log`, and now say on the line that
   they are quoted from the Actions log and are not citable. Nothing was hand-written into
   `talk/truth.log`.
2. **Done.** ADR-0008 carries `> **Superseded in part, 2026-07-20 (the owner)…`: the four-panel
   Grafana dashboard the whole "measurable" delivery hung on, rejected in the owner's words at the
   second show and tell. The four signals, the C2P/OSCAL route and the PR-acceptance demotion
   survive; the delivery vehicle does not. ADR-0010 carries
   `> **Superseded in part, 2026-08-28 (eco-system ticket 13 D5)…`: the consumer-side `sunset:` is
   not carried, supersede is publisher-side, and ADR-0023's last decision point is where the rule
   now lives. Its second banner retires the dashboard countdown with ADR-0008's.
3. **Done, in the current vocabulary.** ADR-0019, 0020, 0021 and 0023 each gained one sentence
   naming what its acceptance rests on, with the originating ticket as a link. **Delegated:** the
   line is written as `**Delegated** ([ADR-0025] point 3): the owner agreed …, so this is the
   assistant's decision, recorded and not re-asked. It rests on a bare agree, not a ratification`,
   rather than copied verbatim from ADR-0022, because ADR-0025 point 4 retires the word
   "provisional" *and names this ticket as what re-labels it*. Copying the old wording would have
   re-introduced the retired word into four more files. ADR-0022's own line is re-labelled the
   same way.
   **A correction found while writing it.** The first draft called ticket 13 D5 owner-reasoned,
   on the strength of "Q5 was put to the owner as decision D5 with a three-lens panel verdict".
   The owner's actual words were "I agree with you're more advanced reasoning" — an endorsement of
   the assistant's reasoning and not a reason of the owner's own. Under ADR-0025 point 3 that is a
   bare agree. ADR-0010's banner and ADR-0023's line both say so, and both say why the record of
   2026-08-28 calls it "decided": under the vocabulary of that day a panel verdict outranked a bare
   agree, and ADR-0025 retired the ranking.
4. **Done, and mostly already done.** The `CONTEXT.md` half landed with ticket 89 on 2026-09-05 and
   goes further than this item asked: the **Governed namespace** entry says there is no `CREATE`
   deny *in what the platform renders*, names the window in which that sentence was false, and
   names the gap still open — all three adopters still SERVE the `Deny` in what they composed
   under platform `v2.0.1`, graded by `verify/deny-is-not-a-rung/`. It was not re-edited. What
   this ticket added is the attribution the record never carried: ticket 75 gains a section
   **Assistant-made calls listed here, not re-decided**, whose first entry is the promotion of
   `governed-namespace-requires-claim` to Deny inside an implementation run with no round. Listed,
   **not re-decided**: the owner's Q5 answer disposed of it and ticket 89 executed the reversal.
5. **Done: restored, not deleted. Delegated.** GAPS process rule 1 — "No recommendation attached
   to an architectural question. State the trade, or make the call and record it as the
   assistant's" — is back in `map.md`'s process rules with a dated note. Two reasons. Its second
   half is now ADR-0025 and binds everywhere, so deleting the rule would delete a live rule to
   avoid a redundancy. Its first half still binds the only questions that reach the owner (purpose,
   dates, identities, money, authorisations, a real person) and it was **not** followed: ticket 75
   put twelve questions each with a `➡️ My call:` attached, and nine came back a bare letter.
   Deleting it from `GAPS.md` was the alternative and is refused on a third ground: `GAPS.md` is a
   dated review record and this estate does not rewrite those.
6. **Nothing to do.** Closed 2026-09-05 by ticket 91; not redone. The one hub-side residue is in
   the fact table: `map.md` must not say "The currency controller is retired".
7. **Done.** ADR-0004 gains a dated **Sequencing note** (the cloud plane lands in tuppence beside
   the lifted ledger, the RDS/S3 policies become versioned members of platform's published
   `implementations`, graded at admission in KinD, built after the Pod slice runs once —
   sequencing, not deferral; the ADR stays accepted). ADR-0007's last-mile section loses
   "(proposed — confirm)" and gains a dated **Confirmed** note with the mechanism: the handbook is
   a compose-time render under the artefact's own tag, `verify-fresh.sh` becomes the truth-surface
   script, the summaries become a skill a human runs — and the note says plainly that **nothing in
   the estate renders a handbook today**. ADR-0010's note is item 2's banner; one banner serves
   both and says so.
8. **Done: the runbook is corrected. Delegated; `--remote` declined.** Section 1 said driftwood's
   bring-up is "pointed at the real `policy-as-versioned-driftwood` GitHub repo (mo-09 retired the
   in-cluster git-server this used to seed)". Read `scripts/up.sh` step 3: it copies `gitops/` into
   `.work/`, `git init`s it, commits as `demo@driftwood`, makes an **unsigned** annotated tag
   `v1.0.0`, clones that bare into a lighttpd image, `kind load`s it, and applies a `GitRepository`
   whose `url` is the in-cluster git server. The correction says that, in those words, and adds
   that no signature is verified anywhere in the beat. `--remote` is declined because making the
   cluster reconcile the real remote at a signed tag is GAPS 3.15 and the substance of tickets 16,
   40 and 42 — it needs the venue network at reconcile time, a tag that exists, and the
   gitsign-verifying source controller to make the signature mean anything. Shipping a half-built
   `--remote` would put a second unmeasured claim beside the one this correction removes.
9. **Declined, with the material recorded and marked unapplied. Delegated.** The banner text, the
   org description and the measured repository list are in
   [patches/ticket-80/legacy-signpost.md](../patches/ticket-80/legacy-signpost.md), whose first
   paragraph says nothing in it has been applied. Two reasons, both measured on 2026-09-06: the
   build brief authorises pushes to the hub and the eight enactment repos, and fifteen
   repositories in another organisation are not among them; and `gh auth status` reports scopes
   `delete_repo, gist, read:org, repo, workflow`, so **no** token held here can set an org
   description, whatever the authorisation. `gh api orgs/policy-as-versioned-flux` returns
   `"description": null`, so the finding stands. `gh repo list` returns 16 repositories: the hub
   itself needs no signpost, `apps` is archived and cannot take a commit, and the remaining
   fourteen are the ticket's fourteen, named in the file.
10. **Done, in platform, as a pull request.** `platform/README.md` called the adopter apparatus
    "the `config-base` pattern, one level up", inherited "rather than copy-pasted per
    institution". Measured 2026-09-06 at each adopter's own `origin/main` (driftwood `96f4d0d`,
    tuppence `f7c9f6a`, ludlow `d40b3fb`): three separate gate files, not even a shared filename —
    `.github/scripts/adopter-gate.py` (1087 lines), `.github/scripts/adopter-gate.py` (829),
    `.github/scripts/adopter_gate.py` (1213) — with **131** identical non-comment lines common to
    all three, and no package in platform they come from. The review's "1087, 661 and 1213 … share
    260" was measured on a different day and is not re-quoted. Which it is: **three independent
    forks, on purpose, for this build**, quoted from ticket 75 Q7's folded decision and not
    re-decided. [policy-as-versioned-platform/platform#15](https://github.com/policy-as-versioned-platform/platform/pull/15),
    open, not merged.

### Verified

    bash verify/cited-truth/verify-cited-truth.sh                 PASS (exit 0)
    bash talk/verify-all.sh --selfcheck                           PASS (exit 0)
    bash verify/truth-line/verify-truth-line.sh                   PASS (exit 0)
    bash verify/every-green/verify-every-green.sh                 PASS (exit 0), 110 scripts
    bash verify/adr-supersession/verify-adr-supersession.sh       PASS (exit 0)
    bash verify/record/verify-record-states-the-purpose.sh        PASS (exit 0)
    bash verify/can-record/verify-can-record.sh                   PASS (exit 0)
    .venv/bin/python -m pytest tests/test_cited_truth.py -n0 -q   25 passed
    .venv/bin/python -m mypy twin tests conftest.py …             Success: no issues, 175 files

The full `pytest tests/` was **not** run: load average was 30.74/38.98/61.05 with other suites in
flight, and a number nobody watched arrive is not a number. CI on the branch is quoted in the pull
request instead. The standing reds are unchanged and environment-dependent: invariants 44 and 45,
`test_the_suite_is_green` while either is red, and the serial-only `tests/test_seam1_cli.py` leak.

### Waits on the owner

1. **Item 9, the legacy signpost.** An authorisation to write to fourteen repositories in the
   `policy-as-versioned-flux` organisation, which the build brief does not cover. Material ready
   in `patches/ticket-80/legacy-signpost.md`.
2. **Item 9, the org description.** `admin:org` is not in this token's scopes, so the owner sets it
   (text in the same file) or grants the scope. Identity and authorisation, so it is the owner's
   under ADR-0025 point 6 either way.
3. **`apps`** is archived; a banner needs it unarchived first.
4. **platform#15** is open and waits for the integrator to merge as `pavc-other-hand`.

Map line: [80 — The record matches the code, round 2](issues/80-the-record-matches-the-code-round-2.md) — the fifteen tickets citing run 7 of 2026-08-29 as proof their check is in the gate are corrected (twelve appended, three already had one), and `verify/cited-truth/` refuses the sixteenth: a TRUTH line offered as gate-proof must be a recorded line whose `hub=` tree carries a check the ticket names, or the ticket carries a dated correction; a figure quoted beside its run must be that run's; it declares no could-not-look and counts the ungraded population on every run. ADR-0008 and ADR-0010 gain dated superseded-in-part banners (the rejected dashboard, the withdrawn consumer-side `sunset:`); ADR-0019/0020/0021/0023 say their acceptance rests on a bare agree and ADR-0022's line is re-labelled delegated, the word "provisional" gone; ticket 13's three ADR notes are written; GAPS rule 1 is restored to the map; ticket 75 lists the Deny promotion as an assistant-made call; the runbook says driftwood reconciles an unsigned tag from a git server built on the laptop, `--remote` declined; platform#15 says the adopter apparatus is three independent forks (1087/829/1213 lines, 131 shared); item 9 is declined with its material recorded unapplied, waiting on an authorisation and on `admin:org`.
