# talk — the six-org estate, toured from here

> Moved and corrected, mo-12 (2026-08-21). This file used to live at
> `estate/README.md` and described a **monorepo-style working tree** where
> each top-level directory "becomes its own GitHub repo at split". That
> future-tense framing is gone: the split already happened (mo-08), the hub
> no longer holds a copy of the six units (mo-12, this ticket), and the
> content below describes the arrangement **as it is now**, not as it was
> planned to become.

The six `policy-as-versioned-*` units — `platform`, `driftwood`, `tuppence`,
`ludlow`, `nist`, `ico` — are real, separate GitHub repos in their own orgs
(the prefix `policy-as-versioned-` is the impersonation guardrail — every org
carries it). This hub repo (`policy-as-versioned-flux`) does not hold a copy
of them; [`../clone-estate.sh`](../clone-estate.sh) fetches a disposable local
checkout into `.estate-clone/` (git-ignored) whenever `up.sh` or
`verify-all.sh` needs to see them.

| Repo | Role |
|---|---|
| [`policy-as-versioned-platform`](https://github.com/policy-as-versioned-platform/platform) | The shared discipline (Flux templates, FAIR engine, graded cage→OSCAL risk, shift-left, OSCAL, war-gamer). Institutions pin it as a signed dependency. |
| [`policy-as-versioned-driftwood`](https://github.com/policy-as-versioned-driftwood/driftwood) | Institution — e-comm, PCI+GDPR, **teaching default**. Audit-heavy (loosest £). Owns a KinD cluster; the provenance base. |
| [`policy-as-versioned-tuppence`](https://github.com/policy-as-versioned-tuppence/tuppence) | Institution — fintech, FCA+PCI+GDPR. Toward-strict. |
| [`policy-as-versioned-ludlow`](https://github.com/policy-as-versioned-ludlow/ludlow) | Institution — US health, HIPAA. Deny-heavy (strictest £), long-life data. |
| [`policy-as-versioned-nist`](https://github.com/policy-as-versioned-nist/nist) | Regulator — real 800-53 OSCAL controls catalog. |
| [`policy-as-versioned-ico`](https://github.com/policy-as-versioned-ico/ico) | Regulator — small signed penalty schema from real public fine magnitudes. |

Dependency direction: institutions pin `nist` **directly** (own
`gotk-sync-nist.yaml` + `nist-pin-configmap.yaml` each), and pin `platform`
directly; `ico`'s penalty schema arrives by a separate signed-feed route, not
as a `GitRepository`. (`estate/README.md`'s old `nist`/`ico` → `platform` →
institutions chain was corrected by ticket 07 — regulator pins stay direct on
purpose, so `platform` can't withhold regulatory currency.)

Two cross-cutting areas stay **in this hub repo**, not split out to a
`policy-as-versioned-*` org — they belong to no single party, which is what a
cross-party comparison needs:

- [`../verify/`](../verify/) — the cross-institution money-shot beats
  (proportionality, provenance, party/role checking, the feed contract, the £ seam).
- `talk/` (this directory) — the Marp deck + demo runbook that tour the whole
  estate.

## Touring the talk

```sh
talk/verify-all.sh    # the truth surface: every verify*.sh in the estate, graded PASS/FAIL/SKIP
talk/up.sh            # idempotent bring-up; clones the six units first (needs network)
```

See [`talk/deck.md`](deck.md) (Marp) and [`talk/RUNBOOK.md`](RUNBOOK.md).

## The end-to-end harness

`verify/e2e/` drives the seven NORTH-STAR §4 steps inside the gate (ticket 52). One script per
step, each discovered by `talk/verify-all.sh` as its own graded sub-result:

| step | script | built by |
|---|---|---|
| 1 | `verify-e2e-step1-regulator-publishes.sh` | 21 |
| 2 | `verify-e2e-step2-renovate-pins-and-reprices.sh` | 25 |
| 3 | `verify-e2e-step3-price-crosses-band-pr-opens.sh` | 25 (python half), 26 (cluster half) |
| 4 | `verify-e2e-step4-flux-reconciles-cage.sh` | 40 |
| 5 | `verify-e2e-step5-twin-forecasts.sh` | 49 |
| 6 | `verify-e2e-step6-provenance.sh` | 32 |
| 7 | `verify-e2e-step7-honesty.sh` | 52 |

Steps 2 and 3 became real with ticket 25 and run offline, against the committed estate, in
about a second each:

- **Step 2** copies an adopter's committed tree to a temp directory, composes it once, bumps one
  pinned feed version in its own `party.yaml` — the single edit a merged Renovate PR makes — and
  composes again. It fails if `prices[]` comes back identical, and exits 3 naming what is
  missing when no adopter pins a priceable feed that has a newer version on disk. No repo is
  touched: the copy is thrown away.
- **Step 3** (python half) reads the adopter's OWN signed appetite band off `party.yaml`, finds
  the residual that crosses it, and shows the tier change, attributed to the version the
  adopter's `selection-policy` package publishes. It then runs `platform/wargamer/tier_pr.py
  run --dry-run` and asserts the proposer would open a pull request editing the tier
  declaration. **Nothing is opened and nothing is written** — the dry run works on a throwaway
  copy in a directory that is not a git repo, so a real push could not succeed even if the flag
  were ignored. The tier landing in force is step 4's fact, not this one's.

Step N prints `E2E step N <name>` and then `PASS:`, `FAIL:` or `SKIP: step N not built yet,
owned by ticket NN` until its ticket lands. Step 7 runs steps 1 to 6 with a 120s timeout each
and fails if any does not end on one of those three lines. `lib.sh` gives the steps `say`,
`pass`, `fail`, `skip`, the estate path and `cluster_up`/`cluster_down` for the ephemeral KinD
cluster `pav-e2e`, deleted on exit by trap. A step that needs a signed tag not yet cut reads
SKIP naming the tag; the scheduled truth run is the only number that counts.

## Quick start (driftwood — the live one)

```sh
../clone-estate.sh                          # fetch the six units into .estate-clone/
.estate-clone/driftwood/scripts/up.sh       # idempotent: KinD + Flux + reconcile healthy
.estate-clone/driftwood/verify-reconcile.sh
.estate-clone/driftwood/scripts/reset.sh    # tear down
```

See [`../.scratch/talk-spec/the-whole-model.md`](../.scratch/talk-spec/the-whole-model.md) and
[`../.scratch/talk-spec/spec.md`](../.scratch/talk-spec/spec.md) for the full thesis.
