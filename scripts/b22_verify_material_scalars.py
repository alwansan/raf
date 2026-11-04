"""B22: fail-closed same-export original Material scalar value verifier.

W2 counted original scalar slots, B44 checks color values; this independent
read-only verifier checks binary32 scalar VALUES using SHA-authenticated
original owners and a private exact-export identity trace. No proprietary
values, names or object identities appear in reports.
"""
import argparse
import json
import math
from pathlib import Path
import re
import struct

from scripts.b44_verify_material_colors import (
    ALL_HEADER, MATERIAL_HEADER, GUID, ENGINE, FONT_COLLECTION,
    _source_id, _export_pointer,
)


def _float_bits(value):
    if type(value) not in (int, float):
        raise ValueError("Invalid numeric Material scalar")
    try:
        n = float(value)
        if not math.isfinite(n):
            raise ValueError("Nonfinite Material scalar")
        return struct.unpack("<I", struct.pack("<f", n))[0]
    except (OverflowError, struct.error):
        raise ValueError("Out-of-range Material scalar") from None


def normalize(saved, *, exported=False):
    if not isinstance(saved, dict) or not {"m_Floats", "m_Ints"} <= set(saved):
        raise ValueError("Missing Material scalar SavedProperties")
    result = {}
    for field in ("m_Floats", "m_Ints"):
        if not isinstance(saved[field], list):
            raise ValueError("Invalid scalar container")
        values = {}
        for item in saved[field]:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                name, value = item
            elif isinstance(item, dict) and set(item) == {"m_First", "m_Second"}:
                name, value = item["m_First"], item["m_Second"]
            elif exported and isinstance(item, dict) and len(item) == 1:
                name, value = next(iter(item.items()))
            else:
                raise ValueError("Unrecognized scalar entry")
            if not isinstance(name, str) or not name or name in values:
                raise ValueError("Duplicate/invalid Material scalar name")
            if field == "m_Floats":
                values[name] = _float_bits(value)
            else:
                if type(value) is not int or not -(2**31) <= value < 2**31:
                    raise ValueError("Invalid Material int scalar")
                values[name] = value
        result[field] = values
    return result


def original_scalars(root):
    import UnityPy
    from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
    from scripts.w1_stage_zip2_owners import fingerprint
    folder = root / "Raft_Data"
    if root.is_symlink() or folder.is_symlink() or not folder.is_dir():
        raise ValueError("Invalid original source root")
    result = {}
    for name, expected in SHADER_OWNERS.items():
        path = folder / name
        if path.is_symlink() or not path.is_file() or fingerprint(path) != expected:
            raise ValueError("Original owner failed SHA/size verification")
        for obj in UnityPy.load(str(path)).objects:
            if obj.type.name == "Material":
                key = (name, obj.path_id)
                if key in result:
                    raise ValueError("Duplicate source Material")
                result[key] = normalize(obj.read_typetree().get("m_SavedProperties"))
    if not result:
        raise ValueError("No verified Material sources")
    return result


def exported_scalars(project):
    import yaml
    class StrictLoader(yaml.SafeLoader):
        def construct_mapping(self, node, deep=False):
            output = {}
            for k, v in node.value:
                key = self.construct_object(k, deep=deep)
                try:
                    duplicate = key in output
                except TypeError:
                    raise ValueError("Unhashable YAML key") from None
                if duplicate:
                    raise ValueError("Duplicate YAML key")
                output[key] = self.construct_object(v, deep=deep)
            return output

    assets = project / "Assets"
    if assets.is_symlink() or not assets.is_dir():
        raise ValueError("Invalid Unity Assets")
    paths = sorted(assets.rglob("*"))
    if any(path.is_symlink() for path in paths):
        raise ValueError("Symlink in Unity Assets")
    result = {}
    for path in paths:
        if not path.is_file() or path.suffix not in (".mat", ".asset", ".prefab", ".unity"):
            continue
        if path.stat().st_size > 256 * 1024 * 1024:
            raise ValueError("Oversized Material YAML")
        with path.open("rb") as stream:
            if not stream.read(16).lstrip(b"\xef\xbb\xbf").startswith(b"%YAML"):
                continue
        content = path.read_text(encoding="utf-8-sig")
        headers = list(ALL_HEADER.finditer(content))
        if not any(MATERIAL_HEADER.fullmatch(h.group(0)) for h in headers):
            continue
        meta = Path(str(path) + ".meta")
        if meta.is_symlink() or not meta.is_file():
            raise ValueError("Material metadata missing or unsafe")
        guids = GUID.findall(meta.read_text(encoding="utf-8-sig"))
        if len(guids) != 1 or guids[0].lower() == "0" * 32:
            raise ValueError("Invalid Material GUID")
        for i, header in enumerate(headers):
            match = MATERIAL_HEADER.fullmatch(header.group(0))
            if match is None:
                continue
            part = content[header.end():headers[i+1].start() if i+1 < len(headers) else len(content)]
            try:
                obj = yaml.load(part, Loader=StrictLoader)
            except (yaml.YAMLError, ValueError):
                raise ValueError("Malformed Material YAML") from None
            if not isinstance(obj, dict) or not isinstance(obj.get("Material"), dict):
                raise ValueError("Invalid Material document")
            key = (int(match.group(1)), guids[0].lower())
            if key in result:
                raise ValueError("Duplicate exported Material")
            result[key] = normalize(obj["Material"].get("m_SavedProperties"), exported=True)
    if not result:
        raise ValueError("No exported Material documents")
    return result


