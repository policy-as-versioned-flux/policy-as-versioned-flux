# 140 — Fact 4 counts a defaulted false as a difference

Type: task
Status: open
Blocked by: none

## Question

Charted 2026-09-24 by the integrator. The first scheduled drift samples after the composed-set
moves (driftwood run 35995156466, tuppence 36006834728, ludlow 36010939303) all read
`fact_4_rendered_objects_byte_equal_to_an_offline_render` false: 0 of 26 objects absent, and 9
live but unequal. All 9 are the PriorityClasses ticket 111 delivered, each with one difference:

```
".globalDefault absent live"
```

The rendered classes declare `globalDefault: false`. The API server omits a false-valued
`globalDefault`, so the field is absent live. Fact 4's `declared_equal` compare counts a declared
field that is absent live as a difference. The classes are in signed policy bodies
(`policy/v5.0.0`), so the render cannot change.

What this ticket owes:

1. Fact 4 treats a declared zero value that the API server omits as equal, for the fields where
   the API omits it, and records the rule with its reason. It must still fail a declared
   non-zero value that is absent live, and a changed value.
2. Tests at the compare seam in each adopter's `drift/five-facts.py` (driftwood, tuppence,
   ludlow), red first, including a planted `globalDefault: true` that is absent live.
3. The change is in each adopter's own lane script, so a scheduled sample reads the result.

## Done

A scheduled sample on each adopter reads fact 4 true with the delivered PriorityClasses, and the
compare still fails a real difference.
