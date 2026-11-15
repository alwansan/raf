"""Install a verified recovered model shader without changing Material references."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from scripts.b45_install_original_blur import _atomic_replace_bytes, check_safe_ancestors
from scripts.gt_install_original_particle108 import MAX_SHADER, read_bounded, traced_shader
from scripts.gt_original_921_shaderlab import expected_routes_for_shader
from scripts.restore_builtin_shaders import exported_shader_identity


def install(project, trace, source_key, candidate, receipt, backup):
    project = check_safe_ancestors(project)
    backup = check_safe_ancestors(backup)
    if backup.is_relative_to(project) or backup.exists():
        raise ValueError("invalid_model_shader_backup")
    digest = sha256(candidate).hexdigest()
    identity = exported_shader_identity(candidate.decode("utf-8"))
    if identity is None:
        raise ValueError("model_shader_identity_missing")
    counts = expected_routes_for_shader(identity)
    required = {
        "candidate_sha256": digest,
        "compiled_program_table_verified": True,
        "engine_keywords_verified": True,
        "vertex_and_fragment_entrypoints_verified": True,
        "vulkan_platform_only": True,
        "vertex_routes_by_pass": list(counts),
        "fragment_routes_by_pass": list(counts),
    }
    if any(receipt.get(key) != value for key, value in required.items()):
        raise ValueError("model_shader_bundle_evidence_missing")
    target, meta = traced_shader(project / "Assets", trace, source_key)
    previous = read_bounded(target, MAX_SHADER)
    metadata = read_bounded(meta, 65536)
    old_text = previous.decode("utf-8-sig")
    if exported_shader_identity(old_text) != identity:
        raise ValueError("model_shader_identity_mismatch")
    if previous != candidate:
        if "DummyShaderTextExporter" not in old_text:
            raise ValueError("model_shader_export_is_not_dummy")
        backup.mkdir(mode=0o700)
        (backup / "original.shader").write_bytes(previous)
        (backup / "original.shader.meta").write_bytes(metadata)
        if target.read_bytes() != previous or meta.read_bytes() != metadata:
            raise ValueError("model_shader_export_changed")
        _atomic_replace_bytes(target, candidate, ".gt-model-shader-")
        try:
            if target.read_bytes() != candidate or meta.read_bytes() != metadata:
                raise ValueError("model_shader_install_identity_drift")
        except (OSError, ValueError):
            _atomic_replace_bytes(target, previous, ".gt-model-shader-rollback-")
            raise
    return {"original_export_guid_preserved": True, "vulkan_routes_installed": sum(counts)}


def main():
    from scripts.gt_original_921_all_variants import (
        SOURCE_PROFILES, authenticated_shader_reader, select_scene_shader,
    )
    from scripts.t3_original_renderer_shader_impact import load_original
    from scripts.t3_original_top_shader_dxbc_feasibility import selected_high_use

    parser = argparse.ArgumentParser(description=__doc__)
    for key in ("original", "manifest", "project", "trace", "candidate", "receipt", "backup"):
        parser.add_argument("--" + key, type=Path, required=True)
    parser.add_argument("--shader", choices=SOURCE_PROFILES, required=True)
    args = parser.parse_args()
    project = check_safe_ancestors(args.project)
    if any(check_safe_ancestors(path).is_relative_to(project)
           for path in (args.original, args.manifest, args.trace, args.candidate, args.receipt)):
        raise ValueError("private_model_shader_inputs_inside_export")
    slots = {}
    source = load_original(args.original, args.manifest, private_slot_counts=slots)
    if args.shader == "blockpaint":
        source_key = selected_high_use(slots, source)
    else:
        source_key = select_scene_shader(
            slots, source, args.shader, get_tree=authenticated_shader_reader(args.original))
    result = install(project, json.loads(read_bounded(args.trace, 40_000_000)), source_key,
                     read_bounded(args.candidate, MAX_SHADER),
                     json.loads(read_bounded(args.receipt, 65536)), args.backup)
    print("GT_RESTORED_MODEL_SHADER " + json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
