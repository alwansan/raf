"""Bounded SPIR-V UserSemantic *annotation* census; names stay private.

SPV_GOOGLE_hlsl_functionality1 / HlslSemanticGOOGLE metadata can provide an
explicit compiler-declared semantic label, not a proof of DXBC instruction
dataflow. OpName or coincident numeric Location are NEVER provenance.
Only allowlisted numeric aggregate counters leave evaluate(). No source names.
"""
from __future__ import annotations

import re
import struct
from scripts.t3_vf_spirv_component_coverage import _type_components

MAGIC = 0x07230203
EXTENSION = "SPV_GOOGLE_hlsl_functionality1"
OP_EXTENSION = 10
OP_NAME = 5
OP_VARIABLE = 59
OP_DECORATE = 71
OP_MEMBER_DECORATE = 72
OP_DECORATE_STRING_GOOGLE = 5632
OP_MEMBER_DECORATE_STRING_GOOGLE = 5633
DECORATION_LOCATION = 30
DECORATION_COMPONENT = 31
DECORATION_BUILTIN = 11
DECORATION_HLSL_SEMANTIC = 5635
STORAGE_INPUT = 1
MAX_WORDS = 1000000
_NAME_PATTERN = re.compile(r"[A-Za-z_][A-Za-z_0-9]{0,63}\Z")

FIELDS = (
    "original_dx_user_input_records",
    "original_dx_declared_lanes",
    "reflected_spirv_input_records",
    "reflected_spirv_declared_lanes",
    "spv_located_user_variables",
    "spv_semantic_decorated_input_variables",
    "spv_explicit_semantic_matches_original",
    "spv_explicit_semantic_unmatched_original",
    "source_semantics_without_explicit_spv_label",
    "register_location_same_number_candidates",
    "register_location_same_number_type_width_candidates",
    "spv_hlsl_semantic_extension_present",
    "spv_other_interface_decorated_semantic_ignored",
)
BOOLEAN_FIELDS = frozenset(("spv_hlsl_semantic_extension_present",))


def _string(words):
    if not words or len(words) > 65:
        raise ValueError("unbounded_private_SPIRV_literal_string")
    raw = struct.pack("<" + "I" * len(words), *words)
    marker = raw.find(b"\0")
    if marker < 0 or any(raw[marker + 1:]):
        raise ValueError("invalid_private_SPIRV_literal_terminator")
    try:
        value = raw[:marker].decode("ascii")
    except UnicodeError:
        raise ValueError("unsupported_private_SPIRV_literal_encoding") from None
    if len(value) > 64 or any(ord(x) < 32 or ord(x) == 127 for x in value):
        raise ValueError("unbounded_or_control_private_SPIRV_string")
    return value


