"""`twin substrate`: the substrate's own figures, emitted rather than only computable
(build ticket 73).

Build tickets 48-52 built the mechanism — the recipe format, the generator, spine anchoring, the
fidelity eval suite, the planter/detector/scorer split — and ticket 73 part 1 supplied one real
subject's content. What was missing was a **surface**: every one of those figures existed only
when somebody imported the library and called it, so ticket 73's "measured **and reported**"
criterion stayed unticked on a measurement that was already passing. This module is the reported
half, and it deliberately carries both readings in one artefact, because they are two readings of
one generated batch at one checkpoint and a reader comparing them across two files would be
comparing two different batches.

**The report is derived, not authored.** `twin/substrate.py`'s spike established that regenerated
substrate *content* is authored — a live model call cannot promise byte-identity, so an
attestation over it would be a claim. This artefact carries no substrate content: it carries
measurements over a batch produced by `substrate_generator.generate()`, which is the deterministic
reference implementation and draws no external entropy. Swap that generator for a live model and
this mark stops being defensible, which is why the recipe's `model_version` is pinned in the
envelope rather than mentioned in the body.

**Publishing the plants is not a leak.** Every planted signal is already written out in the
committed recipe, in git, for anyone to read. The seal build ticket 52 enforces is between the
*planter and the detector code paths*, not between the plants and a human reader — and the scorer
is by definition the half that reads both, so a score that would not name what it scored would be
unreadable for no gain.

**`twin verify <artefact> --repo R` cannot replay this one**, the same limit `reliability` and
`severity` already carry: the recorded command names the recipe by basename, because a machine
path in the envelope would break `identical_pins_identical_bytes` across machines, and a basename
is not enough to find the file again. The recipe's content hash is pinned, so a reader can still
check the input they hold is the input that was read — what is not automated is re-running the
derivation from the envelope alone.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import TOOL_VERSION, planter, spine as spine_mod, substrate_eval
from .artefact import Artefact, DERIVED
from .canon import sha256_hex
from .detector import detect
from .grades import Capabilities
from .model import Overlay
from .repo import ModelRepo
from .scorer import ScoreResult, score
from .spine import Spine
from .substrate import SubstrateRecipe
from .substrate_generator import generate

KIND_SUBSTRATE_REPORT = "substrate-report"

# Decision ticket 12's own capability, and only it. The spine is read here, but reading an org's
# dated signals is what `synthetic-substrate` AC 1's seam already is (`Spine.from_overlay`), not a
# second capability's work — the same reasoning `unbound_pool` reuses `CAPS_SENSE` rather than
# minting a capability for the pool.
CAPS_SUBSTRATE = ["synthetic-substrate"]


def report(
    repo: ModelRepo, caps: Capabilities, org: str, recipe_path: str | Path, checkpoint: str,
    detected_at: str, command: list[str],
) -> Artefact:
    """One recipe against one org's spine at one checkpoint: seven fidelity dimensions, and the
    planter/detector/scorer walk over the plants that batch actually carries.

    `detected_at` is the date the detector's run is scored as having happened, which is what
    decides timely against late. It defaults to the checkpoint at the CLI: asking the substrate how
    it reads *now* is the ordinary question, and reading it from a later date is the deliberate one.
    """
    path = Path(recipe_path)
    recipe_bytes = path.read_bytes()
    recipe = SubstrateRecipe.from_yaml(recipe_bytes.decode("utf-8"))
    overlay = Overlay.load(repo, org)
    spine = Spine.from_overlay(overlay)

    batch = generate(recipe)
    metrics = substrate_eval.evaluate_fidelity(batch, spine, checkpoint)
    # The over-anchoring attack, counted (build ticket 50). The free-running half has to dominate,
    # or a reader diffing the substrate against the spine recovers the plants directly.
    anchored = spine_mod.anchor(batch, spine, checkpoint)
    split = spine_mod.diff_against_spine(anchored, spine)
    # AC 7's hard gate (build ticket 87): refused before the batch's own report is committed as an
    # artefact, not merely reported as a failing fidelity dimension a reader could ignore.
    substrate_eval.refuse_if_contaminated(anchored)

    dates, reasons, strengths = planter.horizons_for(recipe)
    world = planter.plant(recipe, dates, strengths)
    result = score(world.ground_truth, detect(world.public), detected_at=detected_at)

    return Artefact(
        kind=KIND_SUBSTRATE_REPORT,
        mark=DERIVED,
        command=command,
        pins={
            "model_repo": repo.pin.as_dict(),
            "overlay": overlay.ref.as_dict(),
            "world": overlay.world.ref.as_dict(),
            "org": overlay.org,
            "tool": {"name": "twin", "version": TOOL_VERSION, "capabilities_digest": caps.digest},
            # The recipe is a file outside the model repository, so it is pinned the way any
            # out-of-repo input is: by the hash of the bytes actually read, never by its path.
            "recipe": {
                "id": recipe.id, "sha256": sha256_hex(recipe_bytes), "seed": recipe.seed,
                "model_version": recipe.model_version,
            },
            "spine": spine.pin(),
            "checkpoint": checkpoint,
            "detected_at": detected_at,
        },
        depth=caps.depth_block(CAPS_SUBSTRATE),
        body={
            "fidelity": {
                "metrics": [m.as_dict() for m in metrics],
                "passes": substrate_eval.passes(metrics),
                "unfair_test_conditions": [
                    {"condition": condition, "caught_by": caught_by}
                    for condition, caught_by in substrate_eval.UNFAIR_TEST_CONDITIONS
                ],
            },
            "spine": {
                "facts_total": len(spine.facts),
                "facts_knowable_by_checkpoint": len(spine.at(checkpoint)),
                "anchored_lines": len(split["anchored"]),
                "free_running_lines": len(split["free_running"]),
            },
            "detection": _detection(result, reasons),
        },
    )


def _detection(result: ScoreResult, reasons: dict[str, str]) -> dict[str, Any]:
    """The walk's result, with each plant's horizon reason carried beside its score.

    `hit_rate` and `mean_score` sit next to the per-plant rows rather than instead of them: a mean
    over four plants where three scored zero is the same number as four plants that each scored a
    quarter, and only one of those is a system worth shipping.
    """
    return {
        "detected_at": result.detected_at,
        "hit_rate": result.hit_rate,
        "mean_score": result.mean_score,
        "plants": [
            {
                "channel": p.plant.channel,
                "index": p.plant.index,
                "signal": p.plant.signal,
                "actionability_horizon": p.plant.actionability_horizon,
                "horizon_reason": reasons[p.plant.signal],
                "strength": p.plant.strength,
                "detected": p.detected,
                "timely": p.timely,
                "score": p.score,
                "reason": p.reason,
            }
            for p in result.plant_scores
        ],
        "limitation": result.limitation,
    }
