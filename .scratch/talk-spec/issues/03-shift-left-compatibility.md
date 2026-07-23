# Shift-left policy-version compatibility (dev + CI, before deploy)

Type: prototype
Status: resolved
Blocked by: 02

## Question

Design the mechanism by which a team knows *before deploy* whether their workload is compatible
with the policy versions a target cluster supports — so a deploy-time failure (even to dev) becomes
practically unheard of. Pin the model:

- **Server advertises supported versions** — how does a cluster publish "I support policy versions
  {…}"? (service-discovery analogy). Is it a discovery endpoint, a well-known ConfigMap/CR, a Flux
  artifact? How does the currently-installed `ResourceSet` array become a *consumable contract*?
- **Compatibility window** — adopt a kubectl-style **±1 version-skew** rule, or exact-pin, or a
  declared range? What does "compatible" mean when a control tightens Audit→Deny between versions?
- **The check runs left** — a local dev command and a CI gate that fetch the target's supported
  versions and run the *same* evaluation the cluster would at admission, against the app's manifests,
  offline. Reuse the existing shift-left dev-workflow (`docs/shift-left-dev-workflow.md`) as the
  seed. What's the developer UX — one command, clear pass/fail, "you're on 1.0.0, cluster wants
  ≥2.0.0, here's what fails"?
- **Culture wiring** — CI fail = loud and normal; deploy-time fail = alarm. How do we make the
  left check the path of least resistance rather than a box-tick?

Output: the discovery contract + the dev/CI check design + a rough prototype of the client command.

## Answer

Settled at the decision level (research 08 + the model). **Demonstrable core = the live CI ±1-skew
check:** the cluster advertises its supported policy version(s) via the `ResourceSet` array; dev/CI
reads it kubectl-style (±1 skew), and `kyverno apply` runs the *target version's real action*
offline — so an Audit→Deny flip is caught **in CI, before merge**. That CI catch **is the shift-left
beat** (2026-07-23). **No dedicated dev cluster** — the "a deploy-time fail even to dev is unheard-of"
line stays *narrated*. A per-institution dev cluster is affordable (Q2) and remains optional: build
it only if we later want "watch it pass CI, then land clean in dev" live. Rest is build-work.
