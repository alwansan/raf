"""Authored FFT coordinate compiler diagnostic; no source game assets or player build."""
import argparse
import ast
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
NAME = 'Hidden/RAFT/AuthoredFFTCoordinateProbe'
PRAGMA = '#pragma use_dxc vulkan\n'
MODES = ('dxc', 'hlslcc')
EXPRESSIONS = (
    '_ProbeTex.Sample(sampler_ProbeTex, i.uv)',
    '_ProbeTex.Sample(sampler_ProbeTex, float4(i.uv.yx, 0.25, 0.75).yx)',
    '_ProbeTex.SampleLevel(sampler_ProbeTex, asfloat(asuint(i.uv) ^ uint2(0u, 0x80000000u)), 0.0)',
    '_ProbeTex.Sample(sampler_ProbeTex, float2(asfloat(asint(i.uv.x) ^ (-2147483647 - 1)), i.uv.y))',
    '_ProbeTex.SampleLevel(sampler_ProbeTex, float2(int2(i.uv * 4.0)) * 0.25, 0.0)',
    '_ProbeTex.SampleLevel(sampler_ProbeTex, float2(uint2(abs(i.uv) * 4.0)) * 0.25, 0.0)',
    '_ProbeTex.Load(int3(int2(i.uv * 4.0), 0))',
)


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def digest(data):
    return sha256(data).hexdigest()


def write_json(path, data):
    with path.open('x', encoding='utf-8') as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write('\n')


def production_builders():
    path = ROOT / 'scripts/gt_fft_utilities_restore.py'
    tree = ast.parse(path.read_text(encoding='utf-8'))
    names = {'attach_programs', 'compiler_control'}
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    require({n.name for n in nodes} == names, 'production_builders_missing')
    env = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), 'exec'), env)
    return env


def bodies():
    result = []
    for index, expr in enumerate(EXPRESSIONS):
        result.append('Texture2D<float4> _ProbeTex;\nSamplerState sampler_ProbeTex;\n'
            'struct Input { float4 vertex : POSITION; float2 uv : TEXCOORD0; };\n'
            'struct Varying { float4 pos : SV_POSITION; float2 uv : TEXCOORD0; };\n'
            'Varying gt_vs_main(Input v) { Varying o; o.pos=v.vertex; '
            f'o.uv=v.uv+float2({index}.0/16.0,0.0); return o; }}\n'
            f'float4 gt_fs_main(Varying i) : SV_Target {{ return {expr} * {index+1}.0/8.0; }}\n')
    return result


def shaders():
    build = production_builders()
    layout = ('Shader "'+NAME+'" {\nProperties { _ProbeTex ("Authored texels", 2D) = "white" {} }\nSubShader {\n' +
              ''.join('Pass { Cull Off ZWrite Off ZTest Always\n// Original stage programs attach here\n}\n' for _ in EXPRESSIONS) + '}\nFallback Off\n}\n')
    dxc = build['attach_programs'](layout, bodies())
    modes = {m: build['compiler_control'](dxc,m).encode() for m in MODES}
    require(modes['dxc'].count(PRAGMA.encode()) == 7 and modes['dxc'].replace(PRAGMA.encode(),b'') == modes['hlslcc'], 'compiler_control_not_exact')
    return modes


def command(args, *, ok=True):
    p = subprocess.run([str(a) for a in args], capture_output=True, timeout=90)
    if ok and p.returncode:
        raise ValueError('tool_failed:'+str(args[0])+':'+(p.stdout+p.stderr).decode(errors='replace')[-1800:])
    return p


def sample_ops(asm):
    rows = []
    for line in asm.splitlines():
        fields = line.split(';',1)[0].split()
        if len(fields) >= 6 and fields[1] == '=' and (fields[2].startswith('OpImageSample') or fields[2]=='OpImageFetch'):
            rows.append((fields[2],fields[5]))
    return rows


