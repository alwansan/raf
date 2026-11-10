#!/usr/bin/env python3
"""GFX-MULTI-040: privacy-preserving audit of Android GLES diagnostic ZIP.

User ZIP remains local. Parse the latest GFX040 snapshot, auto-log counters
and optional 256x256 synthetic PNGs; publish ONLY bounded aggregate booleans
and counts. No individual GPU pixels, full device names, proprietary data,
stacks, timestamps, filenames or session tokens leave the private workspace.
"""
from __future__ import annotations

import argparse
import json
import struct
import zipfile
from collections import Counter
from pathlib import Path

EXPECTED_MODES=("Linear","Flat","NoPerspective")
EXPECTED_STATUSES=frozenset((
    "NOT_RUN",
    "GPU_READBACK_IN_PROGRESS",
    "INCONCLUSIVE_NOT_GLES3",
    "INCONCLUSIVE_UNSUPPORTED_OR_NO_COLORED_PIXELS",
    "DIAGNOSTIC_INTERPOLATION_PASS",
    "DIAGNOSTIC_INTERPOLATION_MISMATCH",
))
MAX_ARCHIVE_BYTES=256*1024*1024
MAX_ENTRY_BYTES=64*1024*1024
MAX_ENTRIES=10000
MAX_SNAPSHOT_BYTES=20*1024*1024
EXPECTED_PNG_SIZE=256
PNG_MAGIC=b"\x89PNG\r\n\x1a\n"


def safe_decode_json(raw,where,max_bytes=MAX_SNAPSHOT_BYTES):
    if not isinstance(raw,bytes) or len(raw)>max_bytes:
        raise ValueError("GFX040_"+where+"_SIZE_OR_TYPE_INVALID")
    try:
        return json.loads(raw.decode("utf-8","strict"))
    except (UnicodeError,ValueError):
        raise ValueError("GFX040_"+where+"_JSON_INVALID") from None


def validate_snapshot(source):
    if not isinstance(source,dict) or source.get("experiment")!="GFX-MULTI-040":
        raise ValueError("GFX040_SNAPSHOT_WRONG_EXPERIMENT")
    if (source.get("originalShaderRestored") is not False or
        source.get("originalRaftShaderBytecodeUsed") is not False or
        source.get("originalPcPixelParityVerified") is not False or
        source.get("sourceMaterialCbBindingsVerified") is not False):
        raise ValueError("GFX040_ORIGINAL_SHADER_FALSE_PROOF_FLAG_VIOLATION")
    status=source.get("diagnosticStatus")
    if status not in EXPECTED_STATUSES:
        raise ValueError("GFX040_UNKNOWN_PROBE_DIAGNOSTIC_STATUS")
    rows=source.get("results")
    if not isinstance(rows,list) or len(rows)!=3:
        raise ValueError("GFX040_EXPECTED_EXACTLY_THREE_RESULTS")
    by_name={}
    valid_samples=0
    for row in rows:
        if not isinstance(row,dict) or row.get("name") not in EXPECTED_MODES:
            raise ValueError("GFX040_INVALID_RESULT_MODE")
        mode=row["name"]
        if mode in by_name:
            raise ValueError("GFX040_DUPLICATE_RESULT_MODE")
        for k in ("shaderFound","shaderSupportedOnDevice",
                  "gpuReadbackCompleted","allSamplePositionsHaveColor"):
            if type(row.get(k)) is not bool:
                raise ValueError("GFX040_RESULT_BOOLEAN_MISSING")
        if row["gpuReadbackCompleted"] and not row["shaderSupportedOnDevice"]:
            raise ValueError("GFX040_GPU_READBACK_WITHOUT_SHADER_SUPPORT")
        sampled=row.get("sampledColors")
        if not isinstance(sampled,list) or len(sampled)!=3:
            raise ValueError("GFX040_EXPECTED_THREE_SAMPLE_POSITIONS")
        for color in sampled:
            if not isinstance(color,dict) or not all(
                isinstance(color.get(channel),(int,float)) and
                type(color[channel]) is not bool and
                -0.05<=color[channel]<=1.05
                for channel in ("r","g","b")):
                raise ValueError("GFX040_COLOR_SAMPLE_OUT_OF_BOUNDS")
        valid_samples+=int(row["gpuReadbackCompleted"])
        by_name[mode]=row
    if tuple(sorted(by_name))!=tuple(sorted(EXPECTED_MODES)):
        raise ValueError("GFX040_ORIGINAL_FREE_MODES_INCOMPLETE")
    reported_complete=source.get("allThreeGpuReadbacksComplete")
    if type(reported_complete) is not bool:
        raise ValueError("GFX040_READBACK_COMPLETION_FLAG_MISSING")
    genuine=all(x["gpuReadbackCompleted"] and
                x["allSamplePositionsHaveColor"] for x in rows)
    if reported_complete != genuine:
        raise ValueError("GFX040_READBACK_COMPLETION_FLAG_INCONSISTENT")
    if status=="DIAGNOSTIC_INTERPOLATION_PASS" and (
        not genuine or source.get("flatConstantAcrossInteriorSamples") is not True
        or source.get("perspectiveVsNoPerspectiveDistinguishable") is not True
        or source.get("isGles3") is not True):
        raise ValueError("GFX040_GPU_PASS_WITHOUT_REQUIRED_EVIDENCE")
    return {
        "synthetic_gpu_probe_status":status,
        "three_cases_present":len(by_name)==3,
        "device_reported_gles3":source.get("isGles3") is True,
        "cases_with_gpu_readback":valid_samples,
        "cases_with_supported_shaders":sum(x["shaderSupportedOnDevice"] for x in rows),
        "cases_with_colored_interior_samples":sum(x["allSamplePositionsHaveColor"] for x in rows),
        "all_three_gpu_readbacks_completed":reported_complete,
        "flat_color_stability_reported":source.get("flatConstantAcrossInteriorSamples") is True,
        "perspective_vs_no_perspective_difference_reported":
            source.get("perspectiveVsNoPerspectiveDistinguishable") is True,
        "original_shader48_restored":False,
        "original_gpu_pc_parity_verified":False,
    }


