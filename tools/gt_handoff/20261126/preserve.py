from pathlib import Path
import json,hashlib,shutil,zipfile,subprocess,re,os
repo=Path('/home/a/Documents/Codex/2026-11-13/new-chat/work/raf')
work=Path('/home/a/Documents/Codex/2026-11-20/new-chat-2/work')
oldwork=repo.parent
base=repo/'clients/GT/sessions/20261126-complete-handoff'
for d in ['history','evidence/local','tests','toolchain','inventory']:(base/d).mkdir(parents=True,exist_ok=True)
hashit=lambda b:hashlib.sha256(b).hexdigest()
# Preserve remote and interrupted local restore narratives independently.
shutil.copyfile(repo/'clients/GT/RESTORE_AR.md',base/'history/RESTORE_REMOTE_BEFORE_HANDOFF_AR.md')
shutil.copyfile(work/'pre-handoff-local-restore.md',base/'history/RESTORE_LOCAL_BEFORE_HANDOFF_AR.md')
imported=Path('/home/a/Downloads/RESTORE_AR.md')
if imported.exists():shutil.copyfile(imported,base/'history/RESTORE_IMPORTED_AR.md')
source_files=['gt-fft-utilities-safe.json','gt-fft-utilities-safe-v2.json','gt-fft-utilities-hlslcc-safe.json','gt-fft-coordinate-types-safe.json']
for n in source_files:
 p=oldwork/n
 if p.exists():
  json.loads(p.read_text());shutil.copyfile(p,base/'evidence/local'/n)
shutil.copyfile(work/'next23b-compose-44783011957-safe.json',base/'evidence/local/next23b-compose-44783011957-safe.json')
# Exact historical test receipts, including baseline reruns, not new tests.
for n in ['results.json','baseline-results.json']:
 shutil.copyfile(work/'isolated-tests'/n,base/'tests'/('historical-'+n))
log_inputs=[(p,'isolated-tests/'+p.name) for p in sorted((work/'isolated-tests').glob('*.log'))]
for n in ['isolated-tests-summary.log','fft-seven-red.log','foam-tests.log','foam-red.log','full-tests.log','t5-historical.log','unitypy-install.log']:
 p=work/n
 if p.exists():log_inputs.append((p,n))
