# 77 — Honesty made structural: depth grades, the does-not-do register, thesis sequencing

**What to build:** The three devices that make the honest boundary **structural rather than remembered**.

**Depth grades travel with capabilities, not slides**, so any surface touching a partial capability
displays that it is partial automatically. The prior effort's failure was exactly this: a "Live"
label on a beat that was not live, caught late in adversarial review — because narrated honesty
relies on someone remembering.

The **does-not-do register** is the published-scope-exclusions device turned on the demo itself. Same
primitive, second use; the symmetry is evidence it is the right one.

And the **thesis is sequenced**: anticipation and provable falsifiability first, then proportionate
versioned governance, **concluding** in the one-currency comparison — the most seductive and least
self-evident claim, earned rather than opened with. Lead with the £ and the sharpest person in the
room rightly asks where the number came from. **The order is the argument: earn credibility, then
spend it.**

**Blocked by:** 72, 74, 75, 76

**Status:** done (2026-08-17)

**Reading list:** Decision tickets 20, 22. Spec stories 86, 89, 93.

- [x] Depth grades render automatically on every surface touching a capability; no manual labelling anywhere.
      Already structural, not new work here: `every_capability_depth_graded` has been a live
      constitutional invariant since the walking skeleton (build ticket 07), and `depth_block()`
      (`twin/grades.py`) is called from 12 other modules — 19 of those calls inside
      `twin/verbs.py` alone, one per CLI verb it implements — including every beat script's own
      `twin grade --capability X` step, so a partial capability cannot appear anywhere without its
      computed grade travelling beside it. Audited rather than rebuilt: `grep -rn '\bLive\b'
      twin/*.sh twin/*.md` finds no hand-typed status label anywhere in the beat scripts or
      README, which is the specific failure this criterion names (a "Live" label on a beat that
      was not live).
- [x] The does-not-do register is published and complete, generated from the depth-grade checklists rather than written by hand.
      `twin/does_not_do.py`, decision ticket 15's published-scope-exclusions device turned on the
      demo itself: `register()` is a pure function of `grades.Capabilities`, with no backing YAML
      file and no field an entry could be typed into. `twin does-not-do` publishes it as a
      `derived` artefact. Completeness: `tests/test_does_not_do.py::test_register_is_complete_against_the_shipped_capabilities`
      asserts the register's length equals the capability aggregate's unchecked total exactly (no
      cap, no sample). Generated-not-authored is enforced live by harness guard
      `does_not_do_register_is_generated_never_typed`: checking one criterion off in a checklist
      removes exactly its entry from the register, proving a live read rather than a cache.
- [x] The demo sequence is (b) falsifiability → (c) versioned governance → (a) one-currency comparison, and the £ appears nowhere before the third beat.
      Found not true on inspection: CI ran the three beats as three separate steps in the order
      royal-mail, **netflix**, intel (`.github/workflows/twin.yml`), pricing the second beat before
      the third ran — and inside `beat-netflix.sh` itself, `price`/`trade-off` (the comparison,
      (a)) ran at steps 4–5, before `propose` (governance, (c)) at step 6, contradicting the
      script's own header comment that the comparison was "sequenced to end on." Both fixed: a new
      orchestrator, `twin/beat-sequence.sh`, is now the one place the sequence runs — royal-mail,
      intel, netflix, in that order — and CI's three steps collapsed into one call to it.
      `beat-netflix.sh` reordered so `propose` precedes `price`/`trade-off`, with `substrate` (a
      method footnote, not a thesis claim) moved ahead of both. Checked structurally, not just run:
      harness guard `the_demo_sequence_earns_credibility_before_it_spends_it` reads the beat
      scripts' own source — the sequence names the beats in the declared order, neither
      `beat-royal-mail.sh` nor `beat-intel.sh` calls a pricing verb, and `beat-netflix.sh` calls
      `propose` before `price` — and `tests/test_beat_sequence.py` asserts the same three facts at
      the pytest level.
