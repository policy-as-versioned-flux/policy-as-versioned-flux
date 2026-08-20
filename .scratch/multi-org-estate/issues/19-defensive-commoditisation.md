# 19 — Let a commoditising defence lower the bill

Type: task
Status: done (2026-08-20) — `bash estate/platform/wardley/verify-wardley.sh` step 6 plants an uncorroborated claim and watches the credit disappear.
Blocked by: 15, 14

## Question

Settled in *The forward layer can only ever raise the bill*: a commoditising **defensive** capability
reduces **cost-of-controls**, gated on **corroborated enactment**.

**The job:** extend `estate/platform/wardley/wardley.py`'s `forward_signal()` — which today skips
every component whose `actor != "attacker-capability"` — so a commoditising defence emits a forward
signal that reduces `C_fix` / `C_cage` for the controls it makes cheaper, rather than bumping LEF.
`spiffe-workload-identity` is already on the map, already flagged commoditising, and already unable to
move a number: it is the test case.

**Build the enactment gate honestly.** The estate has no corroboration mechanism — `wargamer.py:138`
reads `risk.get("deployed_move", chosen)`, a *declared* field defaulting to whatever the engine would
have picked, which is an assertion rather than evidence. The twin's `pricing._credit()` /
`NOT_ENACTED` is the shape to mirror, but the estate's side must actually be built. **Fail closed**:
no corroboration, no credit.

**Guard against the obvious failure.** This is the first lever in the estate that makes a number go
*down*, so it is the first one anyone has an incentive to game. A defensive component whose
commoditisation is asserted rather than observed, or an enactment claimed rather than corroborated,
would quietly reduce the board line — precisely the unearned green this estate exists to refuse.
Whatever is built should be provable by planting a violation and watching it fail, the way the twin's
harness guards are.

**Sequencing:** blocked by the per-org forward-layer ticket, which is already editing
`forward_signal()` — landing both separately would collide in the same function.

## Comments

Done 2026-08-20.

1. **`forward_signal()` extended, not forked.** The attacker path is byte-identical (`_forward_risk`,
   unchanged). A new `elif c["actor"] == "defensive-capability"` branch calls a new `_forward_defence()`
   — same K, opposite direction (`factor = 1 / (1 + K*movement)` vs `1 + K*movement`) — and touches
   only `costs.fix` / the new `costs.cage_discount`. LEF is asserted byte-identical to the
   un-discounted control in `selfcheck()`: a cheaper defence changes what the control costs, never how
   often an attacker succeeds.

2. **`../tcor/tcor.py` gained one optional field: `costs.cage_discount`** (default `1.0`), a multiplier
   on the cage move's own `cost_of_controls`. `cage.py`'s tier table stays untouched — its cost is a
   structural, estate-wide constant per tier, and a discount belongs to the ONE risk a cheaper control
   makes cheaper, not to every caged workload in the estate. Every existing risk that never sets it is
   unaffected (`tcor.py selfcheck` 4c pins this).

3. **The enactment gate is a new, small function (`corroborated_enactment()`), not a port of the
   twin's evidence ladder.** The twin's `pricing._credit()` / `NOT_ENACTED` shape is mirrored —
   declared-vs-corroborated, a named refusal reason, fail closed — but the estate has no evidence-grade
   system to plug a multi-channel ladder into, so the estate's own gate is three structural checks: a
   record exists, `declared_by_subject` is explicitly `False`, and every named `evidence` path resolves
   to a real file on disk. All three are planted as violations and watched fail, in both
   `wardley.py selfcheck()` (2d) and `verify-wardley.sh` (step 6, visibly narrated) — the way the
   twin's harness guards prove a gate by breaking it — and the honestly-corroborated case is replanted
   alongside each, so the guard is shown not to refuse indiscriminately.

4. **A new, deliberately UNSIGNED file: `estate/platform/wardley/enactment.json`.** Kept separate from
   `market-intel.json` on purpose — `market-intel.json` is platform's own commoditisation CLAIM,
   signed with the shared feeds key, and a claim cannot corroborate itself. Editing `market-intel.json`
   in place was considered and rejected: the private feeds-signing key is not committed (by design,
   same as every other signed artefact here), so any edit would need a full key rotation and re-sign of
   every other feed that key covers — for one component. `enactment.json` carries both the editorial
   link (`control_risk`, copied from `../wargamer/scenarios/human-device.json`'s
   `stolen-laptop-unattested-device` — the SPIRE tpm_devid / Secure-Enclave device-SVID cage) and the
   independent corroboration (`declared_by_subject: false`, `evidence` naming the already-merged,
   already-reviewed `../identity/spire/helmrelease.yaml` + `../identity/istio/peerauthentication-strict.yaml`).

5. **`spiffe-workload-identity` moves a real number.** At driftwood/tuppence its linked control stays
   deployed at `cage` (no flip needed for the bill to fall): `cage_discount` 0.4545 takes C_cage from
   £6,000 to £2,727, and the chosen move's own TCoR falls from £19,103 to £15,830 —
   `wardley.py selfcheck()` 2c asserts this directly, not just that a factor is `<1`. At ludlow the same
   discounted risk crosses `cage -> fix`, same as every other risk on this map judged against ludlow's
   tighter band — the band, not the signal, decides, exactly the property section 3b already proves for
   the attacker side.

6. **`pqc-transport-migration` still emits nothing — and now for a documented reason, not an accident.**
   It carries no `enactment.json` entry at all (asserted directly: `"pqc-transport-migration" not in
   enact["components"]`). Its own `market-intel.json` note already explained why linking it would be
   dishonest — the commoditised half (transport key agreement) is not what the linked risk's `costs.fix`
   actually buys. A gate that credited every commoditising defence by construction, whether or not the
   link were honest, would be exactly the unearned green this ticket exists to refuse.

Left out of scope, deliberately: `wargamer.py:138`'s own general `risk.get("deployed_move", chosen)`
self-declaration is **unchanged** across the rest of the estate. The ticket's text names it as the
diagnosis for why an honest gate was needed, and cites the twin's shape to mirror for the ONE new credit
path this ticket adds — retrofitting every existing self-declared `deployed_move` read in the estate
(the reactive scenario library, the enforcement war-game) would be a much larger, unrequested change well
past "keep diffs small," and several existing `selfcheck()`/`verify-*.sh` assertions depend on that
existing behaviour. Also left open: whether `enactment.json` should itself be detached-signed like
`market-intel.json` / `wardley-map.json` for the same tamper-evidence guarantee (a `ponytail:` note in
the file names this as the upgrade path) — not required by this ticket's text, and reusing the shared
feeds key would tie its rotation to the same one-key-covers-everything blast radius that made editing
`market-intel.json` in place the wrong move in the first place.

Evidence: `bash estate/platform/wardley/verify-wardley.sh`, `bash estate/platform/tcor/verify-tcor.sh`,
`bash estate/platform/wargamer/verify-wargamer.sh`, `bash estate/platform/graded/verify-graded.sh` and
`bash estate/platform/oscal/verify-upflow.sh` all pass. `bash estate/talk/verify-all.sh`: 25/28 pass:
`verify-honesty.sh` fails on `reflexive.py`'s `signing_key_present` assertion (pre-existing per ticket
16's own resolution — the private feeds-signing key was never committed), and `verify-identity.sh` /
`verify-access.sh` fail on live cluster checks (SPIRE pods / Pomerium pod not present); all three
unrelated to this ticket and out of scope per this batch's `--live` instruction. No live cluster in this
environment.
