"""`honest-build` (build ticket 90, decision ticket 20): the skill definition and the capability
inventory, as data instead of prose.

Decision ticket 20 resolved four questions in prose on 2026-08-05, but `twin/capabilities/
honest-build.yaml` only ever ticked AC 3 (the build order — `twin/demo.sh`'s walking skeleton).
The other three ACs existed only as the decision ticket's own narrative, which is exactly the
distinction this project's own culture (build ticket 03) refuses everywhere else: the checklist
tracks the *code* that realises a decision, never the decision's existence in prose. This module
is that code for AC 1, AC 2 and AC 4.

**AC 1** — the determinism-split test — is queryable in `twin/skills.py` (`classify_by_determinism`,
`SKILL_DEFINITION`), not here: it is a general-purpose predicate skills.py's own harness can use,
and this module asserts against it rather than re-defining it a second time.

**AC 2** — `CAPABILITY_INVENTORY` below, one entry per capability decision ticket 20 Q3 named,
classified `code` / `skill` / `inherited` and checked against real files by `validate_inventory()`.

**AC 4** — `SKILL_OWNING_TICKET` below, one entry per capability classified `skill`, checked
against `.scratch/twin/issues/` by `validate_owning_tickets()` the same way
`twin.grades.acceptance_criteria()` checks a ticket exists before trusting its text.

**The ethics-gate finding, resolved rather than papered over (build ticket 90's own instruction).**
Decision ticket 20 Q3 named `ethics-gate` as the sixth of six skills, and the seam-3 eval harness
(`twin/skill-thresholds.yaml`, `twin/skills.py`, build ticket 47) still scores it as one — that
existing machinery is untouched by this ticket, on purpose: rewriting the "sixth and last of the
six skills" prose that runs through `twin/ethics_gate.py`, five other skill modules' docstrings,
`tests/test_record_skill_scores.py`'s `_EXPECTED_SKILLS`, and `.scratch/twin/map.md` would be a
large, unrequested rewrite chasing a label, not a correction of behaviour. What this module does
instead is classify the capability honestly in the one place a wrong-but-consistent count would
otherwise have been forced: **`ethics-gate` is `code` here**, not `skill`.

The reasoning: `ethics_gate.scorer()` — what `skill-thresholds.yaml`'s `ethics-gate` entry actually
scores — compares only `admitted` and `ladder.stopped_at`, i.e. `admit()`'s ladder-walk plus DPIA
triage. Given a payload of already-quantified facts (booleans, floats, an enum), that computation
has exactly one correct answer and nothing left to interpret — the definition of "reproducible
from pins." Contrast the other five: each documents its own "swap the body for a model call"
upgrade path, because each stands in for a genuinely ambiguous reading of unstructured evidence
(binding a signal to a component, inferring an evolution position from accumulated text, ...).
`ethics_gate.py`'s admission machinery documents no such path, because there is no model call that
would change a correctly-implemented ladder's answer. The one piece of the module that *is*
irreducibly interpretive — `classify_gameability()`'s reading of free-text `metric_description` —
is not part of what the eval harness scores at all, so it does not rescue the module's
classification; `CAPABILITY_INVENTORY`'s note on the `ethics-gate` entry names this in full.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import PACKAGE_DIR
from .grades import DECISION_TICKETS_DIR
from .skills import CODE_KIND, SKILL_KIND, classify_by_determinism, load_thresholds

# Provenance, not determinism (decision ticket 20 Q1: "we inherit code") — arckit-ported code is
# still `code` by the determinism test, so `classify_by_determinism()` never returns this; it is
# `CAPABILITY_INVENTORY`'s own third bucket for "which are inherited from arckit" (AC 2's own
# wording), tracked here rather than in `twin/skills.py` because inheritance is this ticket's
# question, not the eval harness's.
INHERITED_KIND = "inherited"

_VALID_KINDS = (CODE_KIND, SKILL_KIND, INHERITED_KIND)


class HonestBuildError(RuntimeError):
    """An inventory entry with an unknown kind, a module that is not a real non-empty file, a
    skill with no threshold, or a `SKILL_OWNING_TICKET` entry that names no real ticket."""


@dataclass(frozen=True)
class CapabilityEntry:
    name: str
    kind: str  # one of _VALID_KINDS
    module: str  # path relative to twin/, e.g. "wardley.py" — must be a real, non-empty file
    reproducible_from_pins: bool  # the determinism-split test's own input for this capability
    note: str


# -- AC 2: the inventory ---------------------------------------------------------------------
#
# Every capability decision ticket 20 Q3 named, mapped to the module that actually realises it
# in this repository as it stands after build tickets 79-89 (build ticket 90's own instruction:
# run last in the batch so this reflects the system's real, final state).

CAPABILITY_INVENTORY: tuple[CapabilityEntry, ...] = (
    # -- code: on the derivation path, reproducible from pins (decision ticket 20 Q1/Q3) --------
    CapabilityEntry(
        "graph-schema-validation", CODE_KIND, "schema.py", True,
        "Graph schema + validation; authored/derived enforcement (decision tickets 07, 14).",
    ),
    CapabilityEntry(
        "causal-propagation", CODE_KIND, "propagate.py", True,
        "Monte-Carlo propagation through the causal layer, depth attenuation, shared-ancestry "
        "handling (decision ticket 08).",
    ),
    CapabilityEntry(
        "intervention-time-primitives", CODE_KIND, "primitives.py", True,
        "Intervention vs. observation semantics — do() vs. bidirectional belief update "
        "(decision tickets 08, 11).",
    ),
    CapabilityEntry(
        "fair-pricing-engine", CODE_KIND, "pricing.py", True,
        "PERT sampling (pert.py), heavy-tailed severity (severity.py), TVaR, constraint "
        "pre-filter, trade-off curve (tradeoff.py) (decision ticket 09).",
    ),
    CapabilityEntry(
        "scenario-execution-forecast-objects", CODE_KIND, "verbs.py", True,
        "Scenario/execution/forecast objects + pin capture; time-gating by information regime "
        "(regimes.py) (decision ticket 13).",
    ),
    CapabilityEntry(
        "scoring-harness", CODE_KIND, "scoring.py", True,
        "Proper scoring rules, reliability diagrams, regime tagging, contamination discount "
        "(decision tickets 08, 11, 19).",
    ),
    CapabilityEntry(
        "unbound-signal-pool", CODE_KIND, "unbound_pool.py", True,
        "Decay of the unbound signal pool + retrospective sweep (retrospective_sweep.py) "
        "(decision ticket 11).",
    ),
    CapabilityEntry(
        "provenance", CODE_KIND, "attest.py", True,
        "Signing (sign.py), pin capture, reproducibility checks (reproduce.py) "
        "(decision ticket 14).",
    ),
    CapabilityEntry(
        "substrate-eval-suite", CODE_KIND, "substrate_eval.py", True,
        "The fidelity target is measured, not asserted (decision ticket 12).",
    ),
    CapabilityEntry(
        "ethics-gate", CODE_KIND, "ethics_gate.py", True,
        "RECLASSIFIED from decision ticket 20 Q3's own 'skill' listing (build ticket 90 — see "
        "this module's docstring for the full reasoning). skill-thresholds.yaml and "
        "twin/skills.py still score it as one of 'the six real skills'; that machinery is left "
        "as-is. What ethics_gate.scorer() actually scores — admit()'s ladder-walk + DPIA triage "
        "— is a deterministic rule engine over an already-quantified payload with exactly one "
        "correct answer, unlike the other five skills' heuristics, each of which documents its "
        "own 'swap the body for a model call' upgrade path that ethics_gate.py's admission "
        "machinery does not and cannot have. classify_gameability()'s free-text reading is the "
        "one genuinely interpretive piece of this module, and it is not part of what the "
        "threshold entry scores.",
    ),

    # -- inherited from arckit: still code, but ported rather than authored ---------------------
    CapabilityEntry(
        "wardley-maths", INHERITED_KIND, "wardley.py", True,
        "D/K/R Wardley maths — inherited from /arckit:wardley (research 04).",
    ),
    CapabilityEntry(
        "blast-radius", INHERITED_KIND, "blast.py", True,
        "Reverse-dependency traversal — inherited from /arckit:impact.",
    ),
    CapabilityEntry(
        "scheduled-execution", INHERITED_KIND, "schedule.py", True,
        "Scheduled-execution orchestration — inherited from /arckit:build --refresh (research 04).",
    ),

    # -- skill: irreducibly interpretive, produces grade-5 claims (decision ticket 20 Q1/Q3) ----
    CapabilityEntry(
        "signal-classify", SKILL_KIND, "signal_classify.py", False,
        "STEEP-tag + bind signals to components (decision ticket 11).",
    ),
    CapabilityEntry(
        "causal-claims", SKILL_KIND, "causal_claims.py", False,
        "Propose causal edges with sign/lag/elasticity, evidence grade, alternatives "
        "(decision ticket 08).",
    ),
    CapabilityEntry(
        "evolution-judge", SKILL_KIND, "evolution_judge.py", False,
        "Infer component position from accumulated evidence (decision ticket 11).",
    ),
    CapabilityEntry(
        "substrate-generator", SKILL_KIND, "substrate_generator.py", False,
        "Generate the world + plant signals against the eval targets (decision ticket 12).",
    ),
    CapabilityEntry(
        "gameplay-lens", SKILL_KIND, "gameplay_lens.py", False,
        "Wardley plays whose preconditions hold; doctrine/climate suggestions "
        "(decision ticket 13).",
    ),
)

# -- AC 4: each skill's owned decision-record ---------------------------------------------------
#
# Only the capabilities `CAPABILITY_INVENTORY` classifies `skill` — which, after the ethics-gate
# correction above, is five, not six. Validated against `.scratch/twin/issues/` existing, the same
# glob `twin.grades.acceptance_criteria()` uses, by `validate_owning_tickets()` below.

SKILL_OWNING_TICKET: dict[str, str] = {
    "signal-classify": "11",
    "causal-claims": "08",
    "evolution-judge": "11",
    "substrate-generator": "12",
    "gameplay-lens": "13",
}


def validate_inventory(
    inventory: tuple[CapabilityEntry, ...] = CAPABILITY_INVENTORY,
    twin_dir: Path | None = None,
    thresholds_path: Path | None = None,
) -> None:
    """AC 2's own check, literally: every 'code' (or 'inherited') entry has a corresponding
    non-empty module; every 'skill' entry has a threshold entry in skill-thresholds.yaml. Also
    ties AC 1's predicate to AC 2's table, so a hand-edited `kind` that contradicts its own
    `reproducible_from_pins` flag is refused rather than silently trusted."""
    directory = twin_dir or PACKAGE_DIR
    thresholds = load_thresholds(thresholds_path)["thresholds"]
    seen: set[str] = set()
    for entry in inventory:
        if entry.name in seen:
            raise HonestBuildError(f"capability {entry.name!r} is declared twice in the inventory")
        seen.add(entry.name)

        if entry.kind not in _VALID_KINDS:
            raise HonestBuildError(
                f"capability {entry.name!r} declares unknown kind {entry.kind!r} "
                f"(have: {', '.join(_VALID_KINDS)})"
            )

        determinism_kind = classify_by_determinism(entry.reproducible_from_pins)
        if entry.kind == SKILL_KIND and determinism_kind != SKILL_KIND:
            raise HonestBuildError(
                f"capability {entry.name!r} is classified {SKILL_KIND!r} but declares "
                "reproducible_from_pins=True, which the determinism-split test reads as code"
            )
        if entry.kind in (CODE_KIND, INHERITED_KIND) and determinism_kind != CODE_KIND:
            raise HonestBuildError(
                f"capability {entry.name!r} is classified {entry.kind!r} but declares "
                "reproducible_from_pins=False, which the determinism-split test reads as a skill"
            )

        module_path = directory / entry.module
        if not module_path.is_file() or module_path.stat().st_size == 0:
            raise HonestBuildError(
                f"capability {entry.name!r} ({entry.kind}) cites {entry.module}, which is not a "
                "real, non-empty file"
            )

        if entry.kind == SKILL_KIND and entry.name not in thresholds:
            raise HonestBuildError(
                f"capability {entry.name!r} is classified {SKILL_KIND!r} but has no threshold "
                "entry in skill-thresholds.yaml"
            )


def validate_owning_tickets(
    mapping: dict[str, str] = SKILL_OWNING_TICKET,
    inventory: tuple[CapabilityEntry, ...] = CAPABILITY_INVENTORY,
    tickets_dir: Path | None = None,
) -> None:
    """AC 4's own check: every capability the inventory classifies `skill` has exactly one owning
    decision ticket, and that ticket file exists under `.scratch/twin/issues/`."""
    directory = tickets_dir or DECISION_TICKETS_DIR
    skill_names = {e.name for e in inventory if e.kind == SKILL_KIND}

    missing = sorted(skill_names - mapping.keys())
    if missing:
        raise HonestBuildError(f"skill(s) with no owning ticket in SKILL_OWNING_TICKET: {', '.join(missing)}")

    extra = sorted(mapping.keys() - skill_names)
    if extra:
        raise HonestBuildError(
            f"SKILL_OWNING_TICKET names {', '.join(extra)}, which CAPABILITY_INVENTORY does not "
            f"classify {SKILL_KIND!r}"
        )

    for name, ticket in mapping.items():
        if not sorted(directory.glob(f"{ticket}-*.md")):
            raise HonestBuildError(
                f"skill {name!r} claims owning ticket {ticket!r}, which has no file under {directory}"
            )


def inventory_summary() -> dict[str, Any]:
    """A dict view of the inventory, grouped by kind — what a reader (or a future ticket) would
    otherwise have to filter `CAPABILITY_INVENTORY` by hand to get."""
    return {
        kind: sorted(e.name for e in CAPABILITY_INVENTORY if e.kind == kind)
        for kind in _VALID_KINDS
    }
