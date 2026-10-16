"""Pin the executable reviewer and its thin callers at the credential boundary.

These tests use temporary source copies, an isolated ZIP application and synthetic
credentials. They do not mint real credentials or publish fixture observations.
"""
from __future__ import annotations

import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
from types import SimpleNamespace
import zipfile

import pytest
import yaml

from talk import build_observation_delivery as builder
from talk import render_observation_delivery as renderer

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA = "1234567890abcdef1234567890abcdef12345678"
BUNDLE_SHA = "abcdef0123456789" * 4
ORGS = ("driftwood", "tuppence", "ludlow")
SOURCES = {
    "observation_delivery.py": "talk/observation_delivery.py",
    "delivery_enact_record.py": "verify/enact-record/enact_record.py",
    "delivery_other_hand.py": "twin/other_hand.py",
}


def copy_sources(root):
    for path in SOURCES.values():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / path).read_bytes())


def run_python(*args, cwd):
    # -I keeps caller cwd/PYTHONPATH out of imports. The bundled helpers must work
    # without a hub checkout on sys.path, just as they do in adopter Actions.
    return subprocess.run([sys.executable, "-I", *map(str, args)], cwd=cwd,
                          capture_output=True, text=True, timeout=30)


def test_bundle_has_only_fixed_reviewed_sources_and_exact_manifest(tmp_path):
    copy_sources(tmp_path)
    data = builder.build(tmp_path)
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        assert archive.namelist() == sorted([*SOURCES, "SOURCE.json", "__main__.py"])
        manifest = json.loads(archive.read("SOURCE.json"))
        assert set(manifest) == set(SOURCES)
        for name, source in SOURCES.items():
            original = (ROOT / source).read_bytes()
            assert archive.read(name) == original
            assert manifest[name] == {"source": source, "sha256": hashlib.sha256(original).hexdigest()}
        assert archive.read("__main__.py") == (
            b"from observation_delivery import main\nraise SystemExit(main())\n")
        for entry in archive.infolist():
            assert entry.compress_type == zipfile.ZIP_STORED
            assert entry.date_time == (1980, 1, 1, 0, 0, 0)
            assert entry.create_system == 3
            assert entry.external_attr >> 16 == 0o100644
            assert entry.comment == entry.extra == b""
        assert archive.comment == b""


def test_bundle_ignores_source_filesystem_metadata_and_unlisted_files(tmp_path):
    copy_sources(tmp_path)
    first = builder.build(tmp_path)
    for index, path in enumerate(SOURCES.values()):
        source = tmp_path / path
        source.chmod(0o700)
        os.utime(source, (1000000000 + index, 1700000000 + index))
    (tmp_path / "talk/unreviewed.py").write_text("raise RuntimeError('must not bundle')\n")
    assert builder.build(tmp_path) == first == builder.build(tmp_path)


