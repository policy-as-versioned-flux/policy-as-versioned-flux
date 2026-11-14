# Context: the loop

The terms of the loop that `LOOP.md` describes. Each is defined here and nowhere else in the hub.
The older decision records in `docs/adr/` use older words. Where they differ, this file holds.

## Parties

- **Adopter**: the organisation that is caged. Here it is driftwood.
- **Publisher**: a repository that publishes numbers about the world as a **feed**: one JSON file at
  a fixed path, with its version inside it. Here they are ico (the penalties) and feeds (the rows).

## Money

- **Exposure**: the adopter's expected loss in pounds a year: the sum of the amounts of the open
  rows. `LOOP.md` step 2 gives the amount of a row.
- **Tolerance**: the loss a year the adopter says it will bear. It is a sum, or a share of
  turnover, in driftwood's `party.json`, with its basis.
- **Figure**: the exposure plus the current rung's cost a year. It is the one number compared with
  the tolerance. A prediction never enters it.
- **Row**: one way a loss happens, published by feeds, with the capabilities it **needs**, each
  with a source. A row is **closed** when a capability it needs was measured closed this cycle and
  the current rung, or a looser one, declares that capability closed. Otherwise it is **open**. A
  need with no source is ignored, so a row with none never closes. A row with a missing number is
  **unpriced**. Its penalty term uses the regime's **penalty rate**, the chance that one breach
  draws a penalty. A row's **bound** is `upper` when its penalty tier is not cited or the penalty
  rate is missing, and `estimate` otherwise.
- **Basis**: where a number came from: a kind, a date and a sentence. The kinds, weakest first, are
  `not-counted`, `unsourced`, `editorial`, `published` and `counted`. A row is **sourced** only if
  neither of its bases is `editorial`, its tier is cited and the penalty rate is counted.

## The cage

- **Cage**: limits put on a running pod from outside, by two Kyverno policies, platform's
  `cage/cage-tier.yaml` and `cage/cage-netpol.yaml`. Neither denies anything.
- **Rung**: a named cage setting. The ladder is `baseline`, `quarantine`, `isolated`, loosest
  first, in platform's `cage/rungs.json`. A rung keeps what the looser rungs close, and has a cost a
  year with a basis. What a rung does to a pod is read from `cage/cage-tier.yaml`.
- **Notch**: a move to the next rung in ladder order. It is one changed line, the rung line in
  driftwood's `gitops/apps/namespace.yaml`.
- **Governed Namespace**: the one Namespace the cage acts in. It carries
  `policy-as-versioned.dev/governed: "true"` and the rung line.
- **Stamp**: the two labels the cage writes on each pod it has caged: `posture.acme.io/caged: "true"`
  and `posture.acme.io/tier` set to the rung.

## Measuring

- **Capability**: one thing a running pod can do that a live test can check. There are two:
  `egress` and `inbound`. Each cycle reads each one `open` or `closed`.
- **Probe**: that test. It runs from platform's `loop/probe.py`.
- **Reference**: pods outside the cage that run the same test, before and after, to show the
  network works. They are in the Namespace `loop-reference`.
- **Probe pod**: the one caged pod the tests run from.
- **Settled**: every pod in the governed Namespace is Ready and carries the stamp of the rung in
  git. The probe waits for this before it tests. A reading that is not open is settled only when
  it holds on three more reads.

## The cycle

- **Cycle**: one pass of the loop, one run of driftwood's `loop.yml`. In `measure` mode a cycle
  records only. In `act` mode it also opens and lands the notch. The mode is set in `party.json`.
- **Ledger**: a file with one line per cycle: `loop.jsonl` on driftwood's branch `ledger`.
- **Goal**: for a limit, the loosest rung whose predicted figure is at or below it. If none is, the
  rung with the lowest predicted figure, the looser on a tie. A rung's **predicted** figure is the
  amounts of the rows that would stay open if exactly the capabilities declared closed up to that
  rung were closed, plus that rung's cost.
- **Release-ready**: the goal for `(1 - margin) x tolerance` is looser than the current rung. The
  margin and the **dwell**, a number of days, are settings in `party.json`.

## Verdicts

Each cycle gives exactly one, the first that applies, in this order.

- **could-not-look**: the loop could not measure, so it gives no judgement and moves nothing.
- **cage-ineffective**: a capability the current rung declares closed is measured open. Red. No move.
- **could-not-look**, checked again here: a capability is measured closed that the current rung does
  not declare closed. Something other than the cage closed it, so it earns nothing.
- **tighten**: the goal for the tolerance is tighter than the current rung. One notch tighter, now.
- **release**: every row is priced, and the loop has been release-ready on every cycle for the
  dwell, this one included. One notch looser.
- **within**: the figure is at or below the tolerance and every row is priced. Hold.
- **within-partial**: the same, with a row unpriced. The figure is then a lower bound. Hold, never
  release.
- **saturated**: the figure is above the tolerance and no move applies. Red. Hold. The line's
  `unreachable` says how far the lowest predicted figure on the ladder, cost included, is above the
  tolerance.

## Identities and pins

- **Pin**: the exact commit of another repository that driftwood uses, one line each in `party.json`.
- **The app**: the GitHub App `pavc-other-hand`, a machine identity. **The key**: its private key.
- **Default token**: the credential GitHub gives a workflow run.
