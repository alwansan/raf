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


def prove_original_typed_padding_is_unread(source_tail, register_array, reserved_lanes):
    """Fail closed before omitting undefined typed-array padding.

    HLSL scalar/vector arrays use 16-byte element strides. Vulkan Block
    layout forbids new scalar fields inside those original reserved bytes.
    Substitute zero ONLY if every source read provably avoids anonymous
    array lanes; dynamic indexing with a potentially unsafe swizzle fails.
    """
    if not reserved_lanes:
        return 0
    pattern = re.compile(
        r"\b" + re.escape(register_array) +
        r"\[([^\[\]]+)\](?:\.([A-Za-z_]\w*))?")
    positions = set(reserved_lanes)
    seen = 0
    for access in pattern.finditer(source_tail):
        seen += 1
        swizzle = access.group(2)
        if not swizzle or len(swizzle) > 4 or any(ch not in "xyzw" for ch in swizzle):
            raise ValueError("original_array_padding_raw_read_not_proven")
        index = access.group(1).strip()
        for ch in swizzle:
            component = "xyzw".index(ch)
            if index.isascii() and index.isdecimal():
                if int(index) * 4 + component in positions:
                    raise ValueError("original_array_padding_raw_read_not_proven")
            elif any(lane % 4 == component for lane in positions):
                raise ValueError("original_array_padding_dynamic_read_not_proven")
    if re.search(r"\b" + re.escape(register_array) + r"\b",
                 pattern.sub("", source_tail)):
        raise ValueError("original_array_padding_unparsed_raw_read")
    return seen


def rebind_constant_buffers(source, buffers, *, original_array_padding_zero=False):
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

        reserved_typed_padding_lanes = set()
        if original_array_padding_zero is True:
            for member in buffer["members"]:
                count = member.get("array_size", 0)
                if not count:
                    continue
                stride = 64 if member["matrix"] else 16
                for byte in range(member["index"], member["index"] + count * stride, 4):
                    at = byte // 4
                    if at < len(lanes) and lanes[at] is None:
                        reserved_typed_padding_lanes.add(at)
            prove_original_typed_padding_is_unread(
                source[block.end():], array, reserved_typed_padding_lanes)
        elif original_array_padding_zero is not False:
            raise ValueError("unverified_original_typed_padding_zero_optin")
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
                # The raw DXBC source audit proves this reserved anonymous
                # typed-array component cannot be read by the shader.
                if index in reserved_typed_padding_lanes:
                    return "0.0"
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



