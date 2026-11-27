"""Real compiler regression for authored texture/sampler metadata and space0.

No game inputs. Exercise production stage_parameter_records, the real binary
parameter reader, source name registry, rebind and Unity declaration merger.
Only non-resource CB/mesh/varying verification is stubbed in the stage fixture;
this result is not their proof, a Unity run, or game/Android rendering evidence.
"""
import argparse
import ast
import base64
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import types
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.gt_original_921_all_variants import stage_parameter_records
from scripts.gt_original_921_resource_rebind import rebind_resources, verify_rebound_resources
from scripts.gt_resource_register_contract import strip_registered_resources

TOOLS = ('glslangValidator', 'spirv-val', 'spirv-opt')


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def production_symbols(path, names, **scope):
    tree = ast.parse((ROOT / path).read_text(encoding='utf-8'), filename=path)
    nodes = [node for node in tree.body if (
        isinstance(node, ast.FunctionDef) and node.name in names or
        isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in names for t in node.targets))]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), path, 'exec'), scope)
    require(all(n in scope for n in names), 'missing_production_symbol')
    return scope


def module(name, **values):
    obj = types.ModuleType(name)
    obj.__dict__.update(values)
    return obj


def fingerprint(path):
    data = path.read_bytes()
    return {'bytes':len(data), 'sha256':sha256(data).hexdigest()}


def packed_name(name):
    b = name.encode('ascii')
    return struct.pack('<i', len(b)) + b + b'\0' * (-len(b) % 4)


def parameter_blob():
    # One authored zero-size group, no CB parameters, one texture override.
    return (struct.pack('<ii',202012090,1) + packed_name('SyntheticGlobal') +
            struct.pack('<iiii',0,0,0,1) + packed_name('_MainTex') + struct.pack('<iiiI',0,3,7,4))


def stage_source(stage, explicit):
    tex, sampler = (21,16) if stage == 'vert' else (9,4)
    space = ', space0' if explicit else ''
    head = f'Texture2D<float4> t3 : register(t{tex}{space});\nSamplerState s7 : register(s{sampler}{space});\n'
    if stage == 'vert':
        return head + '''struct AuthoredInput { float4 pos : POSITION; float2 uv : TEXCOORD0; };
struct AuthoredOutput { float4 pos : SV_POSITION; float2 uv : TEXCOORD0; };
AuthoredOutput main(AuthoredInput i) {
    AuthoredOutput o; o.pos = i.pos;
    o.pos.x += t3.SampleLevel(s7, i.uv, 0.0).r / 1024.0;
    o.uv = i.uv; return o;
}
'''
    return head + '''float4 main(float2 uv : TEXCOORD0) : SV_Target0 { return t3.Sample(s7, uv); }
'''


