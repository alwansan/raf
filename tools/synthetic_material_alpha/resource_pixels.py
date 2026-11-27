"""Render an authored shader emitted by the real resource metadata compiler probe."""
import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
SHADER = 'Assets/SyntheticResourcePixels.shader'
PROBE = 'Assets/Editor/SyntheticResourcePixelValidation.cs'
W = H = 4
TEXELS = {'A':[(.125,.75,.25,0),(.875,.25,.75,1)],
          'B':[(.5,.125,1,.5),(.25,.875,.125,1)],
          'white':[(1,1,1,1)]*2,'decoy':[(.75,0,1,1),(0,1,0,1)]}
CASES = [('A_point','A','Point','Clamp'),('A_linear','A','Bilinear','Clamp'),
         ('A_repeat','A','Bilinear','Repeat'),('B_point','B','Point','Clamp'),
         ('B_linear','B','Bilinear','Clamp'),('A_point_after_B','A','Point','Clamp'),
         ('white_substitute','white','Point','Clamp'),('decoy_as_main','decoy','Point','Clamp')]
BG = (.125,.25,.5,1)
SETTINGS = '''%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!129 &1
PlayerSettings:
  m_ObjectHideFlags: 0
  serializedVersion: 26
  companyName: SyntheticValidation
  productName: SyntheticResourcePixels
  m_ActiveColorSpace: 1
'''
HEADER = b'''Shader "Hidden/RAFT/SyntheticResourcePixels" {
Properties {
 [NoScaleOffset] _MainTex ("Authored main", 2D) = "white" {}
 [NoScaleOffset] _OldTex ("Authored decoy", 2D) = "white" {}
}
SubShader { Tags { "Queue"="Transparent" "RenderType"="Transparent" }
Pass { Cull Off ZWrite Off ZTest Always Blend SrcAlpha OneMinusSrcAlpha, One OneMinusSrcAlpha
HLSLPROGRAM
#pragma target 5.0
#pragma only_renderers vulkan
#pragma vertex gt_vs_main
#pragma fragment gt_fs_main
'''
TAIL = b'\nENDHLSL\n} }\nFallback Off\n}\n'


def require(ok, why):
    if not ok:
        raise ValueError(why)


def digest(data):
    return sha256(data).hexdigest()


def source_factory(stage, explicit):
    # Source slots t3/s7, distinct translated ordinals for each stage.
    t,s = (21,16) if stage=='vert' else (9,4)
    space = ', space0' if explicit else ''
    head = f'Texture2D<float4> t3 : register(t{t}{space});\nSamplerState s7 : register(s{s}{space});\n'
    if stage=='vert':
        return head+'''struct AuthoredInput { float4 pos : POSITION; float2 uv : TEXCOORD0; };
struct AuthoredOutput { float4 pos : SV_POSITION; float2 uv : TEXCOORD0; float marker : TEXCOORD1; };
AuthoredOutput main(AuthoredInput i) {
    AuthoredOutput o; o.pos = i.pos; o.uv = i.uv;
    o.marker = t3.SampleLevel(s7, float2(0.625, 0.5), 0.0).r;
    return o;
}
'''
    return head+'''float4 main(float2 uv : TEXCOORD0, float marker : TEXCOORD1) : SV_Target0 {
    float4 c = t3.Sample(s7, uv); return float4(marker, c.gba);
}
'''


def shader_bytes(combined):
    require(combined.count(b'Texture2D<float4> _MainTex;')==1 and combined.count(b'SamplerState sampler_MainTex;')==1,
            'shared_named_resource_missing')
    require(b'_OldTex' not in combined and b'register(' not in combined, 'wrong_binding_in_combined_source')
    require(b'_MainTex.SampleLevel(sampler_MainTex,' in combined and b'_MainTex.Sample(sampler_MainTex,' in combined,
            'both_sampling_stages_required')
    return HEADER+combined+TAIL


