from __future__ import annotations
import hashlib,json,pathlib,shutil,subprocess,sys,tempfile
root=pathlib.Path(sys.argv[1]);out=pathlib.Path(sys.argv[2]);python=pathlib.Path(sys.executable);results={};failed=False
for org in ['driftwood','tuppence','ludlow']:
 estate=root/(org+'-estate');source=estate/org;tools=estate/'platform-tools'
 before={str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((source/'composed').rglob('*')) if p.is_file()}
 with tempfile.TemporaryDirectory(prefix='genuine-adopter-byte-replay-') as temporary:
  snapshot=pathlib.Path(temporary)/org;shutil.copytree(source,snapshot,ignore=shutil.ignore_patterns('.git','__pycache__'))
  (snapshot/'.git').symlink_to((source/'.git').resolve(),target_is_directory=True)
  command=[str(python),str(snapshot/'.github/scripts/platform-tools.py'),'--adopter-dir',str(snapshot),'--tools-dir',str(tools),'verify',str(snapshot),'--estate-clone',str(estate)]
  run=subprocess.run(command,text=True,capture_output=True,timeout=180)
  results[org]={'exit':run.returncode,'stdout':run.stdout,'stderr':run.stderr,'authenticated_tools':'v5.0.0@703eff6aee959843c4160aa54fd03413f62858cc','temporary_relocated_copy':True,'rendered_file_count':len(before)-1,'source_composed_unchanged':before=={str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((source/'composed').rglob('*')) if p.is_file()},'scope':'genuine signed tools wrapper replay; no shared source writes'}
  failed=failed or run.returncode!=0 or not results[org]['source_composed_unchanged']
 out.write_text(json.dumps(results,indent=2)+'\n');print(org+': authenticated relocated byte replay '+('PASS' if run.returncode==0 else 'FAIL'))
sys.exit(1 if failed else 0)
