# 02 — What counts as a "verdict", given Audit is not a pass

Type: grilling
Status: open
Blocked by: none

## Question

`CONTEXT.md` defines the bump by "verdict impact on currently-compliant workloads", and its own
examples show the verdict space is **not binary**:

- a new **`Audit`** policy is **minor** — it cannot fail a compliant workload, but it does newly
  *report* on it;
- an **`Audit` → `Deny` promotion** is **major** — the workload's admission outcome flips.

So a workload has at least three states — admitted-clean, admitted-but-reported, refused — and the
bump depends on which transition occurred, in which direction.

**Decide:**

1. **The verdict lattice.** What are the states, and which transitions are major / minor / patch?
   Admitted→refused is clearly major. Admitted-clean→admitted-reported is the "new Audit policy"
   minor. What about refused→admitted (a widening — patch by the rule, since the passing set grows)?
   What about reported→clean?
2. **Whose compliance counts.** The rule says *currently-compliant* workloads. Is a workload that is
   admitted-but-reported "compliant"? If yes, a new Audit rule on it is minor; if no, the same change
   reads as major. `CONTEXT.md`'s own example says minor — confirm that is the intent and record it.
3. **Unversioned and out-of-scope workloads.** A pod claiming no version, or a version outside the
   supported window, is judged by nothing. Does it enter the corpus at all, and does an
   out-of-scope→in-scope change count as a verdict move?

The answers become the engine's core semantics, so they need to be explicit before anything is built.
