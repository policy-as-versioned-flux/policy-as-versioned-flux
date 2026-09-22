#!/usr/bin/env python3
"""Build a labelled corpus for the six twin skills out of MERGED HUMAN CLAIMS.

Map ticket 03 (.scratch/laya-loophole/issues/03-a-labelled-corpus-from-merged-human-claims.md).

WHY THIS EXISTS. The six skills hold 42 hand-authored labelled items between them, and every one
of them was written by the same hand that wrote the heuristic being graded. A label written to
grade a model that replaces a human's judgement has to come from a human's judgement, so this
builder refuses to author a single label. It only harvests ones that already exist because
somebody reviewed and merged them.

THE TWO SOURCES TICKET 03 NAMES.

  A. Merged claim files -- `twin/orgs/<org>/claims/*.yaml` on each adopter's `origin/main`. A
     claim is a human's judgement that passed review. Its `kind` decides which skill it labels:
     `binding` -> signal-classify, `position`/`override` -> evolution-judge. No other kind maps
     to any of the six.
  B. Bound rows in each adopter's `twin/signals.yaml`. Read, counted, and -- see
     `SIGNAL_ROW_VERDICT` below -- reported as labelling NONE of the six skills, because a row
     carries a scenario id and carries neither a STEEP tag nor a single component binding.

WHY THIS READS `origin/main` AND NOT THE WORKING TREE. A checked-out estate clone goes stale, and
a stale clone under-counts merged claims. Every count here is taken from the fetched remote ref,
so "merged" means merged, not "merged as of whenever this directory was last pulled".

WHAT THIS DOES NOT DO. It does not label, infer, relabel, or stretch. A source that yields zero
items reports zero.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# The six skills the twin scores (twin/skill-thresholds.yaml). `toy-classifier` and
# `causal-claims-grade-accuracy` are excluded on purpose: the first is a fixture skill, the second
# is a second metric on causal-claims rather than a seventh skill.
SIX_SKILLS = (
    "signal-classify",
    "evolution-judge",
    "causal-claims",
    "substrate-generator",
    "gameplay-lens",
    "ethics-gate",
)

# Which skill a merged claim of each kind can label, and nothing beyond that. `twin/schema.py`
# `_refine_claim` is the authority on what each kind carries.
CLAIM_KIND_TO_SKILL = {
    "binding": "signal-classify",
    "position": "evolution-judge",
    "override": "evolution-judge",
    "enactment": None,  # an enactment is an act, not a judgement of a thing the six skills judge
}

# WHOSE JUDGEMENT A MERGED CLAIM ACTUALLY CARRIES. Ticket 03's whole premise is that a label used
# to grade a model must come from a human, so "merged" is not the test -- authorship is. The
# schema itself draws the line: `twin/schema.py` `_refine_claim` demands `claimed_by`, checked
# against `twin/roles.yaml`, for an `override` and for nothing else. So:
#
#   HUMAN      an override. Evidence grade 4, "calibrated expert judgement, named by role". The
#              classify-and-judge skill's own rule is "the machine proposes; the role disposes",
#              and an override is the disposal. This is a label.
#   RATIFIED   a binding or a position. Evidence grade 5, no named claimant, WRITTEN BY THE
#              HEURISTIC that the bake-off exists to replace. A human merged the pull request,
#              which is review, not authorship. Grading a candidate model against these measures
#              agreement with the incumbent heuristic, not accuracy -- the exact circularity
#              ticket 03 rules out. Counted, reported, and kept out of the labelled corpus.
#
# This split is the assistant's call under ADR-0025, made 2026-09-21 while resolving ticket 03.
HUMAN_AUTHORED_KINDS = ("override",)
RATIFIED_MACHINE_KINDS = ("binding", "position")

SIGNAL_ROW_VERDICT = (
    "A twin/signals.yaml row binds a pinned feed version to a SCENARIO id. The signal-classify "
    "corpus needs {steep, component}: a STEEP tag and exactly one component binding. A row "
    "carries no STEEP tag at all, and it reaches components only through the scenario, which "
    "names several. So a bound row is a real, merged, human-reviewed label for a question none "
    "of the six skills asks, and deriving a STEEP tag from it here would be this builder "
    "authoring the label -- the one thing ticket 03 forbids."
)


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ("git", "-C", str(repo)) + args, capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def landed_by(repo: Path, ref: str, path: str) -> dict[str, str]:
    """The merge that put `path` on `ref` -- the citation ticket 03 asks every item to carry.

    Two commits are cited, because they answer two different questions. `authored` is the commit
    that added the file, which is when a human wrote the judgement. `merged` is the merge commit
    that put it on the trunk, which is when a second human accepted it. A label's authority comes
    from the second, so an item with no merge commit is not a merged human claim.
    """
    added = git(repo, "log", "--diff-filter=A", "--format=%H|%ad|%s", "--date=short", ref, "--", path)
    if not added:
        return {}
    sha, date, subject = added.splitlines()[0].split("|", 2)
    merges = git(
        repo, "log", "--merges", "--format=%H|%ad|%s", "--date=short", "--ancestry-path",
        f"{sha}..{ref}",
    )
    merge = merges.splitlines()[-1].split("|", 2) if merges else None
    return {
        "authored_commit": sha,
        "authored_at": date,
        "authored_subject": subject,
        "merge_commit": merge[0] if merge else "",
        "merged_at": merge[1] if merge else "",
        "merge_subject": merge[2] if merge else "",
    }


@dataclass
class AdopterReading:
    """One adopter's contribution, counted separately so a per-repo zero stays visible."""

    org: str
    ref: str
    claim_files: list[str] = field(default_factory=list)
    items: list[dict[str, Any]] = field(default_factory=list)
    unmapped_claims: list[dict[str, str]] = field(default_factory=list)
    ratified_machine_claims: list[dict[str, str]] = field(default_factory=list)
    signal_rows: int = 0
    unbound_scenarios: int = 0


