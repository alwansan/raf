"""T2 WATER-001: fail-closed original Foam texture-name ↔ translated image-name check.

Only reports aggregate literal identity and numeric-field presence after original
SHA/authentic 4-stage resource gates. Original registry symbols, programs, private
HLSL and shader source never leave process memory. Equality of names is NOT a
sampler-state, descriptor-to-Unity-material, or Android-pixel proof.
"""
import argparse
import json
from pathlib import Path

from scripts.b20_foam_cb_descriptor_lineage import reflect
from scripts.b25_foam_cb_namebridge import original_name_registry
from scripts.t2_foam_member_abi import STAGES, _physical, original_source_tree
from scripts.t2_foam_resource_abi import (
    ORIGINAL_TEXTURES_PER_STAGE, COMPILED_NUMERIC_RESOURCE_BINDINGS,
    audit as authenticated_resource_audit,
)

MAX_NAME = 256
MAX_NUMERIC = 65535


def original_texture_rows(program, registry, expected_count):
    """Resolve opaque source names privately; expose no original registry value."""
    if not isinstance(program, dict) or not isinstance(registry, dict):
        raise ValueError("Original Foam program/registry unavailable")
    common = program.get("m_CommonParameters")
    if not isinstance(common, dict):
        raise ValueError("Original Foam common texture table unavailable")
    rows = common.get("m_TextureParams")
    if not isinstance(rows, list) or len(rows) != expected_count:
        raise ValueError("Original Foam authenticated texture count drift")
    result = []
    used = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Invalid original texture descriptor")
        name_index = row.get("m_NameIndex")
        if type(name_index) is not int or name_index not in registry:
            raise ValueError("Original Foam texture name index unresolved")
        name = registry[name_index]
        if not isinstance(name, str) or not (0 < len(name) <= MAX_NAME):
            raise ValueError("Original Foam texture name unavailable")
        if name in used:
            raise ValueError("Original Foam texture symbols not unique within stage")
        used.add(name)
        present = {}
        for key in ("m_Index", "m_SamplerIndex", "m_Dim", "m_ArraySize"):
            if key in row:
                value = row[key]
                # Negative one is an unknown/disabled sampler index, not a
                # proven register or Unity texture unit.
                low = -1 if key == "m_SamplerIndex" else 0
                if type(value) is not int or not low <= value <= MAX_NUMERIC:
                    raise ValueError("Invalid original texture numeric shape")
                present[key] = True
            else:
                present[key] = False
        if "m_MultiSampled" in row and type(row["m_MultiSampled"]) is not bool:
            raise ValueError("Invalid original texture multisample shape")
        result.append({"_private_name": name, "_field_presence": present,
                       "_private_numeric_pair": (row.get("m_Index"), row.get("m_SamplerIndex")),
                       "_multisample_present": "m_MultiSampled" in row})
    return result


def translated_image_names(reflection, expected_count, expected_bindings):
    """Validate exact set/binding list before privately comparing image names."""
    if not isinstance(reflection, dict):
        raise ValueError("Translated Foam reflection unavailable")
    rows = reflection.get("separate_images", [])
    if not isinstance(rows, list) or len(rows) != expected_count:
        raise ValueError("Translated Foam authenticated image count drift")
    actual = []
    names = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Malformed translated texture reflection")
        ds, binding, name = row.get("set"), row.get("binding"), row.get("name")
        if (type(ds) is not int or type(binding) is not int or
                not (0 <= ds <= 255 and 0 <= binding <= 255) or
                not isinstance(name, str) or not (0 < len(name) <= MAX_NAME)):
            raise ValueError("Translated texture descriptor/name unavailable")
        actual.append(("separate_images", ds, binding))
        names.append(name)
    if len(set(names)) != len(names):
        raise ValueError("Ambiguous translated image name")
    if tuple(sorted(actual)) != tuple(sorted(
            x for x in expected_bindings if x[0] == "separate_images")):
        raise ValueError("Translated texture binding changed")
    return names


