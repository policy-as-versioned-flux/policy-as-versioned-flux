#!/usr/bin/env python3
"""Read forge and registry facts separately from grading archive eligibility (ticket 156)."""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
EXPECTED = frozenset({"policy-as-versioned-flux", "apps", "readiness-collector", "pr-gate-action",
                      "renovate-config", "handbook-generator", "ledger", "storefront", "api",
                      "reports", "c2p-collector", "datastore", "cloud", "governance-agent",
                      "policy", "fleet"})
ORG = "policy-as-versioned-flux"
ADOPTERS = ("driftwood", "tuppence", "ludlow")
IMAGE = re.compile(r"ghcr\.io/policy-as-versioned-flux/[a-z0-9_-]+(?:@sha256:[a-f0-9]{64}|:[\w.-]+(?:@sha256:[a-f0-9]{64})?)")
PROBE_IMAGE = "ghcr.io/policy-as-versioned-flux/readiness-collector:v1.0.0"


def register(path: Path) -> list[dict]:
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict) or data.get("schema") != 1 or data.get("organization") != ORG:
        raise ValueError("register must identify schema 1 and the incumbent organization")
    rows = data.get("repositories")
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError("register repositories must be a list of records")
    names = [row.get("name") for row in rows]
    if len(names) != len(set(names)) or set(names) != EXPECTED:
        raise ValueError("register must name each of the sixteen incumbent repositories once")
    for row in rows:
        if row.get("disposition") not in {"retained", "lifted", "dropped", "transferred"}:
            raise ValueError(f"unknown disposition for {row['name']}")
        if not row.get("reason") or not isinstance(row.get("checks"), list):
            raise ValueError(f"{row['name']} needs a reason and prerequisite check list")
        if row["disposition"] == "transferred" and row.get("owner") not in {
                f"policy-as-versioned-{party}" for party in ADOPTERS}:
            raise ValueError(f"{row['name']} has no adopter owner")
    return rows


def api(endpoint: str) -> dict:
    result = subprocess.run(["gh", "api", endpoint], capture_output=True, text=True, timeout=60)
    if result.returncode:
        raise ValueError(result.stderr.strip()[:400] or "GitHub API read failed")
    data = json.loads(result.stdout)
    if not isinstance(data, dict):
        raise ValueError("GitHub returned no repository record")
    return data


def anonymous_pull(image: str) -> dict:
    """Read the OCI manifest with an anonymous registry token, never the GitHub credential."""
    repository, separator, ref = image.removeprefix("ghcr.io/").partition("@")
    if separator:
        repository = repository.split(":", 1)[0]
    else:
        repository, ref = repository.rsplit(":", 1)
    try:
        params = urllib.parse.urlencode({"service": "ghcr.io", "scope": f"repository:{repository}:pull"})
        with urllib.request.urlopen(f"https://ghcr.io/token?{params}", timeout=30) as response:
            token = json.load(response)["token"]
        request = urllib.request.Request(f"https://ghcr.io/v2/{repository}/manifests/{ref}",
            headers={"Authorization": f"Bearer {token}", "Accept":
                "application/vnd.oci.image.index.v1+json, application/vnd.docker.distribution.manifest.v2+json"})
        with urllib.request.urlopen(request, timeout=30) as response:
            return {"image": image, "pullable": response.status == 200, "status": response.status,
                    "digest": response.headers.get("Docker-Content-Digest")}
    except urllib.error.HTTPError as error:
        return {"image": image, "pullable": False, "status": error.code}
    except (OSError, ValueError, KeyError) as error:
        return {"image": image, "pullable": None, "error": str(error)[:300]}


def served_images(estate: Path) -> set[str]:
    images: set[str] = set()
    for party in ADOPTERS:
        directory = estate / party
        source = directory / "gitops/flux-system/gotk-sync.yaml"
        if not source.exists():
            raise ValueError(f"{party}: no served apps source pin")
        documents = list(yaml.safe_load_all(source.read_text()))
        pins = [d["spec"]["ref"]["tag"] for d in documents
                if d and d.get("kind") == "GitRepository"]
        if len(pins) != 1:
            raise ValueError(f"{party}: cannot identify one signed apps tag")
        for path in ("gitops/apps",):
            result = subprocess.run(["git", "-C", str(directory), "grep", "-I", "-h", "-E",
                                     "ghcr.io/policy-as-versioned-flux/", pins[0], "--", path],
                                    capture_output=True, text=True, timeout=30)
            if result.returncode not in (0, 1):
                raise ValueError(f"{party}: cannot read manifests at {pins[0]}")
            images.update(IMAGE.findall(result.stdout))
    return images


