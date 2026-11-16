"""Fail-closed authentic next18 Shader48 same-export installer; NO XAPK.

Requires original 82 SHA-authenticated ZIP2 owners, exact 4-Pass/33-pair/
8-orphan/58-program original topology, post-NEXT23 193/45 actual material
audit, serialized Unity Android Vulkan 33 VS/FS routes and the exact
source-owner/PathID to same-instance AssetRipper exported Shader GUID trace.
Only the exported Dummy .shader bytes may change; never its .meta or material
YAML. No runtime keyword parity or Android pixel claims.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from scripts.b45_install_original_blur import _atomic_replace_bytes, check_safe_ancestors
from scripts.gt_install_original_particle108 import MAX_SHADER, read_bounded, traced_shader
from scripts.gt_rank_all82_original_shader_names_after_nine import gather
from scripts.gt_translate_next_remaining_18_shader48 import choose_original_18_by_topology
from scripts.restore_builtin_shaders import exported_shader_identity

STATUS = "GT_EXACT_ORIGINAL_NEXT18_SAME_EXPORT_SHADER48_GUID_INSTALLED_NO_APK"
ROUTES = (8, 13, 8, 4)


def source_identity(original: Path, manifest: Path, quality: Path):
    q = json.loads(read_bounded(quality, 65536))
    c = q.get("counts", {})
    if (q.get("status") != "NATIVE_MATERIAL_SHADER_PROGRAM_AUDIT_ONLY"
            or c.get("material_documents") != 1536
            or c.get("material_docs_using_Unity_builtin_Shader") != 750
            or c.get("material_docs_using_local_custom_Shader") != 786
            or c.get("material_docs_using_dummy_Shader") != 193
            or c.get("material_docs_using_non_dummy_Shader") != 593
            or c.get("distinct_dummy_Shader_targets_referenced") != 45
            or c.get("material_docs_with_unknown_or_broken_Shader") != 0):
        raise ValueError("unverified_post15_real_193_dummy_45_guid_scope")
    original_data = original / "Raft_Data"
    names, owner_count = gather(original_data, manifest)
    if owner_count != 14 or len(names) != 165:
        raise ValueError("original_82_source_Shader48_population_drift")
    # Only one source Shader48 name digest serves 18 materials in post15, and
    # its unique source owner and 4/33/8/58 topology must still be proven.
    return choose_original_18_by_topology(
        original_data, manifest, names,
        q["dummy_shader_material_counts_by_name_digest"])


def verify_receipt(candidate: bytes, receipt: dict):
    required = {
        "candidate_sha256": sha256(candidate).hexdigest(),
        "compiled_program_table_verified": True,
        "vertex_and_fragment_entrypoints_verified": True,
        "vulkan_platform_only": True,
        "vertex_routes_by_pass": list(ROUTES),
        "fragment_routes_by_pass": list(ROUTES),
    }
    if type(receipt) is not dict or any(receipt.get(k) != v for k, v in required.items()):
        raise ValueError("unverified_next18_Unity_Vulkan_33route_serialized_bundle")


def install(project: Path, trace: dict, source_key: tuple, candidate: bytes,
            receipt: dict, backup: Path):
    project, backup = check_safe_ancestors(project), check_safe_ancestors(backup)
    if backup.is_relative_to(project) or backup.exists():
        raise ValueError("unsafe_next18_backup_location")
    verify_receipt(candidate, receipt)
    name = exported_shader_identity(candidate.decode("utf-8-sig"))
    if not name or b"DummyShaderTextExporter" in candidate:
        raise ValueError("untrusted_next18_authentic_ShaderLab")
    target, meta = traced_shader(project / "Assets", trace, source_key)
    original = read_bounded(target, MAX_SHADER)
    metadata = read_bounded(meta, 65536)
    if (exported_shader_identity(original.decode("utf-8-sig")) != name
            or b"DummyShaderTextExporter" not in original):
        raise ValueError("original_next18_same_export_Shader48_not_unique_dummy")
    backup.mkdir(mode=0o700)
    (backup / "original.shader").write_bytes(original)
    (backup / "original.shader.meta").write_bytes(metadata)
    if target.read_bytes() != original or meta.read_bytes() != metadata:
        raise ValueError("original_next18_export_target_changed_before_install")
    _atomic_replace_bytes(target, candidate, ".gt-next18-source-authentic-")
    try:
        if target.read_bytes() != candidate or meta.read_bytes() != metadata:
            raise ValueError("next18_original_exported_Shader_GUID_or_bytes_drift")
    except (OSError, ValueError):
        _atomic_replace_bytes(target, original, ".gt-next18-rollback-")
        raise
    return {
        "original_export_guid_preserved": True,
        "vulkan_routes_installed": sum(ROUTES),
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("original", "manifest", "quality", "project", "trace",
                 "candidate", "receipt", "backup", "out"):
        p.add_argument("--" + name, type=Path, required=True)
    args = p.parse_args(argv)
    project = check_safe_ancestors(args.project)
    if (args.out.exists() or args.out.is_symlink()
            or args.backup.exists() or args.backup.is_symlink()
            or args.backup.resolve().is_relative_to(project)
            or args.out.resolve().is_relative_to(project)
            or args.out.resolve().is_relative_to(args.original.resolve())
            or any(check_safe_ancestors(path).is_relative_to(project)
                   for path in (args.original, args.manifest, args.quality,
                                args.trace, args.candidate, args.receipt))):
        raise ValueError("unsafe_original_next18_export_or_source_path")
    source = source_identity(args.original, args.manifest, args.quality)
    candidate = read_bounded(args.candidate, MAX_SHADER)
    receipt = json.loads(read_bounded(args.receipt, 65536))
    verify_receipt(candidate, receipt)
    result = install(project, json.loads(read_bounded(args.trace, 40_000_000)),
                     source, candidate, receipt, args.backup)
    if (result.get("original_export_guid_preserved") is not True
            or result.get("vulkan_routes_installed") != 33):
        raise ValueError("original_next18_exact_GUID_33route_install_rejected")
    out = {
        "schema_version": 1,
        "status": STATUS,
        "original_source_82_owners_SHA_verified": True,
        "post15_actual_dummy_Material_population_verified": 193,
        "source_original_unrestored_Material_documents_selected": 18,
        "same_export_owner_PathID_to_original_Shader_GUID_checked": True,
        "original_export_Shader48_GUID_preserved": True,
        "original_4_pass_VS_FS_routes_installed": list(ROUTES),
        "Unity_Android_Vulkan_bundle_33_routes_verified": True,
        "original_Material_meta_and_YAML_modified": False,
        "source_original_names_GUIDs_PathIDs_or_program_bytes_published": False,
        "APK_OBB_XAPK_created": False,
        "Adreno_pixels_or_runtime_keyword_parity_verified": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("GT_NEXT18_SAME_EXPORT_ORIGINAL_GUID " + json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
