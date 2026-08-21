# Archiving `policy-as-versioned-flux`

Last migration step (ticket 27, blocked by 26; separate from, and later than,
mo-12's hub-loses-estate work below). The six-org estate is the
faithful-to-intent rebuild; this top-level repo (`policy-as-versioned-flux` —
`policy/`, `fleet/`, `docs/`, `research/`, `spikes/`, root
`README.md`/`CONTEXT.md`) is superseded and becomes **research-only**.

> **Moved, mo-12 (2026-08-21):** this file used to live at `estate/ARCHIVE.md`
> and its checklist assumed `estate/` was still a committed monorepo tree in
> this hub, holding all six units under it. That shape is gone: the six units
> (`platform`, `driftwood`, `tuppence`, `ludlow`, `nist`, `ico`) are now real,
> separate `policy-as-versioned-*` GitHub repos (git history for the old
> `estate/<unit>/` tree is preserved via `git filter-repo`, not lost), and the
> cross-cutting `verify/` + `talk/` moved to this hub repo's own root. The
> proof block below is a **historical record at a specific commit**, from
> before that split — its counts and the literal `estate/talk/verify-all.sh`
> path are accurate for that commit, not for this repo today. Run
> `talk/verify-all.sh` (see [`talk/RUNBOOK.md`](../talk/RUNBOOK.md)) for the
> current honesty gate.

## Proof the new estate is green (gate for archiving) — historical, pre-split

```sh
estate/talk/verify-all.sh
```

Result at archive time (commit `ef84d1636647a...`, 2026-07-31):

```
pass=25 fail=0 skip-live=3
OK: every offline beat is backed by a passing verify-*.sh.
```

The 3 skips are the live Flux-reconcile beats (driftwood/tuppence/ludlow),
which needed `estate/talk/up.sh` against a real cluster — expected off-venue,
not a failure. Deck and runbook (then `estate/talk/deck.md` /
`estate/talk/RUNBOOK.md`, now `talk/deck.md` / `talk/RUNBOOK.md`) are the
toured artifacts and both cite `verify-all.sh` as their honesty gate, then and
now.

## Checklist

- [x] New estate proven — pre-split: `estate/talk/verify-all.sh` 25/25 offline
      beats PASS, 0 fail (3 expected live-cluster skips), commit
      `ef84d1636647a...`, 2026-07-31. Post-split (mo-12): re-run from
      `talk/verify-all.sh` against the six real repos — see
      [`talk/RUNBOOK.md`](../talk/RUNBOOK.md) for the current count.
- [x] Deck + runbook exist and reference the estate: `talk/deck.md`,
      `talk/RUNBOOK.md`
- [ ] `policy-as-versioned-flux` repo archived on GitHub (Settings → Archive
      this repository) — **human/GitHub-admin step, cannot be done
      unattended from this environment**
- [ ] Root `README.md` gets a one-line "Archived — superseded by
      `policy-as-versioned-*` estate, see the talk" banner at archive time
      (do this as part of the same GitHub action, not before — the repo
      must stay live and buildable until the archive step itself)

## What "research-only" means going forward

No further feature work lands here. `policy/`, `fleet/`, `docs/`,
`research/`, `spikes/` stay as the historical record the estate's `spec.md`
and `the-whole-model.md` cite and build on — read, not written. The six live
repos are `platform`, `driftwood`, `tuppence`, `ludlow`, `nist`, `ico` (see
[`talk/README.md`](../talk/README.md)) — this hub repo itself still holds
`verify/` and `talk/`, and stays live and buildable until the archive step
above.
