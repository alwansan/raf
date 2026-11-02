"""Read-only search for valid DXBC shader containers in original Unity objects.

No Unity Editor, Android/native build, game execution, original shader dumps,
republication or paid-plugin source reconstruction. Only actual serialized
ComputeShader objects are inspected. Git LFS pointers are *not* fabricated
or automatically fetched; missing source owners remain explicitly unknown.
"""
import argparse
import gc
import hashlib
import json
from pathlib import Path
import struct

from scripts.mesh_source_files import owned_objects, serialized_sources
from scripts.probe_directx_shader_bridge import inspect, MAX_SHADER_BYTES

MAX_COMPUTE_OBJECT_BYTES = 64 * 1024 * 1024
MAX_MAGIC_HITS_PER_OBJECT = 128
MAX_OBJECT_COUNT = 64


def scan_blob(blob: bytes) -> dict:
    if not isinstance(blob, bytes) or len(blob) > MAX_COMPUTE_OBJECT_BYTES:
        raise ValueError("Original compute object exceeds bounded search scope")
    matches = []
    hits = 0
    start = 0
    while True:
        offset = blob.find(b"DXBC", start)
        if offset < 0:
            break
        hits += 1
        if hits > MAX_MAGIC_HITS_PER_OBJECT:
            raise ValueError("Unusual number of DXBC signatures in original compute object")
        if offset + 32 <= len(blob):
            claimed = struct.unpack_from("<I", blob, offset + 24)[0]
            if 36 <= claimed <= MAX_SHADER_BYTES and offset + claimed <= len(blob):
                try:
                    report = inspect(blob[offset:offset + claimed])
                except ValueError:
                    report = None
                if report is not None:
                    matches.append({
                        "offset_in_original_object": offset,
                        "binary_sha256": report["claimed_sha256"],
                        "bytes": report["bytes"],
                        "container": report["container"],
                        "chunk_tags": report["chunk_tags"],
                        "executable_shader_chunk": report["executable_shader_chunk"],
                        "program_bytes_exported": False,
                    })
        start = offset + 4
    return {
        "valid_dxbc_containers": matches,
        "candidate_dxbc_magic_count": hits,
        # This is a signature hit count, not a validated SPIR-V module count:
        # serialized Unity objects may hold platform-specific compressed blobs.
        "candidate_spirv_magic_count": blob.count(b"\x03\x02\x23\x07"),
        "missing_shader_source_inferred": False,
        "gpu_runtime_verified": False,
    }


def inspect_regular_sources(root: Path) -> dict:
    if not root.is_dir():
        raise ValueError("Original Unity serializations unavailable")
    import UnityPy
    objects = []
    missing_lfs_owners = []
    inspected_files = 0
    for source in serialized_sources(root):
        if source.is_symlink() or not source.is_file():
            raise ValueError("Unsafe original serialized source")
        with source.open("rb") as stream:
            if stream.read(48).startswith(b"version https://git-lfs.github.com/spec/v1"):
                missing_lfs_owners.append(source.name)
                continue
        env = UnityPy.load(str(source))
        inspected_files += 1
        for obj in owned_objects(env):
            if obj.type.name != "ComputeShader":
                continue
            if len(objects) >= MAX_OBJECT_COUNT:
                raise ValueError("Original compute object count exceeded guard")
            raw = obj.get_raw_data()
            result = scan_blob(raw)
            objects.append({
                "owner": source.name,
                "original_path_id": int(obj.path_id),
                "original_object_sha256": hashlib.sha256(raw).hexdigest(),
                "raw_object_bytes": len(raw),
                **result,
            })
        del env
        gc.collect()
    return {
        "regular_unity_sources_examined": inspected_files,
        "unavailable_lfs_owners": sorted(missing_lfs_owners),
        "compute_objects_examined": len(objects),
        "compute_objects": objects,
        "all_nine_original_compute_objects_examined": len(objects) == 9 and not missing_lfs_owners,
        "original_source_modified": False,
        "original_shaders_recovered": False,
        "android_gpu_execution_verified": False,
        "all_platform_shader_programs_decoded": False,
        "standalone_shader_translation_test": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    report = inspect_regular_sources(args.source)
    print("RAFT_ORIGINAL_COMPUTE_DXBC_CONTAINER_SCAN " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
