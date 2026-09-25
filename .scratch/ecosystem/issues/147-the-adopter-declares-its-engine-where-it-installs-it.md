# 147 — The adopter declares its engine where it installs it

Type: task
Status: open
Blocked by: none

## Question

Graduated 2026-09-25 from grilling ticket 71, decisions 2, 5 and 11 (delegated), and ADR-0033
point 2.

The adopter installs its own Kyverno. Adopters sync platform `./distribution` only, not
`./engine`. Each adopter's `drift-sample.yml` installs the raw `install.yaml` from its own
`KYVERNO_VERSION` env, and each `shift-left.yml` pins its own CLI. No adopter declares its engine
anywhere, and `party/schema.json` does not allow a field for it. Build the following in driftwood,
tuppence and ludlow:

1. **The declaration is one file: `gitops/engine/kyverno.yaml`.** It installs Kyverno at an exact
   version, and it states that version as a Kyverno version, for example `1.18.2`, not only as a
   Helm chart version. So a reader needs no chart-to-app lookup. It also carries the sha256 of what
   it installs. The path is decided here (delegated), because ticket 161 reads it.
2. **The drift sample installs from that file.** `drift-sample.yml` stops using its own
   `KYVERNO_VERSION` and checksum. It reads both from the file. The engine is not installed twice.
3. **`shift-left.yml` uses the declared engine.** The adopter's offline CLI version equals its
   declared engine, read from the same file.
4. **A new drift fact: the running engine equals the declared engine.** The sample reads the
   version of the Kyverno controller that runs on the cluster, and compares it with the file. A
   difference is false, and false is a red, as with the existing facts. A version that the sample
   cannot read is `null`, which is could-not-look. Take the next free fact number after the facts
   that tickets 155 and 161 add.
5. **Tell the session that owns ticket 161.** Its `verify-cage-probe.sh` compares the CLI version
   with the adopter's engine version, and must read that version from `gitops/engine/kyverno.yaml`.

Every adopter declares 1.18.2 here. Ticket 150 is the only ticket that moves an adopter to
another engine.

## Done

A scheduled drift sample on each adopter installs Kyverno from `gitops/engine/kyverno.yaml` and
records the engine fact true. A dispatched run does not count. A test with a planted difference
between the declared and the installed engine records the fact false.

## Notes

- Ticket 148 must not land before this ticket lands on all three adopters. If composition prices
  before an adopter declares its engine, that adopter gets the `undeclared-engine` price.
- Tickets 147 and 161 both edit `drift/five-facts.py` in each adopter. Whichever lands second
  rebases.
- The engine versions as read on 2026-09-25: `drift-sample.yml` driftwood `:56-57`, ludlow and
  tuppence `:59-60`; `shift-left.yml` driftwood `:117-118`, ludlow `:140-141`, tuppence
  `:138-139`.
