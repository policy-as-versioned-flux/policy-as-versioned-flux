"""Actual published hub + genuine FX objects: emission, replay and read-only handoff."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

day = Path(__file__).resolve().parent
hub = day.parents[3]
locator = json.loads((day / "adopter-stage2-isolated.json").read_text())
pin = "5bc47331a536476f3580542be794908f5053f816"
main = "14ec4902bcbd4be58ac43e0ab47d0ea1f4c8250d"
generic = "974e73514e0d8d4cad2e6906acf51d1cc27028b3"
fx = "8c84a66951ce89834f33e008380b2c47f054b7c0"
tag = "fx/v2.0.0"
tag_object = "f6edadce94b98a01479a517a1babda92ce8b2243"
env = {**os.environ, "GITSIGN_REKOR_MODE": "offline"}

def run(argv, cwd=None):
    done = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=180)
    assert done.returncode == 0, (argv, done.returncode, done.stdout, done.stderr)
    return done

published_feeds = hub / ".estate-publish/feeds"
assert run(["git", "-C", str(published_feeds), "rev-parse", tag]).stdout.strip() == tag_object
assert run(["git", "-C", str(published_feeds), "rev-parse", tag + "^{commit}"]).stdout.strip() == fx
proof = run(["gitsign", "verify-tag", tag,
    "--certificate-identity=https://github.com/policy-as-versioned-feeds/feeds/.github/workflows/cut-release.yml@refs/heads/main",
    "--certificate-oidc-issuer=https://token.actions.githubusercontent.com"], published_feeds)
(day / "adopter-stage2-final-fx-signature.log").write_text(proof.stdout + proof.stderr)
run(["git", "-C", str(hub / ".estate-publish/hub"), "merge-base", "--is-ancestor", pin, main])
signature = run(["git", "-C", str(hub / ".estate-publish/hub"), "verify-commit", pin])
result = {"scope": "local real source replay; no live run, source release or activation claimed",
    "hub_commit": pin, "published_hub_main": main, "hub_signature": signature.stderr,
    "generic_feeds_head": generic, "FX_tag": tag, "FX_tag_object": tag_object, "FX_commit": fx,
    "FX_signature_log": str(day / "adopter-stage2-final-fx-signature.log"), "adopters": {}}
for org, loc in locator["adopters"].items():
    feeds = Path(loc["estate"]) / "feeds"
    before = run(["git", "-C", str(feeds), "rev-parse", "HEAD"]).stdout.strip()
    run(["git", "-C", str(feeds), "fetch", str(published_feeds), f"refs/tags/{tag}:refs/tags/{tag}"])
    assert run(["git", "-C", str(feeds), "rev-parse", "HEAD"]).stdout.strip() == before == generic
    assert run(["git", "-C", str(feeds), "rev-parse", tag]).stdout.strip() == tag_object
    assert run(["git", "-C", str(feeds), "rev-parse", tag + "^{commit}"]).stdout.strip() == fx

with tempfile.TemporaryDirectory(prefix="pavf-stage2-final-producer-") as temporary:
    clean = Path(temporary) / "hub"
    run(["git", "clone", "--no-hardlinks", "--no-checkout", str(hub / ".estate-publish/hub"), str(clean)])
    run(["git", "-C", str(clean), "checkout", "--detach", pin])
    copies = clean / ".estate-clone"
    copies.mkdir(exist_ok=True)
    feeds = copies / "feeds"
    run(["git", "clone", "--no-hardlinks", str(published_feeds), str(feeds)])
    run(["git", "-C", str(feeds), "checkout", "--detach", fx])
    for org, loc in locator["adopters"].items():
        source = Path(loc["dir"])
        copy = copies / org
        shutil.copytree(source, copy, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        assert f"hub_commit: {pin}" in (copy / "twin/PIN.yaml").read_text()
        old_v1 = (source / "twin/forward-intel/v1/feed.json")
        before_v1 = hashlib.sha256(old_v1.read_bytes()).hexdigest() if old_v1.exists() else None
        emitted = run([sys.executable, str(copy / "twin/emit-forward-intel.py")], clean)
        checked = run([sys.executable, str(copy / "twin/emit-forward-intel.py"), "--check"], clean)
        assert "byte-identical" in checked.stdout
        paths = []
        for generated in (copy / "twin/forward-intel").glob("v*/feed.json"):
            relative = generated.relative_to(copy)
            target = source / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(generated, target)
            paths.append({"path": str(relative), "sha256": hashlib.sha256(target.read_bytes()).hexdigest()})
        if org == "driftwood":
            assert hashlib.sha256(old_v1.read_bytes()).hexdigest() == before_v1
        current = json.loads((copy / f"twin/forward-intel/v{'2' if org == 'driftwood' else '1'}/feed.json").read_text())
        body = current["payload"]
        assert body["rests_on_grade"] == 3
        borrowed = next(d for d in body["derived_from"] if d["party"] == "feeds")
        assert borrowed["version"] == "4" and borrowed["name"] == "threat-register"
        if org == "ludlow":
            reading = body["valuation"]
            assert reading["native_currency"] == "USD" and abs(reading["native_amount"] - 8475000000) < 1
            assert reading["fx"]["period"] == "2025-12"
            assert reading["fx"]["valuation_date"] == "2025-12-31"
            assert reading["fx"]["version"] == "2.0.0" and reading["fx"]["from_rate"] == 1.3126
            assert abs(reading["amount"] - 8475000000 / 1.3126) < 1
        else:
            assert body["valuation"]["native_currency"] == "GBP" and body["valuation"]["fx"] is None
        line = None
        observer = copy / ".github/scripts/twin-sweep.py"
        if observer.exists():
            handoff = Path(temporary) / f"{org}-handoff"
            run([sys.executable, str(observer), "record",
                "--adopter-dir", str(copy), "--at", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "--run-id", "local-source-rehearsal", "--hub-ref", pin,
                "--adopter-ref", run(["git", "-C", str(source), "rev-parse", "HEAD"]).stdout.strip(),
                "--handoff", str(handoff)], clean)
            line = json.loads((handoff / "observation.jsonl").read_text())
            assert line["status"] == "unchanged" and line["emitter_exit"] == 0 and line["moved"] is False
            assert sorted(p.name for p in handoff.iterdir()) == ["observation.jsonl"]
        (day / f"{org}-stage2-final-producer.log").write_text(emitted.stdout + emitted.stderr + checked.stdout + checked.stderr)
        result["adopters"][org] = {"emit_exit": 0, "check_exit": 0, "byte_exact": True,
            "generated": paths, "published_at": current["published_at"], "valuation": body["valuation"],
            "rests_on_grade": body["rests_on_grade"], "borrowed_frequency": borrowed,
            "read_only_observer": line, "immutable_driftwood_v1_preserved": org != "driftwood" or before_v1 == hashlib.sha256(old_v1.read_bytes()).hexdigest()}
        (day / "adopter-stage2-final-producers.json").write_text(json.dumps(result, indent=2) + "\n")
        print(f"{org}: actual clean published hub producer emit/check PASS; handoff {'PASS' if line else 'not this producer clock'}")
    run(["git", "-C", str(feeds), "checkout", "--detach", generic])
    rerun = run([sys.executable, str(copies / "ludlow/twin/emit-forward-intel.py"), "--check"], clean)
    assert "byte-identical" in rerun.stdout
    result["Ludlow_generic_HEAD974_with_real_FX2_objects_byte_replay"] = True
    result["clean_hub_tracked_tree_unchanged"] = not run(["git", "-C", str(clean), "status", "--porcelain", "--untracked-files=no"]).stdout.strip()
(day / "adopter-stage2-final-producers.json").write_text(json.dumps(result, indent=2) + "\n")
