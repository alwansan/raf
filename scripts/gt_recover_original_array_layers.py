#!/usr/bin/env python3
"""GT recovery of the ORIGINAL nine Texture2DArray streamed GPU payloads.

From SHA256-authenticated ZIP2 game originals, preserve the original
Texture2DArray shape/format/mip metadata and copy exact private m_StreamData
ranges into a transient staging directory for eventual Unity Editor import.
Original compressed GPU bytes are NEVER committed, uploaded, or considered
Android-ready without a real compatible format/array-slice decoder and import
proof. GUIDs are private and derived only from same-instance AssetRipper trace.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil

from scripts.gt_verify_original_array_export import (
    COUNT_EXPECTED, exported_meta, match, source_arrays,
)
from scripts.gt_zip2_payloads import fingerprint, manifest, safe, SourceFailure
from scripts.gt_bc3_array_layout import original_layout_report

CHUNK=1024*1024
MAX_ARRAY_STREAM_BYTES=512*1024*1024


def safe_stream_basename(raw) -> str:
    if not isinstance(raw,str) or not raw or "\x00" in raw:
        raise SourceFailure("invalid_original_array_stream_name")
    text=raw.replace("\\","/")
    tokens=text.split("/")
    if any(x in ("..",".") for x in tokens):
        raise SourceFailure("unsafe_original_array_stream_path")
    name=PurePosixPath(text).name
    if (not name or name in (".","..") or
        not name.endswith((".resS",".resource"))):
        raise SourceFailure("unexpected_original_array_stream_suffix")
    return name


def exact_streams(source_root:Path, files:dict, arrays:dict,
                  *, budget=MAX_ARRAY_STREAM_BYTES) ->list[dict]:
    """Plan only m_StreamData byte ranges within independently SHA-pinned streams."""
    if not source_root.is_dir() or source_root.is_symlink():
        raise SourceFailure("untrusted_original_source_root")
    if type(budget) is not int or not 0<budget<=MAX_ARRAY_STREAM_BYTES:
        raise SourceFailure("invalid_array_copy_budget")
    if len(arrays)!=COUNT_EXPECTED:
        raise SourceFailure("original_array_scope_count_drift")
    planned=[]
    verified=set()
    total=0
    # Source has 52 logical layers, but the authentic original has one
    # zero-stream two-layer array: refuse to invent two color/image layers.
    original_layout_report(arrays)
    for identity,meta in sorted(arrays.items()):
        if not isinstance(meta,dict):
            raise SourceFailure("malformed_original_array_metadata")
        size=meta.get("original_stream_size")
        offset=meta.get("private_stream_offset")
        fmt=meta.get("source_format_enum")
        mips=meta.get("source_mipmap_count")
        if (type(size) is not int or size<0 or
            type(fmt) is not int or fmt not in (100,101) or
            type(mips) is not int or mips<=0):
            raise SourceFailure("array_source_format_or_mips_missing")
        if size==0:
            if meta.get("has_image_data") or not meta.get("has_stream_record"):
                raise SourceFailure("zero_stream_array_has_unverified_inline_payload")
            planned.append(dict(identity=identity,provider=None,offset=None,
                            source_format_enum=fmt,mip_count=mips,
                            width=meta["width"],height=meta["height"],
                            depth=meta["depth"],byte_length=0))
            continue
        if type(offset) is not int or offset<0:
            raise SourceFailure("invalid_original_array_stream_extent")
        path=safe_stream_basename(meta.get("private_stream_path"))
        key="Raft_Data/"+path
        if key not in files or files[key][0] not in ("plain","split"):
            raise SourceFailure("unlisted_original_array_stream_provider")
        target=source_root/path
        safe(target)
        if not target.is_file():
            raise SourceFailure("missing_original_array_stream_provider")
        expected_size,expected_sha=files[key][1:]
        if offset+size>expected_size:
            raise SourceFailure("array_stream_extent_outside_authenticated_provider")
        if key not in verified:
            if fingerprint(target)!=(expected_size,expected_sha):
                raise SourceFailure("original_array_stream_sha256_mismatch")
            verified.add(key)
        total+=size
        if total>budget:
            raise SourceFailure("original_array_copy_budget_exceeded")
        planned.append(dict(identity=identity,provider=target,offset=offset,
                            source_format_enum=fmt,mip_count=mips,
                            width=meta["width"],height=meta["height"],
                            depth=meta["depth"],byte_length=size))
    return planned


def recover(source_root:Path,original:dict,trace:dict,meta:dict,
            expected_files:dict,private_output:Path) ->dict:
    """Actually copy exact original compressed array payloads to private stage."""
    source_root,private_output=source_root.absolute(),private_output.absolute()
    safe(source_root)
    safe(private_output)
    if (private_output.exists() or private_output.is_relative_to(source_root)
        or source_root.is_relative_to(private_output)):
        raise SourceFailure("private_array_output_overlaps_source_or_exists")
    # Verify every original Array object has an exact same-instance exported
    # Unity pointer; do not fix/collapse unknown exported object identities.
    provenance=match(original,trace,meta)
    planned=exact_streams(source_root,expected_files,original)
    identities={}
    for row in trace["objects"]:
        if row.get("class_id")!=187:
            continue
        source=row.get("source",{})
        name=Path(str(source.get("owner","")).replace("\\","/")).name
        original_identity=(name,source.get("path_id"))
        if original_identity in original:
            if original_identity in identities:
                raise SourceFailure("duplicate_original_array_trace")
            identities[original_identity]=row["export"]
    if len(identities)!=COUNT_EXPECTED:
        raise SourceFailure("untraced_original_array_payload")
    private_output.mkdir(parents=True,exist_ok=False)
    stage=[]
    total=0
    try:
        for i,row in enumerate(planned):
            source_has_pixels=row["byte_length"]>0
            name=f"array-{i:02d}.original-gpu-bytes" if source_has_pixels else None
            checksum=None
            if source_has_pixels:
                output=private_output/name
                sha=hashlib.sha256()
                remaining=row["byte_length"]
                with row["provider"].open("rb") as src,output.open("xb") as dst:
                    src.seek(row["offset"])
                    while remaining:
                        chunk=src.read(min(CHUNK,remaining))
                        if not chunk:
                            raise SourceFailure("original_array_stream_truncated_during_copy")
                        sha.update(chunk)
                        dst.write(chunk)
                        remaining-=len(chunk)
                if output.stat().st_size!=row["byte_length"]:
                    raise SourceFailure("original_array_stream_length_mismatch")
                checksum=sha.hexdigest()
                total+=row["byte_length"]
            export=identities[row["identity"]]
            stage.append({
                "relative_payload":name,"sha256":checksum,
                "payload_bytes":row["byte_length"],
                "original_payload_state":(
                    "ORIGINAL_COMPRESSED_BC3_STREAM" if source_has_pixels
                    else "NO_ORIGINAL_STREAMED_OR_INLINE_PIXELS"),
                "target_export_guid":export["guid"],
                "target_fileID":export["file_id"],
                "target_export_type":export["type"],
                "source_format_enum":row["source_format_enum"],
                "mipmap_count":row["mip_count"],
                "width":row["width"],"height":row["height"],
                "depth":row["depth"],
            })
        if len(stage)!=COUNT_EXPECTED:
            raise SourceFailure("partial_original_array_payload_recovery")
        (private_output/"private-array-import-manifest.json").write_text(
            json.dumps({"schema":"GT_PRIVATE_ORIGINAL_ARRAY_IMPORT_INPUT_V1",
              "arrays":stage},sort_keys=True,indent=2)+"\n")
    except BaseException:
        shutil.rmtree(private_output)
        raise
    counts=Counter(row["source_format_enum"] for row in planned)
    layout=original_layout_report(original)
    return {
        "schema":"GT_REAL_NINE_ORIGINAL_ARRAY_PAYLOAD_RECOVERY_V1",
        "status":"ORIGINAL_COMPRESSED_ARRAY_PAYLOADS_STAGED_FOR_REENCODE",
        "original_source_array_objects_verified":COUNT_EXPECTED,
        "source_total_layer_count":sum(row["depth"] for row in planned),
        "source_array_layers_with_original_streamed_pixels":layout["source_layers_with_original_stream_bytes"],
        "source_array_layers_without_original_pixels":layout["source_layers_without_original_stream_bytes"],
        "sha256_authenticated_streamed_payloads_copied":sum(row["byte_length"]>0 for row in planned),
        "original_array_objects_with_zero_source_payload":sum(row["byte_length"]==0 for row in planned),
        "original_source_streamed_bytes_restored_to_private_stage":total,
        "original_array_format_enum_histogram":dict(sorted(
            (str(k),v) for k,v in counts.items())),
        "original_export_GUIDs_same_instance_matched":provenance["array_real_export_source_GUIDs_exact_join"],
        "original_game_bytes_or_exporter_GUIDs_published":False,
        "Unity_Editor_Texture2DArray_assets_created":False,
        "Unity_Android_texture_array_import_or_GPU_render_verified":False,
        "git_lfs_used":False,
    }


def main()->int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--zip2-checkout",type=Path,required=True)
    ap.add_argument("--trace",type=Path,required=True)
    ap.add_argument("--project",type=Path,required=True)
    ap.add_argument("--private-output",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    args=ap.parse_args()
    if (args.report.absolute().is_relative_to(args.source.absolute())
        or args.report.absolute().is_relative_to(args.project.absolute())
        or args.report.absolute().is_relative_to(args.private_output.absolute())):
        raise SourceFailure("original_array_public_report_overlaps_private_data")
    from scripts.gt_verify_original_array_export import source_arrays,exported_meta
    owner_manifest=args.zip2_checkout/"RAFT_FILE_MANIFEST.tsv"
    arrays=source_arrays(args.source,owner_manifest)
    checked_manifest=manifest(args.zip2_checkout)
    trace=json.loads(args.trace.read_text(encoding="utf-8"))
    report=recover(args.source,arrays,trace,exported_meta(args.project),
                  checked_manifest,args.private_output)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print("GT_REAL_SOURCE_ARRAY_STREAM_PAYLOAD_RECOVERY "+json.dumps(report,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
