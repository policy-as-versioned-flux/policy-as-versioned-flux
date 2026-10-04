import sys,importlib.util,pathlib,yaml,json
root=pathlib.Path(sys.argv[1]);out=pathlib.Path(sys.argv[2]);results={}
for org in ['driftwood','tuppence','ludlow']:
 d=root/(org+'-estate')/org
 spec=importlib.util.spec_from_file_location('lookup',root/'driftwood-estate/driftwood/.github/scripts/rederive-signals.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);p=(d/'party.yaml').read_text();s=(d/'twin/signals.yaml').read_text();v,changes=m.rederive(p,s,'2026-10-04');assert v==s and not changes
 party=yaml.safe_load(p);lookup=yaml.safe_load(s);scenarios={q.stem for q in (d/'twin/orgs'/org/'scenarios').glob('*.yaml')};rows=lookup['signals'];assert all(r['signal']['scenario'] in scenarios for r in rows)
 engine=yaml.safe_load((d/'gitops/engine/kyverno.yaml').read_text());assert engine['version']=='1.18.2'
 claims=[]
 for f in [d/'deploy/pod.yaml',*(d/'gitops/apps').glob('*.yaml')]:
  for doc in yaml.safe_load_all(f.read_text()):
   if isinstance(doc,dict) and doc.get('kind')=='Pod':
    claim=doc.get('metadata',{}).get('labels',{}).get('policy-as-versioned.dev/policy-version');assert claim=='7.0.0';claims.append({'path':str(f.relative_to(d)),'claim':claim})
 results[org]={'signal_lookup_exact':True,'all_binding_scenarios_exist':True,'source_claims':claims,'engine':'1.18.2','composed_self_pin_retained':yaml.safe_load_all((d/'gitops/composed/composed-set.yaml').read_text()).__next__()['spec']['ref'],'inventory_sha256':__import__('hashlib').sha256((d/'inventory/images.json').read_bytes()).hexdigest()}
 out.write_text(json.dumps(results,indent=2)+'\n');print(org+': exact lookup/claims/engine declarations PASS')
