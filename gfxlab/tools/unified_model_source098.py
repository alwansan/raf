"""Ephemeral source-saved material and exact-PC-variant inputs for GFX098.

Only write private manifests inside generated Unity assets in the CI runner.
Public safe output contains counts; source names/values/bytecode stay private.
"""
import json,hashlib,struct,math
from pathlib import Path
from gfxlab.tools.multi_shader_parameter_blob093 import load_original_shader_private
from gfxlab.tools.multi_shader_one_pass_spirv import exact_pairs,code_from_ref
from gfxlab.tools.multi_source_select import selected_five
from gfxlab.tools.shears_texture_readiness import select_exact_renderer,classify_standard
from gfxlab.tools.shears_provenance_probe import resolve_pptr
from gfxlab.tools.multi_material_texture_semantics import named_entries
from gfxlab.tools.original_model_probe import ZIP2_SHA

def normal_AG_candidate(image):
    """Unity official UnpackNormalmapRGorAG convention, explicit candidate only."""
    from PIL import Image
    image=image.convert('RGBA');out=Image.new('RGBA',image.size)
    pixels=[]
    for r,g,b,a in image.getdata():
        if r!=255:raise ValueError('GFX098_NORMAL_RG_OR_AG_ASSUMPTION_REJECTED')
        x=a/255.*2-1;y=g/255.*2-1;z=math.sqrt(max(0.,1-x*x-y*y))
        pixels.append((a,g,max(0,min(255,round((z*.5+.5)*255))),255))
    out.putdata(pixels);return out

def material_record(material,alias):
    saved=material['m_SavedProperties']
    floats=[{'name':n,'value':v} for n,v in named_entries(saved.get('m_Floats',[]))]
    colors=[{'name':n,'value':[v[k] for k in ('r','g','b','a')]} for n,v in named_entries(saved.get('m_Colors',[]))]
    if any(type(p['value']) not in (float,int) or not math.isfinite(p['value']) for p in floats):raise ValueError('GFX098_FLOAT')
    keys=material.get('m_ValidKeywords');invalid=material.get('m_InvalidKeywords')
    if not isinstance(keys,list) or any(not isinstance(k,str) for k in keys) or invalid:raise ValueError('GFX098_KEYWORDS')
    tags=[{'name':n,'value':v} for n,v in named_entries(material.get('stringTagMap',[]))]
    return dict(alias=alias,floats=floats,colors=colors,keywords=keys,tags=tags,
                disabledPasses=material.get('disabledShaderPasses',[]),
                renderQueue=material['m_CustomRenderQueue'],instancing=material['m_EnableInstancingVariants'],
                doubleSidedGI=material['m_DoubleSidedGI'],lightmapFlags=material['m_LightmapFlags'],textures=[])

def chunk_hashes_private(dx):
    n=struct.unpack_from('<I',dx,28)[0];out={}
    for i in range(n):
        off=struct.unpack_from('<I',dx,32+4*i)[0];tag=dx[off:off+4].decode('ascii');size=struct.unpack_from('<I',dx,off+4)[0]
        if tag in ('SHDR','SHEX','ISGN','ISG1','OSGN','OSG1','OSG5'):
            out[tag]=hashlib.sha256(dx[off+8:off+8+size]).hexdigest()
    return out