def parse_private_spirv(blob):
    """Return PRIVATE per-variable Location/Component/semantic descriptors.

    This intentionally does not print/serialize the parsed private data.
    Rejects duplicate decorations, conflicting IDs and malformed modules.
    """
    if (type(blob) is not bytes or not 20 <= len(blob) <= 4 * MAX_WORDS or
        len(blob) % 4):
        raise ValueError("invalid_or_unbounded_private_SPIRV_module")
    word_count = len(blob) // 4
    words = struct.unpack("<" + "I" * word_count, blob)
    if (words[0] != MAGIC or not 0x00010000 <= words[1] <= 0x00010600
        or not 0 < words[3] <= MAX_WORDS or words[4] != 0):
        raise ValueError("unsupported_private_SPIRV_header")
    bound = words[3]
    position = 5
    variables, locations, components, builtins, semantics = {}, {}, {}, set(), {}
    extension = False
    while position < len(words):
        first = words[position]
        opcode, count = first & 0xffff, first >> 16
        if count < 1 or position + count > len(words):
            raise ValueError("malformed_private_SPIRV_opcode_width")
        item = words[position + 1:position + count]
        if opcode == OP_EXTENSION:
            extension |= _string(item) == EXTENSION
        elif opcode == OP_VARIABLE:
            if len(item) not in (3, 4):
                raise ValueError("invalid_private_SPIRV_variable")
            typ, result_id, storage = item[:3]
            if (not 0 < typ < bound or not 0 < result_id < bound or
                result_id in variables):
                raise ValueError("invalid_or_duplicate_private_SPIRV_variable_id")
            variables[result_id] = storage
        elif opcode == OP_DECORATE:
            if len(item) < 2 or not 0 < item[0] < bound:
                raise ValueError("invalid_private_SPIRV_decoration")
            target, decoration = item[:2]
            if decoration in (DECORATION_LOCATION, DECORATION_COMPONENT, DECORATION_BUILTIN):
                if len(item) != 3:
                    raise ValueError("invalid_private_SPIRV_interface_decoration")
                if decoration == DECORATION_LOCATION:
                    if target in locations:
                        raise ValueError("duplicate_private_SPIRV_location_decoration")
                    locations[target] = item[2]
                elif decoration == DECORATION_COMPONENT:
                    if target in components:
                        raise ValueError("duplicate_private_SPIRV_component_decoration")
                    components[target] = item[2]
                else:
                    builtins.add(target)
        elif opcode == OP_DECORATE_STRING_GOOGLE:
            if len(item) < 3 or not 0 < item[0] < bound:
                raise ValueError("invalid_private_SPIRV_string_decoration")
            target, kind = item[:2]
            if kind == DECORATION_HLSL_SEMANTIC:
                if target in semantics:
                    raise ValueError("duplicate_private_SPIRV_HlslSemantic")
                name = _string(item[2:])
                if not _NAME_PATTERN.fullmatch(name):
                    raise ValueError("unsafe_private_SPIRV_HlslSemantic")
                semantics[target] = name.upper()
        elif opcode in (OP_MEMBER_DECORATE_STRING_GOOGLE,):
            # Nested struct member mapping requires a different provenance
            # parser. Never silently claim this as an ordinary variable.
            raise ValueError("unsupported_private_SPIRV_member_semantic_decoration")
        position += count
    if semantics and not extension:
        raise ValueError("private_SPIRV_semantic_extension_not_declared")
    inputs = {}
    other_semantics = 0
    for ident, name in semantics.items():
        if ident not in variables or variables[ident] != STORAGE_INPUT:
            other_semantics += 1
    for ident, storage in variables.items():
        if storage != STORAGE_INPUT or ident not in locations or ident in builtins:
            continue
        loc, cmp = locations[ident], components.get(ident, 0)
        if not 0 <= loc <= 65535 or not 0 <= cmp <= 3:
            raise ValueError("invalid_private_SPIRV_input_location_component")
        if (loc, cmp) in inputs:
            raise ValueError("duplicate_private_SPIRV_located_user_input")
        inputs[(loc, cmp)] = semantics.get(ident)
    return {"inputs": inputs, "extension_present": extension,
            "other_semantics": other_semantics}


