# 01 — Can the premise be rederived? Reproduce the bumps a human already got right

Type: task
Status: open
Blocked by: none

## Question

Before designing a gate, prove the idea works on answers we already know. The old faithful-floor
estate cut a real, signed release line and **live-proved** each bump:

- `2.0.0` — **major**: `require-department-label` promoted Audit → Deny. A pod missing `department`,
  pinned to 2.0.0, was refused at real admission; it would have been admitted-but-reported under 1.0.x.
- `2.1.1` — **patch**: `require-known-department-label`'s enum widened by `+legal`. A pod with
  `department: legal` was admitted under 2.1.1 and refused under 2.0.1.
- `2.1.x` also added `require-owner-annotation` (Audit) — **minor** by the rule, since an added Audit
  policy cannot fail a compliant workload.

**The job:** take those policy bodies and fixtures as a fixed input, evaluate adjacent version pairs
offline (`kyverno apply`, as `verify-shift-left.sh` already does), and see whether major/minor/patch
falls out of the observed verdict movement — matching `CONTEXT.md`'s definition, without being told
the answer.

Report honestly which bumps rederive, which do not, and **why not** — a "cannot distinguish minor
from patch without X" finding is the most valuable output this ticket can produce, because it names
the corpus and verdict-semantics requirements the rest of the map has to satisfy.

**If the engine cannot reproduce a bump a human already got right and proved, this map's destination
is not reachable in its current form** — say so plainly rather than tuning until it agrees.

AFK. Runnable now, and everything else on this map is sharper once it reports.
