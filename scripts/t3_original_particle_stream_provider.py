#!/usr/bin/env python3
"""SHA-verify the ONE ZIP2 source .resS provider for three original particle textures.

Consumes a PRIVATE runner-local source plan generated from the authentic
six-scene/four-owner ParticleShader48→5 Material21→3 Texture2D28 graph.
Sparse checkout only the private source provider from immutable ZIP2, restore
it with the exact manifest SHA and read 3 bounded streaming payload spans.
Never publish resource names, ranges, image bytes, source hashes or GUIDs.
No AssetRipper Unity export or Android APK/OBB matching occurs here.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

from scripts.t3_stream_extent_guard import validate_extents
from scripts.w1_stage_zip2_owners import ZIP2_SHA, fingerprint, safe, stage

STATUS="ZIP2_SHA_ORIGINAL_PARTICLE108_THREE_IMAGE_STREAM_RANGES_READ"
MAX_SOURCE_PROVIDER_BYTES=2_000_000_000
MAX_PRIVATE_PLAN_BYTES=4096
REL_COLUMNS=("kind","bytes","sha256","mode","relative_path_under_Raft")


def plan_contract(plan:dict, manifest:Path):
    """Validate a private source-scope plan against the immutable manifest."""
    if (type(plan) is not dict or set(plan)!={"schema_version","source_sha",
        "source_scope","providers"} or type(plan["schema_version"]) is not int
        or plan["schema_version"]!=1
        or plan["source_sha"]!=ZIP2_SHA
        or plan["source_scope"]!="T3_private_108_particle_original_Texture2D"
        or type(plan["providers"]) is not dict or len(plan["providers"])!=1):
        raise ValueError("untrusted_private_particle_source_stream_plan")
    name, info=next(iter(plan["providers"].items()))
    if (type(name) is not str or len(name)>128
        or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._ -]*\.(?:resS|resource)",name)
        or ".." in name or type(info) is not dict
        or set(info)!={"bytes","sha256","ranges"}):
        raise ValueError("invalid_private_particle_stream_provider_identity")
    size,digest,ranges=info["bytes"],info["sha256"],info["ranges"]
    if (type(size) is not int or not 0<size<=MAX_SOURCE_PROVIDER_BYTES
        or type(digest) is not str or not re.fullmatch(r"[0-9a-f]{64}",digest)
        or type(ranges) is not list or len(ranges)!=3):
        raise ValueError("invalid_private_particle_stream_provider_pin")
    if (manifest.is_symlink() or not manifest.is_file()
        or manifest.stat().st_size>1024*1024):
        raise ValueError("untrusted_ZIP2_manifest_file")
    with manifest.open("r",encoding="utf-8-sig",newline="") as file:
        rows=list(csv.DictReader(file,delimiter="\t"))
    selected=[row for row in rows
              if row.get("relative_path_under_Raft")=="Raft_Data/"+name]
    if (len(selected)!=1 or tuple(rows[0].keys())!=REL_COLUMNS
        or selected[0].get("kind") not in ("plain","split")
        or selected[0].get("bytes")!=str(size)
        or selected[0].get("sha256")!=digest):
        raise ValueError("original_particle_stream_manifest_pin_mismatch")
    stats=validate_extents({name:size},
                           [(name,offset,length) for offset,length in ranges])
    if stats["extents"]!=3 or stats["providers"]!=1:
        raise ValueError("invalid_original_particle_selected_stream_span_scope")
    return {"name":name,"pin":(size,digest),"kind":selected[0]["kind"],
            "ranges":[(start,length) for start,length in ranges],
            "extents":stats}


def range_fingerprints(path:Path, ranges:list, *, expected_size:int):
    """Read source bytes from SHA-authenticated parent; never return digests."""
    if path.is_symlink() or not path.is_file() or path.stat().st_size!=expected_size:
        raise ValueError("unauthenticated_original_particle_source_stream_bytes")
    digest_set=set()
    count=total=nonzero=0
    with path.open("rb") as stream:
        for start,length in ranges:
            if (type(start) is not int or type(length) is not int
                or start<0 or length<=0 or start>expected_size
                or length>expected_size-start):
                raise ValueError("invalid_source_stream_range_requested")
            stream.seek(start)
            digest=hashlib.sha256()
            remaining=length
            any_nonzero=False
            while remaining:
                chunk=stream.read(min(1024*1024,remaining))
                if not chunk:
                    raise ValueError("short_original_particle_stream_range")
                digest.update(chunk)
                any_nonzero|=any(chunk)
                remaining-=len(chunk)
            digest_set.add(digest.digest())  # private only, never JSON.
            count+=1
            total+=length
            nonzero+=int(any_nonzero)
    return {"read_count":count,"read_bytes":total,
            "distinct_source_range_fingerprints":len(digest_set),
            "nonzero_source_image_ranges":nonzero}


def verify_and_stage(private_plan:Path, zip2:Path, original:Path):
    for path in (private_plan,zip2,original,zip2/"RAFT_FILE_MANIFEST.tsv"):
        safe(path)
    if (not private_plan.is_file()
        or private_plan.stat().st_size>MAX_PRIVATE_PLAN_BYTES
        or not zip2.is_dir() or not original.is_dir()
        or zip2.is_relative_to(original)
        or original.is_relative_to(zip2)):
        raise ValueError("unsafe_ZIP2_particle_source_stream_staging")
    if subprocess.check_output(
        ["git","-C",str(zip2),"rev-parse","HEAD"],
        stderr=subprocess.DEVNULL,text=True).strip()!=ZIP2_SHA:
        raise ValueError("wrong_ZIP2_particle_source_checkout_commit")
    plan=json.loads(private_plan.read_text("utf-8"))
    info=plan_contract(plan,zip2/"RAFT_FILE_MANIFEST.tsv")
    need_bytes=info["pin"][0]
    # Sparse checkout can temporarily require roughly one Git working copy,
    # one reconstructed file and a separate temporary file, plus headroom.
    if shutil.disk_usage(zip2).free < 3*need_bytes+1024**3:
        raise ValueError("insufficient_disk_budget_for_exact_stream_provider")
    relative="Raft_Data/"+info["name"]
    selector="/Raft/"+relative+("/*" if info["kind"]=="split" else "")
    # No shell/echo; source provider name is private and drawn from a
    # SHA-pinned manifest with strict basename validation.
    subprocess.run(["git","-C",str(zip2),"sparse-checkout","set","--no-cone",
                    "--","/RAFT_FILE_MANIFEST.tsv",selector],
                   stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                   check=True,timeout=900)
    provider=original/relative
    staged=stage(zip2,original,{relative:info["pin"]})
    if (len(staged["owners"])!=1
        or staged["verified_bytes"]!=need_bytes
        or staged["lfs_used"] is not False
        or fingerprint(provider)!=info["pin"]):
        raise ValueError("original_stream_provider_sha_staging_unproven")
    checks=range_fingerprints(provider,info["ranges"],expected_size=need_bytes)
    if checks["read_count"]!=3:
        raise ValueError("source_stream_range_read_count_changed")
    return {"schema_version":1,"status":STATUS,
        "immutable_original_ZIP2_commit_verified":True,
        "selected_private_stream_providers":1,
        "selected_external_stream_provider_size_and_SHA256_verified":True,
        "selected_original_Texture2D28_stream_ranges_read":checks["read_count"],
        "selected_original_stream_range_total_bytes_read":checks["read_bytes"],
        "selected_original_stream_ranges_containing_nonzero_bytes":checks["nonzero_source_image_ranges"],
        "selected_original_distinct_range_fingerprints_no_digests":checks["distinct_source_range_fingerprints"],
        "source_stream_metadata_exact_duplicate_ranges":info["extents"]["duplicate_ranges"],
        "source_stream_metadata_partial_overlaps":info["extents"]["partial_overlaps"],
        "source_original_stream_payload_unstaged_after_this_step":False,
        "source_Texture2D_pixels_successfully_decoded":False,
        "same_instance_exported_texture_guid_or_Android_pixels_verified":False,
        "original_raw_resource_paths_hashes_bytes_or_IDs_published":False}


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name in ("private-plan","zip2","original","out"):
        ap.add_argument("--"+name,type=Path,required=True)
    args=ap.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink()
        or args.out.resolve().is_relative_to(args.original.resolve())
        or args.out.resolve().is_relative_to(args.zip2.resolve())):
        raise ValueError("unsafe_private_stream_output_location")
    try:
        safe_result=verify_and_stage(args.private_plan,args.zip2,args.original)
    except Exception as exc:
        safe_result={"schema_version":1,"status":"INCONCLUSIVE",
            "failure_type":type(exc).__name__,
            "same_instance_exported_texture_guid_or_Android_pixels_verified":False,
            "original_raw_resource_paths_hashes_bytes_or_IDs_published":False}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(safe_result,sort_keys=True,indent=2)+"\n")
    print("T3_PARTICLE_108_STREAM_PROVIDER_SOURCE "+json.dumps(safe_result,sort_keys=True))
    return 0 if safe_result["status"]==STATUS else 2


if __name__=="__main__":
    raise SystemExit(main())
