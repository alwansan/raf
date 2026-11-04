"""B38: compare original Material top-level draw/render flags with ONE traced export.

Read-only, original provider SHA authenticated. This complements separate
shader/keyword, color, scalar and texture checks; no raw Material information
is written to reports or console. Source/export comparisons require the exact
same exporter instance, not guessed GUIDs.
"""
import argparse
import json
from pathlib import Path
import re

from scripts.b44_verify_material_colors import (
    ALL_HEADER, MATERIAL_HEADER, GUID, ENGINE, FONT_COLLECTION,
    _source_id, _export_pointer,
)

FIELDS = ("m_CustomRenderQueue", "m_LightmapFlags",
          "m_EnableInstancingVariants", "m_DoubleSidedGI")
FLAGS = frozenset(("m_EnableInstancingVariants", "m_DoubleSidedGI"))


def normalize_state(value):
    """Reject omitted fields, booleans in integer fields and fake enum flags."""
    if not isinstance(value, dict) or any(f not in value for f in FIELDS):
        raise ValueError("Missing Material render-state field")
    result = {}
    for field in FIELDS:
        number = value[field]
        if field in FLAGS:
            if type(number) is bool:
                number = int(number)
            if type(number) is not int or number not in (0, 1):
                raise ValueError("Invalid Material Boolean render flag")
        elif type(number) is not int or not -(2**31) <= number < 2**31:
            raise ValueError("Invalid Material integer render state")
        result[field] = number
    return result


def original_states(source_root):
    import UnityPy
    from scripts.a12_probe_original_blur_passes import SHADER_OWNERS
    from scripts.w1_stage_zip2_owners import fingerprint

    root = Path(source_root)
    folder = root / "Raft_Data"
    if root.is_symlink() or folder.is_symlink() or not folder.is_dir():
        raise ValueError("Invalid authenticated original root")
    result = {}
    for name, expected in SHADER_OWNERS.items():
        path = folder / name
        if path.is_symlink() or not path.is_file() or fingerprint(path) != expected:
            raise ValueError("Original Material owner failed size/SHA check")
        for obj in UnityPy.load(str(path)).objects:
            if obj.type.name == "Material":
                key = (name, obj.path_id)
                if key in result:
                    raise ValueError("Duplicate original Material identity")
                result[key] = normalize_state(obj.read_typetree())
    if not result:
        raise ValueError("No authenticated original Materials")
    return result


def exported_states(project):
    import yaml

    class StrictSafeLoader(yaml.SafeLoader):
        def construct_mapping(self, node, deep=False):
            output = {}
            for key_node, value_node in node.value:
                key = self.construct_object(key_node, deep=deep)
                try:
                    duplicate = key in output
                except TypeError:
                    raise ValueError("Unhashable Material YAML mapping key") from None
                if duplicate:
                    raise ValueError("Duplicate Material YAML mapping key")
                output[key] = self.construct_object(value_node, deep=deep)
            return output

    root = Path(project) / "Assets"
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Unsafe or missing Unity Assets root")
    paths = sorted(root.rglob("*"))
    if any(p.is_symlink() for p in paths):
        raise ValueError("Symlink in actual exported Unity Assets")
    result = {}
    for path in paths:
        if not path.is_file() or path.suffix not in (".mat", ".asset", ".prefab", ".unity"):
            continue
        if path.stat().st_size > 256 * 1024 * 1024:
            raise ValueError("Oversized Material YAML candidate")
        with path.open("rb") as inp:
            if not inp.read(16).lstrip(b"\xef\xbb\xbf").startswith(b"%YAML"):
                continue
        text = path.read_text(encoding="utf-8-sig")
        headers = list(ALL_HEADER.finditer(text))
        if not any(MATERIAL_HEADER.fullmatch(h.group(0)) for h in headers):
            continue
        meta = Path(str(path) + ".meta")
        if meta.is_symlink() or not meta.is_file():
            raise ValueError("Missing or redirected Material metadata")
        guids = GUID.findall(meta.read_text(encoding="utf-8-sig"))
        if len(guids) != 1 or guids[0].lower() == "0" * 32:
            raise ValueError("Invalid Material metadata GUID")
        for index, header in enumerate(headers):
            m = MATERIAL_HEADER.fullmatch(header.group(0))
            if m is None:
                continue
            body = text[header.end():headers[index + 1].start()
                        if index + 1 < len(headers) else len(text)]
            try:
                doc = yaml.load(body, Loader=StrictSafeLoader)
            except (yaml.YAMLError, ValueError):
                raise ValueError("Malformed exported Material YAML") from None
            material = doc.get("Material") if isinstance(doc, dict) else None
            if not isinstance(material, dict):
                raise ValueError("Invalid actual Material document")
            key = (int(m.group(1)), guids[0].lower())
            if key in result:
                raise ValueError("Duplicate exported Material identity")
            result[key] = normalize_state(material)
    if not result:
        raise ValueError("No exported Material documents")
    return result


