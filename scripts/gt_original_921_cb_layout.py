"""Resolve translated 921-slot shader constant buffers against original records."""
import re

# SPIRV-Cross can append a numeric disambiguator to a type/member name.
# The leading cbN of the array member still identifies the original DXBC slot.
BLOCK = re.compile(
    r"\bcbuffer\s+[A-Za-z_]\w*\s*:\s*register\(b(\d+)\)\s*"
    r"\{\s*float4\s+cb(\d+)_0(?:_\d+)?_m0\[(\d+)\]\s*:\s*packoffset\(c0\);\s*\};",
    re.ASCII,
)
VERTEX_INFO = re.compile(
    r"\bcbuffer SPIRV_Cross_VertexInfo\s*\{\s*int SPIRV_Cross_BaseVertex;"
    r"\s*int SPIRV_Cross_BaseInstance;\s*\};"
)


def bind_constant_buffers(source, common, names, layout):
    def by_key(rows, key):
        result = {row[key]: row for row in rows}
        if len(result) != len(rows):
            raise ValueError("ambiguous_original_constant_buffer_metadata")
        return result

    shared_bindings = by_key(common["m_ConstantBufferBindings"], "m_Index")
    variant_bindings = by_key([r for r in layout["resources"] if r["kind"] == 1], "index")
    groups = by_key(layout["groups"], "name")
    shared_layouts = by_key(common["m_ConstantBuffers"], "m_NameIndex")
    name_indices = {name: index for index, name in names.items()}
    result = []
    seen = set()
    for match in BLOCK.finditer(source):
        descriptor, slot, registers = (int(match[i]) for i in (1, 2, 3))
        if slot in seen:
            raise ValueError("duplicate_original_constant_buffer_slot")
        seen.add(slot)
        variant_binding = variant_bindings.get(slot)
        shared_binding = shared_bindings.get(slot)
        if variant_binding is not None:
            name = variant_binding["name"]
            if shared_binding is not None and names[shared_binding["m_NameIndex"]] != name:
                raise ValueError("conflicting_original_constant_buffer_binding")
        elif shared_binding is not None:
            name = names[shared_binding["m_NameIndex"]]
        else:
            raise ValueError("unresolved_original_constant_buffer_slot")
        group = groups.get(name)
        if group is None or not 0 < registers * 16 <= group["used_size"]:
            raise ValueError("original_constant_buffer_layout_or_span_unresolved")
        shared_layout = shared_layouts.get(name_indices.get(name))
        members = list(group["members"])
        if shared_layout is not None:
            for field, matrix in (("m_VectorParams", False), ("m_MatrixParams", True)):
                members.extend({
                    "name": names[item["m_NameIndex"]], "index": item["m_Index"],
                    "type": item["m_Type"], "array_size": item["m_ArraySize"],
                    "rows": item["m_RowCount"] if matrix else 1,
                    "columns": 4 if matrix else item["m_Dim"], "matrix": matrix,
                } for item in shared_layout[field])
            if shared_layout["m_StructParams"]:
                raise ValueError("shared_original_struct_layout_not_decoded")
        by_key(members, "name")
        if any(member["index"] % 4 or not 0 <= member["index"] < group["used_size"]
               for member in [*members, *group["structs"]]):
            raise ValueError("original_constant_buffer_member_offset_outside_layout")
        if any(struct["index"] + struct["size"] * max(1, struct["array_size"]) > group["used_size"]
               for struct in group["structs"]):
            raise ValueError("original_constant_buffer_struct_outside_layout")
        result.append({
            "name": name, "source_slot": slot, "translated_binding": descriptor,
            "translated_register_span_bytes": registers * 16,
            "variant_size_bytes": group["used_size"], "members": members,
            "structs": group["structs"], "shared_layout_present": shared_layout is not None,
            "binding_from_variant": variant_binding is not None,
        })
    if len(result) != len(re.findall(r"\bcbuffer\b", VERTEX_INFO.sub("", source))):
        raise ValueError("unsupported_translated_constant_buffer_declaration")
    return result


def constant_buffer_lanes(buffer):
    """Map original byte offsets to named member components, preserving holes."""
    lanes = [None] * (buffer["variant_size_bytes"] // 4)

    def add(member, base, path, limit):
        rows, columns = member["rows"], member["columns"]
        matrix = member["matrix"]
        if (member["type"] not in (0, 1) or not 1 <= columns <= 4
                or (matrix and (rows != 4 or columns != 4))
                or (not matrix and rows != 1)):
            raise ValueError("unsupported_original_constant_buffer_member_shape")
        offset = base + member["index"]
        count = member["array_size"]
        if offset % (16 if matrix or count else 4):
            raise ValueError("misaligned_original_constant_buffer_member")
        stride = 16 * columns if matrix else 16
        for element in range(max(1, count)):
            start = offset + element * stride
            if not matrix and start % 16 + 4 * columns > 16:
                raise ValueError("original_constant_buffer_vector_crosses_register")
            name = path + ([element] if count else [])
            for column in range(columns if matrix else 1):
                for row in range(rows if matrix else columns):
                    at = start + column * 16 + row * 4
                    if not 0 <= at < limit or lanes[at // 4] is not None:
                        raise ValueError("original_constant_buffer_lane_conflict")
                    lanes[at // 4] = {
                        "path": name, "row": row, "column": column,
                        "type": member["type"], "matrix": matrix,
                    }

    for member in buffer["members"]:
        add(member, 0, [member["name"]], buffer["variant_size_bytes"])
    for struct in buffer["structs"]:
        for element in range(max(1, struct["array_size"])):
            start = struct["index"] + element * struct["size"]
            parent = [struct["name"]] + ([element] if struct["array_size"] else [])
            for member in struct["members"]:
                add(member, start, [*parent, member["name"]], start + struct["size"])
    return lanes
