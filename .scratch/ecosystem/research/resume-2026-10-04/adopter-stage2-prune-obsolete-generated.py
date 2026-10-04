import sys, json, pathlib, yaml, hashlib
root=pathlib.Path(sys.argv[1]);hub=pathlib.Path(sys.argv[2]);out=pathlib.Path(sys.argv[3]);results={}
for org in ['driftwood','tuppence','ludlow']:
 estate=root/(org+'-estate');adopter=estate/org;tools=estate/'platform-tools';sys.path.insert(0,str(tools/'compose'))
 import composition
 party=yaml.safe_load((adopter/'party.yaml').read_text());parents={e['party']:estate/e['party'] for e in party['inherits']};header=yaml.safe_load((adopter/'composed/HEADER.yaml').read_text());doc,rendered=composition.compose(adopter,parents,as_of=header.get('composition-as-of'),replay_observations=True)
 assert doc['outcome']=='composed' and not doc['refusals']
 obsolete=[]
 for p in sorted((adopter/'composed').rglob('*')):
  if not p.is_file(): continue
  rel=str(p.relative_to(adopter))
  if rel not in rendered and rel!='composed/evidence.json': obsolete.append({'path':rel,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 for row in obsolete:(adopter/row['path']).unlink()
 for p in sorted((adopter/'composed').rglob('*'),reverse=True):
  if p.is_dir() and not any(p.iterdir()):p.rmdir()
 results[org]={'removed_only_obsolete_generated_outputs':obsolete,'expected_rendered_count':len(rendered),'expected_sha256':{p:hashlib.sha256(b.encode()).hexdigest() for p,b in sorted(rendered.items())}}
 sys.path.pop(0)
out.write_text(json.dumps(results,indent=2)+'\n');print(json.dumps({k:{'removed':len(v['removed_only_obsolete_generated_outputs']),'rendered':v['expected_rendered_count']} for k,v in results.items()}))
