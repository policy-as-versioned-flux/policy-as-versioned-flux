# 03 — The Canonical "Policy as [Versioned] Code" Thesis

Captured from three primary sources by Chris Nesbitt-Smith (CNS):

1. **Original Medium post** — *What is Policy As [versioned] Code?*
   <https://chrisns.medium.com/what-is-policy-as-versioned-code-306e0341290b>
   (canonical URL; the `medium.com/@chrisns/...` link 302-redirects here)
2. **The talk** — *Policy as [versioned] code* (the "-able" properties live here, not the blog)
   <https://talks.cns.me/PolicyAsVersionedCode.html>
3. **The "mea culpa" technical-argument post** (later, refined position)
   <https://blog.cns.me/posts/policy-versioned-code-mea-culpa-technical-argument-nesbitt-smith-pedef/>

> **Important sourcing note:** The Medium post is the *technical how-to* (semver, Renovate,
> multi-version runtime support). The seven "-able" properties and the "Purposeless policy…"
> one-liner are from **the talk**, not the Medium article. The blog post is the **revision** of
> the whole argument and is the most important source for the Flux design — treat it as the
> refined thesis.

---

## 1. The core thesis

Treat **policy as a versioned software dependency**, not as a gate.

> "If policy is a dependency, then it should behave like one. It should have a version number.
> It should follow semantic versioning. It should live in a Git repository." — *blog (mea culpa)*

The original framing (Medium) is the technical mechanism:

- Policies fail **silently in production**: a deployment that violates policy breaks `main`/`master`
  without the developer knowing, unless they actively watch event logs. The dependency model
  prevents the "broken main branch" scenario by letting consumers **test against a specific policy
  version before deploying**.