def classify_original_and_spirv(source_rows, reflected, data):
    """No mappings from OpName or Location integer equality are trusted."""
    if (type(source_rows) is not list or len(source_rows) > 256 or
        type(reflected) is not dict or set(reflected) !=
            {"inputs", "outputs", "resource_slots"} or
        type(reflected["inputs"]) is not list or len(reflected["inputs"]) > 256 or
        type(data) is not dict or set(data) !=
            {"inputs", "extension_present", "other_semantics"} or
        type(data["inputs"]) is not dict or
        type(data["extension_present"]) is not bool or
        type(data["other_semantics"]) is not int or
        not 0 <= data["other_semantics"] <= 256):
        raise ValueError("invalid_private_source_to_SPIRV_interface_shape")

    dx = {}
    register_lanes = 0
    for row in source_rows:
        if (type(row) is not dict or
            set(row) != {"semantic", "index", "system_value", "type",
                         "register", "mask", "used_mask", "stream"}):
            raise ValueError("malformed_private_original_DXBC_signature_row")
        if (any(type(row[k]) is not int for k in
                ("index", "system_value", "type", "register", "mask", "used_mask", "stream"))
            or type(row["semantic"]) is not str or
            not _NAME_PATTERN.fullmatch(row["semantic"]) or
            not 0 <= row["index"] <= 4095 or not 0 <= row["register"] <= 4095 or
            row["type"] not in (1, 2, 3) or
            not 1 <= row["mask"] <= 15 or
            not 0 <= row["used_mask"] <= 15 or
            row["used_mask"] & ~row["mask"]):
            raise ValueError("invalid_private_original_DXBC_signature_field")
        if row["system_value"]:
            continue
        key = (row["semantic"].upper(), row["index"])
        if key in dx:
            raise ValueError("duplicate_private_original_DXBC_semantic")
        dx[key] = row
        register_lanes += row["mask"].bit_count()
    if len(dx) > 256 or len(data["inputs"]) > 256:
        raise ValueError("unbounded_private_shader_interface")
    located = {}
    declared = 0
    for row in reflected["inputs"]:
        if (type(row) is not dict or set(row) != {"location", "type"} or
            type(row["location"]) is not int or
            not 0 <= row["location"] <= 65535 or
            row["location"] in located):
            raise ValueError("invalid_or_duplicate_private_reflected_input")
        vec = _type_components(row["type"])
        if vec is None:
            raise ValueError("unsupported_private_SPIRV_input_width")
        located[row["location"]] = vec
        declared += vec[1]
    if (len(data["inputs"]) != len(located) or
        {loc for loc, component in data["inputs"]} != set(located) or
        any(component != 0 for loc, component in data["inputs"])):
        raise ValueError("SPIRV_binary_input_location_disagrees_with_safe_reflection")
    # A DXBC string semantic is stored separately from the index in ISGN;
    # compiler extension may serialize it as NAME or NAME0. No guessed aliases.
    def labels(row):
        name, index = row["semantic"].upper(), row["index"]
        return {name + str(index)} | ({name} if index == 0 else set())
    allowed_label_to_key = {}
    for key, row in dx.items():
        for label in labels(row):
            if label in allowed_label_to_key and allowed_label_to_key[label] != key:
                raise ValueError("ambiguous_original_DXBC_semantic_label")
            allowed_label_to_key[label] = key
    matched = set()
    annotated = unmatched = numeric = typed_numeric = 0
    family_by_dx_type = {1: "uint", 2: "int", 3: "float"}
    for (loc, component), label in data["inputs"].items():
        if label is not None:
            annotated += 1
            original_key = allowed_label_to_key.get(label)
            if original_key is None or original_key in matched:
                unmatched += 1
            else:
                matched.add(original_key)
        for source in dx.values():
            if source["register"] != loc:
                continue
            numeric += 1
            vec = located[loc]
            if (vec[0] == family_by_dx_type[source["type"]] and
                vec[1] >= source["mask"].bit_length()):
                typed_numeric += 1
    return {
        "original_dx_user_input_records": len(dx),
        "original_dx_declared_lanes": register_lanes,
        "reflected_spirv_input_records": len(located),
        "reflected_spirv_declared_lanes": declared,
        "spv_located_user_variables": len(data["inputs"]),
        "spv_semantic_decorated_input_variables": annotated,
        "spv_explicit_semantic_matches_original": len(matched),
        "spv_explicit_semantic_unmatched_original": unmatched,
        "source_semantics_without_explicit_spv_label": len(dx) - len(matched),
        "register_location_same_number_candidates": numeric,
        "register_location_same_number_type_width_candidates": typed_numeric,
        "spv_hlsl_semantic_extension_present": int(data["extension_present"]),
        "spv_other_interface_decorated_semantic_ignored": data["other_semantics"],
    }