def compare(trace, original, actual):
    if (not isinstance(trace, dict) or trace.get("schema_version") != 1
        or not isinstance(trace.get("export_instance"), str)
        or re.fullmatch("[0-9a-f]{32}", trace["export_instance"]) is None
        or not isinstance(trace.get("objects"), list)):
        raise ValueError("Invalid same-export trace")
    expected, covered = {}, set()
    skipped_engine = skipped_font = 0
    for row in trace["objects"]:
        if not isinstance(row, dict):
            raise ValueError("Invalid export trace row")
        if row.get("class_id") != 21:
            continue
        src = _source_id(row["source"])
        if src not in original or src in covered:
            raise ValueError("Unknown or duplicate source identity")
        covered.add(src)
        ref = row["export"]
        if not isinstance(ref, dict) or set(ref) != {"file_id", "guid", "type"}:
            raise ValueError("Malformed export pointer")
        if (isinstance(ref["guid"], str) and ref["guid"].lower() in ENGINE
            and ref["type"] == 0 and row.get("exportable") is False):
            skipped_engine += 1
            continue
        if row.get("collection_type") == FONT_COLLECTION:
            skipped_font += 1
            continue
        dst = _export_pointer(ref)
        if dst in expected:
            raise ValueError("Duplicate actual Material pointer")
        expected[dst] = original[src]
    if covered != set(original) or not expected or set(expected) != set(actual):
        raise ValueError("Material identity coverage incomplete")

    changes = {"m_Floats": 0, "m_Ints": 0}
    compared = {"m_Floats": 0, "m_Ints": 0}
    missing = extra = mismatched = 0
    for identity, old in expected.items():
        new = actual[identity]
        if set(old) != {"m_Floats", "m_Ints"} or set(new) != {"m_Floats", "m_Ints"}:
            raise ValueError("Invalid scalar map")
        difference = False
        for field in ("m_Floats", "m_Ints"):
            before, after = old[field], new[field]
            if not isinstance(before, dict) or not isinstance(after, dict):
                raise ValueError("Invalid canonical scalar entries")
            absent, added = before.keys() - after.keys(), after.keys() - before.keys()
            missing += len(absent)
            extra += len(added)
            compared[field] += len(before.keys() & after.keys())
            delta = sum(before[k] != after[k] for k in before.keys() & after.keys())
            changes[field] += delta
            difference |= bool(absent or added or delta)
        mismatched += int(difference)
    return {
        "schema_version": 1,
        "original_materials_verified": len(original),
        "exported_materials_compared": len(expected),
        "engine_redirects_excluded": skipped_engine,
        "font_importer_materials_excluded": skipped_font,
        "float_slots_compared": compared["m_Floats"],
        "int_slots_compared": compared["m_Ints"],
        "missing_scalar_slots": missing,
        "extra_scalar_slots": extra,
        "changed_float32_values": changes["m_Floats"],
        "changed_int32_values": changes["m_Ints"],
        "mismatched_materials": mismatched,
        "scalar_values_preserved": mismatched == 0,
        "unity_gpu_or_device_verified": False,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--private-export-trace", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    if args.out.resolve().is_relative_to(args.project.resolve()):
        raise SystemExit("Refusing report inside original/export project")
    try:
        actual = exported_scalars(args.project)
        original = original_scalars(args.source)
        trace = json.loads(args.private_export_trace.read_text(encoding="utf-8"))
        result = compare(trace, original, actual)
    except (ValueError, TypeError, KeyError):
        raise SystemExit("B22 scalar guard refused unverified input") from None
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("RAFT_B22_SCALAR_PARITY " + json.dumps(result, sort_keys=True))
    if not result["scalar_values_preserved"]:
        raise SystemExit("Original Material scalar values changed during export")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
