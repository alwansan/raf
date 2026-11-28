"""Source-bound, exact seven-mip native Texture2D export correction.

Private selection and bytes remain runner-local. The real configured exporter
must first select a redirect for the exact processed object. No broad cache
bypass, guessed pointer, PNG regeneration, player or Android pixel assertion.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re

from scripts import b05_verify_material_texenv_bindings as b05
from scripts import t3_original_particle_material_texenv as original
from scripts import t3_particle_same_export_bindings as binding
from scripts import gt_particle108_source_pixel_parity as pixels
from scripts import gt_texture_route_payload as native
from scripts.gt_particle108_local_texture_document import strict_mapping
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from tools.gt_particle108_redirect_target import audit

EXPECTED=(64,64,4,7,1,2,21844)
SAMPLER=("m_FilterMode","m_Aniso","m_MipBias","m_WrapU","m_WrapV","m_WrapW")
FIELDS=native.FIELDS
STATUS="EXACT_ORIGINAL_PARTICLE108_NATIVE_SEVEN_MIP_EXPORT"

def need(x,reason):
    if not x: raise audit.ProbeReject(reason)

def select(candidates):
    keys=[key for key,meta in candidates.items() if tuple(meta.get(k) for k in FIELDS)==EXPECTED
          and meta.get("m_MipsStripped")==0 and meta.get("m_LightmapFormat")==0
          and meta.get("m_ColorSpace")==1]
    need(len(keys)==1,"source_seven_mip_identity_not_unique")
    return keys[0]

def sampler(t):
    s=t.m_TextureSettings
    out={k:getattr(s,k,None) for k in SAMPLER}
    need(all(isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x) for x in out.values()),
         "original_sampler_unproved")
    return {k:float(v) if k=="m_MipBias" else int(v) for k,v in out.items()}

def select_source(root,manifest):
    pixels.authenticated_provider_pins(manifest)
    slots,targets={},{}
    scope=original.run(root,manifest,private_material_texenvs=slots,private_local_texture_targets=targets)
    need(scope.get("status")==original.STATUS and len(slots)==5 and len(targets)==3
         and scope.get("six_original_scene_SHA_verified") is True
         and scope.get("four_original_shader_Material_owner_SHA_verified") is True
         and scope.get("original_108_use_ParticleShader48_reference_authenticated") is True,
         "untrusted_original_particle_scope")
    rows={}; textures={}
    for key in targets:
        owner,pid=key
        need(owner in SHADER_OWNERS,"unverified_source_owner")
        _,t=audit.load_texture(root/"Raft_Data"/owner,SHADER_OWNERS[owner],pid)
        rows[key]={k:getattr(t,k,None) for k in (*FIELDS,"m_MipsStripped","m_LightmapFormat","m_ColorSpace")}
        textures[key]=t
    key=select(rows)
    t=textures[key]
    need(not getattr(t,"m_PlatformBlob",None),"unsupported_platform_blob")
    payload,kind=pixels.exact_payload(t,root/"Raft_Data",manifest)
    need(kind=="stream" and len(payload)==21844,"original_mip_stream_extent")
    tree={k:int(v) for k,v in rows[key].items()}
    tree["m_StreamData"]={"path":"","offset":0,"size":0}
    tree["image data"]=payload
    proof=native.proof(tree)
    return slots,targets,key,proof,sampler(t)

def source_approval(root,manifest,path):
    need(not path.exists(),"private_approval_already_exists")
    _,_,key,proof,_=select_source(root,manifest)
    # Only the independently selected source owner/object and exact payload
    # admission are passed to the disposable actual exporter.
    data={"owner":key[0],"path_id":key[1],"payload_sha256":proof.sha256,"payload_bytes":proof.length}
    with path.open("x",encoding="utf8") as f:
        path.chmod(0o600);json.dump(data,f)
    return {"status":"SOURCE_NATIVE_MIP_APPROVAL","source_owner_SHA_verified":True,
            "payload_bytes":proof.length,"mip_count":len(proof.mip_lengths),
            "private_ids_or_payload_disclosed":False}

def actual_body(project,ptr):
    anchor,guid,kind=ptr
    need(anchor>0 and kind==2 and guid not in {"0"*32,*b05.ENGINE},"not_native_external_texture_pointer")
    matches=[]
    for meta in (project/"Assets").rglob("*.meta"):
        need(not meta.is_symlink(),"linked_export_meta")
        raw=pixels.bounded_snapshot(meta,256*1024).decode("utf-8-sig")
        if guid in {g.lower() for g in b05.GUID.findall(raw)}:
            need(len(b05.GUID.findall(raw))==1,"ambiguous_texture_meta")
            data=strict_mapping(raw)
            need(data.get("guid")==guid and type(data.get("NativeFormatImporter")) is dict
                 and data["NativeFormatImporter"].get("mainObjectFileID")==anchor,
                 "native_meta_identity_mismatch")
            matches.append(meta.with_suffix(""))
    need(len(matches)==1 and matches[0].suffix in (".texture2D",".asset"),"native_texture_asset_not_unique")
    text=pixels.bounded_snapshot(matches[0],256*1024).decode("utf-8-sig")
    headers=list(b05.ALL_HEADER.finditer(text))
    need(len(headers)==1,"native_texture_document_not_unique")
    h=b05.DOCUMENT_HEADER.fullmatch(headers[0].group())
    need(h is not None and int(h[1])==28 and int(h[2])==anchor and not h[3],
         "native_texture_class_anchor_mismatch")
    doc=strict_mapping(text[headers[0].end():])
    need(set(doc)=={"Texture2D"} and type(doc["Texture2D"]) is dict,"native_texture_body_missing")
    return doc["Texture2D"]

def verify(root,manifest,project,w1,b02):
    slots,targets,key,proof,source_sampler=select_source(root,manifest)
    w1=json.loads(w1.read_text());b02=json.loads(b02.read_text())
    joined=binding.assess(slots,targets,w1,b02,b05.exported_texenvs(project))
    need(joined.get("status")==binding.STATUS_MATCH and joined.get("selected_exact_material_texenv_pointer_matches")==10
         and joined.get("selected_uv_scale_offset_matches")==10
         and joined.get("selected_texture2d28_missing_export_trace")==0,
         "actual_native_same_export_pointer_join_failed")
    rows=[r for r in b02["objects"] if b05._trace_source(r)==key]
    need(len(rows)==1,"native_texture_trace_not_unique")
    ptr=b05._trace_export(rows[0])
    body=actual_body(project,ptr)
    actual=native.proof(body,exported=True)
    n,mips=native.compare(proof,actual)
    need(body.get("m_ColorSpace")==1 and body.get("m_LightmapFormat")==0
         and not body.get("m_PlatformBlob"),"native_texture_usage_drift")
    ss=body.get("m_TextureSettings")
    need(type(ss) is dict and all(type(ss.get(k)) in (int,float) and math.isclose(ss[k],v,rel_tol=0,abs_tol=1e-6)
                                  for k,v in source_sampler.items()),"native_texture_sampler_drift")
    return {"status":STATUS,"source_owner_and_stream_SHA_verified":True,
            "same_export_instance":True,"selected_materials":5,"selected_texture_targets":3,
            "material_texture_pptr_matches":10,"material_uv_matches":10,
            "selected_native_class28_asset":True,"native_importer_meta_identity_verified":True,
            "mip_bytes_equal":n,"mip_levels_equal":mips,"mip_lengths":list(proof.mip_lengths),
            "source_sampler_fields_equal":len(source_sampler),"color_space_and_usage_equal":True,
            "unity_import_verified":False,"android_pixels_verified":False,"black_fire_restored":False,
            "private_ids_or_payload_disclosed":False,"production":False,"XAPK":False}

def patch(tool,source):
    dest=tool/"Source/AssetRipper.Export.UnityProjects"
    p=dest/"ProjectExporter.cs"
    a="\t\tList<IExportCollection> collections = CreateCollections(fileCollection);"
    text=p.read_text(encoding="utf8")
    need(text.count(a)==1 and text.count("RaftExportLineage.Capture(container, collections);")==1,
         "native_override_patch_anchor")
    c=dest/"RaftGTNativeMipExporter.cs"
    need(not c.exists(),"native_override_already_staged")
    c.write_bytes(source.read_bytes())
    p.write_text(text.replace(a,"\t\tRaftGTNativeMipExporter.Register(this, fileCollection, CreateCollection);\n"+a),encoding="utf8")

def main():
    p=argparse.ArgumentParser();p.add_argument("mode",choices=("patch","prepare","verify"))
    for k in ("tool","source","original","manifest","project","w1","b02","approval","out"):
        p.add_argument("--"+k,type=Path)
    a=p.parse_args()
    if a.mode=="patch":
        patch(a.tool,a.source);return 0
    phase=a.mode
    try:
        r=source_approval(a.original,a.manifest,a.approval) if phase=="prepare" else verify(a.original,a.manifest,a.project,a.w1,a.b02)
        code=0
    except Exception as e:
        r={"status":"INCONCLUSIVE","phase":phase,"failure_category":type(e).__name__,
           "private_ids_or_payload_disclosed":False}
        if isinstance(e,(audit.ProbeReject,native.Unproven,native.Mismatch)):r["reject_reason"]=str(e)
        code=2
    a.out.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n")
    print("GT_PARTICLE108_NATIVE_MIPS "+json.dumps(r,sort_keys=True))
    return code

if __name__=="__main__":raise SystemExit(main())
