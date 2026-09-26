# 148 — Composition prices an unsupported pairing

Type: task
Status: claimed
Blocked by: 146, 147, and the owner's authorisation for a platform tools tag and the adopter tags

## Question

Graduated 2026-09-25 from grilling ticket 71, decisions 6, 16 and 18 (delegated), and ADR-0033
points 3 and 7.

An unsupported pairing is an adopter whose declared engine is not a supported engine of a line, or
of the machinery, that the adopter composes. Composition prices it and never refuses it. Build the
following in the platform tools:

1. **Composition reads three facts.**
   - The adopter's declared engine, from its `gitops/engine/kyverno.yaml` (ticket 147).
   - Each composed line's `tested_engines`, from the platform's `distribution/versions.yaml` at the
     adopter's pinned platform tag.
   - The machinery's `tested_engines`, from the same platform tag (ticket 146 item 4).
2. **An unsupported pairing makes every claimed control a hole.** On an engine that a line does
   not support, the line's control claims do not count. Each control that the line claims is then
   a hole, priced as ADR-0026 prices a hole. The evidence document shows an `unsupported-engine`
   delta that names the line and the engine. The machinery's claim, cm-6, is priced the same way.
   A line or a machinery release with no `tested_engines` supports no engine.
3. **No declaration is priced the same way,** under an `undeclared-engine` delta. Under ADR-0020
   this is a missing behaviour, not a missing instrument: the gate can read the claims and their
   hole prices, and only the engine is unknown.
4. **The composed header records the declared engine.**
5. **The shift-left check runs each line only on engines that the line supports** (decision 18).
   `shift-left/ci-check.py` runs every line in the ±1-major window with the adopter's declared
   engine. A line in the window that does not support that engine is reported by name as an
   unsupported pairing. It is not a compile error and not a pass.
6. **The machinery supports 1.19.1 and moves to `policies.kyverno.io/v1`** in the same tools
   release. Fix each machinery body that ticket 146 item 4 grades red on 1.19.1, as ticket 149
   fixes cage-tier. Then the machinery's `tested_engines` is `[1.18.2, 1.19.1]`. If this ticket
   lands before ticket 149, it adds the 1.19.1 row to the engine table. The bodies are `v1alpha1` today,
   and both engines mark `v1alpha1` deprecated. Ticket 149 moves the policy line's bodies.
7. **A hub check grades the price.** A planted declaration of an engine that a composed line does
   not list gives the `unsupported-engine` delta. Its amount equals the sum of the hole prices of
   the controls that the line claims.

Then the rollout. Each step after the first is an owner step:

- a signed platform tools tag;
- a pin move on each adopter;
- a recompose on each adopter;
- each adopter's signed composed tag, and its composed-set move to that tag (ticket 130's route).
  The machinery reaches a cluster only through that move.

## Done

Each adopter's composed evidence records its declared engine, 1.18.2, and shows no engine delta.
The hub check passes on its planted cases. The truth run after the recomposes records no fall.

## Notes

- The order is a safety rule. This ticket lands only after ticket 147 has landed on all three
  adopters. Otherwise all three get the `undeclared-engine` price, all their claimed controls
  become holes, and the gate records a fall.
- The price assumes the worst case: the body does not load. Whether a body that does not compile
  fails open or refuses at admission is not measured. Ticket 150 measures it. If admission refuses,
  ADR-0033 point 3 reopens.
- The composer reads the substrate from the platform's `engine/namespaces.yaml`, never from the
  adopter (ticket 119). The engine version is the adopter's own fact, so it is read from the
  adopter.

## Comments

