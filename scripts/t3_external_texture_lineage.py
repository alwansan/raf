#!/usr/bin/env python3
"""T3: resolve SHA-pinned original Material external Texture dependencies.

This first-stage probe answers WHICH original ZIP2 provider files are required
to prove B05's 25 cross-owner texture targets. Original owner names are already
public in the immutable ZIP2 manifest; no private object IDs or property names
are written to a report. It does not claim actual export or Android parity.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path, PurePosixPath

from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
from scripts.b03_original_renderer_materials import (
    declared_provider_kind, manifest_provider_basename_counts,
)
from scripts.b05_verify_material_texenv_bindings import (
    B05_SMALL_OWNER_PINS, original_texenvs,
)

SOURCE_OWNER = "sharedassets6.assets"
EXPECTED_MATERIALS = 41
EXPECTED_SLOTS = 227
EXPECTED_EXTERNAL = 25


def dependencies(slots, external_paths, manifest_names, known_pins=None):
    """Resolve fileID via ORIGINAL dependency table; never by pathID alone."""
    if known_pins is None:
        known_pins = SHADER_OWNERS
    if not isinstance(slots, dict) or not isinstance(external_paths, list):
        raise ValueError("invalid_original_dependency_input")
    if len(external_paths) > 65535 or not external_paths:
        raise ValueError("unexpected_original_external_table_size")
    if not isinstance(manifest_names, Counter):
        raise ValueError("untrusted_manifest_name_index")
    found = Counter()
    external = 0
    total = 0
    for owner, materials in slots.items():
        if not isinstance(owner, tuple) or len(owner) != 2 or owner[0] != SOURCE_OWNER:
            raise ValueError("wrong_selected_original_material_owner")
        if not isinstance(materials, dict):
            raise ValueError("invalid_original_material_slot_map")
        total += len(materials)
        for value in materials.values():
            if not isinstance(value, tuple) or len(value) != 2:
                raise ValueError("invalid_normalized_original_slot")
            pointer, _uv = value
            if (not isinstance(pointer, tuple) or len(pointer) != 2
                or any(type(i) is not int or i < 0 for i in pointer)):
                raise ValueError("invalid_source_texture_pointer")
            file_id, path_id = pointer
            if not path_id:
                if file_id:
                    raise ValueError("null_external_texture_target")
                continue
            if not file_id:
                continue
            external += 1
            if file_id > len(external_paths):
                raise ValueError("original_fileid_outside_dependency_table")
            entry = external_paths[file_id - 1]
            kind = declared_provider_kind(entry, manifest_names)
            if kind != "provider_name_declared_in_zip2_manifest":
                raise ValueError("original_external_provider_not_uniquely_declared")
            name = PurePosixPath(entry.replace("\\", "/")).name
            if name == SOURCE_OWNER:
                raise ValueError("external_fileid_aliases_local_owner")
            if name in known_pins:
                found[name] += 1
            else:
                found["__not_yet_pinned__"] += 1
    if (len(slots) != EXPECTED_MATERIALS or total != EXPECTED_SLOTS
            or external != EXPECTED_EXTERNAL):
        raise ValueError("selected_source_counts_drift")
    return {
        "schema_version": 1,
        "scope": "authentic-original-only-external-Texture-owner-index",
        "original_materials": len(slots),
        "texenv_slots": total,
        "external_reference_slots": external,
        "required_sha_pinned_public_provider_names": {
            name: found[name] for name in sorted(found) if name != "__not_yet_pinned__"
        },
        "declared_but_not_pre_pinned": found["__not_yet_pinned__"],
        "external_texture_target_object_class_verified": False,
        "source_to_export_external_target_identity_verified": False,
        "runtime_or_phone_colors_verified": False,
    }


def inspect(source: Path, manifest: Path) -> dict:
    """Require genuine SHA-pinned owner bytes before inspecting dependencies."""
    import UnityPy
    from scripts.w1_stage_zip2_owners import fingerprint
    root = source / "Raft_Data"
    original = root / SOURCE_OWNER
    if (any(x.is_symlink() for x in (source, root, original, manifest))
        or not manifest.is_file() or not original.is_file()
        or fingerprint(original) != B05_SMALL_OWNER_PINS[SOURCE_OWNER]):
        raise ValueError("untrusted_original_material_provider")
    source_materials = original_texenvs(source, owner_names={SOURCE_OWNER})
    env = UnityPy.load(str(original))
    # The authentic serialized file records zero-based dependency table
    # entries; Material m_FileID is one-based into this table.
    paths = [x.path for x in env.file.externals]
    inventory = manifest_provider_basename_counts(manifest)
    return dependencies(source_materials, paths, inventory)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args(argv)
    if (a.out.exists() or a.out.is_symlink()
        or a.out.resolve().is_relative_to(a.source.resolve())):
        raise ValueError("unsafe_public_report_destination")
    report = inspect(a.source, a.manifest)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(report, sort_keys=True, indent=2)+"\n", encoding="utf8")
    print("RAFT_T3_AUTHENTIC_EXTERNAL_OWNER_DEPENDENCIES "+json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
