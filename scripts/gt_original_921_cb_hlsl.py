"""Generate named HLSL CB candidates from the authenticated source layout."""
import json
import re
import subprocess

from scripts.gt_original_921_cb_layout import BLOCK, VERTEX_INFO
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
    used = {int(binding) for binding in re.findall(r"register\([bstu](\d+)\)", source)}
    helper_binding = max(used, default=-1) + 1
    source = VERTEX_INFO.sub(
        lambda match: match[0].replace("SPIRV_Cross_VertexInfo",
                                       f"SPIRV_Cross_VertexInfo : register(b{helper_binding})", 1),
        source,
    )
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
            lines.append((offset, f'{declaration(member)} : packoffset(c{offset // 16}.{"xyzw"[offset % 16 // 4]});'))
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
            lines.append((struct["index"], f'{type_name} {struct["name"]}{suffix} : packoffset(c{start // 4});'))

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
                lines.append((index * 4, f'float {name} : packoffset(c{index // 4}.{"xyzw"[index % 4]});'))
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
        # SPIR-V Block members must appear in increasing byte-offset order.
        # Original metadata can list higher offsets first; gap fields are
        # discovered later while rebuilding source reads. Preserve original
        # offsets and values; sort only the HLSL declaration order.
        ordered_lines = [line for _, line in sorted(lines, key=lambda item: item[0])]
        replacement = "\n".join([*structs, f"cbuffer {cb_name} : register(b{binding}) {{",
                                 *ordered_lines, "};", *lookup])
        tail = re.sub(r"\b" + re.escape(array) + r"\[([^\[\]]+)\]",
                      lambda match: f"{stem}_read({match[1]})", source[block.end():])
        if re.search(r"\b" + re.escape(array) + r"\b", tail):
            raise ValueError("unsupported_original_constant_buffer_access")
        source = source[:block.start()] + replacement + tail
    if by_slot:
        raise ValueError("unused_original_constant_buffer_layout")
    return source


def verify_named_constant_buffers(private, stage, buffers, *, original_hlsl_offsets=False):
    candidate = private / "named-constant-buffers.hlsl"
    baseline = private / "resource-bound.hlsl"
    candidate.write_text(rebind_constant_buffers(baseline.read_text(encoding="utf-8"), buffers),
                         encoding="utf-8")
    binary = candidate.with_suffix(".spv")
    suffix = {0: "frag", 1: "vert"}[stage]
    # HLSL's original explicit packoffset layout can differ from GLSL's
    # default block-packing policy. Only source-authenticated NEXT6 opts in.
    # Keep spirv-val Vulkan 1.1 and exact original offset reflection STRICT.
    compile_argv = ["glslangValidator", "-V", "-D"]
    if original_hlsl_offsets is True:
        compile_argv.append("--hlsl-offsets")
    elif original_hlsl_offsets is not False:
        raise ValueError("unverified_original_hlsl_offsets_opt_in")
    compile_argv.extend(["-S", suffix, "-e", "main",
                         "-o", str(binary), str(candidate)])
    if not command(compile_argv):
        raise ValueError("named_constant_buffer_candidate_compile_failed")
    # Keep raw Vulkan validator diagnostics PRIVATE to this temporary stage.
    # The public source report may expose only a broad numeric/category
    # classification, never original identifiers, CB names or SPIR-V bytes.
    try:
        check = subprocess.run(
            ["spirv-val", "--target-env", "vulkan1.1", str(binary)],
            capture_output=True, timeout=30, check=False)
    except subprocess.TimeoutExpired:
        raise ValueError("named_constant_buffer_candidate_spirv_invalid") from None
    if check.returncode:
        raw = (check.stderr + b"\\n" + check.stdout)[:65536]
        (private / "original-validator-raw-private.log").write_bytes(raw)
        raise ValueError("named_constant_buffer_candidate_spirv_invalid")


    reflected = subprocess.run(["spirv-cross", str(binary), "--reflect"],
                               capture_output=True, timeout=30, check=False)
    if reflected.returncode:
        raise ValueError("named_constant_buffer_reflection_failed")
    return verify_offsets(json.loads(reflected.stdout), buffers)


def verify_offsets(reflection, buffers):
    resources = reflection.get("ubos", [])
    slots = {(row["set"], row["binding"]): row for row in resources}
    if len(slots) != len(resources):
        raise ValueError("named_constant_buffer_descriptor_collision")
    types = reflection.get("types", {})

    def verify_members(original, reflected):
        members = {member["name"]: member for member in reflected}
        total = 0
        for item in original:
            member = members.get(item["name"])
            if member is None or member["offset"] != item["index"]:
                raise ValueError("named_constant_buffer_offset_mismatch")
            if item["array_size"] and member.get("array") != [item["array_size"]]:
                raise ValueError("named_constant_buffer_array_count_mismatch")
            if item.get("matrix") and member.get("matrix_stride") != 16:
                raise ValueError("named_constant_buffer_matrix_stride_mismatch")
            if "members" in item:
                if member.get("array_stride") != item["size"]:
                    raise ValueError("named_constant_buffer_struct_stride_mismatch")
                total += verify_members(item["members"], types[member["type"]]["members"])
            elif item["array_size"] and member.get("array_stride") != (64 if item["matrix"] else 16):
                raise ValueError("named_constant_buffer_array_stride_mismatch")
            total += 1
        return total

    total = 0
    for buffer in buffers:
        resource = slots.get((0, buffer["translated_binding"]))
        expected = buffer["name"]
        if expected == "$Globals":
            expected = f'raft921_cb{buffer["source_slot"]}_Globals'
        if resource is None or resource["name"] != expected:
            raise ValueError("named_constant_buffer_binding_mismatch")
        total += verify_members(buffer["members"] + buffer["structs"],
                                types[resource["type"]]["members"])
    return total
