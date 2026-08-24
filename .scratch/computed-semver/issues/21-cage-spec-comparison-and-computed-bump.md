# 21 — Cage-spec comparison and the computed bump

Type: task
Status: done (2026-08-24)
Blocked by: 19

Source: [`spec.md`](../spec.md), *What the gate measures*, and *Testing Decisions*.

## What to build

The gate measures the bump instead of accepting the declared one. A publisher declares a bump. The
gate computes one from observed movement. It refuses a declared bump weaker than the computed bump. It
permits a stronger one and prints the discrepancy. It never rewrites the number.

**Compliant means admitted.** An Audit rule that fires reports and does not refuse. The opposite
reading makes every new Audit policy a major bump, and that collapses the lane-keeping half of the
thesis into the gate.

**There is no separate refused verdict class.** Refusal is the bottom rung of the cage ladder. The
ladder is a pure function of residual and band.

**Every workload is always caged, and the cage spec is what changes.** The engine compares **cage
specs**, not verdict enums. There is no uncaged state. `deny` is the degenerate case where no
satisfiable spec exists.

**Major is stated at spec level, not at dial level.** The new cage spec must be at least as permissive
as the old one. An enumerated list of surfaces rots on the next mutation added. The tier policy changes
more than dials. It appends a sidecar container, sets a priority class, flips two security-context
fields, and drops capabilities when the tier hardens.

Minor comes from presence plus `validationActions`. Patch means the passing set only grows.

**Read per-policy outcomes, never a pooled CLI exit code.** Ticket 01 proved that trap empirically. A
pooled exit code disagrees with the real admission outcome when the only failure is on an Audit policy.

**The gate never estimates viability.** It prints one sentence instead. The ceiling moved down, and the
gate does not know whose workload dies at the new number. A viability rule needs a threshold.

The engine must reproduce a human's correct answer before it is trusted to give its own.

## Acceptance criteria

- [x] The engine compares cage specs, not verdict enums.
- [x] Major means the new cage spec is not at least as permissive as the old one.
- [x] Minor comes from presence plus `validationActions`.
- [x] Patch means the passing set only grows.
- [x] The engine reads per-policy outcomes and never a pooled exit code.
- [x] The three known-good bumps from the historical release line rederive exactly.
- [x] A declared bump weaker than the computed one refuses.
- [x] The refusal names the corpus entries that moved.
- [x] The refusal names the CEL expression that moved them.
- [x] A stronger declared bump passes and prints the discrepancy.
- [x] `movement[]` carries per-policy verdict movement, naming entries and expressions.
- [x] A ceiling that moves down prints one sentence and no estimate.
- [x] Nothing in the engine rewrites the declared number.

## Comments

Shipped in `platform` at `290b8c7` + `add3995` (cs-21).
