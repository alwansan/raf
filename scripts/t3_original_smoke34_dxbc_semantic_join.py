#!/usr/bin/env python3
"""T3: exact SHA-original smoke34 DXBC VS/FS semantic and mask join (private).

Separate from the 921-use Shader48 and Particle108. Source Shader48 is
authenticated through 17 ParticleSystemRenderers/34 Material slots, original
six scenes and four owners. Original compiled DXBC signatures are compared
privately; only aggregate allowlisted counts leave the runner.
This does NOT link DXBC semantics to SPIR-V locations, ShaderLab or Android.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from scripts import t3_original_smoke34_dxbc_program_inventory as source
from scripts import t3_original_smoke34_spirv_translation as smoke
from scripts import t3_original_921_dxbc_semantic_join as signatures
from scripts.t3_smoke34_sameexport_shaderlab import original_private_smoke_target
from scripts.t3_original_renderer_shader_impact import SHADER_OWNERS_SELECTED
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.w1_stage_zip2_owners import fingerprint
from scripts.w1_recover_graphics_programs import decoded_platforms, records

STATUS = "SHA_ORIGINAL_SMOKE34_TWO_DXBC_SEMANTIC_MASK_PAIRS_CLASSIFIED"
PAIRS = 2
COUNT_KEYS = signatures.COUNTER_FIELDS
LIMIT = 4096
FLAGS_FALSE = {
    "source_original_DXBC_to_SPIRV_location_semantic_map_proven": False,
    "source_original_interpolant_or_texture_alpha_verified": False,
    "source_original_ShaderLab_restore_verified": False,
    "Android_Raft_device_pixel_fix_verified": False,
    "private_original_semantic_names_registers_program_bytes_published": False,
    "game_assets_modified": False,
}


def classify_two_pairs(pairs, *, reader=signatures.read_original_dxbc_signatures,
                       comparer=signatures.compare_original_vf):
    """All original stage data stays private, counters must be complete and safe."""
    if (type(pairs) is not list or len(pairs) != PAIRS or
        any(type(pair) is not tuple or len(pair) != 2 or
            any(type(data) is not bytes or not 0 < len(data) <=
                smoke.MAX_STAGE_BYTES for data in pair) for pair in pairs)):
        raise ValueError("changed_original_smoke34_two_keyword_pairs")
    aggregate = Counter()
    for vertex, fragment in pairs:
        src_vs = reader(vertex)
        src_fs = reader(fragment)
        joined = comparer(src_vs, src_fs)
        if type(joined) is not dict or set(joined) != set(COUNT_KEYS):
            raise ValueError("untrusted_original_smoke34_semantic_aggregate_shape")
        for key, value in joined.items():
            if type(value) is not int or not 0 <= value <= LIMIT:
                raise ValueError("untrusted_original_smoke34_semantic_aggregate_counter")
            aggregate[key] += value
    if aggregate["original_programs_read"] != PAIRS * 2:
        raise ValueError("smoke34_incomplete_original_signature_stage_pairs")
    return {
        "schema_version": 1,
        "status": STATUS,
        "source_role": "smoke_named_17_ParticleSystemRenderers_34_Material_slots",
        "sha_original_scene_count": 6,
        "sha_original_shader_owner_count": 4,
        "exact_original_keyword_vertex_fragment_pairs": PAIRS,
        "source_d3d11_table_records": 8,
        "counts": {key: int(aggregate[key]) for key in COUNT_KEYS},
        "source_original_compiled_DXBC_semantic_pairs_checked": True,
        **FLAGS_FALSE,
    }


def probe(root: Path, manifest: Path):
    import UnityPy
    # Same SHA-verified authentic smoke-linked Shader48 private identity as
    # CI42683328646 and CI42689814110, never infer from name or slot rank.
    shader_identity, state = original_private_smoke_target(root, manifest)
    if (type(state) is not dict or
        state.get("original_pass_color_mask_shaderlab_channels") != "RGB" or
        state.get("original_pass_color_blend_category") != "ALPHA_DEPENDENT" or
        state.get("original_pass_alpha_channel_blend_category") != "ALPHA_DEPENDENT" or
        state.get("original_pass_depth_write_category") != "OFF"):
        raise ValueError("original_smoke34_fixed_pass_semantics_changed")
    owner, private_path_id = shader_identity
    if owner not in SHADER_OWNERS_SELECTED:
        raise ValueError("untrusted_original_smoke34_shader_owner")
    path = root / "Raft_Data" / owner
    if (any(p.is_symlink() for p in (path, *path.parents)) or
        fingerprint(path) != SHADER_OWNERS[owner]):
        raise ValueError("original_smoke34_owner_SHA_mismatch")
    objects = [obj for obj in UnityPy.load(str(path)).file.objects.values()
               if obj.path_id == private_path_id]
    if len(objects) != 1 or objects[0].type.name != "Shader":
        raise ValueError("original_smoke34_Shader48_identity_drift")
    shader = objects[0].read_typetree()
    d3d = [records(segments) for platform, segments in decoded_platforms(shader)
           if platform == 4]
    if len(d3d) != 1:
        raise ValueError("missing_or_duplicate_original_smoke34_D3D11_table")
    baseline = source.classify(d3d[0], shader.get("m_ParsedForm"))
    if (baseline.get("status") != source.STATUS or
        baseline.get("original_D3D11_platform_table_records") != 8 or
        baseline.get("matched_vertex_fragment_permutation_pairs") != PAIRS or
        baseline.get("unmatched_vertex_permutations") != 0 or
        baseline.get("unmatched_fragment_permutations") != 0):
        raise ValueError("original_smoke34_stage_pair_baseline_changed")
    pairs = smoke.exact_two_pairs(shader.get("m_ParsedForm"), d3d[0])
    return classify_two_pairs(pairs)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for key in ("original", "manifest", "out"):
        parser.add_argument("--" + key, required=True, type=Path)
    args = parser.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink() or
        args.out.resolve().is_relative_to(args.original.resolve())):
        raise ValueError("unsafe_original_smoke34_signature_report_destination")
    try:
        report = probe(args.original, args.manifest)
    except Exception as exc:
        report = {"schema_version": 1, "status": "INCONCLUSIVE",
                  "failure_type": type(exc).__name__, **FLAGS_FALSE}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n",
                        encoding="utf-8")
    print("T3_SHA_ORIGINAL_SMOKE34_DXBC_SEMANTIC " + json.dumps(report, sort_keys=True))
    return 0 if report["status"] == STATUS else 2


if __name__ == "__main__":
    raise SystemExit(main())