def collect(rows: list[dict], estate: Path) -> dict:
    facts: dict = {"schema": 1, "observed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
                   "repositories": {}, "images": []}
    for row in rows:
        name = row["name"]
        try:
            record = api(f"repos/{ORG}/{name}")
            facts["repositories"][name] = {"full_name": record.get("full_name"),
                                           "archived": record.get("archived")}
        except (ValueError, OSError, subprocess.SubprocessError) as error:
            facts["repositories"][name] = {"error": str(error)[:400]}
    try:
        images = served_images(estate)
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        facts["image_error"] = str(error)
        images = set()
    # Permanent probe specified by ADR-0036, independent of whether an adopter serves it.
    images.add(PROBE_IMAGE)
    facts["images"] = [anonymous_pull(image) for image in sorted(images)]
    return facts


def grades(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    return {fields[0]: fields[1] for line in path.read_text().splitlines()
            if not line.startswith("#") and len(fields := line.split("\t", 2)) >= 2}


def cage_lane(estate: Path, checks: dict[str, str]) -> bool:
    """A PASS predating the new fact-7 registration cannot authorize the final three archives."""
    for party in ADOPTERS:
        if checks.get(f".estate-clone/{party}/verify-reconcile.sh") != "PASS":
            continue
        directory = estate / party
        try:
            question = yaml.safe_load((directory / "drift/window.yaml").read_text()).get("cage_behaviour_sample", {})
            if "reference" not in json.dumps(question).lower():
                continue
            sample = json.loads((directory / "drift/samples.jsonl").read_text().splitlines()[-1])
            # Delegate registration and seven-fact grading to the actual lane reader.
            result = subprocess.run([sys.executable, str(directory / "drift/five-facts.py"), "grade"],
                                    cwd=directory, capture_output=True, text=True, timeout=60)
            if result.returncode == 0 and "fact_7" in json.dumps(sample) and \
                    "not scored" not in result.stdout.lower() and "predates" not in result.stdout.lower():
                return True
        except (OSError, ValueError, subprocess.SubprocessError):
            continue
    return False


def grade(rows: list[dict], facts: dict, checks: dict[str, str], cage: bool,
          expected_images: set[str] | None = None) -> tuple[int, list[str]]:
    messages: list[str] = []
    if facts.get("schema") != 1 or not facts.get("observed_at"):
        return 1, ["FAIL: forge facts must name schema 1 and the observation time"]
    try:
        observed = dt.datetime.fromisoformat(facts["observed_at"].replace("Z", "+00:00"))
        age = dt.datetime.now(dt.timezone.utc) - observed
    except (ValueError, TypeError, AttributeError):
        return 1, ["FAIL: forge observation time must be a timestamp with a timezone"]
    if age < -dt.timedelta(minutes=5):
        return 1, ["FAIL: forge observations are dated in the future"]
    if age > dt.timedelta(hours=48):
        return 3, ["SKIP: incumbent forge observations are older than the 48h freshness bound"]
    records = facts.get("repositories", {})
    if not isinstance(records, dict):
        return 1, ["FAIL: repository observations must be keyed records"]
    for row in rows:
        name = row["name"]
        record = records.get(name)
        if not isinstance(record, dict) or record.get("error"):
            messages.append(f"SKIP: {name}: no forge facts: {(record or {}).get('error', 'missing')}")
            continue
        if type(record.get("archived")) is not bool or not isinstance(record.get("full_name"), str):
            messages.append(f"FAIL: {name}: malformed repository facts")
            continue
        eligible = all(cage if check == "cage-lane" else checks.get(check) == "PASS"
                       for check in row["checks"])
        if row["disposition"] == "transferred":
            expected = f"{row['owner']}/{name}"
            if record["full_name"] != expected:
                messages.append(f"FAIL: {name}: forge owner is {record['full_name']}, expected {expected}")
            elif record["archived"]:
                messages.append(f"FAIL: {name}: transferred application is archived")
            else:
                messages.append(f"PASS: {name}: forge names new owner {row['owner']}")
        elif record["full_name"] != f"{ORG}/{name}":
            messages.append(f"FAIL: {name}: unexpected repository owner {record['full_name']}")
        elif row["disposition"] == "retained":
            messages.append(f"{'FAIL' if record['archived'] else 'PASS'}: {name}: hub must remain live")
        elif record["archived"] and not eligible:
            messages.append(f"FAIL: {name}: archived without a passing prerequisite {row['checks']}")
        elif record["archived"]:
            messages.append(f"PASS: {name}: archived and its current prerequisite passes")
        elif eligible:
            messages.append(f"LIMIT: {name}: row passes; archive has not been performed")
        else:
            messages.append(f"LIMIT: {name}: archive waits for {row['checks']}")
    if facts.get("image_error"):
        messages.append(f"SKIP: served incumbent images: {facts['image_error']}")
    observations = facts.get("images", [])
    if not isinstance(observations, list) or any(not isinstance(image, dict) for image in observations):
        return 1, messages + ["FAIL: image observations must be a list of records"]
    names = [image.get("image") for image in observations]
    if any(not isinstance(name, str) for name in names) or len(names) != len(set(names)):
        return 1, messages + ["FAIL: anonymous image observations need unique image names"]
    missing_images = (expected_images or {PROBE_IMAGE}) - set(names)
    for served in (expected_images if expected_images is not None else set(names)) - {PROBE_IMAGE}:
        repository = served.removeprefix(f"ghcr.io/{ORG}/").split(":", 1)[0].split("@", 1)[0]
        if (records.get(repository) or {}).get("archived") is True:
            messages.append(f"FAIL: archived repository {repository} still publishes a served image {served}")
    for missing in sorted(missing_images):
        messages.append(f"SKIP: anonymous OCI manifest observation missing for {missing}")
    for image in observations:
        pullable = image.get("pullable")
        prefix = "PASS" if pullable is True else "FAIL" if pullable is False else "SKIP"
        messages.append(f"{prefix}: anonymous OCI manifest read {image.get('image')}: "
                        f"HTTP {image.get('status', 'unobserved')}")
    if not facts.get("images"):
        messages.append("SKIP: no anonymous OCI manifest observations")
    return (1 if any(m.startswith("FAIL:") for m in messages) else
            3 if any(m.startswith("SKIP:") for m in messages) else 0), messages


def selfcheck() -> None:
    rows = register(HERE / "register.yaml")
    facts: dict = {"schema": 1, "observed_at": dt.datetime.now(dt.timezone.utc).isoformat(), "repositories": {
        row["name"]: {"full_name": f"{row.get('owner', ORG)}/{row['name']}",
                      "archived": row["disposition"] in {"dropped", "lifted"}}
        for row in rows}, "images": [{"image": PROBE_IMAGE, "pullable": True, "status": 200}]}
    checks = {check: "PASS" for row in rows for check in row["checks"]}
    assert grade(rows, facts, checks, True)[0] == 0
    for name in ("handbook-generator", "c2p-collector", "datastore", "cloud"):
        limited = dict(checks)
        for check in next(row for row in rows if row["name"] == name)["checks"]:
            limited[check] = "SKIP"
        assert grade(rows, facts, limited, True)[0] == 1, name
    assert grade(rows, facts, checks, False)[0] == 1
    for name in ("ledger", "storefront", "reports", "api"):
        planted = copy.deepcopy(facts)
        planted["repositories"][name]["full_name"] = f"{ORG}/{name}"
        assert grade(rows, planted, checks, True)[0] == 1, name
    planted = copy.deepcopy(facts)
    planted["repositories"]["policy-as-versioned-flux"]["archived"] = True
    assert grade(rows, planted, checks, True)[0] == 1
    planted = copy.deepcopy(facts)
    planted["repositories"]["readiness-collector"]["archived"] = False
    assert any(m.startswith("LIMIT:") for m in grade(rows, planted, checks, True)[1])
    planted = copy.deepcopy(facts)
    planted["images"][0]["pullable"] = False
    assert grade(rows, planted, checks, True)[0] == 1
    planted["images"][0]["pullable"] = None
    assert grade(rows, planted, checks, True)[0] == 3
    assert grade(rows, facts, checks, True, {PROBE_IMAGE, "ghcr.io/served@sha256:fixture"})[0] == 3
    planted = copy.deepcopy(facts)
    planted["images"].append(copy.deepcopy(planted["images"][0]))
    assert grade(rows, planted, checks, True)[0] == 1
    planted = copy.deepcopy(facts)
    planted["observed_at"] = "1900-01-01T00:00:00Z"
    assert grade(rows, planted, checks, True)[0] == 3
    pinned_image = "ghcr.io/policy-as-versioned-flux/cloud:v1.0.1@sha256:" + "a" * 64
    assert IMAGE.findall(pinned_image) == [pinned_image]
    planted = copy.deepcopy(facts)
    planted["images"].append({"image": pinned_image, "pullable": True, "status": 200})
    assert grade(rows, planted, checks, True)[0] == 1
    print("PASS: sixteen rows graded; premature archives, wrong owners, archived hub and failed anonymous pulls are observed false")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("collect", "check", "selfcheck"))
    parser.add_argument("--estate", type=Path, default=ROOT / ".estate-clone")
    parser.add_argument("--facts", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--grades", type=Path, default=ROOT / "talk/captures/_grades.tsv")
    args = parser.parse_args()
    try:
        rows = register(HERE / "register.yaml")
        if args.command == "selfcheck":
            selfcheck()
            return 0
        if args.command == "collect":
            if not args.out:
                parser.error("collect needs --out")
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(json.dumps(collect(rows, args.estate), indent=2) + "\n")
            return 0
        if not args.facts or not args.facts.is_file():
            print("SKIP: no INCUMBENT_FACTS file from the credentialled clocks job")
            return 3
        checks = grades(args.grades)
        expected_images = served_images(args.estate) | {PROBE_IMAGE}
        status, messages = grade(rows, json.loads(args.facts.read_text()), checks,
                                 cage_lane(args.estate, checks), expected_images)
        print("\n".join(messages))
        return status
    except (OSError, ValueError, yaml.YAMLError) as error:
        print(f"FAIL: incumbent register or facts cannot be graded: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
