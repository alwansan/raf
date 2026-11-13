"""Generate named HLSL CB candidates from the authenticated source layout."""
import re

from scripts.gt_original_921_cb_layout import BLOCK
from scripts.w1_rebind_depth_resources import IDENT
from scripts.w1_recover_graphics_programs import command


def declaration(member):
    name = member["name"]
    if not IDENT.fullmatch(name):
        raise ValueError("invalid_original_uniform_identifier")
    if member["matrix"]:
        type_name = "column_major float4x4"
    else:
        # Carry non-float data as raw bits; Unity upload semantics are unverified.
        type_name = {0: "float", 1: "uint"}[member["type"]]
        if member["columns"] > 1:
            type_name += str(member["columns"])
    array = f'[{member["array_size"]}]' if member["array_size"] else ""
    return f"{type_name} {name}{array}"


def rebind_constant_buffers(source, buffers):
    by_slot = {buffer["source_slot"]: buffer for buffer in buffers}
    for block in reversed(list(BLOCK.finditer(source))):
        binding, slot, count = map(int, block.groups())
        buffer = by_slot.pop(slot)
        lanes = buffer["original_named_lanes"]
        array = re.search(r"\b(cb\d+_0(?:_\d+)?_m0)\[", block[0])[1]
        stem = f"raft921_cb{slot}"
        cb_name = buffer["name"]
        if cb_name == "$Globals":
            cb_name = stem + "_Globals"
        if not IDENT.fullmatch(cb_name):
            raise ValueError("invalid_original_buffer_identifier")

        lines, structs = [], []
        widths = {}
        for member in buffer["members"]:
            offset = member["index"]
            lines.append(f'{declaration(member)} : packoffset(c{offset // 16}.{"xyzw"[offset % 16 // 4]});')
            widths[(member["name"],)] = member["columns"]
        for index, struct in enumerate(buffer["structs"]):
            type_name = f"{stem}_type{index}"
            fields = []
            for member in struct["members"]:
                fields.append((member["index"], declaration(member) + ";"))
                widths[(struct["name"], member["name"])] = member["columns"]
            start = struct["index"] // 4
            for lane in range(struct["size"] // 4):
                if lanes[start + lane] is None:
                    fields.append((lane * 4, f"float {stem}_pad{lane};"))
            structs.append("struct " + type_name + " {\n" +
                           "\n".join(field for _, field in sorted(fields)) + "\n};")
            suffix = f'[{struct["array_size"]}]' if struct["array_size"] else ""
            lines.append(f'{type_name} {struct["name"]}{suffix} : packoffset(c{start // 4});')

        def expression(index):
            lane = lanes[index]
            if lane is None:
                for struct in buffer["structs"]:
                    start = struct["index"] // 4
                    width = struct["size"] // 4
                    if start <= index < start + width * max(1, struct["array_size"]):
                        element, offset = divmod(index - start, width)
                        suffix = f"[{element}]" if struct["array_size"] else ""
                        return f'{struct["name"]}{suffix}.{stem}_pad{offset}'
                name = f"{stem}_pad{index}"
                lines.append(f'float {name} : packoffset(c{index // 4}.{"xyzw"[index % 4]});')
                return name
            path = lane["path"]
            value = path[0] + "".join(f"[{part}]" if isinstance(part, int) else "." + part
                                      for part in path[1:])
            if lane["matrix"]:
                value += f'[{lane["row"]}][{lane["column"]}]'
            elif widths[tuple(part for part in path if isinstance(part, str))] > 1:
                value += "." + "xyzw"[lane["row"]]
            return "asfloat(" + value + ")" if lane["type"] else value

        registers = ["float4(" + ", ".join(expression(reg * 4 + lane) for lane in range(4)) + ")"
                     for reg in range(count)]
        lookup = [f"float4 {stem}_read(uint index) {{", "switch (index) {"]
        lookup.extend(f"case {index}: return {value};" for index, value in enumerate(registers))
        # Out-of-range original DXBC constant-buffer loads return zero.
        lookup.extend(["default: return float4(0, 0, 0, 0);", "}", "}"])
        replacement = "\n".join([*structs, f"cbuffer {cb_name} : register(b{binding}) {{",
                                 *lines, "};", *lookup])
        tail = re.sub(r"\b" + re.escape(array) + r"\[([^\[\]]+)\]",
                      lambda match: f"{stem}_read({match[1]})", source[block.end():])
        if re.search(r"\b" + re.escape(array) + r"\b", tail):
            raise ValueError("unsupported_original_constant_buffer_access")
        source = source[:block.start()] + replacement + tail
    if by_slot:
        raise ValueError("unused_original_constant_buffer_layout")
    return source


def verify_named_constant_buffers(private, stage, buffers):
    candidate = private / "named-constant-buffers.hlsl"
    baseline = private / "resource-bound.hlsl"
    candidate.write_text(rebind_constant_buffers(baseline.read_text(encoding="utf-8"), buffers),
                         encoding="utf-8")
    binary = candidate.with_suffix(".spv")
    suffix = {0: "frag", 1: "vert"}[stage]
    if not command(["glslangValidator", "-V", "-D", "-S", suffix, "-e", "main",
                    "-o", str(binary), str(candidate)]):
        raise ValueError("named_constant_buffer_candidate_compile_failed")
    if not command(["spirv-val", "--target-env", "vulkan1.1", str(binary)]):
        raise ValueError("named_constant_buffer_candidate_spirv_invalid")
