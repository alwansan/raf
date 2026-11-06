"""Private original FFT SPIR-V ImageFetch keyed recorder (no HLSL conversion).

This operates ONLY on a SHA-authenticated original SPIR-V disassembly in the
isolated runner. The result and all traces remain private. The public report
never contains original SSA IDs, numeric operands, pixels or source bytes.
"""
import argparse
import json
from pathlib import Path
import re

from scripts.t1_fft_local_store_writers import read_module, image_role, type_shape, value_shape
from scripts.t1_fft_original_keyed_preflight import _decorations, _input_var_shape
from scripts.t1_fft_trace_compare import CAPACITY, INVOCATION_RECORD

PREFIX = "%t1_original_trace_"
ASM_LIMIT = 2 * 1024 * 1024
LINE_LIMIT = 60000
ASSIGN = re.compile(r"^\s*(%\w+)\s*=\s*(Op\w+)\b(.*)$")
ENTRY = re.compile(r'^(\s*OpEntryPoint\s+GLCompute\s+(%\w+)\s+"[^"]+"[^\r\n;]*)(\s*(?:;[^\r\n]*)?)$')
EXPECTED_ROLES = ["source", "butterfly", "butterfly"]


def _pick_type(types, op, fields):
    for name, (actual, args) in types.items():
        if actual == op and args == list(fields):
            return name
    return None


def _layout(text, types, values, decorations, fetches):
    lines = text.splitlines()
    entry = [(i, ENTRY.match(x)) for i, x in enumerate(lines) if ENTRY.match(x)]
    if len(entry) != 1 or sum(x.lstrip().startswith("OpEntryPoint ") for x in lines) != 1:
        raise ValueError("Expected single compute shader entrypoint")
    entry_i, match = entry[0]
    function_id = match.group(2)
    functions = [i for i, x in enumerate(lines)
                 if ASSIGN.match(x) and ASSIGN.match(x).group(2) == "OpFunction"]
    types_indices = [i for i, x in enumerate(lines)
                     if ASSIGN.match(x) and ASSIGN.match(x).group(2).startswith("OpType")]
    if not functions or not types_indices or min(types_indices) <= entry_i:
        raise ValueError("Invalid original SPIR-V logical sections")
    entry_functions = [i for i in functions
                       if ASSIGN.match(lines[i]).group(1) == function_id]
    if len(entry_functions) != 1:
        raise ValueError("Compute entrypoint function not uniquely defined")
    fun_i = entry_functions[0]
    fun_end = next((i for i in range(fun_i + 1, len(lines))
                    if lines[i].split(";", 1)[0].strip() == "OpFunctionEnd"), None)
    label_i = next((i for i in range(fun_i + 1, fun_end or len(lines))
                    if ASSIGN.match(lines[i]) and ASSIGN.match(lines[i]).group(2) == "OpLabel"), None)
    if fun_end is None or label_i is None:
        raise ValueError("Compute entrypoint block is absent")
    fetch_lines = [(i, ASSIGN.match(x)) for i, x in enumerate(lines)
                   if ASSIGN.match(x) and ASSIGN.match(x).group(2) == "OpImageFetch"]
    if len(fetch_lines) != 3 or not all(label_i < i < fun_end for i, _ in fetch_lines):
        raise ValueError("ImageFetch sites not owned by compute entrypoint")
    if [image_role(img, values, decorations) for img, _ in fetches] != EXPECTED_ROLES:
        raise ValueError("Original FFT ImageFetch descriptor roles differ")
    for (_, coord), (_, match_fetch) in zip(fetches, fetch_lines):
        if value_shape(coord, values, types) != ("sint32", 2):
            raise ValueError("Unexpected original ImageFetch coordinate shape")
        if value_shape(match_fetch.group(1), values, types) != ("float32", 4):
            raise ValueError("Unexpected original fetched pixel type")
    return lines, entry_i, match, fun_i, label_i, fetch_lines, min(types_indices), min(functions)


