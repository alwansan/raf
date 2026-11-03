"""Extract bounded numeric SPIR-V image declarations without shader identifiers.

The contract describes declared module types. It does NOT prove an actual Unity
RenderTexture format, memory layout, runtime kernel identity or GPU execution.
"""
import struct


def image_resource_contracts(data):
    """Tie image formats to decorated variables through the original type graph."""
    if not isinstance(data, bytes) or len(data) < 20 or len(data) % 4 or len(data) > 1024 * 1024:
        raise ValueError("Invalid SPIR-V module length")
    words = struct.unpack("<" + "I" * (len(data) // 4), data)
    if words[0] != 0x07230203 or words[4] != 0 or words[3] == 0:
        raise ValueError("Invalid SPIR-V header")
    types, images, sampled_images = {}, {}, {}
    pointers, variables, decorations = {}, {}, {}
    offset = 5
    while offset < len(words):
        header = words[offset]
        n, opcode = header >> 16, header & 65535
        if n < 1 or offset + n > len(words):
            raise ValueError("Invalid SPIR-V instruction boundary")
        args = words[offset + 1:offset + n]
        if opcode in (21, 22):  # OpTypeInt / OpTypeFloat
            if n != (4 if opcode == 21 else 3) or args[0] in types:
                raise ValueError("Invalid numeric type declaration")
            types[args[0]] = (
                ("sint" if args[2] else "uint", args[1]) if opcode == 21
                else ("float", args[1])
            )
        elif opcode == 25:  # OpTypeImage
            if n not in (9, 10) or args[0] in images:
                raise ValueError("Invalid image type declaration")
            images[args[0]] = (args[1], *args[2:8], args[8] if n == 10 else None)
        elif opcode == 27:  # OpTypeSampledImage
            if n != 3 or args[0] in sampled_images:
                raise ValueError("Invalid sampled image type")
            sampled_images[args[0]] = args[1]
        elif opcode == 32:  # OpTypePointer
            if n != 4 or args[0] in pointers:
                raise ValueError("Invalid pointer type")
            pointers[args[0]] = (args[1], args[2])
        elif opcode == 59:  # OpVariable
            if n not in (4, 5) or args[1] in variables:
                raise ValueError("Invalid variable declaration")
            variables[args[1]] = (args[0], args[2])
        elif opcode == 71 and n >= 3:  # OpDecorate
            target, kind = args[0:2]
            if kind in (33, 34):  # Binding / DescriptorSet
                if n != 4:
                    raise ValueError("Invalid descriptor decoration")
                d = decorations.setdefault(target, {})
                if kind in d:
                    raise ValueError("Repeated descriptor decoration")
                d[kind] = args[2]
        offset += n
    result = []
    for var_id, (pointer_id, storage_class) in variables.items():
        pointer = pointers.get(pointer_id)
        if pointer is None or pointer[0] != storage_class:
            raise ValueError("Image variable pointer/storage mismatch")
        type_id = sampled_images.get(pointer[1], pointer[1])
        if type_id not in images:
            continue  # Other descriptors are not images.
        if var_id not in decorations or 33 not in decorations[var_id]:
            raise ValueError("Image binding missing or not on variable")
        scalar_id, dim, depth, arrayed, multisampled, sampled, fmt, access = images[type_id]
        scalar = types.get(scalar_id)
        if scalar is None or scalar[1] not in (16, 32, 64):
            raise ValueError("Undeclared image component type")
        record = {
            "set": decorations[var_id].get(34),
            "binding": decorations[var_id][33],
            "scalar_kind": scalar[0],
            "scalar_bits": scalar[1],
            "dimension_enum": dim,
            "depth_enum": depth,
            "arrayed": arrayed,
            "multisampled": multisampled,
            "sampled_enum": sampled,
            "format_enum": fmt,
            "access_enum": access,
        }
        if any(value > 65535 for key, value in record.items()
               if key not in ("set", "scalar_kind", "access_enum")
               and type(value) is int):
            raise ValueError("Unbounded image declaration enum")
        result.append(record)
    result.sort(key=lambda d: (d["set"] is None, d["set"] or 0, d["binding"]))
    if len(result) > 128:
        raise ValueError("Too many declared image resources")
    pairs = [(x["set"], x["binding"]) for x in result]
    if len(set(pairs)) != len(pairs):
        raise ValueError("Ambiguous image resource binding")
    return {
        "typed_image_declarations": result,
        "count": len(result),
        "names_disclosed": False,
        "unity_format_proven": False,
        "gpu_execution_proven": False,
    }


def compare_image_contracts(original, converted):
    """Describe source/roundtrip declaration drift without names or shader bytes."""
    old = original["typed_image_declarations"]
    new = converted["typed_image_declarations"]

    def mapping(records):
        by_slot = {(r["set"], r["binding"]): r for r in records}
        if len(by_slot) != len(records):
            raise ValueError("Ambiguous typed-image resource slots")
        return by_slot

    a, b = mapping(old), mapping(new)
    fields = ("scalar_kind", "scalar_bits", "dimension_enum", "depth_enum",
              "arrayed", "multisampled", "sampled_enum", "format_enum", "access_enum")
    changed = []
    for slot in sorted(set(a) & set(b), key=lambda x: (x[0] is None, x[0] or 0, x[1])):
        differences = [
            {"field": field, "original": a[slot][field], "roundtrip": b[slot][field]}
            for field in fields if a[slot][field] != b[slot][field]
        ]
        if differences:
            changed.append({"set": slot[0], "binding": slot[1],
                            "differences": differences})
    return {
        "bound_image_slots_preserved": set(a) == set(b),
        "original_only_slots": len(set(a) - set(b)),
        "roundtrip_only_slots": len(set(b) - set(a)),
        "changed_numeric_image_declarations": changed,
        "full_type_declarations_preserved": old == new,
        "names_disclosed": False,
        "numeric_execution_proven": False,
    }
