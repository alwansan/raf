"""B09: stage original Spectrum passes privately from SHA-authenticated ZIP2 owners.

This does NOT create ShaderLab or claim Vulkan/Unity/device equivalence. Original
DXBC and serialized data remain in an external private temporary directory;
only numerical pass/stage relationships and hashes are suitable for CI reports.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile

from scripts.b09_spectrum_topology_contract import (
    TARGET, OWNER, PATH_ID, PASSES, BLOB_SEQUENCES, attest_spectrum,
)



def _safe(path: Path) -> Path:
    path = Path(path).absolute()
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise ValueError("Linked private or source path")
    return path


def _variant_key(meta: dict) -> str:
    """Explicit structural permutation identity; never pair by array position."""
    if not isinstance(meta, dict):
        raise ValueError("Malformed original program variant")
    keys = ("m_ShaderHardwareTier", "m_KeywordIndices", "m_GlobalKeywordIndices", "m_LocalKeywordIndices")
    return json.dumps([meta.get(k) for k in keys], sort_keys=True, separators=(",", ":"))


def stage_pairs(pass_data: dict, entries: list, *, linked_program, stage_variants, output_dir: Path):
    """Select all original vertex/fragment variant pairs and stage each original DXBC.

    Both members must be present, permutation-unique, and match *by identity*.
    A partial or unpaired original program never becomes a synthetic pass.
    """
    if pass_data.get("m_Type") != 0:
        raise ValueError("Non-normal Spectrum pass requires explicit program handling")
    program_by_stage = {}
    for stage, field in ((1, "progVertex"), (0, "progFragment")):
        program = pass_data.get(field)
        if not isinstance(program, dict):
            raise ValueError("Missing original Spectrum shader stage")
        variants = stage_variants(program)
        if not variants:
            raise ValueError("Original Spectrum stage has no variants")
        rows = {}
        for bucket, variant_index, meta in variants:
            key = _variant_key(meta)
            if key in rows:
                raise ValueError("Duplicate original Spectrum permutation")
            code, link = linked_program(meta, entries, stage)
            if not isinstance(code, bytes) or not code:
                raise ValueError("Original Spectrum DXBC is empty")
            rows[key] = {"code": code, "link": link, "bucket": bucket, "variant_index": variant_index}
        program_by_stage[stage] = rows
    if program_by_stage[1].keys() != program_by_stage[0].keys():
        raise ValueError("Original Spectrum vertex/fragment permutations do not match")
    result = []
    for pair_index, key in enumerate(sorted(program_by_stage[1])):
        row = {"pair_index": pair_index, "variant_key_sha256": hashlib.sha256(key.encode()).hexdigest(), "stages": {}}
        for stage in (1, 0):
            stage_row = program_by_stage[stage][key]
            code = stage_row["code"]
            filename = f"pair{pair_index:03d}-stage{stage}.dxbc"
            with (output_dir / filename).open("xb") as stream:
                stream.write(code)
                stream.flush()
                os.fsync(stream.fileno())
            row["stages"][str(stage)] = {
                "sha256": hashlib.sha256(code).hexdigest(), "bytes": len(code),
                "original_blob_index": stage_row["link"]["blob_index"],
                "segment_index": stage_row["link"]["segment_index"],
                "bucket": stage_row["bucket"], "variant_index": stage_row["variant_index"],
            }
        result.append(row)
    return result


def _selected_original(source):
    """Only the B17/W2-verified PathID2432 in the SHA-pinned original owner."""
    import UnityPy
    from scripts.probe_w2_water_shader_stage_bindings import extract_shader
    from scripts.b17_spectrum_stage_descriptors import summarize_passes

    environment = UnityPy.load(str(source / OWNER))
    original = [obj for obj in environment.objects
                if obj.type.name == "Shader" and int(obj.path_id) == PATH_ID]
    if len(original) != 1:
        raise ValueError("Original Spectrum PathID identity is missing or ambiguous")
    shader = original[0]
    tree = shader.read_typetree()
    topology = extract_shader({PATH_ID: shader}, PATH_ID, "Spectrum-graph")
    parsed = tree.get("m_ParsedForm", {})
    subs = parsed.get("m_SubShaders", [])
    if not isinstance(subs, list) or len(subs) != 1 or not isinstance(subs[0], dict):
        raise ValueError("Original Spectrum subshader shape changed")
    descriptors = summarize_passes(subs[0].get("m_Passes"))
    attestation = attest_spectrum(tree, topology, descriptors)
    return PATH_ID, hashlib.sha256(shader.get_raw_data()).hexdigest(), tree, attestation


def stage(source: Path, repo: Path, private: Path, report: Path):
    from scripts.verify_targeted_lfs_compute_sources import verify_sources, EXPECTED
    from scripts.w1_recover_graphics_programs import decoded_platforms, records
    from scripts.w1_recover_depth_passes import linked_program, stage_variants

    source, repo, private, report = (_safe(path) for path in (source, repo, private, report))
    if not source.is_dir() or not repo.is_dir() or not private.parent.is_dir() or not report.parent.is_dir():
        raise ValueError("Missing required source or scratch root")
    if private.is_relative_to(repo) or report.is_relative_to(repo) or source.is_relative_to(repo):
        raise ValueError("Private or original data must remain outside working checkout")
    if private.exists() or report.exists():
        raise ValueError("Refusing to overwrite private data or report")
    verify_sources(source, expected={OWNER: EXPECTED[OWNER]})
    path_id, object_sha, tree, attestation = _selected_original(source)
    parsed = tree.get("m_ParsedForm", {})
    subshaders = parsed.get("m_SubShaders")
    if not isinstance(subshaders, list):
        raise ValueError("Missing serialized Spectrum subshaders")
    counts = [len(sub.get("m_Passes", [])) for sub in subshaders]
    if counts != [PASSES]:
        raise ValueError("Original Spectrum exact seven-pass proof changed")
    tables = [(platform, records(segments)) for platform, segments in decoded_platforms(tree) if platform == 4]
    if len(tables) != 1:
        raise ValueError("Require a unique original D3D11 program table")
    entries = tables[0][1]
    aggregate = {"original_owner": OWNER, "original_owner_sha256": EXPECTED[OWNER][1],
                 "source_topology_attestation": attestation,
                 "original_object_path_id": path_id, "original_object_sha256": object_sha,
                 "original_subshader_pass_counts": counts, "original_passes": sum(counts),
                 "program_entry_count": len(entries), "stages": [], "private_packet_staged": False,
                 "shaderlab_reconstructed": False, "unity_compiled": False,
                 "device_pixels_verified": False, "published_private_programs": False}
    # Temporary staging guarantees failure cannot leave a half-complete packet.
    with tempfile.TemporaryDirectory(prefix="b09-spectrum-", dir=private.parent) as tmp:
        temp = Path(tmp)
        for si, sub in enumerate(subshaders):
            for pi, shader_pass in enumerate(sub["m_Passes"]):
                packet = temp / f"s{si:02d}-p{pi:02d}"
                packet.mkdir()
                pairs = stage_pairs(shader_pass, entries, linked_program=linked_program,
                                    stage_variants=stage_variants, output_dir=packet)
                if len(pairs) != 2:
                    raise ValueError("Original Spectrum two-per-stage permutation proof changed")
                for stage, stage_name in ((1, "progVertex"), (0, "progFragment")):
                    actual = sorted(row["stages"][str(stage)]["original_blob_index"] for row in pairs)
                    expected = sorted(BLOB_SEQUENCES[stage_name][2 * pi:2 * pi + 2])
                    if actual != expected:
                        raise ValueError("Original Spectrum blob-to-pass stage lineage changed")
                aggregate["stages"].append({"subshader": si, "pass_index": pi, "variant_pairs": pairs})
        # Run a second-stage byte-for-byte check of every freshly staged original.
        for row in aggregate["stages"]:
            folder = temp / f"s{row['subshader']:02d}-p{row['pass_index']:02d}"
            for pair in row["variant_pairs"]:
                for stage_index, staged in pair["stages"].items():
                    actual = folder / f"pair{pair['pair_index']:03d}-stage{stage_index}.dxbc"
                    if actual.stat().st_size != staged["bytes"] or hashlib.sha256(actual.read_bytes()).hexdigest() != staged["sha256"]:
                        raise ValueError("Private original DXBC staging mismatch")
        os.rename(temp, private)
    aggregate["private_packet_staged"] = True
    aggregate["private_packet_sha256"] = hashlib.sha256(json.dumps(aggregate["stages"], sort_keys=True).encode()).hexdigest()
    report.write_text(json.dumps(aggregate, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return aggregate


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", required=True, type=Path)
    p.add_argument("--repo", required=True, type=Path)
    p.add_argument("--private", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    try:
        result = stage(args.source, args.repo, args.private, args.out)
    except Exception as error:
        # No path, raw bytes, HLSL, original properties, stack or token in CI output.
        print("RAFT_B09_SPECTRUM " + json.dumps({"status": "blocked", "error_class": type(error).__name__,
                                                   "private_programs_published": False}))
        raise SystemExit(1) from None
    print("RAFT_B09_SPECTRUM " + json.dumps({"status": "staged", "original_passes": result["original_passes"],
                                            "variant_pairs": sum(len(x["variant_pairs"]) for x in result["stages"]),
                                            "private_programs_published": False}))


if __name__ == "__main__":
    main()
