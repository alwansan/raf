"""T2 WATER-001: authenticated Foam member-layout evidence, never ShaderLab.

Compares bounded original Unity serialized *parameter indices* with numerical
SPIR-V reflected member offsets, without assuming Unity m_Index is a byte
offset, guessing an opaque CB name, or publishing original/private names.
B20 authentic four-stage packet and exact source object are mandatory inputs.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path

from scripts.b20_foam_cb_descriptor_lineage import (SOURCE_SLOTS, MAX_HLSL, LEXICAL, probe as b20_probe, reflect)
from scripts.b20_private_foam_packet import ORIGINAL_OBJECT_SHA256, _physical
from scripts.b24_original_foam_stage_translation import OBJECT_ID, OWNER, TARGET, validate_stage
from scripts.b25_foam_cb_namebridge import (inspect_parsed as b25_inspect, original_name_registry, IDENT)
from scripts.w1_stage_zip2_owners import PINS, fingerprint

STAGES = ((0, 1), (0, 0), (1, 1), (1, 0))
CBUFFER_DECL = re.compile(r'\bcbuffer\s+([A-Za-z_]\w*)\s*:\s*register\s*\(\s*b(\d+)(?:\s*,\s*space\d+)?\s*\)\s*\{')
SOURCE_MEMBER_MAX = 128
INDEX_MAX = 65535
ALLOWED_NUMERIC = ("m_Index", "m_ArraySize", "m_Type", "m_Dim", "m_RowCount")
EXPECTED_EXTENTS = {
    (0, 1, 0): (160, 96), (0, 1, 1): (176, 64),
    (0, 1, 2): (368, 336), (0, 0, 0): (160, 128),
    (1, 1, 0): (160, 160), (1, 1, 1): (176, 64),
    (1, 1, 2): (368, 336), (1, 0, 0): (160, 112),
}


def bounded_parameter(row, kind):
    """Keep only structural numbers, never m_NameIndex or private symbols."""
    if not isinstance(row, dict) or type(row.get("m_Index")) is not int:
        raise ValueError("Original CB parameter index schema unknown")
    numeric = {}
    for key in ALLOWED_NUMERIC:
        value = row.get(key)
        if value is not None:
            if type(value) is not int or value < 0 or value > INDEX_MAX:
                raise ValueError("Invalid original CB parameter numeric field")
            numeric[key[2:].lower()] = value
    if numeric["index"] > INDEX_MAX:
        raise ValueError("Original CB index out of range")
    return {"kind": kind, **numeric}


def original_members(buf):
    if not isinstance(buf, dict) or type(buf.get("m_Size")) is not int:
        raise ValueError("Original partial CB malformed")
    vectors, matrices = buf.get("m_VectorParams"), buf.get("m_MatrixParams")
    if (not isinstance(vectors, list) or not isinstance(matrices, list)
            or len(vectors) + len(matrices) > SOURCE_MEMBER_MAX):
        raise ValueError("Original CB members absent or unbounded")
    return {
        "partial_declared_bytes": buf["m_Size"],
        "vector_members": [bounded_parameter(x, "vector") for x in vectors],
        "matrix_members": [bounded_parameter(x, "matrix") for x in matrices],
    }


def source_rows(parsed):
    if not isinstance(parsed, dict) or parsed.get("m_Name") != TARGET:
        raise ValueError("Original Foam shader mismatch")
    # B25 authentic registry/bindings before reading structural member rows.
    attest = b25_inspect(parsed)
    if attest.get("matched_constant_buffer_bindings") != 8:
        raise ValueError("Original Foam register/name attestation absent")
    result = {}
    passes = parsed["m_SubShaders"][0]["m_Passes"]
    for pi, stage in STAGES:
        field = "progVertex" if stage == 1 else "progFragment"
        prog = passes[pi][field]
        validate_stage(prog, stage, {"original_pass": pi})
        buffers = prog["m_CommonParameters"]["m_ConstantBuffers"]
        names = original_name_registry(passes[pi]["m_NameIndices"])
        for slot in SOURCE_SLOTS[(pi, stage)]:
            member = original_members(buffers[slot])
            name_index = buffers[slot].get("m_NameIndex")
            if type(name_index) is not int or name_index not in names:
                raise ValueError("Original Foam private CB name registry drift")
            # Private names remain in process memory, never in JSON results.
            member["_private_original_name"] = names[name_index]
            result[(pi, stage, slot)] = member
    if set(result) != set(EXPECTED_EXTENTS):
        raise ValueError("Original Foam member slot set changed")
    return result


def reflected_members(reflection, slot):
    """Return numeric UBO member layout only. Never include names/types text."""
    if not isinstance(reflection, dict):
        raise ValueError("Malformed original translated reflection")
    ubos, types = reflection.get("ubos"), reflection.get("types")
    if not isinstance(ubos, list) or not isinstance(types, dict):
        raise ValueError("Translated UBO type tree unavailable")
    matches = [x for x in ubos if isinstance(x, dict)
               and x.get("set") == 0 and x.get("binding") == slot]
    if len(matches) != 1:
        raise ValueError("Missing/duplicate translated CB slot")
    u = matches[0]
    size = u.get("block_size")
    if type(size) is not int or not 0 <= size <= INDEX_MAX:
        raise ValueError("Invalid translated UBO extent")
    typ = types.get(u.get("type"))
    if not isinstance(typ, dict):
        raise ValueError("Translated UBO type reference missing")
    members = typ.get("members")
    if not isinstance(members, list) or len(members) > SOURCE_MEMBER_MAX:
        raise ValueError("Translated UBO member type schema absent/unbounded")
    offsets = []
    for member in members:
        if not isinstance(member, dict) or type(member.get("offset")) is not int:
            raise ValueError("Translated member offset unavailable")
        offset = member["offset"]
        if offset < 0 or offset >= max(1, size) or offset % 4:
            raise ValueError("Translated member byte offset malformed")
        offsets.append(offset)
    if len(offsets) != len(set(offsets)):
        raise ValueError("Overlapping reflected member starts")
    return {"reflected_block_bytes": size, "reflected_offsets_bytes": sorted(offsets),
            "reflected_member_count": len(offsets)}


def translated_private_cbuffer_names(hlsl):
    """Lexically resolve compiled HLSL b-registers to names, no public strings."""
    if not isinstance(hlsl, str) or not 0 < len(hlsl.encode("utf-8")) <= MAX_HLSL:
        raise ValueError("Unsafe private HLSL size")
    masked = LEXICAL.sub(lambda m: re.sub(r"[^\r\n]", " ", m.group()), hlsl)
    pairs = {}
    for match in CBUFFER_DECL.finditer(masked):
        slot = int(match.group(2))
        if slot > 31 or slot in pairs:
            raise ValueError("Ambiguous private HLSL cbuffer name binding")
        pairs[slot] = match.group(1)
    return pairs


def private_name_parity(original_name, hlsl_name, reflection, slot):
    """Verify literal symbol equality only, never authenticate upload/alias."""
    if not isinstance(original_name, str) or not original_name:
        raise ValueError("Original CB symbol absent")
    if not isinstance(hlsl_name, str) or not IDENT.fullmatch(hlsl_name):
        raise ValueError("Translated CB symbol malformed")
    ubos = reflection.get("ubos")
    if not isinstance(ubos, list):
        raise ValueError("Translated name reflection unavailable")
    matches = [x for x in ubos if isinstance(x, dict)
               and x.get("set") == 0 and x.get("binding") == slot]
    if len(matches) != 1:
        raise ValueError("Translated name register ambiguous")
    reflected_name = matches[0].get("name")
    if not isinstance(reflected_name, str):
        raise ValueError("Translated reflected name missing")
    return {
        "source_name_literal_hlsl_usable": bool(IDENT.fullmatch(original_name)),
        "source_name_equals_translated_hlsl": original_name == hlsl_name,
        "translated_hlsl_name_equals_spirv_name": hlsl_name == reflected_name,
        "source_name_equals_spirv_name": original_name == reflected_name,
        "unity_original_cb_upload_alias_verified": False,
    }


def compare(source, reflection, slot, key, name_parity=None):
    target = reflected_members(reflection, slot)
    expected_source, expected_reflected = EXPECTED_EXTENTS[key]
    if (source["partial_declared_bytes"] != expected_source
            or target["reflected_block_bytes"] != expected_reflected):
        raise ValueError("Foam original/translated bound extent pin drift")
    original_params = source["vector_members"] + source["matrix_members"]
    # Purely a diagnostic intersection: m_Index is NOT authenticated as byte
    # offset or linked to a reflected SPIR-V member identity.
    register16_candidates = {p["index"] * 16 for p in original_params}
    reflected_offsets = set(target["reflected_offsets_bytes"])
    return {
        "pass": key[0], "stage_code": key[1], "cb_slot": slot,
        "original_partial_declared_bytes": expected_source,
        "translated_reflected_block_bytes": expected_reflected,
        "original_vector_parameter_count": len(source["vector_members"]),
        "original_matrix_parameter_count": len(source["matrix_members"]),
        "translated_member_count": target["reflected_member_count"],
        "candidate_register16_offset_intersection_count":
            len(register16_candidates & reflected_offsets),
        "original_index_unit_verified": False,
        "source_to_translated_member_identity_verified": False,
        **(name_parity or {}),
    }


def original_source_tree(source):
    import UnityPy
    path = Path(source) / OWNER
    if (not _physical(path) or not path.is_file()
            or fingerprint(path) != PINS[OWNER]):
        raise ValueError("Original Foam owner byte SHA mismatch")
    env = UnityPy.load(str(path))
    matches = [x for x in env.file.objects.values()
               if x.type.name == "Shader" and int(x.path_id) == OBJECT_ID]
    if len(matches) != 1 or hashlib.sha256(matches[0].get_raw_data()).hexdigest() != ORIGINAL_OBJECT_SHA256:
        raise ValueError("Original Foam object SHA/path mismatch")
    return matches[0].read_typetree()["m_ParsedForm"]


def audit(source, packet, manifest):
    source, packet, manifest = map(lambda p: Path(p).absolute(), (source, packet, manifest))
    if (not source.is_dir() or not _physical(source)
            or not packet.is_dir() or not _physical(packet)
            or not manifest.is_file() or not _physical(manifest)):
        raise ValueError("Original private source/packet unsafe")
    previous = b20_probe(packet, manifest)
    if (previous.get("authenticated_original_foam_stage_count") != 4
            or not previous.get("all_hlsl_b_slots_numerically_coincide")
            or not previous.get("all_spirv_set0_bindings_numerically_coincide")):
        raise ValueError("B20 original stage CB register verification missing")
    original = source_rows(original_source_tree(source))
    results = []
    for pi, stage in STAGES:
        stage_dir = packet / ("pass%d-stage%d" % (pi, stage))
        raw_reflection = reflect(stage_dir / "original.spv")
        hlsl_path = stage_dir / "private.hlsl"
        if not _physical(hlsl_path) or not hlsl_path.is_file():
            raise ValueError("Private authenticated HLSL stage missing")
        private_hlsl_names = translated_private_cbuffer_names(hlsl_path.read_text(encoding="utf-8"))
        if set(private_hlsl_names) != set(SOURCE_SLOTS[(pi, stage)]):
            raise ValueError("Translated HLSL CB name/register coverage drift")
        for slot in SOURCE_SLOTS[(pi, stage)]:
            key = (pi, stage, slot)
            evidence = private_name_parity(original[key]["_private_original_name"],
                                           private_hlsl_names[slot], raw_reflection, slot)
            results.append(compare(original[key], raw_reflection, slot, key, evidence))
    if len(results) != 8:
        raise ValueError("Foam source member audit coverage incomplete")
    return {
        "status": "original_foam_member_index_and_translated_offset_observed",
        "authenticated_original_foam_stage_count": 4,
        "authenticated_numeric_cb_slot_links": 8,
        "audited_membership_links": len(results),
        "partial_vs_reflected_extent_equal": sum(
            x["original_partial_declared_bytes"] == x["translated_reflected_block_bytes"]
            for x in results),
        "rows": results,
        "source_name_matches_hlsl_count": sum(x["source_name_equals_translated_hlsl"] for x in results),
        "hlsl_name_matches_reflected_spirv_count": sum(x["translated_hlsl_name_equals_spirv_name"] for x in results),
        "source_name_is_literal_hlsl_count": sum(x["source_name_literal_hlsl_usable"] for x in results),
        "original_index_unit_verified": False,
        "source_to_translated_member_identity_verified": False,
        "opaque_cb0_alias_verified": False,
        "unity_constant_buffer_upload_verified": False,
        "shaderlab_installed": False,
        "android_pixels_verified": False,
        "private_source_published": False,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True, type=Path)
    p.add_argument("--packet", required=True, type=Path)
    p.add_argument("--manifest", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    try:
        out = a.out.absolute()
        if (out.exists() or not out.parent.is_dir() or not _physical(out)
                or out.is_relative_to(Path(a.packet).absolute())
                or out.is_relative_to(Path(a.source).absolute())):
            raise ValueError("Unsafe aggregate-only output")
        report = audit(a.source, a.packet, a.manifest)
        out.write_text(json.dumps(report, sort_keys=True) + "\n", encoding="utf-8")
        print("T2_FOAM_ABI " + json.dumps({
            "status": report["status"], "member_links": 8,
            "shaderlab_installed": False, "device_verified": False}))
        return 0
    except BaseException as exc:
        print("T2_FOAM_ABI " + json.dumps({
            "status": "blocked", "exception_type": type(exc).__name__,
            "private_source_published": False, "device_verified": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
