"""Inject an unused GlobalInvocationId Input into a PRIVATE original FFT SPIR-V.

This is a prerequisite probe, NOT original read instrumentation. The patched
module stays in private scratch and must be assembled, spirv-val validated and
tested on Vulkan before any keyed trace is attempted. Never expose private
source, literal values, numeric identifiers or original shader binary.
"""
import argparse
import json
from pathlib import Path
import re

MAX_ASM_BYTES = 2 * 1024 * 1024
MAX_LINES = 60000
NAMESPACE = "%t1_gid_"
PREFIX = "%t1_gid_"
ASSIGNMENT = re.compile(r"^\s*(%\w+)\s*=\s*(Op\w+)\b(.*)$")
ENTRY = re.compile(r'^(\s*OpEntryPoint\s+GLCompute\s+(%\w+)\s+"[^"]+"[^\r\n;]*)(\s*(?:;[^\r\n]*)?)$')
TYPES = {
    "OpTypeInt", "OpTypeFloat", "OpTypeVector", "OpTypePointer",
}
EXPECTED_MEMORY_MODEL = "OpMemoryModel Logical GLSL450"


def _type_for(types, op, operands):
    for result, definition in types.items():
        if definition == (op, tuple(operands)):
            return result
    return None


def inject(assembly):
    if not isinstance(assembly, str) or not 0 < len(assembly.encode("utf-8")) <= MAX_ASM_BYTES:
        raise ValueError("Original SPIR-V assembly size invalid")
    lines = assembly.splitlines(keepends=True)
    if len(lines) > MAX_LINES or re.search(r"%t1_gid_\w*", assembly):
        raise ValueError("Original shader exceeds bound or instrumentation already applied")
    content = [line.rstrip("\r\n") for line in lines]
    if not any(re.match(r"^\s*OpCapability Shader\s*(?:;.*)?$", x) for x in content):
        raise ValueError("Shader capability not proven")
    if not any(x.strip().split(";")[0].strip() == EXPECTED_MEMORY_MODEL for x in content):
        raise ValueError("Expected Vulkan GLSL450 memory model not proven")
    matches = [(i, ENTRY.match(x)) for i, x in enumerate(content) if ENTRY.match(x)]
    if len(matches) != 1 or sum(bool(re.match(r"^\s*OpEntryPoint\b", x)) for x in content) != 1:
        raise ValueError("Expected exactly one compute entry point")
    entry_idx, entry = matches[0]
    function_id = entry.group(2)
    # If the original already exposes this input, do not duplicate. Caller
    # should first use that through a distinct source-authenticated path.
    if any(re.search(r"\bBuiltIn\s+GlobalInvocationId\b", x) for x in content):
        raise ValueError("Original already declares GlobalInvocationId")

    types = {}
    for raw in content:
        match = ASSIGNMENT.match(raw)
        if match and match.group(2).startswith("OpType"):
            types[match.group(1)] = (match.group(2),
                                       tuple(match.group(3).split(";", 1)[0].strip().split()))

    u32 = _type_for(types, "OpTypeInt", ("32", "0"))
    newtypes = []
    if u32 is None:
        u32 = PREFIX + "uint32"
        newtypes.append(f"{u32} = OpTypeInt 32 0")
    v3u = _type_for(types, "OpTypeVector", (u32, "3"))
    if v3u is None:
        v3u = PREFIX + "v3uint"
        newtypes.append(f"{v3u} = OpTypeVector {u32} 3")
    pin = _type_for(types, "OpTypePointer", ("Input", v3u))
    if pin is None:
        pin = PREFIX + "ptr_input_v3uint"
        newtypes.append(f"{pin} = OpTypePointer Input {v3u}")
    variable = PREFIX + "builtin_input"
    loaded = PREFIX + "loaded_id"

    type_positions = [i for i, raw in enumerate(content)
                      if (ASSIGNMENT.match(raw) and
                          ASSIGNMENT.match(raw).group(2).startswith("OpType"))]
    function_positions = [i for i, raw in enumerate(content)
                          if ASSIGNMENT.match(raw) and
                          ASSIGNMENT.match(raw).group(2) == "OpFunction"]
    if not type_positions or not function_positions:
        raise ValueError("Original type/function section not found")
    first_type, first_function = min(type_positions), min(function_positions)
    if first_type <= entry_idx or first_function <= first_type:
        raise ValueError("Unexpected SPIR-V logical layout")
    fn_positions = [i for i in function_positions
                    if ASSIGNMENT.match(content[i]).group(1) == function_id]
    if len(fn_positions) != 1:
        raise ValueError("Compute entry function ID not found")
    fn_idx = fn_positions[0]

    # Locate the entry block of the exact compute entry function, not an
    # unrelated helper function, and insert after its Function OpVariables.
    block = None
    for i in range(fn_idx + 1, len(content)):
        raw = content[i]
        if "OpFunctionEnd" in raw.split(";", 1)[0].split():
            break
        match = ASSIGNMENT.match(raw)
        if match and match.group(2) == "OpLabel":
            block = i
            break
    if block is None:
        raise ValueError("Compute entry function block not found")
    insert_load = block + 1
    while insert_load < len(content):
        raw = content[insert_load]
        tok = raw.split(";", 1)[0].split()
        if not tok:
            insert_load += 1
            continue
        match = ASSIGNMENT.match(raw)
        if match and match.group(2) == "OpVariable" and re.search(r"\bFunction\b", match.group(3)):
            insert_load += 1
            continue
        if tok[0] in ("OpLine", "OpNoLine"):
            insert_load += 1
            continue
        break
    if insert_load >= len(content):
        raise ValueError("Original entrypoint instruction insertion invalid")

    # Perform edits in reverse source order to avoid stale offsets.
    edits = [
        (entry_idx, 1, [entry.group(1) + " " + variable + entry.group(3)]),
        (first_type, 0, [f"OpDecorate {variable} BuiltIn GlobalInvocationId"]),
        (first_function, 0, [*newtypes, f"{variable} = OpVariable {pin} Input"]),
        (insert_load, 0, [f"{loaded} = OpLoad {v3u} {variable}"]),
    ]
    for idx, remove, insert in sorted(edits, reverse=True):
        content[idx:idx + remove] = insert
    patched = "\n".join(content) + "\n"
    if (patched.count(" BuiltIn GlobalInvocationId") != 1 or
            patched.count(f"{loaded} = OpLoad") != 1 or
            patched.count(f"{variable} = OpVariable") != 1):
        raise ValueError("Injected dispatch Input did not preserve uniqueness")
    return patched


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        if not 20 <= args.input.stat().st_size <= MAX_ASM_BYTES:
            raise ValueError("Private assembly outside byte limit")
        updated = inject(args.input.read_text(encoding="utf-8"))
        with args.output.open("x", encoding="utf-8") as target:
            target.write(updated)
    except (OSError, UnicodeError, ValueError):
        parser.exit(2, "Private original dispatch builtin probe could not be proven\n")
    print("RAFT_T1_ORIGINAL_DISPATCH_INPUT_INJECT " + json.dumps({
        "status": "injected_original_spirv_builtin_prerequisite_only",
        "global_invocation_id_added": True,
        "entry_interface_extended": True,
        "unused_builtin_load_added": True,
        "original_fetch_instrumented": False,
        "original_invocation_keyed_buffer_produced": False,
        "numeric_parity_proven": False,
        "private_shader_source_exported": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
