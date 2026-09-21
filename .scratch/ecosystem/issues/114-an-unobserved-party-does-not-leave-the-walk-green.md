# 114 — An unobserved party does not leave the walk green

Type: task
Status: open
Blocked by: none

## Question

Graduated 2026-09-21 from [the Laya and loophole map](../../laya-loophole/map.md), ticket 08.
It is the second survivor of ticket 07's loophole round. Reproduced by
`tests/test_cage_ladder_holes.py`.

`platform/shift-left/tier_binding.py` returns 3, could-not-look, when a party declares two
governed Namespaces, because which one carries the party's tier is not the check's guess to make
(ADR-0020). That is right, and ticket 78 built it on purpose.

The hub's estate walk then throws it away. `verify/tier-binding/tier_binding_estate.py` prints
the party's SKIP line, `continue`s, and returns `1 if failed else 0`. A skipped party is neither
looked at nor failed, so the script exits 0 while one party's cage is unobserved.
`talk/verify-all.sh` grades a script by its exit code alone, so the gate reads PASS.

Measured 2026-09-21 on a planted estate of two bound parties: adding a second governed Namespace
document to one of them produces `SKIP: driftwood`, `PASS: ludlow`, and exit 0.

This is the estate's own defect class, eco-system ticket 98 and the Laya map's call 6: a tool
that cannot report its own failure is not measured, it is trusted.

Two things bound the blast radius, and neither closes it:

- Each adopter's own `shift-left.yml` turns exit 3 into a failed pull request by name, so the
  ambiguity cannot arrive through a pull request that runs that job. It can arrive any other way,
  and the hub's report of the estate is wrong either way.
- The cage the cluster serves does not change. This is a hole in the observation, not in the
  cage.

What this ticket owes:

1. An unobserved party does not leave the walk at exit 0. The likely shape is that a SKIP on a
   party that HAS both a composed artefact and a governed Namespace manifest is a could-not-look
   for the whole walk, distinct from a party that has neither.
2. A selfcheck leg that plants the ambiguous estate, so the repair cannot regress silently.
3. Check the same shape elsewhere. Any hub walk that iterates parties and folds per-party
   verdicts into one exit code can lose a could-not-look the same way.

## Done

The planted ambiguous estate does not exit 0. The selfcheck holds it. The
`adopter-silences-its-own-binding-observation` row in `twin/ecosystem-misuse-catalogue.yaml`
stops waiting on this ticket and names the built mechanism by path.
