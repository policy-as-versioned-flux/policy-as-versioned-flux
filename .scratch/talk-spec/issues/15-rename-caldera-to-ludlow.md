# Rename the health institution: caldera → ludlow (name clash)

Type: grilling
Status: resolved
Blocked by: 01

## Question

`caldera` clashes with [`apache/caldera`](https://github.com/apache/caldera) — MITRE's
adversary-emulation / red-team platform. In a **security-governance** talk that is the worst kind of
clash: the audience hears "the other Caldera". Pick a clash-free replacement for the US-health/HIPAA
institution and rename everywhere.

## Answer

**Renamed to `ludlow` (2026-07-23; user's choice.)**

- **Why rename:** `apache/caldera` is a security tool; naming a demo institution `caldera` in a
  security talk is a collision, not a coincidence the audience will forgive.
- **Vetting discipline (don't swap one clash for another):** checked candidates against
  security / Kubernetes / DevOps / AI-agent tooling. Rejected: **Cairn** (`cairn-dev/cairn`, an
  AI agent that opens PRs — too close to our war-gamer), **Tarn** (`kube-tarian/Tarn`, a k8s
  shift-left security tool — caldera again), **Meridian** & **Halcyon** (both real health *and*
  security companies). **Institution-style British place-names came up clean;** user picked
  **`ludlow`** (Ludlow, Marlow, Alderney all vetted clear).
- **Siblings are fine:** `driftwood` / `tuppence` don't surface in any security/k8s search;
  `nist` / `ico` are intentionally the real regulators (the `policy-as-versioned-` prefix is the
  impersonation guardrail).
- **Done:** all 22 text occurrences renamed across `map.md`, `the-whole-model.md`, `spec.md`, the
  affected tickets (01, 04, 12) and `pitch/slides.py`.

**GitHub org renamed (2026-07-31, via browser):** `policy-as-versioned-caldera` → `policy-as-versioned-ludlow`
— done (`ludlow` resolves, `caldera` 404s; GitHub set up repo redirects). Was safe — the estate is empty (build-fresh),
and GitHub preserves an app install across an org rename, so the Renovate onboarding (ticket 12)
survives. The built `pitch.mp4` is stale regardless and re-renders from the updated `slides.py`.