def wrong_coordinate(asm, expected):
    """Insert a legal equal-width bitcast and alter only the image coordinate."""
    lines = asm.splitlines()
    defs = {}
    targets = []
    for i,line in enumerate(lines):
        parts=line.split(';',1)[0].split()
        if len(parts)>=3 and parts[1]=='=':
            defs[parts[0]]=parts[2:]
            if parts[2].startswith('OpImageSample') or parts[2]=='OpImageFetch':
                targets.append((i,parts))
    require(len(targets)==1 and not any(k.startswith('%gt_bad_') for k in defs), 'one_unmodified_image_operation_required')
    at,parts=targets[0]
    require((parts[2]=='OpImageFetch') == (expected=='fetch'), 'wrong_image_operation_family')
    coord=parts[5]
    typ=defs[coord][1]
    vector=defs[typ]
    require(vector[0]=='OpTypeVector' and vector[2]=='2', 'two_coordinate_lanes_required')
    scalar=defs[vector[1]]
    require(scalar[0]==('OpTypeInt' if expected=='fetch' else 'OpTypeFloat') and scalar[1]=='32', 'unexpected_valid_coordinate_type')
    wanted=['OpTypeFloat','32'] if expected=='fetch' else ['OpTypeInt','32','1']
    new=[]
    scalar_id=next((k for k,v in defs.items() if v==wanted),None)
    if scalar_id is None:
        scalar_id='%gt_bad_scalar';new.append(scalar_id+' = '+' '.join(wanted))
    wanted_vector=['OpTypeVector',scalar_id,'2']
    vector_id=next((k for k,v in defs.items() if v==wanted_vector),None)
    if vector_id is None:
        vector_id='%gt_bad_vector';new.append(vector_id+' = '+' '.join(wanted_vector))
    parts[5]='%gt_bad_coord'
    lines[at:at+1]=['%gt_bad_coord = OpBitcast '+vector_id+' '+coord,' '.join(parts)]
    fn=next(i for i,line in enumerate(lines) if re.search(r'=\s+OpFunction\b',line))
    lines[fn:fn]=new
    return '\n'.join(lines)+'\n'


def cpu_probe(out):
    rows=[]; negatives=[]
    with tempfile.TemporaryDirectory(prefix='gt-fft-authored-') as d:
        root=Path(d)
        for i,body in enumerate(bodies()):
            source=root/f'pass{i}.hlsl'; source.write_text(body)
            for stage,entry in (('vert','gt_vs_main'),('frag','gt_fs_main')):
                module=root/f'{i}-{stage}.spv'
                command(['glslangValidator','-V','-D','-S',stage,'-e',entry,'-o',module,source])
                command(['spirv-val','--target-env','vulkan1.1',module])
                asm=command(['spirv-dis','--raw-id',module]).stdout.decode()
                ops=sample_ops(asm)
                expected='fetch' if i==6 else 'sample'
                require(not ops if stage=='vert' else len(ops)==1 and ((ops[0][0]=='OpImageFetch')==(expected=='fetch')), 'cpu_image_operation_mismatch')
                rows.append({'pass':i,'stage':stage,'sha256':digest(module.read_bytes()),'image_ops':[op for op,_ in ops]})
                if stage=='frag' and i in (0,6):
                    bad=root/f'bad-{i}.spvasm';bad.write_text(wrong_coordinate(asm,expected))
                    binary=bad.with_suffix('.spv')
                    command(['spirv-as','--target-env','vulkan1.1',bad,'-o',binary])
                    p=command(['spirv-val','--target-env','vulkan1.1',binary],ok=False)
                    msg=(p.stdout+p.stderr).decode(errors='replace')
                    reason=r'coordinate.*(?:int|integer)' if expected=='fetch' else r'coordinate.*float'
                    require(p.returncode != 0 and re.search(reason,msg,re.I), 'wrong_coordinate_not_rejected_for_expected_type')
                    negatives.append({'pass':i,'family':expected,'validator_exit':p.returncode,'diagnostic':msg.strip()[:1200]})
        write_json(out,{'status':'PASS_AUTHORED_COORDINATE_COMPILER_CONTROLS','stages':rows,'negative_controls':negatives,'actual_compiler_executed':True,'original_assets_read':False})


