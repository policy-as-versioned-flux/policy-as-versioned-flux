# Demo runbook — touring the estate live

The presenter's operational guide for [`deck.md`](deck.md). Every slide tagged
**[LIVE]** runs a real command against the local KinD estate; this runbook brings
that estate up **idempotently, offline-safe, resettable between runs, and
audience-modular** (re-foreground the institution that matches the room, zero
rebuild). No slide stands in for a thing that doesn't work.

> Thesis in one line: **governance is a proportionate, informed, continuously
> re-tuned response to quantified risk — and versioning the whole chain, with
> every actor attestable, is how proportionality stays honest.**

---

## 0. Pre-flight — before the audience is watching

Prove the whole deck is honest in one command (no cluster, no network needed):

```sh
estate/talk/verify-all.sh
# -> 25 offline beats PASS; the 3 live reconcile beats SKIP-live until the estate is up.
```

Bring the estate up (idempotent — safe to re-run any time to converge):

```sh
estate/talk/up.sh            # driftwood (teaching default) + all platform layers
                             # that carry the live beats — this is enough for most rooms
```

Now assert including the live reconcile beats:

```sh
estate/talk/verify-all.sh --live
```

Required CLIs: `kind`, `kubectl`, `flux`, `kyverno`, `python3`, `openssl`, `jq`.
The offline gate needs only `python3`/`kyverno`/`openssl`; the live estate needs
`kind`/`flux`. `up.sh` guards for these and tells you what's missing.

**Offline-safe:** every area's `up.sh` is `timeout`-bounded — a slow or absent
image pull just means "re-run", never a hang. `up.sh` steps over a degraded layer
and reports it rather than blocking. There is no venue-Wi-Fi dependency in any
**[LIVE]** beat; the FAIR/TCoR/proportionality/provenance maths is pure and local.

---

## 1. Bring-up order (what `up.sh` does for you)

`up.sh` is a thin orchestrator over the per-area `up.sh` scripts each ticket
shipped. Dependency order (it never creates/deletes a cluster itself — the
institution `up.sh` does, reusing an existing same-named KinD cluster):

1. `estate/driftwood/scripts/up.sh` — KinD `driftwood` + Flux + signed in-cluster
   git source + reconcile. **The base cluster carries every platform layer and
   every live beat.**
2. Platform layers on that cluster, in order: `identity` (SPIRE+Istio+OpenBao) →
   `posture` → `currency-controller` → `graded` → `access` → `eud` →
   `tuppence/reset` (the `customer-accounts-reset` workload flagship).
3. Other institution clusters **only when the room needs them** (see §3).

```sh
estate/talk/up.sh driftwood   # base + platform layers (default)
estate/talk/up.sh tuppence    # + the tuppence institution cluster
estate/talk/up.sh ludlow      # + the ludlow institution cluster
estate/talk/up.sh all         # all three institution clusters (beefy laptop)
```

The **proportionality money-shot** (Beat 3) is proven **offline** by
`verify-proportionality.sh` against both institutions' bands — you do **not**
need ludlow's cluster standing for that beat. Stand ludlow/tuppence up only if
you want their reconcile beat live for that room.

---

## 2. The beat-by-beat live script

Each **[LIVE]** beat is one command; each exits non-zero if the beat would fail
on stage. Full mapping is in [`verify-all.sh`](verify-all.sh); the deck ordering:

