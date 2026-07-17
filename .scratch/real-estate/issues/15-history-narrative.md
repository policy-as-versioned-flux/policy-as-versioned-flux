# 15 — Curated history narrative

**What to build:** The newcomer-readable story of how this project got here — the org split, the webhook-flattening discovery and its fix, the signing mistakes kept as honest records, the go-git tag-resolution saga, the componentization — written as a narrative document in the hub, with links into the raw history. The raw history itself is untouched: it stays as the audit trail (the grilled decision: no rewrite ever in place; "clean history" arrives later as a fresh-org redeploy, which is this epic's sequel, not a ticket in it).

**Blocked by:** None — can start immediately (best written last, when the epic's own story is part of it).

**Status:** done

- [x] A history narrative in the hub docs a newcomer can read in one sitting
- [x] Each episode links to the real commits/PRs/tags it describes
- [x] The fresh-org redeploy endgame and two-org endstate recorded as the deferred decisions they are

## Comments

Done 2026-07-16, written last as planned — the real-estate epic's own story (componentization, the
five-team roster, the bugs found live) is part of the narrative it tells.

`docs/HISTORY.md` in the hub, linked from the README's "Start here" table. Three episodes: the
faithful-floor mechanism-proving phase (webhook-flattening discovery, the go-git tag-resolution
saga, the signing-mistake correction kept as an honest record), the show+tell demo that exposed the
estate as a cardboard cutout, and this epic's answer to that.

**Every commit/PR link verified real before writing the prose around it**, not assumed from
memory: `git cat-file -e` confirmed `1466fdc` (policy) and `99971a8`/`5f8d861` (fleet) exist;
`gh pr view` confirmed `fleet#11`'s and `fleet#19`'s real titles. `apps`' README (already updated
in ticket 08) does the forward-pointing half of this document's story; this document does the
narrative half.

Two deferred decisions named explicitly, not folded into scope: the two-org split (components org
/ model org) and the fresh-org redeploy (the "clean history" a demo viewer asked for — answered as
this project's sequel, a reproducibility proof by actually redeploying fresh, not a rewrite of
this org's real, thrashy history).

## Follow-up (2026-07-17)

This Comments section is dated the day the ticket was written; `docs/HISTORY.md` itself has since
grown a substantial addition (the adversarial-verification hardening wave — see ticket 09's and
this file's own follow-ups) that this section doesn't mention. Noted here rather than left
silently out of date: the document is current, this bookkeeping paragraph just lagged it by a day.