def compare(trace, source, actual):
    """Count value drift only after verifying complete same-instance correspondence."""
    if (not isinstance(trace, dict) or trace.get("schema_version") != 1
        or not isinstance(trace.get("export_instance"), str)
        or re.fullmatch(r"[0-9a-f]{32}", trace["export_instance"]) is None
        or not isinstance(trace.get("objects"), list)):
        raise ValueError("Missing authenticated same-instance export trace")
    assigned, covered = {}, set()
    engine_skips = font_skips = 0
    for row in trace["objects"]:
        if not isinstance(row, dict):
            raise ValueError("Malformed trace row")
        if row.get("class_id") != 21:
            continue
        src = _source_id(row["source"])
        if src not in source or src in covered:
            raise ValueError("Missing or duplicated original identity")
        covered.add(src)
        ref = row["export"]
        if not isinstance(ref, dict) or set(ref) != {"file_id", "guid", "type"}:
            raise ValueError("Bad trace pointer")
        if (isinstance(ref["guid"], str) and ref["guid"].lower() in ENGINE
            and ref["type"] == 0 and row.get("exportable") is False):
            engine_skips += 1
            continue
        if row.get("collection_type") == FONT_COLLECTION:
            font_skips += 1
            continue
        dst = _export_pointer(ref)
        if dst in assigned:
            raise ValueError("Two source Materials mapped to one export identity")
        assigned[dst] = src
    if covered != set(source) or not assigned or set(assigned) != set(actual):
        raise ValueError("Unproven original-to-export Material identity coverage")

    changed = dict.fromkeys(FIELDS, 0)
    material_mismatches = 0
    for dst, src in assigned.items():
        before, after = source[src], actual[dst]
        if set(before) != set(FIELDS) or set(after) != set(FIELDS):
            raise ValueError("Invalid canonical render-state field set")
        different = False
        for field in FIELDS:
            if before[field] != after[field]:
                changed[field] += 1
                different = True
        material_mismatches += int(different)
    return {
        "schema_version": 1,
        "source_materials_verified": len(source),
        "actual_exported_materials_compared": len(assigned),
        "engine_material_redirects_excluded": engine_skips,
        "font_importer_materials_excluded": font_skips,
        "queue_value_mismatches": changed["m_CustomRenderQueue"],
        "lightmap_flags_mismatches": changed["m_LightmapFlags"],
        "instancing_flags_mismatches": changed["m_EnableInstancingVariants"],
        "double_sided_gi_mismatches": changed["m_DoubleSidedGI"],
        "mismatched_materials": material_mismatches,
        "source_render_state_preserved": material_mismatches == 0,
        "shader_pixels_unity_or_device_verified": False,
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--source", type=Path, required=True,
                    help="SHA-verified ZIP2 material providers")
    ap.add_argument("--project", type=Path, required=True,
                    help="actual Unity project exported in same instance as trace")
    ap.add_argument("--private-export-trace", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)
    if args.out.resolve().is_relative_to(args.project.resolve()):
        raise SystemExit("Report must not be within actual Unity Assets project")
    result = compare(json.loads(args.private_export_trace.read_text(encoding="utf-8")),
                     original_states(args.source), exported_states(args.project))
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n",
                        encoding="utf-8")
    print("RAFT_B38_MATERIAL_RENDER_STATE " + json.dumps(result, sort_keys=True))
    return 0 if result["source_render_state_preserved"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
