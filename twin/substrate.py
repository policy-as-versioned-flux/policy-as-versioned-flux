"""The substrate recipe format, seeded regeneration, and the authored-or-derived spike
(build ticket 48).

Decision ticket 12 requires the bulk synthetic substrate to be **regenerable, not merely
stored**: a small, versioned **generator recipe** — prompts, seed, model version, planted-signal
schedule — lives in git, and the bulk output it describes lives outside it, addressed by content
hash (`twin/blob.py`, build ticket 01's exception, exercised here for real for the first time:
that ticket's own reference form round-tripped with no substrate present; this one has some).

## The authored-or-derived spike

`substrate-generator` (build ticket 49) will be a **grade-5, non-deterministic skill** — an LLM
generating a coherent multi-modal corpus. `identical_pins_identical_bytes` needs the *derivation*
to be reproducible given its pins (decision ticket 14: "derivation must be deterministic given the
pins... If we cannot reproduce the derivation, the attestation is a claim rather than a proof.").
A live model call cannot promise that: no provider guarantees byte-identical output for an
identical prompt and seed, on this call or the next one, this model version or the next.

Two toy generators below demonstrate the two cases side by side, so the answer is measured rather
than argued:

- `generate_deterministic` — no model call at all, `random.Random(recipe.seed)` choosing among the
  recipe's own templates. Regenerating from the identical recipe reproduces byte-for-byte, on any
  machine, forever (`tests/test_substrate.py`). This is what "derived" would require, and it is
  the toy ticket 48's first acceptance criterion asks for: recipe + seed regenerates a substrate.
- `generate_non_reproducible` — a stand-in for the real generator. Honest rather than a claim about
  how any actual model behaves: it draws entropy from `os.urandom`, which the recipe cannot pin no
  matter how completely it is written down — exactly what a live call over an API is, because the
  recipe pins the *request*, never the *response*. Regenerating from the identical recipe does
  **not** reproduce (`tests/test_substrate.py`), and nothing about writing the recipe more
  carefully would fix that.

**The answer: regenerated substrate is AUTHORED, not derived.** Once generation touches a model
whose behaviour on a later call is not under this system's control, `identical_pins_identical_bytes`
cannot be asserted for it, and ticket 14 is explicit about the consequence: an attestation that
cannot be reproduced is a claim, not a proof, and nothing here is marked derived on a claim.

Two consequences, both realised rather than left as prose:

- **Pin capture.** A substrate blob is pinned by its own content hash
  (`sha256:<64 hex>:<size>`), never by the recipe that produced it — the recipe describes a
  *request*, the hash names the *response actually received*, and only the second is what a
  downstream artefact can safely reference. `tests/test_substrate.py`'s
  `test_twin_verify_reproduces_a_substrate_referencing_artefact_without_regenerating_the_substrate`
  is the concrete finding the "twin verify attempt" this ticket asks for produced: replaying a
  `sense` artefact that references real substrate reproduces cleanly, and does so **without ever
  calling a substrate generator** — `twin/reproduce.py`'s `sense` branch re-reads the committed
  reference string, the same as any other pinned fact. The reference participates in derivation;
  the bytes behind it never do, which is exactly why they have to be captured once (authored)
  rather than regenerated on demand.
- **Anomaly detection.** `derived_never_human_signed` is exercised against this boundary directly.
  An artefact carrying the substrate content itself, marked `authored`, accepts a human signature
  — someone is accountable for admitting this particular generated batch as ground truth, the same
  shape a `world-model` or the constraint set already carries. An artefact that only *references*
  the substrate by its content hash stays `derived` and refuses one, unchanged from build ticket
  01 — the boundary sits at the reference, not at the bytes it names.
"""

from __future__ import annotations

import os
import random
from dataclasses import dataclass

import yaml

RECIPE_SCHEMA = "twin.substrate-recipe/v1"


class SubstrateRecipeError(ValueError):
    pass


@dataclass(frozen=True)
class SubstrateRecipe:
    """Decision ticket 12's "generator recipe": prompts, seed, model version, planted-signal
    schedule. Small and versioned in git; the bulk output it describes lives outside it."""

    id: str
    seed: int
    templates: tuple[str, ...]
    model_version: str
    planted_signals: tuple[str, ...] = ()

    @classmethod
    def from_yaml(cls, text: str) -> "SubstrateRecipe":
        raw = yaml.safe_load(text)
        if not isinstance(raw, dict) or raw.get("schema") != RECIPE_SCHEMA:
            raise SubstrateRecipeError(f"not a {RECIPE_SCHEMA} recipe")
        try:
            templates = tuple(str(t) for t in raw["templates"])
            if not templates:
                raise SubstrateRecipeError("recipe declares no templates to generate from")
            return cls(
                id=str(raw["id"]),
                seed=int(raw["seed"]),
                templates=templates,
                model_version=str(raw["model_version"]),
                planted_signals=tuple(str(s) for s in raw.get("planted_signals", [])),
            )
        except KeyError as exc:
            raise SubstrateRecipeError(f"recipe missing required field {exc}") from None

    def to_yaml(self) -> str:
        return yaml.safe_dump(
            {
                "schema": RECIPE_SCHEMA,
                "id": self.id,
                "seed": self.seed,
                "templates": list(self.templates),
                "model_version": self.model_version,
                "planted_signals": list(self.planted_signals),
            },
            sort_keys=True,
        )


def generate_deterministic(recipe: SubstrateRecipe, count: int = 20) -> bytes:
    """No model call: `random.Random(recipe.seed)` choosing among the recipe's own templates.

    Regenerating from the identical recipe reproduces byte-for-byte, on any machine, forever —
    the mechanism ticket 48's first acceptance criterion asks for, and the toy demonstration of
    what "derived" would require.
    """
    rng = random.Random(recipe.seed)
    lines = [rng.choice(recipe.templates) for _ in range(count)]
    return ("\n".join(lines) + "\n").encode("utf-8")


def generate_non_reproducible(recipe: SubstrateRecipe, count: int = 20) -> bytes:
    """A stand-in for the real generator (build ticket 49): identical recipe, identical seed and
    templates, but drawing on entropy (`os.urandom`) the recipe cannot pin — the one honest thing
    a live model call over an API actually is. Not a claim about how any real model behaves;
    the minimal, honest simulation that lets the spike be demonstrated in-process, for pennies,
    rather than asserted from a training claim nobody here can verify.
    """
    rng = random.Random(int.from_bytes(os.urandom(8), "big"))
    lines = [rng.choice(recipe.templates) for _ in range(count)]
    return ("\n".join(lines) + "\n").encode("utf-8")