def check_compiler(report, combined, run_id):
    required={'status':'PASS_AUTHORED_RESOURCE_METADATA_AND_REAL_SPIRV','run_id':run_id,'synthetic_only':True,
              'actual_compiler_executed':True,'source_parameter_decoder_executed':True,
              'actual_stage_parameter_records_executed':True,'unrelated_cb_mesh_varying_checks_stubbed':True,
              'stage_resource_records_checked':4,'normalized_rebind_equivalence_checks':4,'combined_source_identical':True,
              'negative_wrong_valid_SPIRV_rejected':True,'negative_invalid_binding_cases_rejected':2,
              'Unity_compilation_or_render_verified':False,'original_game_assets_read':False,'Android_device_pixels_verified':False,'XAPK_requested':False}
    for k,v in required.items():
        require(type(report.get(k)) is type(v) and report[k]==v,'compiler_commitment:'+k)
    require(report['tool_invocations']=={'glslangValidator':14,'spirv-val':14,'spirv-opt':10},'compiler_counts')
    forms=report['forms']; require([f['form'] for f in forms]==['bare','space0'],'compiler_forms')
    for f in forms:
        require(f['combined_hlsl']=={'bytes':len(combined),'sha256':digest(combined)},'compiler_combined_hash')
        require(f['metadata_stage_records']==2 and f['texture_bindings']==2 and f['sampler_bindings']==2,'compiler_binding_counts')
        require([r['stage'] for r in f['normalized_comparisons']]==['vs','fs'] and all(r['baseline_and_rebound_identical'] is True for r in f['normalized_comparisons']),'compiler_equivalence')
        require([r['entrypoint'] for r in f['combined_compiled_stages']]==['gt_vs_main','gt_fs_main'],'compiler_entries')


def stage(project, results, run_id):
    require(bool(run_id) and not project.exists() and not project.is_symlink() and not results.exists() and not results.is_symlink(),'fresh_project_and_results_required')
    require(not project.resolve().is_relative_to(results.resolve()) and not results.resolve().is_relative_to(project.resolve()),'separate_project_and_results_required')
    from resource_register_probe import run_probe
    results.mkdir(parents=True)
    compiler=results/'compiler.json'; combined_path=results/'combined.hlsl'
    run_probe(compiler,run_id,source_factory=source_factory,combined_out=combined_path)
    combined=combined_path.read_bytes(); cb=compiler.read_bytes(); check_compiler(json.loads(cb),combined,run_id)
    shader=shader_bytes(combined); probe=Path(__file__).with_name('SyntheticResourcePixelValidation.cs').read_bytes()
    files={SHADER:shader,PROBE:probe,'Packages/manifest.json':b'{"dependencies":{}}\n',
           'ProjectSettings/ProjectVersion.txt':b'm_EditorVersion: 2021.3.45f2\n','ProjectSettings/ProjectSettings.asset':SETTINGS.encode()}
    for name, data in files.items():
        dest=project/name; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(data)
    info={'status':'PREPARED','run_id':run_id,'synthetic_only':True,'Unity_render_executed':False,
          'compiler_sha256':digest(cb),'combined_sha256':digest(combined),'files':{k:digest(v) for k,v in files.items()}}
    (results/'generated.shader').write_bytes(shader)
    (results/'stage.json').write_text(json.dumps(info,sort_keys=True,indent=2)+'\n')
    (project/'synthetic-resource-fixture.json').write_text(json.dumps(info,sort_keys=True)+'\n')


def texsample(texture, filter, wrap, u):
    tex=TEXELS[texture]
    def index(i): return i%2 if wrap=='Repeat' else max(0,min(1,i))
    if filter=='Point': return tex[index(math.floor(2*u))]
    p=2*u-.5; i=math.floor(p); f=p-i
    return tuple(a*(1-f)+b*f for a,b in zip(tex[index(i)],tex[index(i+1)]))


def pixel(case,x, *, wrong_vertex=False):
    _,t,f,w=case
    v=texsample(t,f,w,.625)[0]; c=texsample(t,f,w,(x+.5)/W); a=c[3]
    rgb=(c[0] if wrong_vertex else v,c[1],c[2])
    return [rgb[i]*a+BG[i]*(1-a) for i in range(3)]+[1.]


