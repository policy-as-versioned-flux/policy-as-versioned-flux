
from pathlib import Path
import subprocess,json,hashlib,sys,re
out=Path('.scratch/ecosystem/research/resume-2026-10-04');repo=Path('.estate-publish/feeds').resolve();base='974e73514e0d8d4cad2e6906acf51d1cc27028b3';candidate='d62f74e52ed992798a75cf3f4f138ec9c83db80a'
def git(*a):return subprocess.check_output(['git','-C',str(repo),*a])
def sh(b):return hashlib.sha256(b).hexdigest()
head=git('rev-parse','HEAD').decode().strip();assert head==candidate;assert not git('status','--porcelain=v1').decode().strip();assert git('log','-1','--format=%G?').decode().strip()=='G';assert git('rev-parse','HEAD^').decode().strip()==base
tracked=git('ls-tree','-r','--name-only',base).decode().splitlines();oldchecks=[];changed=[]
for n in tracked:
 b=git('show',base+':'+n);current=git('show',candidate+':'+n);assert (repo/n).read_bytes()==current
 if current!=b:changed.append(n)
 if re.fullmatch(r'[^/]+/v[0-9]+/feed.json',n):oldchecks.append({'path':n,'sha256':sh(current),'equals_base':current==b})
assert changed==['fx/bump.yaml'],changed;assert all(x['equals_base'] for x in oldchecks)
added=git('diff','--name-only','--diff-filter=A',base,candidate).decode().splitlines();expected=['fetch/source/hmrc/2025-12.csv','fetch/source/hmrc/2026-08.csv','fetch/source/hmrc/PROVENANCE.json','fetch/source/periods/2025-12/fx.json','fx/README.md','fx/v2/feed.json'];assert sorted(added)==sorted(expected),added
manifest=[{'path':n,'sha256':sh(git('show',candidate+':'+n)),'bytes':len(git('show',candidate+':'+n))} for n in sorted(changed+added)]
patterns={'private_key':rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----','github_token':rb'(?:gh[pousr]_[A-Za-z0-9]{36,255}|github_pat_[A-Za-z0-9_]{70,255})','aws_access_id':rb'(?:AKIA|ASIA)[A-Z0-9]{16}','slack_token':rb'xox[baprs]-[A-Za-z0-9-]{20,}'}
hits=[{'path':n,'pattern':k} for n in changed+added for k,r in patterns.items() if re.search(r,(repo/n).read_bytes())];assert not hits
sys.path.insert(0,str(repo/'fetch'));import fx,lib
prov=json.loads((repo/'fetch/source/hmrc/PROVENANCE.json').read_text());assert sh((repo/'fetch/fx.py').read_bytes())==prov['normalizer_sha256']
old=json.loads((repo/'fx/v1/feed.json').read_text());new=json.loads((repo/'fx/v2/feed.json').read_text());assert new['name']=='fx' and new['kind']=='feed' and new['published_by']=='feeds' and new['version']=='2.0.0';assert new['published_at']=='2026-10-04T00:00:00Z';primary=[]
for period,row in prov['periods'].items():
 raw=(repo/row['raw_csv']).read_bytes();assert sh(raw)==row['raw_sha256'];actual=fx.parse(raw,period,row['source_url']);envelope=new if period=='2025-12' else old;assert actual==envelope['payload'];assert sh(json.dumps(actual,sort_keys=True,separators=(',',':')).encode())==row['normalized_payload_sha256'];assert len(actual['rates'])==row['unique_currency_count'];assert actual['rates']['USD']==row['USD_units_per_GBP1']
 if period=='2025-12':
  assert actual['rates']['USD']==1.3126;assert json.loads((repo/row['offline_replay_payload']).read_text())==actual;assert sh((repo/row['offline_replay_payload']).read_bytes())==row['offline_replay_payload_sha256'];assert sh((repo/row['prepared_envelope']).read_bytes())==row['prepared_envelope_sha256']
 try:fx.parse(raw,'2026-08' if period=='2025-12' else '2025-12',row['source_url'])
 except ValueError as e:assert 'dates do not match' in str(e)
 else:raise AssertionError('parser accepted the wrong month')
 primary.append({'period':period,'raw_sha256':sh(raw),'parsed_payload_semantics_equal':True,'USD_units_per_GBP1':actual['rates']['USD'],'unique_currencies':len(actual['rates']),'wrong_month_parse_refused':True})
rule=lib.load_rule('fx');computed=lib.bump_engine.compute(old,new,rule);assert computed=='major';assert lib.next_version(old['version'],computed)=='2.0.0';removed=sorted(set(old['payload']['rates'])-set(new['payload']['rates']));added_codes=sorted(set(new['payload']['rates'])-set(old['payload']['rates']));assert removed==['VES'] and added_codes==['BGN','VED']
assert new['payload_schema']=='fx/payload.schema.json';assert (repo/'fetch/source/fx.json').read_bytes()==git('show',base+':fetch/source/fx.json');assert json.loads((repo/'fetch/source/fx.json').read_text())==old['payload']
namespace=subprocess.run(['git','-C',str(repo),'show-ref','--verify','--quiet','refs/tags/fx/v2.0.0']).returncode;assert namespace==1,namespace
checks=json.loads((out/'fx2-source-checks.json').read_text());assert checks['checks']['verify-feeds.sh']['exit']==0;assert checks['checks']['verify-market-and-news.sh']['exit']==0;assert checks['checks']['december-offline-primary-replay']['exit']==0
for n in manifest:assert sh((repo/n['path']).read_bytes())==n['sha256']
assert git('rev-parse','HEAD').decode().strip()==candidate and not git('status','--porcelain=v1').decode().strip()
proof={'status':'PASS: exact signed-G FX2 source candidate; no authentic FX2 release yet','review_scope':'independent read-only source/preservation/primary parser/bump review; no external actions','base':base,'branch':git('branch','--show-current').decode().strip(),'head':head,'tree':git('rev-parse','HEAD^{tree}').decode().strip(),'signature':'G','clean':True,'candidate_source_manifest':manifest,'manifest_sha256':sh(json.dumps(manifest,sort_keys=True,separators=(',',':')).encode()),'existing_tracked_paths_byte_exact_except':['fx/bump.yaml'],'tracked_path_count':len(tracked),'frozen_major_envelopes':oldchecks,'default_august_payload_byte_exact':True,'unchanged_fetch_code_uses_current_UTC_month_unless_explicit_FEEDS_FX_PERIOD':True,'explicit_offline_replay_does_not_claim_new_live_fetch':True,'primary_replay':primary,'computed_bump':computed,'normal_next_version':'2.0.0','removed_currencies':removed,'added_currencies':added_codes,'unchanged_catalogue_publishes_fx_namespace':True,'unchanged_payload_schema':True,'local_fx2_namespace_unused':True,'remote_namespace_absence_still_root_release_prerequisite':True,'negative_high_confidence_secret_scan':hits,'native_release_gate_proof':checks,'normal_release_prerequisites':['match exact reviewed source head during ordinary review/merge; cut main only with feed=fx version=2.0.0 after normal remote tag absence check','normal release workflow dispatch at immutable fx/v2.0.0 ref with tag=fx/v2.0.0; verify genuine cut-release main identity, Actions issuer and actual peeled commit','only after authentic receipt update matching exact consumer FX/hub pins, replay actual producers, and recompose; source candidate alone is not signed rate or activation']}
(out/'fx2-source-standards-review.json').write_text(json.dumps(proof,indent=2)+'\n')
(out/'fx2-source-standards-review.md').write_text("""# FX2 source Standards review — 2026-10-04

PASS for exact clean SSH-signed source d62f74e52ed992798a75cf3f4f138ec9c83db80a, tree b88fb77f96cadf1a9639cae369ed529bd4e1731c, based at authentic974e73514e0d8d4cad2e6906acf51d1cc27028b3. [Independent source manifest and checks](fx2-source-standards-review.json) bind all seven changed paths. No source/index edits or external actions by reviewer.

All existing tracked bytes are unchanged except fx/bump.yaml minor→major. Every12 prior-major envelope, default August offline payload, parser, converter, rule, schema, catalogue and workflow is preserved. December is added at fx/v2/feed.json, declaring2.0.0 under the existing FX catalogue/schema path; no duplicate discovery record or payload-shape change is needed.

Independent calls to the actual unchanged fetch/fx.py parser reproduce both complete captured official CSV tables, with matching raw and canonical payload hashes. December supplies USD1.3126 per GBP1 for2025-12; August remains USD1.3367 for2026-08. Each parser call rejects the other month. Explicit December replay matches the envelope; default replay remains byte-exact August. Existing live-fetch code still chooses current UTC month unless an explicit reviewed historical period is supplied. Candidate provenance and README distinguish captured preparation/offline replay from genuine signed release or a new live observation.

The unchanged normal bump engine computes major and next_version yields2.0.0: VES is removed, BGN/VED added. No currency is silently renamed and no rate extrapolated. Native publisher gates and dated/missing-month converter checks pass in the saved exact candidate proof. No high-confidence credential/private-key match in candidate blobs.

No concrete hard finding or consequential smell. Local fx/v2.0.0 tag namespace is unused; root must check real remote absence before normal main cut. Cut inputs are feed=fx, version=2.0.0; release verification must dispatch at immutable ref fx/v2.0.0 with tag=fx/v2.0.0, binding genuine signer identity/issuer and peeled source commit. Consumer FX pins and corrected hub producer replay wait for that authentic receipt. Source preparation itself is not a signed rate or live activation.
""")
print('Independent FX2 review PASS: exact clean signed d62f74e5,7-path manifest,12frozen envelopes, both actual primary parses, normal major, local namespace unused')
