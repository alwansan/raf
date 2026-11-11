"""Private exact-PC shader requests with independently pinned PlayerSettings baseline."""
import argparse,json,hashlib
from pathlib import Path
from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA,read_manifest
from gfxlab.tools.multi_shader_parameter_blob093 import load_original_shader_private
from gfxlab.tools.multi_shader_one_pass_spirv import exact_pairs,code_from_ref
from gfxlab.tools.unified_model_source098 import chunk_hashes_private

def prepare(zip2,stage,out,safe):
    import UnityPy
    manifest=read_manifest(zip2);meta=manifest['Raft_Data/globalgamemanagers'];p=zip2/'Raft/Raft_Data/globalgamemanagers'
    if meta['kind']!='plain' or p.stat().st_size!=int(meta['bytes']) or hashlib.sha256(p.read_bytes()).hexdigest()!=meta['sha256']:raise ValueError('GFX099_GLOBAL_SETTINGS_IDENTITY')
    players=[o.read_typetree(check_read=False) for o in UnityPy.load(str(p)).objects if o.type.name=='PlayerSettings']
    if len(players)!=1 or players[0].get('m_ActiveColorSpace')!=1:raise ValueError('GFX099_ORIGINAL_COLOR_BASELINE')
    tree,_,programs=load_original_shader_private(stage_originals(zip2,stage));requests=[]
    for si,sub in enumerate(tree['m_ParsedForm']['m_SubShaders']):
        for pp in sub['m_Passes']:
            for row,kind in zip(exact_pairs(pp)[0],('Vertex','Pixel')):
                dx=code_from_ref(row,programs,kind);hashes=chunk_hashes_private(dx);prog=programs[row['m_BlobIndex']]
                requests.append(dict(subshader=si,passName=pp['m_State']['m_Name'],stage='Vertex' if kind=='Vertex' else 'Fragment',
                    tier=row.get('m_ShaderHardwareTier',-1),keywords=list(prog.m_Keywords)+(list(prog.m_LocalKeywords) if prog.m_LocalKeywords else []),
                    originalSHDR=hashes.get('SHDR',hashes.get('SHEX','')),originalISGN=hashes.get('ISGN',hashes.get('ISG1','')),
                    originalOSGN=hashes.get('OSGN',hashes.get('OSG1',hashes.get('OSG5','')))))
    if len(requests)!=14:raise ValueError('GFX099_REQUEST_COUNT')
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(dict(sourceSHA=ZIP2_SHA,sourceColorSpaceCode=1,requests=requests)))
    result=dict(experiment='GFX-MULTI-099',sourceSHA=ZIP2_SHA,sourceColorSpaceCode=1,sourceColorSpace='Linear',
                global_settings_sha256=meta['sha256'],requestedStages=14,originalShaderRestored=False,phase_closed=False)
    safe.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
def main():
    p=argparse.ArgumentParser();p.add_argument('--zip2',type=Path,required=True);p.add_argument('--stage',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--safe',type=Path,required=True);a=p.parse_args();prepare(a.zip2,a.stage,a.out,a.safe)
if __name__=='__main__':main()
