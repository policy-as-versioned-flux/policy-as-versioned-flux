#!/usr/bin/env python3
"""Grade an adopter's served twin workflow against ADR-0031 (ticket 142).

Reads origin/main with git show. Working-tree proposals are never served proof.
The local child sandbox is a separate live measurement, named as a ceiling here.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path
from typing import Any

import yaml

LADDER = ('baseline', 'restricted', 'quarantine', 'isolated')
INERT = ('actions/checkout', 'actions/upload-artifact', 'actions/download-artifact')
HEX = re.compile(r'^[0-9a-f]{40}$')
PROGRAM = re.compile(r'(?m)^\s*(?:python3?|bash|sh|node|npx)\s+|\./\S+\.py')
HUB = 'policy-as-versioned-flux/policy-as-versioned-flux'


def grade(files: dict[str, str]) -> list[str]:
    errors = []
    try:
        workflow = yaml.safe_load(files['.github/workflows/twin-sweep.yml'])
        pin = yaml.safe_load(files['twin/PIN.yaml'])
        evidence = json.loads(files['composed/evidence.json'])
        jobs = workflow['jobs']
        twin, writer = jobs['twin'], jobs['write']
    except (KeyError, ValueError, TypeError, yaml.YAMLError) as exc:
        return ['served twin cage instrument is missing or malformed: ' + str(exc)]
    prices = [p for p in evidence.get('prices', []) if p.get('kind') == 'agent-cage' and p.get('subject') == 'twin-agent']
    if len(prices) != 1 or prices[0].get('proposed_tier') not in LADDER:
        errors.append('served evidence selects no priced twin-agent rung; writer must fall closed to isolated')
    if twin.get('permissions') != {'contents': 'read'}:
        errors.append('twin job holds capabilities beyond contents: read')
    if not HEX.fullmatch(str(pin.get('hub_commit', ''))):
        errors.append('twin/PIN.yaml names no full hub commit')
    checkouts = [s for s in twin.get('steps', []) if s.get('with', {}).get('repository') == HUB]
    if len(checkouts) != 1 or checkouts[0].get('with', {}).get('ref') != '${{ steps.pin.outputs.hub_commit }}':
        errors.append('hub checkout is not the commit the pin-reading step names')
    reader: dict[str, Any] = next((s for s in twin.get('steps', []) if s.get('id') == 'pin'), {})
    if 'twin/PIN.yaml' not in str(reader.get('run', '')) or 'hub_commit=' not in str(reader.get('run', '')):
        errors.append('hub commit output is not read from twin/PIN.yaml')
    if pin.get('tag_cut') is True:
        tag = pin.get('twin_tag')
        if not isinstance(tag, str) or not tag.startswith('twin/v'):
            errors.append('tag_cut declares no signed twin tag')
    for job_name, job in jobs.items():
        for step in job.get('steps', []):
            uses = str(step.get('uses', ''))
            if uses and not re.search(r'@[0-9a-f]{40}$', uses):
                errors.append(job_name + ' action is not pinned by commit: ' + uses)
            if job_name == 'write' and uses and not uses.startswith(tuple(name + '@' for name in INERT)):
                errors.append('writer executes a non-inert action: ' + uses)
            if job_name == 'write' and step.get('with', {}).get('repository') == HUB:
                errors.append('writer checks the hub out with a write credential')
            shell = re.sub(r'(?m)^\s*#.*$', '', str(step.get('run', '')))
            if job_name == 'write' and PROGRAM.search(shell):
                errors.append('writer runs a program from its checkout')
            if 'pip install' in shell and '--require-hashes' not in shell:
                errors.append('twin package download is not hash-pinned')
            if ('curl ' in shell or 'wget ' in shell) and not ('sha256sum' in shell or 'shasum' in shell):
                errors.append(job_name + ' download carries no checksum comparison')
            if job_name == 'write' and ('gh pr create' in shell or 'git checkout -b' in shell):
                condition = str(step.get('if', ''))
                if "steps.cage.outputs.rung == 'baseline'" not in condition or "steps.cage.outputs.rung == 'restricted'" not in condition:
                    errors.append('proposal step runs outside baseline/restricted')
    requirements = files.get('.github/requirements/twin-sweep.txt', '')
    if 'pyyaml==' not in requirements.lower() or not re.search(r'--hash=sha256:[0-9a-f]{64}', requirements):
        errors.append('hash-pinned twin requirements are missing')
    if "needs.twin.outputs.agent_rung != 'isolated'" not in str(writer.get('if', '')):
        errors.append('isolated rung still starts the writer')
    for job_name, job in (('twin', twin), ('write', writer)):
        step = next((s for s in job.get('steps', []) if s.get('id') == 'cage'), {})
        shell = str(step.get('run', ''))
        if not all(word in shell for word in ('agent-cage', 'twin-agent', 'composed/evidence.json', 'rung=isolated')):
            errors.append(job_name + ' does not derive a fail-closed rung from its own evidence')
    return errors


def served(repo: Path) -> dict[str, str]:
    paths = ('.github/workflows/twin-sweep.yml', 'twin/PIN.yaml', 'composed/evidence.json',
             '.github/requirements/twin-sweep.txt')
    files = {}
    for path in paths:
        read = subprocess.run(['git', '-C', str(repo), 'show', 'origin/main:' + path], text=True, capture_output=True)
        if read.returncode == 0:
            files[path] = read.stdout
    return files


def selfcheck(root: Path) -> None:
    # A minimal workflow fixture, independent of the estate checkout. The real
    # check never substitutes it for served files.
    cage = 'jq agent-cage twin-agent composed/evidence.json\nrung=isolated'
    workflow = {"permissions": {"contents": "read"}, "jobs": {
        "twin": {"permissions": {"contents": "read"}, "steps": [
            {"id": "cage", "run": cage},
            {"id": "pin", "run": "read twin/PIN.yaml; echo hub_commit=..."},
            {"uses": "actions/checkout@" + "a" * 40,
             "with": {"repository": HUB, "ref": '${{ steps.pin.outputs.hub_commit }}'}},
            {"run": "pip install --require-hashes -r requirements.txt"}]},
        "write": {"if": "needs.twin.outputs.agent_rung != 'isolated'", "steps": [
            {"id": "cage", "run": cage},
            {"if": "steps.cage.outputs.rung == 'baseline' || steps.cage.outputs.rung == 'restricted'",
             "run": "gh pr create"}]}}}
    files = {'.github/workflows/twin-sweep.yml': yaml.safe_dump(workflow),
             'twin/PIN.yaml': 'hub_commit: ' + 'a' * 40 + '\ntag_cut: false\n',
             '.github/requirements/twin-sweep.txt': 'pyyaml==6.0.3 --hash=sha256:' + 'b' * 64}
    files['composed/evidence.json'] = json.dumps({'prices': [{'kind': 'agent-cage', 'subject': 'twin-agent', 'proposed_tier': 'baseline'}]})
    assert grade(files) == [], grade(files)
    for old, new in (("contents: read", "contents: write"),
                     ("needs.twin.outputs.agent_rung != 'isolated'", "true"),
                     ("steps.cage.outputs.rung == 'baseline'", "true"),
                     ('--require-hashes', ''), ('rung=isolated', 'rung=baseline')):
        planted = dict(files)
        planted['.github/workflows/twin-sweep.yml'] = planted['.github/workflows/twin-sweep.yml'].replace(old, new)
        assert grade(planted), old
    print('PASS: twin cage selfcheck -- five loosened workflows fail')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('check', 'selfcheck'))
    parser.add_argument('--estate', type=Path, default=Path(__file__).resolve().parents[2] / '.estate-clone')
    args = parser.parse_args()
    if args.command == 'selfcheck':
        selfcheck(Path(__file__).resolve().parents[2])
        return 0
    failures = 0
    for org in ('driftwood', 'tuppence', 'ludlow'):
        faults = grade(served(args.estate / org))
        if faults:
            for fault in faults:
                print('FAIL: ' + org + ' served twin cage: ' + fault)
            failures += 1
        else:
            print('PASS: ' + org + ' served twin workflow fits its priced rung dials')
    print('LIMIT: local-clock sandbox is configured; its live resistance to a rebuilt child environment remains unmeasured (ticket 142 item 3)')
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
