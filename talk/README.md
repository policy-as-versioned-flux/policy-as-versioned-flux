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
  (proportionality, provenance, party/role checking).
- `talk/` (this directory) — the Marp deck + demo runbook that tour the whole
  estate.

## Touring the talk

```sh
talk/verify-all.sh    # the truth surface: every verify*.sh in the estate, graded PASS/FAIL/SKIP
talk/up.sh            # idempotent bring-up; clones the six units first (needs network)
```

See [`talk/deck.md`](deck.md) (Marp) and [`talk/RUNBOOK.md`](RUNBOOK.md).

## Quick start (driftwood — the live one)

```sh
../clone-estate.sh                          # fetch the six units into .estate-clone/
.estate-clone/driftwood/scripts/up.sh       # idempotent: KinD + Flux + reconcile healthy
.estate-clone/driftwood/verify-reconcile.sh
.estate-clone/driftwood/scripts/reset.sh    # tear down
```

See [`../.scratch/talk-spec/the-whole-model.md`](../.scratch/talk-spec/the-whole-model.md) and
[`../.scratch/talk-spec/spec.md`](../.scratch/talk-spec/spec.md) for the full thesis.
