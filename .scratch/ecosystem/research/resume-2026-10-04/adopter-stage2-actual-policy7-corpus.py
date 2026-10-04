import sys,json,pathlib,tempfile,hashlib
root=pathlib.Path(sys.argv[1]);out=pathlib.Path(sys.argv[2]);results={};failed=False
for org in ['driftwood','tuppence','ludlow']:
 estate=root/(org+'-estate');tools=estate/'platform-tools';adopter=estate/org;sys.path.insert(0,str(tools/'computed-semver'));import engine_compatibility as e
 binary='/private/tmp/pavf-kyverno-engines/1.18.2/kyverno';bodies,other=e.bodies_in(adopter/'composed/policies/v7.0.0')
 with tempfile.TemporaryDirectory(prefix='actual-adopter-policy7-corpus-') as temporary:
  rows=[e._grade_body(b,tools/'computed-semver/engine-fixtures/v7.0.0'/b['family'],tools/'graded/tests'/b['family'] if b['family'] in e.LEGACY_FAMILIES else None,'7.0.0',binary,pathlib.Path(temporary)) for b in bodies]
 results[org]={'engine':'1.18.2','binary_sha256':hashlib.sha256(pathlib.Path(binary).read_bytes()).hexdigest(),'scope':'actual composed7 bodies against genuine policy7 published fixtures; offline only','bodies':rows,'outcome':'passed' if rows and all(r['outcome']=='passed' for r in rows) else 'failed'}
 failed=failed or results[org]['outcome']!='passed';sys.path.pop(0)
 out.write_text(json.dumps(results,indent=2)+'\n')
 print(org+': '+results[org]['outcome']+' ('+str(len(rows))+' actual policy7 bodies)')
sys.exit(1 if failed else 0)
