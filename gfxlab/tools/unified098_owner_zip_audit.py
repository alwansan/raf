#!/usr/bin/env python3
"""GFX100: safe fail-closed inspection of GFX098 owner outer backup ZIP.
Never extracts private original model images, caches, events or Unity binaries.
Emits aggregate JSON only. Standard library only.
"""
import argparse
import collections
import hashlib
import io
import json
import re
import sys
import zipfile

PREFIX = "com.alwansan.raft.graphicslab.unified098/files/gfxlab/sessions/"
CASE = re.compile(r"(M0[0-5])_mode([34])_[^/]+\.json$")
GPU = ("linear", "flat", "noperspective", "affineemulated")

def check_zip(z):
    entries = z.infolist()
    if len(entries) > 2000 or sum(e.file_size for e in entries) > 300_000_000:
        raise ValueError("ZIP_CONTENTS_BOUNDS")
    for entry in entries:
        if entry.filename.startswith("/") or ".." in entry.filename.split("/") or "\\" in entry.filename:
            raise ValueError("ZIP_UNSAFE_PATH")
    if z.testzip() is not None:
        raise ValueError("ZIP_CRC_ERROR")

def analyze(path):
    with open(path, "rb") as stream:
        archive_sha = hashlib.file_digest(stream, "sha256").hexdigest()
    with zipfile.ZipFile(path) as z:
        check_zip(z)
        names = set(z.namelist())
        sessions = sorted({n[len(PREFIX):].split("/")[0] for n in names
                           if n.startswith(PREFIX) and "/" in n[len(PREFIX):]})
        if not sessions:
            raise ValueError("NO_GFX098_SESSIONS")
        counts = collections.Counter()
        cases = collections.defaultdict(set)
        gpu_spreads = collections.defaultdict(set)
        gpu_hashes = {}
        gpu_statuses = collections.Counter()
        for session in sessions:
            base = PREFIX + session + "/"
            meta = json.loads(z.read(base + "summary.json"))
            if (meta.get("session") != session
                    or meta.get("originalShaderRestored") is not False
                    or meta.get("devicePixelParityVerified") is not False):
                raise ValueError("SOURCE_SHADER_FALSE_PROOF_OR_SESSION_ID")
            events = z.read(base + "events.jsonl").decode().splitlines()
            snapshots = z.read(base + "snapshots.jsonl").decode().splitlines()
            if (len(events) != meta["eventsWritten"]
                    or len(snapshots) != meta["snapshotsWritten"]):
                raise ValueError("SESSION_COUNTS_MISMATCH")
            counts.update(events=len(events), snapshots=len(snapshots),
                          unity_errors=meta["unityErrors"],
                          unity_warnings=meta["unityWarnings"],
                          dropped=meta["messagesDropped"])
            for line in events:
                row = json.loads(line)
                msg = row.get("message", "")
                if "MODEL_MATRIX098_COMPLETED" in msg:
                    if "captures=12 expected=12 failure=" not in msg:
                        raise ValueError("MODEL_MATRIX_INCOMPLETE")
                    counts["matrix_complete"] += 1
                if "GFX041_DIAGNOSTIC_READBACK" in msg:
                    match = re.search(r"mode=(\w+) all_samples_foreground=(\w+) spread=([0-9.]+)", msg)
                    if not match or match[2] != "True":
                        raise ValueError("INVALID_GPU_READBACK")
                    gpu_spreads[match[1]].add(float(match[3]))
                    counts["gpu_readbacks"] += 1
                if "GFX041_SYNTHETIC_GPU_DIAGNOSTIC" in msg:
                    match = re.search(r"status=(\w+)", msg)
                    if match:
                        gpu_statuses[match[1]] += 1
            for name in names:
                if not name.startswith(base + "model-matrix098/") or not name.endswith(".json"):
                    continue
                match = CASE.fullmatch(name.rsplit("/",1)[-1])
                if match is None:
                    raise ValueError("UNEXPECTED_CAPTURE_NAME")
                item = json.loads(z.read(name))
                if item["model"] != match[1] or item["materialMode"] != int(match[2]):
                    raise ValueError("CAPTURE_METADATA_MISMATCH")
                png_name = item["pngFile"]
                if "/" in png_name or "\\" in png_name:
                    raise ValueError("CAPTURE_UNSAFE_PATH")
                png_path = name.rsplit("/",1)[0] + "/" + png_name
                raw = z.read(png_path)
                if (not raw.startswith(b"\x89PNG\r\n\x1a\n")
                        or hashlib.sha256(raw).hexdigest() != item["pngSha256"]):
                    raise ValueError("CAPTURE_IMAGE_SHA_MISMATCH")
                cases[(match[1],match[2])].add(item["pngSha256"])
                counts["capture_count"] += 1
                counts["mode" + match[2]] += 1
            for mode in GPU:
                name = base + "gpu-interpolation-" + mode + ".png"
                if name in names:
                    gpu_hashes[mode] = hashlib.sha256(z.read(name)).hexdigest()
        if set(cases) != {(f"M{m:02d}", mode) for m in range(6) for mode in ("3","4")}:
            raise ValueError("MODEL_MODE_COVERAGE")
        if any(len(hashes) != 1 for hashes in cases.values()):
            raise ValueError("NONDETERMINISTIC_REPEATED_CAPTURE")
        exports = 0
        for name in names:
            if "/" not in name and name.endswith(".zip"):
                with zipfile.ZipFile(io.BytesIO(z.read(name))) as nested:
                    check_zip(nested)
                exports += 1
        return {
            "schema": "gfxlab-gfx098-owner-audit-v1",
            "owner_archive_sha256": archive_sha,
            "outer_and_nested_zip_crc_valid": True,
            "nested_exports_verified": exports,
            "sessions": len(sessions),
            "events": counts["events"], "snapshots": counts["snapshots"],
            "unity_errors": counts["unity_errors"],
            "unity_warnings": counts["unity_warnings"], "dropped_messages": counts["dropped"],
            "complete_matrix_runs": counts["matrix_complete"],
            "capture_png_sha_verified": counts["capture_count"],
            "mode3_captures": counts["mode3"], "mode4_captures": counts["mode4"],
            "unique_model_mode_cases": len(cases), "all_cases_repeated_exactly": True,
            "gpu_readback_events": counts["gpu_readbacks"],
            "gpu_diagnostic_statuses": dict(gpu_statuses),
            "gpu_spread_categories": {key:sorted(value) for key,value in sorted(gpu_spreads.items())},
            "gpu_linear_and_noperspective_png_identical":
                bool(gpu_hashes.get("linear") and gpu_hashes.get("linear") == gpu_hashes.get("noperspective")),
            "originalShaderRestored": False, "phase_closed": False,
            "evidence_level": "GPU_EXPERIMENT_DIAGNOSTIC_ONLY"
        }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("archive")
    args = parser.parse_args()
    try:
        print(json.dumps(analyze(args.archive), indent=2, sort_keys=True))
        return 0
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
        print("GFX098_OWNER_AUDIT_FAILED: " + str(exc), file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
