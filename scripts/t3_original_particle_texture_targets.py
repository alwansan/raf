#!/usr/bin/env python3
"""T3: SHA-original ParticleShader48 linked Texture2D28 type/stream inventory.

The unique original 108-use Particle Shader48 is selected from six verified
original scenes and four SHA-pinned owner files. Its five Material21 objects
link ten local Texture PPtrs. Resolve these PRIVATE owner/pathIDs to real
original Texture2D class 28 and check m_StreamData against the immutable
ZIP2 manifest; emit only numeric source/stream counts. No source image bytes,
private object IDs/names/proprietary paths or Shader code enter reports.
"""
from __future__ import annotations

import argparse
from collections import Counter
import os
import json
from pathlib import Path, PurePosixPath

from scripts import t3_original_particle_material_texenv as particle_material
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.t3_original_texture_stream_dependencies import manifest_stream_index
from scripts.w1_stage_zip2_owners import fingerprint, ZIP2_SHA

STATUS="ZIP2_ORIGINAL_PARTICLE108_THREE_TEXTURE2D28_SOURCE_STREAM_PROVEN"
EXPECTED_LOCAL_TEXTURE_REFERENCES=10
EXPECTED_DISTINCT_TEXTURE_TARGETS=3


def assess(targets:dict, records:dict, manifest_providers:dict, staged:Path,
           *, expected_local:int=EXPECTED_LOCAL_TEXTURE_REFERENCES,
           expected_distinct:int=EXPECTED_DISTINCT_TEXTURE_TARGETS,
           private_stream_plan:dict|None=None):
    """Analyze PRIVATE Texture2D typetrees; do not write identifiers to result.

    targets: {(original_owner, private_path_id): count of Material TexEnv refs}
    records: same keys mapped to (type_name, filtered original Texture2D fields)
    manifest_providers: {basename: (original_size, original_sha256)}
    """
    if (type(targets) is not dict or type(records) is not dict
        or type(manifest_providers) is not dict
        or not isinstance(staged,Path)
        or len(targets)!=expected_distinct or set(records)!=set(targets)
        or sum(targets.values())!=expected_local):
        raise ValueError("incomplete_original_particle_Texture2D28_source_scope")
    if (type(expected_distinct) is not int or expected_distinct<1
        or type(expected_local) is not int or expected_local<expected_distinct):
        raise ValueError("untrusted_original_particle_Texture2D_reference_expectation")
    if private_stream_plan is not None and (type(private_stream_plan) is not dict
        or private_stream_plan):
        raise ValueError("private_original_stream_plan_outparam_must_be_empty_dict")
    stats=Counter()
    used_stream_names=set()
    private_providers={}
    for (owner,pid),row in records.items():
        if (owner not in particle_material.source.MATERIAL_OWNERS
            or type(pid) is not int or pid<=0
            or type(targets[(owner,pid)]) is not int or targets[(owner,pid)]<=0
            or type(row) is not tuple or len(row)!=2
            or row[0]!="Texture2D" or type(row[1]) is not dict):
            raise ValueError("selected_original_particle_texture_not_class28")
        tree=row[1]
        width,height=tree.get("m_Width"),tree.get("m_Height")
        fmt=tree.get("m_TextureFormat")
        complete=tree.get("m_CompleteImageSize")
        if (type(width) is not int or type(height) is not int
            or not 0<width<=65536 or not 0<height<=65536
            or type(fmt) is not int or fmt<0
            or type(complete) is not int or complete<0):
            raise ValueError("invalid_original_particle_Texture2D_metadata")
        stats["original_selected_typed_Texture2D28_targets"]+=1
        stats["original_selected_Texture2D28_material_bindings"]+=targets[(owner,pid)]
        raw=tree.get("m_StreamData")
        if raw is None:
            stats["original_selected_Texture2D28_without_stream_field"]+=1
            continue
        if (type(raw) is not dict or not {"path","offset","size"}<=set(raw)
            or type(raw["path"]) is not str or type(raw["offset"]) is not int
            or type(raw["size"]) is not int or raw["offset"]<0 or raw["size"]<0):
            raise ValueError("malformed_original_particle_Texture2D_StreamData")
        path,offset,size=raw["path"],raw["offset"],raw["size"]
        if size==0 and not path:
            stats["original_selected_Texture2D28_inline_or_unstreamed"]+=1
            continue
        if size==0 or not path:
            raise ValueError("ambiguous_original_particle_Texture2D_StreamData")
        parts=PurePosixPath(path.replace("\\","/")).parts
        if (not parts or any(part in ("..",".") for part in parts)
            or not parts[-1].endswith((".resS",".resource"))):
            raise ValueError("unsupported_original_particle_texture_stream_path")
        name=parts[-1]  # private; basename MUST NOT be emitted.
        provider=manifest_providers.get(name)
        if (type(provider) is not tuple or len(provider)!=2
            or type(provider[0]) is not int or provider[0]<=0
            or type(provider[1]) is not str or len(provider[1])!=64):
            raise ValueError("original_particle_texture_stream_missing_manifest_pin")
        if offset+size>provider[0]:
            raise ValueError("original_particle_texture_stream_extent_beyond_manifest")
        used_stream_names.add(name)
        provider_plan=private_providers.setdefault(name,{
            "bytes":provider[0],"sha256":provider[1],"ranges":[]})
        if provider_plan["bytes"]!=provider[0] or provider_plan["sha256"]!=provider[1]:
            raise ValueError("source_particle_stream_manifest_pin_changed")
        provider_plan["ranges"].append([offset,size])
        stats["original_selected_Texture2D28_manifest_verified_streamed"]+=1
        # Do not stage .resS payloads merely to inspect source metadata;
        # check real file hash only if the bounded source workflow staged one.
        candidate=staged/name
        if candidate.is_symlink():
            raise ValueError("unsafe_staged_original_particle_texture_stream")
        if candidate.is_file():
            if fingerprint(candidate)!=provider:
                raise ValueError("original_particle_texture_stream_staged_SHA_mismatch")
            stats["original_selected_Texture2D28_stream_payload_SHA_verified"]+=1
        elif candidate.exists():
            raise ValueError("invalid_staged_original_particle_texture_stream")
        else:
            stats["original_selected_Texture2D28_stream_provider_not_staged"]+=1
    if (stats["original_selected_typed_Texture2D28_targets"]!=expected_distinct
        or stats["original_selected_Texture2D28_material_bindings"]!=expected_local
        or stats["original_selected_typed_Texture2D28_targets"]!=sum(
          stats[k] for k in (
            "original_selected_Texture2D28_without_stream_field",
            "original_selected_Texture2D28_inline_or_unstreamed",
            "original_selected_Texture2D28_manifest_verified_streamed"))
        or stats["original_selected_Texture2D28_manifest_verified_streamed"]!=(
            stats["original_selected_Texture2D28_stream_payload_SHA_verified"]+
            stats["original_selected_Texture2D28_stream_provider_not_staged"])):
        raise ValueError("original_particle_Texture2D28_stream_accounting_mismatch")
    if private_stream_plan is not None:
        if (len(private_providers)!=len(used_stream_names)
            or sum(len(v["ranges"]) for v in private_providers.values())
              !=stats["original_selected_Texture2D28_manifest_verified_streamed"]):
            raise ValueError("private_original_stream_provider_scope_mismatch")
        private_stream_plan.update(private_providers)
    return {"schema_version":1,"status":STATUS,
        "original_selected_particle_material_texture_ref_slots":expected_local,
        "original_selected_typed_Texture2D28_targets":expected_distinct,
        **{k:stats[k] for k in (
            "original_selected_Texture2D28_material_bindings",
            "original_selected_Texture2D28_without_stream_field",
            "original_selected_Texture2D28_inline_or_unstreamed",
            "original_selected_Texture2D28_manifest_verified_streamed",
            "original_selected_Texture2D28_stream_payload_SHA_verified",
            "original_selected_Texture2D28_stream_provider_not_staged")},
        "original_selected_distinct_manifest_stream_providers":len(used_stream_names),
        "original_selected_Texture2D28_type_and_stream_metadata_verified":True,
        "full_original_Texture2D28_pixel_content_verified":False,
        "same_export_Texture2D28_GUID_or_Android_sampler_binding_verified":False,
        "raw_Shader_Texture_Material_IDs_names_stream_paths_disclosed":False}


