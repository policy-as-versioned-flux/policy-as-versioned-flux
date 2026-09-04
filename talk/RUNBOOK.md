# Demo runbook — touring the estate live

The presenter's operational guide for [`deck.md`](deck.md). Every slide tagged
**[LIVE]** runs a real command against the local KinD estate; this runbook brings
that estate up **idempotently, resettable between runs, and audience-modular**
(re-foreground the institution that matches the room, zero rebuild). No slide
stands in for a thing that doesn't work.

> Thesis in one line: **governance is a proportionate, informed, continuously
> re-tuned response to quantified risk — and versioning the whole chain, with
> every actor attestable, is how proportionality stays honest.**

**No venue-Wi-Fi independence — abandoned, mo-12 (2026-08-21).** This runbook
used to claim *"there is no venue-Wi-Fi dependency in any [LIVE] beat"* and
described the whole estate as **offline-safe**. That guarantee is gone, not
quietly dropped: the six units (`platform`, `driftwood`, `tuppence`, `ludlow`,
`nist`, `ico`) are now real, separate GitHub repos, not directories committed
in this hub, so both `up.sh` and `verify-all.sh` start by fetching them with
[`../clone-estate.sh`](../clone-estate.sh) — network is required, at minimum on
first run at a venue. This was a deliberate trade (ticket 07/09): a mirrored,
offline-safe in-cluster git server made the six "live organisations" a fiction
Flux never actually reconciled from the internet; real GitHub repos make the
demo's own claim true, at the cost of the offline guarantee. Bring a hotspot,
or run `../clone-estate.sh` before you lose signal — `.estate-clone/` then
stays usable offline for the rest of that session (`up.sh`/`verify-all.sh`
skip re-cloning a unit already present; pass `--refresh` to force a re-clone).

---

## 0. Pre-flight — before the audience is watching

Prove the whole deck is honest in one command (needs network on first run, to
clone the six units — see above; no cluster needed):

```sh
talk/verify-all.sh
# -> clones the six units into .estate-clone/ (skipped if already present), then
#    runs every verify*.sh it finds there and in verify/. Each ends PASS (observed
#    true), FAIL (observed false) or SKIP (could not look, exit 3, with a reason).
#    The last line is the TRUTH stamp: date, run number, commits, counts. Quote that.
```

Bring the estate up (idempotent — safe to re-run any time to converge):

```sh
talk/up.sh                   # driftwood (teaching default) + all platform layers
                             # that carry the live beats — this is enough for most rooms
```

Now assert including the live reconcile beats:

```sh
talk/verify-all.sh --live
```

Required CLIs: `git`, `kind`, `kubectl`, `flux`, `kyverno`, `python3`,
`openssl`, `jq`. The offline gate needs `git` (for the clone) plus
`python3`/`kyverno`/`openssl`; the live estate also needs `kind`/`flux`.
`up.sh` guards for these and tells you what's missing.

Every area's `up.sh` is still `timeout`-bounded — a slow or absent image pull
just means "re-run", never a hang. `up.sh` steps over a degraded layer and
reports it rather than blocking. That resilience is real; it is the network
dependency itself, not the handling of a slow network, that changed.

---

**The local clock (ticket 92).** The model-backed steps of the eco-system's clock
run from this machine, not from GitHub: `talk/local-clock.sh --adopter driftwood`
runs them once by hand, `--inject signal.yaml` rehearses with a made-up dated
signal that is marked injected everywhere it lands, and `talk/local-clock.plist`
schedules it with launchd. Prerequisites, what it writes, how to read it and how
to stop it are in [`local-clock.README.md`](local-clock.README.md). Nothing it
does is citable; the gate reads only its marker.

## 1. Bring-up order (what `up.sh` does for you)

`up.sh` is a thin orchestrator over the per-area `up.sh` scripts each ticket
shipped. Dependency order (it never creates/deletes a cluster itself — the
institution `up.sh` does, reusing an existing same-named KinD cluster):