**2026-09-26, owner-instructed: built as two pull requests.** On 2026-09-26 the owner answered
"Authorised" to a list that began "build eco-system tickets 146 to 150" and named "the tools and
adopter tags for ticket 148". This ticket is built as a platform pull request
(policy-as-versioned-platform/platform#48, branch `ticket-148-unsupported-pairing`) and this hub
pull request. Neither pull request cuts a tag, moves a pin or recomposes an adopter. The rollout
is the integrator's.

What the two pull requests build, item by item:

1. **Composition reads three facts.** `compose/composition.py` reads the adopter's
   `gitops/engine/kyverno.yaml` through a new platform module, `engine/declaration.py`. It reads
   each composed line's `tested_engines` from the implementations parent's
   `distribution/versions.yaml`, and the machinery's from `distribution/machinery.yaml` in the
   same tree. That tree is the platform tag in the adopter's `gitops/platform/platform-pin.yaml`,
   and it is the tree that renders the machinery. Every value is read with the grader's own
   `declared_engines`.
2. **An unsupported pairing makes every claimed control a hole.** A claim belongs to a line when
   the policy it names is one of the line's bodies. It belongs to the machinery when it names a
   machinery member. On an engine that a line or the machinery does not support, those claims do
   not count. Each control they name becomes a hole, priced from `holes[]` as ADR-0026 prices any
   hole. Each such subject prints an `unsupported-engine` delta that names the subject, the engine
   and the tested engines. Its amount is the sum of the hole prices of the controls it names, or
   null when none carries a price. No declaration prints the same under `undeclared-engine`.
3. **The header** records `declared-engine`. The evidence gains an `engine` section that lists
   every pairing, and a hole that a pairing opened carries `uncounted_claims`.
4. **The shift-left check.** `shift-left/ci-check.py` reads the declaration at the top of the
   resource's own git repository, or the file `--engine-declaration` names. It runs a line only
   when the line lists the declared engine. Any other line prints `UNSUPPORTED PAIRING @ v<x>` with
   its reason, and it is not run.
5. **1.19.1 on the machinery.** Platform `engine/kyverno/engine-table.yaml` gains the 1.19.1 row.
   Both CLI checksums come from v1.19.1's own `checksums.txt`. The install.yaml checksum is the
   GitHub release API's asset digest. The chart row (3.9.1, appVersion v1.19.1) comes from the
   Kyverno Helm index. Each figure was cross-checked by downloading the file, and the table records
   its source. The grader graded every machinery body on 1.19.1 on a throwaway commit that listed
   it. All seven bodies passed, and no body needed a fix. Then `distribution/machinery.yaml` listed
   `["1.18.2", "1.19.1"]`. The move to `policies.kyverno.io/v1` is not built: see "Not done" below.
6. **The gate stays green with the row.** The hub `truth.yml` engine step installs both rows, and
   `verify/estate-engines/` and `verify/adopter-engines/` still pass. The estate's own pins stay
   1.18.2.
7. **The hub check** is `verify/engine-pairing/`, with its manifest row. It runs the composer the
   estate serves, through its own CLI, on copies of the adopters' committed trees. It derives every
   expected figure itself. `verify/priced-holes/` admits the two new delta kinds.

**2026-09-26, delegated decisions made during the build (ADR-0025).**

- A control that an unsupported line claims is a hole, even when a second, supported line
  also claims it. Reason: a workload chooses which composed line it claims, so a control whose body
  does not load for one line's workloads is not implemented for those workloads. This is the worst
  case that ADR-0033 point 3 prices.
- A `tested_engines` value that the grader's rule does not read as support supports no engine.
  That covers a retired scope, an unknown scope and a malformed list. The composer loads the
  grader's own `declared_engines`, so one rule grades a claim and prices it.
- A present declaration that does not read refuses with the existing kind `missing-instrument`,
  subject `gitops/engine/kyverno.yaml` (ADR-0020). No refusal kind is added. The shared reader
  is stricter than the adopters' own reader in one respect: it refuses a YAML boolean `schema`.
- An engine delta prints on every composition while the pairing stands. Reason: the pairing is a
  fact of the current inputs, not a change since the last artefact. A hole it opens still prints
  `new-hole` once, and that delta's text now names the pairing.
- The shift-left check exits 3 (could not look) when the target line does not support the
  declared engine, when no engine is declared, or when the CLI reports another version. An
  unsupported neighbour is named and does not change the exit. Reason: ADR-0033 rejected refusing
  an unsupported pairing. A red on a neighbour would refuse every pull request of an adopter while
  that neighbour is served.
- The planted flip window lists `tested_engines` on both lines, because the check now runs a line
  only when the line lists an engine. The 5.0.0 value is the served array's own. The 4.0.0 value is
  planted, and the file says so. `verify-shift-left.sh` also runs the window with 4.0.0's last
  served value, the retired scope. That neighbour is then named and not run.
- The machinery's supported engines are read from the implementations tree, not from the tools
  tree, because that tree renders the machinery.
- The tools release that carries this is a **minor**. The precedent is v3.3.0, which added delta
  kinds with no refusal and no price move for the three adopters. The same holds here when both
  pins move. `compose/README.md` names one change that is a major for the tools release: a new
  `PRICE_KINDS` value. This change adds no price kind.

**2026-09-26, what was measured.** Local runs on the owner's Mac. The pinned CLIs 1.18.2 and
1.19.1 (darwin_arm64) were checked against each release's `checksums.txt`. The scratch estates
were each adopter's `origin/main` and each parent at the adopter's pinned commit. Platform was at
`923447e`, this branch's head on top of `origin/main` `cb680f2`. The hub was at `origin/main`
`d47664cd`.

- The grader, `verify-cage-engine.sh` with both engines: `PASS: engine cells -- passed; 3
  cell(s): 3 passed`. Policy 5.0.0 passes on 1.18.2. The machinery passes on 1.18.2 and 1.19.1.
- Platform `compose/verify-composition.sh`: PASS. That includes 13 new tests in
  `test_engine_pairing.py`. Six planted composer defects each fail those tests.
  `shift-left/verify-shift-left.sh` on 1.18.2: every proof passes, including eight engine cases.
  On 1.19.1 it reads SKIP by name. Four planted `ci-check.py` defects each fail it.
- `verify/engine-pairing/` against platform `923447e`: the planted and forward cases pass. The
  served case reads SKIP for all three adopters, because their artefacts predate this composer.
  Planted 2 (driftwood declaring 1.19.1, which 5.0.0 does not list) prints one
  `unsupported-engine` delta for 5.0.0 with amount null. The machinery lists 1.19.1, so it gets
  no delta. Planted 3 plants a claim of `ca-2` on a 5.0.0 body. `ca-2` is covered on 1.18.2. On
  1.19.1 it is a hole of £357,435.42, and the regime entry's open amount rises from £1,429,741.66
  to £1,787,177.08, exactly that hole.
- A simulated rollout on throwaway commits moved each adopter's two pins to `923447e`, recomposed
  and committed. The served case then passes for all three adopters, with no engine delta.
  `composition.py verify` holds each artefact byte for byte, and a second compose shows no drift.
- The real claims carry no price. The regulator's weights (ico penalty-schema v3) name pl-2,
  ra-3, ca-2 and ir-8. The estate's two claims, ac-6 and cm-6, carry no weight. So an unsupported
  pairing on a real adopter today opens two holes with `amount: null`, and moves no pound.
- **Each adopter after the rollout.** Composed from `origin/main` with both pins at a tree like
  `923447e`, each adopter declares 1.18.2 and gets no engine delta. The header gains
  `declared-engine` (kyverno, 1.18.2, `gitops/engine/kyverno.yaml`). The evidence gains the
  `engine` section. Nothing else changes except what the pin move changes anyway: `parents[0]`,
  `members[].source_sha`, the `inherited-from` annotation on each composed file, and the
  comparison identity. Driftwood also gains `prices[5].rests_on_grade: null` and one named absence
  in `HANDBOOK.md`. That is ticket 141's change, which is already on platform `main` and rides the
  same tag. No price, hole, delta or refusal moves.
- **If only the tools pin moves.** Against platform `v4.0.0`, each adopter gets two
  `unsupported-engine` deltas, and ac-6 and cm-6 become new holes. 5.0.0 carries the retired
  scope there, and the tree has no `machinery.yaml`.
- Each adopter's workloads (`deploy/pod.yaml` and every served workload) pass the new
  `ci-check.py` on their own declaration of 1.18.2.
- Hub `verify/estate-engines/`, `verify/adopter-engines/` and `verify/priced-holes/` pass against
  platform `923447e`. The lifted `truth.yml` engine step installs both rows, run with the darwin
  column swapped in. The linux_x86_64 1.19.1 archive was downloaded and hashes to the table's
  figure.
- Hub `tests/test_truth_manifest.py` passes (18). Four hub test files drive the platform
  composer: `tests/test_loophole_adr_0026.py`, `test_loophole_rounds_two_and_three.py`,
  `test_priced_holes.py` and `test_misuse.py`. Against `923447e` they give 119 passed and 2
  failed. The two failures are in `test_loophole_rounds_two_and_three.py`, and they fail the same
  way against platform `origin/main` `cb680f2`. They are outside this ticket.

**Not done.**

- **The machinery move to `policies.kyverno.io/v1`.** Each machinery twin's selfcheck compares
  its body with the ResourceSet template in platform `distribution/versions.yaml`. Measured:
  moving only the four renderers to `v1` fails all three selfchecks. The move needs the seven
  `apiVersion` lines of that template to change in the same commit. This session was not
  permitted to edit `distribution/versions.yaml`, which the brief names a serial resource. Both
  engines' `install.yaml` serve `v1` and mark `v1alpha1` deprecated for all three kinds, as
  measured on 2026-09-26. Item 6 wants this move in the same tools release.
- The rollout: the tools tag, the pin moves, the recomposes and the adopter tags.