def original_compiled_cb_numeric_offset_profile(reflection, buffers, *, validator_text=""):
    """PRIVATE reflection comparison with counts-only, source-name-free output.

    This is diagnostic, never a waiver of strict Vulkan 1.1 validation or
    original member offset/array-stride verification.
    """
    resources = reflection.get("ubos", [])
    types = reflection.get("types", {})
    if not isinstance(resources, list) or not isinstance(types, dict):
        raise ValueError("untrusted_original_cb_reflection_shape")
    slots = {(row.get("set"), row.get("binding")): row
             for row in resources if isinstance(row, dict)}
    result = {
        "compiled_reflection_available": 1,
        "original_source_buffers_checked": 0,
        "original_member_fields_checked": 0,
        "compiled_members_without_source_match": 0,
        "compiled_member_offsets_match_original": 0,
        "compiled_member_offsets_differ_original": 0,
        "compiled_member_offsets_nonmonotonic": 0,
        "compiled_array_strides_differ_original": 0,
        "compiled_array_element_counts_differ_original": 0,
        "compiled_array_missing_reflected_type": 0,
        "compiled_members_struct_or_array": 0,
        "compiled_members_matrix": 0,
        "validator_overlap_pair_reflection_matches": 0,
        "validator_overlap_previous_source_field": 0,
        "validator_overlap_previous_synthetic_padding": 0,
        "validator_overlap_current_source_field": 0,
        "validator_overlap_current_synthetic_padding": 0,
        "validator_overlap_previous_original_array": 0,
        "validator_overlap_current_original_array": 0,
        "compiled_synthetic_padding_within_original_array_span": 0,
        "compiled_synthetic_padding_within_original_struct_span": 0,
        "compiled_synthetic_padding_outside_original_typed_spans": 0,
        "original_source_array_field_count": 0,
        "original_source_struct_field_count": 0,
    }
    for buffer in buffers:
        row = slots.get((0, buffer["translated_binding"]))
        if row is None:
            continue
        typename = row.get("type")
        layout = types.get(typename)
        if not isinstance(layout, dict) or not isinstance(layout.get("members"), list):
            continue
        result["original_source_buffers_checked"] += 1
        original = {m["name"]: m for m in
                    (buffer["members"] + buffer["structs"])}
        # A scalar/vector array occupies a full 16-byte register for every
        # source element, even when only .x or .xy is explicitly named. Any
        # added padding declaration inside that typed footprint overlaps
        # valid original array storage in Vulkan's Block layout.
        typed_spans = []
        for member in buffer["members"]:
            count = member.get("array_size", 0)
            if count:
                span = (64 if member.get("matrix") else 16) * count
                typed_spans.append((member["index"], member["index"] + span,
                                    "array"))
                result["original_source_array_field_count"] += 1
        for member in buffer["structs"]:
            span = member["size"] * max(1, member.get("array_size", 0))
            typed_spans.append((member["index"], member["index"] + span,
                                "struct"))
            result["original_source_struct_field_count"] += 1
        # Original identifiers are inspected privately only. Correlate the
        # numeric SPIR-V validator member index with reflected UBO members.
        # Export only fixed counts, never names/indices/byte offsets.
        for incident in re.finditer(
                r"structure member (\d+) at offset (\d+) overlaps previous "
                r"member ending at offset (\d+)",
                validator_text, flags=re.IGNORECASE):
            member_index, start, end = map(int, incident.groups())
            fields = layout["members"]
            if not 0 < member_index < len(fields) or end < start:
                continue
            current = fields[member_index]
            previous = fields[member_index-1]
            if current.get("offset") != start:
                continue
            result["validator_overlap_pair_reflection_matches"] += 1
            for role, field in (("previous", previous), ("current", current)):
                source = original.get(field.get("name"))
                result["validator_overlap_" + role +
                       ("_source_field" if source is not None
                        else "_synthetic_padding")] += 1
                if source is not None and source.get("array_size"):
                    result["validator_overlap_" + role +
                           "_original_array"] += 1
        previous_offset = -1
        for field in layout["members"]:
            if not isinstance(field, dict):
                continue
            result["original_member_fields_checked"] += 1
            off = field.get("offset")
            if type(off) is not int or off < 0:
                result["compiled_members_without_source_match"] += 1
                continue
            if previous_offset > off:
                result["compiled_member_offsets_nonmonotonic"] += 1
            previous_offset = off
            source = original.get(field.get("name"))
            if source is None:
                result["compiled_members_without_source_match"] += 1
                overlap_types = {
                    kind for lo, hi, kind in typed_spans if lo <= off < hi
                }
                if "array" in overlap_types:
                    result["compiled_synthetic_padding_within_original_array_span"] += 1
                if "struct" in overlap_types:
                    result["compiled_synthetic_padding_within_original_struct_span"] += 1
                if not overlap_types:
                    result["compiled_synthetic_padding_outside_original_typed_spans"] += 1
                continue
            key = ("compiled_member_offsets_match_original" if source["index"] == off
                   else "compiled_member_offsets_differ_original")
            result[key] += 1
            is_struct = "members" in source
            is_array = bool(source.get("array_size"))
            is_matrix = bool(source.get("matrix"))
            result["compiled_members_struct_or_array"] += int(is_struct or is_array)
            result["compiled_members_matrix"] += int(is_matrix)
            expected_stride = (
                source.get("size") if is_struct else
                64 if is_matrix else 16
            )
            if (is_array and field.get("array_stride") != expected_stride):
                result["compiled_array_strides_differ_original"] += 1
            if is_array:
                elements = field.get("array")
                if type(elements) is not list or len(elements) != 1:
                    result["compiled_array_missing_reflected_type"] += 1
                elif type(elements[0]) is not int or elements[0] != source["array_size"]:
                    result["compiled_array_element_counts_differ_original"] += 1
    return result


def verify_named_constant_buffers(private, stage, buffers, *, original_hlsl_offsets=False):
    candidate = private / "named-constant-buffers.hlsl"
    baseline = private / "resource-bound.hlsl"
    candidate.write_text(rebind_constant_buffers(
        baseline.read_text(encoding="utf-8"), buffers,
        original_array_padding_zero=(original_hlsl_offsets is True)),
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
        # On failure, inspect only counts from the privately reflected SPIR-V;
        # no shader source names, offsets, or private IDs leave the runner.
        safe_counts = {"compiled_reflection_available": 0}
        try:
            candidate_reflection = subprocess.run(
                ["spirv-cross", str(binary), "--reflect"],
                capture_output=True, timeout=30, check=False)
            if candidate_reflection.returncode == 0:
                safe_counts = original_compiled_cb_numeric_offset_profile(
                    json.loads(candidate_reflection.stdout), buffers,
                    validator_text=raw.decode("utf-8", "replace"))
        except (ValueError, TypeError, KeyError, OSError,
                subprocess.TimeoutExpired, json.JSONDecodeError):
            pass  # Diagnostics must not alter the authoritative failure.
        (private / "original-validator-layout-counts-private.json").write_text(
            json.dumps(safe_counts, sort_keys=True) + "\n", encoding="utf-8")
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
        if resource is None:
            # Fail closed but distinguish a reflection-elided buffer from
            # a source-name match at a different descriptor location.
            if any(row.get("name") == expected for row in resources):
                raise ValueError("named_constant_buffer_source_name_at_wrong_descriptor")
            raise ValueError("named_constant_buffer_source_block_not_reflected")
        if resource.get("name") != expected:
            raise ValueError("named_constant_buffer_source_block_name_changed")
        total += verify_members(buffer["members"] + buffer["structs"],
                                types[resource["type"]]["members"])
    return total