1. `.estate-clone/driftwood/scripts/up.sh` — KinD `driftwood` + Flux, pointed at the
   real `policy-as-versioned-driftwood` GitHub repo (mo-09 retired the in-cluster
   git-server this used to seed) + reconcile. **The base cluster carries every
   platform layer and every live beat.**
2. Platform layers on that cluster, in order: `identity` (SPIRE+Istio+OpenBao) →
   `posture` → `currency-controller` → `graded` → `access` → `eud` →
   `tuppence/reset` (the `customer-accounts-reset` workload flagship).
3. Other institution clusters **only when the room needs them** (see §3).

```sh
talk/up.sh driftwood   # base + platform layers (default)
talk/up.sh tuppence    # + the tuppence institution cluster
talk/up.sh ludlow      # + the ludlow institution cluster
talk/up.sh all         # all three institution clusters (beefy laptop)
```

The **proportionality money-shot** (Beat 3) is proven **offline** by
`verify-proportionality.sh` against both institutions' bands — you do **not**
need ludlow's cluster standing for that beat. Stand ludlow/tuppence up only if
you want their reconcile beat live for that room.

---

## 2. The beat-by-beat live script

> **SUPERSEDED 2026-08-29 (eco-system ticket 47).** The beat table below is kept
> as the record and is not rewritten. The deck's beats are no longer hand-kept
> here: they are the seven NORTH-STAR §4 steps, generated into
> [`deck.md`](deck.md) by [`build_deck.py`](build_deck.py) from the capture the
> truth surface wrote for each step's check, carrying that run's own grade.
> [`verify-demo.sh`](verify-demo.sh) refuses the deck if a beat's status, a
> cited capture or a figure disagrees with the run. Read the beat list there;
> read this table only for what the July tour did.
>
> **Rebuild cadence (2026-09-03, ticket 66).** The deck describes one recorded
> run, named in its own header (`run=N`) and quoted TRUTH line, and the check
> grades it against that run's committed captures. The clock never rebuilds it.
> Before a talk: `python3 talk/build_deck.py` (the newest recorded run; `--run N`
> for a chosen one), read the beats, commit `talk/deck.md`. `verify-demo.sh`
> prints a note when a newer run has been recorded since; that is a prompt to
> rebuild, not a red.


Each **[LIVE]** beat is one command; each exits non-zero if the beat would fail
on stage. The gate runs every script by discovery, so there is no mapping to keep; the deck ordering:

| Beat | Command | Backed by |
|---|---|---|
| 1. Breach cost (narrated) | `python3 .estate-clone/platform/fair/fair.py summary .estate-clone/platform/fair/scenarios/driftwood-cart-pii.json` | fair.py selfcheck |
| 2. Versioned dependency | `.estate-clone/platform/distribution/verify-coexistence.sh` · `…/verify-orphan-guard.sh` · `…/verify-retirement.sh` | kyverno-test |
| 2b. Shift-left + conditional | `.estate-clone/platform/shift-left/verify-shift-left.sh` · `.estate-clone/platform/policy/verify-conditional.sh` | kyverno CLI |
| **3. Proportionality ⭐** | `verify/proportionality/verify-proportionality.sh` · `.estate-clone/platform/risk/verify-risk-tuned.sh` | FAIR + kyverno |
| 3b. Graded / TCoR | `.estate-clone/platform/graded/verify-graded.sh` · `.estate-clone/platform/tcor/verify-tcor.sh` | cage.py + tcor.py |
| 4. Living loop | `.estate-clone/platform/feeds/verify-feeds.sh` · `…/wardley/verify-wardley.sh` · `…/wargamer/verify-wargamer.sh` | feeds + wargamer |
| 4b. Honest today | `.estate-clone/platform/honesty/verify-honesty.sh` | calibration+integrity |
| **5. Provenance** | `verify/provenance/verify-provenance.sh` · `…/identity/verify-identity.sh` · `…/posture/verify-posture-projection.sh` | SPIFFE chain |
| 5b. Reach + secrets | `.estate-clone/tuppence/reset/verify-reach-secrets.sh` | Istio+OpenBao glob |
| 5c. Human/device | `.estate-clone/platform/access/verify-access.sh` · `…/break-glass/verify-break-glass.sh` · `…/eud/verify-eud.sh` | Pomerium+tpm_devid |
| — Reconcile (live) | `.estate-clone/{driftwood,tuppence,ludlow}/verify-reconcile.sh` | live cluster |

