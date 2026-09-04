# 66 — Propose-only enactment: PRs and policy as a signed pinned dependency

**What to build:** The twin **proposes only** — it opens pull requests against the enactment repositories and never
merges. It changes its own model constantly and the world never without a human.

That is derived rather than asserted: from Article 22, from the fact that a trade-off curve has
nothing to auto-execute, and from agent signatures asserting origin rather than endorsement.

Policy ships as a **signed, pinned dependency** — the enactment channel for machine-enforceable
controls and the substrate proving a control is in force. Held in its **narrowed** form: policy-as-
code is *an* arm, not *the* definition of governance, because the £ engine's whole value depends on
most levers not being code.

**Amended 2026-08-10: propose-only needs two layers, not one.** The original criterion made it a
structural absence — no merge code path exists. That is weaker than it reads, and the twin's own
code already says so. `twin/options.py` carries the comment *"a lock, not a proof. Python has no
private constructor"*.

The deeper objection is the one that matters. "No merge code path" is a property of `twin/` **as it
is today**. The twin is an agent. The day it gains a shell tool, an MCP GitHub server or a subagent
with `gh`, the guarantee disappears **with no diff to `twin/` at all** — and the constitution says
code is disposable by default, so the guarantee has a scheduled expiry. A constraint at the
tool-call boundary holds under composition. An absence does not.

The counterweight stands and is why this is layered rather than replaced: a policy check is a call
site, and a forgotten call site fails open. An absence has no call site to forget. Keep both.

**Do not adopt AWS Dogwood for this.** The evaluated verdict is in the ticket-27 note. Use plain
Cedar if a policy layer is wanted, and treat action-boundary monitoring as the *class* it is.

**Blocked by:** none — was 65, relaxed 2026-09-03 (eco-system ticket 17). The constitution
named this cut on 2026-08-05 and it was never taken; instead 65 closed *unmeasured* from
2026-08-16, so the block was gating the enactment arm on a question with no answer. The
policy-pinning half (criterion 4) takes *unmeasured* as its input rather than waiting on a verdict.

**Status:** refusal built, **PR CHANNEL IS THE ESTATE'S, NOT `twin/`'S** — 2026-09-03. Read
`PR CHANNEL NOT WIRED` from 2026-08-15, and criterion 1's first half is still not built here:
nothing in `twin/` opens a pull request, and `twin propose` still emits an artefact and stops.
What changed is where the channel lives. The eco-system's proposer is each adopter's
`propose-tier.yml` workflow (NORTH-STAR §4 step 3): it re-composes on the adopter's clock through
the pinned platform and opens a pull request only when a residual crosses a band. It fired on
schedule for the first time on 2026-09-01 12:01Z on driftwood and returned `[]`, so **no proposal
PR has yet opened** (eco-system tickets 60 and 74; 78 adds the tighten-only clamp it lacks). The
2026-08-31 thin-slice pull requests are sometimes cited as this channel working; they are not.
The assistant opened them with `gh pr create` under the owner's account at 2026-08-31T08:54Z
(platform #5, driftwood #12, tuppence #9, ludlow #8); the assistant's `gh pr merge` was declined
by Claude Code's permission classifier rather than by `enact_guard.py`; and the owner merged
every one of them by hand the same day, platform #3, #4 and #5 at 13:52Z and the three adopters'
at 16:23Z (`gh pr list --state all --json mergedAt,mergedBy` on each repo, read 2026-09-04: all
`mergedBy: chrisns`). The same day also found the guard's bare-remote hole (a push to an
enactment repo admitted as a self-push; fixed with four tests, hub `d81f202`). So those PRs
evidence that the assistant did not merge and a human did, which is criterion 1's second half
holding; they evidence neither its first half, nor either layer here, nor `twin propose`. Since eco-system ticket 88 (2026-09-03) the guard's checked-in mode
is `other-hand`: a merge is admitted only as the app `pavc-other-hand`, never as the owner's
token; `twin/` itself still has no merge surface. Criterion 1 stays half, and its other half is
owned by eco-system ticket 74 (the first real proposal PR, merged by a human), not by this file.

*As written on 2026-08-15:* the same honest split build tickets 64 and 78 carry. Criterion 1 is
conjunctive and only its second half exists: nothing in `twin/` opens a pull request, so the
ticket does not close on a criterion it has half-built. The precedent is build ticket 54, which
built the retention half of a conjunctive criterion on purpose and left the tick to 55 once the
promotion half genuinely existed beside it.

**Reading list:** Decision ticket 18 (enactment arm). Spec stories 80, 81, 82.

- [ ] The twin opens PRs and has no merge capability, structurally. **Half.** No merge capability is
      built and asserted at two layers. Opening a pull request is not: `twin propose` emits an
      `enactment-proposal` artefact and nothing in `twin/` has touched a live repository. Wiring
      the channel needs a reachable remote and an authorised push, which is an outward-facing act
      this ticket did not take.
