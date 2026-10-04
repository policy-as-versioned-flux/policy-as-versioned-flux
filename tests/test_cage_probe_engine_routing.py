"""Ticket 150: each public adopter probe selects its own declared CLI."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess

import pytest
import yaml

HUB = Path(__file__).resolve().parents[1]
ESTATE = HUB / ".estate-clone"


def binaries() -> dict[str, Path]:
    directory = os.environ.get("KYVERNO_ENGINE_DIR")
    if not directory:
        pytest.skip("declared-engine routing proof needs the installed engine-table binaries")
    assert directory is not None
    found = {v: Path(directory) / v / "kyverno" for v in ("1.18.2", "1.19.1")}
    if not all(p.is_file() for p in found.values()):
        pytest.skip("both exact engine-table binaries are required for the routing proof")
    return found


def probe(repo: Path, engine_dir: Path) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ, KYVERNO_ENGINE_DIR=str(engine_dir))
    env.pop("KYVERNO_CLI", None)
    return subprocess.run(["bash", str(repo / "verify-cage-probe.sh")], env=env,
                          capture_output=True, text=True, timeout=120)


@pytest.mark.parametrize("adopter", ["driftwood", "tuppence", "ludlow"])
@pytest.mark.parametrize("version", ["1.18.2", "1.19.1"])
def test_the_public_probe_selects_the_declared_binary(adopter: str, version: str, tmp_path: Path):
    installed = binaries()
    source = ESTATE / adopter
    repo = tmp_path / adopter
    repo.mkdir()
    shutil.copy(source / "verify-cage-probe.sh", repo)
    shutil.copy(source / "party.yaml", repo)
    for directory in ("drift", "scripts", "gitops", "composed"):
        shutil.copytree(source / directory, repo / directory)
    declaration = repo / "gitops/engine/kyverno.yaml"
    doc = yaml.safe_load(declaration.read_text())
    table = yaml.safe_load((ESTATE / "platform/engine/kyverno/engine-table.yaml").read_text())
    row = next(r for r in table["versions"] if r["version"] == version)
    doc.update(version=version, install={k: row["install"][k] for k in ("url", "sha256")},
               cli={"linux_x86_64": row["cli"]["linux_x86_64"]})
    declaration.write_text(yaml.safe_dump(doc))
    engines = tmp_path / "engines"
    for value, binary in installed.items():
        (engines / value).mkdir(parents=True)
        (engines / value / "kyverno").symlink_to(binary)
    run = probe(repo, engines)
    output = run.stdout + run.stderr
    # The fixture has no repository tags, so the later document proof cannot run.
    assert run.returncode == 3, output
    assert f"ok  kyverno CLI {version} is the engine" in output, output
    assert "the pinned composed tag" in output and "is not present" in output, output


@pytest.mark.parametrize("available", [False, True])
def test_a_missing_or_misidentified_declared_binary_never_uses_path(available: bool, tmp_path: Path):
    installed = binaries()
    engines = tmp_path / "engines"
    if available:
        (engines / "1.18.2").mkdir(parents=True)
        (engines / "1.18.2/kyverno").symlink_to(installed["1.19.1"])
    run = probe(ESTATE / "ludlow", engines)
    output = run.stdout + run.stderr
    assert run.returncode == 3, output
    assert ("the two differ" if available else "no declared kyverno CLI at") in output, output