Balance-sheet (Beat 6) is **narrated** — no command; it reads the £ the live
beats already moved.

---

## 3. Audience-modular — re-foreground the room, zero rebuild

The institution you narrate is a **kubectx switch + which scenario you point at**,
not a rebuild. `driftwood` (general/e-comm) is the teaching default; foreground
`tuppence` (fintech/FCA+PCI) or `ludlow` (health/HIPAA) to match the room:

```sh
talk/up.sh foreground tuppence    # point kubectl at kind-tuppence
talk/up.sh foreground ludlow
talk/up.sh foreground driftwood
```

If that institution's cluster isn't up yet, `foreground` tells you the one
command to stand it up (`talk/up.sh <inst>`). The proportionality
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
.estate-clone/driftwood/scripts/reset.sh soft    # re-seed the git source, keep cluster+Flux, re-converge
```

Full teardown (start clean / end of day):

```sh
.estate-clone/driftwood/scripts/reset.sh         # kind delete cluster driftwood
.estate-clone/tuppence/scripts/reset.sh          # only if you stood tuppence up
.estate-clone/ludlow/scripts/reset.sh            # only if you stood ludlow up
```

After any reset, `talk/up.sh` brings everything back idempotently. The
offline verify beats never need a reset — they are pure and stateless.

---

## 5. The honest footer — say it out loud

Nothing is rounded up to 100%. Backed by [`verify-all.sh`](verify-all.sh):
read the counts from the newest `TRUTH` line in [`truth.log`](truth.log), which
the `truth` workflow writes daily. A script that needs a cluster and cannot see
one says SKIP, never PASS. `--live` turns those SKIPs into FAILs.

Narrated-not-live (real + grounded, gestured not productionised): the
breach-cost open and the balance-sheet close; regulator-publishes-penalties-as-
code as an *industry* norm; full underwriting/board consumption; Windows/Linux
device trust on **UTM vTPM VMs (emulated EK), narrated as virtual** — the one
genuine live hardware root is the **Mac Secure Enclave**. Every one of these is
named and scoped, which is exactly the honesty the thesis argues for.

---

## 6. Reading a red gate

`talk/verify-all.sh` grades every script it discovers by exit code, exactly
three outcomes:

- **PASS** (exit 0) — observed true.
- **SKIP** (exit 3) — could not look; the reason is on the script's last line
  (`SKIP: ...`). Not a failure offline — no cluster is guaranteed present. It
  **does** count as FAIL under `--live`: a script that could not observe its
  target on a run you asked to be live is not honestly green.
- **FAIL** (any other exit) — observed false, errored, or timed out. The row
  names the reason and, for anything past the first line, points at that
  script's capture: `talk/captures/<slug>.out`.

(EXCLUDED is a fourth row, but not a run outcome — it's a script the gate
found and was told not to run, listed with its reason in
`talk/verify-exclusions.txt` because another script already runs it, with
real arguments.)

Every script's full stdout+stderr lands in `talk/captures/<slug>.out`, win or
lose, alongside the table's truncated last line — that's where to look first
when a FAIL row's one-liner isn't enough. A local run's captures are
untracked scratch; the scheduled `truth` workflow is the observation lane
(D1) that commits them next to `truth.log`. After the TRUTH line, the gate
also prints the slowest five scripts by wall-clock time — a script creeping
toward the timeout shows up there before it starts timing out.

The rule to say out loud: **a green that could not look is a red.** SKIP is
not a soft pass — the check never ran. Read `pass=` in the TRUTH line as the
only count of things actually observed true; an offline run's `skip=` proves
nothing either way.
