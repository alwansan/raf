#!/usr/bin/env python3
"""GFX-MULTI-041 owner ZIP audit: count-only 4-mode actual GPU readback proof.

All source ZIP bytes / frame screenshots / device identifiers / raw RGB
samples remain local. Never mistake a synthetic affine GPU PASS for Raft
Shader48 restoration or Windows-PC visual parity.
"""
from __future__ import annotations
import argparse
import json
import zipfile
from pathlib import Path
from gfxlab.tools.interpolation_owner_zip_audit import (
    safe_decode_json,png_synthetic_shape,MAX_ENTRIES,MAX_ARCHIVE_BYTES,
    MAX_ENTRY_BYTES,MAX_SNAPSHOT_BYTES,
)

MODES=("Linear","Flat","NoPerspective","AffineEmulated")
STATUSES={
    "NOT_RUN","GPU_READBACK_IN_PROGRESS","INCONCLUSIVE_NOT_GLES3",
    "INCONCLUSIVE_SHADER_OR_READBACK","DIAGNOSTIC_FLAT_MISMATCH",
    "DIAGNOSTIC_LINEAR_CPU_MISMATCH","DIAGNOSTIC_EMULATED_AFFINE_CPU_MISMATCH",
    "DIAGNOSTIC_REFERENCE_GEOMETRY_UNDISTINGUISHABLE",
    "DIAGNOSTIC_NATIVE_NOPERSPECTIVE_MATCHES_AFFINE",
    "DIAGNOSTIC_NATIVE_QUALIFIER_COLLAPSED_TO_SMOOTH",
    "DIAGNOSTIC_NATIVE_NOPERSPECTIVE_OTHER_RESULT",
}
REQUIRED_FALSE=(
    "originalShaderRestored","originalRaftShaderBytecodeUsed",
    "originalPcPixelParityVerified","sourceMaterialCbBindingsVerified",
)
MEAN_FIELDS=(
    "gpuLinearVsCpuPerspectiveError",
    "gpuAffineEmulatedVsCpuAffineError",
    "gpuNativeVsCpuAffineError","gpuNativeVsLinearError",
    "cpuExpectedPerspectiveAffineDifference",
)

def check_report(s):
    if not isinstance(s,dict) or s.get("experiment")!="GFX-MULTI-041":
        raise ValueError("GFX041_NOT_ORIGINAL_FREE_AFFINE_REFERENCE")
    if any(s.get(k) is not False for k in REQUIRED_FALSE):
        raise ValueError("GFX041_FALSE_AUTHENTIC_SHADER_CLAIM")
    if s.get("diagnosticStatus") not in STATUSES:
        raise ValueError("GFX041_STATUS_UNEXPECTED")
    rows=s.get("results")
    if not isinstance(rows,list) or len(rows)!=4 or {
        r.get("name") for r in rows if isinstance(r,dict)}!=set(MODES):
        raise ValueError("GFX041_EXACT_FOUR_MODES_REQUIRED")
    if any(type(s.get(k)) is not bool for k in (
        "allFourGpuReadbacksComplete","affineEmulatedMatchesCpu",
        "linearPerspectiveMatchesCpu","nativeNoPerspectiveMatchesAffine",
        "nativeNoPerspectiveMatchesSmooth",
        "flatConstantAcrossInteriorSamples","isGles3")):
        raise ValueError("GFX041_GUARD_BOOLEAN_FIELDS_INVALID")
    means={}
    for k in MEAN_FIELDS:
        v=s.get(k)
        if type(v) not in (int,float) or not 0<=v<=1:
            raise ValueError("GFX041_MEAN_ERROR_OUT_OF_BOUNDS")
        means[k]=round(v,6)
    counts={}
    for row in rows:
        if not isinstance(row,dict):
            raise ValueError("GFX041_MODE_RECORD_INVALID")
        for k in ("shaderFound","shaderSupportedOnDevice","gpuReadbackCompleted",
                  "allSamplePositionsHaveColor"):
            if type(row.get(k)) is not bool:
                raise ValueError("GFX041_MODE_BOOL_MISSING")
        if row["gpuReadbackCompleted"] and not row["shaderSupportedOnDevice"]:
            raise ValueError("GFX041_GPU_READBACK_WITHOUT_SHADER")
        if row["allSamplePositionsHaveColor"] and not row["gpuReadbackCompleted"]:
            raise ValueError("GFX041_COLORED_PIXELS_WITHOUT_GPU_READBACK")
        samples=row.get("sampledColors")
        if not isinstance(samples,list) or len(samples)!=3 or any(
            not isinstance(c,dict) or any(
                type(c.get(ch)) not in (int,float) or not -.05<=c[ch]<=1.05
                for ch in ("r","g","b")
            ) for c in samples):
            raise ValueError("GFX041_GPU_SAMPLE_SHAPE_INVALID")
        counts[row["name"]] = (
            row["shaderSupportedOnDevice"],row["gpuReadbackCompleted"],
            row["allSamplePositionsHaveColor"],
        )
    all_complete=all(r[1] and r[2] for r in counts.values())
    if all_complete!=s["allFourGpuReadbacksComplete"]:
        raise ValueError("GFX041_COMPLETION_FLAG_CONTRADICTION")
    st=s["diagnosticStatus"]
    if st.startswith("DIAGNOSTIC_NATIVE_") and not (
        all_complete and s["isGles3"] and
        s["linearPerspectiveMatchesCpu"] and s["affineEmulatedMatchesCpu"] and
        s["flatConstantAcrossInteriorSamples"]):
        raise ValueError("GFX041_NATIVE_CLASSIFICATION_WITHOUT_REFERENCE")
    if st=="DIAGNOSTIC_NATIVE_QUALIFIER_COLLAPSED_TO_SMOOTH" and (
        s["nativeNoPerspectiveMatchesSmooth"] is not True or
        s["nativeNoPerspectiveMatchesAffine"] is True):
        raise ValueError("GFX041_COLLAPSE_CLASSIFICATION_CONTRADICTS_METRICS")
    if st=="DIAGNOSTIC_NATIVE_NOPERSPECTIVE_MATCHES_AFFINE" and (
        s["nativeNoPerspectiveMatchesAffine"] is not True):
        raise ValueError("GFX041_NATIVE_MATCH_CLASSIFICATION_CONTRADICTS_METRICS")
    return {
        "experiment":"GFX-MULTI-041",
        "status":st,
        "source_only_synthetic_mode_count":len(counts),
        "device_is_gles3":s["isGles3"],
        "all_four_gpu_readbacks":all_complete,
        "supported_shader_modes":sum(r[0] for r in counts.values()),
        "colored_gpu_readback_modes":sum(r[1] and r[2] for r in counts.values()),
        "linear_perspective_matches_cpu":s["linearPerspectiveMatchesCpu"],
        "emulated_affine_matches_cpu":s["affineEmulatedMatchesCpu"],
        "native_noperspective_matches_affine":s["nativeNoPerspectiveMatchesAffine"],
        "native_noperspective_matches_linear":s["nativeNoPerspectiveMatchesSmooth"],
        "flat_constant_across_samples":s["flatConstantAcrossInteriorSamples"],
        "cpu_model_and_gpu_average_error_metrics":means,
        "source_original_shader48_restored":False,
        "pc_vs_adreno_original_pixel_parity":False,
    }

