import pathlib,yaml,json,sys
root=pathlib.Path(sys.argv[1]);out=pathlib.Path(sys.argv[2]);rows={}
for org in ['driftwood','tuppence','ludlow']:
 d=root/(org+'-estate')/org;h=yaml.safe_load((d/'composed/HEADER.yaml').read_text());keys=list(h);obs={k:v for k,v in h.items() if 'observation' in k or 'parent' in k};rows[org]={'header_keys':keys,'header_parent_and_observations':obs,'primary_pin':yaml.safe_load((d/'gitops/flux-system/gotk-sync-feeds.yaml').read_text())['spec']['ref']}
out.write_text(json.dumps(rows,indent=2,default=str)+'\n');print(json.dumps({k:{'keys':v['header_keys'],'pin':v['primary_pin']} for k,v in rows.items()}))
