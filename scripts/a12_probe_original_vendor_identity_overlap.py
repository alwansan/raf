"""CPU-only original Unity Shader object / authenticated built-in identity intersection.

Strict scope: two SHA-pinned resource owners previously vetted by W1, not the
full AssetRipper export and not a Unity shader restoration. Never report original
names, raw shaders, GUIDs, or individual object identifiers.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

from scripts.restore_builtin_shaders import archive_sources, download
from scripts.verify_targeted_lfs_compute_sources import verify_sources
from scripts.w1_recover_graphics_programs import OWNERS

EXPECTED_OWNER_SHADER_OBJECTS = 105
EXPECTED_VENDOR_IDENTITIES = 198


def analyse_rows(rows, vendor):
    """Return counts and a whole-inventory digest; no private identities survive."""
    if not isinstance(vendor, dict) or not vendor or any(not isinstance(n, str) for n in vendor):
        raise ValueError("Missing authenticated built-in identity mapping")
    seen_objects = set()
    observed_names = Counter()
    count = Counter()
    material = []
    for row in rows:
        if len(row) != 4:
            raise ValueError("Invalid original shader identity tuple")
        owner, object_id, parsed, serialized = row
        if not isinstance(owner, str) or not owner or type(object_id) is not int:
            raise ValueError("Invalid original shader object reference")
        objkey = (owner, object_id)
        if objkey in seen_objects:
            raise ValueError("Duplicated original Shader object")
        seen_objects.add(objkey)
        for token in (parsed, serialized):
            if token is not None and not isinstance(token, str):
                raise ValueError("Non-textual original Shader identity")
        parsed, serialized = parsed or "", serialized or ""
        # Aggregate fingerprint intentionally binds names to their owner and
        # serialized object id without exposing a per-name or per-object hash.
        material.append((owner, object_id, parsed, serialized))
        count["original_shader_objects"] += 1
        if parsed and serialized and parsed != serialized:
            count["conflicting_serialized_names"] += 1
            continue
        name = parsed or serialized
        if not name:
            count["missing_serialized_names"] += 1
            continue
        count["usable_serialized_names"] += 1
        observed_names[name] += 1
        if name in vendor:
            count["exact_vendor_identity_objects"] += 1
            if parsed and serialized:
                count["exact_vendor_objects_with_both_names"] += 1
            elif serialized and not parsed:
                count["exact_vendor_objects_fallback_only"] += 1
        else:
            count["nonvendor_identity_objects"] += 1
    if not count["original_shader_objects"]:
        raise ValueError("Empty original Shader object inventory")
    digest = hashlib.sha256(
        json.dumps(sorted(material), sort_keys=True, ensure_ascii=True,
                   separators=(",", ":")).encode("ascii")
    ).hexdigest()
    return {
        "original_shader_objects": count["original_shader_objects"],
        "usable_serialized_names": count["usable_serialized_names"],
        "missing_serialized_names": count["missing_serialized_names"],
        "conflicting_serialized_names": count["conflicting_serialized_names"],
        "nonvendor_identity_objects": count["nonvendor_identity_objects"],
        "exact_vendor_identity_objects": count["exact_vendor_identity_objects"],
        "exact_vendor_objects_with_both_names": count["exact_vendor_objects_with_both_names"],
        "exact_vendor_objects_fallback_only": count["exact_vendor_objects_fallback_only"],
        "unique_usable_names": len(observed_names),
        "unique_exact_vendor_names": sum(name in vendor for name in observed_names),
        "repeated_identity_objects": sum(n - 1 for n in observed_names.values()),
        "whole_inventory_sha256": digest,
        "full_original_export_provenance_verified": False,
        "asset_ripper_140_shader_export_identity_verified": False,
        "recovered_original_shaderlab_programs_installed": False,
        "unity_or_device_execution": False,
        "ready_for_build": False,
    }


def authenticated_rows(root):
    """Read the same original two-owner inventory that W1 source-pinned.

    Guard the exact owner SHA/length before UnityPy sees any original bytes.
    Other serialized asset files are deliberately OUT OF SCOPE.
    """
    verify_sources(root, expected=OWNERS)
    import UnityPy

    rows = []
    for owner in sorted(OWNERS):
        env = UnityPy.load(str(root / owner))
        for obj in env.file.objects.values():
            if obj.type.name != "Shader":
                continue
            tree = obj.read_typetree()
            parsed = tree.get("m_ParsedForm", {})
            if parsed is None:
                parsed = {}
            if not isinstance(parsed, dict):
                raise ValueError("Original parsed shader metadata not a mapping")
            rows.append((owner, int(obj.path_id),
                         parsed.get("m_Name"), tree.get("m_Name")))
    if len(rows) != EXPECTED_OWNER_SHADER_OBJECTS:
        raise ValueError("Authenticated original two-owner Shader inventory count drift")
    return rows


def run(root, out):
    vendor, _files, _license = archive_sources(download())
    if len(vendor) != EXPECTED_VENDOR_IDENTITIES:
        raise ValueError("Authenticated Unity built-in identity count drift")
    rows = authenticated_rows(root)
    report = analyse_rows(rows, vendor)
    report.update({
        "vendor_archive_sha256_verified": True,
        "original_two_owner_sha_pins_verified": True,
        "original_two_owner_inventory_complete": True,
        "original_owner_count": len(OWNERS),
        "original_export_scope_complete": False,
        "unresolved_native_41624581951_zero_match": True,
    })
    safe = json.dumps(report, sort_keys=True)
    # Only numeric counts and a whole-inventory fingerprint leave this process.
    out.write_text(safe + "\n", encoding="utf-8")
    print("RAFT_A12_ORIGINAL_VENDOR_INTERSECTION " + safe)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    run(args.source, args.out)


if __name__ == "__main__":
    main()