| Beat | Command | Backed by |
|---|---|---|
| 1. Breach cost (narrated) | `python3 estate/platform/fair/fair.py summary estate/platform/fair/scenarios/driftwood-cart-pii.json` | fair.py selfcheck |
| 2. Versioned dependency | `estate/platform/distribution/verify-coexistence.sh` · `…/verify-orphan-guard.sh` · `…/verify-retirement.sh` | kyverno-test |
| 2b. Shift-left + conditional | `estate/platform/shift-left/verify-shift-left.sh` · `estate/platform/policy/verify-conditional.sh` | kyverno CLI |
| **3. Proportionality ⭐** | `estate/verify/proportionality/verify-proportionality.sh` · `estate/platform/risk/verify-risk-tuned.sh` | FAIR + kyverno |
| 3b. Graded / TCoR | `estate/platform/graded/verify-graded.sh` · `estate/platform/tcor/verify-tcor.sh` | cage.py + tcor.py |
| 4. Living loop | `estate/platform/feeds/verify-feeds.sh` · `…/wardley/verify-wardley.sh` · `…/wargamer/verify-wargamer.sh` | feeds + wargamer |
| 4b. Honest today | `estate/platform/honesty/verify-honesty.sh` | calibration+integrity |
| **5. Provenance** | `estate/verify/provenance/verify-provenance.sh` · `…/identity/verify-identity.sh` · `…/posture/verify-posture-projection.sh` | SPIFFE chain |
| 5b. Reach + secrets | `estate/tuppence/reset/verify-reach-secrets.sh` | Istio+OpenBao glob |
| 5c. Human/device | `estate/platform/access/verify-access.sh` · `…/break-glass/verify-break-glass.sh` · `…/eud/verify-eud.sh` | Pomerium+tpm_devid |
| — Reconcile (live) | `estate/{driftwood,tuppence,ludlow}/verify-reconcile.sh` | live cluster |

Balance-sheet (Beat 6) is **narrated** — no command; it reads the £ the live
beats already moved.

---

## 3. Audience-modular — re-foreground the room, zero rebuild

The institution you narrate is a **kubectx switch + which scenario you point at**,
not a rebuild. `driftwood` (general/e-comm) is the teaching default; foreground
`tuppence` (fintech/FCA+PCI) or `ludlow` (health/HIPAA) to match the room:

```sh
estate/talk/up.sh foreground tuppence    # point kubectl at kind-tuppence
estate/talk/up.sh foreground ludlow
estate/talk/up.sh foreground driftwood
```

If that institution's cluster isn't up yet, `foreground` tells you the one
command to stand it up (`estate/talk/up.sh <inst>`). The proportionality
comparison and the FAIR/TCoR maths are per-institution **inputs** to the same
engine — so re-foregrounding is instant; only a live reconcile beat for that
specific institution needs its cluster running.

Per-room emphasis:

- **tuppence / fintech** — lead the workload-identity flagship (Beat 5b:
  `customer-accounts-reset` loses reach *and* its secret out of currency).
- **ludlow / health** — lead the proportionality money-shot (Beat 3: the strict
  band flips the same control to Deny; long-life PHI, HNDL/PQ real).
- **driftwood / general** — the full spine as written.

---

## 4. Reset between runs

Fast, idempotent, and it does **not** delete the cluster (seconds, not minutes):

```sh
estate/driftwood/scripts/reset.sh soft    # re-seed the git source, keep cluster+Flux, re-converge
```

Full teardown (start clean / end of day):

```sh
estate/driftwood/scripts/reset.sh         # kind delete cluster driftwood
estate/tuppence/scripts/reset.sh          # only if you stood tuppence up
estate/ludlow/scripts/reset.sh            # only if you stood ludlow up
```

After any reset, `estate/talk/up.sh` brings everything back idempotently. The
offline verify beats never need a reset — they are pure and stateless.

---

## 5. The honest footer — say it out loud

Nothing is rounded up to 100%. Backed by [`verify-all.sh`](verify-all.sh):
**25 offline beats pass with no cluster and no network**; the **3 institution
reconcile beats** are the only ones that need a brought-up cluster (`--live`).

Narrated-not-live (real + grounded, gestured not productionised): the
breach-cost open and the balance-sheet close; regulator-publishes-penalties-as-
code as an *industry* norm; full underwriting/board consumption; Windows/Linux
device trust on **UTM vTPM VMs (emulated EK), narrated as virtual** — the one
genuine live hardware root is the **Mac Secure Enclave**. Every one of these is
named and scoped, which is exactly the honesty the thesis argues for.