def audit_zip(path):
    with zipfile.ZipFile(path) as z:
        entries=z.infolist()
        if len(entries)>MAX_ENTRIES or sum(i.file_size for i in entries)>MAX_ARCHIVE_BYTES:
            raise ValueError("GFX041_ZIP_LIMITS")
        if any(i.file_size>MAX_ENTRY_BYTES for i in entries):
            raise ValueError("GFX041_ZIP_ENTRY_LIMIT")
        names={i.filename for i in entries}
        if "README.txt" not in names:
            raise ValueError("GFX041_ZIP_README_MISSING")
        snapshots=sorted(n for n in names if n.startswith("sessions/")
                         and n.endswith("/snapshots.jsonl"))
        matches=[]
        for name in snapshots:
            raw=z.read(name)
            if len(raw)>MAX_SNAPSHOT_BYTES:
                raise ValueError("GFX041_SESSION_JSONL_LIMIT")
            for line in raw.splitlines():
                if not line.strip():continue
                row=safe_decode_json(line,"OWNER_ZIP_ROW")
                if not isinstance(row,dict) or row.get("kind")!="state_snapshot":
                    raise ValueError("GFX041_SNAPSHOT_RECORD_INVALID")
                body=row.get("stateJson")
                if not isinstance(body,str) or len(body)>1000000:
                    raise ValueError("GFX041_STATE_NOT_VALID_JSON_TEXT")
                try:s=json.loads(body)
                except ValueError:raise ValueError("GFX041_STATE_JSON_MALFORMED") from None
                if isinstance(s,dict) and s.get("experiment")=="GFX-MULTI-041":
                    matches.append((name,s))
        if not matches:raise ValueError("GFX041_OWNER_GPU_SNAPSHOTS_ABSENT")
        name,latest=matches[-1]
        verified=check_report(latest)
        prefix=name.rsplit("/",1)[0]+"/"
        pngs=sum(int((prefix+"gpu-interpolation-"+mode.lower()+".png") in names and
             png_synthetic_shape(z.read(prefix+"gpu-interpolation-"+mode.lower()+".png")))
             for mode in MODES)
        summary=prefix+"summary.json"
        if summary not in names:
            raise ValueError("GFX041_OWNER_SESSION_SUMMARY_MISSING")
        counters=safe_decode_json(z.read(summary),"OWNER_SESSION_SUMMARY")
        if counters.get("originalShaderRestored") is not False:
            raise ValueError("GFX041_SOURCE_FALSE_CLAIM_IN_SESSION")
        errors=counters.get("unityErrors",0)
        warnings=counters.get("unityWarnings",0)
        dropped=counters.get("messagesDropped",0)
        if any(type(x) is not int or x<0 for x in (errors,warnings,dropped)):
            raise ValueError("GFX041_SESSION_ERROR_COUNTER_MALFORMED")
        return {
            **verified,
            "session_count":len(snapshots),
            "matching_gfx041_snapshots":len(matches),
            "synthetic_gpu_256x256_png_count":pngs,
            "unity_errors":errors,
            "unity_warnings":warnings,
            "messages_dropped":dropped,
            "source_owner_images_logs_device_identifiers_exported":False,
        }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--zip",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    a=p.parse_args()
    data=audit_zip(a.zip)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
    print("GFX_MULTI041_SAFE_OWNER_ZIP "+json.dumps(data,sort_keys=True))

if __name__=="__main__":main()
