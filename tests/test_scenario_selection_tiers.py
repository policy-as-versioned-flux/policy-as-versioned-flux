"""AC 6 (decision ticket 13): the four-tier scenario-selection rule — standing library,
precondition-triggered, event-triggered, ad-hoc, "nothing else is speculatively generated" — is
the complete, non-overlapping set. Checked against the source directly, the same discipline
`twin/invariants/harness.py`'s own `backtest_is_a_pure_composition` uses for a structural claim
about a CLI command (`inspect.getsource`, not the docstring), rather than only asserted in prose.

There are exactly two primitives a scenario or an opportunity can come out of:
`verbs.run()` (executes a scenario, emits forecasts) and `gameplay_lens.propose()`/`.sweep()`
(surfaces a precondition-matched opportunity — a different primitive entirely, never a scenario
execution under another name). Every call site of either, across `twin/*.py`, is one of:

- **Tier 1, standing library** — `schedule.sweep()`, which calls `verbs.run()` in a loop over
  every scenario in every overlay, unconditionally, no scenario named by a human.
- **Tier 2, precondition-triggered** — `gameplay_lens.sweep()`, which calls `propose()` over
  every org's map, unconditionally, no component named by a human.
- **Tiers 3 and 4, event-triggered and ad-hoc** — `cli.cmd_run` and `cli.cmd_backtest`, both a
  human or automation naming one scenario directly. Decision ticket 13 does not distinguish these
  two at the code level: an event-triggered re-run and an ad-hoc human-posed run are the identical
  call, differing only in *why* it was invoked, which the resolved decision states rather than
  this ticket inventing a second command to encode.
- `reproduce.replay` also calls `verbs.run()`, but originates nothing: it replays a command
  already recorded by one of the four tiers above, read out of an already-emitted artefact's own
  pins, never named fresh by this function (`tests/test_reproduce.py` exercises `replay` itself).

Scoped to `twin/*.py` — the product surface — not `twin/invariants/*.py`, whose own guards call
`verbs.run()` internally to check unrelated properties (determinism, regime gating) of a scenario
they construct for that purpose; that is the test harness exercising a primitive, not a fifth way
a scenario gets selected to run in the product. Stated here rather than left as a silent narrowing.
"""

from __future__ import annotations

import inspect
from pathlib import Path

from twin import cli, gameplay_lens, reproduce, schedule, verbs

_TWIN_DIR = Path(verbs.__file__).resolve().parent

# Every top-level module allowed to call `verbs.run(` — tier 1 (`schedule.py`), tiers 3+4
# (`cli.py`), and `reproduce.py`'s mechanical replay. `verbs.py` itself is the definition.
_RUN_CALLERS = {"cli.py", "schedule.py", "reproduce.py"}

# Every top-level module allowed to call `gameplay_lens.propose(` or `gameplay_lens.sweep(` —
# tier 2's own sweep, and `cli.py`'s `twin gameplay-sweep`. `gameplay_lens.py` itself is the
# definition. (`ethics_gate.py` names `gameplay_lens.propose()` once in a docstring, checked and
# excluded explicitly below, not silently — it carries no import of the module and cannot call it.)
_PROPOSE_CALLERS = {"cli.py"}


def _modules_naming(needle: str) -> set[str]:
    return {
        path.name
        for path in sorted(_TWIN_DIR.glob("*.py"))
        if path.name != "__init__.py" and needle in path.read_text(encoding="utf-8")
    }


def test_verbs_run_is_called_only_from_the_named_tiers() -> None:
    """A fifth caller here would be a fifth, unaccounted-for way to select a scenario to run."""
    assert _modules_naming("verbs.run(") == _RUN_CALLERS


def test_gameplay_lens_is_called_only_from_the_named_tier() -> None:
    hits = _modules_naming("gameplay_lens.propose(") | _modules_naming("gameplay_lens.sweep(")
    # `twin/ethics_gate.py` names `gameplay_lens.propose()` once, in a docstring describing what
    # its own claim shape states — prose, not a call — checked here rather than silently excluded:
    # its own source carries no `gameplay_lens.` import at all, so it cannot call it.
    assert "import gameplay_lens" not in (_TWIN_DIR / "ethics_gate.py").read_text(encoding="utf-8")
    assert hits == _PROPOSE_CALLERS | {"ethics_gate.py"}


def test_no_gameplay_opportunity_is_a_scenario_execution_under_another_name() -> None:
    """Tier 2 never calls tier 1/3/4's own primitive — an opportunity is surfaced, not run."""
    source = inspect.getsource(gameplay_lens.sweep)
    assert "propose(" in source
    assert "verbs.run(" not in source


def test_the_standing_library_names_no_scenario_at_the_call_site() -> None:
    """Tier 1: `schedule.sweep()` iterates every scenario in every overlay unconditionally."""
    source = inspect.getsource(schedule.sweep)
    assert "verbs.run(" in source
    assert "for scenario_id in sorted(overlay.scenarios)" in source


def test_the_precondition_sweep_names_no_component_at_the_call_site() -> None:
    """Tier 2: `gameplay_lens.sweep()` scans every org's map unconditionally."""
    source = inspect.getsource(gameplay_lens.sweep)
    assert "for org in orgs(repo)" in source


def test_run_and_backtest_are_the_only_human_or_automation_named_entry_points() -> None:
    """Tiers 3 and 4 share this one call, on purpose (see module docstring)."""
    assert "verbs.run(" in inspect.getsource(cli.cmd_run)
    assert "verbs.run(" in inspect.getsource(cli.cmd_backtest)


def test_reproduce_replay_reads_the_scenario_from_the_recorded_command_not_a_fresh_argument() -> None:
    """`reproduce.replay` is `verbs.run(`'s fourth caller, but it originates nothing: `verb` and
    every flag it passes on are read out of `envelope["produced_by"]["command"]`, an already-
    emitted artefact's own pin — never a parameter this function itself exposes to a caller."""
    assert "run" in reproduce.VERBS and "backtest" in reproduce.VERBS
    source = inspect.getsource(reproduce.replay)
    assert "verbs.run(" in source
    assert '_need(flags, "scenario"' in source
    assert "def replay(worktree" in source and "doc: dict[str, Any]" in source, (
        "replay's own signature takes no scenario parameter — confirms nothing is named fresh here"
    )