def stage(project, results, mode, run_id):
    require(mode in MODES and bool(run_id) and not project.exists() and not results.exists() and not project.is_symlink() and not results.is_symlink(), 'fresh_project_results_required')
    require(not project.resolve().is_relative_to(results.resolve()) and not results.resolve().is_relative_to(project.resolve()), 'separate_paths_required')
    results.mkdir(parents=True)
    source=shaders()[mode]
    cpu_probe(results/'cpu.json')
    editor=(ROOT/'android-port/Experiments/GT/Editor/FFTUtilitiesShaderValidation.cs').read_bytes()
    files={'Assets/GTFFTUtilities.shader':source,'Assets/Editor/FFTUtilitiesShaderValidation.cs':editor,
           'CandidateCompiler.txt':(mode+'\n').encode(),'CandidateSha256.txt':(digest(source)+'\n').encode(),
           'Packages/manifest.json':b'{"dependencies":{}}\n','ProjectSettings/ProjectVersion.txt':b'm_EditorVersion: 2021.3.45f2\n'}
    for path,data in files.items():
        p=project/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    write_json(results/'stage.json',{'status':'PREPARED','mode':mode,'run_id':run_id,'synthetic_only':True,'Unity_executed':False,
        'source_sha256':digest(source),'editor_sha256':digest(editor),'cpu_sha256':digest((results/'cpu.json').read_bytes()),
        'compiler_control_only_seven_pragmas':True,'pass_count':7,'original_assets_read':False})
    (project/'SourceReceipt.json').write_bytes((results/'stage.json').read_bytes())
    (results/'authored.shader').write_bytes(source)


def verify(project, results, decoder, mode, run_id, exit_code):
    sys.path.insert(0,str(ROOT))
    from scripts.gt_verify_921_shader_bundle import _decode_fft_empty_routes
    from scripts.gt_fft_receipt_contract import verify_commitments, verify_original_commitments, require_same_decoded_receipt
    source=(results/'authored.shader').read_bytes(); cpu=(results/'cpu.json').read_bytes()
    stage_info=json.loads((results/'stage.json').read_text())
    require(source==shaders()[mode] and source==(project/'Assets/GTFFTUtilities.shader').read_bytes(), 'source_changed')
    require(stage_info['run_id']==run_id and stage_info['mode']==mode and stage_info['source_sha256']==digest(source) and stage_info['cpu_sha256']==digest(cpu), 'stage_identity_mismatch')
    receipt_path=project/'ProbeResults/gt-fft-utilities-unity-safe.json'
    receipt=receipt_path.read_bytes(); (results/'unity.json').write_bytes(receipt); u=json.loads(receipt)
    expected={'unityVersion':'2021.3.45f2','checkpoint':'compiler_results','candidateSha256':digest(source),'compilerControl':mode,'passCount':7,'registeredKeywordVariants':1,'errors':0,'androidVulkanOnly':True,'privateBundleCompiled':True,'originalMaterialGuidProven':False,'gamePlayerBuilt':False,'devicePixelsProven':False}
    require(type(exit_code) is int and exit_code==0,'Unity_exit_failure')
    for k,v in expected.items():require(type(u.get(k)) is type(v) and u[k]==v,'Unity_receipt_mismatch:'+k)
    bundle=(project/'ProbeResults/Private/gt-fft-utilities').read_bytes();require(0<len(bundle)<8*1024*1024,'bundle_size')
    stage_raw=(results/'stage.json').read_bytes()
    require(stage_raw==(project/'SourceReceipt.json').read_bytes(), 'source_receipt_changed')
    _,_,commitments=verify_commitments(source,stage_raw,receipt,bundle)
    routes,detail=_decode_fft_empty_routes(bundle,NAME,decoder,authored_coordinate_profile=True)
    controls=[]
    def must_reject(name, expected_reason, operation):
        try:
            operation()
        except ValueError as exc:
            require(str(exc)==expected_reason, 'wrong_receipt_control_reason:'+name+':'+str(exc))
            controls.append({'name':name,'reason':str(exc),'rejected':True})
        else:
            raise ValueError('receipt_control_accepted:'+name)
    def mutate(data):
        i=len(data)//2
        return data[:i]+bytes([data[i]^1])+data[i+1:]
    def whitespace_mutation(data):
        changed=data.replace(b'\n',b' ',1)
        require(len(changed)==len(data) and changed!=data and json.loads(changed)==json.loads(data),
                'valid_same_size_JSON_mutation_required')
        return changed
    must_reject('same_size_candidate','fft_unity_receipt:candidateSha256',
                lambda: verify_commitments(mutate(source),stage_raw,receipt,bundle))
    must_reject('same_size_source_receipt','fft_unity_receipt:sourceReceiptSha256',
                lambda: verify_commitments(source,whitespace_mutation(stage_raw),receipt,bundle))
    must_reject('same_size_bundle','fft_unity_receipt:bundleSha256',
                lambda: verify_commitments(source,stage_raw,receipt,mutate(bundle)))
    legacy=dict(u);legacy.pop('receiptSchemaVersion')
    must_reject('legacy_receipt','fft_unity_receipt:receiptSchemaVersion',
                lambda: verify_commitments(source,stage_raw,json.dumps(legacy).encode(),bundle))
    stale=dict(u);stale['bundleBytes']=len(bundle)+1
    must_reject('wrong_bundle_size','fft_unity_receipt:bundleBytes',
                lambda: verify_commitments(source,stage_raw,json.dumps(stale).encode(),bundle))
    changed_receipt=whitespace_mutation(receipt)
    _,_,changed_commitments=verify_commitments(source,stage_raw,changed_receipt,bundle)
    must_reject('changed_unity_receipt_bytes','fft_decoded_receipt_does_not_match_actual_bundle',
                lambda: require_same_decoded_receipt(commitments,changed_commitments))
    must_reject('authored_not_original','fft_source_receipt:status',
                lambda: verify_original_commitments(source,stage_raw,receipt,bundle))
    modules={m['sha256']:m for m in detail['modules']}
    passes=[]
    fragment_blobs=set()
    for p in detail['passes']:
        rows=p['stages']['progFragment']['rows']
        fragment_blobs.update(row['blob_index'] for row in rows)
        found=[modules[h] for row in rows for h in row['module_sha256']]
        require(bool(found),'missing_fragment_proof')
        passes.append({'pass':p['pass'],'fragment_modules':found})
    (results/'authored.bundle').write_bytes(bundle)
    write_json(results/'verified.json',{'status':'PASS_AUTHORED_UNITY_ANDROID_VULKAN_COORDINATES','mode':mode,'run_id':run_id,
        'source_sha256':digest(source),'unity_receipt_sha256':digest(receipt),'bundle_sha256':digest(bundle),'bundle_bytes':len(bundle),
        'routes':routes,'passes':passes,'validated_fragment_referenced_blobs':len(fragment_blobs),'actual_android_bundle':True,
        'receipt_v2_commitments':commitments,'receipt_negative_controls':controls,'original_game_or_device_pixels_verified':False,'XAPK_requested':False})


