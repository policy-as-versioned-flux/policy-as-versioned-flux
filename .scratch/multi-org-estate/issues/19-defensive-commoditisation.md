# 19 — Let a commoditising defence lower the bill

Type: task
Status: open
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
