"""Measure committed source A window change through each institution's normal gate."""
import json
from pathlib import Path
import subprocess
import sys
import yaml

day = Path(__file__).resolve().parent
rows = json.loads((day / "adopter-source-A-ci-repaired-candidates.json").read_text())
results = {}
for org, row in rows.items():
    repo = Path(row["directory"])
    gate = repo / ".github/scripts" / ("adopter_gate.py" if org == "ludlow" else "adopter-gate.py")
    out = day / f"{org}-source-A-ci-repaired-grade.json"
    md = day / f"{org}-source-A-ci-repaired-grade.md"
    if org == "driftwood":
        argv = [sys.executable, str(gate), "compose", str(repo.parent / "platform"),
                "v3.0.1", "UNRELEASED-SOURCE-A", "--adopter-dir", str(repo),
                "--base-ref", row["base"], "--head-ref", row["head"],
                "--out", str(out), "--markdown-out", str(md)]
    elif org == "tuppence":
        old_pin = day / "tuppence-stage2-final-source-A-old-platform-pin.yaml"
        old_pin.write_bytes(subprocess.check_output(["git", "-C", str(repo), "show",
                                                    f"{row['base']}:gitops/platform/platform-pin.yaml"]))
        env = yaml.safe_load((repo / ".github/workflows/shift-left.yml").read_text())["env"]
        argv = [sys.executable, str(gate), "--platform-dir", str(repo.parent / "platform"),
                "--new-pin-yaml", str(repo / "gitops/platform/platform-pin.yaml"),
                "--old-pin-yaml", str(old_pin),
                "--identity-regexp", env["EVIDENCE_EXPECTED_IDENTITY_REGEXP"],
                "--issuer", env["EXPECTED_ISSUER"], "--adopter-dir", str(repo),
                "--base-ref", row["base"], "--head-ref", row["head"], "--out", str(out)]
    else:
        argv = [sys.executable, str(gate), "--platform-dir", str(repo.parent / "platform"),
                "--ludlow-dir", str(repo), "--old-ref", row["base"], "--new-ref", row["head"],
                "--composed-base-ref", row["base"], "--composed-head-ref", row["head"],
                "--out-comment", str(md)]
    proc = subprocess.run(argv, capture_output=True, text=True)
    (day / f"{org}-source-A-ci-repaired-grade.log").write_text(proc.stdout + proc.stderr)
    assert proc.returncode == 0, (org, proc.stdout, proc.stderr)
    if org == "driftwood":
        evidence = json.loads(out.read_text())
        result = evidence["result"]
        assert result["composed_bump"] == "major", (org, result)
        assert result["acceptance"]["admitted"] is True, (org, result)
    elif org == "tuppence":
        result = json.loads(out.read_text())
        assert result["composed"] == "major", (org, result)
        assert result["acceptance"]["admitted"] is True, (org, result)
    else:
        assert "composed=major, admitted:" in proc.stdout, proc.stdout
        result = {"composed_bump": "major", "acceptance_admitted": True,
                  "normal_gate_stdout": proc.stdout, "rendered_grade": str(md)}
        out.write_text(json.dumps(result, indent=2) + "\n")
    results[org] = {"head": row["head"], "base": row["base"], "argv": argv, "exit": proc.returncode,
                    "result": result, "grade": str(out),
                    "prospective_release": "v4.0.0", "remote_unused_check": "required before normal cut",
                    "publication_hold": row["publication_hold"]}
(day / "adopter-source-A-ci-repaired-grades.json").write_text(json.dumps(results, indent=2) + "\n")
print(json.dumps(results, indent=2))
