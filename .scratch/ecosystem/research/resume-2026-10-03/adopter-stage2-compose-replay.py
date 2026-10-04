#!/usr/bin/env python3
"""Candidate-only compose/replay diagnostic; never write shared composed files."""
from __future__ import annotations

import json
import difflib
from pathlib import Path
import shutil
import sys
import tempfile
import traceback

import yaml

ROOT = Path(__file__).resolve().parents[4]
DEST = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / ".estate-clone/platform/compose"))
import composition


def main() -> int:
    results = {}
    failed = False
    for org in ("driftwood", "tuppence", "ludlow"):
        adopter = ROOT / ".estate-clone" / org
        party = yaml.safe_load((adopter / "party.yaml").read_text())
        trees = composition._default_parent_trees(party, adopter.parent)
        try:
            document, rendered = composition.compose(adopter, trees)
            if document["outcome"] != "composed":
                raise ValueError("candidate composition refused: " + str(document.get("refusals")))
            (DEST / (org + "-stage2-compose-document.json")).write_text(
                json.dumps(document, indent=2, sort_keys=True) + "\n"
            )
            with tempfile.TemporaryDirectory(prefix="stage2-byte-replay-") as temporary:
                snapshot = Path(temporary) / org
                shutil.copytree(adopter, snapshot, ignore=shutil.ignore_patterns(".git", "__pycache__"))
                # All git operations performed by composition/validation are reads.
                # The snapshot reads the authentic tag objects and committed baseline.
                (snapshot / ".git").symlink_to((adopter / ".git").resolve(), target_is_directory=True)
                for relative, content in rendered.items():
                    path = snapshot / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(content)
                # Remove derived YAML retired by this candidate's re-render.
                for path in (snapshot / "composed").rglob("*.yaml"):
                    if str(path.relative_to(snapshot)) not in rendered:
                        path.unlink()
                replayed, mismatches = composition.verify(snapshot, trees)
                if not replayed:
                    header = yaml.safe_load((snapshot / "composed/HEADER.yaml").read_text())
                    _, replay_rendered = composition.compose(
                        snapshot, trees,
                        as_of=header.get("composition-as-of"),
                        replay_observations=True,
                    )
                    differences = []
                    for relative, content in replay_rendered.items():
                        before = (snapshot / relative).read_text()
                        if before != content:
                            differences.extend(difflib.unified_diff(
                                before.splitlines(keepends=True), content.splitlines(keepends=True),
                                fromfile=relative + " (fresh)", tofile=relative + " (replay)",
                            ))
                    (DEST / (org + "-stage2-byte-replay.diff")).write_text("".join(differences))
                    raise ValueError("candidate byte replay differs: " + str(mismatches))
            results[org] = {
                "outcome": "composed",
                "refusals": document.get("refusals", []),
                "rendered_files": len(rendered),
                "temporary_copy_byte_replay": True,
                "shared_composed_files_written": False,
                "candidate_only": True,
                "authenticated_foundation_adoption": False,
                "cve_prices": [row for row in document.get("prices", []) if row.get("name") == "cve"],
            }
            print(org + ": candidate composed and temporary-copy byte replay PASS")
        except (Exception, SystemExit) as error:
            failed = True
            results[org] = {
                "outcome": "instrument_error",
                "error": str(error),
                "traceback": traceback.format_exc(),
                "shared_composed_files_written": False,
                "candidate_only": True,
            }
            print(org + ": " + str(error))
    (DEST / "adopter-stage2-compose-replay.json").write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