- [x] **A second layer at the tool-call boundary**, so the guarantee survives the twin gaining a shell tool, an MCP GitHub server or a subagent with `gh`. Structural absence alone does not survive composition.
- [x] The two layers are stated as layers, with the failure mode of each named: an absence has no call site to forget, and a policy check is a call site that can be forgotten.
- [ ] Policy ships as a signed, version-pinned dependency consumed by real separate repositories.
      **Read and reported, with two words qualified.** Six cross-repository pins across three
      consumers are real and version-pinned. **Signed** is the sources' own declaration and is
      verified by nothing here — no tag checked, no Rekor entry looked up, and
      `estate/verify/provenance/verify-provenance.sh` records that this repository's own commits are
      not keyless-signed either. **Separate** is true by URL and not yet by existence:
      `estate/README.md` describes a monorepo-style working tree whose directories become their own
      repositories *at split*. Both are stated as limits inside the artefact rather than asserted.
- [x] Agent signatures on proposals assert origin only; no proposal carries implied endorsement.
- [x] The narrowed claim is written into the artefact: this is one enactment arm among many.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.

## What was built

`twin/enact.py` is layer 1 and `twin propose` is its only verb: it emits an `enactment-proposal`
artefact and there is no sibling command, and no flag on this one, that disposes. The harness guard
`enactment_is_propose_only_at_both_layers` asserts the module's public surface as an **allow-list**
(`propose`, `dependency_pins`) rather than screening for merge-shaped names, on the reasoning
`prefilter_precedes_pricing` already uses: a keyword match would miss one named `land`.

`twin/enact_guard.py` is layer 2 — a `PreToolUse` hook, stdlib only, importing nothing from `twin/`
because it runs outside the package it guards. It refuses `gh pr merge`, the REST shape of the same
act, and a direct push to an enactment repository (resolving a bare remote rather than only reading
the command line), plus any tool whose name says `merge` — which is how an MCP GitHub server names
it. It fired on this ticket's own implementation session, refusing a `Bash` call that carried the
merge string in a test fixture, which is the first evidence it does anything.

The two layers are stated as layers in the emitted artefact and in `twin/README.md`, each with the
failure mode of the other's construction: layer 1 fails under composition and cannot be forgotten;
layer 2 fails by a forgotten call site and cannot be composed around. The guard closes layer 2's own
failure mode by reading its registration back out of `.claude/settings.json`.

**Endorsement is refused structurally rather than by a field.** The proposal is a *derived*
artefact, so `derived_never_human_signed` already refuses a human signature on it: there is no slot
an endorsement could be written into, and a hand-touched proposal is a detectable anomaly. No new
invariant was needed and none was weakened.

`dependency_pins()` reads the real pins out of the estate's committed Flux sources — six
cross-repository, across three separate consumer repositories (driftwood, ludlow and tuppence, each
pinning `platform` and `nist` by signed tag), plus three self-syncs counted separately because a
repository syncing itself consumes nobody's policy. It reports the limit with them: **every commit
line in the estate is a commented-out placeholder**, so each is a tag pin, and a tag can be moved.

`twin/capabilities/enactment.yaml` is decision ticket 18's first capability file. Two of five tick;
ACs 2 and 5 are build ticket 68, AC 4 is build ticket 67.

## What this does not do

Two of these are why the ticket does not close.

- **No pull request is opened against a live repository.** The proposal is the artefact; the channel
  that would carry it to GitHub is the estate's existing `propose-policy-pr.sh`. This is criterion
  1's unbuilt half.
- **Nothing verifies the signature or the force.** The pins evidence what the repositories *declare*
  they consume. No tag is verified, no Rekor entry is looked up, and no cluster is asked whether a
  control is running. Whether continuous proof of force is even required is build ticket 65's
  question and is still open. This is criterion 4's qualification.
- **The tool-name leg of layer 2 is a keyword screen**, which is the technique layer 1 refuses on
  principle. The difference is that layer 1 can enumerate its own public surface and this cannot:
  the MCP tool namespace is unbounded and mostly not ours. `squash_pull_request` is caught because
  `squash` is listed; a server that calls it `apply_changes` is caught by nothing here. The command
  patterns have the same ceiling — a differently-named wrapper, or a hand-rolled `curl` against the
  REST API, is not matched. The upgrade named in the module removes the guessing entirely: a GitHub
  App token with `pull_requests: write` and no `contents: write`, which makes the refusal the
  server's rather than ours.
- **A subagent is not asserted anywhere.** Whether a runtime routes a subagent's tool calls through
  its hooks is the runtime's property, so neither the suite nor the tests claim it. What is
  asserted is that `decide` refuses whatever it is handed, and that the registration routes *every*
  tool name to it rather than a merge-shaped subset — the matcher gap that a first draft of this
  ticket left open and both review axes found independently.

## What remains before this closes

1. Wire the PR channel: `twin propose` opens a real pull request against an enactment repository,
   and demonstrably does not merge it.
2. Verify rather than repeat the signature: check a consumed tag, or record honestly that the
   estate's tags are unsigned today.
