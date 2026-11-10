"""Private original-stage GLES assets for an Android driver compiler probe.

Does not bind Unity material data or claim original pixels. Anonymous pair IDs
only; raw shader assets are never committed/uploaded loose. Only signed APK
and safe aggregate metadata are delivered for the owner's offline phone test.
"""
import argparse,json,re,tempfile,hashlib,os
from pathlib import Path
from gfxlab.tools.original_model_probe import stage_originals,ZIP2_SHA
from gfxlab.tools.multi_shader_one_pass_spirv import source_pair,code_from_ref,translate_pair
from gfxlab.tools.multi_shader_gles_stage_io import run_quiet,public_interfaces
from gfxlab.tools.multi_shader_shdr_declaration_census import source_shader_chunk
from gfxlab.tools.multi_shader_source_spirv_binding_check import private_source_slots
from gfxlab.tools.multi_shader_original_decl_profile_coverage import canonical_private_declaration_profile
from gfxlab.tools.multi_shader_all_variant_dxbc_sample_census import private_signature
from gfxlab.tools.multi_shader_dxbc_sample_pair_parity import original_sample_pairs
from gfxlab.tools.multi_shader_pass_joint_batch062 import select_pass_scoped_joint_classes

def representatives(programs,passes):
    cache={}
    def inspect(meta,kind):
        key=(meta['m_BlobIndex'],kind)
        if key not in cache:
            dx=code_from_ref(meta,programs,kind);shdr=source_shader_chunk(dx)
            slots,cb=private_source_slots(shdr)
            pairs,stats=original_sample_pairs(shdr,slots['resource'],slots['sampler'])
            cache[key]={'decl':canonical_private_declaration_profile(slots,cb),
                        'sampling':private_signature(pairs),
                        'unresolved':stats['source_original_unresolved_dynamic_t_s'],'dx':dx}
        return cache[key]
    selected=[]
    for start in range(0,157,24):
        rows,safe,_=select_pass_scoped_joint_classes(passes,inspect,start=start,budget=24)
        if safe['pass_scoped_joint_declaration_and_sample_use_classes']!=157:raise ValueError('GFX094_CLASS_DRIFT')
        selected.extend(rows)
    if len(selected)!=157:raise ValueError('GFX094_PAIR_COUNT')
    return selected,inspect

def controlled_glsl_names(source,reflection,stage):
    """Pure identifier changes for GLES linking; not original binding semantics.

    Stage-private uniform blocks/samplers avoid falsely conflating D3D's
    independent VS/FS resource namespaces. Numeric IO candidates get common
    names. CPU pair linkage is required, not inferred from successful stages.
    """
    if not isinstance(source,str) or not source.startswith('#version 310 es'):raise ValueError('GFX094_GLES_VERSION')
    names={}
    interface='outputs' if stage=='vertex' else 'inputs'
    for row in reflection.get(interface,[]):
        if 'location' not in row:continue
        loc=row['location'];name=row.get('name')
        if type(loc)!=int or not isinstance(name,str) or not re.fullmatch(r'[A-Za-z_]\w*',name):raise ValueError('GFX094_INTERFACE')
        names[name]='gfx_io_%d_c%d'%(loc,row.get('component',0))
    for name in re.findall(r'\buniform\s+(?:lowp\s+|mediump\s+|highp\s+)?(?:[iu]?sampler\w+)\s+(\w+)',source):
        names[name]=stage+'_'+name
    for name in re.findall(r'\buniform\s+(\w+)\s*\{',source):names[name]=stage+'_'+name
    if len(set(names.values()))!=len(names):raise ValueError('GFX094_RENAME_COLLISION')
    return re.sub(r'\b[A-Za-z_]\w*\b',lambda m:names.get(m[0],m[0]),source)

def build_pack(stage,out):
    programs,passes=source_pair(stage);chosen,inspect=representatives(programs,passes)
    out.mkdir(parents=True,exist_ok=True);rows=[]
    for i,(passrow,vm,fm) in enumerate(chosen):
        ident='P%03d'%i
        with tempfile.TemporaryDirectory(prefix='gfx094-private-') as td:
            folder=Path(td);translated=translate_pair(inspect(vm,'Vertex')['dx'],inspect(fm,'Pixel')['dx'],folder)
            if not all(translated[k]['vulkan11_spirv_validation_success'] for k in ('vertex','fragment')):raise ValueError('GFX094_SPV_VALIDATION')
            refs={}
            for stage,ext in (('vertex','vert'),('fragment','frag')):
                spv=folder/(stage+'.spv');ok,raw=run_quiet(['spirv-cross',str(spv),'--reflect'])
                if not ok:raise ValueError('GFX094_REFLECTION')
                refs[stage]=json.loads(raw);target=folder/(stage+'.glsl')
                if not run_quiet(['spirv-cross',str(spv),'--version','310','--es','--output',str(target)])[0]:raise ValueError('GFX094_GLSL')
                source=controlled_glsl_names(target.read_text(),refs[stage],stage)
                (folder/('probe.'+ext)).write_text(source)
                (out/(ident+'.'+ext)).write_text(source)
            io=public_interfaces(refs['vertex'],refs['fragment'])
            if not io['location_type_parity']:raise ValueError('GFX094_STAGE_IO')
            # Cross-stage GLES link is a meaningful preflight; shader output is
            # captured privately, never printed as it may contain shader text.
            ok,_=run_quiet(['glslangValidator','-l',str(folder/'probe.vert'),str(folder/'probe.frag')])
            if not ok:raise ValueError('GFX094_OFFLINE_PAIR_LINK_FAILED_'+ident)
            rows.append(dict(id=ident,subshader=passrow['subshader'],pass_position=passrow['pass'],
                VS_sha256=hashlib.sha256((out/(ident+'.vert')).read_bytes()).hexdigest(),
                FS_sha256=hashlib.sha256((out/(ident+'.frag')).read_bytes()).hexdigest()))
    d=dict(experiment='GFX-MULTI-094',source_sha=ZIP2_SHA,build_source_sha=os.environ.get('GITHUB_SHA',''),pairs=rows,
       source_pairs=157,source_stages=314,offline_linked_pairs=157,originalShaderRestored=False,
       actual_Material_CB_payload_bound=False,model_rendered=False,PC_pixel_parity=False,phase_closed=False)
    (out/'manifest.json').write_text(json.dumps(d,indent=2)+'\n')
    return {k:v for k,v in d.items() if k!='pairs'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--zip2',type=Path,required=True);p.add_argument('--stage',type=Path,required=True);p.add_argument('--assets',type=Path,required=True);p.add_argument('--safe',type=Path,required=True)
    a=p.parse_args();d=build_pack(stage_originals(a.zip2,a.stage),a.assets);a.safe.write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d))
if __name__=='__main__':main()
