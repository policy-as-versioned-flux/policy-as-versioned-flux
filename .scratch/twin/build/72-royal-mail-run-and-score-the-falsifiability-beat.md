# 72 — Royal Mail: run and score the falsifiability beat

**What to build:** Rewind under **as-consumed**, project, score. The beat that earns the right to make any other
claim: the viewer does not have to trust the machinery — they watch it be checked.

A demo whose thesis is *"we can prove when we're wrong"* **cannot be embarrassed by showing
failures**. The red result is a feature, which is precisely what the prior effort's thesis could not
absorb when it had to soften an overclaim.

**Blocked by:** 71, 70

**Status:** done (2026-08-15)

**Reading list:** Decision ticket 22. Spec stories 90, 93.

- [x] Rewound under as-consumed, projected, and scored against the key with the contamination discount applied.
      `twin/beat-royal-mail.sh` — one shell surface, six ordinary CLI commands, no beat-specific
      code path. `twin backtest --regime as-consumed --at 2018-06-01` pins the FY2017-18 results
      commit, so the October profit warning and the answer key itself are absent from the tree the
      forecast is computed against rather than filtered out afterwards. Carillion and Enron are run
      and scored to give the two legs, and `twin score --discount-enron --discount-obscure` carries
      the measured discount into the card, additively, beside the raw figure
      (`tests/test_royal_mail_beat.py::test_the_beat_rewinds_under_as_consumed_before_it_projects`,
      `::test_the_beat_scores_against_the_key_with_the_discount_applied`).
- [x] The score is reported as it lands, including where it is poor.
      **It lands red: brier 0.9025, worse than a coin flip.** The one world model this key carries
      is the market consensus at flotation, which put the shortfall at 0.05, and it happened. The
      score reaches the surface through `cli._say_score`, which prints **descending** on a
      `lower-is-better` rule — the poorest forecast is the first row, not the last
      (`::test_the_poor_score_is_printed_first_rather_than_buried`). Printed in `cmd_score` rather
      than in the beat, because `twin/demo.sh` already read a score card back with its own inline
      reader and a second beat doing the same would have made the beat the first place a score
      could quietly be left out. Two closures on that: every emitted forecast is either scored or
      named in `unscoreable` with a reason, so a poor forecast cannot leave by the door an
      unresolvable one uses; and the printed output names every world model the card scored, so the
      surface cannot report a subset of the artefact. Both are asserted against the *worst* score
      rather than a fixed figure, so adding an ensemble member that gets it right still passes and
      re-authoring the losing belief does not (harness guard
      `a_scored_forecast_is_never_silently_dropped`,
      `::test_no_forecast_leaves_without_being_scored_or_named_unscoreable`).
- [x] The three-regime gap is shown, localising any failure to sensing, interpretation or model.
      `twin regimes` at the same T: as-consumed and as-knowable both admit 5 facts, with-hindsight
      admits 7. The sensing gap is **empty** — this fixture commits each claim with the signal it
      binds, so everything knowable had been ingested — and the interpretation gap names the two
      post-T facts, the profit warning and the answer key. The model residual is **declined with a
      stated reason rather than reported as a zero**: nothing here infers a belief from a signal,
      so the three probabilities are identical by construction and a zero would read as "the model
      is fine" when it means "nothing consumes a signal"
      (`::test_the_three_regime_gap_localises_a_failure`).
- [x] Depth grades displayed on every capability the beat touches.
      Automatic, from the envelope: `cli._emit` already prints the computed grade of every
      capability that produced an artefact, so each of the three artefacts the beat **presents** —
      the bundle, the card, the regime gap — announces `domain-model` 1/7, `provenance` 2/4,
      `scenario-engine` 4/7 and `sense-move` 6/8 without the script labelling anything. The test
      compares each printed grade against what `Capabilities.load()` computes from the decision
      tickets, so a grade written into an envelope by hand fails rather than merely type-checking
      (`::test_every_artefact_the_beat_emits_carries_computed_depth_grades`). **Scope stated
      plainly:** the two discount legs' `run`/`score` go to `/dev/null` as setup and their grades
      are not on screen, and `fixture`, `verify` and `grade` emit no artefact and so carry no depth
      block. The claim is over what the beat shows, not over every process it starts. The gap this
      found is the beat's *own* capability — see the last criterion.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One new harness guard, `a_scored_forecast_is_never_silently_dropped`, black-box on all three
      legs (bundle-to-card, card-to-stdout, and the red result itself). Zero invariants or guards
      weakened; no `checks_module_sha256`/`body_sha256` in `twin/invariants/manifest.yaml` moved,
      since the sixteen constitutional invariants (`twin/invariants/checks.py`) are untouched.
      `twin/invariants/golden-digests.json` **was** re-blessed, gated and cited — every artefact's
      `capabilities_digest` pin moves the moment a capability file is added, and nothing about a
      scoring rule, a serialisation or an engine output changed with it.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      **Decision ticket 22 had no capability file at all**, so the demo — the one thing a viewer
      actually looks at — was the single capability on screen carrying no grade. That is the
      skeleton-as-ceiling failure the constitution names, in the worst possible place, and it is
      the fourth time this gap has been found and filled rather than left empty (build ticket 47
      for decision ticket 15, 63 for 10, 66 for 18). `twin/capabilities/demo-slice.yaml` now
      computes it, and the beat prints it as its closing step. **It opens at `stub`, 0 of 4, and
      that is the honest reading, not a placeholder**: this ticket runs the first of four beats, AC
      2 needs all three subjects (build tickets 73-76) and ACs 1, 3 and 4 are build ticket 77's own
      work. The denominator grew by four and the numerator did not move
      (`::test_the_demo_slice_grade_is_computed_from_decision_ticket_22`).