def run_probe(out, run_id):
    require(not out.exists() and not out.is_symlink() and bool(run_id), 'fresh_output_and_run_id_required')
    for tool in TOOLS:
        require(shutil.which(tool) is not None, 'required_compiler_missing:' + tool)
    commands = Counter()
    def command(argv):
        result = subprocess.run(argv, capture_output=True, text=True, timeout=45)
        commands[Path(argv[0]).name] += 1
        if result.returncode:
            print((result.stdout+'\n'+result.stderr)[-4000:], file=sys.stderr)
        return result.returncode == 0
    def compile_stage(source, binary, stage, entry='main'):
        require(command(['glslangValidator','-V','-D','-S',stage,'-e',entry,'-o',str(binary),str(source)]), 'compile_failed')
        require(command(['spirv-val','--target-env','vulkan1.1',str(binary)]), 'spirv_validation_failed')

    registry = production_symbols('scripts/b25_foam_cb_namebridge.py', ['original_name_registry'], re=re)['original_name_registry']
    assembler = production_symbols('scripts/gt_original_921_shaderlab.py',
        ['unity_resource_bindings','combine_stages','TOP_LEVEL','HELPER','GLOBAL','MEMBER','PACKOFFSET','ordered_buffer'],
        re=re, strip_registered_resources=strip_registered_resources)
    modules = {}
    for name, fields in (
        ('scripts.b25_foam_cb_namebridge', {'original_name_registry':registry}),
        ('scripts.w1_recover_graphics_programs', {'command':command}),
        ('scripts.gt_original_921_cb_hlsl', {'verify_named_constant_buffers':lambda *a,**k:0}),
        ('scripts.gt_original_921_cb_layout', {'bind_constant_buffers':lambda *a:[], 'constant_buffer_lanes':lambda *a:[]}),
        ('scripts.gt_original_921_semantics', {'verify_varyings':lambda *a:0, 'verify_vertex_inputs':lambda *a:0,
                                              'verify_vulkan_varying_pair':lambda *a:0}),
    ):
        modules[name] = module(name, **fields)
    variants, combined_bytes = [], []
    binding_expected = [{'kind':'t','slot':3,'source_texture_name':'_MainTex'},
                        {'kind':'s','slot':7,'source_texture_name':'_MainTex'}]
    with tempfile.TemporaryDirectory(prefix='gt-authored-resource-') as tmp, patch.dict(sys.modules,modules):
        root = Path(tmp)
        for label, explicit in (('bare',False),('space0',True)):
            folder = root/label; folder.mkdir()
            program = {'m_ParameterBlobIndices':[[0]], 'm_CommonParameters':{'m_TextureParams':[
                {'m_Index':3,'m_NameIndex':11,'m_SamplerIndex':7},
                {'m_Index':5,'m_NameIndex':12,'m_SamplerIndex':9}]}}
            passes = [{'subshader':0,'pass':0,'original_vertex_program':program,'original_fragment_program':program,
                       'original_name_indices':[('_OldTex',11),('_UnusedTex',12)]}]
            pair = {'subshader':0,'pass':0}
            for key,stage in (('vs','vert'),('fs','frag')):
                program_dir=folder/key; program_dir.mkdir()
                source=program_dir/'private.hlsl'; source.write_text(stage_source(stage,explicit),encoding='utf-8')
                (program_dir/'source.dxbc').write_bytes(b'authored-non-DXBC-placeholder-for-stubbed-varying-check')
                compile_stage(source,program_dir/'roundtrip.spv',stage)
                pair[key]={'program_ref':key,'player_bucket':0,'bucket_ordinal':0}
            raw=parameter_blob()
            report=stage_parameter_records([pair],[],passes,[(None,raw)],folder,{'vs':'vs','fs':'fs'})
            packet=json.loads((folder/'original-private-parameter-records.json').read_text())
            require(report['original_variant_stages_with_parameter_records']==2 and
                    report['translated_texture_declarations_mapped_to_source_name']==2 and
                    report['translated_sampler_declarations_mapped_to_source_texture']==2,
                    'stage_record_population')
            require(packet['blobs_base64']['0']==base64.b64encode(raw).decode(), 'parameter_blob_commitment')
            require(len(packet['stage_records'])==2 and all(row['source_texture_sampler_bindings']==binding_expected
                    for row in packet['stage_records']), 'source_slot_metadata_mapping_drift')
            stages, normalized = [], []
            for i,key in enumerate(('vs','fs')):
                bound=folder/f'bound-stage-{i:03d}'
                before=bound/'resource-baseline-normalized.spv'; after=bound/'resource-bound-normalized.spv'
                require(before.read_bytes()==after.read_bytes() and before.stat().st_size>0, 'rebind_changed_SPIRV')
                hlsl=(bound/'resource-bound.hlsl').read_text()
                original=(folder/key/'private.hlsl').read_text()
                require(re.findall(r'register\([^)]*\)',hlsl)==re.findall(r'register\([^)]*\)',original), 'translated_register_changed')
                require('_MainTex' in hlsl and 'sampler_MainTex' in hlsl and '_OldTex' not in hlsl, 'name_override_drift')
                text=assembler['unity_resource_bindings'](hlsl,key)
                require('register(' not in text,'register_annotation_not_stripped')
                text,n=re.subn(r'\bmain(?=\s*\()',f'gt_{key}_main',text)
                require(n==1,'entrypoint_drift'); stages.append(text)
                normalized.append({'stage':key,'baseline_and_rebound_identical':True,'normalized_spirv':fingerprint(after)})
            combined=assembler['combine_stages'](*stages)
            require(combined.count('Texture2D<float4> _MainTex;')==1 and
                    combined.count('SamplerState sampler_MainTex;')==1,'cross_stage_resource_declaration_not_shared')
            final=folder/'combined.hlsl'; final.write_text(combined,encoding='utf-8')
            compiled=[]
            for key,stage in (('vs','vert'),('fs','frag')):
                binary=folder/(key+'.spv'); compile_stage(final,binary,stage,'gt_'+key+'_main')
                compiled.append({'stage':key,'entrypoint':'gt_'+key+'_main','spirv':fingerprint(binary)})
            combined_bytes.append(final.read_bytes())
            variants.append({'form':label,'metadata_stage_records':2,'texture_bindings':2,'sampler_bindings':2,
                             'parameter_blob':{'bytes':len(raw),'sha256':sha256(raw).hexdigest()},
                             'normalized_comparisons':normalized,'combined_hlsl':fingerprint(final),'combined_compiled_stages':compiled})
        require(combined_bytes[0]==combined_bytes[1], 'space0_and_bare_combined_shader_differ')
        # Positive compile + wrong-but-valid baseline; production equivalence gate must reject it.
        bad=root/'bad_baseline';bad.mkdir()
        (bad/'private.hlsl').write_text(stage_source('frag',True),encoding='utf-8')
        wrong=bad/'different.hlsl'; wrong.write_text(stage_source('frag',True).replace('t3.Sample(s7, uv)','t3.Sample(s7, uv).bgra'),encoding='utf-8')
        compile_stage(wrong,bad/'roundtrip.spv','frag')
        try:
            verify_rebound_resources(bad,0,binding_expected,root/'negative-bound')
        except ValueError as e:
            require(str(e)=='original_resource_rebound_changed_spirv','negative_control_failed_for_wrong_reason:'+str(e))
        else:
            raise ValueError('negative_wrong_program_accepted')
        # Exact invalid-space and metadata failures at the production binder.
        for source,bindings in ((stage_source('frag',True).replace('space0','space1'),binding_expected),
                                (stage_source('frag',True),binding_expected[:1])):
            try: rebind_resources(source,bindings)
            except ValueError: pass
            else: raise ValueError('invalid_binding_accepted')
    result={'status':'PASS_AUTHORED_RESOURCE_METADATA_AND_REAL_SPIRV', 'run_id':run_id,
            'synthetic_only':True,'actual_compiler_executed':True,'source_parameter_decoder_executed':True,
            'actual_stage_parameter_records_executed':True,'unrelated_cb_mesh_varying_checks_stubbed':True,
            'forms':variants,'stage_resource_records_checked':4,'normalized_rebind_equivalence_checks':4,
            'combined_source_identical':True,'negative_wrong_valid_SPIRV_rejected':True,
            'negative_invalid_binding_cases_rejected':2,'tool_invocations':dict(commands),
            'versions':{tool:subprocess.check_output([tool,'--version'],text=True).splitlines()[0] for tool in TOOLS},
            'Unity_compilation_or_render_verified':False,'original_game_assets_read':False,
            'Android_device_pixels_verified':False,'XAPK_requested':False}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps(result,sort_keys=True))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--run-id',required=True)
    args=parser.parse_args()
    run_probe(args.out,args.run_id)
