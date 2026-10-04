import pathlib,yaml,json,sys
root=pathlib.Path(sys.argv[1]);out=pathlib.Path(sys.argv[2]);rows={}
for org in ['driftwood','tuppence','ludlow']:
 d=root/(org+'-estate')/org;h=yaml.safe_load((d/'composed/HEADER.yaml').read_text());doc=json.loads((d/'composed/evidence.json').read_text());feeds=[{'party':r.get('party'),'name':r.get('name'),'version':r.get('version'),'source_last_edit_sha':r.get('sha'),'publisher_observation':r.get('publisher_observation'),'header_record_keys':list(r)} for r in h.get('vendored-feeds',[]) if r.get('party')=='feeds'];rows[org]={'checkout_and_pin':'974e73514e0d8d4cad2e6906acf51d1cc27028b3','header_feeds':feeds,'document_publisher_observations':[r.get('publisher_observation') for r in doc.get('vendored',[]) if r.get('party')=='feeds']}
out.write_text(json.dumps(rows,indent=2,default=str)+'\n');print(json.dumps(rows,indent=2))
