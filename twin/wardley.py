"""The Wardley spine: evolution positions and the D/K/R relations.

**Inherited, not rebuilt** (build ticket 14). The bands and the three relations are ported from
the installed arckit plugin, `~/.claude/plugins/cache/arc-kit/arckit/6.7.5/`:

* the stage bands from `hooks/validate-wardley-math.mjs` (`evolutionToStage`), and
* `D`, `K` and `R` from `skills/wardley-mapping/references/mathematical-models.md`, section B.

Ported because that side of arckit is deterministic maths validated on write, which is exactly
the code half of the determinism split (decision ticket 20). The judgement half — which position
a component actually holds, which play to make — is a skill and lands at build ticket 44.

**Three caveats travel with the inheritance, recorded here because here is where they bite.**

1. arckit publishes each relation with an **action band** ("must invest", "strong candidate for
   outsourcing"). The number is inherited; the action band is **not**, and must not be. An action
   band in an artefact is a recommended action under another name, which `no_recommended_action_field`
   refuses. A reader may draw the action; the artefact never states it.
2. arckit's own `impact` analysis carries **no history**, so its deltas cannot be scored against
   what happened. Nothing here may treat a D/K/R number as a forecast: these are positional
   descriptions of a map, not claims about the future, and nothing scores them.
3. arckit's £ deltas are **prose rather than formulas**. No money enters through this module. The
   £ chain is build tickets 23-33 and starts from a distribution, never from a position.
4. arckit's published worked example for `R` prints `0.85 x 0.75 = 0.64`, which is 0.6375 rounded
   for display. The maths is inherited at full precision; the rounding is not, because a display
   convention inside a byte-reproducible artefact is a divergence waiting to happen.

No quantisation. Each relation is a single IEEE-754 multiplication over values parsed from text,
so it is bit-identical on every platform — unlike `math.log` in the scoring rules, which is why
that module declares a precision and this one does not.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Ported from arckit `evolutionToStage`: < 0.25 genesis, < 0.50 custom, < 0.75 product, else
# commodity. arckit spells the second stage "Custom"; the schema here spells it "custom-built".
BANDS: tuple[tuple[str, float, float], ...] = (
    ("genesis", 0.0, 0.25),
    ("custom-built", 0.25, 0.50),
    ("product", 0.50, 0.75),
    ("commodity", 0.75, 1.0),
)

RELATIONS = ("differentiation_pressure", "commodity_leverage", "dependency_risk")


class WardleyError(ValueError):
    """A position that is not a position."""


def stage_of(position: float) -> str:
    """Which stage an axis position falls in. The inherited banding, exactly."""
    value = float(position)
    if not 0.0 <= value <= 1.0:
        raise WardleyError(f"evolution position {value} is outside the axis [0, 1]")
    for name, low, high in BANDS:
        if value < high:
            return name
    return BANDS[-1][0]


def band(stage: str) -> tuple[float, float]:
    for name, low, high in BANDS:
        if name == stage:
            return low, high
    raise WardleyError(f"unknown evolution stage {stage!r}")


def midpoint(stage: str) -> float:
    """The position a stage implies when no finer one is authored.

    Derived rather than defaulted-to-zero: a stage *is* a position, coarsely. Recording the
    midpoint keeps the axis populated while leaving the authored value distinguishable — a
    component that declares `evolution_position` says so in the artefact.
    """
    low, high = band(stage)
    return (low + high) / 2


def differentiation_pressure(visibility: float, evolution: float) -> float:
    """`D(v) = visibility x (1 - evolution)` — arckit mathematical-models.md, section B."""
    return float(visibility) * (1.0 - float(evolution))


def commodity_leverage(visibility: float, evolution: float) -> float:
    """`K(v) = (1 - visibility) x evolution` — same source."""
    return (1.0 - float(visibility)) * float(evolution)


def dependency_risk(visibility_a: float, evolution_b: float) -> float:
    """`R(a, b) = visibility(a) x (1 - evolution(b))` — how risky it is that a visible component
    depends on an immature one. Same source."""
    return float(visibility_a) * (1.0 - float(evolution_b))


@dataclass(frozen=True)
class Position:
    """Where one component sits on the map, and what the relations say about it."""

    component: str
    visibility: float
    evolution: float
    stage: str
    position_authored: bool

    @classmethod
    def of(cls, component_id: str, doc: dict[str, Any]) -> "Position | None":
        """A component's position, or `None` when it declares none.

        Never guessed. A component with no stage has no place on the axis, and inventing one
        would put a number nobody authored into a map somebody reads.
        """
        stage = doc.get("evolution")
        visibility = doc.get("visibility")
        if stage is None or visibility is None:
            return None
        authored = doc.get("evolution_position")
        return cls(
            component=component_id,
            visibility=float(visibility),
            evolution=float(authored) if authored is not None else midpoint(str(stage)),
            stage=str(stage),
            position_authored=authored is not None,
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "component": self.component,
            "stage": self.stage,
            "evolution": self.evolution,
            "evolution_position_authored": self.position_authored,
            "visibility": self.visibility,
            "differentiation_pressure": differentiation_pressure(self.visibility, self.evolution),
            "commodity_leverage": commodity_leverage(self.visibility, self.evolution),
        }


def positions(components: dict[str, dict[str, Any]]) -> dict[str, Position]:
    found = {i: Position.of(i, doc) for i, doc in sorted(components.items())}
    return {i: p for i, p in found.items() if p is not None}


def map_of(components: dict[str, dict[str, Any]], edges: Any) -> dict[str, Any]:
    """The map, derived from the graph. There is no authoring step and no separate map file.

    `dependency_risk` is computed per structural edge, because R is a property of a dependency
    rather than of a component. Edges whose either end has no position are listed by name instead
    of being silently dropped: an omission a reader cannot see is worse than a gap they can.
    """
    placed = positions(components)
    risks = []
    unplaced_edges = []
    for edge in edges:
        # Spelled out rather than imported from `schema.STRUCTURAL_EDGE`: schema imports this
        # module for the band check, so importing it back would be a cycle.
        if edge.type != "needs":
            continue
        source, target = placed.get(edge.source), placed.get(edge.target)
        if source is None or target is None:
            unplaced_edges.append(edge.id)
            continue
        risks.append(
            {
                "from": edge.source,
                "to": edge.target,
                "dependency_risk": dependency_risk(source.visibility, target.evolution),
            }
        )
    return {
        "axis": {
            "evolution": [{"stage": n, "from": lo, "to": hi} for n, lo, hi in BANDS],
            "inherited_from": "arckit 6.7.5 — hooks/validate-wardley-math.mjs, "
            "skills/wardley-mapping/references/mathematical-models.md section B",
            "action_bands_inherited": False,
        },
        "positions": [p.as_dict() for p in placed.values()],
        "dependency_risk": risks,
        "unpositioned": sorted(set(components) - set(placed)),
        "edges_without_both_ends_positioned": sorted(unplaced_edges),
    }


def plot(wardley: dict[str, Any], width: int = 64, height: int = 17) -> str:
    """The map as text, rendered from the same block the artefact carries.

    A render, not a second model: it reads `map_of`'s output and nothing else, so a map cannot
    disagree with the graph it came from.
    """
    grid = [[" "] * width for _ in range(height)]
    labels: list[str] = []
    for i, entry in enumerate(sorted(wardley["positions"], key=lambda p: str(p["component"]))):
        letter = chr(ord("a") + i) if i < 26 else "?"
        x = min(width - 1, int(float(entry["evolution"]) * (width - 1)))
        y = min(height - 1, int((1.0 - float(entry["visibility"])) * (height - 1)))
        grid[y][x] = letter
        labels.append(
            f"  {letter}  {entry['component']}  ({entry['stage']}, "
            f"evo {entry['evolution']:.3f}, vis {entry['visibility']:.2f}, "
            f"D {entry['differentiation_pressure']:.3f}, K {entry['commodity_leverage']:.3f})"
        )

    quarter = width // 4
    rows = ["  visible to the user"]
    rows += ["  |" + "".join(row) for row in grid]
    rows.append("  +" + "-" * width + "> evolution")
    rows.append("   " + "".join(name.ljust(quarter)[:quarter] for name, _, _ in BANDS))
    return "\n".join(rows + [""] + labels)