- Policies get **semantic version numbers** (e.g. `1.20.30`):
  - **major** = wholly incompatible / breaking change
  - **minor** = backwards-compatible addition (e.g. new functionality)
  - **patch** = backwards-compatible bug fix
  - (verbatim caveats from the post: *"Don't be fooled by the decimal points, they're not real
    (1.20.0 is greater than 1.3.0)"*)
- The **runtime must support multiple policy versions simultaneously** — at least three semver
  versions — to allow *"transitionary periods for old policy versions to be retired."*

Medium post structure (verbatim headings, in order):
*The status-quo → What happens when you want to update the policy itself? → So what can you do about
all of this? → Quick recap semantic versioning → Your runtime needs to support multiple policy
versions 😱 → Show me the code → Caveats → Now, it's your turn.*

The Medium post is explicitly a continuation of *"PodSecurityPolicy is Dead, Long live…?"* and ends:
> "As you can see, this is far from the finished article."

---

## 2. The seven "-able" properties (verbatim — from the TALK)

The talk presents these on a slide headed **"(easily:)"**, each ticked off (✅) as it is satisfied
by semver + dependency management + testing:

| Property | What it means (synthesised from talk + Medium framing) |
|---|---|
| **visible** | Policy is visible in a repository — not hidden. Security-through-obscurity is rejected. |
| **communicable** | Versioning + release notes let you communicate changes and manage expectations via semver. |
| **consumable** | Policy should be readily consumable and easy to parse by the consumer. |
| **testable** | Tests give everyone confidence in stability and surface potential side-effects (pass/fail examples). |
| **usable** | Consumers can test *themselves* against the policy locally and in CI/CD before deploying. |
| **updatable** | Updating policy is no different to any other dependency — use Dependabot / Renovate. |
| **measurable** | You can measure adoption/compliance (the status quo is *"slow if not impossible to update and measure"*). |

> These seven words are the backbone of the canonical thesis. They are the talk's checklist for
> "what good looks like." The Flux design should be able to claim each one.

---

## 3. The central one-liner and the "why"

> **"Purposeless policy is potentially practically pointless policy."**

On the slides each word is emphasised individually across separate slides, then reunified — it is
the memorable closing statement.

The argument behind it: **policy must carry its rationale — its risk and its "why."** When teams
understand *why* a policy exists (the risk it mitigates, the organisational rationale), they embrace
it rather than route around it. This enables **informed debate through pull requests rather than
exemption requests**, and lets policy evolve as the risk landscape and business needs change.

Medium reinforces this:
> "the advantages of exposing policy and communicating that effectively with its developers far
> outweigh any potential security advantage" — and policy should be *"grounded in informed threat
> modelling"* rather than *"emotional and anecdotal"* reasoning.

---

## 4. The mea culpa — what changed (CRITICAL for the Flux design)

### 4a. What "pedef" / the slug is about
The slug `...nesbitt-smith-pedef` is **not** an acronym defined in the post. It appears to be a
generated permalink suffix, not a concept. (No "Policy Enforcement Definition Framework" or similar
is introduced in the text. Do not invent meaning for it in the PRD.)

### 4b. The literal "mea culpa" (attribution)
The first-order confession is about **credit, not technical error**. CNS realised the idea's lineage
traces to **Michael Brunton-Spall's 2016 GOTO Amsterdam talk** ("Rugged: Being Secure & Agile"),
which he had internalised so completely he forgot the source:

> "I owe someone a credit… For six years I carried an idea around, refined it, engineered it into
> working code, and presented it at twenty-one conferences across three continents without once
> citing where it came from."
> "I had been so thoroughly convinced by his argument that I forgot it was his."

### 4c. The TECHNICAL revisions — what he now concedes was oversimplified

**(i) Not everything is a dependency. Some policy belongs at the gate.**
The original "policy as dependency" framing over-reached. He now draws a hard line using
**Gregor Hohpe's guardrail vs. lane-keeping-assist distinction**:

> "A guardrail stops you at the point of failure. Lane keeping assist nudges you continuously,
> correcting in real time before you ever reach the edge."

> "Most policy-as-code implementations treat policy as a gatekeeper. An admission controller that
> blocks your deployment… Policy should be lane keeping assist… Policy should be a dependency —
> versioned, tested, consumed, and updated automatically — not a gate."

But — the honest limit:
> "Now — I need to be honest about the limits of this argument. **Some policies belong at the gate.**
> Access control. Data protection. Cryptographic key management…"
> "Policies that govern **whether a workload is permitted to exist at all** — security boundaries,
> data classification, access control — those belong at the gate."
> "If a workload is about to deploy with an unencrypted database connection to a production
> environment containing personal data, I do not want lane keeping assist. **I want a locked door.**"

**The refined split (this is the load-bearing design decision):**
> "Policy should be lane keeping assist where lane keeping assist is appropriate. And that turns out
> to be **most of the policy surface area that enterprises actually struggle with**. The labelling.
> The tagging. The configuration standards. The operational metadata."

- **Dependency / lane-keeping model (~80% of surface):** labelling, tagging, configuration
  standards, operational metadata → versioned, distributed as automated PRs, unit-tested,
  adopted gradually.
- **Admission-control / gate (catastrophic boundaries only):** access control, data protection /
  data classification, cryptographic key management → a "locked door."

**(ii) "The thing I missed was the human part."**
Versioning alone is insufficient — it solves distribution for *engineers* but not *governance*.
He imports **GDS Way**-style human review cycles:

> "A team notices a practice that works… and they submit it as a proposal. Other teams review it,
> challenge it, adopt it or push back. **Every accepted practice carries a date. Every practice must
> be regularly reviewed**… if nobody can argue that a practice is still good… it gets **removed.
> Not archived. Not deprecated. Removed.**"

So policy must be **dated, defended, and deleted-if-undefended** — active governance, not just Git
history.

**(iii) The "last mile" problem.**
Versioning bridges engineers, not non-technical consumers ("the Cleaner"):

> "The dependency model provides the single source of truth… But the **last mile to non-technical
> consumers** — how the Cleaner's manual stays in sync — is a different problem that the versioning
> alone does not solve."

### 4d. Measurability, concretely
> "Renovate — the dependency update tool — has generated **over 1,222 automated pull requests**."
> "When the CIO wants to know how many teams are compliant, the answer is **a GitHub PR search
> away**." (adoption measured via PR acceptance.)

---

## 5. References to Flux / GitOps / OCI / admission control / runtime distribution

| Concept | Present? | Notes for the Flux PRD |
|---|---|---|
| **Admission control** | Yes (refined) | Reframed as the *minority* path — only for catastrophic boundaries (access/data/crypto). The "gate." |
| **Runtime multi-version distribution** | Yes (Medium) | Runtime must serve ≥3 semver policy versions concurrently; old versions retired over a transition window. **This is the direct hook for OCI-distributed, versioned policy bundles.** |
| **Dependency distribution** | Yes | Renovate / Dependabot push policy updates as PRs. The "pull" update mechanism. |
| **GitOps** | Implied, not named | Git as single source of truth, PRs as the change/debate mechanism. CNS does **not** use the word "GitOps." |
| **OCI** | **Not mentioned** | Opportunity: the Flux design can satisfy "consumable/updatable/multi-version runtime" via OCI artifacts. New contribution, faithful to thesis. |
| **Flux** | **Not mentioned** | Entirely new. Must map onto the refined thesis (dependency for the 80%, gate for the rest, plus human governance + last-mile). |
| **Engines named** | Kyverno (primary), OPA (implied/historical), Checkov, Renovate, KiND, GitHub Actions, Kustomize, Terraform | Kyverno is the reference engine in both eras. |

---

## 6. Quotable passages for the PRD "background / thesis" section

- *"Purposeless policy is potentially practically pointless policy."* (talk — the headline)
- *"If policy is a dependency, then it should behave like one. It should have a version number. It
  should follow semantic versioning. It should live in a Git repository."* (blog)
- *"Policy should be lane keeping assist where lane keeping assist is appropriate. And that turns out
  to be most of the policy surface area that enterprises actually struggle with."* (blog — refined thesis)
- *"Policy should be a dependency — versioned, tested, consumed, and updated automatically — not a gate."* (blog)
- *"Some policies belong at the gate… If a workload is about to deploy with an unencrypted database
  connection to a production environment containing personal data, I do not want lane keeping assist.
  I want a locked door."* (blog — the limit)
- *"Every accepted practice carries a date. Every practice must be regularly reviewed… it gets
  removed. Not archived. Not deprecated. Removed."* (blog — governance)
- *"The advantages of exposing policy and communicating that effectively with its developers far
  outweigh any potential security advantage."* (Medium — visibility)
- *"When the CIO wants to know how many teams are compliant, the answer is a GitHub PR search away."*
  (blog — measurable)

---

## 7. Design implications for "Policy as Versioned Flux"

1. **Honour the split.** The system is a **dependency/lane-keeping distributor for the ~80%**
   (labels, tags, config, operational metadata), *and* must still allow a hard **admission-control
   gate** for the catastrophic minority (access control, data classification, crypto). Do not build a
   gate-only system — that is exactly the mistake v1 over-corrected and v2 walked back.
2. **Multi-version runtime is non-negotiable** (≥3 semver versions concurrently, with a retirement
   window). OCI artifacts + Flux are the natural delivery for this — a contribution the thesis invites
   but never named.
3. **Carry the "why".** Each policy artifact must carry rationale/risk metadata so debate happens in
   PRs, not exemption tickets. Satisfies *communicable* and the "purposeless policy" thesis.
4. **Satisfy all seven "-able"s** as acceptance criteria: visible, communicable, consumable, testable,
   usable, updatable, measurable.
5. **Add the human governance layer** v1 missed: dated policies, mandatory review, delete-if-undefended.
6. **Don't forget the last mile** — versioning alone does not reach non-technical consumers; note this
   as an explicit open problem in the PRD rather than claiming Flux solves it.
