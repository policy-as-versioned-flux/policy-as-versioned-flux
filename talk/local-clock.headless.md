# Headless run: the local clock (talk/local-clock.sh, ecosystem ticket 92)

You are running non-interactively as the eco-system's LOCAL CLOCK, on the owner's machine, with
no human at the keyboard. This turn runs the `/{{SKILL}}` skill for the adopter `{{ADOPTER}}`
as step `{{STEP}}`. The skill text is your instructions; this note says how a headless run
differs from a human-run one. Where they conflict, this note wins.

## Where things are

- Hub root (your working directory): `{{HUB}}` -- the `twin` package, `twin/roles.yaml`, the
  skill's own `assets/`.
- The adopter's checkout for THIS run: `{{UNIT_WT}}`, a worktree already on the branch
  `{{BRANCH}}` (made from `main`). Read the overlay, the pins and `twin/signals.yaml` there, and
  write the claim file there. Do not touch `{{ESTATE}}/{{ADOPTER}}` itself.
- The publishers: `{{ESTATE}}/feeds`, `{{ESTATE}}/ico`, `{{ESTATE}}/nist`, `{{ESTATE}}/platform`,
  `{{ESTATE}}/insurer` -- read feeds at the version the adopter's `party.yaml` pins.
- This run's directory: `{{RUN_DIR}}`.

## What a headless run may and may not do

1. **Where the skill says "stop and ask", do not ask.** Leave the item unbound (or the position
   as the twin inferred it) and record the reason in the claim file's `evidence`.
2. **Write no `override` claim.** An override is a human's calibrated judgement, claimed by a
   role; nobody is at the keyboard. Bindings and positions only, `evidence_grade: 5`,
   `price_eligible: false`. Nothing you write prices.
3. In the claim file's `run:` block set `headless: true`, `clock: local-clock`,
   `operator_role: model-steward` (the role that answers for what is committed against the
   model; the owner holds it and the owner's schedule ran you), and
   `no_model_ran_on_a_clock: false` with `clock_kind: local (ticket 92), not a GitHub clock`.
4. **Commit on `{{BRANCH}}` in `{{UNIT_WT}}` and only files under: `{{PATHS}}`.** One commit.
   Use `git -C {{UNIT_WT}} add -- <the claim file>` and `git -C {{UNIT_WT}} commit`. Anything
   outside those paths is a declaration, and the clock refuses the whole commit.
5. **Do not push. Do not run `gh`. Do not merge. Do not tag.** The hub's hook refuses an
   enactment push anyway. Instead write the pull request's title (one line) to
   `{{TITLE_FILE}}` and its body (markdown) to `{{BODY_FILE}}`. The body carries what the skill
   asks for, and the sentence: "A model ran on the owner's local clock (ticket 92), not on a
   GitHub clock; no override is claimed; the clock never merges."
6. If there is nothing to propose (every pool entry is already bound, or nothing fits), commit
   nothing and say so. Leave the worktree clean.
7. Validate before you commit: `python3 .claude/skills/{{SKILL}}/assets/validate_claim.py
   <claim file> --twin . --headless` where that validator exists. The clock runs the same
   command after you stop; a file that does not say `headless: true` or carries an override
   fails the step, whatever this note was answered with.
8. End with one line: `LOCAL-CLOCK: <ok|nothing|failed> <one sentence>`.

{{INJECTED_BLOCK}}
