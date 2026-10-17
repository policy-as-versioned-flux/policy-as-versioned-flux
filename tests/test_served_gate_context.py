"""Actual served gate/cold callers on unsigned filesystem and CLI instruments.

No fixture signature, world grade or consumer retirement decision is fabricated.
The production integration separately uses the real published gate/compiler.
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import tempfile
from types import ModuleType
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Captured from Ludlow2533793e (same9c033bf workflow tree), gate step only.
LUDLOW_RETIREMENT_WORKFLOW = r'''
jobs:
  gate:
    steps:
      - name: adopter gate -- verify pin, verify platform's evidence, compose this institution's own bump
        run: |
          python3 ludlow/.github/scripts/adopter_gate.py \
            --ludlow-dir ludlow \
            --platform-dir platform \
            --old-ref "${{ github.event.pull_request.base.sha }}" \
            --new-ref "${{ github.event.pull_request.head.sha }}" \
            --composed-base-ref "${{ github.event.pull_request.base.sha }}" \
            --composed-head-ref "${{ github.event.pull_request.head.sha }}" \
            --retirement-tools-dir platform-tools \
            --out-comment adopter-gate-comment.md \
            --identity-regexp "${ADOPTER_GATE_IDENTITY_REGEXP}" \
            --issuer "${ADOPTER_GATE_ISSUER}"
'''


def check_served_retirement_call_uses_independent_compiler_and_rejects_shared_literal(
        grader: ModuleType, tmp_path: Path) -> None:
    tokens = grader.gate_argv(LUDLOW_RETIREMENT_WORKFLOW, 'adopter_gate.py')
    planted = {'base_sha': 'a' * 40, 'head_sha': 'b' * 40,
               'base_tag': 'v2.0.0', 'head_tag': 'v2.0.1'}
    policy, compiler = tmp_path / 'policy-v2.0.1', tmp_path / 'compiler-v5.1.0'
    def mapping(argv):
        return grader.build_mapping(argv, tmp_path / 'adopter_gate.py', planted, policy,
                                    tmp_path / 'adopter', tmp_path / 'summary.json', tmp_path / 'comment.md',
                                    ('identity', 'issuer'), compiler_tools_dir=compiler)
    resolved = grader.resolve_argv(tokens, mapping(tokens))
    assert resolved[resolved.index('--platform-dir') + 1] == str(policy)
    assert resolved[resolved.index('--retirement-tools-dir') + 1] == str(compiler)
    assert len(resolved) == len(tokens)
    collision = ['platform' if token == 'platform-tools' else token for token in tokens]
    with unittest.TestCase().assertRaisesRegex(grader.Unresolved, 'two different roles'):
        mapping(collision)
    unknown = [*tokens, '--unplanted-role', 'literal']
    with unittest.TestCase().assertRaisesRegex(grader.Unresolved, '--unplanted-role'):
        grader.resolve_argv(unknown, mapping(unknown))


def _served_tools_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Unsigned local Git and CLI instruments; these prove caller mechanics, not trust."""
    import os
    import subprocess
    env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)
    source, unit = tmp_path / 'platform-source', tmp_path / 'unit'
    source.mkdir()
    subprocess.run(['git', 'init', '-q', '-b', 'main', str(source)], check=True, env=env)
    (source / 'compiler.txt').write_text('synthetic compiler fixture\n')
    subprocess.run(['git', '-C', str(source), 'add', '.'], check=True, env=env)
    subprocess.run(['git', '-C', str(source), '-c', 'user.name=fixture',
                    '-c', 'user.email=fixture@example.invalid', '-c', 'commit.gpgsign=false',
                    'commit', '-qm', 'unsigned fixture'], check=True, env=env)
    sha = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True, env=env).strip()
    subprocess.run(['git', '-C', str(source), 'tag', 'v5.1.0'], check=True, env=env)
    scripts = unit / '.github/scripts'
    scripts.mkdir(parents=True)
    (unit / '.github/workflows').mkdir()
    (unit / '.github/workflows/shift-left.yml').write_text(
        'env:\n  ADOPTER_GATE_IDENTITY_REGEXP: fixture-identity\n  ADOPTER_GATE_ISSUER: fixture-issuer\n'
        + LUDLOW_RETIREMENT_WORKFLOW)
    (unit / '.github/platform-tools-pin.yaml').write_text(
        'kind: GitRepository\nspec:\n  url: https://github.com/policy-as-versioned-platform/platform\n'
        f'  ref: {{tag: v5.1.0, commit: {sha}}}\n')
    (unit / '.gitignore').write_text('__pycache__/\n')
    (unit / 'party.yaml').write_text(
        'party: ludlow\nroles: [adopter]\nbaseline: LOW\n'
        'inherits: [{party: platform, kind: implementations, version: "5.0.0"}]\n'
        'overlay: {add: [], restate: []}\n')
    (scripts / 'read-pins.py').write_text('"""Synthetic helper imported by the CLI instrument."""\n')
    marker = tmp_path / 'prepared.json'
    (scripts / 'platform-tools.py').write_text(
        'import argparse, importlib, json, os, pathlib, subprocess\n'
        "importlib.import_module('read-pins')\n"
        'p=argparse.ArgumentParser(); p.add_argument("--adopter-dir"); p.add_argument("--tools-dir"); '
        'p.add_argument("command"); a=p.parse_args()\n'
        'assert a.command == "check"\n'
        f'assert subprocess.check_output(["git","-C",a.tools_dir,"rev-parse","HEAD"],text=True).strip()=={sha!r}\n'
        f'pathlib.Path({str(marker)!r}).write_text(json.dumps({{"HOME":os.environ.get("HOME"),"tools":a.tools_dir}}))\n'
        'print("OK: synthetic dependency prepared; not a signature verification")\n')
    # The actual run_gate subprocess reaches this test instrument through the served workflow.
    (scripts / 'adopter_gate.py').write_text(
        'import json, os, pathlib, subprocess, sys\n'
        'args=sys.argv[1:]; adopter=pathlib.Path(args[args.index("--ludlow-dir")+1]); '
        'tools=pathlib.Path(args[args.index("--retirement-tools-dir")+1])\n'
        'assert (tools/"compiler.txt").is_file()\n'
        'assert (adopter/".github/scripts/platform-tools.py").is_file()\n'
        'assert (adopter/"party.yaml").is_file()\n'
        'assert subprocess.check_output(["git","-C",str(adopter),"status","--porcelain"],text=True)==""\n'
        'comment=pathlib.Path(args[args.index("--out-comment")+1]); '
        'comment.write_text("composed=none\\n")\n'
        'print(json.dumps({key:os.environ.get(key) for key in '
        '["HOME","TUF_ROOT","HTTPS_PROXY","https_proxy","NO_PROXY","no_proxy"]}))\n')
    return source, unit, marker


