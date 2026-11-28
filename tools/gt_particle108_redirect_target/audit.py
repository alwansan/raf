"""Compare original Particle108 redirect against its exact original PC engine target.

All private source IDs, pointers, object bytes and decoded pixels stay in the
isolated runner. No exporter override, Android runtime assertion or raw upload.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from scripts import b05_verify_material_texenv_bindings as b05
from scripts import t3_original_particle_material_texenv as original
from scripts import t3_particle_same_export_bindings as binding
from scripts import gt_particle108_source_pixel_parity as pixels
from scripts import w1_stage_zip2_owners as staging
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS

REDIRECT="AssetRipper.Export.UnityProjects.RedirectExportCollection"
ENGINE_FILES={
    "0000000000000000e000000000000000":"Raft_Data/Resources/unity default resources",
    "0000000000000000f000000000000000":"Raft_Data/Resources/unity_builtin_extra",
}
OBSERVED="OBSERVED_ORIGINAL_PC_ENGINE_REDIRECT_TARGET"
META=("m_Width","m_Height","m_TextureFormat","m_TextureDimension","m_ImageCount",
      "m_MipCount","m_MipsStripped","m_LightmapFormat","m_TextureUsageMode",
      "m_ColorSpace","m_CompleteImageSize")

class ProbeReject(ValueError):
    pass

def require(ok,reason):
    if not ok:
        raise ProbeReject(reason)

def selected_redirect(targets,b02):
    require(type(targets) is dict and len(targets)==3,"source_target_scope")
    selected=[]
    for row in b02["nonexportable_texture_sources"]:
        key=b05._trace_source(row)
        if key not in targets:
            continue
        require(row.get("collection_implementation")==REDIRECT,"wrong_collection")
        require(row.get("container_export_pointer_captured") is True,"missing_pointer")
        p=row["container_export"]
        require(set(p)=={"file_id","guid","type"},"pointer_schema")
        ptr=b05._export_pointer({"fileID":p["file_id"],"guid":p["guid"],"type":p["type"]})
        require(ptr[0]>0 and ptr[1] in ENGINE_FILES and ptr[2]==0,"not_exact_builtin_pointer")
        group=row.get("same_texture_sprite_group")
        count=row.get("sprite_group_count")
        require(type(group) is bool and type(count) is int and -1<=count<=100000,
                "missing_processed_group_evidence")
        require((group and count>=0) or not group,"inconsistent_sprite_group")
        selected.append((key,ptr,group,count))
    require(len(selected)==1,"selected_redirect_not_unique")
    return selected[0]

def metadata(t):
    # Numeric descriptors only; no source labels or private IDs.
    result={}
    for name in META:
        x=getattr(t,name,None)
        if x is None:
            continue
        require(isinstance(x,int) and not isinstance(x,bool),"unsupported_texture_metadata")
        result[name[2:]]=int(x)
    require(all(k in result for k in ("Width","Height","TextureFormat","TextureDimension","ImageCount","MipCount")),
            "incomplete_texture_metadata")
    return result

def load_texture(path,pin,pid):
    import UnityPy
    raw=pixels.verified_range(path,pin,0,pin[0])
    env=UnityPy.load(raw)
    matches=[o for o in env.file.objects.values() if o.path_id==pid]
    require(len(matches)==1,"target_pathid_not_unique")
    obj=matches[0]
    require(obj.type.name=="Texture2D","target_not_texture2d")
    return obj, obj.read()

def raw_digest(obj):
    raw=obj.get_raw_data()
    require(isinstance(raw,(bytes,bytearray,memoryview)) and len(raw)>0,"missing_raw_texture_object")
    return hashlib.sha256(raw).hexdigest()

def compare(original_root,manifest,engine_root,project,w1_path,b02_path,out):
    report={"status":"INCONCLUSIVE","phase":"source_scope",
            "original_pc_engine_target_only":True,"android_target_pixels_verified":False,
            "black_fire_restored":False,"production":False,"player":False,"XAPK":False,
            "private_source_ids_pointers_bytes_or_pixels_published":False}
    try:
        # Independently authenticate the exact manifest blob before using any range.
        pixels.authenticated_provider_pins(manifest)
        slots,targets={},{}
        scope=original.run(original_root,manifest,private_material_texenvs=slots,
                           private_local_texture_targets=targets)
        require(scope.get("status")==original.STATUS and
                scope.get("six_original_scene_SHA_verified") is True and
                scope.get("four_original_shader_Material_owner_SHA_verified") is True and
                scope.get("original_108_use_ParticleShader48_reference_authenticated") is True,
                "untrusted_source_graph")
        w1=json.loads(w1_path.read_text())
        b02=json.loads(b02_path.read_text())
        exported=b05.exported_texenvs(project)
        linked=binding.assess(slots,targets,w1,b02,exported)
        require(linked["status"]==binding.STATUS_NONEXPORTABLE_MATCH and
                linked.get("selected_nonexportable_collection_implementations")=={REDIRECT:1},
                "same_export_pointer_not_proven")
        key,ptr,group,count=selected_redirect(targets,b02)
        report.update(same_export_pointer_verified=True,actual_redirect_collection=True,
                      selected_processed_same_texture_sprite_group=group,
                      selected_processed_sprite_count=count)
        report["phase"]="original_source_texture"
        owner,pid=key
        require(owner in SHADER_OWNERS,"unverified_source_owner")
        source_obj,source=load_texture(original_root/"Raft_Data"/owner,SHADER_OWNERS[owner],pid)
        src_payload,kind=pixels.exact_payload(source,original_root/"Raft_Data",manifest)
        report.update(source_metadata=metadata(source),source_payload_bytes=len(src_payload),
                      source_payload_storage=kind,source_owner_SHA_verified=True,
                      source_raw_object_digest_computed=bool(raw_digest(source_obj)))
        report["phase"]="engine_target_texture"
        rel=ENGINE_FILES[ptr[1]]
        target_obj,target=load_texture(engine_root/rel,staging.PINS[rel],ptr[0])
        report.update(engine_target_owner_SHA_verified=True,engine_target_exact_pathid_class28=True,
                      engine_target_catalogue="default_resources" if ptr[1].startswith("0000000000000000e") else "builtin_extra",
                      target_metadata=metadata(target),
                      same_cache_key_name_and_dimensions=(source.m_Name==target.m_Name and
                          source.m_Width==target.m_Width and source.m_Height==target.m_Height),
                      target_raw_object_digest_computed=bool(raw_digest(target_obj)))
        target_payload,target_kind=pixels.exact_payload(target,(engine_root/rel).parent,manifest)
        report.update(target_payload_bytes=len(target_payload),target_payload_storage=target_kind,
                      payload_bytes_equal=src_payload==target_payload)
        report["phase"]="independent_decoded_top_mip_comparison"
        src_image=pixels.decode_payload(source,src_payload)
        dst_image=pixels.decode_payload(target,target_payload)
        report["top_mip_comparison"]=pixels.compare_pixels(src_image,dst_image)
        report["status"]=OBSERVED
        report["phase"]="complete"
    except Exception as e:
        # Do not print arbitrary exception text; it may carry private IDs/paths.
        report["failure_category"]=type(e).__name__
        if isinstance(e,ProbeReject):
            report["reject_reason"]=str(e)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("GT_PARTICLE108_ORIGINAL_PC_REDIRECT_TARGET "+json.dumps(report,sort_keys=True))
    return 0 if report["status"]==OBSERVED else 2

def main():
    p=argparse.ArgumentParser()
    for k in ("original","manifest","engine","project","w1-trace","b02-trace","out"):
        p.add_argument("--"+k,type=Path,required=True)
    a=p.parse_args()
    require(not a.out.exists() and not any(a.out.resolve().is_relative_to(x.resolve())
            for x in (a.original,a.engine,a.project)),"unsafe_public_output")
    return compare(a.original,a.manifest,a.engine,a.project,a.w1_trace,a.b02_trace,a.out)

if __name__=="__main__":
    raise SystemExit(main())
