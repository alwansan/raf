#!/usr/bin/env python3
"""T3: original SHA-original smoke34 Shader48 D3D11 vertex/fragment feasibility.

Reuses privately authenticated 17-renderer/34-slot smoke Shader48 source from
six SHA-pinned original scenes. Only aggregate stage/keyword counts leave CI;
no original shader names, IDs, binaries, bytecode hashes or game assets.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from scripts.t3_smoke34_sameexport_shaderlab import original_private_smoke_target
from scripts import t3_original_top_shader_dxbc_feasibility as graph
from scripts import t3_original_renderer_shader_impact as source
from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.w1_stage_zip2_owners import fingerprint
from scripts.w1_recover_graphics_programs import decoded_platforms, records

STATUS = "SOURCE_SHA_ORIGINAL_SMOKE34_D3D11_STAGES_CLASSIFIED"
MISSING = "SOURCE_SHA_ORIGINAL_SMOKE34_D3D11_PLATFORM_MISSING"
COUNTERS = (
    "genuine_D3D11_vertex_stage_variant_records",
    "genuine_D3D11_fragment_stage_variant_records",
    "distinct_original_linked_D3D11_programs",
    "matched_vertex_fragment_permutation_pairs",
    "normal_passes_with_matched_permutation_pair",
    "normal_passes_without_matched_permutation_pair",
    "unmatched_vertex_permutations",
    "unmatched_fragment_permutations",
    "stage_variants_with_keywords",
)
COMMON = {
    "schema_version": 1,
    "original_shader_role": "smoke_named_17_renderers_34_slots",
    "original_shader_source_identity_private": True,
    "original_source_RGB_ColorMask_verified": True,
    "original_source_AlphaDependent_color_and_alpha_verified": True,
    "original_source_ZWrite_OFF_verified": True,
    "original_shader_passes_verified": 1,
    "original_shader_subshaders_verified": 1,
    "same_source_programs_compiled_for_Android_verified": False,
    "authored_original_ShaderLab_recovery_verified": False,
    "source_original_program_bytes_hashes_or_private_IDs_published": False,
    "native_game_device_smoke_pixels_verified": False,
}


def classify(table, parsed, *, summarizer=graph.summarize):
    """Safe source-only category; D3D absent is evidence not false success."""
    if type(parsed) is not dict:
        raise ValueError("missing_original_smoke34_parsed_shader")
    sub = parsed.get("m_SubShaders")
    if (type(sub) is not list or len(sub) != 1
        or type(sub[0]) is not dict
        or type(sub[0].get("m_Passes")) is not list
        or len(sub[0]["m_Passes"]) != 1
        or type(sub[0]["m_Passes"][0]) is not dict
        or sub[0]["m_Passes"][0].get("m_Type") != 0):
        raise ValueError("changed_original_smoke34_normal_Pass")
    out = dict(COMMON)
    if table is None:
        out.update(status=MISSING, original_D3D11_platform_present=False,
                   original_D3D11_platform_table_records=0,
                   source_original_D3D11_vertex_fragment_pair_available=False)
        out.update({k: 0 for k in COUNTERS})
        return out
    if (type(table) is not list or not table or len(table) > 200000
        or any(type(row) is not tuple or len(row) != 2
               or type(row[0]) is not int or row[0] < 0
               or type(row[1]) is not bytes or not row[1]
               for row in table)):
        raise ValueError("invalid_original_smoke34_D3D11_program_table")
    private = summarizer(parsed, table)
    if (type(private) is not dict
        or private.get("status") != graph.STATUS
        or private.get("original_source_Shader48_SubShader_count") != 1
        or private.get("original_source_Shader48_pass_count") != 1
        or private.get("normal_passes") != 1
        or private.get("non_normal_passes_not_stage_linked") != 0
        or any(type(private.get(k)) is not int or private[k] < 0
               for k in COUNTERS)):
        raise ValueError("inconsistent_original_smoke34_D3D11_source_stage_links")
    out.update(status=STATUS, original_D3D11_platform_present=True,
               original_D3D11_platform_table_records=len(table))
    out.update({k: private[k] for k in COUNTERS})
    out["source_original_D3D11_vertex_fragment_pair_available"] = (
        out["genuine_D3D11_vertex_stage_variant_records"] > 0
        and out["genuine_D3D11_fragment_stage_variant_records"] > 0
        and out["matched_vertex_fragment_permutation_pairs"] > 0)
    return out


def probe(root: Path, manifest: Path):
    import UnityPy
    shader_key, state = original_private_smoke_target(root, manifest)
    if (state.get("original_pass_color_mask_shaderlab_channels") != "RGB"
        or state.get("original_pass_color_blend_category") != "ALPHA_DEPENDENT"
        or state.get("original_pass_alpha_channel_blend_category") != "ALPHA_DEPENDENT"
        or state.get("original_pass_depth_write_category") != "OFF"):
        raise ValueError("changed_source_original_smoke34_alpha_mask")
    owner, pid = shader_key
    if owner not in source.SHADER_OWNERS_SELECTED:
        raise ValueError("unexpected_smoke34_private_shader_owner")
    path = root / "Raft_Data" / owner
    if path.is_symlink() or fingerprint(path) != SHADER_OWNERS[owner]:
        raise ValueError("original_smoke34_shader_owner_SHA_changed")
    objs = [o for o in UnityPy.load(str(path)).file.objects.values()
            if o.path_id == pid]
    if len(objs) != 1 or objs[0].type.name != "Shader":
        raise ValueError("unresolved_original_smoke34_shader_class")
    shader = objs[0].read_typetree()
    tables = [records(segments) for platform, segments in decoded_platforms(shader)
              if platform == 4]
    if len(tables) > 1:
        raise ValueError("duplicate_original_smoke34_D3D11_platform")
    out = classify(tables[0] if tables else None, shader.get("m_ParsedForm"))
    out["source_original_six_scenes_SHA_verified"] = True
    out["source_original_four_shader_owners_SHA_verified"] = True
    return out


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for name in ("original", "manifest", "out"):
        p.add_argument("--" + name, required=True, type=Path)
    a = p.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink()
        or a.out.resolve().is_relative_to(a.original.resolve())):
        raise ValueError("unsafe_private_original_smoke34_D3D11_report_destination")
    try:
        out = probe(a.original, a.manifest)
    except Exception as exc:
        out = {
            "schema_version": 1,
            "status": "INCONCLUSIVE",
            "failure_type": type(exc).__name__,
            "source_original_program_bytes_hashes_or_private_IDs_published": False,
            "native_game_device_smoke_pixels_verified": False,
        }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2, sort_keys=True)+"\n",
                     encoding="utf-8")
    print("T3_SHA_ORIGINAL_SMOKE34_D3D11 " + json.dumps(out, sort_keys=True))
    return 0 if out["status"] in (STATUS, MISSING) else 2


if __name__ == "__main__":
    raise SystemExit(main())
