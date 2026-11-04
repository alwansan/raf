"""B09 original Spectrum packet -> private DXBC/Vulkan/HLSL structural roundtrips.

Only the SHA-bound numerical stage summary is publishable. Raw original DXBC,
SPIR-V and translated HLSL stay outside the git checkout and CI artifacts.
This DOES NOT claim complete ShaderLab, Unity import, pixels or device parity.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tempfile

from scripts.b09_spectrum_topology_contract import OWNER, PATH_ID, PASSES, BLOB_SEQUENCES
from scripts.verify_targeted_lfs_compute_sources import EXPECTED


def _safe(path):
    path = Path(path).absolute()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError("Unsafe original/scratch symlink")
    return path


def validate_packet(packet, manifest):
    if (manifest.get("original_owner") != OWNER
            or manifest.get("original_owner_sha256") != EXPECTED[OWNER][1]
            or manifest.get("original_object_path_id") != PATH_ID
            or manifest.get("original_subshader_pass_counts") != [PASSES]
            or manifest.get("private_packet_staged") is not True
            or manifest.get("source_topology_attestation", {}).get("authenticated_variant_stage_programs") != 28):
        raise ValueError("Original Spectrum owner/graph attestation missing")
    rows = manifest.get("stages")
    if not isinstance(rows, list) or len(rows) != PASSES:
        raise ValueError("Spectrum original seven-pass packet missing")
    blobs = {}
    for pi, item in enumerate(rows):
        if not isinstance(item, dict) or item.get("subshader") != 0 or item.get("pass_index") != pi:
            raise ValueError("Spectrum pass order changed")
        pairs = item.get("variant_pairs")
        if not isinstance(pairs, list) or len(pairs) != 2:
            raise ValueError("Spectrum original variant pairing changed")
        for vi, pair in enumerate(pairs):
            if not isinstance(pair, dict) or pair.get("pair_index") != vi:
                raise ValueError("Spectrum permutation index changed")
            stages = pair.get("stages")
            if not isinstance(stages, dict) or set(stages) != {"0", "1"}:
                raise ValueError("Spectrum stage pair missing")
            for stage, name in ((0, "progFragment"), (1, "progVertex")):
                meta = stages[str(stage)]
                blob = meta.get("original_blob_index")
                digest = meta.get("sha256")
                size = meta.get("bytes")
                if (type(blob) is not int or blob < 0
                        or type(size) is not int or not 0 < size <= 4 * 1024 * 1024
                        or not isinstance(digest, str) or len(digest) != 64
                        or any(c not in "0123456789abcdef" for c in digest)):
                    raise ValueError("Invalid original DXBC metadata")
                if blob not in BLOB_SEQUENCES[name][2*pi:2*pi+2]:
                    raise ValueError("Original stage blob index not in pass")
                path = _safe(packet / f"s00-p{pi:02d}" / f"pair{vi:03d}-stage{stage}.dxbc")
                if not path.is_file() or path.stat().st_size != size:
                    raise ValueError("Original stage packet missing/size changed")
                data = path.read_bytes()
                if hashlib.sha256(data).hexdigest() != digest:
                    raise ValueError("Original stage packet SHA mismatch")
                key = (stage, blob)
                if key in blobs and blobs[key][0] != digest:
                    raise ValueError("Reused original stage blob changed")
                blobs[key] = (digest, data)
        for stage, name in ((0, "progFragment"), (1, "progVertex")):
            indices = sorted(pair["stages"][str(stage)]["original_blob_index"] for pair in pairs)
            if indices != sorted(BLOB_SEQUENCES[name][2*pi:2*pi+2]):
                raise ValueError("Original Spectrum stage permutation/linkage changed")
    return blobs


def translate_packet(packet, stage_report, repo, output, *, translator=None):
    packet, stage_report, repo, output = map(_safe, (packet, stage_report, repo, output))
    if not packet.is_dir() or not stage_report.is_file() or not repo.is_dir() or output.exists():
        raise ValueError("Original packet/report missing or output exists")
    if any(p.is_relative_to(repo) for p in (packet, stage_report, output)):
        raise ValueError("Original stage bytes/output must remain outside git checkout")
    manifest = json.loads(stage_report.read_text(encoding="utf-8"))
    blobs = validate_packet(packet, manifest)
    if translator is None:
        from scripts.w1_recover_graphics_programs import translate as translator
    observed = []
    with tempfile.TemporaryDirectory(prefix="b09-private-spirv-", dir=output.parent) as scratch:
        for (stage, blob), (digest, code) in sorted(blobs.items()):
            target = Path(scratch) / f"s{stage}b{blob}"
            target.mkdir()
            result = translator(code, stage, target)
            if (not isinstance(result, dict) or result.get("dxbc_sha256") != digest
                    or result.get("vulkan11_valid") is not True
                    or result.get("hlsl_recovered") is not True
                    or result.get("roundtrip_vulkan11_valid") is not True):
                raise ValueError("Spectrum original private stage translation failed")
            observed.append({"stage": stage, "original_blob_index": blob,
                             "dxbc_sha256": digest, "bytes": len(code),
                             "vulkan11_valid": True, "hlsl_recovered_privately": True,
                             "roundtrip_vulkan11_valid": True, "pixel_equivalence": False})
    aggregate = {"original_owner_sha256": EXPECTED[OWNER][1],
                 "original_object_sha256": manifest["original_object_sha256"],
                 "original_pass_count": PASSES, "stage_references_verified": PASSES * 4,
                 "original_stage_blob_slots": len(blobs),
                 "stage_roundtrips_verified": len(observed),
                 "stages": observed, "private_programs_published": False,
                 "shaderlab_reconstructed": False, "unity_gpu_or_device_verified": False}
    output.write_text(json.dumps(aggregate, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return aggregate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private", type=Path, required=True)
    parser.add_argument("--stage-report", type=Path, required=True)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = translate_packet(args.private, args.stage_report, args.repo, args.out)
    except Exception as exc:
        print("RAFT_B09_SPECTRUM_TRANSLATION " + json.dumps({
            "status": "blocked", "error_class": type(exc).__name__,
            "private_programs_published": False}))
        raise SystemExit(1) from None
    print("RAFT_B09_SPECTRUM_TRANSLATION " + json.dumps({
        "status": "structural_roundtrips_verified",
        "original_passes": result["original_pass_count"],
        "stage_roundtrips": result["stage_roundtrips_verified"],
        "unity_gpu_or_device_verified": False}))


if __name__ == "__main__":
    main()
