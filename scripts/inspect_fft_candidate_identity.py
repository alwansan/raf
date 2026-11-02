"""Inspect two *candidate* original FFT ComputeShaders without guessing identity.

Only use after exact LFS SHA256 authentication. Never print proprietary
names, shader instructions or source. Indices remain in serialized order.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from scripts.verify_targeted_lfs_compute_sources import verify_sources
from scripts.probe_original_compute_containers import scan_blob
from scripts.run_original_dxbc_translation_probe import version_tokens

EXPECTED_CANDIDATES = {
    ("resources.assets", 905): "f1e78e6dd6a069481444892f8d63c7b88850b789714ce8ebb136846b0c672f62",
    ("sharedassets0.assets", 2456): "9d934f5c99183c6df5cf2f1fefc9d3e5ec4bce5da5f96a86e4c02910d5322247",
}


def rank(metadata):
    selected = set()
    for row in metadata:
        kernels = row.get("metadata", {}).get("metadata_array_totals", {}).get("kernels", 0)
        if kernels >= 7:
            selected.add((row["owner"], row["object_path_id"]))
    if selected != set(EXPECTED_CANDIDATES):
        raise ValueError("Original FFT candidate set changed; do not assign kernel indices")
    return sorted(selected)


def identity_summary(tree):
    if not isinstance(tree, dict):
        raise ValueError("Serialized compute source has no readable dictionary")
    name = tree.get("m_Name")
    if not isinstance(name, str) or len(name) > 256:
        name = ""
    variants = tree.get("variants")
    if not isinstance(variants, list) or len(variants) != 1 or not isinstance(variants[0], dict):
        raise ValueError("Serialized compute shader variants absent or ambiguous")
    kernels = variants[0].get("kernels")
    if not isinstance(kernels, list) or len(kernels) > 64:
        raise ValueError("Serialized kernel table absent or outside safe scope")
    name_hashes = []
    for entry in kernels:
        identifier = None
        if isinstance(entry, dict):
            for key in ("name", "m_Name"):
                value = entry.get(key)
                if isinstance(value, str) and 0 < len(value) <= 256:
                    identifier = hashlib.sha256(value.encode("utf-8")).hexdigest()
                    break
        name_hashes.append(identifier)
    lower = name.casefold()
    return {
        "asset_name_sha256": hashlib.sha256(name.encode("utf-8")).hexdigest() if name else None,
        "asset_name_contains_fft": "fft" in lower,
        "asset_name_contains_water": "water" in lower,
        "asset_name_contains_spectrum": "spectrum" in lower,
        "original_serialized_kernel_count": len(kernels),
        "kernel_identifier_sha256_by_original_slot": name_hashes,
        "original_kernel_order_rewritten": False,
        "names_or_programs_disclosed": False,
    }


def inspect(root: Path):
    verify_sources(root)
    import UnityPy
    results = []
    for owner, path_id in sorted(EXPECTED_CANDIDATES):
        source = root / owner
        env = UnityPy.load(str(source))
        objects = [o for o in env.file.objects.values()
                   if o.type.name == "ComputeShader" and int(o.path_id) == path_id]
        if len(objects) != 1:
            raise ValueError("Candidate original ComputeShader missing or ambiguous")
        obj = objects[0]
        raw = obj.get_raw_data()
        if hashlib.sha256(raw).hexdigest() != EXPECTED_CANDIDATES[(owner, path_id)]:
            raise ValueError("Original candidate ComputeShader object SHA256 changed")
        scanned = scan_blob(raw)
        identity = identity_summary(obj.read_typetree())
        dxbc = scanned["valid_dxbc_containers"]
        if len(dxbc) != identity["original_serialized_kernel_count"]:
            raise ValueError("Original kernel/program slot counts differ; cannot infer mapping")
        versions = Counter()
        for row in dxbc:
            start = row["offset_in_original_object"]
            data = raw[start:start + row["bytes"]]
            tokens = version_tokens(data)
            if len(tokens) != 1:
                raise ValueError("Non-unique original DXBC shader stage token")
            key = (tokens[0]["shader_stage_code"], *tokens[0]["shader_model"])
            versions[str(key)] += 1
        results.append({
            "owner": owner,
            "original_path_id": path_id,
            "original_object_sha256": hashlib.sha256(raw).hexdigest(),
            "dxbc_programs_detected": len(dxbc),
            "dxbc_shader_stage_model_counts": dict(sorted(versions.items())),
            **identity,
            "fft_owner_proven": False,
        })
    return {"candidate_count": len(results), "candidates": results,
            "fft_resource_bindings_verified": False, "android_gpu_executed": False,
            "original_source_modified": False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    args = p.parse_args()
    print("RAFT_PRIVATE_FFT_COMPUTE_CANDIDATES " + json.dumps(inspect(args.source), sort_keys=True))


if __name__ == "__main__":
    main()
