# 15 — The forward layer can only ever raise the bill

Type: grilling
Status: resolved
Blocked by: none

## Question

The AI-Wardley layer is **monotone-pessimistic**: a commoditising *attacker* capability raises the
linked LEF, but no commoditising *defence* can lower any cost. `spiffe-workload-identity` is on the
map, flagged commoditising, and structurally incapable of moving a number — `forward_signal()` skips
any component whose `actor != "attacker-capability"`.

Concretely, from the scenario-slate research: npm shipped default-off lifecycle scripts (Jul 2026) and
revoked classic tokens (Dec 2025). Both are real, free reductions in supply-chain risk for this estate.
Both are invisible to the model. A forward layer that can only ever argue for spending more is one an
audience should distrust — and a CFO certainly will.

**Decide:**

1. **Should defensive commoditisation reduce cost at all?** The argument for: it is symmetric, true,
   and the layer already tracks the components. The argument against: cheap-to-run defence is not the
   same as deployed defence, and crediting a control nobody installed is exactly the unearned green
   this estate exists to refuse. Is there a defensible middle — credit only where enactment is
   *corroborated*, mirroring the twin's evidence-graded mitigation credit?
2. **If yes, through which term?** A cost-of-controls reduction, an LEF reduction on the linked risk,
   or a new move-cost input to `tcor.crossover`. Each changes a different line of the balance sheet.
3. **If no, say so on the map and in the model** — a documented, deliberate asymmetry is honest; a
   silent one reads as a thumb on the scale.

Note `pqc-transport-migration` in the proposed slate is a defensive component and is inert *by this
same rule*, so the slate has a worked example either way.

## Answer

Resolved by grilling, 2026-08-20. **Yes — through cost-of-controls, gated on corroborated enactment.**

**1. The term is cost-of-controls, not LEF.** npm shipping default-off lifecycle scripts (Jul 2026)
and revoking classic tokens (Dec 2025) genuinely lowers what a control *costs* to operate; it does not
lower attack frequency. Reducing LEF would credit the wrong thing and double-count against the
attacker-side commoditisation the layer already models. `tcor.py`'s `cost_of_controls` (`C_fix`,
`C_cage` via `cage.TIERS[...]["cost"]`) is where a cheaper defence belongs.

**2. Gated on corroborated enactment.** Crediting a defensive improvement nobody adopted is the
unearned green this estate refuses — "this got cheaper in the world" and "we actually adopted it" are
different claims. Mirror the twin's `pricing._credit()` shape, whose `NOT_ENACTED` constant refuses
credit for an option with no corroborated enactment.

**Note the estate's own mechanism is thinner than the twin's.** `wargamer.py:138` reads
`risk.get("deployed_move", chosen)` — a *declared* field, defaulting to whatever the engine would
have picked. That is an assertion, not corroboration: nothing checks the control is actually running.
So the gate has to be built, not merely borrowed, and it should be honest about its evidence grade
rather than treating a declared `deployed_move` as proof of enactment.

**3. The asymmetry was real and is now named.** `forward_signal()` skips any component whose
`actor != "attacker-capability"`, so `spiffe-workload-identity` sits on the map flagged commoditising
and structurally incapable of moving any number. A forward layer that can only ever argue for
spending more is one a CFO will eventually stop believing. Implementation raised as its own ticket.
