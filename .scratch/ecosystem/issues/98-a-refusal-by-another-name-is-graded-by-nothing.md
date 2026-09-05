# 98 — A refusal by another name is graded by nothing

Type: task (AFK)
Status: open
Blocked by: none

## Question

The estate has a doctrine: nothing is denied, and a workload that does not fit its cage runs on a
tighter rung. Ticket 89 built a register that grades every Deny-shaped rule. Nothing grades the
other way a workload can be stopped: a MUTATION that makes a pod inadmissible. It has happened
twice, both times found by RUNNING a policy rather than reading one, and no static check in this
repository can see it.

Build a check that catches a mutation whose product the API server would reject. Done = the check
is in the gate, it goes red on each of the two instances below replayed as fixtures, and its
manifest row declares what it cannot see.

## Notes

Charted 2026-09-05 from ticket 89's round-2 build. Ticket 89 records the shape in
`deny_register.BLIND_SPOTS`; this ticket is the one that grades it.

**The two instances, both real.**

1. **2026-08-28, ticket 26.** The priority trio and the duplicate sidecar. A cage mutation produced
   a pod the API server would not accept.
2. **2026-09-05, ticket 89 round 2.** The new orphan cage named the PriorityClass `cage-isolated`.
   Every PriorityClass the estate ships is version-suffixed — `distribution/policies/v4.0.0/
   priorityclasses.yaml` declares `cage-baseline-4-0-0`, `cage-restricted-4-0-0`,
   `cage-quarantine-4-0-0` and `cage-isolated-4-0-0`. The plain name exists on no cluster, and the
   Priority admission plugin rejects a pod naming a PriorityClass that does not exist. So the cage
   built to REPLACE a refusal would have made every pod it caged inadmissible. The builder found it
   by running the beat, not by reading the body, and fixed it before the branch was reviewed.

**Why a static check is hard, and what to aim at anyway.** Whether the API server accepts a mutated
object depends on the cluster: which PriorityClasses exist, which admission plugins are on, whether
a field is immutable on UPDATE. A check that decided that offline would be guessing. Three things
are checkable without a cluster and would have caught both instances:

* **Every name a mutation writes into a reference field must be a name the same release ships.**
  `priorityClassName` is the one that bit. A mutation naming `cage-isolated` while the release
  declares `cage-isolated-4-0-0` is a defect the renderer can refuse at render time.
* **A mutation on UPDATE must be byte-identical on a already-mutated object.** `cage-tier`'s own
  header already argues this for its sidecar; nothing asserts it. An UPDATE mutation that adds a
  container to an immutable list is the second instance's shape.
* **A field a mutation writes must be one the resource allows to change on that operation.**

The live half belongs where a cluster is: `graded/verify-graded.sh`'s cluster tail, which has never
had a cluster on a citable run (review finding P2-6). State that rather than simulating it.

**Do not simulate an API server.** A check that plants a fake rejection and prints a PASS would be
the exact defect this estate keeps finding. What cannot be looked at offline is named and exits 3.

## Comments

**2026-09-05.** Both instances share a property worth stating: the mutation was correct as a
document and wrong as an effect. Reading it proved nothing. Every check in this estate that has
caught one did so by executing the policy against a resource, which is why `verify-orphan-guard.sh`
and `verify-graded.sh` are the places this belongs rather than a new scanner.