def prepare(stage,modeldir,request_path):
    # Recover PPtr identities independently; never infer sharing from name/value equality.
    selection,_=selected_five(stage);envs,types,owner,renderer=select_exact_renderer(stage)
    keys=[resolve_pptr(renderer['m_Materials'][0],owner,[x.path for x in envs[owner].file.externals])[1]]
    keys += [(m['owner'],m['material_pid']) for e in selection['selected'] for m in e['materials']]
    if len(keys)!=7 or len(set(keys))!=6:raise ValueError('GFX098_MATERIAL_IDENTITIES')
    aliases={key:'MAT_%02d'%i for i,key in enumerate(dict.fromkeys(keys))};tex_alias={};slot=0;normal_count=0
    for mi in range(6):
        folder=modeldir/('M%02d'%mi);cfg=json.loads((folder/'config.json').read_text());records=[]
        for local,old in enumerate(cfg['materials']):
            key=keys[slot];slot+=1;material=types[key[0]][key[1]].read_typetree(check_read=False)
            record=material_record(material,aliases[key]);externals=[x.path for x in envs[key[0]].file.externals]
            by_role={r['role']:r for r in old['textures']}
            for name,value in named_entries(material['m_SavedProperties']['m_TexEnvs']):
                role=classify_standard(name);ref=resolve_pptr(value['m_Texture'],key[0],externals)[1]
                if ref is None:
                    record['textures'].append(dict(property=name,role='null',file='',alias='',normalCandidateFile='',scale=[value['m_Scale'][k] for k in ('x','y')],offset=[value['m_Offset'][k] for k in ('x','y')]))
                    continue
                if role not in by_role:raise ValueError('GFX098_UNSUPPORTED_BOUND_ROLE')
                if ref not in tex_alias:tex_alias[ref]='TEX_%02d'%len(tex_alias)
                tex=types[ref[0]][ref[1]].read_typetree(check_read=False)
                candidate=''
                if role=='normal':
                    from PIL import Image
                    candidate=Path(by_role[role]['file']).stem+'_AG_unpacked_candidate.png'
                    normal_AG_candidate(Image.open(folder/by_role[role]['file'])).save(folder/candidate);normal_count+=1
                record['textures'].append(dict(property=name,role=role,file=by_role[role]['file'],alias=tex_alias[ref],
                    normalCandidateFile=candidate,sRGB=tex['m_ColorSpace']==1,sourceMipCount=tex['m_MipCount'],
                    scale=[value['m_Scale'][k] for k in ('x','y')],offset=[value['m_Offset'][k] for k in ('x','y')]))
            records.append(record)
        (folder/'source098.json').write_text(json.dumps(dict(model=cfg['id'],sourceSHA=ZIP2_SHA,materials=records),indent=2)+'\n')
    if slot!=7 or len(tex_alias)!=18 or normal_count!=7:raise ValueError('GFX098_ALIAS_OR_TEXTURE_COVERAGE')
    tree,_,programs=load_original_shader_private(stage);requests=[]
    for si,sub in enumerate(tree['m_ParsedForm']['m_SubShaders']):
        for pp in sub['m_Passes']:
            pair=exact_pairs(pp)[0]
            for meta,kind in zip(pair,('Vertex','Pixel')):
                dx=code_from_ref(meta,programs,kind);prog=programs[meta['m_BlobIndex']];hashes=chunk_hashes_private(dx)
                requests.append(dict(subshader=si,passName=pp['m_State']['m_Name'],
                    stage='Vertex' if kind=='Vertex' else 'Fragment',tier=meta.get('m_ShaderHardwareTier',-1),
                    keywords=list(prog.m_Keywords)+(list(prog.m_LocalKeywords) if prog.m_LocalKeywords else []),
                    originalSHDR=hashes.get('SHDR',hashes.get('SHEX','')),
                    originalISGN=hashes.get('ISGN',hashes.get('ISG1','')),
                    originalOSGN=hashes.get('OSGN',hashes.get('OSG1',hashes.get('OSG5','')))))
    request_path.parent.mkdir(parents=True,exist_ok=True)
    request_path.write_text(json.dumps(dict(sourceSHA=ZIP2_SHA,requests=requests),indent=2)+'\n')
    return dict(experiment='GFX-MULTI-098',models=6,material_slots=7,unique_material_aliases=6,unique_texture_aliases=18,
                normal_AG_candidate_copies=7,private_PC_compile_requests=len(requests),
                originalShaderRestored=False,phase_closed=False,rig_restored=False)

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--stage',type=Path,required=True);p.add_argument('--models',type=Path,required=True);p.add_argument('--requests',type=Path,required=True);p.add_argument('--safe',type=Path,required=True)
    a=p.parse_args();d=prepare(a.stage,a.models,a.requests);a.safe.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d))
if __name__=='__main__':main()
