"""Read real pinned source snapshots; no quote rendering or remote mutation."""
from pathlib import Path
import hashlib, importlib.util, json, os, subprocess, tempfile
import yaml
E = Path(__file__).resolve().parent
H = E.parents[3]
R = Path('/private/tmp/pavf-insurer-maintenance-20261004')
P = H / '.estate-publish/platform'
BASE = '8d4a5ae684e4a58c8242bc8b6e50794473ef302b'
TOOLS = '703eff6aee959843c4160aa54fd03413f62858cc'
LOC = json.loads((E / 'adopter-stage2-isolated.json').read_text())['adopters']
def git(repo, *a): return subprocess.check_output(['git','-C',str(repo),*a])
def sha(b): return hashlib.sha256(b).hexdigest()
assert git(R,'rev-parse','HEAD').decode().strip() == BASE
assert git(P,'rev-parse','v5.0.0^{commit}').decode().strip() == TOOLS
assert git(R,'diff','--name-only').decode().splitlines() == ['gitops/platform/platform-pin.yaml','party.yaml']
old = yaml.safe_load(git(R,'show',BASE+':party.yaml'))
new = yaml.safe_load((R/'party.yaml').read_text())
assert old['inherits'][0]['version']=='3.3.0' and new['inherits'][0]['version']=='5.0.0'
old['inherits'][0]['version']='5.0.0'
assert old==new
before = list(yaml.safe_load_all(git(R,'show',BASE+':gitops/platform/platform-pin.yaml')))
after = list(yaml.safe_load_all((R/'gitops/platform/platform-pin.yaml').read_text()))
assert len(after)==1 and after[0]['kind']=='GitRepository'
assert after[0]['spec']['ref']=={'tag':'v5.0.0','commit':TOOLS}
before[0]['spec']['ref']=after[0]['spec']['ref']
assert before==after
pub=yaml.safe_load(git(P,'show','v5.0.0:party.yaml'))
record=next(e for e in pub['publishes'] if e['kind']=='implementations')
assert record['name']=='cloud'
assert not git(P,'ls-tree','-r','--name-only','v3.3.0',record['path']).strip()
assert git(P,'ls-tree','-r','--name-only','v5.0.0',record['path']).strip()
paths=git(R,'ls-tree','-r','--name-only',BASE).decode().splitlines()
preserved={}
for path in paths:
 if path not in ('party.yaml','gitops/platform/platform-pin.yaml'):
  b=git(R,'show',BASE+':'+path)
  assert (R/path).read_bytes()==b,path
  preserved[path]=sha(b)
result={'scope':'pure-consumer parent declaration; no cloud activation, quote render, release or live observation',
        'base':BASE,'compatible_published_tools_commit':TOOLS,'implementation_record':record,
        'all_other_committed_bytes_preserved':preserved,'snapshots':{}}
spec=importlib.util.spec_from_file_location('insurer_quote',R/'pricing/quote.py')
q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
with tempfile.TemporaryDirectory(prefix='pavf-insurer-pin-snapshots-') as t:
 t=Path(t); oldrepo=t/'before-insurer';oldrepo.mkdir()
 (oldrepo/'party.yaml').write_bytes(git(R,'show',BASE+':party.yaml'))
 (oldrepo/'terms').mkdir()
 for path in (R/'terms').glob('*.yaml'):(oldrepo/'terms'/path.name).write_bytes(path.read_bytes())
 for label,tag in (('old','v3.3.0'),('new','v5.0.0')):
  d=t/label/'party';d.mkdir(parents=True)
  (d/'pin_content.py').write_bytes(git(P,'show',tag+':party/pin_content.py'))
 adopters=t/'adopters'
 for org,loc in LOC.items():
  repo=Path(loc['dir']);dst=adopters/org;(dst/'composed').mkdir(parents=True)
  for path in ('party.yaml','composed/HEADER.yaml'):(dst/path).write_bytes(git(repo,'show','v2.0.0:'+path))
  tag=git(repo,'rev-parse','v2.0.0').decode().strip()
  commit=git(repo,'rev-parse','v2.0.0^{commit}').decode().strip()
  outcomes={}
  for label,repo_source in (('old',oldrepo),('new',R)):
   q.REPO=str(repo_source);q.PLATFORM_DIR=str(t/label)
   try:
    payload=q.payload(org,str(adopters))
    outcomes[label]={'kind':'priced','payload':payload}
   except q.Refused as exc:outcomes[label]={'kind':'Refused','reason':str(exc)}
  if outcomes['old']['kind']=='priced' and outcomes['new']['kind']=='priced':
   prior=json.loads(json.dumps(outcomes['old']['payload']))
   prior['priced_against'][0]['version']='5.0.0'
   assert prior==outcomes['new']['payload'],org
   effects='only platform priced_against version changes; numeric quote and signed terms identical'
  else:
   assert outcomes['old']==outcomes['new'],outcomes
   effects='same typed missing-instrument refusal; neither parent invents a quote'
  result['snapshots'][org]={'actual_tag':'v2.0.0','tag_object':tag,'commit':commit,
      'HEADER_sha256':sha((dst/'composed/HEADER.yaml').read_bytes()),'terms_sha256':sha((R/'terms'/f'{org}.yaml').read_bytes()),
      'outcomes':outcomes,'measured_effect':effects}
result['pin_content_old_new_byte_equal']=git(P,'show','v3.3.0:party/pin_content.py')==git(P,'show','v5.0.0:party/pin_content.py')
(E/'insurer-compatible-platform-pin-snapshot-check.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps({org:row['measured_effect'] for org,row in result['snapshots'].items()},indent=2))