patterns=[re.compile(rb'gh[pousr]_[A-Za-z0-9]{20,}'),re.compile(rb'github_pat_[A-Za-z0-9_]{30,}'),re.compile(rb'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----')]
rows=[]
archive=base/'tests/historical-test-logs.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p,name in log_inputs:
  data=p.read_bytes()
  if any(pattern.search(data) for pattern in patterns):raise ValueError('potential credential in historical receipt')
  zi=zipfile.ZipInfo(name,date_time=(2026,11,20,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED
  z.writestr(zi,data)
  rows.append(dict(member=name,bytes=len(data),sha256=hashit(data)))
(base/'tests/historical-test-logs-manifest.json').write_text(json.dumps({'historical':True,'archive':archive.name,'sha256':hashit(archive.read_bytes()),'members':rows},indent=2)+'\n')
(base/'toolchain/python-freeze-historical.txt').write_text(subprocess.check_output([str(oldwork/'unity-reader/bin/python'),'-m','pip','freeze'],text=True))
(base/'toolchain/source-free-requirements.txt').write_text('PyYAML==6.0.3\npillow==13.0.0\n')
packages=[]
for p in sorted((oldwork/'debs').glob('*.deb')):packages.append(dict(filename=p.name,bytes=p.stat().st_size,sha256=hashit(p.read_bytes())))
tar=oldwork/'unity-src/unitypy-1.23.0.tar.gz'
(base/'toolchain/versions-and-checksums.json').write_text(json.dumps({'python':'3.12.3','Unity':'2021.3.45f2','UnityPy':'1.23.0 loaded via PYTHONPATH source tree, not pip-installed in historical freeze','UnityPy_sdist':{'filename':tar.name,'bytes':tar.stat().st_size,'sha256':hashit(tar.read_bytes()),'official_url':'https://files.pythonhosted.org/packages/c9/8d/b5f68af949762edad75b3fb2eb304640ebd2b919eb2f3594f8ae865b0ca4/unitypy-1.23.0.tar.gz'},'smolv_source_commit':'6303e979b59153ee7007fd14e06d3fed8687b64c','AssetRipper_historical_source_commit':'036098ab525a3f9f693dc101edeb21faad4d32d8','local_arm64_deb_packages':packages,'dependencies_vendored':False,'private_game_assets_vendored':False,'historical_compiler_path':'work/debs/root/usr/bin','historical_library_path':'work/debs/root/usr/lib/aarch64-linux-gnu'},indent=2)+'\n')
tools=repo/'tools/gt_handoff/20261126';tools.mkdir(parents=True,exist_ok=True)
for n in ['run-tests-isolated.py','port_post23_native.py']:shutil.copyfile(work/n,tools/n)
# Machine-readable runtime fidelity audit, using the current actual scripts.
keyword_rows=[]
for label in ['30','23','18','17','15','11','10p33','10p31','7p11','7p33']:
 p=repo/('scripts/gt_translate_next_remaining_'+label+'_shader48.py');s=p.read_text()
 keyword_rows.append({'group':'NEXT'+label,'source_script':str(p.relative_to(repo)),'compose_call_lines':[i+1 for i,l in enumerate(s.splitlines()) if 'compose(' in l],'private_compile_selector_mode':bool(re.search(r'compose\(private,\s*engine_keywords=False\)',s)),'original_runtime_keyword_selection_verified':False})
(base/'evidence/ten-group-runtime-keyword-audit.json').write_text(json.dumps({'read_only_review':True,'date':'2026-11-26','source_base':'f3c8a2cdacf04fdbfbced5f87a1407da223e3a15','mechanism':'compose(engine_keywords=False) emits private GT_ORIGINAL_921_Pn_Vn; absence selects route0; original material keywords do not select the remaining source permutations','groups':keyword_rows,'material_census_is_pixel_or_runtime_proof':False},indent=2)+'\n')
missing={'search_roots':['/home/a/Documents/Codex','/home/a/Downloads','/mnt/data'],'available_in_this_checkout':False,'reconstruct_missing_bytes_from_hashes':False,'remote_narrative_preserved':'history/RESTORE_REMOTE_BEFORE_HANDOFF_AR.md','items':[{'name':'raft-batch3-synthetic-bindings/','verification_summary_sha256':'d5f08e9519b19e9f118ba46d3246f1f0ab9441417ce017c13b509277ce12474e','historical_claim':'two local Vulkan runs /240 pixels; raw execution receipts not present here'},{'name':'raft-batch4-resource-metadata/','verification_summary_sha256':'6536ae8fd8caef25c9fd0942aa0c1b42e4bf7f887c12bbdfc63916473fec62cc','historical_claim':'two local Vulkan runs /240 pixels; adapter.py and upstream candidate patch not present here','upstream_candidate_patch_sha256':'247217382b6d87655fb9da24bbc0d699038456f943a0acf906831c7a4100d150','candidate_sha256':'7ae5c42ffe7630709dee27d046bdc38d9424bfb774e601e5cd8027431b410a24'},{'name':'raft-batch5-local-recovery-20261126.zip','sha256':'a7b0a80c25c753f6e081f9307c804575399d833e5deec5ff338ef4ceee5222a6','test_file':'raft-batch5-stage-enumeration/test_enumeration.py','test_file_sha256':'73f532759de1541d782a9955ec415669718040d48ca5d09c8ea03539ff9628ca','tests_log_sha256':'3bac234ddbc3e96c5d3b3c156185765d67788464930a2a3d163640933c26cc32','historical_claim':'15 isolated enumeration tests; actual production stage_parameter_records not executed'}]}
(base/'inventory/KNOWN_MISSING_LOCAL_ARTIFACTS.json').write_text(json.dumps(missing,indent=2)+'\n')
print(json.dumps({'historical_log_members':len(rows),'archive_bytes':archive.stat().st_size,'evidence_files':len(list(base.rglob('*.*'))),'missing_historical_batches':len(missing['items'])}))
