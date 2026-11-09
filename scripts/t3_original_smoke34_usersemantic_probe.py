#!/usr/bin/env python3
"""Original SHA-original smoke34 two-PS SPIR-V explicit UserSemantic census.

Checks *actual* compiler-emitted SPIR-V annotations on private original and
HLSL-roundtrip modules. Compiler OpName and numeric register/Location equality
are NOT accepted as provenance. Semantic names/programs remain private; only
allowlisted aggregate counters and fixed false device gates are published.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import tempfile

from scripts import t3_original_smoke34_ps_readmask_spirv as baseline
from scripts import t3_original_921_dxbc_semantic_join as dxbc
from scripts import t3_smoke34_spirv_usersemantic_annotations as annotations
from scripts.w1_recover_graphics_programs import translate
from scripts.w1_recover_depth_passes import reflection

PAIRS = 2
STATUS = "SHA_ORIGINAL_SMOKE34_SPIRV_EXPLICIT_USERSEMANTIC_PROVENANCE_AVAILABILITY"
STAGE_COUNTS = tuple(
    phase + "_" + k for phase in ("original", "roundtrip") for k in annotations.FIELDS
)
COUNTERS = ("genuine_fragment_pairs_examined",) + STAGE_COUNTS
FALSE_CLAIMS = {
    "original_DXBC_semantics_to_SPIRV_instruction_dataflow_proven": False,
    "numerical_register_Location_coincidence_is_provenance": False,
    "source_roundtrip_semantic_value_equivalence_proven": False,
    "authored_original_ShaderLab_restored": False,
    "Android_Adreno_smoke_pixels_verified": False,
    "private_semantics_shader_bytes_ids_hashes_or_locations_published": False,
    "game_assets_modified": False,
}


def evaluate(pairs, private_root: Path, *,
             translator=translate, reflector=reflection,
             reader=dxbc.read_original_dxbc_signatures,
             scanner=annotations.parse_private_spirv,
             classifier=annotations.classify_original_and_spirv):
    if (type(pairs) is not list or len(pairs) != PAIRS or
        not isinstance(private_root, Path) or
        not private_root.is_dir() or private_root.is_symlink() or
        any(type(pair) is not tuple or len(pair) != 2 or
            any(type(code) is not bytes or
                not 0 < len(code) <= baseline.MAX_PROGRAM_BYTES
                for code in pair) for pair in pairs)):
        raise ValueError("invalid_original_smoke34_explicit_provenance_scope")
    counters = Counter()
    for i, (vs, ps) in enumerate(pairs):
        vertex = reader(vs)
        fragment = reader(ps)
        if (type(vertex) is not dict or type(fragment) is not dict or
            fragment.get("input_tag") not in ("ISGN", "ISG1") or
            vertex.get("output_tag") not in ("OSGN", "OSG1", "OSG5")):
            raise ValueError("original_smoke34_DXBC_signature_stage_mismatch")
        linkage = dxbc.compare_original_vf(vertex, fragment)
        if (linkage["original_programs_read"] != 2 or
            linkage["original_unmatched_fragment_semantic_records"] != 0 or
            linkage["original_matched_semantic_missing_output_component_lanes"] != 0 or
            linkage["original_matched_semantic_type_mismatches"] != 0):
            raise ValueError("original_smoke34_DXBC_semantic_baseline_changed")

        temporary = private_root / ("private-original-pair-" + str(i) + "-ps")
        temporary.mkdir(exist_ok=False)
        flags = translator(ps, 0, temporary)
        if (type(flags) is not dict or
            ("stage" in flags and flags["stage"] != 0) or
            any(flags.get(k) is not True for k in
                ("vulkan11_valid", "hlsl_recovered", "roundtrip_vulkan11_valid"))):
            raise ValueError("private_smoke34_SPIRV_translator_not_complete")
        for phase, filename in (("original", "original.spv"),
                                ("roundtrip", "roundtrip.spv")):
            binary_path = temporary / filename
            if (binary_path.is_symlink() or not binary_path.is_file() or
                not 20 <= binary_path.stat().st_size <= 4*annotations.MAX_WORDS):
                raise ValueError("private_original_smoke34_SPIRV_stage_file_invalid")
            safe_reflected = reflector(binary_path)
            private_data = scanner(binary_path.read_bytes())
            classified = classifier(fragment["input"], safe_reflected, private_data)
            if type(classified) is not dict or set(classified) != set(annotations.FIELDS):
                raise ValueError("untrusted_private_SPIRV_annotation_classifier_fields")
            for key, value in classified.items():
                upper = (1 if key in annotations.BOOLEAN_FIELDS else 256)
                if type(value) is not int or not 0 <= value <= upper:
                    raise ValueError("untrusted_private_SPIRV_annotation_count")
                counters[phase + "_" + key] += value
        counters["genuine_fragment_pairs_examined"] += 1
    if (counters["genuine_fragment_pairs_examined"] != PAIRS or
        counters["original_original_dx_user_input_records"] != 7 or
        counters["roundtrip_original_dx_user_input_records"] != 7 or
        counters["original_original_dx_declared_lanes"] != 28 or
        counters["roundtrip_original_dx_declared_lanes"] != 28 or
        counters["original_reflected_spirv_declared_lanes"] != 28 or
        counters["roundtrip_reflected_spirv_declared_lanes"] != 28):
        raise ValueError("smoke34_source_authentic_declared_interface_baseline_changed")
    return {
        "schema_version": 1,
        "status": STATUS,
        "source": "SHA_original_smoke34_17_emitters_34_material_slots",
        "source_sha_pinned_scenes": 6,
        "source_sha_pinned_owners": 4,
        "original_exact_keyword_matched_fragment_pairs": PAIRS,
        "counts": {key: int(counters[key]) for key in COUNTERS},
        "original_source_semantics_compiler_decorations_censused": True,
        **FALSE_CLAIMS,
    }


def probe(original_root: Path, manifest: Path, *,
          translator=translate, reflector=reflection):
    # The preceding original smoke34 readmask probe authenticated this exact
    # shader, pass RGB/alpha blend, six scenes, four owners, and two stages.
    # Reuse its source selector, never fuzzy-match names or export bytecode.
    from scripts.t3_smoke34_sameexport_shaderlab import original_private_smoke_target
    from scripts.t3_original_renderer_shader_impact import SHADER_OWNERS_SELECTED
    from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
    from scripts.w1_stage_zip2_owners import fingerprint
    from scripts.w1_recover_graphics_programs import decoded_platforms, records
    from scripts import t3_original_smoke34_dxbc_program_inventory as inventory
    from scripts import t3_original_smoke34_spirv_translation as stages
    import UnityPy
    selection, state = original_private_smoke_target(original_root, manifest)
    if (type(state) is not dict or
        state.get("original_pass_color_mask_shaderlab_channels") != "RGB" or
        state.get("original_pass_color_blend_category") != "ALPHA_DEPENDENT" or
        state.get("original_pass_alpha_channel_blend_category") != "ALPHA_DEPENDENT" or
        state.get("original_pass_depth_write_category") != "OFF"):
        raise ValueError("original_smoke34_private_pass_state_baseline_drift")
    owner, private_id = selection
    if owner not in SHADER_OWNERS_SELECTED:
        raise ValueError("original_smoke34_wrong_Shader_owner")
    path = original_root / "Raft_Data" / owner
    if path.is_symlink() or fingerprint(path) != SHADER_OWNERS[owner]:
        raise ValueError("original_smoke34_owner_SHA_drift")
    objects = [x for x in UnityPy.load(str(path)).file.objects.values()
               if x.path_id == private_id]
    if len(objects) != 1 or objects[0].type.name != "Shader":
        raise ValueError("original_smoke34_shader_object_not_unique")
    tree = objects[0].read_typetree()
    tables = [records(v) for p, v in decoded_platforms(tree) if p == 4]
    if len(tables) != 1:
        raise ValueError("original_smoke34_D3D11_platform_not_unique")
    original = inventory.classify(tables[0], tree.get("m_ParsedForm"))
    if (original.get("status") != inventory.STATUS or
        original.get("original_D3D11_platform_table_records") != 8 or
        original.get("matched_vertex_fragment_permutation_pairs") != PAIRS or
        original.get("unmatched_vertex_permutations") != 0 or
        original.get("unmatched_fragment_permutations") != 0):
        raise ValueError("original_smoke34_compiled_keyword_table_drift")
    private_pairs = stages.exact_two_pairs(tree.get("m_ParsedForm"), tables[0])
    with tempfile.TemporaryDirectory(prefix="t3-smoke34-private-annot-") as root:
        return evaluate(private_pairs, Path(root),
                        translator=translator, reflector=reflector)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    for f in ("original", "manifest", "out"):
        p.add_argument("--" + f, type=Path, required=True)
    args = p.parse_args(argv)
    if (args.out.exists() or args.out.is_symlink() or
        args.out.resolve().is_relative_to(args.original.resolve())):
        raise ValueError("smoke34_annotation_private_report_destination")
    try:
        report = probe(args.original, args.manifest)
    except Exception as exc:
        # Never print untrusted names, GPU code, compiler stderr or private IDs.
        report = {"schema_version": 1, "status": "INCONCLUSIVE",
                  "exception_type": type(exc).__name__, **FALSE_CLAIMS}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    print("T3_SMOKE34_ORIGINAL_USERSEMANTIC_CENSUS " + json.dumps(report, sort_keys=True))
    return 0 if report["status"] == STATUS else 2


if __name__ == "__main__":
    raise SystemExit(main())
