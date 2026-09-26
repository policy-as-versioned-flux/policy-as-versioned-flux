#!/usr/bin/env python3
"""Scratch driver around an UNMODIFIED byte copy of platform's engine_compatibility.py.

Adaptations (all here, none in the copied module):
  * mode `row`: calls engine_compatibility._published_row(repo, entry, binary) directly,
    bypassing check()'s `tested_engines == [running version]` guard, so 1.19.1 can be graded
    against the real policy/v5.0.0 tag. Everything else (git tag/tree checks, archive, _adapt,
    _matrix) is the harness's own code.
  * mode `variant`: calls engine_compatibility._matrix(root, '5.0.0', family, binary) on a
    scratch COPY of the tagged tree whose bodies were edited (variant dir), because a modified
    body has no tag. Same adaptation + same assertion parsing as the harness.
  * _run is wrapped so the FULL kyverno output is saved (the harness keeps only a sha256 and
    the last 6000 chars on failure).
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('engine_compatibility', HERE / 'engine_compatibility.py')
ec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ec)

CAPTURED: list[dict] = []
_orig_run = ec._run


def _capturing_run(args, **kwargs):
    result = _orig_run(args, **kwargs)
    if len(args) > 1 and args[1] == 'test':
        CAPTURED.append({'args': args, 'rc': result.returncode,
                         'output': result.stdout + result.stderr})
    return result


ec._run = _capturing_run


def save(label: str, payload: dict) -> None:
    out = HERE / 'captures' / label
    out.mkdir(parents=True, exist_ok=True)
    (out / 'result.json').write_text(json.dumps(payload, indent=2))
    for i, cap in enumerate(CAPTURED):
        family = Path(cap['args'][2]).name
        (out / f'{family}.kyverno-test.out.txt').write_text(
            '$ ' + ' '.join(cap['args']) + f'\n# rc={cap["rc"]}\n' + cap['output'])
    print(json.dumps({k: v for k, v in payload.items() if k not in ('rows', 'matrices', 'limits')}, indent=1))
    for m in payload.get('matrices', []) + [m for r in payload.get('rows', []) for m in r.get('matrices', [])]:
        print(f"{label}: {m['family']}: outcome={m['outcome']} passed={m['passed_assertions']} "
              f"failed={m['failed_assertions']} exit={m['exit_code']}")


def main() -> int:
    mode, binary, label = sys.argv[1], sys.argv[2], sys.argv[3]
    if mode == 'check':
        repo = Path(sys.argv[4])
        report = ec.check(repo, binary)
        save(label, report)
        print(label + ': check outcome=' + report['outcome'])
    elif mode == 'row':
        repo = Path(sys.argv[4])
        entry = {'version': '5.0.0', 'tag': 'policy/v5.0.0',
                 'commit': '597f214bcdf10a77c957debc7e8a7842e1156fb8'}
        row = ec._published_row(repo, entry, binary)
        save(label, {'mode': 'row', 'binary': binary, 'rows': [row]})
        print(label + ': row outcome=' + row['outcome'])
    elif mode == 'variant':
        variant = Path(sys.argv[4])
        work = HERE / 'work' / label
        if work.exists():
            shutil.rmtree(work)
        shutil.copytree(variant, work)
        matrices = [ec._matrix(work, '5.0.0', family, binary) for family in ec.FAMILIES]
        outcome = 'passed' if all(m['outcome'] == 'passed' for m in matrices) else 'failed'
        save(label, {'mode': 'variant', 'variant': str(variant), 'binary': binary,
                     'matrices': matrices, 'outcome': outcome})
        print(label + ': variant outcome=' + outcome)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