@pytest.mark.parametrize("source", list(SOURCES.values()))
def test_each_trusted_source_changes_bundle_and_its_manifest(tmp_path, source):
    copy_sources(tmp_path)
    before = builder.build(tmp_path)
    path = tmp_path / source
    path.write_bytes(path.read_bytes() + b"\n# synthetic source change\n")
    after = builder.build(tmp_path)
    assert hashlib.sha256(after).digest() != hashlib.sha256(before).digest()
    with zipfile.ZipFile(io.BytesIO(after)) as archive:
        member = next(name for name, value in SOURCES.items() if value == source)
        assert json.loads(archive.read("SOURCE.json"))[member]["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()


def test_builder_cli_detects_missing_stale_and_corrupt_output(tmp_path):
    copy_sources(tmp_path)
    script = tmp_path / "talk/build_observation_delivery.py"
    script.write_bytes((ROOT / "talk/build_observation_delivery.py").read_bytes())
    output = tmp_path / "talk/observation-delivery.pyz"
    missing = run_python(script, "--check", cwd=tmp_path)
    assert missing.returncode != 0 and "bundle is stale" in missing.stderr
    built = run_python(script, cwd=tmp_path)
    assert built.returncode == 0, built.stderr
    assert built.stdout == hashlib.sha256(output.read_bytes()).hexdigest() + "  observation-delivery.pyz\n"
    checked = run_python(script, "--check", cwd=tmp_path)
    assert checked.returncode == 0 and checked.stdout == built.stdout
    original = output.read_bytes()
    output.write_bytes(original + b"unexpected trailing payload")
    assert run_python(script, "--check", cwd=tmp_path).returncode != 0
    output.write_bytes(original)
    source = tmp_path / "twin/other_hand.py"
    source.write_bytes(source.read_bytes() + b"\n# changed mint source\n")
    stale = run_python(script, "--check", cwd=tmp_path)
    assert stale.returncode != 0 and "bundle is stale" in stale.stderr
    assert output.read_bytes() == original  # A check never silently rebuilds.


def test_zip_application_help_and_refusal_need_no_source_checkout(tmp_path):
    bundle = tmp_path / "reviewer.pyz"
    bundle.write_bytes(builder.build())
    isolated = tmp_path / "isolated"
    isolated.mkdir()
    # An accidental import from a checkout would fail loudly; -I also proves
    # neither cwd nor an inherited PYTHONPATH is needed for bundled execution.
    for package in ("talk", "twin"):
        (isolated / package).mkdir()
        (isolated / package / "__init__.py").write_text("raise RuntimeError('untrusted checkout executed')\n")
    help_result = run_python(bundle, "--help", cwd=isolated)
    assert help_result.returncode == 0, help_result.stderr
    for option in ("--repository", "--workflow", "--run-id", "--attempt", "--authority-root", "--check-only", "--mint"):
        assert option in help_result.stdout
    refused = run_python(bundle, "--run-id", "100", "--attempt", "1",
                         "--repository", "foreign/repository", "--workflow", "twin-sweep",
                         "--root", isolated, "--check-only", cwd=isolated)
    assert refused.returncode == 1
    assert "PENDING: no trusted observation profile" in refused.stderr
    assert "Traceback" not in refused.stderr and "untrusted checkout executed" not in refused.stderr


def test_zip_application_imports_exact_bundled_helpers_without_checkout(tmp_path):
    bundle = tmp_path / "reviewer.pyz"
    bundle.write_bytes(builder.build())
    source = """
import datetime as dt, json, pathlib, sys
sys.path.insert(0, sys.argv[1])
import observation_delivery as controller
import delivery_other_hand as mint
import delivery_enact_record as enact
root = pathlib.Path(sys.argv[2])
controller.window(root, dt.date(2026, 10, 17))
print(json.dumps([controller.__file__, enact.__file__, mint.__file__]))
"""
    authority = tmp_path / "authority"
    (authority / "twin").mkdir(parents=True)
    (authority / "twin/ENACT_MODE").write_text("development\n")
    (authority / "owner.md").write_text('2026-09-24, owner: "agree".\n')
    (authority / "twin/ENACT_MODE.why").write_text(
        "mode: development\nuntil: '2026-10-22'\nsaid:\n"
        "  - on: '2026-09-24'\n    by: owner\n    words: agree\n    where: owner.md\n")
    result = run_python("-c", source, bundle, authority, cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    origins = json.loads(result.stdout)
    assert origins == [str(bundle) + "/" + member for member in SOURCES]


@pytest.mark.parametrize("org", ORGS)
def test_rendered_caller_is_immutable_default_branch_code_with_closed_interface(org):
    text = renderer.render(org, SOURCE_SHA, BUNDLE_SHA)
    workflow = yaml.load(text, Loader=yaml.BaseLoader)
    assert "@ORG@" not in text and "@SOURCE_SHA@" not in text and "@BUNDLE_SHA256@" not in text
    assert set(workflow["on"]) == {"workflow_run", "workflow_dispatch"}
    assert workflow["on"]["workflow_run"] == {"workflows": ["drift-sample", "twin-sweep"], "types": ["completed"]}
    inputs = workflow["on"]["workflow_dispatch"]["inputs"]
    assert set(inputs) == {"workflow", "run_id", "attempt"}
    assert inputs["workflow"]["options"] == ["drift-sample", "twin-sweep"]
    assert all(value["required"] == "true" for value in inputs.values())
    assert workflow["permissions"] == {"contents": "read", "actions": "read", "pull-requests": "read"}
    assert workflow["concurrency"]["cancel-in-progress"] == "false"
    assert "workflow_run.id || inputs.run_id" in workflow["concurrency"]["group"]
    assert "workflow_run.run_attempt || inputs.attempt" in workflow["concurrency"]["group"]
    assert set(workflow["jobs"]) == {"review"}
    job = workflow["jobs"]["review"]
    assert job["environment"] == "observation-delivery"
    assert "github.ref_name == github.event.repository.default_branch" in job["if"]
    assert "github.event.workflow_run.head_repository.full_name == github.repository" in job["if"]
    assert "github.event.workflow_run.head_branch == github.event.repository.default_branch" in job["if"]
    assert job["env"]["DELIVERY_REPOSITORY"] == f"policy-as-versioned-{org}/{org}"
    assert job["env"]["DELIVERY_SOURCE"] == SOURCE_SHA
    assert job["env"]["DELIVERY_SHA256"] == BUNDLE_SHA
    steps = job["steps"]
    actions = [step for step in steps if "uses" in step]
    assert [step["uses"].split("@")[0] for step in actions] == ["actions/checkout", "actions/setup-python"]
    assert all(re.fullmatch(r"[^@]+@[0-9a-f]{40}", step["uses"]) for step in actions)
    assert actions[0]["with"] == {"ref": "${{ github.event.repository.default_branch }}", "fetch-depth": "0", "persist-credentials": "false"}
    assert "download-artifact" not in text and "upload-artifact" not in text
    assert "workflow_run.head_sha" not in actions[0]["with"]["ref"]
    assert not any("secrets." in str(value) for value in job["env"].values())
    secret_steps = [index for index, step in enumerate(steps) if "secrets." in str(step)]
    assert secret_steps == [len(steps) - 1]
    install, preflight, writer = steps[-3:]
    assert "pyyaml==6.0.3 --hash=sha256:" in install["run"]
    assert "pip install --require-hashes --only-binary=:all:" in install["run"]
    assert "/${DELIVERY_SOURCE}/talk/observation-delivery.pyz" in install["run"]
    assert install["run"].count("sha256sum --check --strict") == 2
    assert '"$DELIVERY_SHA256" "$RUNNER_TEMP/observation-delivery.pyz"' in install["run"]
    assert '"$GITSIGN_SHA256" "$RUNNER_TEMP/delivery-gitsign"' in install["run"]
    assert job["env"]["GITSIGN_VERSION"] == "0.17.1"
    assert job["env"]["GITSIGN_SHA256"] == "69213a8a0813a151e5a47d0060862952ff833a845d57309dff76f7ba6600abae"
    assert preflight["env"] == {"GH_TOKEN": "${{ github.token }}"}
    assert writer["env"] == {"PAVC_OTHER_HAND_PRIVATE_KEY": "${{ secrets.PAVC_OTHER_HAND_PRIVATE_KEY }}",
                              "TRUTH_READ_TOKEN": "${{ github.token }}"}
    for step in (preflight, writer):
        command = step["run"]
        assert 'python3 "$RUNNER_TEMP/observation-delivery.pyz"' in command
        for flag, value in (("repository", "DELIVERY_REPOSITORY"), ("workflow", "DELIVERY_WORKFLOW"),
                            ("run-id", "DELIVERY_RUN_ID"), ("attempt", "DELIVERY_ATTEMPT")):
            assert f'--{flag} "${value}"' in command
        assert '--root "$GITHUB_WORKSPACE" --authority-root "$RUNNER_TEMP/delivery-authority"' in command
    assert preflight["run"].rstrip().endswith("--check-only")
    assert writer["run"].rstrip().endswith("--mint")


@pytest.mark.parametrize("org", ["platform", "driftwood/../../escape", "", "DRIFTWOOD", "nist"])
def test_renderer_refuses_unregistered_adopter(org):
    with pytest.raises(ValueError, match="no trusted adopter profile"):
        renderer.render(org, SOURCE_SHA, BUNDLE_SHA)


@pytest.mark.parametrize("source,bundle", [
    ("main", BUNDLE_SHA), (SOURCE_SHA[:-1], BUNDLE_SHA), (SOURCE_SHA.upper(), BUNDLE_SHA),
    (SOURCE_SHA + "\n", BUNDLE_SHA), (SOURCE_SHA, "latest"), (SOURCE_SHA, BUNDLE_SHA[:-1]),
    (SOURCE_SHA, BUNDLE_SHA.upper()), (SOURCE_SHA, BUNDLE_SHA + "\n"),
])
def test_renderer_refuses_moving_malformed_or_injected_pins(source, bundle):
    with pytest.raises(ValueError, match="exact source commit and bundle SHA256"):
        renderer.render("driftwood", source, bundle)


def test_renderer_cli_outputs_exact_reviewed_template(tmp_path):
    output = tmp_path / "delivery.yml"
    result = run_python(ROOT / "talk/render_observation_delivery.py", "--org", "ludlow",
                        "--source-sha", SOURCE_SHA, "--bundle-sha256", BUNDLE_SHA,
                        "--output", output, cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert output.read_text() == renderer.render("ludlow", SOURCE_SHA, BUNDLE_SHA)


@pytest.fixture
def mint_boundary(monkeypatch, tmp_path):
    module = importlib.import_module("talk.observation_delivery")
    events, paths = [], []
    key, jwt, token = "synthetic private key\n", "synthetic.jwt", "synthetic-writer-token"
    monkeypatch.setenv("PAVC_OTHER_HAND_PRIVATE_KEY", key)
    monkeypatch.setenv("RUNNER_TEMP", str(tmp_path))
    monkeypatch.setenv("GH_TOKEN", "ambient-writer")
    monkeypatch.setenv("GITHUB_TOKEN", "ambient-default")
    monkeypatch.setenv("TRUTH_READ_TOKEN", "synthetic-reader")

    def print_mask(value, **kwargs):
        assert kwargs == {"flush": True}
        events.append(("mask", value))

    def app_jwt(app_id, path):
        assert app_id == "4819564"
        assert "PAVC_OTHER_HAND_PRIVATE_KEY" not in os.environ
        assert path.parent == tmp_path and path.read_text() == key
        assert stat.S_IMODE(path.stat().st_mode) == 0o600
        paths.append(path)
        events.append(("jwt",))
        return jwt

    def installation_for_org(value, org):
        assert value == jwt and "PAVC_OTHER_HAND_PRIVATE_KEY" not in os.environ
        assert events[-1] == ("mask", "::add-mask::" + jwt)
        events.append(("installation", org))
        return 42

    def http(method, path, bearer, body):
        assert method == "POST" and path == "/app/installations/42/access_tokens"
        assert bearer == jwt and "PAVC_OTHER_HAND_PRIVATE_KEY" not in os.environ
        assert ("mask", "::add-mask::" + jwt) in events
        events.append(("token", body))
        return {"token": token}

    helper = SimpleNamespace(app_jwt=app_jwt, installation_for_org=installation_for_org, _http=http)
    monkeypatch.setitem(sys.modules, "delivery_other_hand", helper)
    monkeypatch.setattr(module, "print", print_mask, raising=False)
    return module, helper, events, paths, token


@pytest.mark.parametrize("org", ORGS)
def test_mint_is_repository_only_without_actions_or_extra_key_environment(mint_boundary, monkeypatch, org):
    module, _, events, paths, token = mint_boundary
    profile = module.select_profile(f"policy-as-versioned-{org}/{org}", "drift-sample")
    module.mint_for(profile)
    assert events == [("jwt",), ("mask", "::add-mask::synthetic.jwt"),
                      ("installation", f"policy-as-versioned-{org}"),
                      ("token", {"repositories": [org], "permissions": {"contents": "write", "pull_requests": "write"}}),
                      ("mask", "::add-mask::" + token)]
    assert len(paths) == 1 and not paths[0].exists()
    assert "PAVC_OTHER_HAND_PRIVATE_KEY" not in os.environ
    assert os.environ["GH_TOKEN"] == token

    def child(command, **kwargs):
        assert events[-1] == ("mask", "::add-mask::" + token)
        assert not paths[0].exists()
        env = kwargs["env"]
        assert all(name not in env for name in ("GITHUB_TOKEN", "TRUTH_READ_TOKEN", "PAVC_OTHER_HAND_PRIVATE_KEY"))
        assert env["GH_TOKEN"] == ("synthetic-reader" if command[3] == "GET" else token)
        return SimpleNamespace(returncode=0, stdout='{"fixture": true}')

    monkeypatch.setattr(module.subprocess, "run", child)
    assert module.github_api("GET", "repos/fixture") == {"fixture": True}
    assert module.github_api("POST", "repos/fixture/pulls/1/reviews", {"event": "APPROVE"}) == {"fixture": True}


@pytest.mark.parametrize("failure", ["sign", "installation", "http", "empty-token"])
def test_mint_failure_removes_environment_key_and_temp_file(mint_boundary, monkeypatch, failure):
    module, helper, events, paths, _ = mint_boundary

    def fail(*args, **kwargs):
        if failure == "sign":
            paths.append(args[1])
        raise RuntimeError("synthetic sensitive transport body")

    if failure == "empty-token":
        helper._http = lambda *args: {"token": ""}
    else:
        monkeypatch.setattr(helper, {"sign": "app_jwt", "installation": "installation_for_org", "http": "_http"}[failure], fail)
    with pytest.raises(module.Refusal, match="could not mint.*narrow writer token") as caught:
        module.mint_for(module.select_profile("policy-as-versioned-tuppence/tuppence", "twin-sweep"))
    assert "sensitive transport body" not in str(caught.value)
    assert "PAVC_OTHER_HAND_PRIVATE_KEY" not in os.environ
    assert paths and all(not path.exists() for path in paths)
    assert os.environ["GH_TOKEN"] == "ambient-writer"
    assert ("mask", "::add-mask::synthetic-writer-token") not in events


def test_mint_does_not_fall_back_to_local_key_without_environment_key(mint_boundary, monkeypatch):
    module, _, events, paths, _ = mint_boundary
    monkeypatch.delenv("PAVC_OTHER_HAND_PRIVATE_KEY")
    with pytest.raises(module.Refusal, match="environment has no App key"):
        module.mint_for(module.select_profile("policy-as-versioned-ludlow/ludlow", "twin-sweep"))
    assert events == paths == []


@pytest.mark.parametrize("mode", ["--check-only", "--mint"])
def test_cli_repeats_validation_after_mint_and_never_mints_for_check_only(monkeypatch, tmp_path, capsys, mode):
    module = importlib.import_module("talk.observation_delivery")
    calls = []
    repository = "policy-as-versioned-driftwood/driftwood"
    authority = tmp_path / "authority"
    monkeypatch.setattr(sys, "argv", ["observation-delivery.pyz", "--repository", repository,
                                    "--workflow", "twin-sweep", "--run-id", "100", "--attempt", "2",
                                    "--root", str(tmp_path), "--authority-root", str(authority), mode])

    def deliver(root, run_id, **options):
        assert root == tmp_path and run_id == 100
        assert options == {"repository": repository, "workflow": "twin-sweep", "attempt": 2,
                           "authority_root": authority, "check_only": options["check_only"]}
        calls.append(("validate", options["check_only"]))
        return "PENDING verified original" if options["check_only"] else "RECORDED original"

    monkeypatch.setattr(module, "deliver", deliver)
    monkeypatch.setattr(module, "mint_for", lambda profile: calls.append(("mint", profile.repository)))
    assert module.main() == 0
    if mode == "--check-only":
        assert calls == [("validate", True)]
        assert capsys.readouterr().out == "PENDING verified original\n"
    else:
        assert calls == [("validate", True), ("mint", repository), ("validate", False)]
        assert capsys.readouterr().out == "RECORDED original\n"


def test_cli_refused_preflight_never_calls_minter_or_writer(monkeypatch, tmp_path, capsys):
    module = importlib.import_module("talk.observation_delivery")
    checks = []
    monkeypatch.setattr(sys, "argv", ["observation-delivery.pyz", "--repository",
                                    "policy-as-versioned-tuppence/tuppence", "--workflow", "drift-sample",
                                    "--run-id", "100", "--attempt", "1", "--root", str(tmp_path),
                                    "--authority-root", str(tmp_path / "authority"), "--mint"])

    def refused(*args, **kwargs):
        assert kwargs["check_only"] is True
        checks.append("preflight")
        raise module.Refusal("synthetic invalid signature")

    def forbidden(*args, **kwargs):
        pytest.fail("a refused read-only preflight must not reach the mint helper")

    monkeypatch.setattr(module, "deliver", refused)
    monkeypatch.setattr(module, "mint_for", forbidden)
    assert module.main() == 1
    assert checks == ["preflight"]
    assert capsys.readouterr().err == "PENDING: synthetic invalid signature\n"


@pytest.mark.parametrize("instrument", ["git", "gitsign"])
def test_initial_preflight_instruments_never_inherit_environment_key_or_tokens(monkeypatch, tmp_path, instrument):
    module = importlib.import_module("talk.observation_delivery")
    for name in ("PAVC_OTHER_HAND_PRIVATE_KEY", "GH_TOKEN", "GITHUB_TOKEN", "TRUTH_READ_TOKEN"):
        monkeypatch.setenv(name, "synthetic-" + name)
    calls = []

    def child(command, **kwargs):
        calls.append(command)
        assert command[0] == instrument
        assert all(name not in kwargs["env"] for name in
                   ("PAVC_OTHER_HAND_PRIVATE_KEY", "GH_TOKEN", "GITHUB_TOKEN", "TRUTH_READ_TOKEN"))
        return SimpleNamespace(returncode=0, stdout=b"")

    monkeypatch.setattr(module.subprocess, "run", child)
    if instrument == "git":
        assert module.git(tmp_path, "rev-parse", "HEAD") == ""
    else:
        assert module.verify_signature(tmp_path, "a" * 40,
                                       {"head_sha": "b" * 40, "event": "schedule"}, "main") is None
    assert len(calls) == 1
    # The writer's later mint still has the key; only untrusted child inheritance
    # is removed during the first read-only validation.
    assert os.environ["PAVC_OTHER_HAND_PRIVATE_KEY"] == "synthetic-PAVC_OTHER_HAND_PRIVATE_KEY"
