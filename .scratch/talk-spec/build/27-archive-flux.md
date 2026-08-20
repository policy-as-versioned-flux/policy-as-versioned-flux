# 27 — Archive `policy-as-versioned-flux`

**What to build:** Once the new estate stands and the demo runs green, archive the old `policy-as-versioned-flux` estate — the last migration step.

**Blocked by:** 26

**Status:** NOT DONE — neither AC met; do not archive yet

- [ ] New estate proven (deck + runbook green) — **not currently true**: `bash estate/talk/verify-all.sh` fails 1 of 25 offline beats (honesty/reflexive, ticket 25). `estate/ARCHIVE.md`'s own "proof the new estate is green" section cites `pass=25 fail=0 skip-live=3` at "commit `ef84d1636647a...`" — but that commit (`ef84d16`, 2026-07-31, "Estate build wave 1: tickets 01,02") only ever contained tickets 01+02; `estate/talk/verify-all.sh` did not exist yet at that commit (`git show ef84d16:estate/talk/verify-all.sh` → `fatal: path ... exists on disk, but not in 'ef84d16'`). The cited evidence is not reproducible and cannot have been produced by that command at that commit — `ARCHIVE.md`'s green claim is unverifiable as written, independent of today's real 24/25
- [ ] `policy-as-versioned-flux` archived (research-only, superseded) — **not done**: root `README.md` carries no "Archived" banner; `ARCHIVE.md`'s own checklist still has both remaining boxes unticked (`repo archived on GitHub` — human/admin step; `README banner` — deliberately deferred to the same action). Nothing to redo here; just not yet reached

## Comments

- 2026-08-20 (audit mo-02): this is the clearest case in the audit of the board not matching reality — `ready-for-agent` was wrong in the opposite direction from most other tickets: it undersold nothing, it just never got corrected once `estate/ARCHIVE.md` was written claiming the gate had already passed. That claim cites a commit that predates the very script it quotes output from, so it was never true as written, and today's real run is 24/25 (ticket 25's bug) rather than the claimed 25/25 regardless. Recommend: fix ticket 25, get a real `pass=25 fail=0` `verify-all.sh` run at the actual `HEAD` commit, update `ARCHIVE.md`'s evidence block to cite that real run, then this ticket's first AC is genuinely met. The second AC (GitHub archive + README banner) is explicitly a human/admin action per `ARCHIVE.md` and was never expected to be agent-doable. Status corrected from `ready-for-agent` to `NOT DONE`.