def run(original:Path,manifest:Path, *, private_stream_plan:dict|None=None):
    import UnityPy
    private={}
    baseline=particle_material.run(original,manifest,private_local_texture_targets=private)
    if (baseline.get("status")!=particle_material.STATUS
        or baseline.get("six_original_scene_SHA_verified") is not True
        or baseline.get("four_original_shader_Material_owner_SHA_verified") is not True
        or baseline.get("original_particle_renderer_material_slot_references")!=108
        or baseline.get("original_particle_material_objects")!=5
        or baseline.get("original_particle_texenv_slots")!=10
        or baseline.get("original_particle_texenv_local_texture_pointers")!=10
        or baseline.get("original_particle_texenv_external_texture_pointers")!=0
        or baseline.get("original_particle_texenv_null_texture_slots")!=0
        or len(private)!=EXPECTED_DISTINCT_TEXTURE_TARGETS
        or sum(private.values())!=EXPECTED_LOCAL_TEXTURE_REFERENCES):
        raise ValueError("untrusted_original_particle_texture_source_baseline")
    grouped={}
    for owner,pid in private:
        if owner not in particle_material.source.MATERIAL_OWNERS or type(pid) is not int or pid<=0:
            raise ValueError("invalid_original_particle_local_Texture_target")
        grouped.setdefault(owner,set()).add(pid)
    found={}
    for owner,ids in grouped.items():
        path=original/"Raft_Data"/owner
        if path.is_symlink() or fingerprint(path)!=SHADER_OWNERS[owner]:
            raise ValueError("original_particle_texture_owner_SHA_drift")
        env=UnityPy.load(str(path))
        for obj in env.file.objects.values():
            if obj.path_id not in ids:continue
            key=(owner,obj.path_id)
            if key in found or obj.type.name!="Texture2D":
                raise ValueError("original_particle_local_pointer_not_unique_Texture2D")
            typetree=obj.read_typetree()
            # Deliberately avoid copying m_ImageData/raw pixel/source payloads.
            found[key]=("Texture2D",{
                k:typetree.get(k) for k in
                ("m_Width","m_Height","m_TextureFormat","m_CompleteImageSize","m_StreamData")
            })
    if set(found)!=set(private):
        raise ValueError("original_particle_local_Texture2D_missing_from_authenticated_owner")
    out=assess(private,found,manifest_stream_index(manifest),
               original/"Raft_Data",private_stream_plan=private_stream_plan)
    out["six_original_scene_SHA_verified"]=True
    out["four_original_material_shader_owner_SHA_verified"]=True
    out["source_108_particle_Shader48_Material21_and_Texture2D28_chain_verified"]=True
    return out


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for flag in ("original","manifest","out"):
        ap.add_argument("--"+flag,type=Path,required=True)
    ap.add_argument("--private-plan",type=Path)
    args=ap.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink()
        or args.out.resolve().is_relative_to(args.original.resolve())):
        raise ValueError("unsafe_original_particle_Texture2D_public_report_path")
    if args.private_plan is not None:
        plan_path=args.private_plan.absolute()
        if (plan_path.is_symlink() or plan_path.exists()
            or plan_path==args.out.absolute()
            or plan_path.resolve().is_relative_to(args.original.resolve())
            or any(x.is_symlink() for x in plan_path.parents)):
            raise ValueError("unsafe_source_private_stream_plan_path")
    try:
        private_plan={} if args.private_plan is not None else None
        result=run(args.original,args.manifest,private_stream_plan=private_plan)
        if private_plan is not None and result["status"]==STATUS:
            if (len(private_plan)!=1
                or sum(len(v["ranges"]) for v in private_plan.values())!=3):
                raise ValueError("unexpected_exact_original_particle_stream_provider")
            doc={"schema_version":1,"source_sha":ZIP2_SHA,
                 "source_scope":"T3_private_108_particle_original_Texture2D",
                 "providers":private_plan}
            args.private_plan.parent.mkdir(parents=True,exist_ok=True)
            with args.private_plan.open("x",encoding="utf-8") as out:
                json.dump(doc,out,sort_keys=True)
                out.write("\n")
            os.chmod(args.private_plan,0o600)
    except Exception as exc:
        result={"schema_version":1,"status":"INCONCLUSIVE",
                "failure_type":type(exc).__name__,
                "full_original_Texture2D28_pixel_content_verified":False,
                "same_export_Texture2D28_GUID_or_Android_sampler_binding_verified":False,
                "raw_Shader_Texture_Material_IDs_names_stream_paths_disclosed":False}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print("T3_ORIGINAL_PARTICLE108_TEXTURE2D28 "+json.dumps(result,sort_keys=True))
    return 0 if result["status"]==STATUS else 2


if __name__=="__main__":
    raise SystemExit(main())
