"""Stage and independently verify an authored Unity Vulkan keyword pixel probe."""
import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import sys
import unittest
import copy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.gt_runtime_keyword_contract import strict_engine_router

GLOBAL = 'GT_A2_GLOBAL'
LOCAL = 'GT_A2_LOCAL'
KEYS = [(GLOBAL, LOCAL), (GLOBAL,), (LOCAL,), ()]
WIDTH, HEIGHT = 6, 4
# (case, material index, global keyword, A local, B local,
#  global impostor for local keyword, material A global, expected route)
CASES = [
    ('empty_A', 0, False, False, False, False, False, 3),
    ('global_on_A', 0, True, False, False, False, False, 1),
    ('global_off_A', 0, False, False, False, False, False, 3),
    ('local_on_A', 0, False, True, False, False, False, 2),
    ('isolated_B', 1, False, True, False, False, False, 3),
    ('both_A', 0, True, True, False, False, False, 0),
    ('global_B', 1, True, True, False, False, False, 1),
    ('global_off_local_A', 0, False, True, False, False, False, 2),
    ('global_impostor_B', 1, False, True, False, True, False, 3),
    ('local_off_A', 0, False, False, False, True, False, 3),
    ('material_global_A', 0, False, False, False, False, True, 1),
    ('material_global_isolation_B', 1, False, False, False, False, True, 3),
    ('material_global_off_A', 0, False, False, False, False, False, 3),
    ('local_on_B', 1, False, False, True, False, False, 2),
    ('isolated_A', 0, False, False, True, False, False, 3),
]
NEGATIVE = {'empty_A': 0, 'isolated_B': 2, 'global_impostor_B': 2,
            'material_global_isolation_B': 1, 'isolated_A': 2}
SETTINGS = '''%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!129 &1
PlayerSettings:
  m_ObjectHideFlags: 0
  serializedVersion: 26
  companyName: SyntheticValidation
  productName: SyntheticKeywordPixels
  m_ActiveColorSpace: 1
'''


def shader_bytes():
    # Use the actual strict router, with an explicitly authored local scope.
    # This does not infer or change the game's original keyword scopes.
    pragmas, router = strict_engine_router(KEYS, {i: f'#define GT_A2_ROUTE {i+1}.0' for i in range(4)})
    assert '#pragma multi_compile __ ' + LOCAL in pragmas
    pragmas = [p.replace('multi_compile __ ' + LOCAL, 'multi_compile_local __ ' + LOCAL) for p in pragmas]
    body = '''Shader "Hidden/RAFT/SyntheticKeywordPixels" {
Properties { _ProbeMaterialMarker ("Authored marker", Float) = 0.25 }
SubShader { Tags { "Queue"="Geometry" "RenderType"="Opaque" }
Pass { Cull Off ZWrite Off ZTest Always Blend Off
HLSLPROGRAM
#pragma target 3.5
#pragma only_renderers vulkan
#pragma vertex vert
#pragma fragment frag
#include "UnityCG.cginc"
'''+ '\n'.join(pragmas) + '\n' + router + '''
float _ProbeMaterialMarker;
struct App { float4 vertex:POSITION; };
struct Varying { float4 pos:SV_POSITION; float marker:TEXCOORD0; };
Varying vert(App a) { Varying o; o.pos=UnityObjectToClipPos(a.vertex); o.marker=GT_A2_ROUTE/8.0; return o; }
float4 frag(Varying i):SV_Target { return float4(i.marker,GT_A2_ROUTE/16.0,_ProbeMaterialMarker,1.0); }
ENDHLSL
} }
Fallback Off
}
'''
    return body.encode()


def fixture():
    return {'Assets/SyntheticKeywordPixels.shader': shader_bytes(),
            'Assets/Editor/SyntheticKeywordPixelValidation.cs': Path(__file__).with_name('SyntheticKeywordPixelValidation.cs').read_bytes(),
            'Packages/manifest.json': b'{"dependencies":{}}\n',
            'ProjectSettings/ProjectVersion.txt': b'm_EditorVersion: 2021.3.45f2\n',
            'ProjectSettings/ProjectSettings.asset': SETTINGS.encode()}


