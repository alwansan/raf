"""Inspect only exact authored Actions bundles; do not relax the original FFT gate."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'clients/GT/sessions/20261127-fft-coordinate-diagnostic'))
from review_coordinate_artifacts import review, read_archive, require, digest, exact_fields, PRAGMA
from fft_coordinate_probe import NAME, sample_ops


def row_keywords(row, names):
    result={}
    for key in ('m_KeywordIndices','m_GlobalKeywordIndices','m_LocalKeywordIndices'):
        indices=row.get(key,[])
        require(isinstance(indices,list) and all(type(i) is int and 0<=i<len(names) for i in indices),'invalid_keyword_indices:'+key)
        require(len(set(indices))==len(indices),'duplicate_keyword_index:'+key)
        result[key]=[names[i] for i in indices]
    return result


def replay(path, archive_sha, mode, run_id, decoder, original_job_success):
    import UnityPy
    from scripts.gt_verify_921_shader_bundle import unity_vulkan_modules, spirv_execution_models
    from scripts.w1_recover_graphics_programs import decoded_platforms, records
    from scripts.w1_recover_depth_passes import stage_variants
    receipt,source=review(path,archive_sha,run_id,mode,original_job_success)
    _,raw=read_archive(path,archive_sha)
    require('unity.json' in raw and 'authored.bundle' in raw,'Unity_bundle_missing')
    exact_fields(receipt['unity_receipt'],{'checkpoint':'compiler_results','errors':0,'passCount':7,'registeredKeywordVariants':1,'androidVulkanOnly':True,'privateBundleCompiled':True})
    bundle=raw['authored.bundle']
    trees=[o.read_typetree() for o in UnityPy.load(bundle).objects if o.type.name=='Shader']
    require(len(trees)==1 and trees[0]['m_ParsedForm']['m_Name']==NAME and list(trees[0]['platforms'])==[18],'authored_bundle_identity')
    tree=trees[0];[(platform,segments)]=list(decoded_platforms(tree));require(platform==18,'platform')
    entries=records(segments);parsed=tree['m_ParsedForm'];names=parsed['m_KeywordNames']
    require(isinstance(names,list) and len(names)<=256 and all(isinstance(n,str) and n for n in names) and len(set(names))==len(names),'keyword_name_table')
    subshaders=parsed['m_SubShaders'];require(len(subshaders)==1 and len(subshaders[0]['m_Passes'])==7,'pass_topology')
    decoded={};modules={};passes=[];used=set();counts=Counter()
    with tempfile.TemporaryDirectory(prefix='gt-fft-replay-') as tmp:
        def blob(index):
            require(type(index) is int and 0<=index<len(entries),'invalid_blob_index')
            if index not in decoded:
                refs=[]
                for data in unity_vulkan_modules(entries[index][1]):
                    if data[:4]==b'LOMS':data=subprocess.run([str(decoder)],input=data,capture_output=True,timeout=15,check=True).stdout
                    h=digest(data)
                    if h not in modules:
                        models=spirv_execution_models(data);require(bool(models) and models<={0,4},'unexpected_execution_model')
                        module=Path(tmp)/(h+'.spv');module.write_bytes(data)
                        val=subprocess.run(['spirv-val','--target-env','vulkan1.1',str(module)],capture_output=True,timeout=30)
                        dis=subprocess.run(['spirv-dis','--raw-id',str(module)],capture_output=True,timeout=30,check=True).stdout.decode()
                        ops=[op for op,_ in sample_ops(dis)]
                        modules[h]={'sha256':h,'models':sorted(models),'bytes':len(data),'image_ops':ops,'validator_exit':val.returncode,
                                    'validator_diagnostic':(val.stdout+val.stderr).decode(errors='replace').strip()[:1200]}
                    refs.append(h)
                require(bool(refs),'empty_compiled_blob');decoded[index]=refs
            return decoded[index]
        for i,p in enumerate(subshaders[0]['m_Passes']):
            stages={}
            for key,model in (('progVertex',0),('progFragment',4)):
                rows=stage_variants(p[key]);fallback=False
                if key=='progFragment' and not rows:
                    rows=stage_variants(p['progVertex']);fallback=True
                details=[];keys=set()
                for bucket,ordinal,row in rows:
                    kw=row_keywords(row,names);active=tuple(sorted(set().union(*map(set,kw.values()))));used.update(active)
                    index=row['m_BlobIndex'];refs=[h for h in blob(index) if model in modules[h]['models']]
                    if not refs:continue
                    keys.add(active);details.append({'bucket':bucket,'ordinal':ordinal,'blob_index':index,'active_keywords':list(active),'keyword_indices_by_lane':kw,'module_sha256':refs})
                    if model==4:
                        for h in refs:
                            ops=modules[h]['image_ops'];counts['fragment_references']+=1
                            if len(ops)!=1 or (ops[0]=='OpImageFetch')!=(i==6):counts['wrong_fragment_family']+=1
                require(bool(details),'missing_stage:'+str(i)+':'+key)
                stages[key]={'rows':details,'route_keys':[list(k) for k in sorted(keys)],'empty_route':() in keys,'fragment_table_fallback':fallback}
            passes.append({'pass':i,'stages':stages})
    invalid=sum(m['validator_exit']!=0 for m in modules.values());wrong=counts['wrong_fragment_family']
    empty_pairs=all(p['stages']['progVertex']['empty_route'] and p['stages']['progFragment']['empty_route'] for p in passes)
    strict_table=not names and not used
    return {'mode':mode,'run_id':run_id,'archive_sha256':archive_sha,'bundle_sha256':digest(bundle),'source_sha256':digest(source),
            'Unity_bundle_compile_receipt_verified':True,'serialized_keyword_names':names,'used_keyword_names':sorted(used),
            'serialized_keyword_flags':list(parsed.get('m_KeywordFlags',[])), 'all_passes_have_empty_route_pair':empty_pairs,
            'original_zero_keyword_table_condition_met':strict_table,'original_gate_changed':False,
            'pass_count':len(passes),'passes':passes,'decoded_blob_count':len(decoded),'validated_unique_modules':len(modules),
            'invalid_modules':invalid,'fragment_references':counts['fragment_references'],'wrong_fragment_family_references':wrong,
            'modules':[modules[h] for h in sorted(modules)],'coordinate_diagnostic_pass':invalid==0 and wrong==0,
            'original_game_or_device_pixels_verified':False},source


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--decoder',type=Path,required=True);p.add_argument('--run-id-prefix',required=True);p.add_argument('--out',type=Path,required=True)
    for m in ('dxc','hlslcc'):
        p.add_argument('--'+m,type=Path,required=True);p.add_argument('--'+m+'-sha256',required=True);p.add_argument('--'+m+'-job-success',type=int,choices=(0,1),required=True)
    a=p.parse_args();require(not a.out.exists(),'fresh_output_required');results={};sources={}
    for m in ('dxc','hlslcc'):
        results[m],sources[m]=replay(getattr(a,m),getattr(a,m+'_sha256'),m,a.run_id_prefix+'-'+m,a.decoder,bool(getattr(a,m+'_job_success')))
    require(sources['dxc'].replace(PRAGMA,b'')==sources['hlslcc'],'different_control_bodies')
    success=all(r['coordinate_diagnostic_pass'] for r in results.values())
    data={'status':'PASS_AUTHORED_BUNDLE_COORDINATE_DIAGNOSTIC' if success else 'FAIL_AUTHORED_BUNDLE_COORDINATE_DIAGNOSTIC','exact_pragma_only_control':True,'original_gate_changed':False,'modes':results,'original_game_or_device_pixels_verified':False,'XAPK_requested':False}
    a.out.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n');print(json.dumps({k:{f:v[f] for f in ('serialized_keyword_names','used_keyword_names','validated_unique_modules','invalid_modules','wrong_fragment_family_references','all_passes_have_empty_route_pair','coordinate_diagnostic_pass')} for k,v in results.items()},sort_keys=True))
    raise SystemExit(0 if success else 2)
