# 02 — Audit all 27 talk-spec build ticket statuses

Type: task
Status: done (2026-08-20)
Blocked by: none

## Question

What is actually done in `.scratch/talk-spec/build/`? 25 of 27 tickets read `Status: ready-for-agent`
despite the estate demonstrably working; only 14 and 17 carry honest `REOPENED — NOT DONE` detail.
The board cannot be trusted as a picture of reality.

**The job:** for each ticket 01–27, verify its acceptance criteria against the actual tree and the
verify scripts, then set an accurate Status and tick/untick its ACs with a citation (file, test, or
command output) — the same discipline the `twin/` capability checklists use. Where a ticket is
genuinely incomplete, say so with the specific unmet AC rather than a blanket status.

**Method (owner's instruction):** parallel, medium-effort Sonnet agents, one per ticket or small
batch. Do not let an agent tick an AC without a citation.

Report the corrected done/not-done split. Expect this to surface work nobody is tracking.

## Answer

Audited all 27 tickets, one at a time, against the real tree and by actually running the relevant
`verify-*.sh` (offline; no live cluster was reachable — see below). Corrected split:

- **19 done**: 01, 03, 04, 05, 06, 07, 09, 10, 11, 12, 13, 15, 16, 18, 19, 21, 22, 23, 24
- **8 not fully done**:
  - **02, 08** — `PARTIAL`. Scaffolding/config real and correct; the literal live-cluster ACs
    (KinD up, Flux reconciling) are unverified in this environment — no Docker daemon was reachable
    (`docker info` hung >120s) and `kind get clusters` was empty.
  - **14, 17** — already `REOPENED — NOT DONE` before this audit (the two the meta-ticket named as
    honest). Re-confirmed: no commit touches either area since the 2026-07-31 live bring-up that
    found the bug, so both stand unchanged.
  - **20** — downgraded from `ready-for-agent` to `PARTIAL`. Real gap, not an environment limit: only
    VM *specs* and `tpm_devid` enrolment *templates* exist; no UTM VM has ever actually been built
    (`swtpm`/`utmctl` not installed anywhere checkable, `estate/platform/eud/vms/` holds only JSON
    specs, no disk images).
  - **25** — downgraded from `ready-for-agent` to `REOPENED — NOT DONE`. Real, reproducible bug, not
    an environment gap: `estate/platform/honesty/verify-honesty.sh` fails —
    `reflexive.py`'s `feed_integrity()` checks for the **private** signing key file (deliberately
    gitignored) instead of the **public** one actually used for verification, so
    `signing_key_present` is always `False` on a clean checkout. Isolating the rest:
    `reflexive.py govern-self` alone returns `passes_own_test: true` — only this one flag is wrong.
    Not fixed here (out of scope for an audit-only ticket).
  - **26** — downgraded to `REOPENED — NOT DONE` for the same reason as 25: the deck/runbook
    artifacts are solid, but the ticket's own AC ("every demo-live claim backed by a passing
    verify-*.sh") is false today because of 25's bug — `estate/talk/verify-all.sh` is 24/25 offline
    beats, not 25/25.
  - **27** — downgraded to `NOT DONE`. `estate/ARCHIVE.md` cites `pass=25 fail=0` at commit
    `ef84d1636647a...`, but that commit only ever contained tickets 01+02 —
    `estate/talk/verify-all.sh` did not exist yet at that commit
    (`git show ef84d16:estate/talk/verify-all.sh` → path not found). The citation is unverifiable as
    written, independent of today's real 24/25. Neither AC (estate proven green; repo archived on
    GitHub) is met; the archive step itself is explicitly a human/admin action per `ARCHIVE.md`.

**Work nobody was tracking, surfaced by this audit:** the ticket-25 signing-key bug (real code
defect), and the ticket-27 `ARCHIVE.md` evidence citation that cites a commit predating the script
it quotes — both invisible from the board's blanket `ready-for-agent` labels. Everything else that
was previously unlabelled turned out to be genuinely built and passing offline.

Status: resolved. See each ticket's own `## Comments` for its individual citation trail.