## Five gaps this ticket found and closed on the way

**`twin/demo.sh` could not have been passing in CI.** Line 16 used `mktemp -d -t twin-demo`. BSD
mktemp appends the random suffix for you; **GNU coreutils refuses with "too few X's in template"**,
so under `set -euo pipefail` the script aborted on its own first line — on Linux, which is where
`.github/workflows/twin.yml` runs it. Verified against real GNU coreutils 9.11, not reasoned about:
`PATH=…/gnubin bash twin/demo.sh` failed immediately and now passes. The beat script had inherited
the same line verbatim, so this ticket would have added a second CI step that could never go green
while claiming CI ran it end to end. Both now use an explicit `XXXXXXXX` template.

**`twin grade --capability <unknown>` printed nothing and exited 0.** The filter simply matched no
row. The beat's closing step asks for one capability's grade and then states a conclusion about it,
so deleting or renaming `demo-slice.yaml` would have left the beat printing that conclusion with
nothing behind it. `cmd_grade` now calls `caps.require()`, which refuses and names what exists.

**The beat's reproduce-refusal test accepted any non-zero exit.** `twin verify` exits 2 both for
the honest "a discount cannot be replayed from pins alone" refusal and for a missing file, so a
typo'd path would have "passed" it. It now greps the refusal's own message.

**The standing library did not sweep Royal Mail.** Build ticket 71 authored the answer key and did
not add it to `fixtures.build_standing_library`, so the library swept five answer keys and not the
sixth — the fixture existed, the sweep could not see it. The cause is that the sweep list was a
hand-maintained second copy of a set that also lives in the CLI. There is now one list,
`fixtures.BUILDERS`, which `build_standing_library` iterates and `twin fixture --org` reads for its
own `choices`; the two cannot drift because there is no longer a second one, and
`tests/test_scenario_library.py` asserts the repo count against `len(fixtures.BUILDERS)` rather
than against a number somebody remembers to increment.

**The answer keys were unreachable from the CLI.** A shell surface could build only the default
fixture and the pocket org, so any beat over a real key would have had to import `twin.fixtures`
from a heredoc. `twin fixture --org <name>` now builds any of them by name.

## What review changed, and what it did not

Two review passes ran against the first draft. Both found the same thing in different words: the
first draft's guard **could not fail**. Its "every score reaches the screen" leg matched the world
model's *name* in stdout, so a surface printing names and dropping every figure passed it; and its
"worst is printed first" leg ran on a card with one score, where any ordering is first. Both were
proved by probe, not argued. The guard now checks the figure itself, and runs the ordering leg on a
three-model card where the two orders differ — re-probed, and a names-only surface and a best-first
sort each fail it now.

Review also removed two tests that could not fail (a partition check on a one-forecast card; a
substring match of verb names against `--help` text, which passed with `twin run` deleted) and one
that restated `verbs.py`'s own arithmetic. `--pocket-org` went with them: it was a second spelling
of `--name pocket` that silently won when both were given. Net, the change set lost more test lines
than it gained.

What review did **not** change is the red result. Nothing here was tuned to make the beat look
better, and the guard's threshold is deliberately on the *worst* score, so it stays true when an
ensemble member eventually gets it right.

## What this beat does not show

The key carries **one** world model, so the execution emits one forecast and there is no ensemble
spread to present — decision ticket 22's plurality refusal is satisfied trivially here rather than
demonstrated. The same single belief is why the three regimes produce identical probabilities and
the model residual declines to compute. Neither is hidden: the regime artefact states the reason in
its own body, and this beat's job is falsifiability, which a single scored belief carries. The
ensemble is build ticket 74's beat, on Netflix.
