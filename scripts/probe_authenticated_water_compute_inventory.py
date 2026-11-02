"""Cross-check original ComputeShader ownership, metadata and DXBC provenance.

Use ONLY after verifying exact LFS SHA256. Not a shader restorer; a DXBC
signature is not evidence of FFT identity or Android GPU execution.
"""
import argparse
import json
from pathlib import Path

from scripts.verify_targeted_lfs_compute_sources import verify_sources
from scripts.probe_original_compute_containers import inspect_regular_sources
from scripts.audit_original_compute_metadata import inspect as inspect_metadata


def reconcile(scanner, metadata):
    if scanner["unavailable_lfs_owners"]:
        raise ValueError("Not all original LFS owner files hydrated")
    left = {
        (x["owner"], x["original_path_id"]): x["original_object_sha256"]
        for x in scanner["compute_objects"]
    }
    right = {
        (x["owner"], x["object_path_id"]): x["original_object_sha256"]
        for x in metadata["compute_objects"]
    }
    if (len(left) != 9 or len(right) != 9 or left != right
            or not scanner["all_nine_original_compute_objects_examined"]):
        raise ValueError("Original nine ComputeShader identities not corroborated")
    return {
        "original_compute_shader_objects_correlated": len(left),
        "source_owner_identity_matched": True,
        "original_objects": scanner["compute_objects"],
        "serialized_compute_metadata": metadata["compute_objects"],
        "fft_kernel_index_order_verified": False,
        "water_compute_owner_verified": False,
        "android_gpu_execution_verified": False,
        "private_program_bytes_published": False,
        "original_assets_modified": False,
    }


def probe(root: Path):
    provenance = verify_sources(root)
    scanner = inspect_regular_sources(root)
    metadata = inspect_metadata(root, expected_objects=9)
    return {"lfs_provenance": provenance, **reconcile(scanner, metadata)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    print("RAFT_AUTHENTIC_COMPUTE_9_OBJECT_PROBE " + json.dumps(probe(args.source), sort_keys=True))


if __name__ == "__main__":
    main()
