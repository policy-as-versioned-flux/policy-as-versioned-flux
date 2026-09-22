#!/usr/bin/env python3
"""Step 1 of the bake-off: dump the six skills' real labelled corpora to JSON.

Map ticket 04 (.scratch/laya-loophole/issues/04-the-bake-off-laya-against-the-six-heuristics.md).

WHY THIS IS A SEPARATE PROCESS. The bake-off needs two pinned environments that cannot be one.
`twin` runs in the repository's own `.venv`. Laya needs `transformers==5.9.0` and `torch==2.9.1`
in `~/.cache/laya-bench/venv`, pinned by ticket 02's `bench/requirements.txt`; installing either
set into the other's interpreter would change the environment one of the two recorded numbers was
taken in. So the corpora are dumped here, Laya is run against the dump by `run_laya.py` in its own
interpreter, and `score.py` reads the predictions back into `twin.skills.evaluate()` in this one.

WHAT IS AND IS NOT DUMPED. `input` and `expected` exactly as each skill's own `labelled_corpus()`
builds them, plus the corpus digest `twin.skills.evaluate()` will compute. Ticket 04 item 3 needs
Laya scored on the SAME corpus digest `heuristic-0.1.0` was scored on, so the digest is carried
here and re-asserted by `score.py`. `expected` is dumped because `score.py` needs it; `run_laya.py`
never reads it, and there is an assertion in that file saying so.
"""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from twin import causal_claims as cc
from twin import ethics_gate as eg
from twin import evolution_judge as ej
from twin import gameplay_lens as gl
from twin import signal_classify as sc
from twin import substrate_generator as sg
from twin.canon import digest_of


def build() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        corpora = {
            sc.SKILL: sc.labelled_corpus(tmp_dir / "signal-classify"),
            ej.SKILL: ej.labelled_corpus(tmp_dir / "evolution-judge"),
            cc.SKILL: cc.labelled_corpus(tmp_dir / "causal-claims"),
            gl.SKILL: gl.labelled_corpus(tmp_dir / "gameplay-lens"),
            sg.SKILL: sg.labelled_corpus(),
            eg.SKILL: eg.labelled_corpus(),
        }
    return {
        skill: {"corpus_digest": digest_of(corpus), "items": corpus}
        for skill, corpus in corpora.items()
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(Path(__file__).parent / "corpora.json"))
    args = ap.parse_args()
    doc = build()
    Path(args.out).write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    for skill, entry in sorted(doc.items()):
        print("%-28s %3d items  digest %s" % (skill, len(entry["items"]), entry["corpus_digest"]))
    print("wrote %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
