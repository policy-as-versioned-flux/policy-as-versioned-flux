"""Ingest, STEEP tagging, and automated binding at throughput (build ticket 53, decision ticket
11 Q2).

Decision ticket 11 Q2 decided binding is **fully automated at volume, trusted downstream rather
than gated at entry** — "this works because the trust machinery is downstream, not at the gate."
Build ticket 43 built the mechanism (`twin/signal_classify.py`) and proved it against a labelled
corpus; this ticket proves the mechanism actually *runs*, unattended, at the volume the
weather-forecast frame (decision ticket 08) needs — against the substrate build ticket 48's
recipe format makes regenerable, because until substrate exists there is nothing to run a
pipeline against at volume.

**No human gate, by construction, not by policy.** `ingest_run` calls `signal_classify.classify`
directly, in a loop, with no confirmation, review or approval step anywhere in its call graph —
there is no parameter through which a caller could inject one (`tests/test_ingest.py`, harness
guard `ingest_runs_unattended_with_provenance_and_measured_throughput`). The safety argument this
rests on is entirely downstream, and is documented here rather than assumed: every item stays at
evidence grade 5 (`signal_classify.classify` cannot self-assert higher —
`signal_classify_is_grade_5_by_construction`), grade 5 cannot price a scored forecast
(`grade_5_only_path_never_prices`), any binding stays contestable (`twin/challenges.py`, build
ticket 60), and binding quality is measured over time through the skill-eval harness's own
labelled-corpus threshold (build tickets 42/43) rather than assumed correct because a human once
looked at it.

**Throughput is measured, not assumed.** `ingest_run` times its own loop wall-clock and reports
`items_per_second` computed from what actually happened, never a declared or hoped-for figure —
the identical discipline `twin/schedule.py`'s scheduled sweep already applies to *forecast*
volume (decision ticket 11 Q5), applied here to *ingest* volume (Q2).

**Every item is provenanced.** Each classified item carries the substrate blob's own content-hash
reference (`twin/blob.py`, exercised for real at build ticket 48), the recipe id and model
version that generated it, and its own index within the batch — the same shape a `signal`
document's required `provenance` field already carries (`twin/schema.py`).

`ponytail:` the substrate this pipeline runs against is `substrate.generate_deterministic` —
build ticket 48's toy, seeded generator, not the real seeded-LLM one (build ticket 49, not yet
built and not a blocker here: this ticket needs *volume*, and the toy generator is exactly as
voluminous as the real one would be). Swapping in the real generator changes nothing about this
module: `ingest_run` reads `recipe` and `count` and gets a byte string back, and does not care
which function produced the bytes.

`ponytail:` no CLI verb. Every other "runs unattended" pipeline in this codebase (`twin sweep`,
`twin gameplay-sweep`) is wired to `twin/cli.py` for a real scheduler to call, but doing that here
would mean inventing a file-based recipe format this ticket does not own (`twin/substrate.py`'s
`SubstrateRecipe` has no on-disk home in a model repository yet — build tickets 49/52 are where
that lands). `ingest_run` is a typed function, exercised at seam 2, exactly the shape
`schedule.sweep()` was before ticket 09 wired its own CLI verb. Add a `twin ingest` subcommand
once a recipe has somewhere to live in git.
"""

from __future__ import annotations

import time
from typing import Any

from . import verbs
from .artefact import Artefact, DERIVED
from .blob import BlobRef
from .grades import Capabilities
from .model import Overlay
from .repo import ModelRepo
from .signal_classify import SignalClassifyError, classify
from .substrate import SubstrateRecipe, generate_deterministic

KIND_INGEST_RUN = "ingest-run"

# The mechanism decision ticket 11 Q2 already decided and build ticket 43 built
# (`twin/signal_classify.py`); this pipeline exercises it at volume, so it carries the identical
# capability set `sense` does rather than a capability of its own.
CAPS_INGEST = verbs.CAPS_SENSE


class IngestError(RuntimeError):
    pass


def candidates_of(overlay: Overlay) -> list[dict[str, str]]:
    """Every component a signal in this overlay might bind to — world layer and org overlay
    together, the same merged set `Overlay.graph()` reads (`twin/model.py`)."""
    merged: dict[str, dict[str, Any]] = {**overlay.world.components, **overlay.components}
    return [{"id": str(c["id"]), "name": str(c["name"])} for c in merged.values()]


def ingest_run(
    repo: ModelRepo,
    caps: Capabilities,
    org: str,
    recipe: SubstrateRecipe,
    count: int,
    command: list[str],
) -> Artefact:
    """Run `signal-classify`, unattended, over `count` items generated from `recipe` — the
    pipeline decision ticket 11 Q2 decided and build ticket 43 built, exercised here at a
    declared volume.

    `count` is the declared throughput target — how much volume to run against. What actually
    happened (elapsed wall-clock, items/second) is measured and reported in the body, never
    assumed to equal what was declared.
    """
    if count <= 0:
        raise IngestError(f"ingest: count must be positive, got {count}")

    overlay = Overlay.load(repo, org)
    candidates = candidates_of(overlay)
    if not candidates:
        raise IngestError(f"ingest: overlay {org!r} declares no component to bind against")

    payload = generate_deterministic(recipe, count=count)
    substrate_ref = BlobRef.of(payload)
    lines = payload.decode("utf-8").splitlines()

    items: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    started = time.monotonic()
    for index, line in enumerate(lines):
        provenance = {
            "substrate": str(substrate_ref),
            "recipe": recipe.id,
            "model_version": recipe.model_version,
            "index": index,
        }
        try:
            result = classify(
                {"statement": line, "source": f"substrate:{recipe.id}", "candidates": candidates}
            )
        except SignalClassifyError as exc:
            failures.append({"index": index, "reason": str(exc), "provenance": provenance})
            continue
        items.append({**result, "provenance": provenance})
    elapsed = time.monotonic() - started

    return Artefact(
        kind=KIND_INGEST_RUN,
        # No human gate at entry: nothing in this pipeline could carry a human's accountability,
        # so it is never marked authored (`derived_never_human_signed`).
        mark=DERIVED,
        command=command,
        pins={
            "model_repo": repo.pin.as_dict(),
            "overlay": overlay.ref.as_dict(),
            "world": overlay.world.ref.as_dict(),
            "org": overlay.org,
            "tool": {"name": "twin", "version": verbs.TOOL_VERSION, "capabilities_digest": caps.digest},
            "substrate": str(substrate_ref),
            "recipe": {"id": recipe.id, "seed": recipe.seed, "model_version": recipe.model_version},
        },
        depth=caps.depth_block(CAPS_INGEST),
        body={
            "throughput": throughput_report(len(lines), elapsed),
            "items": items,
            "failures": failures,
            "gate": (
                "no human gate at entry (decision ticket 11 Q2); safety rests on downstream "
                "gating — grade-5-by-construction, use-gating, contestability and calibration"
            ),
        },
    )


def throughput_report(declared_count: int, elapsed_seconds: float) -> dict[str, Any]:
    """What actually happened, computed — never a hardcoded or assumed rate."""
    return {
        "declared_count": declared_count,
        "elapsed_seconds": elapsed_seconds,
        "items_per_second": (declared_count / elapsed_seconds) if elapsed_seconds > 0 else None,
    }
