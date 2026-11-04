"""B05: small SHA-pinned original Raft Material texture/UV parser acceptance.

Consumes ONE verified original ZIP2 owner. No original names, PathIDs, texture
values, coordinates or raw bytes are written to output or workflow artifacts.
This is original-source parsing, NOT source->Unity-export fidelity or device proof.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from scripts.b05_verify_material_texenv_bindings import normalize_texenvs, B05_SMALL_OWNER_PINS
from scripts.w1_stage_zip2_owners import fingerprint

OWNER = "sharedassets6.assets"
OWNER_BYTES, OWNER_SHA256 = B05_SMALL_OWNER_PINS[OWNER]


def classify_original(material_records: list) -> dict:
    """Validate original nested shape with B05's actual production normalizer."""
    stats = Counter()
    for record in material_records:
        if not isinstance(record, dict) or "m_TexEnvs" not in record:
            raise ValueError("Original Material lacks authentic TexEnvs field")
        slots = normalize_texenvs(record["m_TexEnvs"], exported=False)
        stats["materials"] += 1
        stats["texenv_slots"] += len(slots)
        if not slots:
            stats["materials_without_slots"] += 1
        bound_in_material = 0
        for pointer, transform in slots.values():
            file_id, path_id = pointer
            if path_id == 0:
                stats["null_slots"] += 1
            elif file_id == 0:
                stats["bound_same_owner"] += 1
                bound_in_material += 1
            else:
                stats["bound_external_owner"] += 1
                bound_in_material += 1
            if transform is None:
                stats["uv_missing"] += 1
            else:
                if len(transform) != 4:
                    raise ValueError("Invalid normalized original UV width")
                stats["uv_complete"] += 1
        if bound_in_material:
            stats["materials_with_bound_texture"] += 1
    if stats["materials"] == 0:
        raise ValueError("No authentic original Material objects in selected owner")
    if stats["texenv_slots"] != sum(stats[key] for key in (
        "null_slots", "bound_same_owner", "bound_external_owner"
    )):
        raise AssertionError("TexEnv classification total mismatch")
    if stats["texenv_slots"] != stats["uv_missing"] + stats["uv_complete"]:
        raise AssertionError("TexEnv transform total mismatch")
    return {
        "schema_version": 1,
        "owner": OWNER,
        "owner_verified_bytes": OWNER_BYTES,
        "owner_verified_sha256": OWNER_SHA256,
        "materials": stats["materials"],
        "materials_without_slots": stats["materials_without_slots"],
        "materials_with_bound_texture": stats["materials_with_bound_texture"],
        "texenv_slots": stats["texenv_slots"],
        "null_slots": stats["null_slots"],
        "bound_same_owner": stats["bound_same_owner"],
        "bound_external_owner": stats["bound_external_owner"],
        "uv_complete": stats["uv_complete"],
        "uv_missing": stats["uv_missing"],
        "original_parse_verified": True,
        "same_instance_export_verified": False,
        "source_export_texenv_fidelity_verified": False,
        "original_source_modified": False,
        "unity_android_pixels_verified": False,
        "ready_for_build": False,
    }


def inspect(root: Path) -> dict:
    root = root.absolute()
    target = root / "Raft_Data" / OWNER
    if any(p.is_symlink() for p in (target, *target.parents)):
        raise ValueError("Refuse linked original provider")
    if not target.is_file() or fingerprint(target) != (OWNER_BYTES, OWNER_SHA256):
        raise ValueError("Authentic ZIP2 owner bytes/SHA256 changed")
    import UnityPy

    env = UnityPy.load(str(target))
    records = []
    for obj in env.objects:
        if obj.type.name != "Material":
            continue
        tree = obj.read_typetree()
        saved = tree.get("m_SavedProperties") if isinstance(tree, dict) else None
        if not isinstance(saved, dict):
            raise ValueError("Original Material saved properties missing")
        records.append(saved)
    return classify_original(records)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--original", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args(argv)
    try:
        root, out = args.original.resolve(), args.out.absolute()
        if out.is_relative_to(root) or out.is_symlink():
            raise ValueError("Report cannot overwrite source provider")
        result = inspect(root)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        print("B05_AUTHENTIC_ORIGINAL_TEXENV_SHAPES " + json.dumps(result, sort_keys=True))
        return 0
    except Exception as error:
        # A traceback may include original private Material string values.
        # Deliberately give a typed fail-closed reason without source content.
        print("B05_AUTHENTIC_ORIGINAL_TEXENV_SHAPES FAILED " + type(error).__name__)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
