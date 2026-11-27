"""Check authored DXC/HLSLcc control archives against the exact GitHub run."""
import argparse
from hashlib import sha256
import io
import json
from pathlib import Path, PurePosixPath
import re
import stat
from zipfile import ZipFile

PRAGMA = b'#pragma use_dxc vulkan\n'
MODES = ('dxc', 'hlslcc')
EDITOR_VERSION = '2021.3.45f2'


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def digest(data):
    return sha256(data).hexdigest()


def fingerprint(data):
    return {'bytes':len(data),'sha256':digest(data)}


def parse(data):
    def pairs(items):
        result={}
        for k,v in items:
            require(k not in result,'duplicate_json_key')
            result[k]=v
        return result
    def invalid(_):
        raise ValueError('nonfinite_json')
    return json.loads(data.decode('utf-8'),object_pairs_hook=pairs,parse_constant=invalid)


def exact_fields(obj, fields):
    for k,v in fields.items():
        require(type(obj.get(k)) is type(v) and obj[k]==v,'field_mismatch:'+k)


def read_archive(path, expected_sha):
    require(path.is_file() and not path.is_symlink() and 0<path.stat().st_size<16*1024*1024,'archive_bounds')
    data=path.read_bytes();require(digest(data)==expected_sha,'archive_digest')
    with ZipFile(io.BytesIO(data)) as z:
        entries=z.infolist(); names=[PurePosixPath(i.filename) for i in entries]
        require(3<=len(entries)<=6 and len(set(n.name for n in names))==len(entries),'archive_population')
        require(all(not n.is_absolute() and '..' not in n.parts and len(n.parts)<=2 for n in names) and len({n.parent for n in names})==1,'archive_paths')
        require(all(not i.is_dir() and not stat.S_ISLNK(i.external_attr>>16) and 0<i.file_size<8*1024*1024 for i in entries),'archive_members')
        require(z.testzip() is None,'archive_crc')
        raw={n.name:z.read(i) for n,i in zip(names,entries)}
    require({'cpu.json','stage.json','authored.shader'}<=raw.keys()<={'cpu.json','stage.json','authored.shader','unity.json','authored.bundle','verified.json'},'archive_member_names')
    return data,raw