def distance(a,b): return max(abs(x-y) for x,y in zip(a,b))


def verify(report, run_id, exit_code, shader_hash, probe_hash):
    require(type(exit_code) is int and exit_code==0,'unity_exit')
    required={'schema_version':1,'run_id':run_id,'status':'READBACK_COMPLETE','Unity_version':'2021.3.45f2','backend':'Vulkan',
              'active_color_space':'Linear','synthetic_only':True,'Unity_render_executed':True,'Android_device':False,'production_pixels':False,
              'XAPK':False,'shader_sha256':shader_hash,'probe_sha256':probe_hash}
    for k,v in required.items(): require(type(report.get(k)) is type(v) and report[k]==v,'receipt_mismatch:'+k)
    require(type(report.get('graphics_device_name')) is str and bool(report['graphics_device_name']),'device_missing')
    rows=report['cases']; require(type(rows) is list and len(rows)==len(CASES),'case_population')
    observed={}; errors=[]
    for row,case in zip(rows,CASES):
        for k,v in zip(('name','texture','filter','wrap'),case): require(row.get(k)==v,'case_mismatch:'+k)
        require(row.get('main_property_verified') is True and row.get('decoy_property_verified') is True,'material_binding')
        samples=row['samples']; require(type(samples) is list and len(samples)==W*H,'pixel_population')
        values=[]
        for i,item in enumerate(samples):
            require(type(item) is dict and set(item)=={'rgba'},'sample_shape'); v=item['rgba']
            require(type(v) is list and len(v)==4 and all(type(c) in (int,float) and math.isfinite(c) for c in v),'invalid_pixel')
            error=distance(v,pixel(case,i%W)); require(error<=.002,'pixel_mismatch:'+case[0]+':'+str(i))
            values.append(v); errors.append(error)
        observed[case[0]]=values
    controls=[('A_linear','A_point'),('A_repeat','A_linear'),('B_point','A_point'),('B_linear','B_point'),
              ('white_substitute','A_point'),('decoy_as_main','A_point')]
    by_name={c[0]:c for c in CASES}; gaps={}
    for actual,wrong in controls:
        gaps[actual+'_versus_'+wrong]=max(distance(v,pixel(by_name[wrong],i%W)) for i,v in enumerate(observed[actual]))
    gaps['wrong_vertex_uses_fragment_red']=max(distance(v,pixel(by_name['B_linear'],i%W,wrong_vertex=True)) for i,v in enumerate(observed['B_linear']))
    require(min(gaps.values())>=.05,'wrong_binding_not_distinguished')
    require(max(distance(a,b) for a,b in zip(observed['A_point'],observed['A_point_after_B']))<=.002,'texture_swap_restore_failed')
    return {'status':'PASS_AUTHORED_METADATA_UNITY_VULKAN_PIXELS','run_id':run_id,'cases':len(rows),'pixels':W*H*len(rows),
            'rgba_components':4*W*H*len(rows),'max_error':max(errors),'wrong_binding_comparisons':gaps,
            'device':report['graphics_device_name'],'shader_sha256':shader_hash,'probe_sha256':probe_hash,
            'original_game_or_android_pixels_verified':False,'XAPK_requested':False}


def verify_results(results, run_id, exit_code, out):
    require(not out.exists() and not out.is_symlink(),'fresh_output_required')
    cb=(results/'compiler.json').read_bytes(); combined=(results/'combined.hlsl').read_bytes()
    shader=(results/'generated.shader').read_bytes(); info=json.loads((results/'stage.json').read_text())
    check_compiler(json.loads(cb),combined,run_id); require(shader==shader_bytes(combined),'shader_not_exact_compiler_output')
    probe_hash=digest(Path(__file__).with_name('SyntheticResourcePixelValidation.cs').read_bytes())
    require(info=={'status':'PREPARED','run_id':run_id,'synthetic_only':True,'Unity_render_executed':False,
                  'compiler_sha256':digest(cb),'combined_sha256':digest(combined),'files':{
                  SHADER:digest(shader),PROBE:probe_hash,'Packages/manifest.json':digest(b'{"dependencies":{}}\n'),
                  'ProjectSettings/ProjectVersion.txt':digest(b'm_EditorVersion: 2021.3.45f2\n'),
                  'ProjectSettings/ProjectSettings.asset':digest(SETTINGS.encode())}},'stage_commitment')
    raw=(results/'raw.unity.json').read_bytes();require(0<len(raw)<1024*1024,'receipt_size')
    result=verify(json.loads(raw),run_id,exit_code,digest(shader),probe_hash)
    result.update(compiler_sha256=digest(cb),combined_sha256=digest(combined),raw_receipt_sha256=digest(raw))
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result,sort_keys=True))
    return result


