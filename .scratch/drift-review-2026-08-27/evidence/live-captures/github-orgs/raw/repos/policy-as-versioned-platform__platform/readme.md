# policy-as-versioned-platform

**GitHub org:** [`policy-as-versioned-platform`](https://github.com/policy-as-versioned-platform) ·
**Role:** publisher, risk-bearer · **Licence:** [Apache-2.0](LICENSE)

Part of the *Policy as Versioned Code* estate: a shared platform, two regulators, three regulated
institutions, each its own independent GitHub organisation, exchanging signed, versioned
dependencies. Full thesis, design decisions (ADRs) and the other five parties:
[policy-as-versioned-flux](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux).

**The shared discipline** — the governance machinery every institution inherits
as a *pinned, signed dependency* (the `config-base` pattern, one level up), so
the same apparatus is inherited rather than copy-pasted per institution.

What lives here (built across later tickets — this is the skeleton):

- **Flux distribution templates** — `ResourceSet` version fan-out, signed
  `GitRepository`, prune-on-retire, drift-heal, `dependsOn`/health, the
  notification event spine. *(ticket 03)*
- **FAIR risk engine** — `(min,mode,max)` → beta-PERT → Monte-Carlo → ALE ·
  VaR₉₅ · TVaR + risk load. *(ticket 01)*
- **the cage → OSCAL `risk`/POA&M up-flow** — a one-off that fails a check is
  caged, priced, never exempted (no ledger; banned outright, see `CONTEXT.md`).
- **shift-left harness** — ±1 version-skew off the `ResourceSet` array.
- **war-gamer + AI-Wardley** — collect → war-game → signed policy PR
  (propose-never-dispose).

The platform governs **itself** under the same risk model (Kyverno/Flux/platform
in scope) — it passes its own test. This is the **reflexive** part of the role
composition: `platform` is a **publisher** to the five other parties, and also
a **risk-bearer** in its own right, carrying a strict £10k appetite band
(`risk/appetite.json`, org `platform`, `root_of_trust: true`) rather than
standing outside the apparatus it ships.

## Releases (ticket mo-10)

A release is one or more signed, semver git tags on one commit, cut by
[`cut-release.yml`](.github/workflows/cut-release.yml) (`workflow_dispatch`).
Two dispatch forms, exactly one per run: the single-tag legacy form
(`version` + `message` inputs) still works unchanged; a `tags` input (a JSON
array of `{"tag","message"}` objects) cuts several tags off the same commit
in one dispatch — ticket cs-13, needed for a repair release that publishes
platform `1.0.0`, policy `2.0.0` and policy `3.0.0` from a single commit (an
honest MAJOR renumbering off each line's own nominal start — see cs-15's
release commit). The
existing-tag refusal runs for every tag before any tag is created, and every
tag is pushed in one atomic `git push` — either all of them land or none do.
Each tag is gitsign-signed keyless, using the workflow run's own GitHub
Actions identity — no browser login, no long-lived key. The list handling,
refusal, signing and push live in `.github/scripts/cut-release-*`, with an
offline twin at [`verify-cut-release-tags.sh`](verify-cut-release-tags.sh).
[`release.yml`](.github/workflows/release.yml) then verifies that signature
identity-pinned (the expected signer, not just "a valid signature exists")
against an offline Rekor bundle, runs
[`shift-left/verify-shift-left.sh`](shift-left/verify-shift-left.sh) as the
release gate, and publishes a GitHub Release.

Institutions pin `{tag, commit}` (`gitops/platform/platform-pin.yaml` in each
of `driftwood`/`tuppence`/`ludlow`) and bump via a Renovate PR their own repo
opens against itself — never a moving branch, never automerged.