def check_prepared_tools_context_is_separate_exact_and_committed_before_planting(
        grader: ModuleType, tmp_path: Path) -> None:
    import yaml
    source, unit, marker = _served_tools_fixture(tmp_path)
    context, reason = grader.prepare_gate_context('ludlow', unit, source, tmp_path / 'prepared')
    assert context is not None, reason
    assert context.compiler_tools_dir != source
    assert context.compiler_tools_dir != tmp_path / 'policy-v2.0.1'
    assert marker.is_file()
    tags = {'v2.0.0': 'a' * 40, 'v2.0.1': 'b' * 40}
    repo = tmp_path / 'adopter'
    planted = grader.plant(repo, grader.CASES['retirement'], tags, party='ludlow', context=context)
    for ref, version in [(planted['base_sha'], '2.0.0'), (planted['head_sha'], '2.0.1')]:
        for path in ['.github/platform-tools-pin.yaml', '.github/scripts/platform-tools.py',
                     '.github/scripts/read-pins.py', '.gitignore']:
            assert grader._git(repo, 'show', f'{ref}:{path}').stdout.encode() == (unit / path).read_bytes()
        party = yaml.safe_load(grader._git(repo, 'show', f'{ref}:party.yaml').stdout)
        served_party = yaml.safe_load((unit / 'party.yaml').read_text())
        served_party['inherits'][0]['version'] = version
        assert party == served_party
    assert grader._git(repo, 'status', '--porcelain').stdout == ''
    assert not list(repo.glob('implementation-retirements/*'))
    work = tmp_path / 'gate'; work.mkdir()
    result, reason = grader.run_gate('ludlow', unit, planted, tmp_path / 'policy-v2.0.1', repo,
                                     work, context=context)
    assert result is not None, reason
    assert result['exit'] == 0, result