class Tests(unittest.TestCase):
    def test_authored_operations(self):
        self.assertEqual(len(bodies()),7)
        self.assertEqual(sum('.Load(' in b for b in bodies()),1)
        self.assertEqual(sum('.Sample' in b for b in bodies()),6)
        self.assertEqual(len(set(bodies())),7)
    def test_mutation(self):
        asm='%f = OpTypeFloat 32\n%v = OpTypeVector %f 2\n%fun = OpFunction %void None %ft\n%coord = OpLoad %v %var\n%r = OpImageSampleImplicitLod %v4 %image %coord\nOpFunctionEnd\n'
        result=wrong_coordinate(asm,'sample')
        self.assertIn('%gt_bad_scalar = OpTypeInt 32 1',result)
        self.assertIn('%gt_bad_coord = OpBitcast %gt_bad_vector %coord',result)
        self.assertEqual(sample_ops(result),[('OpImageSampleImplicitLod','%gt_bad_coord')])
        with self.assertRaises(ValueError):wrong_coordinate(result,'sample')
    def test_fetch(self):
        asm='%i = OpTypeInt 32 1\n%v = OpTypeVector %i 2\n%f = OpTypeFloat 32\n%fv = OpTypeVector %f 2\n%fun = OpFunction %void None %ft\n%coord = OpLoad %v %var\n%r = OpImageFetch %v4 %image %coord Lod %zero\nOpFunctionEnd\n'
        result=wrong_coordinate(asm,'fetch')
        self.assertIn('%gt_bad_coord = OpBitcast %fv %coord',result)
        self.assertIn('%r = OpImageFetch %v4 %image %gt_bad_coord Lod %zero',result)
        with self.assertRaises(ValueError):wrong_coordinate(asm,'sample')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('selftest','stage','verify'));p.add_argument('--project',type=Path);p.add_argument('--results',type=Path);p.add_argument('--decoder',type=Path);p.add_argument('--mode',choices=MODES);p.add_argument('--run-id');p.add_argument('--exit-code',type=int);a=p.parse_args()
    if a.action=='selftest':unittest.main(argv=[sys.argv[0],'-v'])
    elif a.action=='stage':stage(a.project,a.results,a.mode,a.run_id)
    else:verify(a.project,a.results,a.decoder,a.mode,a.run_id,a.exit_code)