- [x] A deliberately red result is shown rather than hidden — incompleteness is on-message for this thesis.
      Pre-existing, from build ticket 72: `beat-royal-mail.sh` step 3 prints the worst score first
      ("worse than a coin flip") rather than burying it, and its own header comment states "THE
      RESULT IS RED AND THAT IS THE POINT." `beat-sequence.sh` streams that beat's output verbatim
      as the first of the three it runs, so the red result opens the sequence rather than being
      summarised away.
- [x] Every claim in the demo traces to a capability at a stated depth.
      Pre-existing, from the walking skeleton onward: every artefact-producing `twin` command
      writes a `depth` block naming the capabilities behind it (`grades.Capabilities.depth_block`),
      and each beat script's closing step prints the computed grade of every capability it touched,
      unchecked criteria and all — demonstrated live in this ticket's own evidence run below.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      Two harness guards added, `does_not_do_register_is_generated_never_typed` and
      `the_demo_sequence_earns_credibility_before_it_spends_it` (`twin/invariants/harness.py`) —
      the same class of addition build ticket 34's precedent allows and build tickets 56/78 already
      used for their own harness guards. Both cite decision ticket 22 (and the first, decision
      ticket 15) in their own docstrings. No constitutional invariant, no
      `twin/invariants/manifest.yaml` entry and no `checks_module_sha256` changed — harness guards
      sit outside that hash lock. `./bin/twin verify` run clean against both (see Evidence).
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      This ticket has no single owning decision ticket — its reading list cites two (20 and 22) —
      the same position build tickets 34, 56 and 78 found for a ticket of this shape, so
      `twin/grades.py`'s machinery (which grades a capability against one decision ticket) does not
      apply. This checklist itself, computed against the seven items above, is the evidence: seven
      checked, zero unchecked, each citing the file, test or guard that makes it true.

## Also found and fixed: two-axis review of the diff

Same discipline build tickets 56 and 78 name for themselves: findings recorded and fixed, not
glossed over.

- **Spec axis, real gap.** CI's own step order (`.github/workflows/twin.yml`) ran royal-mail,
  netflix, intel — pricing the second beat before the declared third one ran, which is exactly the
  drift this ticket exists to make structural. Fixed: the three steps collapsed into one call to
  the new `twin/beat-sequence.sh`, so CI now runs the same declared order the harness guard checks
  rather than a hand-maintained ordering that could drift from it a second time.
- **Spec axis, real gap.** `beat-netflix.sh`'s own header comment already claimed the cross-domain
  comparison was "sequenced to end on," but the script itself priced at steps 4–5 and proposed
  enactment afterward at step 6 — the comment was aspirational, not true. Fixed by reordering
  (substrate, then propose, then price/trade-off) rather than by rewriting the comment to match
  the wrong behaviour.
- **Standards axis, judgement call, not fixed** — noted, left as found: `does_not_do.py`'s
  `register()` and `grades.py`'s `depth_block()` both walk a `Capabilities` object into a flat
  list, and a shared "survey every capability" helper was considered. Two call sites with
  different output shapes (register entries vs. a keyed summary block) is not yet the abstraction
  earning its cost.
- **Spec axis, real gap, found by a six-way review of this diff.** Two independent reviewers
  (code quality, testing) flagged `tests/test_beat_sequence.py` as a verbatim second
  implementation of `the_demo_sequence_earns_credibility_before_it_spends_it`'s three checks —
  exactly the "third copy" `beat-royal-mail.sh` already declines to write for a different guard.
  Fixed: the pytest file now runs that one guard through `invariants.run(only=[...])`, the pattern
  `tests/test_invariant_suite.py`'s own `_one()` helper already established, instead of
  re-implementing it. The testing reviewer separately found the guard's own trade-off-position leg
  was missing — `price` was checked against `propose` but `trade-off` was not, so a regression
  that reordered only `trade-off` ahead of `propose` would have passed undetected. Fixed in the one
  place the check now lives.
