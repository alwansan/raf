"""Rejoin the prestaged exact original graph to its fresh actual export.

Only this selected source graph is tested; no repeated population census, no
shader program installation, no Unity/GPU/production claim.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

from tools.gt_top_resource_closure import prestage as prep, probe as prior, texture_observation, selected_array
from tools.gt_top_original_renderer import probe as previous
from tools.gt_shader_fanout import audit
from scripts import gt_material_route_values as values
from scripts import gt_particle108_local_texture_document as native
from scripts.b05_verify_material_texenv_bindings import normalize_texenvs
from scripts import gt_particle108_source_pixel_parity as pixels
from scripts import gt_zip2_payloads as zip2

STATUS="GT_TOP_PRESTAGED_EXACT_RESOURCE_RECHECK"
need=prior.need

class Source(prep.Source):
    def acquire(self,name):
        rel=prep.exact_rel(name)
        record=self.records.get(rel)
        path=self.a.original/rel
        need(record is not None and path.is_file(),"selected_dependency_not_prepared_before_export")
        need(zip2.fingerprint(path)==(record[1],record[2]),"selected_dependency_SHA_drift")

def join(a,plan,source):
    w,b,r=[json.loads(p.read_text()) for p in (a.w1,a.b02,a.renderer_trace)]
    need(w["schema_version"]==b["schema_version"]==r["schema_version"]==1 and
         previous.GUID.fullmatch(w["export_instance"]) and
         w["export_instance"]==b["export_instance"]==r["export_instance"],
         "different_export_instances")
    mt=previous.trace_map(w,{21,48})
    rr=previous.trace_map(r,{23,33,43})
    tt=previous.trace_map(b,set(prep.TYPES.values()))
    keys=[tuple(k) for k in plan["keys"]]
    shader=tuple(plan["shader"])
    mk0=tuple(plan["material"])
    rk0=tuple(plan["renderer"])
    xk0=tuple(plan["mesh"])
    need(tuple(k[0] for k in keys)==(23,33,21,43) and keys[0][1:]==rk0
         and keys[2][1:]==mk0 and keys[3][1:]==xk0,"invalid_private_selected_graph")
    renderer=source.obj(rk0,"MeshRenderer").read_typetree(check_read=False)
    filt=source.obj(keys[1][1:],"MeshFilter").read_typetree(check_read=False)
    mat=source.obj(mk0,"Material").read_typetree(check_read=False)
    source.obj(xk0,"Mesh")
    source.obj(shader,"Shader")
    need(len(renderer["m_Materials"])==1 and source.resolve(rk0[0],renderer["m_Materials"][0])==mk0
         and source.resolve(rk0[0],renderer["m_GameObject"])==source.resolve(keys[1][1],filt["m_GameObject"])
         and source.resolve(keys[1][1],filt["m_Mesh"])==xk0
         and source.resolve(mk0[0],mat["m_Shader"])==shader,"original_selected_graph_drift")
    sp=mt[(48,*shader)]
    sg=previous.native_key(sp)
    need(sp[0]==4800000 and sp[2]=="3","original_shader_pointer_drift")
    export=[previous.native_key(rr[keys[0]]),previous.native_key(rr[keys[1]]),
            previous.native_key(mt[keys[2]]),previous.native_key(rr[keys[3]])]
    wanted=defaultdict(set)
    for g,f in export:
        wanted[g].add(f)
    docs=previous.actual_docs(a.project,wanted)
    need(all(k in docs and docs[k][0]==cls for k,cls in zip(export,(23,33,21,43))),
         "selected_actual_native_graph_missing")
    rk,fk,mk,xk=export
    previous.check_links(docs[rk][1],docs[fk][1],docs[mk][1],rk[0],fk[0],mk,sg,xk)
    need(previous.keywords(mat)==previous.keywords(docs[mk][1]),"selected_saved_keyword_drift")
    return mat,mk,xk,tt

def exact_slot(before,after,owner,export_guid,source,trace,planned):
    ptr,_=before
    if not ptr[1]:
        need(planned is None,"private_null_plan_drift")
        return prior.check_texture_slot(before,after,owner,export_guid,source.resolve,{})
    need(planned is not None,"typed_source_texture_dependency_unresolved")
    key=source.resolve(owner,{"m_FileID":ptr[0],"m_PathID":ptr[1]})
    need(key==tuple(planned["key"]),"private_texture_plan_identity_drift")
    obj=source.file(key[0]).objects.get(key[1])
    cls=planned["class"]
    need(obj is not None and prep.TYPES.get(obj.type.name)==cls,"source_texture_type_drift")
    exact=trace.get((cls,*key))
    need(exact is not None,"typed_texture_trace_unavailable")
    # Reuse the strict pointer/UV comparer; map only the single authenticated
    # typed target under the internal comparer key. No claim of class28 here.
    _,exp,kind=prior.check_texture_slot(before,after,owner,export_guid,source.resolve,{(28,*key):exact})
    return key,exp,kind,cls

def run(a,report):
    plan=json.loads(a.plan.read_text())
    need(plan["schema_version"]==1,"invalid_private_plan")
    source=Source(a)
    mat,mk,xk,trace=join(a,plan,source)
    report["selected_exact_original_graph_rejoined"]=True
    report["phase"]="mesh_and_material"
    index=prior.file_index(a.project,{mk[0],xk[0]})
    need(set(index)=={mk[0],xk[0]},"selected_asset_identity_missing")
    try:
        report["mesh"]=prior.mesh_check(source,tuple(plan["mesh"]),index[xk[0]][0],xk[1])
    except Exception as exc:
        report["mesh"]={"status":"UNPROVEN","reason":prior.classify(exc)}
    actual=native.strict_mapping(prior.document(index[mk[0]][0],mk[1],21))
    need(set(actual)=={"Material"} and type(actual["Material"]) is dict,"actual_material_root")
    actual=actual["Material"]
    try:
        report["material_values"]={"status":"MATCH","counts":values.compare(mat,actual)}
    except values.Mismatch:
        report["material_values"]={"status":"MISMATCH"}
    except Exception as exc:
        report["material_values"]={"status":"UNPROVEN","reason":prior.classify(exc)}
    report["phase"]="typed_texture_dependencies"
    before=normalize_texenvs(mat["m_SavedProperties"]["m_TexEnvs"])
    after=normalize_texenvs(actual["m_SavedProperties"]["m_TexEnvs"],exported=True)
    rows=Counter()
    linked={}
    array_sources={}
    for prop in sorted(before.keys()&after.keys()):
        planned=plan["texture_targets"].get(prop)
        if planned is not None and planned["class"]==187:
            try:
                ptr=before[prop][0]
                key=source.resolve(plan["material"][0],{"m_FileID":ptr[0],"m_PathID":ptr[1]})
                need(key==tuple(planned["key"]),"private_texture_plan_identity_drift")
                array_sources[key]=texture_observation.array_source(source.obj(key,"Texture2DArray").read_typetree(check_read=False))
            except Exception as exc:
                rows["array_source_"+prior.classify(exc)]+=1
        try:
            value=exact_slot(before[prop],after[prop],plan["material"][0],mk[0],source,trace,
                             plan["texture_targets"].get(prop))
            if value is None:
                rows["null_slots_matched"]+=1
                continue
            key,exp,kind,cls=value
            need(linked.setdefault(key,(exp,kind,cls))==(exp,kind,cls),"inconsistent_texture_target")
            rows["nonnull_exact_typed_pointer_and_UV"]+=1
            rows["class_"+str(cls)+"_slots"]+=1
        except Exception as exc:
            rows["slot_"+prior.classify(exc)]+=1
    report["texture_slots"]={"source":len(before),"export":len(after),"missing":len(before.keys()-after.keys()),
                             "extra":len(after.keys()-before.keys()),"counts":dict(rows)}
    report["selected_array_source_observations"]=list(array_sources.values())
    targets=prior.file_index(a.project,{v[0][0] for v in linked.values()})
    observed=[]
    for key,(exp,kind,cls) in sorted(linked.items()):
        record={"class":cls,"physical_target_present":exp[0] in targets}
        try:
            need(record["physical_target_present"],"traced_texture_asset_missing")
            path,meta=targets[exp[0]]
            if cls==28:
                need(kind==0 or audit.registry.is_texture(path,meta,exp[1]),"typed_Texture2D_target_not_proven")
                record.update(prior.texture_check(source,key,path,meta,exp[1],kind,semantic_observation=True))
            elif cls==187 and path.suffix.lower()==".png":
                need(key in array_sources,"selected_array_source_metadata_unproven")
                record.update(texture_observation.array_png_observation(array_sources[key],path,meta,exp[1],kind))
                if a.repair_selected_array:
                    matpath=index[mk[0]][0]
                    mat_before=zip2.fingerprint(matpath)
                    record["selected_array_repair"]=selected_array.run(source.obj(key,"Texture2DArray"),path,meta,exp[0],exp[1],kind,repair=True)
                    need(zip2.fingerprint(matpath)==mat_before,"selected_material_changed_during_array_grid_repair")
                    record["selected_array_repair"]["material_bytes_unchanged"]=True
                    if record["selected_array_repair"]["private_grid_repair_applied"]:
                        record["status"]="ARRAY_GRID_REPAIRED_TOP_MIPS_MATCH"
            elif path.suffix.lower() in (".asset",".cubemap",".rendertexture",".mat",".unity",".prefab"):
                body=prior.document(path,exp[1],cls)
                root=native.strict_mapping(body)
                name=next(k for k,v in prep.TYPES.items() if v==cls)
                need(set(root)=={name} and type(root[name]) is dict,"typed_texture_document_root")
                record.update(status="TYPED_NATIVE_DOCUMENT_ONLY",reason="non_Texture2D_pixel_decoder_not_tested")
            else:
                record.update(status="UNPROVEN",reason="non_Texture2D_importer_identity_not_proven")
        except Exception as exc:
            record.update(status="UNPROVEN",reason=str(exc) if isinstance(exc,selected_array.SelectedArrayError) else prior.classify(exc))
        observed.append(record)
    report["texture_unique_targets"]=len(linked)
    report["texture_results"]=observed
    report["physical_texture_targets_present"]=sum(v["physical_target_present"] for v in observed)
    report["texture_status_counts"]=dict(Counter(v["status"] for v in observed))
    report["serialized_mesh_fields_match"]=report["mesh"]["status"]=="MATCH"
    report["serialized_material_values_match"]=report["material_values"]["status"]=="MATCH"
    report["all_saved_TexEnv_edges_and_UV_match"]=(set(before)==set(after) and
        rows["null_slots_matched"]+rows["nonnull_exact_typed_pointer_and_UV"]==len(before))
    two=[v for v in observed if v["class"]==28]
    report["all_linked_Texture2D_top_mips_match"]=bool(two) and all(v["status"]=="MATCH" for v in two)
    report["all_nonnull_texture_payloads_verified"]=bool(observed) and all(v["status"]=="MATCH" for v in observed) and report["all_saved_TexEnv_edges_and_UV_match"]
    report["bounded_mesh_material_texture_top_mip_closure"]=(report["serialized_mesh_fields_match"] and
        report["serialized_material_values_match"] and report["all_nonnull_texture_payloads_verified"])
    report["status"]=STATUS
    report["phase"]="complete"

def main():
    p=argparse.ArgumentParser()
    for name in ("original","manifest","project","w1","b02","renderer-trace","plan","out"):
        p.add_argument("--"+name,type=Path,required=True)
    p.add_argument("--repair-selected-array",action="store_true",
                   help="Only in the disposable actual export, after exact source layer parity")
    a=p.parse_args()
    report={"status":"INCONCLUSIVE","phase":"same_instance_join","unity_gpu_pixels_verified":False,
            "white_mesh_repair_verified":False,"full_mip_sampler_ABI_verified":False,
            "production":False,"android_device":False,"XAPK":False}
    try:
        run(a,report)
    except Exception as exc:
        report["failure_category"]=prior.classify(exc)
    with a.out.open("x") as f:
        json.dump(report,f,indent=2,sort_keys=True)
        f.write("\n")
    print("GT_TOP_PRESTAGED_EXACT_RESOURCE_RECHECK "+json.dumps(report,sort_keys=True))
    return 0 if report["status"]==STATUS else 2

if __name__=="__main__":
    raise SystemExit(main())