def hashes():
    return {k: sha256(v).hexdigest() for k, v in fixture().items()}


def stage(project, out):
    if project.exists() or project.is_symlink() or out.exists() or out.is_symlink():
        raise ValueError('fresh_project_and_receipt_required')
    files = fixture()
    for name, data in files.items():
        dest = project / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    manifest = {'synthetic_only': True, 'files': hashes(), 'route_keys': KEYS}
    (project/'synthetic-keyword-fixture.json').write_text(json.dumps(manifest, sort_keys=True)+'\n')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({'status':'PREPARED','Unity_render_executed':False, **manifest},sort_keys=True,indent=2)+'\n')


def pixel(route, material):
    return [(route+1)/8, (route+1)/16, .25 if material == 0 else .75, 1.]


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def vector(value):
    require(type(value) is list and len(value) == 4 and all(type(v) in (int,float) and math.isfinite(v) for v in value),'invalid_pixel')
    return value


def diff(a,b):
    return max(abs(x-y) for x,y in zip(a,b))


def verify(receipt, run_id, exit_code, expected_hashes=None):
    h = hashes() if expected_hashes is None else expected_hashes
    require(type(exit_code) is int and exit_code == 0, 'Unity_failed')
    expected = {'schema_version':1,'run_id':run_id,'status':'PASS','Unity_version':'2021.3.45f2',
                'backend':'Vulkan','active_color_space':'Linear','synthetic_only':True,
                'Unity_render_executed':True,'Android_device':False,'production_pixels':False,
                'XAPK':False,'global_overridable':True,'local_overridable':False,
                'shader_sha256':h['Assets/SyntheticKeywordPixels.shader'],
                'probe_sha256':h['Assets/Editor/SyntheticKeywordPixelValidation.cs']}
    for k,v in expected.items():
        require(type(receipt.get(k)) is type(v) and receipt[k] == v, 'receipt_mismatch:'+k)
    require(type(receipt.get('graphics_device_name')) is str and bool(receipt['graphics_device_name']), 'device_missing')
    rows = receipt.get('cases')
    require(type(rows) is list and len(rows) == len(CASES),'case_population')
    errors, separation, covered = [], [], set()
    for row,case in zip(rows, CASES):
        name,mat,g,al,bl,impostor,mg,route = case
        fields = {'name':name,'material':mat,'global_enabled':g,'local_A':al,'local_B':bl,
                  'global_local_impostor':impostor,'material_global_A':mg,'route':route}
        for k,v in fields.items():
            require(type(row.get(k)) is type(v) and row[k] == v, 'case_mismatch:'+name+':'+k)
        raw = row.get('samples')
        require(type(raw) is list and all(type(item) is dict and set(item)=={'rgba'} for item in raw),'sample_wrapper:'+name)
        samples = [item['rgba'] for item in raw]
        require(type(samples) is list and len(samples) == WIDTH*HEIGHT,'pixel_population:'+name)
        expected = pixel(route, mat)
        error = max(diff(vector(value),expected) for value in samples)
        require(error <= .002, 'pixel_mismatch:'+name)
        if name in NEGATIVE:
            gap = min(diff(vector(value),pixel(NEGATIVE[name],mat)) for value in samples)
            require(gap >= .06,'negative_control_not_detected:'+name)
            separation.append(gap)
        covered.add(route)
        errors.append(error)
    require(covered == set(range(4)), 'route_coverage')
    return {'status':'PASS_AUTHORED_UNITY_VULKAN_KEYWORD_PIXELS','run_id':run_id,'case_count':len(rows),
            'checked_pixels':len(rows)*WIDTH*HEIGHT,'checked_rgba_components':4*len(rows)*WIDTH*HEIGHT,
            'routes_observed':sorted(covered),'empty_route':3,'negative_controls':len(separation),
            'minimum_wrong_route_separation':min(separation),'max_error':max(errors),
            'device':receipt['graphics_device_name'],'global_local_scope_tested_on_authored_shader':True,
            'original_runtime_or_Android_pixels_verified':False,'XAPK_requested':False,
            'input_sha256':h}