def compare_private_names(original_rows, reflected_names):
    """Literal comparison only; NEVER emit original/reflection private symbols."""
    if not isinstance(original_rows, list) or not isinstance(reflected_names, list):
        raise ValueError("Invalid original/translated texture symbols")
    if len(original_rows) != len(reflected_names):
        raise ValueError("Texture identity cardinality mismatch")
    # Validate untrusted report shapes before dereferencing private fields.
    # A malformed row must fail closed without exposing a private source symbol.
    for row in original_rows:
        if not isinstance(row, dict) or set(row) != {
                "_private_name", "_field_presence", "_private_numeric_pair",
                "_multisample_present"}:
            raise ValueError("Malformed original texture identity row")
        if (not isinstance(row["_private_name"], str)
                or not 0 < len(row["_private_name"]) <= MAX_NAME
                or type(row["_multisample_present"]) is not bool):
            raise ValueError("Malformed original texture identity value")
        presence = row["_field_presence"]
        if (not isinstance(presence, dict)
                or set(presence) != {"m_Index", "m_SamplerIndex", "m_Dim", "m_ArraySize"}
                or any(type(value) is not bool for value in presence.values())):
            raise ValueError("Malformed original texture field presence")
        pair = row["_private_numeric_pair"]
        if (not isinstance(pair, tuple) or len(pair) != 2):
            raise ValueError("Malformed original texture numeric pair")
        for key, value in zip(("m_Index", "m_SamplerIndex"), pair):
            present = presence[key]
            low = -1 if key == "m_SamplerIndex" else 0
            if (present and (type(value) is not int or not low <= value <= MAX_NUMERIC)):
                raise ValueError("Original texture numeric pair outside descriptor domain")
            if not present and value is not None:
                raise ValueError("Original texture numeric pair contradicts field presence")
    if any(not isinstance(name, str) or not 0 < len(name) <= MAX_NAME
           for name in reflected_names):
        raise ValueError("Malformed translated image identity")
    source_names = [x["_private_name"] for x in original_rows]
    if len(source_names) != len(set(source_names)) or len(reflected_names) != len(set(reflected_names)):
        raise ValueError("Texture symbol identity ambiguous")
    reflected_set = set(reflected_names)
    matches = sum(name in reflected_set for name in source_names)
    numeric_pairs = [x["_private_numeric_pair"] for x in original_rows]
    # A repeated original pair is ambiguous, not evidence of a translated alias.
    # Only aggregate cardinalities leave private scratch. A public digest of
    # low-domain original indices is enumerable and MUST NOT be emitted.
    # m_SamplerIndex == -1 is explicitly unknown/disabled, not a proven pair.
    complete_pairs = [p for p in numeric_pairs if (type(p[0]) is int and type(p[1]) is int and p[1] >= 0)]
    presence = {
        k: sum(bool(x["_field_presence"][k]) for x in original_rows)
        for k in ("m_Index", "m_SamplerIndex", "m_Dim", "m_ArraySize")
    }
    return {
        "source_texture_count": len(original_rows),
        "original_complete_numeric_pairs": len(complete_pairs),
        "original_distinct_numeric_pairs": len(set(complete_pairs)),
        "numeric_pair_identity_to_spirv_verified": False,
        "translated_image_count": len(reflected_names),
        "literal_original_to_spirv_image_name_matches": matches,
        "original_numeric_field_presence_counts": presence,
        "original_multisampled_field_present_count": sum(
            x["_multisample_present"] for x in original_rows),
        "literal_name_equality_is_shaderlab_upload_proof": False,
        "original_texture_index_unit_or_sampler_state_verified": False,
        "private_source_names_disclosed": False,
    }


def audit(source, packet, manifest):
    source, packet, manifest = map(
        lambda path: Path(path).absolute(), (source, packet, manifest))
    if (not source.is_dir() or not packet.is_dir() or not manifest.is_file()
            or not all(_physical(p) for p in (source, packet, manifest))):
        raise ValueError("Private Foam original/packet paths unavailable")
    previous = authenticated_resource_audit(source, packet, manifest)
    if (previous.get("authenticated_original_texture_rows") != 6
            or previous.get("authenticated_translated_sampled_images") != 6
            or previous.get("authenticated_translated_separate_samplers") != 6
            or not previous.get("original_to_compiled_resource_cardinality_verified")):
        raise ValueError("Authenticated original Foam texture ABI prerequisite absent")
    original = original_source_tree(source)
    passes = original["m_SubShaders"][0]["m_Passes"]
    output = []
    for pi, stage in STAGES:
        p = passes[pi]
        names = original_name_registry(p["m_NameIndices"])
        prog = p["progVertex" if stage == 1 else "progFragment"]
        expected = ORIGINAL_TEXTURES_PER_STAGE[(pi, stage)]
        source_rows = original_texture_rows(prog, names, expected)
        reflection = reflect(packet / ("pass%d-stage%d" % (pi, stage)) / "original.spv")
        image_names = translated_image_names(
            reflection, expected, COMPILED_NUMERIC_RESOURCE_BINDINGS[(pi, stage)])
        safe = compare_private_names(source_rows, image_names)
        output.append({"pass": pi, "stage_code": stage, **safe})
    if len(output) != 4 or sum(x["source_texture_count"] for x in output) != 6:
        raise ValueError("Original Foam texture identity stage coverage invalid")
    return {
        "status": "original_foam_private_texture_literal_identity_audited",
        "source_authentic_stages": 4,
        "source_texture_rows": 6,
        "translated_image_rows": 6,
        "literal_name_matches": sum(
            x["literal_original_to_spirv_image_name_matches"] for x in output),
        "rows": output,
        "source_to_shaderlab_material_binding_verified": False,
        "source_to_sampler_binding_verified": False,
        "original_sampler_state_verified": False,
        "shaderlab_import_verified": False,
        "device_pixels_verified": False,
        "private_shader_symbols_published": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for arg in ("source", "packet", "manifest", "out"):
        p.add_argument("--" + arg, required=True, type=Path)
    a = p.parse_args()
    try:
        out = a.out.absolute()
        if (out.exists() or not out.parent.is_dir() or not _physical(out)
                or out.is_relative_to(a.packet.absolute())
                or out.is_relative_to(a.source.absolute())):
            raise ValueError("Unsafe safe-report output")
        result = audit(a.source, a.packet, a.manifest)
        out.write_text(json.dumps(result, sort_keys=True) + "\n", encoding="utf-8")
        print("T2_FOAM_TEXTURE_IDENTITY " + json.dumps({
            "status": result["status"], "source_texture_rows": 6,
            "literal_name_matches": result["literal_name_matches"],
            "shaderlab_or_device_verified": False,
            "private_code_published": False}))
        return 0
    except BaseException as exc:
        # Never print private data, path or source symbol from exception message.
        print("T2_FOAM_TEXTURE_IDENTITY " + json.dumps({
            "status": "blocked", "exception_type": type(exc).__name__,
            "shaderlab_or_device_verified": False, "private_code_published": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
