#!/usr/bin/env python3
"""GT: install one SHA-original-derived private Spectrum ShaderLab in ONE exported identity.

Source authenticity is established by pinned ZIP2 stages and private generation
upstream. This installer independently checks the exact source proof/ShaderLab,
requires one pre-existing exported shader name and unique original .meta GUID,
keeps the .meta byte-for-byte, and makes a complete external rollback backup.
Never invent a GUID, create a competing Shader, publish private ShaderLab/keyword
text, or claim Unity/Adreno rendering parity from file replacement.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

from scripts.b09_spectrum_topology_contract import TARGET, PASSES
from scripts.b49_shaderlab_pass_contract import pass_coverage
from scripts.restore_builtin_shaders import (
    exported_shader_identity, _require_safe_asset_path,
)
from scripts.b45_install_original_blur import check_safe_ancestors, _atomic_replace_bytes

MAX_PRIVATE = 16 * 1024 * 1024
MAX_PROOF = 65536
KEY = re.compile(
    r"(?m)^[ \t]*#pragma multi_compile __ ([_A-Za-z][_A-Za-z0-9]{0,127})[ \t]*$"
)
SOURCE_PROOF = {
    "status": "PRIVATE_SPECTRUM_ORIGINAL_KEYWORD_INDEX4_SEVEN_PASS_ROUTED_SHADERLAB_CANDIDATE",
    "source_original_pass_count": 7,
    "source_original_keyword_index": 4,
    "source_original_keyword_variants_per_pass": 2,
    "source_program_variant_stage_references": 28,
    "source_original_keyword_index_name_authenticated": True,
    "source_original_VS_FS_pair_hashes_authenticated": True,
    "private_seven_program_keyword_pragmas": 7,
    "original_HLSL_register_bindings_unchanged": True,
    "original_shader_keyword_flags_pragma_scope_proven": False,
    "original_material_keyword_runtime_selection_parity_proven": False,
    "original_Material_sampler_CB0_RT_GUID_binding_proven": False,
    "original_game_ShaderLab_modified": False,
    "Unity_Android_2021_import_or_GPU_proven": False,
    "original_Adreno_pixel_parity_proven": False,
    "original_keyword_names_or_ShaderLab_published": False,
}


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _proof(candidate: Path, report: Path) -> bytes:
    if (candidate.is_symlink() or report.is_symlink()
            or not candidate.is_file() or not report.is_file()
            or not 0 < candidate.stat().st_size <= MAX_PRIVATE
            or not 0 < report.stat().st_size <= MAX_PROOF):
        raise ValueError("missing_or_unsafe_private_original_source")
    source = json.loads(report.read_text(encoding="utf-8"))
    if not isinstance(source, dict) or any(
        type(source.get(k)) is not type(v) or source[k] != v
        for k, v in SOURCE_PROOF.items()
    ):
        raise ValueError("original_Spectrum_source_keyword_evidence_incomplete")
    data = candidate.read_bytes()
    if len(data) > MAX_PRIVATE or data.startswith(b"\xef\xbb\xbf"):
        raise ValueError("unsafe_private_original_candidate_bytes")
    text = data.decode("utf-8")
    covers = pass_coverage(text)
    keyword_pragmas = KEY.findall(text)
    if (exported_shader_identity(text) != TARGET
            or not text.startswith('Shader "' + TARGET + '" {')
            or "DummyShaderTextExporter" in text
            or "No subprograms found" in text
            or covers["pass_count"] != PASSES
            or covers["subshader_pass_counts"] != [PASSES]
            or covers["passes_with_complete_program"] != PASSES
            or covers["all_subshaders_programmed"] is not True
            or covers["pass_braces_balanced"] is not True
            or text.count("HLSLPROGRAM") != PASSES
            or text.count("ENDHLSL") != PASSES
            or len(keyword_pragmas) != PASSES
            or len(set(keyword_pragmas)) != 1):
        raise ValueError("private_original_Spectrum_ShaderLab_not_seven_complete_passes")
    return data


def inspect(project: Path, candidate: Path, source_report: Path):
    project = check_safe_ancestors(Path(project))
    candidate = check_safe_ancestors(Path(candidate))
    source_report = check_safe_ancestors(Path(source_report))
    if candidate.is_relative_to(project) or source_report.is_relative_to(project):
        raise ValueError("original_candidate_or_proof_inside_reconstructed_project")
    content = _proof(candidate, source_report)
    assets = project / "Assets"
    _require_safe_asset_path(assets, assets)
    if not assets.is_dir() or assets.is_symlink():
        raise ValueError("original_exported_Assets_missing")
    target = None
    all_shaders = 0
    for path in assets.rglob("*.shader"):
        _require_safe_asset_path(assets, path)
        if not path.is_file() or path.is_symlink():
            raise ValueError("symlinked_or_invalid_original_shader_export")
        # AssetRipper source may have dummy programs. Exact *serialized name*
        # is the only safe replacement identity; no filename assumptions.
        data = path.read_bytes()
        if len(data) > MAX_PRIVATE:
            continue
        if exported_shader_identity(data.decode("utf-8-sig")) == TARGET:
            all_shaders += 1
            target = path
    if all_shaders != 1 or target is None:
        raise ValueError("expected_exactly_one_exported_original_Spectrum_identity")
    meta = Path(str(target) + ".meta")
    _require_safe_asset_path(assets, meta)
    if not meta.is_file() or meta.is_symlink():
        raise ValueError("original_Spectrum_meta_missing")
    original, original_meta = target.read_bytes(), meta.read_bytes()
    rows = [x for x in original_meta.splitlines() if x.startswith(b"guid:")]
    if len(rows) != 1 or not re.fullmatch(rb"guid:[ \t]*[0-9a-fA-F]{32}[ \t]*", rows[0]):
        raise ValueError("original_Spectrum_meta_guid_invalid")
    guid = rows[0].split(b":", 1)[1].strip().lower()
    for other in assets.rglob("*.meta"):
        _require_safe_asset_path(assets, other)
        if not other.is_file() or other.is_symlink():
            raise ValueError("unsafe_original_exported_meta")
        if other == meta:
            continue
        for line in other.read_bytes().splitlines():
            if line.startswith(b"guid:") and line.split(b":", 1)[1].strip().lower() == guid:
                raise ValueError("original_Spectrum_GUID_collision")
    return {
        "project": project, "assets": assets, "target": target, "meta": meta,
        "original": original, "original_meta": original_meta, "candidate": content,
    }


def stage(project: Path, candidate: Path, source_report: Path,
          backup: Path, *, apply: bool) -> dict:
    inspected = inspect(project, candidate, source_report)
    target = inspected["target"]
    meta = inspected["meta"]
    original = inspected["original"]
    metadata = inspected["original_meta"]
    source = inspected["candidate"]
    result = {
        "status": "SOURCE_AUTHENTIC_SPECTRUM_EXPORTED_GUID_REPLACEMENT_STAGED"
                  if apply else "SOURCE_AUTHENTIC_SPECTRUM_EXPORTED_IDENTITY_PREFLIGHT",
        "source_original_seven_passes": True,
        "source_keyword_two_variants_per_pass": True,
        "exported_exact_identity_matches": 1,
        "exported_original_meta_preserved": True,
        "exported_target_unique_GUID": True,
        "shader_source_sha256": _sha(source),
        "exported_preinstall_sha256": _sha(original),
        "exported_meta_sha256": _sha(metadata),
        "target_relative_path_sha256": _sha(str(target.relative_to(inspected["assets"])).encode()),
        "actual_Unity2021_compilation_verified": False,
        "original_runtime_material_texture_or_buffer_bindings_proven": False,
        "Adreno_water_pixels_proven": False,
        "private_original_shader_text_published": False,
        "original_GUID_invented_or_changed": False,
    }
    if not apply:
        return result
    backup = check_safe_ancestors(Path(backup))
    if (backup == inspected["project"] or backup.is_relative_to(inspected["project"])
            or backup.is_relative_to(inspected["assets"])
            or backup.exists()):
        raise ValueError("external_fresh_backup_required")
    backup.mkdir(parents=True)
    try:
        (backup / "original.shader").write_bytes(original)
        (backup / "original.shader.meta").write_bytes(metadata)
        if ((backup / "original.shader").read_bytes() != original
                or (backup / "original.shader.meta").read_bytes() != metadata):
            raise ValueError("original_Spectrum_external_backup_incomplete")
    except BaseException:
        shutil.rmtree(backup)
        raise
    try:
        _require_safe_asset_path(inspected["assets"], target)
        _require_safe_asset_path(inspected["assets"], meta)
        if target.read_bytes() != original or meta.read_bytes() != metadata:
            raise ValueError("original_Spectrum_exported_target_changed_during_staging")
        _atomic_replace_bytes(target, source, ".gt-spectrum-")
        if target.read_bytes() != source or meta.read_bytes() != metadata:
            raise ValueError("original_Spectrum_exported_target_or_meta_drift")
    except BaseException:
        if target.is_file() and not target.is_symlink():
            try:
                if meta.read_bytes() != metadata:
                    raise ValueError("original_Spectrum_meta_changed_during_failed_install")
                _atomic_replace_bytes(target, original, ".gt-spectrum-rollback-")
                if target.read_bytes() != original:
                    raise ValueError("original_Spectrum_rollback_not_verified")
            except BaseException as exc:
                raise RuntimeError("Spectrum_restore_failed_external_backup_retained") from exc
        raise
    result["original_export_backup_external_verified"] = True
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--private-shader", required=True, type=Path)
    parser.add_argument("--source-proof", required=True, type=Path)
    parser.add_argument("--backup", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--apply", action="store_true")
    a = parser.parse_args()
    try:
        if a.out.exists() or a.out.is_symlink() or a.out.is_relative_to(a.project):
            raise ValueError("unsafe_Spectrum_aggregate_report_output")
        result = stage(a.project, a.private_shader, a.source_proof,
                       a.backup, apply=a.apply)
        a.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
        print("GT_NATIVE_SPECTRUM_EXPORT_SAFE " + json.dumps(result, sort_keys=True))
    except BaseException as exc:
        print("GT_NATIVE_SPECTRUM_EXPORT_BLOCKED "
              + json.dumps({"error_class": type(exc).__name__,
                            "source_or_keyword_published": False,
                            "original_game_GUID_modified": False}))
        raise SystemExit(2) from None


if __name__ == "__main__":
    main()
