# Context: Policy as Versioned Code, on Flux

The ubiquitous language for this project. A glossary, not a spec — no implementation
details. When a term here conflicts with how someone is speaking, the term here wins
(or we change it here, deliberately).

This project is a faithful re-implementation of Chris Nesbitt-Smith's (CNS) **Policy as
[Versioned] Code** thesis onto **Flux CD**. Source material: the talk, the original Medium
post, the later "mea culpa" blog post, and two reference GitHub orgs (`example-policy-org`,
`policy-as-versioned-code`). Full research is in `./research/`.

Since 2026-08-27 the destination is the eco-system in [NORTH-STAR.md](NORTH-STAR.md). Entries below
were rewritten in its cage and schedule vocabulary on 2026-08-28 (eco-system ticket 02). Older ADRs
that a rewritten entry cites stay as the record of the decision at the time.

---

## Core thesis terms

- **Party** — Any of the six units of the estate. Deliberately *not* given a collective noun in
  prose: name the kind instead ("the platform, two regulators and three institutions"), because the
  argument depends on these being different kinds of party exchanging signed dependencies across
  trust boundaries. What is true of all six: each is represented by its own **independent GitHub
  organisation**.

- **Role** — What a party *does*. Roles **compose**; they are not a partition, and a party may hold
  several:
  - **publisher** — ships a signed, versioned artefact others pin (`platform`, `nist`, `ico`);
  - **risk-bearer** — has a declared risk-appetite band, so the £ engine can price it
    (`driftwood`, `tuppence`, `ludlow`, **and `platform`** — the apparatus prices its own risk
    against a strict £10k band, see *reflexive*);
  - **adopter** — pins and consumes another party's artefact (the three institutions; `platform`
    itself as it pins `nist`), and becomes a **publisher** of its own **composed artefact** the
    moment it inherits from more than one parent.

- **Institution** — A regulated, risk-bearing adopter: `driftwood` (UK retail), `tuppence` (UK bank),
  `ludlow` (US health). Kept over "consumer" because it carries the regulatory weight the
  proportionality argument depends on, even though "consumer" better describes the dependency
  direction.

- **Regulator** — A publisher that ships controls or penalties as a signed, versioned artefact and
  bears no risk of its own here (`nist`, `ico`).

- **`org`** — **A deliberately overloaded term, documented rather than renamed.** In code and in
  emitted artefact fields it means *risk-bearer* — `tolerance_for(org)` resolves an appetite band and
  exits for a party that has none. In infrastructure it means *GitHub organisation*, which all six
  parties have. The overload is tolerated because `org` is a field name in emitted artefacts and
  golden digests, and renaming it would churn the provenance surface for a vocabulary win. Read it as
  "risk-bearer" in code, "GitHub organisation" in deployment.