def check_preparation_refusal_is_unknown_before_any_gate_answer(grader: ModuleType, tmp_path: Path) -> None:
    source, unit, _ = _served_tools_fixture(tmp_path)
    runner = unit / '.github/scripts/platform-tools.py'
    runner.write_text('import sys\nprint("REFUSED: synthetic dependency failure",file=sys.stderr)\nsys.exit(97)\n')
    context, reason = grader.prepare_gate_context('ludlow', unit, source, tmp_path / 'prepared')
    assert context is None
    assert 'dependency' in reason and '97' in reason and 'synthetic dependency failure' in reason
    runner.unlink()
    context, reason = grader.prepare_gate_context('ludlow', unit, source, tmp_path / 'missing')
    assert context is None and 'platform-tools.py' in reason


class ServedGateContext(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix='served-gate-context-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.fold = load_module('served_gate_fold', 'verify/fold-agreement/fold_agreement.py')

    def test_actual_retirement_roles_remain_distinct_and_fail_closed(self) -> None:
        check_served_retirement_call_uses_independent_compiler_and_rejects_shared_literal(
            self.fold, self.root)

    def test_prepared_context_reaches_actual_gate_call_with_clean_committed_runtime(self) -> None:
        check_prepared_tools_context_is_separate_exact_and_committed_before_planting(
            self.fold, self.root)

    def test_missing_or_refusing_dependency_is_unknown(self) -> None:
        check_preparation_refusal_is_unknown_before_any_gate_answer(self.fold, self.root)

    def test_preparation_precedes_actual_cold_call_and_cold_environment_is_restored(self) -> None:
        source, unit, marker = _served_tools_fixture(self.root)
        before = dict(os.environ)
        context, reason = self.fold.prepare_gate_context('ludlow', unit, source, self.root / 'prepared')
        self.assertIsNotNone(context, reason)
        prepared = marker.read_bytes()
        self.assertEqual(json.loads(prepared)['HOME'], before.get('HOME'))
        work = self.root / 'cold'; work.mkdir()
        repo = work / 'adopter'
        planted = self.fold.plant(repo, self.fold.CASES['quiet'],
                                   {'v2.0.0': 'a' * 40, 'v2.0.1': 'b' * 40},
                                   party='ludlow', context=context)
        real = load_module('served_gate_real_signature', 'verify/real-signature/real_signature.py')
        code, output = real.offline_exit(self.fold, 'ludlow', unit, planted,
                                         self.root / 'policy-v2.0.1', repo, work, context=context)
        self.assertEqual(code, 0, output)
        observed = json.loads(output)
        expected = real.COLD_ENV(work / 'cold-home', work / 'cold-tuf')
        for key in observed:
            self.assertEqual(observed[key], expected[key], key)
        self.assertEqual(dict(os.environ), before)
        self.assertEqual(marker.read_bytes(), prepared, 'dependency must not be prepared in cold HOME')


if __name__ == '__main__':
    unittest.main()
