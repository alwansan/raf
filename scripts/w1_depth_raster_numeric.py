"""Actual paired vertex/fragment CPU Vulkan raster and D32 differential.
No original/derived source, compiler contents or pixel payloads are published.
"""
import argparse, hashlib, json, os, re, struct, subprocess, tempfile
from pathlib import Path
from scripts.verify_targeted_lfs_compute_sources import verify_sources
from scripts.w1_recover_graphics_programs import OWNERS, decoded_platforms, records, translate
from scripts.w1_recover_depth_passes import OBJECT_SHA256, linked_program, stage_variants, digest, interfaces_match
from scripts.w1_rebind_depth_resources import rebind, signature_inputs
from scripts.w1_depth_shaderlab import val
from scripts.probe_original_fft_software_vulkan import private_command

def reflection(path):
    return json.loads(private_command(['spirv-cross',str(path),'--reflect']))

def normalize_bindings(binary, reflected, program, name_indices, rebuilt):
    """Original register/property metadata, never descriptor declaration order."""
    names=dict((ix,name) for name,ix in name_indices)
    textures={};samplers={}
    for row in program.get('m_CommonParameters',{}).get('m_TextureParams',[]):
        ti,si,ni=row['m_Index'],row['m_SamplerIndex'],row['m_NameIndex']
        if ti not in (0,1) or si not in (0,1) or ni not in names or ti in textures:
            raise ValueError('Unsupported original sampled resource topology')
        textures[ti]=names[ni]
        expected='sampler'+names[ni]
        if si in samplers and samplers[si]!=expected:
            raise ValueError('Ambiguous original sampler name')
        samplers[si]=expected
    if any(reflected.get(k) for k in ('ubos','ssbos','images','textures')):
        raise ValueError('Unsupported graphics resource class')
    wanted={};seen={'t':set(),'s':set()}
    for field,kind,table,base in (('separate_images','t',textures,0),('separate_samplers','s',samplers,2)):
        for resource in reflected.get(field,[]):
            name=resource['name']
            if rebuilt:
                candidates=[ix for ix,value in table.items() if value==name]
            else:
                match=re.search(r'(?:^|_)'+kind+r'([01])$',name)
                candidates=[int(match[1])] if match else []
            if len(candidates)!=1 or candidates[0] not in table or candidates[0] in seen[kind]:
                raise ValueError('Original resource identity unresolved or duplicated')
            ix=candidates[0];seen[kind].add(ix);wanted[name]=base+ix
    if seen['t']!=set(textures) or seen['s']!=set(samplers):
        raise ValueError('Original resource mapping not fully consumed')
    words=list(struct.unpack('<%dI'%(len(binary)//4),binary))
    if len(words)<5 or words[0]!=0x07230203: raise ValueError('Invalid private SPIR-V')
    instructions=[];position=5;ids={}
    while position<len(words):
        count=words[position]>>16;opcode=words[position]&65535
        if not count or position+count>len(words): raise ValueError('Malformed private SPIR-V instruction')
        instructions.append((position,count,opcode))
        if opcode==5:
            name=struct.pack('<%dI'%(count-2),*words[position+2:position+count]).split(b'\0',1)[0].decode()
            if name in wanted:
                if name in ids: raise ValueError('Duplicate private resource name')
                ids[name]=words[position+1]
        position+=count
    if set(ids)!=set(wanted): raise ValueError('Reflected resource IDs unavailable')
    targets={ids[name]:binding for name,binding in wanted.items()};decorations=set()
    for p,n,op in instructions:
        if op==71 and n==4 and words[p+1] in targets:
            if words[p+2] in (33,34):
                key=(words[p+1],words[p+2])
                if key in decorations: raise ValueError('Duplicate descriptor decoration')
                decorations.add(key)
                words[p+3]=targets[words[p+1]] if words[p+2]==33 else 0
    if decorations!={(target,kind) for target in targets for kind in (33,34)}:
        raise ValueError('Missing descriptor binding or set')
    return struct.pack('<%dI'%len(words),*words),len(textures)

def supported_state(state):
    if state['rtSeparateBlend'] or val(state['culling'])!=0 or val(state['alphaToMask'])!=0:
        raise ValueError('Raster state needs explicit additional support')
    b=state['rtBlend0']
    if [val(b[k]) for k in ('srcBlend','destBlend','srcBlendAlpha','destBlendAlpha','blendOp','blendOpAlpha')]!=[1,0,1,0,0,0]:
        raise ValueError('Nontrivial original blending unsupported')
    for k in ('offsetFactor','offsetUnits'):
        if val(state[k])!=0: raise ValueError('Depth bias unsupported')
    if 'conservative' in state and val(state['conservative'])!=0:
        raise ValueError('Conservative state unsupported')
    if [val(state[k]) for k in ('stencilRef','stencilReadMask','stencilWriteMask')]!=[0,255,255]:
        raise ValueError('Nondefault stencil unsupported')
    for key in ('stencilOp','stencilOpFront','stencilOpBack'):
        if [val(state[key][k]) for k in ('comp','pass','fail','zFail')]!=[8,0,0,0]:
            raise ValueError('Nondefault stencil operation unsupported')
    flags=[int(val(b['colMask'])),int(val(state['zWrite'])),int(val(state['zTest'])),int(val(state['zClip']))]
    if flags[0] not in (0,15) or flags[1] not in (0,1) or not 0<=flags[2]<=8 or flags[3] not in (0,1):
        raise ValueError('Unsupported depth or mask enum')
    return flags

def interface_rows(ref,key):
    return sorted([{'location':r['location'],'type':r['type']} for r in ref.get(key,[]) if 'location' in r],key=lambda r:r['location'])

def compare(runner,stages,state,seed,mutation,texture_count,canary=False):
    mask,write,test,clip=state
    command=[str(runner),*[str(x) for x in stages],str(mask),str(write),str(test),str(seed),str(mutation),str(texture_count),str(clip)]
    if canary: command.append('--canary')
    result=subprocess.run(command,capture_output=True,timeout=45)
    if result.returncode:
        safe=[l for l in result.stderr.decode(errors='replace').splitlines() if l.startswith('RAFT_W1_RASTER_ERROR ')]
        raise ValueError(safe[0][:250] if len(safe)==1 else 'Private graphics executor failed')
    lines=[l for l in result.stdout.decode().splitlines() if l.startswith('RAFT_W1_RASTER_DIFF ')]
    if len(lines)!=1: raise ValueError('Missing graphics aggregate')
    value=json.loads(lines[0].split(' ',1)[1])
    if not value['cpu_vulkan'] or value['android_or_unity_render'] or value['mutation']!=mutation:
        raise ValueError('Unsupported graphics platform or mutation claim')
    if not value.get('synchronization_validation_enabled') or value.get('vulkan_validation_errors')!=0:
        raise ValueError('Vulkan API/synchronization validation not clean')
    return value

def canary(runner,folder):
    vertex='#version 450\nlayout(location=0) in vec4 p; layout(location=1) in vec2 uv; void main(){gl_Position=p;}\n'
    fragment='#version 450\nlayout(location=0) out vec4 color; void main(){color=vec4(0.2,0.4,0.6,0.8);gl_FragDepth=0.25;}\n'
    shaders=[]
    for stage,text in (('vert',vertex),('frag',fragment)):
        path=folder/('canary.'+stage);out=folder/('canary-'+stage+'.spv');path.write_text(text)
        private_command(['glslangValidator','-V','-S',stage,'-o',str(out),str(path)])
        private_command(['spirv-val','--target-env','vulkan1.1',str(out)]);shaders.append(out)
    result=compare(runner,shaders+shaders,[15,1,8,1],19,0,0,True)
    if not result['known_color_depth_canary'] or not result['within_tolerance']:
        raise ValueError('Known independent graphics canary failed')
    for mutation in (2,3):
        if compare(runner,shaders+shaders,[15,1,8,1],19,mutation,0)['within_tolerance']:
            raise ValueError('Known graphics geometry/depth negative not detected')
    return result

def analyze(root,runner):
    verify_sources(root,expected=OWNERS)
    import UnityPy
    obj=UnityPy.load(str(root/'sharedassets0.assets')).file.objects[2407]
    if hashlib.sha256(obj.get_raw_data()).hexdigest()!=OBJECT_SHA256:
        raise ValueError('Original Depth Copy identity changed')
    tree=obj.read_typetree()
    tables=[records(s) for p,s in decoded_platforms(tree) if p==4]
    if len(tables)!=1: raise ValueError('Ambiguous original graphics table')
    rows=[]
    with tempfile.TemporaryDirectory(prefix='w1-raster-private-') as tmp:
        folder=Path(tmp);canary_result=canary(runner,folder)
        for si,sub in enumerate(tree['m_ParsedForm']['m_SubShaders']):
            for pi,p in enumerate(sub['m_Passes']):
                row={'subshader':si,'pass':pi,'status':'inconclusive','state_sha256':digest(p['m_State'])}
                try:
                    row['phase']='state';state=supported_state(p['m_State'])
                    originals=[];rebuilt=[];interfaces={};texture_count=None
                    for field,stage,suffix in (('progVertex',1,'vert'),('progFragment',0,'frag')):
                        row['phase']='stage_recovery'
                        program=p[field];variants=stage_variants(program)
                        if len(variants)!=1: raise ValueError('Unexpected graphics variant')
                        code,_=linked_program(variants[0][2],tables[0],stage)
                        dest=folder/('s%d-p%d-%s'%(si,pi,suffix));dest.mkdir()
                        result=translate(code,stage,dest)
                        if not result['roundtrip_vulkan11_valid']: raise ValueError('Original translation failed')
                        source,bindings=rebind((dest/'private.hlsl').read_text(),program,p['m_NameIndices'],original_inputs=signature_inputs(code) if stage==1 else None)
                        hlsl=dest/'rebound.hlsl';spv=dest/'rebound.spv';hlsl.write_text(source)
                        private_command(['glslangValidator','-V','-D','-S',suffix,'-e','main','-o',str(spv),str(hlsl)])
                        pair=[]
                        for path,is_rebuilt in ((dest/'original.spv',False),(spv,True)):
                            row['phase']='resource_binding'
                            ref=reflection(path);normalized,count=normalize_bindings(path.read_bytes(),ref,program,p['m_NameIndices'],is_rebuilt)
                            target=dest/('rebuilt-normalized.spv' if is_rebuilt else 'original-normalized.spv');target.write_bytes(normalized)
                            private_command(['spirv-val','--target-env','vulkan1.1',str(target)])
                            pair.append(target)
                            if stage==1:
                                if interface_rows(ref,'inputs')!=[{'location':0,'type':'vec4'},{'location':1,'type':'vec2'}]:
                                    raise ValueError('Vertex attribute interface needs explicit support')
                            else:
                                if texture_count is not None and texture_count!=count:
                                    raise ValueError('Original and rebuilt texture counts disagree')
                                texture_count=count
                            interfaces[(stage,is_rebuilt)]={'inputs':interface_rows(ref,'inputs'),'outputs':interface_rows(ref,'outputs')}
                        originals.append(pair[0]);rebuilt.append(pair[1])
                    for is_rebuilt in (False,True):
                        if not interfaces_match(interfaces[(1,is_rebuilt)],interfaces[(0,is_rebuilt)]):
                            raise ValueError('Paired graphics varying locations disagree')
                    stages=originals+rebuilt
                    row['phase']='positive_raster'
                    positive=[compare(runner,stages,state,seed,0,texture_count) for seed in (0,19,257)]
                    row['phase']='negative_raster'
                    negative={str(mode):not compare(runner,stages,state,19,mode,texture_count)['within_tolerance'] for mode in (1,2,3,4)}
                    row.update(status='executed',scenarios=positive,negative_controls_detected=negative,all_selected_equal=all(r['within_tolerance'] for r in positive),textures_mapped=texture_count)
                except Exception as exc:
                    row.update(failure_type=type(exc).__name__,failure_category=str(exc) if isinstance(exc,ValueError) else 'private_graphics_preparation')
                rows.append(row)
    return {'source_sha':os.environ.get('GITHUB_SHA'),'original_object_sha256':OBJECT_SHA256,'canary':canary_result,'rows':rows,'executed':sum(r['status']=='executed' for r in rows),'equal_pairs':sum(r.get('all_selected_equal',False) for r in rows),'actual_cpu_vulkan_graphics':True,'unity_or_adreno_proven':False,'original_guid_changed':False}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,required=True);parser.add_argument('--runner',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    try: report=analyze(args.source,args.runner)
    except Exception as exc:
        report={'source_sha':os.environ.get('GITHUB_SHA'),'executed':0,'failure_type':type(exc).__name__,'failure_category':str(exc) if isinstance(exc,ValueError) else 'private_canary_or_preparation','unity_or_adreno_proven':False}
    args.out.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n');print('RAFT_W1_DEPTH_RASTER '+json.dumps(report,sort_keys=True))
    if report['executed']!=9 or report.get('equal_pairs')!=9 or not all(all(r['negative_controls_detected'].values()) for r in report.get('rows',[])):
        raise SystemExit('Graphics raster comparison incomplete or mismatched; no acceptance')

