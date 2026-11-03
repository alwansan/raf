"""Private fragment-operation comparison; compute lifting is NOT raster/depth proof."""
import argparse, hashlib, json, os, re, subprocess, tempfile
from pathlib import Path
from scripts.verify_targeted_lfs_compute_sources import verify_sources
from scripts.w1_recover_graphics_programs import OWNERS, decoded_platforms, records, translate
from scripts.w1_recover_depth_passes import OBJECT_SHA256, linked_program, stage_variants
from scripts.probe_original_fft_software_vulkan import private_command

def lift(text, reflection, mutation=None):
    # Support only ordinary vec2 UVs and one depth/color output. Anything else
    # is a different experiment, never silently approximated.
    if reflection.get('ubos') or reflection.get('ssbos') or reflection.get('images'):
        raise ValueError('Unsupported fragment resources')
    if re.search(r'\b(dFdx|dFdy|fwidth|discard|textureProj|textureGrad|textureGather)\b', text):
        raise ValueError('Unsupported fragment operation for compute lifting')
    lines=text.splitlines()
    stripped=[]; inputs=[]; outputs=[]; textures=[]
    for line in lines:
        m=re.fullmatch(r'layout\(location = (\d+)\) in (vec2|vec4) (\w+);',line.strip())
        if m:
            inputs.append((m[2],m[3]));continue
        m=re.fullmatch(r'layout\(location = (\d+)\) out (float|vec4) (\w+);',line.strip())
        if m:
            outputs.append((m[2],m[3]));stripped.append(m[2]+' '+m[3]+';');continue
        m=re.fullmatch(r'(?:layout\([^\n]+\) )?uniform sampler2D (\w+);',line.strip())
        if m:
            name=m[1]
            slot=re.fullmatch(r'SPIRV_Cross_Combinedt([01])s[01]',name)
            if not slot: raise ValueError('Unsupported combined resource identity')
            ix=int(slot[1]); textures.append(ix)
            if mutation=='resource': ix=1-ix
            stripped.append('layout(set=0,binding=%d) uniform sampler2D %s;'%(ix,name));continue
        stripped.append(line)
    if not inputs or len(inputs)>2 or len(outputs)>1 or len(textures)!=len(set(textures)):
        raise ValueError('Unsupported original fragment interface')
    source='\n'.join(stripped)
    if 'gl_FragCoord' in source or 'gl_FrontFacing' in source:
        raise ValueError('Raster-dependent builtin not lifted')
    depth='gl_FragDepth' in source
    if depth and outputs or not depth and len(outputs)!=1:
        raise ValueError('Unsupported fragment result topology')
    source=source.replace('gl_FragDepth','w1_depth')
    if len(re.findall(r'void main\(\)',source))!=1:
        raise ValueError('Ambiguous fragment entry')
    source=source.replace('void main()','void w1_fragment()')
    uv='vec2(uv.y,uv.x)' if mutation=='axis' else 'uv'
    declarations='\n'.join(t+' '+n+';' for t,n in inputs)
    assignments='\n'.join(n+' = '+(uv if t=='vec2' else 'vec4('+uv+',0.0,1.0)')+';' for t,n in inputs)
    result='vec4(w1_depth)' if depth else ('vec4('+outputs[0][1]+')')
    if mutation=='arithmetic': result='('+result+' + vec4(0.25))'
    source=source.replace('#version 450','#version 450\n#define texture(T,U) textureLod(T,U,0.0)\n'+declarations+'\nfloat w1_depth;')
    source+='\nlayout(local_size_x=1,local_size_y=1) in;\nlayout(rgba32f,set=0,binding=2) uniform writeonly image2D w1_out;\n'
    source+='void main(){ ivec2 p=ivec2(gl_GlobalInvocationID.xy); vec2 uv=(vec2(p)+vec2(0.5))/vec2(imageSize(w1_out)); '+assignments+' w1_fragment(); imageStore(w1_out,p,'+result+'); }\n'
    return source, {'input_count':len(inputs),'output_is_depth':depth,'texture_slots':sorted(textures)}

def compile_lift(spv, folder, tag, mutation=None):
    text=private_command(['spirv-cross',str(spv),'--version','450']).decode()
    reflection=json.loads(private_command(['spirv-cross',str(spv),'--reflect']))
    lifted,shape=lift(text,reflection,mutation)
    glsl=folder/(tag+'.comp'); output=folder/(tag+'.spv')
    glsl.write_text(lifted)
    private_command(['glslangValidator','-V','-S','comp','-o',str(output),str(glsl)])
    private_command(['spirv-val','--target-env','vulkan1.1',str(output)])
    return output,shape

