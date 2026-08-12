"""The derived index — a store, and therefore never authoritative.

Git-versioned text is the source of truth; any store is a derived index rebuildable from it
(`store_rebuildable_from_git`). Written per unit rather than as one global file, so no single
derived artefact mixes tenants.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from .canon import canonical_json, digest_of, sha256_hex
from .model import ORGS, Overlay, World, orgs

SCHEMA = "twin.index/v1"
MARKER = ".twin-index"


class IndexError_(RuntimeError):
    """Refused to write an index."""


def _world_index(repo: Any) -> dict[str, Any]:
    world = World.load(repo)
    return {
        "schema": SCHEMA,
        "unit": "world",
        "ref": world.ref.as_dict(),
        "components": sorted(world.components),
        "propositions": sorted(world.propositions),
        "world_models": sorted(world.world_models),
    }


def _overlay_index(repo: Any, org: str) -> dict[str, Any]:
    overlay = Overlay.load(repo, org)
    return {
        "schema": SCHEMA,
        "unit": "overlay",
        "org": org,
        "ref": overlay.ref.as_dict(),
        "world_ref": overlay.world.ref.as_dict(),
        "components": sorted(overlay.components),
        "world_models": sorted(overlay.world_models),
        "signals": sorted(overlay.signals),
        "claims": sorted(overlay.claims),
        "scenarios": sorted(overlay.scenarios),
        "outcomes": sorted(overlay.outcomes),
        "people": sorted(overlay.people),
        "edges": sorted(overlay.edges),
        "perspectives": sorted(overlay.perspectives),
        "regrades": sorted(overlay.regrades),
        # The behavioural overlay is deliberately absent. A derived index of the most private
        # object in the system would be a copy of it that nobody gated.
    }


def build(repo: Any) -> dict[str, bytes]:
    """Relative path -> file bytes. Pure function of the repository at its pin."""
    files = {"world.json": canonical_json(_world_index(repo))}
    for org in orgs(repo):
        files[f"{ORGS}/{org}.json"] = canonical_json(_overlay_index(repo, org))
    return files


def write(repo: Any, out_dir: str | Path) -> Path:
    """Replace the index at `out_dir`.

    Rebuilding means deleting first, and `--out` is whatever the operator typed — so refuse
    anything that is not empty, not already an index, or not a directory. A derived store is
    cheap to lose; the directory someone typed by mistake is not.
    """
    out = Path(out_dir)
    if out.exists():
        if not out.is_dir() or out.is_symlink():
            raise IndexError_(f"{out} is not a directory; refusing to replace it")
        existing = {p.name for p in out.iterdir()}
        if existing and MARKER not in existing:
            raise IndexError_(
                f"{out} is not empty and was not written by twin (no {MARKER}); refusing to delete it"
            )
        shutil.rmtree(out)
    out.mkdir(parents=True)
    (out / MARKER).write_text(f"{SCHEMA}\n", encoding="utf-8")
    for rel, data in build(repo).items():
        target = out / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return out


def digest(files: dict[str, bytes]) -> str:
    return digest_of({rel: sha256_hex(data) for rel, data in sorted(files.items())})


def read_digest(out_dir: str | Path) -> str:
    root = Path(out_dir)
    files = {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*.json"))}
    return digest(files)
