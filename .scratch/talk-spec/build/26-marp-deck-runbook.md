# 26 — Marp deck + demo runbook

**What to build:** The first-class Marp deck authored *against the built estate* (every demo-live claim real) + an idempotent, offline-safe, resettable, audience-modular demo runbook.

**Blocked by:** 09, 13, 17, 19, 22, 24

**Status:** REOPENED — NOT DONE. Deck + runbook are real and complete; the honesty gate this ticket's own AC3 requires currently fails (ticket 25's bug)

- [x] Marp deck: breach-cost open → versioned dependency → proportionality (live) → living loop (live) → provenance (live) → balance-sheet close — `estate/talk/deck.md` (real `marp: true` frontmatter) headings in order: `Beat 1 ... cost? [NARRATED]`, `Beat 2 — versioned dependency [LIVE]`, `Beat 3 — Proportionality [LIVE] ⭐`, `Beat 4 — the living loop [LIVE]`, `Beat 5 — Provenance [LIVE]`, `Beat 6 — risk on the balance sheet [NARRATED]` — exact match
- [x] Runbook brings the estate up idempotently, offline-safe, resettable; audience-modular (re-foreground any institution) — `estate/talk/RUNBOOK.md` §3 "Audience-modular — re-foreground the room, zero rebuild" (`up.sh foreground {tuppence,ludlow,driftwood}`), §"Fast, idempotent... reset" (`reset.sh soft` / full); tree-verified, not live-executed here (no cluster, see ticket 02)
- [ ] Every demo-live claim backed by a passing `verify-*.sh` — **FAILS today**: `bash estate/talk/verify-all.sh` → 1 offline beat fails: `the number is honest today (calibration+integrity)|estate/platform/honesty/verify-honesty.sh` → `FAIL: reflexive selfcheck failed` (ticket 25's bug). `RUNBOOK.md`'s own beat table cites this exact script for its "Beat 4b — is the number honest today? [LIVE]" slide, so the deck currently makes one claim its own honesty gate does not back

## Comments

- 2026-08-20 (audit mo-02): the deck and runbook artifacts themselves are genuinely well-built and complete (AC1/AC2 fully tree-verified). This ticket is REOPENED for the same reason as 25: `verify-honesty.sh`'s reflexive selfcheck fails today (`signing_key_present` checks the wrong key file), so the deck's own stated honesty gate does not currently back all its LIVE claims. Fixing ticket 25's one-line bug should close this AC too — tracked there, not fixed here (out of scope for an audit ticket). Status corrected from `ready-for-agent` to `REOPENED — NOT DONE`.