class Tests(unittest.TestCase):
    def fake(self):
        return dict(schema_version=1,run_id='test',status='READBACK_COMPLETE',Unity_version='2021.3.45f2',backend='Vulkan',active_color_space='Linear',
                    synthetic_only=True,Unity_render_executed=True,Android_device=False,production_pixels=False,XAPK=False,
                    shader_sha256='shader',probe_sha256='probe',graphics_device_name='test double',cases=[
                    dict(zip(('name','texture','filter','wrap'),case),main_property_verified=True,decoy_property_verified=True,
                         samples=[{'rgba':pixel(case,i%W)} for i in range(W*H)]) for case in CASES])
    def test_oracle_points(self):
        self.assertEqual(pixel(CASES[0],0),list(BG));self.assertEqual(pixel(CASES[0],3),[.875,.25,.75,1.])
        self.assertEqual(pixel(CASES[1],1),[.265625,.34375,.46875,1.]);self.assertEqual(pixel(CASES[1],0),list(BG))
        self.assertNotEqual(pixel(CASES[2],0),pixel(CASES[1],0))
    def test_full_gate(self):
        r=verify(self.fake(),'test',0,'shader','probe');self.assertEqual(r['pixels'],128);self.assertEqual(len(r['wrong_binding_comparisons']),7)
    def test_reject_tampering(self):
        for kind in ('stale','texture','sampler','vertex','missing','binding','nan','shader','status'):
            with self.subTest(kind=kind):
                d=self.fake()
                if kind=='stale':d['run_id']='old'
                if kind=='texture':d['cases'][3]['samples']=d['cases'][0]['samples']
                if kind=='sampler':d['cases'][1]['samples']=d['cases'][0]['samples']
                if kind=='vertex':d['cases'][4]['samples']=[{'rgba':pixel(CASES[4],i%W,wrong_vertex=True)} for i in range(W*H)]
                if kind=='missing':d['cases'].pop()
                if kind=='binding':d['cases'][0]['main_property_verified']=False
                if kind=='nan':d['cases'][0]['samples'][0]['rgba'][0]=float('nan')
                if kind=='shader':d['shader_sha256']='changed'
                if kind=='status':d['status']='FAIL'
                with self.assertRaises(ValueError):verify(d,'test',0,'shader','probe')
    def test_failed_exit(self):
        with self.assertRaises(ValueError):verify(self.fake(),'test',1,'shader','probe')
    def test_register_fixture(self):
        a=source_factory('vert',True);b=source_factory('frag',True)
        for token in ('t21, space0','s16, space0','SampleLevel(s7,'):self.assertIn(token,a)
        for token in ('t9, space0','s4, space0','Sample(s7,'):self.assertIn(token,b)
        self.assertNotIn('space0',source_factory('vert',False))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('selftest','stage','verify'))
    p.add_argument('--project',type=Path);p.add_argument('--results',type=Path);p.add_argument('--run-id');p.add_argument('--exit-code',type=int);p.add_argument('--out',type=Path)
    a=p.parse_args()
    if a.action=='selftest':unittest.main(argv=[sys.argv[0],'-v'])
    elif a.action=='stage':stage(a.project,a.results,a.run_id)
    else:verify_results(a.results,a.run_id,a.exit_code,a.out)