- **Policy** — A set of rules that mitigates a risk. Comes in two intents: *security-enforcing*
  (e.g. data-at-rest encryption) and *consistency-enforcing* (e.g. required labels). A policy is
  only worth having if it carries its **purpose** ("purposeless policy is potentially practically
  pointless policy").

- **Exemption** — **A banned concept. There are none, ever.** An exemption is a carve-out for a named
  workload, and this project does not have them at any scope, in any file, under any name — the
  everything-is-codified rule admits no exceptions to itself. The legitimate alternatives, in order
  of preference: express the allowance as **conditional policy** ("you may do X *if* you meet
  conditions C", so anyone meeting C is treated identically and nobody asks a favour); or let the
  **cage implement the control on the workload's behalf** and price the residual. A workload that can
  satisfy neither is caged tighter until the cage is untenable — the bottom rung is "too expensive
  to run or not functional", reached by the £, never by a carve-out, and never a refusal (reversal 5). (The estate shipped an exemptions ledger that contradicted this; it is
  removed — see `.scratch/govern-what-you-dont-control/issues/05-remove-the-exemption-ledger.md`.)

- **Policy as a dependency** — The central move: treat a body of policy like a software
  dependency — semantically versioned, stored in version control, distributed to consumers,
  unit-tested, and updated via reviewed pull requests. NOT (primarily) a deploy-time gate.

- **The seven "-ables"** — The talk's checklist for "what good looks like". Each is an acceptance
  property the system must be able to claim: **visible, communicable, consumable, testable,
  usable, updatable, measurable.**

- **Cage** (supersedes the mea-culpa's lane-keeping vs. gate; rewritten 2026-08-28, ticket 09) —
  **There is no gate. Everything is always caged.** A workload, a human, a device, a model action
  and the twin itself each run inside a cage. The **cage spec** is the only variable, and the **£
  selects the spec**. The spec is a **tier** on one ladder: **baseline, restricted, quarantine,
  isolated, infra**. The mea-culpa's two ends survive as rungs: continuous, corrective guidance is
  the loose end; the **bottom rung is `isolated`** (the quarantine cage plus no ingress, no egress,
  first eviction) and it replaces every earlier deny or refusal, so nothing is ever refused, only
  caged. A "locked door" is therefore the bottom rung reached by the £, not a separate mechanism.
  In the owner's words (2026-09-02, ticket 75): the estate is a **mutating admission controller**
  more than a validating one; a workload can be unable to run only because it does not fit its
  cage, never because it is deliberately denied.
  **The one sentence (2026-09-05, ticket 89): nothing is denied; a workload that does not fit its
  cage does not run.** It is the sentence ADR-0014, ADR-0018 §4 and ADR-0022's 2026-08-28 addendum
  now all carry, replacing "the one refusal the doctrine allows". Which Deny-shaped rules the
  estate still SERVES, what was decided about each and what each waits for is the register at
  `verify/deny-is-not-a-rung/register.yaml`, graded on every run: this entry is doctrine, that
  register is the state of the code, and the check refuses to let them disagree.
  An unknown or unlabelled tier fails closed to `isolated`. The cage mutation is **tighten-only**: a
  tightened rule and the default cage never contradict. This *cage-tier* axis is independent of
  *adoption cadence* (ADR-0002). The tier is declared on the signed **governed namespace**
  manifest and rendered onto every pod in it; the **twin** computes it under the org's
  perspective and the **proposer** enacts it as a PR (re-grill 21). See ADR-0003 for the engine and
  ADR-0022 for the ladder.

- **The "why" / rationale** — Risk/threat-model metadata that travels *with* each policy version,
  so disagreement is resolved by a **pull request to the policy** (informed debate), not by an
  out-of-band **exemption request**. Grounded in threat modelling, not "emotional and anecdotal"
  reasoning.

- **Human-governance layer** (mea-culpa addition) — Versioning distributes policy to *engineers*
  but does not *govern* it. Borrowed from GDS Way: every accepted policy is **dated**, **regularly
  reviewed**, and **deleted if no longer defensible** ("Not archived. Not deprecated. Removed.").
  Realised as **editorial review** (a reviewed PR changes/removes a policy — never time-triggered;
  see [ADR-0006](docs/adr/0006-deterministic-policy-no-time-conditions.md)), supported by the agent
  governance layer. See [ADR-0007](docs/adr/0007-agent-assisted-editorial-governance.md).

- **Agent governance layer** — An AI/agent layer that reads each policy's embedded
  rationale/risk/ethos plus external signals (CVEs, cloud/regulatory change, Wardley climatic
  movement) and surfaces noise-reduced **business decisions** as review PRs/issues. It **prompts**
  editorial review; it **never edits enforcement**. Specified as architecture + a thin demonstrator.
  Its concrete instance is the **proposer**.

- **Proposer** (rewritten 2026-08-28, tickets 10 and 15) — The agent governance layer as it
  actually runs. A proposer war-games the signed feeds against the deployed controls, and it raises
  every resulting change as a reviewed PR. It edits the tier declaration in the signed **composed
  artefact**, never the label directly (reversal 13), and signs the proposal commit with the
  workflow's Actions identity (reversal 16). It is **bounded** by a confidence floor, a rate limit
  and the **rejection ledger**: a declined proposal decays and re-raises, and is never a register of
  accepted risk (re-grill 22). It exposes no `merge()` and no `approve()`. The **adopter** runs the
  proposer in its own repo, against its own **composed artefact**, because selection is the
  risk-bearing act. It may also open a PR that governs an **ungoverned namespace**. A run starts on
  a daily **schedule** (every unit has one; each org picks its time), when a merged version-pin bump
  lands, or when a human dispatches one. A scheduled run re-composes at today's date and proposes
  without committing: it runs the LLM-free steps (fetch, re-price, open the proposal) and may
  append an **observation**, never a **declaration**. Reasoning over the gathered results is
  packaged as Claude Code skills a human runs (reversals 7, 14, 15). Nothing timed ever changes a
  verdict on its own; the reviewed PR is the unit of adoption, and author and merger are different
  identities for now (re-grill 29). See
  [ADR-0015](docs/adr/0015-adopter-runs-the-proposer-and-it-opens-the-pr.md); its "nothing on a
  clock" clause is superseded by NORTH-STAR principle 5 and ticket 10.

- **Advisory metadata** — `created` / `lastReviewed` / rationale / risk / ethos carried on each
  policy version (annotations + `rationale.md`, OSCAL-mappable). Read by humans and the agent layer
  only; **never consumed by the engine** (keeps policy deterministic).

- **The last-mile problem** (mea-culpa addition) — Versioning reaches technical consumers but not
  non-technical ones (the talk's "Cleaner"). An explicitly **acknowledged open problem**, not
  something the system claims to solve.

- **Policy version** (rewritten 2026-08-28) — A semantic version of one package: a publisher's
  policy, a regulator's catalogue or penalty schema, a feed, or an adopter's **composed artefact**.
  Every package carries its own semver, and a composed set that extends others is a new package with
  its own version, as ESLint shareable configs do (re-grill 2, ticket 06). Semver is **computed from
  measured verdict movement, never declared** (ADR-0011): **major** = any change that moves a
  currently-caged workload to a tighter cage tier or turns a pass into a fail (a new or tightened
  `Deny`, an `Audit`→`Deny` promotion, free-text label → enum, a baseline addition); **minor** = an
  addition that moves nothing already caged (e.g. a new `Audit` policy); **patch** = fix/widening
  (the passing set only grows, and widening is priced, not refused). ("Don't be fooled by the
  decimal points — 1.20.0 > 1.3.0.") **Compliant means caged at a tier the £ accepts** — an `Audit`
  finding reports without moving the tier, so a workload carrying `Audit` findings is compliant for
  this definition. A **re-price is a release**: a feed that moves cages yields a computed bump, a
  signed tag and a Renovate PR (re-grill 8), and the £ cost of every computed move is attached to the
  signed evidence (re-grill 15). **Reset on bump** — against the base (the highest existing tag lower than the
  declared version), the leftmost component that increased must zero every component to its right; a
  gap is legal, but the historical `2.1.1` release fails this rule, correctly (base `2.0.1`, minor
  increased, patch should have reset to `0` but stayed `1`).

- **Multi-version coexistence** — A single runtime (cluster) must accept and evaluate **multiple
  policy versions simultaneously** (≥3), so old versions can be retired over a transition window
  rather than via a flag-day breaking change. *The crux of the original implementation.* The number
  is the owner's own (2022-03-11 post: retirement runs forward and back by one version, so at
  least three significant versions), re-affirmed 2026-09-02 (ticket 75 Q3) as three declared lines
  and a priced supersede.

- **Version pin** — The single declaration by which a consumer (workload / cluster) states which
  policy version applies to it. The original's signature elegance: **one string** served as both
  the dependency pin *and* the engine's workload selector.

- **Compliance / measurable** — The ability to answer "which part of the estate is on which policy
  version, and is it actually passing?" In the original this was a proxy ("a GitHub PR search
  away" — i.e. *bump acceptance*). See open question on proxy-vs-ground-truth.

- **Consumer** — A repo/workload that depends on a policy version (the original's `app1..3`,
  `infra1..3`). Opts in to a version and is judged against it.

- **Composed artefact** — A party's effective policy set, inherited from its parents' own signed
  artefacts (the diamond, e.g. `driftwood -> platform -> nist` and `driftwood -> nist`) and rendered
  down to the flat, per-version files the engine reads. The adopter signs it exactly as any
  **publisher** signs an artefact — the same gitsign-signed tag, no second mechanism — but the file
  also carries each parent's resolved commit SHA, once, declaring which parent versions it was
  rendered from. A verifier re-renders from those pinned SHAs and checks the result byte-for-byte.
  It holds **every kind** the version tree ships — `ValidatingPolicy`, `MutatingPolicy` and
  `GeneratingPolicy` — keyed on the identity family plus the name with its version stripped, because
  the `policy-as-versioned.dev/policy` label is a family name and not a unique key. It also carries
  the **platform-machinery** members under a second numbering axis, the platform tag, because they
  cannot self-scope to one claim.
  See [ADR-0012](docs/adr/0012-composed-artefact-self-signed-pinned-sha.md) and
  [ADR-0016](docs/adr/0016-a-subclass-never-restates-a-mutate.md).

- **Restatement** — A subclass declaring an inherited rule at a different strictness. A restatement
  is accepted only when it is **stricter**, on the `Audit < Deny` ladder; a weakening is never an
  override and never an **exemption**, it is a declared inability that is **caged** and priced. The
  ladder is a `ValidatingPolicy` concept, so a restatement applies to a `ValidatingPolicy` and to
  nothing else: a `MutatingPolicy` and a `GeneratingPolicy` carry no action, and a composition that
  restates one is refused. An adopter's only knob on the graded members is the cage **tier**, which
  is a priced verdict the £ selects and only the **proposer** turns.
  See [ADR-0016](docs/adr/0016-a-subclass-never-restates-a-mutate.md).

- **Baseline** — The named subset of a catalogue's controls that a party claims apply to it. A
  **regulator** publishes baselines by name, as OSCAL profiles, signed and versioned like any other
  artefact it publishes (NIST's own are LOW, MODERATE and HIGH, at 149, 287 and 370 controls). An
  **adopter** selects one by name, in the party artefact it signs, because selection is the
  risk-bearing act. An adopter may **add** controls to its selected baseline and may remove one;
  a removal is priced, never refused (ADR-0026, 2026-09-04): the regulator's **control weight**
  prices a control whether or not the adopter selected it, so a removal hides nothing from the
  pound, and it prints as a **delta** under the adopter's own signature. A control the adopter
  cannot meet is caged and priced, not dropped. A baseline control that nothing implements is a
  **hole**; a composition **prices** every hole, new or pre-existing, and a new hole moves the
  tier, never refuses (rewritten 2026-08-28, ticket 15; ADR-0026 supersedes ADR-0013 and ADR-0017
  on this point, ticket 39, 2026-09-04). A control the adopter adds is an ordinary new hole until
  a **control claim** fills it, and its removal prints as a delta like any other.
  See [ADR-0013](docs/adr/0013-regulator-publishes-baselines-adopter-selects.md) and
  [ADR-0017](docs/adr/0017-a-control-claim-belongs-to-whoever-ships-the-implementation.md) (both
  superseded in part) and
  [ADR-0026](docs/adr/0026-a-hole-is-priced-never-refused-the-claim-keys-on-source-and-id.md).

- **Control claim** — A signed statement, in a party's OSCAL component-definition, that a policy
  that party ships evidences a **control id**. A control claim belongs to whoever ships the
  implementation, and a party may never claim against a policy another party ships. Any party's
  claim fills a **hole**, including the adopter's own. Not the pod's *claim* label, which names a
  **policy version**. See
  [ADR-0017](docs/adr/0017-a-control-claim-belongs-to-whoever-ships-the-implementation.md).

- **Control id** — A control's identity is the **bare id the catalogue itself writes**: `ac-6`, never
  `AC-6` and never `nist-800-53:AC-6`. `AC-6` and `AC-06` are display labels the catalogue also
  carries, and are never keys. Which catalogue an id belongs to is stated once, by the `source` or
  `href` on the enclosing block, never repeated as a prefix on the id. Resolution is exact-string:
  no case-folding, no prefix-stripping, and an id absent from every pinned catalogue is a hard
  failure, a **missing instrument** (ADR-0020), because nothing pinned defines it. A **control
  claim** and a **hole** key on `(source, id)`: the catalogue the enclosing `href` names and the
  bare id there, so a second `controls` parent (an adopter's own catalogue) cannot collide with
  the regulator's ids; on the wire a bare id is the baseline catalogue's and `source:id` names any
  other parent (ADR-0026, 2026-09-04, refining ADR-0013). See
  [ADR-0013](docs/adr/0013-regulator-publishes-baselines-adopter-selects.md) and
  [ADR-0026](docs/adr/0026-a-hole-is-priced-never-refused-the-claim-keys-on-source-and-id.md).

- **Orphan guard** (rewritten 2026-08-28, ticket 09; corrected twice on 2026-09-05, ticket 89) —
  A **pair**, both rendered from the platform's declared version array. The guard is an `Audit`
  `ValidatingPolicy` that **reports** any workload whose `policy-version` label is **not in** the
  array and **never denies one**; the **orphan cage** is a `MutatingPolicy` that puts that same
  workload on the **bottom rung** — `isolated`, the caged marker, the isolated dials, the
  `cage-isolated` PriorityClass, host namespaces shut, all capabilities dropped on containers and
  initContainers — and `cage-netpol-bottom-rung` generates its deny-all NetworkPolicy. It judges
  a **claim**, and only a claim.
  This entry has been wrong twice and both are recorded rather than quietly fixed. From
  2026-08-28 it said the guard "cages to `isolated`": it did not, it shipped
  `validationActions: [Deny]` for another eight days and the gate graded the denial as correct.
  Its first correction said the workload is caged by **cage-tier**: that is also false, because
  **every served copy of cage-tier is scoped to its own version** (`only-this-policy-version`)
  and an orphan claim is by definition a version no served line carries — so cage-tier does not
  match such a pod at all, and the guard demoted alone left it running with no tier, no limits,
  no hardening and no reach cage. The cage above is what makes the demotion safe, and the two
  are disjoint by construction: cage-tier takes claims **in** the array, the orphan cage takes
  claims **not** in it.
  The versioned rules an orphan claim escapes are still a **priced hole** (ADR-0026), and the
  guard's report is the observation that price rests on. Folding the bottom-rung selection into
  cage-tier's own tier expression remains tidier and remains ticket 84's, because that is a
  versioned policy body and so a new declared line. A pod carrying no claim is handled by the cage mutation
  itself, which renders the **governed namespace**'s declared tier onto every pod at admission and
  clobbers whatever the pod carried; a governed namespace that declares nothing renders to
  `isolated`, and infrastructure is declared explicitly at the **infra tier** (re-grill 28,
  reversals 11 and 12). Together they close the original's silent-ungovernance gap in both forms: a
  retired claim and no claim each land in a cage, never outside policy. The `Deny` form was not
  "the July record" when this said so: it shipped until 2026-09-05 and ticket 89 removed it. The
  guard's own emitted policy is
  **platform machinery**, numbered by the platform's own tag, so a reader can tell it apart from an
  actually-unversioned policy. See
  [ADR-0014](docs/adr/0014-unclaimed-is-caged-governed-namespace-requires-claim.md) (superseded in
  part).

- **Governed namespace** (rewritten 2026-08-28, tickets 09 and 15) — A namespace inside which every
  workload is caged at the **tier** the namespace declares, marked by
  `policy-as-versioned.dev/governed: "true"`. The label and the tier on the adopter's own
  `Namespace` manifest **are** the declaration: the adopter writes them, signs them under the same
  tag as its **composed artefact**, and the composed artefact carries no namespace list of its own.
  The pod label is an output only, rendered from the namespace at admission. There is no `CREATE`
  deny **in what the platform renders** (ticket 89, 2026-09-05; between 2026-08-28 and that date
  this sentence was false and the estate shipped one): a pod that claims nothing is admitted by a
  `MutatingPolicy` onto the **bottom rung** and observed by a paired `Audit` report, and a
  namespace that declares no tier renders to `isolated`. **All three adopters still SERVE the
  `Deny`**, in what they composed under platform `v2.0.1`, and will until the owner merges that
  branch, `cut-release.yml` cuts the next signed tag and each adopter's pin bump re-composes;
  `verify/deny-is-not-a-rung/` grades exactly that gap and names the tag, and does not read green
  while a copy survives. The scope is `CREATE`, plus `UPDATE` for a pod the policy already caged
  — without `UPDATE` a caged pod could relabel its way out of its reach cage for good, and
  without the gate the mutation would inject a WAF sidecar into the de-posture patch's immutable
  container list and the API server would reject it, which is the cage becoming a refusal by
  another name. Its opposite is an **ungoverned namespace**, which is priced, never
  refused. See [ADR-0018](docs/adr/0018-the-namespace-manifest-is-the-governed-declaration.md)
  (§1 stands; §4 superseded by ADR-0022).

- **Currency controller** (the term, written 2026-09-05, ticket 91; it was an aside inside the
  retired **De-postured** entry below) — The estate's **only post-admission re-caging mechanism**,
  published by **platform** as a versioned member of its `implementations` package and numbered by
  the platform's own tag. Admission is a snapshot: the **cage** mutation and the **orphan guard**
  judge a pod once, when it is created, and never again. The controller is the second look. One
  bounded pass per minute, as a CronJob on the adopter's cluster, it reads the same version array
  the orphan guard allow-lists and, for every running pod whose **claim** the array no longer
  declares, does the one thing that sentence names:

  > a pod admitted under a version that is later retired is **re-caged to `isolated`** on the next
  > controller pass.

  It may only **tighten**. It writes the bottom rung and nothing else, it holds a pod it would not
  tighten, and its grant carries no `delete` on pods — a workload is never removed, only caged
  (ADR-0022; ticket 75 Q5). A version array it cannot read is a **missing instrument**
  (ADR-0020): the pass refuses and re-cages nothing, because an empty supported set would read the
  whole estate as stale. Ticket 13 item 2 retired it on a homonym — "ticket 07's fx feed replaces
  it", where that **currency** is money and this one is version currency — and ticket 75 Q13
  withdrew the retirement.

  **Its precondition, which is part of the term.** The re-cage patch removes the pod's **claim**,
  and every *served* copy of the reach-generating policy is gated on that claim. So a re-caged pod
  **cannot generate its own reach cage**: it can only be *selected* by a `cage-reach-isolated` the
  namespace **already carries**, generated when some pod claiming a currently-served version was
  admitted there above `baseline`. **In a namespace with none, the re-cage writes `isolated` as a
  label and changes nothing the pod can reach** — which is the state of `tuppence-reset` on the
  demo cluster today. Closing that is a separate question this mechanism does not own.

  **What it costs.** Tighten-only holds, and two things are softer afterwards. `infra` is a
  platform *role declaration* on a Namespace, not a rung, so a pod carrying it reads as unknown and
  is **overwritten** with the bottom rung rather than moved along the ladder. And the re-caged pod
  is outside the scope of the cage mutation, the **orphan guard** and the served reach policy
  alike, so its rung is held by a label no admission will ever re-assert; a claiming pod's rung is
  re-clobbered from its Namespace on every update, this one's is not, and what still holds it is
  RBAC — a workload cannot patch its own pod.

  Graded by `.estate-clone/platform/currency-controller/verify-currency.sh`, whose offline half
  derives the seam from the bodies the estate actually **serves** (never from the authoring copies
  under `graded/`, which no Kustomization serves and which lack the version gate that decides this)
  and whose live half is a named could-not-look until a cluster carries the instrument, a stale pod
  and a reach cage in that pod's namespace.

- **De-postured** (superseded 2026-09-05 by the **Currency controller** entry above; kept because
  ADR-0014 and the shipped `posture-trust-boundary` policy still use the word) — The state of a
  running workload whose claimed policy version has since been retired from the version array, and
  from which the currency controller has therefore stripped **both** the identity posture label and
  the version claim in one patch. The workload **keeps running** and is **caged**, not denied: it
  loses its posture-derived identity and the reach and secrets that identity buys, and the residual
  is priced against its party's appetite band. What the word never covered, and what ticket 91
  added, is the **rung**: stripping the claim takes the pod permanently out of the cage mutation's
  scope, so a patch that named no tier froze the pod at whatever rung admitted it and the
  retirement changed nothing. The patch now writes `isolated` in the same update. This is the
  **exemption**-free settlement in miniature — the bottom rung is "too expensive to run or not
  functional", reached by the £, and never a carve-out.

- **Twin** (rewritten 2026-08-28, ticket 11) — The eco-system's intelligence participant. It
  consumes the signed feeds, an adopter's own **twin overlay** and history; it publishes **priced
  forecasts and forward intelligence** under a declared **perspective**, signed by the twin agent
  (an **actor class** of its own) and scored against reality under proper scoring rules. Each
  adopter org (`driftwood`, `tuppence`, `ludlow`) has a twin of its own, whose overlay lives in the
  adopter's own signed repo with the shared world layer vendored and pinned by the same tag; the
  twin itself is a self-versioned, signed package. The eleven real firms it models today stay as
  the backtest corpus and as evals of the model and tooling (re-grills 31, 39). A subscribed feed
  version becomes a **sensed signal** by lookup, with no judgement; anything needing judgement is a
  skill a human runs. On every sweep it plays its **standing scenarios**. The twin **computes a
  cage tier** under the org's perspective; the **proposer** enacts it as a PR (re-grill 21). The
  twin acts inside a priced cage of its own; propose-only is the outermost setting, with an Article
  22 floor for significant decisions about people (re-grill 37). One £, many perspectives: no
  perspective is privileged (re-grill 33).

---

- **Feed** (added 2026-08-28) — A signed, versioned artefact that prices and carries no rules: a
  threat register, a CVE list, an EOL list, market intel, a penalty schema, a prediction-market
  move, a news event. Every feed is one **envelope**: `kind: feed`, a free `name`, a version, the
  publisher, a date, a payload schema and the payload. Only the payload differs between feeds. The
  signature is the publisher's tag (ADR-0012, ADR-0019).

- **Size facts** (rewritten 2026-08-28, ticket 24) — What an adopter declares about its own scale
  so a price is proportionate to it: turnover, customers, data subjects, headcount, optionally
  **relevant revenue**, and the date they were true. Signed by the adopter alone. Stale facts widen a
  price to the publisher's **widening target**; they never refuse one.

- **Obligation** (added 2026-08-28) — A regime an adopter declares it answers to, by name, in its
  party artefact. Only a declared obligation is priced. A declared obligation with no price in any
  subscribed feed is an instrument fault.

- **Reporting currency** (added 2026-08-28) — The one currency a party states every sum in. Every
  amount carries its own currency; a sum converts through a dated, signed FX feed or not at all.

- **Perspective** (added 2026-08-28) — Who pays and what their red lines are. A price is only
  meaningful under a named perspective. No perspective is privileged, and no sum crosses two.

- **Forward intel** (added 2026-08-28) — What the twin publishes: a scenario under a perspective,
  with its trade-off curve, signed by the adopter's twin agent. It never carries a recommended
  action. The estate prices it like any other feed.

- **Selection policy** (added 2026-08-28) — The adopter's own versioned, signed rule that turns a
  trade-off curve into one cage tier. The curve never picks; the policy does.

- **Price** (rewritten 2026-08-28, tickets 14, 15 and 24) — An annualised amount with a currency
  and a perspective, produced by the estate's engine from a scenario. A price with no perspective
  is not a price. A regime's price is the sum of its **holes**; a **switching cost** is a price; a
  **premium** is not (it is a cost on the sheet). Size arithmetic belongs to the publisher whose
  regime is priced, and the adopter only supplies its signed **size facts**. A price may be restated
  **per customer**.

- **Appetite** (rewritten 2026-08-28, ticket 14) — The annual loss an adopter declares it will
  carry, as an amount with a currency, signed by the adopter alone on its party artefact. The £
  selects the first cage tier whose residual sits under it. It also carries the adopter's cover
  terms, if any: **attachment and limit** with exclusions, so the attachment equals the appetite and
  the sheet shows retained, transferred and excluded loss summing to the simulated total.

- **Instrument fault** (added 2026-08-28) — The gate cannot read something it needs to price: a
  regime with no penalty schema, a date with no FX rate. It refuses. Contrast a priced hole, which
  is a behaviour the gate can read and prices (ADR-0020).

- **Parent kind** (rewritten 2026-08-28) — What a party's parent gives it. Exactly three:
  **controls** (a catalogue plus named baselines), **implementations** (policy bodies plus control
  claims), **feed** (prices, no rules). Closed; a new feed is a new `name`, not a new kind.

- **Subscription** (added 2026-08-28) — An adopter's pin of a parent, recorded in its signed party
  artefact with the date it first pinned. There is no other subscription record.

- **Discovery record** (added 2026-08-28) — A publisher's own declaration, in its signed party
  artefact, of what it publishes and which versions it has revoked. The set of these records is the
  only catalogue.

- **Revocation** (added 2026-08-28) — A publisher withdraws a feed version by publishing a newer one
  and listing the old one as revoked. A tag is never deleted. A pin to a revoked version is a priced
  hole: the cage tightens; it is never refused.

- **Tier** (added 2026-08-28, ticket 09) — The rung of the cage ladder a **governed namespace** is
  declared at: baseline, restricted, quarantine, isolated or infra. Declared on the signed
  Namespace manifest, rendered onto every pod in it, chosen by the **selection policy** against the
  price.

- **Isolated** (added 2026-08-28, ticket 09) — The bottom rung of the cage ladder. The workload
  runs with the quarantine cage, no ingress, no egress, and is evicted first. It replaces every
  earlier deny or refusal; nothing is ever refused, only caged.

- **Floor** (added 2026-08-28, ticket 09) — A tighten-only lower bound on the tier an adopter
  declares in its overlay. Selection clamps to the floor in ladder order. Lowering or removing a
  floor is priced, never refused. It is a constraint on selection, not a default tier and not an
  **appetite**.

- **Infra tier** (added 2026-08-28, ticket 09) — The cage a platform-role party declares for its
  own namespaces. Only a party whose signed party artefact carries the platform role may declare
  it; any other party's infra declaration renders to **isolated**.

- **Observation** (added 2026-08-28, tickets 10 and 16) — A dated record a **schedule** may append
  to a repo without review: a truth line, a drift sample, a **capture**. It asserts what was seen,
  never what should be, and never changes a tier, pin, floor, overlay or priced evidence.

- **Declaration** (added 2026-08-28, tickets 10 and 16) — An artefact that states what an org has
  chosen or signed, and so changes what the estate enforces or prices: a tier, a pin, a floor, an
  overlay, priced evidence. It reaches main only through a reviewed, signed PR, never from a clock.

- **Rejection ledger** (added 2026-08-28, ticket 10) — The set of closed-unmerged proposal PRs for
  one key, weighted by age with a half-life. It suppresses re-raising the same proposal for a while
  and is never a register of accepted risk. A proposal with a different price is a new proposal.
  Derived, never kept as a file.

- **Declared bump** (added 2026-08-28, tickets 10 and 18) — The versioned, reviewed statement of a
  release's intended semver step, which the release workflow reads and nothing else declares. For
  a feed publisher the fetch computes it from the payload change and reviews it in the feed PR;
  `none` opens no PR, and the observation still lands on the **observation branch**. Also called
  the bump file.

- **Degraded publish** (added 2026-08-28, ticket 18) — A publisher release whose declared bump the
  gate computed as weaker than the real change. It is published anyway, with a prerelease suffix on
  the declared number, a degraded evidence outcome and a quarantine tier on its version entry. The
  adopter prices it under its own perspective and composes it only by deliberate pin.

- **Twin overlay** (added 2026-08-28, ticket 11) — An adopter's own signed description of its value
  chain, roles, causal edges, perspective and **standing scenarios**, from which its
  **forward intel** feed is rendered.

- **Sensed signal** (added 2026-08-28, ticket 11) — A dated, sourced statement the twin plays
  forward; a new version of a subscribed feed becomes one by lookup, with no judgement applied.

- **Standing scenario** (added 2026-08-28, ticket 11) — A shock the twin keeps ready to play
  against an adopter's overlay on every sweep; six per adopter.

- **Trust domain** (added 2026-08-28, ticket 12) — The identity boundary owned by one party that
  runs a cluster. Each such party has exactly one. Trust between two domains is a federation the
  party records on its own party artefact and can withdraw alone.

- **Reach demand** (added 2026-08-28, ticket 12) — What a serving workload requires of a caller:
  the caller's trust domain, a minimum cage tier and a version window. Declared by the serving org
  in its own composed artefact. A caller that fails it loses reach to that service; the loss is
  priced on the caller's side, and it is never a gate.

- **Actor class** (added 2026-08-28, ticket 12) — One of five kinds of thing that holds an identity
  in the eco-system: workload, human, device, model action, and the twin agent. Each class has a
  named issuer and a distinct subject; no class shares another's subject.

- **Platform machinery** (added 2026-08-28, ticket 12) — The identity and access substrate the
  platform publishes as one versioned package with control claims, pinned and reconciled by each
  org like any other package, and declared at the **infra tier** on the platform's own namespaces.
  The **orphan guard** and the cage mutation belong to the same class: objects the platform's own
  tag numbers, not a policy version.

- **Supersede** (added 2026-08-28, ticket 13) — A publisher retires a version by publishing a newer
  one. A pin behind a newer published version is priced by the EOL ramp from the newer version's
  publish date. No consumer-side sunset field exists. Contrast **revocation**, which is withdrawal.

- **Handbook** (added 2026-08-28, ticket 13) — The human-readable render of an adopter's composed
  policy, produced at compose time and carried under the same signed tag as the artefact, so
  render-at-tag equals the committed render.

- **Lift** (added 2026-08-28, ticket 13) — Moving a mechanism or application from the original org
  into an eco-system party by re-label and re-pin, graded green by the truth surface before the
  original repo is archived.

- **Exposure** (added 2026-08-28, ticket 14) — The aggregate annual loss summary an adopter
  publishes under its own perspective in its composed artefact, built from its priced risks; the
  signed input an insurer quotes against. Public by design: the cost of a rival reading it is a
  priced scenario on the adopter's own sheet.

- **Quote** (added 2026-08-28, ticket 14) — A signed feed from the insurer naming one insured
  party, the cover terms, a **premium**, a validity window, what **exposure** it was priced against,
  and the conditions whose breach voids or uplifts it. A lapsed quote prices as fully retained.

- **Attachment and limit** (added 2026-08-28, ticket 14) — The annual aggregate loss band an insurer
  covers: below attachment the adopter retains (its tolerance), above limit it retains again.
  Exclusions name obligations or controls kept outside the band.

- **Premium** (added 2026-08-28, ticket 14) — The contract amount an adopter pays for a **quote**. A
  cost on the adopter's sheet, not a **price**, so it sums with retained loss and control cost.

- **Hole** (added 2026-08-28, ticket 15; built 2026-09-03, ticket 38) — A selected control no
  **control claim** covers, keyed `(source, id)`: the catalogue that defines it and its bare id
  there. Priced as the regulator's **control weight** for that control times the adopter's sized
  **exposure** for the regime, so the regime's price is the sum of its holes and implementing a
  control reduces it; a hole no pinned weight names carries no amount, a named absence rather
  than a zero. Never refused, never counted; the new-hole and widening refusals are gone and
  each new, closed or widened hole prints as a **delta** on the evidence document under the
  adopter's own perspective and currency. A removal prints as a `removed-control` delta carrying
  the amount the hole carried, and the regime's price does not move (ADR-0026, 2026-09-04; its
  platform build waits).

- **Delta** (added 2026-09-03, ticket 38) — What changed since the adopter's last signed composed
  artefact and what a pinned instrument prices it at: a new or closed **hole**, a baseline
  widening, a new or closed **ungoverned namespace**. Each carries the adopter's perspective and
  currency and an amount or a named absence. A delta is a report of a priced move, never a wall;
  it replaced the three composition refusals ADR-0013, ADR-0017 and ADR-0018 point 3 carried
  (recorded by ADR-0026, 2026-09-04), which also makes a removed control and a baseline narrowing
  deltas once their platform build lands.

- **Control weight** (added 2026-08-28, ticket 15) — A regulator's published statement, keyed on
  the catalogue and **control id**, of which controls a violation type turns on. Part of the
  penalty feed; changing it is a major version.

- **Ungoverned namespace** (added 2026-08-28, ticket 15; built 2026-09-03, ticket 38) — A
  namespace in an adopter's repo carrying the institution label without the governed label.
  Priced as its workload share (pod-owning kinds in the repo walk, over the same across every
  institution namespace) of the adopter's whole uncaged residual, LEF-ramped by the EOL feed's
  own ramp from `since` — the date of the first signed tag whose composed header recorded it,
  read off tag history so it survives a close and a reopen — as of the newest pinned feed's
  publish date, and bounded at the whole residual. What cannot be read (no signed tag names it,
  no feed prices the residual) is a named limit on the price, never an invented date or a zero.
  Never refused. The **proposer** may open a PR to govern it. The live case is tuppence's
  `tuppence-reset`, recorded since 2026-08-25.

- **Bespoke control** (added 2026-08-28, ticket 15; built 2026-09-03, ticket 38) — A control an
  adopter defines itself, published as a small OSCAL catalogue of which the adopter is the source
  and pinned as a `controls` parent of itself (the self-pin resolves to the adopter's own tree,
  signed by the same tag as its composed artefact); named in `overlay.controls` as `party:id`
  and priced by the scenario the control's `scenario` prop names. Priced only by a scenario the
  adopter signs; without one it is an **instrument fault**.

- **Register entry** (added 2026-08-28, ticket 15) — A twin blast-radius hit that cannot be
  priced. Crosses the pound seam in the **forward intel** payload and takes the cage tier selected
  for the priced hits in the same scenario, strictest if none priced. Unpriceable never means
  unenforced.

- **Verified source** (added 2026-08-28, ticket 16) — A publisher's repository fetched by a
  consumer cluster only so its signed tag can be checked at the source boundary and its resolved
  commit compared with the composed set's recorded parent. Nothing is installed from it.

- **Switching cost** (added 2026-08-28, ticket 19) — The annual £ an adopter would bear if it
  dropped one publisher: the holes and price moves that open when that publisher's edges are
  removed. Computed by the adopter's composition, never stated by the publisher, and carried as a
  **price** with a perspective and currency.

- **Reliability score** (added 2026-08-28, ticket 19) — A published measure of how well a
  publisher's past prices matched realised outcomes, issued as a feed by a party that publishes no
  scored feed. A score below an adopter's declared threshold widens that adopter's price range until
  it re-pins or the score recovers.

- **Vendored payload** (added 2026-08-28, ticket 19) — The copy of every feed payload and converter
  an adopter priced, kept inside its own signed composed artefact, so the adopter can re-derive its
  prices with no publisher reachable.

- **Capture** (added 2026-08-28, ticket 20) — The saved output of one truth-surface verify script
  from one named gate run. An **observation**, never a **declaration**. The only source a demo beat
  may quote a figure from.

- **Could-not-look** (added 2026-08-28, ticket 20) — A demo beat's rendering when the gate's script
  for that step exited SKIP; shows the gate's reason. Distinct from "no check yet", the generator's
  own status for a step with no verify script, which carries no gate grade.

- **Market-moves feed** (added 2026-08-28, ticket 22) — A signed **feed** of dated price levels per
  prediction-market question, selected by a versioned mechanical rule. It carries series, never
  moves or probabilities. The twin derives moves and binds them; the estate never prices a market
  level directly.

- **Observation branch** (added 2026-08-28, ticket 22) — The branch on a publisher repo where a
  scheduled fetch appends **observations** every run. A release PR opens from it only when the
  feed's own rule says the series changed.

- **News feed** (added 2026-08-28, ticket 23) — A signed **feed** of observed, dated events. Each
  entry says only what was said, when, and where it was read. It carries no classification,
  coordinate or scope. Planted stimuli never enter it.

- **Headline skill** (added 2026-08-28, ticket 23) — Judgement a human runs over unbound signals.
  It proposes which component a headline binds to and, if the human judges a move, an attributable
  position override. Its output enters by reviewed PR and is scored later.

- **Claim scope** (added 2026-08-28, ticket 23) — A statement carried by a **forward intel**
  scenario naming what it asserts (a judged position by a named role) and what it does not (an
  independent engine finding), with the claims it derives from.

- **Relevant revenue** (added 2026-08-28, ticket 24) — An optional **size fact** an adopter may
  declare for a regime priced on the revenue of the business area in breach rather than global
  turnover. Defaults to turnover when undeclared.

- **Fit check** (added 2026-08-28, ticket 24) — A published fine printed beside a size-derived
  price so a reviewer can judge whether the price is plausible. It never enters the price.

- **Widening target** (added 2026-08-28, ticket 24) — The sourced amount a publisher ships on a
  formula that has no statutory cap, used as the widening target when an adopter's **size facts**
  are stale. Also called widen-to.

- **Per customer** (added 2026-08-28, ticket 24) — A **price** restated as the amount divided by the
  adopter's declared customers, under the same perspective and currency. Never summed; absent when
  customers is undeclared.

- **Provisions** (added 2026-08-28, ticket 24) — A publisher-shipped count of the distinct
  provisions a violation type breaches, multiplying a per-provision annual cap. Defaults to one.

## Project posture (resolved)

- **Fidelity = "faithful to intent."** Reproduce the thesis and its ethos 1:1, but let Flux do
  natively what the 2022 implementation had to hack (the scaffolding that only existed because
  GitOps tooling couldn't yet express "versioned policy as a live dependency" is dropped, not
  preserved). The PRD targets this **faithful-to-intent floor**; a separate **modern-reference
  report** (`docs/modern-reference-transport.md`) documents transport upgrades. The north star is
  [NORTH-STAR.md](NORTH-STAR.md).

- **Transport = signed git tags, keyless (gitsign).** Policy is distributed as semver **git tags**
  (faithful to 2022), signed **keyless** with `sigstore/gitsign` (no long-lived GPG keys). Consumed
  via a Flux `GitRepository` pinned on `spec.ref.tag` **and `spec.ref.commit`** (the tag's resolved
  SHA — force-move-proof; Renovate writes both). See [ADR-0001](docs/adr/0001-transport-signed-git-tags-gitsign.md).
  - **Known limitation (accepted):** Flux `GitRepository.spec.verify` is PGP-only and cannot verify
    gitsign signatures today, so there is **no Flux-native verified-source admission gate** on the
    floor. Verification happens **in CI / at-merge** (`gitsign verify` against Rekor). The native
    gate is pending upstream **[fluxcd/source-controller#1068](https://github.com/fluxcd/source-controller/issues/1068)**
    (a tracked project action — see `docs/upstream/`).
  - **Deferred to north-star (need OCI):** signed *attestations* carrying the "why", and SBOM. On
    the floor the rationale rides as versioned files in the policy repo (Kyverno annotations +
    `rationale.md`).

- **Adoption cadence = pinned everywhere + Renovate PR.** Consumers and clusters pin exact tags;
  new versions land only via a reviewed Renovate PR (`automerge:false`), in every environment.
  Live semver ranges are rejected. See [ADR-0002](docs/adr/0002-adoption-pinned-plus-renovate-pr.md).
  **Adoption cadence (pin vs range) and enforcement action (Audit vs Deny) are independent axes** —
  do not conflate them.

- **Engine = Kyverno; policies authored as CEL `ValidatingPolicy`.** See
  [ADR-0003](docs/adr/0003-kyverno-validatingpolicy-cel.md).

- **Two planes:** **workload plane** (native Kubernetes workloads) and **cloud plane** (cloud
  resources). Both governed by the *same* versioned Kyverno engine. The cloud plane is built by
  **harvesting** ControlPlane's **collie** (cloud-as-CR) — its OSCAL catalogue + policy intent as
  data; its generator/Lula toolchain dropped. See
  [ADR-0004](docs/adr/0004-cloud-plane-fork-collie.md).

- **Deterministic policy.** Policy bodies contain no time-conditional logic (no expiry/start
  dates); the same manifest + same policy version always evaluates the same. See
  [ADR-0006](docs/adr/0006-deterministic-policy-no-time-conditions.md).

- **Sunset = scheduled proposal, never scheduled application.** A fleet's array entry may carry a
  `sunset:` date; on that date a machine opens a retirement PR that a human must merge — nothing
  timed ever changes an admission verdict on its own. See
  [ADR-0010](docs/adr/0010-sunset-scheduled-proposals-not-application.md).

- **Install/fleet layer = ControlPlane Flux Operator** (`FluxInstance` + `ResourceSet` matrix);
  thesis stays vanilla-Flux-expressible. See
  [ADR-0005](docs/adr/0005-controlplane-flux-operator-resourceset.md).

- **No bespoke tooling.** Developer/CI shift-left uses native CLIs directly (`flux build`/`flux
  diff` | `kyverno apply`/`kyverno test`, `gitsign verify`) — no wrapper, no re-implemented
  `policy-checker`. The 2022 bash/Docker checker is deleted, not ported.

- **Proof = KiND, free & reproducible.** Workload plane runs fully on KiND; the cloud plane is
  proven at the admission level — current Crossplane v2 provider-family CRDs installed in KiND, CR
  specs judged by Kyverno at admission (no ProviderConfig, auth, or reconcile); no LocalStack/AWS on
  the critical path. `wait` + CEL health checks replace jsonpath polling. A
  real-cloud e2e (live RDS/S3, optional LocalStack provisioning, C2P over realized state) is
  optional and documented.

---

## Flux terms (plain-English, for the glossary)

- **[Flux](https://fluxcd.io/) / GitOps Toolkit** — A set of Kubernetes controllers that continuously make the cluster
  match desired state declared in Git/registries. Replaces "run a script to apply things".
- **Source object** (`GitRepository` / `OCIRepository`) — A declarative object saying "the policy
  lives *here*, at *this version*." The **pin** lives on its `spec.ref`.
- **`Kustomization`** (Flux) — A declarative object saying "apply the manifests from that source,
  in this order, and keep them applied."
- **OCI artifact** — The policy bundle packaged and pushed into a container registry (like an
  image, but it's policy files), addressable by an immutable digest and signable with cosign.
  *Not used on the faithful floor* (see ADR-0001); relevant to the north-star report.
- **[gitsign](https://github.com/sigstore/gitsign)** — Sigstore's keyless signer for git **commits/tags**: signs with a short-lived
  Fulcio cert via OIDC (no long-lived key), logged in the Rekor transparency log. Verified with
  `gitsign verify` (not plain `git verify-commit`). Flux cannot verify it yet (issue #1068).
- **[cosign](https://github.com/sigstore/cosign)** — Sigstore's keyless signer/verifier for **OCI** artifacts. Flux *can* verify it
  (`OCIRepository.spec.verify`). The OCI-world counterpart to gitsign.
- **Pin vs. range** — A *pin* is an exact version (`ref.tag: 2.1.1`); a *range* (`ref.semver:
  ">=2.0.0"`) lets Flux auto-adopt new matching versions with no human in the loop.
- **Flux Operator** (ControlPlane) — Installs/manages Flux declaratively via a `FluxInstance` CR,
  with distroless/FIPS-hardened images. Used as the install + fleet layer (ADR-0005). The thesis
  stays vanilla-Flux-expressible regardless.
- **`ResourceSet`** (Flux Operator) — Templates many objects from a table of inputs. Used to
  generate the coexistence matrix (clusters × policy versions) as data.

## Cloud-plane terms

- **[Crossplane](https://crossplane.io)** — Lets you declare cloud resources (an RDS instance, an S3 bucket) as Kubernetes
  custom resources, so cloud is provisioned and reconciled by Kubernetes controllers.
- **cloud-as-CR** — The pattern of representing cloud intent as Kubernetes CRs (via Crossplane) so
  the *same* Kyverno engine governs cloud at admission/runtime, exactly as it governs workloads.
- **[collie](https://github.com/controlplaneio/collie)** — ControlPlane's (Apache-2.0, dormant since 2023) toolkit demonstrating Kyverno
  governance + compliance for Crossplane-provisioned cloud infra. We **harvest** its reusable IP (the
  NIST 800-53r5 → RDS/S3 policy intent + OSCAL catalogue) and rebuild the cloud plane natively; its
  generator/Lula/bootstrap are dropped (ADR-0004).
- **[OSCAL](https://pages.nist.gov/OSCAL)** — NIST's Open Security Controls Assessment Language: a machine-readable standard for
  expressing security control catalogues, baselines, and assessment results. The formal carrier of
  the "measurable" pillar on the cloud plane.
- **[C2P — Compliance-to-Policy](https://github.com/oscal-compass/compliance-to-policy-go)** — OSCAL Compass (CNCF Sandbox) tool. Its `result2oscal`
  direction consumes the Kyverno PolicyReports the single engine already emits and produces OSCAL
  **assessment-results** (controls satisfied/not). The carrier of the "measurable" pillar's control
  attestation. See [ADR-0009](docs/adr/0009-oscal-attestation-via-c2p.md).
- **[Policy Reporter](https://github.com/kyverno/policy-reporter)** — Kyverno sub-project: PolicyReport CRs → Prometheus/UI/dashboards. The
  live measurability layer beneath C2P.
- **NIST 800-53r5** — The US-federal control catalogue collie ships policies against (illustrative
  for UK; a UK CAF/GovAssure catalogue can be added — OSCAL is framework-agnostic).

---

## Decision log

See `docs/adr/` for the hard-to-reverse decisions and their rationale.
