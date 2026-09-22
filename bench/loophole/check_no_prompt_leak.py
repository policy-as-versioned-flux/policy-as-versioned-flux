"""Prove no loophole prompt text reaches the project tree (ADR-0030 point 7).

loophole carries no licence, so the estate may keep the model's responses and never
loophole's own prompt text. The committed call log stores a sha256 and a length for each
prompt in place of the text. This check confirms that, rather than asserting it.

Method: take every run of 8 consecutive words from the upstream prompt module, normalise
whitespace and case, and look for each one in the files named. A hit is a leak. A negative
control proves the detector fires: every run must be found in the source itself, or the check
refuses to report at all.

Moved from `.scratch/laya-loophole/bench/check_no_prompt_leak.py` by eco-system ticket 115.
The method is unchanged. A directory argument is now walked, so a whole round can be checked.

Usage:
  LOOPHOLE_SRC=<clone> python bench/loophole/check_no_prompt_leak.py <file-or-dir> [...]

Exit 0 clean, 1 on any leak. A failed control exits with its reason.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

WINDOW = 8
WORD = re.compile(r"\S+")


def normalise(text: str) -> str:
    return " ".join(text.lower().split())


def shingles(text: str, window: int = WINDOW) -> set[str]:
    words = WORD.findall(normalise(text))
    return {" ".join(words[i:i + window]) for i in range(len(words) - window + 1)}


def prompt_module(src: Path) -> Path:
    path = src / "loophole" / "prompts.py"
    if not path.exists():
        sys.exit(f"no prompt module at {path}")
    return path


def load_needles(src: Path) -> set[str]:
    return shingles(prompt_module(src).read_text())


def control_hits(needles: set[str], src: Path) -> int:
    hay = normalise(prompt_module(src).read_text())
    return sum(1 for n in needles if n in hay)


def require_control(needles: set[str], src: Path) -> int:
    """The negative control: the detector must fire on text that really is a copy."""
    hits = control_hits(needles, src)
    if not needles or hits != len(needles):
        sys.exit(f"CONTROL FAILED: {hits}/{len(needles)} runs found in the source itself")
    return hits


def files_under(paths: list[Path]) -> list[Path]:
    out: list[Path] = []
    for path in paths:
        if path.is_dir():
            out += sorted(p for p in path.rglob("*") if p.is_file())
        else:
            out.append(path)
    return out


def scan(needles: set[str], paths: list[Path]) -> dict[str, list[str]]:
    """Every leaked run, per file. An empty list is a clean file."""
    result: dict[str, list[str]] = {}
    for path in files_under(paths):
        hay = normalise(path.read_text(errors="replace"))
        result[str(path)] = sorted(n for n in needles if n in hay)
    return result


def main(argv: list[str]) -> int:
    src = os.environ.get("LOOPHOLE_SRC")
    if not src:
        sys.exit("set LOOPHOLE_SRC to the loophole clone outside the project tree")
    if not argv:
        sys.exit("name at least one file or directory to check")
    clone = Path(src)
    needles = load_needles(clone)
    print(f"prompt module: {prompt_module(clone)}")
    print(f"distinct {WINDOW}-word runs: {len(needles)}")
    hits = require_control(needles, clone)
    print(f"negative control: {hits}/{len(needles)} runs found in the source itself, "
          f"so the detector fires")

    leaked = 0
    for path, found in scan(needles, [Path(a) for a in argv]).items():
        print(f"{'LEAK' if found else 'clean'}: {path} ({len(found)} runs)")
        for h in found[:5]:
            print(f"    {h!r}")
        leaked += len(found)
    print(f"total leaked runs: {leaked}")
    return 1 if leaked else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
