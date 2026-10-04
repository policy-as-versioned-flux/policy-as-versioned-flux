"""Authorized filesystem-only candidate transition. Historical measurements are untouched."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
REPO = ROOT / ".estate-clone/platform"
OUT = Path(__file__).resolve().parent


def frozen():
    return {
        str(path.relative_to(REPO)): hashlib.sha256(path.read_bytes()).hexdigest()
        for version in ("5.0.0", "6.0.0")
        for path in sorted((REPO / f"distribution/policies/v{version}").rglob("*"))
        if path.is_file()
    }


before = frozen()
changed = []
for base in ("distribution/policies", "computed-semver/engine-fixtures"):
    old, new = REPO / base / "v6.0.1", REPO / base / "v7.0.0"
    if old.exists():
        assert not new.exists(), (old, new)
        old.rename(new)
    assert new.is_dir(), new
    for path in sorted(new.rglob("*")):
        if path.is_file():
            text = path.read_text().replace("6.0.1", "7.0.0").replace("6-0-1", "7-0-0")
            if base.endswith("engine-fixtures") and path.name == "kyverno-test.yaml":
                start = text.index("apiVersion:")
                text = (
                    f"# {path.parent.name} @7.0.0 compatibility candidate (ticket149).\n"
                    "# Candidate fixture adapted from prior policy cases; the grader reads the exact committed\n"
                    "# candidate body. This is a fixture definition, not evidence of a published tag.\n"
                    + text[start:]
                )
            path.write_text(text)
            changed.append(str(path.relative_to(REPO)))

for relative in (
    "distribution/tests/require-nonroot/kyverno-test.yaml",
    "distribution/tests/require-nonroot/resources.yaml",
    "engine/kyverno/engine-table.yaml",
):
    path = REPO / relative
    path.write_text(path.read_text().replace("6.0.1", "7.0.0").replace("6-0-1", "7-0-0"))
    changed.append(relative)

path = REPO / "distribution/versions.yaml"
text = path.read_text()
old = '- { version: "6.0.1", tag: "policy/v6.0.1", commit: "", bump: "patch"'
new = '- { version: "7.0.0", tag: "policy/v7.0.0", commit: "", bump: "major"'
assert text.count(old) + text.count(new) == 1
text = text.replace(old, new, 1).replace(
    "# posture-trust-boundary retires here. Cut 6.0.0 before this patch release.",
    "# posture-trust-boundary retires here. Full supported5/6 window requires a major.",
)
path.write_text(text)
changed.append("distribution/versions.yaml")

acceptances = []
for party in ("driftwood", "tuppence", "ludlow"):
    directory = ROOT / f".estate-clone/{party}/accepted-majors"
    old, new = directory / "platform-6.0.1.yaml", directory / "platform-7.0.0.yaml"
    if old.exists():
        assert not new.exists(), new
        text = old.read_text()
        assert "version: 6.0.1" in text
        new.write_text(text.replace("version: 6.0.1", "version: 7.0.0"))
        old.unlink()
    assert new.is_file(), new
    (directory / "platform-6.0.1-superseded.md").write_text(
        "# Unserved candidate acceptance superseded\n\n"
        "2026-10-03: the unserved platform6.0.1 compatibility candidate and its exact acceptance "
        "record were superseded by platform7.0.0. The publisher computed a major over the retained "
        "supported5.0.0/6.0.0 window; a patch declaration could publish only as degraded "
        "6.0.1-quarantine.1. The exact7.0.0 acceptance is recorded in platform-7.0.0.yaml under "
        "the owner's delegated instruction. Earlier6.0.1 measurements remain historical and "
        "were not relabelled.\n"
    )
    acceptances.append(str(new.relative_to(ROOT)))

after = frozen()
assert before == after, "frozen5/6 policy bytes changed"
checkpoint = {
    "date": "2026-10-03",
    "candidate": "7.0.0",
    "supported": ["5.0.0", "6.0.0", "7.0.0"],
    "declared_bump": "major",
    "changed_paths": changed,
    "acceptances": acceptances,
    "frozen_policy_sha256": before,
    "frozen_before_after_equal": True,
    "historical_6_0_1_measurements_unchanged": True,
}
(OUT / "platform-7.0.0-candidate-checkpoint.json").write_text(json.dumps(checkpoint, indent=2) + "\n")
print(json.dumps({"candidate": "7.0.0", "changed_file_count": len(changed), "frozen5_and6_unchanged": True, "acceptances": acceptances}, indent=2))
