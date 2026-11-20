"""Translate SHA-authenticated NEXT23b stages privately; publish numeric proof only.

This source-only step does not compose/install ShaderLab or establish Unity,
GUID restoration, rendering or device compatibility.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import shutil

from scripts.gt_next23b_source_topology_census import select_remaining_23_source_owners
from scripts.gt_rank_all82_original_shader_names_after_nine import gather
from scripts.gt_stage_serialized_owners import read_expected
from scripts.gt_serialized_graphics_counts import verify
from scripts.gt_original_921_all_variants import enumerate_all
from scripts.t3_original_top_shader_dxbc_feasibility import summarize
from scripts.w1_recover_depth_passes import linked_program, stage_variants, variant_key
from scripts.w1_recover_graphics_programs import decoded_platforms, records, translate

STATUS = "GT_NEXT23B_SHA_ORIGINAL_D3D11_PRIVATE_STAGES_TRANSLATED"
FIELDS = ("original_source_Shader48_pass_count",
          "matched_vertex_fragment_permutation_pairs",
          "unmatched_vertex_permutations", "unmatched_fragment_permutations",
          "distinct_original_linked_D3D11_programs")
EXPECTED = (4, 1156, 0, 0, 134)
COMPILER_FIELDS = ("vulkan11_valid", "hlsl_recovered", "roundtrip_vulkan11_valid")


def validate_topology(profile):
    if any(type(profile.get(k)) is not int or profile[k] != v
           for k, v in zip(FIELDS, EXPECTED)):
        raise ValueError("authenticated_original_next23b_topology_drift")


def recover_programs(distinct, private, translator=translate):
    if len(distinct) != 134:
        raise ValueError("original_next23b_distinct_program_population_drift")
    counts = Counter()
    refs = {}
    for index, (ident, record) in enumerate(distinct.items()):
        folder = private / ("program-%03d" % index)
        folder.mkdir(mode=0o700)
        result = translator(record["source_code"], record["stage"], folder)
        if not isinstance(result, dict) or any(type(result.get(k)) is not bool for k in COMPILER_FIELDS):
            raise ValueError("untrusted_next23b_compiler_result")
        refs[ident] = folder.name
        counts["attempted"] += 1
        for key in COMPILER_FIELDS:
            counts[key] += int(result[key])
        counts["all_three_valid"] += int(all(result[k] for k in COMPILER_FIELDS))
    return refs, counts


def run(original, manifest, quality, private):
    import UnityPy
    for tool in ("vkd3d-compiler", "spirv-val", "spirv-cross", "glslangValidator"):
        if shutil.which(tool) is None:
            raise ValueError("missing_next23b_private_translation_tool")
    names, _ = gather(original, manifest)
    candidates = select_remaining_23_source_owners(names, json.loads(quality.read_text("utf-8")))
    pins = read_expected(manifest)
    selected = []
    for owner, pid in candidates:
        if owner not in pins:
            raise ValueError("untrusted_next23b_source_owner")
        _, size, digest = pins[owner]
        source = original / owner
        if source.is_symlink() or not source.is_file():
            raise ValueError("unsafe_next23b_source_owner")
        verify(source, size, digest)
        objects = [obj for obj in UnityPy.load(str(source)).objects
                   if obj.path_id == pid and str(obj.type.name) == "Shader"]
        if len(objects) != 1:
            raise ValueError("next23b_source_shader_object_not_unique")
        tree = objects[0].read_typetree()
        tables = [records(data) for platform, data in decoded_platforms(tree) if platform == 4]
        if len(tables) != 1:
            raise ValueError("next23b_source_D3D11_table_not_unique")
        profile = summarize(tree.get("m_ParsedForm"), tables[0])
        validate_topology(profile)
        selected.append((owner, pid, tree, tables[0]))
    if len(selected) != 1:
        raise ValueError("next23b_source_identity_not_unique")
    owner, pid, tree, table = selected[0]
    paired, orphans, passes, distinct = enumerate_all(
        tree["m_ParsedForm"], table, variants=stage_variants,
        permutation=variant_key, linker=linked_program,
        topology=(4, 1156, 0, 134), per_stage_variant_cap=2048)
    if private.exists() or private.is_symlink() or not private.parent.is_dir():
        raise ValueError("unsafe_next23b_private_location")
    private.mkdir(mode=0o700)
    refs, counts = recover_programs(distinct, private)
    def stage_row(row):
        return {k: (refs[v] if k == "program_ref" else v) for k, v in row.items()}
    packet = {"schema_version": 1, "source_owner": owner, "source_PathID": pid,
              "original_ParsedForm": tree["m_ParsedForm"], "original_passes": passes,
              "paired": [{"subshader": p["subshader"], "pass": p["pass"],
                          "vs": stage_row(p["vs"]), "fs": stage_row(p["fs"])} for p in paired],
              "unpaired": orphans}
    (private / "original-private-variant-manifest.json").write_text(json.dumps(packet, sort_keys=True) + "\n", encoding="utf-8")
    return {"schema_version": 1,
            "status": STATUS if counts["all_three_valid"] == 134 else "PARTIAL_NEXT23B_PRIVATE_STAGE_TRANSLATION",
            "actual_source_material_quality_run": 43929698985,
            "original_source_82_owners_authenticated": True,
            "source_Shader48_Pass_count": 4, "source_paired_VSFS_routes": len(paired),
            "source_unpaired_variants": len(orphans), "source_distinct_D3D11_programs": len(distinct),
            "private_programs_attempted": counts["attempted"],
            **{k: counts[k] for k in COMPILER_FIELDS},
            "all_three_compiler_gates_valid": counts["all_three_valid"],
            "original_names_digests_owner_PathIDs_GUIDs_shader_bytes_exported": False,
            "Unity_shader_installation_same_export_GUID_or_device_render_proven": False,
            "APK_OBB_XAPK_created": False}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    for key in ("original", "manifest", "quality", "private", "out"):
        p.add_argument("--" + key, type=Path, required=True)
    a = p.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink() or a.private.is_symlink()
            or a.out.resolve().is_relative_to(a.original.resolve())
            or a.out.resolve().is_relative_to(a.private.resolve())
            or a.private.resolve().is_relative_to(a.original.resolve())):
        raise ValueError("unsafe_next23b_public_private_separation")
    try:
        report = run(a.original, a.manifest, a.quality, a.private)
    except Exception as exc:
        report = {"schema_version": 1, "status": "INCONCLUSIVE", "error_type": type(exc).__name__,
                  "original_names_digests_owner_PathIDs_GUIDs_shader_bytes_exported": False,
                  "APK_OBB_XAPK_created": False}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("GT_NEXT23B_PRIVATE_STAGE_TRANSLATION_SAFE " + json.dumps(report, sort_keys=True))
    return 0 if report["status"] == STATUS else 2


if __name__ == "__main__":
    raise SystemExit(main())
