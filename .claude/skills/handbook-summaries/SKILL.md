---
name: handbook-summaries
description: Write plain-language summaries of one adopter's composed policies, for a human to review and land by pull request. Run by a person, never by a clock and never by the compose step.
disable-model-invocation: true
---

# handbook-summaries

The original handbook generator wove agent-authored plain-language summaries into the page with
`claude -p --with-summaries`, cached by a hash of each policy's `rationale.md`. Eco-system ticket 34
moved that half here and left the other half where it belongs.

**Why the two halves are separate, and why this one cannot go back in the page.**
`composed/HANDBOOK.md` is a **compose-time render**: every sentence in it is derived from a field of
the adopter's composed artefact, so the page can be re-rendered from the artefact and compared byte
for byte (`platform/compose/verify-fresh.sh`). That comparison is the only reason to trust it. A
summary is a paraphrase — it is *not* derivable from the artefact, so a summary inside the render
would make the byte comparison fail on every run, and removing the comparison to accommodate it
would give back a page nobody can check. So a summary lands **outside `composed/`**, in its own
pull request, reviewed like any other prose.

**Why a person runs this and a clock does not.** A clock appends observations, never declarations
([ADR-0023](../../../docs/adr/0023-a-clock-appends-observations-and-one-signature-verified-by-a-controller.md)).
A summary is a declaration about what a policy means. It arrives as a reviewed pull request or it
does not arrive.

## What to do

1. **Pick the adopter and the ref.** One of `driftwood`, `tuppence`, `ludlow`. Read the artefact as
   **served**, never from a working tree:

   ```sh
   git -C .estate-clone/<adopter> show <ref>:composed/HANDBOOK.md
   git -C .estate-clone/<adopter> show <ref>:composed/evidence.json
   git -C .estate-clone/<adopter> ls-tree -r --name-only <ref> composed/policies/
   ```

   Prefer the newest signed tag; if none carries a handbook, use `origin/main` and say which you
   read in the pull request body.

2. **Read the page first.** It already states every field. Your job is not to restate it — a
   summary that repeats the table is noise, and worse, it is a second copy that can go stale.

3. **Write one short summary per policy object**, into
   `handbook/summaries/<policy-version>/<object-name>.md` in **that adopter's** repository. Never
   into `composed/` — a file there is compared byte-for-byte against a re-render and yours will
   fail it, correctly.

   Each summary answers, in plain English and in a few sentences:
   - what a person doing ordinary work would notice this rule doing to them;
   - what it will *not* do (this estate mutates and prices; it does not deny —
     [ADR-0022](../../../docs/adr/0022-the-cage-ladder-tier-per-namespace-isolated-rung-floor-and-infra.md),
     ticket 89);
   - what a person should do if it gets in their way.

4. **Say what you could not say.** If the artefact does not carry what a sentence would need, write
   that, naming the field, exactly as the render does (ADR-0020). Do not fill it in from memory,
   from another adopter, or from the platform's own documentation. An invented sentence here is
   worse than in the render, because nothing downstream compares it to anything.

5. **Head every file with its provenance**, so a reader can tell how stale it is:

   ```md
   <!-- summary of <object-name>, written from <adopter>@<ref> on <date>, by a human running the
        handbook-summaries skill. Not derived from the artefact and not graded by any check.
        The derived page is composed/HANDBOOK.md. -->
   ```

6. **Open a pull request** against that adopter, base `main`, and let a human merge it. Title it
   `Handbook summaries: <adopter> <ref>`.

## What this skill must never do

- Write into `composed/` anything at all.
- Edit `composed/HANDBOOK.md`. That file is generated; a hand edit is caught at the next gate run
  and is the exact failure `verify-fresh.sh` exists for.
- Merge its own pull request.
- Claim a summary is checked by anything. Nothing in the gate grades the *content* of these files,
  by design: there is no instrument that can, and inventing one would be inventing a number
  (ADR-0020). The only guard is the human review on the pull request.

## What is graded, and where

| thing | graded by | claim |
| --- | --- | --- |
| `composed/HANDBOOK.md` | `platform/compose/verify-fresh.sh`, hub `verify/handbook/` | it is a byte-identical re-render of the artefact served at the same ref |
| `handbook/summaries/**` | nothing | it is one person's paraphrase, reviewed on a pull request |
