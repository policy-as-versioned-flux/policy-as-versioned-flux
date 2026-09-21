"""Ticket 07 / ticket 11: prove no loophole prompt text reaches the project tree.

loophole carries no licence (map call 5), so the estate may keep the model's
responses and never loophole's own prompt text. The committed call log stores a
sha256 and a length for each prompt in place of the text. This check confirms
that, rather than asserting it.

Method: take every run of 8 or more consecutive words from the upstream prompt
module, normalise whitespace and case, and look for each one in the committed
artefacts. A hit is a leak. A negative control proves the detector fires.

Usage:
  LOOPHOLE_SRC=<clone> python check_no_prompt_leak.py <file> [<file> ...]
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


def main() -> int:
    src = os.environ.get("LOOPHOLE_SRC")
    if not src:
        sys.exit("set LOOPHOLE_SRC to the loophole clone outside the project tree")
    prompts = Path(src) / "loophole" / "prompts.py"
    if not prompts.exists():
        sys.exit(f"no prompt module at {prompts}")

    needles = shingles(prompts.read_text())
    print(f"prompt module: {prompts}")
    print(f"distinct {WINDOW}-word runs: {len(needles)}")

    # Negative control: the detector must fire on text that really is a copy.
    control = normalise(prompts.read_text())
    control_hits = sum(1 for n in needles if n in control)
    if control_hits != len(needles):
        sys.exit(f"CONTROL FAILED: {control_hits}/{len(needles)} runs found in the source itself")
    print(f"negative control: {control_hits}/{len(needles)} runs found in the source itself, "
          f"so the detector fires")

    leaked = 0
    for arg in sys.argv[1:]:
        path = Path(arg)
        hay = normalise(path.read_text())
        hits = sorted(n for n in needles if n in hay)
        status = "LEAK" if hits else "clean"
        print(f"{status}: {path} ({len(hits)} runs)")
        for h in hits[:5]:
            print(f"    {h!r}")
        leaked += len(hits)

    print(f"total leaked runs: {leaked}")
    return 1 if leaked else 0


if __name__ == "__main__":
    raise SystemExit(main())
