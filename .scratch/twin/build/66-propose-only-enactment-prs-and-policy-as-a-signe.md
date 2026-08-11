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

**Blocked by:** 65

**Status:** ready-for-agent

**Reading list:** Decision ticket 18 (enactment arm). Spec stories 80, 81, 82.

- [ ] The twin opens PRs and has no merge capability, structurally.
- [ ] **A second layer at the tool-call boundary**, so the guarantee survives the twin gaining a shell tool, an MCP GitHub server or a subagent with `gh`. Structural absence alone does not survive composition.
- [ ] The two layers are stated as layers, with the failure mode of each named: an absence has no call site to forget, and a policy check is a call site that can be forgotten.
- [ ] Policy ships as a signed, version-pinned dependency consumed by real separate repositories.
- [ ] Agent signatures on proposals assert origin only; no proposal carries implied endorsement.
- [ ] The narrowed claim is written into the artefact: this is one enactment arm among many.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