def png_synthetic_shape(data):
    if not isinstance(data,bytes) or len(data)<33 or len(data)>MAX_ENTRY_BYTES:
        return False
    if not data.startswith(PNG_MAGIC) or data[12:16]!=b"IHDR":
        return False
    width,height=struct.unpack_from(">II",data,16)
    return width==EXPECTED_PNG_SIZE and height==EXPECTED_PNG_SIZE


def audit_zip(path):
    with zipfile.ZipFile(path) as z:
        entries=z.infolist()
        if len(entries)>MAX_ENTRIES or sum(i.file_size for i in entries)>MAX_ARCHIVE_BYTES:
            raise ValueError("GFX040_LOG_ZIP_UNBOUNDED")
        if any(i.file_size>MAX_ENTRY_BYTES for i in entries):
            raise ValueError("GFX040_ZIP_ENTRY_TOO_LARGE")
        paths={i.filename for i in entries}
        if "README.txt" not in paths:
            raise ValueError("GFX040_EXPORT_ZIP_README_MISSING")
        snapshots=[p for p in paths if p.startswith("sessions/") and
                   p.endswith("/snapshots.jsonl")]
        if not snapshots:
            raise ValueError("GFX040_NO_SESSION_SNAPSHOTS")
        summaries=[p for p in paths if p.startswith("sessions/") and
                   p.endswith("/summary.json")]
        all_matching=[]
        for name in sorted(snapshots):
            content=z.read(name)
            if len(content)>MAX_SNAPSHOT_BYTES:
                raise ValueError("GFX040_SESSION_JSONL_TOO_LARGE")
            for line in content.splitlines():
                if not line.strip():
                    continue
                row=safe_decode_json(line,"ROW")
                if not isinstance(row,dict) or row.get("kind")!="state_snapshot":
                    raise ValueError("GFX040_UNKNOWN_SNAPSHOT_ROW")
                state=row.get("stateJson")
                if not isinstance(state,str) or len(state)>1000000:
                    raise ValueError("GFX040_STATE_TEXT_INVALID")
                try:
                    state_doc=json.loads(state)
                except ValueError:
                    raise ValueError("GFX040_INNER_STATE_JSON_INVALID") from None
                if isinstance(state_doc,dict) and state_doc.get("experiment")=="GFX-MULTI-040":
                    all_matching.append((name,state_doc))
        if not all_matching:
            raise ValueError("GFX040_NO_EXPERIMENT_GFX040_SNAPSHOTS")
        latest_snapshot_name,latest_state=all_matching[-1]
        verified=validate_snapshot(latest_state)
        session_root=latest_snapshot_name.rsplit("/",1)[0]+"/"
        expected_names=[
            session_root+"gpu-interpolation-"+mode.lower()+".png"
            for mode in EXPECTED_MODES
        ]
        existing=sum(int(name in paths and png_synthetic_shape(z.read(name)))
                     for name in expected_names)
        matches=0
        unity_errors=0
        dropped=0
        for name in summaries:
            if not name.startswith(session_root):
                continue
            doc=safe_decode_json(z.read(name),"SUMMARY")
            if not isinstance(doc,dict):
                raise ValueError("GFX040_SUMMARY_SHAPE_INVALID")
            if doc.get("originalShaderRestored") is not False:
                raise ValueError("GFX040_SUMMARY_ORIGINAL_SOURCE_STATUS_INVALID")
            unity_errors=doc.get("unityErrors",0)
            dropped=doc.get("messagesDropped",0)
            if type(unity_errors) is not int or unity_errors<0 or type(dropped) is not int or dropped<0:
                raise ValueError("GFX040_SUMMARY_LOG_COUNTERS_INVALID")
            matches+=1
        if matches!=1:
            raise ValueError("GFX040_SELECTED_SESSION_SUMMARY_MISSING_OR_DUPLICATE")
        return {
            "experiment":"GFX-MULTI-040",
            "schema":"gfxlab-gfx040-private-zip-safe-summary-v1",
            "sessions_with_snapshots":len(snapshots),
            "gfx040_state_snapshots_examined":len(all_matching),
            "synthetic_pngs_256x256_verified":existing,
            "test_logs_unity_errors":unity_errors,
            "test_logs_messages_dropped":dropped,
            "source_owner_data_text_published":False,
            **verified
        }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    summary=audit_zip(a.zip)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n")
    print("GFX_MULTI040_SAFE_OWNER_GPU_LOG_SUMMARY "+json.dumps(summary,sort_keys=True))


if __name__=="__main__":
    main()
