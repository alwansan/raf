#!/usr/bin/env python3
"""T3: prove original 106 selected Material-linked Texture2D stream dependencies.

Stage only SHA-pinned serialized original Material/Texture owner files. Read
m_StreamData, validate exact referenced provider file name/size against the
immutable ZIP2 manifest, and report whether each original resource payload
was actually staged for the bounded AssetRipper experiment. NO .resS pixels,
original object IDs or raw source values enter the report or repository.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path, PurePosixPath

from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.b05_verify_material_texenv_bindings import original_texenvs
from scripts.b03_original_renderer_materials import manifest_provider_basename_counts
from scripts.t3_linked_texture_sampler_export import source_targets, OWNER
from scripts.w1_stage_zip2_owners import fingerprint

EXPECTED_DISTINCT = 106
PINS = {name:SHADER_OWNERS[name] for name in (
    "sharedassets6.assets", "sharedassets0.assets", "sharedassets1.assets")}
COLUMNS = ("kind","bytes","sha256","mode","relative_path_under_Raft")


def manifest_stream_index(path:Path):
    if path.is_symlink() or not path.is_file() or path.stat().st_size>1024*1024:
        raise ValueError("unsafe_or_oversize_original_ZIP2_manifest")
    with path.open("r",encoding="utf-8-sig",newline="") as f:
        reader=csv.DictReader(f,delimiter="\t")
        if tuple(reader.fieldnames or ())!=COLUMNS:
            raise ValueError("unexpected_original_manifest_columns")
        rows=list(reader)
    source={}
    for row in rows:
        rel=row["relative_path_under_Raft"]
        if not isinstance(rel,str) or not rel.startswith("Raft_Data/") or "\\" in rel:
            continue
        if not rel.endswith((".resS",".resource")):
            continue
        parts=PurePosixPath(rel).parts
        if any(p in ("",".","..") for p in parts):
            raise ValueError("unsafe_original_stream_provider_manifest_path")
        name=parts[-1]
        if name in source:
            raise ValueError("ambiguous_stream_provider_basename")
        try:
            size=int(row["bytes"])
        except (TypeError,ValueError):
            raise ValueError("invalid_original_stream_manifest_bytes") from None
        if size<=0 or not isinstance(row["sha256"],str) or len(row["sha256"])!=64:
            raise ValueError("invalid_stream_manifest_pin")
        source[name]=(size,row["sha256"])
    if not source:
        raise ValueError("no_original_streaming_provider_inventory")
    return source


def evaluate(records:dict, providers:dict, staged:Path, expected=EXPECTED_DISTINCT):
    """Count typed original source stream offsets; no proprietary paths in output."""
    if not isinstance(records,dict) or len(records)!=expected:
        raise ValueError("missing_authenticated_original_Texture2D_population")
    if not isinstance(providers,dict):
        raise ValueError("invalid_original_stream_manifest_inventory")
    counts=Counter()
    names=Counter()
    maxends={}
    for key, value in records.items():
        if not isinstance(key,tuple) or len(key)!=2 or key[0] not in PINS:
            raise ValueError("unexpected_Texture2D_original_owner")
        if not isinstance(value,dict):
            raise ValueError("original_Texture2D_typetree_not_mapping")
        stream=value.get("m_StreamData")
        if stream is None:
            counts["no_original_StreamData_field"]+=1
            continue
        if not isinstance(stream,dict) or not {"path","offset","size"} <= set(stream):
            counts["unrecognized_original_StreamData_schema"]+=1
            continue
        path,offset,size=stream["path"],stream["offset"],stream["size"]
        if (not isinstance(path,str) or type(offset) is not int or offset<0
                or type(size) is not int or size<0):
            counts["invalid_original_StreamData_values"]+=1
            continue
        if not size or not path:
            if size or (not size and path):
                counts["original_partial_StreamData"]+=1
            else:
                counts["original_inline_or_unstreamed_texture"]+=1
            continue
        counts["original_external_streamed_Texture2D"]+=1
        raw=path.replace("\\","/")
        name=PurePosixPath(raw).name
        if (not name or name in (".","..") or
            not name.endswith((".resS",".resource"))):
            counts["unknown_stream_path_category"]+=1
            continue
        if name not in providers:
            counts["original_stream_provider_not_in_manifest"]+=1
            continue
        extent=offset+size
        if extent>providers[name][0]:
            counts["original_StreamData_extent_beyond_manifest_provider"]+=1
            continue
        names[name]+=1
        maxends[name]=max(extent,maxends.get(name,0))
        candidate=staged/name
        if candidate.is_symlink():
            counts["linked_staged_original_stream_provider_refused"]+=1
        elif candidate.is_file():
            counts["staged_original_stream_provider_present_unhashed"]+=1
        else:
            counts["required_original_stream_provider_not_staged"]+=1

    actual_good=sum(names.values())
    return {
        "schema_version":1,
        "experiment":"T3-original-106-source-linked-Texture2D-stream-dependencies",
        "selected_original_linked_Texture2D_objects":len(records),
        "authentic_original_owner_count":len({key[0] for key in records}),
        "source_stream_classes":dict(sorted(counts.items())),
        "required_streaming_provider_names":dict(sorted(names.items())),
        "required_streaming_provider_count":len(names),
        "original_stream_extents_by_provider_end_bytes":dict(sorted(maxends.items())),
        "original_manifest_declared_stream_objects_verified":actual_good,
        "full_original_stream_payloads_in_bounded_export_verified":False,
        "source_original_SHA_validated":True,
        "texture_pixels_or_game_device_verified":False,
        "status":"ORIGINAL_SOURCE_STREAM_DEPENDENCIES_BOUNDED_NOT_RUNTIME_PARITY",
    }


def probe(root:Path, manifest:Path):
    import UnityPy
    if root.is_symlink() or any(p.is_symlink() for p in (root,root/"Raft_Data",manifest)):
        raise ValueError("unsafe_original_source_parent")
    owners=root/"Raft_Data"
    for name,pin in PINS.items():
        file=owners/name
        if file.is_symlink() or not file.is_file() or fingerprint(file)!=pin:
            raise ValueError("original_linked_Texture2D_owner_SHA_mismatch")
    materials=original_texenvs(root,owner_names={OWNER})
    source=UnityPy.load(str(owners/OWNER))
    ext=[x.path for x in source.file.externals]
    selected,scoped=source_targets(materials,ext,manifest_provider_basename_counts(manifest))
    if len(selected)!=EXPECTED_DISTINCT:
        raise ValueError("linked_texture_source_population_not_106")
    records={}
    for name in PINS:
        env=UnityPy.load(str(owners/name))
        targets={pid for provider,pid in selected if provider==name}
        for obj in env.file.objects.values():
            if obj.path_id not in targets: continue
            if obj.type.name!="Texture2D" or (name,obj.path_id) in records:
                raise ValueError("selected_original_object_not_unique_Texture2D")
            records[(name,obj.path_id)]=obj.read_typetree()
    if set(records)!=selected:
        raise ValueError("original_selected_Texture2D_missing_from_pinned_sources")
    return evaluate(records,manifest_stream_index(manifest),owners)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--original",type=Path,required=True)
    p.add_argument("--manifest",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args(argv)
    if a.out.exists() or a.out.is_symlink() or a.out.resolve().is_relative_to(a.original.resolve()):
        raise ValueError("original_raw_source_report_destination_refused")
    stage="authentic_selected_original_Texture2D_StreamData"
    try:
        r=probe(a.original,a.manifest)
    except Exception as err:
        r={"schema_version":1,"experiment":"T3-original-106-source-linked-Texture2D-stream-dependencies",
           "status":"INCONCLUSIVE","phase":stage,"exception_type":type(err).__name__,
           "texture_pixels_or_game_device_verified":False}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf8")
    print("T3_AUTHENTIC_TEXTURE_STREAM_DEPENDENCIES "+json.dumps(r,sort_keys=True))
    return 0 if r["status"]=="ORIGINAL_SOURCE_STREAM_DEPENDENCIES_BOUNDED_NOT_RUNTIME_PARITY" else 2


if __name__=="__main__": raise SystemExit(main())