class ContractTests(unittest.TestCase):
    def fake(self):
        h = hashes()
        data = dict(schema_version=1,run_id='authored-test',status='PASS',Unity_version='2021.3.45f2',backend='Vulkan',
                    active_color_space='Linear',graphics_device_name='test double',synthetic_only=True,Unity_render_executed=True,
                    Android_device=False,production_pixels=False,XAPK=False,global_overridable=True,local_overridable=False,
                    shader_sha256=h['Assets/SyntheticKeywordPixels.shader'],probe_sha256=h['Assets/Editor/SyntheticKeywordPixelValidation.cs'])
        data['cases'] = [dict(name=n,material=m,global_enabled=g,local_A=a,local_B=b,global_local_impostor=i,
                              material_global_A=mg,route=r,samples=[{'rgba':pixel(r,m)} for _ in range(WIDTH*HEIGHT)]) for n,m,g,a,b,i,mg,r in CASES]
        return data
    def test_exact_oracle_fixture(self):
        r=verify(self.fake(),'authored-test',0)
        self.assertEqual(r['checked_pixels'],360)
        self.assertEqual(r['negative_controls'],5)
    def test_tampered_receipts_rejected(self):
        for mutation in ('stale','route0','vs','fs','material','missing','scope','nan','state'):
            with self.subTest(mutation=mutation):
                d=self.fake()
                if mutation=='stale': d['run_id']='stale'
                if mutation=='route0': d['cases'][0]['samples']=[{'rgba':pixel(0,0)} for _ in range(24)]
                if mutation=='vs': d['cases'][0]['samples'][0]['rgba'][0]=.125
                if mutation=='fs': d['cases'][0]['samples'][0]['rgba'][1]=.0625
                if mutation=='material': d['cases'][0]['samples'][0]['rgba'][2]=.75
                if mutation=='missing': d['cases'].pop()
                if mutation=='scope': d['local_overridable']=True
                if mutation=='nan': d['cases'][0]['samples'][0]['rgba'][0]=float('nan')
                if mutation=='state': d['cases'][0]['global_enabled']=True
                with self.assertRaises(ValueError): verify(d,'authored-test',0)
    def test_process_failure_rejected(self):
        with self.assertRaises(ValueError): verify(self.fake(),'authored-test',1)
    def test_source_router(self):
        s=shader_bytes().decode()
        self.assertIn('#pragma multi_compile_local __ '+LOCAL,s)
        self.assertIn('#pragma multi_compile __ '+GLOBAL,s)
        self.assertEqual(s.count('#define GT_A2_ROUTE '),4)
        self.assertIn('#error Unmapped_original_keyword_set',s)
        self.assertIn('!defined(GT_A2_GLOBAL) && !defined(GT_A2_LOCAL)\n#define GT_A2_ROUTE 4.0',s)
    def test_case_scope_truth_table(self):
        for _,m,g,a,b,i,mg,r in CASES:
            effective=set()
            if g or (m==0 and mg): effective.add(GLOBAL)
            if (a if m==0 else b): effective.add(LOCAL)
            self.assertEqual(set(KEYS[r]),effective)


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=('stage','verify','selftest'))
    p.add_argument('--project',type=Path)
    p.add_argument('--receipt',type=Path)
    p.add_argument('--out',type=Path)
    p.add_argument('--run-id')
    p.add_argument('--exit-code',type=int)
    a=p.parse_args()
    if a.command=='selftest': unittest.main(argv=[sys.argv[0],'-v'])
    elif a.command=='stage': stage(a.project,a.out)
    else:
        if not a.run_id or a.out.exists(): raise ValueError('fresh_receipt_required')
        result=verify(json.loads(a.receipt.read_text()),a.run_id,a.exit_code)
        a.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
        print(json.dumps(result,sort_keys=True))