- **Spec axis, real gap, found by the code-quality reviewer.** The
  `does_not_do_register_is_generated_never_typed` guard built its patched `Capabilities` with the
  *original*, now-stale digest (`Capabilities(patched, caps.digest)`), violating
  `Capabilities.digest`'s own contract (`digest_of` the summaries it actually holds). Harmless
  today — nothing in the guard reads `.digest` — but a landmine for the next guard that reuses this
  patch-and-compare shape and does trust it. Fixed: the digest is recomputed from the patched dict
  the same way `Capabilities.load()` computes its own.
- **Spec axis, real gap, found by the performance reviewer.** `cmd_does_not_do` computed
  `does_not_do.published()` once for the console summary and `does_not_do.artefact()` recomputed
  it a second time internally. Fixed: `artefact()` now accepts the already-computed `body`.
- **Spec axis, real gap, found by the documentation reviewer.** This section and the checklist
  above both had inaccuracies once checked against a live run: the "19 modules" claim in AC 1
  actually meant 19 call sites inside `twin/verbs.py` alone (12 other modules call
  `depth_block()`, not 19); `twin/README.md`'s "Twelve checks" paragraph already enumerated 14
  names before this ticket touched it, and bumping the header by this ticket's own +2 landed on
  "Fourteen" instead of the true "Sixteen"; the README's "Run it" quick reference never gained the
  line for this ticket's own `beat-sequence.sh` (nor, pre-existing and fixed in passing,
  `beat-intel.sh`); and this file's own Evidence section (below) reported a pytest count taken
  before the `test_beat_sequence.py` consolidation above changed it. All fixed against a live
  recount, not carried forward — the discipline build ticket 56 named for the capability table and
  build ticket 78 repeated for its own harness-guard list.

## What is honestly true now, and what still isn't

Depth grades, the demo sequence and the does-not-do register are all structural now — computed
and checked, not narrated — for the parts of the honest boundary this ticket owns. What still
isn't true: `demo-slice` itself is still graded `stub` (0/4), because decision ticket 22's own
acceptance criteria ask for a rendered, presentable demo artefact this ticket does not build —
this ticket makes the *honesty* of that demo structural, not the demo's own completeness. The
does-not-do register says so about itself: `demo-slice-1` through `demo-slice-4` are four of its
34 entries.

## Evidence

Re-derived after the six-way review above fixed six real findings, two of them in this section's
own numbers — the same discipline the review section names, applied to itself rather than exempted.

```
.venv/bin/python -m pytest tests/test_does_not_do.py tests/test_beat_sequence.py \
  tests/test_netflix_beat.py tests/test_royal_mail_beat.py tests/test_intel_beat.py -q
  41 passed

.venv/bin/mypy twin tests conftest.py --ignore-missing-imports --warn-unused-ignores
  Success: no issues found in 148 source files

.venv/bin/python -m pytest -q
  1443 passed, 1 failed in 296.56s (0:04:56)
  FAILED test_the_suite_is_green — known, pre-existing, unrelated: build ticket 64's probe has
  gone stale (drift_window_is_actually_being_sampled) and build ticket 70's coverage-floor finding
  (flux_coverage_floor_is_still_reachable) — neither new guard from this ticket is in the failure
  list and both passed clean.

.venv/bin/python -m twin verify
  RESULT: 68 passed, 2 failed, 2 skipped (0 pending invariants, 2 skipped and not faked)
  Same two known failures as above. does_not_do_register_is_generated_never_typed and
  the_demo_sequence_earns_credibility_before_it_spends_it both PASS — this ticket's own two
  harness guards going live, not a change elsewhere in the suite.

bash twin/beat-sequence.sh
  PASS: the demo sequence ran b -> b -> c -> a. Royal Mail and Intel both proved the twin can
  be checked, and neither one priced anything. Netflix proposed enactment before it priced a
  response, so the one-currency comparison concluded the sequence rather than opening it.
```
