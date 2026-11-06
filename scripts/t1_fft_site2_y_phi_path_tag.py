"""Private SPIR-V path counters for third original-derived FFT butterfly Y Phi.

Inject exactly two extra per-dispatch-X u32 atomic counters into the validated
Phi incoming predecessor terminator blocks. This is a source-only instrumented
artifact: it requires a future 128-word zeroed SSBO at set0/binding3 and exact
64x1x1 invocation fixture, and MUST NOT be shipped as an authored game shader.

Counter words [2*x + 0, 2*x + 1] tag the entry and loop-backedge execution
counts for each x invocation, without logging proprietary SSA or coordinate
values. Static validation is NOT GPU execution, preservation of output, or
proof of chosen Phi value at the third fetch.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess

from scripts.t1_fft_local_store_writers import read_module, value_shape
from scripts.t1_fft_spirv_reaching_stores import parse_functions
from scripts.t1_fft_site2_y_phi_inputs import analyze as incoming_probe, top_phi
from scripts.t1_fft_site2_y_phi_recurrence import analyze as recurrence_probe

PREFIX = "%t1_phi_route_"
MAX_ASSEMBLY_BYTES = 4 * 1024 * 1024
TRACE_SET, TRACE_BINDING = 0, 3
WORKGROUP_SIZE = (64, 1, 1)
COUNTER_U32 = 128

ASSIGN = re.compile(r"^\s*(%\w+)\s*=\s*(Op\w+)\b(.*)$")
ANNOTATION = re.compile(r"^\s*OpDecorate\s+(%\w+)\s+(DescriptorSet|Binding)\s+(\d+)\s*$")
BUILTIN = re.compile(r"^\s*OpDecorate\s+(%\w+)\s+BuiltIn\s+GlobalInvocationId\s*$")
BRANCH = re.compile(r"^\s*OpBranch\s+(%\w+)\s*$")


def _stripped(line):
    return line.split(";", 1)[0].strip()


def _global_invocation_input(text, types, values):
    items = [m.group(1) for line in text.splitlines()
             if (m := BUILTIN.match(_stripped(line))) is not None]
    if len(items) != 1:
        raise ValueError("Unique GlobalInvocationId not attested")
    gid = items[0]
    op, pointer, operands = values.get(gid, ("", None, []))
    if op != "OpVariable" or operands != ["Input"]:
        raise ValueError("GlobalInvocationId is not a direct Input variable")
    pointer_op, pointer_args = types.get(pointer, ("", []))
    if pointer_op != "OpTypePointer" or len(pointer_args) != 2 or pointer_args[0] != "Input":
        raise ValueError("Invocation Input pointer shape invalid")
    vec = pointer_args[1]
    vec_op, vec_args = types.get(vec, ("", []))
    if vec_op != "OpTypeVector" or len(vec_args) != 2 or vec_args[1] != "3":
        raise ValueError("Invocation ID is not a three-lane vector")
    scalar = vec_args[0]
    if types.get(scalar) != ("OpTypeInt", ["32", "0"]):
        raise ValueError("Invocation ID must be uint32x3")
    return gid, vec, scalar


def _layout(lines, types, values):
    if sum(_stripped(l) == "OpCapability Shader" for l in lines) != 1:
        raise ValueError("Expected exactly one Shader capability")
    if sum(_stripped(l) == "OpMemoryModel Logical GLSL450" for l in lines) != 1:
        raise ValueError("Expected Logical GLSL450 memory model")
    entrances = [m.group(1) for l in lines
                 if (m := re.match(r'^\s*OpEntryPoint\s+GLCompute\s+(%\w+)\s+"[^"]+"', _stripped(l))) is not None]
    if len(entrances) != 1 or sum(_stripped(l).startswith("OpEntryPoint ") for l in lines) != 1:
        raise ValueError("One unique compute entrypoint required")
    function_id = entrances[0]
    execution = [l for l in lines if re.match(
        rf"^\s*OpExecutionMode\s+{re.escape(function_id)}\s+LocalSize\s+64\s+1\s+1\s*$",
        _stripped(l))]
    if len(execution) != 1:
        raise ValueError("This counter layout is confined to original 64x1x1 fixture")

    decoration = {}
    for line in lines:
        match = ANNOTATION.match(_stripped(line))
        if match:
            key = (match.group(1), match.group(2))
            if key in decoration:
                raise ValueError("Duplicate descriptor decoration")
            decoration[key] = int(match.group(3))
    if any(v == TRACE_SET and decoration.get((ident, "Binding")) == TRACE_BINDING
           for (ident, field), v in decoration.items() if field == "DescriptorSet"):
        raise ValueError("Private counter set0/binding3 already occupied")
    entries = [i for i, l in enumerate(lines) if
               (m := ASSIGN.match(_stripped(l))) and m.group(2) == "OpFunction"]
    declarations = [i for i, l in enumerate(lines) if
                    (m := ASSIGN.match(_stripped(l))) and m.group(2).startswith("OpType")]
    if not entries or not declarations or min(declarations) >= min(entries):
        raise ValueError("Invalid SPIR-V declaration/function logical sections")
    return min(declarations), min(entries)


def _predecessors(text, phi_root, args):
    owners = [(fun, block) for fun in parse_functions(text)
              for block, seq in fun["blocks"].items()
              if any(rid == phi_root and op == "OpPhi" for op, rid, _ in seq)]
    if len(owners) != 1:
        raise ValueError("Third Y Phi has ambiguous CFG owner")
    fun, phi_block = owners[0]
    if len(args) != 4:
        raise ValueError("Third Y Phi requires exactly two predecessor pairs")
    preds = args[1::2]
    if len(set(preds)) != 2:
        raise ValueError("Third Y Phi predecessor alias detected")
    for pred in preds:
        seq = fun["blocks"].get(pred)
        if not seq or seq[-1][0] != "OpBranch" or seq[-1][2] != [phi_block]:
            raise ValueError("Third Y Phi incoming edge not unconditional exact branch")
    return preds, phi_block


def instrument(assembly):
    if type(assembly) is not str or PREFIX in assembly or not 20 <= len(assembly.encode("utf-8")) <= MAX_ASSEMBLY_BYTES:
        raise ValueError("Private FFT SPIR-V source unbounded or already tagged")
    checked = incoming_probe(assembly, require_original=True)
    recurrence = recurrence_probe(assembly, require_original=True)
    if (checked.get("status") != "verified_translated_site2_y_phi_incoming_cfg"
            or checked.get("incoming_count") != 2 or recurrence.get("incoming_count") != 2):
        raise ValueError("Third FFT butterfly Phi incoming provenance unverified")
    roots = checked["incoming"]
    static = recurrence["inputs"]
    candidates = [i for i in range(2) if (roots[i]["predecessor_in_structural_cfg_cycle"]
                  is False and static[i]["same_selected_phi_component_data_edge_possible"] is False
                  and static[i]["unknown_dataflow_possible"] is False)]
    loops = [i for i in range(2) if (roots[i]["predecessor_in_structural_cfg_cycle"]
             is True and static[i]["same_selected_phi_component_data_edge_possible"] is True
             and static[i]["unknown_dataflow_possible"] is False)]
    if len(candidates) != 1 or len(loops) != 1 or candidates[0] == loops[0]:
        raise ValueError("Private entry and real loop value recurrence not distinguished")
    labels = {candidates[0]: 0, loops[0]: 1}

    types, values, _, _, fetches = read_module(assembly)
    phi_root, lane, status = top_phi(fetches[2][1], values, types)
    if status != "phi" or phi_root is None or value_shape(phi_root, values, types)[0] != "float32":
        raise ValueError("Third Y Phi component identity lost")
    op, _, args = values[phi_root]
    if op != "OpPhi":
        raise ValueError("Third Y no longer OpPhi")
    preds, phi_block = _predecessors(assembly, phi_root, args)
    lines = assembly.splitlines()
    type_index, function_index = _layout(lines, types, values)
    gid, gidtype, u32 = _global_invocation_input(assembly, types, values)

    extra_types = [
        f"{PREFIX}array = OpTypeRuntimeArray {u32}",
        f"{PREFIX}block = OpTypeStruct {PREFIX}array",
        f"{PREFIX}ptr_struct = OpTypePointer StorageBuffer {PREFIX}block",
        f"{PREFIX}ptr_word = OpTypePointer StorageBuffer {u32}",
    ]
    # Reuse actual existing u32 type; new fixed public constants only.
    consts = [
        f"{PREFIX}c0 = OpConstant {u32} 0",
        f"{PREFIX}c1 = OpConstant {u32} 1",
        f"{PREFIX}c2 = OpConstant {u32} 2",
        f"{PREFIX}buffer = OpVariable {PREFIX}ptr_struct StorageBuffer",
    ]
    annotations = [
        f"OpDecorate {PREFIX}array ArrayStride 4",
        f"OpMemberDecorate {PREFIX}block 0 Offset 0",
        f"OpDecorate {PREFIX}block Block",
        f"OpDecorate {PREFIX}buffer DescriptorSet 0",
        f"OpDecorate {PREFIX}buffer Binding 3",
    ]
    positions = []
    for input_idx, pred in enumerate(preds):
        target = labels[input_idx]
        block_labels = [i for i, l in enumerate(lines)
                        if _stripped(l) == f"{pred} = OpLabel"]
        if len(block_labels) != 1:
            raise ValueError("Phi predecessor label missing or duplicated")
        i = block_labels[0] + 1
        stop = i
        while stop < len(lines) and _stripped(lines[stop]) != "OpFunctionEnd" and not re.search(
                r"=\s*OpLabel\b", _stripped(lines[stop])):
            stop += 1
        branch_positions = [k for k in range(i, stop)
                            if BRANCH.match(_stripped(lines[k]))]
        if len(branch_positions) != 1 or BRANCH.match(_stripped(lines[branch_positions[0]])).group(1) != phi_block:
            raise ValueError("Third Phi predecessor physical branch locator ambiguous")
        last = [k for k in range(i, stop) if _stripped(lines[k]) and not _stripped(lines[k]).startswith("OpLine ")]
        if not last or last[-1] != branch_positions[0]:
            raise ValueError("Terminator location is not final in predecessor")
        positions.append((branch_positions[0], target))
    if len({p[0] for p in positions}) != 2:
        raise ValueError("Same physical branch would be instrumented twice")

    # Two slot counters per x invocation: 0 = entry, 1 = loop continuation.
    # Caller must bind 128 zeroed u32 words and limit dispatch to exactly 64x1x1.
    inserts = [(type_index, annotations), (function_index, extra_types + consts)]
    for at, tag in positions:
        prefix = f"{PREFIX}edge{tag}_"
        instructions = [
            f"{prefix}gid = OpLoad {gidtype} {gid}",
            f"{prefix}x = OpCompositeExtract {u32} {prefix}gid 0",
            f"{prefix}twox = OpIMul {u32} {prefix}x {PREFIX}c2",
            f"{prefix}index = OpIAdd {u32} {prefix}twox {PREFIX}c{tag}",
            f"{prefix}pointer = OpAccessChain {PREFIX}ptr_word {PREFIX}buffer {PREFIX}c0 {prefix}index",
            f"{prefix}atomic = OpAtomicIAdd {u32} {prefix}pointer {PREFIX}c1 {PREFIX}c0 {PREFIX}c1",
        ]
        inserts.append((at, instructions))
    for index, content in sorted(inserts, reverse=True):
        lines[index:index] = content
    result = "\n".join(lines) + "\n"
    if result.count(" = OpAtomicIAdd ") != 2:
        raise ValueError("Phi edge counter insertion incomplete")
    return result, {
        "status": "private_third_fft_phi_Y_two_predecessor_counter_source",
        "two_unconditional_Cfg_predecessor_edges_tagged": True,
        "source_local_group_size": [64, 1, 1],
        "counter_storage_set": TRACE_SET,
        "counter_storage_binding": TRACE_BINDING,
        "required_zeroed_counter_words": COUNTER_U32,
        "index_layout": "invocation_x_times_2_plus_entry_or_backedge",
        "branch_tags": ["entry", "backedge"],
        "source_opcode_count": 2,
        "shader_original_source_mutated": False,
        "private_original_shader_bytes_logged": False,
        "actual_GPU_counter_readback_proven": False,
        "output_invariance_proven": False,
        "authored_unity_runtime_kernel_identity_proven": False,
        "android_water_proven": False,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("private_original_derived_spirv_assembly", type=Path)
    p.add_argument("private_instrumented_spirv_assembly", type=Path)
    a = p.parse_args()
    try:
        src, dest = a.private_original_derived_spirv_assembly, a.private_instrumented_spirv_assembly
        if (src.is_symlink() or not src.is_file() or not 20 <= src.stat().st_size <= MAX_ASSEMBLY_BYTES
                or dest.is_symlink() or dest.exists() or not dest.parent.is_dir()):
            raise ValueError("Private assembly source or target is unsafe")
        report_text, report = instrument(src.read_text(encoding="utf-8"))
        with dest.open("x", encoding="utf-8") as output:
            output.write(report_text)
    except (OSError, UnicodeError, ValueError, KeyError, TypeError, IndexError):
        p.exit(2, "RAFT_T1_SITE2Y_PHI_PATH_TAG source_injection_unverified=true\n")
    print("RAFT_T1_SITE2Y_PHI_PATH_TAG " + json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
