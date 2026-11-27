"""Verify bounded authored compiler evidence from a known GitHub Actions artifact."""
import argparse
from hashlib import sha256
import io
import json
from pathlib import Path, PurePosixPath
import re
import stat
from zipfile import ZipFile


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def review(path, expected_sha, run_id):
    require(path.is_file() and not path.is_symlink() and 0 < path.stat().st_size < 1024*1024,'archive_bounds')
    data=path.read_bytes()
    require(sha256(data).hexdigest()==expected_sha,'archive_digest')
    with ZipFile(io.BytesIO(data)) as z:
        members=z.infolist(); names=[PurePosixPath(i.filename) for i in members]
        require(len(members)==3 and {n.name for n in names}=={'compiler.json','source-tests.log','depth-tests.log'},'archive_population')
        require(all(not n.is_absolute() and '..' not in n.parts and len(n.parts)<=2 for n in names)
                and len({n.parent for n in names})==1,'archive_paths')
        require(all(not i.is_dir() and not stat.S_ISLNK(i.external_attr>>16) and 0<i.file_size<512*1024 for i in members),'member_bounds')
        require(z.testzip() is None,'archive_crc')
        raw={n.name:z.read(i) for i,n in zip(members,names)}
    p=json.loads(raw['compiler.json'])
    required={'status':'PASS_AUTHORED_RESOURCE_METADATA_AND_REAL_SPIRV','run_id':run_id,'synthetic_only':True,
              'actual_compiler_executed':True,'source_parameter_decoder_executed':True,
              'actual_stage_parameter_records_executed':True,'unrelated_cb_mesh_varying_checks_stubbed':True,
              'stage_resource_records_checked':4,'normalized_rebind_equivalence_checks':4,
              'combined_source_identical':True,'negative_wrong_valid_SPIRV_rejected':True,
              'negative_invalid_binding_cases_rejected':2,'Unity_compilation_or_render_verified':False,
              'original_game_assets_read':False,'Android_device_pixels_verified':False,'XAPK_requested':False}
    for k,v in required.items(): require(type(p.get(k)) is type(v) and p[k]==v,'receipt_mismatch:'+k)
    require(p.get('tool_invocations')=={'glslangValidator':14,'spirv-val':14,'spirv-opt':10},'compiler_invocation_population')
    def fingerprint(row):
        return type(row.get('bytes')) is int and row['bytes']>0 and bool(re.fullmatch('[0-9a-f]{64}',row.get('sha256','')))
    forms=p['forms'];require([f['form'] for f in forms]==['bare','space0'],'register_forms')
    for f in forms:
        require(f['metadata_stage_records']==2 and f['texture_bindings']==2 and f['sampler_bindings']==2,'resource_population')
        require(fingerprint(f['parameter_blob']) and fingerprint(f['combined_hlsl']),'source_commitment')
        require([r['stage'] for r in f['normalized_comparisons']]==['vs','fs'] and
                all(r['baseline_and_rebound_identical'] is True and fingerprint(r['normalized_spirv']) for r in f['normalized_comparisons']),'normalized_comparison')
        require([r['entrypoint'] for r in f['combined_compiled_stages']]==['gt_vs_main','gt_fs_main'] and
                all(fingerprint(r['spirv']) for r in f['combined_compiled_stages']),'combined_compiled_stages')
    require(forms[0]['parameter_blob']==forms[1]['parameter_blob'] and forms[0]['combined_hlsl']==forms[1]['combined_hlsl'],'form_byte_commitment_drift')
    require(set(p['versions'])=={'glslangValidator','spirv-val','spirv-opt'} and all(type(s) is str and s for s in p['versions'].values()),'compiler_versions')
    for name,count in [('source-tests.log',10),('depth-tests.log',3)]:
        s=raw[name].decode('utf-8'); require(re.search(r'Ran '+str(count)+r' tests? in ',s) and s.rstrip().endswith('OK') and len(re.findall(r' \.\.\. ok$',s,re.M))==count,'unit_test_log:'+name)
    return {'archive_sha256':expected_sha,'archive_bytes':len(data),'run_id':run_id,'members':{k:{'bytes':len(v),'sha256':sha256(v).hexdigest()} for k,v in sorted(raw.items())},'receipt':p,'unit_tests':13,'receipt_consistency_verified_locally':True,'compiler_reexecuted_locally':False,'run_authenticity_requires_github_job_identity':True}


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--archive',required=True,type=Path);ap.add_argument('--sha256',required=True);ap.add_argument('--run-id',required=True);ap.add_argument('--out',required=True,type=Path);a=ap.parse_args()
    require(not a.out.exists(),'fresh_output_required')
    result=review(a.archive,a.sha256,a.run_id);a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(json.dumps(result,sort_keys=True))
