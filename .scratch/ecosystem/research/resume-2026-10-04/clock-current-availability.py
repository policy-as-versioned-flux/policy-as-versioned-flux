"""Read-only current clock availability; workflow success is not a new-source baseline."""
from pathlib import Path
import base64
import datetime
import hashlib
import json
import subprocess
import sys

HUB = Path('/Users/cns/httpdocs/controlplane/policy-as-versioned-flux')
E = HUB / '.scratch/ecosystem/research/resume-2026-10-04'
sys.path.insert(0, str(HUB / 'talk'))
from truth_manifest import parse_truth

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

report = {'started_at': now(), 'scope': 'Read-only public Actions metadata and committed primary observation availability',
    'workflow_success_is_not_qualified_new_source_PolicyReport_baseline': True,
    'new_qualifying_baseline_established_by_this_audit': False,
    'no_dispatch_trigger_or_external_mutation': True,
    'historical_record_preserved': 'adopter-stage2-clock-availability.json', 'adopters': {}, 'hub': {}}
out = E / 'clock-current-availability.json'

def save():
    report['last_read_at'] = now()
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')

def api(endpoint):
    command = ['gh', 'api', endpoint]
    result = subprocess.run(command, capture_output=True, text=True, timeout=25)
    if result.returncode:
        raise RuntimeError(result.stderr.strip())
    return json.loads(result.stdout)

def run_summary(run):
    fields = ['id', 'event', 'status', 'conclusion', 'head_sha', 'head_branch', 'created_at', 'updated_at', 'html_url']
    return {key: run.get(key) for key in fields}

def content(repo, path, ref):
    data = api(f'repos/{repo}/contents/{path}?ref={ref}')
    if data.get('encoding') == 'base64' and data.get('content') is not None:
        body = base64.b64decode(data['content'])
    else:
        result = subprocess.run(['gh', 'api', '-H', 'Accept: application/vnd.github.raw+json',
            f'repos/{repo}/contents/{path}?ref={ref}'], capture_output=True, timeout=25)
        if result.returncode:
            raise RuntimeError(result.stderr.decode().strip())
        body = result.stdout
    return {'path': path, 'ref': ref, 'blob_sha': data['sha'],
        'sha256': hashlib.sha256(body).hexdigest(), 'bytes': len(body)}, body.decode()

save()
for org in ['driftwood', 'tuppence', 'ludlow']:
    repo = f'policy-as-versioned-{org}/{org}'
    row = {'repository': repo, 'reads': {}, 'errors': []}
    report['adopters'][org] = row
    try:
        data = api(f'repos/{repo}/actions/workflows/drift-sample.yml/runs?event=schedule&per_page=3')
        row['latest_scheduled_runs'] = [run_summary(run) for run in data['workflow_runs']]
    except Exception as error:
        row['errors'].append({'read': 'latest_scheduled_runs', 'error': str(error)})
    save()
    try:
        main = api(f'repos/{repo}/git/ref/heads/main')['object']['sha']
        row['main_at_read'] = main
        metadata, text = content(repo, 'drift/samples.jsonl', main)
        row['reads']['samples'] = metadata
        samples = [json.loads(line) for line in text.splitlines() if line.strip()]
        if samples:
            latest_run = samples[-1].get('run')
            latest = [sample for sample in samples if sample.get('run') == latest_run]
            row['latest_committed_sample_run'] = latest_run
            row['latest_committed_samples'] = [{'ts': sample.get('ts'), 'run': sample.get('run'),
                'source': sample.get('source'), 'revision': sample.get('revision'), 'pin': sample.get('pin'),
                'verdict': sample.get('verdict'),
                'rendered_from': sample.get('facts', {}).get('fact_4_rendered_objects_byte_equal_to_an_offline_render', {}).get('rendered_from'),
                'policy_version_in_force': sample.get('facts', {}).get('fact_6_the_bottom_rung_is_admitted_and_runs', {}).get('policy_version_in_force')}
                for sample in latest]
        row['qualified_new_source_PolicyReport_baseline'] = 'Not established: retained five-facts samples and successful workflow metadata alone do not prove a new-source PolicyReport baseline.'
    except Exception as error:
        row['errors'].append({'read': 'committed_samples', 'error': str(error)})
    save()
    print('READ:', org, flush=True)

repo = 'policy-as-versioned-flux/policy-as-versioned-flux'
hub = report['hub']
hub['repository'] = repo
hub['errors'] = []
try:
    data = api(f'repos/{repo}/actions/workflows/truth.yml/runs?event=schedule&per_page=3')
    hub['latest_scheduled_truth_runs'] = [run_summary(run) for run in data['workflow_runs']]
except Exception as error:
    hub['errors'].append({'read': 'latest_scheduled_truth_runs', 'error': str(error)})
save()
try:
    main = api(f'repos/{repo}/git/ref/heads/main')['object']['sha']
    hub['main_at_read'] = main
    metadata, text = content(repo, 'talk/truth.log', main)
    hub['truth_log'] = metadata
    lines = [line for line in text.splitlines() if line.startswith('TRUTH ')]
    hub['latest_truth_line'] = lines[-1] if lines else None
    hub['latest_truth_parsed'] = parse_truth(lines[-1]) if lines else None
    modern = [line for line in lines if all(parse_truth(line).get(key) is not None
        for key in ['split', 'skip_split', 'ceiling', 'enact'])]
    hub['latest_modern_truth_line'] = modern[-1] if modern else None
    hub['latest_modern_truth_parsed'] = parse_truth(modern[-1]) if modern else None
    for name, path in [('grades', 'talk/captures/_grades.tsv'),
        ('step4', 'talk/captures/verify_e2e_verify-e2e-step4-flux-reconciles-cage.out')]:
        try:
            info, body = content(repo, path, main)
            hub[name] = info
            if name == 'grades':
                hub['step4_grade_rows'] = [line for line in body.splitlines() if 'step4-flux-reconciles-cage' in line]
            else:
                hub['step4_capture_tail'] = body.splitlines()[-25:]
        except Exception as error:
            hub['errors'].append({'read': name, 'error': str(error)})
except Exception as error:
    hub['errors'].append({'read': 'committed_truth', 'error': str(error)})
report['completed_at'] = now()
save()
print('Saved clock-current-availability.json; no new-source live PolicyReport baseline inferred.', flush=True)
