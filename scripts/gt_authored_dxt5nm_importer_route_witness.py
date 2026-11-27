"""Actual authored V12 witness; V11 pixel gate must remain green for each V12 control."""
from dataclasses import asdict
from pathlib import Path
import argparse
import json
from copy import deepcopy
import yaml
from scripts import gt_renderer_submesh_routes as gate
from scripts import gt_imported_dxt5nm_route_importer as nm
from scripts import gt_imported_png_route_importer as v9
from scripts import gt_imported_png_route_pixels as png
from scripts.gt_authored_imported_png_route_witness import load,need

FIELD="selected_same_route_imported_dxt5nm_supported_serialized_importer_state_verified"
FULL="selected_same_route_imported_dxt5nm_complete_supported_schema_verified"
SWIZZLE="selected_same_route_imported_dxt5nm_swizzle_verified"
V11="selected_same_route_imported_dxt5nm_png_top_mip_and_importer_verified"

def audit(root,out):
    root=Path(root);out=Path(out)
    need(not out.exists() and out.parent.is_dir(),"fresh_V12_receipt")
    states={}
    objects,externals,mapping,vertices,proofs,requests,pins,producer=load(root,states=states,bc3_mode=True,normalmap=True)
    need(producer.get("bc3_fixture_variant")=="normalmap_dxt5nm","normalmap_fixture_variant")
    files,docs=gate.actual_index(root/"project",mapping)
    need(len(files)==9 and len(docs)==11 and set(states)==set(proofs) and len(states)==2,"V12_actual_population")
    keys=sorted(states)
    need(all(type(p) is nm.Proof for p in states.values()),"V12_distinct_source_proof")
    def run(f=files,s=states,*,v12=True):
        return gate.compare(objects,externals,mapping,f,docs,vertex_payloads=vertices,
            material_values=True,material_keywords=True,png_top_mips=proofs,png_normalmap=True,
            png_importer_states=s if v12 else None)
    baseline=run();v11=run(v12=False)
    need(v11[V11] and v11["schema_version"]==11 and FIELD not in v11,"V11_independent_baseline")
    rows=[]
    for k in keys:
        ptr=mapping[k][1];path,meta=files[ptr[0]]
        imp=png.importer_document(meta,ptr,texture_type=1)
        rows.append(dict(source=asdict(states[k]),actual_metadata=meta,source_rgba_sha256=proofs[k].rgba_sha256,
                         swizzle_present="swizzle" in imp))
    (out.parent/"normalmap-importer-diagnostic.json").write_text(json.dumps(dict(baseline=baseline,source_and_actual=rows),indent=2,sort_keys=True)+"\n")
    need(baseline[FIELD] and baseline["schema_version"]==12 and not baseline["reason_counts"],"V12_actual_baseline:"+str(baseline["reason_counts"]))
    need(not baseline[FULL] and not baseline[SWIZZLE] and all(not row["swizzle_present"] for row in rows),"V12_swizzle_absence_scope")
    for k,v in {"complete_renderer_routes":2,"complete_imported_png_bound_submesh_routes":4,
                "imported_png_top_mip_slots_matched":4,"imported_png_pixels_matched_per_route":140,
                "imported_png_importer_state_slots_matched":4,"imported_png_importer_sampler_fields_matched_per_route":24,
                "imported_png_importer_source_mapping_fields_matched_per_route":36,
                "imported_png_importer_exporter_policy_fields_matched_per_route":68,
                "dxt5nm_importer_observed_bumpmap_defaults_matched_per_route":12,
                "imported_png_importer_swizzle_unknown_slots":4}.items():
        need(baseline["counts"].get(k)==v,"V12_count:"+k)
    for f in ("selected_same_route_imported_png_supported_serialized_importer_state_verified",
              "selected_same_route_imported_png_serialized_importer_state_verified",
              "selected_same_route_imported_png_top_mip_verified","selected_same_route_imported_bc3_png_top_mip_verified",
              "selected_same_route_native_texture_sampler_verified","dxt5nm_lower_mips_or_Unity_import_verified",
              "dxt5nm_GPU_normal_fidelity_verified","original_runtime_importer_or_Android_platform_fidelity_verified"):
        need(baseline.get(f,False) is False,"V12_scope_promotion:"+f)
    k=keys[0];ptr=mapping[k][1];path,meta=files[ptr[0]]
    # Metadata mutations preserve the actual GUID and exact PNG. Require
    # old V11 to stay true and the new gate to fail with the expected reason.
    controls={}
    def reject(name,reason,f=files,s=states):
        old=run(f,s,v12=False)
        need(old[V11],"V11_control_not_pass:"+name)
        result=run(f,s)
        need(not result[FIELD] and result["reason_counts"].get(reason,0)>0,"V12_control_not_rejected:"+name+":"+str(result["reason_counts"]))
        controls[name]={"reason":reason,"V11_pass":True}
    def edit(name,scope,key,value,reason):
        d=yaml.safe_load(meta);obj=d["TextureImporter"]
        if scope=="platformSettings":obj=obj[scope][0]
        elif scope:obj=obj[scope]
        need(key not in obj or obj[key]!=value,"V12_control_degenerate:"+name)
        obj[key]=value
        f=dict(files);f[ptr[0]]=(path,yaml.safe_dump(d))
        reject(name,reason,f)
    # Mutate all six distinct sampler fields independently.
    for name,value in (("filterMode",2),("aniso",3),("mipBias",.25),("wrapU",1),("wrapV",1),("wrapW",2)):
        edit("sampler_"+name,"textureSettings",name,value,"same_route_png_importer_"+name+"_drift")
    for scope,name,value in (("mipmaps","enableMipMap",0),(None,"isReadable",0),(None,"streamingMipmaps",1),
                              (None,"streamingMipmapsPriority",3),(None,"maxTextureSize",4096)):
        edit("mapping_"+name,scope,name,value,"same_route_png_source_mapping_"+name+"_drift")
    for scope,name,value in ((None,"alphaIsTransparency",0),(None,"nPOTScale",1),(None,"compressionQuality",51),
                              ("platformSettings","overridden",1),("platformSettings","textureCompression",0)):
        edit("policy_"+name,scope,name,value,"same_route_png_exporter_policy_"+name+"_drift")
    edit("heightScale","bumpmap","heightScale",.5,"same_route_png_normal_exporter_policy_heightScale_drift")
    for name in ("convertToNormalMap","externalNormalMap","normalMapFilter"):
        edit("default_"+name,"bumpmap",name,1,"same_route_png_normal_observed_bumpmap_default_"+name+"_drift")
    edit("wrong_swizzle",None,"swizzle",0,"same_route_png_exporter_policy_swizzle_drift")
    edit("null_swizzle",None,"swizzle",None,"invalid_png_exporter_policy_swizzle")
    bad=dict(states);bad[k]=states[keys[1]]
    reject("same_size_source_state_swap","same_route_png_importer_filterMode_drift",s=bad)
    bad=dict(states);bad[k]=v9.Proof(**asdict(states[k]))
    reject("ordinary_V9_receipt","missing_png_source_importer_proof",s=bad)
    bad=dict(states);del bad[k]
    reject("missing_source_state","missing_png_source_importer_proof",s=bad)
    # Explicit identity swizzle is a counterfactual positive, not actual evidence.
    f=dict(files)
    for key in keys:
        p=mapping[key][1];image,md=files[p[0]]
        d=yaml.safe_load(md);d["TextureImporter"]["swizzle"]=50462976
        f[p[0]]=(image,yaml.safe_dump(d))
    explicit=run(f)
    need(explicit[FIELD] and explicit[FULL] and explicit[SWIZZLE] and
         explicit["counts"]["imported_png_importer_exporter_policy_fields_matched_per_route"]==72,
         "V12_explicit_swizzle_positive_control")
    result=dict(status="PASS_ACTUAL_AUTHORED_PUBLIC_DXT5NM_SUPPORTED_IMPORTER_STATE_ROUTE_JOIN",
        baseline=baseline,source_and_actual=rows,controls=controls,counterfactual_count=len(controls),
        explicit_swizzle_positive_control_only=True,actual_full_supported_schema_verified=False,
        actual_swizzle_verified=False,source_states=2,actual_importers=2,
        original_assets_read=False,original_serialized_source_verified=False,Unity_import_verified=False,
        Android_device=False,XAPK=False)
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps(result,sort_keys=True))

def main():
    p=argparse.ArgumentParser();p.add_argument("--root",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();audit(a.root,a.out)

if __name__=="__main__":main()
