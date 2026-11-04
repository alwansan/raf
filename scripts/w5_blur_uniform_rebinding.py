"""Private, sparse Unity CB reconstruction for the bounded original Blur stages.

Never log the returned source or plans. No fallback values are synthesized:
unmapped allocation lanes remain independent uniform fields, not zero padding.
This emits a candidate implementation, not proof of Unity uniform upload.
"""
import re

from scripts.blur_cb_lane_map import build as lane_map

IDENT = re.compile(r"[A-Za-z_]\w*\Z", re.ASCII)
BLOCK = re.compile(
    r"\bcbuffer\s+([A-Za-z_]\w*)\s*:\s*register\(b(\d+)\)\s*"
    r"\{\s*float4\s+(cb(\d+)_0_m0)\[(\d+)\]\s*:\s*packoffset\(c0\);\s*\};",
    re.ASCII,
)


def rebind(source, plan):
    """Retain descriptor registers and full original CB allocations/member offsets.

    Only float vectors and 4x4 matrices with static float4 register reads are
    currently supported. A matrix is stored column-major; HLSL row indexing is
    explicitly transposed to recover original DXBC register-column indexing.
    No matrix multiplication/order or arithmetic statements are rewritten.
    """
    buffers = plan["buffers"]
    slots, identifiers, models = {}, set(), {}
    for buffer in buffers:
        slot = buffer["slot"]
        if type(slot) is not int or not 0 <= slot < 16 or slot in slots:
            raise ValueError("Unsupported original CB slot")
        if buffer["partial"] is not True or buffer["allocation_bytes"] % 16:
            raise ValueError("Unsupported original CB allocation")
        if not 0 < buffer["allocation_bytes"] <= 65536:
            raise ValueError("Unbounded original CB allocation")
        # $Globals is the compiler-owned global uniform buffer, not a legal
        # HLSL identifier. Give only this exact ABI spelling a private label;
        # retain every actual uniform field identity and descriptor register.
        buffer_name = "__raft_w5_Globals" if buffer["name"] == "$Globals" else buffer["name"]
        for name in [buffer_name] + [m["name"] for m in buffer["members"]]:
            if not isinstance(name, str) or not IDENT.fullmatch(name) or name in identifiers:
                raise ValueError("Ambiguous original uniform identity")
            if name.startswith("__raft_w5_") and not (name == buffer_name == "__raft_w5_Globals" and buffer["name"] == "$Globals"):
                raise ValueError("Reserved candidate padding identity")
            identifiers.add(name)
        model = lane_map(buffer)
        for member in buffer["members"]:
            if member["kind"] == "matrix" and (
                member["serialized_dimension"] != 4 or member["serialized_index"] % 16
            ):
                raise ValueError("Unsupported original matrix layout")
            if member["kind"] == "vector" and (
                member["serialized_index"] % 16 // 4 + member["serialized_dimension"] > 4
            ):
                raise ValueError("Original vector crosses a register")
        slots[slot], models[slot] = buffer, model

    matches = list(BLOCK.finditer(source))
    if len(matches) != len(buffers) or len(re.findall(r"\bcbuffer\b", source)) != len(matches):
        raise ValueError("Unsupported translated CB declaration")
    arrays, replacements = {}, []
    seen_slots = set()
    hole_bytes = 0
    for match in matches:
        original_slot, count = int(match[4]), int(match[5])
        if original_slot not in slots or original_slot in seen_slots:
            raise ValueError("Missing or duplicate translated original slot")
        seen_slots.add(original_slot)
        buffer, model = slots[original_slot], models[original_slot]
        if not 0 < count * 16 <= buffer["allocation_bytes"]:
            raise ValueError("Translated CB span exceeds original allocation")
        buffer_name = "__raft_w5_Globals" if buffer["name"] == "$Globals" else buffer["name"]
        lines = [f'cbuffer {buffer_name} : register(b{match[2]})', "{"]
        for member in buffer["members"]:
            offset, dim = member["serialized_index"], member["serialized_dimension"]
            typename = "column_major float4x4" if member["kind"] == "matrix" else (
                "float" if dim == 1 else f"float{dim}"
            )
            component = "xyzw"[offset % 16 // 4]
            lines.append(f'    {typename} {member["name"]} : packoffset(c{offset // 16}.{component});')
        # Declare every hole, including original unused trailing allocation.
        # Do not shrink a partial buffer to the compiler's smaller used span.
        for index, member_lane in enumerate(model["lanes"]):
            if member_lane is None:
                name = f"__raft_w5_hole_{original_slot}_{index}"
                if re.search(r"\b" + re.escape(name) + r"\b", source):
                    raise ValueError("Candidate padding name already in source")
                lines.append(f'    float {name} : packoffset(c{index // 4}.{"xyzw"[index % 4]});')
        lines.append("};")
        hole_bytes += model["unmapped_bytes"]
        arrays[match[3]] = (original_slot, count)
        replacements.append((match.start(), match.end(), "\n".join(lines)))
    for start, end, value in reversed(replacements):
        source = source[:start] + value + source[end:]

    reads = 0
    for variable, (slot, count) in arrays.items():
        buffer, model = slots[slot], models[slot]
        pattern = re.compile(r"\b" + re.escape(variable) + r"\[([0-9]+)u?\]")

        def replace(match):
            nonlocal reads
            register = int(match[1])
            if not 0 <= register < count:
                raise ValueError("Translated CB read outside declared span")
            expressions = []
            for lane in range(register * 4, register * 4 + 4):
                mapped = model["lanes"][lane]
                if mapped is None:
                    expressions.append(f"__raft_w5_hole_{slot}_{lane}")
                    continue
                ordinal, component = mapped
                member = buffer["members"][ordinal]
                name = member["name"]
                if member["kind"] == "matrix":
                    expressions.append(f"transpose({name})[{component // 4}].{'xyzw'[component % 4]}")
                else:
                    expressions.append(name if member["serialized_dimension"] == 1 else
                                       name + "." + "xyzw"[component])
            reads += 1
            return "float4(" + ", ".join(expressions) + ")"

        source = pattern.sub(replace, source)
        if re.search(r"\b" + re.escape(variable) + r"\b", source):
            raise ValueError("Dynamic or unrecognized translated CB read")
    if not reads:
        raise ValueError("No translated original CB reads")
    return source, {
        "buffers_rebound": len(buffers),
        "members_rebound": sum(len(b["members"]) for b in buffers),
        "original_allocation_bytes": sum(b["allocation_bytes"] for b in buffers),
        "unmapped_bytes_preserved": hole_bytes,
        "static_register_reads_rebound": reads,
        "unity_uniform_upload_verified": False,
        "private_names_published": False,
    }