def review(path, expected_sha, run_id, mode, job_success):
    data,raw=read_archive(path,expected_sha)
    cpu,stage=(parse(raw[k]) for k in ('cpu.json','stage.json'))
    source=raw['authored.shader'];source_hash=digest(source)
    exact_fields(stage,{'status':'PREPARED','mode':mode,'run_id':run_id,'synthetic_only':True,'Unity_executed':False,
                        'source_sha256':source_hash,'cpu_sha256':digest(raw['cpu.json']),'compiler_control_only_seven_pragmas':True,
                        'pass_count':7,'original_assets_read':False})
    require(source.count(PRAGMA)==(7 if mode=='dxc' else 0) and source.count(b'HLSLPROGRAM')==7 and source.count(b'ENDHLSL')==7,'source_topology')
    exact_fields(cpu,{'status':'PASS_AUTHORED_COORDINATE_COMPILER_CONTROLS','actual_compiler_executed':True,'original_assets_read':False})
    require([(r['pass'],r['stage']) for r in cpu['stages']]==[(i,s) for i in range(7) for s in ('vert','frag')],'stage_population')
    for row in cpu['stages']:
        require(bool(re.fullmatch('[0-9a-f]{64}',row['sha256'])),'stage_digest')
        ops=row['image_ops']; require(ops==[] if row['stage']=='vert' else len(ops)==1 and (ops[0]=='OpImageFetch' if row['pass']==6 else ops[0].startswith('OpImageSample')),'cpu_operation_family')
    require([(n['pass'],n['family']) for n in cpu['negative_controls']]==[(0,'sample'),(6,'fetch')],'negative_control_population')
    for n in cpu['negative_controls']:
        require(type(n['validator_exit']) is int and n['validator_exit']!=0 and re.search(r'coordinate.*(?:float)' if n['family']=='sample' else r'coordinate.*(?:int|integer)',n['diagnostic'],re.I),'negative_control_diagnostic')
    result={'archive':fingerprint(data),'mode':mode,'run_id':run_id,'members':{k:fingerprint(v) for k,v in sorted(raw.items())},
            'cpu_valid_stages':len(cpu['stages']),'negative_controls':cpu['negative_controls'],
            'job_success':job_success,'bundle_acceptance':False,'local_compiler_or_Unity_reexecution':False,'local_bundle_decoder_reexecution':False}
    if 'unity.json' in raw:
        u=parse(raw['unity.json']);exact_fields(u,{'unityVersion':EDITOR_VERSION,'candidateSha256':source_hash,'compilerControl':mode,
                                                'gamePlayerBuilt':False,'devicePixelsProven':False,'originalMaterialGuidProven':False})
        result['unity_receipt']=u
    if 'verified.json' in raw:
        require('unity.json' in raw and 'authored.bundle' in raw,'verified_missing_inputs')
        v=parse(raw['verified.json']);bundle=raw['authored.bundle']
        exact_fields(v,{'status':'PASS_AUTHORED_UNITY_ANDROID_VULKAN_COORDINATES','mode':mode,'run_id':run_id,'source_sha256':source_hash,
                        'unity_receipt_sha256':digest(raw['unity.json']),'bundle_sha256':digest(bundle),'bundle_bytes':len(bundle),
                        'actual_android_bundle':True,'original_game_or_device_pixels_verified':False,'XAPK_requested':False})
        exact_fields(u,{'checkpoint':'compiler_results','errors':0,'passCount':7,'registeredKeywordVariants':1,'androidVulkanOnly':True,'privateBundleCompiled':True})
        exact_fields(v['routes'],{'vulkan_platform_only':True,'compiled_program_table_verified':True,'vertex_routes_by_pass':[1]*7,'fragment_routes_by_pass':[1]*7})
        require([p['pass'] for p in v['passes']]==list(range(7)),'compiled_pass_population')
        for p in v['passes']:
            require(bool(p['fragment_modules']),'missing_fragment_module')
            for m in p['fragment_modules']:
                require(4 in m['models'] and bool(re.fullmatch('[0-9a-f]{64}',m['sha256'])),'fragment_model_or_digest')
                ops=m['image_ops']; require(len(ops)==1 and (ops[0]=='OpImageFetch' if p['pass']==6 else ops[0].startswith('OpImageSample')),'bundle_image_operation_family')
        if u.get('receiptSchemaVersion') == 2:
            exact_fields(u, {'candidateBytes':len(source),'sourceReceiptSha256':digest(raw['stage.json']),
                'bundleSha256':digest(bundle),'bundleBytes':len(bundle),'failureType':''})
            exact_fields(v['receipt_v2_commitments'], {
                'receipt_schema_version':2,'candidate_sha256':source_hash,'candidate_bytes':len(source),
                'source_receipt_sha256':digest(raw['stage.json']),'unity_receipt_sha256':digest(raw['unity.json']),
                'bundle_sha256':digest(bundle),'bundle_bytes':len(bundle),
                'unity_receipt_byte_commitments_verified':True,'cryptographic_attestation_verified':False})
            require(len(v['receipt_negative_controls'])==7 and all(c['rejected'] is True for c in v['receipt_negative_controls']),
                    'receipt_negative_controls_missing')
        result['verified']=v
        result['bundle_acceptance']=job_success
    if job_success:
        require(result['bundle_acceptance'],'successful_job_without_verified_bundle')
    return result,source


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run-id-prefix',required=True)
    for m in MODES:
        p.add_argument('--'+m,type=Path,required=True);p.add_argument('--'+m+'-sha256',required=True);p.add_argument('--'+m+'-job-success',type=int,choices=(0,1),required=True)
    p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    require(not a.out.exists() and not a.out.is_symlink(),'fresh_output_required')
    rows={};sources={}
    for m in MODES:
        rows[m],sources[m]=review(getattr(a,m),getattr(a,m+'_sha256'),a.run_id_prefix+'-'+m,m,bool(getattr(a,m+'_job_success')))
    require(sources['dxc'].replace(PRAGMA,b'')==sources['hlslcc'],'different_control_bodies')
    result={'schema_version':1,'modes':rows,'exact_pragma_only_control':True,'original_failure_reproduced_by_Unity':None,
            'original_game_or_device_pixels_verified':False,'XAPK_requested':False,'execution_authenticity_requires_matching_GitHub_jobs':True}
    a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'exact_pragma_only_control':True,'acceptances':{k:v['bundle_acceptance'] for k,v in rows.items()}},sort_keys=True))
