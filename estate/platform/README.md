# policy-as-versioned-platform

**The shared discipline** — the governance machinery every institution inherits
as a *pinned, signed dependency* (the `config-base` pattern, one level up), so
the same apparatus is inherited rather than copy-pasted per institution.

What lives here (built across later tickets — this is the skeleton):

- **Flux distribution templates** — `ResourceSet` version fan-out, signed
  `GitRepository`, prune-on-retire, drift-heal, `dependsOn`/health, the
  notification event spine. *(ticket 03)*
- **FAIR risk engine** — `(min,mode,max)` → beta-PERT → Monte-Carlo → ALE ·
  VaR₉₅ · TVaR + risk load. *(ticket 01)*
- **ledger → PolicyException render** and the OSCAL `risk`/POA&M up-flow.
- **shift-left harness** — ±1 version-skew off the `ResourceSet` array.
- **war-gamer + AI-Wardley** — collect → war-game → signed policy PR
  (propose-never-dispose).

The platform governs **itself** under the same risk model (Kyverno/Flux/platform
in scope) — it passes its own test.
