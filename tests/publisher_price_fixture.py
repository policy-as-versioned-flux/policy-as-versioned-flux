"""Whole cross-party source fixture; never a genuine release or monetary outcome.

Production SDKs, publisher converter/gate and compose run unchanged. Only the
external certificate/signature boundary is an explicitly synthetic executable.
All fixture histories and numeric declarations belong to disposable repositories.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import yaml

HUB = Path(__file__).resolve().parents[1]
LABEL = 'Explicit synthetic source fixture; no world observation or price credit.'


def source_roots():
    value = os.environ.get('PAVC_PRICE_TEST_SOURCES')
    roots = ({k: Path(v).resolve() for k, v in json.loads(value).items()} if value else
             {p: HUB / '.estate-clone' / p for p in ('platform', 'nist', 'feeds')})
    for party, path in [('platform', 'compose/composition.py'),
                        ('nist', 'publisher-reliability/price_records.py'),
                        ('feeds', '.github/scripts/publisher-release-gate.py')]:
        if party not in roots or not (roots[party] / path).is_file():
            raise RuntimeError(f'publisher price vertical instrument missing: {party}/{path}')
    return roots


def git(repo, *args, at='2019-11-01T00:00:00Z'):
    env = dict(os.environ, GIT_AUTHOR_NAME='explicit synthetic source fixture',
               GIT_AUTHOR_EMAIL='fixture@example.invalid', GIT_COMMITTER_NAME='explicit synthetic source fixture',
               GIT_COMMITTER_EMAIL='fixture@example.invalid', GIT_AUTHOR_DATE=at, GIT_COMMITTER_DATE=at,
               GIT_NO_REPLACE_OBJECTS='1')
    return subprocess.check_output(['git', '-C', str(repo), '-c', 'commit.gpgsign=false',
        '-c', 'tag.gpgsign=false', '-c', 'core.hooksPath=/dev/null', *args], env=env,
        stderr=subprocess.PIPE, timeout=30).decode().strip()


def new_repo(root, party):
    repo = root / party
    repo.mkdir(parents=True, exist_ok=True)
    git(repo, 'init', '-q', '-b', 'main')
    git(repo, 'remote', 'add', 'origin', f'https://github.com/policy-as-versioned-{party}/{party}')
    return repo


def write(repo, path, value):
    dest = repo / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(value if isinstance(value, str) else json.dumps(value))


def publish(repo, tag, at):
    git(repo, 'add', '.', at=at)
    git(repo, 'commit', '-qm', LABEL, at=at)
    git(repo, 'tag', '--no-sign', '-a', tag, '-m', LABEL, at=at)
    commit = git(repo, 'rev-parse', 'HEAD')
    git(repo, 'update-ref', 'refs/remotes/origin/main', commit)
    def reference(path):
        return {'party': repo.name, 'tag': tag, 'commit': commit, 'path': path,
                'git_blob': git(repo, 'rev-parse', commit + ':' + path)}
    return reference


def signature_boundary(root):
    directory = root / 'signature-fixture-bin'
    directory.mkdir()
    executable = directory / 'gitsign'
    executable.write_text('#!' + sys.executable + '\n' + '''import os,pathlib,re,sys
assert sys.argv[1] == 'verify-tag'
party=pathlib.Path.cwd().name
identity=f'https://github.com/policy-as-versioned-{party}/{party}/.github/workflows/cut-release.yml@refs/heads/main'
assert ('--certificate-identity-regexp=^'+re.escape(identity)+'$' in sys.argv or
        '--certificate-identity='+identity in sys.argv)
assert '--certificate-oidc-issuer=https://token.actions.githubusercontent.com' in sys.argv
if os.environ.get('PAVC_SYNTHETIC_REJECT_TAG') == sys.argv[2]:
    print('Explicit synthetic signer rejection for selected tag', file=sys.stderr)
    raise SystemExit(1)
print('EXPLICIT SYNTHETIC SIGNATURE BOUNDARY; no genuine certificate verification')
print('Good signature from synthetic fixture')
print('Validated Git signature: true')
print('Validated Rekor entry: true')
print('Validated Certificate claims: true')
''')
    executable.chmod(0o755)
    return {'PATH': str(directory) + os.pathsep + os.environ.get('PATH', '')}


def whole_fixture(root, actual, *, degraded=False, unresolved=False):
    """Build real SDK inputs, an independent annual resolution and scorer release."""
    sys.path.insert(0, str(actual['platform'] / 'compose'))
    sys.path.insert(0, str(actual['nist'] / 'publisher-reliability'))
    import composition as ct
    from price_records import build_forecast, build_resolution
    from price_accuracy import build_price_report, check_price_report

    sources = root / 'sources'
    sources.mkdir()
    adopter = new_repo(sources, 'driftwood')
    ct._write_fixture_adopter(adopter, 'SMALL', extra_inherits=[{
        'party': 'feeds', 'kind': 'feed', 'name': 'threat-register', 'version': 'v3',
        'since': '2019-11-01'}])
    party = yaml.safe_load((adopter / 'party.yaml').read_text())
    party['party'] = 'driftwood'
    party['appetite']['tolerance']['amount'] = 15
    party['size'] = {'turnover': {'amount': 100, 'currency': 'GBP'},
                     'customers': 1, 'headcount': 1, 'as_of': '2019-11-01'}
    write(adopter, 'party.yaml', yaml.safe_dump(party))
    context = publish(adopter, 'context/v1.0.0', '2019-11-01T00:00:00Z')('party.yaml')

    publisher = new_repo(sources, 'feeds')
    for relative in ['bump.py', '.github/scripts/publisher-release-gate.py',
                     'threat-register/to_fair_scenario.py', 'threat-register/rule.yaml',
                     'threat-register/payload.release-cage.schema.v1.json']:
        dest = publisher / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(actual['feeds'] / relative, dest)
    write(publisher, 'party.yaml', yaml.safe_dump({'party': 'feeds', 'roles': ['publisher'],
        'inherits': [], 'overlay': {'add': [], 'restate': []}, 'publishes': [{'kind': 'feed',
            'name': 'threat-register', 'path': 'threat-register',
            'payload_schema': 'threat-register/payload.release-cage.schema.v1.json'}]}))
    write(publisher, 'threat-register/bump.yaml', 'bump: patch\n')
    payload = {'feed_version': 'v3', 'published_by': 'feeds', 'currency': 'GBP', 'note': LABEL,
        'institutions': {'driftwood': {'lef': [1, 1, 1], 'threat': 'Synthetic loss',
            'flavour': LABEL, 'source': LABEL, 'lm_gbp': [9, 9, 9],
            'lm_basis': {'kind': 'editorial', 'statement': LABEL, 'as_of': '2019-11-01'}}}}
    envelope = {'kind': 'feed', 'name': 'threat-register', 'version': '3.0.0',
        'published_by': 'feeds', 'published_at': '2019-11-01T00:00:00Z',
        'payload_schema': 'threat-register/payload.release-cage.schema.v1.json', 'payload': payload}
    if degraded:
        # Removing a synthetic prior entry computes MAJOR through the real ladder.
        payload['institutions']['retired-synthetic'] = copy.deepcopy(payload['institutions']['driftwood'])
    path = 'threat-register/v3/feed.json'
    write(publisher, path, envelope)
    publish(publisher, 'threat-register/v3.0.0', '2019-11-01T00:00:00Z')
    payload['institutions'].pop('retired-synthetic', None)
    payload['institutions']['driftwood']['lm_gbp'] = [10, 10, 10]
    version = '3.0.1-quarantine.1' if degraded else '3.0.1'
    target_tag = 'threat-register/v' + version
    envelope.update(version=version, published_at='2019-11-02T00:00:00Z')
    write(publisher, path, envelope)
    # The actual native producer binds committed semantic input/code bytes.
    git(publisher, 'add', '.')
    git(publisher, 'commit', '-qm', LABEL, at='2019-11-02T00:00:00Z')
    git(publisher, 'update-ref', 'refs/remotes/origin/main', 'HEAD')
    gate = publisher / '.github/scripts/publisher-release-gate.py'
    native_path, cage_path = 'threat-register/price-native.json', 'threat-register/price-cage.json'
    built = subprocess.run([sys.executable, str(gate), 'build', 'threat-register',
        target_tag, native_path, cage_path], cwd=publisher, capture_output=True, text=True)
    if built.returncode:
        raise AssertionError('actual publisher native proof build refused: ' + built.stderr + built.stdout)
    cage_link = {'path': cage_path, 'git_blob': git(publisher, 'hash-object', cage_path)}
    payload['release_cage'] = cage_link
    write(publisher, path, envelope)
    target = publish(publisher, target_tag, '2019-11-02T00:00:00Z')
    # Obtain the raw predictive scenario from the actual publisher CLI.
    stage = root / 'generator-stage'
    stage.mkdir()
    write(stage, 'payload.json', payload)
    write(stage, 'context.json', {'schema': 'publisher-reliability/generator-context-v1',
                               'source': context, 'document': party})
    emitted = subprocess.run([sys.executable, str(publisher / 'threat-register/to_fair_scenario.py'),
        'forecast-base', 'payload.json', 'context.json'], cwd=stage, capture_output=True, text=True)
    if emitted.returncode:
        raise AssertionError('actual publisher forecast-base refused: ' + emitted.stderr)
    base = json.loads(emitted.stdout)
    widened = copy.deepcopy(base)
    for state in ('warn', 'deny'):
        widened[state]['lm'] = [40, 40, 40]
    horizon = {'starts_at': '2020-01-01T00:00:00Z', 'ends_at': '2021-01-01T00:00:00Z',
               'boundary': '[start,end)'}
    unit = {'currency': 'GBP', 'basis': 'explicit synthetic nominal GBP'}
    inventory = {'schema': 'publisher-reliability/price-cases-v1', 'profile_id': 'synthetic-annual',
        'cases': [{'case_id': 'case-one', 'subject': 'driftwood', 'perspective': 'driftwood',
                   'horizon': horizon, 'context_ref': context}]}
    write(publisher, 'price/cases.json', inventory)
    upstream = json.loads((actual['nist'] / 'publisher-reliability/PRICE-UPSTREAM.json').read_text())
    engine = {'party': 'platform', 'tag': upstream['tag'], 'commit': upstream['commit'],
              'path': 'fair/fair.py', 'git_blob': upstream['files'][0]['git_blob']}
    profile = {'schema': 'publisher-reliability/price-profile-v1', 'id': 'synthetic-annual',
        'criterion': 'money-empirical-crps/v1', 'outcome_kind': 'annual-aggregate-loss/v1',
        'target_feed': {'publisher': 'feeds', 'name': 'threat-register'}, 'unit': unit,
        'definition': {'loss_categories': ['synthetic-only'], 'accounting_rule': LABEL,
                       'completeness_rule': 'complete synthetic annual ledger', 'finality_rule': 'settled'},
        'horizon_rule': {'duration': 'P1Y', 'boundary': '[start,end)', 'calendar': 'UTC-Gregorian'},
        'resolver_rule': {'party': 'ico', 'source_schema': 'synthetic-ledger/v1',
            'amount_pointer': '/amount', 'finality_pointer': '/final', 'completeness_pointer': '/complete',
            'evidence_uri_prefix': 'https://fixture.invalid/'},
        'population': {'case_inventory': {'path': 'price/cases.json',
                'git_blob': git(publisher, 'hash-object', 'price/cases.json')},
            'registration_deadline': 'strictly-before-horizon-start', 'aggregation': 'equal-case-mean',
            'overlap_rule': 'distinct-case-subject-horizon-no-overlap'},
        'generator': {'kind': 'pinned-fair-annual-empirical/v1', 'engine': engine, 'state': 'warn',
                      'parameter_policy': 'explicit-per-registration-recorded-not-inferred'}}
    write(publisher, 'price/profile.json', profile)
    write(publisher, 'price/widening.json', {'schema': 'publisher-reliability/widening-v1',
        'id': 'synthetic-widening', 'profile_id': profile['id'], 'unit': unit,
        'authority': 'publisher-loss-model', 'authoritative_value_action': 'preserve',
        'affected_sources': ['/warn/lm', '/deny/lm'], 'citation': LABEL,
        'release_cage': cage_link, 'target': widened})
    declared = publish(publisher, 'price-profile/v1.0.0', '2019-12-01T00:00:00Z')
    scorer = new_repo(sources, 'nist')
    shutil.copytree(actual['nist'] / 'publisher-reliability', scorer / 'publisher-reliability',
        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    shutil.copyfile(actual['nist'] / 'party.yaml', scorer / 'party.yaml')
    generator = {'kind': 'pinned-fair-annual-empirical/v1', 'engine': engine,
        'converter': target('threat-register/to_fair_scenario.py'),
        'invocation': ['forecast-base', 'payload.json', 'context.json'], 'context_ref': context,
        'scenario': base, 'state': 'warn', 'seed': 42, 'iterations': 2}
    forecast = build_forecast(scorer, profile=declared('price/profile.json'), target=target(path),
        case_id='case-one', emitted_at='2019-12-02T00:00:00Z', generator=generator, source_roots=sources)
    write(publisher, 'price/forecast.json', forecast)
    forecast_ref = publish(publisher, 'price-forecast/v1.0.0', '2019-12-03T00:00:00Z')('price/forecast.json')
    resolver = new_repo(sources, 'ico')
    resolution, resolved = None, None
    if unresolved:
        write(resolver, 'README.md', LABEL + '\nNo annual outcome is published in this fixture.\n')
        publish(resolver, 'unresolved/v1.0.0', '2021-01-02T00:00:00Z')
    else:
        write(resolver, 'ledger.json', {'schema': 'synthetic-ledger/v1', 'amount': '30',
            'final': True, 'complete': True, 'case_id': 'case-one', 'subject': 'driftwood',
            'perspective': 'driftwood', 'horizon': horizon, 'unit': unit})
        observed = publish(resolver, 'ledger/v1.0.0', '2021-01-02T00:00:00Z')('ledger.json')
        resolution = build_resolution(scorer, forecast=forecast_ref, profile=declared('price/profile.json'),
            source=observed, resolved_at='2021-01-02T00:00:00Z', published_at='2021-01-03T00:00:00Z',
            evidence_uri='https://fixture.invalid/explicit-synthetic-ledger', source_roots=sources)
        write(resolver, 'resolution.json', resolution)
        resolved = publish(resolver, 'resolution/v1.0.0', '2021-01-03T00:00:00Z')('resolution.json')
    manifest = {'schema': 'publisher-reliability/price-input-set-v1', 'cohorts': [{
        'schema': 'publisher-reliability/price-inputs-v1', 'profile': declared('price/profile.json'),
        'target': target(path), 'cases': [{'case_id': 'case-one', 'forecast': forecast_ref,
                                        'resolution': resolved}]}]}
    report = build_price_report(scorer, manifest, '2021-02-01T00:00:00Z', sources)
    check_price_report(scorer, report, sources)
    report_version = json.loads((scorer / 'publisher-reliability/price-version.json').read_text())['version']
    envelope = {'kind': 'feed', 'name': 'publisher-reliability', 'version': report_version,
        'published_by': 'nist', 'published_at': report['cutoff'],
        'payload_schema': 'publisher-reliability/price-payload.schema.json', 'payload': report}
    write(scorer, 'publisher-reliability/v2/feed.json', envelope)
    report_ref = publish(scorer, 'publisher-reliability/v' + report_version, '2021-02-01T00:00:00Z')(
        'publisher-reliability/v2/feed.json')
    party['inherits'].append({'party': 'nist', 'kind': 'feed', 'name': 'publisher-reliability',
                              'version': 'v2', 'since': '2026-10-18'})
    party['appetite']['publisher_reliability'] = [{
        'schema': 'publisher-reliability/adopter-policy-v1',
        'target_edge': {'party': 'feeds', 'name': 'threat-register', 'version': 'v3'},
        'report': report_ref, 'profile': declared('price/profile.json'),
        'criterion': 'money-empirical-crps/v1', 'unit': unit, 'minimum_cases': 1,
        'aggregation': 'equal-case-mean', 'bar': '-10', 'on_below': 'publisher-widen-to/v1',
        'widening': declared('price/widening.json')}]
    write(adopter, 'party.yaml', yaml.safe_dump(party))
    platform, catalog = root / 'fixture-platform', root / 'fixture-nist'
    ct._write_fixture_platform(platform, actual['platform'], [])
    ct._write_fixture_catalog(catalog)
    trees = {'fixture-platform': platform, 'fixture-nist': catalog,
             'feeds': publisher, 'nist': scorer, 'ico': resolver, 'driftwood': adopter}
    return {'adopter': adopter, 'trees': trees, 'party': party, 'report': report,
            'forecast': forecast, 'resolution': resolution, 'base': base, 'widened': widened,
            'sources': sources, 'ct': ct}