def instrument(assembly):
    if not isinstance(assembly, str) or not 20 <= len(assembly.encode("utf-8")) <= ASM_LIMIT:
        raise ValueError("Private assembly length invalid")
    if len(assembly.splitlines()) > LINE_LIMIT or PREFIX in assembly:
        raise ValueError("Original shader exceeds bound or already contains recorder")
    types, values, decor, _, fetches = read_module(assembly)
    lines, entry_i, entry, _, label_i, fetch_lines, type_i, first_function = _layout(
        assembly, types, values, decor, fetches)
    desc, builtins, member_builtins, interfaces = _decorations(assembly)
    if len(builtins) != 1 or member_builtins:
        raise ValueError("Expected one original direct invocation builtin")
    builtin = next(iter(builtins))
    pointee = _input_var_shape(builtin, types, values)
    if builtin not in interfaces or type_shape(pointee, types) != ("sint32", 3):
        raise ValueError("Original invocation builtin interface/type not proven")
    occupied = {(v, desc[(id_, "Binding")])
                for (id_, kind), v in desc.items()
                if kind == "DescriptorSet" and (id_, "Binding") in desc}
    if (0, 3) in occupied:
        raise ValueError("Private trace descriptor set0 binding3 collision")
    if any(x.lstrip().startswith("OpCapability Shader") for x in lines) is False:
        raise ValueError("Original module is not a compute shader")
    if "OpMemoryModel Logical GLSL450" not in assembly:
        raise ValueError("Unexpected source memory model")

    scalar_u32 = _pick_type(types, "OpTypeInt", ("32", "0"))
    scalar_s32 = _pick_type(types, "OpTypeInt", ("32", "1"))
    scalar_f32 = _pick_type(types, "OpTypeFloat", ("32",))
    if scalar_s32 is None or scalar_f32 is None:
        raise ValueError("Original scalar numeric types unavailable")
    added = []
    if scalar_u32 is None:
        scalar_u32 = PREFIX + "u32"
        added.append(f"{scalar_u32} = OpTypeInt 32 0")
    v3u = _pick_type(types, "OpTypeVector", (scalar_u32, "3"))
    if v3u is None:
        v3u = PREFIX + "v3u"
        added.append(f"{v3u} = OpTypeVector {scalar_u32} 3")
    v4u = _pick_type(types, "OpTypeVector", (scalar_u32, "4"))
    if v4u is None:
        v4u = PREFIX + "v4u"
        added.append(f"{v4u} = OpTypeVector {scalar_u32} 4")
    booltype = _pick_type(types, "OpTypeBool", ())
    if booltype is None:
        booltype = PREFIX + "bool"
        added.append(f"{booltype} = OpTypeBool")

    new_types = {
        "arr": f"{PREFIX}array",
        "block": f"{PREFIX}block",
        "ptrblock": f"{PREFIX}ptr_buffer",
        "ptrword": f"{PREFIX}ptr_word",
        "ptrfunc": f"{PREFIX}ptr_fun_u32",
    }
    added.extend((
        f'{new_types["arr"]} = OpTypeRuntimeArray {scalar_u32}',
        f'{new_types["block"]} = OpTypeStruct {new_types["arr"]}',
        f'{new_types["ptrblock"]} = OpTypePointer StorageBuffer {new_types["block"]}',
        f'{new_types["ptrword"]} = OpTypePointer StorageBuffer {scalar_u32}',
        f'{new_types["ptrfunc"]} = OpTypePointer Function {scalar_u32}',
    ))
    existing_constants = {}
    for ident, (op, typ, operands) in values.items():
        if op == "OpConstant" and typ == scalar_u32 and len(operands) == 1:
            if operands[0].isdecimal() and int(operands[0]) <= CAPACITY:
                existing_constants.setdefault(int(operands[0]), ident)
    nums = sorted(set(range(13)) | {CAPACITY - 1, CAPACITY})
    const = {}
    for num in nums:
        if num in existing_constants:
            const[num] = existing_constants[num]
        else:
            const[num] = f"{PREFIX}const{num}"
            added.append(f"{const[num]} = OpConstant {scalar_u32} {num}")
    buffer = PREFIX + "buffer"
    added.append(f"{buffer} = OpVariable {new_types['ptrblock']} StorageBuffer")

    decorations = [
        f'OpDecorate {new_types["arr"]} ArrayStride 4',
        f'OpMemberDecorate {new_types["block"]} 0 Offset 0',
        f'OpDecorate {new_types["block"]} Block',
        f'OpDecorate {buffer} DescriptorSet 0',
        f'OpDecorate {buffer} Binding 3',
    ]

    occ_vars = [f"{PREFIX}occ_{site}" for site in range(3)]
    local_init = [f"{var} = OpVariable {new_types['ptrfunc']} Function {const[0]}"
                  for var in occ_vars]

    def record(site, fetch):
        rid = fetch.group(1)
        args = fetch.group(3).split(";", 1)[0].strip().split()
        # args = result type, image operand, coordinate, optional ImageOperands
        if len(args) < 3:
            raise ValueError("ImageFetch has no coordinate operand")
        coord = args[2]
        prefix = f"{PREFIX}s{site}_"
        stmts = []
        def emit(stem, opcode, *operands):
            name = prefix + stem
            stmts.append(f"{name} = {opcode} {' '.join(operands)}")
            return name
        def store(word, value):
            off = (base if word == 0 else
                   emit(f"offset{word}", "OpIAdd", scalar_u32, base, const[word]))
            ptr = emit(f"ptr{word}", "OpAccessChain", new_types["ptrword"],
                       buffer, const[0], off)
            stmts.append(f"OpStore {ptr} {value}")

        occurrence = emit("occ_before", "OpLoad", scalar_u32, occ_vars[site])
        increment = emit("occ_after", "OpIAdd", scalar_u32, occurrence, const[1])
        stmts.append(f"OpStore {occ_vars[site]} {increment}")
        pointer = emit("count_ptr", "OpAccessChain", new_types["ptrword"],
                       buffer, const[0], const[0])
        index = emit("index", "OpAtomicIAdd", scalar_u32, pointer,
                     const[1], const[0], const[1])
        in_bounds = emit("in_bounds", "OpULessThan", booltype, index, const[CAPACITY])
        slot = emit("slot", "OpSelect", scalar_u32, in_bounds, index,
                    const[CAPACITY - 1])
        row_start = emit("row_start", "OpIMul", scalar_u32, slot, const[12])
        base = emit("base", "OpIAdd", scalar_u32, row_start, const[1])

        gid_vec = emit("gid_signed", "OpLoad",
                       pointee, builtin)
        gid_unsigned = emit("gid_unsigned", "OpBitcast", v3u, gid_vec)
        gid = [emit(f"gid_{j}", "OpCompositeExtract", scalar_u32,
                    gid_unsigned, str(j)) for j in range(3)]
        coords = [
            emit(f"coord_{j}", "OpBitcast", scalar_u32,
                 emit(f"coord_signed_{j}", "OpCompositeExtract", scalar_s32,
                      coord, str(j)))
            for j in (0, 1)
        ]
        pixels_u = emit("pixel_uint", "OpBitcast", v4u, rid)
        channels = [emit(f"pixel_{j}", "OpCompositeExtract", scalar_u32,
                         pixels_u, str(j)) for j in range(4)]
        items = [const[site], *gid, occurrence, *coords, const[0], *channels]
        if len(items) != 12 or INVOCATION_RECORD.size != 48:
            raise ValueError("Original keyed trace layout width not proven")
        for j, item in enumerate(items):
            store(j, item)
        return stmts

    # Mutation indices are computed only on the original disassembly and
    # applied in reverse. No source item is modified in the repository.
    # spirv-as --target-env vulkan1.1 emits SPIR-V <= 1.3: OpEntryPoint
    # interfaces contain Input/Output variables only. StorageBuffer MUST
    # remain a global descriptor but MUST NOT be appended to that interface.
    edits = [
        (type_i, 0, decorations),
        (first_function, 0, added),
        (label_i + 1, 0, local_init),
    ]
    for site, (idx, match) in enumerate(fetch_lines):
        edits.append((idx + 1, 0, record(site, match)))
    for idx, remove, replacement in sorted(edits, key=lambda x:x[0], reverse=True):
        lines[idx:idx + remove] = replacement
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("private_original_assembly", type=Path)
    parser.add_argument("private_instrumented_assembly", type=Path)
    args = parser.parse_args()
    try:
        if not 20 <= args.private_original_assembly.stat().st_size <= ASM_LIMIT:
            raise ValueError("Original private FFT assembly outside byte bound")
        modified = instrument(args.private_original_assembly.read_text(encoding="utf-8"))
        with args.private_instrumented_assembly.open("x", encoding="utf-8") as out:
            out.write(modified)
    except (OSError, ValueError, UnicodeError, KeyError, IndexError):
        parser.exit(2, "Original private SPIR-V keyed ImageFetch instrumenter rejected input\n")
    print("RAFT_T1_ORIGINAL_KEYED_INSTRUMENT " + json.dumps({
        "status": "private_original_spirv_imagefetch_instrumented_unvalidated",
        "imagefetch_sites": 3, "invocation_record_u32_words": 12,
        "storage_descriptor_set": 0, "storage_descriptor_binding": 3,
        "capacity": CAPACITY, "capacity_overflow_clamped_and_counter_reported": True,
        "source_builtin": "existing_signed32_vector3_GlobalInvocationId",
        "actual_gpu_execution_proven": False, "numeric_parity_proven": False,
        "private_shader_source_exported": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
