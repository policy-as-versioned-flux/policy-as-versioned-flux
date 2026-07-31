# Archiving `policy-as-versioned-flux`

Last migration step (ticket 27, blocked by 26). The new six-org estate under
`estate/` is the faithful-to-intent rebuild; this top-level repo
(`policy-as-versioned-flux` — everything outside `estate/`: `policy/`,
`fleet/`, `docs/`, `research/`, `spikes/`, root `README.md`/`CONTEXT.md`) is
superseded and becomes **research-only**.

## Proof the new estate is green (gate for archiving)

```sh
estate/talk/verify-all.sh
```

Result at archive time (commit `ef84d1636647a...`, 2026-07-31):

```
pass=25 fail=0 skip-live=3
OK: every offline beat is backed by a passing verify-*.sh.
```

The 3 skips are the live Flux-reconcile beats (driftwood/tuppence/ludlow),
which need `estate/talk/up.sh` against a real cluster — expected off-venue,
not a failure. Deck (`estate/talk/deck.md`) and runbook
(`estate/talk/RUNBOOK.md`) are the toured artifacts and both cite this same
verify-all.sh as their honesty gate.

## Checklist

- [x] New estate proven — `estate/talk/verify-all.sh`: 25/25 offline beats
      PASS, 0 fail (3 expected live-cluster skips)
- [x] Deck + runbook exist and reference the estate: `estate/talk/deck.md`,
      `estate/talk/RUNBOOK.md`
- [ ] `policy-as-versioned-flux` repo archived on GitHub (Settings → Archive
      this repository) — **human/GitHub-admin step, cannot be done
      unattended from this environment**
- [ ] Root `README.md` gets a one-line "Archived — superseded by
      `policy-as-versioned-*` estate, see the talk" banner at archive time
      (do this as part of the same GitHub action, not before — the repo
      must stay live and buildable until the archive step itself)

## What "research-only" means going forward

No further feature work lands here. `policy/`, `fleet/`, `docs/`,
`research/`, `spikes/` stay as the historical record the new estate's
`spec.md` and `the-whole-model.md` cite and build on — read, not written.
The six live repos are `platform`, `driftwood`, `tuppence`, `ludlow`,
`nist`, `ico` (see `estate/README.md`).