def read_adopter(repo: Path, org: str, ref: str) -> AdopterReading:
    reading = AdopterReading(org=org, ref=ref)

    tree = git(repo, "ls-tree", "-r", "--name-only", ref).splitlines()

    # -- source A: merged claim files
    claims_prefix = f"twin/orgs/{org}/claims/"
    for path in sorted(p for p in tree if p.startswith(claims_prefix) and p.endswith(".yaml")):
        reading.claim_files.append(path)
        doc = yaml.safe_load(git(repo, "show", f"{ref}:{path}"))
        kind = str(doc.get("kind", ""))
        skill = CLAIM_KIND_TO_SKILL.get(kind, None)
        citation = landed_by(repo, ref, path)
        if skill is None:
            reading.unmapped_claims.append(
                {"path": path, "kind": kind, "why": f"claim kind {kind!r} labels none of the six skills"}
            )
            continue
        if not citation.get("merge_commit"):
            reading.unmapped_claims.append(
                {"path": path, "kind": kind, "why": "on the ref but no merge commit landed it; not a merged claim"}
            )
            continue
        if kind in RATIFIED_MACHINE_KINDS:
            reading.ratified_machine_claims.append(
                {
                    "path": path,
                    "kind": kind,
                    "would_label": skill,
                    "why": (
                        f"a {kind!r} claim carries no `claimed_by` and is written by the heuristic under test; "
                        "merging it is review, not authorship, so it is not a human label"
                    ),
                }
            )
            continue
        reading.items.append(build_item(org, path, doc, skill, citation))

    # -- source B: bound rows in the signal lookup
    if f"twin/signals.yaml" in tree:
        lookup = yaml.safe_load(git(repo, "show", f"{ref}:twin/signals.yaml")) or {}
        reading.signal_rows = len(lookup.get("signals") or [])
        reading.unbound_scenarios = len(lookup.get("unbound_scenarios") or [])

    return reading


def build_item(org: str, path: str, doc: dict[str, Any], skill: str, citation: dict[str, str]) -> dict[str, Any]:
    """One corpus item in the shape `twin/skills.py` `evaluate()` requires: id, input, expected.

    `input` holds only what the skill may see. `expected` holds the human's merged judgement.
    Nothing is invented: every value here is read off the claim file.
    """
    item: dict[str, Any] = {
        "id": f"{org}:{doc.get('id', Path(path).stem)}",
        "skill": skill,
        "source": "merged-claim",
        "cites": citation,
        "path": f"{org}:{path}",
    }
    if skill == "evolution-judge":
        item["input"] = {
            "component": {"id": doc.get("component"), "name": doc.get("component")},
            "evidence": [{"statement": str(doc.get("evidence", "")).strip(), "date": citation.get("authored_at", "")}],
        }
        item["expected"] = {"evolution_position": doc.get("evolution_position")}
        item["evidence_grade"] = doc.get("evidence_grade")
    elif skill == "signal-classify":
        item["input"] = {
            "statement": doc.get("statement"),
            "source": doc.get("source"),
            "candidates": [{"id": doc.get("component"), "name": doc.get("component")}],
        }
        item["expected"] = {"steep": doc.get("steep"), "component": doc.get("component")}
    return item


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--estate", default=".estate-clone", type=Path, help="the estate clone root")
    parser.add_argument("--adopters", nargs="*", default=["driftwood", "ludlow", "tuppence"])
    parser.add_argument("--ref", default="origin/main", help="the ref to read; a merged claim is one on the trunk")
    parser.add_argument("--out", type=Path, default=None, help="write the corpus JSON here")
    args = parser.parse_args()

    readings = []
    for org in args.adopters:
        repo = args.estate / org
        if not (repo / ".git").exists():
            print(f"{org}: no clone at {repo}", file=sys.stderr)
            continue
        readings.append(read_adopter(repo, org, args.ref))

    per_skill = {skill: 0 for skill in SIX_SKILLS}
    items: list[dict[str, Any]] = []
    for reading in readings:
        for item in reading.items:
            per_skill[item["skill"]] += 1
            items.append(item)

    report = {
        "ticket": "laya-loophole/03",
        "ref": args.ref,
        "adopters": [
            {
                "org": r.org,
                "claim_files": r.claim_files,
                "items": len(r.items),
                "unmapped_claims": r.unmapped_claims,
                "ratified_machine_claims": r.ratified_machine_claims,
                "signal_rows_bound": r.signal_rows,
                "unbound_scenarios": r.unbound_scenarios,
            }
            for r in readings
        ],
        "signal_row_verdict": SIGNAL_ROW_VERDICT,
        "items_per_skill": per_skill,
        "total_items": len(items),
        "items": items,
    }

    text = json.dumps(report, indent=2, sort_keys=False)
    if args.out:
        args.out.write_text(text + "\n", encoding="utf-8")

    print(f"ref: {args.ref}")
    for r in readings:
        print(
            f"  {r.org:<10} claim files {len(r.claim_files)}  human-authored items {len(r.items)}  "
            f"ratified machine claims {len(r.ratified_machine_claims)} (excluded)  "
            f"bound signal rows {r.signal_rows} (label none of the six)"
        )
    print("items per skill, from merged HUMAN-AUTHORED claims (overrides only):")
    for skill in SIX_SKILLS:
        print(f"  {skill:<22} {per_skill[skill]}")
    print(f"total: {len(items)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