def compare(runner,a,b,seed):
    raw=private_command([str(runner),str(a),str(b),'31','19',str(seed)],timeout=60).decode()
    lines=[x for x in raw.splitlines() if x.startswith('RAFT_W1_VULKAN_DIFF ')]
    if len(lines)!=1: raise ValueError('Missing bounded numerical result')
    d=json.loads(lines[0].split(' ',1)[1])
    if not d.get('cpu_software_vulkan') or d.get('unity_gpu_or_android_device_verified'):
        raise ValueError('Unsupported device claim')
    if d['original_written_pixels']!=589 or d['roundtrip_written_pixels']!=589:
        raise ValueError('Incomplete output coverage')
    return {k:d[k] for k in ('within_selected_tolerance','max_abs_difference','relative_l2_difference','nonfinite_components','write_coverage_mismatch_pixels')}

def analyze(root,runner):
    verify_sources(root,expected=OWNERS)
    import UnityPy
    obj=UnityPy.load(str(root/'sharedassets0.assets')).file.objects[2407]
    if hashlib.sha256(obj.get_raw_data()).hexdigest()!=OBJECT_SHA256:
        raise ValueError('Original Depth object identity changed')
    tree=obj.read_typetree()
    tables=[records(s) for p,s in decoded_platforms(tree) if p==4]
    if len(tables)!=1: raise ValueError('Ambiguous original D3D11 table')
    rows=[]
    with tempfile.TemporaryDirectory(prefix='w1-fragment-private-') as tmp:
        folder=Path(tmp)
        for si,sub in enumerate(tree['m_ParsedForm']['m_SubShaders']):
            for pi,p in enumerate(sub['m_Passes']):
                row={'subshader':si,'pass':pi,'status':'inconclusive'}
                try:
                    variants=stage_variants(p['progFragment'])
                    if len(variants)!=1: raise ValueError('Unexpected original fragment variant')
                    code,link=linked_program(variants[0][2],tables[0],0)
                    dest=folder/('s%d-p%d'%(si,pi));dest.mkdir()
                    result=translate(code,0,dest)
                    if not result['roundtrip_vulkan11_valid']: raise ValueError('Roundtrip invalid')
                    a,shape=compile_lift(dest/'original.spv',dest,'original-lift')
                    b,other=compile_lift(dest/'roundtrip.spv',dest,'rebuilt-lift')
                    if shape!=other: raise ValueError('Lifted interface differs')
                    positives=[compare(runner,a,b,seed) for seed in (0,19,257)]
                    negatives={}
                    for mutation in ('arithmetic','axis','resource'):
                        changed,_=compile_lift(dest/'roundtrip.spv',dest,'negative-'+mutation,mutation)
                        negatives[mutation]=not compare(runner,a,changed,19)['within_selected_tolerance']
                    row.update(status='executed',original_dxbc_sha256=hashlib.sha256(code).hexdigest(),shape=shape,scenarios=positives,negative_controls_detected=negatives,all_selected_equal=all(r['within_selected_tolerance'] for r in positives))
                except Exception as e:
                    # No original identifiers, source text, compiler stderr or pixels.
                    row.update(failure_type=type(e).__name__,failure_category=str(e) if isinstance(e,ValueError) else 'private_tool_or_executor')
                rows.append(row)
    return {'source_sha':os.environ.get('GITHUB_SHA'),'original_object_sha256':OBJECT_SHA256,'rows':rows,'executed':sum(r['status']=='executed' for r in rows),'equal_pairs':sum(r.get('all_selected_equal',False) for r in rows),'compute_lift_not_raster_or_depth_state':True,'android_or_unity_render_proven':False,'numeric_equivalence_all_inputs':False}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path,required=True);parser.add_argument('--runner',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    report=analyze(args.source,args.runner)
    args.out.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print('RAFT_W1_FRAGMENT_NUMERIC '+json.dumps(report,sort_keys=True))
    if report['executed']!=9 or report['equal_pairs']!=9 or not all(all(r.get('negative_controls_detected',{}).values()) for r in report['rows']):
        raise SystemExit('Original fragment comparison incomplete or different; no equivalence claim')
