"""T2: read-only, fail-closed original Foam Shader export GUID/Material pointer probe.

Runs on an *actual exported* Unity project when available. Only source-free
aggregate counts and booleans may be written/logged. Finding a valid exported
GUID is not independently authenticating the original Unity PPtr/GUID or
proving Unity runtime Shader.Find, material upload or Adreno pixels.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re

from scripts.b24_original_foam_stage_translation import TARGET
from scripts.b49_shaderlab_pass_contract import pass_coverage
from scripts.restore_builtin_shaders import exported_shader_identity
from scripts.w1_audit_export_material_shaders import HEADER, SHADER, ENGINE, pptr

MAX_ASSET_ENTRIES = 250_000
MAX_SHADER_BYTES = 8 * 1024 * 1024
MAX_META_BYTES = 64 * 1024
MAX_YAML_BYTES = 256 * 1024 * 1024
YAML_SUFFIXES = frozenset((".mat", ".asset", ".prefab", ".unity"))
META_GUID = re.compile(rb"(?m)^guid:[ \t]*([0-9a-fA-F]{32})[ \t]*\r?$")
RESERVED = frozenset((*ENGINE, "00000000000000000000000000000000"))


def _unlinked(path: Path) -> None:
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError("linked_foam_export_or_parent")


def _bounded_bytes(path: Path, max_bytes: int) -> bytes:
    if not path.is_file() or path.is_symlink():
        raise ValueError("missing_or_redirected_exported_input")
    size = path.stat().st_size
    if size < 0 or size > max_bytes:
        raise ValueError("oversized_exported_input")
    raw = path.read_bytes()
    if len(raw) != size:
        raise ValueError("concurrent_exported_input_mutation")
    return raw


def _meta_guid(meta: Path) -> str:
    raw = _bounded_bytes(meta, MAX_META_BYTES)
    identifiers = META_GUID.findall(raw.lstrip(b"\xef\xbb\xbf"))
    if len(identifiers) != 1:
        raise ValueError("missing_or_ambiguous_exported_meta_guid")
    guid = identifiers[0].decode("ascii").lower()
    if guid in RESERVED:
        raise ValueError("reserved_exported_meta_guid")
    return guid


def _material_target_counts(entries: list[Path], target_guid: str) -> dict[str, int]:
    counts: Counter = Counter()
    for path in entries:
        if path.suffix not in YAML_SUFFIXES or not path.is_file():
            continue
        raw = _bounded_bytes(path, MAX_YAML_BYTES)
        if not raw.lstrip(b"\xef\xbb\xbf").startswith(b"%YAML"):
            if path.suffix == ".mat":
                raise ValueError("non_YAML_exported_Material_file")
            continue
        try:
            body = raw.decode("utf-8-sig")
        except UnicodeError as exc:
            raise ValueError("invalid_YAML_encoding") from exc
        headers = list(HEADER.finditer(body))
        # A Unity .mat file must contain at least one serialized Material.
        # Without this guard a valid-YAML, wrong-class .mat is silently skipped
        # and the reported Foam GUID inventory appears complete.
        if path.suffix == ".mat" and not any(h.group(1) == "21" for h in headers):
            raise ValueError("exported_Material_file_missing_Material_document")
        for index, header in enumerate(headers):
            if header.group(1) != "21":
                continue
            counts["material_documents"] += 1
            end = headers[index + 1].start() if index + 1 < len(headers) else len(body)
            doc = body[header.end():end]
            refs = SHADER.findall(doc)
            if len(refs) != 1 or len(re.findall(r"(?m)^  m_Shader:", doc)) != 1:
                raise ValueError("ambiguous_exported_Material_shader_field")
            file_id, guid, ref_type = pptr(refs[0])
            if guid == target_guid:
                if file_id != 4800000 or ref_type != "3":
                    raise ValueError("Foam_Material_pointer_invalid_fileID_or_type")
                counts["foam_exported_guid_Material_documents"] += 1
            elif file_id == 0:
                counts["nonfoam_null_Material_documents"] += 1
            else:
                counts["nonfoam_other_Material_documents"] += 1
    if counts["material_documents"] != (
        counts["foam_exported_guid_Material_documents"]
        + counts["nonfoam_null_Material_documents"]
        + counts["nonfoam_other_Material_documents"]
    ):
        raise ValueError("nonconserving_export_Material_counts")
    return dict(counts)


def inspect_export(project: Path) -> dict:
    root = Path(project).absolute()
    _unlinked(root)
    assets = root / "Assets"
    if not assets.is_dir() or assets.is_symlink():
        raise ValueError("missing_original_Unity_export_Assets")
    entries = sorted(assets.rglob("*"))
    if len(entries) > MAX_ASSET_ENTRIES:
        raise ValueError("export_inventory_budget")
    for path in entries:
        if path.is_symlink():
            raise ValueError("symlink_exported_Asset")
    shader_targets = []
    seen_guids: dict[str, Path] = {}
    for path in entries:
        if not path.is_file() or path.suffix != ".meta":
            continue
        guid = _meta_guid(path)
        if guid in seen_guids:
            raise ValueError("duplicate_Assets_meta_guid")
        seen_guids[guid] = path
    for path in entries:
        if not path.is_file() or path.suffix != ".shader":
            continue
        source = _bounded_bytes(path, MAX_SHADER_BYTES)
        try:
            shader_text = source.decode("utf-8-sig")
        except UnicodeError as exc:
            raise ValueError("invalid_exported_ShaderLab_encoding") from exc
        if exported_shader_identity(shader_text) != TARGET:
            continue
        sidecar = Path(str(path) + ".meta")
        if sidecar not in entries:
            raise ValueError("Foam_export_target_meta_missing")
        target_guid = _meta_guid(sidecar)
        shader_targets.append((target_guid, shader_text))
    if len(shader_targets) != 1:
        raise ValueError("ambiguous_or_absent_original_Foam_export_target")
    target_guid, text = shader_targets[0]
    if target_guid not in seen_guids:
        raise ValueError("Foam_exported_guid_not_in_inventory")
    profile = pass_coverage(text)
    if not profile["pass_braces_balanced"]:
        raise ValueError("Foam_exported_ShaderLab_unbalanced")
    material_counts = _material_target_counts(entries, target_guid)
    return {
        "schema_version": 1,
        "status": "EXPORTED_FOAM_GUID_MATERIAL_STRUCTURAL_PROBE_ONLY",
        "exact_Foam_exported_ShaderLab_targets": 1,
        "exported_ShaderLab_original_Foam_name_identity_matched": True,
        "all_Assets_meta_guids_unique_and_wellformed": True,
        "exported_Foam_meta_guid_syntactically_valid": True,
        "exported_Foam_meta_guid_original_Unity_PPtr_proven": False,
        "foam_exported_pass_count": profile["pass_count"],
        "foam_exported_subshader_pass_counts": profile["subshader_pass_counts"],
        "foam_exported_all_subshaders_programmed": profile["all_subshaders_programmed"],
        "foam_exported_has_dummy_export_marker": (
            "//DummyShaderTextExporter" in text or "// No subprograms found" in text
        ),
        "material_documents": material_counts.get("material_documents", 0),
        "material_docs_referencing_exported_Foam_guid": material_counts.get(
            "foam_exported_guid_Material_documents", 0
        ),
        "material_docs_other_nonnull_Shader": material_counts.get(
            "nonfoam_other_Material_documents", 0
        ),
        "material_docs_null_Shader": material_counts.get(
            "nonfoam_null_Material_documents", 0
        ),
        "Foam_Material_links_at_runtime_verified": False,
        "unity_shader_import_compile_verified": False,
        "android_Foam_pixels_verified": False,
        "modified_exported_Assets": False,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--project", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args(argv)
    out = a.out.absolute()
    _unlinked(out)
    if out.exists() or out.is_relative_to(a.project.absolute()) or not out.parent.is_dir():
        raise ValueError("unsafe_Foam_aggregate_output_path")
    try:
        report = inspect_export(a.project)
    except BaseException as exc:
        report = {
            "schema_version": 1,
            "status": "BLOCKED",
            "error_type": type(exc).__name__,
            "exported_Foam_meta_guid_original_Unity_PPtr_proven": False,
            "unity_shader_import_compile_verified": False,
            "android_Foam_pixels_verified": False,
            "modified_exported_Assets": False,
        }
        code = 2
    else:
        code = 0
    out.write_text(json.dumps(report, sort_keys=True) + "\n", encoding="utf-8")
    print("T2_FOAM_EXPORT_GUID_MATERIAL_SAFE " + json.dumps(report, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
