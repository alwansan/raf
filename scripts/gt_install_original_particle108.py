"""Install a compiled Particle108 candidate at its existing AssetRipper Shader48 identity.

All inputs and backups are private. This tool preserves the exported .meta and
Material PPtrs, and requires a successful isolated Unity Vulkan receipt tied to
the candidate digest before editing an exported project.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil

from scripts.b45_install_original_blur import _atomic_replace_bytes, check_safe_ancestors
from scripts.b49_shaderlab_pass_contract import pass_coverage
from scripts.gt_particle108_private_unity_project import KEYWORD
from scripts.restore_builtin_shaders import exported_shader_identity
from scripts.t3_original_particle108_dxbc_feasibility import select
from scripts.t3_original_renderer_shader_impact import load_original
from scripts.t3_smoke34_sameexport_shaderlab import original_private_smoke_target
from scripts.verify_export_lineage import identity, pointer
from scripts.w1_audit_export_material_shaders import ENGINE, GUID

SOURCE_PROOF = {
    "schema": "GT_ORIGINAL_PARTICLE108_UNITY_RESOURCE_BRIDGE_V2",
    "status": "SOURCE_NAMED_STAGE_LOCAL_PRIVATE_HLSL_RECOMPILED_8_OF_8",
    "source_original_particle_shader_108_uses_SHA_verified": True,
    "private_original_DXBC_sample_operand_pairs_verified": 10,
    "private_source_mapped_original_texture_parameter_links": 10,
    "private_source_mapped_original_sampler_parameter_links": 10,
    "private_original_named_constant_buffer_layouts": 24,
    "private_original_named_constant_buffer_reflected_offsets": 68,
    "private_vulkan11_recompiled_stage_branches": 8,
}
UNITY_PROOF = {
    "status": "ORIGINAL_PRIVATE_PARTICLE108_ANDROID_VULKAN_SHADER_BUNDLE_COMPILED",
    "unityVersion": "2021.3.45f2",
    "sourceKeywordCombinations": 4,
    "registeredKeywordVariants": 4,
    "materialPassCount": 1,
    "shaderErrorCount": 0,
    "importedPrivateOriginalShader": True,
    "androidVulkanOnly": True,
    "privateAndroidShaderBundleBuilt": True,
    "unityEditorShaderImportAndCompilationProven": True,
    "gamePlayerBuilt": False,
}
SMOKE_SOURCE_PROOF = {
    "status": "SOURCE_NAMED_SMOKE34_TWO_ROUTES_VULKAN_COMPILED",
    "source_original_smoke_named_particle_renderer_slots": 34,
    "source_original_keyword_variants": 2,
    "private_named_Vulkan_stages_compiled": 4,
    "private_original_DXBC_sample_pairs_verified": 5,
    "private_original_named_constant_buffers": 9,
    "private_original_named_constant_buffer_reflected_offsets": 32,
}
SMOKE_UNITY_PROOF = dict(UNITY_PROOF,
    status="ORIGINAL_PRIVATE_SMOKE34_ANDROID_VULKAN_SHADER_BUNDLE_COMPILED",
    sourceKeywordDimensions=1, sourceKeywordCombinations=2, registeredKeywordVariants=2)
CANDLE_SOURCE_PROOF = {
    "status": "SOURCE_NAMED_CANDLE16_TWO_ROUTES_VULKAN_COMPILED",
    "source_original_candle_named_particle_renderer_slots": 16,
    "source_original_keyword_variants": 2,
    "private_named_Vulkan_stages_compiled": 4,
    "private_original_DXBC_sample_pairs_verified": 3,
    "private_original_named_constant_buffers": 9,
    "private_original_named_constant_buffer_reflected_offsets": 20,
}
CANDLE_UNITY_PROOF = dict(SMOKE_UNITY_PROOF,
    status="ORIGINAL_PRIVATE_CANDLE16_ANDROID_VULKAN_SHADER_BUNDLE_COMPILED")
MAX_SHADER = 16 * 1024 * 1024


def read_bounded(path, limit):
    path = check_safe_ancestors(path)
    if not path.is_file() or not 0 < path.stat().st_size <= limit:
        raise ValueError("missing_or_oversized_private_particle108_input")
    return path.read_bytes()


def require_proof(report, expected):
    if type(report) is not dict or any(
        type(report.get(key)) is not type(value) or report[key] != value
        for key, value in expected.items()
    ):
        raise ValueError("incomplete_particle108_source_or_Unity_proof")


def candidate_bytes(candidate, source_report, unity_report, *, smoke34=False, candle16=False):
    data = read_bounded(candidate, MAX_SHADER)
    source = json.loads(read_bounded(source_report, 65536))
    unity = json.loads(read_bounded(unity_report, 65536))
    if smoke34 and candle16:
        raise ValueError("multiple_particle_shader_targets")
    if candle16:
        expected_source, expected_unity = CANDLE_SOURCE_PROOF, CANDLE_UNITY_PROOF
    elif smoke34:
        expected_source, expected_unity = SMOKE_SOURCE_PROOF, SMOKE_UNITY_PROOF
    else:
        expected_source, expected_unity = SOURCE_PROOF, UNITY_PROOF
    require_proof(source, expected_source)
    require_proof(unity, expected_unity)
    dimensions = 1 if smoke34 or candle16 else 2
    digest = hashlib.sha256(data).hexdigest()
    if source.get("candidate_shader_sha256") != digest or unity.get("candidateShaderSha256") != digest:
        raise ValueError("particle108_candidate_proof_digest_mismatch")
    if type(unity.get("privateBundleBytes")) is not int or unity["privateBundleBytes"] <= 0:
        raise ValueError("missing_particle108_Unity_bundle_evidence")
    text = data.decode("utf-8")
    coverage = pass_coverage(text)
    keywords = KEYWORD.findall(text)
    if (not exported_shader_identity(text)
            or "DummyShaderTextExporter" in text or "No subprograms found" in text
            or coverage["subshader_pass_counts"] != [1]
            or coverage["passes_with_complete_program"] != 1
            or coverage["pass_braces_balanced"] is not True
            or len(keywords) != dimensions or len(set(keywords)) != dimensions):
        raise ValueError("invalid_particle108_source_bound_shader_candidate")
    return data


def traced_shader(assets, trace, source_key):
    """Resolve a unique same-export source Shader48 pointer to its actual .meta."""
    if (type(trace) is not dict or trace.get("schema_version") != 1
            or type(trace.get("export_instance")) is not str
            or len(trace["export_instance"]) != 32
            or any(c not in "0123456789abcdef" for c in trace["export_instance"].lower())
            or type(trace.get("objects")) is not list
            or not 0 < len(trace["objects"]) <= 200000
            or any(type(row) is not dict for row in trace["objects"])):
        raise ValueError("invalid_private_particle108_W1_trace")
    shaders = [row for row in trace["objects"] if row.get("class_id") == 48]
    hits = [pointer(row["export"]) for row in shaders if identity(row["source"]) == source_key]
    if len(hits) != 1:
        raise ValueError("original_particle108_Shader48_trace_not_unique")
    file_id, guid, ref_type = hits[0]
    if (file_id != 4800000 or ref_type != "3" or guid in ENGINE
            or guid == "0" * 32 or sum(pointer(row["export"])[1] == guid for row in shaders) != 1):
        raise ValueError("invalid_or_aliased_original_particle108_Shader48_GUID")

    if not assets.is_dir() or assets.is_symlink():
        raise ValueError("missing_or_unsafe_exported_particle108_assets")
    files = list(assets.rglob("*"))
    if len(files) > 150000 or any(path.is_symlink() for path in files):
        raise ValueError("unsafe_exported_particle108_asset_tree")
    metas = [path for path in files if path.is_file() and path.suffix == ".meta"
             and guid in {x.lower() for x in GUID.findall(
                 read_bounded(path, 8 * 1024 * 1024).decode("utf-8-sig"))}]
    if len(metas) != 1 or not metas[0].name.endswith(".shader.meta"):
        raise ValueError("original_particle108_GUID_does_not_identify_one_exported_shader")
    meta = metas[0]
    return meta.with_suffix(""), meta


def stage(original, manifest, project, trace_file, candidate, source_report,
          unity_report, backup, *, apply=False, smoke34=False, candle16=False):
    project = check_safe_ancestors(project)
    backup = check_safe_ancestors(backup)
    if any(check_safe_ancestors(path).is_relative_to(project)
           for path in (candidate, source_report, unity_report, trace_file, backup)):
        raise ValueError("private_particle108_input_or_backup_inside_export")
    data = candidate_bytes(candidate, source_report, unity_report, smoke34=smoke34, candle16=candle16)
    trace = json.loads(read_bounded(trace_file, 40_000_000))
    if candle16:
        from scripts.gt_smoke34_source_bound_shader import original_candle_target

        source_key = original_candle_target(original, manifest)
        profile, renderer_slots = "CANDLE16", 16
    elif smoke34:
        source_key, _ = original_private_smoke_target(original, manifest)
        profile, renderer_slots = "SMOKE34", 34
    else:
        private = {}
        report = load_original(original, manifest, private_particle_slot_counts=private)
        source_key = select(private, report)
        profile, renderer_slots = "PARTICLE108", 108
    target, meta = traced_shader(project / "Assets", trace, source_key)
    status_prefix = "ORIGINAL_" + profile
    previous = read_bounded(target, MAX_SHADER)
    metadata = read_bounded(meta, 65536)
    old_shader = previous.decode("utf-8-sig")
    if exported_shader_identity(old_shader) != exported_shader_identity(data.decode("utf-8")):
        raise ValueError("source_particle108_shader_name_differs_from_traced_export")
    if previous == data:
        status = status_prefix + "_SOURCE_BOUND_SHADER_ALREADY_INSTALLED"
    elif "DummyShaderTextExporter" not in old_shader:
        raise ValueError("unexpected_non_dummy_particle108_exported_program")
    else:
        status = status_prefix + "_SOURCE_BOUND_SHADER_INSTALL_PREFLIGHT"
        if apply:
            backup.mkdir(mode=0o700)
            try:
                (backup / "original.shader").write_bytes(previous)
                (backup / "original.shader.meta").write_bytes(metadata)
                if ((backup / "original.shader").read_bytes() != previous
                        or (backup / "original.shader.meta").read_bytes() != metadata):
                    raise ValueError("particle108_export_backup_incomplete")
            except BaseException:
                shutil.rmtree(backup)
                raise
            if target.read_bytes() != previous or meta.read_bytes() != metadata:
                raise ValueError("particle108_export_changed_during_install")
            _atomic_replace_bytes(target, data, ".gt-particle108-")
            try:
                if target.read_bytes() != data or meta.read_bytes() != metadata:
                    raise ValueError("particle108_export_candidate_or_meta_drift")
            except (OSError, ValueError):
                _atomic_replace_bytes(target, previous, ".gt-particle108-rollback-")
                raise
            status = status_prefix + "_SOURCE_BOUND_SHADER_INSTALLED"
    return {
        "status": status,
        "source_original_particle_renderer_material_slots": renderer_slots,
        "source_to_export_unique_Shader48_GUID_verified": True,
        "exported_shader_meta_preserved": True,
        "isolated_Unity_Android_Vulkan_candidate_digest_verified": True,
        "native_Unity_scene_or_Android_pixels_proven": False,
        "private_source_names_Guids_or_bytes_published": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("original", "manifest", "project", "trace-file", "candidate",
                 "source-report", "unity-report", "backup"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    profile = parser.add_mutually_exclusive_group()
    profile.add_argument("--smoke34", action="store_true")
    profile.add_argument("--candle16", action="store_true")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    output = args.out
    del args.out
    if output is not None:
        output = check_safe_ancestors(output)
        if output.exists() or output.is_relative_to(check_safe_ancestors(args.project)):
            raise ValueError("unsafe_particle108_install_receipt_destination")
    try:
        result = stage(**vars(args))
    except (OSError, TypeError, ValueError, KeyError):
        result = {"status": "INCONCLUSIVE_PARTICLE108_EXPORT_INSTALL"}
    if output is not None:
        output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("GT_ORIGINAL_PARTICLE108_EXPORT_INSTALL " + json.dumps(result, sort_keys=True))
    return 2 if result["status"] == "INCONCLUSIVE_PARTICLE108_EXPORT_INSTALL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
